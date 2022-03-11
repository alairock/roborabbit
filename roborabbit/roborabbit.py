import asyncio

from roborabbit.connection import Connection
from roborabbit.logger import logger
from roborabbit.rmq import create_from_config


class RoboRabbit:
    _connection = None

    def __init__(self, path, connection: Connection = None):
        self.connection_config = connection
        self.path = path
        self.initialized = False
        self.connection = None
        self.queues = None

    @classmethod
    def set_conn(cls, connection):
        cls._connection = connection

    @classmethod
    async def get_conn(cls):
        return cls._connection

    async def _startup(self):
        if not self.initialized:
            self.connection, self.queues = await create_from_config(self.path, _connection=self.connection_config)
            self.set_conn(self.connection)
            self.initialized = True

    async def _job_definition(self, queue, callback):
        if queue not in self.queues:
            raise Exception(f'Queue is not in your configuration: {queue}')
        async with self.queues[queue].iterator() as _q:
            async for message in _q:
                try:
                    await callback(message)
                    await message.ack()
                except asyncio.CancelledError:
                    await message.nack()
                    self.connection.close()
                except Exception as e:
                    logger.error('Bad things happened. Rejecting message with error:', e)
                    await message.reject()

    async def run(self, queue_map):
        await self._startup()
        jobs = []
        for _qm in queue_map:
            jobs.append(asyncio.create_task(self._job_definition(_qm, queue_map[_qm])))

        await asyncio.wait(jobs)
