# MCP 工具文档

> **文档类型**：工具文档
> **特性名称**：MCP 服务器支持
> **协议版本**：MCP 2024-11-05
> **文档版本**：v1.0
> **创建时间**：2026-03-11
> **关联文档**：[MCP PRD](docs/特性开发/mcp/mcp-01-prd.md) | [MCP 技术方案](docs/特性开发/mcp/mcp-03-技术方案.md)

---

## 📋 工具概览

### MCP 端点

| 端点 | 协议 | 方法 | 描述 |
|------|------|------|------|
| `/mcp/sse` | SSE (Server-Sent Events) | GET | MCP 协议传输层 |

### 暴露的 Tools

| Tool | 优先级 | 描述 |
|------|--------|------|
| `semantic_search` | P0 | 基于 BGE-M3 的语义搜索 |
| `fulltext_search` | P0 | 基于 Whoosh 的全文搜索 |
| `voice_search` | P1 | 基于 FasterWhisper 的语音搜索 |
| `image_search` | P1 | 基于 CN-CLIP 的图像搜索 |
| `hybrid_search` | P1 | 语义+全文混合搜索 |

---

## 🔌 MCP 端点

### 1. SSE 连接端点

**端点**：`GET /mcp/sse`

**协议**：Server-Sent Events (SSE)

**描述**：MCP 客户端（如 Claude Desktop）通过此端点建立持久连接，进行双向通信。

**请求格式**：

```http
GET /mcp/sse HTTP/1.1
Host: 127.0.0.1:8000
Accept: text/event-stream
Cache-Control: no-cache
```

**响应格式**：

```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

event: endpoint
data: {"message":"endpoint","event":"http://127.0.0.1:8000/mcp/sse?sessionId=xxx"}
```

**配置参数**：

| 环境变量 | 默认值 | 描述 |
|----------|--------|------|
| `MCP_SERVER_ENABLED` | `true` | 是否启用 MCP 服务器 |
| `MCP_SSE_ENDPOINT` | `/mcp/sse` | SSE 端点路径 |
| `MCP_SSE_HEARTBEAT_INTERVAL` | `30` | 心跳间隔（秒） |

**Claude Desktop 配置**：

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

## 🛠️ MCP Tools 详细说明

### Tool 1: semantic_search

**MCP Tool 名称**：`semantic_search`

**描述**：基于 BGE-M3 模型的语义搜索，支持自然语言查询理解。适合用自然语言描述的查询，如"关于机器学习算法优化的方法"。

**优先级**：P0（核心功能）

#### 输入参数

| 参数 | 类型 | 必填 | 默认值 | 约束 | 描述 |
|------|------|------|--------|------|------|
| `query` | string | ✅ | - | 1-500 字符 | 搜索查询词 |
| `limit` | integer | ❌ | 20 | 1-100 | 返回结果数量 |
| `threshold` | number | ❌ | 0.7 | 0.0-1.0 | 相似度阈值 |
| `file_types` | array[string] | ❌ | null | - | 文件类型过滤（如 ["pdf", "md"]） |

#### 输入 Schema (JSON Schema)

```json
{
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
      "default": 20
    },
    "threshold": {
      "type": "number",
      "description": "相似度阈值（0.0-1.0，默认0.7）",
      "minimum": 0.0,
      "maximum": 1.0,
      "default": 0.7
    },
    "file_types": {
      "type": "array",
      "description": "文件类型过滤（如 [\"pdf\", \"md\"]）",
      "items": {
        "type": "string"
      }
    }
  },
  "required": ["query"]
}
```

#### 输出格式

```json
{
  "results": [
    {
      "chunk_id": "123",
      "file_path": "D:\\Documents\\机器学习.pdf",
      "file_name": "机器学习.pdf",
      "file_type": "pdf",
      "content": "这是文档的内容摘要...",
      "page_number": 10,
      "score": 0.92,
      "metadata": {
        "author": "张三",
        "created_date": "2025-01-01"
      }
    }
  ],
  "total": 1,
  "query": "机器学习算法优化"
}
```

#### 调用示例

**Claude Desktop 对话**：

```
用户：帮我搜索关于机器学习的文档

Claude：[调用 semantic_search 工具]
      参数：{"query": "机器学习", "limit": 10}

找到了以下关于机器学习的文档：

1. 机器学习算法优化.pdf
   - 相关度：92%
   - 路径：D:\Documents\机器学习.pdf

2. 深度学习入门.md
   - 相关度：87%
   - 路径：D:\Notes\深度学习.md
```

---

### Tool 2: fulltext_search

**MCP Tool 名称**：`fulltext_search`

**描述**：基于 Whoosh 的全文搜索，支持精确关键词匹配和中文分词。适合查找特定术语、代码片段或精确短语。

**优先级**：P0（核心功能）

#### 输入参数

| 参数 | 类型 | 必填 | 默认值 | 约束 | 描述 |
|------|------|------|--------|------|------|
| `query` | string | ✅ | - | 1-500 字符 | 搜索查询词 |
| `limit` | integer | ❌ | 20 | 1-100 | 返回结果数量 |
| `file_types` | array[string] | ❌ | null | - | 文件类型过滤 |

#### 输入 Schema (JSON Schema)

```json
{
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
      "default": 20
    },
    "file_types": {
      "type": "array",
      "description": "文件类型过滤（如 [\"pdf\", \"md\"]）",
      "items": {
        "type": "string"
      }
    }
  },
  "required": ["query"]
}
```

#### 输出格式

```json
{
  "results": [
    {
      "chunk_id": "456",
      "file_path": "D:\\Documents\\Python笔记.md",
      "file_name": "Python笔记.md",
      "file_type": "md",
      "content": "asyncio 是 Python 的异步编程库...",
      "highlighted_content": "asyncio 是 <mark>Python</mark> 的异步编程库...",
      "score": 0.85
    }
  ],
  "total": 1,
  "query": "Python asyncio"
}
```

#### 调用示例

**Claude Desktop 对话**：

```
用户：帮我找包含"asyncio"的代码

Claude：[调用 fulltext_search 工具]
      参数：{"query": "asyncio", "limit": 10}

找到了以下包含"asyncio"的文档：

1. Python异步编程笔记.md
   - 匹配度：85%
   - 路径：D:\Notes\python-async.md
   - 片段：asyncio 是 Python 的异步编程库...
```

---

### Tool 3: voice_search

**MCP Tool 名称**：`voice_search`

**描述**：基于 FasterWhisper 模型的语音搜索，支持语音输入转文本后进行搜索。适合通过语音快速搜索，无需手动输入文字。

**优先级**：P1（重要功能）

#### 输入参数

| 参数 | 类型 | 必填 | 默认值 | 约束 | 描述 |
|------|------|------|--------|------|------|
| `audio_data` | string | ✅ | - | Base64 编码 | 音频数据（WAV/MP3/M4A） |
| `search_type` | string | ❌ | "semantic" | semantic/fulltext/hybrid | 搜索类型 |
| `limit` | integer | ❌ | 20 | 1-100 | 返回结果数量 |
| `threshold` | number | ❌ | 0.7 | 0.0-1.0 | 相似度阈值 |
| `file_types` | array[string] | ❌ | null | - | 文件类型过滤 |

#### 输入 Schema (JSON Schema)

```json
{
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
      "description": "返回结果数量（1-100，默认20）",
      "minimum": 1,
      "maximum": 100,
      "default": 20
    },
    "threshold": {
      "type": "number",
      "description": "相似度阈值（0.0-1.0，默认0.7）",
      "minimum": 0.0,
      "maximum": 1.0,
      "default": 0.7
    },
    "file_types": {
      "type": "array",
      "description": "文件类型过滤（如 [\"pdf\", \"md\"]）",
      "items": {
        "type": "string"
      }
    }
  },
  "required": ["audio_data"]
}
```

#### 输出格式

```json
{
  "transcription": "帮我找关于机器学习的文档",
  "transcription_confidence": 0.95,
  "search_type": "semantic",
  "results": [
    {
      "chunk_id": "789",
      "file_path": "D:\\Documents\\机器学习.pdf",
      "file_name": "机器学习.pdf",
      "file_type": "pdf",
      "content": "这是文档的内容摘要...",
      "score": 0.92
    }
  ],
  "total": 1
}
```

#### 调用示例

**Claude Desktop 对话**：

```
用户：[按住麦克风按钮，说出查询内容]
      "帮我找一下关于机器学习算法优化的文档"

Claude：收到语音查询，正在识别...
[调用 voice_search 工具]
      参数：{
        "audio_data": "base64...",
        "search_type": "semantic",
        "limit": 10
      }

我识别到你的查询是"机器学习算法优化"，正在搜索...

找到了以下相关文档：

1. 深度学习优化技巧.pdf
   - 相关度：94%
   - 路径：D:\Documents\dl-optimization.pdf
```

---

### Tool 4: image_search

**MCP Tool 名称**：`image_search`

**描述**：基于 CN-CLIP 模型的图像搜索，支持图片上传查找相似内容。可以通过图片查找相似的图片或包含相关内容的文档。

**优先级**：P1（重要功能）

#### 输入参数

| 参数 | 类型 | 必填 | 默认值 | 约束 | 描述 |
|------|------|------|--------|------|------|
| `image_data` | string | ✅ | - | Base64 编码 | 图片数据（PNG/JPG） |
| `limit` | integer | ❌ | 20 | 1-100 | 返回结果数量 |
| `threshold` | number | ❌ | 0.7 | 0.0-1.0 | 相似度阈值 |

#### 输入 Schema (JSON Schema)

```json
{
  "type": "object",
  "properties": {
    "image_data": {
      "type": "string",
      "description": "Base64 编码的图片数据（PNG/JPG 格式）"
    },
    "limit": {
      "type": "integer",
      "description": "返回结果数量（1-100，默认20）",
      "minimum": 1,
      "maximum": 100,
      "default": 20
    },
    "threshold": {
      "type": "number",
      "description": "相似度阈值（0.0-1.0，默认0.7）",
      "minimum": 0.0,
      "maximum": 1.0,
      "default": 0.7
    }
  },
  "required": ["image_data"]
}
```

#### 输出格式

```json
{
  "results": [
    {
      "chunk_id": "101",
      "file_path": "D:\\Documents\\架构图.png",
      "file_name": "微服务架构设计图.png",
      "file_type": "png",
      "image_path": "D:\\Documents\\架构图.png",
      "score": 0.89
    }
  ],
  "total": 1,
  "query_image_hash": "abc123"
}
```

#### 调用示例

**Claude Desktop 对话**：

```
用户：[上传一张架构图截图]
      我记得之前保存过类似的架构图，能帮我找找吗？

Claude：让我用这张图片搜索一下...
[调用 image_search 工具]
      参数：{"image_data": "base64...", "limit": 5}

找到了相似的图片！

1. 微服务架构设计图.png
   - 相似度：89%
   - 路径：D:\Documents\architecture.png
```

---

### Tool 5: hybrid_search

**MCP Tool 名称**：`hybrid_search`

**描述**：结合语义搜索和全文搜索的混合搜索，提供最佳的搜索结果。综合向量相似度和文本匹配度进行排序。

**优先级**：P1（重要功能）

#### 输入参数

| 参数 | 类型 | 必填 | 默认值 | 约束 | 描述 |
|------|------|------|--------|------|------|
| `query` | string | ✅ | - | 1-500 字符 | 搜索查询词 |
| `limit` | integer | ❌ | 20 | 1-100 | 返回结果数量 |
| `threshold` | number | ❌ | 0.7 | 0.0-1.0 | 相似度阈值 |
| `semantic_weight` | number | ❌ | 0.7 | 0.0-1.0 | 语义搜索权重 |
| `file_types` | array[string] | ❌ | null | - | 文件类型过滤 |

#### 输入 Schema (JSON Schema)

```json
{
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
      "default": 20
    },
    "threshold": {
      "type": "number",
      "description": "相似度阈值（0.0-1.0，默认0.7）",
      "minimum": 0.0,
      "maximum": 1.0,
      "default": 0.7
    },
    "semantic_weight": {
      "type": "number",
      "description": "语义搜索权重（0.0-1.0，默认0.7）",
      "minimum": 0.0,
      "maximum": 1.0,
      "default": 0.7
    },
    "file_types": {
      "type": "array",
      "description": "文件类型过滤（如 [\"pdf\", \"md\"]）",
      "items": {
        "type": "string"
      }
    }
  },
  "required": ["query"]
}
```

#### 输出格式

```json
{
  "results": [
    {
      "chunk_id": "202",
      "file_path": "D:\\Documents\\Python异步编程.pdf",
      "file_name": "Python异步编程.pdf",
      "file_type": "pdf",
      "content": "asyncio 是 Python 的异步编程库...",
      "semantic_score": 0.92,
      "fulltext_score": 0.78,
      "hybrid_score": 0.88
    }
  ],
  "total": 1,
  "query": "Python 异步编程"
}
```

#### 调用示例

**Claude Desktop 对话**：

```
用户：帮我搜索"asyncio"相关的内容

Claude：[调用 hybrid_search 工具]
      参数：{"query": "asyncio", "limit": 10}

找到了以下相关内容（综合语义和关键词匹配）：

1. Python异步编程笔记.md
   - 语义相关度：92%
   - 关键词匹配度：78%
   - 综合评分：88%
   - 路径：D:\Notes\python-async.md
```

---

## 📡 MCP 协议方法

### 协议版本
MCP 2024-11-05

### 标准方法

MCP 协议定义了以下标准方法，客户端通过 SSE 连接后调用：

#### 1. tools/list
列出所有可用的工具。

**请求**：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}
```

**响应**：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "semantic_search",
        "description": "基于BGE-M3模型的语义搜索...",
        "inputSchema": { ... }
      },
      {
        "name": "fulltext_search",
        "description": "基于Whoosh的全文搜索...",
        "inputSchema": { ... }
      }
    ]
  }
}
```

#### 2. tools/call
调用指定的工具。

**请求**：
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "semantic_search",
    "arguments": {
      "query": "机器学习",
      "limit": 10
    }
  }
}
```

**响应**：
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"results\": [...], \"total\": 10}"
      }
    ]
  }
}
```

#### 3. initialize
初始化 MCP 连接。

**请求**：
```json
{
  "jsonrpc": "2.0",
  "id": 0,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "claude-desktop",
      "version": "1.0.0"
    }
  }
}
```

**响应**：
```json
{
  "jsonrpc": "2.0",
  "id": 0,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {}
    },
    "serverInfo": {
      "name": "xiaoyao-search",
      "version": "1.0.0"
    }
  }
}
```

---

## ⚙️ 配置说明

### 环境变量配置

| 变量名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `MCP_SERVER_ENABLED` | bool | `true` | 是否启用 MCP 服务器 |
| `MCP_SSE_ENDPOINT` | string | `/mcp/sse` | SSE 端点路径 |
| `MCP_SSE_HEARTBEAT_INTERVAL` | int | `30` | 心跳间隔（秒） |
| `MCP_DEFAULT_LIMIT` | int | `20` | 默认返回结果数量 |
| `MCP_DEFAULT_THRESHOLD` | float | `0.7` | 默认相似度阈值 |

### .env 配置示例

```bash
# MCP 服务器配置
MCP_SERVER_ENABLED=true
MCP_SSE_ENDPOINT=/mcp/sse
MCP_SSE_HEARTBEAT_INTERVAL=30

# 搜索默认参数
MCP_DEFAULT_LIMIT=20
MCP_DEFAULT_THRESHOLD=0.7
```

---

## 🔒 错误处理

### 错误响应格式

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32602,
    "message": "Invalid params",
    "data": {
      "query": ["This field is required"]
    }
  }
}
```

### 错误代码

| 错误代码 | 描述 |
|----------|------|
| -32700 | Parse error（JSON 解析错误） |
| -32600 | Invalid Request（无效请求） |
| -32601 | Method not found（方法不存在） |
| -32602 | Invalid params（参数无效） |
| -32603 | Internal error（内部错误） |

### 业务错误

| 错误 | 描述 | 处理建议 |
|------|------|----------|
| 索引未构建 | 搜索索引不存在 | 提示用户先构建索引 |
| 模型未加载 | AI 模型未初始化 | 提示用户检查模型配置 |
| 音频解码失败 | 音频格式不支持 | 提示使用 WAV/MP3/M4A 格式 |

---

## 📊 性能指标

### 预期响应时间

| Tool | 预期响应时间 |
|------|--------------|
| `semantic_search` | < 2s |
| `fulltext_search` | < 1s |
| `voice_search` | < 5s（含语音识别） |
| `image_search` | < 3s |
| `hybrid_search` | < 3s |

### 资源占用

| 资源 | 预期占用 |
|------|----------|
| 内存（不含 AI 模型） | < 500MB |
| 内存（含 AI 模型） | < 8GB |
| CPU（搜索时） | < 50% |
| 带宽（SSE 连接） | < 1KB/s（心跳） |

---

## 🧪 测试工具

### MCP 客户端测试脚本

```python
# 测试 MCP 服务器连接
import asyncio
from mcp import ClientSession, SSEClientTransport

async def test_mcp():
    transport = SSEClientTransport("http://127.0.0.1:8000/mcp/sse")
    async with ClientSession(transport) as session:
        # 初始化
        await session.initialize()

        # 列出工具
        tools = await session.list_tools()
        print("可用工具:", [tool.name for tool in tools.tools])

        # 调用语义搜索
        result = await session.call_tool(
            "semantic_search",
            arguments={"query": "机器学习", "limit": 5}
        )
        print("搜索结果:", result)

asyncio.run(test_mcp())
```

---

## 📚 相关文档

- [MCP PRD](docs/特性开发/mcp/mcp-01-prd.md) - 产品需求文档
- [MCP 技术方案](docs/特性开发/mcp/mcp-03-技术方案.md) - 技术实现方案
- [MCP 原型设计](docs/特性开发/mcp/mcp-02-原型.md) - 用户使用场景
- [MCP 官方文档](https://modelcontextprotocol.io/) - MCP 协议规范

---

**文档结束**

> **文档版本**：v1.0
> **协议版本**：MCP 2024-11-05
> **维护者**：AI助手
>
> **重要提示**：
> - MCP 工具使用 SSE 传输，不是传统 REST API
> - Claude Desktop 作为 MCP 客户端自动发现和调用工具
> - 所有工具参数通过 JSON Schema 定义和验证
