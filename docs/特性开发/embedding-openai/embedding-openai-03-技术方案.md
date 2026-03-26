# 云端嵌入模型调用能力 - 技术方案

> **文档类型**：技术方案
> **特性状态**：规划中
> **创建时间**：2026-03-26
> **最后更新**：2026-03-26

---

## 变更历史

| 版本 | 日期 | 变更内容 |
|-----|------|---------|
| v2.0 | 2026-03-26 | 索引重建机制更新为简化方案（复用现有索引任务系统） |
| v1.0 | 2026-03-26 | 初始版本 - 独立端点方案（方案B） |

---

## 1. 方案概述

### 1.1 技术目标

创建**通用 OpenAI 兼容嵌入模型服务**，支持所有兼容 OpenAI Embeddings API 标准的云服务供应商，与现有本地嵌入模型形成类型互斥的配置体系。

**核心能力**：
- 调用 OpenAI 兼容的 Embeddings API（`/v1/embeddings` 端点）
- 支持任意向量维度（使用模型原始维度）
- 批处理优化（支持批量文本嵌入）
- 错误重试机制（API 调用失败自动重试）
- **切换模型重建索引**：保证向量空间一致性

### 1.2 设计原则

- **类型互斥**：用户只能选择本地或云端嵌入模型其中一种
- **接口统一**：继承 `BaseAIModel` 基类，与本地嵌入模型保持接口一致
- **索引重建**：切换嵌入模型必须重建索引，确保向量空间一致性
- **原始维度**：使用模型的原始向量维度，不做任何归一化处理
- **向后兼容**：保持现有本地嵌入模型可用，不破坏现有功能
- **安全优先**：API 密钥加密存储，日志脱敏处理
- **通用兼容**：支持所有 OpenAI Embeddings API 兼容的服务

### 1.3 技术选型

| 技术/框架 | 用途 | 选择理由 | 替代方案 |
|----------|------|---------|---------|
| aiohttp | HTTP 客户端 | 异步高性能，已在项目中使用 | httpx、requests |
| numpy | 向量处理 | 高效数值计算，与现有代码一致 | TensorFlow、PyTorch |
| tenacity | 重试机制 | 声明式重试，代码简洁 | 手动重试逻辑 |
| BaseAIModel | 服务基类 | 统一接口，易于扩展 | 独立实现 |

### 1.4 支持的供应商

**说明**：本服务支持所有兼容 OpenAI Embeddings API 标准的服务，不限制特定供应商。

| 供应商 | 端点地址示例 | 模型示例 | 向量维度 | 说明 |
|--------|-------------|---------|----------|------|
| OpenAI | `https://api.openai.com/v1` | `text-embedding-3-small` | 1536 | 切换时重建索引 |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-embeddings` | 1024 | 原生1024维 |
| 阿里云 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `text-embedding-v3` | 1024 | 原生1024维 |
| Moonshot | `https://api.moonshot.cn/v1` | `moonshot-v1-embedding` | 1024 | 原生1024维 |
| 其他兼容服务 | 用户自定义 | 用户自定义 | 可变 | 切换时重建索引 |

---

## 2. 架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              API层                                       │
├─────────────────────────────────────────────────────────────────────────┤
│  PUT /api/config/ai-model  │  GET /api/config/ai-models  │            │
│  POST /api/config/ai-model/{id}/test                                   │
└────────────┬───────────────────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────────────────┐
│                        服务层 (Service Layer)                             │
├───────────────────────────────────────────────────────────────────────────┤
│                        AIModelService                                    │
│  - register_model()         # 注册模型                                  │
│  - get_model(embedding)    # 获取嵌入模型                              │
│  - text_embedding()        # 文本嵌入                                  │
│  - batch_text_embedding()  # 批量文本嵌入                             │
└────────────┬───────────────────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────────────────┐
│                      模型管理层 (Model Manager)                             │
├───────────────────────────────────────────────────────────────────────────┤
│                        ModelManager                                      │
│  - models: Dict[model_id, BaseAIModel]                                  │
│  - register_model(model_id, model)                                      │
│  - get_model(model_id)                                                   │
└────────────┬───────────────────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────────────────┐
│                      服务实现层 (Service Implementation)                     │
├───────────────────────────────────────────────────────────────────────────┤
│                        BaseAIModel (ABC)                                  │
│                                  │                                        │
│              ┌───────────────────┴───────────────────┐                     │
│              ▼                                     ▼                      │
│    BGEEmbeddingService                  OpenAIEmbeddingService             │
│    (provider='local')                     (provider='cloud')               │
│    - 本地 BGE-M3 调用                    - OpenAI API 调用               │
│    - 模型文件: BAAI/bge-m3               - 云端供应商 API                │
│    - 1024 维向量输出                     - 支持所有兼容供应商             │
│                                          - 使用模型原始维度               │
└───────────────────────────────────────────────────────────────────────────┘
```

### 2.2 目录结构

```
backend/
├── app/
│   ├── services/
│   │   ├── ai_model_base.py              # 基类（已存在）
│   │   │   └── BaseAIModel(ABC)
│   │   ├── bge_embedding_service.py       # 本地嵌入服务（已存在）
│   │   │   └── BGEEmbeddingService extends BaseAIModel
│   │   ├── openai_embedding_service.py   # OpenAI 兼容嵌入服务（新增）
│   │   │   └── OpenAIEmbeddingService extends BaseAIModel
│   │   └── ai_model_manager.py           # 模型管理器（扩展）
│   │
│   ├── models/
│   │   └── ai_model.py                   # 数据模型（无变更）
│   │
│   └── api/
│       └── config.py                     # 配置 API（无变更）
│
└── requirements.txt                       # 依赖（无新增）
```

### 2.3 数据流

**本地模型（BGE-M3）流程**：

```
用户配置本地嵌入模型
    ↓
前端: provider='local', model_name='BAAI/bge-m3', device='cpu'
    ↓
后端: 创建 BGEEmbeddingService(config)
    ↓
模型管理器: register_model('embedding_local', bge_service)
    ↓
调用: ai_model_service.text_embedding(texts)
    ↓
BGEEmbeddingService.predict()
    ↓
本地模型推理（CPU/GPU）
    ↓
返回 1024 维向量
```

**云端模型（OpenAI 兼容）流程**：

```
用户配置云端嵌入模型
    ↓
前端: provider='cloud', model_name='text-embedding-3-small',
     api_key='sk-xxx', endpoint='https://api.openai.com/v1'
    ↓
后端: 创建 OpenAIEmbeddingService(config)
    ↓
模型管理器: register_model('embedding_cloud', openai_service)
    ↓
调用: ai_model_service.text_embedding(texts)
    ↓
OpenAIEmbeddingService.predict()
    ↓
POST {endpoint}/embeddings
    ↓
接收云端向量（使用模型原始维度，如1536维）
    ↓
重建索引时直接使用原始向量构建 Faiss 索引
    ↓
返回原始向量
```

---

## 3. 核心模块设计

### 3.1 OpenAI 兼容嵌入服务（新增）

**文件**：`backend/app/services/openai_embedding_service.py`

```python
"""
OpenAI兼容的文本嵌入服务
支持所有兼容OpenAI Embeddings API标准的服务
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass

import aiohttp
import numpy as np
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from app.services.ai_model_base import (
    BaseAIModel, ModelType, ProviderType, ModelStatus, AIModelException
)
from app.utils.enum_helpers import get_enum_value

logger = logging.getLogger(__name__)


class OpenAIEmbeddingService(BaseAIModel):
    """
    OpenAI兼容的文本嵌入服务

    支持所有兼容OpenAI Embeddings API标准的服务：
    - OpenAI 官方
    - DeepSeek
    - 阿里云通义千问
    - Moonshot
    - 其他兼容 OpenAI Embeddings API 标准的服务
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化OpenAI兼容嵌入服务

        Args:
            config: 配置字典，包含以下字段：
                - api_key: API密钥（必需）
                - endpoint: API端点地址（可选，默认官方地址）
                - model: 模型名称（必需）
                - embedding_dim: 目标向量维度（可选，默认1024）
                - timeout: 请求超时时间（可选，默认30秒）
                - batch_size: 批处理大小（可选，默认100）
                - max_retries: 最大重试次数（可选，默认3）
        """
        if config is None:
            config = {}

        # 验证必需参数
        if "api_key" not in config or not config["api_key"]:
            raise AIModelException("api_key 是必需参数")
        if "model" not in config or not config["model"]:
            raise AIModelException("model 是必需参数")

        # 初始化配置
        self.api_key = config["api_key"]
        self.endpoint = config.get("endpoint", "https://api.openai.com/v1")
        self.model = config["model"]
        self.timeout = config.get("timeout", 30)
        self.batch_size = config.get("batch_size", 100)
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay = config.get("retry_delay", 1.0)

        # HTTP会话（延迟初始化）
        self.session: Optional[aiohttp.ClientSession] = None

        # 调用父类初始化
        super().__init__(
            model_name=self.model,
            model_type=ModelType.EMBEDDING,
            provider=ProviderType.CLOUD,
            config=config
        )

    async def load_model(self) -> bool:
        """
        加载模型（创建HTTP会话并验证连接）

        Returns:
            bool: 加载成功返回True
        """
        try:
            # 创建HTTP会话
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)

            # 测试连接
            await self._test_connection()

            self.update_status(ModelStatus.LOADED)
            logger.info(f"OpenAI嵌入服务加载成功: {self.model}")
            return True

        except Exception as e:
            self.update_status(ModelStatus.ERROR, str(e))
            logger.error(f"OpenAI嵌入服务加载失败: {e}")
            raise AIModelException(f"加载失败: {str(e)}")

    async def unload_model(self) -> bool:
        """
        卸载模型（关闭HTTP会话）

        Returns:
            bool: 卸载成功返回True
        """
        try:
            if self.session:
                await self.session.close()
                self.session = None

            self.update_status(ModelStatus.UNLOADED)
            logger.info("OpenAI嵌入服务已卸载")
            return True

        except Exception as e:
            logger.error(f"卸载OpenAI嵌入服务失败: {e}")
            return False

    async def predict(
        self,
        texts: Union[str, List[str]],
        **kwargs
    ) -> np.ndarray:
        """
        生成文本嵌入向量

        Args:
            texts: 单个文本或文本列表
            **kwargs: 额外参数

        Returns:
            np.ndarray: 嵌入向量矩阵，shape=(n, 1024)
        """
        if not isinstance(texts, list):
            texts = [texts]

        all_embeddings = []

        # 分批处理
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]

            try:
                batch_embeddings = await self._call_embeddings_api(batch_texts)
                all_embeddings.extend(batch_embeddings)
            except Exception as e:
                logger.error(f"批处理嵌入失败 (batch {i}): {e}")
                raise AIModelException(f"嵌入失败: {str(e)}")

        return np.array(all_embeddings)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(1.0),
        retry=retry_if_exception_type(aiohttp.ClientError)
    )
    async def _call_embeddings_api(self, texts: List[str]) -> List[List[float]]:
        """
        调用OpenAI兼容的Embeddings API

        Args:
            texts: 文本列表

        Returns:
            List[List[float]]: 嵌入向量列表
        """
        if not self.session:
            raise AIModelException("服务未加载，请先调用load_model()")

        url = f"{self.endpoint}/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        request_data = {
            "input": texts,
            "model": self.model
        }

        logger.debug(f"调用嵌入API: {url}, 文本数量: {len(texts)}")

        async with self.session.post(url, json=request_data, headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"API请求失败: {response.status} - {error_text}")
                raise AIModelException(
                    f"API请求失败: HTTP {response.status} - {error_text}"
                )

            result = await response.json()

            # 提取嵌入向量（使用原始维度）
            embeddings = []
            for item in result.get("data", []):
                embedding = item.get("embedding", [])
                embeddings.append(embedding)

            logger.debug(f"成功获取 {len(embeddings)} 个嵌入向量")
            logger.info(f"向量维度: {len(embeddings[0])} (使用模型原始维度)")
            return embeddings

    async def _test_connection(self) -> bool:
        """
        测试API连接

        Returns:
            bool: 连接成功返回True

        Raises:
            AIModelException: 连接失败
        """
        try:
            # 调用一次API测试
            test_embedding = await self._call_embeddings_api(["test"])
            logger.info(f"API连接测试成功，向量维度: {len(test_embedding[0])}")
            return True

        except Exception as e:
            logger.error(f"API连接测试失败: {e}")
            raise AIModelException(f"API连接测试失败: {str(e)}")

    async def compute_similarity(
        self,
        query_embedding: np.ndarray,
        corpus_embeddings: np.ndarray
    ) -> np.ndarray:
        """
        计算查询向量与语料库向量的相似度

        Args:
            query_embedding: 查询向量，shape=(1024,)
            corpus_embeddings: 语料库向量，shape=(n, 1024)

        Returns:
            np.ndarray: 相似度分数，shape=(n,)
        """
        # 归一化
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        corpus_norm = corpus_embeddings / np.linalg.norm(corpus_embeddings, axis=1, keepdims=True)

        # 余弦相似度
        similarities = np.dot(corpus_norm, query_norm)
        return similarities

    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息

        Returns:
            Dict[str, Any]: 模型信息
        """
        return {
            "model_name": self.model,
            "model_type": "embedding",
            "provider": "cloud",
            "endpoint": self.endpoint,
            "embedding_dim": self.embedding_dim,
            "dimension_mode": self.dimension_mode,
            "batch_size": self.batch_size,
            "status": self.status.value if self.status else "unknown"
        }


def create_openai_embedding_service(config: Dict[str, Any]) -> OpenAIEmbeddingService:
    """
    工厂函数：创建OpenAI兼容嵌入服务

    Args:
        config: 配置字典

    Returns:
        OpenAIEmbeddingService: 嵌入服务实例
    """
    return OpenAIEmbeddingService(config)
```

### 3.2 AI 模型管理器扩展

**文件**：`backend/app/services/ai_model_manager.py`

**修改内容**：

```python
# 在现有代码中添加云端嵌入服务的创建逻辑

async def _create_default_models(self):
    """创建默认模型配置"""
    for model_id, model_config in self.model_configs.items():
        model_type = model_config["model_type"]
        provider = model_config.get("provider", "local")

        if model_type == "embedding":
            if provider == "local":
                # 现有逻辑：创建本地嵌入服务
                from app.services.bge_embedding_service import create_bge_service
                embedding_service = create_bge_service(model_config["config"])
                self.model_manager.register_model(model_id, embedding_service)
            elif provider == "cloud":
                # 新增逻辑：创建云端嵌入服务
                from app.services.openai_embedding_service import create_openai_embedding_service
                embedding_service = create_openai_embedding_service(model_config["config"])
                self.model_manager.register_model(model_id, embedding_service)
        # ... 其他模型类型的处理
```

---

## 4. API 接口设计

### 4.1 配置接口（复用现有）

**PUT /api/config/ai-model**

更新嵌入模型配置，支持本地/云端互斥切换。

**请求示例（切换到云端）**：

```json
{
  "model_type": "embedding",
  "provider": "cloud",
  "model_name": "text-embedding-3-small",
  "config": {
    "api_key": "sk-xxxxxxxxxxxx",
    "endpoint": "https://api.openai.com/v1",
    "model": "text-embedding-3-small",
    "timeout": 30,
    "batch_size": 100
  }
}
```

**请求示例（切换回本地）**：

```json
{
  "model_type": "embedding",
  "provider": "local",
  "model_name": "BAAI/bge-m3",
  "config": {
    "device": "cpu"
  }
}
```

**响应示例**：

```json
{
  "success": true,
  "message": "配置已保存",
  "data": {
    "model_id": "embedding_cloud",
    "provider": "cloud",
    "model_name": "text-embedding-3-small"
  }
}
```

### 4.2 测试接口（复用现有）

**POST /api/config/ai-model/{id}/test**

测试云端嵌入模型配置。

**请求示例**：

```json
{
  "model_type": "embedding",
  "provider": "cloud",
  "config": {
    "api_key": "sk-xxxxxxxxxxxx",
    "endpoint": "https://api.openai.com/v1",
    "model": "text-embedding-3-small"
  }
}
```

**响应示例**：

```json
{
  "success": true,
  "message": "连接成功",
  "data": {
    "embedding_dim": 1536,
    "test_text": "test",
    "response_time_ms": 245
  }
}
```

---

## 5. 数据库设计

### 5.1 数据表（复用现有）

**表名**：`ai_models`

**新增配置示例**：

```sql
-- 云端嵌入模型配置
INSERT INTO ai_models (model_type, provider, model_name, config_json, is_active)
VALUES (
    'embedding',
    'cloud',
    'text-embedding-3-small',
    '{
        "api_key": "sk-xxx",
        "endpoint": "https://api.openai.com/v1",
        "model": "text-embedding-3-small",
        "embedding_dim": 1024,
        "timeout": 30,
        "batch_size": 100
    }',
    true
);

-- 本地嵌入模型配置（保持不变）
INSERT INTO ai_models (model_type, provider, model_name, config_json, is_active)
VALUES (
    'embedding',
    'local',
    'BAAI/bge-m3',
    '{
        "device": "cpu",
        "embedding_dim": 1024
    }',
    false
);
```

**约束说明**：

- `model_type = 'embedding'` 时，`provider` 只能是 `'local'` 或 `'cloud'`
- 同时只能有一个 `is_active = true` 的嵌入模型配置
- 配置切换时，需要将旧配置的 `is_active` 设为 `false`

---

## 6. 业务逻辑设计

### 6.1 嵌入模型切换流程

```
用户在前端切换嵌入模型来源
    ↓
前端发送 PUT /api/config/ai-model
    ↓
后端验证配置
    ↓
    ├─ 验证失败 → 返回错误
    │
    └─ 验证成功 → 更新数据库
                   │
                   ├─ provider='local' → 加载本地嵌入服务
                   │                     │
                   │                     ├─ 卸载云端服务
                   │                     ├─ 加载本地模型
                   │                     └─ 返回成功
                   │
                   └─ provider='cloud' → 加载云端嵌入服务
                                         │
                                         ├─ 卸载本地模型
                                         ├─ 初始化云端服务
                                         ├─ 测试连接
                                         └─ 返回成功
```

### 6.2 文本嵌入流程

```
搜索请求到达后端
    ↓
AI模型管理器获取当前活跃的嵌入模型
    ↓
    ├─ provider='local' → 调用 BGEEmbeddingService
    │                         │
    │                         └─ 返回 1024 维向量
    │
    └─ provider='cloud' → 调用 OpenAIEmbeddingService
                             │
                             ├─ 调用云端 API
                             ├─ 获取原始向量（使用模型原始维度）
                             └─ 返回原始向量
    ↓
重建索引时直接使用原始向量构建 Faiss 索引
    ↓
返回搜索结果
```

### 6.3 错误处理流程

```
云端嵌入 API 调用
    ↓
    ├─ 成功 → 返回向量
    │
    └─ 失败 → 重试逻辑
                 │
                 ├─ 重试 1 次 → 失败
                 ├─ 重试 2 次 → 失败
                 ├─ 重试 3 次 → 失败
                 │
                 └─ 返回错误
                            │
                            ├─ 如果已配置本地模型 → 建议降级到本地
                            └─ 否则 → 返回错误信息
```

---

## 7. 性能优化

### 7.1 批处理优化

- **批量请求**：支持一次请求最多 `batch_size` 个文本（默认 100）
- **分批处理**：文本列表自动分批，避免 API 单次请求限制
- **并发控制**：使用信号量控制并发请求数

### 7.2 缓存策略

- **模型缓存**：HTTP 会话复用，避免重复创建
- **配置缓存**：模型配置缓存到内存，减少数据库查询

### 7.3 错误重试

- **指数退避**：重试间隔逐渐增加（1s, 2s, 4s）
- **最大重试次数**：默认 3 次，可配置

---

## 8. 国际化架构

### 8.1 后端国际化

**设计原则**：
- 复用现有的 `I18N` 类（位于 `backend/app/core/i18n.py`）
- 支持 `Accept-Language` 请求头自动检测语言环境
- 使用点表示法访问嵌套翻译键（如 `model.cloud_embedding_success`）
- 支持参数化翻译（如 `向量维度: {dimension}`）

**语言环境检测**：

```python
from app.core.i18n import get_locale_from_header

def get_locale_from_header(accept_language: Optional[str] = None) -> str:
    """
    从 Accept-Language 头中提取语言环境

    支持: zh-CN, zh-CN;q=0.9, en;q=0.8
    默认: zh_CN
    """
```

**翻译键结构**：

```json
{
  "model": {
    "cloud_embedding_success": "云端嵌入模型测试成功，向量维度: {dimension}",
    "rebuild_already_running": "重建任务正在进行中，进度：{progress}%"
  },
  "index_rebuild": {
    "title": "索引重建",
    "status_running": "重建中"
  }
}
```

**API 端点使用示例**：

```python
from fastapi import Header
from app.core.i18n import i18n, get_locale_from_header

@router.post("/api/index/rebuild/start")
async def start_rebuild(
    request: RebuildRequest,
    accept_language: Optional[str] = Header(None)
):
    # 获取语言环境
    locale = get_locale_from_header(accept_language)

    # 错误处理使用国际化
    if is_running:
        raise HTTPException(
            status_code=409,
            detail={
                "message": i18n.t("model.rebuild_already_running", locale, progress=50)
            }
        )

    # 成功消息使用国际化
    return {
        "message": i18n.t("model.rebuild_started", locale, task_id=task_id)
    }
```

---

### 8.2 前端国际化

**框架**：Vue-i18n @ 9

**翻译键文件**：
- `frontend/src/locale/lang/zh-cn.ts` - 中文
- `frontend/src/locale/lang/en-us.ts` - 英文

**使用示例**：

```vue
<template>
  <a-form-item :label="$t('embedding.apiKey')">
    <a-input v-model:value="cloudConfig.api_key" />
  </a-form-item>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

// 代码中使用
const message = t('embedding.cloud_service_info');
</script>
```

---

## 9. 安全设计

### 8.1 API 密钥保护

- **加密存储**：API 密钥使用 AES 加密后存储到数据库
- **日志脱敏**：日志中只显示密钥前 8 位和后 4 位
- **传输安全**：使用 HTTPS 协议传输

### 8.2 数据隐私

- **数据不上传**：本地文件和索引数据不上传到云端
- **查询透明**：前端明确提示用户搜索查询会发送到云端
- **配置确认**：切换到云端时需要用户确认

---

## 10. 测试方案

### 10.1 单元测试

**测试文件**：`backend/tests/test_openai_embedding_service.py`

```python
import pytest
import numpy as np
from app.services.openai_embedding_service import OpenAIEmbeddingService, create_openai_embedding_service


class TestOpenAIEmbeddingService:
    """OpenAI嵌入服务测试"""

    @pytest.fixture
    def config(self):
        return {
            "api_key": "test-key",
            "endpoint": "https://api.openai.com/v1",
            "model": "text-embedding-3-small",
            "embedding_dim": 1024,
            "dimension_mode": "truncate"
        }

    def test_create_service(self, config):
        """测试创建服务"""
        service = create_openai_embedding_service(config)
        assert service is not None
        assert service.model == "text-embedding-3-small"
        assert service.embedding_dim == 1024

    def test_normalize_dimension_truncate(self):
        """测试维度归一化 - 截断模式"""
        service = OpenAIEmbeddingService()
        service.embedding_dim = 1024
        service.dimension_mode = "truncate"

    @pytest.mark.asyncio
    async def test_predict(self, config):
        """测试文本嵌入预测（需要mock API）"""
        service = OpenAIEmbeddingService(config)
        # Mock API 调用...
        # result = await service.predict(["test text"])
        # assert result.shape == (1, model_dim)
```

### 10.2 集成测试

**测试场景**：

1. **本地/云端切换测试**
   - 切换到云端，本地模型被卸载
   - 切换到本地，云端服务被卸载
   - 配置正确保存和加载

2. **向量维度测试**
   - 验证不同模型返回正确的向量维度
   - 验证重建索引使用模型原始维度

3. **API 调用测试**
   - 单个文本嵌入
   - 批量文本嵌入
   - 错误重试机制

### 9.3 性能测试

**测试指标**：

| 指标 | 目标值 | 测试方法 |
|------|--------|----------|
| API 响应时间 | < 2s | 单次嵌入请求 |
| 批处理吞吐量 | > 100 texts/min | 批量嵌入请求 |
| 索引重建耗时 | < 15 min | 重建1万文件索引 |
| 并发处理能力 | > 10 req/s | 并发嵌入请求 |

---

## 10. 索引重建机制

### 10.1 设计原则

**核心原则**：切换嵌入模型必须重建索引

**原因**：
- 不同模型的向量空间互不兼容
- 本地 BGE-M3 向量空间 ≠ 云端模型向量空间
- 不同云端模型之间向量空间也不兼容
- 强制重建保证搜索质量

**方案选择**：**简化方案 - 复用现有索引任务系统**

**方案变更说明**：
- ~~原方案（方案B）：独立端点，内存状态管理~~
- **新方案（简化方案）：复用现有的 `run_full_index_task` 和 `IndexJobModel`**
- 清空索引后，为每个历史已完成任务的 folder_path 创建新任务
- 利用 BackgroundTasks 自动排队执行
- 复用现有的 `/api/index/status/{id}` 查询进度

**方案对比**：

| 对比项 | 原方案（独立端点） | 简化方案（复用现有系统） |
|--------|------------------|---------------------|
| 新增接口 | 3个（start/status/cancel） | 1个（rebuild-all） |
| 状态管理 | 内存（不持久化） | 数据库（复用IndexJobModel） |
| 进度查询 | 新端点 | 复用现有端点 |
| 任务排队 | 需实现 | 系统自动排队 |
| 错误处理 | 需实现 | 已有！ |
| 实施时间 | 7 小时 | 2 小时 |
| 代码量 | ~500 行 | ~150 行 |

---

### 10.2 触发条件

| 触发场景 | 是否重建 | 说明 |
|---------|---------|------|
| 本地模型 → 云端模型 | ✅ 是 | 向量空间完全不同 |
| 云端模型 → 本地模型 | ✅ 是 | 向量空间完全不同 |
| 云端模型A → 云端模型B | ✅ 是 | 不同模型向量空间不同 |
| 本地模型配置更新 | ❌ 否 | device 变更不影响向量 |
| 云端模型配置更新 | ⚠️ 可能 | model/endpoint 变更需重建 |

---

### 10.3 用户操作流程

```
用户切换嵌入模型配置
    ↓
保存配置
    ↓
后端验证并保存（不自动触发重建）
    ↓
前端显示引导提示
┌─────────────────────────────────────────────┐
│ ⚠️ 嵌入模型已更改                             │
│                                             │
│ 建议重启应用后在索引管理中重建索引              │
│                                             │
│ [重启应用]  [前往索引管理]                    │
└─────────────────────────────────────────────┘
    ↓
用户选择"前往索引管理"
    ↓
跳转到索引管理页面
    ↓
点击"全量重建索引"按钮
    ↓
确认对话框
┌─────────────────────────────────────────────┐
│ 确认全量重建                                 │
│                                             │
│ 将清空所有索引并按历史任务逐一重建             │
│ 预计耗时较长，是否继续？                      │
│                                             │
│              [取消]  [确认]                  │
└─────────────────────────────────────────────┘
    ↓
用户确认
    ↓
POST /api/index/rebuild-all
    ↓
清空索引 + 创建重建任务
    ↓
显示重建进度列表
    ↓
全部完成
    ↓
显示成功提示
```

---

### 10.4 重建流程

```
用户点击"全量重建索引"并确认
    ↓
┌─────────────────────────────────────────────┐
│ 后端重建流程（复用现有索引任务系统）           │
├─────────────────────────────────────────────┤
│ 1. 清空 indexes 文件夹                       │
│    ├─ 删除所有 Faiss 索引文件（*.index）     │
│    ├─ 删除 Whoosh 索引目录                  │
│    └─ 重置内存中的索引对象                   │
│ 2. 查询历史已完成任务（按 folder_path 去重） │
│    ├─ SELECT * FROM index_jobs             │
│    │   WHERE status = 'completed'          │
│    └─ 按 folder_path 分组去重               │
│ 3. 为每个 folder_path 创建新的重建任务       │
│    ├─ 创建新的 IndexJob 记录                │
│    ├─ job_type = 'create'                  │
│    └─ status = 'pending'                   │
│ 4. 添加到后台任务队列（自动排队执行）         │
│    ├─ background_tasks.add_task(           │
│    │     run_full_index_task,              │
│    │     index_id,                         │
│    │     folder_path,                      │
│    │     recursive=True,                   │
│    │     file_types=None                   │
│    │   )                                  │
│    └─ 利用现有排队机制                     │
│ 5. 返回任务列表                            │
└─────────────────────────────────────────────┘
    ↓
前端并行轮询所有任务进度
┌─────────────────────────────────────────────┐
│ 重建进度                                      │
│                                              │
│ D:\\Documents                      [处理中] │
│ ████████████░░░░░░░░░░░░░░░  60%                 │
│ 已处理: 600 / 1000                           │
│                                              │
│ E:\\Projects                      [等待中] │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░  0%                   │
│                                              │
│ C:\\Work                         [等待中] │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░  0%                   │
└─────────────────────────────────────────────┘
    ↓
全部完成
    ↓
显示成功提示
```

---

### 10.5 API接口设计

**新增单一端点，复用现有进度查询**：

```python
# backend/app/api/index.py（扩展）

# ===== 现有索引任务接口（保持不变）=====
@router.post("/create")
async def create_index(folder_path: str, ...):
    """创建新索引（写入数据库）"""
    # 保持现有逻辑不变
    ...

@router.get("/status/{index_id}")
async def get_index_status(index_id: int):
    """查询索引任务状态（从数据库）"""
    # 保持现有逻辑不变
    ...

@router.get("/list")
async def list_index_tasks(...):
    """查询索引任务列表（从数据库）"""
    # 保持现有逻辑不变
    ...


# ===== 新增：全量重建索引接口（复用现有系统）=====
@router.post("/rebuild-all")
async def rebuild_all_indexes(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    locale: str = Depends(get_locale)
):
    """
    全量重建所有索引

    流程：
    1. 清空 indexes 文件夹
    2. 查询所有历史索引任务（按 folder_path 去重）
    3. 为每个 folder_path 创建新的重建任务
    4. 任务排队执行
    """
    logger.info("开始全量重建所有索引")

    try:
        # 1. 清空索引
        index_service = get_file_index_service()
        index_service.clear_index()

        # 2. 查询所有已完成的历史任务（去重 folder_path）
        completed_jobs = db.query(IndexJobModel).filter(
            IndexJobModel.status == get_enum_value(JobStatus.COMPLETED)
        ).all()

        # 去重：每个 folder_path 只取一个（最新的）
        unique_paths = {}
        for job in completed_jobs:
            if job.folder_path not in unique_paths:
                unique_paths[job.folder_path] = job

        folder_paths = list(unique_paths.keys())

        if not folder_paths:
            raise ValidationException(
                i18n.t('index.no_completed_jobs', locale)
            )

        logger.info(f"找到 {len(folder_paths)} 个需要重建的路径")

        # 3. 为每个路径创建新的重建任务
        created_jobs = []
        for folder_path in folder_paths:
            # 创建新任务记录
            index_job = IndexJobModel(
                folder_path=folder_path,
                job_type=JobType.CREATE,
                status=get_enum_value(JobStatus.PENDING)
            )
            db.add(index_job)
            db.commit()
            db.refresh(index_job)

            created_jobs.append(index_job)

            # 4. 添加到后台任务队列（自动排队）
            background_tasks.add_task(
                run_full_index_task,
                index_job.id,
                folder_path,
                recursive=True,
                file_types=None
            )

            logger.info(f"重建任务已创建: id={index_job.id}, path={folder_path}")

        return {
            "success": True,
            "data": [IndexJobInfo(**job.to_dict()) for job in created_jobs],
            "message": i18n.t('index.rebuild_all_started', locale, count=len(created_jobs))
        }

    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"全量重建失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=i18n.t('index.rebuild_all_failed', locale) + f": {str(e)}"
        )


# ===== 清空索引方法（新增到 FileIndexService）=====
def clear_index(self):
    """
    清空 indexes 文件夹下的所有索引数据

    删除所有 Faiss 索引文件和 Whoosh 索引目录
    重置内存中的索引对象
    """
    import os
    import shutil
    import glob

    logger.info("开始清空 indexes 文件夹")

    # 1. 删除所有 Faiss 索引文件
    faiss_dir = os.path.dirname(self.faiss_index_path)
    if os.path.exists(faiss_dir):
        faiss_files = glob.glob(os.path.join(faiss_dir, "*.index"))
        for faiss_file in faiss_files:
            try:
                os.remove(faiss_file)
                logger.info(f"已删除: {faiss_file}")
            except Exception as e:
                logger.warning(f"删除失败: {faiss_file}, {e}")

    # 2. 删除 Whoosh 索引目录
    if os.path.exists(self.whoosh_index_path):
        try:
            shutil.rmtree(self.whoosh_index_path)
            logger.info(f"已删除 Whoosh 索引: {self.whoosh_index_path}")
        except Exception as e:
            logger.warning(f"删除 Whoosh 失败: {e}")

    # 3. 重置内存中的索引对象
    self._faiss_index = None
    self._whoosh_index = None

    logger.info("indexes 文件夹清空完成")
```

**接口对照表**：

| 功能 | 接口 | 说明 |
|------|------|------|
| 全量重建 | `POST /api/index/rebuild-all` | 新增，清空索引+按历史任务重建 |
| 查询状态 | `GET /api/index/status/{id}` | 复用现有端点 |
| 任务列表 | `GET /api/index/list` | 复用现有端点 |

---

### 10.6 前端进度显示

```vue
<template>
  <!-- 索引管理页面 -->
  <a-card title="索引管理">
    <!-- 统计信息 -->
    <a-row :gutter="16" style="margin-bottom: 16px;">
      <a-col :span="8">
        <a-statistic title="索引文件" :value="status.indexed_files || 0" />
      </a-col>
      <a-col :span="8">
        <a-statistic title="索引任务" :value="status.total_jobs || 0" />
      </a-col>
    </a-row>

    <!-- 操作按钮 -->
    <a-space style="margin-bottom: 16px;">
      <a-button @click="handleAddFiles">
        <PlusOutlined />
        添加文件
      </a-button>

      <a-button @click="handleUpdateIndex">
        <SyncOutlined />
        更新索引
      </a-button>

      <!-- 全量重建索引按钮 -->
      <a-button
        type="primary"
        danger
        @click="handleRebuildAll"
        :loading="isRebuilding"
      >
        <RebuildOutlined />
        {{ t('index.rebuildAll') }}
      </a-button>
    </a-space>

    <!-- 重建进度列表 -->
    <a-card
      v-if="rebuildJobs.length > 0"
      :title="t('index.rebuildProgress')"
      size="small"
    >
      <a-list
        :data-source="rebuildJobs"
        size="small"
      >
        <template #renderItem="{ item }">
          <a-list-item>
            <template #actions>
              <a-tag :color="getStatusColor(item.status)">
                {{ getStatusText(item.status) }}
              </a-tag>
            </template>
            <a-list-item-meta>
              <template #title>
                <a-typography-text ellipsis :content="item.folder_path" style="max-width: 500px;" />
              </template>
              <template #description>
                <a-space>
                  <span>{{ t('index.processed') }}: {{ item.processed_files }} / {{ item.total_files }}</span>
                  <a-progress
                    :percent="item.progress"
                    size="small"
                    :status="getProgressStatus(item.status)"
                    style="width: 150px;"
                  />
                </a-space>
              </template>
            </a-list-item-meta>
          </a-list-item>
        </template>
      </a-list>
    </a-card>
  </a-card>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Modal, message } from 'ant-design-vue'
import { RebuildOutlined, PlusOutlined, SyncOutlined } from '@ant-design/icons-vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const isRebuilding = ref(false)
const rebuildJobs = ref([])
const status = ref({})

let pollTimer = null

// 全量重建
const handleRebuildAll = () => {
  Modal.confirm({
    title: t('index.rebuildAllConfirm'),
    content: t('index.rebuildAllWarning'),
    okText: t('common.confirm'),
    cancelText: t('common.cancel'),
    okButtonProps: { danger: true },
    onOk: async () => {
      isRebuilding.value = true
      try {
        const response = await fetch('/api/index/rebuild-all', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
        const result = await response.json()

        if (result.success) {
          message.success(t('index.rebuildAllStarted', { count: result.data.length }))
          rebuildJobs.value = result.data

          // 开始轮询所有任务的进度
          startPolling()
        }
      } catch (error) {
        message.error(t('index.rebuildAllFailed'))
      } finally {
        isRebuilding.value = false
      }
    }
  })
}

// 轮询所有重建任务的进度
const startPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
  }

  pollTimer = setInterval(async () => {
    try {
      // 并行查询所有任务状态
      const promises = rebuildJobs.value.map(job =>
        fetch(`/api/index/status/${job.index_id}`)
          .then(res => res.json())
      )

      const results = await Promise.all(promises)

      rebuildJobs.value = results.map(r => r.data)

      // 检查是否全部完成
      const allCompleted = rebuildJobs.value.every(
        job => job.status === 'completed' || job.status === 'failed'
      )

      if (allCompleted) {
        clearInterval(pollTimer)
        pollTimer = null

        const completed = rebuildJobs.value.filter(
          j => j.status === 'completed'
        ).length
        const failed = rebuildJobs.value.filter(
          j => j.status === 'failed'
        ).length

        if (failed > 0) {
          message.warning(t('index.rebuildAllPartial', { completed, failed }))
        } else {
          message.success(t('index.rebuildAllComplete', { count: completed }))
        }

        // 刷新状态
        await fetchStatus()
      }
    } catch (error) {
      console.error('轮询失败:', error)
    }
  }, 2000)
}

// 获取状态
const fetchStatus = async () => {
  try {
    const response = await fetch('/api/index/status')
    const result = await response.json()
    if (result.success) {
      status.value = result.data
    }
  } catch (error) {
    console.error('获取状态失败:', error)
  }
}

const getStatusColor = (status: string) => {
  const colors = {
    pending: 'default',
    processing: 'processing',
    completed: 'success',
    failed: 'error'
  }
  return colors[status] || 'default'
}

const getStatusText = (status: string) => {
  return t(`index.jobStatus.${status}`)
}

const getProgressStatus = (status: string) => {
  const statusMap = {
    processing: 'active',
    completed: 'success',
    failed: 'exception'
  }
  return statusMap[status] || null
}

onMounted(() => {
  fetchStatus()
})

onUnmounted(() => {
  if (pollTimer) {
    clearInterval(pollTimer)
  }
})
</script>
```

---

### 10.7 设置页面引导

```vue
<!-- 切换模型后的引导提示 -->
<a-alert
  v-if="showModelChangeWarning"
  type="warning"
  show-icon
  closable
  @close="showModelChangeWarning = false"
  style="margin-bottom: 16px;"
>
  <template #message>
    {{ t('settingsEmbedding.modelChanged') }}
  </template>
  <template #description>
    <p>{{ t('settingsEmbedding.rebuildTip') }}</p>
    <a-space>
      <a-button type="primary" size="small" @click="restartApp">
        <ReloadOutlined />
        {{ t('common.restartApp') }}
      </a-button>
      <a-button size="small" @click="goToIndexManagement">
        <FolderOpenOutlined />
        {{ t('settingsEmbedding.goToIndex') }}
      </a-button>
    </a-space>
  </template>
</a-alert>

<script setup lang="ts">
const showModelChangeWarning = ref(false)

// 保存配置后检测模型变化
const handleSaveConfig = async () => {
  // ... 保存逻辑 ...

  const response = await updateAIModelConfig(config)

  if (response.requires_rebuild) {
    showModelChangeWarning.value = true
  }
}

const restartApp = () => {
  window.location.reload()
}

const goToIndexManagement = () => {
  router.push('/index-management')
}
</script>
```

---

### 10.8 i18n 翻译键

```json
{
  "index": {
    "rebuildAll": "全量重建索引",
    "rebuildAllConfirm": "确认全量重建",
    "rebuildAllWarning": "将清空所有索引并按历史任务逐一重建，预计耗时较长",
    "rebuildAllStarted": "已启动 {count} 个重建任务",
    "rebuildAllComplete": "全量重建完成！成功完成 {count} 个任务",
    "rebuildAllPartial": "重建完成：成功 {completed} 个，失败 {failed} 个",
    "rebuildAllFailed": "全量重建失败",
    "rebuildProgress": "重建进度",
    "processed": "已处理",
    "jobStatus": {
      "pending": "等待中",
      "processing": "处理中",
      "completed": "已完成",
      "failed": "失败"
    }
  },
  "settingsEmbedding": {
    "modelChanged": "嵌入模型已更改",
    "rebuildTip": "建议重启应用后在索引管理中重建索引",
    "goToIndex": "前往索引管理"
  }
}
```

---

### 10.9 前端调用示例

```typescript
// 1. 保存嵌入模型配置
const saveConfig = async (config: AIModelConfig) => {
  const response = await api.put('/api/config/ai-model', config);
  const result = await response.json();

  if (result.success) {
    // 显示引导提示，不自动触发重建
    showModelChangeWarning.value = true;
  }
};

// 2. 用户前往索引管理页，点击全量重建
const handleRebuildAll = async () => {
  Modal.confirm({
    title: t('index.rebuildAllConfirm'),
    content: t('index.rebuildAllWarning'),
    okButtonProps: { danger: true },
    onOk: async () => {
      const response = await api.post('/api/index/rebuild-all');
      const result = await response.json();

      if (result.success) {
        message.success(t('index.rebuildAllStarted', { count: result.data.length }));
        rebuildJobs.value = result.data;
        startPolling();
      }
    }
  });
};

// 3. 轮询所有任务进度（复用现有接口）
const startPolling = () => {
  const timer = setInterval(async () => {
    const promises = rebuildJobs.value.map(job =>
      api.get(`/api/index/status/${job.index_id}`)
    );

    const results = await Promise.all(promises);
    rebuildJobs.value = results.map(r => r.data);

    // 检查是否全部完成
    const allCompleted = rebuildJobs.value.every(
      job => job.status === 'completed' || job.status === 'failed'
    );

    if (allCompleted) {
      clearInterval(timer);
      const completed = rebuildJobs.value.filter(j => j.status === 'completed').length;
      const failed = rebuildJobs.value.filter(j => j.status === 'failed').length;

      if (failed > 0) {
        message.warning(t('index.rebuildAllPartial', { completed, failed }));
      } else {
        message.success(t('index.rebuildAllComplete', { count: completed }));
      }
    }
  }, 2000);
};
```

---

## 11. 部署方案

### 11.1 部署步骤

1. **代码部署**
   ```bash
   # 1. 拉取最新代码
   git pull

   # 2. 安装依赖（无需新增）
   pip install -r requirements.txt

   # 3. 重启服务
   python main.py
   ```

2. **数据库迁移**
   ```sql
   -- 无需迁移，复用现有 ai_models 表
   ```

3. **验证部署**
   ```bash
   # 1. 检查 API 端点
   curl http://127.0.0.1:8000/docs

   # 2. 测试配置接口
   curl -X PUT http://127.0.0.1:8000/api/config/ai-model \
     -H "Content-Type: application/json" \
     -d '{"model_type":"embedding","provider":"local",...}'
   ```

### 10.2 回滚方案

```bash
# 如果出现问题，立即切回本地模型
curl -X PUT http://127.0.0.1:8000/api/config/ai-model \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "embedding",
    "provider": "local",
    "model_name": "BAAI/bge-m3",
    "config": {"device": "cpu", "embedding_dim": 1024}
  }'
```

---

## 12. 监控与日志

### 11.1 日志记录

**关键日志点**：

| 日志点 | 级别 | 内容 |
|--------|------|------|
| 服务加载 | INFO | 加载成功/失败，配置信息（脱敏） |
| API 调用 | DEBUG | 请求参数（文本数量），响应时间 |
| 维度归一化 | DEBUG | 原始维度，目标维度，处理模式 |
| 错误重试 | WARNING | 重试次数，错误原因 |
| API 错误 | ERROR | HTTP 状态码，错误信息 |

**日志格式**：

```python
logger.info(f"OpenAI嵌入服务加载成功: model={self.model}, dim={self.embedding_dim}")
logger.debug(f"调用嵌入API: url={url}, 文本数量={len(texts)}")
logger.warning(f"API请求失败，重试 {retry_count}/{self.max_retries}: {error}")
```

### 11.2 监控指标

**关键指标**：

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| API 成功率 | API 调用成功比例 | < 95% |
| API 响应时间 | API 调用耗时 | > 5s |
| 维度归一化率 | 需要归一化的请求比例 | > 50% |
| 错误重试率 | 需要重试的请求比例 | > 10% |

---

## 13. 后续扩展

### 12.1 短期优化

- [ ] 添加更多维度处理模式（PCA 降维、随机投影等）
- [ ] 支持动态批处理大小（根据 API 限流自动调整）
- [ ] 优化高并发场景下的性能

### 12.2 中期规划

- [ ] 支持多嵌入模型并行（混合检索）
- [ ] 添加嵌入质量评估工具
- [ ] 支持自定义向量维度（需重建 Faiss 索引）

### 12.3 长期愿景

- [ ] 支持本地模型微调后上传到云端
- [ ] 企业专属云端嵌入服务
- [ ] 嵌入向量缓存机制

---

## 14. 风险与挑战

### 13.1 技术风险

| 风险项 | 风险等级 | 影响 | 应对措施 | 状态 |
|-------|---------|------|---------|------|
| API 调用失败 | 中 | 搜索功能中断 | 自动重试 + 降级到本地 | 规划中 |
| 索引重建耗时 | 中 | 用户体验 | 进度提示 + 后台重建 | 规划中 |
| API 配额耗尽 | 低 | 搜索功能受限 | 用户配置限额 + 提示 | 规划中 |

### 13.2 业务风险

| 风险项 | 风险等级 | 影响 | 应对措施 | 状态 |
|-------|---------|------|---------|------|
| 用户接受度低 | 中 | 功能使用率低 | 提供免费试用 + 详细说明 | 规划中 |
| 成本增加 | 低 | 运营成本上升 | 设置使用限额 + 按需付费 | 规划中 |

---

## 14. 总结

本技术方案设计了完整的云端嵌入模型调用能力，核心要点：

1. **服务实现**：`OpenAIEmbeddingService` 类，支持所有 OpenAI 兼容 API
2. **原始维度**：使用模型的原始向量维度，不做任何归一化处理
3. **索引重建**：切换模型必须重建索引，确保向量空间一致性
4. **重建方案**：简化方案 - 复用现有索引任务系统，减少代码量
5. **重建接口**：单一端点 `POST /api/index/rebuild-all`，复用现有进度查询
6. **类型互斥**：与本地嵌入模型互斥，用户只能选择一种
7. **向后兼容**：保持现有本地嵌入模型可用
8. **安全优先**：API 密钥加密存储，日志脱敏处理

---

**文档版本**：v2.0（简化方案）
**最后更新**：2026-03-26
**变更内容**：索引重建机制从独立端点方案（方案B）更新为简化方案（复用现有索引任务系统）

---

> **使用说明**：
> 1. 本技术方案文档基于现有架构设计
> 2. 复用现有 AI 模型配置和管理机制
> 3. 与 OpenAI 兼容大模型服务保持一致的架构模式
> 4. 支持所有兼容 OpenAI Embeddings API 标准的服务
> 5. 切换嵌入模型时必须重建索引，保证向量空间一致性
> 6. **索引重建采用简化方案**：复用现有 `run_full_index_task` 和 `IndexJobModel`
