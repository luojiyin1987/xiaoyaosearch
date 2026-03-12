"""
MCP 工具基类辅助函数
"""
import json
from typing import Any, Dict, List


def format_search_result(result: dict) -> str:
    """
    格式化搜索结果为 JSON 字符串

    Args:
        result: 搜索结果字典

    Returns:
        str: JSON 格式结果
    """
    data = result.get('data', {})
    results = data.get('results', [])

    formatted = {
        "total": data.get('total', 0),
        "search_time": data.get('search_time', 0),
        "results": [
            {
                "file_name": item.get('file_name', ''),
                "file_path": item.get('file_path', ''),
                "file_type": item.get('file_type', ''),
                "relevance_score": item.get('relevance_score', 0),
                "preview_text": item.get('preview_text', ''),
                "highlight": item.get('highlight', ''),
                "source_type": item.get('source_type', 'filesystem'),
                "source_url": item.get('source_url')
            }
            for item in results
        ]
    }

    return json.dumps(formatted, ensure_ascii=False, indent=2)


def format_image_result(result: dict) -> str:
    """
    格式化图像搜索结果为 JSON 字符串

    Args:
        result: 图像搜索结果字典

    Returns:
        str: JSON 格式结果
    """
    data = result.get('data', {})
    results = data.get('results', [])

    formatted = {
        "total": data.get('total', 0),
        "search_time": data.get('search_time', 0),
        "results": [
            {
                "file_name": item.get('file_name', ''),
                "file_path": item.get('file_path', ''),
                "file_type": item.get('file_type', ''),
                "similarity": item.get('similarity', 0),
                "preview_url": item.get('preview_url', ''),
                "thumbnail_url": item.get('thumbnail_url', '')
            }
            for item in results
        ]
    }

    return json.dumps(formatted, ensure_ascii=False, indent=2)
