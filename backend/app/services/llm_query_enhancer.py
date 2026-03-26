"""
LLM查询增强服务 - 使用云端大语言模型进行查询扩展和重写
"""

import json
import re
from typing import Dict, Optional

from app.services.ai_model_manager import ai_model_service
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class LLMQueryEnhancer:
    """LLM查询增强器

    使用 ai_model_service 当前激活的 LLM 模型进行查询扩展和重写
    """

    def __init__(self):
        """初始化LLM查询增强器"""
        # 从 ai_model_service 获取当前激活的 LLM 模型信息
        self.model_info = self._get_active_llm_info()
        logger.info(f"LLM查询增强器初始化完成，使用模型: {self.model_info}")

    def _get_active_llm_info(self) -> str:
        """获取当前激活的 LLM 模型信息"""
        try:
            # 获取 LLM 模型配置
            from app.models.ai_model import AIModelModel
            from app.core.database import get_db

            with next(get_db()) as db:
                # 查询激活的 LLM 模型
                llm_model = db.query(AIModelModel).filter(
                    AIModelModel.model_type == 'llm',
                    AIModelModel.is_active == True
                ).first()

                if llm_model:
                    provider = llm_model.provider
                    model_name = llm_model.model_name
                    return f"{provider}:{model_name}"
                else:
                    return "未配置LLM模型"
        except Exception as e:
            logger.warning(f"获取LLM模型信息失败: {e}")
            return "未知模型"

    async def enhance_query(self, query: str) -> Dict[str, any]:
        """增强搜索查询

        Args:
            query: 原始查询词

        Returns:
            Dict: 增强结果，包含扩展查询和重写查询
        """
        # 检查是否需要增强
        if not self._should_enhance_query(query):
            return {
                'success': True,
                'original_query': query,
                'expanded_query': query,
                'rewritten_query': query,
                'enhanced': False
            }

        try:
            # 构建提示词
            prompt = self._build_simple_prompt(query)

            # 调用LLM
            response = await ai_model_service.text_generation(
                messages=prompt,
                temperature=0.3,
                max_tokens=150
            )

            if not response or not response.get('content'):
                return self._create_fallback_response(query)

            # 解析响应
            enhanced_content = response.get('content', '').strip()
            result = self._parse_simple_response(enhanced_content, query)

            logger.info(f"查询增强完成: '{query}' -> '{result['expanded_query']}'")
            return result

        except Exception as e:
            logger.error(f"查询增强失败: {str(e)}")
            return self._create_fallback_response(query)

    def _should_enhance_query(self, query: str) -> bool:
        """判断是否需要增强查询"""
        query = query.strip()

        # 不增强的情况
        if len(query) <= 2:
            return False

        # 文件名或路径查询
        if any(sep in query for sep in ['.', '/', '\\', ':']):
            return False

        # 已用引号的精确查询
        if query.startswith('"') and query.endswith('"'):
            return False

        # 包含操作符的复杂查询
        if any(op in query.lower() for op in [' and ', ' or ', ' not ', '+', '-']):
            return False

        return True

    def _build_simple_prompt(self, query: str) -> str:
        """构建简单的增强提示词"""
        return f"""你是一个搜索查询优化专家。请对以下中文查询进行优化：

原始查询：{query}

请提供JSON格式响应：
{{
    "expanded_query": "扩展查询（添加3-5个同义词，用空格分隔）",
    "rewritten_query": "重写查询（更准确的表达）"
}}

示例：
输入：怎么用Python
输出：{{"expanded_query": "怎么用Python Python使用方法 Python教程 Python入门 Python操作指南", "rewritten_query": "Python使用方法教程"}}

请只返回JSON，不要其他内容。"""

    def _parse_simple_response(self, content: str, original_query: str) -> Dict[str, any]:
        """解析简单的LLM响应"""
        try:
            # 提取JSON
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)

                return {
                    'success': True,
                    'original_query': original_query,
                    'expanded_query': parsed.get('expanded_query', original_query),
                    'rewritten_query': parsed.get('rewritten_query', original_query),
                    'enhanced': True
                }
        except:
            pass

        # JSON解析失败，使用规则增强
        return self._create_rule_based_response(original_query)

    def _create_rule_based_response(self, query: str) -> Dict[str, any]:
        """基于规则的查询增强"""
        # 简单的同义词映射
        expansions = {
            '怎么用': ['使用方法', '操作指南', '教程', '使用步骤'],
            '如何': ['怎么', '怎样', '如何操作', '方法'],
            '什么是': ['定义', '概念', '含义', '解释'],
            '为什么': ['原因', '理由', '原理', '成因'],
            '下载': ['下载地址', '获取', '安装包'],
            '安装': ['安装教程', '配置', '部署', '搭建'],
            '打不开': ['无法启动', '启动失败', '运行错误'],
            '错误': ['问题', '异常', 'bug', '故障'],
            '教程': ['指南', '手册', '文档', '学习资料'],
            '配置': ['设置', '参数', '选项', '自定义']
        }

        query_lower = query.lower()
        expanded_terms = []

        for key, synonyms in expansions.items():
            if key in query_lower:
                expanded_terms.extend(synonyms)
                break

        expanded_query = query + ' ' + ' '.join(expanded_terms[:3])

        return {
            'success': True,
            'original_query': query,
            'expanded_query': expanded_query.strip(),
            'rewritten_query': query,
            'enhanced': True
        }

    def _create_fallback_response(self, query: str) -> Dict[str, any]:
        """创建备用响应"""
        return {
            'success': True,
            'original_query': query,
            'expanded_query': query,
            'rewritten_query': query,
            'enhanced': False
        }


# 全局实例
_llm_query_enhancer = None


def get_llm_query_enhancer() -> LLMQueryEnhancer:
    """获取LLM查询增强器实例"""
    global _llm_query_enhancer
    if _llm_query_enhancer is None:
        _llm_query_enhancer = LLMQueryEnhancer()
    return _llm_query_enhancer