# Plugin Development Guide

> **Document Type**: Development Guide
> **Target Audience**: Plugin Developers
> **Created**: 2026-02-22
> **Document Version**: v1.0
> **Current Support**: Data Source Plugins Only

**Important Notice**: Current version only supports **data source plugin** development. Other plugin types (AI models, search engines, etc.) are architecturally reserved but not yet implemented.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Quick Start](#2-quick-start)
3. [Data Source Plugin Development](#3-data-source-plugin-development)
4. [Complete Example](#4-complete-example)
5. [Debugging and Testing](#5-debugging-and-testing)

---

## 1. Architecture Overview

### 1.1 Plugin Architecture

XiaoyaoSearch adopts a **microkernel architecture**, minimizing core system functionality and implementing extensions as plugins:

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                             │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                    Microkernel (Core)                        │
│  • Plugin Lifecycle  • Configuration  • Database  • Search  │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                      Plugins Layer                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Data Source │  │ AI Model    │  │ Search Eng  │         │
│  │ Yuque/Feishu│  │ OpenAI/Claude│  │ Faiss/Whoosh│         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Core Design Principles

| Principle | Description |
|-----------|-------------|
| **Convention over Configuration** | Plugins auto-discovered in `data/plugins/` |
| **Interface Isolation** | Abstract base classes define interfaces |
| **Async First** | Follows asyncio architecture |
| **Fault Isolation** | Plugin failures don't affect core functionality |

---

## 2. Quick Start

### 2.1 Plugin Directory Structure

```
data/plugins/
├── datasource/              # Data source plugin directory
│   └── your-plugin/         # Your plugin
│       ├── plugin.py        # Plugin implementation (required)
│       ├── config.yaml      # Plugin configuration (required)
│       ├── data/            # Data storage directory
│       └── README.md        # Documentation
```

### 2.2 Three Steps to Create a Plugin

**Step 1**: Create plugin directory and files
```bash
mkdir -p data/plugins/datasource/myplugin
cd data/plugins/datasource/myplugin
touch plugin.py config.yaml
```

**Step 2**: Write plugin code (see Section 3)
**Step 3**: Enable plugin and restart backend

---

## 3. Data Source Plugin Development

### 3.1 Plugin Interface

All data source plugins must inherit from `DataSourcePlugin` and implement the following methods:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class DataSourcePlugin(ABC):
    """Data source plugin base class"""

    @classmethod
    @abstractmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """Return plugin metadata"""
        pass

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize plugin"""
        pass

    @abstractmethod
    async def sync(self) -> bool:
        """Sync data to local (core method)"""
        pass

    @abstractmethod
    async def cleanup(self):
        """Cleanup resources"""
        pass

    def get_file_source_info(self, file_path: str, content: str) -> Dict[str, Any]:
        """Get data source info (optional)"""
        return {"source_type": None, "source_url": None}
```

### 3.2 Configuration File Format

```yaml
# config.yaml
plugin:
  id: myplugin              # Unique plugin identifier
  name: My Plugin           # Display name
  version: "1.0.0"          # Version number
  type: datasource          # Plugin type
  enabled: true             # Enable plugin

datasource:
  # Data source specific configuration
  api_url: "https://api.example.com"
  download_dir: "./data/downloaded"
```

### 3.3 Data Flow

```
External Data Source
    │
    │  plugin.sync() download files
    ▼
Local File System (data/plugins/datasource/myplugin/data/*.md)
    │
    │  FileScanner scan
    ▼
Index and Search (automatic)
```

---

## 4. Complete Example

### 4.1 Minimal Plugin Implementation

```python
# plugin.py
import asyncio
from pathlib import Path
from typing import Dict, Any
from app.plugins.interface.datasource import DataSourcePlugin
from app.core.logging_config import logger


class MyDataSource(DataSourcePlugin):
    """My data source plugin"""

    def __init__(self):
        self._config = {}
        self._plugin_dir = None

    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        return {
            "id": "myplugin",
            "name": "My Data Source",
            "version": "1.0.0",
            "type": "datasource",
            "author": "Your Name",
            "description": "Plugin description"
        }

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize: prepare directories, validate config"""
        try:
            self._config = config
            self._plugin_dir = Path(__file__).parent

            # Create download directory
            download_dir = self._plugin_dir / "data" / "downloaded"
            download_dir.mkdir(parents=True, exist_ok=True)

            logger.info(f"Plugin initialized: {download_dir}")
            return True
        except Exception as e:
            logger.error(f"Plugin initialization failed: {e}")
            return False

    async def sync(self) -> bool:
        """Sync: download data to local"""
        try:
            download_dir = self._plugin_dir / "data" / "downloaded"

            # TODO: Implement your download logic
            # Example: Call API, download files, etc.

            # Example: create test file
            test_file = download_dir / "test.md"
            test_file.write_text("# Test Document\nContent...")

            logger.info(f"Sync completed: {test_file}")
            return True
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return False

    def get_file_source_info(self, file_path: str, content: str) -> Dict[str, Any]:
        """Return data source info (called during indexing)"""
        return {
            "source_type": "myplugin",
            "source_url": None
        }

    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Plugin cleanup completed")
```

### 4.2 Configuration File

```yaml
# config.yaml
plugin:
  id: myplugin
  name: My Data Source
  version: "1.0.0"
  type: datasource
  enabled: true

datasource:
  # Add your configuration items here
  api_url: "https://api.example.com"
```

### 4.3 Yuque Plugin Reference

The complete Yuque plugin implementation uses `yuque-dl` CLI tool:

```python
# Core sync logic
async def sync(self) -> bool:
    """Call yuque-dl to download data"""
    cmd = ["npx", "yuque-dl", self.repo_url, "-d", self.download_dir]
    process = await asyncio.create_subprocess_exec(*cmd)
    await process.communicate()
    return process.returncode == 0
```

See: [yuque-dl documentation](./yuque-dl.md)

---

## 5. Debugging and Testing

### 5.1 Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                  Application Startup                         │
├─────────────────────────────────────────────────────────────┤
│  1. Scan data/plugins/ directory                            │
│  2. Read each plugin's config.yaml                          │
│  3. Load and initialize plugins (call initialize())          │
│  4. Auto-execute sync (call sync())                         │
│  5. Save downloaded files to data/ directory                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Build Index (Manual Trigger)                    │
├─────────────────────────────────────────────────────────────┤
│  User manually calls index API, specifies plugin directory: │
│                                                              │
│  POST /api/index/create                                     │
│  {                                                           │
│    "folder_path": "data/plugins/datasource/myplugin/data",   │
│    "recursive": true                                         │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 View Logs

Plugin loading and sync logs are output to console when starting backend:

```
INFO: Start scanning plugin directory: data/plugins
INFO: Loading plugin: myplugin
INFO: Plugin initialized successfully: myplugin
INFO: Auto-executing plugin sync: myplugin
INFO: Sync completed, downloaded 10 files
INFO: Plugin loading completed, loaded 1 plugin total
```

### 5.3 Testing Steps

**Step 1**: Place plugin in correct directory
```bash
# Ensure plugin directory structure is correct
data/plugins/datasource/myplugin/
├── plugin.py
├── config.yaml
└── data/
```

**Step 2**: Start backend, check loading logs
```bash
cd backend
python main.py
```

**Step 3**: Check synced files
```bash
# View files downloaded by plugin
ls data/plugins/datasource/myplugin/data/
```

**Step 4**: Manually build index
```bash
# Use curl or API tool
curl -X POST "http://127.0.0.1:8000/api/index/create" \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "data/plugins/datasource/myplugin/data", "recursive": true}'
```

**Step 5**: Test search
```bash
curl -X POST "http://127.0.0.1:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "test keyword"}'
```

### 5.4 Common Issues

| Issue | Solution |
|-------|----------|
| Plugin not loaded | Check `enabled: true` in `config.yaml` |
| Initialization failed | Check console logs for detailed error messages |
| Sync no files | Check plugin `sync()` method implementation |
| Index failed | Confirm synced files exist in `data/` directory |
| Search no results | Confirm index is built and search keywords match file content |

---

## Appendix

### Related Documents

- [Technical Specification](../特性开发/plugins+yuque/plugins+yuque-03-技术方案.md)
- [Microkernel Architecture](../微内核架构设计.md)
- [Architecture Decision](../架构决策/AD-20260222-插件架构与语雀数据源.md)
- [yuque-dl documentation](./yuque-dl.md)

### Tech Stack

| Technology | Purpose |
|------------|---------|
| Python ABC | Plugin interface definition |
| importlib | Plugin dynamic loading |
| asyncio | Async processing |
| YAML | Configuration file format |

---

**Document Version**: v1.0
**Created**: 2026-02-22
**Maintainer**: XiaoyaoSearch Team
