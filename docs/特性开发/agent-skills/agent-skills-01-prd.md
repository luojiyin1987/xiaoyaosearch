# Agent Skill：小遥搜索 MCP 能力

> **文档类型**：Agent Skill 特性PRD
> **基础版本**：基于 [MCP 技术方案](../mcp/mcp-03-技术方案.md)
> **特性状态**：规划中
> **创建时间**：2026-03-18
> **最后更新**：2026-03-18

---

## 1. 特性概述

### 1.1 定位（一句话）

为 Claude Code 提供小遥搜索的 MCP 工具调用能力，使其能够通过 MCP 协议访问本地文件的语义搜索、全文搜索、图像搜索、语音搜索和混合搜索功能。

### 1.2 背景与动机

- **用户痛点**：
  - 痛点1：Claude Code 缺少本地文件搜索的 AI 工具支持
  - 痛点2：开发者需要手动配置 MCP 服务器才能使用搜索能力
  - 痛点3：缺乏统一的工具调用规范和最佳实践

- **业务价值**：
  - 增强 Claude Code 能力：为 AI 助手提供本地文件搜索能力
  - 简化集成：Claude Code 可直接发现和使用 MCP 工具
  - 统一接口：提供标准化的工具调用规范

- **技术必要性**：
  - 小遥搜索已实现 5 个 MCP 工具（BGE-M3、Whoosh、CN-CLIP、FasterWhisper）
  - MCP 协议支持工具自动发现
  - 需要通过 Agent Skill 规范工具调用方式

### 1.3 目标用户

- **主要用户**：
  - Claude Code 用户
  - 需要本地文件搜索能力的 AI 助手
  - MCP 协议集成开发者

- **使用场景**：
  - Claude Code 询问本地文档内容时自动调用搜索
  - AI 助手需要搜索本地文件获取上下文
  - 通过语音/图片搜索本地文件

### 1.4 与主版本的关系

- **依赖关系**：
  - 依赖 MCP 服务器实现（backend/app/mcp/）
  - 依赖 FastAPI SSE 端点（/mcp/sse）
  - 依赖现有搜索服务（ChunkSearchService、ImageSearchService）

- **影响范围**：
  - 新增 `.claude/skills/xiaoyao-search/` 目录
  - 新增 Skill 文档和工具定义文件

---

## 2. 增量需求

### 2.1 功能变更清单

#### 新增功能

| 功能点 | 优先级 | 影响范围 | 说明 |
|-------|-------|---------|------|
| xiaoyao-search Skill 主文件 | P0 | Agent Skill | 定义 Skill 名称、描述、可用的 MCP 工具列表 |
| MCP 工具定义文件 | P0 | Agent Skill | 定义 5 个 MCP 工具的调用规范 |
| 连接配置规则 | P0 | Agent Skill | 指导如何连接小遥搜索 MCP 服务器 |
| 工具使用示例 | P0 | Agent Skill | 提供各工具的调用示例 |

---

## 3. 核心功能（Agent Skill 能力）

### 3.1 可用 MCP 工具

小遥搜索 MCP 服务器提供以下 5 个工具：

| 工具名称 | 功能 | AI 模型 | 参数 |
|---------|------|---------|------|
| semantic_search | 语义搜索 | BGE-M3 | query, limit, threshold, file_types |
| fulltext_search | 全文搜索 | Whoosh | query, limit, file_types |
| hybrid_search | 混合搜索 | BGE-M3 + Whoosh | query, limit, threshold, file_types |
| image_search | 图像搜索 | CN-CLIP | image_path, limit, threshold |
| voice_search | 语音搜索 | FasterWhisper | audio_path, search_type, limit, threshold |

### 3.2 连接配置

**MCP SSE 端点**: `http://127.0.0.1:8000/mcp`

**Claude Code 配置示例**:
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

---

## 4. Skill 文件设计

### 4.1 Skill 主文件

**文件**: `.claude/skills/xiaoyao-search/SKILL.md`

```yaml
---
name: xiaoyao-search
description: 小遥搜索 MCP 工具 - 本地文件智能搜索（语义/全文/图像/语音/混合搜索）
metadata:
  tags: mcp, search, local-files, semantic-search, vector-search, ai-tools
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
  - query: 搜索关键词（1-500字符）
  - limit: 返回结果数（1-100，默认20）
  - threshold: 相似度阈值（0.0-1.0，默认0.7）
  - file_types: 文件类型过滤（可选）

### 2. fulltext_search（全文搜索）
- **用途**：基于 Whoosh 的精确关键词匹配
- **适用**：查找特定术语、代码片段
- **参数**：
  - query: 搜索关键词（1-500字符）
  - limit: 返回结果数（1-100，默认20）
  - file_types: 文件类型过滤（可选）

### 3. hybrid_search（混合搜索）
- **用途**：结合语义和全文搜索，RRF 算法融合结果
- **适用**：需要全面搜索结果的场景
- **参数**：
  - query: 搜索关键词（1-500字符）
  - limit: 返回结果数（1-100，默认20）
  - threshold: 相似度阈值（0.0-1.0，默认0.7）
  - file_types: 文件类型过滤（可选）

### 4. image_search（图像搜索）
- **用途**：基于 CN-CLIP 的图像相似度搜索
- **适用**：用图片查找相似的本地文件
- **参数**：
  - image_path: 图片绝对路径（如 C:/Users/test/pic.jpg）
  - limit: 返回结果数（1-100，默认20）
  - threshold: 相似度阈值（0.0-1.0，默认0.7）

### 5. voice_search（语音搜索）
- **用途**：FasterWhisper 语音识别后搜索
- **适用**：通过语音快速搜索本地文件
- **参数**：
  - audio_path: 音频绝对路径（如 C:/Users/test/voice.mp3）
  - search_type: 搜索类型（semantic/fulltext/hybrid，默认semantic）
  - limit: 返回结果数（1-100，默认20）
  - threshold: 相似度阈值（0.0-1.0，默认0.7）

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
  threshold=0.7
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
- 查看 /mcp/sse 端点是否可访问

### 问题2：搜索结果为空
- 确认索引已构建
- 检查查询词是否正确
- 降低 threshold 值尝试

### 问题3：图像/语音搜索失败
- 确认文件路径为绝对路径
- 检查文件格式是否支持
- 检查文件大小是否在限制内（10MB）

---

## 5. 技术方案

### 5.1 Skill 目录结构

```
.claude/skills/
└── xiaoyao-search/                     # Skill 名称
    ├── SKILL.md                        # Skill 主文件（必需）
    └── rules/                          # 规则目录（可选）
        ├── tools.md                    # MCP 工具详细定义
        ├── connection.md                # 连接配置指南
        └── examples.md                 # 使用示例
```

### 5.2 实施计划

| 步骤 | 内容 | 预计时间 |
|------|------|----------|
| 1 | 创建 Skill 目录 | 0.5小时 |
| 2 | 编写 SKILL.md 主文件 | 1小时 |
| 3 | 编写 tools.md 工具定义 | 1小时 |
| 4 | 编写 connection.md 连接配置 | 0.5小时 |
| 5 | 编写 examples.md 使用示例 | 1小时 |

---

## 6. 验收标准

### 6.1 功能验收

- [ ] Skill 主文件格式正确，包含必要元数据
- [ ] 5 个 MCP 工具定义完整
- [ ] 连接配置说明清晰
- [ ] 使用示例可直接使用

### 6.2 内容验收

- [ ] 包含所有工具的参数说明
- [ ] 包含响应格式说明
- [ ] 包含故障排查指南
- [ ] 包含代码示例

---

## 7. 变更历史

| 版本 | 日期 | 变更内容 | 变更人 | 审核人 |
|-----|------|---------|-------|-------|
| v1.0 | 2026-03-18 | 初始版本，创建小遥搜索 MCP Agent Skill | AI助手 | 用户 |

---

## 8. 相关文档

### 8.1 MCP 实现文档

- [MCP 技术方案](../mcp/mcp-03-技术方案.md) - MCP 技术实现
- [MCP 开发任务清单](../mcp/mcp-04-开发任务清单.md) - 开发任务分解

### 8.2 参考资源

- [MCP 协议规范](https://modelcontextprotocol.io/specification/2025-11-25/)
- [fastmcp 官方文档](https://github.com/PrefectHQ/fastmcp)

---

**文档版本**：v1.0
**创建时间**：2026-03-18
**维护者**：AI助手
