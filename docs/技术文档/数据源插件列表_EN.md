# Data Source Plugins List

> **Document Type**: Plugin Reference
> **Target Audience**: Users and Developers
> **Created**: 2026-02-24
> **Version**: v1.0

This document lists all data source types supported by XiaoyaoSearch, along with implemented and planned plugins.

---

## Table of Contents

1. [Supported Data Source Types](#1-supported-data-source-types)
2. [Plugin Development](#2-plugin-development)
3. [Implemented Plugins](#3-implemented-plugins)
4. [Planned Plugins](#4-planned-plugins)

---

## 1. Supported Data Source Types

XiaoyaoSearch uses a plugin-based architecture supporting multiple data source types. Each type has a unique icon and color identifier:

### Type Definitions

| Type ID | Chinese Name | English Name | Icon | Color | Source Type |
|---------|--------------|--------------|------|-------|-------------|
| `filesystem` | 本地文件 | Local File | 📁 Database | #1890ff Blue | Built-in |
| `yuque` | 语雀 | Yuque | ☁️ Cloud | #52c41a Green | Cloud Knowledge Base |
| `feishu` | 飞书 | Feishu | ☁️ Cloud | #722ed1 Purple | Cloud Collaboration |
| `dingding` | 钉钉 | DingTalk | ☁️ Cloud | #0089FF Sky Blue | Cloud Collaboration |
| `notion` | Notion | Notion | ☁️ Cloud | #fa541c Orange | Cloud Notes |
| `github` | GitHub | GitHub | 🔗 Link | #24292e Black | Code Hosting |
| `gitlab` | GitLab | GitLab | 🔗 Link | #FC6D26 Orange | Code Hosting |
| `confluence` | Confluence | Confluence | ☁️ Cloud | #0052CC Dark Blue | Enterprise Knowledge Base |
| `wordpress` | WordPress | WordPress | 📄 FileText | #21759b Dark Blue | Blog Platform |
| `obsidian` | Obsidian | Obsidian | 📊 Database | #7c3aed Purple | Local Notes |
| `dropbox` | Dropbox | Dropbox | ☁️ Cloud | #0061FE Blue | Cloud Storage |
| `googledrive` | Google Drive | Google Drive | ☁️ Cloud | #4285F4 Blue-Green | Cloud Storage |
| `onedrive` | OneDrive | OneDrive | ☁️ Cloud | #0078D4 Sky Blue | Cloud Storage |
| `figma` | Figma | Figma | 🖼️ Picture | #F24E1E Red | Design Tool |

### Category Description

#### 🖥️ Local Data Sources
- **filesystem**: Local file system, built-in system support
- **obsidian**: Obsidian local note vault

#### ☁️ Cloud Knowledge Bases
- **yuque**: Alibaba Yuque knowledge base
- **feishu**: Feishu/Lark Suite documents
- **dingding**: DingTalk documents
- **notion**: Notion notes
- **confluence**: Atlassian Confluence enterprise knowledge base

#### 💻 Developer Platforms
- **github**: GitHub repositories and Wiki
- **gitlab**: GitLab repositories

#### 📝 Content Platforms
- **wordpress**: WordPress blog posts

#### ☁️ Cloud Storage Services
- **dropbox**: Dropbox cloud storage
- **googledrive**: Google Drive
- **onedrive**: Microsoft OneDrive

#### 🎨 Design Tools
- **figma**: Figma design files and comments

### Color Specification

Data source types not in the predefined list will:
- Display the original `source_type` value
- Use default blue style (`#1890ff`)

---

## 2. Plugin Development

Want to develop a new data source plugin? Please refer to:

**📖 [Plugin Development Guide](./插件开发文档.md)** (Chinese)

The document includes:
- Architecture overview
- Quick start guide
- Complete example code
- Debugging and testing methods

### Quick Links

| Document | Description |
|----------|-------------|
| [Plugin Development Guide](./插件开发文档.md) | Complete guide for data source plugin development |
| [Microkernel Architecture Design](../微内核架构设计.md) | Plugin architecture design specification |
| [Technical Solution](../特性开发/plugins+yuque/plugins+yuque-03-技术方案.md) | Plugin system technical implementation |

---

## 3. Implemented Plugins

### ✅ Local File (filesystem)

**Status**: Built-in | **Priority**: Core

**Description**:
- Default supported data source
- No additional configuration required
- Supports local file system search

**Features**:
- Supports multiple file formats (documents, audio, video, images)
- Automatic indexing and vectorization
- Intelligent file content extraction

**Configuration**: No configuration needed, system built-in

---

### ✅ Yuque (yuque)

**Status**: Built-in (Disabled by Default) | **Priority**: High | **Version**: v1.0

**Description**:
- Built-in plugin, no additional installation required
- Disabled by default, requires manual activation
- Uses `yuque-dl` CLI tool for data sync
- Automatically downloads Markdown format documents

**Features**:
- 🔄 Auto sync on startup (when enabled)
- 📄 Supports Markdown format export
- 🏷️ Preserves document metadata
- 🔗 Supports source link navigation

**How to Enable**:

**Step 1**: Copy configuration template to actual configuration file
```bash
# In plugin directory
cd backend/data/plugins/datasource/yuque
cp config.yaml.example config.yaml
```

**Step 2**: Edit `config.yaml` to enable the plugin
```yaml
plugin:
  enabled: true  # Change false to true
```

**Configuration**:
Configuration template: `backend/data/plugins/datasource/yuque/config.yaml.example`
Actual configuration file: `backend/data/plugins/datasource/yuque/config.yaml`

Full configuration example (config.yaml):
```yaml
plugin:
  id: yuque
  name: Yuque Knowledge Base
  version: "1.0.0"
  type: datasource
  enabled: true  # Manually enable

datasource:
  repos:
    - name: "Personal Brand"                     # Knowledge base name
      url: "https://www.yuque.com/username/repo/slug"  # Yuque knowledge base URL
      download_dir: "./data/product-docs"       # Local download directory
      token: "your_yuque_token"                 # Yuque API Token
      ignore_images: true                       # Whether to ignore image downloads
```

**Usage Instructions**:
1. Get Yuque API Token: [Reference](https://github.com/gxr404/yuque-dl/blob/main/docs/GET_TOEKN.md)
2. Copy `config.yaml.example` to `config.yaml`
3. Edit `config.yaml`, set `enabled` to `true`, configure URL and Token
4. Restart backend for auto sync

**Plugin Location**: `backend/data/plugins/datasource/yuque/`

---

### ✅ Feishu (feishu)

**Status**: Built-in (Enabled by Default) | **Priority**: High | **Version**: v1.0

**Description**:
- Built-in plugin, no additional installation required
- Enabled by default
- Zero-config design, automatically recognizes Feishu export format
- Supports Markdown documents exported from Feishu

**Features**:
- ✨ Zero-config: Automatically recognizes Feishu export format
- 🏷️ Metadata extraction: Extracts source link from document end
- ⚡ Performance optimized: Only parses last 500 characters
- 🔗 Supports source link navigation

**Usage Instructions**:
1. Export document from Feishu as Markdown format
2. Place exported file in scan directory
3. Build index
4. Search results will display "Feishu" identifier

**Feishu Export Format**:
```markdown
---
> Updated: 2026-03-30 02:52:46
> Source: feishu
> URL: <https://feishu.cn/wiki/MZKMwqpljiod1ak38Cscnr8hnkh>
---
```

**Plugin Location**: `backend/data/plugins/datasource/feishu/`

---

### ✅ DingTalk (dingding)

**Status**: Built-in (Enabled by Default) | **Priority**: High | **Version**: v1.0

**Description**:
- Built-in plugin, no additional installation required
- Enabled by default
- Zero-config design, automatically recognizes DingTalk export format
- Supports `.xyddjson` metadata files generated by DingTalk export tool

**Features**:
- ✨ Zero-config: Automatically recognizes `.xyddjson` metadata files
- 📦 Standalone metadata: JSON format, structured and easy to parse
- ⚡ Superior performance: Parsing speed <1ms, better than Feishu
- 🔗 Supports source link navigation
- 🛡️ Strong fault tolerance: Parsing failure doesn't affect original file indexing

**Usage Instructions**:
1. Install DingTalk export tool (browser extension)
2. Export document from DingTalk (supports .docx, .pdf, etc.)
3. Export tool automatically generates `.xyddjson` metadata file
4. Place exported file and metadata file in scan directory
5. Build index, system automatically recognizes DingTalk documents
6. Search results will display "DingTalk" identifier

**.xyddjson Metadata Format**:

```json
{
  "version": "1.0.0",
  "source": "dingtalk-docs",
  "exportTool": "xiaoyaosearch-dingding-export",
  "exportToolVersion": "1.0.0",
  "exportTime": "2026-04-08T15:30:00.000Z",
  "file": {
    "fileName": "项目报告.docx",
    "originalName": "项目报告",
    "dentryUuid": "A1B2C3D4E5F6G7H8",
    "url": "https://alidocs.dingtalk.com/i/nodes/A1B2C3D4E5F6G7H8"
  }
}
```

**Directory Structure Example**:
```
D:\Documents\DingTalk_Export\
├── 需求文档.docx
├── 需求文档.docx.xyddjson      ← Metadata file
├── 技术方案.pdf
└── 技术方案.pdf.xyddjson      ← Metadata file
```

**Technical Advantages** (vs Feishu):

| Aspect | Feishu | DingTalk | DingTalk Advantage |
|--------|--------|----------|-------------------|
| Metadata Location | End of file content | Standalone JSON file | Structured, maintainable |
| Parsing Method | Regex | JSON parsing | More reliable, faster |
| Parsing Performance | ~1ms | <1ms | Better performance |
| Reliability | Depends on export format | Standard JSON | Strong fault tolerance |
| Extensibility | Feishu only | Can extend to other platforms | Highly versatile |

**Plugin Location**: `backend/data/plugins/datasource/dingding/`

---

## 4. Planned Plugins

The following plugins are in planning. Contributions are welcome!

### 🔥 High Priority

| Plugin | Status | Est. Duration | Description |
|--------|--------|---------------|-------------|
| **GitHub** | 📋 Planned | 2-3 weeks | Code repository and README document search |
| **Confluence** | 📋 Planned | 2-3 weeks | Enterprise knowledge base integration |
| **Obsidian** | 📋 Planned | 1-2 weeks | Local note vault support |

### 🟡 Medium Priority

| Plugin | Status | Description |
|--------|--------|-------------|
| **Notion** | 📋 Planned | Notion database integration |
| **Figma** | 📋 Planned | Design files and comments search |
| **Google Drive** | 📋 Planned | Google Docs and cloud files |

### 🟢 Low Priority

| Plugin | Status | Description |
|--------|--------|-------------|
| **GitLab** | 📋 Planned | GitLab code repositories |
| **WordPress** | 📋 Planned | WordPress blog posts |
| **Dropbox** | 📋 Planned | Dropbox cloud files |
| **OneDrive** | 📋 Planned | Microsoft OneDrive |

---

## Plugin Development Contribution

Want to contribute a new data source plugin?

1. 📖 Read [Plugin Development Guide](./插件开发文档.md)
2. 💬 Discuss your plugin plan in Issues
3. 🔧 Reference existing plugin implementations (e.g., Yuque plugin)
4. ✅ Submit a Pull Request

---

**Document Version**: v1.2
**Created**: 2026-02-24
**Maintainer**: XiaoyaoSearch Team
**Changelog**:
- v1.2 (2026-04-08): DingTalk plugin implemented
- v1.1 (2026-03-31): Feishu plugin implemented
- v1.0 (2026-02-24): Initial version, defined 13 data source types