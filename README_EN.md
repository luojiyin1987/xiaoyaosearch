# XiaoyaoSearch

English | [简体中文](README.md)

![XiaoyaoSearch](docs/产品文档/应用截图/小遥搜索.png)

## 📖 Project Introduction

![XiaoyaoSearch](docs/产品文档/logo/logo_256x256.png)

XiaoyaoSearch is a cross-platform local desktop application (Windows/MacOS/Linux) designed for knowledge workers, content creators, and technical developers. Through integrated AI models, it supports multiple input methods including voice input (within 30 seconds), text input, and image input, converting user queries into semantic meaning for intelligent search and deep retrieval of local files.

## ⭐️ Important Notes
- This project is completely free for non-commercial use, allowing modification and distribution (subject to preserving copyright notices and agreement); commercial use requires authorization. See [XiaoyaoSearch Software License Agreement](LICENSE_EN) for details
- This project is entirely implemented through Vibe Coding, providing all source code and development documentation (context) for everyone to learn and exchange
  ![Development Documentation](docs/产品文档/应用截图/开发文档.png)

## 👨‍💻 Author Introduction

<div align="center">

<table>
<tr>
<td align="center" width="120">
<img src="docs/产品文档/应用截图/author-avatar.jpg" alt="dtsola" width="120" style="border-radius: 50%;">
</td>
<td>

**dtsola**
IT Solution Architect | One-Person Company Practitioner

🌐 [Website](https://www.dtsola.com) &nbsp;|&nbsp; 📺 [Bilibili](https://space.bilibili.com/736015) &nbsp;|&nbsp; 💬 WeChat: dtsola (please state your purpose)

</td>
</tr>
</table>

![WeChat QR Code](docs/产品文档/应用截图/个人二维码.png)

</div>

### ✨ Core Features

- **🎤 Multimodal Input**: Supports voice recording, text input, and image upload
- **🔍 Deep Retrieval**: Supports content and filename search for videos (mp4, avi), audio (mp3, wav), and documents (txt, markdown, office, pdf)
- **🧠 AI-Enhanced**: Integrates advanced AI models including BGE-M3, FasterWhisper, CN-CLIP, and OLLAMA
- **⚡ High Performance**: Hybrid retrieval architecture based on Faiss vector search and Whoosh full-text search
- **🔒 Privacy & Security**: Runs locally, data is not uploaded to the cloud, supports privacy mode
- **🎨 Modern Interface**: Modern desktop application based on Electron + Vue 3 + TypeScript

## 📖 Core Interfaces

### Search Interface

#### Main Interface
![Search Interface](docs/产品文档/应用截图/搜索界面-主界面.png)

#### Text Search
![Text Search](docs/产品文档/应用截图/搜索界面-文本搜索.png)

#### Voice Search
![Voice Search](docs/产品文档/应用截图/搜索界面-语音搜索.png)

#### Image Search
![Image Search](docs/产品文档/应用截图/搜索界面-图片搜索.png)

### Index Management Interface
![Index Management Interface](docs/产品文档/应用截图/索引管理界面.png)

### Settings Interface
![Settings Interface](docs/产品文档/应用截图/设置界面.png)

## 🏗️ Technical Architecture

### System Architecture Diagram

![System Architecture](docs/产品文档/应用截图/系统架构.png)

### Tech Stack

**Frontend Technologies**
- **Framework**: Electron + Vue 3 + TypeScript
- **UI Library**: Ant Design Vue
- **State Management**: Pinia
- **Build Tool**: Vite

**Backend Technologies**
- **Framework**: Python 3.10 + FastAPI + Uvicorn
- **AI Models**: BGE-M3 + FasterWhisper + CN-CLIP + Ollama
- **Search Engine**: Faiss (Vector Search) + Whoosh (Full-text Search)
- **Database**: SQLite + Index Files

### Project Structure

```
xiaoyaosearch/
├── backend/                        # Backend service (Python FastAPI)
│   ├── app/                       # Application core code
│   │   ├── api/                   # API routing layer
│   │   ├── core/                  # Core configuration
│   │   ├── models/                # Data models
│   │   ├── services/              # Business services
│   │   ├── schemas/               # Data schemas
│   │   └── utils/                 # Utility functions
│   ├── requirements.txt           # Python dependencies
│   ├── main.py                   # Application entry point
│   └── .env                      # Environment variables
├── frontend/                      # Frontend application (Electron + Vue3)
│   ├── src/                      # Source code
│   │   ├── main/                 # Electron main process
│   │   ├── preload/              # Preload scripts
│   │   └── renderer/             # Vue renderer process
│   ├── out/                      # Build output
│   ├── dist-electron/            # Package output
│   ├── resources/                # Application resources
│   ├── package.json              # Node.js dependencies
│   └── electron-builder.yml      # Package configuration
├── docs/                          # Project documentation
│   ├── 00-mrd.md                  # Market research
│   ├── 01-prd.md                  # Product requirements
│   ├── 02-原型.md                 # Product prototype
│   ├── 03-技术方案.md             # Technical solution
│   ├── 04-开发任务清单.md         # Development tasks
│   ├── 05-开发排期表.md           # Development schedule
│   ├── 开发进度.md                # Progress tracking
│   ├── 接口文档.md                # API documentation
│   ├── 数据库设计文档.md          # Database design
│   └── 高保真原型/                # UI prototype
├── data/                          # Data directory
│   ├── database/                  # SQLite database
│   ├── indexes/                   # Search indexes
│   │   ├── faiss/                 # Vector indexes
│   │   └── whoosh/                # Full-text indexes
│   ├── models/                   # Model files
│   └── logs/                   # Log files
├── .claude/                       # Claude assistant configuration
├── LICENSE                        # Software license agreement (Chinese)
├── LICENSE_EN                     # Software license agreement (English)
├── README.md                      # Project description (Chinese)
└── README_EN.md                   # Project description (English)
```

## 🚀 Quick Start

### Method 1: Integrated Package Deployment (Recommended for General Users)

> **Target Audience**: Non-developers who want to quickly experience XiaoyaoSearch
> **Supported Platform**: Windows only
> **Deployment Difficulty**: ⭐ Simple (One-click installation)

#### Download Integrated Package

Download the latest Windows integrated package from Baidu Drive:
- Link: https://pan.baidu.com/s/1lDaWjMCRXIT-Sqx9UFjerg?pwd=37ed
- Extraction code: 37ed

Please select the latest version to download (e.g., `XiaoyaoSearch-Windows-v1.1.1.zip`)

#### Installation Steps

**1. Extract the Package**

Extract the downloaded archive to any directory (paths without Chinese characters are recommended)

**2. Run Environment Setup Script**

Double-click `scripts/setup.bat`, which will automatically:
- Extract Python embedded runtime
- Install backend Python dependencies
- Install frontend Node dependencies
- Generate configuration files
- Create data directories

**3. Install Ollama**

Double-click `runtime\ollama\OllamaSetup.exe` and follow the prompts.

After installation, open a command line and run:
```bash
ollama serve
ollama pull qwen2.5:1.5b
```

**4. Download AI Models**

Download default models from Baidu Drive:
- Link: https://pan.baidu.com/s/1jRcTztvjf8aiExUh6oayVg
- Extraction code: ycr5

Extract models to corresponding directories:
- `data\models\embedding\BAAI\bge-m3\` - Embedding model
- `data\models\cn-clip\` - Vision model
- `data\models\faster-whisper\` - Speech recognition model

**5. Launch the Application**

Double-click `scripts/startup.bat`, which will:
- Start backend service
- Start frontend service

**Detailed Documentation**: [Integrated Package Deployment Guide](docs/部署文档/整合包部署指南.md)

---

### Method 2: Developer Deployment

> **Target Audience**: Developers who want to contribute to the project
> **Supported Platform**: Windows / macOS / Linux
> **Deployment Difficulty**: ⭐⭐⭐ Requires development environment

#### Environment Requirements

- **Operating System**: Windows / macOS / Linux
- **Python**: 3.10.11+ (https://www.python.org/downloads/)
- **Node.js**: 21.x+ (https://nodejs.org/en/download)
- **Memory**: 16GB or more recommended
- **Graphics Card**: RTX3060 6GB or more recommended

#### Installation Steps

**1. Clone the Project**
```bash
git clone https://github.com/dtsola/xiaoyaosearch.git
cd xiaoyaosearch
```

**2. Backend Deployment**

```shell
# Enter backend directory
cd backend

# Install dependency packages (CPU version inference engine by default)
pip install -r requirements.txt

# Install faster-whisper
pip install faster-whisper

# Enable CUDA (optional, note: cuda version needs to be determined based on environment)
pip uninstall torch torchaudio torchvision
pip install torch==2.1.0+cu121 torchaudio==2.1.0+cu121 torchvision==0.16.0+cu121 --index-url https://download.pytorch.org/whl/cu121

```

**Install ffmpeg**:
https://ffmpeg.org/download.html

**Install ollama**:
https://ollama.com/

**Configure `.env` file**:
```env

# Data configuration
FAISS_INDEX_PATH=../data/indexes/faiss
WHOOSH_INDEX_PATH=../data/indexes/whoosh
DATABASE_PATH=../data/database/xiaoyao_search.db

# API configuration
API_HOST=127.0.0.1
API_PORT=8000
API_RELOAD=true

# Log configuration
LOG_LEVEL=info
LOG_FILE=../data/logs/app.log
```

**Prepare Models**:
System default model description:
- ollama: qwen2.5:1.5b
- Embedding model: BAAI/bge-m3
- Speech recognition model: Systran/faster-whisper-base
- Vision model: OFA-Sys/chinese-clip-vit-base-patch16

Note: It is recommended to prepare the default models first, successfully start the application, and then change models.

Ollama model:
ollama pull qwen2.5:1.5b (choose according to your situation)

All model download addresses: (Baidu Drive)
Link: https://pan.baidu.com/s/1jRcTztvjf8aiExUh6oayVg?pwd=ycr5 Extraction code: ycr5

Embedding model:
- Model root directory: data/models/embedding
- Extract the downloaded model directly into the root directory, the corresponding relationships are as follows
  - data/models/embedding/BAAI/bge-m3
  - data/models/embedding/BAAI/bge-small-zh
  - data/models/embedding/BAAI/bge-large-zh

Speech recognition model:
- Model root directory: data/models/faster-whisper
- Extract the downloaded model directly into the root directory, the corresponding relationships are as follows
  - data/models/faster-whisper/Systran/faster-whisper-base
  - data/models/faster-whisper/Systran/faster-whisper-small
  - data/models/faster-whisper/Systran/faster-whisper-medium
  - data/models/faster-whisper/Systran/faster-whisper-large-v3

Vision model:
- Model root directory: data/models/cn-clip
- Extract the downloaded model directly into the root directory, the corresponding relationships are as follows
  - data/models/cn-clip/OFA-Sys/chinese-clip-vit-base-patch16
  - data/models/cn-clip/OFA-Sys/chinese-clip-vit-large-patch14



**Start Backend Service**:
```shell
# Start with built-in configuration
python main.py

# Or start with uvicorn
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

#### 3. Frontend Deployment

```shell
# Enter frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🤝 How to Contribute

<div align="center">

![Developer Community](docs/运营文档/开发者交流群图.png)

</div>

Thank you for your interest in XiaoyaoSearch! We welcome contributions in any form, whether it's code, documentation, bug fixes, or new feature suggestions.

### Contribution Methods

#### Method 1: Submit a Pull Request (Recommended)

**Step 1: Fork the Project**
1. Visit the [xiaoyaosearch](https://github.com/dtsola/xiaoyaosearch) repository
2. Click the "Fork" button in the upper right corner to fork the project to your GitHub account

**Step 2: Clone to Local**
```bash
git clone https://github.com/<your-username>/xiaoyaosearch.git
cd xiaoyaosearch
```

**Step 3: Create a Feature Branch**
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

**Step 4: Make Changes**
- Follow the project coding standards
- Ensure your code has appropriate comments
- Run tests to ensure functionality works correctly

**Step 5: Commit Your Changes**
```bash
git add .
git commit -m "feat(scope): brief description of your changes"
```
Commit format conventions:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation update
- `style`: Code formatting changes
- `refactor`: Code refactoring
- `perf`: Performance optimization
- `test`: Testing related
- `chore`: Build/toolchain related

**Step 6: Push to GitHub**
```bash
git push origin feature/your-feature-name
```

**Step 7: Create a Pull Request**
1. Visit your forked repository page
2. Click the "Compare & pull request" button
3. Fill in the PR description:
   - Title: Briefly describe the changes
   - Description: Detailed explanation of the reason, implementation, and test results
4. Wait for maintainer review

#### Method 2: Submit an Issue

If you find a bug or have a feature suggestion:
1. Visit the [Issues](https://github.com/dtsola/xiaoyaosearch/issues) page
2. Click "New Issue"
3. Select an appropriate issue template
4. Describe the problem or suggestion in detail

### Code Standards

#### Frontend Standards
- Component naming: PascalCase (e.g., `SearchPanel.vue`)
- Variables/Functions: camelCase (e.g., `searchResults`)
- Constants: UPPER_SNAKE_CASE (e.g., `MAX_FILE_SIZE`)
- Code comments: Use Chinese

#### Backend Standards
- File naming: snake_case (e.g., `search_service.py`)
- Class names: PascalCase (e.g., `SearchService`)
- Functions/Variables: snake_case (e.g., `search_files`)
- Constants: UPPER_SNAKE_CASE (e.g., `MAX_RESULTS`)
- Code comments: Use Chinese

### Contribution Guidelines

- ✅ Follow project coding standards
- ✅ Keep code simple, avoid over-engineering
- ✅ Add appropriate error handling
- ✅ Ensure proper test coverage
- ✅ Update relevant documentation

### Get Help

- 💬 WeChat: dtsola (please note "XiaoyaoSearch Contribution")
- 📧 Email: Contact via https://www.dtsola.com
- 📺 Bilibili: https://space.bilibili.com/736015

### Contributor Benefits

- 📝 Your name will appear in the project contributors list
- 🌟 Your changes will help thousands of users
- 🤝 Join the indie developer community for exchange and learning
- 🎁 Outstanding contributors may receive project merchandise

---

**Let's build a better local search experience together!** 🚀

## Product Roadmap
[Product Roadmap](ROADMAP_EN.md)

## Project Contributors
Thanks to the following people for their contributions to this project:
- [@jidingliu](https://github.com/jidingliu) - Code submission and project promotion