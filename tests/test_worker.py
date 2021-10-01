import asyncio
from roborabbit.rmq import worker
import asyncio


async def work():
    # await worker('queue_1', 'tests/test_1.yaml')
    print('start work')
    async for r in worker('queue_1', 'tests/test_1.yaml'):
        print(r)
        print('taking a message!')

try:
    asyncio.run(work())
except KeyboardInterrupt:
    # <-- could happen here
    print('here')
finally:
    # <-- could happen here
    print('there')
