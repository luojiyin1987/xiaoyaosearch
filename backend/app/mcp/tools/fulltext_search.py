"""
全文搜索工具 - fastmcp 实现
"""
from typing import Optional, List
from fastmcp import FastMCP
from app.services.chunk_search_service import get_chunk_search_service
from app.schemas.enums import SearchType
from app.mcp.tools import format_search_result
from app.core.logging_config import get_logger
from app.core.config import get_settings

logger = get_logger(__name__)


def register_fulltext_search(mcp: FastMCP):
    """注册全文搜索工具到 FastMCP"""
    # 从配置中读取默认值
    settings = get_settings()
    default_limit = settings.mcp.default_limit

    @mcp.tool()
    async def fulltext_search(
        query: str,
        limit: int = default_limit,
        file_types: Optional[List[str]] = None
    ) -> str:
        """
        基于Whoosh的全文搜索，支持精确关键词匹配和短语查询。

        适合查找特定的关键词或短语，支持布尔运算符（AND, OR, NOT）。
        搜索速度极快，适合精确匹配场景。

        Args:
            query: 搜索查询词（1-500字符）
            limit: 返回结果数量（1-100，默认20）
            file_types: 文件类型过滤（可选）

        Returns:
            JSON 格式的搜索结果
        """
        if not query or len(query) > 500:
            raise ValueError("query 必须为1-500字符")
        if not 1 <= limit <= 100:
            raise ValueError("limit 必须为1-100")

        logger.info(f"执行全文搜索: query={query}, limit={limit}")

        # 转换 file_types 为 filters
        filters = None
        if file_types:
            filters = {"file_types": file_types}

        service = get_chunk_search_service()
        result = await service.search(
            query=query,
            search_type=SearchType.FULLTEXT,
            limit=limit,
            offset=0,
            filters=filters
        )

        return format_search_result(result)
