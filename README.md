
# HFSS MCP Server

基于 Model Context Protocol (MCP) 的 ANSYS HFSS 自动化服务器，支持持久化 HFSS 连接。

## 目录说明

- `hfss_server.py`：主服务端代码，负责 MCP 协议、HFSS 会话管理、日志、异常处理等。
- `tee_waveguide*.py`：实验/测试脚本，仅供开发调试，不纳入主支持和维护范围。

## 功能特性

- 🔌 **持久化连接** - HFSS 连接在多次调用间保持不断开
- 🚀 **MCP 协议兼容** - 可与支持 MCP 的 AI 助手集成
- 📦 **常用工具** - 创建工程、建模、保存项目等
- 🎯 **会话管理** - 支持多项目切换和会话恢复

## 快速开始

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

---

## 未来扩展功能（PyAEDT 支持方向）

### 1. 建模与几何操作
- `hfss_create_cylinder`：创建圆柱体
- `hfss_create_sphere`：创建球体
- `hfss_create_polyline`：创建多段线/拉伸/扫掠
- `hfss_unite`：布尔合并对象
- `hfss_subtract`：布尔减法
- `hfss_intersect`：布尔交集

### 2. 端口与边界条件
- `hfss_assign_wave_port`：分配波导端口
- `hfss_assign_lumped_port`：分配集总端口
- `hfss_assign_boundary`：分配PEC/PMC/Radiation等边界

### 3. 变量与参数化
- `hfss_list_variables`：列出所有设计变量
- `hfss_set_variable`：设置/修改变量
- `hfss_delete_variable`：删除变量
- `hfss_parameter_sweep`：参数扫描与批量仿真

### 4. 仿真控制
- `hfss_create_setup`：创建/配置仿真设置
- `hfss_run_analysis`：运行仿真
- `hfss_batch_solve`：批量仿真任务

### 5. 结果与后处理
- `hfss_get_s_parameters`：提取 S 参数
- `hfss_export_field_plot`：导出场分布图片/数据
- `hfss_export_report`：导出报告/曲线/表格

### 6. 项目与设计管理
- `hfss_list_projects`：列出所有工程
- `hfss_import_project`：导入工程
- `hfss_export_project`：导出工程
- `hfss_rename_project`：重命名工程
- `hfss_delete_project`：删除工程

### 7. 高级与自动化
- 自动错误恢复与重连
- 日志与异常追踪增强
- 复杂流程自动化脚本支持

---
如需优先实现上述某项功能，请在 issue 或开发计划中标注。

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

## 开发与维护说明

- **主支持文件**：仅 `hfss_server.py` 作为主服务端代码，建议所有新功能、性能优化、日志改进等均在此文件实现。
- **实验脚本**：`tee_waveguide*.py` 仅为开发实验用途，不纳入正式维护和文档管理。

## 日志改进建议

- 推荐统一使用 `logging` 标准库，设置合理的日志级别（INFO/DEBUG/ERROR），并输出到文件和控制台。
- 日志格式建议包含时间、模块、级别、消息，便于排查问题。
- 关键操作（如会话创建、关闭、异常、外部调用）应有详细日志。
- 可考虑增加日志轮转（如 `logging.handlers.RotatingFileHandler`）。

## 贡献与开发规范

- 代码需包含必要的注释和类型标注，便于后续维护。
- 建议为核心功能补充单元测试（可用 pytest）。
- 重要变更请在本 README 或代码注释中说明。

---
如需扩展功能、性能优化或日志增强，请直接修改 `hfss_server.py` 并遵循上述规范。

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
