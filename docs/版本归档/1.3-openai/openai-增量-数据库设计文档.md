# OpenAI兼容大模型服务 - 数据库设计文档增量

> **文档类型**：增量数据库设计文档
> **基础版本**：基于 [主数据库设计文档](../../数据库设计文档.md)
> **特性状态**：已完成
> **创建时间**：2026-02-28
> **最后更新**：2026-02-28

---

## 1. 增量说明

### 1.1 概述

本文档描述了 OpenAI 兼容大模型服务特性对数据库的增量变更。

**核心声明**：✅ **无需数据库迁移**

- 数据库表结构**完全不变**
- 复用现有 `ai_models` 表
- `provider` 字段已支持 `local/cloud` 值
- `config_json` 字段以 JSON 格式灵活存储不同配置

### 1.2 设计理念

**配置即JSON**：通过 `config_json` 字段的 JSON 灵活性，支持不同 provider 的差异化配置，无需修改表结构。

| Provider | config_json 结构 |
|----------|------------------|
| local | `{"base_url": "...", "timeout": 30, ...}` |
| cloud | `{"api_key": "...", "endpoint": "...", "model": "...", ...}` |

---

## 2. 表结构说明（复用现有表）

### 2.1 ai_models AI模型配置表

**表结构（无变更）**：

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 主键，唯一标识模型配置 |
| model_type | TEXT | NOT NULL | 模型类型：embedding/speech/vision/llm |
| provider | TEXT | NOT NULL | **提供商类型：local/cloud** ✨ 已支持 |
| model_name | TEXT | NOT NULL | 模型名称（如qwen2.5:1.5b、qwen-turbo） |
| config_json | TEXT | NOT NULL | **JSON格式的模型配置参数** ✨ 灵活存储 |
| is_active | BOOLEAN | DEFAULT TRUE | 是否启用该模型 |
| created_at | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP | 配置创建时间 |
| updated_at | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP | 配置更新时间 |

**索引（无变更）**：

| 索引名 | 字段 | 类型 |
|--------|------|------|
| PRIMARY | id | 主键 |
| UNIQUE | model_type, provider, model_name | 唯一约束 |
| INDEX | model_type | 普通索引 |
| INDEX | provider | 普通索引 |
| INDEX | is_active | 普通索引 |

---

## 3. config_json 字段结构

### 3.1 provider='local' 的 JSON 结构

```json
{
  "base_url": "http://localhost:11434",
  "timeout": 30,
  "temperature": 0.7,
  "num_ctx": 2048
}
```

**字段说明**：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| base_url | string | 否 | http://localhost:11434 | Ollama 服务地址 |
| timeout | integer | 否 | 30 | 请求超时时间（秒） |
| temperature | float | 否 | 0.7 | 温度参数（0.0-2.0） |
| num_ctx | integer | 否 | 2048 | 上下文窗口大小 |

### 3.2 provider='cloud' 的 JSON 结构（新增）

```json
{
  "api_key": "sk-xxxxxxxxxxxx",
  "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1",
  "model": "qwen-turbo",
  "timeout": 60,
  "temperature": 0.7,
  "max_tokens": 2048,
  "top_p": 1.0
}
```

**字段说明**：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| api_key | string | **是** | - | API 密钥（加密存储） |
| endpoint | string | 否 | https://api.openai.com/v1 | API 端点地址 |
| model | string | **是** | - | 模型名称 |
| timeout | integer | 否 | 60 | 请求超时时间（秒） |
| temperature | float | 否 | 0.7 | 温度参数（0.0-2.0） |
| max_tokens | integer | 否 | 2048 | 最大生成 token 数 |
| top_p | float | 否 | 1.0 | 核采样参数（0.0-1.0） |

---

## 4. 数据示例

### 4.1 本地 Ollama 模型配置示例

**数据库记录**：

| id | model_type | provider | model_name | config_json | is_active |
|----|------------|----------|------------|-------------|-----------|
| 1 | llm | local | qwen2.5:1.5b | `{"base_url":"http://localhost:11434","timeout":30,"temperature":0.7}` | true |

**SQL 插入语句**：

```sql
INSERT INTO ai_models (model_type, provider, model_name, config_json, is_active)
VALUES (
    'llm',
    'local',
    'qwen2.5:1.5b',
    '{"base_url": "http://localhost:11434", "timeout": 30, "temperature": 0.7}',
    1
);
```

### 4.2 云端 OpenAI 兼容模型配置示例（新增）

**数据库记录**：

| id | model_type | provider | model_name | config_json | is_active |
|----|------------|----------|------------|-------------|-----------|
| 2 | llm | cloud | qwen-turbo | `{"api_key":"***","endpoint":"https://dashscope.aliyuncs.com/compatible-mode/v1","model":"qwen-turbo","timeout":60}` | false |

> **安全说明**：`api_key` 在数据库中加密存储，查询时显示脱敏值 `sk-****...****1234`

**SQL 插入语句**：

```sql
INSERT INTO ai_models (model_type, provider, model_name, config_json, is_active)
VALUES (
    'llm',
    'cloud',
    'qwen-turbo',
    '{"api_key": "sk-xxxxxxxxxxxx", "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1", "model": "qwen-turbo", "timeout": 60}',
    0
);
```

### 4.3 多供应商配置示例

| id | model_type | provider | model_name | config_json | is_active |
|----|------------|----------|------------|-------------|-----------|
| 1 | llm | local | qwen2.5:1.5b | `{"base_url":"http://localhost:11434"}` | true |
| 2 | llm | cloud | gpt-3.5-turbo | `{"api_key":"***","endpoint":"https://api.openai.com/v1","model":"gpt-3.5-turbo"}` | false |
| 3 | llm | cloud | qwen-turbo | `{"api_key":"***","endpoint":"https://dashscope.aliyuncs.com/compatible-mode/v1","model":"qwen-turbo"}` | false |
| 4 | llm | cloud | deepseek-chat | `{"api_key":"***","endpoint":"https://api.deepseek.com/v1","model":"deepseek-chat"}` | false |

---

## 5. 安全设计

### 5.1 API 密钥加密存储

**加密方案**：使用 Fernet 对称加密

```python
# 加密工具函数
import base64
from cryptography.fernet import Fernet

# 生成密钥（首次启动时生成并保存到环境变量）
ENCRYPTION_KEY = Fernet.generate_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

def encrypt_api_key(api_key: str) -> str:
    """加密 API 密钥"""
    encrypted = cipher_suite.encrypt(api_key.encode())
    return base64.b64encode(encrypted).decode()

def decrypt_api_key(encrypted_key: str) -> str:
    """解密 API 密钥"""
    encrypted = base64.b64decode(encrypted_key.encode())
    return cipher_suite.decrypt(encrypted).decode()
```

**存储流程**：

```
用户输入 API 密钥
    ↓
应用层：encrypt_api_key(api_key)
    ↓
数据库：存储加密后的密钥
    ↓
应用层：decrypt_api_key(encrypted_key)
    ↓
API调用：使用原始密钥
```

### 5.2 密钥脱敏显示

**脱敏规则**：显示前7位 + `...` + 后4位

```python
def mask_api_key(api_key: str) -> str:
    """脱敏 API 密钥"""
    if not api_key or len(api_key) < 10:
        return "***"
    return f"{api_key[:7]}...{api_key[-4:]}"

# 示例：
# sk-abc123def456789xyz012
# ↓
# sk-abc1...x012
```

**使用场景**：
- API 响应中的 `config_json` 字段
- 日志输出
- 前端显示

### 5.3 加密存储实现

**数据库存储示例**：

| 存储前 | 存储后（加密） | 显示时（脱敏） |
|--------|---------------|---------------|
| `sk-abc123def456789` | `gAAAAABl...xyz=` (加密) | `sk-abc1...6789` (脱敏) |

**代码示例**：

```python
# 保存配置时加密
config = {
    "api_key": encrypt_api_key(user_input_api_key),  # 加密存储
    "endpoint": user_input_endpoint,
    "model": user_input_model
}
config_json = json.dumps(config)

# 存入数据库
INSERT INTO ai_models (config_json) VALUES (config_json)

# 读取配置时解密
config = json.loads(row.config_json)
api_key = decrypt_api_key(config["api_key"])  # 解密使用

# 返回给前端时脱敏
config["api_key"] = mask_api_key(api_key)
```

---

## 6. 数据操作

### 6.1 查询操作

**查询所有 LLM 模型配置**：

```sql
SELECT id, model_type, provider, model_name, config_json, is_active
FROM ai_models
WHERE model_type = 'llm'
ORDER BY created_at DESC;
```

**查询启用的云端模型**：

```sql
SELECT id, model_name, config_json
FROM ai_models
WHERE model_type = 'llm'
  AND provider = 'cloud'
  AND is_active = 1;
```

**查询特定供应商的配置**：

```sql
SELECT id, model_name, config_json
FROM ai_models
WHERE provider = 'cloud'
  AND json_extract(config_json, '$.endpoint') LIKE '%dashscope%';
```

### 6.2 更新操作

**更新云端模型配置**：

```sql
UPDATE ai_models
SET config_json = '{
    "api_key": "sk-new-key-encrypted",
    "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model": "qwen-turbo",
    "timeout": 60
}',
updated_at = CURRENT_TIMESTAMP
WHERE id = 2;
```

**切换启用状态**：

```sql
-- 启用云端模型
UPDATE ai_models SET is_active = 1 WHERE id = 2;

-- 禁用本地模型
UPDATE ai_models SET is_active = 0 WHERE id = 1;
```

### 6.3 删除操作

**删除模型配置**：

```sql
DELETE FROM ai_models WHERE id = 2;
```

---

## 7. 数据验证

### 7.1 应用层验证

由于 SQLite 不支持 JSON 字段验证，需要在应用层实现：

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, Literal

class LocalLLMConfig(BaseModel):
    """本地 LLM 配置"""
    base_url: str = "http://localhost:11434"
    timeout: int = Field(default=30, ge=1, le=300)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

class CloudLLMConfig(BaseModel):
    """云端 LLM 配置"""
    api_key: str = Field(..., min_length=20, max_length=128)
    endpoint: str = "https://api.openai.com/v1"
    model: str = Field(..., min_length=1, max_length=100)
    timeout: int = Field(default=60, ge=1, le=600)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=1, le=128000)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)

    @validator('api_key')
    def validate_api_key(cls, v):
        if not v.startswith('sk-'):
            raise ValueError('API密钥必须以 sk- 开头')
        return v

    @validator('endpoint')
    def validate_endpoint(cls, v):
        if not v.startswith('https://'):
            raise ValueError('端点地址必须使用 HTTPS')
        return v
```

### 7.2 数据库触发器（可选）

```sql
-- 检查 provider 值
CREATE TRIGGER validate_provider
BEFORE INSERT ON ai_models
BEGIN
    SELECT CASE
        WHEN NEW.provider NOT IN ('local', 'cloud') THEN
            RAISE(ABORT, 'Invalid provider: must be local or cloud')
    END;
END;

-- 确保 JSON 格式正确（应用层实现，SQLite不支持）
```

---

## 8. 数据迁移

### 8.1 迁移说明

**无需数据库迁移**：

- ✅ 表结构完全不变
- ✅ 索引完全不变
- ✅ `provider` 字段已支持 `cloud` 值
- ✅ `config_json` 字段已支持 JSON 格式

### 8.2 兼容性验证

**验证现有数据**：

```sql
-- 检查现有 provider 值
SELECT DISTINCT provider FROM ai_models;

-- 预期结果：
-- provider
-- ---------
-- local
```

**验证新增配置**：

```sql
-- 插入测试数据
INSERT INTO ai_models (model_type, provider, model_name, config_json, is_active)
VALUES (
    'llm',
    'cloud',
    'qwen-turbo',
    '{"api_key": "sk-test", "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1", "model": "qwen-turbo"}',
    0
);

-- 验证插入
SELECT * FROM ai_models WHERE provider = 'cloud';
```

---

## 9. 性能考虑

### 9.1 索引使用

**现有索引已覆盖查询场景**：

| 查询场景 | 使用索引 |
|---------|---------|
| 查询特定模型类型 | `INDEX (model_type)` |
| 查询特定提供商 | `INDEX (provider)` |
| 查询启用状态 | `INDEX (is_active)` |
| 组合查询 | `UNIQUE (model_type, provider, model_name)` |

**查询优化示例**：

```sql
-- 优化前：全表扫描
SELECT * FROM ai_models WHERE provider = 'cloud';

-- 优化后：使用索引
-- EXPLAIN QUERY PLAN SELECT * FROM ai_models WHERE provider = 'cloud';
-- 预期：SEARCH ai_models USING INDEX idx_ai_models_provider
```

### 9.2 JSON 查询性能

**JSON 提取操作**：

```sql
-- 提取 endpoint
SELECT json_extract(config_json, '$.endpoint') as endpoint
FROM ai_models
WHERE provider = 'cloud';

-- 提取 model
SELECT json_extract(config_json, '$.model') as model
FROM ai_models
WHERE provider = 'cloud';
```

**性能建议**：
- JSON 查询比直接字段查询慢约 10-20%
- 建议在应用层解析 JSON，避免数据库端 JSON 操作
- 对于频繁查询的字段（如 endpoint），可考虑应用层缓存

---

## 10. 备份与恢复

### 10.1 数据备份

**备份 ai_models 表**：

```bash
# 使用 SQLite 命令行工具
sqlite3 data/database/xiaoyao_search.db ".dump ai_models" > ai_models_backup.sql

# 或使用 Python
python -c "
import sqlite3
conn = sqlite3.connect('data/database/xiaoyao_search.db')
with open('ai_models_backup.json', 'w') as f:
    for row in conn.execute('SELECT * FROM ai_models'):
        f.write(str(row))
conn.close()
"
```

### 10.2 数据恢复

**恢复 ai_models 表**：

```bash
# 从 SQL 文件恢复
sqlite3 data/database/xiaoyao_search.db < ai_models_backup.sql

# 或手动插入
sqlite3 data/database/xiaoyao_search.db "
INSERT INTO ai_models (model_type, provider, model_name, config_json, is_active)
VALUES ('llm', 'cloud', 'qwen-turbo', '{\"api_key\": \"sk-...\"}', 0);
"
```

---

## 11. 监控与维护

### 11.1 配置统计

**统计模型配置分布**：

```sql
SELECT
    provider,
    model_type,
    COUNT(*) as count,
    SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_count
FROM ai_models
GROUP BY provider, model_type;
```

**预期结果**：

| provider | model_type | count | active_count |
|----------|------------|-------|--------------|
| local | llm | 1 | 1 |
| cloud | llm | 3 | 0 |

### 11.2 配置健康检查

**检查云端模型配置完整性**：

```sql
SELECT
    id,
    model_name,
    CASE
        WHEN json_extract(config_json, '$.api_key') IS NULL THEN 'Missing api_key'
        WHEN json_extract(config_json, '$.endpoint') IS NULL THEN 'Missing endpoint'
        WHEN json_extract(config_json, '$.model') IS NULL THEN 'Missing model'
        ELSE 'OK'
    END as status
FROM ai_models
WHERE provider = 'cloud';
```

### 11.3 配置变更历史

**查询最近更新的配置**：

```sql
SELECT
    id,
    provider,
    model_name,
    updated_at,
    CASE
        WHEN updated_at > datetime('now', '-7 days') THEN 'Recent'
        ELSE 'Old'
    END as age
FROM ai_models
ORDER BY updated_at DESC
LIMIT 10;
```

---

## 12. 相关文档

- [PRD文档](./openai-01-prd.md) - 产品需求文档
- [技术方案](./openai-03-技术方案.md) - 技术实现方案
- [接口文档增量](./openai-增量-接口文档.md) - 接口变更说明
- [架构决策](../../架构决策/AD-20260228-01-OpenAI兼容大模型服务.md) - 架构决策文档
- [主数据库设计文档](../../数据库设计文档.md) - 完整数据库设计

---

## 13. 附录

### 13.1 完整表结构 SQL

```sql
CREATE TABLE IF NOT EXISTS ai_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_type TEXT NOT NULL,
    provider TEXT NOT NULL,
    model_name TEXT NOT NULL,
    config_json TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(model_type, provider, model_name)
);

CREATE INDEX IF NOT EXISTS idx_ai_models_model_type ON ai_models(model_type);
CREATE INDEX IF NOT EXISTS idx_ai_models_provider ON ai_models(provider);
CREATE INDEX IF NOT EXISTS idx_ai_models_is_active ON ai_models(is_active);
```

### 13.2 测试数据

```sql
-- 本地 Ollama 配置
INSERT INTO ai_models (model_type, provider, model_name, config_json, is_active)
VALUES
    ('llm', 'local', 'qwen2.5:1.5b', '{"base_url": "http://localhost:11434", "timeout": 30, "temperature": 0.7}', 1),
    ('llm', 'local', 'qwen2.5:3b', '{"base_url": "http://localhost:11434", "timeout": 60, "temperature": 0.5}', 0);

-- 云端 OpenAI 兼容配置
INSERT INTO ai_models (model_type, provider, model_name, config_json, is_active)
VALUES
    ('llm', 'cloud', 'gpt-3.5-turbo', '{"api_key": "sk-xxx", "endpoint": "https://api.openai.com/v1", "model": "gpt-3.5-turbo"}', 0),
    ('llm', 'cloud', 'qwen-turbo', '{"api_key": "sk-xxx", "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1", "model": "qwen-turbo"}', 0),
    ('llm', 'cloud', 'deepseek-chat', '{"api_key": "sk-xxx", "endpoint": "https://api.deepseek.com/v1", "model": "deepseek-chat"}', 0);
```

---

**文档版本**：v1.0
**维护者**：AI助手
**最后更新**：2026-02-28

> **使用说明**：
> 1. 本文档为增量数据库设计文档，描述与主数据库设计文档的差异
> 2. **核心结论**：无需数据库迁移，完全复用现有 ai_models 表
> 3. 数据库表结构 100% 向后兼容
> 4. 实施周期：0 天（无需数据库变更）
