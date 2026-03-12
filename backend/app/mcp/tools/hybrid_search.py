"""
混合搜索工具 - fastmcp 实现
"""
from typing import Optional, List
from fastmcp import FastMCP
from app.services.chunk_search_service import get_chunk_search_service
from app.schemas.enums import SearchType
from app.mcp.tools import format_search_result
from app.core.logging_config import get_logger
from app.core.config import get_settings

logger = get_logger(__name__)


def register_hybrid_search(mcp: FastMCP):
    """注册混合搜索工具到 FastMCP"""
    # 从配置中读取默认值
    settings = get_settings()
    default_limit = settings.mcp.default_limit
    default_threshold = settings.mcp.default_threshold

    @mcp.tool()
    async def hybrid_search(
        query: str,
        limit: int = default_limit,
        threshold: float = default_threshold,
        file_types: Optional[List[str]] = None
    ) -> str:
        """
        混合搜索，结合语义搜索和全文搜索的优势。

        同时使用BGE-M3语义理解和Whoosh精确匹配，
        通过RRF（Reciprocal Rank Fusion）算法融合结果，
        提供更全面的搜索结果。

        Args:
            query: 搜索查询词（1-500字符）
            limit: 返回结果数量（1-100，默认20）
            threshold: 相似度阈值（0.0-1.0，默认0.7）
            file_types: 文件类型过滤（可选）

        Returns:
            JSON 格式的搜索结果
        """
        if not query or len(query) > 500:
            raise ValueError("query 必须为1-500字符")
        if not 1 <= limit <= 100:
            raise ValueError("limit 必须为1-100")
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold 必须为0.0-1.0")

        logger.info(f"执行混合搜索: query={query}, limit={limit}")

        service = get_chunk_search_service()
        result = await service.search(
            query=query,
            search_type=SearchType.HYBRID,
            limit=limit,
            offset=0,
            threshold=threshold,
            file_types=file_types
        )

        return format_search_result(result)
