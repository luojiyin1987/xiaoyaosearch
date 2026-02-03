# 小遥搜索 XiaoyaoSearch - 项目基础文档

> **项目概述**：小遥搜索是一款支持多模态AI智能搜索的本地桌面应用，为知识工作者、内容创作者和技术开发者提供语音、文本、图像输入的智能文件检索能力。

## 🎯 核心功能

- **多模态智能搜索**：语音输入（30秒内）、文本输入、图片输入，AI转换为语义搜索
- **本地文件深度检索**：视频、音频、文档的内容和文件名搜索
- **灵活AI模型配置**：云端API（OpenAI、Claude、阿里云）和本地模型（Ollama、FastWhisper、CN-CLIP）自由切换

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

- **当前阶段**：第五阶段应用打包和发布（即将完成）
- **开发周期**：8-10周（2025年11月-2026年2月）
- **MVP开发**：100%完成
- **i18n国际化**：100%完成，720+翻译键
- **API接口**：36个接口全部实现

> **进度管理**：任务完成后必须更新 [开发进度文档](docs/开发进度.md)

## 🤖 AI助手指南

### 工作要求
- **语言**：必须使用中文进行所有回复、文档编写和代码注释
- **检查清单**：功能完整性、代码规范、错误处理、测试覆盖、文档同步

### 文档导航
| 需求类型 | 主要文档 |
|---------|----------|
| 技术实现 | [技术方案](docs/03-技术方案.md) |
| 产品需求 | [产品需求文档](docs/01-prd.md) |
| 实时进度 | [开发进度](docs/开发进度.md) |
| 接口规范 | [API接口文档](docs/接口文档.md) |
| i18n国际化 | [i18n技术方案](docs/特性开发/i18n/i18n-03-技术方案.md) |
| API测试 | [测试文档目录](docs/测试文档/测试用例/) |

### 快速链接
- 🔧 技术问题 → [技术方案文档](docs/03-技术方案.md)
- 📋 产品问题 → [产品需求文档](docs/01-prd.md)
- 📊 进度跟踪 → [开发进度文档](docs/开发进度.md)

---

**文档版本**：v6.0 (精简版)
**维护者**：AI助手
**重要提醒**：所有AI回复、文档编写、代码注释必须使用中文
