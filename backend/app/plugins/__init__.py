"""
插件系统模块

提供插件化架构支持，包括：
- BasePlugin: 通用插件基类
- DataSourcePlugin: 数据源插件接口
- PluginLoader: 插件加载器
"""

from .base import BasePlugin, PluginType
from .loader import PluginLoader

__all__ = [
    "BasePlugin",
    "PluginType",
    "PluginLoader",
]
