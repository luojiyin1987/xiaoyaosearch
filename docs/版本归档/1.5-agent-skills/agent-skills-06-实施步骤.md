# Agent Skill：小遥搜索 MCP 能力 - 实施步骤

> **文档类型**：实施步骤
> **特性状态**：待开始
> **创建时间**：2026-03-18
> **预计工期**：4 小时
> **关联文档**：[Agent Skill PRD](./agent-skills-01-prd.md) | [Agent Skill 技术方案](./agent-skills-03-技术方案.md) | [Agent Skill 实施方案](./agent-skills-实施方案.md)

---

## 📋 实施概览

| 阶段 | 任务 | 预计时间 | 优先级 |
|------|------|----------|--------|
| 1️⃣ 创建目录 | Skill 目录结构创建 | 0.5 小时 | P0 |
| 2️⃣ SKILL.md | 主文件编写 | 1 小时 | P0 |
| 3️⃣ 规则文件 | 详细规则编写 | 2 小时 | P0 |
| 4️⃣ 验证测试 | 格式验证和测试 | 0.5 小时 | P0 |
| **总计** | | **4 小时** | |

---

## 阶段 1：创建目录（0.5 小时）

### 1.1 创建 Skill 目录

**执行命令**：

```bash
# 在项目根目录创建 Skill 目录
mkdir -p skills/xiaoyao-search/rules
```

**验证目录结构**：

```
skills/xiaoyao-search/
└── rules/                       # 空目录，等待创建文件
```

---

## 阶段 2：SKILL.md 主文件（1 小时）

### 2.1 创建 SKILL.md

**文件路径**：`skills/xiaoyao-search/SKILL.md`

**完整内容**：

```markdown
---
name: xiaoyao-search
description: 小遥搜索 MCP 工具 - 本地文件智能搜索（语义/全文/图像/语音/混合搜索）
metadata:
  tags: mcp, search, local-files, semantic-search, vector-search, ai-tools
  version: 1.0.0
  author: xiaoyao-search
---

## When to use

当需要搜索本地文件时使用此 Skill：

- 通过自然语言描述搜索本地文档
- 查找包含特定关键词的文件
- 用图片搜索相似的本地图片
- 用语音转文字后搜索文件
- 需要综合语义和全文搜索结果

## Capability

小遥搜索 MCP 服务器提供以下 5 个搜索工具：

### 1. semantic_search（语义搜索）
- **用途**：基于 BGE-M3 向量模型的语义搜索
- **适用**：自然语言查询，如"关于机器学习的文档"
- **参数**：
  - `query`: string - 搜索关键词（1-500字符）
  - `limit`: int - 返回结果数（1-100，默认20）
  - `threshold`: float - 相似度阈值（0.0-1.0，默认0.7）
  - `file_types`: string[] - 文件类型过滤（可选）

### 2. fulltext_search（全文搜索）
- **用途**：基于 Whoosh 的精确关键词匹配
- **适用**：查找特定术语、代码片段
- **参数**：
  - `query`: string - 搜索关键词（1-500字符）
  - `limit`: int - 返回结果数（1-100，默认20）
  - `file_types`: string[] - 文件类型过滤（可选）

### 3. hybrid_search（混合搜索）
- **用途**：结合语义和全文搜索，RRF 算法融合结果
- **适用**：需要全面搜索结果的场景
- **参数**：
  - `query`: string - 搜索关键词（1-500字符）
  - `limit`: int - 返回结果数（1-100，默认20）
  - `threshold`: float - 相似度阈值（0.0-1.0，默认0.7）
  - `file_types`: string[] - 文件类型过滤（可选）

### 4. image_search（图像搜索）
- **用途**：基于 CN-CLIP 的图像相似度搜索
- **适用**：用图片查找相似的本地文件
- **参数**：
  - `image_path`: string - 图片绝对路径
  - `limit`: int - 返回结果数（1-100，默认20）
  - `threshold`: float - 相似度阈值（0.0-1.0，默认0.7）

### 5. voice_search（语音搜索）
- **用途**：FasterWhisper 语音识别后搜索
- **适用**：通过语音快速搜索本地文件
- **参数**：
  - `audio_path`: string - 音频绝对路径
  - `search_type`: string - 搜索类型（semantic/fulltext/hybrid，默认semantic）
  - `limit`: int - 返回结果数（1-100，默认20）
  - `threshold`: float - 相似度阈值（0.0-1.0，默认0.7）

## Usage

### 前提条件

1. 小遥搜索后端服务已启动（默认 http://127.0.0.1:8000）
2. MCP 功能已启用（默认启用）
3. 索引已构建完成

### 调用方式

Claude Code 通过 MCP 协议自动发现和调用工具：

```
用户：帮我找一下关于 Python 异步编程的文档
→ Claude Code 调用 semantic_search(query="Python 异步编程")
→ 返回搜索结果
→ Claude 基于结果回答用户
```

### 响应格式

搜索结果返回 JSON 格式：
```json
{
  "total": 10,
  "search_time": 0.523,
  "results": [
    {
      "file_name": "async_guide.md",
      "file_path": "D:/docs/async_guide.md",
      "file_type": "markdown",
      "relevance_score": 0.95,
      "preview_text": "Python异步编程指南..."
    }
  ]
}
```

## Examples

### 示例1：语义搜索
```
用户：查找关于机器学习算法优化的文档

调用：semantic_search(
  query="机器学习算法优化",
  limit=10,
  threshold=0.5
)
```

### 示例2：全文搜索
```
用户：查找包含 async def 的 Python 文件

调用：fulltext_search(
  query="async def",
  limit=20,
  file_types=["python"]
)
```

### 示例3：图像搜索
```
用户：找一下跟这张图片相似的设计稿

调用：image_search(
  image_path="C:/Users/test/reference.png",
  limit=10
)
```

### 示例4：语音搜索
```
用户：（语音输入）帮我找一下上周的会议记录

调用：voice_search(
  audio_path="C:/Users/test/voice.mp3",
  search_type="semantic"
)
```

### 示例5：混合搜索
```
用户：全面搜索关于 Vue3 组件开发的资料

调用：hybrid_search(
  query="Vue3 组件开发",
  limit=20,
  threshold=0.6
)
```

## Configuration

### 环境变量

| 变量名 | 默认值 | 说明 |
|-------|--------|------|
| MCP_SSE_ENABLED | true | 启用 MCP SSE |
| MCP_SERVER_NAME | xiaoyao-search | 服务器名称 |
| MCP_DEFAULT_LIMIT | 20 | 默认结果数 |
| MCP_DEFAULT_THRESHOLD | 0.7 | 默认相似度阈值 |
| MCP_VOICE_ENABLED | true | 启用语音搜索 |

### 连接测试

```bash
# 测试 MCP SSE 端点
curl http://127.0.0.1:8000/mcp

# 检查后端健康状态
curl http://127.0.0.1:8000/api/system/health
```

## Troubleshooting

### 问题1：工具调用失败
- 检查后端服务是否启动
- 确认 MCP_SSE_ENABLED=true
- 查看 /mcp 端点是否可访问

### 问题2：搜索结果为空
- 确认索引已构建
- 检查查询词是否正确
- 降低 threshold 值尝试

### 问题3：图像/语音搜索失败
- 确认文件路径为绝对路径
- 检查文件格式是否支持
- 检查文件大小是否在限制内（10MB）
```

### 2.2 验证 SKILL.md

- [ ] YAML frontmatter 格式正确
- [ ] name 与目录名一致
- [ ] 5 个工具定义完整
- [ ] Markdown 语法正确

---

## 阶段 3：规则文件（2 小时）

### 3.1 创建 tools.md

**文件路径**：`skills/xiaoyao-search/rules/tools.md`

```markdown
# MCP 工具详细定义

本文档详细定义小遥搜索 MCP 服务器提供的 5 个搜索工具。

## 1. semantic_search

### 功能描述

基于 BGE-M3 向量模型的语义搜索，支持自然语言查询理解。

### 适用场景

- 用自然语言描述搜索内容
- 需要理解查询意图
- 查找语义相关的文档

### 参数定义

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| query | string | 是 | - | 搜索关键词（1-500字符） |
| limit | int | 否 | 20 | 返回结果数量（1-100） |
| threshold | float | 否 | 0.7 | 相似度阈值（0.0-1.0） |
| file_types | string[] | 否 | null | 文件类型过滤 |

### 返回格式

```json
{
  "total": 10,
  "search_time": 0.523,
  "results": [
    {
      "file_name": "example.md",
      "file_path": "D:/docs/example.md",
      "file_type": "markdown",
      "relevance_score": 0.95,
      "preview_text": "文档预览..."
    }
  ]
}
```

### 错误处理

| 错误码 | 说明 |
|--------|------|
| query 长度超限 | 返回 400 错误 |
| limit 超出范围 | 返回 400 错误 |

---

## 2. fulltext_search

### 功能描述

基于 Whoosh 的全文搜索，支持精确关键词匹配和中文分词。

### 适用场景

- 查找特定关键词
- 搜索代码片段
- 精确短语匹配

### 参数定义

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| query | string | 是 | - | 搜索关键词（1-500字符） |
| limit | int | 否 | 20 | 返回结果数量（1-100） |
| file_types | string[] | 否 | null | 文件类型过滤 |

---

## 3. hybrid_search

### 功能描述

结合语义搜索和全文搜索，使用 RRF 算法融合结果。

### 适用场景

- 需要全面搜索结果
- 不确定使用哪种搜索方式
- 希望获得更准确的排序

### 参数定义

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| query | string | 是 | - | 搜索关键词（1-500字符） |
| limit | int | 否 | 20 | 返回结果数量（1-100） |
| threshold | float | 否 | 0.7 | 相似度阈值（0.0-1.0） |
| file_types | string[] | 否 | null | 文件类型过滤 |

---

## 4. image_search

### 功能描述

基于 CN-CLIP 模型的图像搜索，通过图片查找相似内容。

### 适用场景

- 用参考图查找相似图片
- 查找包含相似元素的文档
- 设计素材搜索

### 参数定义

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| image_path | string | 是 | - | 图片绝对路径 |
| limit | int | 否 | 20 | 返回结果数量（1-100） |
| threshold | float | 否 | 0.7 | 相似度阈值（0.0-1.0） |

### 支持格式

- jpg, jpeg, png, gif, bmp, webp

### 文件限制

- 最大：10MB
- 最小：1KB

---

## 5. voice_search

### 功能描述

基于 FasterWhisper 的语音搜索，将语音转为文字后进行搜索。

### 适用场景

- 语音输入搜索
- 快速记录查找
- 会议记录搜索

### 参数定义

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| audio_path | string | 是 | - | 音频绝对路径 |
| search_type | string | 否 | semantic | 搜索类型 |
| limit | int | 否 | 20 | 返回结果数量（1-100） |
| threshold | float | 否 | 0.7 | 相似度阈值（0.0-1.0） |

### search_type 选项

- semantic：语义搜索
- fulltext：全文搜索
- hybrid：混合搜索

### 支持格式

- wav, mp3, m4a, flac, aac, ogg, opus

### 文件限制

- 最大：10MB（约30秒音频）
- 最小：1KB
```

### 3.2 创建 connection.md

**文件路径**：`skills/xiaoyao-search/rules/connection.md`

```markdown
# 连接配置指南

本文档说明如何配置各种 AI 助手连接到小遥搜索 MCP 服务器。

## MCP SSE 端点

**地址**：`http://127.0.0.1:8000/mcp`

## Claude Code / Claude Desktop 配置

### Windows

编辑文件：`%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "xiaoyao-search": {
      "url": "http://127.0.0.1:8000/mcp",
      "type": "sse"
    }
  }
}
```

### macOS

编辑文件：`~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "xiaoyao-search": {
      "url": "http://127.0.0.1:8000/mcp",
      "type": "sse"
    }
  }
}
```

### Linux

编辑文件：`~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "xiaoyao-search": {
      "url": "http://127.0.0.1:8000/mcp",
      "type": "sse"
    }
  }
}
```

## VS Code (with MCP extension)

打开设置，添加以下配置：

```json
{
  "mcpServers": {
    "xiaoyao-search": {
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

## Cursor 配置

编辑 `~/.cursor/settings.json` 或在设置中添加：

```json
{
  "mcpServers": {
    "xiaoyao-search": {
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

## 环境变量配置

在 `backend/.env` 文件中配置：

```bash
# MCP 服务器配置
MCP_SSE_ENABLED=true
MCP_SERVER_NAME=xiaoyao-search
MCP_SERVER_VERSION=1.0.0
MCP_DEFAULT_LIMIT=20
MCP_DEFAULT_threshold=0.5
MCP_VOICE_ENABLED=true
MCP_LOG_LEVEL=INFO
```

## 连接测试

### 测试 1：检查后端服务

```bash
curl http://127.0.0.1:8000/api/system/health
```

预期响应：
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 测试 2：检查 MCP 端点

```bash
curl http://127.0.0.1:8000/mcp
```

预期响应：SSE 连接响应（会保持连接打开）

### 测试 3：检查工具列表

使用 MCP 客户端工具测试：

```bash
# 安装 mcp CLI
pip install mcp[cli]

# 测试服务器
mcp dev python -c "
from app.mcp.server import create_mcp_server
mcp = create_mcp_server()
print([t.name for t in mcp._tools])
"
```

## 故障排查

### 问题：连接失败

1. 确认后端服务正在运行
2. 检查端口 8000 是否被占用
3. 确认防火墙允许访问
4. 检查 URL 是否正确

### 问题：工具不可见

1. 重启 AI 助手
2. 检查 MCP 配置是否保存成功
3. 查看 AI 助手日志
```

### 3.3 创建 examples.md

**文件路径**：`skills/xiaoyao-search/rules/examples.md`

```markdown
# 使用示例

本文档提供小遥搜索 MCP 工具的详细使用示例。

## 示例 1：语义搜索

### 场景

用户想要查找关于"机器学习算法优化"的文档。

### 调用

```python
semantic_search(
    query="机器学习算法优化",
    limit=10,
    threshold=0.5
)
```

### 响应

```json
{
  "total": 10,
  "search_time": 0.523,
  "results": [
    {
      "file_name": "ml_optimization_guide.md",
      "file_path": "D:/docs/ml_optimization_guide.md",
      "file_type": "markdown",
      "relevance_score": 0.95,
      "preview_text": "机器学习算法优化指南..."
    },
    {
      "file_name": "gradient_descent.py",
      "file_path": "D:/code/gradient_descent.py",
      "file_type": "python",
      "relevance_score": 0.89,
      "preview_text": "梯度下降算法实现..."
    }
  ]
}
```

---

## 示例 2：全文搜索代码

### 场景

用户想找包含 `async def` 的 Python 文件。

### 调用

```python
fulltext_search(
    query="async def",
    limit=20,
    file_types=["python"]
)
```

### 响应

```json
{
  "total": 5,
  "search_time": 0.123,
  "results": [
    {
      "file_name": "async_handler.py",
      "file_path": "D:/code/async_handler.py",
      "file_type": "python",
      "relevance_score": 1.0,
      "highlight": "...async def process_request():...",
      "preview_text": "异步请求处理函数..."
    }
  ]
}
```

---

## 示例 3：图像搜索

### 场景

用户有一张参考图片，想要找相似的设计稿。

### 调用

```python
image_search(
    image_path="C:/Users/test/reference.png",
    limit=10
)
```

### 响应

```json
{
  "total": 10,
  "search_time": 1.245,
  "results": [
    {
      "file_name": "design_v1.png",
      "file_path": "D:/design/design_v1.png",
      "file_type": "image",
      "relevance_score": 0.92,
      "preview_text": "设计稿版本1..."
    }
  ],
  "input_info": {
    "file_path": "C:/Users/test/reference.png",
    "file_size_kb": 256.5,
    "file_format": ".png"
  }
}
```

---

## 示例 4：语音搜索

### 场景

用户通过语音输入"帮我找一下上周的会议记录"。

### 调用

```python
voice_search(
    audio_path="C:/Users/test/voice.mp3",
    search_type="semantic"
)
```

### 响应

```json
{
  "total": 3,
  "search_time": 2.567,
  "results": [
    {
      "file_name": "meeting_2024_01_15.md",
      "file_path": "D:/meetings/meeting_2024_01_15.md",
      "file_type": "markdown",
      "relevance_score": 0.88,
      "preview_text": "会议记录..."
    }
  ],
  "transcription": {
    "text": "帮我找一下上周的会议记录",
    "enhanced_query": "上周会议记录",
    "language": "zh",
    "duration": 3.5
  },
  "input_info": {
    "file_path": "C:/Users/test/voice.mp3",
    "file_size_kb": 128.0,
    "file_format": ".mp3"
  }
}
```

---

## 示例 5：混合搜索

### 场景

用户想要全面搜索"Vue3 组件开发"的资料。

### 调用

```python
hybrid_search(
    query="Vue3 组件开发",
    limit=20,
    threshold=0.6
)
```

### 响应

```json
{
  "total": 20,
  "search_time": 0.678,
  "results": [
    {
      "file_name": "vue3_components.md",
      "file_path": "D:/docs/vue3_components.md",
      "file_type": "markdown",
      "relevance_score": 0.95,
      "source": "semantic",
      "preview_text": "Vue3 组件开发指南..."
    },
    {
      "file_name": "Component.vue",
      "file_path": "D:/code/Component.vue",
      "file_type": "vue",
      "relevance_score": 0.92,
      "source": "fulltext",
      "highlight": "...<script setup>...组件...",
      "preview_text": "Vue3 组件示例..."
    }
  ]
}
```

---

## 最佳实践

### 1. 选择合适的搜索类型

| 场景 | 推荐搜索类型 |
|------|-------------|
| 自然语言描述 | semantic_search |
| 精确关键词 | fulltext_search |
| 全面搜索 | hybrid_search |
| 图片参考 | image_search |
| 语音输入 | voice_search |

### 2. 调整阈值

- 高阈值（>0.8）：精确匹配
- 中阈值（0.5-0.8）：平衡
- 低阈值（<0.5）：更多结果

### 3. 文件类型过滤

```python
# 只搜索文档
file_types=["pdf", "doc", "docx", "md", "txt"]

# 只搜索代码
file_types=["py", "js", "ts", "java", "go"]

# 只搜索图片
file_types=["jpg", "png", "gif"]
```
```

---

## 阶段 4：验证测试（0.5 小时）

### 4.1 验证文件结构

**检查命令**：

```bash
# 列出所有文件
ls -la skills/xiaoyao-search/
ls -la skills/xiaoyao-search/rules/
```

**预期结果**：

```
skills/xiaoyao-search/
├── SKILL.md
└── rules/
    ├── tools.md
    ├── connection.md
    └── examples.md
```

### 4.2 验证 YAML 语法

**检查 SKILL.md frontmatter**：

```bash
# 使用 Python 检查 YAML 语法
python -c "import yaml; yaml.safe_load(open('skills/xiaoyao-search/SKILL.md').read().split('---')[1])"
```

### 4.3 验证 Markdown 语法

**使用工具检查**：

```bash
# 安装 markdownlint（可选）
npm install -g markdownlint

# 检查语法
markdownlint skills/xiaoyao-search/
```

---

## ✅ 验收清单

### 文件验收

- [ ] `skills/xiaoyao-search/SKILL.md` 存在
- [ ] `skills/xiaoyao-search/rules/tools.md` 存在
- [ ] `skills/xiaoyao-search/rules/connection.md` 存在
- [ ] `skills/xiaoyao-search/rules/examples.md` 存在

### 内容验收

- [ ] SKILL.md 包含正确的 YAML frontmatter
- [ ] 5 个工具定义完整
- [ ] 连接配置示例完整
- [ ] 使用示例完整

### 格式验收

- [ ] YAML 语法正确
- [ ] Markdown 语法正确
- [ ] 文件编码为 UTF-8

---

## 📝 实施记录

| 日期 | 阶段 | 状态 | 备注 |
|------|------|------|------|
| 2026-03-18 | 阶段1 | 待开始 | 创建目录 |
| 2026-03-18 | 阶段2 | 待开始 | SKILL.md |
| 2026-03-18 | 阶段3 | 待开始 | 规则文件 |
| 2026-03-18 | 阶段4 | 待开始 | 验证测试 |

---

**文档版本**：v1.0
**创建时间**：2026-03-18
**维护者**：AI助手
