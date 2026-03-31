# 插件化架构与语雀数据源 - 技术方案

> **文档类型**：技术方案
> **特性状态**：已完成
> **创建时间**：2026-02-22
> **最后更新**：2026-02-22 (v2.7 - 启动时自动同步)

---

## 1. 方案概述

### 1.1 技术目标

建立**通用插件化架构**，支持多种类型的插件扩展，包括数据源插件、AI模型插件等。优先实现数据源插件，语雀数据源采用 CLI 工具集成方案。

### 1.2 设计原则

- **约定优于配置**：插件文件放到`data/plugins/`目录下即自动发现
- **配置集成**：使用现有的 Pydantic Settings 配置系统，支持环境变量
- **自动加载**：系统启动时自动扫描和加载插件
- **类型隔离**：不同类型插件独立目录、独立接口
- **异步优先**：遵循现有异步架构（asyncio）
- **最小侵入**：不修改现有 FileScanner 和 FileIndexService 核心逻辑

### 1.3 支持的插件类型

| 插件类型 | 接口 | 状态 | 说明 |
|---------|------|------|------|
| **数据源插件** | `DataSourcePlugin` | ✅ 已实现 | 扫描外部数据源并索引内容 |
| **AI模型插件** | `AIModelPlugin` | 🚧 架构预留 | 提供AI模型服务（本版本不实现） |
| **搜索引擎插件** | `SearchEnginePlugin` | 🚧 规划中 | 替换或扩展搜索引擎 |
| **内容解析器插件** | `ContentParserPlugin` | 🚧 规划中 | 支持新的文件格式解析 |

### 1.4 技术选型

| 技术/框架 | 用途 | 选择理由 |
|----------|------|---------|
| Python ABC | 插件接口定义 | 标准库，类型安全 |
| importlib | 插件动态加载 | Python标准库，无额外依赖 |
| Pydantic Settings | 配置管理 | 复用现有配置系统，支持环境变量 |
| asyncio | 异步处理 | 遵循现有异步架构 |
| asyncio subprocess | CLI工具调用 | 异步进程管理 |
| yuque-dl | 语雀数据获取 | 成熟开源工具，避免维护API |

---

## 2. 架构设计

### 2.1 整体架构（简化版 - 同步模式）

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              API层                                       │
├─────────────────────────────────────────────────────────────────────────┤
│  /api/search  │  /api/index/build  │  /api/datasource/sync               │
└────────────┬──────────────────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────────────────┐
│                        服务层 (Service Layer)                             │
├───────────────────────────────────────────────────────────────────────────┤
│  PluginLoader  │  DataSourceManager  │  IndexService  │  SearchService   │
└────────────┬──────────────────────────────────────────┬───────────────────┘
             │                                          │
┌────────────▼──────────────────────────────────────────▼───────────────────┐
│                        插件层 (Plugin Layer)                                │
├───────────────────────────────────────────────────────────────────────────┤
│  BasePlugin(interface) - 通用插件基类                                      │
│  └─ DataSourcePlugin(interface) - 核心方法: sync() + get_sync_dirs()      │
│      └─ YuqueDataSource (调用 yuque-dl CLI 下载到本地)                    │
│  └─ [AIModelPlugin - 架构预留]                                             │
└────────────┬──────────────────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────────────────┐
│                   本地文件系统 (统一数据层)                                  │
├───────────────────────────────────────────────────────────────────────────┤
│  data/plugins/datasource/yuque/data/downloaded/*.md                      │
│  + 用户配置的本地目录 (D:/Documents, D:/Projects, ...)                     │
└────────────┬──────────────────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────────────────┐
│              现有流程（完全复用，无需修改）                                  │
├───────────────────────────────────────────────────────────────────────────┤
│  FileSystemDataSource.scan() → 所有文件统一扫描                            │
│  IndexService → 统一索引构建 (Faiss + Whoosh)                              │
│  SearchService → 统一搜索服务                                              │
└───────────────────────────────────────────────────────────────────────────┘
```

**数据流说明**：

```
外部数据源 (语雀)                    本地文件系统
    │                                   │
    │  YuqueDataSource.sync()          │
    │  ──────────────────────────>      │
    │  (yuque-dl 下载 Markdown)         │
    │                                   │
    │  data/plugins/datasource/yuque/data/downloaded/*.md
    │                                   │
    │  FileSystemDataSource.scan()     │
    │  <──────────────────────────      │
    │  (扫描所有目录，包括插件下载的文件) │
    │                                   │
    ▼                                   ▼
统一的索引和搜索流程 (完全复用现有实现)
```

### 2.2 插件目录结构

```
data/plugins/
├── datasource/              # 数据源插件目录
│   ├── yuque/              # 语雀知识库插件
│   │   ├── plugin.py       # 插件实现
│   │   ├── data/           # 下载的数据目录
│   │   │   └── downloaded/ # yuque-dl 下载的markdown文件
│   └── feishu/             # 飞书文档插件（未来）
│
│   [注：本地文件数据源保持现有实现，不放在插件目录]
├── ai_model/               # AI模型插件目录（架构预留）
│
├── search_engine/          # 搜索引擎插件目录（未来）
│
├── content_parser/         # 内容解析器插件目录（未来）
│
└── auth/                   # 认证插件目录（未来）
```

### 2.3 模块划分（基于现有后端结构）

```
backend/
├── app/
│   ├── plugins/                          # 新增：插件框架模块
│   │   ├── __init__.py
│   │   ├── base.py                      # 通用插件基类
│   │   ├── interface/                   # 插件接口定义集合
│   │   │   ├── __init__.py
│   │   │   ├── base.py                  # BasePlugin接口
│   │   │   ├── datasource.py            # DataSourcePlugin接口
│   │   │   └── ai_model.py              # AIModelPlugin接口（预留）
│   │   └── loader.py                    # 插件加载器
│   │
│   ├── core/
│   │   ├── config.py                     # 扩展：新增 PluginConfig 配置类
│   │   ├── database.py
│   │   └── logging_config.py
│   │
│   ├── models/                           # 扩展：数据源相关字段
│   │   ├── file.py                       # FileModel 添加 source_type、source_url 等
│   │   └── ...
│   │
│   ├── services/                         # 现有服务（保持不变）
│   │   ├── file_scanner.py               # 文件扫描服务
│   │   ├── file_index_service.py         # 文件索引服务
│   │   ├── chunk_index_service.py        # 分块索引服务
│   │   └── ...
│   │
│   └── api/                              # 扩展：新增插件管理API
│       └── ...
│
└── data/
    └── plugins/                          # 插件目录
        └── datasource/
            └── yuque/
                ├── plugin.py
                └── data/
                    └── downloaded/
```

### 2.4 现有服务集成点

| 现有服务 | 集成方式 | 说明 |
|---------|---------|------|
| **FileScanner** | 扩展扫描目录 | 插件的 `get_sync_dirs()` 返回的目录加入扫描列表 |
| **FileIndexService** | 无需修改 | 自动处理所有扫描到的文件 |
| **ChunkIndexService** | 无需修改 | 自动处理大文件分块 |
| **AppConfig (Pydantic)** | 新增 PluginConfig | 插件配置通过环境变量管理 |

---

## 3. 核心模块设计（基于现有异步架构）

### 3.1 配置管理扩展（复用 Pydantic Settings）

```python
# backend/app/core/config.py 新增配置类

from pydantic import Field
from typing import List, Optional

class PluginConfig(BaseSettings):
    """插件系统配置"""

    # 插件目录配置（默认值）
    plugin_dir: str = Field(default="data/plugins", description="插件根目录")

    class Config:
        env_prefix = "PLUGIN_"

# 无需更新主配置类，插件配置独立管理
```

**配置方式说明**：
- ✅ 插件系统配置使用默认值，无需环境变量
- ✅ 每个插件有自己的配置文件（放在插件目录下）
- ✅ 配置文件格式：YAML（人类可读，易于编辑）
- ✅ 支持多个知识库配置（如多个语雀知识库）

### 3.2 通用插件基类（异步架构）

```python
# backend/app/plugins/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class PluginType(Enum):
    """插件类型枚举"""
    DATASOURCE = "datasource"       # 数据源插件
    AI_MODEL = "ai_model"           # AI模型插件（架构预留）
    SEARCH_ENGINE = "search_engine" # 搜索引擎插件（预留）
    CONTENT_PARSER = "content_parser"  # 内容解析器插件（预留）

class BasePlugin(ABC):
    """插件基类，所有插件的父类（异步架构）"""

    @classmethod
    @abstractmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """
        返回插件元数据

        Returns:
            Dict[str, Any]: 包含以下键的字典:
                - id: 插件唯一标识（必填）
                - name: 显示名称（必填）
                - version: 版本号（必填，semver格式）
                - type: 插件类型（必填，见PluginType）
                - author: 作者（必填）
                - description: 描述（必填）
        """
        pass

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化插件

        Args:
            config: 插件配置参数（从 PluginConfig 获取）

        Returns:
            bool: 初始化是否成功
        """
        pass

    @abstractmethod
    async def cleanup(self):
        """清理资源（关闭连接、释放句柄等）"""
        pass

    def get_status(self) -> Dict[str, Any]:
        """
        获取插件运行状态（可选实现）

        Returns:
            Dict[str, Any]: 状态信息
        """
        return {"status": "running", "health": "healthy"}

    async def health_check(self) -> bool:
        """健康检查（可选实现）"""
            bool: 是否健康
        """
        return True
```

### 3.2 数据源插件接口（同步模式 + 异步架构）

**设计理念**：数据源插件的核心职责是**将外部数据同步到本地文件系统**，后续的文件扫描、索引、搜索流程完全复用现有实现。

```python
# backend/app/plugins/interface/datasource.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pathlib import Path
import logging
from ..base import BasePlugin

logger = logging.getLogger(__name__)

class DataSourcePlugin(BasePlugin):
    """
    数据源插件接口（异步架构）

    核心职责：将外部数据源同步到本地文件系统
    后续流程：复用现有的 FileScanner + FileIndexService
    """

    @classmethod
    @abstractmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """返回插件元数据"""
        pass

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化插件

        Args:
            config: 插件配置参数（从 PluginConfig 获取）

        Returns:
            bool: 初始化是否成功
        """
        pass

    @abstractmethod
    async def sync(self) -> bool:
        """
        同步外部数据到本地文件系统（核心方法）

        工作流程：
        1. 从外部数据源（如语雀API）获取数据
        2. 保存为本地文件（Markdown、PDF等）
        3. 保存到插件的 data/ 目录下

        Returns:
            bool: 同步是否成功
        """
        pass

    def get_file_source_info(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        获取文件的数据源信息（索引时调用）

        由插件自己实现提取逻辑，实现解耦：
        - 插件最了解自己的文件格式
        - 索引服务不需要硬编码提取规则

        Args:
            file_path: 文件路径
            content: 文件内容

        Returns:
            Dict[str, Any]: 包含以下键的字典:
                - source_type: 数据源类型（如 "yuque", "feishu"）
                - source_url: 原始文档URL（可选）
        """
        # 默认实现：返回空（子类可以覆盖）
        return {"source_type": None, "source_url": None}

    @abstractmethod
    async def cleanup(self):
        """清理资源"""
        pass
```

**插件核心职责**：
1. **初始化** (`initialize`) - 检测工具、准备目录、验证配置
2. **同步** (`sync`) - 调用外部工具下载数据到本地
3. **提供元数据** (`get_file_source_info`) - 为索引服务提供数据源信息

**插件不做的事情**：
- ❌ 不主动执行同步（由用户通过 API 触发）
- ❌ 不返回同步目录（用户在配置文件中指定，索引时手动填写）
- ❌ 不触发索引构建（由用户单独调用索引 API）

**工作流程图**：

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户操作层                                │
│                                                                   │
│  1. 配置插件 (config.yaml)                                       │
│  2. 调用插件同步 API（手动触发）                                   │
│  3. 调用索引构建 API（手动触发，指定插件目录）                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        插件层                                    │
│  YuqueDataSource                                                │
│  ├─ initialize() → 检测 yuque-dl 工具                           │
│  └─ sync() → 调用 yuque-dl 下载文件                             │
│      → data/plugins/datasource/yuque/data/product/              │
│      → data/plugins/datasource/yuque/data/tech/                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        本地文件系统                                │
│  用户手动指定这些目录进行索引:                                     │
│  - data/plugins/datasource/yuque/data/product/*.md             │
│  - data/plugins/datasource/yuque/data/tech/*.md                │
└─────────────────────────────────────────────────────────────────┘
```

**设计优势**：
- ✅ **极简设计**：插件只做下载，职责单一
- ✅ **用户控制**：所有操作由用户手动触发
- ✅ **透明清晰**：用户完全了解数据流向
- ✅ **易于调试**：同步后的文件可直接查看
- ✅ **异步优先**：遵循现有异步架构

### 3.3 AI模型插件接口（架构预留）

```python
# backend/app/plugins/interface/ai_model.py
from abc import ABC, abstractmethod
from typing import Dict, Any
from ..base import BasePlugin

class AIModelPlugin(BasePlugin):
    """AI模型插件接口（本版本不实现，仅架构预留）"""

    @classmethod
    @abstractmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """返回插件元数据"""
        pass

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        pass

    @abstractmethod
    async def cleanup(self):
        """清理资源"""
        pass

    # 以下方法在后续版本实现
    # async def chat(self, messages, **kwargs): ...
    # async def embedding(self, text, **kwargs): ...
```

### 3.4 插件加载器

```python
# backend/app/plugins/loader.py
from typing import Dict, Optional, Type
from pathlib import Path
import importlib.util
import sys
from .base import BasePlugin, PluginType
from app.core.logging_config import logger

class PluginLoader:
    """插件加载器 - 支持多种插件类型"""

    def __init__(self, plugin_dir: Path):
        self.plugin_dir = plugin_dir
        self._loaded_plugins: Dict[str, BasePlugin] = {}
        self._plugin_configs: Dict[str, Dict[str, Any]] = {}
        self._plugin_types: Dict[str, str] = {}  # plugin_id -> plugin_type

    async def discover_and_load_all(self) -> Dict[str, BasePlugin]:
        """
        发现并加载所有插件

        Returns:
            Dict[str, BasePlugin]: 插件ID到插件实例的映射
        """
        logger.info(f"开始扫描插件目录: {self.plugin_dir}")

        # 遍历所有插件类型目录
        plugin_type_dirs = [
            (PluginType.DATASOURCE, "datasource"),
        ]

        for plugin_type, type_dir_name in plugin_type_dirs:
            type_dir = self.plugin_dir / type_dir_name
            if not type_dir.exists():
                logger.debug(f"插件类型目录不存在: {type_dir}")
                continue

            await self._load_plugins_from_dir(type_dir, plugin_type)

        logger.info(f"插件加载完成，共加载 {len(self._loaded_plugins)} 个插件")
        return self._loaded_plugins

    async def _load_plugins_from_dir(self, type_dir: Path, plugin_type: PluginType):
        """从指定目录加载插件"""
        for plugin_path in type_dir.iterdir():
            if not plugin_path.is_dir():
                continue

            # 跳过隐藏目录
            if plugin_path.name.startswith('.'):
                continue

            # 检查必需文件
            plugin_file = plugin_path / "plugin.py"
            config_file = plugin_path / "config.yaml"

            if not plugin_file.exists():
                logger.warning(f"插件目录缺少plugin.py: {plugin_path}")
                continue

            if not config_file.exists():
                logger.warning(f"插件目录缺少config.yaml: {plugin_path}")
                continue

            # 加载插件
            await self._load_plugin(plugin_path, plugin_type)

    async def _load_plugin(self, plugin_path: Path, plugin_type: PluginType):
        """加载单个插件"""
        plugin_id = plugin_path.name

        try:
            # 1. 读取配置文件
            config = self._load_config(plugin_path / "config.yaml")

            # 检查是否启用
            if not config.get("plugin", {}).get("enabled", False):
                logger.info(f"插件已禁用: {plugin_id}")
                return

            # 验证插件类型匹配
            config_type = config.get("plugin", {}).get("type")
            if config_type != plugin_type.value:
                logger.warning(f"插件类型不匹配: {plugin_id} (配置:{config_type}, 目录:{plugin_type.value})")
                return

            # 2. 动态导入插件模块
            plugin_file = plugin_path / "plugin.py"
            spec = importlib.util.spec_from_file_location(
                f"plugin_{plugin_type.value}_{plugin_id}",
                plugin_file
            )
            if spec is None or spec.loader is None:
                logger.error(f"无法加载插件模块: {plugin_id}")
                return

            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            # 3. 查找插件类
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    issubclass(attr, BasePlugin) and
                    attr != BasePlugin):
                    plugin_class = attr
                    break

            if plugin_class is None:
                logger.error(f"未找到插件类: {plugin_id}")
                return

            # 4. 实例化并初始化插件
            plugin_instance = plugin_class()

            # 获取特定类型的配置
            plugin_config = config.get("datasource", {})

            if not await plugin_instance.initialize(plugin_config):
                logger.error(f"插件初始化失败: {plugin_id}")
                return

            self._loaded_plugins[plugin_id] = plugin_instance
            self._plugin_configs[plugin_id] = config
            self._plugin_types[plugin_id] = plugin_type.value

            logger.info(f"插件加载成功: {plugin_id} (类型: {plugin_type.value})")

        except Exception as e:
            logger.error(f"加载插件失败 {plugin_id}: {e}")

    def _load_config(self, config_file: Path) -> Dict[str, Any]:
        """加载配置文件"""
        import yaml
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def get_plugin(self, plugin_id: str) -> Optional[BasePlugin]:
        """获取插件实例"""
        return self._loaded_plugins.get(plugin_id)

    def get_plugins_by_type(self, plugin_type: str) -> Dict[str, BasePlugin]:
        """按类型获取插件"""
        return {
            pid: plugin
            for pid, plugin in self._loaded_plugins.items()
            if self._plugin_types.get(pid) == plugin_type
        }

    async def cleanup_all(self):
        """清理所有插件"""
        for plugin_id, plugin in self._loaded_plugins.items():
            try:
                await plugin.cleanup()
            except Exception as e:
                logger.error(f"清理插件失败 {plugin_id}: {e}")

        self._loaded_plugins.clear()
```

---

## 4. 语雀数据源插件实现（yuque-dl CLI集成）

### 4.1 设计思路

**核心决策**：采用 CLI 工具集成方式，而非直接调用语雀 API。

**理由**：
- ✅ **开发快速**：节省 3-5 天 API 客户端开发时间
- ✅ **功能完整**：yuque-dl 支持增量下载、断点续传、附件下载
- ✅ **维护成本低**：API 变更由 yuque-dl 维护者处理
- ✅ **稳定性高**：利用成熟的开源工具

**工作流程**：
```
1. 检测 yuque-dl 工具是否可用（npx 或全局安装）
2. 调用 yuque-dl 下载知识库到本地目录
3. 返回下载目录路径，供 FileSystemDataSource 扫描
4. 后续索引和搜索流程完全复用现有实现
```

### 4.2 配置文件（支持多个知识库）

```yaml
# data/plugins/datasource/yuque/config.yaml
plugin:
  id: yuque
  name: 语雀知识库
  version: "1.0.0"
  type: datasource
  enabled: true

# 知识库配置列表（支持多个知识库）
repos:
  # 知识库 1：产品文档
  - name: "产品文档"
    url: "https://www.yuque.com/your-org/product-docs"
    download_dir: "./data/product-docs"
    token: ""  # 可选，私有知识库需要
    cookie_key: "_yuque_session"  # 可选，企业部署
    ignore_images: false
    incremental: true

  # 知识库 2：技术文档
  - name: "技术文档"
    url: "https://www.yuque.com/your-org/tech-docs"
    download_dir: "./data/tech-docs"
    token: ""
    ignore_images: false
    incremental: true

  # 知识库 3：设计文档
  - name: "设计文档"
    url: "https://www.yuque.com/your-org/design-docs"
    download_dir: "./data/design-docs"
    token: ""
    ignore_images: true  # 设计文档可能图片较多，可选择忽略
    incremental: true
```

**配置说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | 知识库名称（用于标识） |
| `url` | string | ✅ | 语雀知识库 URL |
| `download_dir` | string | ✅ | 下载目录（相对于插件目录） |
| `token` | string | ❌ | 语雀 Cookie（私有知识库需要） |
| `cookie_key` | string | ❌ | 企业部署的 Cookie Key（默认 `_yuque_session`） |
| `ignore_images` | boolean | ❌ | 是否忽略图片（默认 false） |
| `incremental` | boolean | ❌ | 是否增量下载（默认 true） |

```

### 4.3 插件实现（简化版 - 仅同步）

```python
# data/plugins/datasource/yuque/plugin.py
import asyncio
import os
from pathlib import Path
from typing import Dict, Any, List

from app.plugins.interface.datasource import DataSourcePlugin
from app.core.logging_config import logger


class YuqueDataSource(DataSourcePlugin):
    """
    语雀知识库数据源插件（基于 yuque-dl CLI 工具）

    插件只做两件事：
    1. 初始化 - 检测 yuque-dl 工具、准备目录
    2. 同步 - 调用 yuque-dl 下载文件到本地

    支持多个知识库配置
    """

    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._yuque_dl_path: str = None
        self._plugin_dir: Path = None
        self._repos: List[Dict[str, Any]] = []  # 多个知识库配置

    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        return {
            "id": "yuque",
            "name": "语雀知识库",
            "version": "1.0.0",
            "type": "datasource",
            "author": "XiaoyaoSearch Team",
            "description": "基于 yuque-dl 的语雀知识库文档同步（支持多知识库）",
            "datasource_type": "yuque",
            "dependencies": ["Node.js 18.4+", "yuque-dl"]
        }

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化插件

        只做准备工作：
        - 检测 yuque-dl 工具是否可用
        - 创建下载目录
        - 验证配置有效性
        """
        try:
            self._config = config
            self._plugin_dir = Path(__file__).parent

            # 获取知识库配置列表
            self._repos = config.get("repos", [])
            if not self._repos:
                logger.warning("未配置任何知识库，请在 config.yaml 中添加 repos 配置")
                return False

            # 初始化每个知识库的下载目录
            for repo in self._repos:
                download_dir_rel = repo.get("download_dir", f"./data/{repo.get('name', 'default')}")
                download_dir = self._plugin_dir / download_dir_rel
                download_dir.mkdir(parents=True, exist_ok=True)
                repo["_download_dir"] = download_dir  # 保存绝对路径
                logger.info(f"准备下载目录: {download_dir}")

            # 检测 yuque-dl 工具
            self._yuque_dl_path = await self._find_yuque_dl()
            if not self._yuque_dl_path:
                logger.error(
                    "未找到 yuque-dl 工具，请安装: npm install -g yuque-dl "
                    "或确保 Node.js 18.4+ 已安装以使用 npx"
                )
                return False

            logger.info(f"语雀数据源初始化成功，使用: {self._yuque_dl_path}")
            logger.info(f"已配置 {len(self._repos)} 个知识库，等待手动同步")
            return True

        except Exception as e:
            logger.error(f"语雀数据源初始化失败: {e}")
            return False

    async def _find_yuque_dl(self) -> str:
        """查找 yuque-dl 可执行文件"""
        # 1. 检查 npx（优先，因为不需要全局安装）
        if await self._check_command("npx yuque-dl --version"):
            return "npx yuque-dl"

        # 2. 检查全局安装的 yuque-dl
        if await self._check_command("yuque-dl --version"):
            return "yuque-dl"

        # 3. 检查配置文件中指定的路径
        custom_path = self._config.get("yuque_dl_path")
        if custom_path and os.path.exists(custom_path):
            return custom_path

        return None

    async def _check_command(self, cmd: str) -> bool:
        """检查命令是否可用"""
        try:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            return proc.returncode == 0
        except Exception:
            return False

    async def sync(self) -> bool:
        """
        同步所有配置的语雀知识库到本地目录（核心方法）

        Returns:
            bool: 所有知识库同步是否都成功
        """
        all_success = True
        total_files = 0

        for repo in self._repos:
            repo_name = repo.get("name", "unknown")
            logger.info(f"开始同步知识库: {repo_name}")

            try:
                cmd = self._build_yuque_dl_command(repo)
                logger.debug(f"执行命令: {' '.join(cmd)}")

                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                stdout, stderr = await process.communicate()

                if process.returncode != 0:
                    error_msg = stderr.decode("utf-8", errors="ignore")
                    logger.error(f"知识库 {repo_name} 同步失败: {error_msg}")
                    all_success = False
                    continue

                # 统计下载的文件数
                download_dir = repo["_download_dir"]
                file_count = sum(1 for _ in download_dir.rglob("*.md"))
                total_files += file_count
                logger.info(f"知识库 {repo_name} 同步成功，共 {file_count} 个文件")

            except Exception as e:
                logger.error(f"知识库 {repo_name} 同步异常: {e}")
                all_success = False

        logger.info(f"语雀知识库同步完成，总计 {total_files} 个文件")
        return all_success

    def _build_yuque_dl_command(self, repo: Dict[str, Any]) -> List[str]:
        """构建单个知识库的 yuque-dl 命令"""
        cmd = []

        # 添加命令前缀（npx 或直接命令）
        if self._yuque_dl_path.startswith("npx"):
            cmd.extend(["npx", "yuque-dl"])
        else:
            cmd.append(self._yuque_dl_path)

        # 添加知识库 URL
        cmd.append(repo["url"])

        # 添加输出目录
        download_dir = repo["_download_dir"]
        cmd.extend(["-d", str(download_dir)])

        # 添加认证 token（如果配置了）
        token = repo.get("token")
        if token:
            cmd.extend(["-t", token])

        # 如果是企业部署，指定 cookie key
        cookie_key = repo.get("cookie_key", "_yuque_session")
        if cookie_key != "_yuque_session":
            cmd.extend(["-k", cookie_key])

        # 是否忽略图片
        if repo.get("ignore_images", False):
            cmd.append("--ignoreImg")

        # 是否增量下载
        if repo.get("incremental", True):
            cmd.append("--incremental")

        return cmd

    async def cleanup(self):
        """清理资源"""
        pass

    def get_file_source_info(self, file_path: str, content: str) -> dict:
        """
        获取语雀文档的数据源信息（索引时调用）

        语雀文档底部包含：原文: <https://www.yuque.com/...>

        Args:
            file_path: 文件路径
            content: 文件内容

        Returns:
            dict: {source_type, source_url}
        """
        import re

        # 从文件路径判断（双重确认）
        path_str = str(file_path).replace("\\", "/")
        if "data/plugins/datasource/yuque/" not in path_str:
            return {"source_type": None, "source_url": None}

        # 从文件内容提取原始URL
        source_url = None
        yuque_pattern = r'原文:\s*<(https://www\.yuque\.com/[^>]+)>'
        match = re.search(yuque_pattern, content)
        if match:
            source_url = match.group(1).strip()

        return {
            "source_type": "yuque",
            "source_url": source_url
        }
```

### 4.4 requirements.txt

```txt
# data/plugins/datasource/yuque/requirements.txt
# 语雀数据源插件依赖

# 外部依赖（需要在系统环境安装）：
# - Node.js 18.4+
# - yuque-dl (npm install -g yuque-dl)

# Python 依赖：
pyyaml>=6.0
```

### 4.5 README.md

```markdown
# 语雀知识库插件

基于 [yuque-dl](https://github.com/gxr404/yuque-dl) 的语雀知识库数据源插件。

## 安装依赖

### 1. 安装 Node.js

确保系统已安装 Node.js 18.4 或更高版本：

```bash
node --version
```

### 2. 安装 yuque-dl

```bash
npm install -g yuque-dl
```

或使用 npx（无需全局安装）：

```bash
npx yuque-dl --version
```

## 配置说明

编辑 `config.yaml` 文件：

```yaml
yuque_dl:
  # 知识库 URL
  repo_url: "https://www.yuque.com/your-org/repo"

  # 语雀 Cookie（访问私有知识库需要）
  # 获取方式：浏览器 DevTools -> Application -> Cookies -> _yuque_session
  token: ""
```

## 使用场景

| 场景 | 配置说明 |
|------|---------|
| 公开知识库 | 仅需配置 `repo_url` |
| 私有知识库 | 需配置 `token`（`_yuque_session` Cookie） |
| 企业部署 | 需配置 `cookie_key` 和 `token` |
| 密码保护知识库 | 输入密码后获取对应 Cookie |

## 获取 Cookie

1. 登录语雀
2. 打开浏览器 DevTools（F12）
3. 进入 Application -> Cookies -> https://www.yuque.com
4. 找到 `_yuque_session`，复制其值

## 支持的功能

- ✅ 增量下载（仅下载新增/修改的文档）
- ✅ 断点续传（中断后可继续下载）
- ✅ 图片下载
- ✅ 附件下载
- ✅ TOC 目录生成
```

---

## 5. 数据源信息提取

### 5.1 设计原则

**核心思路**：由插件自己提供数据源信息，实现完全解耦。

**优势**：
- ✅ **插件最了解自己的格式**：每个数据源的文件格式和元数据位置不同，由插件自己实现最准确
- ✅ **索引服务无需修改**：添加新数据源时，不需要修改索引服务代码
- ✅ **易于扩展**：新插件只需实现 `get_file_source_info()` 方法

### 5.2 插件接口方法

```python
# backend/app/plugins/interface/datasource.py

class DataSourcePlugin(BasePlugin):
    # ... 其他方法 ...

    def get_file_source_info(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        获取文件的数据源信息（索引时调用）

        Args:
            file_path: 文件路径
            content: 文件内容

        Returns:
            Dict[str, Any]:
                - source_type: 数据源类型（如 "yuque", "feishu"）
                - source_url: 原始文档URL（可选）
        """
        # 默认实现：返回空（子类覆盖）
        return {"source_type": None, "source_url": None}
```

### 5.3 语雀插件实现示例

```python
# data/plugins/datasource/yuque/plugin.py

import re

class YuqueDataSource(DataSourcePlugin):
    # ... 其他方法 ...

    def get_file_source_info(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        获取语雀文档的数据源信息

        语雀文档底部包含：原文: <https://www.yuque.com/...>
        """
        # 从文件路径判断（双重确认）
        if "data/plugins/datasource/yuque/" not in file_path.replace("\\", "/"):
            return {"source_type": None, "source_url": None}

        # 从文件内容提取原始URL
        source_url = None
        yuque_pattern = r'原文:\s*<(https://www\.yuque\.com/[^>]+)>'
        match = re.search(yuque_pattern, content)
        if match:
            source_url = match.group(1).strip()

        return {
            "source_type": "yuque",
            "source_url": source_url
        }
```

### 5.4 FileModel 字段扩展

```python
# backend/app/models/file.py 新增字段

class FileModel(Base):
    """文件索引表模型（扩展）"""

    # ... 现有字段 ...

    # ========== 新增：数据源相关字段 ==========
    source_type = Column(String(50), default="filesystem", comment="数据源类型(filesystem/yuque/feishu)")
    source_url = Column(String(1000), nullable=True, comment="原始文档URL（用于外部数据源）")
    # ========================================
```

**字段获取方式**：

| 字段 | 获取方式 | 说明 |
|------|---------|------|
| `source_type` | 调用插件的 `get_file_source_info()` 方法 | 每个插件返回自己的 source_type |
| `source_url` | 调用插件的 `get_file_source_info()` 方法 | 每个插件从文件内容提取自己的 URL 格式 |

---

## 6. 应用启动集成（基于现有 main.py）

### 6.1 lifespan 函数扩展

在现有的 `main.py` lifespan 中添加插件加载逻辑：

```python
# backend/main.py 扩展

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理（扩展）

    新增：插件系统初始化
    """
    logger.info("=" * 50)
    logger.info("小遥搜索服务启动中...")
    logger.info("=" * 50)

    try:
        # ========== 现有初始化逻辑 ==========
        # 初始化数据库
        logger.info("初始化数据库...")
        init_database()
        logger.info("数据库初始化完成")

        # 初始化AI模型服务
        logger.info("加载AI模型...")
        try:
            from app.services.ai_model_manager import ai_model_service
            await ai_model_service.initialize()
            ai_model_service._initialized = True
            logger.info("AI模型服务加载完成")
        except Exception as e:
            logger.warning(f"AI模型服务初始化失败: {str(e)}")
            logger.info("继续运行，但AI功能可能不可用")
            try:
                ai_model_service._initialized = False
            except:
                pass

        # 初始化索引缓存
        logger.info("初始化索引缓存...")
        try:
            from app.services.file_index_service import get_file_index_service
            index_service = get_file_index_service()
            await index_service.load_indexed_files_cache()
            logger.info("索引缓存初始化完成")
        except Exception as e:
            logger.warning(f"索引缓存初始化失败: {str(e)}")
            logger.info("继续运行，但首次增量更新可能较慢")

        # ========== 新增：插件系统初始化 ==========
        logger.info("初始化插件系统...")
        try:
            from app.plugins.loader import PluginLoader
            from app.core.config import get_settings

            settings = get_settings()
            plugin_dir = Path(settings.plugin.plugin_dir)
            plugin_dir.mkdir(parents=True, exist_ok=True)

            # 创建插件加载器
            app.state.plugin_loader = PluginLoader(plugin_dir)

            # 发现并加载所有插件
            loaded_plugins = await app.state.plugin_loader.discover_and_load_all()
            logger.info(f"✅ 插件系统启动完成，已加载 {len(loaded_plugins)} 个插件")

            # 自动执行数据源插件的同步（增量更新）
            for plugin_id, plugin in loaded_plugins.items():
                if hasattr(plugin, 'sync'):
                    logger.info(f"自动执行插件同步: {plugin_id}")
                    sync_result = await plugin.sync()
                    if sync_result:
                        logger.info(f"✅ 插件 {plugin_id} 同步完成")
                    else:
                        logger.warning(f"⚠️ 插件 {plugin_id} 同步失败")

        except Exception as e:
            logger.error(f"插件系统初始化失败: {str(e)}")
            logger.info("继续运行，但插件功能不可用")
        # =====================================

        logger.info("✅ 小遥搜索服务启动完成")
        logger.info(f"📖 API文档: http://127.0.0.1:8000/docs")
        logger.info(f"📋 ReDoc文档: http://127.0.0.1:8000/redoc")

    except Exception as e:
        logger.error(f"❌ 服务启动失败: {str(e)}")
        raise

    yield

    # 关闭时执行
    logger.info("小遥搜索服务关闭中...")
    try:
        # 新增：清理插件
        if hasattr(app.state, 'plugin_loader'):
            await app.state.plugin_loader.cleanup_all()
            logger.info("插件资源清理完成")

        logger.info("资源清理完成")
    except Exception as e:
        logger.error(f"资源清理失败: {str(e)}")
```

### 6.2 索引构建时机与方式

**核心原则**：
- 应用启动时自动执行插件同步（增量更新）
- 用户手动触发索引构建，明确指定需要索引的目录

**工作流程**：

```
┌─────────────────────────────────────────────────────────────────┐
│                      应用启动时                                  │
├─────────────────────────────────────────────────────────────────┤
│  1. 插件加载器发现并加载插件                                      │
│  2. 数据源插件执行 sync() → 增量下载文件到本地                     │
│     └─ yuque-dl --incremental (只下载新增/修改的文件)               │
│  3. 显示同步目录信息（仅供参考）                                  │
│  4. [不自动构建索引]                                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ 用户需要搜索时
┌─────────────────────────────────────────────────────────────────┐
│                      用户手动触发索引构建                          │
├─────────────────────────────────────────────────────────────────┤
│  用户需要明确指定所有需要索引的目录：                              │
│                                                                  │
│  # 索引用户目录                                                   │
│  POST /api/index/create                                          │
│  { "folder_path": "D:/Documents", "recursive": true }            │
│                                                                  │
│  # 索引语雀产品文档（插件同步的目录）                               │
│  POST /api/index/create                                          │
│  { "folder_path": "data/plugins/datasource/yuque/data/product" } │
│                                                                  │
│  # 索引语雀技术文档                                               │
│  POST /api/index/create                                          │
│  { "folder_path": "data/plugins/datasource/yuque/data/tech" }    │
└─────────────────────────────────────────────────────────────────┘
```

**启动时自动同步的好处**：

| 好处 | 说明 |
|------|------|
| **自动更新** | 启动时自动获取最新文档 |
| **增量下载** | yuque-dl 的 `--incremental` 只下载变化部分 |
| **无需手动** | 用户无需手动触发同步 |
| **保持最新** | 每次启动都有最新的外部数据 |
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ 用户需要搜索时
┌─────────────────────────────────────────────────────────────────┐
│                      用户手动触发索引构建                          │
├─────────────────────────────────────────────────────────────────┤
│  用户需要明确指定所有需要索引的目录：                              │
│                                                                  │
│  调用 1: 索引用户目录                                             │
│  POST /api/index/create                                          │
│  {                                                                │
│    "folder_path": "D:/Documents",                                │
│    "recursive": true                                             │
│  }                                                                │
│                                                                  │
│  调用 2: 索引插件目录（如需要）                                    │
│  POST /api/index/create                                          │
│  {                                                                │
│    "folder_path": "data/plugins/datasource/yuque/data/product", │
│    "recursive": true                                             │
│  }                                                                │
│                                                                  │
│  调用 3: 索引另一个插件目录（如需要）                              │
│  POST /api/index/create                                          │
│  {                                                                │
│    "folder_path": "data/plugins/datasource/yuque/data/tech",    │
│    "recursive": true                                             │
│  }                                                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      索引构建                                    │
├─────────────────────────────────────────────────────────────────┤
│  FileIndexService.build_index()                                  │
│  └── 构建索引 (Faiss + Whoosh)                                   │
└─────────────────────────────────────────────────────────────────┘
```

**API 调用示例**：

```bash
# 用户需要分别调用索引 API，明确指定每个目录

# 1. 索引用户文档
curl -X POST "http://127.0.0.1:8000/api/index/create" \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "D:/Documents", "recursive": true}'

# 2. 索引语雀产品文档（插件同步的目录）
curl -X POST "http://127.0.0.1:8000/api/index/create" \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "data/plugins/datasource/yuque/data/product", "recursive": true}'

# 3. 索引语雀技术文档
curl -X POST "http://127.0.0.1:8000/api/index/create" \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "data/plugins/datasource/yuque/data/tech", "recursive": true}'
```

**为什么手动指定？**

| 优势 | 说明 |
|------|------|
| **用户可控** | 用户明确知道哪些目录被索引 |
| **灵活性** | 用户可以选择只索引部分插件目录 |
| **透明性** | 索引范围完全由用户决定 |
| **避免意外** | 不会意外索引不需要的文件 |

---
        recursive=request.recursive,
        file_types=request.file_types
    )

    return IndexCreateResponse(task_id=task_id)
```

**为什么不在启动时自动构建索引？**

| 方案 | 优点 | 缺点 |
|------|------|------|
| **启动时自动构建** | 无需手动操作 | 启动时间长、消耗资源、用户可能不需要 |
| **手动触发构建** | 用户可控、按需构建 | 需要手动操作一次 |

**推荐方案**：手动触发 + 自动包含插件目录

- ✅ 启动快速：只同步文件，不构建索引
- ✅ 按需构建：用户需要时才构建索引
- ✅ 自动包含：无需手动指定插件目录
- ✅ 增量更新：后续增量索引自动包含插件目录

---
- ✅ 每个插件有自己的配置文件（YAML 格式）
- ✅ 语雀插件支持多个知识库配置

---

## 7. 数据库变更（基于现有 FileModel）

### 7.1 FileModel 扩展

当前 `FileModel` ([models/file.py](backend/app/models/file.py)) 已有完善的字段设计，需要添加两个数据源相关字段：

```python
# backend/app/models/file.py 新增字段

class FileModel(Base):
    """文件索引表模型（扩展）"""
    __tablename__ = "files"

    # ... 现有字段保持不变 ...

    # ========== 新增：数据源相关字段 ==========
    source_type = Column(String(50), default="filesystem", comment="数据源类型(filesystem/yuque/feishu)")
    source_url = Column(String(1000), nullable=True, comment="原始文档URL（用于外部数据源）")
    # ========================================
```

### 7.2 数据库迁移 SQL

```sql
-- 为现有 files 表添加数据源相关字段
ALTER TABLE files ADD COLUMN source_type TEXT DEFAULT 'filesystem';
ALTER TABLE files ADD COLUMN source_url TEXT;

-- 创建索引（可选，如果需要按数据源类型筛选）
CREATE INDEX IF NOT EXISTS idx_files_source_type ON files(source_type);
```

### 7.3 索引服务适配

`FileIndexService` 需要在索引时调用插件方法获取数据源信息：

```python
# backend/app/services/file_index_service.py 扩展

class FileIndexService:
    """文件索引服务（扩展）"""

    def __init__(self):
        # ... 现有代码 ...
        self._plugin_loader = None  # 插件加载器引用

    def set_plugin_loader(self, plugin_loader):
        """设置插件加载器引用（由 main.py 在启动时注入）"""
        self._plugin_loader = plugin_loader

    async def _extract_source_info(self, file_path: str, content: str) -> dict:
        """
        提取数据源信息（调用插件方法）

        Returns:
            dict: {source_type, source_url}
        """
        # 默认值（本地文件）
        source_info = {"source_type": "filesystem", "source_url": None}

        # 如果没有插件加载器，返回默认值
        if not self._plugin_loader:
            return source_info

        # 遍历所有数据源插件，找到能处理此文件的插件
        datasource_plugins = self._plugin_loader.get_plugins_by_type("datasource")
        for plugin_id, plugin in datasource_plugins.items():
            try:
                # 调用插件的 get_file_source_info 方法
                plugin_info = plugin.get_file_source_info(file_path, content)
                if plugin_info.get("source_type"):
                    # 插件成功返回信息，使用插件的结果
                    return plugin_info
            except Exception as e:
                # 插件调用失败，继续尝试下一个插件
                from app.core.logging_config import logger
                logger.warning(f"插件 {plugin_id} 获取源信息失败: {e}")
                continue

        return source_info

    async def _save_to_database(self, file_info: FileInfo, content: str) -> FileModel:
        """保存到数据库（扩展）"""
        # ... 现有逻辑 ...

        # 新增：调用插件方法提取数据源信息
        source_info = await self._extract_source_info(str(file_path), content)
        file_model.source_type = source_info["source_type"]
        file_model.source_url = source_info["source_url"]

        # ... 其余逻辑 ...
```

**main.py 启动时注入插件加载器**：

```python
# backend/main.py 扩展

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... 现有初始化逻辑 ...

    # ========== 插件系统初始化 ==========
    logger.info("初始化插件系统...")
    try:
        from app.plugins.loader import PluginLoader
        from app.core.config import get_settings

        settings = get_settings()
        plugin_dir = Path(settings.plugin.plugin_dir)
        plugin_dir.mkdir(parents=True, exist_ok=True)

        # 创建插件加载器
        app.state.plugin_loader = PluginLoader(plugin_dir)

        # 发现并加载所有插件
        loaded_plugins = await app.state.plugin_loader.discover_and_load_all()
        logger.info(f"✅ 插件系统启动完成，已加载 {len(loaded_plugins)} 个插件")

        # 注入到索引服务
        from app.services.file_index_service import get_file_index_service
        index_service = get_file_index_service()
        index_service.set_plugin_loader(app.state.plugin_loader)

        # 自动执行数据源插件的同步（增量更新）
        for plugin_id, plugin in loaded_plugins.items():
            if hasattr(plugin, 'sync'):
                logger.info(f"自动执行插件同步: {plugin_id}")
                sync_result = await plugin.sync()
                if sync_result:
                    logger.info(f"✅ 插件 {plugin_id} 同步完成")
                else:
                    logger.warning(f"⚠️ 插件 {plugin_id} 同步失败")

    except Exception as e:
        logger.error(f"插件系统初始化失败: {str(e)}")
        logger.info("继续运行，但插件功能不可用")
    # =====================================

    yield

    # ... 清理逻辑 ...
```

---

## 8. 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-02-22 | 初始版本（数据源插件专用） |
| v1.2 | 2026-02-22 | 约定优于配置版本 |
| v2.0 | 2026-02-22 | 通用插件系统架构 |
| v2.1 | 2026-02-22 | yuque-dl CLI集成方案 |
| v2.2 | 2026-02-22 | 同步模式简化设计 |
| v2.3 | 2026-02-22 | 基于实际后端实现适配 |
| v2.4 | 2026-02-22 | 配置简化与多知识库支持 |
| v2.5 | 2026-02-22 | 索引构建手动触发 |
| **v2.6** | **2026-02-22** | **插件极简化** |
| **v2.7** | **2026-02-22** | **启动时自动同步** |

### v2.7 主要变更（当前版本）

**启动时自动同步**：
- ✅ **自动增量更新**：应用启动时自动执行插件同步
- ✅ **增量下载**：yuque-dl 的 `--incremental` 只下载变化部分
- ✅ **无需手动**：用户无需手动触发同步
- ✅ **保持最新**：每次启动都有最新的外部数据

**工作流程**：
```
1. 应用启动 → 加载插件 → 自动执行同步（增量）
2. 用户需要搜索时 → 手动调用索引 API
```

### v2.6 主要变更

**插件极简化**：
- ✅ **只做两件事**：插件只负责初始化和同步
- ✅ **移除 get_sync_dirs()**：不再返回同步目录列表

### v2.5 主要变更

**索引构建方式调整**：
- ✅ **移除自动包含**：不再自动将插件目录加入索引范围
- ✅ **手动指定**：用户需要明确指定所有需要索引的目录
- ✅ **透明可控**：索引范围完全由用户决定
- ✅ **FileScanner 无需修改**：保持现有实现不变

### v2.4 主要变更

**配置简化**：
- ✅ **移除环境变量**：插件系统配置使用默认值，无需额外环境变量
- ✅ **独立配置文件**：每个插件有自己的 YAML 配置文件
- ✅ **约定优于配置**：插件目录结构固定，配置文件位置约定

**多知识库支持**：
- ✅ **语雀多知识库**：支持配置多个语雀知识库
- ✅ **独立下载目录**：每个知识库有独立的下载目录
- ✅ **批量同步**：一次同步所有配置的知识库

**配置示例**：
```yaml
repos:
  - name: "产品文档"
    url: "https://www.yuque.com/your-org/product"
    download_dir: "./data/product"
  - name: "技术文档"
    url: "https://www.yuque.com/your-org/tech"
    download_dir: "./data/tech"
```

### v2.3 主要变更

**适配现有后端架构**：
- ✅ **配置管理**：使用 Pydantic Settings (PluginConfig) 替代 YAML 文件
- ✅ **异步架构**：插件接口遵循现有 asyncio 异步模式
- ✅ **数据模型**：基于现有 FileModel 扩展，添加数据源相关字段
- ✅ **服务集成**：与 FileScanner、FileIndexService 无缝集成
- ✅ **启动流程**：在现有 main.py lifespan 中添加插件初始化

### v2.2 主要变更

- ✅ **插件接口简化**：移除 `scan()` 和 `get_content()` 方法
- ✅ **新增同步模式**：插件只负责 `sync()` 下载文件到本地
- ✅ **新增目录返回**：`get_sync_dirs()` 返回下载目录供 FileScanner 扫描
- ✅ **完全复用现有流程**：本地文件扫描、索引、搜索无需修改
- ✅ **移除 DataSourceItem**：不再需要抽象数据层
- ✅ **移除本地文件插件**：本地文件数据源保持现有实现
- ✅ **架构图更新**：清晰展示"插件同步→本地文件→现有流程"的数据流

### v2.1 主要变更

- ✅ 语雀插件改用 yuque-dl CLI 工具集成
- ✅ 移除 YuqueClient API 客户端
- ✅ 增加 yuque-dl 工具检测逻辑
- ✅ 增加 subprocess 命令调用
- ✅ 增加 Front Matter 元数据提取
- ✅ 简化配置文件，增加 yuque-dl 专属配置
- ✅ 增加 requirements.txt 说明外部依赖
- ✅ 增加 README.md 使用说明

### v2.0 主要变更

- ✅ 新增 `BasePlugin` 通用基类
- ✅ 新增 `AIModelPlugin` AI模型接口（架构预留）
- ✅ 新增 `PluginType` 插件类型枚举
- ✅ 插件目录按类型组织
- ✅ 配置文件支持插件类型标识
- ✅ PluginLoader支持多类型插件加载

---

**文档版本**: v2.7
**创建时间**: 2026-02-22
**最后更新**: 2026-02-22 (v2.7 - 启动时自动同步)
**维护者**: 开发者
