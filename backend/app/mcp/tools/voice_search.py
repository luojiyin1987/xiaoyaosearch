"""
语音搜索工具 - fastmcp 实现
"""
import base64
import io
import json
from typing import Optional, List
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
        audio_data: str,
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
        支持 WAV、MP3、M4A 格式。

        Args:
            audio_data: Base64 编码的音频数据
            search_type: 搜索类型（semantic/fulltext/hybrid，默认semantic）
            limit: 返回结果数量（1-100，默认20）
            threshold: 相似度阈值（0.0-1.0，默认0.7）
            file_types: 文件类型过滤（可选）
            enable_query_enhancement: 是否启用LLM查询增强（默认true）

        Returns:
            JSON 格式的搜索结果（包含语音识别结果）
        """
        # 检查语音搜索是否启用
        if not voice_enabled:
            return json.dumps({
                "error": "语音搜索未启用",
                "message": "请在配置中启用 MCP_VOICE_ENABLED"
            }, ensure_ascii=False, indent=2)

        # 1. 解码音频数据
        audio_bytes = base64.b64decode(audio_data)
        audio_file = io.BytesIO(audio_bytes)

        # 2. 语音识别
        transcription = await ai_model_service.speech_to_text(audio_file)
        query = transcription.get("text", "").strip()

        if not query:
            return json.dumps({
                "error": "语音识别失败",
                "transcription": transcription
            }, ensure_ascii=False, indent=2)

        logger.info(f"语音识别结果: {query}, 搜索类型: {search_type}, 增强={enable_query_enhancement}")

        # 3. LLM查询增强（与前端API保持一致）
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

        # 4. 执行搜索
        service = get_chunk_search_service()

        result = await service.search(
            query=enhanced_query,
            search_type=search_type_enum,
            limit=limit,
            offset=0,
            threshold=threshold,
            filters=filters
        )

        # 5. 格式化结果并添加识别信息
        formatted = json.loads(format_search_result(result))
        formatted["transcription"] = {
            "text": query,
            "enhanced_query": enhanced_query if enhanced_query != query else None,
            "language": transcription.get("language"),
            "duration": transcription.get("duration")
        }

        return json.dumps(formatted, ensure_ascii=False, indent=2)
