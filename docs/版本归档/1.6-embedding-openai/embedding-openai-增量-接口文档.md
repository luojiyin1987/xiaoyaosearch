# 云端嵌入模型调用能力 - 接口文档增量

> **文档类型**：增量接口文档
> **基础版本**：基于 [主接口文档](../../接口文档.md)
> **特性状态**：已完成
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
- **新增接口**：全量重建索引接口（复用现有索引任务系统）

### 1.2 向后兼容性

**兼容性声明**：✅ 完全向后兼容

- 现有本地 BGE-M3 配置保持不变
- 新增的云端配置为可选功能
- 数据库表结构无变更
- **向量维度**：使用模型原始维度，不做归一化处理
- **索引重建**：切换模型后需手动重建索引（在索引管理页操作）

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

### 4.3 新增翻译键

**后端翻译键**（`backend/app/locales/`）：

| 键名 | 中文示例 | 英文示例 |
|------|---------|---------|
| `model.cloud_embedding_success` | 云端嵌入模型测试成功，向量维度: {dimension} | Cloud embedding model test successful, vector dimension: {dimension} |
| `model.cloud_auth_failed` | 云端API认证失败：{error} | Cloud API authentication failed: {error} |
| `index.rebuild_all_started` | 已启动 {count} 个重建任务 | Started {count} rebuild tasks |
| `index.rebuild_all_failed` | 全量重建失败 | Full rebuild failed |
| `index.rebuild_all_partial` | 重建完成：成功 {completed} 个，失败 {failed} 个 | Rebuild completed: {completed} succeeded, {failed} failed |
| `index.rebuild_all_complete` | 全量重建完成！成功完成 {count} 个任务 | Full rebuild completed! {count} tasks succeeded |
| `index.no_completed_jobs` | 未找到已完成的历史索引任务，无法重建 | No completed index jobs found, cannot rebuild |
| `index.rebuild_all_warning` | 将清空所有索引并按历史任务逐一重建，预计耗时较长，是否继续？ | This will clear all indexes and rebuild by historical tasks, taking a long time, continue? |

**前端翻译键**（`frontend/src/locale/lang/`）：

| 键名 | 中文示例 | 英文示例 |
|------|---------|---------|
| `embedding.providerLocal` | 本地（推荐，免费离线） | Local (Recommended, Free & Offline) |
| `embedding.providerCloud` | 云端（高质量，需API密钥） | Cloud (High quality, requires API key) |
| `embedding.cloudDataSafe` | 您的本地文件和索引数据存储在本地，不会上传 | Your local files and index data are stored locally, not uploaded |
| `embedding.testConnection` | 测试连接 | Test Connection |
| `embedding.modelChanged` | 嵌入模型已更改 | Embedding model has changed |
| `embedding.rebuildTip` | 建议重启应用后在索引管理中重建索引 | Recommended to restart the app and rebuild indexes in index management |
| `index.rebuildAll` | 全量重建索引 | Rebuild All Indexes |
| `index.rebuildAllConfirm` | 确认全量重建 | Confirm Full Rebuild |
| `index.rebuildAllWarning` | 将清空所有索引并按历史任务逐一重建，预计耗时较长 | This will clear all indexes and rebuild by historical tasks, taking a long time |
| `index.rebuildProgress` | 重建进度 | Rebuild Progress |
| `index.processed` | 已处理 | Processed |
| `index.jobStatus.pending` | 等待中 | Pending |
| `index.jobStatus.processing` | 处理中 | Processing |
| `index.jobStatus.completed` | 已完成 | Completed |
| `index.jobStatus.failed` | 失败 | Failed |

---

## 5. 错误码扩展

### 5.1 新增错误码

| 错误码 | HTTP状态码 | 说明 | 建议处理 |
|--------|-----------|------|---------|
| EMBEDDING_CLOUD_AUTH_FAILED | 401 | 云端 API 认证失败 | 检查 API 密钥 |
| EMBEDDING_CLOUD_MODEL_NOT_FOUND | 404 | 云端模型不存在 | 检查模型名称 |
| EMBEDDING_CLOUD_RATE_LIMIT | 429 | 云端 API 请求频率超限 | 降低请求频率或升级套餐 |
| EMBEDDING_CLOUD_TIMEOUT | 504 | 云端 API 请求超时 | 增加超时时间或检查网络 |

---

## 6. 业务逻辑说明

### 6.1 本地/云端互斥切换

**规则**：
1. 同一时间只能有一个活跃的嵌入模型配置
2. 切换到云端时，自动卸载本地模型
3. 切换到本地时，自动关闭云端服务
4. **切换模型后需手动重建索引**（在索引管理页操作）

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
                                        └─ 返回成功
                                        │
                                        ↓
                                    前端显示引导提示
                                        │
                                        ↓
                                    用户前往索引管理页
                                        │
                                        ↓
                                    手动点击"全量重建索引"
```

---

## 7. 安全考虑

### 7.1 API 密钥保护

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

### 7.2 日志脱敏

**规则**：日志中 API 密钥只显示前 8 位和后 4 位

```
正常日志：API 密钥: sk-xxxxxxxxxxxx
脱敏日志：API 密钥: sk-xxx***xxxx
```

---

## 8. 支持的云端供应商

### 8.1 已验证供应商

| 供应商 | 端点地址 | 推荐模型 | 状态 |
|--------|---------|---------|------|
| OpenAI | https://api.openai.com/v1 | text-embedding-3-small | ✅ 已验证 |
| DeepSeek | https://api.deepseek.com/v1 | deepseek-embeddings | ✅ 已验证 |
| 阿里云 | https://dashscope.aliyuncs.com/compatible-mode/v1 | text-embedding-v3 | ✅ 已验证 |
| Moonshot | https://api.moonshot.cn/v1 | moonshot-v1-embedding | ✅ 已验证 |

### 8.2 其他兼容供应商

所有兼容 OpenAI Embeddings API 标准的服务均可使用，用户只需配置：
- `api_key`：供应商提供的 API 密钥
- `endpoint`：供应商的 API 端点地址
- `model`：供应商支持的模型名称

---

## 9. 全量重建索引接口

### 9.1 设计说明

**方案**：简化方案 - 复用现有索引任务系统

**核心原理**：
- 清空索引文件后，为每个历史已完成的索引任务创建新的重建任务
- 利用现有的 `run_full_index_task` 和 `IndexJobModel`
- 通过 BackgroundTasks 自动排队执行
- 复用现有的 `/api/index/status/{id}` 查询进度

**与现有系统的关系**：

| 方面 | 说明 |
|------|------|
| 数据来源 | 查询 `index_jobs` 表中 `status='completed'` 的历史任务 |
| 去重逻辑 | 按 `folder_path` 去重，每个路径创建一个重建任务 |
| 任务创建 | 创建新的 `IndexJobModel` 记录 |
| 任务执行 | 调用现有的 `run_full_index_task` |
| 进度查询 | 复用 `/api/index/status/{id}` 端点 |

---

### 9.2 全量重建索引

**接口**：`POST /api/index/rebuild-all`

**说明**：清空所有索引文件，按历史任务创建重建任务并排队执行。

---

#### 请求体

```http
POST /api/index/rebuild-all
Content-Type: application/json
```

**请求参数**：无

---

#### 响应体（成功启动）

```json
{
  "success": true,
  "data": [
    {
      "index_id": 101,
      "folder_path": "D:\\Documents",
      "status": "pending",
      "total_files": 5000,
      "processed_files": 0,
      "progress": 0,
      "created_at": "2026-03-26T10:00:00"
    },
    {
      "index_id": 102,
      "folder_path": "E:\\Projects",
      "status": "pending",
      "total_files": 3000,
      "processed_files": 0,
      "progress": 0,
      "created_at": "2026-03-26T10:00:00"
    }
  ],
  "message": "已启动 2 个重建任务"
}
```

**响应字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| index_id | integer | 索引任务ID |
| folder_path | string | 文件夹路径 |
| status | string | 任务状态：pending/processing/completed/failed |
| total_files | integer | 总文件数 |
| processed_files | integer | 已处理文件数 |
| progress | float | 进度百分比（0-100） |

---

#### 响应体（无历史任务）

```json
{
  "success": false,
  "error": {
    "code": "NO_COMPLETED_JOBS",
    "message": "未找到已完成的历史索引任务，无法重建"
  }
}
```

---

#### 响应体（清空索引失败）

```json
{
  "success": false,
  "error": {
    "code": "CLEAR_INDEX_FAILED",
    "message": "清空索引文件失败",
    "details": {
      "error": "权限不足或文件被占用"
    }
  }
}
```

---

### 9.3 查询任务状态（复用现有接口）

**接口**：`GET /api/index/status/{index_id}`

**说明**：复用现有的索引任务状态查询接口。

---

#### 响应体（处理中）

```json
{
  "success": true,
  "data": {
    "index_id": 101,
    "folder_path": "D:\\Documents",
    "status": "processing",
    "total_files": 5000,
    "processed_files": 2500,
    "progress": 50.0,
    "current_file": "D:\\Documents\\report.pdf",
    "error_message": ""
  }
}
```

---

### 9.4 前端调用示例

```typescript
// 1. 切换模型后显示引导
const handleModelChanged = () => {
  Modal.info({
    title: t('embedding.modelChanged'),
    content: (
      <div>
        <p>{t('embedding.rebuildTip')}</p>
        <Space>
          <Button onClick={restartApp}>{t('common.restartApp')}</Button>
          <Button onClick={goToIndexManagement}>{t('embedding.goToIndex')}</Button>
        </Space>
      </div>
    )
  });
};

// 2. 在索引管理页点击全量重建
const handleRebuildAll = async () => {
  Modal.confirm({
    title: t('index.rebuildAllConfirm'),
    content: t('index.rebuildAllWarning'),
    okButtonProps: { danger: true },
    onOk: async () => {
      const response = await fetch('/api/index/rebuild-all', {
        method: 'POST'
      });
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
      fetch(`/api/index/status/${job.index_id}`).then(res => res.json())
    );
    const results = await Promise.all(promises);

    rebuildJobs.value = results.map(r => r.data);

    // 检查是否全部完成
    const allDone = rebuildJobs.value.every(
      job => job.status === 'completed' || job.status === 'failed'
    );

    if (allDone) {
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

## 10. 附录

### 10.1 相关文档

- [主接口文档](../../接口文档.md)
- [数据库设计文档](../../数据库设计文档.md)
- [云端嵌入模型 PRD](./embedding-openai-01-prd.md)
- [云端嵌入模型技术方案](./embedding-openai-03-技术方案.md)
- [全量重建索引实施方案](./embedding-openai-全量重建索引-实施方案.md)

---

**文档版本**：v2.0（简化方案）
**维护者**：AI 助手
**最后更新**：2026-03-26
