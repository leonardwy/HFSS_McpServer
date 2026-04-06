import sys
sys.path.insert(0, '.')
from hfss_server import session_manager
import psutil

print("=== HFSS MCP Server Status ===")
print()

# Check HFSS process
print("HFSS Processes:")
for proc in psutil.process_iter(['pid', 'name']):
    try:
        if 'ansys' in proc.info['name'].lower():
            print(f"  {proc.info['name']} (PID: {proc.info['pid']})")
    except:
        pass

print()
print("Session Manager State:")
print(f"  is_valid: {session_manager.is_valid()}")
print(f"  is_initialized: {session_manager.is_initialized}")
print(f"  is_connected: {session_manager.is_connected}")
print(f"  _current_session: {session_manager._current_session}")
print(f"  _sessions count: {len(session_manager._sessions)}")

if session_manager._current_session:
    print(f"  Session project: {session_manager._current_session.name}")
    print(f"  Session design: {session_manager._current_session.design_name}")
