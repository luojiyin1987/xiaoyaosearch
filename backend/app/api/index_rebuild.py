"""
索引重建 API 端点 - 独立端点，不与现有索引任务系统混用

端点前缀：/api/index/rebuild
- POST /start - 开始重建
- GET /status - 查询状态
- POST /cancel - 取消重建
"""
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from app.services.index_rebuild_service import get_index_rebuild_service
from app.core.i18n import i18n, get_locale_from_header
from app.core.logging_config import logger

router = APIRouter(prefix="/api/index/rebuild", tags=["索引重建"])


class RebuildRequest(BaseModel):
    """重建请求模型"""
    config: Dict[str, Any] = Field(..., description="新的嵌入模型配置")
    force: bool = Field(default=False, description="是否强制重建")


@router.post("/start")
async def start_rebuild(
    request: RebuildRequest,
    accept_language: Optional[str] = Header(None)
):
    """
    开始索引重建（内存状态，不写数据库）

    Args:
        request: 重建请求
        accept_language: Accept-Language 头，用于国际化

    Returns:
        重建任务信息
    """
    # 获取语言环境
    locale = get_locale_from_header(accept_language)

    service = get_index_rebuild_service()
    result = await service.start_rebuild(
        new_model_config=request.config,
        force=request.force
    )

    if result.get("success"):
        return result

    # 根据错误码返回相应的 HTTP 状态码和国际化消息
    error = result.get("error", {})
    code = error.get("code")

    if code == "REBUILD_JOB_RUNNING":
        details = error.get("details", {})
        raise HTTPException(
            status_code=409,
            detail={
                "code": code,
                "message": i18n.t("model.rebuild_already_running", locale, progress=details.get("progress", 0)),
                "details": details
            }
        )
    elif code == "NO_CURRENT_MODEL":
        raise HTTPException(
            status_code=400,
            detail={
                "code": code,
                "message": i18n.t("model.rebuild_no_current_model", locale)
            }
        )
    elif code == "BACKUP_FAILED":
        raise HTTPException(
            status_code=500,
            detail={
                "code": code,
                "message": i18n.t("model.rebuild_backup_failed", locale, error=error.get("message", ""))
            }
        )
    elif code == "NO_INDEX_FILES":
        raise HTTPException(
            status_code=400,
            detail={
                "code": code,
                "message": i18n.t("model.rebuild_no_index_files", locale)
            }
        )
    else:
        raise HTTPException(
            status_code=500,
            detail={
                "code": code,
                "message": i18n.t("model.rebuild_start_failed", locale, error=error.get("message", ""))
            }
        )


@router.get("/status")
async def get_rebuild_status(accept_language: Optional[str] = Header(None)):
    """
    查询重建状态（内存查询，不访问数据库）

    Args:
        accept_language: Accept-Language 头，用于国际化

    Returns:
        重建状态信息
    """
    locale = get_locale_from_header(accept_language)
    service = get_index_rebuild_service()
    result = service.get_status()

    # 添加国际化状态消息
    if result.get("data"):
        status = result["data"].get("status")
        if status == "none":
            result["data"]["status_message"] = i18n.t("index_rebuild.status_none", locale)
        elif status == "running":
            result["data"]["status_message"] = i18n.t("index_rebuild.status_running", locale)
        elif status == "completed":
            result["data"]["status_message"] = i18n.t("index_rebuild.status_completed", locale)
        elif status == "failed":
            result["data"]["status_message"] = i18n.t("index_rebuild.status_failed", locale)
        elif status == "cancelled":
            result["data"]["status_message"] = i18n.t("index_rebuild.status_cancelled", locale)

    return result


@router.post("/cancel")
async def cancel_rebuild(accept_language: Optional[str] = Header(None)):
    """
    取消重建

    取消当前正在进行的重建任务，自动回滚到原模型配置

    Args:
        accept_language: Accept-Language 头，用于国际化

    Returns:
        取消结果
    """
    locale = get_locale_from_header(accept_language)
    service = get_index_rebuild_service()
    result = await service.cancel_rebuild()

    if result.get("success"):
        return result

    error = result.get("error", {})
    raise HTTPException(
        status_code=400,
        detail={
            "code": error.get("code"),
            "message": i18n.t("model.rebuild_cancel_failed", locale, error=error.get("message", ""))
        }
    )
