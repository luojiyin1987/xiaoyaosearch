# data/plugins/datasource/dingding
"""
钉钉文档数据源插件包

识别钉钉导出工具生成的 .xyddjson 元数据文件并提取文档信息。
"""

from .plugin import DingdingDataSource

__all__ = ["DingdingDataSource"]
__version__ = "1.0.0"
