# XiaoyaoSearch - Plugin Development Guide

> **Document Version**: v2.0
> **Last Updated**: 2026-02-22
> **Design Principle**: Convention over Configuration

---

## Table of Contents

1. [Plugin System Overview](#plugin-system-overview)
2. [Plugin Types](#plugin-types)
3. [Common Plugin Interface](#common-plugin-interface)
4. [Data Source Plugin Development](#data-source-plugin-development)
5. [AI Model Plugin Development](#ai-model-plugin-development)
6. [Configuration File Specification](#configuration-file-specification)
7. [Development Examples](#development-examples)
8. [Best Practices](#best-practices)
9. [FAQ](#faq)
10. [API Reference](#api-reference)

---

## Plugin System Overview

### What is a Plugin?

The XiaoyaoSearch plugin system is a modular extension framework that allows developers to extend system functionality through independent plugins. Each plugin is a standalone Python module that can be installed, configured, and used without modifying the core code.

### Design Principles

**Convention over Configuration**: Plugins are managed through the file system and configuration files, without requiring API interfaces.

- **Installation**: Copy the plugin directory to `data/plugins/` to complete installation
- **Configuration**: Configure through `config.yaml` file
- **Auto-discovery**: System automatically scans and loads plugins on startup
- **Hot-plugging**: Disable plugins by renaming the directory or modifying configuration

### Plugin Directory Structure

```
data/plugins/
├── datasource/              # Data source plugins directory
│   ├── yuque/              # Yuque knowledge base plugin
│   ├── feishu/             # Feishu document plugin
│   └── filesystem/         # Local file plugin
├── ai_model/               # AI model plugins directory
│   ├── openai/             # OpenAI model plugin
│   ├── claude/             # Claude model plugin
│   └── ollama/             # Ollama local model plugin
├── search_engine/          # Search engine plugins directory (future)
│   └── elasticsearch/      # Elasticsearch engine
├── content_parser/         # Content parser plugins directory (future)
│   ├── pdf/                # PDF parser
│   └── docx/               # DOCX parser
└── auth/                   # Authentication plugins directory (future)
    └── oauth/              # OAuth authentication
```

---

## Plugin Types

### Currently Supported Plugin Types

| Plugin Type | Description | Status | Interface |
|-------------|-------------|--------|-----------|
| **Data Source Plugin** | Scan external data sources and index content | ✅ Implemented | `DataSourcePlugin` |
| **AI Model Plugin** | Provide AI model services (text/image/voice) | ✅ Implemented | `AIModelPlugin` |

### Planned Plugin Types

| Plugin Type | Description | Status | Interface |
|-------------|-------------|--------|-----------|
| **Search Engine Plugin** | Replace or extend search engines | 🚧 Planned | `SearchEnginePlugin` |
| **Content Parser Plugin** | Support new file format parsing | 🚧 Planned | `ContentParserPlugin` |
| **Storage Plugin** | Support different storage backends | 🚧 Planned | `StoragePlugin` |
| **Authentication Plugin** | Support different authentication methods | 🚧 Planned | `AuthPlugin` |
| **Notification Plugin** | Integrate notification services | 🚧 Planned | `NotificationPlugin` |

> 💡 **Tip**: If you need a plugin type that is still in planning, please submit an Issue or Pull Request.

---

## Common Plugin Interface

### BasePlugin Base Class

All plugins must inherit from the `BasePlugin` base class, which provides basic plugin lifecycle management:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BasePlugin(ABC):
    """Plugin base class, parent of all plugins"""

    # Plugin metadata
    metadata: Dict[str, Any] = None

    @classmethod
    @abstractmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """Return plugin metadata

        Returns:
            Dict[str, Any]: Dictionary containing the following keys:
                - id: Unique plugin identifier
                - name: Display name
                - version: Version number (semver format)
                - type: Plugin type (datasource/ai_model/search_engine, etc.)
                - author: Author
                - description: Description
                - dependencies: Dependency list (optional)
        """
        pass

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize plugin

        Args:
            config: Configuration dictionary loaded from config.yaml

        Returns:
            bool: Return True if initialization succeeds, False otherwise
        """
        pass

    @abstractmethod
    async def cleanup(self):
        """Clean up resources (close connections, release handles, etc.)"""
        pass

    def get_status(self) -> Dict[str, Any]:
        """Get plugin running status (optional implementation)"""
        return {
            "status": "running",
            "health": "healthy"
        }
```

### Plugin Metadata Specification

All plugins' `get_metadata()` method must return the following standard fields:

```python
{
    "id": "plugin_id",              # Unique plugin identifier (required)
    "name": "Plugin Display Name",   # Display name (required)
    "version": "1.0.0",             # Version number (required, semver format)
    "type": "datasource",           # Plugin type (required)
    "author": "Author Name",        # Author (required)
    "description": "Plugin description",  # Description (required)
    "dependencies": [],             # Other plugins depended on (optional)
    "min_system_version": "1.0.0"   # Minimum system version requirement (optional)
}
```

---

## Data Source Plugin Development

### DataSourcePlugin Interface

Data source plugins are used to scan external data sources and index their content into XiaoyaoSearch.

```python
from typing import AsyncIterator, Dict, Any
from app.plugins.interface import DataSourcePlugin

class MyDataSourcePlugin(DataSourcePlugin):
    """Data source plugin example"""

    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        return {
            "id": "my_datasource",
            "name": "My Data Source",
            "version": "1.0.0",
            "type": "datasource",
            "author": "Your Name",
            "description": "Data source description",
            "datasource_type": "my_datasource"  # Data source type identifier
        }

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize data source connection"""
        self.config = config
        # Initialize client, validate configuration, etc.
        return True

    async def scan(self, **kwargs) -> AsyncIterator[Dict[str, Any]]:
        """Scan data source and return standardized data items

        Yields:
            Dict[str, Any]: Data item containing:
                - id: Unique identifier
                - filename: File name
                - path: Path or URL
                - content: Content
                - file_type: File type
                - source_type: Data source type
                - source_url: Original URL (optional)
                - source_name: Data source name
        """
        # Implement scanning logic
        pass

    async def cleanup(self):
        """Clean up resources"""
        pass
```

### Data Source Plugin Directory

```
data/plugins/datasource/
├── my_datasource/
│   ├── plugin.py           # Plugin implementation (required)
│   ├── config.yaml         # Configuration file (required)
│   ├── requirements.txt    # Dependency list (optional)
│   └── README.md           # Usage documentation (optional)
```

### Configuration File Example

```yaml
# data/plugins/datasource/my_datasource/config.yaml
plugin:
  id: my_datasource
  name: My Data Source
  version: "1.0.0"
  type: datasource
  enabled: true

datasource:
  type: my_datasource
  api_key: "your_api_key"
  base_url: "https://api.example.com"

sync:
  interval: 60
  batch_size: 50
```

---

## AI Model Plugin Development

### AIModelPlugin Interface

AI model plugins provide integration with different AI services, supporting text models, image models, and voice models.

```python
from typing import AsyncIterator, Dict, Any, Optional
from enum import Enum
from app.plugins.interface import AIModelPlugin

class ModelType(Enum):
    """AI model types"""
    TEXT = "text"        # Text model (chat, embedding)
    IMAGE = "image"      # Image model (image understanding)
    VOICE = "voice"      # Voice model (speech recognition)
    VIDEO = "video"      # Video model (reserved)

class MyAIModelPlugin(AIModelPlugin):
    """AI model plugin example"""

    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        return {
            "id": "my_ai_model",
            "name": "My AI Model",
            "version": "1.0.0",
            "type": "ai_model",
            "author": "Your Name",
            "description": "AI model description",
            "model_type": ModelType.TEXT.value,  # Model type
            "supported_features": [              # Supported features
                "chat",
                "embedding",
                "streaming"
            ]
        }

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize AI model client"""
        self.config = config
        # Initialize client
        return True

    async def chat(self,
                   messages: list,
                   stream: bool = False,
                   **kwargs) -> AsyncIterator[Dict[str, Any]] | Dict[str, Any]:
        """Chat interface

        Args:
            messages: Message list
            stream: Whether to stream output
            **kwargs: Other parameters

        Returns:
            Stream or single result
        """
        if stream:
            async for chunk in self._chat_stream(messages, **kwargs):
                yield chunk
        else:
            return await self._chat_once(messages, **kwargs)

    async def embedding(self, text: str, **kwargs) -> list[float]:
        """Text embedding interface

        Args:
            text: Input text

        Returns:
            list[float]: Text vector
        """
        # Implement embedding logic
        pass

    async def cleanup(self):
        """Clean up resources"""
        pass
```

### AI Model Plugin Directory

```
data/plugins/ai_model/
├── my_ai_model/
│   ├── plugin.py           # Plugin implementation (required)
│   ├── config.yaml         # Configuration file (required)
│   ├── requirements.txt    # Dependency list (optional)
│   └── README.md           # Usage documentation (optional)
```

### Configuration File Example

```yaml
# data/plugins/ai_model/my_ai_model/config.yaml
plugin:
  id: my_ai_model
  name: My AI Model
  version: "1.0.0"
  type: ai_model
  enabled: true

model:
  type: text                # Model type: text/image/voice
  api_key: "your_api_key"
  base_url: "https://api.example.com/v1"
  model_name: "model-name"
  timeout: 30

capabilities:
  chat: true                # Support chat
  embedding: true           # Support embedding
  streaming: true           # Support streaming output
  vision: false             # Support image understanding
```

---

## Configuration File Specification

### Common Configuration Structure

All plugin configuration files must follow the following structure:

```yaml
# ========== Plugin Metadata (required) ==========
plugin:
  id: string                 # Unique plugin identifier (required)
  name: string               # Display name (required)
  version: string            # Version number (required, semver format)
  type: string               # Plugin type (required)
  enabled: boolean           # Whether enabled (required)

# ========== Plugin-specific Configuration ==========
# Configuration items vary by plugin type
```

### Data Source Plugin Configuration

```yaml
plugin:
  id: my_datasource
  name: My Data Source
  version: "1.0.0"
  type: datasource
  enabled: true

# Data source specific configuration
datasource:
  type: string               # Data source type
  # ... other configuration items

sync:
  interval: integer          # Sync interval (minutes)
  batch_size: integer        # Batch size
  timeout: integer           # Request timeout (seconds)
```

### AI Model Plugin Configuration

```yaml
plugin:
  id: my_ai_model
  name: My AI Model
  version: "1.0.0"
  type: ai_model
  enabled: true

# AI model specific configuration
model:
  type: string               # Model type: text/image/voice
  # ... other configuration items

capabilities:
  chat: boolean              # Support chat
  embedding: boolean         # Support embedding
  streaming: boolean         # Support streaming output
  vision: boolean            # Support image understanding
```

---

## Development Examples

### Example 1: Simple File System Data Source Plugin

```python
# data/plugins/datasource/simple_file/plugin.py
import aiofiles
from pathlib import Path
from typing import AsyncIterator, Dict, Any
from app.plugins.interface import DataSourcePlugin

class SimpleFilePlugin(DataSourcePlugin):
    """Simple file system plugin"""

    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        return {
            "id": "simple_file",
            "name": "Simple File System",
            "version": "1.0.0",
            "type": "datasource",
            "author": "Your Name",
            "description": "Scan Markdown files in specified directory",
            "datasource_type": "simple_file"
        }

    async def initialize(self, config: Dict[str, Any]) -> bool:
        self.config = config
        self.scan_path = Path(config.get("scan_path", "."))
        if not self.scan_path.exists():
            raise ValueError(f"Path does not exist: {self.scan_path}")
        return True

    async def scan(self, **kwargs) -> AsyncIterator[Dict[str, Any]]:
        for file_path in self.scan_path.rglob("*.md"):
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()

            yield {
                "id": f"simple_file_{file_path.stem}",
                "filename": file_path.name,
                "path": str(file_path),
                "content": content,
                "file_type": "markdown",
                "source_type": "simple_file",
                "source_url": None,
                "source_name": "Simple File System"
            }

    async def cleanup(self):
        pass
```

### Example 2: OpenAI AI Model Plugin

```python
# data/plugins/ai_model/openai/plugin.py
import openai
from typing import AsyncIterator, Dict, Any
from app.plugins.interface import AIModelPlugin, ModelType

class OpenAIPlugin(AIModelPlugin):
    """OpenAI AI model plugin"""

    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        return {
            "id": "openai",
            "name": "OpenAI",
            "version": "1.0.0",
            "type": "ai_model",
            "author": "XiaoyaoSearch Team",
            "description": "OpenAI GPT model integration",
            "model_type": ModelType.TEXT.value,
            "supported_features": ["chat", "embedding", "streaming"]
        }

    async def initialize(self, config: Dict[str, Any]) -> bool:
        self.config = config
        self.client = openai.AsyncAI(api_key=config["api_key"])
        return True

    async def chat(self,
                   messages: list,
                   stream: bool = False,
                   **kwargs) -> AsyncIterator[Dict[str, Any]] | Dict[str, Any]:
        model = kwargs.get("model", self.config.get("model", "gpt-4"))

        if stream:
            stream_response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True
            )
            async for chunk in stream_response:
                if chunk.choices[0].delta.content:
                    yield {
                        "content": chunk.choices[0].delta.content,
                        "finish_reason": None
                    }
            yield {"finish_reason": "stop"}
        else:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages
            )
            return {
                "content": response.choices[0].message.content,
                "finish_reason": response.choices[0].finish_reason
            }

    async def embedding(self, text: str, **kwargs) -> list[float]:
        model = kwargs.get("model", self.config.get("embedding_model", "text-embedding-3-small"))
        response = await self.client.embeddings.create(
            model=model,
            input=text
        )
        return response.data[0].embedding

    async def cleanup(self):
        await self.client.close()
```

---

## Best Practices

### 1. Error Handling

```python
async def scan(self, **kwargs) -> AsyncIterator[Dict[str, Any]]:
    try:
        items = await self.client.get_items()
    except Exception as e:
        print(f"Plugin error: {e}")
        return  # Silent failure, doesn't affect other plugins

    for item in items:
        try:
            yield self._process_item(item)
        except Exception as e:
            print(f"Failed to process item: {e}")
            continue
```

### 2. Configuration Validation

```python
async def initialize(self, config: Dict[str, Any]) -> bool:
    # Validate required configuration
    required = ["api_key", "base_url"]
    for key in required:
        if key not in config:
            raise ValueError(f"Missing required configuration: {key}")
    return True
```

### 3. Resource Cleanup

```python
async def cleanup(self):
    """Ensure resources are properly released"""
    if hasattr(self, 'client'):
        if hasattr(self.client, 'aclose'):
            await self.client.aclose()
        elif hasattr(self.client, 'close'):
            await self.client.close()
```

### 4. Logging

```python
import logging

class MyPlugin(DataSourcePlugin):
    def __init__(self):
        self.logger = logging.getLogger(f"plugin.{self.__class__.__name__}")

    async def scan(self, **kwargs):
        self.logger.info(f"Starting scan: {self.config}")
        # ...
```

---

## FAQ

### Q1: How do I determine my plugin type?

Choose a plugin type based on the functionality you want to extend:

| Need | Plugin Type |
|------|-------------|
| Add new data sources (e.g., Yuque, Feishu) | Data Source Plugin (datasource) |
| Integrate new AI services (e.g., Claude, Gemini) | AI Model Plugin (ai_model) |
| Add new file format support | Content Parser Plugin (planned) |
| Replace search engine | Search Engine Plugin (planned) |

### Q2: Can plugins communicate with each other?

Direct communication is not recommended. Plugins should remain independent and exchange data through system-provided services:
- Use database to share data
- Use system event mechanism
- Use message queues (such as Redis)

### Q3: How to test plugins?

```python
import pytest
from app.plugins.loader import PluginLoader

@pytest.mark.asyncio
async def test_my_plugin():
    loader = PluginLoader()
    plugin = await loader.load_plugin("my_plugin")
    assert await plugin.initialize({}) is True
    # Test functionality
    await plugin.cleanup()
```

### Q4: Can plugins depend on third-party libraries?

Yes. Create `requirements.txt` in the plugin directory:

```txt
# data/plugins/my_plugin/requirements.txt
httpx==0.24.0
openai==1.0.0
```

### Q5: How to disable a plugin?

**Method 1**: Modify configuration file
```yaml
plugin:
  enabled: false
```

**Method 2**: Rename plugin directory
```bash
mv data/plugins/my_plugin data/plugins/my_plugin.disabled
```

---

## API Reference

### DataSourcePlugin Complete Interface

```python
class DataSourcePlugin(BasePlugin):
    """Data source plugin abstract base class"""

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
    async def scan(self, **kwargs) -> AsyncIterator[Dict[str, Any]]:
        """Scan data source and return standardized data items"""
        pass

    @abstractmethod
    async def cleanup(self):
        """Clean up resources"""
        pass
```

### AIModelPlugin Complete Interface

```python
class AIModelPlugin(BasePlugin):
    """AI model plugin abstract base class"""

    @classmethod
    @abstractmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """Return plugin metadata"""
        pass

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize plugin"""
        pass

    async def chat(self,
                   messages: list,
                   stream: bool = False,
                   **kwargs) -> AsyncIterator[Dict[str, Any]] | Dict[str, Any]:
        """Chat interface (optional implementation)"""
        raise NotImplementedError

    async def embedding(self, text: str, **kwargs) -> list[float]:
        """Text embedding interface (optional implementation)"""
        raise NotImplementedError

    async def understand_image(self, image: str, prompt: str, **kwargs) -> str:
        """Image understanding interface (optional implementation)"""
        raise NotImplementedError

    async def transcribe_audio(self, audio: str, **kwargs) -> str:
        """Speech recognition interface (optional implementation)"""
        raise NotImplementedError

    @abstractmethod
    async def cleanup(self):
        """Clean up resources"""
        pass
```

---

## Appendix

### A. Plugin Type Mapping Table

| Plugin Type | Directory | Interface | Status |
|-------------|----------|-----------|--------|
| datasource | `data/plugins/datasource/` | DataSourcePlugin | ✅ |
| ai_model | `data/plugins/ai_model/` | AIModelPlugin | ✅ |
| search_engine | `data/plugins/search_engine/` | SearchEnginePlugin | 🚧 |
| content_parser | `data/plugins/content_parser/` | ContentParserPlugin | 🚧 |
| storage | `data/plugins/storage/` | StoragePlugin | 🚧 |
| auth | `data/plugins/auth/` | AuthPlugin | 🚧 |

### B. Recommended Development Tools

- **Code Editor**: VSCode + Python extension
- **Debug Tools**: pytest + pytest-asyncio
- **API Testing**: httpx + pytest-mock
- **YAML Validation**: yamllint

### C. Related Documentation

- [Technical Solution](../特性开发/plugins+yuque/plugins+yuque-03-技术方案.md)
- [Task List](../特性开发/plugins+yuque/plugins+yuque-04-开发任务清单.md)
- [Database Design](../特性开发/plugins+yuque/plugins+yuque-增量-数据库设计文档.md)

### D. Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 2026-02-22 | Initial version (data source plugins only) |
| v2.0 | 2026-02-22 | Refactored to general plugin system, supporting multiple plugin types |

---

**Document Maintained By**: Developer
**Last Updated**: 2026-02-22 (v2.0 - General Plugin System)
**Feedback Channel**: GitHub Issues
