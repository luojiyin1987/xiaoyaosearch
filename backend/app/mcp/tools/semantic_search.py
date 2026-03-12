"""
语义搜索工具 - fastmcp 实现
"""
from typing import Optional, List
from fastmcp import FastMCP
from app.services.chunk_search_service import get_chunk_search_service
from app.services.llm_query_enhancer import get_llm_query_enhancer
from app.schemas.enums import SearchType
from app.mcp.tools import format_search_result
from app.core.logging_config import get_logger
from app.core.config import get_settings
from app.utils.enum_helpers import is_semantic_search

logger = get_logger(__name__)


def register_semantic_search(mcp: FastMCP):
    """注册语义搜索工具到 FastMCP"""
    # 从配置中读取默认值
    settings = get_settings()
    default_limit = settings.mcp.default_limit
    default_threshold = settings.mcp.default_threshold

    @mcp.tool()
    async def semantic_search(
        query: str,
        limit: int = default_limit,
        threshold: float = default_threshold,
        file_types: Optional[List[str]] = None,
        enable_query_enhancement: bool = True
    ) -> str:
        """
        基于BGE-M3模型的语义搜索，支持自然语言查询理解。

        适合用自然语言描述的查询，如"关于机器学习算法优化的方法"。
        支持文件类型过滤和相似度阈值设置。

        Args:
            query: 搜索查询词（1-500字符）
            limit: 返回结果数量（1-100，默认20）
            threshold: 相似度阈值（0.0-1.0，默认0.7）
            file_types: 文件类型过滤（可选）
            enable_query_enhancement: 是否启用LLM查询增强（默认true）

        Returns:
            JSON 格式的搜索结果
        """
        # 参数验证
        if not query or len(query) > 500:
            raise ValueError("query 必须为1-500字符")
        if not 1 <= limit <= 100:
            raise ValueError("limit 必须为1-100")
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold 必须为0.0-1.0")

        logger.info(f"执行语义搜索: query={query}, limit={limit}, 增强={enable_query_enhancement}")

        # LLM查询增强（与前端API保持一致）
        enhanced_query = query
        if enable_query_enhancement:
            try:
                query_enhancer = get_llm_query_enhancer()
                enhancement_result = await query_enhancer.enhance_query(query)
                if enhancement_result.get('success', False) and enhancement_result.get('enhanced', False):
                    # 语义搜索使用扩展查询
                    enhanced_query = enhancement_result.get('expanded_query', query)
                    logger.info(f"LLM查询增强: '{query}' -> '{enhanced_query}'")
            except Exception as e:
                logger.warning(f"LLM查询增强失败，使用原始查询: {str(e)}")
                enhanced_query = query

        # 转换 file_types 为 filters
        filters = None
        if file_types:
            filters = {"file_types": file_types}

        # 执行搜索（使用增强后的查询）
        service = get_chunk_search_service()
        result = await service.search(
            query=enhanced_query,
            search_type=SearchType.SEMANTIC,
            limit=limit,
            offset=0,
            threshold=threshold,
            filters=filters
        )

        return format_search_result(result)
