# 小遥搜索 XiaoyaoSearch

[English Version](README_EN.md) | 简体中文

![小遥搜索](docs/产品文档/应用截图/小遥搜索.png)

## 📖 项目简介

![小遥搜索](docs/产品文档/logo/logo_256x256.png)

小遥搜索是一款专为知识工作者、内容创作者和技术开发者设计的跨平台本地桌面应用（Windows/MacOS/Linux）。通过集成的AI模型，支持语音输入（30秒内）、文本输入、图片输入等多种方式，将用户的查询转换为语义进行智能搜索，实现对本地文件的深度检索。

## ⭐️ 重要说明
- 本项目非商业使用完全免费，允许修改和分发（需保留版权声明和协议）；商业目的需授权，详细见[小遥搜索软件授权协议](LICENSE)
- 本项目完全通过Vibe Coding实现，提供所有源码及开发文档（上下文）供大家交流学习
  ![开发文档](docs/产品文档/应用截图/开发文档.png)

## 👨‍💻 作者介绍

<div align="center">

<table>
<tr>
<td align="center" width="120">
<img src="docs/产品文档/应用截图/author-avatar.jpg" alt="dtsola" width="120" style="border-radius: 50%;">
</td>
<td>

**dtsola**
IT解决方案架构师 | 一人公司实践者

🌐 [个人网站](https://www.dtsola.com) &nbsp;|&nbsp; 📺 [B站](https://space.bilibili.com/736015) &nbsp;|&nbsp; 💬 微信：dtsola（请备注来意）

</td>
</tr>
</table>

![微信二维码](docs/产品文档/应用截图/个人二维码.png)

</div>

### ✨ 核心特性

- **🎤 多模态输入**：支持语音录音、文本输入、图片上传
- **🔍 深度检索**：支持视频（mp4、avi）、音频（mp3、wav）、文档（txt、markdown、office、pdf）的内容和文件名搜索
- **🧠 AI增强**：集成BGE-M3、FasterWhisper、CN-CLIP、OLLAMA等先进AI模型
- **⚡ 高性能**：基于Faiss向量搜索和Whoosh全文搜索的混合检索架构
- **🔒 隐私安全**：本地运行，数据不上传云端，支持隐私模式
- **🎨 现代界面**：基于Electron + Vue 3 + TypeScript的现代化桌面应用

<div align="center">

![用户交流群](docs/运营文档/用户交流群图.png)

</div>

## 📖 核心界面

### 搜索界面

#### 主界面
![搜索界面](docs/产品文档/应用截图/搜索界面-主界面.png)

#### 通过文本搜索
![通过文本搜索](docs/产品文档/应用截图/搜索界面-文本搜索.png)

#### 通过语音搜索
![通过语音搜索](docs/产品文档/应用截图/搜索界面-语音搜索.png)

#### 通过图片搜索
![通过图片搜索](docs/产品文档/应用截图/搜索界面-图片搜索.png)

### 索引管理界面
![索引管理界面](docs/产品文档/应用截图/索引管理界面.png)

### 设置界面
![设置界面](docs/产品文档/应用截图/设置界面.png)

## 🏗️ 技术架构

### 系统架构图

![系统架构](docs/产品文档/应用截图/系统架构.png)

### 技术栈

**前端技术**
- **框架**: Electron + Vue 3 + TypeScript
- **UI库**: Ant Design Vue
- **状态管理**: Pinia
- **构建工具**: Vite

**后端技术**
- **框架**: Python 3.10 + FastAPI + Uvicorn
- **AI模型**: BGE-M3 + FasterWhisper + CN-CLIP + Ollama
- **搜索引擎**: Faiss (向量搜索) + Whoosh (全文搜索)
- **数据库**: SQLite + 索引文件

### 项目结构

```
xiaoyaosearch/
├── backend/                        # 后端服务 (Python FastAPI)
│   ├── app/                       # 应用核心代码
│   │   ├── api/                   # API路由层
│   │   ├── core/                  # 核心配置
│   │   ├── models/                # 数据模型
│   │   ├── services/              # 业务服务
│   │   ├── schemas/               # 数据模式
│   │   └── utils/                 # 工具函数
│   ├── requirements.txt           # Python依赖
│   ├── main.py                   # 应用入口
│   └── .env                      # 环境变量
├── frontend/                      # 前端应用 (Electron + Vue3)
│   ├── src/                      # 源代码
│   │   ├── main/                 # Electron主进程
│   │   ├── preload/              # 预加载脚本
│   │   └── renderer/             # Vue渲染进程
│   ├── out/                      # 构建输出
│   ├── dist-electron/            # 打包输出
│   ├── resources/                # 应用资源
│   ├── package.json              # Node.js依赖
│   └── electron-builder.yml      # 打包配置
├── docs/                          # 项目文档
│   ├── 00-mrd.md                  # 市场调研
│   ├── 01-prd.md                  # 产品需求
│   ├── 02-原型.md                 # 产品原型
│   ├── 03-技术方案.md             # 技术方案
│   ├── 04-开发任务清单.md         # 开发任务
│   ├── 05-开发排期表.md           # 开发排期
│   ├── 开发进度.md                # 进度跟踪
│   ├── 接口文档.md                # API文档
│   ├── 数据库设计文档.md          # 数据库设计
│   └── 高保真原型/                # UI原型
├── data/                          # 数据目录
│   ├── database/                  # SQLite数据库
│   ├── indexes/                   # 搜索索引
│   │   ├── faiss/                 # 向量索引
│   │   └── whoosh/                # 全文索引
│   ├── models/                   # 模型文件
│   └── logs/                   # 日志文件
├── .claude/                       # Claude助手配置
├── LICENSE                        # 软件授权协议（中文版）
├── LICENSE_EN                     # 软件授权协议（英文版）
├── README.md                      # 项目说明（中文版）
└── README_EN.md                   # 项目说明（英文版）
```

## 🚀 快速开始

### 方式一：整合包部署（推荐普通用户）

> **适用人群**：非开发者、希望快速体验小遥搜索的用户
> **支持平台**：仅支持 Windows
> **部署难度**：⭐ 简单（一键安装）

#### 下载整合包

从百度网盘下载最新的 Windows 整合包：
- 链接：https://pan.baidu.com/s/1lDaWjMCRXIT-Sqx9UFjerg?pwd=37ed
- 提取码：37ed

请选择最新版本下载（如 `XiaoyaoSearch-Windows-v1.1.1.zip`）

#### 安装步骤

**1. 解压整合包**

将下载的压缩包解压到任意目录（建议不要包含中文路径）

**2. 运行环境准备脚本**

双击运行 `scripts/setup.bat`，脚本会自动完成以下操作：
- 解压 Python 嵌入式运行时
- 安装后端 Python 依赖
- 安装前端 Node 依赖
- 生成配置文件
- 创建数据目录

> **RTX 50 系显卡用户**：如果您使用 RTX 50 系显卡，请运行 `scripts/setup_rtx50显卡.bat`，该脚本会安装支持 CUDA 12.8 的 PyTorch 版本以获得最佳性能。

**3. 安装 Ollama**

双击运行 `runtime\ollama\OllamaSetup.exe`，按提示完成安装。

安装完成后，打开命令行运行：
```bash
ollama serve
ollama pull qwen2.5:1.5b
```

**4. 下载 AI 模型**

从百度网盘下载默认模型：
- 链接：https://pan.baidu.com/s/1jRcTztvjf8aiExUh6oayVg
- 提取码：ycr5

将模型解压到对应目录：
- `data\models\embedding\BAAI\bge-m3\` - 嵌入模型
- `data\models\cn-clip\` - 视觉模型
- `data\models\faster-whisper\` - 语音识别模型

**5. 启动应用**

双击运行 `scripts/startup.bat`，脚本会：
- 启动后端服务
- 启动前端服务

**详细文档**：[整合包部署指南](docs/部署文档/整合包部署指南.md)

---

### 方式二：开发者部署

> **适用人群**：开发者、希望参与项目贡献的用户
> **支持平台**：Windows / macOS / Linux
> **部署难度**：⭐⭐⭐ 需要开发环境

#### 环境要求

- **操作系统**: Windows / macOS / Linux
- **Python**: 3.10.11+（https://www.python.org/downloads/）
- **Node.js**: 21.x+（https://nodejs.org/en/download）
- **内存**: 建议16GB 以上
- **显卡**: 建议RTX3060 6GB以上

#### 安装步骤

**1. 克隆项目**
```bash
git clone https://github.com/dtsola/xiaoyaosearch.git
cd xiaoyaosearch
```

**2. 后端部署**

```shell
# 进入后端目录
cd backend

# 安装依赖包（默认CPU版本的推理引擎）
pip install -r requirements.txt

# 安装faster-whisper
pip install faster-whisper

# 启用CUDA（可选，注意：cuda版本需根据环境确定）
pip uninstall torch torchaudio torchvision

# RTX 40 系及更早显卡（CUDA 12.1）
pip install torch==2.1.0+cu121 torchaudio==2.1.0+cu121 torchvision==0.16.0+cu121 --index-url https://download.pytorch.org/whl/cu121

# RTX 50 系显卡（CUDA 12.8）
pip install torch==2.10.0+cu128 torchaudio==2.10.0+cu128 torchvision==0.22.0+cu128 --index-url https://download.pytorch.org/whl/cu128

```

**安装ffmpeg**:
https://ffmpeg.org/download.html

**安装ollama**:
https://ollama.com/

**配置 `.env` 文件**:
```env

# 数据配置
FAISS_INDEX_PATH=../data/indexes/faiss
WHOOSH_INDEX_PATH=../data/indexes/whoosh
DATABASE_PATH=../data/database/xiaoyao_search.db

# API配置
API_HOST=127.0.0.1
API_PORT=8000
API_RELOAD=true

# 日志配置
LOG_LEVEL=info
LOG_FILE=../data/logs/app.log
```

**准备模型**:
系统默认模型说明：
- ollama：qwen2.5:1.5b
- 嵌入模型：BAAI/bge-m3
- 语音识别模型：Systran/faster-whisper-base
- 视觉模型：OFA-Sys/chinese-clip-vit-base-patch16

注意：建议先准备默认模型，先成功启动应用后，再更换模型。

ollama模型：
ollama pull qwen2.5:1.5b （根据情况自行选择）

所有模型下载地址：（百度盘）
链接: https://pan.baidu.com/s/1jRcTztvjf8aiExUh6oayVg?pwd=ycr5 提取码: ycr5 

嵌入模型：
- 模型根目录：data/models/embedding
- 将下载的模型直接解压放入到根目录即可，以下是对应关系
  - data/models/embedding/BAAI/bge-m3
  - data/models/embedding/BAAI/bge-small-zh
  - data/models/embedding/BAAI/bge-large-zh

语音识别模型：
- 模型根目录：data/models/faster-whisper
- 将下载的模型直接解压放入到根目录即可，以下是对应关系
  - data/models/faster-whisper/Systran/faster-whisper-base
  - data/models/faster-whisper/Systran/faster-whisper-small
  - data/models/faster-whisper/Systran/faster-whisper-medium
  - data/models/faster-whisper/Systran/faster-whisper-large-v3

视觉模型：
- 模型根目录：data/models/cn-clip
- 将下载的模型直接解压放入到根目录即可，以下是对应关系
  - data/models/cn-clip/OFA-Sys/chinese-clip-vit-base-patch16
  - data/models/cn-clip/OFA-Sys/chinese-clip-vit-large-patch14



**启动后端服务**:
```shell
# 使用内置配置启动
python main.py

# 或使用uvicorn启动
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

#### 3. 前端部署

```shell
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

---

## 🤝 如何共享代码

<div align="center">

![开发者交流群](docs/运营文档/开发者交流群图.png)

</div>

感谢你对小遥搜索的关注！我们欢迎任何形式的贡献，无论是代码、文档、Bug 修复还是新功能建议。

### 贡献方式

#### 方式一：提交 Pull Request（推荐）

**步骤 1：Fork 项目**
1. 访问 [xiaoyaosearch](https://github.com/dtsola/xiaoyaosearch) 仓库
2. 点击右上角的 "Fork" 按钮，将项目 Fork 到你的 GitHub 账户

**步骤 2：克隆到本地**
```bash
git clone https://github.com/<你的用户名>/xiaoyaosearch.git
cd xiaoyaosearch
```

**步骤 3：创建功能分支**
```bash
git checkout -b feature/你的功能名称
# 或
git checkout -b fix/问题描述
```

**步骤 4：进行开发**
- 按照项目代码规范进行开发
- 确保代码有适当的注释
- 运行测试确保功能正常

**步骤 5：提交代码**
```bash
git add .
git commit -m "feat(scope): 简洁描述你的改动"
```
提交格式规范：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具链相关

**步骤 6：推送到 GitHub**
```bash
git push origin feature/你的功能名称
```

**步骤 7：创建 Pull Request**
1. 访问你 Fork 的仓库页面
2. 点击 "Compare & pull request" 按钮
3. 填写 PR 描述：
   - 标题：简洁说明改动内容
   - 描述：详细说明改动原因、实现方式、测试结果
4. 等待维护者审核

#### 方式二：提交 Issue

如果你发现了 Bug 或有功能建议：
1. 访问 [Issues](https://github.com/dtsola/xiaoyaosearch/issues) 页面
2. 点击 "New Issue"
3. 选择合适的 Issue 模板
4. 详细描述问题或建议

### 代码规范

#### 前端规范
- 组件命名：PascalCase（如 `SearchPanel.vue`）
- 变量/函数：camelCase（如 `searchResults`）
- 常量：UPPER_SNAKE_CASE（如 `MAX_FILE_SIZE`）
- 代码注释：使用中文

#### 后端规范
- 文件命名：snake_case（如 `search_service.py`）
- 类名：PascalCase（如 `SearchService`）
- 函数/变量：snake_case（如 `search_files`）
- 常量：UPPER_SNAKE_CASE（如 `MAX_RESULTS`）
- 代码注释：使用中文

### 贡献指南

- ✅ 遵循项目的代码规范
- ✅ 保持代码简洁，避免过度设计
- ✅ 添加适当的错误处理
- ✅ 确保代码有适当的测试
- ✅ 更新相关文档

### 获取帮助

- 💬 微信：dtsola（请备注 "小遥搜索贡献"）
- 📧 邮件：通过官网 https://www.dtsola.com 联系
- 📺 B站：https://space.bilibili.com/736015

### 贡献者权益

- 📝 你的名字将出现在项目贡献者列表中
- 🌟 你的改动将帮助成千上万的用户
- 🤝 加入独立开发者社区，交流学习
- 🎁 优秀贡献者可获得项目周边礼品

---

**让我们一起打造更好的本地搜索体验！** 🚀

## 产品路线图
[产品路线图](ROADMAP.md)

## 数据源插件列表

小遥搜索支持**插件化架构**，可通过插件扩展多种数据源：

### 支持的数据源类型

| 类型 | 说明 | 状态 |
|------|------|------|
| 📁 本地文件 | 系统内置，无需配置 | ✅ 已实现 |
| ☁️ 语雀 | 阿里语雀知识库 | ✅ 已实现 |
| ☁️ 飞书 | 飞书文档 | 📋 计划中 |
| ☁️ Notion | Notion 笔记 | 📋 计划中 |
| 🔗 GitHub | 代码仓库和 Wiki | 📋 计划中 |
| 🔗 GitLab | GitLab 代码仓库 | 📋 计划中 |

### 完整列表

查看完整的数据源插件列表（13种类型）：

**📖 [数据源插件列表](docs/技术文档/数据源插件列表.md)** | [English Version](docs/技术文档/数据源插件列表_EN.md)

### 开发插件

想要开发新的数据源插件？

**📖 [插件开发文档](docs/技术文档/插件开发文档.md)**

---

## 项目贡献者
感谢以下人员为本项目做出的贡献：
- [@jidingliu](https://github.com/jidingliu) - 提交代码及项目宣传