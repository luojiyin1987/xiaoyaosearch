# 特性PRD：MCP 服务器支持

> **文档类型**：特性增量PRD
> **基础版本**：基于 [主PRD文档](../../01-prd.md)
> **特性状态**：规划中
> **创建时间**：2026-03-11
> **最后更新**：2026-03-11

---

## 1. 特性概述

### 1.1 定位（一句话）

为小遥搜索添加 Model Context Protocol (MCP) 服务器能力，使 Claude Desktop 等 AI 应用能够连接小遥搜索进行本地文件智能搜索。

### 1.2 背景与动机

- **用户痛点**：
  - 痛点1：Claude Desktop 用户无法直接访问本地文件，需要在 AI 对话和文件系统之间来回切换
  - 痛点2：知识工作者希望 AI 能够理解和搜索本地文档，但缺乏安全可靠的连接方式
  - 痛点3：现有本地搜索工具与 AI 应用割裂，无法形成智能工作流

- **业务价值**：
  - 连接 Claude 生态：通过 MCP 协议无缝接入 Claude Desktop，扩大产品影响力
  - 提升用户粘性：用户依赖小遥搜索作为本地数据源，增强平台依赖
  - 扩展 AI 能力：让 AI 应用能够访问和理解用户的本地知识库
  - 建立技术壁垒：率先支持 MCP 协议，抢占本地搜索与 AI 融合的市场先机

- **技术必要性**：
  - MCP 是 Anthropic 推出的开源协议，已成为 AI 应用与本地数据源连接的事实标准
  - 现有搜索服务架构完善，通过适配器模式可快速集成 MCP 协议
  - 集成到 FastAPI 进程，共享 AI 模型和搜索服务，避免重复加载，节省内存

### 1.3 目标用户

- **主要用户**：
  - Claude Desktop 重度用户：需要 AI 协助处理本地文档的知识工作者
  - 开发者和技术人员：希望 AI 能够理解代码库和技术文档
  - 内容创作者：需要 AI 协助管理和检索创作素材
  - 研究人员：需要 AI 协助分析研究资料和文献

- **使用场景**：
  - 用户在 Claude Desktop 中询问"我的项目中有哪些关于异步编程的文档？"
  - 用户让 AI 分析"我之前保存的产品设计稿在哪里？"
  - 用户通过图片搜索找到包含相似图表的文档

### 1.4 与主版本的关系

- **依赖关系**：
  - 依赖主 PRD 中的搜索服务：语义搜索、全文搜索、图搜图、混合搜索（P1）
  - 依赖现有的 AI 模型管理：BGE-M3、FasterWhisper、CN-CLIP
  - 依赖现有索引系统：Faiss 向量索引、Whoosh 全文索引

- **影响范围**：
  - 后端：在现有 FastAPI 服务中集成 MCP 服务器，添加 SSE 端点
  - 前端：无变更（Claude Desktop 直接通过 SSE 连接）
  - 数据库：无变更（复用现有 SQLite 数据库和索引文件）

---

## 2. 增量需求（与主PRD的差异）

> **说明**：本章节重点突出与主PRD的差异，避免重复主PRD中已定义的内容

### 2.1 功能变更清单

> **说明**：本特性聚焦 MCP 搜索核心 MVP，仅包含 P0 和 P1 级别的搜索工具

#### 新增功能

| 功能点 | 优先级 | 影响范围 | 兼容性 | 说明 |
|-------|-------|---------|-------|------|
| MCP 服务器主类 | P0 | 后端 | N/A | 实现 MCP 协议标准的服务器类，基于 mcp-python-sdk |
| SSE 传输端点 | P0 | 后端 | N/A | 在 FastAPI 中添加 MCP SSE 端点 |
| 语义搜索工具 | P0 | 后端 | N/A | 暴露语义搜索能力作为 MCP Tool |
| 全文搜索工具 | P0 | 后端 | N/A | 暴露全文搜索能力作为 MCP Tool |
| 语音搜索工具 | P1 | 后端 | N/A | 暴露语音搜索能力作为 MCP Tool，支持语音转文字后搜索 |
| 图像搜索工具 | P1 | 后端 | N/A | 暴露图搜图能力作为 MCP Tool |
| 混合搜索工具 | P1 | 后端 | N/A | 暴露混合搜索能力作为 MCP Tool |
| 搜索服务适配器 | P0 | 后端 | N/A | 适配现有搜索服务为 MCP 工具调用 |

#### 修改功能

| 功能点 | 原有实现 | 修改方案 | 影响范围 | 兼容性 |
|-------|---------|---------|---------|-------|
| FastAPI 主入口 | 单一服务 | 集成 MCP 服务器，添加 SSE 端点 | 后端 | 是，不影响现有功能 |

---

## 3. 用户故事（增量场景）

> **说明**：只记录新增场景或重大变更的场景

### 场景1：通过 Claude 搜索本地文档

- 作为 **知识工作者**
- 我想要 **在 Claude Desktop 中询问关于我本地文档的问题**
- 以便于 **AI 能够直接搜索和理解我的本地知识库，提供智能回答**

**验收标准**：
- [ ] Claude Desktop 能够成功连接小遥搜索 MCP 服务器
- [ ] 可以通过自然语言查询本地文档
- [ ] 搜索结果包含文件名、路径、相关度分数和预览文本
- [ ] AI 能够基于搜索结果提供有价值的回答

### 场景2：通过 Claude 进行语义搜索

- 作为 **开发者**
- 我想要 **让 Claude 理解我的技术查询意图并搜索相关文档**
- 以便于 **快速找到相关的代码文件、技术文档和笔记**

**验收标准**：
- [ ] Claude 能够调用语义搜索工具
- [ ] 支持自然语言查询（如"异步编程的最佳实践"）
- [ ] 返回按相关度排序的结果
- [ ] 能够过滤文件类型（文档、代码、图片等）

### 场景3：通过 Claude 搜索图片内容

- 作为 **设计师**
- 我想要 **上传图片让 Claude 在本地文件中找到相似的视觉内容**
- 以便于 **定位相关的设计素材、参考图和文档**

**验收标准**：
- [ ] Claude 能够调用图像搜索工具
- [ ] 支持图片输入（PNG、JPG 格式）
- [ ] 返回相似的图片和包含相关内容的文档
- [ ] 能够提供图片预览

---

## 4. 核心流程（增量部分）

### 4.1 新增流程

#### 4.1.1 FastAPI 启动流程（集成 MCP）

```
FastAPI 启动
  ↓
加载现有服务（数据库、AI模型、插件等）
  ↓
初始化 MCP 服务器实例
  ↓
注册搜索工具（semantic_search, fulltext_search, voice_search, image_search, hybrid_search）
  ↓
添加 SSE 传输端点到 FastAPI 路由
  ↓
FastAPI 服务启动完成（同时支持 HTTP API 和 SSE）
  ↓
等待 Claude Desktop 通过 SSE 连接
```

#### 4.1.2 Claude 搜索流程

```
用户在 Claude Desktop 中输入查询
  ↓
Claude 分析用户意图，选择合适的 MCP 工具
  ↓
Claude 通过 SSE 连接调用小遥搜索 MCP 工具（如 semantic_search）
  ↓
FastAPI 接收 SSE 请求，路由到 MCP 服务器处理
  ↓
MCP 服务器通过 SearchAdapter 调用现有搜索服务
  ↓
搜索服务执行查询（Faiss/Whoosh）
  ↓
MCP 服务器格式化搜索结果为 JSON
  ↓
通过 SSE 返回结果给 Claude Desktop
  ↓
Claude 基于搜索结果生成智能回答
  ↓
展示给用户
```

### 4.2 修改流程

> **说明**：本特性为纯增量功能，不涉及修改现有流程

---

## 5. 详细设计

### 5.1 后端设计

#### 模块结构

| 模块路径 | 类型 | 说明 |
|---------|------|------|
| `backend/app/mcp/__init__.py` | 新增 | MCP 模块初始化 |
| `backend/app/mcp/server.py` | 新增 | MCP 服务器主类 |
| `backend/app/mcp/config.py` | 新增 | MCP 配置管理 |
| `backend/app/mcp/transport.py` | 新增 | SSE 传输层实现 |
| `backend/app/mcp/tools/__init__.py` | 新增 | 工具模块初始化 |
| `backend/app/mcp/tools/semantic_search.py` | 新增 | 语义搜索工具 |
| `backend/app/mcp/tools/fulltext_search.py` | 新增 | 全文搜索工具 |
| `backend/app/mcp/tools/voice_search.py` | 新增 | 语音搜索工具 |
| `backend/app/mcp/tools/image_search.py` | 新增 | 图像搜索工具 |
| `backend/app/mcp/tools/hybrid_search.py` | 新增 | 混合搜索工具 |
| `backend/app/mcp/adapters/__init__.py` | 新增 | 适配器模块初始化 |
| `backend/app/mcp/adapters/search_adapter.py` | 新增 | 搜索服务适配器 |
| `backend/main.py` | 修改 | 集成 MCP 服务器，添加 SSE 端点 |

#### MCP 工具设计

**工具1：semantic_search（语义搜索）**

```python
Tool(
    name="semantic_search",
    description="基于BGE-M3模型的语义搜索，支持自然语言查询理解。适合用自然语言描述的查询，如'关于机器学习算法优化的方法'。",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "搜索查询词（1-500字符）"
            },
            "limit": {
                "type": "integer",
                "description": "返回结果数量（1-100）",
                "default": 20
            },
            "threshold": {
                "type": "number",
                "description": "相似度阈值（0.0-1.0）",
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
```

**工具2：fulltext_search（全文搜索）**

```python
Tool(
    name="fulltext_search",
    description="基于Whoosh的全文搜索，支持精确关键词匹配和中文分词。适合查找特定术语、代码片段或精确短语。",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "搜索查询词（1-500字符）"
            },
            "limit": {
                "type": "integer",
                "description": "返回结果数量（1-100）",
                "default": 20
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
```

**工具3：voice_search（语音搜索）**

```python
Tool(
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
                "description": "搜索类型（semantic/fulltext/hybrid）",
                "enum": ["semantic", "fulltext", "hybrid"],
                "default": "semantic"
            },
            "limit": {
                "type": "integer",
                "description": "返回结果数量（1-100）",
                "default": 20
            },
            "threshold": {
                "type": "number",
                "description": "相似度阈值（0.0-1.0）",
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
```

**工具4：image_search（图像搜索）**

```python
Tool(
    name="image_search",
    description="基于CN-CLIP模型的图像搜索，支持图片上传查找相似内容。可以通过图片查找相似的图片或包含相关内容的文档。",
    inputSchema={
        "type": "object",
        "properties": {
            "image_data": {
                "type": "string",
                "description": "Base64 编码的图片数据"
            },
            "limit": {
                "type": "integer",
                "description": "返回结果数量（1-100）",
                "default": 20
            },
            "threshold": {
                "type": "number",
                "description": "相似度阈值（0.0-1.0）",
                "default": 0.7
            }
        },
        "required": ["image_data"]
    }
)
```

**工具5：hybrid_search（混合搜索）**

```python
Tool(
    name="hybrid_search",
    description="结合语义搜索和全文搜索的混合搜索，提供最佳的搜索结果。综合向量相似度和文本匹配度进行排序。",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "搜索查询词（1-500字符）"
            },
            "limit": {
                "type": "integer",
                "description": "返回结果数量（1-100）",
                "default": 20
            },
            "threshold": {
                "type": "number",
                "description": "相似度阈值（0.0-1.0）",
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
```

#### 搜索服务适配器设计

```python
class SearchAdapter:
    """搜索服务适配器，将现有搜索服务适配为 MCP 工具"""

    def __init__(self):
        self.chunk_search_service = get_chunk_search_service()
        self.image_search_service = get_image_search_service()

    async def semantic_search(self, query: str, limit: int, threshold: float, file_types: List[str] = None) -> dict:
        """语义搜索"""
        result = await self.chunk_search_service.search(
            query=query,
            search_type=SearchType.SEMANTIC,
            limit=limit,
            offset=0,
            threshold=threshold,
            file_types=file_types
        )
        return self._format_result(result)

    async def fulltext_search(self, query: str, limit: int, file_types: List[str] = None) -> dict:
        """全文搜索"""
        result = await self.chunk_search_service.search(
            query=query,
            search_type=SearchType.FULLTEXT,
            limit=limit,
            offset=0,
            file_types=file_types
        )
        return self._format_result(result)

    async def image_search(self, image_data: str, limit: int, threshold: float) -> dict:
        """图像搜索"""
        # 解码 Base64 图片数据
        # 调用 ImageSearchService
        # 返回格式化结果
        pass

    async def hybrid_search(self, query: str, limit: int, threshold: float, file_types: List[str] = None) -> dict:
        """混合搜索"""
        result = await self.chunk_search_service.search(
            query=query,
            search_type=SearchType.HYBRID,
            limit=limit,
            offset=0,
            threshold=threshold,
            file_types=file_types
        )
        return self._format_result(result)

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
```

#### 配置管理

**MCP 配置参数**

```python
class MCPConfig(BaseSettings):
    """MCP 服务器配置"""

    # 服务器配置
    server_name: str = Field(default="xiaoyao-search", description="服务器名称")
    server_version: str = Field(default="1.0.0", description="服务器版本")

    # 搜索配置
    default_limit: int = Field(default=20, ge=1, le=100, description="默认结果数量")
    default_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="默认相似度阈值")

    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")

    class Config:
        env_prefix = "MCP_"
```

**环境变量配置**

在 `backend/.env` 中添加：

```bash
# MCP服务器配置
MCP_SERVER_NAME=xiaoyao-search
MCP_SERVER_VERSION=1.0.0
MCP_DEFAULT_LIMIT=20
MCP_DEFAULT_THRESHOLD=0.7
MCP_LOG_LEVEL=INFO
MCP_SSE_ENABLED=true  # 启用SSE传输
```

#### FastAPI 集成设计

**在 FastAPI 主入口中集成 MCP 服务器**

```python
# backend/main.py 添加
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
        else:
            app.state.mcp_server = None
            logger.info("MCP 服务器未启用")
    except Exception as e:
        logger.error(f"❌ MCP 服务器初始化失败: {str(e)}")
        app.state.mcp_server = None
    # =====================================

    yield

    # 关闭时清理...
```

**添加 SSE 端点**

```python
# backend/main.py 添加路由
from app.mcp.transport import create_sse_endpoint

@app.get("/mcp/sse")
async def mcp_sse_endpoint(request: Request):
    """
    MCP SSE 传输端点

    Claude Desktop 通过此端点连接小遥搜索
    示例 URL: http://127.0.0.1:8000/mcp
    """
    if not app.state.mcp_server:
        raise HTTPException(status_code=503, detail="MCP 服务器未启用")

    return await create_sse_endpoint(app.state.mcp_server, request)
```

**Claude Desktop 配置**

```json
{
  "mcpServers": {
    "xiaoyao-search": {
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

---

## 7. 技术方案

### 7.1 技术选型

| 技术/框架 | 用途 | 选择理由 | 替代方案 |
|----------|------|---------|---------|
| **mcp-python-sdk** | MCP 协议实现 | Anthropic 官方 Python SDK，完整支持 MCP 协议规范 | 自己实现 MCP 协议 |
| **asyncio** | 异步框架 | 与现有 FastAPI 架构兼容，支持高并发 | 多线程 |
| **Pydantic** | 数据验证 | 与现有代码一致，提供类型安全 | 纯字典 |
| **适配器模式** | 架构模式 | 无需修改现有搜索服务，降低耦合 | 直接修改现有服务 |

### 7.2 架构变更

**整体架构（集成方案）**

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

**架构优势**：
1. **内存高效**：AI 模型只加载一次，无需重复加载（节省 4-6GB 内存）
2. **共享服务**：Electron 前端和 Claude Desktop 共享搜索服务和模型
3. **部署简单**：单一进程，无需管理多个服务
4. **直接调用**：MCP 工具直接调用搜索服务，无 HTTP 开销
5. **适配器模式**：通过 SearchAdapter 复用现有搜索服务，无需修改现有代码
6. **向后兼容**：现有功能和 API 完全不受影响

### 7.3 依赖变更

**后端依赖**

在 `backend/requirements.txt` 中添加：

```python
# MCP协议支持
mcp>=0.9.0
```

**依赖说明**：
- `mcp>=0.9.0`：Anthropic 官方 Python MCP SDK，提供 MCP 协议的完整实现

---

## 10. 测试计划

### 10.1 测试范围

| 测试类型 | 测试重点 | 测试场景数 | 优先级 |
|---------|---------|-----------|-------|
| 单元测试 | MCP 服务器类、工具执行器、适配器 | 15 | P0 |
| 集成测试 | MCP 工具与搜索服务集成 | 8 | P0 |
| 端到端测试 | Claude Desktop 完整搜索流程 | 5 | P0 |
| 性能测试 | 搜索响应时间、并发支持 | 3 | P1 |
| 兼容性测试 | 不同版本的 Claude Desktop | 2 | P1 |

### 10.2 核心测试用例

**用例1：FastAPI 集成 MCP 服务器启动**
- 前置条件：后端环境配置完成，依赖已安装
- 操作步骤：
  1. 启动 FastAPI 服务：`python backend/main.py`
  2. 观察服务器启动日志，确认 MCP 服务器初始化成功
  3. 访问健康检查端点：`http://127.0.0.1:8000/api/system/health`
  4. 验证 SSE 端点可访问：`curl http://127.0.0.1:8000/mcp`
- 预期结果：
  - FastAPI 服务成功启动
  - MCP 服务器初始化成功，日志显示 "✅ MCP 服务器初始化完成"
  - SSE 端点返回 200 响应
  - 所有搜索工具正确注册
  - 无错误日志
- 优先级：P0

**用例2：语义搜索工具调用**
- 前置条件：MCP 服务器运行中，索引已构建
- 操作步骤：
  1. Claude Desktop 调用 `semantic_search` 工具
  2. 传入查询参数：`{"query": "异步编程", "limit": 10}`
  3. 观察返回结果
- 预期结果：
  - 返回相关文档列表
  - 结果包含文件名、路径、相关度分数
  - 响应时间 < 2 秒
- 优先级：P0

**用例3：全文搜索工具调用**
- 前置条件：MCP 服务器运行中，索引已构建
- 操作步骤：
  1. Claude Desktop 调用 `fulltext_search` 工具
  2. 传入查询参数：`{"query": "async def", "limit": 10}`
  3. 观察返回结果
- 预期结果：
  - 返回包含 "async def" 的文档
  - 结果按相关度排序
  - 高亮显示匹配文本
- 优先级：P0

**用例4：图像搜索工具调用**
- 前置条件：MCP 服务器运行中，图像索引已构建
- 操作步骤：
  1. Claude Desktop 调用 `image_search` 工具
  2. 传入 Base64 编码的图片数据
  3. 观察返回结果
- 预期结果：
  - 返回相似图片列表
  - 包含相似度分数
  - 提供图片预览 URL
- 优先级：P1

**用例5：Claude Desktop 端到端测试**
- 前置条件：Claude Desktop 已配置小遥搜索 MCP 服务器
- 配置示例：
  ```json
  {
    "mcpServers": {
      "xiaoyao-search": {
        "url": "http://127.0.0.1:8000/mcp"
      }
    }
  }
  ```
- 操作步骤：
  1. 启动小遥搜索后端服务
  2. 重启 Claude Desktop
  3. 在 Claude Desktop 中输入："帮我找一下关于异步编程的文档"
  4. 观察 Claude 调用 MCP 工具
  5. 验证搜索结果展示
- 预期结果：
  - Claude Desktop 成功连接到小遥搜索
  - Claude 自动选择合适的搜索工具（如 semantic_search）
  - 搜索结果正确展示
  - Claude 基于结果生成有价值的回答
  - 响应时间 < 2 秒
- 优先级：P0

### 10.3 回归测试范围

- [ ] 搜索服务（ChunkSearchService、ImageSearchService）- 确保适配器不影响现有功能
- [ ] FastAPI 接口 - 确保 MCP 模块不干扰现有 API
- [ ] SSE 端点 - 确保与现有路由不冲突
- [ ] 前端应用 - 确保小遥搜索应用正常运行
- [ ] 内存占用 - 确保模型只加载一次，无内存泄漏

---

## 11. 验收标准

### 11.1 功能验收

- [ ] FastAPI 集成 MCP 服务器成功启动
- [ ] SSE 端点可访问并响应 MCP 握手
- [ ] 所有搜索工具（semantic_search、fulltext_search、voice_search、image_search、hybrid_search）可正常调用
- [ ] 搜索结果格式符合 MCP 协议规范
- [ ] Claude Desktop 能够成功连接并使用搜索工具

### 11.2 质量验收

- [ ] 无 P0/P1 级别 Bug
- [ ] P2 级别 Bug ≤ 3
- [ ] 单元测试覆盖率 ≥ 80%
- [ ] 搜索响应时间 ≤ 2 秒（语义/全文/混合搜索）
- [ ] 图像搜索响应时间 ≤ 3 秒
- [ ] 并发支持 ≥ 5 个同时连接

### 11.3 文档验收

- [ ] PRD 文档完整
- [ ] 技术方案文档完整
- [ ] Claude Desktop 配置文档完整
- [ ] 用户使用指南完整
- [ ] API 文档更新（如需要）

---

## 13. 成功指标

### 13.1 业务指标

| 指标名称 | 基线值 | 目标值 | 测量周期 | 负责人 |
|---------|-------|-------|---------|-------|
| MCP 连接成功率 | N/A | ≥ 95% | 每周 | 开发团队 |
| 搜索工具调用成功率 | N/A | ≥ 98% | 每周 | 开发团队 |
| 用户反馈评分 | N/A | ≥ 4.0/5.0 | 每月 | 产品经理 |
| Claude Desktop 用户增长率 | N/A | ≥ 10% | 每月 | 运营团队 |

### 13.2 技术指标

| 指标名称 | 基线值 | 目标值 | 测量方式 | 负责人 |
|---------|-------|-------|---------|-------|
| 搜索响应时间 | N/A | ≤ 2 秒 | MCP 日志分析 | 开发团队 |
| FastAPI 稳定性 | N/A | 99% 可用 | 运行监控 | 开发团队 |
| 内存增量 | N/A | ≤ 100MB | 系统监控 | 开发团队 |
| SSE 连接支持 | N/A | ≥ 5 | 压力测试 | 测试团队 |

---

## 14. 风险与挑战

### 14.1 技术风险

| 风险项 | 风险等级 | 影响 | 应对措施 | 负责人 | 状态 |
|-------|---------|------|---------|-------|------|
| MCP SDK 兼容性问题 | 中 | Claude Desktop 无法连接 | 使用官方 SDK，关注版本更新，及时升级 | 开发团队 | 规划中 |
| SSE 传输稳定性 | 中 | 数据传输中断 | 完善错误处理，添加超时机制 | 开发团队 | 规划中 |
| FastAPI 路由冲突 | 低 | SSE 端点无法访问 | 合理规划路由前缀，避免冲突 | 开发团队 | 规划中 |
| 搜索服务性能 | 低 | 搜索响应慢 | 优化索引，添加缓存 | 开发团队 | 规划中 |
| 适配器层引入延迟 | 低 | 影响用户体验 | 最小化适配器逻辑，直接调用 | 开发团队 | 规划中 |

### 14.2 业务风险

| 风险项 | 风险等级 | 影响 | 应对措施 | 负责人 | 状态 |
|-------|---------|------|---------|-------|------|
| Claude Desktop 用户基数小 | 中 | 功能使用率低 | 加强宣传，突出 MCP 价值 | 运营团队 | 规划中 |
| 用户配置复杂 | 中 | 用户放弃使用 | 提供详细配置指南，简化配置流程 | 产品经理 | 规划中 |
| MCP 协议变更 | 低 | 需要适配新协议 | 关注 MCP 社区动态，预留扩展接口 | 开发团队 | 规划中 |

### 14.3 时间风险

| 风险项 | 风险等级 | 影响 | 应对措施 | 负责人 | 状态 |
|-------|---------|------|---------|-------|------|
| MCP SDK 学习曲线 | 低 | 开发周期延长 | 提前学习 SDK，参考官方示例 | 开发团队 | 规划中 |
| Claude Desktop 测试耗时 | 中 | 测试周期延长 | 提前准备测试环境，自动化测试 | 测试团队 | 规划中 |

---

## 16. 变更历史

| 版本 | 日期 | 变更内容 | 变更人 | 审核人 |
|-----|------|---------|-------|-------|
| v1.0 | 2026-03-11 | 初始版本，MCP 服务器功能规划（独立进程 + stdio） | AI助手 | 用户 |
| v1.1 | 2026-03-11 | 精简为 MVP 核心功能，仅保留 P0/P1 级别的搜索工具 | AI助手 | 用户 |
| v1.2 | 2026-03-11 | 架构调整为集成方案（FastAPI 集成 + SSE 端点），共享模型节省内存 | AI助手 | 用户 |

---

## 17. 相关文档

### 17.1 产品文档
- [主PRD文档](../../01-prd.md) - 基础产品需求文档
- [原型设计](./mcp-02-原型.md) - 原型设计文档（待创建）
- [用户手册](../../docs/用户手册.md) - 用户使用手册

### 17.2 技术文档
- [技术方案](./mcp-03-技术方案.md) - 技术实现方案（待创建）
- [API文档](../../接口文档.md) - 接口文档
- [数据库设计](../../数据库设计文档.md) - 数据库设计

### 17.3 项目文档
- [开发任务清单](./mcp-04-开发任务清单.md) - 任务分解（待创建）
- [开发排期表](./mcp-05-开发排期表.md) - 时间规划（待创建）

### 17.4 外部资源
- [MCP 官方文档](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Claude Desktop 文档](https://docs.anthropic.com/en/docs/claude-desktop/mcp)

---

## 18. 附录

### 18.1 术语表

| 术语 | 定义 |
|-----|------|
| **MCP** | Model Context Protocol，模型上下文协议，由 Anthropic 推出的开源协议 |
| **SSE** | Server-Sent Events，服务器推送事件，MCP 的 HTTP 传输方式 |
| **Claude Desktop** | Anthropic 开发的桌面 AI 应用，可作为 MCP 客户端 |
| **适配器模式** | 将一个类的接口转换成客户希望的另一个接口，使得原本由于接口不兼容而不能一起工作的那些类可以一起工作 |
| **语义搜索** | 基于向量相似度的搜索，理解查询意图而非关键词匹配 |
| **全文搜索** | 基于关键词匹配的搜索，支持中文分词 |
| **混合搜索** | 结合语义搜索和全文搜索的综合搜索方式 |

### 18.2 参考资源
- [MCP 协议规范](https://modelcontextprotocol.io/specification/2025-11-25/)
- [MCP Python SDK 文档](https://github.com/modelcontextprotocol/python-sdk)
- [Claude Desktop 配置指南](https://docs.anthropic.com/en/docs/claude-desktop/mcp#configuration)

### 18.3 FAQ

**Q1: MCP 服务器是否会影响小遥搜索应用的性能？**
A: 影响极小。MCP 服务器集成在 FastAPI 进程中，共享已加载的 AI 模型和搜索服务，不会重复加载资源。只有在 Claude Desktop 调用时才会产生额外的 SSE 通信开销（< 100MB 内存增量）。

**Q2: 如何确认 MCP 服务器是否正常运行？**
A: 启动 FastAPI 服务后，检查日志中是否显示 "✅ MCP 服务器初始化完成"。也可以通过 Claude Desktop 的 MCP 服务器状态查看，或者直接访问 SSE 端点：`curl http://127.0.0.1:8000/mcp`。

**Q3: 是否需要关闭小遥搜索应用才能使用 MCP 服务器？**
A: 不需要。MCP 服务器集成在 FastAPI 服务中，和小遥搜索应用共用同一个后端服务。只需确保后端服务正常运行即可。

**Q4: MCP 服务器是否会暴露用户的敏感数据？**
A: 不会。MCP 服务器只在本地运行，所有通信都通过 SSE 在本地进行（127.0.0.1），不会上传任何数据到云端。

**Q5: 如何配置 Claude Desktop 连接小遥搜索 MCP 服务器？**
A: 需要编辑 Claude Desktop 的配置文件（`%APPDATA%\Claude\claude_desktop_config.json`），添加以下配置：
```json
{
  "mcpServers": {
    "xiaoyao-search": {
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```
详见配置文档。

**Q6: 为什么选择集成方案而不是独立进程？**
A: 集成方案有以下优势：
1. 内存高效：AI 模型只加载一次，节省 4-6GB 内存
2. 部署简单：单一进程，无需管理多个服务
3. 直接调用：MCP 工具直接调用搜索服务，无 HTTP 开销
4. 共享服务：Electron 前端和 Claude Desktop 共享相同的搜索服务和模型

---

**文档版本**：v1.2
**创建时间**：2026-03-11
**最后更新**：2026-03-11
**维护者**：AI助手

> **使用说明**：
> 1. 本 PRD 文档基于模板编写，涵盖 MCP 服务器功能的完整需求
> 2. 请根据实际开发情况更新文档内容
> 3. 标记为 "待创建" 的文档将在后续开发中补充
> 4. 表格中的示例内容请替换为实际内容
> 5. v1.2 版本采用集成方案（FastAPI 集成 + SSE 端点），共享 AI 模型节省内存
