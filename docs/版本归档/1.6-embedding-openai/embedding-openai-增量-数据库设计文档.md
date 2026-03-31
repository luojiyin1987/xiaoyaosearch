# 云端嵌入模型调用能力 - 数据库设计文档增量

> **文档类型**：增量数据库设计文档
> **基础版本**：基于 [主数据库设计文档](../../数据库设计文档.md)
> **特性状态**：规划中
> **创建时间**：2026-03-26
> **最后更新**：2026-03-26

---

## 1. 增量说明

### 1.1 概述

本文档描述了云端嵌入模型调用能力特性对数据库的增量变更。

**核心声明**：✅ **无需数据库迁移**

- 数据库表结构**完全不变**
- 复用现有 `ai_models` 表
- `provider` 字段已支持 `local/cloud` 值
- `config_json` 字段以 JSON 格式灵活存储不同配置

### 1.2 设计理念

**配置即JSON**：通过 `config_json` 字段的 JSON 灵活性，支持不同 provider 的差异化配置，无需修改表结构。

| Provider | model_type | config_json 结构 |
|----------|-----------|------------------|
| local | embedding | `{"device": "cpu"}` |
| cloud | embedding | `{"api_key": "...", "endpoint": "...", "model": "...", "timeout": 30, "batch_size": 100}` |

---

## 2. 表结构说明（复用现有表）

### 2.1 ai_models AI模型配置表

**表结构（无变更）**：

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 主键，唯一标识模型配置 |
| model_type | TEXT | NOT NULL | 模型类型：embedding/speech/vision/llm |
| provider | TEXT | NOT NULL | **提供商类型：local/cloud** ✨ 已支持 |
| model_name | TEXT | NOT NULL | 模型名称（如 BAAI/bge-m3、text-embedding-3-small） |
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

### 3.1 provider='local' 的 JSON 结构（现有，无变更）

```json
{
  "device": "cpu"
}
```

**字段说明**：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| device | string | 否 | cpu | 运行设备：cpu 或 cuda |

---

### 3.2 provider='cloud' 的 JSON 结构（新增）

```json
{
  "api_key": "sk-xxxxxxxxxxxx",
  "endpoint": "https://api.openai.com/v1",
  "model": "text-embedding-3-small",
  "timeout": 30,
  "batch_size": 100,
  "max_retries": 3
}
```

**字段说明**：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| api_key | string | 是 | - | API 密钥（AES 加密存储） |
| endpoint | string | 否 | https://api.openai.com/v1 | API 端点地址 |
| model | string | 是 | - | 模型名称 |
| timeout | integer | 否 | 30 | 请求超时时间（秒） |
| batch_size | integer | 否 | 100 | 批处理大小 |
| max_retries | integer | 否 | 3 | 最大重试次数 |

---

## 4. 数据示例

### 4.1 本地嵌入模型配置（现有，无变更）

```sql
INSERT INTO ai_models (model_type, provider, model_name, config_json, is_active)
VALUES (
    'embedding',
    'local',
    'BAAI/bge-m3',
    '{
        "device": "cpu"
    }',
    false
);
```

---

### 4.2 云端嵌入模型配置（新增）

```sql
-- OpenAI 官方
INSERT INTO ai_models (model_type, provider, model_name, config_json, is_active)
VALUES (
    'embedding',
    'cloud',
    'text-embedding-3-small',
    '{
        "api_key": "sk-xxxxxxxxxxxx",
        "endpoint": "https://api.openai.com/v1",
        "model": "text-embedding-3-small",
        "timeout": 30,
        "batch_size": 100
    }',
    true
);

-- DeepSeek
INSERT INTO ai_models (model_type, provider, model_name, config_json, is_active)
VALUES (
    'embedding',
    'cloud',
    'deepseek-embeddings',
    '{
        "api_key": "sk-xxxxxxxxxxxx",
        "endpoint": "https://api.deepseek.com/v1",
        "model": "deepseek-embeddings"
    }',
    false
);

-- 阿里云通义千问
INSERT INTO ai_models (model_type, provider, model_name, config_json, is_active)
VALUES (
    'embedding',
    'cloud',
    'text-embedding-v3',
    '{
        "api_key": "sk-xxxxxxxxxxxx",
        "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "text-embedding-v3"
    }',
    false
);
```

---

## 5. 业务约束

### 5.1 本地/云端互斥约束

**规则**：对于 `model_type='embedding'` 的配置，同一时间只能有一个 `is_active=true` 的记录。

**实现方式**：应用层约束

```python
def update_embedding_model(config: AIModelConfig):
    """更新嵌入模型配置，确保互斥性"""

    # 1. 验证配置
    if config.model_type != "embedding":
        raise ValueError("此接口仅支持嵌入模型配置")

    if config.provider not in ["local", "cloud"]:
        raise ValueError("provider 必须是 'local' 或 'cloud'")

    # 2. 测试连接
    if config.provider == "cloud":
        test_result = await test_cloud_connection(config.config)
        if not test_result.success:
            raise ValueError(f"连接测试失败: {test_result.error}")

    # 3. 更新数据库（原子操作）
    with db.transaction():
        # 3.1 将所有现有嵌入模型设为不活跃
        db.execute(
            "UPDATE ai_models SET is_active = false WHERE model_type = 'embedding'"
        )

        # 3.2 插入或更新新配置
        db.execute(
            """
            INSERT INTO ai_models (model_type, provider, model_name, config_json, is_active)
            VALUES (?, ?, ?, ?, true)
            ON CONFLICT(model_type, provider, model_name)
            DO UPDATE SET is_active = true, config_json = ?, updated_at = CURRENT_TIMESTAMP
            """,
            (config.model_type, config.provider, config.model_name,
             json.dumps(config.config), json.dumps(config.config))
        )

    # 4. 重新加载模型
    await reload_embedding_model()
```

---

### 5.2 API 密钥加密约束

**规则**：`api_key` 字段在存储到 `config_json` 前必须加密。

**加密实现**：

```python
from cryptography.fernet import Fernet
import os
import base64

class APIKeyEncryption:
    """API 密钥加密/解密工具"""

    def __init__(self):
        # 从环境变量获取加密密钥
        key_str = os.getenv("API_ENCRYPTION_KEY")
        if not key_str:
            # 如果未设置，生成新密钥并提示
            key = Fernet.generate_key()
            logger.warning(f"API_ENCRYPTION_KEY 未设置，已生成新密钥: {key.decode()}")
            logger.warning("请将此密钥保存到环境变量 API_ENCRYPTION_KEY")
            key_str = key.decode()

        self.fernet = Fernet(key_str.encode())

    def encrypt(self, api_key: str) -> str:
        """加密 API 密钥"""
        encrypted = self.fernet.encrypt(api_key.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, encrypted_key: str) -> str:
        """解密 API 密钥"""
        encrypted = base64.urlsafe_b64decode(encrypted_key.encode())
        decrypted = self.fernet.decrypt(encrypted)
        return decrypted.decode()


# 使用示例
encryption = APIKeyEncryption()

# 保存配置前加密
config = {
    "api_key": encryption.encrypt("sk-xxxxxxxxxxxx"),
    "endpoint": "https://api.openai.com/v1",
    "model": "text-embedding-3-small"
}
db.execute("INSERT INTO ai_models (config_json) VALUES (?)", (json.dumps(config),))

# 读取配置后解密
row = db.execute("SELECT config_json FROM ai_models WHERE id = ?", (model_id,)).fetchone()
config = json.loads(row["config_json"])
api_key = encryption.decrypt(config["api_key"])
```

---

## 6. 数据库操作示例

### 6.1 查询当前活跃的嵌入模型

```sql
SELECT
    id,
    model_type,
    provider,
    model_name,
    config_json,
    is_active,
    updated_at
FROM ai_models
WHERE model_type = 'embedding'
  AND is_active = true
LIMIT 1;
```

**返回示例**：

```json
{
  "id": 2,
  "model_type": "embedding",
  "provider": "cloud",
  "model_name": "text-embedding-3-small",
  "config_json": {
    "api_key": "encrypted_key_here",
    "endpoint": "https://api.openai.com/v1",
    "model": "text-embedding-3-small"
  },
  "is_active": true,
  "updated_at": "2026-03-26T10:00:00"
}
```

---

### 6.2 切换嵌入模型（本地 → 云端）

```sql
-- 步骤 1：将现有模型设为不活跃
UPDATE ai_models
SET is_active = false
WHERE model_type = 'embedding' AND is_active = true;

-- 步骤 2：激活云端模型配置
UPDATE ai_models
SET is_active = true, updated_at = CURRENT_TIMESTAMP
WHERE model_type = 'embedding'
  AND provider = 'cloud'
  AND model_name = 'text-embedding-3-small';
```

---

### 6.3 切换嵌入模型（云端 → 本地）

```sql
-- 步骤 1：将现有模型设为不活跃
UPDATE ai_models
SET is_active = false
WHERE model_type = 'embedding' AND is_active = true;

-- 步骤 2：激活本地模型配置
UPDATE ai_models
SET is_active = true, updated_at = CURRENT_TIMESTAMP
WHERE model_type = 'embedding'
  AND provider = 'local'
  AND model_name = 'BAAI/bge-m3';
```

---

### 6.4 删除云端嵌入模型配置

```sql
DELETE FROM ai_models
WHERE model_type = 'embedding'
  AND provider = 'cloud'
  AND model_name = 'text-embedding-3-small';
```

---

## 7. 数据迁移说明

### 7.1 无需迁移的原因

1. **表结构支持**：现有 `ai_models` 表的 `provider` 字段已支持 `local/cloud` 值
2. **JSON 灵活性**：`config_json` 字段可以存储任意 JSON 结构，无需修改表结构
3. **索引兼容**：现有索引完全满足新特性的查询需求

---

### 7.2 升级步骤

**步骤 1**：备份现有数据库

```bash
cp xiaoyaosearch.db xiaoyaosearch.db.backup
```

**步骤 2**：无需执行任何 SQL 迁移脚本

**步骤 3**：启动应用，验证功能

```bash
cd backend
python main.py
```

**步骤 4**：测试云端嵌入模型配置

```bash
curl -X PUT http://127.0.0.1:8000/api/config/ai-model \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "embedding",
    "provider": "cloud",
    "model_name": "text-embedding-3-small",
    "config": {
      "api_key": "sk-xxx",
      "endpoint": "https://api.openai.com/v1",
      "model": "text-embedding-3-small"
    }
  }'
```

---

## 8. 安全考虑

### 8.1 API 密钥加密存储

**存储格式**：`config_json` 中的 `api_key` 字段使用 AES 加密

```json
{
  "api_key": "gAAAAABlxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "endpoint": "https://api.openai.com/v1",
  "model": "text-embedding-3-small"
}
```

**密钥管理**：
- 加密密钥从环境变量 `API_ENCRYPTION_KEY` 读取
- 如果未设置，应用启动时会生成新密钥并提示用户
- 密钥长度必须为 32 字节（URL-safe base64 编码后 44 字符）

---

### 8.2 日志脱敏

**规则**：日志中 API 密钥只显示前 8 位和后 4 位

```python
def mask_api_key(api_key: str) -> str:
    """脱敏 API 密钥"""
    if len(api_key) <= 12:
        return "***"
    return f"{api_key[:8]}...{api_key[-4:]}"

# 正常：sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# 脱敏：sk-xxxx...xxxx
```

---

## 9. 性能优化

### 9.1 配置缓存

**策略**：将活跃的嵌入模型配置缓存到内存，减少数据库查询

```python
from functools import lru_cache
import threading

class EmbeddingModelCache:
    """嵌入模型配置缓存"""

    def __init__(self):
        self._cache = None
        self._lock = threading.RLock()
        self._last_update = None

    def get_active_model(self) -> Optional[Dict[str, Any]]:
        """获取当前活跃的嵌入模型配置"""
        with self._lock:
            if self._cache is None or self._is_expired():
                self._refresh()
            return self._cache

    def _is_expired(self) -> bool:
        """检查缓存是否过期"""
        if self._last_update is None:
            return True
        return (time.time() - self._last_update) > 300  # 5 分钟过期

    def _refresh(self):
        """从数据库刷新缓存"""
        row = db.execute(
            "SELECT * FROM ai_models WHERE model_type = 'embedding' AND is_active = true"
        ).fetchone()

        if row:
            self._cache = {
                "id": row["id"],
                "provider": row["provider"],
                "model_name": row["model_name"],
                "config": json.loads(row["config_json"])
            }
        else:
            self._cache = None

        self._last_update = time.time()

    def invalidate(self):
        """使缓存失效（配置更新时调用）"""
        with self._lock:
            self._cache = None
            self._last_update = None


# 全局缓存实例
embedding_cache = EmbeddingModelCache()
```

---

## 10. 附录

### 10.1 相关文档

- [主数据库设计文档](../../数据库设计文档.md)
- [主接口文档](../../接口文档.md)
- [云端嵌入模型 PRD](./embedding-openai-01-prd.md)
- [云端嵌入模型技术方案](./embedding-openai-03-技术方案.md)
- [云端嵌入模型接口文档增量](./embedding-openai-增量-接口文档.md)

---

### 10.2 数据库表结构完整定义

```sql
CREATE TABLE IF NOT EXISTS ai_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_type TEXT NOT NULL CHECK(model_type IN ('embedding', 'speech', 'vision', 'llm')),
    provider TEXT NOT NULL CHECK(provider IN ('local', 'cloud')),
    model_name TEXT NOT NULL,
    config_json TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(model_type, provider, model_name)
);

CREATE INDEX IF NOT EXISTS idx_ai_models_model_type ON ai_models(model_type);
CREATE INDEX IF NOT EXISTS idx_ai_models_provider ON ai_models(provider);
CREATE INDEX IF NOT EXISTS idx_ai_models_is_active ON ai_models(is_active);
```

---

**文档版本**：v1.0
**维护者**：AI 助手
**最后更新**：2026-03-26
