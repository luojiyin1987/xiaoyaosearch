# MCP 服务器支持 - 技术方案

> **文档类型**：技术方案
> **特性状态**：规划中
> **创建时间**：2026-03-11
> **最后更新**：2026-03-11
> **关联文档**：[MCP PRD](./mcp-01-prd.md) | [MCP 原型](./mcp-02-原型.md)

---

## 1. 方案概述

### 1.1 技术目标

为小遥搜索添加 **Model Context Protocol (MCP)** 服务器能力，使 Claude Desktop 等 AI 应用能够连接小遥搜索进行本地文件智能搜索。采用 **FastAPI 集成 + SSE 端点** 方案，共享 AI 模型和搜索服务，避免重复加载，节省内存。

### 1.2 设计原则

- **内存高效**：AI 模型只加载一次，MCP 和 Electron 前端共享服务
- **部署简单**：单一进程，无需管理多个服务
- **向后兼容**：现有功能和 API 完全不受影响
- **协议标准**：基于 Anthropic 官方 MCP 协议规范
- **适配器模式**：通过 SearchAdapter 复用现有搜索服务
- **功能开关**：可通过环境变量启用/禁用 MCP 服务

### 1.3 技术选型

| 技术/框架 | 用途 | 选择理由 | 替代方案 |
|----------|------|---------|---------|
| **mcp-python-sdk** | MCP 协议实现 | Anthropic 官方 Python SDK，完整支持 MCP 协议规范 | 自己实现 MCP 协议 |
| **SSE (Server-Sent Events)** | 传输协议 | MCP HTTP 传输方式，支持远程访问 | stdio（仅本地） |
| **FastAPI** | Web 框架 | 现有框架，集成简单 | Flask、Django |
| **asyncio** | 异步框架 | 与 FastAPI 兼容，支持高并发 | 多线程 |
| **Pydantic** | 数据验证 | 与现有代码一致，类型安全 | 纯字典 |
| **适配器模式** | 架构模式 | 无需修改现有搜索服务，降低耦合 | 直接修改现有服务 |

### 1.4 支持的搜索工具

| 工具名称 | 优先级 | AI 模型 | 说明 |
|---------|-------|---------|------|
| semantic_search | P0 | BGE-M3 | 语义搜索，支持自然语言查询 |
| fulltext_search | P0 | Whoosh | 全文搜索，精确关键词匹配 |
| voice_search | P1 | FasterWhisper | 语音搜索，语音转文字后搜索 |
| image_search | P1 | CN-CLIP | 图像搜索，图片查找相似内容 |
| hybrid_search | P1 | BGE-M3 + Whoosh | 混合搜索，语义+全文 |

---

## 2. 架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           统一 FastAPI 进程                              │
│                            端口 8000                                     │
├─────────────────────────────────────────────────────────────────────────┤
│  HTTP API 层                                                              │
│  ┌─────────────────────┐  ┌─────────────────────┐                        │
│  │   /api/*            │  │   /mcp/sse          │                        │
│  │   (Electron前端)    │  │   (Claude Desktop)  │                        │
│  └─────────────────────┘  └─────────────────────┘                        │
├─────────────────────────────────────────────────────────────────────────┤
│  业务逻辑层                                                               │
│  ┌─────────────────────┐  ┌─────────────────────┐                        │
│  │  FastAPI Routers    │  │  MCP 服务器          │                        │
│  │  - search_router    │  │  - MCP Protocol     │                        │
│  │  - index_router     │  │  - Tools (搜索工具)  │                        │
│  │  - config_router    │  │  - SSE Transport    │                        │
│  │  - settings_router  │  │  - Resource Handler │                        │
│  └─────────────────────┘  └─────────────────────┘                        │
│                                ↓                                         │
│                    ┌─────────────────────┐                                │
│                    │  SearchAdapter      │                                │
│                    │  (搜索服务适配器)    │                                │
│                    └─────────────────────┘                                │
├─────────────────────────────────────────────────────────────────────────┤
│  服务层（共享）                                                           │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌──────────────────┐ │
│  │ ChunkSearchService  │  │ ImageSearchService  │  │ AIModelManager   │ │
│  │ (语义/全文/混合)     │  │ (图搜图)            │  │ (AI模型管理)     │ │
│  └─────────────────────┘  └─────────────────────┘  └──────────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│  数据层（共享）                                                           │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌──────────────────┐ │
│  │  BGE-M3 模型         │  │  FasterWhisper      │  │  CN-CLIP 模型    │ │
│  └─────────────────────┘  └─────────────────────┘  └──────────────────┘ │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌──────────────────┐ │
│  │  Faiss 向量索引      │  │  Whoosh 全文索引    │  │  SQLite 数据库   │ │
│  └─────────────────────┘  └─────────────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘

通信方式：
┌──────────────────┐         HTTP SSE         ┌──────────────────┐
│  Claude Desktop  │ ←──────────────────────→ │ FastAPI + MCP    │
│  (MCP Client)    │     端点: /mcp/sse       │  (单一进程)       │
└──────────────────┘                          └──────────────────┘
```

### 2.2 目录结构

```
backend/
├── app/
│   ├── mcp/                                # MCP 模块（新增）
│   │   ├── __init__.py                     # 模块初始化
│   │   ├── server.py                       # MCP 服务器主类
│   │   ├── config.py                       # MCP 配置管理
│   │   ├── transport.py                    # SSE 传输层实现
│   │   ├── tools/                          # 工具模块
│   │   │   ├── __init__.py
│   │   │   ├── semantic_search.py          # 语义搜索工具
│   │   │   ├── fulltext_search.py          # 全文搜索工具
│   │   │   ├── voice_search.py             # 语音搜索工具
│   │   │   ├── image_search.py             # 图像搜索工具
│   │   │   └── hybrid_search.py            # 混合搜索工具
│   │   └── adapters/                       # 适配器模块
│   │       ├── __init__.py
│   │       └── search_adapter.py           # 搜索服务适配器
│   │
│   ├── services/                           # 现有服务（无变更）
│   │   ├── chunk_search_service.py         # 块搜索服务
│   │   ├── image_search_service.py         # 图像搜索服务
│   │   └── ai_model_manager.py             # AI 模型管理器
│   │
│   ├── core/                               # 核心模块（扩展）
│   │   └── config.py                       # 全局配置（添加 MCP 配置）
│   │
│   └── api/                                # API 模块（无变更）
│       ├── search_router.py
│       ├── index_router.py
│       └── config_router.py
│
├── main.py                                 # FastAPI 主入口（修改）
│
└── requirements.txt                         # 依赖（添加 mcp 包）
```

### 2.3 数据流

**Claude Desktop 搜索流程**：

```
用户在 Claude Desktop 输入查询
    ↓
Claude 分析意图，选择合适的工具（如 semantic_search）
    ↓
Claude 通过 SSE 发送工具调用请求
    ↓
FastAPI 接收 SSE 请求，路由到 /mcp/sse 端点
    ↓
MCP 服务器解析请求，提取工具名和参数
    ↓
SearchAdapter 调用对应搜索服务
    ↓
搜索服务执行查询（Faiss/Whoosh）
    ↓
MCP 服务器格式化结果为 MCP 协议格式
    ↓
通过 SSE 返回结果给 Claude Desktop
    ↓
Claude 基于结果生成智能回答
```

---

## 3. 核心实现

### 3.1 MCP 服务器主类

```python
# backend/app/mcp/server.py
from mcp.server import Server
from mcp.types import Tool, TextContent
from app.mcp.tools.semantic_search import SemanticSearchTool
from app.mcp.tools.fulltext_search import FulltextSearchTool
from app.mcp.tools.voice_search import VoiceSearchTool
from app.mcp.tools.image_search import ImageSearchTool
from app.mcp.tools.hybrid_search import HybridSearchTool
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class MCPServer:
    """MCP 服务器主类"""

    def __init__(self, config: MCPConfig):
        self.config = config
        self.server = Server(config.server_name)
        self._tools = {}
        self._init_tools()

    def _init_tools(self):
        """初始化所有工具"""
        tools = [
            SemanticSearchTool(),
            FulltextSearchTool(),
            VoiceSearchTool(),
            ImageSearchTool(),
            HybridSearchTool()
        ]

        for tool in tools:
            self._tools[tool.name] = tool
            logger.info(f"✅ 注册工具: {tool.name}")

    @property
    def tools(self) -> list[Tool]:
        """获取所有工具定义"""
        return [tool.definition for tool in self._tools.values()]

    async def call_tool(self, name: str, arguments: dict) -> list[TextContent]:
        """调用工具"""
        if name not in self._tools:
            raise ValueError(f"未知工具: {name}")

        tool = self._tools[name]
        logger.info(f"调用工具: {name}, 参数: {arguments}")

        try:
            result = await tool.execute(arguments)
            return [TextContent(type="text", text=result)]
        except Exception as e:
            logger.error(f"工具执行失败: {name}, 错误: {str(e)}")
            return [TextContent(type="text", text=f"错误: {str(e)}")]

def create_mcp_server() -> MCPServer:
    """创建 MCP 服务器实例"""
    from app.mcp.config import get_mcp_config
    config = get_mcp_config()
    return MCPServer(config)
```

### 3.2 SSE 传输层

```python
# backend/app/mcp/transport.py
from fastapi import Request
from fastapi.responses import StreamingResponse
from mcp.server.sse import SseServerTransport
from app.mcp.server import MCPServer
from app.core.logging_config import get_logger

logger = get_logger(__name__)

async def create_sse_endpoint(mcp_server: MCPServer, request: Request):
    """
    创建 SSE 传输端点

    Args:
        mcp_server: MCP 服务器实例
        request: FastAPI 请求对象

    Returns:
        StreamingResponse: SSE 响应
    """
    async def handle_sse():
        """SSE 处理逻辑"""
        # 创建 SSE 传输
        transport = SseServerTransport("/mcp/sse")

        async with transport.connect_sse(
            request.scope,
            request.receive,
            request._send
        ) as streams:
            # 注册工具
            await mcp_server.server.list_tools()

            # 处理请求
            await mcp_server.server.run(
                *streams,
                mcp_server.server.create_initialization_options()
            )

    logger.info("📡 SSE 连接建立")
    return StreamingResponse(
        handle_sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
```

### 3.3 工具基类

```python
# backend/app/mcp/tools/__init__.py
from abc import ABC, abstractmethod
from mcp.types import Tool
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class BaseTool(ABC):
    """工具基类"""

    def __init__(self):
        self._definition = None

    @property
    @abstractmethod
    def definition(self) -> Tool:
        """工具定义"""
        pass

    @abstractmethod
    async def execute(self, arguments: dict) -> str:
        """执行工具

        Args:
            arguments: 工具参数

        Returns:
            str: JSON 格式的结果字符串
        """
        pass

    def _format_result(self, data: dict) -> str:
        """格式化结果为 JSON 字符串

        Args:
            data: 结果数据

        Returns:
            str: JSON 字符串
        """
        import json
        return json.dumps(data, ensure_ascii=False, indent=2)
    def _validate_arguments(self, arguments: dict, required: list[str]) -> None:
        """验证参数

        Args:
            arguments: 工具参数
            required: 必需参数列表

        Raises:
            ValueError: 参数验证失败
        """
        missing = [key for key in required if key not in arguments]
        if missing:
            raise ValueError(f"缺少必需参数: {', '.join(missing)}")
```

### 3.4 语义搜索工具

```python
# backend/app/mcp/tools/semantic_search.py
from mcp.types import Tool
from app.mcp.tools import BaseTool
from app.mcp.adapters.search_adapter import SearchAdapter

class SemanticSearchTool(BaseTool):
    """语义搜索工具"""

    def __init__(self):
        super().__init__()
        self.adapter = SearchAdapter()

    @property
    def definition(self) -> Tool:
        return Tool(
            name="semantic_search",
            description="基于BGE-M3模型的语义搜索，支持自然语言查询理解。适合用自然语言描述的查询，如'关于机器学习算法优化的方法'。",
            inputSchema={
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
                        "description": "返回结果数量（1-100）",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 20
                    },
                    "threshold": {
                        "type": "number",
                        "description": "相似度阈值（0.0-1.0）",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.7
                    },
                    "file_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "文件类型过滤（可选）"
                    }
                },
                "required": ["query"]
            }
        )

    async def execute(self, arguments: dict) -> str:
        """执行语义搜索"""
        self._validate_arguments(arguments, ["query"])

        result = await self.adapter.semantic_search(
            query=arguments["query"],
            limit=arguments.get("limit", 20),
            threshold=arguments.get("threshold", 0.7),
            file_types=arguments.get("file_types")
        )

        return self._format_result(result)
```

### 3.5 语音搜索工具

```python
# backend/app/mcp/tools/voice_search.py
import base64
import io
from mcp.types import Tool
from app.mcp.tools import BaseTool
from app.mcp.adapters.search_adapter import SearchAdapter
from app.services.ai_model_manager import ai_model_service

class VoiceSearchTool(BaseTool):
    """语音搜索工具"""

    def __init__(self):
        super().__init__()
        self.adapter = SearchAdapter()

    @property
    def definition(self) -> Tool:
        return Tool(
            name="voice_search",
            description="基于FasterWhisper模型的语音搜索，支持语音输入转文本后进行搜索。适合通过语音快速搜索，无需手动输入文字。支持中英文语音识别，音频时长建议不超过30秒。",
            inputSchema={
                "type": "object",
                "properties": {
                    "audio_data": {
                        "type": "string",
                        "description": "Base64 编码的音频数据（支持 WAV、MP3、M4A 格式）"
                    },
                    "search_type": {
                        "type": "string",
                        "description": "搜索类型",
                        "enum": ["semantic", "fulltext", "hybrid"],
                        "default": "semantic"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回结果数量（1-100）",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 20
                    },
                    "threshold": {
                        "type": "number",
                        "description": "相似度阈值（0.0-1.0）",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.7
                    },
                    "file_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "文件类型过滤（可选）"
                    }
                },
                "required": ["audio_data"]
            }
        )

    async def execute(self, arguments: dict) -> str:
        """执行语音搜索"""
        self._validate_arguments(arguments, ["audio_data"])

        # 1. 解码音频数据
        audio_bytes = base64.b64decode(arguments["audio_data"])
        audio_file = io.BytesIO(audio_bytes)

        # 2. 语音识别
        transcription = await ai_model_service.transcribe(audio_file)
        query = transcription["text"].strip()

        if not query:
            return self._format_result({
                "error": "语音识别失败",
                "transcription": transcription
            })

        # 3. 执行搜索
        search_type = arguments.get("search_type", "semantic")
        if search_type == "semantic":
            result = await self.adapter.semantic_search(
                query=query,
                limit=arguments.get("limit", 20),
                threshold=arguments.get("threshold", 0.7),
                file_types=arguments.get("file_types")
            )
        elif search_type == "fulltext":
            result = await self.adapter.fulltext_search(
                query=query,
                limit=arguments.get("limit", 20),
                file_types=arguments.get("file_types")
            )
        else:  # hybrid
            result = await self.adapter.hybrid_search(
                query=query,
                limit=arguments.get("limit", 20),
                threshold=arguments.get("threshold", 0.7),
                file_types=arguments.get("file_types")
            )

        # 4. 添加识别结果
        result["transcription"] = {
            "text": query,
            "language": transcription.get("language"),
            "duration": transcription.get("duration")
        }

        return self._format_result(result)
```

### 3.6 搜索服务适配器

```python
# backend/app/mcp/adapters/search_adapter.py
from typing import List, Optional
from app.services.chunk_search_service import get_chunk_search_service
from app.services.image_search_service import get_image_search_service
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class SearchAdapter:
    """搜索服务适配器，将现有搜索服务适配为 MCP 工具"""

    def __init__(self):
        self.chunk_search_service = get_chunk_search_service()
        self.image_search_service = get_image_search_service()

    async def semantic_search(
        self,
        query: str,
        limit: int = 20,
        threshold: float = 0.7,
        file_types: Optional[List[str]] = None
    ) -> dict:
        """语义搜索"""
        from app.models.schemas import SearchType

        result = await self.chunk_search_service.search(
            query=query,
            search_type=SearchType.SEMANTIC,
            limit=limit,
            offset=0,
            threshold=threshold,
            file_types=file_types
        )
        return self._format_result(result)

    async def fulltext_search(
        self,
        query: str,
        limit: int = 20,
        file_types: Optional[List[str]] = None
    ) -> dict:
        """全文搜索"""
        from app.models.schemas import SearchType

        result = await self.chunk_search_service.search(
            query=query,
            search_type=SearchType.FULLTEXT,
            limit=limit,
            offset=0,
            file_types=file_types
        )
        return self._format_result(result)

    async def hybrid_search(
        self,
        query: str,
        limit: int = 20,
        threshold: float = 0.7,
        file_types: Optional[List[str]] = None
    ) -> dict:
        """混合搜索"""
        from app.models.schemas import SearchType

        result = await self.chunk_search_service.search(
            query=query,
            search_type=SearchType.HYBRID,
            limit=limit,
            offset=0,
            threshold=threshold,
            file_types=file_types
        )
        return self._format_result(result)

    async def image_search(
        self,
        image_data: str,
        limit: int = 20,
        threshold: float = 0.7
    ) -> dict:
        """图像搜索"""
        import base64
        from io import BytesIO

        # 解码图片数据
        image_bytes = base64.b64decode(image_data)
        image_file = BytesIO(image_bytes)

        # 调用图像搜索服务
        result = await self.image_search_service.search(
            image=image_file,
            limit=limit,
            threshold=threshold
        )
        return self._format_image_result(result)

    def _format_result(self, result: dict) -> dict:
        """格式化搜索结果为 MCP 友好的 JSON 格式"""
        data = result.get('data', {})
        results = data.get('results', [])

        return {
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

    def _format_image_result(self, result: dict) -> dict:
        """格式化图像搜索结果"""
        data = result.get('data', {})
        results = data.get('results', [])

        return {
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
```

### 3.7 FastAPI 集成

```python
# backend/main.py（修改部分）
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.logging_config import get_logger, logger
from app.mcp.server import create_mcp_server
from app.mcp.transport import create_sse_endpoint

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # ... 现有初始化代码 ...

    # ========== MCP 服务器初始化 ==========
    logger.info("初始化 MCP 服务器...")
    try:
        from app.core.config import get_settings
        settings = get_settings()

        if settings.mcp.sse_enabled:
            # 创建 MCP 服务器实例
            mcp_server = create_mcp_server()
            app.state.mcp_server = mcp_server
            logger.info("✅ MCP 服务器初始化完成")
            logger.info(f"📡 SSE 端点: http://127.0.0.1:8000/mcp/sse")
        else:
            app.state.mcp_server = None
            logger.info("MCP 服务器未启用")
    except Exception as e:
        logger.error(f"❌ MCP 服务器初始化失败: {str(e)}")
        app.state.mcp_server = None
    # =====================================

    yield

    # 关闭时清理...
    # ... 现有清理代码 ...

# 创建 FastAPI 应用
app = FastAPI(...)

# ========== MCP SSE 端点 ==========
from fastapi import Request, HTTPException

@app.get("/mcp/sse")
async def mcp_sse_endpoint(request: Request):
    """
    MCP SSE 传输端点

    Claude Desktop 通过此端点连接小遥搜索
    示例 URL: http://127.0.0.1:8000/mcp/sse
    """
    if not app.state.mcp_server:
        raise HTTPException(status_code=503, detail="MCP 服务器未启用")

    return await create_sse_endpoint(app.state.mcp_server, request)

# MCP 健康检查端点
@app.get("/mcp/health")
async def mcp_health():
    """MCP 服务器健康检查"""
    return {
        "status": "enabled" if app.state.mcp_server else "disabled",
        "tools": len(app.state.mcp_server.tools) if app.state.mcp_server else 0
    }
# =====================================

# ... 其他路由 ...
```

---

## 4. 配置管理

### 4.1 配置模型

```python
# backend/app/mcp/config.py
from pydantic import BaseSettings, Field
from typing import Optional

class MCPConfig(BaseSettings):
    """MCP 服务器配置"""

    # 服务器配置
    server_name: str = Field(default="xiaoyao-search", description="服务器名称")
    server_version: str = Field(default="1.0.0", description="服务器版本")

    # SSE 配置
    sse_enabled: bool = Field(default=True, description="是否启用 SSE 传输")
    sse_path: str = Field(default="/mcp/sse", description="SSE 端点路径")

    # 搜索配置
    default_limit: int = Field(default=20, ge=1, le=100, description="默认结果数量")
    default_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="默认相似度阈值")

    # 语音搜索配置
    voice_enabled: bool = Field(default=True, description="是否启用语音搜索")
    voice_max_duration: int = Field(default=30, ge=1, le=60, description="最大音频时长（秒）")

    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")

    class Config:
        env_prefix = "MCP_"

# 全局配置实例
_mcp_config: Optional[MCPConfig] = None

def get_mcp_config() -> MCPConfig:
    """获取 MCP 配置"""
    global _mcp_config
    if _mcp_config is None:
        _mcp_config = MCPConfig()
    return _mcp_config

def set_mcp_config(config: MCPConfig):
    """设置 MCP 配置"""
    global _mcp_config
    _mcp_config = config
```

### 4.2 全局配置扩展

```python
# backend/app/core/config.py（扩展部分）
from pydantic import BaseSettings

class Settings(BaseSettings):
    # ... 现有配置 ...

    # MCP 配置
    mcp_sse_enabled: bool = Field(default=True, description="是否启用 MCP SSE 服务")
    mcp_default_limit: int = Field(default=20, ge=1, le=100, description="MCP 默认结果数量")
    mcp_default_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="MCP 默认相似度阈值")

    class Config:
        env_prefix = ""
```

### 4.3 环境变量配置

```bash
# backend/.env（添加）
# ========== MCP 服务器配置 ==========
MCP_SSE_ENABLED=true
MCP_SERVER_NAME=xiaoyao-search
MCP_SERVER_VERSION=1.0.0
MCP_DEFAULT_LIMIT=20
MCP_DEFAULT_THRESHOLD=0.7
MCP_VOICE_ENABLED=true
MCP_VOICE_MAX_DURATION=30
MCP_LOG_LEVEL=INFO
# =====================================
```

---

## 5. API 设计

### 5.1 SSE 端点

**端点**: `GET /mcp/sse`

**描述**: MCP SSE 传输端点，Claude Desktop 通过此端点连接

**响应**:
```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

**示例请求**:
```bash
curl -N http://127.0.0.1:8000/mcp/sse
```

### 5.2 健康检查端点

**端点**: `GET /mcp/health`

**描述**: MCP 服务器健康检查

**响应示例**:
```json
{
  "status": "enabled",
  "tools": 5
}
```

### 5.3 工具列表端点

**端点**: 通过 MCP 协议自动暴露

**描述**: 返回所有可用的 MCP 工具

**响应示例**:
```json
{
  "tools": [
    {
      "name": "semantic_search",
      "description": "基于BGE-M3模型的语义搜索...",
      "inputSchema": {...}
    },
    {
      "name": "fulltext_search",
      "description": "基于Whoosh的全文搜索...",
      "inputSchema": {...}
    },
    ...
  ]
}
```

---

## 6. 测试方案

### 6.1 单元测试

```python
# tests/test_mcp_tools.py
import pytest
from app.mcp.tools.semantic_search import SemanticSearchTool

class TestSemanticSearchTool:
    """语义搜索工具测试"""

    @pytest.fixture
    def tool(self):
        return SemanticSearchTool()

    def test_tool_definition(self, tool):
        """测试工具定义"""
        assert tool.definition.name == "semantic_search"
        assert "query" in tool.definition.inputSchema["properties"]

    @pytest.mark.asyncio
    async def test_execute_success(self, tool, mock_search_service):
        """测试成功执行"""
        result = await tool.execute({
            "query": "测试查询",
            "limit": 10
        })
        assert "results" in result

    @pytest.mark.asyncio
    async def test_execute_missing_query(self, tool):
        """测试缺少必需参数"""
        with pytest.raises(ValueError, match="缺少必需参数"):
            await tool.execute({"limit": 10})

    @pytest.mark.asyncio
    async def test_execute_invalid_limit(self, tool):
        """测试无效参数"""
        with pytest.raises(Exception):
            await tool.execute({
                "query": "测试",
                "limit": 999  # 超过最大值
            })
```

### 6.2 集成测试

```python
# tests/test_mcp_integration.py
import pytest
from httpx import AsyncClient
from app.main import app

class TestMCPIntegration:
    """MCP 集成测试"""

    @pytest.fixture
    async def client(self):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac

    @pytest.mark.asyncio
    async def test_sse_endpoint(self, client):
        """测试 SSE 端点"""
        response = await client.get("/mcp/sse")
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        """测试健康检查端点"""
        response = await client.get("/mcp/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["enabled", "disabled"]
```

### 6.3 端到端测试

```python
# tests/test_mcp_e2e.py
import pytest
from mcp.client import Client

class TestMCPEndToEnd:
    """MCP 端到端测试"""

    @pytest.mark.asyncio
    async def test_full_search_flow(self):
        """测试完整搜索流程"""
        # 连接到 MCP 服务器
        client = Client("http://127.0.0.1:8000/mcp/sse")
        await client.connect()

        # 获取工具列表
        tools = await client.list_tools()
        assert "semantic_search" in [t.name for t in tools]

        # 调用搜索工具
        result = await client.call_tool(
            "semantic_search",
            {"query": "测试查询", "limit": 10}
        )

        assert "results" in result
        await client.disconnect()
```

---

## 7. 部署方案

### 7.1 依赖安装

```bash
# backend/requirements.txt（添加）
# MCP 协议支持
mcp>=0.9.0

# SSE 传输支持（通常包含在 mcp 包中）
# uvicorn[standard]  # 已存在
```

### 7.2 部署步骤

1. **安装依赖**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   ```bash
   # 编辑 .env 文件
   MCP_SSE_ENABLED=true
   ```

3. **启动服务**
   ```bash
   python main.py
   ```

4. **验证部署**
   ```bash
   # 检查健康状态
   curl http://127.0.0.1:8000/mcp/health

   # 检查 SSE 端点
   curl -N http://127.0.0.1:8000/mcp/sse
   ```

### 7.3 Claude Desktop 配置

```json
{
  "mcpServers": {
    "xiaoyao-search": {
      "url": "http://127.0.0.1:8000/mcp/sse"
    }
  }
}
```

---

## 8. 监控与日志

### 8.1 日志记录

```python
# 使用统一日志配置
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# 关键日志点
logger.info("✅ MCP 服务器初始化完成")
logger.info(f"📡 SSE 连接建立: {client_host}")
logger.info(f"🔍 调用工具: {tool_name}, 参数: {arguments}")
logger.info(f"✓ 工具执行完成: {tool_name}, 耗时: {duration}ms")
logger.error(f"✗ 工具执行失败: {tool_name}, 错误: {error}")
```

### 8.2 性能监控

```python
# backend/app/mcp/middleware.py
import time
from fastapi import Request
from app.core.logging_config import get_logger

logger = get_logger(__name__)

async def log_mcp_requests(request: Request, call_next):
    """记录 MCP 请求"""
    start_time = time.time()

    # 处理请求
    response = await call_next(request)

    # 计算耗时
    duration = (time.time() - start_time) * 1000

    # 记录日志
    if request.url.path.startswith("/mcp"):
        logger.info(f"MCP 请求: {request.method} {request.url.path} - {response.status_code} - {duration:.2f}ms")

    return response
```

---

## 9. 安全设计

### 9.1 本地绑定

```python
# SSE 端点仅允许本地访问
from fastapi import Request, HTTPException

@app.get("/mcp/sse")
async def mcp_sse_endpoint(request: Request):
    # 检查来源 IP
    client_host = request.client.host
    if client_host not in ["127.0.0.1", "::1", "localhost"]:
        logger.warning(f"拒绝远程连接: {client_host}")
        raise HTTPException(status_code=403, detail="仅允许本地访问")

    # ... 正常处理 ...
```

### 9.2 参数验证

```python
# 使用 Pydantic 进行参数验证
from pydantic import BaseModel, Field, validator

class SemanticSearchParams(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(default=20, ge=1, le=100)
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    file_types: Optional[List[str]] = None

    @validator("file_types")
    def validate_file_types(cls, v):
        if v:
            valid_types = ["pdf", "docx", "md", "txt", "png", "jpg"]
            invalid = [f for f in v if f.lower() not in valid_types]
            if invalid:
                raise ValueError(f"无效的文件类型: {', '.join(invalid)}")
        return v
```

### 9.3 资源限制

```python
# 限制音频文件大小
MAX_AUDIO_SIZE = 10 * 1024 * 1024  # 10MB

async def validate_audio_size(audio_data: str):
    """验证音频文件大小"""
    import base64
    size = len(base64.b64decode(audio_data))
    if size > MAX_AUDIO_SIZE:
        raise ValueError(f"音频文件过大，最大允许 {MAX_AUDIO_SIZE // 1024 // 1024}MB")
```

---

## 10. 性能优化

### 10.1 连接复用

- SSE 连接保持长连接，避免频繁建立连接
- 使用连接池管理搜索服务

### 10.2 结果缓存

```python
# backend/app/mcp/cache.py
from functools import lru_cache
from hashlib import sha256
import json

def cache_key(params: dict) -> str:
    """生成缓存键"""
    params_str = json.dumps(params, sort_keys=True)
    return sha256(params_str.encode()).hexdigest()

@lru_cache(maxsize=100)
async def cached_search(key: str, search_func, *args, **kwargs):
    """缓存搜索结果"""
    return await search_func(*args, **kwargs)
```

### 10.3 并发控制

```python
# 限制并发搜索数量
import asyncio

class SemaphoreLimiter:
    def __init__(self, max_concurrent: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def __aenter__(self):
        await self.semaphore.acquire()

    async def __aexit__(self, *args):
        self.semaphore.release()

# 使用
limiter = SemaphoreLimiter(max_concurrent=10)

async def execute_search():
    async with limiter:
        # 执行搜索
        pass
```

---

## 11. 故障处理

### 11.1 错误码

| 错误码 | 描述 | 处理方式 |
|-------|------|---------|
| 403 | 远程连接拒绝 | 返回"仅允许本地访问" |
| 503 | MCP 服务未启用 | 提示检查配置 |
| 400 | 参数验证失败 | 返回具体错误信息 |
| 500 | 工具执行失败 | 返回错误详情和堆栈 |

### 11.2 重试机制

```python
# 客户端重试建议
{
  "maxRetries": 3,
  "retryDelay": 1000,
  "retryableErrors": ["timeout", "connection_error"]
}
```

---

## 12. 后续优化

### 12.1 功能扩展

- [ ] 添加 Resources 支持（文件资源访问）
- [ ] 添加 Prompts 支持（预定义提示词模板）
- [ ] 支持更多搜索过滤条件
- [ ] 支持搜索结果导出

### 12.2 性能优化

- [ ] 实现搜索结果缓存
- [ ] 优化大文件处理
- [ ] 添加搜索性能监控

### 12.3 用户体验

- [ ] 提供配置验证工具
- [ ] 添加搜索历史记录
- [ ] 支持自定义搜索参数

---

**文档版本**：v1.0
**创建时间**：2026-03-11
**最后更新**：2026-03-11
**维护者**：AI助手

> **使用说明**：
> 1. 本技术方案基于 FastAPI 集成 + SSE 端点方案
> 2. 与现有代码保持一致，复用搜索服务
> 3. 所有代码示例使用中文注释
> 4. 配置参数支持环境变量覆盖
