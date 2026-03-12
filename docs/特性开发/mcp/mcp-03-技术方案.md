# MCP 服务器支持 - 技术方案

> **文档类型**：技术方案
> **特性状态**：开发中
> **创建时间**：2026-03-11
> **最后更新**：2026-03-12（采用 fastmcp 实现）
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
| **fastmcp** | MCP 协议实现 | PrefectHQ 维护的 Python MCP 框架，装饰器模式简洁优雅，自动 Schema 生成，原生 SSE 支持，代码量减少 60% | mcp-python-sdk |
| **SSE (Server-Sent Events)** | 传输协议 | MCP HTTP 传输方式，支持远程访问 | stdio（仅本地） |
| **FastAPI** | Web 框架 | 现有框架，fastmcp 原生支持 ASGI 集成 | Flask、Django |
| **asyncio** | 异步框架 | 与 FastAPI 兼容，支持高并发 | 多线程 |
| **Pydantic** | 数据验证 | fastmcp 自动从类型提示生成验证 | 纯字典 |
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

### 2.1 整体架构（fastmcp 简化版）

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           统一 FastAPI 进程                              │
│                            端口 8000                                     │
├─────────────────────────────────────────────────────────────────────────┤
│  HTTP API 层                                                              │
│  ┌─────────────────────┐  ┌─────────────────────┐                        │
│  │   /api/*            │  │   /mcp/sse          │                        │
│  │   (Electron前端)    │  │   (Claude Desktop)  │                        │
│  └─────────────────────┘  │   fastmcp 自动处理   │                        │
│                           └─────────────────────┘                        │
├─────────────────────────────────────────────────────────────────────────┤
│  业务逻辑层                                                               │
│  ┌─────────────────────┐  ┌─────────────────────┐                        │
│  │  FastAPI Routers    │  │  FastMCP 服务器      │                        │
│  │  - search_router    │  │  - @mcp.tool 装饰器  │                        │
│  │  - index_router     │  │  - 自动 Schema 生成  │                        │
│  │  - config_router    │  │  - 内置 SSE 传输     │                        │
│  │  - settings_router  │  │  - ASGI 应用挂载     │                        │
│  └─────────────────────┘  └─────────────────────┘                        │
│                                ↓                                         │
│                    ┌─────────────────────┐                                │
│                    │  搜索服务函数        │                                │
│                    │  (直接调用现有服务)  │                                │
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

通信方式（fastmcp 自动处理）：
┌──────────────────┐         HTTP SSE         ┌──────────────────┐
│  Claude Desktop  │ ←──────────────────────→ │ FastAPI + FastMCP│
│  (MCP Client)    │     端点: /mcp/sse       │  (单一进程)       │
└──────────────────┘    mcp.http_app(path)     └──────────────────┘
                        自动生成 ASGI 应用
```

**fastmcp 架构优势：**
- ✅ **简化设计**：无需单独的 `SearchAdapter` 适配器层
- ✅ **自动集成**：`mcp.http_app(path)` 自动生成 ASGI 应用
- ✅ **装饰器模式**：`@mcp.tool` 装饰器自动注册工具
- ✅ **类型安全**：从类型提示自动生成 Schema 和参数验证

### 2.2 目录结构

```
backend/
├── app/
│   ├── mcp/                                # MCP 模块（新增）
│   │   ├── __init__.py                     # 模块初始化
│   │   ├── server.py                       # FastMCP 服务器实例（使用装饰器模式）
│   │   ├── config.py                       # MCP 配置管理
│   │   └── tools/                          # 工具模块（使用 @mcp.tool 装饰器）
│   │       ├── __init__.py
│   │       ├── semantic_search.py          # 语义搜索工具
│   │       ├── fulltext_search.py          # 全文搜索工具
│   │       ├── voice_search.py             # 语音搜索工具
│   │       ├── image_search.py             # 图像搜索工具
│   │       └── hybrid_search.py            # 混合搜索工具
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
└── requirements.txt                         # 依赖（添加 fastmcp）
```

**fastmcp 简化点：**
- ✅ 无需 `transport.py` - fastmcp 内置 SSE 支持
- ✅ 无需 `adapters/` - 工具函数直接调用现有服务
- ✅ 无需 `BaseTool` 基类 - 使用装饰器定义工具
- ✅ 自动 Schema 生成 - 从类型提示自动生成

### 2.3 数据流（fastmcp 自动处理）

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
fastmcp 自动解析请求，提取工具名和参数
    ↓
fastmcp 根据类型提示自动验证参数
    ↓
调用对应的 @mcp.tool 装饰器函数
    ↓
工具函数直接调用现有搜索服务（无需适配器）
    ↓
搜索服务执行查询（Faiss/Whoosh）
    ↓
fastmcp 自动格式化结果为 MCP 协议格式
    ↓
通过内置 SSE 传输返回结果给 Claude Desktop
    ↓
Claude 基于结果生成智能回答
```

**fastmcp 自动化处理：**
- ✅ **自动参数验证**：从类型提示自动生成验证逻辑
- ✅ **自动错误处理**：统一异常捕获和错误格式化
- ✅ **自动协议转换**：自动将 Python 对象转换为 MCP 协议格式
- ✅ **自动 SSE 管理**：内置 SSE 连接管理和心跳检测

---

## 3. 核心实现

### 3.1 FastMCP 服务器主类（fastmcp 方案）

```python
# backend/app/mcp/server.py
from fastmcp import FastMCP
from app.mcp.tools.semantic_search import register_semantic_search
from app.mcp.tools.fulltext_search import register_fulltext_search
from app.mcp.tools.voice_search import register_voice_search
from app.mcp.tools.image_search import register_image_search
from app.mcp.tools.hybrid_search import register_hybrid_search
from app.core.logging_config import get_logger

logger = get_logger(__name__)

def create_mcp_server() -> FastMCP:
    """
    创建 FastMCP 服务器实例

    Returns:
        FastMCP: FastMCP 服务器实例
    """
    from app.mcp.config import get_mcp_config
    config = get_mcp_config()

    # 创建 FastMCP 实例
    mcp = FastMCP(
        name=config.server_name,
        version=config.server_version
    )

    # 注册所有搜索工具
    register_semantic_search(mcp)
    register_fulltext_search(mcp)
    register_voice_search(mcp)
    register_image_search(mcp)
    register_hybrid_search(mcp)

    logger.info(f"✅ FastMCP 服务器初始化完成: {config.server_name}")
    return mcp
```

### 3.2 语义搜索工具（fastmcp 装饰器模式）

```python
# backend/app/mcp/tools/semantic_search.py
from typing import Optional, List
from fastmcp import FastMCP
from app.services.chunk_search_service import get_chunk_search_service
from app.models.schemas import SearchType
import json

def register_semantic_search(mcp: FastMCP):
    """注册语义搜索工具"""

    @mcp.tool
    async def semantic_search(
        query: str,
        limit: int = 20,
        threshold: float = 0.7,
        file_types: Optional[List[str]] = None
    ) -> str:
        """
        基于BGE-M3模型的语义搜索，支持自然语言查询理解。

        适合用自然语言描述的查询，如"关于机器学习算法优化的方法"。
        支持文件类型过滤和相似度阈值设置。

        Args:
            query: 搜索查询词（1-500字符）
            limit: 返回结果数量（1-100，默认20）
            threshold: 相似度阈值（0.0-1.0，默认0.7）
            file_types: 文件类型过滤（可选）

        Returns:
            JSON 格式的搜索结果
        """
        # 参数验证
        if not query or len(query) > 500:
            raise ValueError("query 必须为1-500字符")
        if not 1 <= limit <= 100:
            raise ValueError("limit 必须为1-100")
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold 必须为0.0-1.0")

        # 执行搜索
        service = get_chunk_search_service()
        result = await service.search(
            query=query,
            search_type=SearchType.SEMANTIC,
            limit=limit,
            offset=0,
            threshold=threshold,
            file_types=file_types
        )

        # 格式化结果
        return json.dumps(_format_search_result(result), ensure_ascii=False, indent=2)


def _format_search_result(result: dict) -> dict:
    """格式化搜索结果"""
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
```

### 3.3 全文搜索工具

```python
# backend/app/mcp/tools/fulltext_search.py
from typing import Optional, List
from fastmcp import FastMCP
from app.services.chunk_search_service import get_chunk_search_service
from app.models.schemas import SearchType
import json

def register_fulltext_search(mcp: FastMCP):
    """注册全文搜索工具"""

    @mcp.tool
    async def fulltext_search(
        query: str,
        limit: int = 20,
        file_types: Optional[List[str]] = None
    ) -> str:
        """
        基于Whoosh的全文搜索，支持精确关键词匹配和短语查询。

        适合查找特定的关键词或短语，支持布尔运算符（AND, OR, NOT）。
        搜索速度极快，适合精确匹配场景。

        Args:
            query: 搜索查询词（1-500字符）
            limit: 返回结果数量（1-100，默认20）
            file_types: 文件类型过滤（可选）

        Returns:
            JSON 格式的搜索结果
        """
        from app.mcp.tools.semantic_search import _format_search_result

        service = get_chunk_search_service()
        result = await service.search(
            query=query,
            search_type=SearchType.FULLTEXT,
            limit=limit,
            offset=0,
            file_types=file_types
        )

        return json.dumps(_format_search_result(result), ensure_ascii=False, indent=2)
```

### 3.4 语音搜索工具

```python
# backend/app/mcp/tools/voice_search.py
import base64
import io
from typing import Optional, List
from fastmcp import FastMCP
from app.services.chunk_search_service import get_chunk_search_service
from app.services.ai_model_manager import ai_model_service
from app.models.schemas import SearchType
import json

def register_voice_search(mcp: FastMCP):
    """注册语音搜索工具"""

    @mcp.tool
    async def voice_search(
        audio_data: str,
        search_type: str = "semantic",
        limit: int = 20,
        threshold: float = 0.7,
        file_types: Optional[List[str]] = None
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

        Returns:
            JSON 格式的搜索结果（包含语音识别结果）
        """
        from app.mcp.tools.semantic_search import _format_search_result

        # 1. 解码音频数据
        audio_bytes = base64.b64decode(audio_data)
        audio_file = io.BytesIO(audio_bytes)

        # 2. 语音识别
        transcription = await ai_model_service.transcribe(audio_file)
        query = transcription["text"].strip()

        if not query:
            return json.dumps({
                "error": "语音识别失败",
                "transcription": transcription
            }, ensure_ascii=False, indent=2)

        # 3. 执行搜索
        service = get_chunk_search_service()
        search_type_enum = SearchType(search_type)

        result = await service.search(
            query=query,
            search_type=search_type_enum,
            limit=limit,
            offset=0,
            threshold=threshold,
            file_types=file_types
        )

        # 4. 格式化结果并添加识别信息
        formatted = _format_search_result(result)
        formatted["transcription"] = {
            "text": query,
            "language": transcription.get("language"),
            "duration": transcription.get("duration")
        }

        return json.dumps(formatted, ensure_ascii=False, indent=2)
```

### 3.5 图像搜索工具

```python
# backend/app/mcp/tools/image_search.py
import base64
from io import BytesIO
from fastmcp import FastMCP
from app.services.image_search_service import get_image_search_service
import json

def register_image_search(mcp: FastMCP):
    """注册图像搜索工具"""

    @mcp.tool
    async def image_search(
        image_data: str,
        limit: int = 20,
        threshold: float = 0.7
    ) -> str:
        """
        基于CN-CLIP模型的图像搜索，支持图片查找相似内容。

        上传图片后，将搜索与该图片相似的文件。
        支持查找相似图片、包含相似元素的文档等。

        Args:
            image_data: Base64 编码的图片数据
            limit: 返回结果数量（1-100，默认20）
            threshold: 相似度阈值（0.0-1.0，默认0.7）

        Returns:
            JSON 格式的搜索结果
        """
        # 解码图片数据
        image_bytes = base64.b64decode(image_data)
        image_file = BytesIO(image_bytes)

        # 执行图像搜索
        service = get_image_search_service()
        result = await service.search(
            image=image_file,
            limit=limit,
            threshold=threshold
        )

        # 格式化结果
        return json.dumps(_format_image_result(result), ensure_ascii=False, indent=2)


def _format_image_result(result: dict) -> dict:
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

### 3.6 混合搜索工具

```python
# backend/app/mcp/tools/hybrid_search.py
from typing import Optional, List
from fastmcp import FastMCP
from app.services.chunk_search_service import get_chunk_search_service
from app.models.schemas import SearchType
import json

def register_hybrid_search(mcp: FastMCP):
    """注册混合搜索工具"""

    @mcp.tool
    async def hybrid_search(
        query: str,
        limit: int = 20,
        threshold: float = 0.7,
        file_types: Optional[List[str]] = None
    ) -> str:
        """
        混合搜索，结合语义搜索和全文搜索的优势。

        同时使用BGE-M3语义理解和Whoosh精确匹配，
        通过RRF（Reciprocal Rank Fusion）算法融合结果，
        提供更全面的搜索结果。

        Args:
            query: 搜索查询词（1-500字符）
            limit: 返回结果数量（1-100，默认20）
            threshold: 相似度阈值（0.0-1.0，默认0.7）
            file_types: 文件类型过滤（可选）

        Returns:
            JSON 格式的搜索结果
        """
        from app.mcp.tools.semantic_search import _format_search_result

        service = get_chunk_search_service()
        result = await service.search(
            query=query,
            search_type=SearchType.HYBRID,
            limit=limit,
            offset=0,
            threshold=threshold,
            file_types=file_types
        )

        return json.dumps(_format_search_result(result), ensure_ascii=False, indent=2)
```

### 3.7 FastAPI 集成（fastmcp 方案）

```python
# backend/main.py（修改部分）
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.logging_config import get_logger, logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # ... 现有初始化代码 ...

    # ========== FastMCP 服务器初始化 ==========
    logger.info("初始化 FastMCP 服务器...")
    try:
        from app.core.config import get_settings
        settings = get_settings()

        if settings.mcp_sse_enabled:
            # 导入并创建 FastMCP 服务器
            from app.mcp.server import create_mcp_server
            mcp_server = create_mcp_server()

            # 获取 ASGI 应用并挂载到 FastAPI
            # fastmcp 内置支持通过 http_app() 获取 ASGI 应用
            mcp_asgi_app = mcp_server.http_app(path="/mcp/sse")

            # 将 MCP ASGI 应用挂载到主应用
            app.state.mcp_asgi_app = mcp_asgi_app
            app.state.mcp_server = mcp_server

            logger.info("✅ FastMCP 服务器初始化完成")
            logger.info(f"📡 SSE 端点: http://127.0.0.1:8000/mcp/sse")
        else:
            app.state.mcp_asgi_app = None
            app.state.mcp_server = None
            logger.info("FastMCP 服务器未启用")
    except Exception as e:
        logger.error(f"❌ FastMCP 服务器初始化失败: {str(e)}")
        app.state.mcp_asgi_app = None
        app.state.mcp_server = None
    # =====================================

    yield

    # 关闭时清理...
    # ... 现有清理代码 ...

# 创建 FastAPI 应用
from fastapi import Request
from fastapi.responses import Response

app = FastAPI(
    title="小遥搜索 API",
    lifespan=lifespan
)

# ========== FastMCP SSE 端点（方式一：直接挂载）==========
# 通过 Starlette Mount 挂载 FastMCP ASGI 应用
from starlette.routing import Mount

# 方式一：使用 Starlette Mount（推荐）
# 在应用创建时挂载
if app.state.mcp_asgi_app:
    app.mount("/mcp", app.state.mcp_asgi_app)
    logger.info("✅ FastMCP SSE 端点已挂载到 /mcp")

# 方式二：手动路由（如果需要更多控制）
@app.api_route("/mcp/sse", methods=["GET", "POST", "OPTIONS"])
async def mcp_sse_proxy(request: Request):
    """
    FastMCP SSE 传输端点代理

    Claude Desktop 通过此端点连接小遥搜索
    示例 URL: http://127.0.0.1:8000/mcp/sse

    注意：fastmcp 自动处理 SSE 连接，此处仅作为代理
    """
    if not app.state.mcp_asgi_app:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="FastMCP 服务器未启用")

    # 代理请求到 FastMCP ASGI 应用
    return await app.state.mcp_asgi_app(request.scope, request.receive, request._send)
# =====================================================

# MCP 健康检查端点
@app.get("/mcp/health")
async def mcp_health():
    """FastMCP 服务器健康检查"""
    # fastmcp 自动暴露工具列表
    tools = []
    if app.state.mcp_server:
        # FastMCP 通过 mcp._tool_manager 获取工具列表
        tools = list(app.state.mcp_server._tool_manager._tools.keys())

    return {
        "status": "enabled" if app.state.mcp_server else "disabled",
        "server": "fastmcp",
        "tools_count": len(tools),
        "tools": tools
    }

# ... 其他路由 ...
```

**fastmcp 集成优势：**
- ✅ **一行代码挂载**：`mcp.http_app(path="/mcp/sse")` 自动生成 ASGI 应用
- ✅ **自动 SSE 处理**：无需手动实现 SSE 传输层
- ✅ **标准 FastAPI 集成**：使用 `app.mount()` 挂载
- ✅ **自动工具发现**：fastmcp 自动扫描所有 `@mcp.tool` 装饰器

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
# MCP 协议支持（使用 fastmcp）
fastmcp>=0.4.0

# SSE 传输支持（fastmcp 内置）
# uvicorn[standard]  # 已存在
```

**fastmcp vs mcp-python-sdk 对比：**
| 特性 | fastmcp | mcp-python-sdk |
|------|---------|----------------|
| 代码量 | ~200 行 | ~600 行 |
| 工具定义 | `@mcp.tool` 装饰器 | 继承 `BaseTool` 类 |
| Schema 生成 | 自动从类型提示 | 手动定义 `inputSchema` |
| SSE 支持 | 内置 `http_app()` | 需手动实现 |
| FastAPI 集成 | `app.mount()` 一行挂载 | 需自定义 SSE 端点 |
| 维护状态 | PrefectHQ 活跃维护 | Anthropic 官方 |

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

**文档版本**：v2.0（采用 fastmcp）
**创建时间**：2026-03-11
**最后更新**：2026-03-12（改用 fastmcp 实现）
**维护者**：AI助手

> **使用说明**：
> 1. 本技术方案基于 FastAPI 集成 + fastmcp 方案（2026-03-12 更新）
> 2. fastmcp 相比 mcp-python-sdk 代码量减少约 60%
> 3. 使用装饰器模式 (`@mcp.tool`) 定义工具，自动 Schema 生成
> 4. FastAPI 集成通过 `mcp.http_app(path)` 一行代码挂载
> 5. 与现有代码保持一致，复用搜索服务
> 6. 所有代码示例使用中文注释
> 7. 配置参数支持环境变量覆盖

> **技术变更说明**（2026-03-12）：
> - **框架选择**：从 mcp-python-sdk 迁移到 fastmcp
> - **主要优势**：代码更简洁、自动 Schema 生成、原生 FastAPI 集成
> - **关键变化**：
>   - 工具定义：`class BaseTool` → `@mcp.tool` 装饰器
>   - 参数验证：手动 `inputSchema` → 自动类型提示生成
>   - SSE 传输：手动实现 → `mcp.http_app()` 内置
>   - FastAPI 集成：自定义端点 → `app.mount()` 挂载
