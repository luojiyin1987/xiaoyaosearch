# 小遥搜索 XiaoyaoSearch - 项目基础文档

> **项目概述**：小遥搜索是一款支持多模态AI智能搜索的本地桌面应用，为知识工作者、内容创作者和技术开发者提供语音、文本、图像输入的智能文件检索能力。

## 🎯 核心功能

- **多模态智能搜索**：语音输入（30秒内）、文本输入、图片输入，AI转换为语义搜索
- **本地文件深度检索**：视频、音频、文档的内容和文件名搜索
- **灵活AI模型配置**：云端API（OpenAI、Claude、阿里云）和本地模型（Ollama、FastWhisper、CN-CLIP）自由切换
- **插件化架构与语雀数据源** 🚧：建立插件化框架支持多数据源扩展，优先实现语雀知识库数据源（规划中）
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

### 插件化架构与语雀数据源 🚧
- **[插件化PRD](docs/特性开发/plugins+yuque/plugins+yuque-01-prd.md)** - 插件化架构与语雀数据源产品需求（663行）
- **[插件化原型](docs/特性开发/plugins+yuque/plugins+yuque-02-原型.md)** - 原型设计和UI规范
- **[插件化技术方案](docs/特性开发/plugins+yuque/plugins+yuque-03-技术方案.md)** - Python ABC + importlib插件架构实现
- **[插件化任务清单](docs/特性开发/plugins+yuque/plugins+yuque-04-开发任务清单.md)** - 开发任务分解
- **[插件化排期表](docs/特性开发/plugins+yuque/plugins+yuque-05-开发排期表.md)** - 时间规划和里程碑

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

- **当前阶段**：特性开发阶段 - 插件化架构与语雀数据源
- **开发周期**：8-10周（2025年11月-2026年2月）
- **MVP开发**：100%完成
- **i18n国际化**：100%完成，720+翻译键
- **API接口**：36个接口全部实现
- **插件化架构与语雀数据源**：规划中，需求分析完成
- **视频画面搜索**：⏸️ 已暂停，优先开发插件化架构

> **进度管理**：任务完成后必须更新 [开发进度文档](docs/开发进度.md)

## 🤖 AI助手指南

### 工作要求
- **语言**：必须使用中文进行所有回复、文档编写和代码注释
- **检查清单**：功能完整性、代码规范、错误处理、测试覆盖、文档同步

### 当前开发特性说明

#### 插件化架构与语雀数据源 🚧 规划中

**功能定位**：
建立插件化架构，实现数据源的热插拔和独立开发，优先支持语雀知识库数据源。

**核心价值**：
- 扩展产品边界，从本地搜索升级为全场景知识搜索
- 提升用户粘性，云端数据源绑定增强平台依赖
- 建立插件生态，降低后续数据源接入成本

**技术实现**：
- **插件接口**：Python ABC定义DataSourcePlugin抽象基类
- **动态加载**：importlib实现插件热插拔
- **数据源抽象**：DataSourceItem标准化数据项
- **配置管理**：Pydantic验证配置，支持API动态管理
- **API集成**：httpx异步调用语雀API

**配置管理**：
- `PLUGIN_DIR`: 插件目录（默认data/plugins）
- `PLUGIN_AUTO_DISCOVER`: 插件自动发现（默认true）
- 语雀配置：api_token、repo_slug、base_url

**设计完成度**：
- ✅ 全局PRD文档同步
- ✅ 全局技术方案同步
- ✅ 特性PRD文档完成（663行）
- ✅ 特性技术方案完成
- ✅ 特性任务清单完成
- ✅ 特性排期表完成
- ⏳ 待开发：插件框架、语雀插件、API接口

#### 视频画面搜索 ⏸️ 已暂停

**暂停原因**：优先开发插件化架构与语雀数据源特性

**功能定位**：
为小遥搜索添加视频画面搜索能力，用户可通过图片检索视频内容，快速定位视频中的关键画面。

**核心价值**：
- 扩展搜索能力覆盖视频内容，提升产品竞争力
- 弥补现有视频搜索仅基于音频转录的不足
- 为内容创作者和知识工作者提供更高效的检索工具

**技术实现**：
- **关键帧提取**：使用FFmpeg按固定间隔提取视频关键帧（默认10秒）
- **图像理解**：复用现有CN-CLIP模型进行图像特征编码
- **向量搜索**：与图搜图共享Faiss索引，支持图片和视频帧混合搜索
- **元数据管理**：video_frames表存储帧元数据（timestamp、frame_path、faiss_index_id）

**配置管理**：
- `VIDEO_FRAME_SEARCH_ENABLED`: 是否启用视频画面搜索（默认false）
- `VIDEO_FRAME_INTERVAL`: 关键帧提取间隔（默认10秒）
- `VIDEO_FRAME_MAX_DURATION`: 最大处理时长（默认600秒）
- `VIDEO_FRAME_RESOLUTION`: 帧分辨率（默认224像素）

**设计完成度**：
- ✅ 全局PRD文档同步
- ✅ 全局原型设计同步
- ✅ 全局技术方案同步
- ✅ 全局技术选型同步
- ✅ 全局代码架构同步
- ✅ 全局数据库设计同步
- ✅ 全局索引构建逻辑同步
- ✅ 特性PRD文档完成（678行）
- ✅ 特性原型设计完成
- ✅ 特性技术方案完成（FFmpeg vs OpenCV对比）
- ⏸️ 待开发：关键帧提取服务、元数据管理、搜索扩展（已暂停）

### 文档导航
| 需求类型 | 主要文档 |
|---------|----------|
| 技术实现 | [技术方案](docs/03-技术方案.md) |
| 产品需求 | [产品需求文档](docs/01-prd.md) |
| 实时进度 | [开发进度](docs/开发进度.md) |
| 接口规范 | [API接口文档](docs/接口文档.md) |
| i18n国际化 | [i18n技术方案](docs/特性开发/i18n/i18n-03-技术方案.md) |
| 插件化架构 | [插件化PRD](docs/特性开发/plugins+yuque/plugins+yuque-01-prd.md) |
| 视频画面搜索 | [视频搜索PRD](docs/特性开发/videosearch/videosearch-01-prd.md) |
| API测试 | [测试文档目录](docs/测试文档/测试用例/) |

### 快速链接
- 🔧 技术问题 → [技术方案文档](docs/03-技术方案.md)
- 📋 产品问题 → [产品需求文档](docs/01-prd.md)
- 📊 进度跟踪 → [开发进度文档](docs/开发进度.md)
- 🔌 插件化架构 → [插件化架构PRD](docs/特性开发/plugins+yuque/plugins+yuque-01-prd.md)
- 🎬 视频搜索 → [视频画面搜索PRD](docs/特性开发/videosearch/videosearch-01-prd.md)

---

**文档版本**：v8.0 (插件化架构规划版)
**维护者**：AI助手
**重要提醒**：所有AI回复、文档编写、代码注释必须使用中文

**特性开发说明**：
- 🔌 **插件化架构与语雀数据源** 🚧 规划中
  - **技术栈**：Python ABC + importlib + Pydantic + httpx + PyYAML
  - **核心能力**：插件化框架、数据源抽象、热插拔、API管理
  - **配置参数**：PLUGIN_DIR、PLUGIN_AUTO_DISCOVER
  - **开发状态**：需求分析完成，文档100%同步
  - **全局文档**：已同步到PRD、技术方案
  - **特性文档**：PRD、原型、技术方案、任务清单、排期表

- 🎬 **视频画面搜索** ⏸️ 已暂停
  - **暂停原因**：优先开发插件化架构与语雀数据源特性
  - **技术栈**：FFmpeg关键帧提取 + CN-CLIP图像理解 + Faiss向量搜索
  - **功能开关**：默认禁用，通过后端.env配置启用
  - **配置参数**：VIDEO_FRAME_SEARCH_ENABLED、VIDEO_FRAME_INTERVAL、VIDEO_FRAME_MAX_DURATION
  - **开发状态**：需求分析和项目排期完成，文档100%同步
  - **全局文档**：已同步到PRD、原型、技术方案、技术选型、代码架构、数据库设计、索引构建逻辑
  - **特性文档**：PRD、原型、技术方案、任务清单、排期表
