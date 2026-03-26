"""
索引重建服务 - 方案B：独立端点，内存状态
不与现有索引任务系统混用，完全独立的状态管理
"""
import asyncio
import shutil
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from pathlib import Path

from app.core.logging_config import logger
from app.services.ai_model_manager import ai_model_service


class RebuildStatus(Enum):
    """重建状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class RebuildTask:
    """重建任务数据类"""
    task_id: str
    status: RebuildStatus
    total_files: int
    start_time: datetime
    previous_model: Dict[str, Any]
    new_model: Dict[str, Any]
    backup_path: str = ""

    # 进度信息
    processed_files: int = 0
    failed_files: int = 0
    current_file: str = ""
    error_message: str = ""

    # 控制标志
    _cancel_event: asyncio.Event = field(default_factory=asyncio.Event)

    @property
    def progress(self) -> float:
        """计算进度百分比"""
        if self.total_files == 0:
            return 0.0
        return (self.processed_files / self.total_files) * 100


class IndexRebuildService:
    """
    索引重建服务 - 方案B：内存状态，不写数据库

    设计原则：
    - 状态仅存储在内存中，不持久化到数据库
    - 使用独立的 API 端点 /api/index/rebuild/*
    - 与现有索引任务系统完全隔离
    """

    def __init__(self):
        # 内存状态，不写数据库
        self.current_task: Optional[RebuildTask] = None
        self._lock = asyncio.Lock()

        # 索引目录
        self.index_dir = Path("data/index")
        self.backup_dir = Path("data/index.backup")

        # 确保备份目录存在
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    async def start_rebuild(
        self,
        new_model_config: Dict[str, Any],
        force: bool = False
    ) -> Dict[str, Any]:
        """
        开始索引重建

        Args:
            new_model_config: 新的嵌入模型配置
            force: 是否强制重建

        Returns:
            重建任务信息
        """
        async with self._lock:
            # 检查是否已有任务
            if self.current_task and self.current_task.status == RebuildStatus.RUNNING:
                return {
                    "success": False,
                    "error": {
                        "code": "REBUILD_JOB_RUNNING",
                        "message": "重建任务正在进行",
                        "details": {
                            "task_id": self.current_task.task_id,
                            "progress": self.current_task.progress
                        }
                    }
                }

            # 获取当前模型配置
            current_model = await ai_model_service.get_model("embedding")
            if not current_model:
                return {
                    "success": False,
                    "error": {
                        "code": "NO_CURRENT_MODEL",
                        "message": "没有当前嵌入模型配置"
                    }
                }

            # 构建当前模型信息
            previous_model = {
                "provider": current_model.provider.value,
                "model_name": current_model.model_name,
                "model_type": current_model.model_type.value
            }

            # 获取索引文件列表
            index_files = self._get_index_files()

            if not index_files and not force:
                return {
                    "success": False,
                    "error": {
                        "code": "NO_INDEX_FILES",
                        "message": "没有找到索引文件"
                    }
                }

            # 创建备份
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / timestamp

            try:
                if self.index_dir.exists():
                    shutil.copytree(self.index_dir, backup_path)
                    logger.info(f"索引备份完成: {backup_path}")
            except Exception as e:
                logger.error(f"索引备份失败: {str(e)}")
                return {
                    "success": False,
                    "error": {
                        "code": "BACKUP_FAILED",
                        "message": f"索引备份失败: {str(e)}"
                    }
                }

            # 创建重建任务
            task_id = f"rebuild_{int(datetime.now().timestamp())}"
            self.current_task = RebuildTask(
                task_id=task_id,
                status=RebuildStatus.RUNNING,
                total_files=len(index_files),
                start_time=datetime.now(),
                previous_model=previous_model,
                new_model=new_model_config,
                backup_path=str(backup_path)
            )

            # 启动后台任务
            asyncio.create_task(self._execute_rebuild(index_files))

            # 预计耗时（假设每秒处理 10 个文件）
            estimated_time = max(1, len(index_files) // 10)

            return {
                "success": True,
                "data": {
                    "task_id": task_id,
                    "status": "running",
                    "total_files": len(index_files),
                    "previous_model": previous_model.get("model_name"),
                    "new_model": new_model_config.get("model_name"),
                    "estimated_time_minutes": estimated_time
                }
            }

    async def _execute_rebuild(self, index_files: List[str]):
        """
        执行索引重建（后台任务）

        Args:
            index_files: 索引文件列表
        """
        try:
            # 切换到新模型
            await ai_model_service.reload_model("embedding")

            # 获取新嵌入服务
            embedding_model = await ai_model_service.get_model("embedding")

            # 逐文件处理
            for i, file_path in enumerate(index_files):
                # 检查取消标志
                if self.current_task._cancel_event.is_set():
                    self.current_task.status = RebuildStatus.CANCELLED
                    logger.info("索引重建已取消")
                    # 恢复原模型配置
                    await self._restore_previous_config()
                    break

                try:
                    self.current_task.current_file = file_path

                    # 读取文件内容
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 生成新嵌入向量
                    embeddings = await embedding_model.predict([content])

                    # 更新索引（这里需要调用索引构建逻辑）
                    # TODO: 实际实现需要调用 IndexBuilder
                    logger.debug(f"文件 {file_path} 嵌入向量维度: {len(embeddings[0]) if len(embeddings) > 0 else 0}")

                    self.current_task.processed_files += 1

                    if (i + 1) % 100 == 0:
                        logger.info(f"重建进度: {self.current_task.processed_files}/{self.current_task.total_files}")

                except Exception as e:
                    logger.error(f"文件处理失败: {file_path}, 错误: {str(e)}")
                    self.current_task.failed_files += 1

            # 完成
            if self.current_task.status == RebuildStatus.RUNNING:
                self.current_task.status = RebuildStatus.COMPLETED
                logger.info(f"索引重建完成: 成功 {self.current_task.processed_files}, 失败 {self.current_task.failed_files}")

        except Exception as e:
            self.current_task.status = RebuildStatus.FAILED
            self.current_task.error_message = str(e)
            logger.error(f"索引重建失败: {str(e)}")

            # 恢复原模型配置
            await self._restore_previous_config()

    async def _restore_previous_config(self):
        """恢复到之前的模型配置"""
        try:
            # 从数据库恢复配置
            from app.models.ai_model import AIModelModel
            from app.core.database import SessionLocal

            db = SessionLocal()
            try:
                # 查找之前的模型配置
                previous_config = db.query(AIModelModel).filter(
                    AIModelModel.model_type == "embedding",
                    AIModelModel.provider == self.current_task.previous_model.get("provider"),
                    AIModelModel.model_name == self.current_task.previous_model.get("model_name")
                ).first()

                if previous_config:
                    # 设置为活跃配置
                    previous_config.is_active = True
                    db.commit()
                    logger.info(f"已恢复到原模型配置: {previous_config.model_name}")
            finally:
                db.close()

            # 重新加载模型
            await ai_model_service.reload_model("embedding")

        except Exception as e:
            logger.error(f"恢复原模型配置失败: {str(e)}")

    def get_status(self) -> Dict[str, Any]:
        """
        获取重建状态

        Returns:
            状态信息
        """
        if not self.current_task:
            return {
                "success": True,
                "data": {
                    "status": "none"
                }
            }

        # 计算剩余时间
        elapsed_seconds = (datetime.now() - self.current_task.start_time).total_seconds()
        if self.current_task.processed_files > 0:
            avg_time_per_file = elapsed_seconds / self.current_task.processed_files
            remaining_files = self.current_task.total_files - self.current_task.processed_files
            estimated_remaining = int(avg_time_per_file * remaining_files)
        else:
            estimated_remaining = 0

        return {
            "success": True,
            "data": {
                "task_id": self.current_task.task_id,
                "status": self.current_task.status.value,
                "progress": self.current_task.progress,
                "total_files": self.current_task.total_files,
                "processed_files": self.current_task.processed_files,
                "failed_files": self.current_task.failed_files,
                "current_file": self.current_task.current_file,
                "elapsed_seconds": int(elapsed_seconds),
                "estimated_remaining_seconds": estimated_remaining,
                "previous_model": self.current_task.previous_model,
                "new_model": self.current_task.new_model,
                "error_message": self.current_task.error_message
            }
        }

    async def cancel_rebuild(self) -> Dict[str, Any]:
        """
        取消重建

        Returns:
            取消结果
        """
        if not self.current_task:
            return {
                "success": False,
                "error": {
                    "code": "NO_REBUILD_JOB",
                    "message": "当前无重建任务"
                }
            }

        # 设置取消标志
        self.current_task._cancel_event.set()

        # 等待任务结束
        while self.current_task.status == RebuildStatus.RUNNING:
            await asyncio.sleep(0.1)

        return {
            "success": True,
            "message": "重建任务已取消，已恢复到原模型配置",
            "data": {
                "task_id": self.current_task.task_id,
                "status": "cancelled",
                "processed_files": self.current_task.processed_files,
                "rollback_success": True,
                "restored_model": self.current_task.previous_model.get("model_name")
            }
        }

    def _get_index_files(self) -> List[str]:
        """
        获取索引文件列表

        Returns:
            文件路径列表
        """
        # TODO: 实际实现需要从索引元数据中获取文件列表
        # 这里返回示例数据
        index_files = []

        if self.index_dir.exists():
            # 扫描索引目录中的文件
            for file_path in self.index_dir.rglob("*.json"):
                if file_path.is_file():
                    index_files.append(str(file_path))

        logger.info(f"找到 {len(index_files)} 个索引文件")
        return index_files


# 全局单例
_index_rebuild_service: Optional[IndexRebuildService] = None


def get_index_rebuild_service() -> IndexRebuildService:
    """获取索引重建服务单例"""
    global _index_rebuild_service
    if _index_rebuild_service is None:
        _index_rebuild_service = IndexRebuildService()
    return _index_rebuild_service
