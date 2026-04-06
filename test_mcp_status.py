"""Test MCP client for checking HFSS status"""
import asyncio
import sys
sys.path.insert(0, '.')

from mcp.client import Client

async def test():
    # Connect to MCP server via stdin/stdout
    import subprocess
    
    server_process = subprocess.Popen(
        [sys.executable, 'hfss_server.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give server time to start
    await asyncio.sleep(1)
    
    print("Server started, testing tools...")
    
    # For now, just check process status
    print("\nHFSS Process Status:")
    import psutil
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if 'ansys' in proc.info['name'].lower():
                print(f"  {proc.info['name']} (PID: {proc.info['pid']})")
        except:
            pass
    
    print("\nNote: MCP server is running but we need to connect via MCP protocol")
    print("Use MCP Inspector or Claude Desktop to interact with the server")
    
    # Clean up
    server_process.terminate()

asyncio.run(test())
