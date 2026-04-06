"""Debug script for hfss_launch_app"""
import asyncio
import logging
import sys

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

sys.path.insert(0, '.')

async def test():
    print("=" * 50)
    print("Starting hfss_launch_app debug test")
    print("=" * 50)
    
    from hfss_server import handle_tool_call, session_manager
    
    print(f"\nBefore call:")
    print(f"  is_valid: {session_manager.is_valid()}")
    print(f"  is_initialized: {session_manager.is_initialized}")
    
    try:
        result = await handle_tool_call('hfss_launch_app', {'non_graphical': False})
        print(f"\nResult: {result}")
    except Exception as e:
        print(f"\nException: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\nAfter call:")
    print(f"  is_valid: {session_manager.is_valid()}")
    print(f"  is_initialized: {session_manager.is_initialized}")
    if session_manager._current_session:
        print(f"  session: {session_manager._current_session.name}")

asyncio.run(test())
