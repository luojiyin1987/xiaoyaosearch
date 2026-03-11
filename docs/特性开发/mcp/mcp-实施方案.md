# MCP 服务器支持 - 实施方案

> **文档类型**：实施方案
> **特性状态**：已批准，待开发
> **创建时间**：2026-03-11
> **决策时间**：2026-03-11
> **决策人**：产品负责人
> **关联文档**：[架构决策 AD-20260311-01](../../架构决策/AD-20260311-01-MCP服务器架构选择.md)

---

## 1. 实施概述

### 1.1 目标

为小遥搜索添加 **MCP (Model Context Protocol)** 服务器支持，使 Claude Desktop 等 AI 应用能够连接小遥搜索进行本地文件搜索，包括语义搜索、全文搜索、语音搜索、图像搜索和混合搜索。

### 1.2 核心决策点（已确定）

| 决策项 | 决策结果 | 状态 |
|--------|---------|------|
| **架构选择** | FastAPI 集成 + SSE 端点 | ✅ 已确定 |
| **通信方式** | Server-Sent Events (HTTP) | ✅ 已确定 |
| **工具范围** | 5 个搜索工具（P0 + P1） | ✅ 已确定 |
| **服务复用** | 适配器模式复用现有服务 | ✅ 已确定 |
| **配置管理** | 环境变量（MCP_ 前缀） | ✅ 已确定 |

### 1.3 设计原则

- **内存优化**：AI 模型只加载一次，在 FastAPI 进程内共享
- **简化部署**：无需启动独立进程，配置简单
- **服务复用**：通过适配器复用现有搜索服务，不修改现有代码
- **最小侵入**：MCP 模块独立，不影响现有功能
- **协议标准**：严格遵循 MCP 2024-11-05 协议规范

---

## 2. 技术方案对比

### 2.1 架构方案对比

| 对比维度 | 方案A：FastAPI集成+SSE | 方案B：独立进程+stdio |
|---------|----------------------|---------------------|
| **内存占用** | 低（AI模型加载一次，约4-6GB） | 高（两份模型实例，约8-12GB） |
| **部署复杂度** | 低（无需额外进程） | 高（需要进程管理） |
| **服务调用** | 直接调用（无通信开销） | 需要进程间通信 |
| **代码复用** | 高（直接调用现有服务） | 中（需要适配层） |
| **Claude Desktop支持** | ✅ 原生支持 SSE | ✅ 原生支持 stdio |
| **扩展性** | 中（与 FastAPI 耦合） | 高（独立扩展） |

**推荐：方案A（FastAPI 集成 + SSE）**
- 理由：内存占用降低 50%，部署简单，符合 Claude Desktop 官方推荐

### 2.2 工具范围对比

| 工具 | 优先级 | 复杂度 | 决策 |
|------|--------|--------|------|
| `semantic_search` | P0 | 低 | ✅ 必须实现 |
| `fulltext_search` | P0 | 低 | ✅ 必须实现 |
| `voice_search` | P1 | 中 | ✅ 必须实现 |
| `image_search` | P1 | 中 | ✅ 必须实现 |
| `hybrid_search` | P1 | 中 | ✅ 必须实现 |
| Resources | P2 | 中 | ❌ 后续版本 |
| Prompts | P2 | 低 | ❌ 后续版本 |

**推荐：实现 P0 + P1 工具**
- 理由：覆盖主要搜索场景，Resources/Prompts 可后续扩展

---

## 3. 实施方案

### 3.1 推荐方案：FastAPI 集成 + SSE 端点

#### 方案架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         Claude Desktop                          │
│                   (MCP 客户端，第三方应用)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ SSE (HTTP)
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI 主进程                              │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                     /mcp/sse 端点                          │ │
│  │                    (SSE 传输层)                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                   MCPServer (MCP 协议)                     │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐          │ │
│  │  │  Tool 1    │  │  Tool 2    │  │  Tool 3-5  │          │ │
│  │  │ semantic   │  │ fulltext   │  │ voice/     │          │ │
│  │  │ _search    │  │ _search    │  │ image/     │          │ │
│  │  └─────┬──────┘  └─────┬──────┘  │ hybrid     │          │ │
│  │        └───────────────┴───────────┤            │          │ │
│  │                          ↓          └────────────┘          │ │
│  │              ┌───────────────────────┐                    │ │
│  │              │   SearchAdapter       │                    │ │
│  │              │  (适配现有搜索服务)     │                    │ │
│  │              └───────────┬───────────┘                    │ │
│  └──────────────────────────┼─────────────────────────────────┘ │
│                              ↓                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                 现有搜索服务（无需修改）                     │ │
│  │  ┌──────────────────┐  ┌──────────────────┐              │ │
│  │  │ ChunkSearch      │  │ FullTextSearch   │              │ │
│  │  │ Service          │  │ Service          │              │ │
│  │  └──────────────────┘  └──────────────────┘              │ │
│  │  ┌──────────────────┐  ┌──────────────────┐              │ │
│  │  │ ImageSearch      │  │ VoiceRecognition │              │ │
│  │  │ Service          │  │ Service          │              │ │
│  │  └──────────────────┘  └──────────────────┘              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              ↓                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    AI 模型（共享）                          │ │
│  │  BGE-M3 | FasterWhisper | CN-CLIP                          │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                        ┌─────────────────┐
                        │  本地数据库/索引  │
                        │  SQLite + Faiss │
                        └─────────────────┘
```

#### 核心设计

1. **MCP 模块结构**：
   ```
   backend/app/mcp/
   ├── __init__.py
   ├── server.py              # MCP 服务器主类
   ├── config.py              # MCP 配置管理
   ├── sse_transport.py       # SSE 传输层
   ├── tools/
   │   ├── __init__.py
   │   ├── base.py            # 工具基类
   │   ├── semantic_search.py
   │   ├── fulltext_search.py
   │   ├── voice_search.py
   │   ├── image_search.py
   │   └── hybrid_search.py
   └── adapters/
       ├── __init__.py
       └── search_adapter.py  # 搜索服务适配器
   ```

2. **FastAPI 集成**：
   - SSE 端点：`GET /mcp/sse`
   - 生命周期：随 FastAPI 启动/停止
   - 配置：环境变量 `MCP_*`

3. **工具实现**：
   - 继承 `BaseTool` 抽象基类
   - 通过 `SearchAdapter` 调用现有服务
   - 返回符合 MCP 协议的 JSON 格式

---

## 4. 实施步骤

### 第一阶段：MCP 模块搭建（Day 1，约 8 小时）

#### 4.1 创建目录结构

**新建目录和文件**：
```bash
backend/app/mcp/
├── __init__.py
├── server.py
├── config.py
├── sse_transport.py
├── tools/
│   ├── __init__.py
│   └── base.py
└── adapters/
    ├── __init__.py
    └── search_adapter.py
```

#### 4.2 实现配置管理

**新建文件：`backend/app/mcp/config.py`**

```python
"""
MCP 服务器配置管理
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class MCPServerConfig:
    """MCP 服务器配置"""
    # 服务器配置
    enabled: bool = True
    sse_endpoint: str = "/mcp/sse"
    heartbeat_interval: int = 30

    # 搜索默认参数
    default_limit: int = 20
    default_threshold: float = 0.7

    # 模型配置
    semantic_weight: float = 0.7  # 混合搜索语义权重

    @classmethod
    def from_env(cls) -> "MCPServerConfig":
        """从环境变量加载配置"""
        return cls(
            enabled=os.getenv("MCP_SERVER_ENABLED", "true").lower() == "true",
            sse_endpoint=os.getenv("MCP_SSE_ENDPOINT", "/mcp/sse"),
            heartbeat_interval=int(os.getenv("MCP_SSE_HEARTBEAT_INTERVAL", "30")),
            default_limit=int(os.getenv("MCP_DEFAULT_LIMIT", "20")),
            default_threshold=float(os.getenv("MCP_DEFAULT_THRESHOLD", "0.7")),
            semantic_weight=float(os.getenv("MCP_SEMANTIC_WEIGHT", "0.7")),
        )

    def validate(self) -> None:
        """验证配置"""
        if self.default_limit < 1 or self.default_limit > 100:
            raise ValueError("default_limit 必须在 1-100 之间")

        if self.default_threshold < 0.0 or self.default_threshold > 1.0:
            raise ValueError("default_threshold 必须在 0.0-1.0 之间")

        if self.semantic_weight < 0.0 or self.semantic_weight > 1.0:
            raise ValueError("semantic_weight 必须在 0.0-1.0 之间")
```

#### 4.3 实现 MCP 服务器主类

**新建文件：`backend/app/mcp/server.py`**

```python
"""
MCP 服务器主类
"""
import logging
from typing import Optional, Dict, Any, List

from mcp import Server
from mcp.server.models import InitializationOptions
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent

from app.mcp.config import MCPServerConfig
from app.mcp.tools.base import BaseTool
from app.mcp.tools.semantic_search import SemanticSearchTool
from app.mcp.tools.fulltext_search import FulltextSearchTool
from app.mcp.tools.voice_search import VoiceSearchTool
from app.mcp.tools.image_search import ImageSearchTool
from app.mcp.tools.hybrid_search import HybridSearchTool

logger = logging.getLogger(__name__)


class MCPServer:
    """
    MCP 服务器

    负责：
    1. 管理 MCP 协议服务器
    2. 注册和调用工具
    3. 处理客户端连接
    """

    def __init__(self, config: MCPServerConfig):
        """
        初始化 MCP 服务器

        Args:
            config: MCP 服务器配置
        """
        self.config = config
        self.server: Optional[Server] = None
        self.tools: Dict[str, BaseTool] = {}

        logger.info("初始化 MCP 服务器")

    async def start(self) -> None:
        """启动 MCP 服务器"""
        try:
            logger.info("启动 MCP 服务器...")

            # 创建 MCP 服务器实例
            self.server = Server("xiaoyao-search")

            # 注册工具
            await self._register_tools()

            logger.info(f"MCP 服务器启动成功，注册工具: {list(self.tools.keys())}")

        except Exception as e:
            logger.error(f"启动 MCP 服务器失败: {str(e)}")
            raise

    async def stop(self) -> None:
        """停止 MCP 服务器"""
        try:
            logger.info("停止 MCP 服务器...")

            # 清理工具资源
            for tool in self.tools.values():
                await tool.cleanup()

            self.tools.clear()
            self.server = None

            logger.info("MCP 服务器已停止")

        except Exception as e:
            logger.error(f"停止 MCP 服务器失败: {str(e)}")

    async def _register_tools(self) -> None:
        """注册所有工具"""
        if not self.server:
            raise RuntimeError("MCP 服务器未初始化")

        # 创建工具实例
        tools_to_register = [
            SemanticSearchTool(self.config),
            FulltextSearchTool(self.config),
            VoiceSearchTool(self.config),
            ImageSearchTool(self.config),
            HybridSearchTool(self.config),
        ]

        # 注册到 MCP 服务器
        for tool in tools_to_register:
            tool_name = tool.name

            # 注册工具处理器
            @self.server.call_tool()
            async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
                if name == tool_name:
                    result = await tool.execute(arguments)
                    return [TextContent(type="text", text=result)]
                else:
                    raise ValueError(f"未知工具: {name}")

            # 注册工具定义
            self.tools[tool_name] = tool
            logger.info(f"注册工具: {tool_name}")

    @self.server.list_tools()
    async def list_tools(self) -> List[Tool]:
        """列出所有可用工具"""
        return [
            Tool(
                name=tool.name,
                description=tool.description,
                inputSchema=tool.input_schema
            )
            for tool in self.tools.values()
        ]

    def get_tools_info(self) -> List[Dict[str, Any]]:
        """获取工具信息（用于调试）"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "priority": tool.priority
            }
            for tool in self.tools.values()
        ]
```

#### 4.4 实现 SSE 传输层

**新建文件：`backend/app/mcp/sse_transport.py`**

```python
"""
MCP SSE 传输层
"""
import logging
from typing import AsyncIterator

from fastapi import Request
from mcp.server.sse import SseServerTransport
from starlette.responses import StreamingResponse

from app.mcp.server import MCPServer

logger = logging.getLogger(__name__)


async def create_sse_endpoint(mcp_server: MCPServer, request: Request) -> StreamingResponse:
    """
    创建 SSE 端点

    Args:
        mcp_server: MCP 服务器实例
        request: FastAPI 请求

    Returns:
        StreamingResponse: SSE 响应
    """
    async def event_stream() -> AsyncIterator[str]:
        """SSE 事件流"""
        try:
            logger.info("新 SSE 连接建立")

            # 创建 SSE 传输层
            transport = SseServerTransport("/mcp/sse")

            # 处理 MCP 消息
            async with transport.connect() as streams:
                async with mcp_server.server.incoming_message(streams[0]) as messages:
                    async for message in messages:
                        # 发送消息到客户端
                        yield f"data: {message.model_dump_json()}\n\n"

        except Exception as e:
            logger.error(f"SSE 连接错误: {str(e)}")
            yield f"event: error\ndata: {{\"message\": \"{str(e)}\"}}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
```

---

### 第二阶段：工具实现（Day 2-3，约 24 小时）

#### 4.5 实现工具基类

**新建文件：`backend/app/mcp/tools/base.py`**

```python
"""
MCP 工具基类
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class ToolPriority(Enum):
    """工具优先级"""
    P0 = "P0"  # 核心功能
    P1 = "P1"  # 重要功能
    P2 = "P2"  # 可选功能


class BaseTool(ABC):
    """
    MCP 工具基类

    所有 MCP 工具必须继承此类并实现 execute 方法
    """

    def __init__(self, priority: ToolPriority = ToolPriority.P1):
        """
        初始化工具

        Args:
            priority: 工具优先级
        """
        self.priority = priority

    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述"""
        pass

    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """输入参数 JSON Schema"""
        pass

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> str:
        """
        执行工具

        Args:
            arguments: 工具参数

        Returns:
            str: JSON 格式的执行结果
        """
        pass

    async def cleanup(self) -> None:
        """清理工具资源"""
        pass

    def _format_result(self, results: list, total: int, **extra) -> str:
        """
        格式化执行结果

        Args:
            results: 结果列表
            total: 总数
            **extra: 额外字段

        Returns:
            str: JSON 格式结果
        """
        import json

        result = {
            "results": results,
            "total": total,
            **extra
        }

        return json.dumps(result, ensure_ascii=False, indent=2)
```

#### 4.6 实现搜索适配器

**新建文件：`backend/app/mcp/adapters/search_adapter.py`**

```python
"""
搜索服务适配器
负责将 MCP 工具调用转换为现有搜索服务调用
"""
import logging
from typing import Dict, Any, List, Optional

from app.services.chunk_search_service import ChunkSearchService
from app.services.fulltext_search_service import FullTextSearchService
from app.services.image_search_service import ImageSearchService
from app.services.voice_recognition_service import VoiceRecognitionService

logger = logging.getLogger(__name__)


class SearchAdapter:
    """
    搜索服务适配器

    职责：
    1. 将 MCP 工具参数转换为搜索服务参数
    2. 调用现有搜索服务
    3. 将搜索结果转换为 MCP 格式
    """

    def __init__(self):
        """初始化适配器（服务实例由依赖注入提供）"""
        self.chunk_search: Optional[ChunkSearchService] = None
        self.fulltext_search: Optional[FullTextSearchService] = None
        self.image_search: Optional[ImageSearchService] = None
        self.voice_recognition: Optional[VoiceRecognitionService] = None

    def set_services(
        self,
        chunk_search: ChunkSearchService,
        fulltext_search: FullTextSearchService,
        image_search: ImageSearchService,
        voice_recognition: VoiceRecognitionService
    ) -> None:
        """设置搜索服务实例"""
        self.chunk_search = chunk_search
        self.fulltext_search = fulltext_search
        self.image_search = image_search
        self.voice_recognition = voice_recognition
        logger.info("搜索服务适配器初始化完成")

    async def semantic_search(
        self,
        query: str,
        limit: int = 20,
        threshold: float = 0.7,
        file_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        语义搜索

        Args:
            query: 搜索查询
            limit: 返回数量
            threshold: 相似度阈值
            file_types: 文件类型过滤

        Returns:
            搜索结果
        """
        if not self.chunk_search:
            raise RuntimeError("语义搜索服务未初始化")

        results = await self.chunk_search.search(
            query_text=query,
            limit=limit,
            threshold=threshold,
            file_type_filter=file_types
        )

        return self._format_search_results(results, query)

    async def fulltext_search(
        self,
        query: str,
        limit: int = 20,
        file_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """全文搜索"""
        if not self.fulltext_search:
            raise RuntimeError("全文搜索服务未初始化")

        results = await self.fulltext_search.search(
            query_text=query,
            limit=limit,
            file_type_filter=file_types
        )

        return self._format_search_results(results, query)

    async def voice_search(
        self,
        audio_data: str,
        search_type: str = "semantic",
        limit: int = 20,
        threshold: float = 0.7,
        file_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """语音搜索"""
        if not self.voice_recognition:
            raise RuntimeError("语音识别服务未初始化")

        # 1. 语音识别
        transcription = await self.voice_recognition.transcribe(audio_data)

        # 2. 根据搜索类型调用相应搜索
        if search_type == "semantic":
            results = await self.semantic_search(
                query=transcription["text"],
                limit=limit,
                threshold=threshold,
                file_types=file_types
            )
        elif search_type == "fulltext":
            results = await self.fulltext_search(
                query=transcription["text"],
                limit=limit,
                file_types=file_types
            )
        else:  # hybrid
            results = await self.hybrid_search(
                query=transcription["text"],
                limit=limit,
                threshold=threshold,
                file_types=file_types
            )

        return {
            "transcription": transcription["text"],
            "transcription_confidence": transcription.get("confidence", 0.0),
            "search_type": search_type,
            **results
        }

    async def image_search(
        self,
        image_data: str,
        limit: int = 20,
        threshold: float = 0.7
    ) -> Dict[str, Any]:
        """图像搜索"""
        if not self.image_search:
            raise RuntimeError("图像搜索服务未初始化")

        results = await self.image_search.search(
            image_data=image_data,
            limit=limit,
            threshold=threshold
        )

        return {
            "results": results,
            "total": len(results),
            "query_image_hash": results[0].get("image_hash", "") if results else ""
        }

    async def hybrid_search(
        self,
        query: str,
        limit: int = 20,
        threshold: float = 0.7,
        semantic_weight: float = 0.7,
        file_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """混合搜索"""
        # 并行调用语义和全文搜索
        import asyncio

        semantic_results, fulltext_results = await asyncio.gather(
            self.semantic_search(query, limit * 2, threshold, file_types),
            self.fulltext_search(query, limit * 2, file_types),
            return_exceptions=True
        )

        # 合并和重排序结果
        merged = self._merge_and_rerank(
            semantic_results["results"] if not isinstance(semantic_results, Exception) else [],
            fulltext_results["results"] if not isinstance(fulltext_results, Exception) else [],
            semantic_weight
        )

        return {
            "results": merged[:limit],
            "total": len(merged),
            "query": query
        }

    def _format_search_results(self, results: List[Any], query: str) -> Dict[str, Any]:
        """格式化搜索结果为 MCP 格式"""
        formatted_results = []

        for item in results:
            formatted_results.append({
                "chunk_id": item.get("id", ""),
                "file_path": item.get("file_path", ""),
                "file_name": item.get("file_name", ""),
                "file_type": item.get("file_type", ""),
                "content": item.get("content", "")[:500],  # 截断长内容
                "page_number": item.get("page_number"),
                "score": item.get("score", 0.0),
                "metadata": item.get("metadata", {})
            })

        return {
            "results": formatted_results,
            "total": len(formatted_results),
            "query": query
        }

    def _merge_and_rerank(
        self,
        semantic_results: List[Dict],
        fulltext_results: List[Dict],
        semantic_weight: float
    ) -> List[Dict]:
        """合并和重排序混合搜索结果"""
        # TODO: 实现基于分数的融合算法
        merged = []

        # 添加语义搜索结果
        for item in semantic_results:
            item["semantic_score"] = item.get("score", 0.0)
            item["fulltext_score"] = 0.0
            item["hybrid_score"] = item["semantic_score"] * semantic_weight
            merged.append(item)

        # 添加全文搜索结果
        for item in fulltext_results:
            existing = next((m for m in merged if m["chunk_id"] == item.get("id")), None)

            if existing:
                # 合并分数
                existing["fulltext_score"] = item.get("score", 0.0)
                existing["hybrid_score"] = (
                    existing["semantic_score"] * semantic_weight +
                    existing["fulltext_score"] * (1 - semantic_weight)
                )
            else:
                item["semantic_score"] = 0.0
                item["fulltext_score"] = item.get("score", 0.0)
                item["hybrid_score"] = item["fulltext_score"] * (1 - semantic_weight)
                merged.append(item)

        # 按混合分数排序
        merged.sort(key=lambda x: x["hybrid_score"], reverse=True)

        return merged


# 全局适配器实例
search_adapter = SearchAdapter()
```

#### 4.7 实现语义搜索工具

**新建文件：`backend/app/mcp/tools/semantic_search.py`**

```python
"""
语义搜索工具
"""
import logging
from typing import Dict, Any

from app.mcp.tools.base import BaseTool, ToolPriority
from app.mcp.config import MCPServerConfig
from app.mcp.adapters.search_adapter import search_adapter

logger = logging.getLogger(__name__)


class SemanticSearchTool(BaseTool):
    """语义搜索工具（基于 BGE-M3）"""

    def __init__(self, config: MCPServerConfig):
        super().__init__(priority=ToolPriority.P0)
        self.config = config

    @property
    def name(self) -> str:
        return "semantic_search"

    @property
    def description(self) -> str:
        return """基于 BGE-M3 模型的语义搜索，支持自然语言查询理解。

适合用自然语言描述的查询，如"关于机器学习算法优化的方法"。

使用示例：
- 查找关于人工智能的文档
- 搜索 Python 异步编程相关内容
- 找到数据库性能优化资料"""

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索查询词（1-500字符）",
                    "minLength": 1,
                    "maxLength": 500
                },
                "limit": {
                    "type": "integer",
                    "description": "返回结果数量（1-100，默认20）",
                    "minimum": 1,
                    "maximum": 100,
                    "default": self.config.default_limit
                },
                "threshold": {
                    "type": "number",
                    "description": "相似度阈值（0.0-1.0，默认0.7）",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": self.config.default_threshold
                },
                "file_types": {
                    "type": "array",
                    "description": "文件类型过滤（如 [\"pdf\", \"md\"]）",
                    "items": {"type": "string"}
                }
            },
            "required": ["query"]
        }

    async def execute(self, arguments: Dict[str, Any]) -> str:
        """执行语义搜索"""
        try:
            query = arguments["query"]
            limit = arguments.get("limit", self.config.default_limit)
            threshold = arguments.get("threshold", self.config.default_threshold)
            file_types = arguments.get("file_types")

            logger.info(f"执行语义搜索: query={query}, limit={limit}")

            result = await search_adapter.semantic_search(
                query=query,
                limit=limit,
                threshold=threshold,
                file_types=file_types
            )

            return self._format_result(
                results=result["results"],
                total=result["total"],
                query=result["query"]
            )

        except Exception as e:
            logger.error(f"语义搜索失败: {str(e)}")
            raise ValueError(f"语义搜索失败: {str(e)}")
```

#### 4.8 实现其他工具

类似地实现：
- `fulltext_search.py` - 全文搜索工具
- `voice_search.py` - 语音搜索工具
- `image_search.py` - 图像搜索工具
- `hybrid_search.py` - 混合搜索工具

（代码结构类似，此处省略详细实现）

---

### 第三阶段：FastAPI 集成（Day 4，约 6 小时）

#### 4.9 添加 SSE 端点

**修改文件：`backend/app/main.py`**

```python
# 在现有导入后添加
from app.mcp.server import MCPServer
from app.mcp.config import MCPServerConfig
from app.mcp.sse_transport import create_sse_endpoint

# 在 FastAPI app 定义后添加
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    # ... 现有启动逻辑 ...

    # 初始化 MCP 服务器
    mcp_config = MCPServerConfig.from_env()

    if mcp_config.enabled:
        try:
            app.state.mcp_server = MCPServer(mcp_config)
            await app.state.mcp_server.start()
            logger.info("✅ MCP 服务器启动成功")
        except Exception as e:
            logger.error(f"❌ MCP 服务器启动失败: {str(e)}")
            app.state.mcp_server = None

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    # ... 现有关闭逻辑 ...

    # 停止 MCP 服务器
    if hasattr(app.state, "mcp_server") and app.state.mcp_server:
        try:
            await app.state.mcp_server.stop()
            logger.info("✅ MCP 服务器已停止")
        except Exception as e:
            logger.error(f"❌ MCP 服务器停止失败: {str(e)}")

# 添加 SSE 端点
@app.get("/mcp/sse")
async def mcp_sse_endpoint(request: Request):
    """
    MCP SSE 端点

    Claude Desktop 通过此端点连接 MCP 服务器
    """
    if not hasattr(app.state, "mcp_server") or not app.state.mcp_server:
        raise HTTPException(status_code=503, detail="MCP 服务器未启用")

    return await create_sse_endpoint(app.state.mcp_server, request)
```

---

### 第四阶段：配置与文档（Day 5，约 2.5 小时）

#### 4.10 环境变量配置

**修改文件：`backend/.env`**

```bash
# ========== MCP 服务器配置 ==========
MCP_SERVER_ENABLED=true
MCP_SSE_ENDPOINT=/mcp/sse
MCP_SSE_HEARTBEAT_INTERVAL=30

# 搜索默认参数
MCP_DEFAULT_LIMIT=20
MCP_DEFAULT_THRESHOLD=0.7
MCP_SEMANTIC_WEIGHT=0.7
```

#### 4.11 配置文档

已创建以下文档：
- [MCP PRD](./mcp-01-prd.md)
- [MCP 原型设计](./mcp-02-原型.md)
- [MCP 技术方案](./mcp-03-技术方案.md)
- [MCP 工具文档](../../mcp工具文档.md)

---

## 5. 工作量与排期

### 5.1 工作量分解

| 阶段 | 任务 | 预计时间 |
|------|------|----------|
| 一 | MCP 模块搭建 | 8 小时 |
| 二 | 搜索工具实现 | 24 小时 |
| 三 | FastAPI 集成 | 6 小时 |
| 四 | 配置与文档 | 2.5 小时 |
| 五 | 测试与验收（可选） | 21 小时 |
| **总计（核心）** | | **40.5 小时（5 天）** |
| **总计（含测试）** | | **61.5 小时（6 天）** |

### 5.2 里程碑

| 里程碑 | 预计完成时间 | 关键交付物 |
|--------|-------------|-----------|
| M1: MCP 框架完成 | Day 1 | MCPServer、配置管理、SSE 传输层 |
| M2: 工具框架完成 | Day 2 | BaseTool、SearchAdapter、semantic_search |
| M3: 核心工具完成 | Day 3 | fulltext_search、voice_search |
| M4: 全部工具与集成完成 | Day 4 | image_search、hybrid_search、FastAPI 集成 |
| M5: 功能验收完成 | Day 5 | 配置文档、单元测试、集成测试 |

---

## 6. 风险与应对

| 风险项 | 风险等级 | 影响 | 应对措施 |
|--------|---------|------|---------|
| mcp-python-sdk API 学习曲线 | 中 | 延期 1-2 天 | 提前阅读官方文档，参考示例代码 |
| AI 模型内存不足 | 高 | 无法运行 | 优化模型加载顺序，添加内存检查 |
| Claude Desktop 连接问题 | 中 | 验收失败 | 详细调试日志，参考官方配置文档 |
| FasterWhisper 兼容性 | 中 | voice_search 失败 | 支持多种音频格式降级处理 |
| CN-CLIP 推理性能 | 低 | 图搜缓慢 | 批量处理优化 |
| SSE 连接稳定性 | 中 | 频繁断连 | 心跳保活机制 |

---

## 7. 验收标准

### 功能验收

- [ ] Claude Desktop 可成功连接 `/mcp/sse` 端点
- [ ] `semantic_search` 工具可正常调用并返回结果
- [ ] `fulltext_search` 工具可正常调用并返回结果
- [ ] `voice_search` 工具可识别音频并搜索
- [ ] `image_search` 工具可查找相似图片
- [ ] `hybrid_search` 工具可综合语义和全文搜索
- [ ] 工具参数验证正确（类型、范围、必填）
- [ ] 错误处理友好且信息完整

### 性能验收

- [ ] 语义搜索响应时间 < 2s
- [ ] 全文搜索响应时间 < 1s
- [ ] 语音搜索（含识别）< 5s
- [ ] 图像搜索 < 3s
- [ ] 混合搜索 < 3s
- [ ] 内存占用 < 8GB（含 AI 模型）

### 质量验收

- [ ] 无 P0/P1 级别 Bug
- [ ] P2 级别 Bug ≤ 3
- [ ] 代码符合项目规范
- [ ] 配置文档清晰易懂
- [ ] Claude Desktop 配置示例正确

---

## 8. 决策建议

### 推荐方案：FastAPI 集成 + SSE 端点

**优势：**

1. ✅ **内存优化**：AI 模型只加载一次，节省 4-6GB 内存
2. ✅ **简化部署**：无需启动独立进程，配置简单
3. ✅ **直接调用**：直接调用现有搜索服务，无通信开销
4. ✅ **Claude Desktop 支持**：官方推荐的 SSE 传输方式

**权衡：**

1. ⚠️ MCP 模块与 FastAPI 耦合（但影响有限）
2. ⚠️ 需要处理 FastAPI 生命周期管理

---

## 9. 决策记录

### 确定方案：FastAPI 集成 + SSE 端点

**决策时间**：2026-03-11

**确定内容**：

| 决策项 | 决策结果 |
|--------|---------|
| 架构选择 | ✅ FastAPI 集成 + SSE |
| 通信方式 | ✅ Server-Sent Events |
| 工具范围 | ✅ 5 个搜索工具（P0 + P1） |
| 服务复用 | ✅ 适配器模式 |
| 配置管理 | ✅ 环境变量（MCP_ 前缀） |

**方案优势：**

1. ✅ **内存占用降低 50%**：AI 模型只加载一次
2. ✅ **部署简单**：无需额外进程管理
3. ✅ **服务复用**：通过适配器直接调用现有服务
4. ✅ **官方推荐**：Claude Desktop 支持 SSE 传输

**已知权衡：**

1. ⚠️ MCP 模块与 FastAPI 耦合
2. ⚠️ 需要处理生命周期管理

---

## 10. 相关文档

- [架构决策 AD-20260311-01](../../架构决策/AD-20260311-01-MCP服务器架构选择.md) - 架构决策文档
- [MCP PRD](./mcp-01-prd.md) - 产品需求文档
- [MCP 原型设计](./mcp-02-原型.md) - 原型设计说明
- [MCP 技术方案](./mcp-03-技术方案.md) - 技术实现方案
- [MCP 任务清单](./mcp-04-开发任务清单.md) - 任务分解
- [MCP 开发排期表](./mcp-05-开发排期表.md) - 时间规划
- [MCP 工具文档](../../mcp工具文档.md) - 工具接口文档

---

**文档版本**: v1.0
**创建时间**: 2026-03-11
**最后更新**: 2026-03-11
**状态**: 已批准，待开发
