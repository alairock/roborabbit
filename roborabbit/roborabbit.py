import asyncio

from roborabbit.logger import logger
from roborabbit.rmq import create_from_config


class RoboRabbit:
    def __init__(self, path):
        self.path = path
        self.initialized = False
        self.connection = None
        self.queues = None

    async def _startup(self):
        if not self.initialized:
            self.connection, self.queues = await create_from_config(self.path)
            self.initialized = True

    async def _worker(self, queue):
        if queue not in self.queues:
            raise Exception(f'Queue is not in your configuration: {queue}')

        async with self.queues[queue].iterator() as _q:
            async for message in _q:
                try:
                    yield message
                    message.ack()
                except asyncio.CancelledError:
                    message.nack()
                    self.connection.close()
                except Exception as e:
                    logger.error(e)
                    message.reject()

    async def _job_definition(self, queue, callback):
        async for message in self._worker(queue):
            await callback(message)

    async def run(self, queue_map):
        await self._startup()
        jobs = []
        for _qm in queue_map:
            jobs.append(asyncio.create_task(self._job_definition(_qm, queue_map[_qm])))

        await asyncio.wait(jobs)
