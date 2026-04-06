#!/usr/bin/env python3
"""MCP 客户端测试"""
import asyncio
import json
from hfss_server import app

async def test_client():
    from mcp.server.stdio import stdio_server
    
    messages = []
    
    async def read_input():
        # 初始化请求
        init_req = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        }
        print(json.dumps(init_req), flush=True)
        messages.append(init_req)
        
        # initialized 通知
        init_notify = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        print(json.dumps(init_notify), flush=True)
        messages.append(init_notify)
        
        # tools/list 请求
        list_req = {
            "jsonrpc": "2.0",
            "id": "2",
            "method": "tools/list",
            "params": {}
        }
        print(json.dumps(list_req), flush=True)
        messages.append(list_req)
    
    # 运行 MCP 服务器
    import sys
    from mcp.server import Server
    
    read_stream = asyncio.StreamReader()
    write_stream = asyncio.StreamWriter
    
    # 读取输入
    await read_input()
    
    # 运行服务器
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(test_client())
