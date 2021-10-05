import asyncio
from roborabbit.roborabbit import RoboRabbit
from roborabbit.connection import Connection
from pathlib import Path


async def handler(event):
    print(event)


async def work():
    connection = Connection(host='localhostz', username='bob', password='pas123', port=4499, virtualhost='/')
    robo = RoboRabbit(Path('test_1.yaml'), connection)
    await robo.run({'queue_1': handler})

try:
    asyncio.run(work())
except KeyboardInterrupt:
    # <-- could happen here
    print('here')
finally:
    # <-- could happen here
    print('there')
