# 插件化架构与语雀数据源 - 技术方案

> **文档类型**：技术方案
> **特性状态**：规划中
> **创建时间**：2026-02-22
> **最后更新**：2026-02-22 (v2.0 - 通用插件系统)

---

## 1. 方案概述

### 1.1 技术目标

建立**通用插件化架构**，支持多种类型的插件扩展，包括数据源插件、AI模型插件等。优先实现数据源插件和AI模型插件，后续可扩展到搜索引擎、内容解析器、认证等插件类型。

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
| **AI模型插件** | `AIModelPlugin` | ✅ 已实现 | 提供AI模型服务（对话、嵌入、图像理解） |
| **搜索引擎插件** | `SearchEnginePlugin` | 🚧 规划中 | 替换或扩展搜索引擎 |
| **内容解析器插件** | `ContentParserPlugin` | 🚧 规划中 | 支持新的文件格式解析 |
| **存储插件** | `StoragePlugin` | 🚧 规划中 | 支持不同的存储后端 |
| **认证插件** | `AuthPlugin` | 🚧 规划中 | 支持不同的认证方式 |

### 1.4 技术选型

| 技术/框架 | 用途 | 选择理由 |
|----------|------|---------|
| Python ABC | 插件接口定义 | 标准库，类型安全 |
| importlib | 插件动态加载 | Python标准库，无额外依赖 |
| PyYAML | 配置文件解析 | 人类可读，易于编辑 |
| httpx | API调用 | 异步HTTP客户端，已集成 |
| Pydantic | 配置验证 | 数据验证，类型安全 |

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
│  PluginLoader  │  DataSourceManager  │  AIModelManager  │  IndexService  │
└────────────┬──────────────────────────────────────────┬───────────────────┘
             │                                          │
┌────────────▼──────────────────────────────────────────▼───────────────────┐
│                        插件层 (Plugin Layer)                                │
├───────────────────────────────────────────────────────────────────────────┤
│  BasePlugin(interface) - 通用插件基类                                      │
│  ├─ DataSourcePlugin(interface)  ├─ AIModelPlugin(interface)             │
│  │   ├─ FileSystemDataSource        │   ├─ OpenAIModel                   │
│  │   ├─ YuqueDataSource             │   ├─ ClaudeModel                   │
│  │   └─ FeishuDataSource            │   └─ OllamaModel                   │
│  └─ [未来插件类型]...                                                         │
└────────────┬──────────────────────────────────────────┬───────────────────┘
             │                                          │
┌────────────▼──────────────────────────────────────────▼───────────────────┐
│                        数据层 (Data Layer)                                  │
├───────────────────────────────────────────────────────────────────────────┤
│  本地文件  │  语雀API  │  OpenAI API  │  Faiss索引  │  Whoosh  │  SQLite  │
└───────────────────────────────────────────────────────────────────────────┘
```

### 2.2 插件目录结构

```
data/plugins/
├── datasource/              # 数据源插件目录
│   ├── yuque/              # 语雀知识库插件
│   │   ├── plugin.py
│   │   ├── config.yaml
│   │   ├── client.py
│   │   └── requirements.txt
│   ├── feishu/             # 飞书文档插件
│   │   ├── plugin.py
│   │   ├── config.yaml
│   │   └── requirements.txt
│   └── filesystem/         # 本地文件插件
│       ├── plugin.py
│       └── config.yaml
│
├── ai_model/               # AI模型插件目录
│   ├── openai/             # OpenAI模型插件
│   │   ├── plugin.py
│   │   ├── config.yaml
│   │   └── requirements.txt
│   ├── claude/             # Claude模型插件
│   │   ├── plugin.py
│   │   ├── config.yaml
│   │   └── requirements.txt
│   └── ollama/             # Ollama本地模型插件
│       ├── plugin.py
│       ├── config.yaml
│       └── requirements.txt
│
├── search_engine/          # 搜索引擎插件目录（未来）
│   └── elasticsearch/      # Elasticsearch引擎
│
├── content_parser/         # 内容解析器插件目录（未来）
│   ├── pdf/                # PDF解析器
│   └── docx/               # DOCX解析器
│
└── auth/                   # 认证插件目录（未来）
    └── oauth/              # OAuth认证
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
│   │   │   ├── ai_model.py              # AIModelPlugin接口
│   │   │   └── search_engine.py         # SearchEnginePlugin接口（预留）
│   │   ├── loader.py                    # 插件加载器
│   │   └── config_parser.py             # 配置文件解析器
│   │
│   ├── services/
│   │   ├── datasource/                   # 数据源服务层
│   │   │   ├── __init__.py
│   │   │   ├── base.py                  # 基础数据项
│   │   │   ├── filesystem.py            # 本地文件数据源
│   │   │   └── manager.py               # 数据源管理器
│   │   ├── ai_model/                     # AI模型服务层
│   │   │   ├── __init__.py
│   │   │   ├── base.py                  # AI模型基类
│   │   │   └── manager.py               # AI模型管理器
│   │   └── unified_index_service.py      # 统一索引服务
│   │
│   └── core/
│       └── config.py                     # 配置扩展
│
└── data/
    └── plugins/                          # 插件目录
        ├── datasource/
        │   ├── yuque/
        │   │   ├── plugin.py
        │   │   ├── config.yaml
        │   │   ├── client.py
        │   │   └── requirements.txt
        │   └── feishu/
        │       └── ...
        └── ai_model/
            ├── openai/
            │   ├── plugin.py
            │   ├── config.yaml
            │   └── requirements.txt
            └── claude/
                └── ...
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
    AI_MODEL = "ai_model"           # AI模型插件
    SEARCH_ENGINE = "search_engine" # 搜索引擎插件（预留）
    CONTENT_PARSER = "content_parser"  # 内容解析器插件（预留）
    STORAGE = "storage"             # 存储插件（预留）
    AUTH = "auth"                   # 认证插件（预留）
    NOTIFICATION = "notification"   # 通知插件（预留）

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
                - dependencies: 依赖的其他插件（可选）
                - min_system_version: 最低系统版本要求（可选）
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

### 3.3 AI模型插件接口

```python
# backend/app/plugins/interface/ai_model.py
from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncIterator, Optional, Union
from enum import Enum
from ..base import BasePlugin, PluginType

class ModelType(Enum):
    """AI模型类型"""
    TEXT = "text"        # 文本模型（对话、嵌入）
    IMAGE = "image"      # 图像模型（图像理解）
    VOICE = "voice"      # 语音模型（语音识别）
    VIDEO = "video"      # 视频模型（预留）

class AIModelPlugin(BasePlugin):
    """AI模型插件接口"""

    @classmethod
    @abstractmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """
        返回插件元数据

        Returns:
            Dict[str, Any]: 包含以下额外键:
                - model_type: 模型类型（见ModelType）
                - supported_features: 支持的功能列表（可选）
                    * chat: 对话
                    * embedding: 文本嵌入
                    * streaming: 流式输出
                    * vision: 图像理解
                    * transcribe: 语音识别
        """
        pass

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        pass

    async def chat(
        self,
        messages: list,
        stream: bool = False,
        **kwargs
    ) -> Union[AsyncIterator[Dict[str, Any]], Dict[str, Any]]:
        """
        对话接口（可选实现）

        Args:
            messages: 消息列表
            stream: 是否流式输出
            **kwargs: 其他参数（model, temperature等）

        Returns:
            流式返回或单次返回结果
        """
        raise NotImplementedError

    async def embedding(self, text: str, **kwargs) -> list[float]:
        """
        文本嵌入接口（可选实现）

        Args:
            text: 输入文本
            **kwargs: 其他参数（model等）

        Returns:
            list[float]: 文本向量
        """
        raise NotImplementedError

    async def understand_image(self, image: str, prompt: str, **kwargs) -> str:
        """
        图像理解接口（可选实现）

        Args:
            image: 图像路径或URL
            prompt: 提示词
            **kwargs: 其他参数

        Returns:
            str: 理解结果
        """
        raise NotImplementedError

    async def transcribe_audio(self, audio: str, **kwargs) -> str:
        """
        语音识别接口（可选实现）

        Args:
            audio: 音频文件路径
            **kwargs: 其他参数

        Returns:
            str: 识别文本
        """
        raise NotImplementedError

    @abstractmethod
    async def cleanup(self):
        """清理资源"""
        pass
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
            (PluginType.AI_MODEL, "ai_model"),
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
            if plugin_type == PluginType.DATASOURCE:
                plugin_config = config.get("datasource", {})
            elif plugin_type == PluginType.AI_MODEL:
                plugin_config = config.get("model", {})
            else:
                plugin_config = {}

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

    def get_plugin_type(self, plugin_id: str) -> Optional[str]:
        """获取插件类型"""
        return self._plugin_types.get(plugin_id)

    def get_plugins_by_type(self, plugin_type: str) -> Dict[str, BasePlugin]:
        """按类型获取插件"""
        return {
            pid: plugin
            for pid, plugin in self._loaded_plugins.items()
            if self._plugin_types.get(pid) == plugin_type
        }

    def list_plugins(self) -> Dict[str, Dict[str, Any]]:
        """列出所有插件信息"""
        return {
            plugin_id: {
                "id": plugin_id,
                "name": config.get("plugin", {}).get("name"),
                "type": self._plugin_types.get(plugin_id),
                "version": config.get("plugin", {}).get("version"),
                "enabled": config.get("plugin", {}).get("enabled", False),
                "loaded": plugin_id in self._loaded_plugins
            }
            for plugin_id, config in self._plugin_configs.items()
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

### 3.5 配置文件解析器

```python
# backend/app/plugins/config_parser.py
from typing import Dict, Any, Optional
import yaml
from pathlib import Path
from pydantic import BaseModel, ValidationError
from app.core.logging_config import logger

class PluginConfigModel(BaseModel):
    """插件配置模型"""
    id: str
    name: str
    version: str
    type: str                # 新增：插件类型
    enabled: bool = True

class DatasourceConfigModel(BaseModel):
    """数据源配置模型"""
    type: str

class AIModelConfigModel(BaseModel):
    """AI模型配置模型"""
    type: str                # 模型类型: text/image/voice

class ConfigParser:
    """配置文件解析器"""

    @staticmethod
    def parse_plugin_config(config_path: Path) -> Optional[Dict[str, Any]]:
        """
        解析插件配置文件

        Args:
            config_path: 配置文件路径

        Returns:
            Optional[Dict]: 解析后的配置，失败返回None
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                raw_config = yaml.safe_load(f)

            # 验证配置结构
            if "plugin" not in raw_config:
                raise ValueError("缺少 plugin 配置段")

            # 验证必需字段
            plugin_config = raw_config["plugin"]
            if not plugin_config.get("id"):
                raise ValueError("plugin.id 不能为空")
            if not plugin_config.get("name"):
                raise ValueError("plugin.name 不能为空")
            if not plugin_config.get("type"):
                raise ValueError("plugin.type 不能为空")

            # 根据插件类型验证特定配置段
            plugin_type = plugin_config["type"]
            if plugin_type == "datasource":
                if "datasource" not in raw_config:
                    raise ValueError("数据源插件缺少 datasource 配置段")
            elif plugin_type == "ai_model":
                if "model" not in raw_config:
                    raise ValueError("AI模型插件缺少 model 配置段")

            logger.info(f"配置文件解析成功: {config_path}")
            return raw_config

        except yaml.YAMLError as e:
            logger.error(f"YAML解析失败 {config_path}: {e}")
        except ValueError as e:
            logger.error(f"配置验证失败 {config_path}: {e}")
        except Exception as e:
            logger.error(f"读取配置文件失败 {config_path}: {e}")

        return None

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> tuple[bool, list]:
        """
        验证配置

        Args:
            config: 配置字典

        Returns:
            tuple[bool, list]: (是否有效, 错误信息列表)
        """
        errors = []

        try:
            PluginConfigModel(**config.get("plugin", {}))
        except ValidationError as e:
            errors.extend([f"plugin.{err['loc'][0]}: {err['msg']}" for err in e.errors()])

        # 根据插件类型验证特定配置
        plugin_type = config.get("plugin", {}).get("type")

        if plugin_type == "datasource":
            try:
                DatasourceConfigModel(**config.get("datasource", {}))
            except ValidationError as e:
                errors.extend([f"datasource.{err['loc'][0]}: {err['msg']}" for err in e.errors()])

        elif plugin_type == "ai_model":
            try:
                AIModelConfigModel(**config.get("model", {}))
            except ValidationError as e:
                errors.extend([f"model.{err['loc'][0]}: {err['msg']}" for err in e.errors()])

        return len(errors) == 0, errors
```

---

## 4. 数据源插件实现

### 4.1 配置文件示例

```yaml
# data/plugins/datasource/yuque/config.yaml
plugin:
  id: yuque
  name: 语雀知识库
  version: "1.0.0"
  type: datasource              # 插件类型
  enabled: true

datasource:
  type: yuque
  api_token: "your_yuque_api_token_here"
  repo_slug: "username/knowledge_base"
  base_url: "https://www.yuque.com/api/v2"

sync:
  interval: 60
  batch_size: 50
  timeout: 30
```

### 4.2 语雀插件实现

```python
# data/plugins/datasource/yuque/plugin.py
from app.plugins.interface.datasource import DataSourcePlugin, DataSourceItem
from typing import Dict, Any, AsyncIterator, Optional
from .client import YuqueClient
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class YuqueDataSource(DataSourcePlugin):
    """语雀知识库数据源插件"""

    _client: Optional[YuqueClient] = None
    _repo_slug: str = None

    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        return {
            "id": "yuque",
            "name": "语雀知识库",
            "version": "1.0.0",
            "type": "datasource",
            "author": "XiaoyaoSearch Team",
            "description": "支持语雀知识库文档搜索",
            "datasource_type": "yuque"
        }

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化语雀客户端"""
        try:
            api_token = config.get("api_token")
            repo_slug = config.get("repo_slug")
            base_url = config.get("base_url", "https://www.yuque.com/api/v2")

            if not api_token or not repo_slug:
                logger.error("缺少必要配置: api_token 或 repo_slug")
                return False

            self._repo_slug = repo_slug
            self._client = YuqueClient(api_token=api_token, base_url=base_url)

            # 测试连接
            user_info = await self._client.get_user_info()
            if not user_info:
                logger.error("语雀API连接失败: 无效的Token")
                return False

            logger.info(f"语雀数据源初始化成功: {repo_slug}")
            return True

        except Exception as e:
            logger.error(f"语雀数据源初始化失败: {e}")
            return False

    async def scan(self, **kwargs) -> AsyncIterator[DataSourceItem]:
        """扫描语雀文档"""
        if self._client is None:
            raise RuntimeError("插件未初始化")

        docs = await self._client.get_repo_docs(self._repo_slug)

        for doc in docs:
            try:
                doc_detail = await self._client.get_doc_detail(doc['slug'])
                if not doc_detail:
                    continue

                item = DataSourceItem(
                    id=f"yuque:{doc['id']}",
                    title=doc['title'],
                    content=self._extract_content(doc_detail),
                    source_type="yuque",
                    url=doc.get('url'),
                    author=doc.get('created_by', {}).get('name'),
                    created_at=self._parse_datetime(doc.get('created_at')),
                    modified_at=self._parse_datetime(doc.get('updated_at')),
                    metadata={
                        'slug': doc['slug'],
                        'repo_slug': self._repo_slug,
                        'word_count': doc_detail.get('word_count', 0)
                    }
                )

                yield item

            except Exception as e:
                logger.warning(f"处理文档失败 {doc.get('id')}: {e}")
                continue

    def _extract_content(self, doc_detail: Dict[str, Any]) -> str:
        """提取文档内容"""
        content = doc_detail.get('content', '')
        # 移除markdown特殊符号
        import re
        content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
        content = re.sub(r'\[.*?\]\(.*?\)', '', content)
        content = re.sub(r'#+\s*', '', content)
        return content.strip()

    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """解析时间字符串"""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except:
            return None

    async def get_content(self, item_id: str) -> Optional[str]:
        """获取文档内容"""
        if self._client is None:
            return None

        if item_id.startswith('yuque:'):
            item_id = item_id[6:]

        doc_detail = await self._client.get_doc_detail(item_id)
        if doc_detail:
            return self._extract_content(doc_detail)

        return None

    async def cleanup(self):
        """清理资源"""
        if self._client:
            await self._client.close()
            self._client = None
```

---

## 5. AI模型插件实现

### 5.1 配置文件示例

```yaml
# data/plugins/ai_model/openai/config.yaml
plugin:
  id: openai
  name: OpenAI
  version: "1.0.0"
  type: ai_model              # 插件类型
  enabled: true

model:
  type: text                  # 模型类型
  api_key: "your_openai_api_key"
  base_url: "https://api.openai.com/v1"
  model: "gpt-4"
  embedding_model: "text-embedding-3-small"

capabilities:
  chat: true                  # 支持对话
  embedding: true             # 支持嵌入
  streaming: true             # 支持流式输出
  vision: true                # 支持图像理解
```

### 5.2 OpenAI插件实现

```python
# data/plugins/ai_model/openai/plugin.py
from app.plugins.interface.ai_model import AIModelPlugin, ModelType
from typing import Dict, Any, AsyncIterator
from openai import AsyncOpenAI
import logging

logger = logging.getLogger(__name__)

class OpenAIModel(AIModelPlugin):
    """OpenAI AI模型插件"""

    _client: AsyncOpenAI = None

    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        return {
            "id": "openai",
            "name": "OpenAI",
            "version": "1.0.0",
            "type": "ai_model",
            "author": "XiaoyaoSearch Team",
            "description": "OpenAI GPT模型集成",
            "model_type": ModelType.TEXT.value,
            "supported_features": ["chat", "embedding", "streaming", "vision"]
        }

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化OpenAI客户端"""
        try:
            self._config = config
            self._client = AsyncOpenAI(
                api_key=config.get("api_key"),
                base_url=config.get("base_url")
            )
            return True
        except Exception as e:
            logger.error(f"OpenAI初始化失败: {e}")
            return False

    async def chat(
        self,
        messages: list,
        stream: bool = False,
        **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """对话接口"""
        model = kwargs.get("model", self._config.get("model", "gpt-4"))

        if stream:
            stream_response = await self._client.chat.completions.create(
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
            response = await self._client.chat.completions.create(
                model=model,
                messages=messages
            )
            yield {
                "content": response.choices[0].message.content,
                "finish_reason": response.choices[0].finish_reason
            }

    async def embedding(self, text: str, **kwargs) -> list[float]:
        """文本嵌入接口"""
        model = kwargs.get("model", self._config.get("embedding_model", "text-embedding-3-small"))
        response = await self._client.embeddings.create(
            model=model,
            input=text
        )
        return response.data[0].embedding

    async def cleanup(self):
        """清理资源"""
        if self._client:
            await self._client.close()
```

---

## 6. 应用启动集成

### 6.1 启动时加载插件

```python
# backend/app/main.py
from contextlib import asynccontextmanager
from app.plugins.loader import PluginLoader
from app.services.datasource.manager import get_datasource_manager
from app.services.ai_model.manager import get_ai_model_manager
from pathlib import Path

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时加载插件
    plugin_dir = Path("data/plugins")
    plugin_loader = PluginLoader(plugin_dir)

    # 发现并加载所有插件
    loaded_plugins = await plugin_loader.discover_and_load_all()

    # 设置到管理器
    datasource_manager = get_datasource_manager()
    datasource_manager.set_loader(plugin_loader)

    ai_model_manager = get_ai_model_manager()
    ai_model_manager.set_loader(plugin_loader)

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
| **v2.0** | **2026-02-22** | **通用插件系统架构** |

### v2.0 主要变更

- ✅ 新增 `BasePlugin` 通用基类
- ✅ 新增 `AIModelPlugin` AI模型接口
- ✅ 新增 `PluginType` 插件类型枚举
- ✅ 新增 `ModelType` AI模型类型枚举
- ✅ 插件目录按类型组织
- ✅ 配置文件支持插件类型标识
- ✅ PluginLoader支持多类型插件加载

---

**文档版本**: v2.0
**创建时间**: 2026-02-22
**最后更新**: 2026-02-22 (v2.0 - 通用插件系统)
**维护者**: 开发者
