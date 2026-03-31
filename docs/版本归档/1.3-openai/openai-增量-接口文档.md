# OpenAI兼容大模型服务 - 接口文档增量

> **文档类型**：增量接口文档
> **基础版本**：基于 [主接口文档](../../接口文档.md)
> **特性状态**：已完成
> **创建时间**：2026-02-28
> **最后更新**：2026-02-28

---

## 1. 增量说明

### 1.1 概述

本文档描述了 OpenAI 兼容大模型服务特性对现有接口的增量变更。

**变更类型**：
- **修改接口**：扩展现有接口参数，支持云端模型配置
- **新增字段**：provider 字段新增可选值 "cloud"
- **配置变更**：config 字段根据 provider 不同包含不同配置项

### 1.2 向后兼容性

**兼容性声明**：✅ 完全向后兼容

- 现有 Ollama（本地）配置保持不变
- 新增的云端配置为可选功能
- 数据库表结构无变更

---

## 2. 接口变更

### 2.1 更新AI模型配置（扩展）

**接口**：`POST /api/config/ai-model`

**变更类型**：修改（扩展参数）

**变更说明**：provider 字段新增可选值 "cloud"，config 字段根据 provider 不同包含不同配置项。

---

#### 请求体（Ollama 本地 - 现有配置，无变更）

```http
POST /api/config/ai-model
Content-Type: application/json

{
  "model_type": "llm",
  "provider": "local",
  "model_name": "qwen2.5:1.5b",
  "config": {
    "base_url": "http://localhost:11434",
    "timeout": 30,
    "temperature": 0.7
  }
}
```

**Ollama 配置项说明**：

| 配置项 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| base_url | string | 否 | http://localhost:11434 | Ollama 服务地址 |
| timeout | integer | 否 | 30 | 请求超时时间（秒） |
| temperature | float | 否 | 0.7 | 温度参数（0.0-2.0） |

---

#### 请求体（OpenAI 兼容云端 - 新增配置）

```http
POST /api/config/ai-model
Content-Type: application/json

{
  "model_type": "llm",
  "provider": "cloud",
  "model_name": "qwen-turbo",
  "config": {
    "api_key": "sk-xxxxxxxxxxxx",
    "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "timeout": 60,
    "temperature": 0.7,
    "max_tokens": 2048,
    "top_p": 1.0
  }
}
```

**OpenAI 兼容配置项说明**：

| 配置项 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| api_key | string | **是** | - | API 密钥（加密存储） |
| endpoint | string | 否 | https://api.openai.com/v1 | API 端点地址 |
| timeout | integer | 否 | 60 | 请求超时时间（秒） |
| temperature | float | 否 | 0.7 | 温度参数（0.0-2.0） |
| max_tokens | integer | 否 | 2048 | 最大生成 token 数 |
| top_p | float | 否 | 1.0 | 核采样参数（0.0-1.0） |

---

#### 响应（统一格式）

```json
{
  "success": true,
  "message": "配置已保存，请重启应用以生效",
  "data": {
    "id": 1,
    "model_type": "llm",
    "provider": "cloud",
    "model_name": "qwen-turbo",
    "config_json": "{\"api_key\": \"***\", \"endpoint\": \"https://...\", ...}",
    "is_active": true,
    "created_at": "2026-02-28T10:00:00Z",
    "updated_at": "2026-02-28T10:00:00Z"
  }
}
```

**安全说明**：
- API 密钥在响应中脱敏显示（仅显示前7位和后4位）
- 数据库中加密存储
- 日志中不记录完整密钥

---

### 2.2 测试AI模型（扩展）

**接口**：`POST /api/config/ai-model/{model_id}/test`

**变更类型**：修改（支持云端模型测试）

**变更说明**：测试接口扩展支持云端模型，自动识别 provider 类型并执行对应的测试逻辑。

---

#### 请求体（统一格式）

```http
POST /api/config/ai-model/1/test
Content-Type: application/json

{
  "test_data": "你好，请简单介绍一下你自己。"
}
```

**请求参数说明**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| test_data | string | 否 | "你好，请简单介绍一下你自己。" | 测试消息内容 |

---

#### 响应（Ollama 本地模型）

```json
{
  "success": true,
  "data": {
    "model_id": 1,
    "test_passed": true,
    "response_time": 0.52,
    "test_message": "连接成功！模型响应正常",
    "test_data": "你好，请简单介绍一下你自己。",
    "response_content": "你好！我是小遥搜索的AI助手，基于Ollama本地模型运行，可以帮助你进行智能搜索和文档检索...",
    "provider": "local"
  }
}
```

---

#### 响应（OpenAI 兼容云端模型）

```json
{
  "success": true,
  "data": {
    "model_id": 2,
    "test_passed": true,
    "response_time": 1.23,
    "test_message": "连接成功！模型响应正常",
    "test_data": "你好，请简单介绍一下你自己。",
    "response_content": "你好！我是小遥搜索的AI助手，使用云端大语言模型运行，可以帮助你进行智能搜索和文档检索...",
    "provider": "cloud",
    "usage": {
      "prompt_tokens": 15,
      "completion_tokens": 30,
      "total_tokens": 45
    }
  }
}
```

**响应字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| model_id | integer | 模型配置 ID |
| test_passed | boolean | 测试是否通过 |
| response_time | float | 响应时间（秒） |
| test_message | string | 测试结果消息 |
| test_data | string | 测试输入内容 |
| response_content | string | 模型响应内容 |
| provider | string | 提供商类型（local/cloud） |
| usage | object | Token 使用统计（仅云端模型） |

---

#### 错误响应示例

**API 密钥无效（401）**：

```json
{
  "success": false,
  "error": {
    "code": "unauthorized",
    "message": "API 密钥无效或已过期，请检查配置"
  }
}
```

**网络连接失败**：

```json
{
  "success": false,
  "error": {
    "code": "connection_failed",
    "message": "无法连接到 API 端点，请检查网络和端点地址"
  }
}
```

**请求超时**：

```json
{
  "success": false,
  "error": {
    "code": "request_timeout",
    "message": "请求超时，请检查网络连接或增加超时时间"
  }
}
```

---

### 2.3 获取所有AI模型配置（无变更）

**接口**：`GET /api/config/ai-models`

**变更类型**：无变更（仅响应数据可能包含云端模型）

**响应示例（包含云端模型）**：

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "model_type": "llm",
      "provider": "local",
      "model_name": "qwen2.5:1.5b",
      "config_json": "{\"base_url\": \"http://localhost:11434\"}",
      "is_active": true,
      "created_at": "2026-02-28T08:00:00Z",
      "updated_at": "2026-02-28T08:00:00Z"
    },
    {
      "id": 2,
      "model_type": "llm",
      "provider": "cloud",
      "model_name": "qwen-turbo",
      "config_json": "{\"api_key\": \"sk-a1b2...\", \"endpoint\": \"https://...\"}",
      "is_active": false,
      "created_at": "2026-02-28T10:00:00Z",
      "updated_at": "2026-02-28T10:00:00Z"
    }
  ]
}
```

---

## 3. 数据模型变更

### 3.1 AIModelConfigRequest（扩展）

```typescript
interface AIModelConfigRequest {
  model_type: string;               // 模型类型 embedding/speech/vision/llm
  provider: string;                 // 提供商类型 local/cloud ✨ 新增 "cloud" 值
  model_name: string;               // 模型名称 (1-100字符)
  config: Record<string, any>;      // 模型配置参数 ✨ 根据 provider 不同
}

// provider='local' 时的 config 结构
interface LocalLLMConfig {
  base_url?: string;                // Ollama 服务地址
  timeout?: number;                 // 请求超时时间（秒）
  temperature?: number;             // 温度参数
}

// provider='cloud' 时的 config 结构（新增）
interface CloudLLMConfig {
  api_key: string;                  // ✨ API 密钥（必填）
  endpoint?: string;                // ✨ API 端点地址
  timeout?: number;                 // 请求超时时间（秒）
  temperature?: number;             // 温度参数
  max_tokens?: number;              // 最大生成 token 数
  top_p?: number;                   // 核采样参数
}
```

### 3.2 ModelTestResponse（扩展）

```typescript
interface ModelTestResponse {
  success: boolean;
  data: {
    model_id: number;
    test_passed: boolean;
    response_time: number;
    test_message: string;
    test_data: string;
    response_content: string;
    provider: string;               // ✨ 新增：提供商类型
    usage?: TokenUsage;             // ✨ 新增：Token 使用统计（仅云端）
  };
}

interface TokenUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}
```

---

## 4. 支持的供应商配置

### 4.1 OpenAI 官方

```json
{
  "model_type": "llm",
  "provider": "cloud",
  "model_name": "gpt-3.5-turbo",
  "config": {
    "api_key": "sk-xxxxxxxxxxxx",
    "endpoint": "https://api.openai.com/v1",
    "temperature": 0.7,
    "max_tokens": 2048
  }
}
```

### 4.2 阿里云通义千问

```json
{
  "model_type": "llm",
  "provider": "cloud",
  "model_name": "qwen-turbo",
  "config": {
    "api_key": "sk-xxxxxxxxxxxx",
    "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "temperature": 0.7,
    "max_tokens": 2048
  }
}
```

### 4.3 DeepSeek

```json
{
  "model_type": "llm",
  "provider": "cloud",
  "model_name": "deepseek-chat",
  "config": {
    "api_key": "sk-xxxxxxxxxxxx",
    "endpoint": "https://api.deepseek.com/v1",
    "temperature": 0.7,
    "max_tokens": 4096
  }
}
```

### 4.4 Moonshot AI

```json
{
  "model_type": "llm",
  "provider": "cloud",
  "model_name": "moonshot-v1-8k",
  "config": {
    "api_key": "sk-xxxxxxxxxxxx",
    "endpoint": "https://api.moonshot.cn/v1",
    "temperature": 0.7,
    "max_tokens": 2048
  }
}
```

---

## 5. 错误码扩展

### 5.1 新增业务错误码

| 错误码 | HTTP状态码 | 说明 | 解决方案 |
|--------|------------|------|----------|
| CLOUD_API_KEY_INVALID | 401 | API 密钥无效 | 检查 API 密钥是否正确 |
| CLOUD_API_UNAUTHORIZED | 401 | API 认证失败 | 检查 API 密钥是否有效 |
| CLOUD_RATE_LIMIT_EXCEEDED | 429 | 请求频率超限 | 稍后重试或升级套餐 |
| CLOUD_QUOTA_EXCEEDED | 429 | 配额已用尽 | 检查账户余额或配额 |
| CLOUD_ENDPOINT_INVALID | 400 | 端点地址无效 | 检查 endpoint 配置 |
| CLOUD_CONNECTION_FAILED | 503 | 连接云端失败 | 检查网络连接 |
| CLOUD_REQUEST_TIMEOUT | 504 | 请求超时 | 增加超时时间或检查网络 |
| CLOUD_MODEL_NOT_FOUND | 404 | 模型不存在 | 检查 model_name 是否正确 |

### 5.2 错误响应格式

```json
{
  "success": false,
  "error": {
    "code": "CLOUD_API_KEY_INVALID",
    "message": "API 密钥无效或已过期",
    "details": "请检查配置的 API 密钥是否正确"
  }
}
```

---

## 6. 安全说明

### 6.1 API 密钥保护

**存储安全**：
- API 密钥在数据库中加密存储（Fernet 加密）
- 使用环境变量管理加密密钥
- 密钥不以明文形式记录在任何日志中

**传输安全**：
- 强制使用 HTTPS 协议
- 验证 SSL 证书
- 支持自定义 CA 证书

**显示安全**：
- API 密钥在前端脱敏显示（sk-****...****1234）
- 日志中记录脱敏后的密钥
- 响应中不返回完整密钥

### 6.2 密钥脱敏格式

```python
# 脱敏函数
def mask_api_key(api_key: str) -> str:
    """脱敏 API 密钥"""
    if not api_key or len(api_key) < 10:
        return "***"
    return f"{api_key[:7]}...{api_key[-4:]}"

# 示例
# 输入: sk-abc123def456789xyz012
# 输出: sk-abc1...x012
```

### 6.3 前端显示示例

```vue
<!-- API 密钥输入框 -->
<a-form-item label="API 密钥">
  <a-input-password
    v-model:value="llmConfig.api_key"
    placeholder="sk-..."
  />
</a-form-item>

<!-- 已保存的密钥显示（脱敏） -->
<a-descriptions-item label="API 密钥">
  {{ maskApiKey(savedConfig.api_key) }}
  <!-- 显示为: sk-a1b2...x012 -->
</a-descriptions-item>
```

---

## 7. 前端集成示例

### 7.1 配置服务扩展

```typescript
// api/config.ts
export interface LLMConfig {
  provider: 'local' | 'cloud';      // 新增 provider 字段
  model_name: string;
  base_url?: string;                // local 使用
  api_key?: string;                 // cloud 使用
  endpoint?: string;                // cloud 使用
  temperature?: number;
  max_tokens?: number;              // cloud 使用
}

export class AIModelConfigService {
  // 保存 LLM 配置
  static async saveLLMConfig(config: LLMConfig) {
    const requestBody: any = {
      model_type: 'llm',
      provider: config.provider,
      model_name: config.model_name,
      config: {}
    };

    // 根据 provider 构建不同的配置
    if (config.provider === 'local') {
      requestBody.config = {
        base_url: config.base_url,
        temperature: config.temperature
      };
    } else {
      requestBody.config = {
        api_key: config.api_key,
        endpoint: config.endpoint,
        temperature: config.temperature,
        max_tokens: config.max_tokens
      };
    }

    return await api.post('/api/config/ai-model', requestBody);
  }

  // 测试模型连接
  static async testModel(modelId: number, testData?: string) {
    return await api.post(`/api/config/ai-model/${modelId}/test`, {
      test_data: testData || '你好，请简单介绍一下你自己。'
    });
  }
}
```

### 7.2 Vue 组件集成

```vue
<script setup lang="ts">
import { ref, reactive } from 'vue';
import { message } from 'ant-design-vue';
import { AIModelConfigService } from '@/api/config';

// LLM 配置
const llmConfig = reactive({
  provider: 'local' as 'local' | 'cloud',
  model_name: 'qwen2.5:1.5b',
  base_url: 'http://localhost:11434',
  api_key: '',
  endpoint: 'https://api.openai.com/v1',
  temperature: 0.7,
  max_tokens: 2048
});

// 切换提供商类型
const handleProviderChange = (value: 'local' | 'cloud') => {
  llmConfig.provider = value;

  // 重置为默认配置
  if (value === 'local') {
    llmConfig.model_name = 'qwen2.5:1.5b';
    llmConfig.base_url = 'http://localhost:11434';
  } else {
    llmConfig.model_name = 'gpt-3.5-turbo';
    llmConfig.endpoint = 'https://api.openai.com/v1';
  }
};

// 保存配置
const saveConfig = async () => {
  try {
    const response = await AIModelConfigService.saveLLMConfig(llmConfig);

    if (response.success) {
      message.success('配置已保存，请重启应用以生效');
    }
  } catch (error) {
    message.error('保存配置失败');
  }
};

// 测试连接
const testConnection = async () => {
  try {
    const response = await AIModelConfigService.testModel(currentModelId.value);

    if (response.success) {
      const { test_passed, response_time, response_content, usage } = response.data;

      if (test_passed) {
        message.success(`测试成功！响应时间: ${response_time}秒`);
        console.log('模型响应:', response_content);

        if (usage) {
          console.log('Token 使用:', usage);
        }
      }
    }
  } catch (error) {
    message.error('测试连接失败');
  }
};
</script>
```

---

## 8. 测试用例

### 8.1 配置云端模型

**请求**：
```http
POST /api/config/ai-model
Content-Type: application/json

{
  "model_type": "llm",
  "provider": "cloud",
  "model_name": "qwen-turbo",
  "config": {
    "api_key": "sk-test123456789",
    "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1"
  }
}
```

**预期响应**：
```json
{
  "success": true,
  "message": "配置已保存，请重启应用以生效",
  "data": {
    "id": 2,
    "model_type": "llm",
    "provider": "cloud",
    "model_name": "qwen-turbo",
    "config_json": "{\"api_key\": \"sk-test...6789\", \"endpoint\": \"https://...\"}",
    "is_active": true
  }
}
```

### 8.2 测试云端模型

**请求**：
```http
POST /api/config/ai-model/2/test
Content-Type: application/json

{
  "test_data": "你好"
}
```

**预期响应**：
```json
{
  "success": true,
  "data": {
    "model_id": 2,
    "test_passed": true,
    "response_time": 1.5,
    "test_message": "连接成功！模型响应正常",
    "test_data": "你好",
    "response_content": "你好！我是小遥搜索的AI助手...",
    "provider": "cloud",
    "usage": {
      "prompt_tokens": 5,
      "completion_tokens": 20,
      "total_tokens": 25
    }
  }
}
```

### 8.3 API 密钥无效错误

**请求**：
```http
POST /api/config/ai-model/2/test
Content-Type: application/json
```

**预期响应**：
```json
{
  "success": false,
  "error": {
    "code": "CLOUD_API_KEY_INVALID",
    "message": "API 密钥无效或已过期"
  }
}
```

---

## 9. 相关文档

- [PRD文档](./openai-01-prd.md) - 产品需求文档
- [技术方案](./openai-03-技术方案.md) - 技术实现方案
- [架构决策](../../架构决策/AD-20260228-01-OpenAI兼容大模型服务.md) - 架构决策文档
- [主接口文档](../../接口文档.md) - 完整API接口文档

---

**文档版本**：v1.0
**维护者**：AI助手
**最后更新**：2026-02-28

> **使用说明**：
> 1. 本文档为增量接口文档，描述与主接口文档的差异
> 2. 所有接口变更完全向后兼容
> 3. 数据库表结构无变更
> 4. 实施周期：2-3 天
