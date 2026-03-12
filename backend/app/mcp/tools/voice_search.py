"""
语音搜索工具 - fastmcp 实现
"""
import os
import io
import json
from typing import Optional, List
from pathlib import Path
from fastmcp import FastMCP
from app.services.chunk_search_service import get_chunk_search_service
from app.services.ai_model_manager import ai_model_service
from app.services.llm_query_enhancer import get_llm_query_enhancer
from app.schemas.enums import SearchType
from app.mcp.tools import format_search_result
from app.core.logging_config import get_logger
from app.core.config import get_settings
from app.utils.enum_helpers import is_semantic_search, is_hybrid_search

logger = get_logger(__name__)


def register_voice_search(mcp: FastMCP):
    """注册语音搜索工具到 FastMCP"""
    # 从配置中读取默认值
    settings = get_settings()
    default_limit = settings.mcp.default_limit
    default_threshold = settings.mcp.default_threshold
    voice_enabled = settings.mcp.voice_enabled

    @mcp.tool()
    async def voice_search(
        audio_path: str,
        search_type: str = "semantic",
        limit: int = default_limit,
        threshold: float = default_threshold,
        file_types: Optional[List[str]] = None,
        enable_query_enhancement: bool = True
    ) -> str:
        """
        基于FasterWhisper模型的语音搜索，支持语音输入转文本后进行搜索。

        适合通过语音快速搜索，无需手动输入文字。
        支持中英文语音识别，音频时长建议不超过30秒。
        支持 WAV、MP3、M4A、FLAC 格式。

        Args:
            audio_path: 音频文件绝对路径（如 C:/Users/test/recordings/voice.mp3）
            search_type: 搜索类型（semantic/fulltext/hybrid，默认semantic）
            limit: 返回结果数量（1-100，默认20）
            threshold: 相似度阈值（0.0-1.0，默认0.7）
            file_types: 文件类型过滤（可选）
            enable_query_enhancement: 是否启用LLM查询增强（默认true）

        Returns:
            JSON 格式的搜索结果（包含语音识别结果）

        Examples:
            voice_search(audio_path="C:/Users/test/recordings/voice.mp3")
            voice_search(audio_path="D:/audio/record.wav", search_type="hybrid")
        """
        # 检查语音搜索是否启用
        if not voice_enabled:
            return json.dumps({
                "error": "语音搜索未启用",
                "message": "请在配置中启用 MCP_VOICE_ENABLED"
            }, ensure_ascii=False, indent=2)

        try:
            # 转换为Path对象处理
            audio_file_path = Path(audio_path)

            # 检查路径是否为绝对路径
            if not audio_file_path.is_absolute():
                return json.dumps({
                    "error": f"只支持绝对路径: {audio_path}",
                    "hint": "请提供完整的绝对路径，如 C:/Users/test/recordings/voice.mp3"
                }, ensure_ascii=False, indent=2)

            # 检查文件是否存在
            if not audio_file_path.exists():
                return json.dumps({
                    "error": f"音频文件不存在: {audio_path}",
                    "hint": "请检查文件路径是否正确"
                }, ensure_ascii=False, indent=2)

            # 检查是否为文件
            if not audio_file_path.is_file():
                return json.dumps({
                    "error": f"路径不是文件: {audio_path}",
                    "hint": "请提供音频文件路径，而不是目录路径"
                }, ensure_ascii=False, indent=2)

            # 检查文件大小（限制10MB，约30秒音频）
            file_size = audio_file_path.stat().st_size
            if file_size > 10 * 1024 * 1024:
                return json.dumps({
                    "error": f"音频文件过大: {file_size / 1024 / 1024:.2f}MB",
                    "hint": "音频文件不能超过10MB，建议控制在30秒以内"
                }, ensure_ascii=False, indent=2)

            # 检查文件大小（最小1KB）
            if file_size < 1024:
                return json.dumps({
                    "error": f"音频文件过小: {file_size}字节",
                    "hint": "音频文件可能损坏，请检查文件"
                }, ensure_ascii=False, indent=2)

            # 支持的音频格式
            file_ext = audio_file_path.suffix.lower()
            supported_formats = {'.wav', '.mp3', '.m4a', '.flac', '.aac', '.ogg', '.opus'}
            if file_ext not in supported_formats:
                return json.dumps({
                    "error": f"不支持的音频格式: {file_ext}",
                    "hint": f"支持的格式: {', '.join(supported_formats)}",
                    "your_format": file_ext
                }, ensure_ascii=False, indent=2)

            logger.info(f"执行语音搜索: 文件={audio_path}, 大小={file_size/1024:.2f}KB, 搜索类型={search_type}")

            # 读取音频文件
            with open(audio_path, 'rb') as f:
                audio_bytes = f.read()
            audio_file = io.BytesIO(audio_bytes)

            # 语音识别
            transcription = await ai_model_service.speech_to_text(audio_file)
            query = transcription.get("text", "").strip()

            if not query:
                return json.dumps({
                    "error": "语音识别失败",
                    "hint": "请确保音频清晰，使用支持的格式（WAV/MP3/M4A）",
                    "transcription": transcription
                }, ensure_ascii=False, indent=2)

            logger.info(f"语音识别结果: {query}, 搜索类型: {search_type}, 增强={enable_query_enhancement}")

            # LLM查询增强（与前端API保持一致）
            enhanced_query = query
            search_type_enum = SearchType(search_type)

            if enable_query_enhancement:
                try:
                    query_enhancer = get_llm_query_enhancer()
                    enhancement_result = await query_enhancer.enhance_query(query)
                    if enhancement_result.get('success', False) and enhancement_result.get('enhanced', False):
                        # 根据搜索类型选择最佳查询
                        if is_semantic_search(search_type_enum):
                            enhanced_query = enhancement_result.get('expanded_query', query)
                        elif search_type_enum == SearchType.FULLTEXT:
                            enhanced_query = enhancement_result.get('rewritten_query', query)
                        else:  # HYBRID
                            enhanced_query = enhancement_result.get('expanded_query', query)
                        logger.info(f"LLM查询增强: '{query}' -> '{enhanced_query}'")
                except Exception as e:
                    logger.warning(f"LLM查询增强失败，使用原始查询: {str(e)}")
                    enhanced_query = query

            # 转换 file_types 为 filters
            filters = None
            if file_types:
                filters = {"file_types": file_types}

            # 执行搜索
            service = get_chunk_search_service()

            result = await service.search(
                query=enhanced_query,
                search_type=search_type_enum,
                limit=limit,
                offset=0,
                threshold=threshold,
                filters=filters
            )

            # 格式化结果并添加识别信息
            formatted = json.loads(format_search_result(result))
            formatted["transcription"] = {
                "text": query,
                "enhanced_query": enhanced_query if enhanced_query != query else None,
                "language": transcription.get("language"),
                "duration": transcription.get("duration")
            }
            formatted["input_info"] = {
                "file_path": str(audio_path),
                "file_size_kb": round(file_size / 1024, 2),
                "file_format": file_ext
            }

            return json.dumps(formatted, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"语音搜索失败: {str(e)}")
            return json.dumps({
                "error": f"语音搜索失败: {str(e)}",
                "hint": "请检查音频文件是否有效，或联系管理员"
            }, ensure_ascii=False, indent=2)
