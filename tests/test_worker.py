import asyncio
from roborabbit.roborabbit import RoboRabbit
from pathlib import Path


async def handler(event):
    print(event)


async def work():
    robo = RoboRabbit(Path('test_1.yaml'))
    await robo.run({'queue_1': handler})

try:
    asyncio.run(work())
except KeyboardInterrupt:
    # <-- could happen here
    print('here')
finally:
    # <-- could happen here
    print('there')
