# MCP 服务器支持 - 实施步骤（fastmcp 版本）

> **文档类型**：实施步骤
> **特性状态**：开发中
> **创建时间**：2026-03-12
> **预计工期**：3 天（24 小时）
> **关联文档**：[MCP 技术方案](./mcp-03-技术方案.md) | [MCP 实施方案](./mcp-实施方案.md)

---

## 📋 实施概览

| 阶段 | 任务 | 预计时间 | 优先级 |
|------|------|----------|--------|
| 1️⃣ 环境准备 | 依赖安装、目录创建 | 1 小时 | P0 |
| 2️⃣ 配置管理 | MCP 配置实现 | 1 小时 | P0 |
| 3️⃣ FastMCP 服务器 | 服务器主类、工具注册 | 2 小时 | P0 |
| 4️⃣ 搜索工具实现 | 5 个搜索工具 | 10 小时 | P0 |
| 5️⃣ FastAPI 集成 | SSE 端点、生命周期 | 3 小时 | P0 |
| 6️⃣ 测试验证 | 功能测试、性能测试 | 7 小时 | P1 |
| **总计** | | **24 小时（3 天）** | |

---

## 阶段 1：环境准备（1 小时）

### 1.1 安装依赖

**修改文件**：`backend/requirements.txt`

```bash
# ========== MCP 协议支持 ==========
# 使用 fastmcp 框架（PrefectHQ 维护）
fastmcp>=0.4.0
# =====================================
```

**执行安装**：

```bash
cd backend
pip install fastmcp>=0.4.0
```

### 1.2 创建目录结构

**执行命令**：

```bash
# 创建 MCP 模块目录
mkdir -p backend/app/mcp/tools

# 创建空的 __init__.py 文件
touch backend/app/mcp/__init__.py
touch backend/app/mcp/tools/__init__.py
```

**目录结构**：

```
backend/app/mcp/
├── __init__.py
├── server.py              # FastMCP 服务器实例
├── config.py              # MCP 配置管理
└── tools/
    ├── __init__.py
    ├── semantic_search.py  # 语义搜索工具
    ├── fulltext_search.py  # 全文搜索工具
    ├── voice_search.py     # 语音搜索工具
    ├── image_search.py     # 图像搜索工具
    └── hybrid_search.py    # 混合搜索工具
```

---

## 阶段 2：配置管理（1 小时）

### 2.1 创建 MCP 配置类

**新建文件**：`backend/app/mcp/config.py`

```python
"""
MCP 服务器配置管理
"""
from pydantic import BaseModel, Field
from typing import Optional


class MCPConfig(BaseModel):
    """MCP 服务器配置"""

    # 服务器配置
    server_name: str = Field(default="xiaoyao-search", description="服务器名称")
    server_version: str = Field(default="1.0.0", description="服务器版本")

    # SSE 配置
    sse_enabled: bool = Field(default=True, description="是否启用 SSE 传输")
    sse_path: str = Field(default="/mcp/sse", description="SSE 端点路径")

    # 搜索配置
    default_limit: int = Field(default=20, ge=1, le=100, description="默认结果数量")
    default_threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="默认相似度阈值")

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

### 2.2 更新全局配置

**修改文件**：`backend/app/core/config.py`

在 `Settings` 类中添加：

```python
class Settings(BaseSettings):
    # ... 现有配置 ...

    # MCP 配置
    mcp_sse_enabled: bool = Field(default=True, description="是否启用 MCP SSE 服务")
    mcp_default_limit: int = Field(default=20, ge=1, le=100, description="MCP 默认结果数量")
    mcp_default_threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="MCP 默认相似度阈值")

    class Config:
        env_prefix = ""
```

### 2.3 配置环境变量

**修改文件**：`backend/.env`

```bash
# ========== MCP 服务器配置 ==========
MCP_SSE_ENABLED=true
MCP_SERVER_NAME=xiaoyao-search
MCP_SERVER_VERSION=1.0.0
MCP_DEFAULT_LIMIT=20
MCP_DEFAULT_THRESHOLD=0.5
MCP_VOICE_ENABLED=true
MCP_VOICE_MAX_DURATION=30
MCP_LOG_LEVEL=INFO
# =====================================
```

---

## 阶段 3：FastMCP 服务器（2 小时）

### 3.1 创建 FastMCP 服务器主类

**新建文件**：`backend/app/mcp/server.py`

```python
"""
FastMCP 服务器主类
"""
from fastmcp import FastMCP
from app.mcp.config import get_mcp_config
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def create_mcp_server() -> FastMCP:
    """
    创建 FastMCP 服务器实例

    Returns:
        FastMCP: FastMCP 服务器实例
    """
    config = get_mcp_config()

    # 创建 FastMCP 实例
    mcp = FastMCP(
        name=config.server_name,
        version=config.server_version
    )

    logger.info(f"✅ FastMCP 服务器初始化完成: {config.server_name}")
    return mcp


def register_mcp_tools(mcp: FastMCP):
    """
    注册所有 MCP 工具

    Args:
        mcp: FastMCP 服务器实例
    """
    from app.mcp.tools.semantic_search import register_semantic_search
    from app.mcp.tools.fulltext_search import register_fulltext_search
    from app.mcp.tools.voice_search import register_voice_search
    from app.mcp.tools.image_search import register_image_search
    from app.mcp.tools.hybrid_search import register_hybrid_search

    # 注册所有搜索工具
    register_semantic_search(mcp)
    register_fulltext_search(mcp)
    register_voice_search(mcp)
    register_image_search(mcp)
    register_hybrid_search(mcp)

    logger.info("✅ 所有 MCP 工具注册完成")
```

### 3.2 创建工具基类辅助函数

**新建文件**：`backend/app/mcp/tools/__init__.py`

```python
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
```

---

## 阶段 4：搜索工具实现（10 小时）

### 4.1 语义搜索工具

**新建文件**：`backend/app/mcp/tools/semantic_search.py`

```python
"""
语义搜索工具 - fastmcp 实现
"""
from typing import Optional, List
from fastmcp import FastMCP
from app.services.chunk_search_service import get_chunk_search_service
from app.models.schemas import SearchType
from app.mcp.tools import format_search_result
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def register_semantic_search(mcp: FastMCP):
    """注册语义搜索工具到 FastMCP"""

    @mcp.tool
    async def semantic_search(
        query: str,
        limit: int = 20,
        threshold: float = 0.5,
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

        logger.info(f"执行语义搜索: query={query}, limit={limit}")

        # 执行搜索（直接调用现有服务）
        service = get_chunk_search_service()
        result = await service.search(
            query=query,
            search_type=SearchType.SEMANTIC,
            limit=limit,
            offset=0,
            threshold=threshold,
            file_types=file_types
        )

        return format_search_result(result)
```

### 4.2 全文搜索工具

**新建文件**：`backend/app/mcp/tools/fulltext_search.py`

```python
"""
全文搜索工具 - fastmcp 实现
"""
from typing import Optional, List
from fastmcp import FastMCP
from app.services.chunk_search_service import get_chunk_search_service
from app.models.schemas import SearchType
from app.mcp.tools import format_search_result
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def register_fulltext_search(mcp: FastMCP):
    """注册全文搜索工具到 FastMCP"""

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
        if not query or len(query) > 500:
            raise ValueError("query 必须为1-500字符")
        if not 1 <= limit <= 100:
            raise ValueError("limit 必须为1-100")

        logger.info(f"执行全文搜索: query={query}, limit={limit}")

        service = get_chunk_search_service()
        result = await service.search(
            query=query,
            search_type=SearchType.FULLTEXT,
            limit=limit,
            offset=0,
            file_types=file_types
        )

        return format_search_result(result)
```

### 4.3 语音搜索工具

**新建文件**：`backend/app/mcp/tools/voice_search.py`

```python
"""
语音搜索工具 - fastmcp 实现
"""
import base64
import io
from typing import Optional, List
from fastmcp import FastMCP
from app.services.chunk_search_service import get_chunk_search_service
from app.services.ai_model_manager import ai_model_service
from app.models.schemas import SearchType
from app.mcp.tools import format_search_result
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def register_voice_search(mcp: FastMCP):
    """注册语音搜索工具到 FastMCP"""

    @mcp.tool
    async def voice_search(
        audio_data: str,
        search_type: str = "semantic",
        limit: int = 20,
        threshold: float = 0.5,
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

        logger.info(f"语音识别结果: {query}, 搜索类型: {search_type}")

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
        formatted = json.loads(format_search_result(result))
        formatted["transcription"] = {
            "text": query,
            "language": transcription.get("language"),
            "duration": transcription.get("duration")
        }

        return json.dumps(formatted, ensure_ascii=False, indent=2)
```

### 4.4 图像搜索工具

**新建文件**：`backend/app/mcp/tools/image_search.py`

```python
"""
图像搜索工具 - fastmcp 实现
"""
import base64
from io import BytesIO
from fastmcp import FastMCP
from app.services.image_search_service import get_image_search_service
from app.mcp.tools import format_image_result
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def register_image_search(mcp: FastMCP):
    """注册图像搜索工具到 FastMCP"""

    @mcp.tool
    async def image_search(
        image_data: str,
        limit: int = 20,
        threshold: float = 0.5
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

        logger.info(f"执行图像搜索: limit={limit}, threshold={threshold}")

        # 执行图像搜索
        service = get_image_search_service()
        result = await service.search(
            image=image_file,
            limit=limit,
            threshold=threshold
        )

        return format_image_result(result)
```

### 4.5 混合搜索工具

**新建文件**：`backend/app/mcp/tools/hybrid_search.py`

```python
"""
混合搜索工具 - fastmcp 实现
"""
from typing import Optional, List
from fastmcp import FastMCP
from app.services.chunk_search_service import get_chunk_search_service
from app.models.schemas import SearchType
from app.mcp.tools import format_search_result
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def register_hybrid_search(mcp: FastMCP):
    """注册混合搜索工具到 FastMCP"""

    @mcp.tool
    async def hybrid_search(
        query: str,
        limit: int = 20,
        threshold: float = 0.5,
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
        if not query or len(query) > 500:
            raise ValueError("query 必须为1-500字符")
        if not 1 <= limit <= 100:
            raise ValueError("limit 必须为1-100")
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold 必须为0.0-1.0")

        logger.info(f"执行混合搜索: query={query}, limit={limit}")

        service = get_chunk_search_service()
        result = await service.search(
            query=query,
            search_type=SearchType.HYBRID,
            limit=limit,
            offset=0,
            threshold=threshold,
            file_types=file_types
        )

        return format_search_result(result)
```

---

## 阶段 5：FastAPI 集成（3 小时）

### 5.1 修改 FastAPI 主入口

**修改文件**：`backend/main.py`

在文件顶部添加导入：

```python
# 在现有导入后添加
from app.mcp.server import create_mcp_server, register_mcp_tools
from app.mcp.config import get_mcp_config
```

### 5.2 更新生命周期管理

**修改文件**：`backend/main.py`

在 `lifespan` 函数中添加 MCP 服务器初始化：

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # ========== 现有初始化代码 ==========
    logger.info("初始化应用...")

    # 现有的 AI 模型初始化、搜索服务初始化等代码...

    logger.info("✅ 应用初始化完成")

    # ========== FastMCP 服务器初始化 ==========
    logger.info("初始化 FastMCP 服务器...")
    try:
        from app.core.config import get_settings
        settings = get_settings()

        if settings.mcp_sse_enabled:
            # 创建 FastMCP 服务器实例
            mcp_server = create_mcp_server()

            # 注册所有工具
            register_mcp_tools(mcp_server)

            # 获取 ASGI 应用
            mcp_asgi_app = mcp_server.http_app(path="/mcp/sse")

            # 挂载到 FastAPI
            app.mount("/mcp", mcp_asgi_app)

            # 保存到 app.state
            app.state.mcp_server = mcp_server
            app.state.mcp_asgi_app = mcp_asgi_app

            logger.info("✅ FastMCP 服务器初始化完成")
            logger.info(f"📡 SSE 端点: http://127.0.0.1:8000/mcp")
        else:
            app.state.mcp_server = None
            app.state.mcp_asgi_app = None
            logger.info("FastMCP 服务器未启用")
    except Exception as e:
        logger.error(f"❌ FastMCP 服务器初始化失败: {str(e)}")
        app.state.mcp_server = None
        app.state.mcp_asgi_app = None
    # =====================================

    yield

    # ========== 关闭时清理 ==========
    # 现有的清理代码...
    logger.info("应用关闭")
```

### 5.3 添加健康检查端点

**修改文件**：`backend/main.py`

```python
from fastapi import HTTPException

# MCP 健康检查端点
@app.get("/mcp/health")
async def mcp_health():
    """FastMCP 服务器健康检查"""
    tools = []
    if app.state.mcp_server:
        # FastMCP 通过 _tool_manager 获取工具列表
        tools = list(app.state.mcp_server._tool_manager._tools.keys())

    return {
        "status": "enabled" if app.state.mcp_server else "disabled",
        "server": "fastmcp",
        "tools_count": len(tools),
        "tools": tools
    }
```

---

## 阶段 6：测试验证（7 小时）

### 6.1 单元测试

**新建文件**：`tests/test_mcp_tools.py`

```python
"""
MCP 工具单元测试
"""
import pytest
import json
from app.mcp.server import create_mcp_server, register_mcp_tools
from app.mcp.config import MCPConfig


@pytest.fixture
def mcp_server():
    """创建 FastMCP 服务器实例"""
    config = MCPConfig()
    mcp = create_mcp_server()
    register_mcp_tools(mcp)
    return mcp


class TestSemanticSearch:
    """语义搜索工具测试"""

    @pytest.mark.asyncio
    async def test_execute_success(self, mcp_server, mock_search_service):
        """测试成功执行"""
        # 模拟搜索结果
        mock_search_service.search.return_value = {
            'data': {
                'total': 1,
                'search_time': 0.1,
                'results': [{
                    'file_name': 'test.pdf',
                    'file_path': '/path/to/test.pdf',
                    'relevance_score': 0.9
                }]
            }
        }

        # 调用工具
        result = await mcp_server._tool_manager._tools['semantic_search'](
            query="测试查询",
            limit=10,
            threshold=0.5
        )

        # 验证结果
        result_dict = json.loads(result)
        assert result_dict['total'] == 1
        assert len(result_dict['results']) == 1

    @pytest.mark.asyncio
    async def test_invalid_query(self, mcp_server):
        """测试无效查询"""
        with pytest.raises(ValueError, match="query 必须为1-500字符"):
            await mcp_server._tool_manager._tools['semantic_search'](
                query="",  # 空查询
                limit=10
            )


class TestFulltextSearch:
    """全文搜索工具测试"""

    @pytest.mark.asyncio
    async def test_execute_success(self, mcp_server, mock_search_service):
        """测试成功执行"""
        # 模拟搜索结果
        mock_search_service.search.return_value = {
            'data': {
                'total': 1,
                'search_time': 0.05,
                'results': [{
                    'file_name': 'test.txt',
                    'file_path': '/path/to/test.txt',
                    'relevance_score': 1.0
                }]
            }
        }

        result = await mcp_server._tool_manager._tools['fulltext_search'](
            query="关键词",
            limit=20
        )

        result_dict = json.loads(result)
        assert result_dict['total'] == 1
```

### 6.2 集成测试

**新建文件**：`tests/test_mcp_integration.py`

```python
"""
MCP 集成测试
"""
import pytest
from httpx import AsyncClient
from app.main import app


class TestMCPIntegration:
    """MCP 集成测试"""

    @pytest.fixture
    async def client(self):
        """创建测试客户端"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        """测试健康检查端点"""
        response = await client.get("/mcp/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] in ["enabled", "disabled"]
        assert data["server"] == "fastmcp"

    @pytest.mark.asyncio
    async def test_sse_endpoint(self, client):
        """测试 SSE 端点"""
        response = await client.get("/mcp/sse")
        # SSE 端点应该返回 200 或需要特殊处理
        assert response.status_code in [200, 403]  # 403 如果来源检查失败
```

### 6.3 端到端测试

**测试流程**：

1. **启动 FastAPI 服务器**
   ```bash
   cd backend
   python main.py
   ```

2. **检查健康状态**
   ```bash
   curl http://127.0.0.1:8000/mcp/health
   ```

   预期响应：
   ```json
   {
     "status": "enabled",
     "server": "fastmcp",
     "tools_count": 5,
     "tools": ["semantic_search", "fulltext_search", "voice_search", "image_search", "hybrid_search"]
   }
   ```

3. **配置 Claude Desktop**

   编辑 `~/.config/Claude/claude_desktop_config.json`：

   ```json
   {
     "mcpServers": {
       "xiaoyao-search": {
         "url": "http://127.0.0.1:8000/mcp"
       }
     }
   }
   ```

4. **重启 Claude Desktop**

5. **在 Claude Desktop 中测试**

   输入测试查询：
   - "使用语义搜索查找关于机器学习的文档"
   - "使用全文搜索查找关键词 FastAPI"
   - "使用混合搜索查找 Python 异步编程"

### 6.4 性能测试

**测试脚本**：`tests/test_mcp_performance.py`

```python
"""
MCP 性能测试
"""
import pytest
import time
from app.mcp.server import create_mcp_server, register_mcp_tools


@pytest.mark.asyncio
async def test_semantic_search_performance():
    """测试语义搜索性能"""
    mcp = create_mcp_server()
    register_mcp_tools(mcp)

    # 记录开始时间
    start_time = time.time()

    # 执行搜索
    result = await mcp._tool_manager._tools['semantic_search'](
        query="机器学习算法优化",
        limit=20,
        threshold=0.5
    )

    # 计算耗时
    duration = time.time() - start_time

    # 验证性能
    assert duration < 2.0, f"语义搜索耗时 {duration:.2f}s 超过 2s 阈值"


@pytest.mark.asyncio
async def test_fulltext_search_performance():
    """测试全文搜索性能"""
    mcp = create_mcp_server()
    register_mcp_tools(mcp)

    start_time = time.time()

    result = await mcp._tool_manager._tools['fulltext_search'](
        query="FastAPI",
        limit=20
    )

    duration = time.time() - start_time

    assert duration < 1.0, f"全文搜索耗时 {duration:.2f}s 超过 1s 阈值"
```

---

## 阶段 7：部署与验证（可选，3 小时）

### 7.1 构建前端应用

```bash
cd frontend
npm run build
```

### 7.2 启动完整应用

```bash
# 终端 1：启动后端
cd backend
python main.py

# 终端 2：启动前端
cd frontend
npm run electron:dev
```

### 7.3 验证清单

- [ ] 后端启动成功，无错误日志
- [ ] 访问 `http://127.0.0.1:8000/mcp/health` 返回正确状态
- [ ] SSE 端点 `http://127.0.0.1:8000/mcp` 可访问
- [ ] Claude Desktop 可连接到 MCP 服务器
- [ ] Claude Desktop 可调用 `semantic_search` 工具
- [ ] Claude Desktop 可调用 `fulltext_search` 工具
- [ ] Claude Desktop 可调用 `voice_search` 工具
- [ ] Claude Desktop 可调用 `image_search` 工具
- [ ] Claude Desktop 可调用 `hybrid_search` 工具
- [ ] 所有工具返回结果格式正确
- [ ] 搜索结果与 Electron 前端一致

---

## 📊 完成检查清单

### 代码实现

- [ ] 依赖已添加到 `requirements.txt`
- [ ] MCP 配置类已实现
- [ ] FastMCP 服务器主类已实现
- [ ] 语义搜索工具已实现
- [ ] 全文搜索工具已实现
- [ ] 语音搜索工具已实现
- [ ] 图像搜索工具已实现
- [ ] 混合搜索工具已实现
- [ ] FastAPI 集成已完成
- [ ] 健康检查端点已添加

### 测试验证

- [ ] 单元测试已编写
- [ ] 集成测试已编写
- [ ] 性能测试已通过
- [ ] Claude Desktop 连接成功
- [ ] 所有工具可正常调用
- [ ] 搜索结果正确返回

### 文档更新

- [ ] 技术方案文档已更新
- [ ] 实施方案文档已更新
- [ ] 接口文档已更新
- [ ] 配置说明已更新

---

## 🔧 故障排查

### 常见问题

**1. SSE 端点无法访问**

```bash
# 检查端口是否被占用
netstat -ano | findstr :8000

# 检查防火墙设置
# Windows: 允许 Python 通过防火墙
```

**2. Claude Desktop 无法连接**

- 检查配置文件路径是否正确
- 确认 FastAPI 服务正在运行
- 查看 Claude Desktop 日志：`Help` → `View Logs`

**3. 工具调用失败**

- 检查搜索服务是否已初始化
- 查看 FastAPI 日志输出
- 确认 AI 模型已加载

**4. fastmcp 导入错误**

```bash
# 重新安装 fastmcp
pip install --upgrade fastmcp

# 验证安装
python -c "from fastmcp import FastMCP; print('OK')"
```

---

## 📚 相关文档

- [MCP PRD](./mcp-01-prd.md) - 产品需求文档
- [MCP 技术方案](./mcp-03-技术方案.md) - 技术实现方案（v2.0 采用 fastmcp）
- [MCP 实施方案](./mcp-实施方案.md) - 实施方案（v2.0 采用 fastmcp）
- [MCP 任务清单](./mcp-04-开发任务清单.md) - 任务分解
- [MCP 开发排期表](./mcp-05-开发排期表.md) - 时间规划
- [架构决策 AD-20260311-01](../../架构决策/AD-20260311-01-MCP服务器架构选择.md) - 架构决策文档

---

**文档版本**：v1.0
**创建时间**：2026-03-12
**预计工期**：3 天（24 小时）
**维护者**：AI助手
