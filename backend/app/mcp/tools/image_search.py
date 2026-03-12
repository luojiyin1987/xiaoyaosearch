"""
图像搜索工具 - fastmcp 实现
"""
import base64
from io import BytesIO
from fastmcp import FastMCP
from app.services.image_search_service import get_image_search_service
from app.mcp.tools import format_image_result
from app.core.logging_config import get_logger
from app.core.config import get_settings

logger = get_logger(__name__)


def register_image_search(mcp: FastMCP):
    """注册图像搜索工具到 FastMCP"""
    # 从配置中读取默认值
    settings = get_settings()
    default_limit = settings.mcp.default_limit
    default_threshold = settings.mcp.default_threshold

    @mcp.tool()
    async def image_search(
        image_data: str,
        limit: int = default_limit,
        threshold: float = default_threshold
    ) -> str:
        """
        基于CN-CLIP模型的图像搜索，支持图片查找相似内容。

        上传图片后，将搜索与该图片相似的文件。
        支持查找相似图片、包含相似元素的文档等。

        Args:
            image_data: Base64 编码的图片数据
            limit: 返回结果数量（1-100，默认20）
            threshold: 相似度阈值（0.0-1.0，默认0.7）

        Returns:
            JSON 格式的搜索结果
        """
        # 解码图片数据
        image_bytes = base64.b64decode(image_data)
        image_file = BytesIO(image_bytes)

        logger.info(f"执行图像搜索: limit={limit}, threshold={threshold}")

        # 执行图像搜索
        service = get_image_search_service()
        result = await service.search(
            image=image_file,
            limit=limit,
            threshold=threshold
        )

        return format_image_result(result)
