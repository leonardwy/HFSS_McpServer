# HFSS MCP Server

基于 Model Context Protocol (MCP) 的 ANSYS HFSS 自动化服务器，支持持久化 HFSS 连接。

## 功能特性

- 🔌 **持久化连接** - HFSS 连接在多次调用间保持不断开
- 🚀 **MCP 协议兼容** - 可与支持 MCP 的 AI 助手集成
- 📦 **常用工具** - 创建工程、建模、保存项目等
- 🎯 **会话管理** - 支持多项目切换和会话恢复

## 快速开始

### 前置要求

- ANSYS HFSS 2024 R2 或更高版本
- Python 3.9+
- ansys-aedt-core (`pip install ansys-aedt-core`)
- mcp (`pip install mcp`)

### 安装

```bash
pip install ansys-aedt-core mcp
```

### 配置 MCP (VS Code / Cursor / Claude Desktop)

#### VS Code 配置
1. 打开设置 → 搜索 "MCP" → 点击 "Edit in settings.json"
2. 或直接编辑 `C:/Users/<用户名>/AppData/Roaming/Code/User/mcp.json`：

```json
{
  "servers": {
    "hfss": {
      "command": "python",
      "args": ["e:/project/GitHub/HFSS_McpServer/HFSS_McpServer/hfss_server.py"],
      "type": "stdio"
    }
  },
  "inputs": []
}
```

#### Cursor / Claude Desktop 配置
在对应的 MCP 配置文件中添加：

```json
{
  "mcpServers": {
    "hfss": {
      "command": "python",
      "args": ["d:/hfss_mcp/hfss_server.py"]
    }
  }
}
```

### 使用方法

1. 先启动 HFSS（打开任意工程或空白界面）
2. 在 VS Code 中重新加载窗口（Ctrl+Shift+P → Reload Window）
3. MCP 服务器将自动连接
4. 开始使用工具调用

## 测试验证

### 手动测试 MCP 服务器

可以通过命令行直接测试 MCP 协议：

```bash
cd e:/project/GitHub/HFSS_McpServer/HFSS_McpServer
python hfss_server.py
```

测试请求文件格式：

```json
{"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}
{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"hfss_start_app","arguments":{}}}
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"hfss_get_session_status","arguments":{}}}
```

保存为 `test_mcp.txt`，然后运行：
```bash
type test_mcp.txt | python hfss_server.py
```

### 测试结果示例

成功连接后会显示：
```
=== HFSS Session Status ===

Current Design:
  Project: Project1
  Design: HFSSDesign1
  Solution Type: Terminal
  Objects: 0

All Designs in Project1:
  - HFSSDesign1 [CURRENT]

Project Path: E:/documant/Ansoft/
```

### 技术细节

- **PyAEDT 版本**: 0.25.1+
- **AEDT 版本**: 2026.1
- **连接方式**: gRPC (端口 50051)
- **协议版本**: MCP 2024-11-05
- **会话持久化**: 自动保存状态到 `hfss_session_state.json`

## 可用工具

| 工具名称 | 描述 |
|---------|------|
| `hfss_start_app` | 连接现有 HFSS 应用 |
| `hfss_launch_app` | 启动新的 HFSS 应用 |
| `hfss_create_project` | 创建新工程 |
| `hfss_create_box` | 创建长方体模型 |
| `hfss_list_objects` | 列出所有模型对象 |
| `hfss_get_object_info` | 获取指定对象的详细信息（类型、材质、边界盒、体积） |
| `hfss_save_project` | 保存当前工程 |
| `hfss_get_session_status` | 获取会话状态 |
| `hfss_get_messages` | 获取 HFSS 日志消息 |
| `hfss_stop_app` | 停止 HFSS 应用 |

## 项目结构

```
hfss_mcp/
├── hfss_server.py      # MCP 服务器主程序
├── mcp_config.json     # MCP 配置示例
├── test_*.py           # 测试脚本
├── debug_*.py          # 调试脚本
└── README.md
```

## 工作原理

1. MCP 服务器启动时，在导入 PyAEDT 之前禁用 `atexit.register`
2. 这可以防止 Python 退出时释放 HFSS Desktop
3. HFSS 连接通过 gRPC 保持活跃
4. 每次工具调用复用同一连接

## 故障排除

**Q: 每次调用后 HFSS 连接断开？**
A: 确保在导入 `ansys.aedt.core` **之前**禁用 atexit.register

**Q: 找不到 HFSS 进程？**
A: 确保 HFSS 应用程序已经在运行（打开任意工程）

## License

MIT
