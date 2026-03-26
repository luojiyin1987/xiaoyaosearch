# 云端嵌入模型调用能力 - 接口文档增量

> **文档类型**：增量接口文档
> **基础版本**：基于 [主接口文档](../../接口文档.md)
> **特性状态**：规划中
> **创建时间**：2026-03-26
> **最后更新**：2026-03-26

---

## 1. 增量说明

### 1.1 概述

本文档描述了云端嵌入模型调用能力特性对现有接口的增量变更。

**变更类型**：
- **修改接口**：扩展现有接口参数，支持云端嵌入模型配置
- **新增字段**：provider 字段新增可选值 "cloud"
- **配置变更**：config 字段根据 provider 不同包含不同配置项

### 1.2 向后兼容性

**兼容性声明**：✅ 完全向后兼容

- 现有本地 BGE-M3 配置保持不变
- 新增的云端配置为可选功能
- 数据库表结构无变更
- API 路径无变更
- **向量维度**：使用模型原始维度，不做归一化处理
- **索引重建**：切换模型时必须重建索引

---

## 2. 接口变更

### 2.1 更新AI模型配置（扩展）

**接口**：`PUT /api/config/ai-model`

**变更类型**：修改（扩展参数）

**变更说明**：provider 字段新增可选值 "cloud"，config 字段根据 provider 不同包含不同配置项。

---

#### 请求体（本地嵌入模型 - 现有配置，无变更）

```http
PUT /api/config/ai-model
Content-Type: application/json

{
  "model_type": "embedding",
  "provider": "local",
  "model_name": "BAAI/bge-m3",
  "config": {
    "device": "cpu"
  }
}
```

**本地嵌入模型配置项说明**：

| 配置项 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| device | string | 否 | cpu | 运行设备：cpu 或 cuda |

---

#### 请求体（OpenAI 兼容云端 - 新增配置）

```http
PUT /api/config/ai-model
Content-Type: application/json

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

**云端嵌入模型配置项说明**：

| 配置项 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| api_key | string | 是 | - | API 密钥（加密存储） |
| endpoint | string | 否 | https://api.openai.com/v1 | API 端点地址 |
| model | string | 是 | - | 模型名称 |
| timeout | integer | 否 | 30 | 请求超时时间（秒） |
| batch_size | integer | 否 | 100 | 批处理大小 |

**向量维度说明**：使用模型的原始向量维度，不做任何归一化处理。

---

#### 响应体（成功）

```json
{
  "code": 200,
  "message": "配置更新成功",
  "data": {
    "id": 1,
    "model_type": "embedding",
    "provider": "cloud",
    "model_name": "text-embedding-3-small",
    "is_active": true,
    "created_at": "2026-03-26T10:00:00",
    "updated_at": "2026-03-26T10:00:00"
  }
}
```

---

#### 响应体（失败 - 参数验证错误）

```json
{
  "code": 400,
  "message": "参数验证失败",
  "details": {
    "api_key": ["api_key 是必填参数"],
    "model": ["model 是必填参数"]
  }
}
```

---

#### 响应体（失败 - 连接测试失败）

```json
{
  "code": 503,
  "message": "连接测试失败",
  "details": {
    "error": "authentication failed: invalid api key",
    "suggestion": "请检查 API 密钥是否正确"
  }
}
```

---

### 2.2 测试AI模型连接（扩展）

**接口**：`POST /api/config/ai-model/test`

**变更类型**：修改（扩展测试场景）

**变更说明**：新增云端嵌入模型连接测试场景。

---

#### 请求体（云端嵌入模型测试）

```http
POST /api/config/ai-model/test
Content-Type: application/json

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

---

#### 响应体（成功）

```json
{
  "code": 200,
  "message": "连接成功",
  "data": {
    "provider": "cloud",
    "model": "text-embedding-3-small",
    "embedding_dim": 1536,
    "test_text": "test",
    "response_time_ms": 245
  }
}
```

**响应字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| embedding_dim | integer | 云端模型原始向量维度 |
| test_text | string | 测试文本 |
| response_time_ms | integer | 响应时间（毫秒） |

---

#### 响应体（失败 - 认证失败）

```json
{
  "code": 401,
  "message": "认证失败",
  "details": {
    "error": "invalid api key",
    "provider": "OpenAI",
    "suggestion": "请检查 API 密钥是否正确"
  }
}
```

---

#### 响应体（失败 - 模型不存在）

```json
{
  "code": 404,
  "message": "模型不存在",
  "details": {
    "error": "model 'text-embedding-xxx' not found",
    "suggestion": "请检查模型名称是否正确"
  }
}
```

---

### 2.3 获取AI模型列表（无变更）

**接口**：`GET /api/config/ai-models`

**变更类型**：无变更

**说明**：接口保持不变，返回结果中可能包含 provider="cloud" 的嵌入模型配置。

---

#### 响应体（包含云端嵌入模型）

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "models": [
      {
        "id": 1,
        "model_type": "embedding",
        "provider": "local",
        "model_name": "BAAI/bge-m3",
        "is_active": false,
        "config": {
          "device": "cpu"
        }
      },
      {
        "id": 2,
        "model_type": "embedding",
        "provider": "cloud",
        "model_name": "text-embedding-3-small",
        "is_active": true,
        "config": {
          "endpoint": "https://api.openai.com/v1",
          "model": "text-embedding-3-small",
          "timeout": 30,
          "batch_size": 100
        }
      }
    ]
  }
}
```

**注意**：出于安全考虑，`api_key` 字段不会在列表接口中返回。

---

## 3. 数据模型变更

### 3.1 AIModelConfig（扩展）

**类型**：Pydantic Model

**变更说明**：config 字段根据 provider 不同包含不同配置项。

```python
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class LocalEmbeddingConfig(BaseModel):
    """本地嵌入模型配置"""
    device: str = "cpu"


class CloudEmbeddingConfig(BaseModel):
    """云端嵌入模型配置"""
    api_key: str = Field(..., description="API 密钥")
    endpoint: str = Field(default="https://api.openai.com/v1", description="API 端点地址")
    model: str = Field(..., description="模型名称")
    timeout: int = Field(default=30, ge=1, le=120, description="请求超时时间（秒）")
    batch_size: int = Field(default=100, ge=1, le=1000, description="批处理大小")


class AIModelConfig(BaseModel):
    """AI 模型配置"""
    model_type: str  # 'embedding', 'llm', etc.
    provider: str    # 'local', 'cloud'
    model_name: str
    config: Union[LocalEmbeddingConfig, CloudEmbeddingConfig, Dict[str, Any]]
    is_active: bool = True
```

---

## 4. 国际化支持

### 4.1 语言环境检测

**请求头**：`Accept-Language`

**支持值**：
- `zh-CN` 或 `zh_CN` - 简体中文（默认）
- `en-US` 或 `en_US` - 英文
- 支持带权重的格式：`zh-CN;q=0.9, en;q=0.8`

**检测逻辑**：后端自动从 `Accept-Language` 头中解析语言环境。

---

### 4.2 国际化响应示例

**请求示例**：

```http
PUT /api/config/ai-model
Content-Type: application/json
Accept-Language: en-US

{
  "model_type": "embedding",
  "provider": "cloud",
  "model_name": "text-embedding-3-small",
  "config": {
    "api_key": "sk-xxx",
    "endpoint": "https://api.openai.com/v1",
    "model": "text-embedding-3-small"
  }
}
```

**中文响应**（`Accept-Language: zh-CN`）：

```json
{
  "code": 200,
  "message": "配置更新成功",
  "data": { ... }
}
```

**英文响应**（`Accept-Language: en-US`）：

```json
{
  "code": 200,
  "message": "Configuration updated successfully",
  "data": { ... }
}
```

---

### 4.3 参数化翻译

**示例**：云端嵌入模型测试成功

**中文**：
```json
{
  "code": 200,
  "message": "云端嵌入模型测试成功，向量维度: 1536，响应正常",
  "data": { ... }
}
```

**英文**：
```json
{
  "code": 200,
  "message": "Cloud embedding model test successful, vector dimension: 1536, response normal",
  "data": { ... }
}
```

---

### 4.4 新增翻译键

**后端翻译键**（`backend/app/locales/`）：

| 键名 | 中文示例 | 英文示例 |
|------|---------|---------|
| `model.cloud_embedding_success` | 云端嵌入模型测试成功，向量维度: {dimension} | Cloud embedding model test successful, vector dimension: {dimension} |
| `model.cloud_auth_failed` | 云端API认证失败：{error} | Cloud API authentication failed: {error} |
| `model.rebuild_already_running` | 重建任务正在进行中，进度：{progress}% | Rebuild task is in progress, progress: {progress}% |
| `index_rebuild.status_running` | 重建中 | Rebuilding |

**前端翻译键**（`frontend/src/locale/lang/`）：

| 键名 | 中文示例 | 英文示例 |
|------|---------|---------|
| `embedding.providerLocal` | 本地（推荐，免费离线） | Local (Recommended, Free & Offline) |
| `embedding.cloudDataSafe` | 您的本地文件和索引数据存储在本地，不会上传 | Your local files and index data are stored locally, not uploaded |
| `embedding.testConnection` | 测试连接 | Test Connection |

---

## 5. 错误码扩展

### 4.1 新增错误码

| 错误码 | HTTP状态码 | 说明 | 建议处理 |
|--------|-----------|------|---------|
| EMBEDDING_CLOUD_AUTH_FAILED | 401 | 云端 API 认证失败 | 检查 API 密钥 |
| EMBEDDING_CLOUD_MODEL_NOT_FOUND | 404 | 云端模型不存在 | 检查模型名称 |
| EMBEDDING_CLOUD_RATE_LIMIT | 429 | 云端 API 请求频率超限 | 降低请求频率或升级套餐 |
| EMBEDDING_CLOUD_TIMEOUT | 504 | 云端 API 请求超时 | 增加超时时间或检查网络 |

---

## 5. 业务逻辑说明

### 5.1 本地/云端互斥切换

**规则**：
1. 同一时间只能有一个活跃的嵌入模型配置
2. 切换到云端时，自动卸载本地模型
3. 切换到本地时，自动关闭云端服务
4. **切换模型必须重建索引**（不同模型的向量空间不兼容）

**流程**：

```
用户提交 provider='cloud' 配置
    ↓
验证配置参数
    ↓
    ├─ 验证失败 → 返回错误
    │
    └─ 验证成功 → 测试云端连接
                      │
                      ├─ 连接失败 → 返回错误
                      │
                      └─ 连接成功 → 更新数据库
                                        │
                                        ├─ 将现有 is_active=true 设为 false
                                        ├─ 插入新配置，is_active=true
                                        ├─ 卸载本地嵌入模型
                                        ├─ 初始化云端嵌入服务
                                        ├─ 返回成功 + need_rebuild=true
                                        └─ 提示用户重建索引
```

---

## 6. 安全考虑

### 6.1 API 密钥保护

**加密存储**：API 密钥使用 AES 加密后存储

```python
from cryptography.fernet import Fernet

def encrypt_api_key(api_key: str) -> str:
    """加密 API 密钥"""
    key = os.getenv("API_ENCRYPTION_KEY")
    fernet = Fernet(key)
    return fernet.encrypt(api_key.encode()).decode()

def decrypt_api_key(encrypted_key: str) -> str:
    """解密 API 密钥"""
    key = os.getenv("API_ENCRYPTION_KEY")
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_key.encode()).decode()
```

---

### 6.2 日志脱敏

**规则**：日志中 API 密钥只显示前 8 位和后 4 位

```
正常日志：API 密钥: sk-xxxxxxxxxxxx
脱敏日志：API 密钥: sk-xxx***xxxx
```

---

## 7. 支持的云端供应商

### 7.1 已验证供应商

| 供应商 | 端点地址 | 推荐模型 | 状态 |
|--------|---------|---------|------|
| OpenAI | https://api.openai.com/v1 | text-embedding-3-small | ✅ 已验证 |
| DeepSeek | https://api.deepseek.com/v1 | deepseek-embeddings | ✅ 已验证 |
| 阿里云 | https://dashscope.aliyuncs.com/compatible-mode/v1 | text-embedding-v3 | ✅ 已验证 |
| Moonshot | https://api.moonshot.cn/v1 | moonshot-v1-embedding | ✅ 已验证 |

### 7.2 其他兼容供应商

所有兼容 OpenAI Embeddings API 标准的服务均可使用，用户只需配置：
- `api_key`：供应商提供的 API 密钥
- `endpoint`：供应商的 API 端点地址
- `model`：供应商支持的模型名称

---

## 8. 索引重建接口（独立端点，方案B）

### 8.1 设计说明

**重建原则**：切换嵌入模型必须重建索引

**独立状态管理**：索引重建使用独立的内存状态和API端点，与现有索引任务系统完全隔离。

**架构隔离**：

| 系统 | 数据来源 | 状态存储 | API端点 | 用途 |
|------|---------|---------|---------|------|
| **索引任务系统** | 扫描文件夹 | 数据库表 | `/api/index/*` | 创建新索引 |
| **索引重建系统** | 当前索引文件 | 内存（不持久化） | `/api/index/rebuild/*` | 换模型重建 |

**隔离原因**：
1. **数据隔离**：不污染现有100条索引任务记录
2. **语义隔离**：重建是"换模型"，不是"新建索引"
3. **状态隔离**：重建是临时操作，无需持久化
4. **接口隔离**：独立的端点，避免混淆

---

### 8.2 开始重建

**接口**：`POST /api/index/rebuild/start`

**说明**：开始索引重建，创建内存任务状态（不写数据库）。

---

#### 请求体

```json
{
  "model_config": {
    "model_type": "embedding",
    "provider": "cloud",
    "model_name": "text-embedding-3-small",
    "config": {
      "api_key": "sk-xxx",
      "endpoint": "https://api.openai.com/v1"
    }
  },
  "force": false
}
```

**请求参数说明**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| model_config | object | 是 | - | 新的嵌入模型配置 |
| force | boolean | 否 | false | 是否强制重建（跳过确认） |

---

#### 响应体（成功启动）

```json
{
  "success": true,
  "data": {
    "task_id": "rebuild_1711478400",
    "status": "running",
    "total_files": 10000,
    "previous_model": "BAAI/bge-m3",
    "new_model": "text-embedding-3-small",
    "estimated_time_minutes": 10
  }
}
```

**响应字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| task_id | string | 重建任务ID（内存） |
| status | string | 任务状态：running |
| total_files | integer | 总文件数 |
| previous_model | string | 原模型名称 |
| new_model | string | 新模型名称 |
| estimated_time_minutes | integer | 预计耗时（分钟） |

---

#### 响应体（已有任务进行中）

```json
{
  "success": false,
  "error": {
    "code": "REBUILD_JOB_RUNNING",
    "message": "重建任务正在进行",
    "details": {
      "task_id": "rebuild_1711478300",
      "status": "running",
      "progress": 35
    }
  }
}
```

---

### 8.3 查询重建状态

**接口**：`GET /api/index/rebuild/status`

**说明**：查询当前重建任务状态（内存查询，不访问数据库）。

---

#### 响应体（重建中）

```json
{
  "success": true,
  "data": {
    "task_id": "rebuild_1711478400",
    "status": "running",
    "progress": 45.5,
    "total_files": 10000,
    "processed_files": 4550,
    "failed_files": 5,
    "current_file": "/path/to/document.pdf",
    "elapsed_seconds": 270,
    "estimated_remaining_seconds": 330,
    "previous_model": {
      "provider": "local",
      "model_name": "BAAI/bge-m3"
    },
    "new_model": {
      "provider": "cloud",
      "model_name": "text-embedding-3-small"
    },
    "error_message": ""
  }
}
```

**响应字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| task_id | string | 任务ID |
| status | string | 状态：running/completed/failed/cancelled |
| progress | float | 进度百分比（0-100） |
| total_files | integer | 总文件数 |
| processed_files | integer | 已处理文件数 |
| failed_files | integer | 失败文件数 |
| current_file | string | 当前处理的文件路径 |
| elapsed_seconds | integer | 已用时间（秒） |
| estimated_remaining_seconds | integer | 预计剩余时间（秒） |
| previous_model | object | 原模型配置 |
| new_model | object | 新模型配置 |
| error_message | string | 错误信息（失败时） |

---

#### 响应体（无重建任务）

```json
{
  "success": true,
  "data": {
    "status": "none"
  }
}
```

---

### 8.4 取消重建

**接口**：`POST /api/index/rebuild/cancel`

**说明**：取消当前重建任务，自动回滚到原模型配置。

---

#### 请求体

```json
{}
```

---

#### 响应体（取消成功）

```json
{
  "success": true,
  "message": "重建任务已取消，已恢复到原模型配置",
  "data": {
    "task_id": "rebuild_1711478400",
    "status": "cancelled",
    "processed_files": 4550,
    "rollback_success": true,
    "restored_model": "BAAI/bge-m3"
  }
}
```

---

#### 响应体（无重建任务）

```json
{
  "success": false,
  "error": {
    "code": "NO_REBUILD_JOB",
    "message": "当前无重建任务"
  }
}
```

---

### 8.5 更新AI模型配置（扩展响应）

**接口**：`PUT /api/config/ai-model`

**变更说明**：当检测到嵌入模型变更时，响应中增加 `need_rebuild` 字段。

---

#### 响应体（需要重建索引）

```json
{
  "success": true,
  "data": {
    "id": 2,
    "model_type": "embedding",
    "provider": "cloud",
    "model_name": "text-embedding-3-small",
    "is_active": true,
    "need_rebuild": true,
    "rebuild_info": {
      "new_model": "text-embedding-3-small",
      "new_provider": "cloud",
      "file_count": 10000,
      "estimated_time_minutes": 10,
      "cloud_api_required": true,
      "previous_model": "BAAI/bge-m3"
    }
  }
}
```

**rebuild_info 字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| new_model | string | 新模型名称 |
| new_provider | string | 新提供商类型：local/cloud |
| file_count | integer | 需要重建的文件数量 |
| estimated_time_minutes | integer | 预计耗时（分钟） |
| cloud_api_required | boolean | 是否需要调用云端API |
| previous_model | string | 原模型名称 |

---

#### 响应体（无需重建）

```json
{
  "success": true,
  "data": {
    "id": 1,
    "model_type": "embedding",
    "provider": "local",
    "model_name": "BAAI/bge-m3",
    "is_active": true,
    "need_rebuild": false
  }
}
```

---

### 8.6 接口对照表

| 功能 | 索引任务系统 | 索引重建系统 | 说明 |
|------|-------------|-------------|------|
| 开始任务 | `POST /api/index/create` | `POST /api/index/rebuild/start` | 完全独立 |
| 查询状态 | `GET /api/index/status/{id}` | `GET /api/index/rebuild/status` | 独立端点 |
| 取消任务 | `DELETE /api/index/{id}` | `POST /api/index/rebuild/cancel` | 独立端点 |
| 任务列表 | `GET /api/index/list` | - | 重建无列表 |
| 数据来源 | 扫描文件夹 | 当前索引元数据 | 不同来源 |
| 状态存储 | 数据库表 | 内存（不持久化） | 不同存储 |

---

### 8.7 前端调用示例

```typescript
// 1. 保存嵌入模型配置，检测是否需要重建
const saveConfig = async (config: AIModelConfig) => {
  const response = await api.put('/api/config/ai-model', config);
  const result = await response.json();

  if (result.data.need_rebuild) {
    // 显示确认对话框
    showRebuildConfirm(result.data.rebuild_info);
  }
};

// 2. 确认后开始重建
const startRebuild = async () => {
  const response = await api.post('/api/index/rebuild/start', {
    model_config: newConfig,
    force: false
  });
  const result = await response.json();
  const taskId = result.data.task_id;

  // 开始轮询状态
  pollRebuildStatus();
};

// 3. 轮询重建状态
const pollRebuildStatus = async () => {
  const interval = setInterval(async () => {
    const response = await api.get('/api/index/rebuild/status');
    const result = await response.json();

    updateProgress(result.data);

    if (result.data.status === 'completed') {
      clearInterval(interval);
      showSuccess('索引重建完成');
    } else if (result.data.status === 'failed') {
      clearInterval(interval);
      showError(result.data.error_message);
    }
  }, 1000);
};

// 4. 取消重建
const cancelRebuild = async () => {
  const response = await api.post('/api/index/rebuild/cancel');
  const result = await response.json();

  if (result.success) {
    showInfo('已取消，已恢复到原模型配置');
  }
};

// 注意：索引任务系统的接口保持不变
const createIndex = async (folderPath: string) => {
  // 这是创建新索引，与重建完全独立
  const response = await api.post('/api/index/create', {
    folder_path: folderPath
  });
  // ... 返回 index_id
};

const getIndexStatus = async (indexId: number) => {
  // 查询索引任务状态，与重建状态完全独立
  const response = await api.get(`/api/index/status/${indexId}`);
  // ...
};
```

---

## 9. 附录

### 9.1 相关文档
    "task_type": "rebuild",
    "message": "索引重建任务已创建",
    "rebuild_info": {
      "new_model": "text-embedding-3-small",
      "new_provider": "cloud",
      "total_files": 10000,
      "estimated_time_minutes": 10,
      "cloud_api_required": true,
      "previous_backup": "index.backup/"
    }
  }
}
```

**响应字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| task_type | string | 任务类型：create（新建）/rebuild（重建） |
| rebuild_info | object | 重建相关信息（仅在重建模式下返回） |
| rebuild_info.new_model | string | 新嵌入模型名称 |
| rebuild_info.new_provider | string | 新提供商类型：local/cloud |
| rebuild_info.total_files | integer | 需要重建的文件数量 |
| rebuild_info.estimated_time_minutes | integer | 预计耗时（分钟） |
| rebuild_info.cloud_api_required | boolean | 是否需要调用云端API |
| rebuild_info.previous_backup | string | 备份路径 |

---

#### 响应体（已有任务进行中）

```json
{
  "success": false,
  "error": {
    "code": "INDEX_JOB_RUNNING",
    "message": "索引任务正在运行",
    "details": {
      "index_id": 1,
      "status": "processing",
      "progress": 35,
      "task_type": "rebuild"
    }
  }
}
```

---

## 9. 附录

### 9.1 相关文档

- [主接口文档](../../接口文档.md)
- [数据库设计文档](../../数据库设计文档.md)
- [云端嵌入模型 PRD](./embedding-openai-01-prd.md)
- [云端嵌入模型技术方案](./embedding-openai-03-技术方案.md)

---

**文档版本**：v1.0
**维护者**：AI 助手
**最后更新**：2026-03-26
