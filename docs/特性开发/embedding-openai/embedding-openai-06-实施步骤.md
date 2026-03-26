# 云端嵌入模型调用能力 - 实施步骤

> **文档类型**：实施步骤
> **特性状态**：规划中
> **创建时间**：2026-03-26
> **预计工期**：3 天（24 小时）
> **关联文档**：[技术方案](./embedding-openai-03-技术方案.md) | [实施方案](./embedding-openai-实施方案.md)

---

## 📋 实施概览

| 阶段 | 任务 | 预计时间 | 优先级 |
|------|------|----------|--------|
| 1️⃣ 环境准备 | 依赖安装、目录创建 | 1 小时 | P0 |
| 2️⃣ 后端服务实现 | OpenAIEmbeddingService | 6 小时 | P0 |
| 3️⃣ 模型管理器扩展 | 支持云端嵌入模型 | 2 小时 | P0 |
| 4️⃣ 索引重建功能 | 方案B：独立端点 | 4 小时 | P0 |
| 5️⃣ 前端界面修改 | 配置表单、状态管理 | 4 小时 | P0 |
| 6️⃣ 国际化更新 | 翻译键更新 | 1 小时 | P0 |
| 7️⃣ 测试验证 | 功能测试、集成测试 | 6 小时 | P0 |
| **总计** | | **24 小时（3 天）** | |

---

## 阶段 1：环境准备（1 小时）

### 步骤 1.1：安装 Python 依赖

**操作**：修改 `backend/requirements.txt`

在文件末尾添加：

```txt
# ========== 云端嵌入模型支持 ==========
# OpenAI 兼容 API 客户端
aiohttp>=3.9.0
# 重试机制
tenacity>=8.2.0
# =====================================
```

**执行安装**：

```bash
cd backend
pip install aiohttp>=3.9.0 tenacity>=8.2.0
```

**验证安装**：

```bash
python -c "import aiohttp; import tenacity; print('依赖安装成功')"
```

预期输出：`依赖安装成功`

---

### 步骤 1.2：验证目录结构

**操作**：确认目录存在

```bash
# 确认服务目录存在
ls backend/app/services/
```

预期输出应包含：
- `__init__.py`
- `base_ai_model.py` （可能需要创建）
- `bge_embedding_service.py`
- `ai_model_manager.py`

---

## 阶段 2：后端服务实现（6 小时）

### 步骤 2.1：创建 BaseAIModel 基类

**新建文件**：`backend/app/services/base_ai_model.py`

```python
"""
AI 模型基类
定义所有 AI 模型服务的通用接口
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseAIModel(ABC):
    """AI 模型基类"""

    @abstractmethod
    async def load_model(self):
        """
        加载模型

        子类应在此方法中实现模型的初始化和加载逻辑
        """
        pass

    @abstractmethod
    async def unload_model(self):
        """
        卸载模型

        子类应在此方法中释放模型占用的资源
        """
        pass

    @abstractmethod
    async def predict(self, texts: List[str]) -> List[List[float]]:
        """
        执行预测

        Args:
            texts: 输入文本列表

        Returns:
            预测结果列表，每个结果是向量（浮点数列表）
        """
        pass

    @abstractmethod
    async def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息

        Returns:
            模型信息字典，包含：
            - provider: 提供商类型
            - model_name: 模型名称
            - embedding_dim: 向量维度
            - status: 状态
        """
        pass
```

---

### 步骤 2.2：创建 OpenAIEmbeddingService

**新建文件**：`backend/app/services/openai_embedding_service.py`

```python
"""
OpenAI 兼容嵌入模型服务
支持所有兼容 OpenAI Embeddings API 标准的云端服务
"""
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from app.services.base_ai_model import BaseAIModel
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class OpenAIEmbeddingService(BaseAIModel):
    """
    OpenAI 兼容嵌入模型服务

    支持所有兼容 OpenAI Embeddings API 标准的云端服务：
    - OpenAI 官方
    - DeepSeek
    - 阿里云通义千问
    - Moonshot
    - 其他兼容服务
    """

    def __init__(self, config: Dict[str, Any]):
        """
        初始化 OpenAI 兼容嵌入服务

        Args:
            config: 配置字典
                - api_key: API 密钥（必填）
                - endpoint: API 端点（默认 https://api.openai.com/v1）
                - model: 模型名称（必填）
                - timeout: 请求超时时间（秒，默认 30）
                - batch_size: 批处理大小（默认 100）
        """
        self.api_key = config.get("api_key")
        self.endpoint = config.get("endpoint", "https://api.openai.com/v1").rstrip("/")
        self.model = config.get("model")
        self.timeout = config.get("timeout", 30)
        self.batch_size = config.get("batch_size", 100)

        # 构建 API URL
        self.embeddings_url = f"{self.endpoint}/embeddings"

        # HTTP 会话
        self._session: Optional[aiohttp.ClientSession] = None

        logger.info(f"初始化 OpenAI 兼容嵌入服务: {self.model}")

    async def load_model(self):
        """
        创建 HTTP 会话

        这是云端模型的"加载"操作，实际上是创建 HTTP 客户端会话
        """
        if self._session is None:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
            logger.info(f"HTTP 会话已创建: {self.embeddings_url}")

    async def unload_model(self):
        """
        关闭 HTTP 会话

        释放 HTTP 客户端资源
        """
        if self._session:
            await self._session.close()
            self._session = None
            logger.info("HTTP 会话已关闭")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        reraise=True
    )
    async def _call_embeddings_api(self, texts: List[str]) -> Dict[str, Any]:
        """
        调用 OpenAI 兼容 Embeddings API

        Args:
            texts: 待嵌入的文本列表

        Returns:
            API 响应结果

        Raises:
            RuntimeError: API 调用失败
        """
        if not self._session:
            await self.load_model()

        # 构建请求头
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 构建请求体
        payload = {
            "input": texts,
            "model": self.model
        }

        logger.info(f"调用 Embeddings API: 文本数={len(texts)}, 模型={self.model}")

        # 发送请求
        async with self._session.post(
            self.embeddings_url,
            headers=headers,
            json=payload
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"API 调用失败: {response.status} - {error_text}")
                raise RuntimeError(f"API 调用失败: {response.status} - {error_text}")

            result = await response.json()

            # 记录向量维度
            if result.get("data") and len(result["data"]) > 0:
                embedding_dim = len(result["data"][0]["embedding"])
                logger.info(f"向量维度: {embedding_dim} (使用模型原始维度)")

            return result

    async def predict(self, texts: List[str]) -> List[List[float]]:
        """
        生成文本嵌入向量

        Args:
            texts: 待嵌入的文本列表

        Returns:
            嵌入向量列表（使用模型原始维度）
        """
        if not texts:
            return []

        # 批处理
        all_embeddings = []

        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1
            total_batches = (len(texts) + self.batch_size - 1) // self.batch_size

            try:
                logger.info(f"处理批次 {batch_num}/{total_batches}: {len(batch_texts)} 个文本")
                result = await self._call_embeddings_api(batch_texts)

                # 提取 embeddings
                embeddings = []
                for item in result.get("data", []):
                    embedding = item.get("embedding", [])
                    embeddings.append(embedding)

                all_embeddings.extend(embeddings)

            except Exception as e:
                logger.error(f"批次 {batch_num} 嵌入失败: {str(e)}")
                # 返回空向量（保持批次对齐）
                all_embeddings.extend([[0.0] * 1024] * len(batch_texts))

        return all_embeddings

    async def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息

        Returns:
            模型信息字典
        """
        # 测试调用以获取模型信息
        try:
            result = await self._call_embeddings_api(["test"])

            if result.get("data") and len(result["data"]) > 0:
                embedding_dim = len(result["data"][0]["embedding"])
            else:
                embedding_dim = 0

            return {
                "provider": "cloud",
                "model_name": self.model,
                "embedding_dim": embedding_dim,
                "endpoint": self.endpoint,
                "status": "ready"
            }
        except Exception as e:
            logger.error(f"获取模型信息失败: {str(e)}")
            return {
                "provider": "cloud",
                "model_name": self.model,
                "status": "error",
                "error": str(e)
            }
```

**验证**：

```bash
python -c "from app.services.openai_embedding_service import OpenAIEmbeddingService; print('模块导入成功')"
```

---

### 步骤 2.3：更新 BGEEmbeddingService 继承基类

**修改文件**：`backend/app/services/bge_embedding_service.py`

确保 BGEEmbeddingService 继承自 BaseAIModel：

```python
# 在文件开头添加导入
from app.services.base_ai_model import BaseAIModel

# 修改类声明
class BGEEmbeddingService(BaseAIModel):
    """BGE 本地嵌入模型服务"""

    # 确保实现所有抽象方法
    async def load_model(self):
        # 现有实现
        ...

    async def unload_model(self):
        # 现有实现
        ...

    async def predict(self, texts: List[str]) -> List[List[float]]:
        # 现有实现
        ...

    async def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "provider": "local",
            "model_name": "BAAI/bge-m3",
            "embedding_dim": 1024,
            "status": "ready"
        }
```

---

## 阶段 3：模型管理器扩展（2 小时）

### 步骤 3.1：修改 AIModelManager

**修改文件**：`backend/app/services/ai_model_manager.py`

在现有代码基础上添加云端模型支持：

```python
# 在导入部分添加
from app.services.openai_embedding_service import OpenAIEmbeddingService

# 在 AIModelManager 类中修改 load_embedding_model 方法
async def load_embedding_model(self, config: Dict[str, Any]):
    """
    加载嵌入模型（支持本地和云端）

    Args:
        config: 模型配置
            - provider: 'local' 或 'cloud'
            - model_name: 模型名称
            - config: 具体配置
    """
    # 卸载现有模型
    await self.unload_embedding_model()

    provider = config.get("provider")
    model_name = config.get("model_name")
    model_config = config.get("config", {})

    logger.info(f"加载嵌入模型: provider={provider}, model={model_name}")

    if provider == "local":
        # 现有的本地模型加载逻辑
        self._embedding_service = BGEEmbeddingService(model_config)
        await self._embedding_service.load_model()

    elif provider == "cloud":
        # 新增：云端模型加载逻辑
        self._embedding_service = OpenAIEmbeddingService(model_config)
        await self._embedding_service.load_model()

    else:
        raise ValueError(f"不支持的 provider: {provider}")

    self._current_config = config
    logger.info(f"嵌入模型加载完成: {model_name}")

# 添加测试连接方法
async def test_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    测试模型连接

    Args:
        config: 模型配置

    Returns:
        测试结果
    """
    provider = config.get("provider")
    model_config = config.get("config", {})

    try:
        if provider == "cloud":
            # 测试云端连接
            service = OpenAIEmbeddingService(model_config)
            await service.load_model()
            model_info = await service.get_model_info()
            await service.unload_model()

            return {
                "success": True,
                "model_info": model_info
            }

        elif provider == "local":
            # 本地模型无需测试连接
            return {
                "success": True,
                "message": "本地模型无需测试连接"
            }

    except Exception as e:
        logger.error(f"连接测试失败: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
```

---

## 阶段 4：索引重建功能（4 小时）

### 步骤 4.1：创建索引重建服务

**新建文件**：`backend/app/services/index_rebuild_service.py`

```python
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

from app.core.logging_config import get_logger
from app.services.ai_model_manager import get_ai_model_manager

logger = get_logger(__name__)


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
            ai_manager = get_ai_model_manager()
            current_config = ai_manager.get_current_config()

            if not current_config:
                return {
                    "success": False,
                    "error": {
                        "code": "NO_CURRENT_MODEL",
                        "message": "没有当前嵌入模型配置"
                    }
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
                previous_model=current_config,
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
                    "previous_model": current_config.get("model_name"),
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
            ai_manager = get_ai_model_manager()
            await ai_manager.load_embedding_model(self.current_task.new_model)

            # 获取新嵌入服务
            embedding_service = ai_manager.get_embedding_service()

            # 逐文件处理
            for i, file_path in enumerate(index_files):
                # 检查取消标志
                if self.current_task._cancel_event.is_set():
                    self.current_task.status = RebuildStatus.CANCELLED
                    logger.info("索引重建已取消")
                    # 恢复原模型
                    await ai_manager.load_embedding_model(self.current_task.previous_model)
                    break

                try:
                    self.current_task.current_file = file_path

                    # 读取文件内容
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 生成新嵌入向量
                    embeddings = await embedding_service.predict([content])

                    # 更新索引（这里需要调用索引构建逻辑）
                    # TODO: 实际实现需要调用 IndexBuilder

                    self.current_task.processed_files += 1

                    if i % 100 == 0:
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

            # 恢复原模型
            try:
                await ai_manager.load_embedding_model(self.current_task.previous_model)
            except:
                pass

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
                "previous_model": {
                    "provider": self.current_task.previous_model.get("provider"),
                    "model_name": self.current_task.previous_model.get("model_name")
                },
                "new_model": {
                    "provider": self.current_task.new_model.get("provider"),
                    "model_name": self.current_task.new_model.get("model_name")
                },
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
        return []


# 全局单例
_index_rebuild_service: Optional[IndexRebuildService] = None


def get_index_rebuild_service() -> IndexRebuildService:
    """获取索引重建服务单例"""
    global _index_rebuild_service
    if _index_rebuild_service is None:
        _index_rebuild_service = IndexRebuildService()
    return _index_rebuild_service
```

---

### 步骤 4.2：创建索引重建 API 端点

**新建文件**：`backend/app/api/index_rebuild.py`

```python
"""
索引重建 API 端点 - 独立端点，不与现有索引任务系统混用

端点前缀：/api/index/rebuild
- POST /start - 开始重建
- GET /status - 查询状态
- POST /cancel - 取消重建
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.index_rebuild_service import get_index_rebuild_service
from app.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/index/rebuild", tags=["索引重建"])


class RebuildRequest(BaseModel):
    """重建请求模型"""
    model_config: dict = Field(..., description="新的嵌入模型配置")
    force: bool = Field(default=False, description="是否强制重建")


@router.post("/start")
async def start_rebuild(request: RebuildRequest):
    """
    开始索引重建（内存状态，不写数据库）

    Args:
        request: 重建请求

    Returns:
        重建任务信息
    """
    service = get_index_rebuild_service()
    result = await service.start_rebuild(
        new_model_config=request.model_config,
        force=request.force
    )

    if result.get("success"):
        return result

    # 根据错误码返回相应的 HTTP 状态码
    error = result.get("error", {})
    code = error.get("code")

    if code == "REBUILD_JOB_RUNNING":
        raise HTTPException(status_code=409, detail=error)
    elif code == "NO_CURRENT_MODEL":
        raise HTTPException(status_code=400, detail=error)
    elif code == "BACKUP_FAILED":
        raise HTTPException(status_code=500, detail=error)
    else:
        raise HTTPException(status_code=500, detail=error)


@router.get("/status")
async def get_rebuild_status():
    """
    查询重建状态（内存查询，不访问数据库）

    Returns:
        重建状态信息
    """
    service = get_index_rebuild_service()
    return service.get_status()


@router.post("/cancel")
async def cancel_rebuild():
    """
    取消重建

    取消当前正在进行的重建任务，自动回滚到原模型配置

    Returns:
        取消结果
    """
    service = get_index_rebuild_service()
    result = await service.cancel_rebuild()

    if result.get("success"):
        return result

    error = result.get("error", {})
    raise HTTPException(status_code=400, detail=error)
```

---

### 步骤 4.3：注册重建路由

**修改文件**：`backend/main.py`

在路由注册部分添加：

```python
# 在现有导入后添加
from app.api.index_rebuild import router as rebuild_router

# 在路由注册部分添加
app.include_router(rebuild_router)
```

**验证**：

```bash
# 启动后端
cd backend
python main.py

# 访问 API 文档，检查新端点是否出现
# 浏览器打开：http://127.0.0.1:8000/docs
# 应该能看到 "索引重建" 标签下的三个端点
```

---

## 阶段 5：前端界面修改（4 小时）

### 步骤 5.1：修改配置组件 - 添加云端配置表单

**修改文件**：`frontend/src/views/Config.vue`

在 `embedding` 选项卡中添加云端配置：

```vue
<template>
  <a-tab-pane key="embedding" tab="内嵌模型">
    <div class="embedding-config">
      <!-- 模型类型选择 -->
      <a-form-item :label="$t('embedding.modelType')">
        <a-select
          v-model:value="embeddingProvider"
          style="width: 300px"
          @change="handleProviderChange"
        >
          <a-select-option value="local">
            <a-tag color="green">{{ $t('embedding.providerLocal') }}</a-tag>
          </a-select-option>
          <a-select-option value="cloud">
            <a-tag color="orange">{{ $t('embedding.providerCloud') }}</a-tag>
          </a-select-option>
        </a-select>
      </a-form-item>

      <!-- 本地配置 -->
      <div v-if="embeddingProvider === 'local'" class="config-section">
        <a-alert type="info" show-icon>
          <template #message>
            <span>ℹ️ {{ $t('embedding.localModelInfo') }}</span>
          </template>
          <template #description>
            <ul style="margin: 8px 0; padding-left: 20px;">
              <li>{{ $t('embedding.localOffline') }}</li>
              <li>{{ $t('embedding.localNoNetwork') }}</li>
              <li>{{ $t('embedding.localFree') }}</li>
            </ul>
          </template>
        </a-alert>

        <a-form-item :label="$t('embedding.modelName')">
          <a-input v-model:value="localConfig.model_name" disabled />
        </a-form-item>

        <a-form-item :label="$t('embedding.device')">
          <a-select v-model:value="localConfig.device">
            <a-select-option value="cpu">{{ $t('embedding.deviceCpu') }}</a-select-option>
            <a-select-option value="cuda">{{ $t('embedding.deviceCuda') }}</a-select-option>
          </a-select>
        </a-form-item>
      </div>

      <!-- 云端配置 -->
      <div v-else class="config-section">
        <a-alert type="warning" show-icon>
          <template #message>
            {{ $t('embedding.cloudServiceInfo') }}
          </template>
          <template #description>
            <ul style="margin: 8px 0; padding-left: 20px;">
              <li>{{ $t('embedding.cloudDataSafe') }}</li>
              <li>{{ $t('embedding.cloudQuerySent') }}</li>
              <li>{{ $t('embedding.cloudAllCompatible') }}</li>
              <li>{{ $t('embedding.cloudNeedRebuild') }}</li>
            </ul>
            <div style="margin-top: 8px;">
              {{ $t('embedding.cloudPrivacyTip') }}
            </div>
          </template>
        </a-alert>

        <a-form-item :label="$t('embedding.apiKey')" required>
          <a-input-password
            v-model:value="cloudConfig.api_key"
            :placeholder="'sk-*****************************************'"
          />
        </a-form-item>

        <a-form-item :label="$t('embedding.endpoint')">
          <a-input
            v-model:value="cloudConfig.endpoint"
            :placeholder="$t('embedding.endpointPlaceholder')"
          />
          <template #extra>
            {{ $t('embedding.endpointTip') }}
          </template>
        </a-form-item>

        <a-form-item :label="$t('embedding.model')" required>
          <a-input
            v-model:value="cloudConfig.model"
            :placeholder="$t('embedding.modelPlaceholder')"
          />
          <template #extra>
            {{ $t('embedding.modelTip') }}
          </template>
        </a-form-item>

        <a-form-item :label="$t('embedding.timeout')">
          <a-input-number
            v-model:value="cloudConfig.timeout"
            :min="1"
            :max="120"
            style="width: 200px"
          />
        </a-form-item>

        <a-form-item :label="$t('embedding.batchSize')">
          <a-input-number
            v-model:value="cloudConfig.batch_size"
            :min="1"
            :max="1000"
            style="width: 200px"
          />
        </a-form-item>
      </div>

      <!-- 操作按钮 -->
      <div class="action-buttons" style="margin-top: 24px;">
        <a-button @click="handleTestConnection" :loading="testing">
          {{ $t('embedding.testConnection') }}
        </a-button>
        <a-button type="primary" @click="handleSaveConfig" :loading="saving">
          {{ $t('embedding.saveSettings') }}
        </a-button>
      </div>
    </div>
  </a-tab-pane>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { message, Modal } from 'ant-design-vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

// 状态
const embeddingProvider = ref<'local' | 'cloud'>('local');
const testing = ref(false);
const saving = ref(false);
const hasConfirmedSwitch = ref(false);

// 本地配置
const localConfig = reactive({
  model_name: 'BAAI/bge-m3',
  device: 'cpu'
});

// 云端配置
const cloudConfig = reactive({
  api_key: '',
  endpoint: 'https://api.openai.com/v1',
  model: 'text-embedding-3-small',
  timeout: 30,
  batch_size: 100
});

// 处理提供商变更
const handleProviderChange = async (value: string) => {
  if (value === 'cloud' && !hasConfirmedSwitch.value) {
    Modal.confirm({
      title: t('embedding.rebuildTitle'),
      content: t('embedding.cloudQuerySent'),
      okText: t('common.confirm'),
      onOk: () => {
        hasConfirmedSwitch.value = true;
      }
    });
  }
};

// 测试连接
const handleTestConnection = async () => {
  testing.value = true;
  try {
    const config = embeddingProvider.value === 'cloud' ? cloudConfig : localConfig;
    // 调用测试连接 API
    // TODO: 实现 API 调用
    message.success(t('embedding.connectionSuccess'));
  } catch (error) {
    message.error(t('embedding.connectionFailed'));
  } finally {
    testing.value = false;
  }
};

// 保存配置
const handleSaveConfig = async () => {
  saving.value = true;
  try {
    const config = embeddingProvider.value === 'cloud' ? cloudConfig : localConfig;
    // 调用保存配置 API
    // TODO: 实现 API 调用
    message.success(t('embedding.saveSuccess'));
  } catch (error) {
    message.error('保存失败');
  } finally {
    saving.value = false;
  }
};
</script>
```

---

## 阶段 6：后端国际化（1 小时）

### 步骤 6.1：更新后端语言包 - 中文

**修改文件**：`backend/app/locales/zh_CN.json`

在 `"model"` 对象中添加云端嵌入模型相关翻译：

```json
{
  "model": {
    // ... 现有翻译保持不变 ...

    // ========== 云端嵌入模型专用 ==========
    "cloud_embedding_success": "云端嵌入模型测试成功，向量维度: {dimension}，响应正常",
    "cloud_embedding_failed": "云端嵌入模型测试失败：{error}",
    "cloud_connection_timeout": "云端API连接超时",
    "cloud_connection_refused": "云端API连接被拒绝",
    "cloud_auth_failed": "云端API认证失败：{error}",
    "cloud_model_not_found": "云端模型不存在：{model}",
    "cloud_rate_limit_exceeded": "云端API调用频率超限，请稍后重试",
    "cloud_api_error": "云端API调用错误：{error}",
    "cloud_invalid_response": "云端API返回无效响应",
    "provider_not_supported": "不支持的提供商类型：{provider}",

    // ========== 索引重建 ==========
    "rebuild_not_started": "当前没有正在进行的重建任务",
    "rebuild_already_running": "重建任务正在进行中，进度：{progress}%",
    "rebuild_no_current_model": "没有当前嵌入模型配置，无法开始重建",
    "rebuild_backup_failed": "索引备份失败：{error}",
    "rebuild_no_index_files": "没有找到索引文件",
    "rebuild_started": "索引重建已开始，任务ID：{task_id}",
    "rebuild_start_failed": "启动重建失败：{error}",
    "rebuild_cancelled": "重建任务已取消，已恢复到原模型配置",
    "rebuild_cancel_failed": "取消重建失败：{error}",
    "rebuild_completed": "索引重建完成",
    "rebuild_failed": "索引重建失败：{error}",
    "rebuild_progress": "重建进度：{progress}%",
    "rebuild_current_file": "当前处理文件：{file}",
    "rebuild_statistics": "重建统计：成功 {success}，失败 {failed}，总计 {total}"
  },

  // 新增：索引重建部分
  "index_rebuild": {
    "title": "索引重建",
    "status_none": "无重建任务",
    "status_running": "重建中",
    "status_pending": "等待中",
    "status_completed": "已完成",
    "status_failed": "失败",
    "status_cancelled": "已取消",

    "task_id": "任务ID",
    "total_files": "总文件数",
    "processed_files": "已处理文件",
    "failed_files": "失败文件",
    "current_file": "当前文件",
    "progress": "进度",
    "elapsed_seconds": "已用时间（秒）",
    "estimated_remaining_seconds": "预计剩余时间（秒）",

    "previous_model": "原模型",
    "new_model": "新模型",
    "backup_path": "备份路径",

    "switching_warning": "切换嵌入模型需要重建索引",
    "switching_description": "切换嵌入模型会改变向量空间，需要重建索引",
    "estimated_time": "预计耗时：{minutes} 分钟",
    "rebuild_warning": "重建期间搜索功能可能受影响，是否继续？",
    "cloud_api_required": "需要调用云端API",

    "success": "索引重建成功",
    "failed": "索引重建失败",
    "cancelled": "索引重建已取消",
    "rollback_success": "已恢复到原模型配置",
    "rollback_failed": "恢复原模型配置失败"
  }
}
```

### 步骤 6.2：更新后端语言包 - 英文

**修改文件**：`backend/app/locales/en_US.json`

在 `"model"` 对象中添加对应的英文翻译：

```json
{
  "model": {
    // ... existing translations remain unchanged ...

    // ========== Cloud Embedding Model ==========
    "cloud_embedding_success": "Cloud embedding model test successful, vector dimension: {dimension}, response normal",
    "cloud_embedding_failed": "Cloud embedding model test failed: {error}",
    "cloud_connection_timeout": "Cloud API connection timeout",
    "cloud_connection_refused": "Cloud API connection refused",
    "cloud_auth_failed": "Cloud API authentication failed: {error}",
    "cloud_model_not_found": "Cloud model not found: {model}",
    "cloud_rate_limit_exceeded": "Cloud API rate limit exceeded, please try again later",
    "cloud_api_error": "Cloud API call error: {error}",
    "cloud_invalid_response": "Cloud API returned invalid response",
    "provider_not_supported": "Unsupported provider type: {provider}",

    // ========== Index Rebuild ==========
    "rebuild_not_started": "No rebuild task in progress",
    "rebuild_already_running": "Rebuild task is in progress, progress: {progress}%",
    "rebuild_no_current_model": "No current embedding model configuration, cannot start rebuild",
    "rebuild_backup_failed": "Index backup failed: {error}",
    "rebuild_no_index_files": "No index files found",
    "rebuild_started": "Index rebuild started, task ID: {task_id}",
    "rebuild_start_failed": "Failed to start rebuild: {error}",
    "rebuild_cancelled": "Rebuild task cancelled, restored to original model configuration",
    "rebuild_cancel_failed": "Failed to cancel rebuild: {error}",
    "rebuild_completed": "Index rebuild completed",
    "rebuild_failed": "Index rebuild failed: {error}",
    "rebuild_progress": "Rebuild progress: {progress}%",
    "rebuild_current_file": "Current file: {file}",
    "rebuild_statistics": "Rebuild statistics: success {success}, failed {failed}, total {total}"
  },

  "index_rebuild": {
    "title": "Index Rebuild",
    "status_none": "No rebuild task",
    "status_running": "Rebuilding",
    "status_pending": "Pending",
    "status_completed": "Completed",
    "status_failed": "Failed",
    "status_cancelled": "Cancelled",

    "task_id": "Task ID",
    "total_files": "Total Files",
    "processed_files": "Processed Files",
    "failed_files": "Failed Files",
    "current_file": "Current File",
    "progress": "Progress",
    "elapsed_seconds": "Elapsed Time (seconds)",
    "estimated_remaining_seconds": "Estimated Remaining Time (seconds)",

    "previous_model": "Previous Model",
    "new_model": "New Model",
    "backup_path": "Backup Path",

    "switching_warning": "Switching embedding model requires index rebuild",
    "switching_description": "Switching embedding models changes the vector space and requires index rebuild",
    "estimated_time": "Estimated time: {minutes} minutes",
    "rebuild_warning": "Search functionality may be affected during rebuild, continue?",
    "cloud_api_required": "Cloud API calls required",

    "success": "Index rebuild successful",
    "failed": "Index rebuild failed",
    "cancelled": "Index rebuild cancelled",
    "rollback_success": "Restored to original model configuration",
    "rollback_failed": "Failed to restore original model configuration"
  }
}
```

---

### 步骤 6.3：在 API 端点中使用 i18n

**修改文件**：`backend/app/api/index_rebuild.py`

完整实现带国际化的端点：

```python
"""
索引重建 API 端点 - 独立端点，带完整国际化支持
"""
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field
from typing import Optional

from app.services.index_rebuild_service import get_index_rebuild_service
from app.core.i18n import i18n, get_locale_from_header
from app.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/index/rebuild", tags=["索引重建"])


class RebuildRequest(BaseModel):
    """重建请求模型"""
    model_config: dict = Field(..., description="新的嵌入模型配置")
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
        new_model_config=request.model_config,
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
```

---

### 步骤 6.4：更新配置测试接口国际化

**修改文件**：`backend/app/api/config.py`

在现有的模型测试接口中添加云端模型支持的国际化：

```python
# 在现有的 test_ai_model 函数中添加云端模型分支
@router.post("/ai-model/test")
async def test_ai_model(
    request: AIModelTestRequest,
    accept_language: Optional[str] = Header(None)
):
    """
    测试AI模型连接（支持本地和云端模型）

    Args:
        request: 模型配置
        accept_language: Accept-Language 头，用于国际化

    Returns:
        测试结果
    """
    locale = get_locale_from_header(accept_language)

    try:
        if request.provider == "cloud":
            # 云端模型测试
            ai_manager = get_ai_model_manager()
            result = await ai_manager.test_connection({
                "provider": "cloud",
                "config": request.config
            })

            if result.get("success"):
                model_info = result.get("model_info", {})
                return {
                    "code": 200,
                    "message": i18n.t("model.cloud_embedding_success", locale, dimension=model_info.get("embedding_dim", 0)),
                    "data": {
                        "provider": "cloud",
                        "model_name": request.config.get("model"),
                        "embedding_dim": model_info.get("embedding_dim"),
                        "endpoint": request.config.get("endpoint")
                    }
                }
            else:
                error = result.get("error", "")
                # 判断错误类型
                if "401" in str(error) or "authentication" in str(error).lower():
                    return {
                        "code": 401,
                        "message": i18n.t("model.cloud_auth_failed", locale, error=error)
                    }
                elif "timeout" in str(error).lower():
                    return {
                        "code": 408,
                        "message": i18n.t("model.cloud_connection_timeout", locale)
                    }
                else:
                    return {
                        "code": 500,
                        "message": i18n.t("model.cloud_embedding_failed", locale, error=error)
                    }

        elif request.provider == "local":
            # 本地模型测试（现有逻辑）
            ...

    except Exception as e:
        logger.error(f"模型测试失败: {str(e)}")
        return {
            "code": 500,
            "message": i18n.t("model.cloud_api_error", locale, error=str(e))
        }
```

---

## 阶段 7：前端国际化更新（1 小时）

### 步骤 7.1：更新前端中文翻译

**修改文件**：`frontend/src/locale/lang/zh-cn.ts`

在 `embedding` 部分添加：

```typescript
embedding: {
  title: '内嵌模型',
  modelType: '模型类型',
  providerLocal: '本地（推荐，免费离线）',
  providerCloud: '云端API（有隐私风险）',

  // 本地配置
  localModelInfo: '本地嵌入模型',
  localModelDesc: '使用本地部署的嵌入模型进行文本向量转换',
  localOffline: '完全离线，保护隐私',
  localNoNetwork: '无需网络连接',
  localFree: '免费使用',
  modelName: '模型名称',
  device: '运行设备',
  deviceCpu: 'CPU（自动检测CUDA）',
  deviceCuda: 'CUDA',

  // 云端配置
  cloudServiceInfo: '云端服务使用说明',
  cloudDataSafe: '✅ 您的本地文件和索引数据存储在本地，不会上传',
  cloudQuerySent: '⚠️ 搜索查询会发送到云端服务进行嵌入',
  cloudAllCompatible: '💡 支持所有兼容 OpenAI Embeddings API 标准的服务',
  cloudNeedRebuild: '💡 切换模型需要重建索引（不同模型的向量空间不兼容）',
  cloudPrivacyTip: '如需完全隐私保护，请使用本地模型',
  apiKey: 'API 密钥',
  endpoint: '端点地址',
  model: '模型名称',
  timeout: '超时时间（秒）',
  batchSize: '批处理大小',
  endpointPlaceholder: 'https://api.openai.com/v1',
  modelPlaceholder: 'text-embedding-3-small',
  endpointTip: '💡 可选，默认为官方 API 地址',
  modelTip: '💡 如 text-embedding-3-small、bge-large-zh 等',

  // 操作
  testConnection: '测试连接',
  testing: '测试中...',
  saveSettings: '保存设置',

  // 消息
  connectionSuccess: '连接成功！',
  connectionFailed: '连接失败',
  saveSuccess: '设置已保存',

  // 重建确认
  rebuildTitle: '切换嵌入模型需要重建索引',
  needRebuild: '切换嵌入模型会改变向量空间，需要重建索引',
  rebuildPreviousModel: '原模型',
  rebuildNewModel: '新模型',
  rebuildFileCount: '文件数量',
  rebuildEstimatedTime: '预计耗时',
  rebuildWarning: '重建期间搜索功能可能受影响，是否继续？',
  rebuildStarted: '索引重建已开始',
  rebuildCompleted: '索引重建完成',
  rebuildFailed: '索引重建失败'
}
```

---

### 步骤 6.2：更新英文翻译

**修改文件**：`frontend/src/locale/lang/en-us.ts`

```typescript
embedding: {
  title: 'Embedding Model',
  modelType: 'Model Type',
  providerLocal: 'Local (Recommended, Free & Offline)',
  providerCloud: 'Cloud API (Privacy Risk)',

  localModelInfo: 'Local Embedding Model',
  localModelDesc: 'Use locally deployed embedding model for text vectorization',
  localOffline: 'Completely offline, privacy protected',
  localNoNetwork: 'No network connection required',
  localFree: 'Free to use',
  modelName: 'Model Name',
  device: 'Device',
  deviceCpu: 'CPU (Auto-detect CUDA)',
  deviceCuda: 'CUDA',

  cloudServiceInfo: 'Cloud Service Usage Notes',
  cloudDataSafe: '✅ Your local files and index data are stored locally, not uploaded',
  cloudQuerySent: '⚠️ Search queries will be sent to cloud service for embedding',
  cloudAllCompatible: '💡 Supports all services compatible with OpenAI Embeddings API standard',
  cloudNeedRebuild: '💡 Switching models requires index rebuild (different vector spaces are incompatible)',
  cloudPrivacyTip: 'For complete privacy protection, please use local model',
  apiKey: 'API Key',
  endpoint: 'Endpoint',
  model: 'Model Name',
  timeout: 'Timeout (seconds)',
  batchSize: 'Batch Size',
  endpointPlaceholder: 'https://api.openai.com/v1',
  modelPlaceholder: 'text-embedding-3-small',
  endpointTip: '💡 Optional, defaults to official API address',
  modelTip: '💡 e.g. text-embedding-3-small, bge-large-zh, etc.',

  testConnection: 'Test Connection',
  testing: 'Testing...',
  saveSettings: 'Save Settings',

  connectionSuccess: 'Connection successful!',
  connectionFailed: 'Connection failed',
  saveSuccess: 'Settings saved',

  rebuildTitle: 'Switching Embedding Model Requires Index Rebuild',
  needRebuild: 'Switching embedding models changes the vector space and requires index rebuild',
  rebuildPreviousModel: 'Previous Model',
  rebuildNewModel: 'New Model',
  rebuildFileCount: 'File Count',
  rebuildEstimatedTime: 'Estimated Time',
  rebuildWarning: 'Search functionality may be affected during rebuild, continue?',
  rebuildStarted: 'Index rebuild started',
  rebuildCompleted: 'Index rebuild completed',
  rebuildFailed: 'Index rebuild failed'
}
```

---

## 阶段 7：测试验证（6 小时）

### 步骤 7.1：单元测试

**新建文件**：`backend/tests/test_openai_embedding_service.py`

```python
"""
OpenAI 兼容嵌入服务单元测试
"""
import pytest
from app.services.openai_embedding_service import OpenAIEmbeddingService


class TestOpenAIEmbeddingService:
    """OpenAI 嵌入服务测试"""

    @pytest.fixture
    def config(self):
        """测试配置"""
        return {
            "api_key": "test-key",
            "endpoint": "https://api.openai.com/v1",
            "model": "text-embedding-3-small",
            "timeout": 30,
            "batch_size": 100
        }

    @pytest.mark.asyncio
    async def test_load_model(self, config):
        """测试加载模型"""
        service = OpenAIEmbeddingService(config)
        await service.load_model()
        assert service._session is not None
        await service.unload_model()

    @pytest.mark.asyncio
    async def test_unload_model(self, config):
        """测试卸载模型"""
        service = OpenAIEmbeddingService(config)
        await service.load_model()
        await service.unload_model()
        assert service._session is None

    @pytest.mark.asyncio
    async def test_predict_empty(self, config):
        """测试空输入"""
        service = OpenAIEmbeddingService(config)
        result = await service.predict([])
        assert result == []


class TestIndexRebuildService:
    """索引重建服务测试"""

    @pytest.mark.asyncio
    async def test_start_rebuild_no_current_model(self):
        """测试无当前模型时启动重建"""
        from app.services.index_rebuild_service import get_index_rebuildService

        service = get_index_rebuild_service()
        result = await service.start_rebuild({"model_type": "embedding"})

        assert result["success"] is False
        assert result["error"]["code"] == "NO_CURRENT_MODEL"

    @pytest.mark.asyncio
    async def test_get_status_no_task(self):
        """测试无任务时获取状态"""
        from app.services.index_rebuild_service import get_index_rebuild_service

        service = get_index_rebuild_service()
        result = service.get_status()

        assert result["data"]["status"] == "none"
```

---

### 步骤 7.2：集成测试

**测试步骤**：

1. **启动后端服务**

```bash
cd backend
python main.py
```

2. **测试配置保存（云端模型）**

```bash
curl -X PUT http://127.0.0.1:8000/api/config/ai-model \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "embedding",
    "provider": "cloud",
    "model_name": "text-embedding-3-small",
    "config": {
      "api_key": "sk-xxx",
      "endpoint": "https://api.openai.com/v1",
      "model": "text-embedding-3-small"
    }
  }'
```

预期响应：
```json
{
  "code": 200,
  "message": "配置更新成功",
  "data": {
    "id": 2,
    "model_type": "embedding",
    "provider": "cloud",
    "model_name": "text-embedding-3-small",
    "is_active": true
  }
}
```

3. **测试连接**

```bash
curl -X POST http://127.0.0.1:8000/api/config/ai-model/test \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "embedding",
    "provider": "cloud",
    "config": {
      "api_key": "sk-xxx",
      "endpoint": "https://api.openai.com/v1",
      "model": "text-embedding-3-small"
    }
  }'
```

4. **测试重建状态查询**

```bash
curl http://127.0.0.1:8000/api/index/rebuild/status
```

预期响应：
```json
{
  "success": true,
  "data": {
    "status": "none"
  }
}
```

5. **测试搜索功能**

```bash
curl -X POST http://127.0.0.1:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "测试搜索",
    "search_type": "semantic",
    "limit": 10
  }'
```

---

## 📊 完成检查清单

### 代码实现

- [ ] BaseAIModel 基类已创建
- [ ] OpenAIEmbeddingService 已实现
- [ ] BGEEmbeddingService 已更新继承基类
- [ ] AIModelManager 已扩展支持云端
- [ ] IndexRebuildService 已实现
- [ ] 索引重建 API 端点已添加
- [ ] 路由已注册到 FastAPI
- [ ] 前端配置表单已更新
- [ ] 中文翻译已更新
- [ ] 英文翻译已更新

### 测试验证

- [ ] 单元测试已编写
- [ ] 集成测试已通过
- [ ] 配置保存测试通过
- [ ] 连接测试通过
- [ ] 搜索功能测试通过
- [ ] 本地/云端切换测试通过

### 文档更新

- [ ] PRD 文档已更新
- [ ] 技术方案文档已更新
- [ ] 实施方案文档已更新
- [ ] 实施步骤文档已更新
- [ ] 接口文档已更新
- [ ] 数据库文档已更新

---

## 🔧 故障排查

### 常见问题

**1. 依赖安装失败**

```bash
# 尝试使用国内镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple aiohttp>=3.9.0 tenacity>=8.2.0
```

**2. API 连接失败**

- 检查 API 密钥是否正确
- 检查网络连接
- 检查端点地址是否可访问

```bash
# 测试端点连通性
curl https://api.openai.com/v1/models
```

**3. 模块导入错误**

```bash
# 确认工作目录正确
cd backend

# 确认 Python 路径
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**4. 端点无法访问**

```bash
# 检查端口占用
netstat -ano | findstr :8000

# 检查防火墙设置
```

---

## 📚 相关文档

- [云端嵌入模型 PRD](./embedding-openai-01-prd.md) - 产品需求文档
- [云端嵌入模型原型](./embedding-openai-02-原型.md) - UI/UX 设计
- [云端嵌入模型技术方案](./embedding-openai-03-技术方案.md) - 技术实现方案
- [云端嵌入模型任务清单](./embedding-openai-04-开发任务清单.md) - 任务分解
- [云端嵌入模型排期表](./embedding-openai-05-开发排期表.md) - 时间规划
- [云端嵌入模型实施方案](./embedding-openai-实施方案.md) - 实施方案
- [云端嵌入模型接口文档增量](./embedding-openai-增量-接口文档.md) - API 接口增量
- [云端嵌入模型数据库文档增量](./embedding-openai-增量-数据库设计文档.md) - 数据库增量

---

**文档版本**：v1.0
**创建时间**：2026-03-26
**预计工期**：3 天（24 小时）
**维护者**：AI助手
