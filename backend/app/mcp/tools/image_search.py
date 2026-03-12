"""
图像搜索工具 - fastmcp 实现
"""
import os
import json
from io import BytesIO
from pathlib import Path
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
        image_path: str,
        limit: int = default_limit,
        threshold: float = default_threshold
    ) -> str:
        """
        基于CN-CLIP模型的图像搜索，支持图片查找相似内容。

        上传图片后，将搜索与该图片相似的文件。
        支持查找相似图片、包含相似元素的文档等。

        Args:
            image_path: 图片文件绝对路径（如 C:/Users/test/Pictures/photo.jpg）
            limit: 返回结果数量（1-100，默认20）
            threshold: 相似度阈值（0.0-1.0，默认0.7）

        Returns:
            JSON 格式的搜索结果

        Examples:
            image_search(image_path="C:/Users/test/Pictures/photo.jpg")
            image_search(image_path="D:/images/screenshot.png")
        """
        try:
            # 转换为Path对象处理
            image_file_path = Path(image_path)

            # 检查路径是否为绝对路径
            if not image_file_path.is_absolute():
                return json.dumps({
                    "error": f"只支持绝对路径: {image_path}",
                    "hint": "请提供完整的绝对路径，如 C:/Users/test/Pictures/photo.jpg"
                }, ensure_ascii=False, indent=2)

            # 检查文件是否存在
            if not image_file_path.exists():
                return json.dumps({
                    "error": f"图片文件不存在: {image_path}",
                    "hint": "请检查文件路径是否正确"
                }, ensure_ascii=False, indent=2)

            # 检查是否为文件
            if not image_file_path.is_file():
                return json.dumps({
                    "error": f"路径不是文件: {image_path}",
                    "hint": "请提供图片文件路径，而不是目录路径"
                }, ensure_ascii=False, indent=2)

            # 检查文件大小（限制10MB）
            file_size = image_file_path.stat().st_size
            if file_size > 10 * 1024 * 1024:
                return json.dumps({
                    "error": f"图片文件过大: {file_size / 1024 / 1024:.2f}MB",
                    "hint": "图片大小不能超过10MB，请压缩后重试"
                }, ensure_ascii=False, indent=2)

            # 检查文件大小（最小1KB）
            if file_size < 1024:
                return json.dumps({
                    "error": f"图片文件过小: {file_size}字节",
                    "hint": "图片文件可能损坏，请检查文件"
                }, ensure_ascii=False, indent=2)

            # 支持的图片格式
            file_ext = image_file_path.suffix.lower()
            supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
            if file_ext not in supported_formats:
                return json.dumps({
                    "error": f"不支持的图片格式: {file_ext}",
                    "hint": f"支持的格式: {', '.join(supported_formats)}",
                    "your_format": file_ext
                }, ensure_ascii=False, indent=2)

            logger.info(f"执行图像搜索: 文件={image_path}, 大小={file_size/1024:.2f}KB, limit={limit}, threshold={threshold}")

            # 读取图片文件
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            image_file = BytesIO(image_bytes)

            # 执行图像搜索
            from app.services.ai_model_manager import ai_model_service
            from app.services.image_search_service import ensure_image_search_service

            # 确保图像搜索服务已初始化
            service = await ensure_image_search_service()

            # 使用 AI 模型管理器对图片进行编码（复用全局 CLIP 模型）
            query_vector = await ai_model_service.encode_image(image_file)

            # 使用向量进行搜索
            result = await service.search_similar_images(
                query_vector=query_vector,
                limit=limit,
                threshold=threshold
            )

            # 在结果中添加输入源信息
            result_dict = json.loads(format_image_result(result))
            result_dict["input_info"] = {
                "file_path": str(image_path),
                "file_size_kb": round(file_size / 1024, 2),
                "file_format": file_ext
            }
            return json.dumps(result_dict, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"图像搜索失败: {str(e)}")
            return json.dumps({
                "error": f"图像搜索失败: {str(e)}",
                "hint": "请检查图片文件是否有效，或联系管理员"
            }, ensure_ascii=False, indent=2)
