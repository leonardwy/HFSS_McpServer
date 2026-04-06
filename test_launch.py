import asyncio
import sys
sys.path.insert(0, '.')
from hfss_server import handle_tool_call

async def test():
    print('Starting test...')
    result = await handle_tool_call('hfss_launch_app', {'non_graphical': False})
    print(f'Result: {result}')
    with open('test_result.txt', 'w') as f:
        f.write(f'Result: {result}\n')

asyncio.run(test())
print('Done')
