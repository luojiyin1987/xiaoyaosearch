# 架构决策：Agent Skill 封装 MCP 能力

**决策日期**：2026年3月18日

## 背景

小遥搜索已实现 MCP 服务器支持，提供 5 个搜索工具（语义搜索、全文搜索、混合搜索、图像搜索、语音搜索）。但这些能力仅能通过手动配置 Claude Desktop 等 AI 助手来使用，缺乏统一的文档规范和 AI 可发现的工具定义。

为了使 Claude Code、VS Code、Cursor、OpenCode 等 AI 助手能够更方便地发现和使用小遥搜索的 MCP 工具能力，需要创建 Agent Skill 规范文档。

## 解决方案

创建小遥搜索 MCP 能力的 Agent Skill，遵循 Claude Agent Skills 规范：

1. **Skill 目录结构**：
   ```
   .claude/skills/xiaoyao-search/
   ├── SKILL.md                  # 主文件（必需）
   └── rules/                    # 详细规则（可选）
       ├── tools.md             # 工具详细定义
       ├── connection.md        # 连接配置指南
       └── examples.md          # 使用示例
   ```

2. **SKILL.md 主文件内容**：
   - YAML frontmatter（name, description, metadata）
   - When to use（使用场景）
   - Capability（5 个工具定义）
   - Usage（使用说明）
   - Examples（调用示例）
   - Configuration（配置说明）
   - Troubleshooting（故障排查）

3. **MCP 端点**：`http://127.0.0.1:8000/mcp`

4. **跨平台支持**：支持 Claude Code、Claude Desktop、VS Code、Cursor 等支持 MCP 协议的 AI 助手

## 影响

- **正向影响**：
  - AI 助手可自动发现小遥搜索 MCP 工具
  - 统一的文档规范提升易用性
  - 支持多种 AI 助手（跨平台）
  - 纯文档类 Skill，不修改现有代码

- **依赖关系**：
  - 依赖 MCP 服务器实现（backend/app/mcp/）
  - 依赖 FastAPI SSE 端点（/mcp）
  - 不依赖前端代码

- **无需变更**：
  - 无需修改 backend 代码
  - 无需修改前端代码
  - 无需修改数据库结构

---

**决策编号**：AD-20260318-01
