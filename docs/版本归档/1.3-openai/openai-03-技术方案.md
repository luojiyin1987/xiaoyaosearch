# OpenAI兼容大模型服务 - 技术方案

> **文档类型**：技术方案
> **特性状态**：规划中
> **创建时间**：2026-02-28
> **最后更新**：2026-02-28

---

## 1. 方案概述

### 1.1 技术目标

创建**通用 OpenAI 兼容大语言模型服务**，支持所有兼容 OpenAI API 标准的云服务供应商（OpenAI、阿里云、DeepSeek、Moonshot 等），与现有 Ollama 本地服务形成类型互斥的配置体系。

### 1.2 设计原则

- **类型互斥**：用户只能选择 Ollama（本地）或 OpenAI 兼容（云端）其中一种
- **接口统一**：两种服务继承同一基类 `BaseAIModel`，保持接口一致性
- **最小侵入**：精简 Ollama 服务，移除云端备选逻辑，降低复杂度
- **向后兼容**：保持现有 Ollama 配置可用，不破坏现有功能
- **安全优先**：API 密钥加密存储，日志脱敏处理

### 1.3 技术选型

| 技术/框架 | 用途 | 选择理由 | 替代方案 |
|----------|------|---------|---------|
| aiohttp | HTTP 客户端 | 异步高性能，已在项目中使用 | httpx、requests |
| BaseAIModel | 服务基类 | 统一接口，易于扩展 | 独立实现 |
| Pydantic | 配置验证 | 类型安全，自动验证 | 手动验证 |

### 1.4 支持的供应商

| 供应商 | 端点地址 | 模型示例 | 优先级 |
|--------|----------|---------|-------|
| OpenAI | `https://api.openai.com/v1` | `gpt-3.5-turbo` | P0 |
| 阿里云通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-turbo` | P0 |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` | P1 |
| Moonshot | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` | P1 |

---

## 2. 架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              API层                                       │
├─────────────────────────────────────────────────────────────────────────┤
│  PUT /api/config/ai-model  │  GET /api/config/ai-models  │            │
│  POST /api/config/ai-model/{id}/test                                   │
└────────────┬───────────────────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────────────────┐
│                        服务层 (Service Layer)                             │
├───────────────────────────────────────────────────────────────────────────┤
│                        AIModelService                                    │
│  - register_model()         # 注册模型                                  │
│  - get_model(llm)          # 获取LLM模型                               │
│  - text_generation()        # 文本生成                                  │
└────────────┬───────────────────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────────────────┐
│                      模型管理层 (Model Manager)                             │
├───────────────────────────────────────────────────────────────────────────┤
│                        ModelManager                                      │
│  - models: Dict[model_id, BaseAIModel]                                  │
│  - register_model(model_id, model)                                      │
│  - get_model(model_id)                                                   │
└────────────┬───────────────────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────────────────┐
│                      服务实现层 (Service Implementation)                     │
├───────────────────────────────────────────────────────────────────────────┤
│                        BaseAIModel (ABC)                                  │
│                                  │                                        │
│              ┌───────────────────┴───────────────────┐                     │
│              ▼                                     ▼                      │
│    OllamaLLMService                    OpenAILLMService                   │
│    (provider='local')                    (provider='cloud')                  │
│    - 本地 Ollama 调用                    - OpenAI API 调用                 │
│    - http://localhost:11434           - 云端供应商 API                    │
│                                         └─ 支持所有兼容供应商               │
└───────────────────────────────────────────────────────────────────────────┘
```

### 2.2 目录结构

```
backend/
├── app/
│   ├── services/
│   │   ├── ai_model_base.py              # 基类（已存在）
│   │   │   └── BaseAIModel(ABC)
│   │   ├── ollama_service.py             # Ollama 服务（精简）
│   │   │   └── OllamaLLMService extends BaseAIModel
│   │   ├── openai_llm_service.py         # OpenAI 兼容服务（新增）
│   │   │   └── OpenAILLMService extends BaseAIModel
│   │   └── ai_model_manager.py           # 模型管理器（扩展）
│   │
│   ├── models/
│   │   └── ai_model.py                   # 数据模型（无变更）
│   │
│   └── api/
│       └── config.py                     # 配置 API（无变更）
│
└── requirements.txt                       # 依赖（无新增）
```

### 2.3 数据流

**本地模型（Ollama）流程**：

```
用户配置 Ollama
    ↓
前端: provider='local', model_name='qwen2.5:1.5b', base_url='http://localhost:11434'
    ↓
后端: 创建 OllamaLLMService(config)
    ↓
模型管理器: register_model('llm_local', ollama_service)
    ↓
调用: ai_model_service.text_generation(messages)
    ↓
OllamaLLMService.predict()
    ↓
POST http://localhost:11434/api/chat
    ↓
返回生成结果
```

**云端模型（OpenAI 兼容）流程**：

```
用户配置云端模型
    ↓
前端: provider='cloud', model_name='qwen-turbo', api_key='sk-xxx', endpoint='https://...'
    ↓
后端: 创建 OpenAILLMService(config)
    ↓
模型管理器: register_model('llm_cloud', openai_service)
    ↓
调用: ai_model_service.text_generation(messages)
    ↓
OpenAILLMService.predict()
    ↓
POST {endpoint}/chat/completions
    ↓
返回生成结果
```

---

## 3. 核心模块设计

### 3.1 OpenAI 兼容服务（新增）

**文件**：`backend/app/services/openai_llm_service.py`

```python
"""
OpenAI兼容的大语言模型服务
支持所有兼容OpenAI API标准的供应商（OpenAI、阿里云、DeepSeek、Moonshot等）
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass

import aiohttp

from app.services.ai_model_base import BaseAIModel, ModelType, ProviderType, ModelStatus, AIModelException
from app.utils.enum_helpers import get_enum_value

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """聊天消息数据类"""
    role: str  # system, user, assistant
    content: str


class OpenAILLMService(BaseAIModel):
    """
    OpenAI兼容的大语言模型服务

    支持所有兼容OpenAI API标准的供应商：
    - OpenAI 官方
    - 阿里云通义千问
    - DeepSeek
    - Moonshot
    - 其他兼容 OpenAI API 标准的服务
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化OpenAI兼容大语言模型服务

        Args:
            config: 模型配置参数，包含：
                - api_key: API密钥 (必需)
                - endpoint: API端点地址 (可选，默认 https://api.openai.com/v1)
                - model: 模型名称 (必需)
                - timeout: 请求超时时间(秒)
                - temperature: 温度参数
                - max_tokens: 最大生成token数
        """
        if config is None:
            config = {}

        # 验证必需参数
        if "api_key" not in config or not config["api_key"]:
            raise ValueError("api_key 是必需参数")

        if "model" not in config or not config["model"]:
            raise ValueError("model 是必需参数")

        # 默认配置
        default_config = {
            "endpoint": "https://api.openai.com/v1",
            "timeout": 60,
            "temperature": 0.7,
            "max_tokens": 2048,
            "top_p": 1.0,
        }

        default_config.update(config)

        super().__init__(
            model_name=default_config["model"],
            model_type=ModelType.LLM,
            provider=ProviderType.CLOUD,
            config=default_config
        )

        self.session: Optional[aiohttp.ClientSession] = None
        self.api_key = self.config["api_key"]
        self.endpoint = self.config["endpoint"].rstrip('/')
        self.model = self.config["model"]

        logger.info(f"初始化OpenAI兼容服务，模型: {self.model}, 端点: {self.endpoint}")

    async def load_model(self) -> bool:
        """加载模型（验证API连接）"""
        try:
            self.update_status(ModelStatus.LOADING)
            logger.info(f"开始验证OpenAI兼容API连接: {self.endpoint}")

            # 创建HTTP会话
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.get("timeout", 60))
            )

            # 发送测试请求验证连接
            await self._test_connection()

            self.update_status(ModelStatus.LOADED)
            logger.info(f"OpenAI兼容API连接验证成功: {self.model}")
            return True

        except Exception as e:
            error_msg = f"OpenAI兼容API连接失败: {str(e)}"
            logger.error(error_msg)
            self.update_status(ModelStatus.ERROR, error_msg)
            raise AIModelException(error_msg, model_name=self.model_name)

    async def unload_model(self) -> bool:
        """卸载模型"""
        try:
            logger.info(f"开始卸载OpenAI兼容服务: {self.model}")

            # 关闭HTTP会话
            if self.session:
                await self.session.close()
                self.session = None

            self.update_status(ModelStatus.UNLOADED)
            logger.info("OpenAI兼容服务卸载成功")
            return True

        except Exception as e:
            error_msg = f"卸载OpenAI兼容服务失败: {str(e)}"
            logger.error(error_msg)
            return False

    async def predict(self, messages: Union[str, List[Message], List[Dict]], **kwargs) -> Dict[str, Any]:
        """
        大语言模型预测

        Args:
            messages: 输入消息
            **kwargs: 预测参数

        Returns:
            Dict[str, Any]: 生成结果
        """
        if self.status != ModelStatus.LOADED:
            raise AIModelException(
                f"模型未加载，当前状态: {get_enum_value(self.status)}",
                model_name=self.model_name
            )

        try:
            # 标准化消息格式
            standardized_messages = self._standardize_messages(messages)

            # 获取预测参数
            temperature = kwargs.get("temperature", self.config.get("temperature", 0.7))
            max_tokens = kwargs.get("max_tokens", self.config.get("max_tokens", 2048))
            top_p = kwargs.get("top_p", self.config.get("top_p", 1.0))

            logger.info(f"开始OpenAI兼容API预测，消息数量: {len(standardized_messages)}")

            # 构建请求数据
            request_data = {
                "model": self.model,
                "messages": standardized_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
            }

            # 发送请求
            url = f"{self.endpoint}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            async with self.session.post(url, json=request_data, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise AIModelException(
                        f"OpenAI兼容API请求失败: {response.status} - {error_text}",
                        model_name=self.model_name
                    )

                result = await response.json()

            # 处理响应
            choice = result.get("choices", [{}])[0]
            message = choice.get("message", {})
            content = message.get("content", "")

            usage = result.get("usage", {})

            self.record_usage()
            logger.info(f"OpenAI兼容API预测完成，生成文本长度: {len(content)}")

            return {
                "content": content,
                "model": self.model,
                "provider": "cloud",
                "finish_reason": choice.get("finish_reason"),
                "usage": {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                }
            }

        except Exception as e:
            error_msg = f"OpenAI兼容API预测失败: {str(e)}"
            logger.error(error_msg)
            raise AIModelException(error_msg, model_name=self.model_name)

    def _standardize_messages(self, messages: Union[str, List[Message], List[Dict]]) -> List[Dict]:
        """标准化消息格式"""
        if isinstance(messages, str):
            return [{"role": "user", "content": messages}]
        elif isinstance(messages, list):
            if messages and isinstance(messages[0], Message):
                return [{"role": msg.role, "content": msg.content} for msg in messages]
            elif messages and isinstance(messages[0], dict):
                return messages
            else:
                raise AIModelException(f"不支持的消息格式: {type(messages[0])}", model_name=self.model_name)
        else:
            raise AIModelException(f"不支持的消息类型: {type(messages)}", model_name=self.model_name)

    async def _test_connection(self) -> bool:
        """测试API连接"""
        try:
            # 发送一个简单的测试请求
            url = f"{self.endpoint}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            request_data = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 10
            }

            async with self.session.post(url, json=request_data, headers=headers) as response:
                if response.status == 200:
                    logger.info("OpenAI兼容API连接测试成功")
                    return True
                else:
                    error_text = await response.text()
                    raise AIModelException(f"API连接测试失败: {response.status} - {error_text}")

        except Exception as e:
            raise AIModelException(f"连接测试异常: {str(e)}")

    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "model_name": self.model_name,
            "model_type": get_enum_value(self.model_type),
            "provider": get_enum_value(self.provider),
            "endpoint": self.endpoint,
            "model": self.model,
            "temperature": self.config.get("temperature", 0.7),
            "max_tokens": self.config.get("max_tokens", 2048),
            "top_p": self.config.get("top_p", 1.0),
        }

    def _get_test_input(self) -> str:
        """获取健康检查的测试输入"""
        return "你好，请简单介绍一下你自己。"


# 工厂函数
def create_openai_compatible_service(config: Dict[str, Any]) -> OpenAILLMService:
    """
    创建OpenAI兼容大语言模型服务实例

    Args:
        config: 模型配置参数

    Returns:
        OpenAILLMService: OpenAI兼容服务实例
    """
    return OpenAILLMService(config)
```

### 3.2 Ollama 服务精简（修改）

**文件**：`backend/app/services/ollama_service.py`

**修改内容**：

1. **移除云端备选逻辑**：删除 `_init_cloud_models()` 方法
2. **移除云端调用**：删除 `_predict_with_cloud()` 方法
3. **简化预测逻辑**：`predict()` 方法仅调用本地 Ollama

**关键代码变更**：

```python
# 原代码（第 141-205 行）
async def predict(self, messages: Union[str, List[Message], List[Dict]], **kwargs) -> Dict[str, Any]:
    # ... 标准化消息 ...

    # 选择推理方式
    if use_cloud and self.config.get("use_cloud_fallback", True):
        result = await self._predict_with_cloud(standardized_messages, cloud_provider, **kwargs)
    else:
        result = await self._predict_with_ollama(standardized_messages, **kwargs)

    # ...

# 新代码（简化版）
async def predict(self, messages: Union[str, List[Message], List[Dict]], **kwargs) -> Dict[str, Any]:
    # ... 标准化消息 ...

    # 直接使用本地 Ollama 预测
    result = await self._predict_with_ollama(standardized_messages, **kwargs)

    # ...
```

### 3.3 模型管理器扩展（修改）

**文件**：`backend/app/services/ai_model_manager.py`

**修改内容**：`_create_default_models()` 方法支持云模型

```python
# 新增代码片段
async def _create_default_models(self):
    """创建默认模型实例"""
    try:
        for model_id, model_config in self.model_configs.items():
            model_type = model_config["model_type"]
            provider = model_config.get("provider", "local")
            config = model_config["config"]

            # 解析 JSON 配置
            if isinstance(config, str):
                import json
                config = json.loads(config)

            try:
                if model_type == "llm":
                    # 根据 provider 创建不同的服务
                    if provider == "local":
                        model = create_ollama_service(config)
                    elif provider == "cloud":
                        from app.services.openai_llm_service import create_openai_compatible_service
                        model = create_openai_compatible_service(config)
                    else:
                        logger.warning(f"不支持的 LLM provider: {provider}")
                        continue

                    self.model_manager.register_model(model_id, model)
                    self.default_models["llm"] = model_id
                    await self.model_manager.load_model(model_id)
                    logger.info(f"创建并加载 llm 模型: {model_id}")

                # ... 其他模型类型保持不变 ...

            except Exception as model_error:
                logger.warning(f"创建 llm 模型失败 ({model_id}): {str(model_error)}")

    except Exception as e:
        logger.error(f"创建默认模型实例失败: {str(e)}")
```

---

## 4. 接口设计

### 4.1 配置保存接口（扩展）

**接口**：`PUT /api/config/ai-model`

**请求体（Ollama）**：

```json
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

**请求体（OpenAI 兼容）**：

```json
{
  "model_type": "llm",
  "provider": "cloud",
  "model_name": "qwen-turbo",
  "config": {
    "api_key": "sk-xxxxxxxxxxxx",
    "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "timeout": 60,
    "temperature": 0.7,
    "max_tokens": 2048
  }
}
```

**响应**：

```json
{
  "success": true,
  "message": "配置已保存，请重启应用以生效",
  "data": {
    "id": 1,
    "model_type": "llm",
    "provider": "cloud",
    "model_name": "qwen-turbo",
    "config_json": "{...}",
    "is_active": true
  }
}
```

### 4.2 测试连接接口（扩展）

**接口**：`POST /api/config/ai-model/{id}/test`

**请求体**：

```json
{
  "test_data": "你好，请简单介绍一下你自己。"
}
```

**响应（成功）**：

```json
{
  "success": true,
  "data": {
    "model_id": 1,
    "test_passed": true,
    "response_time": 1.23,
    "test_message": "连接成功！模型响应正常",
    "test_data": "你好，请简单介绍一下你自己。",
    "response_content": "你好！我是小遥搜索的AI助手..."
  }
}
```

---

## 5. 前端实现

### 5.1 设置页面修改

**文件**：`frontend/src/renderer/src/views/Settings.vue`

**修改内容**：

```vue
<template>
  <!-- 大语言模型设置 -->
  <a-tab-pane key="llm" :tab="t('settingsLLM.title')">
    <div class="settings-section">
      <h3>{{ t('settingsLLM.title') }}</h3>
      <a-form layout="vertical">

        <!-- 模型类型选择器（新增） -->
        <a-form-item :label="t('settingsLLM.modelType')">
          <a-select
            v-model:value="llmConfig.provider"
            style="width: 200px"
            @change="handleProviderChange"
          >
            <a-select-option value="local">
              {{ t('settingsLLM.modelTypeOllama') }}
            </a-select-option>
            <a-select-option value="cloud">
              {{ t('settingsLLM.modelTypeOpenAI') }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <!-- Ollama 配置表单 -->
        <div v-if="llmConfig.provider === 'local'" class="config-form">
          <a-alert
            :message="t('settingsLLM.localOllamaService')"
            :description="t('settingsLLM.localOllamaDesc')"
            type="info"
            show-icon
          />

          <a-form-item :label="t('settingsLLM.modelName')">
            <a-input
              v-model:value="llmConfig.model_name"
              :placeholder="t('settingsLLM.modelNamePlaceholder')"
            />
          </a-form-item>

          <a-form-item :label="t('settingsLLM.serviceUrl')">
            <a-input
              v-model:value="llmConfig.base_url"
              :placeholder="t('settingsLLM.serviceUrlPlaceholder')"
            />
          </a-form-item>
        </div>

        <!-- OpenAI 兼容配置表单（新增） -->
        <div v-else class="config-form">
          <!-- 云端服务说明卡片 -->
          <a-alert
            type="info"
            show-icon
            closable
            class="cloud-service-info"
          >
            <template #message>
              <span>{{ t('settingsLLM.cloudServiceInfo.title') }}</span>
            </template>
            <template #description>
              <div class="cloud-service-info-content">
                <p>{{ t('settingsLLM.cloudServiceInfo.description') }}</p>
                <ul class="info-list">
                  <li class="info-item-success">
                    <span>{{ t('settingsLLM.cloudServiceInfo.localDataSafe') }}</span>
                  </li>
                  <li class="info-item-warning">
                    <span>{{ t('settingsLLM.cloudServiceInfo.querySent') }}</span>
                  </li>
                  <li class="info-item-tip">
                    <span>{{ t('settingsLLM.cloudServiceInfo.betterUnderstanding') }}</span>
                  </li>
                </ul>
                <p class="info-notice">
                  {{ t('settingsLLM.cloudServiceInfo.recommendation') }}
                </p>
              </div>
            </template>
          </a-alert>

          <a-form-item :label="t('settingsLLM.apiKey')">
            <a-input-password
              v-model:value="llmConfig.api_key"
              :placeholder="t('settingsLLM.apiKeyPlaceholder')"
            />
          </a-form-item>

          <a-form-item :label="t('settingsLLM.endpoint')">
            <a-input
              v-model:value="llmConfig.endpoint"
              :placeholder="t('settingsLLM.endpointPlaceholder')"
            />
            <div class="form-help">{{ t('settingsLLM.endpointHelp') }}</div>
          </a-form-item>

          <a-form-item :label="t('settingsLLM.modelName')">
            <a-input
              v-model:value="llmConfig.model_name"
              :placeholder="t('settingsLLM.modelNamePlaceholderCloud')"
            />
            <div class="form-help">{{ t('settingsLLM.modelNameHelp') }}</div>
          </a-form-item>
        </div>

      </a-form>
    </div>
    <div class="settings-section">
      <a-space>
        <a-button
          type="primary"
          :loading="llmConfig.isTesting"
          @click="testLLMModel"
        >
          {{ t('settingsLLM.testConnection') }}
        </a-button>
        <a-button
          :loading="llmConfig.isLoading"
          @click="saveLLMConfig"
        >
          {{ t('settingsSpeech.saveSettings') }}
        </a-button>
      </a-space>
    </div>
  </a-tab-pane>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { AIModelConfigService } from '@/api/config'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// 扩展配置结构
const llmConfig = reactive({
  provider: 'local',      // 'local' | 'cloud'（新增）
  model_name: 'qwen2.5:1.5b',
  base_url: 'http://localhost:11434',
  api_key: '',            // 新增
  endpoint: '',           // 新增
  isLoading: false,
  isTesting: false
})

// 类型切换处理（新增）
const handleProviderChange = (value: string) => {
  llmConfig.provider = value

  // 重置配置
  if (value === 'local') {
    llmConfig.model_name = 'qwen2.5:1.5b'
    llmConfig.base_url = 'http://localhost:11434'
  } else {
    llmConfig.model_name = 'gpt-3.5-turbo'
    llmConfig.endpoint = 'https://api.openai.com/v1'
  }
}

// 保存配置（修改）
const saveLLMConfig = async () => {
  llmConfig.isLoading = true
  try {
    const config: any = {
      model_type: 'llm',
      provider: llmConfig.provider,
      model_name: llmConfig.model_name,
      config: {}
    }

    // 根据 provider 添加不同配置
    if (llmConfig.provider === 'local') {
      config.config = {
        base_url: llmConfig.base_url
      }
    } else {
      config.config = {
        api_key: llmConfig.api_key,
        endpoint: llmConfig.endpoint
      }
    }

    const response = await AIModelConfigService.updateAIModelConfig(config)

    if (response.success) {
      message.success(t('settingsLLM.saveSuccessRestart'))
      await loadAIModels()
    } else {
      message.error(t('error.llmConfigSaveFailed'))
    }
  } catch (error) {
    console.error('保存大语言模型配置失败:', error)
    message.error(t('error.llmConfigSaveFailed'))
  } finally {
    llmConfig.isLoading = false
  }
}

// 加载配置（修改）
const loadAIModels = async () => {
  try {
    const response = await AIModelConfigService.getAIModels('llm')
    if (response.success) {
      const model = response.data[0]
      if (model) {
        const config = AIModelConfigService.parseModelConfig(model.config_json)

        llmConfig.provider = model.provider
        llmConfig.model_name = model.model_name

        if (model.provider === 'local') {
          llmConfig.base_url = config.base_url || 'http://localhost:11434'
        } else {
          llmConfig.api_key = config.api_key || ''
          llmConfig.endpoint = config.endpoint || ''
        }
      }
    }
  } catch (error) {
    console.error('加载AI模型配置失败:', error)
  }
}

onMounted(() => {
  loadAIModels()
})
</script>

<style scoped>
.config-form {
  margin-top: var(--space-4);
  padding: var(--space-4);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  background: var(--surface-02);
}

.form-help {
  margin-top: var(--space-2);
  color: var(--text-tertiary);
  font-size: 0.875rem;
}

/* 云端服务说明卡片样式 */
.cloud-service-info {
  margin-bottom: var(--space-4);
}

.cloud-service-info-content {
  line-height: 1.6;
}

.cloud-service-info-content p {
  margin-bottom: var(--space-3);
}

.info-list {
  list-style: none;
  padding-left: 0;
  margin: var(--space-3) 0;
}

.info-item-success,
.info-item-warning,
.info-item-tip {
  padding: var(--space-2) 0;
  font-size: 0.875rem;
}

.info-item-success {
  color: #52c41a;
}

.info-item-warning {
  color: #faad14;
}

.info-item-tip {
  color: #1890ff;
}

.info-notice {
  margin-top: var(--space-3);
  padding-top: var(--space-3);
  border-top: 1px solid var(--border-light);
  color: var(--text-secondary);
  font-size: 0.875rem;
}
</style>
```

---

## 6. 国际化实现

### 6.1 中文翻译（zh-CN.ts）

**文件**：`frontend/src/renderer/src/locales/zh-CN.ts`

```typescript
settingsLLM: {
  title: '大语言模型',
  subtitle: '配置大语言模型参数',

  // 新增：类型选择
  modelType: '模型类型',
  modelTypeOllama: 'Ollama（本地）',
  modelTypeOpenAI: 'OpenAI 兼容（云端）',

  // 现有：Ollama 配置
  localOllamaService: '本地 Ollama 服务',
  localOllamaDesc: '使用本地部署的 Ollama 服务运行大语言模型',

  // 新增：OpenAI 兼容配置
  openaiCompatibleService: 'OpenAI 兼容服务',
  openaiCompatibleDesc: '使用兼容 OpenAI API 标准的云端大语言模型',

  // 新增：云端服务说明
  cloudServiceInfo: {
    title: 'ℹ️ 云端服务使用说明',
    description: '使用云端大模型时：',
    localDataSafe: '✅ 您的本地文件和索引数据存储在本地，不会上传',
    querySent: '⚠️ 搜索查询会发送到云端服务进行处理',
    betterUnderstanding: '💡 云端模型可提供更好的语义理解能力',
    recommendation: '如需完全隐私保护，请使用本地 Ollama 服务'
  },

  // 通用配置项
  modelName: '模型名称',
  modelNamePlaceholder: '如 qwen2.5:1.5b',
  modelNamePlaceholderCloud: '如 gpt-3.5-turbo、qwen-turbo、deepseek-chat',
  modelNameHelp: '如 qwen-turbo、deepseek-chat 等',

  serviceUrl: '服务地址',
  serviceUrlPlaceholder: 'http://localhost:11434',

  // 新增：云端配置项
  apiKey: 'API 密钥',
  apiKeyPlaceholder: 'sk-...',
  endpoint: '端点地址',
  endpointPlaceholder: 'https://api.openai.com/v1',
  endpointHelp: '可选，默认为官方 API 地址',

  // 操作
  testConnection: '测试连接',
  saveSettings: '保存设置',
  saveSuccessRestart: '设置已保存，请重启应用以生效',
  pleaseSaveFirst: '请先保存大语言模型配置',
  testData: '你好，请简单介绍一下你自己。'
}
```

### 6.2 英文翻译（en-US.ts）

```typescript
settingsLLM: {
  title: 'Large Language Model',
  subtitle: 'Configure LLM parameters',

  modelType: 'Model Type',
  modelTypeOllama: 'Ollama (Local)',
  modelTypeOpenAI: 'OpenAI Compatible (Cloud)',

  localOllamaService: 'Local Ollama Service',
  localOllamaDesc: 'Use locally deployed Ollama service to run LLM',

  openaiCompatibleService: 'OpenAI Compatible Service',
  openaiCompatibleDesc: 'Use cloud LLM that is compatible with OpenAI API standard',

  // Cloud Service Info
  cloudServiceInfo: {
    title: 'ℹ️ Cloud Service Usage',
    description: 'When using cloud LLM:',
    localDataSafe: '✅ Your local files and index data stay on device, not uploaded',
    querySent: '⚠️ Search queries will be sent to cloud service for processing',
    betterUnderstanding: '💡 Cloud models provide better semantic understanding',
    recommendation: 'For complete privacy, use local Ollama service'
  },

  modelName: 'Model Name',
  modelNamePlaceholder: 'e.g. qwen2.5:1.5b',
  modelNamePlaceholderCloud: 'e.g. gpt-3.5-turbo, qwen-turbo, deepseek-chat',
  modelNameHelp: 'e.g. qwen-turbo, deepseek-chat, etc.',

  serviceUrl: 'Service URL',
  serviceUrlPlaceholder: 'http://localhost:11434',

  apiKey: 'API Key',
  apiKeyPlaceholder: 'sk-...',
  endpoint: 'Endpoint URL',
  endpointPlaceholder: 'https://api.openai.com/v1',
  endpointHelp: 'Optional, defaults to official API endpoint',

  testConnection: 'Test Connection',
  saveSettings: 'Save Settings',
  saveSuccessRestart: 'Settings saved. Please restart the app to apply changes.',
  pleaseSaveFirst: 'Please save LLM configuration first',
  testData: 'Hello, please briefly introduce yourself.'
}
```

---

## 7. 安全设计

### 7.1 API 密钥加密存储

**存储方案**：数据库中加密存储 API 密钥

```python
# 加密工具函数
import base64
from cryptography.fernet import Fernet

# 生成密钥（首次启动时生成并保存）
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

### 7.2 日志脱敏

```python
# 日志输出时脱敏 API 密钥
def mask_api_key(api_key: str) -> str:
    """脱敏 API 密钥"""
    if not api_key or len(api_key) < 10:
        return "***"
    return f"{api_key[:7]}...{api_key[-4:]}"

# 示例：sk-abc123def456789 -> sk-abc1...6789
logger.info(f"使用 API 密钥: {mask_api_key(api_key)}")
```

### 7.3 传输安全

- 强制使用 HTTPS
- 验证 SSL 证书
- 超时控制（默认 60 秒）

---

## 8. 错误处理

### 8.1 错误码映射

| HTTP 状态码 | 错误类型 | 处理方式 |
|------------|---------|---------|
| 401 | API 密钥无效 | 提示用户检查 API 密钥 |
| 429 | 请求限流 | 提示用户稍后重试 |
| 500 | 服务器错误 | 提示用户联系供应商 |
| timeout | 网络超时 | 提示用户检查网络连接 |

### 8.2 异常处理

```python
class OpenAIException(Exception):
    """OpenAI API 异常基类"""
    pass

class OpenAIConnectionError(OpenAIException):
    """连接异常"""
    pass

class OpenAIAuthenticationError(OpenAIException):
    """认证异常"""
    pass

class OpenAIRateLimitError(OpenAIException):
    """限流异常"""
    pass

# 异常处理映射
def handle_openai_error(status_code: int, error_text: str) -> OpenAIException:
    """将 HTTP 错误转换为业务异常"""
    if status_code == 401:
        return OpenAIAuthenticationError("API 密钥无效或已过期")
    elif status_code == 429:
        return OpenAIRateLimitError("请求频率超限，请稍后重试")
    elif status_code >= 500:
        return OpenAIException(f"服务器错误: {error_text}")
    else:
        return OpenAIException(f"未知错误: {error_text}")
```

---

## 9. 测试方案

### 9.1 单元测试

```python
# tests/test_openai_llm_service.py
import pytest
from app.services.openai_llm_service import OpenAILLMService

@pytest.mark.asyncio
async def test_load_model_success():
    """测试模型加载成功"""
    config = {
        "api_key": "sk-test",
        "model": "gpt-3.5-turbo",
        "endpoint": "https://api.openai.com/v1"
    }
    service = OpenAILLMService(config)
    result = await service.load_model()
    assert result is True

@pytest.mark.asyncio
async def test_predict():
    """测试预测功能"""
    # 使用 mock 或真实 API 密钥进行测试
    pass
```

### 9.2 集成测试

```python
# tests/test_openai_integration.py
import pytest
from app.services.ai_model_manager import ai_model_service

@pytest.mark.asyncio
async def test_cloud_model_registration():
    """测试云模型注册"""
    config = {
        "model_type": "llm",
        "provider": "cloud",
        "model_name": "qwen-turbo",
        "config": {
            "api_key": "sk-test",
            "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1"
        }
    }

    result = await ai_model_service.register_model("llm_cloud_test", config)
    assert result is True
```

---

## 10. 部署清单

### 10.1 后端部署

| 文件 | 变更类型 | 操作 |
|------|---------|------|
| `backend/app/services/openai_llm_service.py` | 新建 | 创建文件 |
| `backend/app/services/ollama_service.py` | 修改 | 移除云端备选逻辑 |
| `backend/app/services/ai_model_manager.py` | 修改 | 支持云模型注册 |

### 10.2 前端部署

| 文件 | 变更类型 | 操作 |
|------|---------|------|
| `frontend/src/renderer/src/views/Settings.vue` | 修改 | 添加类型选择、动态表单和云端服务说明卡片 |
| `frontend/src/renderer/src/locales/zh-CN.ts` | 修改 | 添加 17 个翻译键（含云端服务说明 6 个） |
| `frontend/src/renderer/src/locales/en-US.ts` | 修改 | 添加 17 个翻译键（含云端服务说明 6 个） |

### 10.3 依赖变更

无新增依赖，复用现有 `aiohttp`。

---

## 11. 性能优化

### 11.1 连接池管理

```python
# 复用 HTTP 会话，避免重复创建
self.session = aiohttp.ClientSession(
    timeout=aiohttp.ClientTimeout(total=60),
    connector=aiohttp.TCPConnector(limit=10)  # 连接池大小
)
```

### 11.2 请求超时控制

```python
# 设置合理的超时时间
timeout = aiohttp.ClientTimeout(
    total=60,      # 总超时
    connect=10,    # 连接超时
    sock_read=30   # 读取超时
)
```

---

## 12. 相关文档

- [PRD文档](./openai-01-prd.md) - 产品需求文档
- [原型设计](./openai-02-原型.md) - 原型设计说明
- [架构决策](../../架构决策/AD-20260228-01-OpenAI兼容大模型服务.md) - 架构决策文档

---

**文档结束**

> **说明**：
> 1. 本技术方案遵循现有异步架构和代码规范
> 2. 向后兼容，保持现有 Ollama 配置可用
> 3. 无新增外部依赖，复用现有 aiohttp
> 4. 实施周期：2-3 天
