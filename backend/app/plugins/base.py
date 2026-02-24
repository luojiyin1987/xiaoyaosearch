"""
插件基类模块

定义插件系统的核心抽象接口。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PluginType(Enum):
    """插件类型枚举"""
    DATASOURCE = "datasource"
    AI_MODEL = "ai_model"
    SEARCH_ENGINE = "search_engine"
    POST_PROCESSOR = "post_processor"


class PluginStatus(Enum):
    """插件状态枚举"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"
    DISABLED = "disabled"


class BasePlugin(ABC):
    """插件基类（异步架构）

    所有插件必须继承此类并实现抽象方法。

    设计原则：
    - 异步优先：所有可能耗时的操作使用 async/await
    - 错误隔离：插件错误不应影响主系统
    - 资源管理：提供 cleanup 方法确保资源正确释放
    """

    def __init__(self):
        self._status = PluginStatus.UNINITIALIZED
        self._config: Optional[Dict[str, Any]] = None
        self._error_message: Optional[str] = None

    @classmethod
    @abstractmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """返回插件元数据

        Returns:
            dict: 包含以下字段的元数据字典
                - id (str): 插件唯一标识符
                - name (str): 插件显示名称
                - version (str): 插件版本号（语义化版本）
                - type (str): 插件类型（PluginType 枚举值）
                - author (str): 插件作者
                - description (str): 插件描述
                - dependencies (List[str]): 依赖列表（可选）
        """
        pass

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件

        在插件加载后调用，用于执行初始化操作。

        Args:
            config: 插件配置字典，从 config.yaml 中读取

        Returns:
            bool: 初始化是否成功

        注意：
            - 初始化失败时设置 self._error_message
            - 初始化成功时设置 self._status = PluginStatus.READY
        """
        pass

    @abstractmethod
    async def cleanup(self):
        """清理插件资源

        在应用关闭或插件卸载时调用。

        注意：
            - 必须保证幂等性（多次调用无副作用）
            - 清理失败应记录日志但不抛出异常
        """
        pass

    @property
    def status(self) -> PluginStatus:
        """获取插件状态"""
        return self._status

    @property
    def is_ready(self) -> bool:
        """检查插件是否就绪"""
        return self._status == PluginStatus.READY

    @property
    def error_message(self) -> Optional[str]:
        """获取错误信息"""
        return self._error_message

    def _set_error(self, message: str):
        """设置错误状态和错误信息

        Args:
            message: 错误信息
        """
        self._status = PluginStatus.ERROR
        self._error_message = message
        logger.error(f"插件 {self.__class__.__name__} 错误: {message}")

    def _set_ready(self):
        """设置就绪状态"""
        self._status = PluginStatus.READY
        self._error_message = None
        logger.info(f"插件 {self.__class__.__name__} 已就绪")

    def get_health_check(self) -> Dict[str, Any]:
        """获取插件健康状态信息

        Returns:
            dict: 健康状态信息
                - status (PluginStatus): 插件状态
                - is_ready (bool): 是否就绪
                - error (Optional[str]): 错误信息（如果有）
        """
        return {
            "status": self._status.value,
            "is_ready": self.is_ready,
            "error": self._error_message
        }

    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证插件配置（可选重写）

        Args:
            config: 待验证的配置

        Returns:
            bool: 配置是否有效
        """
        return True

    def __repr__(self) -> str:
        metadata = self.get_metadata()
        return f"<{self.__class__.__name__} id={metadata.get('id')} version={metadata.get('version')} status={self._status.value}>"
