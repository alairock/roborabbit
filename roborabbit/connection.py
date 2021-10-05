import os
import aio_pika
import asyncio
from roborabbit.logger import logger


async def connect(cfg=None):
    for _ in range(10):
        # try to connect 10 times
        try:
            username = cfg.get('username', os.getenv('RABBIT_USER', '/'))
            password = cfg.get('password', os.getenv('RABBIT_PASS', 'guest'))
            host = cfg.get('host', os.getenv('RABBIT_HOST', os.getenv('RABBIT_URL', 'localhost')))
            port = cfg.get('port', os.getenv('RABBIT_PORT', 5672))
            virtualhost = cfg.get('virtualhost', os.getenv('RABBIT_VHOST', os.getenv('RABBIT_VIRTUALHOST', '/')))
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


class Connection:
    def __init__(self,
                 host=None,
                 username=None,
                 password=None,
                 port=None,
                 virtualhost=None):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.virtualhost = virtualhost
