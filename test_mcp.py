#!/usr/bin/env python3
"""MCP 服务器测试脚本"""
import asyncio
import json
import sys
from hfss_server import app

async def test_mcp():
    from mcp.server.stdio import stdio_server
    
    async def send_message(msg):
        print(json.dumps(msg), flush=True)
    
    # 初始化请求
    init_request = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0"}
        }
    }
    
    print(f"Sending: {init_request}", file=sys.stderr)
    await send_message(init_request)
    
    # 等待响应
    # ...
    
    print("Test completed", file=sys.stderr)

if __name__ == "__main__":
    asyncio.run(test_mcp())
