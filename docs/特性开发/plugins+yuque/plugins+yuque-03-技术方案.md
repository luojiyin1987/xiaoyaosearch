# 插件化架构与语雀数据源 - 技术方案

> **文档类型**：技术方案
> **特性状态**：规划中
> **创建时间**：2026-02-22
> **最后更新**：2026-02-22 (v2.1 - yuque-dl CLI集成)

---

## 1. 方案概述

### 1.1 技术目标

建立**通用插件化架构**，支持多种类型的插件扩展，包括数据源插件、AI模型插件等。优先实现数据源插件，语雀数据源采用 CLI 工具集成方案。

### 1.2 设计原则：约定优于配置

- **插件放置即安装**：插件文件放到`data/plugins/`目录下即自动发现
- **配置文件管理**：通过`config.yaml`文件配置，无需API
- **自动加载**：系统启动时自动扫描和加载插件
- **类型隔离**：不同类型插件独立目录、独立接口
- **简单优先**：移除所有不必要的复杂性

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
| PyYAML | 配置文件解析 | 人类可读，易于编辑 |
| asyncio subprocess | CLI工具调用 | 异步进程管理 |
| yuque-dl | 语雀数据获取 | 成熟开源工具，避免维护API |

---

## 2. 架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              API层                                       │
├─────────────────────────────────────────────────────────────────────────┤
│  /api/search (响应增加source_type、source_url、source_name)               │
└────────────┬──────────────────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────────────────┐
│                        服务层 (Service Layer)                             │
├───────────────────────────────────────────────────────────────────────────┤
│  PluginLoader  │  DataSourceManager  │  IndexService                     │
└────────────┬──────────────────────────────────────────┬───────────────────┘
             │                                          │
┌────────────▼──────────────────────────────────────────▼───────────────────┐
│                        插件层 (Plugin Layer)                                │
├───────────────────────────────────────────────────────────────────────────┤
│  BasePlugin(interface) - 通用插件基类                                      │
│  └─ DataSourcePlugin(interface)                                          │
│      ├─ FileSystemDataSource                                             │
│      └─ YuqueDataSource (yuque-dl CLI集成)                               │
│  └─ [AIModelPlugin - 架构预留]                                             │
└────────────┬──────────────────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────────────────┐
│                        数据层 (Data Layer)                                  │
├───────────────────────────────────────────────────────────────────────────┤
│  本地文件  │  yuque-dl CLI  │  Faiss索引  │  Whoosh  │  SQLite              │
└───────────────────────────────────────────────────────────────────────────┘
```

### 2.2 插件目录结构

```
data/plugins/
├── datasource/              # 数据源插件目录
│   ├── yuque/              # 语雀知识库插件
│   │   ├── plugin.py       # 插件实现
│   │   ├── config.yaml     # 配置文件
│   │   ├── requirements.txt # Python依赖（说明Node.js依赖）
│   │   └── data/           # 下载的数据目录
│   │       └── downloaded/ # yuque-dl 下载的markdown文件
│   ├── feishu/             # 飞书文档插件（未来）
│   └── filesystem/         # 本地文件插件
│
├── ai_model/               # AI模型插件目录（架构预留）
│
├── search_engine/          # 搜索引擎插件目录（未来）
│
├── content_parser/         # 内容解析器插件目录（未来）
│
└── auth/                   # 认证插件目录（未来）
```

### 2.3 模块划分

```
backend/
├── app/
│   ├── plugins/                          # 插件框架模块
│   │   ├── __init__.py
│   │   ├── base.py                      # 通用插件基类
│   │   ├── interface/                   # 插件接口定义集合
│   │   │   ├── __init__.py
│   │   │   ├── base.py                  # BasePlugin接口
│   │   │   ├── datasource.py            # DataSourcePlugin接口
│   │   │   └── ai_model.py              # AIModelPlugin接口（预留）
│   │   ├── loader.py                    # 插件加载器
│   │   └── config_parser.py             # 配置文件解析器
│   │
│   ├── services/
│   │   ├── datasource/                   # 数据源服务层
│   │   │   ├── __init__.py
│   │   │   ├── base.py                  # 基础数据项
│   │   │   ├── filesystem.py            # 本地文件数据源
│   │   │   └── manager.py               # 数据源管理器
│   │   └── unified_index_service.py      # 统一索引服务
│   │
│   └── core/
│       └── config.py                     # 配置扩展
│
└── data/
    └── plugins/                          # 插件目录
        └── datasource/
            └── yuque/
                ├── plugin.py
                ├── config.yaml
                ├── requirements.txt
                └── data/
                    └── downloaded/
```

---

## 3. 核心模块设计

### 3.1 通用插件基类

```python
# backend/app/plugins/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum

class PluginType(Enum):
    """插件类型枚举"""
    DATASOURCE = "datasource"       # 数据源插件
    AI_MODEL = "ai_model"           # AI模型插件（架构预留）
    SEARCH_ENGINE = "search_engine" # 搜索引擎插件（预留）
    CONTENT_PARSER = "content_parser"  # 内容解析器插件（预留）

class BasePlugin(ABC):
    """插件基类，所有插件的父类"""

    # 插件元数据（子类必须覆盖）
    metadata: Dict[str, Any] = None

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
            config: 从config.yaml读取的配置参数

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
        return {
            "status": "running",
            "health": "healthy"
        }

    async def health_check(self) -> bool:
        """
        健康检查（可选实现）

        Returns:
            bool: 是否健康
        """
        return True
```

### 3.2 数据源插件接口

```python
# backend/app/plugins/interface/datasource.py
from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncIterator, Optional
from dataclasses import dataclass
from datetime import datetime
from ..base import BasePlugin

@dataclass
class DataSourceItem:
    """标准化数据项"""
    id: str                              # 唯一标识
    title: str                           # 标题
    content: str                         # 内容
    source_type: str                     # 来源类型
    url: Optional[str] = None            # 访问URL
    author: Optional[str] = None         # 作者
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None      # 扩展元数据

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class DataSourcePlugin(BasePlugin):
    """数据源插件接口"""

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
    async def scan(self, **kwargs) -> AsyncIterator[DataSourceItem]:
        """
        扫描数据项（异步迭代器模式）

        Yields:
            DataSourceItem: 数据项
        """
        pass

    @abstractmethod
    async def get_content(self, item_id: str) -> Optional[str]:
        """
        获取单个数据项内容

        Args:
            item_id: 数据项ID

        Returns:
            Optional[str]: 内容文本，失败返回None
        """
        pass

    @abstractmethod
    async def cleanup(self):
        """清理资源"""
        pass
```

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
3. 扫描下载的 Markdown 文件
4. 从 Front Matter 提取元数据
5. 生成 DataSourceItem 流
```

### 4.2 配置文件

```yaml
# data/plugins/datasource/yuque/config.yaml
plugin:
  id: yuque
  name: 语雀知识库
  version: "1.0.0"
  type: datasource
  enabled: true

# yuque-dl 配置
yuque_dl:
  # 知识库 URL
  repo_url: "https://www.yuque.com/your-org/repo"

  # 下载目录（相对于插件目录）
  download_dir: "./data/downloaded"

  # 语雀 Cookie（用于访问私有知识库）
  # 获取方式：浏览器 DevTools -> Application -> Cookies -> _yuque_session
  token: ""

  # 企业部署的 Cookie Key（可选）
  # 企业版语雀的 cookie key 可能不是 _yuque_session
  cookie_key: "_yuque_session"

  # 是否忽略图片下载
  ignore_images: false

  # 是否启用增量下载
  incremental: true

  # 是否输出 TOC 目录
  toc: false

  # yuque-dl 可执行文件路径（可选，默认自动查找）
  # yuque_dl_path: "/usr/local/bin/yuque-dl"

# 同步配置
sync:
  # 自动同步间隔（秒），0 表示手动同步
  interval: 3600
  # 每次扫描的批次大小
  batch_size: 50
```

### 4.3 插件实现

```python
# data/plugins/datasource/yuque/plugin.py
import asyncio
import os
import re
from pathlib import Path
from typing import Dict, Any, AsyncIterator, Optional
from datetime import datetime

from app.plugins.interface.datasource import DataSourcePlugin, DataSourceItem
from app.core.logging_config import logger

import yaml


class YuqueDataSource(DataSourcePlugin):
    """语雀知识库数据源插件（基于 yuque-dl CLI 工具）"""

    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._yuque_dl_path: Optional[str] = None
        self._download_dir: Path = None
        self._plugin_dir: Path = None

    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        return {
            "id": "yuque",
            "name": "语雀知识库",
            "version": "1.0.0",
            "type": "datasource",
            "author": "XiaoyaoSearch Team",
            "description": "基于 yuque-dl 的语雀知识库文档搜索",
            "datasource_type": "yuque",
            "dependencies": ["Node.js 18.4+", "yuque-dl"]
        }

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        try:
            self._config = config
            self._plugin_dir = Path(__file__).parent

            # 获取下载目录
            download_dir_rel = config.get("download_dir", "./data/downloaded")
            self._download_dir = self._plugin_dir / download_dir_rel
            self._download_dir.mkdir(parents=True, exist_ok=True)

            # 检测 yuque-dl 工具
            self._yuque_dl_path = await self._find_yuque_dl()
            if not self._yuque_dl_path:
                logger.error(
                    "未找到 yuque-dl 工具，请安装: npm install -g yuque-dl "
                    "或确保 Node.js 18.4+ 已安装以使用 npx"
                )
                return False

            logger.info(f"语雀数据源初始化成功，使用: {self._yuque_dl_path}")
            return True

        except Exception as e:
            logger.error(f"语雀数据源初始化失败: {e}")
            return False

    async def _find_yuque_dl(self) -> Optional[str]:
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

    async def scan(self, **kwargs) -> AsyncIterator[DataSourceItem]:
        """扫描语雀文档"""
        try:
            # 1. 调用 yuque-dl 下载知识库
            await self._download_repo()

            # 2. 扫描下载的 Markdown 文件
            async for item in self._scan_downloaded_files():
                yield item

        except Exception as e:
            logger.error(f"扫描语雀文档失败: {e}")
            raise

    async def _download_repo(self) -> bool:
        """调用 yuque-dl 下载知识库"""
        cmd = self._build_yuque_dl_command()
        logger.info(f"运行命令: {' '.join(cmd)}")

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="ignore")
            logger.error(f"yuque-dl 执行失败: {error_msg}")
            return False

        logger.info(f"yuque-dl 执行成功")
        return True

    def _build_yuque_dl_command(self) -> list[str]:
        """构建 yuque-dl 命令"""
        cmd = []

        # 添加命令前缀（npx 或直接命令）
        if self._yuque_dl_path.startswith("npx"):
            cmd.extend(["npx", "yuque-dl"])
        else:
            cmd.append(self._yuque_dl_path)

        # 添加知识库 URL
        cmd.append(self._config["repo_url"])

        # 添加输出目录
        cmd.extend(["-d", str(self._download_dir)])

        # 添加认证 token（如果配置了）
        token = self._config.get("token")
        if token:
            cmd.extend(["-t", token])

        # 如果是企业部署，指定 cookie key
        cookie_key = self._config.get("cookie_key")
        if cookie_key and cookie_key != "_yuque_session":
            cmd.extend(["-k", cookie_key])

        # 是否忽略图片
        if self._config.get("ignore_images", False):
            cmd.append("--ignoreImg")

        # 是否增量下载
        if self._config.get("incremental", True):
            cmd.append("--incremental")

        # 是否输出 TOC
        if self._config.get("toc", False):
            cmd.append("--toc")

        return cmd

    async def _scan_downloaded_files(self) -> AsyncIterator[DataSourceItem]:
        """扫描下载的 Markdown 文件"""
        for root, dirs, files in os.walk(self._download_dir):
            # 跳过隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if not file.endswith(".md"):
                    continue

                file_path = os.path.join(root, file)

                try:
                    # 读取文件内容
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # 提取元数据（从 Front Matter）
                    metadata = self._extract_front_matter(content)

                    # 移除 Front Matter
                    content = self._remove_front_matter(content)

                    # 生成唯一 ID
                    rel_path = os.path.relpath(file_path, self._download_dir)
                    item_id = f"yuque:{rel_path.replace(os.sep, '/').replace('.md', '')}"

                    yield DataSourceItem(
                        id=item_id,
                        title=metadata.get("title", file.replace(".md", "")),
                        content=content,
                        source_type="yuque",
                        url=metadata.get("url", ""),
                        author=metadata.get("author", ""),
                        created_at=self._parse_datetime(metadata.get("created_at")),
                        modified_at=self._parse_datetime(metadata.get("updated_at")),
                        metadata={
                            **metadata,
                            "file_path": file_path,
                            "relative_path": rel_path
                        }
                    )

                except Exception as e:
                    logger.warning(f"处理文件失败 {file_path}: {e}")
                    continue

    def _extract_front_matter(self, content: str) -> Dict[str, Any]:
        """从 Markdown 内容提取 Front Matter 元数据"""
        metadata = {}

        # yuque-dl 的 Front Matter 格式通常在文件顶部
        # ---\nkey: value\n---\n
        front_matter_pattern = r'^---\n(.*?)\n---'
        match = re.match(front_matter_pattern, content, re.DOTALL)

        if match:
            front_matter_text = match.group(1)
            try:
                metadata = yaml.safe_load(front_matter_text) or {}
            except:
                pass

        # 尝试从注释中提取 URL（yuque-dl 的页脚格式）
        # <!--原链接：https://www.yuque.com/...-->
        url_pattern = r'<!--原链接：(.*?)-->'
        url_match = re.search(url_pattern, content)
        if url_match:
            metadata["url"] = url_match.group(1).strip()

        return metadata

    def _remove_front_matter(self, content: str) -> str:
        """移除 Front Matter"""
        front_matter_pattern = r'^---\n.*?\n---\n'
        content = re.sub(front_matter_pattern, '', content, count=1, flags=re.DOTALL)
        return content.strip()

    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """解析时间字符串"""
        if not dt_str:
            return None
        try:
            # 尝试 ISO 格式
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except:
            try:
                # 尝试常见格式
                return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            except:
                return None

    async def get_content(self, item_id: str) -> Optional[str]:
        """获取文档内容"""
        if item_id.startswith('yuque:'):
            item_id = item_id[6:]

        # 从 metadata 中获取文件路径
        file_path = self._download_dir / f"{item_id}.md"

        if not file_path.exists():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return self._remove_front_matter(content)
        except Exception as e:
            logger.error(f"读取文档失败 {item_id}: {e}")
            return None

    async def cleanup(self):
        """清理资源"""
        pass
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

## 5. 本地文件数据源插件

### 5.1 配置文件

```yaml
# data/plugins/datasource/filesystem/config.yaml
plugin:
  id: filesystem
  name: 本地文件
  version: "1.0.0"
  type: datasource
  enabled: true

datasource:
  # 扫描目录列表
  scan_dirs:
    - "D:/Documents"
    - "D:/Projects"

  # 支持的文件扩展名
  extensions:
    - ".md"
    - ".txt"
    - ".pdf"
    - ".docx"
    - ".mp4"
    - ".mp3"
    - ".wav"
    - ".jpg"
    - ".png"

  # 排除的目录
  exclude_dirs:
    - ".git"
    - "node_modules"
    - "__pycache__"
    - ".venv"
```

### 5.2 插件实现

```python
# data/plugins/datasource/filesystem/plugin.py
import os
from pathlib import Path
from typing import Dict, Any, AsyncIterator, Optional
from datetime import datetime

from app.plugins.interface.datasource import DataSourcePlugin, DataSourceItem
from app.core.logging_config import logger


class FileSystemDataSource(DataSourcePlugin):
    """本地文件数据源插件"""

    def __init__(self):
        self._config: Dict[str, Any] = {}

    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        return {
            "id": "filesystem",
            "name": "本地文件",
            "version": "1.0.0",
            "type": "datasource",
            "author": "XiaoyaoSearch Team",
            "description": "扫描本地文件系统",
            "datasource_type": "filesystem"
        }

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        try:
            self._config = config
            scan_dirs = config.get("scan_dirs", [])
            if not scan_dirs:
                logger.warning("未配置扫描目录")
                return False

            logger.info(f"本地文件数据源初始化成功，扫描目录: {scan_dirs}")
            return True

        except Exception as e:
            logger.error(f"本地文件数据源初始化失败: {e}")
            return False

    async def scan(self, **kwargs) -> AsyncIterator[DataSourceItem]:
        """扫描本地文件"""
        scan_dirs = self._config.get("scan_dirs", [])
        extensions = set(self._config.get("extensions", []))
        exclude_dirs = set(self._config.get("exclude_dirs", []))

        for scan_dir in scan_dirs:
            async for item in self._scan_directory(scan_dir, extensions, exclude_dirs):
                yield item

    async def _scan_directory(
        self,
        directory: str,
        extensions: set[str],
        exclude_dirs: set[str]
    ) -> AsyncIterator[DataSourceItem]:
        """扫描目录"""
        for root, dirs, files in os.walk(directory):
            # 排除指定目录
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]

            for file in files:
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file)

                if extensions and ext not in extensions:
                    continue

                try:
                    # 获取文件信息
                    stat = os.stat(file_path)
                    created_at = datetime.fromtimestamp(stat.st_ctime)
                    modified_at = datetime.fromtimestamp(stat.st_mtime)

                    # 读取内容（文本文件）
                    content = ""
                    if ext in ['.md', '.txt']:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                        except:
                            content = f"[二进制文件: {file}]"

                    yield DataSourceItem(
                        id=f"fs:{file_path}",
                        title=file,
                        content=content,
                        source_type="filesystem",
                        url=f"file:///{file_path.replace(os.sep, '/')}",
                        created_at=created_at,
                        modified_at=modified_at,
                        metadata={
                            "file_path": file_path,
                            "file_size": stat.st_size,
                            "extension": ext
                        }
                    )

                except Exception as e:
                    logger.warning(f"处理文件失败 {file_path}: {e}")
                    continue

    async def get_content(self, item_id: str) -> Optional[str]:
        """获取文件内容"""
        if item_id.startswith('fs:'):
            item_id = item_id[3:]

        try:
            with open(item_id, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"读取文件失败 {item_id}: {e}")
            return None

    async def cleanup(self):
        """清理资源"""
        pass
```

---

## 6. 应用启动集成

### 6.1 启动时加载插件

```python
# backend/app/main.py
from contextlib import asynccontextmanager
from app.plugins.loader import PluginLoader
from app.services.datasource.manager import get_datasource_manager
from pathlib import Path

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时加载插件
    plugin_dir = Path("data/plugins")
    plugin_loader = PluginLoader(plugin_dir)

    # 发现并加载所有插件
    loaded_plugins = await plugin_loader.discover_and_load_all()

    # 设置到数据源管理器
    datasource_manager = get_datasource_manager()
    datasource_manager.set_loader(plugin_loader)

    logger.info(f"插件系统启动完成，已加载 {len(loaded_plugins)} 个插件")

    yield

    # 关闭时清理插件
    await plugin_loader.cleanup_all()

app = FastAPI(lifespan=lifespan)
```

---

## 7. 数据库变更

### 7.1 files表扩展

```sql
-- 新增字段
ALTER TABLE files ADD COLUMN source_type TEXT DEFAULT 'filesystem';
ALTER TABLE files ADD COLUMN source_url TEXT;

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_files_source_type ON files(source_type);
```

---

## 8. 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-02-22 | 初始版本（数据源插件专用） |
| v1.2 | 2026-02-22 | 约定优于配置版本 |
| v2.0 | 2026-02-22 | 通用插件系统架构 |
| **v2.1** | **2026-02-22** | **yuque-dl CLI集成方案** |

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

**文档版本**: v2.1
**创建时间**: 2026-02-22
**最后更新**: 2026-02-22 (v2.1 - yuque-dl CLI集成)
**维护者**: 开发者
