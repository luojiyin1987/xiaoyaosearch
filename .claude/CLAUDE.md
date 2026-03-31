# 小遥搜索 XiaoyaoSearch - 项目基础文档

> **项目概述**：小遥搜索是一款支持多模态AI智能搜索的本地桌面应用，为知识工作者、内容创作者和技术开发者提供语音、文本、图像输入的智能文件检索能力。

## 🎯 核心功能

- **多模态智能搜索**：语音输入（30秒内）、文本输入、图片输入，AI转换为语义搜索
- **本地文件深度检索**：视频、音频、文档的内容和文件名搜索
- **灵活AI模型配置**：云端API（OpenAI、Claude、阿里云）和本地模型（Ollama、FastWhisper、CN-CLIP）自由切换
- **插件化架构与数据源扩展（语雀+飞书）** 🚧：建立插件化框架支持多数据源扩展，优先实现语雀知识库数据源和飞书文档数据源（规划中）
- **视频画面搜索** ⏸️：通过图片检索视频内容，快速定位视频中的关键画面（已暂停）

## 💻 开发环境

- **操作系统**：Windows 11
- **Python版本**：3.10.11
- **Node.js版本**：21.x

## 🏗️ 技术架构

### 技术栈
- **前端**：Electron + Vue 3 + TypeScript + Ant Design Vue + vue-i18n@9
- **后端**：Python 3.10 + FastAPI + Uvicorn
- **AI模型**：BGE-M3 + FasterWhisper + CN-CLIP + Ollama
- **搜索引擎**：Faiss（向量）+ Whoosh（全文）
- **数据库**：SQLite + Faiss索引 + Whoosh索引

## 📋 设计文档引用

### 核心文档
- **[PRD](docs/01-prd.md)** - 产品需求文档
- **[原型设计](docs/02-原型.md)** - UI设计和交互规范
- **[技术方案](docs/03-技术方案.md)** - 技术架构和实现细节
- **[技术选型](docs/技术选型.md)** - 技术选型理由和对比
- **[数据库设计](docs/数据库设计文档.md)** - 数据库架构和表结构
- **[MRD](docs/00-mrd.md)** - 市场调研和商业模式
- **[开发进度](docs/开发进度.md)** - 实时进度跟踪
- **[开发排期表](docs/05-开发排期表.md)** - 时间规划

### 技术文档
- **[代码架构](docs/代码架构.md)** - 代码结构和模块划分
- **[搜索逻辑](docs/搜索逻辑.md)** - 搜索功能实现逻辑
- **[索引构建逻辑](docs/索引构建逻辑.md)** - 索引构建管理逻辑
- **[API接口文档](docs/接口文档.md)** - API规范说明

### 开发模板
- **[精益开发流程](docs/base/精益开发流程.md)** - 开发流程规范
- **[MRD/PRD/原型/技术方案/任务清单模板](docs/base/)** - 各类文档模板

### i18n国际化
- **[i18n PRD](docs/特性开发/i18n/i18n-01-prd.md)** - 国际化需求
- **[i18n 技术方案](docs/特性开发/i18n/i18n-03-技术方案.md)** - 国际化技术实现

### OpenAI兼容大模型服务 🚧
- **[OpenAI PRD](docs/特性开发/openai/openai-01-prd.md)** - OpenAI兼容大模型服务产品需求（672行）
- **[OpenAI原型](docs/特性开发/openai/openai-02-原型.md)** - 原型设计和UI规范（857行）
- **[OpenAI技术方案](docs/特性开发/openai/openai-03-技术方案.md)** - aiohttp + Pydantic技术实现（1145行）
- **[OpenAI任务清单](docs/特性开发/openai/openai-04-开发任务清单.md)** - 开发任务分解
- **[OpenAI排期表](docs/特性开发/openai/openai-05-开发排期表.md)** - 时间规划和里程碑
- **[OpenAI增量接口文档](docs/特性开发/openai/openai-增量-接口文档.md)** - API接口增量设计
- **[OpenAI增量数据库设计](docs/特性开发/openai/openai-增量-数据库设计文档.md)** - 数据库表结构增量设计

### 云端嵌入模型调用能力 🔥 开发中（第一优先级）
- **[云端嵌入PRD](docs/特性开发/embedding-openai/embedding-openai-01-prd.md)** - 云端嵌入模型调用能力产品需求（774行）
- **[云端嵌入原型](docs/特性开发/embedding-openai/embedding-openai-02-原型.md)** - 原型设计和UI规范
- **[云端嵌入技术方案](docs/特性开发/embedding-openai/embedding-openai-03-技术方案.md)** - aiohttp + OpenAI API技术实现
- **[云端嵌入任务清单](docs/特性开发/embedding-openai/embedding-openai-04-开发任务清单.md)** - 开发任务分解
- **[云端嵌入排期表](docs/特性开发/embedding-openai/embedding-openai-05-开发排期表.md)** - 时间规划和里程碑
- **[云端嵌入实施步骤](docs/特性开发/embedding-openai/embedding-openai-06-实施步骤.md)** - 完整实施步骤
- **[云端嵌入增量接口文档](docs/特性开发/embedding-openai/embedding-openai-增量-接口文档.md)** - API接口增量设计
- **[云端嵌入增量数据库设计](docs/特性开发/embedding-openai/embedding-openai-增量-数据库设计文档.md)** - 数据库表结构增量设计

### 插件化架构与数据源扩展（语雀+飞书）
- **[插件化PRD](docs/特性开发/plugins+yuque/plugins+yuque-01-prd.md)** - 插件化架构与语雀数据源产品需求（663行）
- **[插件化原型](docs/特性开发/plugins+yuque/plugins+yuque-02-原型.md)** - 原型设计和UI规范
- **[插件化技术方案](docs/特性开发/plugins+yuque/plugins+yuque-03-技术方案.md)** - Python ABC + importlib插件架构实现
- **[插件化任务清单](docs/特性开发/plugins+yuque/plugins+yuque-04-开发任务清单.md)** - 开发任务分解
- **[插件化排期表](docs/特性开发/plugins+yuque/plugins+yuque-05-开发排期表.md)** - 时间规划和里程碑
- **[飞书数据源PRD](docs/特性开发/plugins+feishu/plugins+feishu-01-prd.md)** - 飞书文档数据源产品需求（567行）
- **[飞书数据源技术方案](docs/特性开发/plugins+feishu/plugins+feishu-03-技术方案.md)** - 飞书文档数据源技术方案（671行）
- **[飞书数据源任务清单](docs/特性开发/plugins+feishu/plugins+feishu-04-开发任务清单.md)** - 飞书数据源开发任务清单（467行）

### Agent Skill：小遥搜索 MCP 能力 🚧 规划中
- **[Agent Skill PRD](docs/特性开发/agent-skills/agent-skills-01-prd.md)** - Agent Skill 产品需求
- **[Agent Skill 技术方案](docs/特性开发/agent-skills/agent-skills-03-技术方案.md)** - Agent Skill 技术实现
- **[Agent Skill 实施步骤](docs/特性开发/agent-skills/agent-skills-06-实施步骤.md)** - 开发任务分解

### MCP 服务器支持
- **[MCP PRD](docs/特性开发/mcp/mcp-01-prd.md)** - MCP服务器支持产品需求（925行）
- **[MCP技术方案](docs/特性开发/mcp/mcp-03-技术方案.md)** - FastAPI集成 + SSE端点技术实现（1270行）
- **[MCP任务清单](docs/特性开发/mcp/mcp-04-开发任务清单.md)** - 开发任务分解（622行）
- **[MCP排期表](docs/特性开发/mcp/mcp-05-开发排期表.md)** - 时间规划和里程碑（509行）

### 视频画面搜索 ⏸️ 已暂停
- **[视频搜索PRD](docs/特性开发/videosearch/videosearch-01-prd.md)** - 视频画面搜索产品需求（678行）
- **[视频搜索原型](docs/特性开发/videosearch/videosearch-02-原型.md)** - 原型设计和UI规范
- **[视频搜索技术方案](docs/特性开发/videosearch/videosearch-03-技术方案.md)** - FFmpeg关键帧提取技术实现
- **[视频搜索任务清单](docs/特性开发/videosearch/videosearch-04-开发任务清单.md)** - 开发任务分解
- **[视频搜索排期表](docs/特性开发/videosearch/videosearch-05-开发排期表.md)** - 时间规划和里程碑

### 测试文档
- **[配置接口测试](docs/测试文档/测试用例/test-data-config.md)** - AI模型配置接口测试
- **[搜索接口测试](docs/测试文档/测试用例/test-data-search.md)** - 搜索服务接口测试
- **[索引接口测试](docs/测试文档/测试用例/test-data-index.md)** - 索引管理接口测试
- **[系统接口测试](docs/测试文档/测试用例/test-data-system.md)** - 系统配置接口测试

### 产品资源
- **[高保真原型](docs/高保真原型/v1.0/)** - Vue3前端交互原型
- **[产品文档目录](docs/产品文档/)** - logo、截图、架构图等

## 🛠️ 开发规范

### 代码规范
**语言要求**：所有代码编写、文档编写、注释必须使用中文

**命名规范**：
- 前端：组件PascalCase，变量函数camelCase，常量UPPER_SNAKE_CASE
- 后端：文件snake_case，类名PascalCase，函数变量snake_case，常量UPPER_SNAKE_CASE

### Git规范
- **分支命名**：main/develop/feature功能名/bugfix问题描述/hotfix紧急修复
- **提交格式**：`<type>(<scope>): <subject>`
  - 类型：feat/fix/docs/style/refactor/perf/test/chore
  - 示例：`feat(search): 添加多模态搜索功能`

### 测试规范
- 后端核心服务：>90%
- 前端组件：>80%
- API接口：100%

### 安全规范
- API密钥使用环境变量存储
- 本地数据库文件加密存储
- 用户数据不上传云端

## 🚀 部署指南

### 后端启动（Python FastAPI）
```powershell
cd backend
python -m venv venv
.\venv\Scripts\pip.exe install -r requirements.txt
.\venv\Scripts\python.exe main.py
```
验证：http://127.0.0.1:8000/docs

### 前端启动（Electron + Vue3）
```powershell
cd frontend
npm install
npm run electron:dev
```

### 高保真原型
```powershell
cd docs\高保真原型\v1.0
npm run dev
```

## 📊 项目进度

- **当前阶段**：特性开发阶段 - 飞书数据源插件
- **开发周期**：8-10周（2025年11月-2026年2月）
- **MVP开发**：✅ 已完成
- **i18n国际化**：✅ 已完成
- **API接口**：36个接口全部实现
- **OpenAI兼容大模型服务**：✅ 已完成
- **插件化架构与数据源扩展（语雀+飞书）**：🔥 开发中，飞书数据源插件开发中
- **视频画面搜索**：⏸️ 已暂停，优先开发插件化架构与数据源扩展
- **MCP服务器支持**：✅ 已完成
- **云端嵌入模型调用能力**：✅ 已完成

> **进度管理**：任务完成后必须更新 [开发进度文档](docs/开发进度.md)

## 🤖 AI助手指南

### 工作要求
- **语言**：必须使用中文进行所有回复、文档编写和代码注释
- **检查清单**：功能完整性、代码规范、错误处理、测试覆盖、文档同步

### 当前开发特性说明

#### 插件化架构与数据源扩展（飞书数据源插件） 🔥 开发中（第一优先级）

**功能定位**：
为小遥搜索添加插件化架构，支持飞书文档数据源插件，实现飞书文档的索引和智能搜索能力。

**核心价值**：
- 扩展数据源支持：从本地文件扩展到云端知识库（飞书文档）
- 提升用户价值：支持用户在飞书中的工作文档进行智能搜索
- 建立插件生态：为未来扩展更多数据源奠定基础
- 技术架构升级：从单体架构升级为插件化架构

**技术实现**：
- **插件化框架**：基于Python ABC实现数据源插件基类
- **动态加载**：使用importlib实现插件的动态发现和加载
- **飞书API集成**：通过飞书开放API获取文档内容
- **配置管理**：支持插件目录、自动发现等配置

**配置管理**：
- `PLUGIN_DIR`: 插件目录路径
- `PLUGIN_AUTO_DISCOVER`: 是否自动发现插件
- `FEISHU_APP_ID`: 飞书应用ID
- `FEISHU_APP_SECRET`: 飞书应用密钥

**设计完成度**：
- ✅ 全局PRD文档同步
- ✅ 全局技术方案同步
- ✅ 飞书数据源PRD完成（567行）
- ✅ 飞书数据源技术方案完成（671行）
- ✅ 飞书数据源任务清单完成（467行）
- 🚧 飞书数据源插件开发中

### 文档导航
| 需求类型 | 主要文档 |
|---------|----------|
| 技术实现 | [技术方案](docs/03-技术方案.md) |
| 产品需求 | [产品需求文档](docs/01-prd.md) |
| 实时进度 | [开发进度](docs/开发进度.md) |
| 接口规范 | [API接口文档](docs/接口文档.md) |
| i18n国际化 | [i18n技术方案](docs/特性开发/i18n/i18n-03-技术方案.md) |
| OpenAI大模型PRD | [OpenAI兼容PRD](docs/特性开发/openai/openai-01-prd.md) |
| OpenAI原型 | [OpenAI兼容原型](docs/特性开发/openai/openai-02-原型.md) |
| OpenAI技术方案 | [OpenAI兼容技术方案](docs/特性开发/openai/openai-03-技术方案.md) |
| OpenAI任务清单 | [OpenAI任务清单](docs/特性开发/openai/openai-04-开发任务清单.md) |
| OpenAI排期表 | [OpenAI排期表](docs/特性开发/openai/openai-05-开发排期表.md) |
| OpenAI接口文档 | [OpenAI增量接口文档](docs/特性开发/openai/openai-增量-接口文档.md) |
| OpenAI数据库设计 | [OpenAI增量数据库设计](docs/特性开发/openai/openai-增量-数据库设计文档.md) |
| 插件化架构PRD | [插件化PRD](docs/特性开发/plugins+yuque/plugins+yuque-01-prd.md) |
| 插件化架构技术方案 | [插件化技术方案](docs/特性开发/plugins+yuque/plugins+yuque-03-技术方案.md) |
| 飞书数据源PRD | [飞书数据源PRD](docs/特性开发/plugins+feishu/plugins+feishu-01-prd.md) |
| 飞书数据源技术方案 | [飞书数据源技术方案](docs/特性开发/plugins+feishu/plugins+feishu-03-技术方案.md) |
| 飞书数据源任务清单 | [飞书数据源任务清单](docs/特性开发/plugins+feishu/plugins+feishu-04-开发任务清单.md) |
| 视频画面搜索PRD | [视频搜索PRD](docs/特性开发/videosearch/videosearch-01-prd.md) |
| **云端嵌入PRD** | **[云端嵌入模型PRD](docs/特性开发/embedding-openai/embedding-openai-01-prd.md)** |
| **云端嵌入技术方案** | **[云端嵌入技术方案](docs/特性开发/embedding-openai/embedding-openai-03-技术方案.md)** |
| **云端嵌入实施步骤** | **[云端嵌入实施步骤](docs/特性开发/embedding-openai/embedding-openai-06-实施步骤.md)** |
| **Agent Skill PRD** | **[Agent Skill PRD](docs/特性开发/agent-skills/agent-skills-01-prd.md)** |
| **Agent Skill技术方案** | **[Agent Skill技术方案](docs/特性开发/agent-skills/agent-skills-03-技术方案.md)** |
| **MCP服务器支持PRD** | **[MCP PRD](docs/特性开发/mcp/mcp-01-prd.md)** |
| **MCP服务器支持技术方案** | **[MCP技术方案](docs/特性开发/mcp/mcp-03-技术方案.md)** |
| **MCP服务器支持任务清单** | **[MCP任务清单](docs/特性开发/mcp/mcp-04-开发任务清单.md)** |
| API测试 | [测试文档目录](docs/测试文档/测试用例/) |

### 快速链接
- 🔧 技术问题 → [技术方案文档](docs/03-技术方案.md)
- 📋 产品问题 → [产品需求文档](docs/01-prd.md)
- 📊 进度跟踪 → [开发进度文档](docs/开发进度.md)
- 🤖 OpenAI大模型PRD → [OpenAI兼容大模型服务PRD](docs/特性开发/openai/openai-01-prd.md)
- 🎨 OpenAI原型 → [OpenAI兼容大模型服务原型](docs/特性开发/openai/openai-02-原型.md)
- ⚙️ OpenAI技术方案 → [OpenAI兼容大模型服务技术方案](docs/特性开发/openai/openai-03-技术方案.md)
- 📋 OpenAI任务清单 → [OpenAI兼容大模型服务任务清单](docs/特性开发/openai/openai-04-开发任务清单.md)
- 📅 OpenAI排期表 → [OpenAI兼容大模型服务排期表](docs/特性开发/openai/openai-05-开发排期表.md)
- 🔌 OpenAI接口文档 → [OpenAI兼容大模型服务接口文档](docs/特性开发/openai/openai-增量-接口文档.md)
- 🗄️ OpenAI数据库设计 → [OpenAI兼容大模型服务数据库设计](docs/特性开发/openai/openai-增量-数据库设计文档.md)
- 🔌 插件化架构 → [插件化架构PRD](docs/特性开发/plugins+yuque/plugins+yuque-01-prd.md)
- 📄 飞书数据源PRD → [飞书数据源PRD](docs/特性开发/plugins+feishu/plugins+feishu-01-prd.md)
- ⚙️ 飞书数据源技术方案 → [飞书数据源技术方案](docs/特性开发/plugins+feishu/plugins+feishu-03-技术方案.md)
- 📋 飞书数据源任务清单 → [飞书数据源任务清单](docs/特性开发/plugins+feishu/plugins+feishu-04-开发任务清单.md)
- 🎬 视频搜索 → [视频画面搜索PRD](docs/特性开发/videosearch/videosearch-01-prd.md)
- 🔥 云端嵌入模型PRD → [云端嵌入模型调用能力PRD](docs/特性开发/embedding-openai/embedding-openai-01-prd.md)
- ⚙️ 云端嵌入技术方案 → [云端嵌入技术方案](docs/特性开发/embedding-openai/embedding-openai-03-技术方案.md)
- 📋 云端嵌入实施步骤 → [云端嵌入实施步骤](docs/特性开发/embedding-openai/embedding-openai-06-实施步骤.md)
- 🔥 Agent Skill PRD → [Agent Skill PRD](docs/特性开发/agent-skills/agent-skills-01-prd.md)
- ⚙️ Agent Skill技术方案 → [Agent Skill技术方案](docs/特性开发/agent-skills/agent-skills-03-技术方案.md)
- ✅ MCP服务器支持PRD → [MCP服务器支持PRD](docs/特性开发/mcp/mcp-01-prd.md)
- ⚙️ MCP服务器支持技术方案 → [MCP服务器支持技术方案](docs/特性开发/mcp/mcp-03-技术方案.md)
- 📋 MCP服务器支持任务清单 → [MCP服务器支持任务清单](docs/特性开发/mcp/mcp-04-开发任务清单.md)

---

**文档版本**：v15.0 (飞书数据源插件开发版)
**维护者**：AI助手
**重要提醒**：所有AI回复、文档编写、代码注释必须使用中文

**当前开发重点**：🔥 插件化架构与数据源扩展（飞书数据源插件）

**特性开发说明**：
- 🔌 **插件化架构与数据源扩展（语雀+飞书）** 🔥 开发中（第一优先级）
  - **技术栈**：Python ABC + importlib + Pydantic + httpx + PyYAML
  - **核心能力**：插件化框架、数据源抽象、热插拔、API管理
  - **数据源支持**：语雀知识库、飞书文档
  - **配置参数**：PLUGIN_DIR、PLUGIN_AUTO_DISCOVER
  - **开发状态**：飞书数据源插件开发中
  - **全局文档**：已同步到PRD、技术方案
  - **特性文档**：PRD、原型、技术方案、任务清单、排期表、飞书PRD（567行）、飞书技术方案（671行）、飞书任务清单（467行）
- 🤖 **OpenAI兼容大模型服务** 🚧 规划中
  - **技术栈**：aiohttp + Pydantic + OpenAI API标准
  - **核心能力**：云端大模型集成、动态表单、API密钥加密
  - **配置参数**：provider（local/cloud）、api_key、endpoint、model
  - **开发状态**：需求分析、原型设计和技术方案完成，PRD文档完成（672行），原型文档完成（857行），技术方案完成（1145行），任务清单完成，排期表完成，增量接口文档完成，增量数据库设计完成
  - **全局文档**：已同步到PRD、原型、技术方案
  - **特性文档**：PRD、原型、技术方案、任务清单、排期表、增量接口文档、增量数据库设计文档
- ✅ **云端嵌入模型调用能力** ✅ 已完成
  - **技术栈**：aiohttp + OpenAI API + Pydantic + tenacity
  - **核心能力**：云端嵌入模型集成、本地/云端互斥切换、批量文本嵌入、API调用重试
  - **配置参数**：provider（local/cloud）、api_key、endpoint、model、维度处理模式
  - **开发状态**：已完成
  - **全局文档**：已同步到PRD、原型、技术方案
  - **特性文档**：PRD、原型、技术方案、任务清单、排期表、实施方案、增量接口文档、增量数据库设计文档

- 🎬 **视频画面搜索** ⏸️ 已暂停
  - **暂停原因**：优先开发插件化架构与语雀数据源特性
  - **技术栈**：FFmpeg关键帧提取 + CN-CLIP图像理解 + Faiss向量搜索
  - **功能开关**：默认禁用，通过后端.env配置启用
  - **配置参数**：VIDEO_FRAME_SEARCH_ENABLED、VIDEO_FRAME_INTERVAL、VIDEO_FRAME_MAX_DURATION
  - **开发状态**：需求分析和项目排期完成，文档100%同步
  - **全局文档**：已同步到PRD、原型、技术方案、技术选型、代码架构、数据库设计、索引构建逻辑
  - **特性文档**：PRD、原型、技术方案、任务清单、排期表

- 🔥 **Agent Skill：小遥搜索 MCP 能力** 🔥 开发中（第一优先级）
  - **技术栈**：MCP 协议 + Claude Agent Skills 规范 + SKILL.md
  - **核心能力**：为 Claude Code 提供 MCP 工具调用能力、5个搜索工具（语义/全文/语音/图像/混合）
  - **配置参数**：MCP SSE 端点 `http://127.0.0.1:8000/mcp`
  - **开发状态**：需求分析和设计完成
  - **全局文档**：待同步
  - **特性文档**：PRD、技术方案、实施步骤

---

