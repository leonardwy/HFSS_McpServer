# HFSS 自动建模知识库使用指南

## 概述

本项目为 HFSS MCP Server 集成了一套自动化"文档→知识库→建模决策"流程，支持你在自动建模时：
1. **智能检索**：按建模问题查询相关规则和经验
2. **实时建议**：获取官方文档背后的最佳实践映射
3. **参数决策**：基于知识库推荐优化建模参数

## 快速开始

### 步骤 1：构建知识库

如果你已有 ANSYS ProductDocPDF，一条命令生成本地知识库：

```bash
cd e:/project/GitHub/HFSS_McpServer/HFSS_McpServer
python quickstart.py build
```

或使用更细粒度的参数：

```bash
python scripts/build_hfss_kb.py \
  --doc-root "E:/download/ANSYS2026R1/ANSYS2026R1_ProductDocPDF/v261" \
  --output "hfss_modeling_knowledge_base.json" \
  --max-files 150
```

**输出**：
- `hfss_modeling_knowledge_base.json`（~5-10 MB）
- 包含提取的关键段落、标签和建议

### 步骤 2：检查知识库状态

```bash
python quickstart.py status
```

输出示例：
```
[+] HFSS Modeling Knowledge Base Status
    Generated at: 2026-05-18T21:02:43
    Source root: E:\download\ANSYS2026R1\ANSYS2026R1_ProductDocPDF\v261
    Scanned files: 41
    Total entries: 250
    Tags in use:
      - 参数化与扫描
      - 求解类型与设置
      - 网格与收敛
      - 端口激励设置
      - 辐射边界与计算域
      - 通用HFSS建模
```

### 步骤 3：启动 MCP 服务器

```bash
python quickstart.py server
```

或直接：

```bash
python hfss_server.py
```

## MCP 工具使用

### 1. 查询建模知识

调用 `hfss_query_modeling_knowledge` 工具：

**输入示例**：
```json
{
  "query": "wave port setup for coaxial feed",
  "top_k": 5
}
```

**输出示例**：
```
[OK] HFSS modeling knowledge hits for query: wave port setup for coaxial feed

1. Solder_Fatigue_Analysis_Using_Sherlock_and_AEDT_Icepak.pdf - p15
   Source: Solder_Fatigue_Analysis_Using_Sherlock_and_AEDT_Icepak.pdf
   Tags: 求解类型与设置, 网格与收敛
   Summary: 该页包含与求解类型与设置相关的HFSS/AEDT关键词，可用于自动建模决策。
   Recommendation: 根据结构和目标选择求解类型；端口网络问题优先 Driven 模式，并在 setup 中配置自适应与频率点。
   
2. ACT_Customization_Guide_for_Electronics_Desktop.pdf - p8
   Source: ACT_Customization_Guide_for_Electronics_Desktop.pdf
   Tags: 参数化与扫描
   Summary: 该页包含与参数化与扫描相关的HFSS/AEDT关键词，可用于自动建模决策。
   Recommendation: 把关键几何和材料参数变量化，再配置频率扫和参数扫，保证自动建模后可直接用于优化。
...
```

### 2. 查看知识库状态

调用 `hfss_get_modeling_knowledge_status` 工具：

**输入**：
```json
{}
```

**输出**：
```
[OK] HFSS modeling knowledge base status
Entries: 250
Source root: E:\download\ANSYS2026R1\ANSYS2026R1_ProductDocPDF\v261
Scanned files: 41
Generated at: 2026-05-18T21:02:43
```

## 建模工作流建议

### 完整的自动建模流程示例

假设你要自动生成一个 **微带贴片天线** 模型：

#### 1. 知识查询阶段
```python
# 查询"微带天线"相关规则
query = "microstrip antenna substrate port placement"
hits = mcp.call_tool("hfss_query_modeling_knowledge", 
                     query=query, top_k=5)

# 查询"网格策略"
query = "mesh convergence frequency sweep"
hits = mcp.call_tool("hfss_query_modeling_knowledge", 
                     query=query, top_k=3)
```

#### 2. 几何建模阶段
基于知识库建议，创建几何：

```python
# 创建介质板
substrate_material = "Rogers_4003"
mcp.call_tool("hfss_create_box", 
              center_position=[0, 0, -thickness/2],
              dimensions=[length, width, thickness],
              material=substrate_material,
              name="Substrate")

# 创建馈电口贴片
mcp.call_tool("hfss_create_box",
              center_position=[feed_x, feed_y, 0],
              dimensions=[patch_length, patch_width, copper_thickness],
              material="Copper",
              name="PatchAntenna")

# 创建空气包络
mcp.call_tool("hfss_create_box",
              center_position=[0, 0, 0],
              dimensions=[airbox_x, airbox_y, airbox_z],
              name="AirBox")
```

#### 3. 激励与边界条件
根据知识库 "端口激励设置" 和 "辐射边界与计算域" 标签：

```python
# 添加馈电端口（根据建议选择 wave port）
mcp.call_tool("hfss_assign_wave_port",
              object_name="Substrate",
              face_id=10,  # 贴片下表面
              port_name="FeedPort")

# 在空气包络外表面添加辐射边界
mcp.call_tool("hfss_assign_radiation_boundary",
              object_name="AirBox",
              face_id=[1, 2, 3, 4, 5, 6],  # 6个面
              boundary_name="Radiation_Outer")
```

#### 4. 求解设置
基于知识库 "求解类型与设置" 标签：

```python
# 创建 Driven Modal 求解器（适合端口激励）
mcp.call_tool("hfss_create_setup",
              setup_name="S11_Sweep",
              frequency="10GHz")

# 参数化扫描
mcp.call_tool("hfss_set_variable",
              name="freq_center", 
              value="5GHz")

mcp.call_tool("hfss_set_variable",
              name="freq_span",
              value="5GHz")
```

#### 5. 运行与验证

```python
# 运行仿真
mcp.call_tool("hfss_run_analysis", 
              setup_name="S11_Sweep")

# 提取 S 参数
mcp.call_tool("hfss_get_s_parameters",
              setup_name="S11_Sweep")
```

## 知识库标签说明

| 标签 | 适用场景 | 核心建议 |
|-----|--------|--------|
| **端口激励设置** | 馈电结构设计 | 波导/同轴优先 wave port；集总馈电 lumped port；必要时设置 de-embed |
| **辐射边界与计算域** | 开放辐射问题 | 先创建空气包络，再在外表面赋予 Radiation 或 PML 边界 |
| **求解类型与设置** | 仿真参数 | 端口网络问题优先 Driven 模式；本征模优先 Eigenmode；配置自适应与频率点 |
| **网格与收敛** | 网格策略 | 依赖自适应网格；关键缝隙、馈点、薄介质附近增加局部网格关注 |
| **参数化与扫描** | 设计优化 | 把关键几何和材料参数变量化；配置频率扫和参数扫；保证可直接用于优化 |

## 知识库文件格式

```json
{
  "metadata": {
    "generated_at": "2026-05-18T21:02:43",
    "source_root": "E:\\download\\ANSYS2026R1\\ANSYS2026R1_ProductDocPDF\\v261",
    "scanned_files": 41,
    "matched_chunks": 468,
    "entry_count": 250,
    "note": "Automatically extracted from local ANSYS PDFs..."
  },
  "entries": [
    {
      "title": "PDF_Name - pNN",
      "source": "PDF_Name.pdf",
      "page": 15,
      "tags": ["标签1", "标签2"],
      "summary": "该页包含与标签1相关的HFSS/AEDT关键词...",
      "recommendation": "建议行动：...",
      "raw_excerpt": "原始文本片段...",
      "score": 3
    },
    ...
  ]
}
```

## 故障排查

### 知识库构建失败

**问题**：`pypdf` 未安装
```
Missing dependency 'pypdf'. Install with: pip install pypdf
```

**解决**：
```bash
pip install pypdf
```

**问题**：文档目录不存在或路径错误
```
Invalid doc root: E:/download/...
```

**解决**：修改 `quickstart.py` 中的 `DOC_ROOT` 变量或使用 `--doc-root` 参数指定正确路径。

### 知识库为空或条目太少

**可能原因**：
1. 提供的 PDF 文件与 HFSS/AEDT 无关
2. 筛选规则过严格

**解决**：
- 检查 `--max-files` 参数，增大扫描范围
- 在 `scripts/build_hfss_kb.py` 中调整 `HFSS_CORE_KEYWORDS` 或 `HFSS_MODELING_KEYWORDS`
- 手动添加高价值条目到知识库 JSON

### 查询结果不相关

**可能原因**：
知识库使用简单的关键词匹配，对于复杂语义的查询可能不够精确。

**改进建议**：
1. 简化查询，使用核心关键词（如 "wave port" 而非 "how to assign wave port"）
2. 多次查询不同的关键词组合
3. 参考返回的 URL 和页码，在原 PDF 中查看完整上下文

## 进阶用法

### 自定义知识库条目

直接编辑 `hfss_modeling_knowledge_base.json` 中的 `entries` 数组，添加自己的最佳实践：

```json
{
  "title": "Custom Best Practice: PCB Stack-up",
  "source": "Internal Wiki",
  "page": 0,
  "tags": ["参数化与扫描", "端口激励设置"],
  "summary": "PCB 堆叠设计的标准流程",
  "recommendation": "在 HFSS 3D Layout 中先定义 PCB 层堆叠，再从 CAD 导入器件；馈电孔必须穿过所有介质层。",
  "raw_excerpt": "PCB stack-up checklist: ...",
  "score": 5
}
```

### 集成到自动建模脚本

```python
import json
from pathlib import Path

def get_modeling_advice(topic: str):
    kb_path = Path("hfss_modeling_knowledge_base.json")
    with kb_path.open("r", encoding="utf-8") as f:
        kb = json.load(f)
    
    hits = [e for e in kb["entries"] 
            if topic.lower() in str(e.get("tags", "")).lower()]
    
    for hit in hits[:3]:
        print(f"Recommendation: {hit['recommendation']}")
        print(f"Source: {hit['source']} p{hit['page']}\n")

# 使用
get_modeling_advice("microstrip")
```

## 后续计划

- [ ] **向量化检索**：用 embedding 模型替代关键词匹配，支持语义相似度检索
- [ ] **知识库版本管理**：支持多个 ANSYS 版本的知识库并行维护
- [ ] **AI 增强总结**：用 LLM 对 PDF 段落进行结构化总结和重新分类
- [ ] **自动工具映射**：根据查询结果自动推荐相应的 MCP 工具调用序列
- [ ] **反馈机制**：收集用户的建模结果反馈，优化知识库质量

## 参考资源

- [HFSS MCP Server README](./README.md)
- [HFSS_MCP_EXPERIENCE.md](./HFSS_MCP_EXPERIENCE.md) - 已知问题和 workaround
- [ANSYS AEDT 官方文档](https://www.ansys.com/)

## 许可与免责

本知识库由官方 ANSYS 文档自动提取，仅供参考。关键建模决策应遵循官方文档和技术支持建议。

---

**最后更新**：2026-05-18
**版本**：1.0-beta
