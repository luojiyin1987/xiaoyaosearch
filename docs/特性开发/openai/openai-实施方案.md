# OpenAI兼容大模型服务 - 实施方案

> **文档类型**：实施方案
> **特性状态**：已批准，待开发
> **创建时间**：2026-02-28
> **决策时间**：2026-02-28
> **决策人**：产品负责人

---

## 1. 实施概述

### 1.1 目标

为小遥搜索添加 OpenAI 兼容的大语言模型服务支持，用户可选择使用云端大模型（如阿里云通义千问、DeepSeek、Moonshot 等）替代或补充本地 Ollama 模型。

### 1.2 核心决策点（已确定）

| 决策项 | 决策结果 | 状态 |
|--------|---------|------|
| **类型互斥设计** | Ollama 与 OpenAI 兼容二选一 | ✅ 已确定 |
| **统一接口** | 继承 BaseAIModel 基类 | ✅ 已确定 |
| **API 密钥存储** | 加密存储，日志脱敏 | ✅ 已确定 |
| **前端UI** | 类型选择器 + 动态表单 | ✅ 已确定 |
| **向后兼容** | 保持现有 Ollama 配置可用 | ✅ 已确定 |

### 1.3 设计原则

- **类型互斥**：用户只能选择 Ollama（本地）或 OpenAI 兼容（云端）其中一种
- **接口统一**：两种服务继承同一基类 `BaseAIModel`，保持接口一致性
- **最小侵入**：精简 Ollama 服务，移除云端备选逻辑，降低复杂度
- **安全优先**：API 密钥加密存储，日志脱敏处理
- **向后兼容**：保持现有 Ollama 配置可用，不破坏现有功能

---

## 2. 技术方案对比

### 2.1 OpenAI 服务实现方式对比

| 对比维度 | 方案A：新建服务类 | 方案B：扩展现有服务 |
|---------|-------------------|---------------------|
| **代码结构** | 清晰分离 | 混合在一起 |
| **维护性** | 高（独立维护） | 中（耦合度高） |
| **扩展性** | 高（易于添加新供应商） | 低（修改现有代码） |
| **测试难度** | 低（独立测试） | 高（需要考虑多种场景） |
| **向后兼容** | 完全兼容 | 可能破坏现有功能 |

**推荐：方案A（新建服务类）**
- 理由：代码清晰、易于维护、向后兼容

### 2.2 API 密钥存储方式对比

| 对比维度 | 明文存储 | Base64编码 | 对称加密 |
|---------|---------|-----------|---------|
| **安全性** | 低 | 低 | 高 |
| **实现难度** | 简单 | 简单 | 中等 |
| **性能影响** | 无 | 低 | 低 |
| **密钥管理** | 无需 | 无需 | 需要管理加密密钥 |

**推荐：对称加密（Fernet）**
- 理由：安全性高，性能影响可接受

---

## 3. 实施方案

### 3.1 推荐方案：独立服务类 + 类型互斥

#### 方案特点

```
用户选择类型 → 后端根据 provider 创建服务
     ↓                      ↓
┌────────────┐        ┌──────────────┐
│ local      │        │ cloud        │
│ ↓          │        │ ↓            │
│ OllamaLLM  │        │ OpenAILLM    │
│ Service    │        │ Service      │
└────────────┘        └──────────────┘
```

#### 核心设计

1. **独立服务类**：新建 `OpenAILLMService`，继承 `BaseAIModel`
2. **类型互斥**：前端配置表单互斥显示，后端根据 provider 创建对应服务
3. **统一接口**：两种服务实现相同的接口方法（load_model、predict、get_model_info）
4. **精简 Ollama**：移除 `ollama_service.py` 中的云端备选逻辑

#### 工作流程

```
┌─────────────────────────────────────────────────────────────────┐
│                      前端配置保存                                │
├─────────────────────────────────────────────────────────────────┤
│  用户选择类型：local 或 cloud                                   │
│  ┌─────────────────┐    ┌──────────────────┐                  │
│  │ Ollama（本地）   │    │ OpenAI（云端）   │                  │
│  │ - 模型名称      │    │ - API密钥       │                  │
│  │ - 服务地址      │    │ - 端点地址      │                  │
│  └─────────────────┘    │ - 模型名称      │                  │
│                          └──────────────────┘                  │
│                                                                  │
│  PUT /api/config/ai-model                                         │
│  {                                                                │
│    "model_type": "llm",                                          │
│    "provider": "local" | "cloud",  ← 类型标识                    │
│    "model_name": "...",                                          │
│    "config": {...}                                               │
│  }                                                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      后端服务创建                                │
├─────────────────────────────────────────────────────────────────┤
│  AIModelManager._create_default_models()                         │
│  └── 根据 provider 创建对应服务                                  │
│      if provider == "local":                                     │
│          model = create_ollama_service(config)                   │
│      elif provider == "cloud":                                   │
│          model = create_openai_compatible_service(config)       │
│                                                                  │
│  model_manager.register_model("llm", model)                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      统一服务调用                                │
├─────────────────────────────────────────────────────────────────┤
│  ai_model_service.text_generation(messages)                     │
│  └── llm_model.predict(messages)                                 │
│      ├── OllamaLLMService.predict()  或                           │
│      └── OpenAILLMService.predict()                              │
│                                                                  │
│  两种服务返回相同格式的结果：                                     │
│  {                                                                │
│    "content": "...",                                             │
│    "provider": "local" | "cloud",                                │
│    "usage": {...}                                                │
│  }                                                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. 实施步骤

### 第一阶段：后端服务实现（1-1.5天）

#### 4.1 创建 OpenAI 兼容服务

**新建文件：`backend/app/services/openai_llm_service.py`**

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

#### 4.2 精简 Ollama 服务

**修改文件：`backend/app/services/ollama_service.py`**

**删除内容：**
1. 移除 `_init_cloud_models()` 方法（约 30 行）
2. 移除 `_predict_with_cloud()` 方法（约 20 行）
3. 移除 `cloud_config` 相关配置项

**修改 predict 方法：**

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

#### 4.3 扩展模型管理器

**修改文件：`backend/app/services/ai_model_manager.py`**

**修改 `_create_default_models()` 方法：**

```python
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
                    # ========== 新增：根据 provider 创建不同的服务 ==========
                    if provider == "local":
                        from app.services.ollama_service import create_ollama_service
                        model = create_ollama_service(config)
                    elif provider == "cloud":
                        from app.services.openai_llm_service import create_openai_compatible_service
                        model = create_openai_compatible_service(config)
                    else:
                        logger.warning(f"不支持的 LLM provider: {provider}")
                        continue
                    # =========================================================

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

### 第二阶段：前端界面修改（0.5-1天）

#### 4.4 修改设置页面组件

**修改文件：`frontend/src/renderer/src/views/Settings.vue`**

**扩展响应式状态：**

```typescript
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
```

**添加类型选择器（模板）：**

```vue
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
```

**添加动态表单（模板）：**

```vue
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

<!-- OpenAI 兼容配置表单 -->
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
```

**添加类型切换处理（脚本）：**

```typescript
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
```

**修改保存配置方法：**

```typescript
const saveLLMConfig = async () => {
  llmConfig.isLoading = true
  try {
    const config: any = {
      model_type: 'llm',
      provider: llmConfig.provider,
      model_name: llmConfig.model_name,
      config: {}
    }

    // ========== 新增：根据 provider 添加不同配置 ==========
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
    // =========================================================

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
```

---

### 第三阶段：国际化更新（0.5天）

#### 4.5 添加中文翻译

**修改文件：`frontend/src/renderer/src/locales/zh-CN.ts`**

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

#### 4.6 添加英文翻译

**修改文件：`frontend/src/renderer/src/locales/en-US.ts`**

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

### 第四阶段：安全实现（可选，0.5天）

#### 4.7 API 密钥加密存储

**新建工具模块：`backend/app/utils/security.py`**

```python
import base64
from cryptography.fernet import Fernet

# 生成密钥（首次启动时生成并保存到环境变量或配置文件）
# ENCRYPTION_KEY 应该安全存储，这里仅为示例
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


def mask_api_key(api_key: str) -> str:
    """脱敏 API 密钥（用于日志输出）"""
    if not api_key or len(api_key) < 10:
        return "***"
    return f"{api_key[:7]}...{api_key[-4:]}"
```

---

## 5. 工作量与排期

### 5.1 工作量分解

| 阶段 | 任务 | 预计时间 |
|------|------|----------|
| 一 | 后端服务实现 | 1-1.5天 |
| 二 | 前端界面修改 | 0.5-1天 |
| 三 | 国际化更新 | 0.5天 |
| 四 | 安全实现（可选） | 0.5天 |
| 五 | 测试与验证 | 0.5-1天 |
| **总计** | | **2.5-3.5天** |

### 5.2 里程碑

| 里程碑 | 预计完成时间 | 关键交付物 |
|--------|-------------|-----------|
| M1: 后端服务完成 | Day 1 | OpenAI服务类、精简Ollama、扩展管理器 |
| M2: 前端界面完成 | Day 2 | 类型选择器、动态表单 |
| M3: 国际化完成 | Day 2 | 中英文翻译 |
| M4: 全部完成 | Day 3 | 功能测试通过、多供应商兼容 |

---

## 6. 风险与应对

| 风险项 | 风险等级 | 影响 | 应对措施 |
|--------|---------|------|---------|
| API 兼容性问题 | 中 | 部分供应商不兼容 | 严格遵循 OpenAI API 标准，添加兼容性测试 |
| API 密钥存储安全 | 高 | 用户数据安全风险 | 加密存储、日志脱敏、不上传云端 |
| Ollama 精简破坏现有功能 | 高 | 向后兼容性问题 | 充分回归测试、保持兼容 |
| 前端类型互斥逻辑错误 | 中 | 配置错误 | v-if/v-else 条件验证、添加测试 |
| 时间延期 | 低 | 进度延迟 | 优先实现 P0 任务，P1 任务可延后 |

---

## 7. 验收标准

### 功能验收

- [ ] 用户可以选择 Ollama（本地）或 OpenAI 兼容（云端）类型
- [ ] Ollama 配置表单正确显示和提交
- [ ] OpenAI 兼容配置表单正确显示和提交
- [ ] 测试连接功能正常工作
- [ ] 配置保存后重启生效
- [ ] 支持至少 4 种主流供应商（OpenAI、阿里云、DeepSeek、Moonshot）

### 质量验收

- [ ] 无 P0/P1 级别 Bug
- [ ] P2 级别 Bug ≤ 3
- [ ] 代码覆盖率 ≥ 80%
- [ ] API 密钥加密存储（如实施）
- [ ] 所有接口响应时间 < 3s

---

## 8. 决策建议

### 推荐方案：独立服务类 + 类型互斥

**优势：**

1. ✅ **代码清晰**：独立服务类，职责单一
2. ✅ **易于维护**：OpenAI 服务独立维护，不影响 Ollama
3. ✅ **易于扩展**：新增供应商只需配置，无需修改代码
4. ✅ **向后兼容**：保持现有 Ollama 配置可用

**权衡：**

1. ⚠️ 需要用户主动选择类型（无法同时使用）
2. ⚠️ 前端需要增加类型选择器

---

## 9. 决策记录

### 确定方案：独立服务类 + 类型互斥

**决策时间**：2026-02-28

**确定内容**：

| 决策项 | 决策结果 |
|--------|---------|
| 服务实现方式 | ✅ 新建独立服务类 |
| 类型选择 | ✅ 前端互斥选择 |
| 接口统一 | ✅ 继承 BaseAIModel |
| API 密钥存储 | ✅ 加密存储 + 日志脱敏 |
| 向后兼容 | ✅ 保持现有配置可用 |

**方案优势：**

1. ✅ **代码清晰**：独立服务类，职责单一
2. ✅ **易于维护**：OpenAI 服务独立维护
3. ✅ **易于扩展**：新增供应商只需配置
4. ✅ **向后兼容**：保持现有 Ollama 配置可用

**已知权衡：**

1. ⚠️ 用户需要主动选择类型（无法同时使用本地和云端）
2. ⚠️ 云端模型需要网络连接

---

## 10. 相关文档

- [PRD文档](./openai-01-prd.md) - 产品需求文档
- [原型设计](./openai-02-原型.md) - 原型设计说明
- [技术方案](./openai-03-技术方案.md) - 技术实现方案
- [任务清单](./openai-04-开发任务清单.md) - 任务分解
- [开发排期表](./openai-05-开发排期表.md) - 时间规划
- [架构决策](../../架构决策/AD-20260228-01-OpenAI兼容大模型服务.md) - 架构决策文档

---

**文档版本**: v1.0
**创建时间**: 2026-02-28
**最后更新**: 2026-02-28
**状态**: 已批准，待开发
