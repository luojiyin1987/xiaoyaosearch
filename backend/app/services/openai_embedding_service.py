"""
OpenAI 兼容嵌入模型服务
支持所有兼容 OpenAI Embeddings API 标准的云端服务
"""
import asyncio
import aiohttp
from typing import List, Dict, Any, Union
import numpy as np
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from app.services.ai_model_base import (
    BaseAIModel,
    ModelType,
    ProviderType,
    ModelStatus,
    AIModelException
)
from app.utils.enum_helpers import get_enum_value
from app.core.logging_config import logger


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
                - embedding_dim: 嵌入向量维度（自动检测）
        """
        # 验证必填参数
        api_key = config.get("api_key")
        if not api_key:
            raise AIModelException("API 密钥不能为空", error_code="MISSING_API_KEY")

        model = config.get("model")
        if not model:
            raise AIModelException("模型名称不能为空", error_code="MISSING_MODEL")

        # 默认配置
        default_config = {
            "api_key": api_key,
            "endpoint": "https://api.openai.com/v1",
            "model": model,
            "timeout": 30,
            "batch_size": 10,  # 修改：降低批处理大小以兼容更多云端 API（阿里云限制为 10）
            "embedding_dim": None,  # 将从 API 自动检测
            "max_retries": 3,
            "retry_min_wait": 2,
            "retry_max_wait": 10
        }
        default_config.update(config)

        super().__init__(
            model_name=default_config["model"],
            model_type=ModelType.EMBEDDING,
            provider=ProviderType.CLOUD,
            config=default_config
        )

        # 构建 API URL
        self.endpoint = self.config["endpoint"].rstrip("/")
        self.embeddings_url = f"{self.endpoint}/embeddings"

        # HTTP 会话
        self._session: aiohttp.ClientSession = None
        self._embedding_dim: int = None

        logger.info(f"初始化 OpenAI 兼容嵌入服务: {self.model_name}, 端点: {self.endpoint}")

    async def load_model(self) -> bool:
        """
        创建 HTTP 会话

        这是云端模型的"加载"操作，实际上是创建 HTTP 客户端会话

        Returns:
            bool: 加载是否成功
        """
        try:
            self.update_status(ModelStatus.LOADING)

            if self._session is None:
                timeout = aiohttp.ClientTimeout(total=self.config["timeout"])
                self._session = aiohttp.ClientSession(timeout=timeout)

            # 测试连接并获取模型信息
            try:
                model_info = await self._fetch_model_info()
                self._embedding_dim = model_info.get("embedding_dim")
                logger.info(f"云端嵌入模型连接成功，向量维度: {self._embedding_dim}")
            except Exception as e:
                logger.warning(f"获取模型信息失败，将在首次预测时重试: {str(e)}")

            self.update_status(ModelStatus.LOADED)
            logger.info(f"HTTP 会话已创建: {self.embeddings_url}")
            return True

        except Exception as e:
            error_msg = f"创建 HTTP 会话失败: {str(e)}"
            logger.error(error_msg)
            self.update_status(ModelStatus.ERROR, error_msg)
            raise AIModelException(error_msg, model_name=self.model_name)

    async def unload_model(self) -> bool:
        """
        关闭 HTTP 会话

        释放 HTTP 客户端资源

        Returns:
            bool: 卸载是否成功
        """
        try:
            logger.info(f"开始卸载 OpenAI 兼容嵌入服务: {self.model_name}")

            if self._session:
                await self._session.close()
                self._session = None

            self.update_status(ModelStatus.UNLOADED)
            logger.info("HTTP 会话已关闭")
            return True

        except Exception as e:
            error_msg = f"关闭 HTTP 会话失败: {str(e)}"
            logger.error(error_msg)
            return False

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
            AIModelException: API 调用失败
        """
        if not self._session:
            await self.load_model()

        # 构建请求头
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json"
        }

        # 构建请求体
        payload = {
            "input": texts,
            "model": self.model_name
        }

        logger.debug(f"调用 Embeddings API: 文本数={len(texts)}, 模型={self.model_name}")

        # 发送请求
        async with self._session.post(
            self.embeddings_url,
            headers=headers,
            json=payload
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"API 调用失败: {response.status} - {error_text}")

                # 根据状态码判断错误类型
                if response.status == 401:
                    raise AIModelException("API 密钥无效", error_code="INVALID_API_KEY")
                elif response.status == 429:
                    raise AIModelException("API 调用频率超限", error_code="RATE_LIMIT_EXCEEDED")
                elif response.status == 500:
                    raise AIModelException("云端服务内部错误", error_code="SERVICE_ERROR")
                else:
                    raise AIModelException(f"API 调用失败: {response.status}", error_code=str(response.status))

            result = await response.json()

            # 记录向量维度
            if result.get("data") and len(result["data"]) > 0:
                embedding_dim = len(result["data"][0]["embedding"])
                if self._embedding_dim is None:
                    self._embedding_dim = embedding_dim
                    logger.info(f"检测到向量维度: {embedding_dim}")

            return result

    async def _fetch_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息（通过测试调用）

        Returns:
            模型信息字典
        """
        result = await self._call_embeddings_api(["test"])

        if result.get("data") and len(result["data"]) > 0:
            embedding_dim = len(result["data"][0]["embedding"])
        else:
            embedding_dim = 0

        return {
            "provider": get_enum_value(self.provider),
            "model_name": self.model_name,
            "embedding_dim": embedding_dim,
            "endpoint": self.endpoint,
            "status": "ready"
        }

    async def predict(self, inputs: Union[str, List[str]], **kwargs) -> np.ndarray:
        """
        生成文本嵌入向量

        Args:
            inputs: 输入文本或文本列表
            **kwargs: 其他预测参数
                - batch_size: 批处理大小

        Returns:
            嵌入向量数组（使用模型原始维度）

        Raises:
            AIModelException: 预测失败时抛出异常
        """
        if self.status != ModelStatus.LOADED:
            raise AIModelException(
                f"模型未加载，当前状态: {get_enum_value(self.status)}",
                model_name=self.model_name
            )

        try:
            # 标准化输入
            if isinstance(inputs, str):
                texts = [inputs]
            else:
                texts = inputs

            if not texts:
                raise AIModelException("输入文本不能为空", model_name=self.model_name)

            # 获取批处理大小
            batch_size = kwargs.get("batch_size", self.config.get("batch_size", 10))

            logger.info(f"开始云端嵌入预测，文本数量: {len(texts)}，批大小: {batch_size}")

            # 批处理
            all_embeddings = []

            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_num = i // batch_size + 1
                total_batches = (len(texts) + batch_size - 1) // batch_size

                try:
                    logger.debug(f"处理批次 {batch_num}/{total_batches}: {len(batch_texts)} 个文本")
                    result = await self._call_embeddings_api(batch_texts)

                    # 提取 embeddings（按索引排序）
                    embeddings_data = result.get("data", [])
                    embeddings_data_sorted = sorted(embeddings_data, key=lambda x: x["index"])

                    embeddings = [item["embedding"] for item in embeddings_data_sorted]
                    all_embeddings.extend(embeddings)

                except Exception as e:
                    logger.error(f"批次 {batch_num} 嵌入失败: {str(e)}")
                    # 返回空向量（保持批次对齐）
                    if self._embedding_dim:
                        all_embeddings.extend([[0.0] * self._embedding_dim] * len(batch_texts))
                    else:
                        raise AIModelException(f"批次 {batch_num} 嵌入失败且未知向量维度", error_code="EMBEDDING_FAILED")

            # 转换为 numpy 数组
            embeddings_array = np.array(all_embeddings, dtype=np.float32)

            self.record_usage()
            logger.info(f"云端嵌入预测完成，输出形状: {embeddings_array.shape}")
            return embeddings_array

        except AIModelException:
            raise
        except Exception as e:
            error_msg = f"云端嵌入预测失败: {str(e)}"
            logger.error(error_msg)
            raise AIModelException(error_msg, model_name=self.model_name)

    async def compute_similarity(self, query_embedding: np.ndarray, corpus_embeddings: np.ndarray) -> np.ndarray:
        """
        计算查询向量与语料库向量的相似度

        Args:
            query_embedding: 查询向量 [1, embedding_dim] 或 [embedding_dim]
            corpus_embeddings: 语料库向量 [n_docs, embedding_dim]

        Returns:
            np.ndarray: 相似度分数 [n_docs]
        """
        try:
            # 确保query_embedding是2D
            if query_embedding.ndim == 1:
                query_embedding = query_embedding.reshape(1, -1)

            # 计算余弦相似度
            similarities = np.dot(corpus_embeddings, query_embedding.T).flatten()

            return similarities

        except Exception as e:
            error_msg = f"相似度计算失败: {str(e)}"
            logger.error(error_msg)
            raise AIModelException(error_msg, model_name=self.model_name)

    async def search_similar(self, query: str, corpus_texts: List[str], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        搜索相似文本

        Args:
            query: 查询文本
            corpus_texts: 语料库文本列表
            top_k: 返回Top-K结果

        Returns:
            List[Dict[str, Any]]: 相似文本列表，包含文本内容和相似度分数
        """
        try:
            # 编码查询文本
            query_embedding = await self.predict(query)

            # 编码语料库文本
            corpus_embeddings = await self.predict(corpus_texts)

            # 计算相似度
            similarities = await self.compute_similarity(query_embedding, corpus_embeddings)

            # 获取Top-K结果
            top_indices = np.argsort(similarities)[::-1][:top_k]

            results = []
            for idx in top_indices:
                results.append({
                    "text": corpus_texts[idx],
                    "similarity": float(similarities[idx]),
                    "index": int(idx)
                })

            return results

        except Exception as e:
            error_msg = f"相似文本搜索失败: {str(e)}"
            logger.error(error_msg)
            raise AIModelException(error_msg, model_name=self.model_name)

    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息

        Returns:
            Dict[str, Any]: 模型信息字典
        """
        return {
            "model_name": self.model_name,
            "model_type": get_enum_value(self.model_type),
            "provider": get_enum_value(self.provider),
            "embedding_dim": self._embedding_dim or self.config.get("embedding_dim", "unknown"),
            "endpoint": self.endpoint,
            "timeout": self.config.get("timeout", 30),
            "batch_size": self.config.get("batch_size", 100),
            "max_retries": self.config.get("max_retries", 3)
        }

    def _get_test_input(self) -> str:
        """获取健康检查的测试输入"""
        return "test"

    async def health_check(self) -> bool:
        """
        模型健康检查

        Returns:
            bool: 模型是否健康可用
        """
        try:
            if self.status != ModelStatus.LOADED:
                return False

            # 调用 API 测试
            await self._call_embeddings_api([self._get_test_input()])
            return True

        except Exception as e:
            logger.error(f"云端嵌入模型健康检查失败: {str(e)}")
            return False


# 创建 OpenAI 嵌入服务实例的工厂函数
def create_openai_embedding_service(config: Dict[str, Any]) -> OpenAIEmbeddingService:
    """
    创建 OpenAI 兼容嵌入服务实例

    Args:
        config: 模型配置参数

    Returns:
        OpenAIEmbeddingService: OpenAI 兼容嵌入服务实例
    """
    return OpenAIEmbeddingService(config)
