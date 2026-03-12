"""
FastMCP 服务器主类
"""
from fastmcp import FastMCP
from app.core.logging_config import get_logger
from app.core.config import get_settings

logger = get_logger(__name__)


def create_mcp_server() -> FastMCP:
    """
    创建 FastMCP 服务器实例

    Returns:
        FastMCP: FastMCP 服务器实例
    """
    settings = get_settings()
    config = settings.mcp

    # 创建 FastMCP 实例
    # 注意：message_path 现在在 http_app() 调用时设置
    mcp = FastMCP(
        name=config.server_name,
        version=config.server_version,
    )

    logger.info(f"✅ FastMCP 服务器初始化完成: {config.server_name}")
    return mcp


def register_mcp_tools(mcp: FastMCP):
    """
    注册所有 MCP 工具

    Args:
        mcp: FastMCP 服务器实例
    """
    from app.mcp.tools.semantic_search import register_semantic_search
    from app.mcp.tools.fulltext_search import register_fulltext_search
    from app.mcp.tools.voice_search import register_voice_search
    from app.mcp.tools.image_search import register_image_search
    from app.mcp.tools.hybrid_search import register_hybrid_search

    # 注册所有搜索工具
    register_semantic_search(mcp)
    register_fulltext_search(mcp)
    register_voice_search(mcp)
    register_image_search(mcp)
    register_hybrid_search(mcp)

    logger.info("✅ 所有 MCP 工具注册完成")
