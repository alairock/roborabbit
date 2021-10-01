import os
import aio_pika
import asyncio
from roborabbit.logger import logger


async def connect(cfg=None):
    for _ in range(10):
        # try to connect 10 times
        try:
            vh = cfg['virtualhost'] if cfg['virtualhost'] != '/' else ''
            username = os.getenv('RABBIT_USER', cfg['username'])
            password = os.getenv('RABBIT_PASS', cfg['password'])
            host = os.getenv('RABBIT_HOST', cfg['host'])
            port = os.getenv('RABBIT_PORT', cfg['port'])
            virtualhost = os.getenv('RABBIT_VHOST', vh)
            connection_url = f"amqp://{username}:{password}@{host}:{port}/{virtualhost}"
            logger.info(f'Connecting to {connection_url}')
            connection: aio_pika.RobustConnection = await aio_pika.connect_robust(
                connection_url,
                client_properties={"client_properties": {
                    "service": "roborabbit"}},
            )
            logger.info('Connected!')
            break
        except ConnectionError:
            # try again
            logger.info('Connection failed, trying again...')
            await asyncio.sleep(3)
        else:
            raise ConnectionError(
                f"Could not connect to rabbit at {cfg.url} "
                f"with username {cfg.username}"
            )
    return connection
