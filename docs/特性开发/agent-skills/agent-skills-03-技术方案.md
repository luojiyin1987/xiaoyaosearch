# Agent Skill：小遥搜索 MCP 能力 - 技术方案

> **文档类型**：技术方案
> **特性状态**：规划中
> **创建时间**：2026-03-18
> **最后更新**：2026-03-18
> **关联文档**：[Agent Skill PRD](./agent-skills-01-prd.md)

---

## 1. 方案概述

### 1.1 技术目标

创建小遥搜索 MCP 能力的 **Agent Skill**，使 Claude Code、VS Code、Cursor、OpenCode 等 AI 助手能够通过 MCP 协议发现和使用小遥搜索的本地文件搜索能力。

### 1.2 设计原则

- **标准化**：遵循 Claude Agent Skills 规范格式
- **跨平台**：支持多种 AI 助手（MCP 协议通用）
- **开箱即用**：AI 助手可自动发现可用工具
- **完整文档**：包含使用示例和故障排查指南

### 1.3 技术选型

| 技术/框架 | 用途 | 选择理由 |
|----------|------|---------|
| **MCP 协议** | 工具发现和调用 | Anthropic 官方标准，AI 助手原生支持 |
| **SKILL.md** | Skill 主文件 | Claude Agent Skills 规范必需文件 |
| **rules/** | 规则目录 | 可选的详细规则文件 |
| **YAML frontmatter** | 元数据 | Skill 列表展示和分类 |

---

## 2. Skill 规范

### 2.1 文件结构

```
.claude/skills/
└── xiaoyao-search/                  # Skill 目录（必须与 name 一致）
    ├── SKILL.md                     # 必需：Skill 主文件
    └── rules/                       # 可选：详细规则目录
        ├── tools.md                 # 工具详细定义
        ├── connection.md            # 连接配置指南
        └── examples.md              # 使用示例
```

### 2.2 SKILL.md 格式规范

**必需字段**：
- `name`: Skill 名称（使用连字符，如 `xiaoyao-search`）
- `description`: 一句话描述（显示在 Skill 列表中）

**可选字段**：
- `metadata`: 额外元数据
  - `tags`: 标签数组（用于分类和搜索）
  - `version`: Skill 版本
  - `author`: 作者

**示例**：
```yaml
---
name: xiaoyao-search
description: 小遥搜索 MCP 工具 - 本地文件智能搜索
metadata:
  tags: mcp, search, local-files, semantic-search, ai-tools
  version: 1.0.0
  author: xiaoyao-search
---
```

### 2.3 内容结构

SKILL.md 文件应包含以下章节：

1. **When to use**: 何时使用此 Skill
2. **Capability**: 可用能力列表（工具定义）
3. **Usage**: 使用说明和前提条件
4. **Examples**: 调用示例
5. **Configuration**: 配置说明
6. **Troubleshooting**: 故障排查

---

## 3. MCP 工具定义

### 3.1 工具列表

小遥搜索 MCP 服务器提供以下 5 个工具：

| 工具名称 | 功能 | AI 模型 | 参数 |
|---------|------|---------|------|
| semantic_search | 语义搜索 | BGE-M3 | query, limit, threshold, file_types |
| fulltext_search | 全文搜索 | Whoosh | query, limit, file_types |
| hybrid_search | 混合搜索 | BGE-M3 + Whoosh | query, limit, threshold, file_types |
| image_search | 图像搜索 | CN-CLIP | image_path, limit, threshold |
| voice_search | 语音搜索 | FasterWhisper | audio_path, search_type, limit, threshold |

### 3.2 工具参数定义

每个工具在 SKILL.md 中应包含：

1. **用途说明**：工具的功能描述
2. **适用场景**：什么时候使用这个工具
3. **参数列表**：
   - 参数名
   - 类型
   - 默认值
   - 说明
   - 有效范围

**示例**：

```markdown
### semantic_search（语义搜索）

- **用途**：基于 BGE-M3 向量模型的语义搜索
- **适用**：自然语言查询，如"关于机器学习的文档"

**参数**：
- `query`: string - 搜索关键词（1-500字符）
- `limit`: int - 返回结果数（1-100，默认20）
- `threshold`: float - 相似度阈值（0.0-1.0，默认0.7）
- `file_types`: string[] - 文件类型过滤（可选）
```

### 3.3 响应格式

搜索结果统一返回 JSON 格式：

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

---

## 4. 连接配置

### 4.1 MCP SSE 端点

**端点地址**: `http://127.0.0.1:8000/mcp`

### 4.2 AI 助手配置

**Claude Code / Claude Desktop**:
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

**VS Code (with MCP extension)**:
```json
{
  "mcpServers": {
    "xiaoyao-search": {
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

**Cursor**:
```json
{
  "mcpServers": {
    "xiaoyao-search": {
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

### 4.3 环境变量配置

| 变量名 | 默认值 | 说明 |
|-------|--------|------|
| MCP_SSE_ENABLED | true | 启用 MCP SSE |
| MCP_SERVER_NAME | xiaoyao-search | 服务器名称 |
| MCP_DEFAULT_LIMIT | 20 | 默认结果数 |
| MCP_DEFAULT_THRESHOLD | 0.7 | 默认相似度阈值 |
| MCP_VOICE_ENABLED | true | 启用语音搜索 |

---

## 5. 使用示例

### 5.1 语义搜索

```
用户：帮我找一下关于 Python 异步编程的文档

调用：semantic_search(
  query="Python 异步编程",
  limit=10,
  threshold=0.7
)
```

### 5.2 全文搜索

```
用户：查找包含 async def 的 Python 文件

调用：fulltext_search(
  query="async def",
  limit=20,
  file_types=["python"]
)
```

### 5.3 混合搜索

```
用户：全面搜索关于 Vue3 组件开发的资料

调用：hybrid_search(
  query="Vue3 组件开发",
  limit=20,
  threshold=0.6
)
```

### 5.4 图像搜索

```
用户：找一下跟这张图片相似的设计稿

调用：image_search(
  image_path="C:/Users/test/reference.png",
  limit=10
)
```

### 5.5 语音搜索

```
用户：（语音输入）帮我找一下上周的会议记录

调用：voice_search(
  audio_path="C:/Users/test/voice.mp3",
  search_type="semantic"
)
```

---

## 6. 故障排查

### 6.1 工具调用失败

**检查项**：
- [ ] 后端服务是否启动（http://127.0.0.1:8000）
- [ ] MCP_SSE_ENABLED=true
- [ ] /mcp 端点是否可访问

**排查命令**：
```bash
# 测试端点
curl http://127.0.0.1:8000/mcp

# 检查健康状态
curl http://127.0.0.1:8000/api/system/health
```

### 6.2 搜索结果为空

**检查项**：
- [ ] 索引已构建
- [ ] 查询词是否正确
- [ ] threshold 是否过高

**解决方案**：
- 降低 threshold 值（如从 0.7 降到 0.5）
- 使用混合搜索获取更多结果

### 6.3 图像/语音搜索失败

**检查项**：
- [ ] 文件路径为绝对路径
- [ ] 文件格式支持
- [ ] 文件大小在限制内（10MB）

**支持的格式**：
- 图像：jpg, jpeg, png, gif, bmp, webp
- 音频：wav, mp3, m4a, flac, aac, ogg, opus

---

## 7. 实施计划

### 7.1 实施步骤

| 步骤 | 内容 | 预计时间 | 状态 |
|------|------|----------|------|
| 1 | 创建 Skill 目录 `.claude/skills/xiaoyao-search/` | 0.5小时 | 待开始 |
| 2 | 编写 SKILL.md 主文件 | 1小时 | 待开始 |
| 3 | 编写 rules/tools.md 工具详细定义 | 1小时 | 待开始 |
| 4 | 编写 rules/connection.md 连接配置指南 | 0.5小时 | 待开始 |
| 5 | 编写 rules/examples.md 使用示例 | 1小时 | 待开始 |
| 6 | 验证 Skill 格式正确性 | 0.5小时 | 待开始 |

### 7.2 目录结构（完成后）

```
.claude/skills/xiaoyao-search/
├── SKILL.md
└── rules/
    ├── tools.md
    ├── connection.md
    └── examples.md
```

---

## 8. 验收标准

### 8.1 格式验收

- [ ] SKILL.md 存在且格式正确
- [ ] 包含必需的 YAML frontmatter
- [ ] 目录名与 name 一致
- [ ] 所有路径引用正确

### 8.2 内容验收

- [ ] 5 个 MCP 工具定义完整
- [ ] 包含参数说明和类型
- [ ] 包含使用示例
- [ ] 包含故障排查指南

### 8.3 功能验收

- [ ] MCP 工具可被 AI 助手发现
- [ ] 工具调用参数正确
- [ ] 响应格式符合规范

---

## 9. 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|-----|------|---------|-------|
| v1.0 | 2026-03-18 | 初始版本 | AI助手 |

---

## 10. 相关文档

- [Agent Skill PRD](./agent-skills-01-prd.md) - 产品需求定义
- [MCP 技术方案](../mcp/mcp-03-技术方案.md) - MCP 技术实现
- [MCP 开发任务清单](../mcp/mcp-04-开发任务清单.md) - 开发任务分解

---

**文档版本**：v1.0
**创建时间**：2026-03-18
**维护者**：AI助手
