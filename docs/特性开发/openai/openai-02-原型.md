# OpenAI兼容大模型服务 - 原型设计

> **文档类型**：原型设计说明
> **特性状态**：已完成
> **创建时间**：2026-02-28
> **最后更新**：2026-02-28

---

## 1. 设计概述

### 1.1 设计目标

为小遥搜索的设置页面添加大语言模型类型选择功能，支持用户在 Ollama（本地）和 OpenAI 兼容（云端）之间切换配置。

### 1.2 设计原则

- **类型互斥**：用户只能选择一种模型类型，不能同时配置
- **配置简化**：每种类型只显示必要的配置项
- **即时验证**：支持测试连接功能，验证配置正确性
- **向后兼容**：保持原有 Ollama 配置可用
- **隐私透明**：明确告知用户云端服务的隐私风险，不默认选择

---

## 2. 页面结构

### 2.1 设置页面布局

```
┌─────────────────────────────────────────────────────────────────────┐
│ 设置                                                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  语音设置  │  大语言模型  │  视觉模型  │  内嵌模型  │           │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ 大语言模型设置                                                  │  │
│  ├───────────────────────────────────────────────────────────────┤  │
│  │                                                                 │  │
│  │  模型类型                                                       │  │
│  │  ┌─────────────────────────────────────────────────────────┐   │  │
│  │  │ [ Ollama（本地）                           ▼ ]        │   │  │
│  │  └─────────────────────────────────────────────────────────┘   │  │
│  │                                                                 │  │
│  │  ┌─ Ollama 配置 ─────────────────────────────────────────┐    │  │
│  │  │                                                            │    │  │
│  │  │  ℹ️ 本地 Ollama 服务                                      │    │  │
│  │  │     使用本地部署的 Ollama 服务运行大语言模型              │    │  │
│  │  │                                                            │    │  │
│  │  │  模型名称                                                 │    │  │
│  │  │  ┌────────────────────────────────────────────────────┐  │    │  │
│  │  │  │ qwen2.5:1.5b                                        │  │    │  │
│  │  │  └────────────────────────────────────────────────────┘  │    │  │
│  │  │                                                            │    │  │
│  │  │  服务地址                                                 │    │  │
│  │  │  ┌────────────────────────────────────────────────────┐  │    │  │
│  │  │  │ http://localhost:11434                             │  │    │  │
│  │  │  └────────────────────────────────────────────────────┘  │    │  │
│  │  │                                                            │    │  │
│  │  └────────────────────────────────────────────────────────┘    │  │
│  │                                                                 │  │
│  │  [ 测试连接 ]  [ 保存设置 ]                                    │  │
│  │                                                                 │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**当用户选择"OpenAI 兼容（云端）"时**：

```
┌─────────────────────────────────────────────────────────────────────┐
│ 设置                                                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ 大语言模型设置                                                  │  │
│  ├───────────────────────────────────────────────────────────────┤  │
│  │                                                                 │  │
│  │  模型类型                                                       │  │
│  │  ┌─────────────────────────────────────────────────────────┐   │  │
│  │  │ [ OpenAI 兼容（云端）                       ▼ ]        │   │  │
│  │  └─────────────────────────────────────────────────────────┘   │  │
│  │                                                                 │  │
│  │  ┌─ ℹ️ 云端服务使用说明 ─────────────────────────────────┐    │  │
│  │  │                                                       │    │  │
│  │  │ 使用云端大模型时：                                    │    │  │
│  │  │                                                       │    │  │
│  │  │ ✅ 您的本地文件和索引数据存储在本地，不会上传          │    │  │
│  │  │ ⚠️ 搜索查询会发送到云端服务进行处理                   │    │  │
│  │  │ 💡 云端模型可提供更好的语义理解能力                   │    │  │
│  │  │                                                       │    │  │
│  │  │ 如需完全隐私保护，请使用本地 Ollama 服务             │    │  │
│  │  └──────────────────────────────────────────────────────┘    │  │
│  │                                                                 │  │
│  │  ┌─ OpenAI 兼容配置 ──────────────────────────────────────┐    │  │
│  │  │                                                            │    │  │
│  │  │  ℹ️ OpenAI 兼容服务                                       │    │  │
│  │  │     使用兼容 OpenAI API 标准的云端大语言模型              │    │  │
│  │  │                                                            │    │  │
│  │  │  API 密钥  *                                              │    │  │
│  │  │  ┌────────────────────────────────────────────────────┐  │    │  │
│  │  │  │ sk-*****************************************      │  │    │  │
│  │  │  └────────────────────────────────────────────────────┘  │    │  │
│  │  │                                                            │    │  │
│  │  │  端点地址                                                  │    │  │
│  │  │  ┌────────────────────────────────────────────────────┐  │    │  │
│  │  │  │ https://dashscope.aliyuncs.com/compatible-mode/v1  │  │    │  │
│  │  │  └────────────────────────────────────────────────────┘  │    │  │
│  │  │  💡 可选，默认为官方 API 地址                             │    │  │
│  │  │                                                            │    │  │
│  │  │  模型名称  *                                              │    │  │
│  │  │  ┌────────────────────────────────────────────────────┐  │    │  │
│  │  │  │ qwen-turbo                                          │  │    │  │
│  │  │  └────────────────────────────────────────────────────┘  │    │  │
│  │  │  💡 如 qwen-turbo、deepseek-chat 等                     │    │  │
│  │  │                                                            │    │  │
│  │  └────────────────────────────────────────────────────────┘    │  │
│  │                                                                 │  │
│  │  [ 测试连接 ]  [ 保存设置 ]                                    │  │
│  │                                                                 │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**隐私警告说明**：
- 信息图标 + 蓝色边框，友好展示
- 默认展开，用户可手动关闭
- 清晰说明数据流向和云端优势

**说明**：两种配置表单是互斥显示的，根据用户选择的模型类型动态切换。

---

## 3. 交互设计

### 3.1 模型类型切换

**交互流程**：

```
用户操作：点击模型类型下拉框
    ↓
显示选项列表：
    • Ollama（本地）✓ 推荐使用
    • OpenAI 兼容（云端）⚠️ 有隐私风险
    ↓
用户选择"OpenAI 兼容"
    ↓
┌─ [重要提示] 隐私风险确认对话框 ───────────────────┐
│                                                     │
│  🔒 切换到云端大模型服务                            │
│                                                     │
│  您即将切换到云端大模型服务，请注意：                │
│                                                     │
│  ⚠️ 您的搜索查询会发送到第三方云端服务              │
│  ⚠️ 搜索内容可能会被云端服务商记录                  │
│  ⚠️ 需要网络连接，无法离线使用                      │
│                                                     │
│  💡 本地文件数据仍存储在您的设备上，不会上传        │
│                                                     │
│  [ 取消 ]  [ 我已了解，继续切换 ]                   │
│                                                     │
└─────────────────────────────────────────────────────┘
    ↓
用户点击"我已了解，继续切换"
    ↓
隐藏当前配置表单
    ↓
显示新类型配置表单（带淡入动画）
    ↓
展开隐私警告卡片（红色边框）
    ↓
表单字段自动聚焦
```

**动画效果**：
- 对话框弹出：缩放 + 淡入 300ms
- 表单切换：淡入淡出 200ms
- 卡片展开：高度过渡 300ms

### 3.2 配置表单验证

**实时验证规则**：

| 字段 | 类型 | 验证规则 | 错误提示 |
|------|------|---------|---------|
| API 密钥 | 云端必填 | 长度 ≥ 20，以 sk- 开头 | API 密钥格式不正确 |
| 端点地址 | 云端选填 | URL 格式验证 | 请输入有效的 URL |
| 模型名称 | 两者必填 | 长度 1-100 | 请输入模型名称 |
| 服务地址 | 本地必填 | URL 格式验证 | 请输入有效的 URL |

**验证时机**：
- 失焦验证：字段失去焦点时验证
- 提交验证：点击保存时全量验证
- 实时提示：错误信息实时显示

### 3.3 测试连接功能

**交互流程**：

```
用户点击"测试连接"
    ↓
按钮显示加载状态（转圈图标）
    ↓
发送测试请求到后端
    ↓
    ├─ 成功 → 显示成功提示（绿色 checkmark）
    │           "连接成功！模型响应正常"
    │
    └─ 失败 → 显示错误提示（红色 X 图标）
                "连接失败：{错误信息}"
    ↓
3 秒后提示自动消失
```

**状态样式**：

```css
/* 正常状态 */
.btn-test {
  background: #1890ff;
}

/* 加载状态 */
.btn-test.loading {
  background: #1890ff;
  opacity: 0.7;
}
.btn-test.loading::after {
  content: "";
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid #fff;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

/* 成功状态 */
.btn-test.success {
  background: #52c41a;
}

/* 失败状态 */
.btn-test.error {
  background: #ff4d4f;
}
```

### 3.4 保存设置流程

```
用户点击"保存设置"
    ↓
前端验证所有必填项
    ↓
    ├─ 验证失败 → 显示错误提示，终止流程
    │
    └─ 验证成功 → 检查provider类型
                   │
                   ├─ provider = 'local' → 直接保存
                   │                       ↓
                   │              构建 API 请求体
                   │              {
                   │                "model_type": "llm",
                   │                "provider": "local",
                   │                "model_name": "...",
                   │                "config": {...}
                   │              }
                   │                       ↓
                   │              发送 POST /api/config/ai-model
                   │                       ↓
                   │              ┌─ 成功 → 显示成功提示
                   │              │          "设置已保存，请重启应用以生效"
                   │              │
                   │              └─ 失败 → 显示错误提示
                   │                          "保存失败：{错误信息}"
                   │
                   └─ provider = 'cloud' → 再次确认隐私风险
                                        ↓
                        ┌─ [隐私提醒] 对话框 ───────────────────┐
                        │                                         │
                        │  🔒 确认保存云端大模型配置              │
                        │                                         │
                        │  您即将保存云端大模型配置，确认使用吗？  │
                        │                                         │
                        │  ⚠️ 搜索查询将发送到第三方云端服务      │
                        │  💡 本地文件数据不会上传，仍在您设备上  │
                        │                                         │
                        │  [ 取消 ]  [ 确认保存 ]                 │
                        │                                         │
                        └─────────────────────────────────────────┘
                                        ↓
                        ├─ 取消 → 终止流程
                        │
                        └─ 确认保存 → 发送请求
                                        ↓
                              发送 POST /api/config/ai-model
                                        ↓
                              ┌─ 成功 → 显示成功提示
                              │          "设置已保存，请重启应用以生效"
                              │          ℹ️ 同时显示：您的搜索将使用云端模型
                              │
                              └─ 失败 → 显示错误提示
                                          "保存失败：{错误信息}"
```

---

## 4. 隐私保护设计

### 4.1 云端服务说明卡片

**设计目标**：友好说明云端服务的工作方式和数据流向

**视觉设计**：
- **边框**：1px 蓝色边框
- **背景**：淡蓝色 (#e6f7ff)
- **图标**：信息图标 (ℹ️)
- **类型**：info（信息提示）

**内容结构**：
```
┌─ ℹ️ 云端服务使用说明 ─────────────────────┐
│                                            │
│ 使用云端大模型时：                         │
│                                            │
│ ✅ 您的本地文件和索引数据存储在本地，不会上传 │
│ ⚠️ 搜索查询会发送到云端服务进行处理        │
│ 💡 云端模型可提供更好的语义理解能力        │
│                                            │
│ 如需完全隐私保护，请使用本地 Ollama 服务  │
│                                            │
└────────────────────────────────────────────┘
```

**交互行为**：
- 默认展开，用户可通过关闭按钮收起
- 纯信息展示，友好说明不强制用户操作

### 4.2 切换确认对话框

**触发时机**：用户从"Ollama（本地）"切换到"OpenAI 兼容（云端）"时

**对话框设计**：
```
┌─ 切换到云端大模型服务 ─────────────────┐
│                                         │
│ 您即将切换到云端大模型服务，请注意：   │
│                                         │
│ ⚠️ 您的搜索查询会发送到第三方云端服务  │
│ ⚠️ 搜索内容可能会被云端服务商记录      │
│ ⚠️ 需要网络连接，无法离线使用          │
│                                         │
│ 💡 本地文件数据仍存储在您的设备上，    │
│    不会上传                            │
│                                         │
│        [ 取消 ]  [ 我已了解，继续切换 ] │
│                                         │
└─────────────────────────────────────────┘
```

**行为规则**：
- 必须主动点击"我已了解，继续切换"才能继续
- 点击"取消"保持当前选择（Ollama）
- 对话框不可绕过，确保用户知情

### 4.3 保存确认对话框

**触发时机**：用户保存云端大模型配置时

**对话框设计**：
```
┌─ 确认保存云端大模型配置 ───────────────┐
│                                         │
│ 您即将保存云端大模型配置，确认使用吗？ │
│                                         │
│ ⚠️ 搜索查询将发送到第三方云端服务      │
│ 💡 本地文件数据不会上传，仍在您设备上  │
│                                         │
│        [ 取消 ]  [ 确认保存 ]           │
│                                         │
└─────────────────────────────────────────┘
```

**保存成功提示**：
```
✅ 设置已保存，您的搜索将使用云端模型
ℹ️ 同时显示隐私提醒，强化用户认知
```

### 4.4 类型选择器标识

**下拉选项设计**：
```
模型类型：[ 请选择 ▼ ]

下拉列表：
  ✓ Ollama（本地）推荐使用
  ⚠️ OpenAI 兼容（云端）有隐私风险
```

**视觉标识**：
- 本地选项：绿色 ✓ 图标 + "推荐使用"标签
- 云端选项：橙色 ⚠️ 图标 + "有隐私风险"标签

### 4.5 默认配置策略

**默认选择**：
- 首次使用：默认选择"Ollama（本地）"
- 升级用户：保持原有配置不变

**配置持久化**：
- 保存用户最后一次的选择
- 重启应用后恢复上次的选择
- 不自动切换到云端服务

---

## 5. 组件设计

### 4.1 LLMSettingsCard 组件

**组件结构**：

```vue
<template>
  <div class="llm-settings-card">
    <!-- 类型选择器 -->
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

      <!-- 服务说明 -->
      <a-alert
        :message="t('settingsLLM.openaiCompatibleService')"
        :description="t('settingsLLM.openaiCompatibleDesc')"
        type="info"
        show-icon
        class="mt-3"
      />

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
        <div class="form-help">
          {{ t('settingsLLM.endpointHelp') }}
        </div>
      </a-form-item>

      <a-form-item :label="t('settingsLLM.modelName')">
        <a-input
          v-model:value="llmConfig.model_name"
          :placeholder="t('settingsLLM.modelNamePlaceholderCloud')"
        />
        <div class="form-help">
          {{ t('settingsLLM.modelNameHelp') }}
        </div>
      </a-form-item>
    </div>

    <!-- 操作按钮 -->
    <a-space>
      <a-button
        type="primary"
        :loading="llmConfig.isTesting"
        @click="testConnection"
      >
        {{ t('settingsLLM.testConnection') }}
      </a-button>
      <a-button
        :loading="llmConfig.isLoading"
        @click="saveConfig"
      >
        {{ t('settingsLLM.saveSettings') }}
      </a-button>
    </a-space>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { message } from 'ant-design-vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const llmConfig = reactive({
  provider: 'local',      // 'local' | 'cloud'
  model_name: 'qwen2.5:1.5b',
  base_url: 'http://localhost:11434',
  api_key: '',
  endpoint: 'https://api.openai.com/v1',
  isLoading: false,
  isTesting: false
})

const handleProviderChange = (value: string) => {
  if (value === 'cloud' && llmConfig.provider === 'local') {
    // 从本地切换到云端，显示确认对话框
    Modal.confirm({
      title: t('settingsLLM.switchConfirmTitle'),
      content: h('div', [
        h('p', t('settingsLLM.switchConfirmMessage')),
        h('ul', { style: { marginLeft: '20px' } }, [
          h('li', t('settingsLLM.switchConfirmRisk1')),
          h('li', t('settingsLLM.switchConfirmRisk2')),
          h('li', t('settingsLLM.switchConfirmRisk3'))
        ]),
        h('p', { style: { marginTop: '12px' } }, t('settingsLLM.switchConfirmNote'))
      ]),
      okText: t('settingsLLM.switchConfirmContinue'),
      cancelText: t('settingsLLM.switchConfirmCancel'),
      onOk: () => {
        llmConfig.provider = value
        llmConfig.model_name = 'gpt-3.5-turbo'
        llmConfig.endpoint = 'https://api.openai.com/v1'
      }
    })
  } else {
    llmConfig.provider = value
    // 重置部分配置
    if (value === 'local') {
      llmConfig.model_name = 'qwen2.5:1.5b'
      llmConfig.base_url = 'http://localhost:11434'
    } else {
      llmConfig.model_name = 'gpt-3.5-turbo'
      llmConfig.endpoint = 'https://api.openai.com/v1'
    }
  }
}

const testConnection = async () => {
  // 测试连接逻辑
}

const saveConfig = async () => {
  // 验证表单
  const isValid = await validateForm()
  if (!isValid) return

  // 如果是云端服务，再次确认隐私风险
  if (llmConfig.provider === 'cloud') {
    Modal.confirm({
      title: t('settingsLLM.saveConfirmTitle'),
      content: h('div', [
        h('p', t('settingsLLM.saveConfirmMessage')),
        h('p', t('settingsLLM.saveConfirmRisk')),
        h('p', { style: { marginTop: '12px' } }, t('settingsLLM.saveConfirmNote'))
      ]),
      okText: t('settingsLLM.saveConfirmSave'),
      cancelText: t('settingsLLM.saveConfirmCancel'),
      onOk: async () => {
        await doSaveConfig()
      }
    })
  } else {
    await doSaveConfig()
  }
}

const doSaveConfig = async () => {
  llmConfig.isLoading = true
  try {
    const response = await fetch('/api/config/ai-model', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model_type: 'llm',
        provider: llmConfig.provider,
        model_name: llmConfig.model_name,
        config: llmConfig.provider === 'local'
          ? { base_url: llmConfig.base_url }
          : { api_key: llmConfig.api_key, endpoint: llmConfig.endpoint }
      })
    })

    const result = await response.json()
    if (result.success) {
      const successMsg = llmConfig.provider === 'cloud'
        ? t('settingsLLM.saveSuccessCloud')
        : t('settingsLLM.saveSuccessRestart')

      message.success(successMsg, 5) // 延长显示时间到5秒
    } else {
      message.error(t('settingsLLM.error.configSaveFailed'))
    }
  } catch (error) {
    message.error(t('settingsLLM.error.configSaveFailed'))
  } finally {
    llmConfig.isLoading = false
  }
}
</script>

<style scoped>
.llm-settings-card {
  padding: var(--space-6);
}

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

/* 云端服务说明样式 */
.cloud-service-info {
  margin-bottom: var(--space-4);
}

.cloud-service-info-content {
  padding: var(--space-2);
}

.info-list {
  margin: var(--space-3) 0;
  padding-left: var(--space-4);
  list-style: none;
}

.info-list li {
  margin-bottom: var(--space-2);
  line-height: 1.6;
  padding-left: var(--space-2);
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
  margin: var(--space-3) 0;
  padding: var(--space-2);
  background: rgba(82, 196, 26, 0.1);
  border-left: 3px solid var(--success-color);
  border-radius: var(--radius-sm);
}

/* 模型类型选择器样式 */
:deep(.ant-select-selector) {
  border-radius: var(--radius-md);
}

:deep(.ant-select-selection-item) {
  font-weight: 500;
}

/* 间距辅助类 */
.mt-3 {
  margin-top: var(--space-3);
}
</style>
```

### 4.2 状态管理

```typescript
// llmConfig 状态结构
interface LLMConfig {
  provider: 'local' | 'cloud'    // 模型提供商类型
  model_name: string              // 模型名称
  base_url: string                // Ollama 服务地址（local）
  api_key: string                 // API 密钥（cloud）
  endpoint: string                // API 端点地址（cloud）
  isLoading: boolean              // 保存加载状态
  isTesting: boolean              // 测试连接状态
}
```

---

## 5. 国际化设计

### 5.1 翻译键组织

```typescript
// zh-CN.ts
settingsLLM: {
  title: '大语言模型',
  subtitle: '配置大语言模型参数',
  llmService: 'LLM服务',

  // 新增：类型选择
  modelType: '模型类型',
  modelTypeOllama: 'Ollama（本地）✓ 推荐使用',
  modelTypeOpenAI: 'OpenAI 兼容（云端）⚠️ 有隐私风险',

  // Ollama 配置
  localOllamaService: '本地 Ollama 服务',
  localOllamaDesc: '使用本地部署的 Ollama 服务运行大语言模型，数据完全私有化',

  // OpenAI 兼容配置（新增）
  openaiCompatibleService: 'OpenAI 兼容服务',
  openaiCompatibleDesc: '使用兼容 OpenAI API 标准的云端大语言模型',

  // 云端服务说明（新增）
  cloudServiceInfo: {
    title: 'ℹ️ 云端服务使用说明',
    description: '使用云端大模型时：',
    localDataSafe: '✅ 您的本地文件和索引数据存储在本地，不会上传',
    querySent: '⚠️ 搜索查询会发送到云端服务进行处理',
    betterUnderstanding: '💡 云端模型可提供更好的语义理解能力',
    recommendation: '如需完全隐私保护，请使用本地 Ollama 服务'
  },

  // 切换确认对话框（新增）
  switchConfirmTitle: '切换到云端大模型服务',
  switchConfirmMessage: '您即将切换到云端大模型服务，请注意：',
  switchConfirmRisk1: '⚠️ 您的搜索查询会发送到第三方云端服务',
  switchConfirmRisk2: '⚠️ 搜索内容可能会被云端服务商记录',
  switchConfirmRisk3: '⚠️ 需要网络连接，无法离线使用',
  switchConfirmNote: '💡 本地文件数据仍存储在您的设备上，不会上传',
  switchConfirmCancel: '取消',
  switchConfirmContinue: '我已了解，继续切换',

  // 保存确认对话框（新增）
  saveConfirmTitle: '确认保存云端大模型配置',
  saveConfirmMessage: '您即将保存云端大模型配置，确认使用吗？',
  saveConfirmRisk: '⚠️ 搜索查询将发送到第三方云端服务',
  saveConfirmNote: '💡 本地文件数据不会上传，仍在您设备上',
  saveConfirmCancel: '取消',
  saveConfirmSave: '确认保存',
  saveSuccessCloud: '设置已保存，您的搜索将使用云端模型',

  // 通用配置项
  modelName: '模型名称',
  modelNamePlaceholder: '如 qwen2.5:1.5b',
  modelNamePlaceholderCloud: '如 gpt-3.5-turbo、qwen-turbo、deepseek-chat',
  modelNameHelp: '如 qwen-turbo、deepseek-chat 等',

  // 服务/端点地址
  serviceUrl: '服务地址',
  serviceUrlPlaceholder: 'http://localhost:11434',
  endpoint: '端点地址',
  endpointPlaceholder: 'https://api.openai.com/v1',
  endpointHelp: '可选，默认为官方 API 地址',

  // API 密钥（新增）
  apiKey: 'API 密钥',
  apiKeyPlaceholder: 'sk-...',

  // 操作
  testConnection: '测试连接',
  saveSettings: '保存设置',
  saveSuccessRestart: '设置已保存，请重启应用以生效',
  pleaseSaveFirst: '请先保存大语言模型配置',
  testData: '你好，请简单介绍一下你自己。',

  // 错误提示
  error: {
    configLoadFailed: '配置加载失败',
    configSaveFailed: '配置保存失败',
    testFailed: '测试连接失败',
    invalidApiKey: 'API 密钥格式不正确',
    invalidUrl: '请输入有效的 URL 地址',
    required: '此字段为必填项'
  }
}
```

### 5.2 英文翻译

```typescript
// en-US.ts
settingsLLM: {
  title: 'Large Language Model',
  subtitle: 'Configure LLM parameters',
  llmService: 'LLM Service',

  modelType: 'Model Type',
  modelTypeOllama: 'Ollama (Local) ✓ Recommended',
  modelTypeOpenAI: 'OpenAI Compatible (Cloud) ⚠️ Privacy Risk',

  localOllamaService: 'Local Ollama Service',
  localOllamaDesc: 'Use locally deployed Ollama service to run LLM. Your data stays completely private.',

  openaiCompatibleService: 'OpenAI Compatible Service',
  openaiCompatibleDesc: 'Use cloud LLM that is compatible with OpenAI API standard',

  // Cloud Service Info (New)
  cloudServiceInfo: {
    title: 'ℹ️ Cloud Service Usage',
    description: 'When using cloud LLM:',
    localDataSafe: '✅ Your local files and index data stay on device, not uploaded',
    querySent: '⚠️ Search queries will be sent to cloud service for processing',
    betterUnderstanding: '💡 Cloud models provide better semantic understanding',
    recommendation: 'For complete privacy, use local Ollama service'
  },

  // Switch Confirmation Dialog (New)
  switchConfirmTitle: 'Switch to Cloud LLM Service',
  switchConfirmMessage: 'You are about to switch to cloud LLM service. Please note:',
  switchConfirmRisk1: '⚠️ Your search queries will be sent to third-party cloud services',
  switchConfirmRisk2: '⚠️ Search content may be logged by cloud service providers',
  switchConfirmRisk3: '⚠️ Requires network connection, cannot work offline',
  switchConfirmNote: '💡 Your local file data remains stored on your device and will not be uploaded',
  switchConfirmCancel: 'Cancel',
  switchConfirmContinue: 'I Understand, Continue',

  // Save Confirmation Dialog (New)
  saveConfirmTitle: 'Confirm Cloud LLM Configuration',
  saveConfirmMessage: 'You are about to save cloud LLM configuration. Confirm to proceed?',
  saveConfirmRisk: '⚠️ Search queries will be sent to third-party cloud services',
  saveConfirmNote: '💡 Local file data will not be uploaded, remains on your device',
  saveConfirmCancel: 'Cancel',
  saveConfirmSave: 'Confirm Save',
  saveSuccessCloud: 'Settings saved. Your searches will use cloud model.',

  modelName: 'Model Name',
  modelNamePlaceholder: 'e.g. qwen2.5:1.5b',
  modelNamePlaceholderCloud: 'e.g. gpt-3.5-turbo, qwen-turbo, deepseek-chat',
  modelNameHelp: 'e.g. qwen-turbo, deepseek-chat, etc.',

  serviceUrl: 'Service URL',
  serviceUrlPlaceholder: 'http://localhost:11434',
  endpoint: 'Endpoint URL',
  endpointPlaceholder: 'https://api.openai.com/v1',
  endpointHelp: 'Optional, defaults to official API endpoint',

  apiKey: 'API Key',
  apiKeyPlaceholder: 'sk-...',

  testConnection: 'Test Connection',
  saveSettings: 'Save Settings',
  saveSuccessRestart: 'Settings saved. Please restart the app to apply changes.',
  pleaseSaveFirst: 'Please save LLM configuration first',
  testData: 'Hello, please briefly introduce yourself.',

  error: {
    configLoadFailed: 'Failed to load configuration',
    configSaveFailed: 'Failed to save configuration',
    testFailed: 'Connection test failed',
    invalidApiKey: 'Invalid API key format',
    invalidUrl: 'Please enter a valid URL',
    required: 'This field is required'
  }
}
```

---

## 6. API 设计

### 6.1 配置保存接口

**请求**：

```http
PUT /api/config/ai-model
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

**云端配置示例**：

```http
PUT /api/config/ai-model
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

### 6.2 测试连接接口

**请求**：

```http
POST /api/config/ai-model/{id}/test
Content-Type: application/json

{
  "test_data": "你好，请简单介绍一下你自己。"
}
```

**响应**：

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

## 7. 样式规范

### 7.1 颜色系统

```css
/* 主题色 */
--primary-color: #1890ff;
--success-color: #52c41a;
--warning-color: #faad14;
--error-color: #ff4d4f;
--info-color: #1890ff;

/* 表面色 */
--surface-01: #ffffff;
--surface-02: #fafafa;
--surface-03: #f5f5f5;

/* 文本色 */
--text-primary: #262626;
--text-secondary: #595959;
--text-tertiary: #8c8c8c;
--text-disabled: #bfbfbf;

/* 边框色 */
--border-light: #f0f0f0;
--border-base: #d9d9d9;
```

### 7.2 间距系统

```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-8: 32px;
```

### 7.3 圆角系统

```css
--radius-sm: 4px;
--radius-md: 8px;
--radius-lg: 12px;
--radius-xl: 16px;
```

---

## 8. 响应式设计

### 8.1 断点定义

```css
/* 移动设备 */
@media (max-width: 576px) {
  .llm-settings-card {
    padding: var(--space-4);
  }

  .config-form {
    padding: var(--space-3);
  }
}

/* 平板设备 */
@media (min-width: 577px) and (max-width: 768px) {
  .llm-settings-card {
    padding: var(--space-5);
  }
}

/* 桌面设备 */
@media (min-width: 769px) {
  .llm-settings-card {
    padding: var(--space-6);
  }
}
```

---

## 9. 状态图

### 9.1 配置状态机

```
┌──────────────────────────────────────────────────────────────────┐
│                         配置状态机                                │
└──────────────────────────────────────────────────────────────────┘

   [未配置]
       │
       │ 用户打开设置页面
       ▼
   [加载配置] ────────────┐
       │                  │
       │ 加载成功          │ 加载失败
       ▼                  ▼
   [已加载:Ollama]    [错误状态]
   [已加载:Cloud]         │
       │                  │ 使用默认配置
       │ 用户修改类型       ▼
       ▼              [已加载:Ollama]
   [切换类型]───────────┘
       │
       │ 用户点击测试
       ▼
   [测试中:加载ing]
       │
       ├─ 成功 → [测试成功:显示提示]
       │
       └─ 失败 → [测试失败:显示错误]
       │
       │ 用户点击保存
       ▼
   [保存中:加载ing]
       │
       ├─ 成功 → [保存成功:显示提示]
       │
       └─ 失败 → [保存失败:显示错误]
```

---

## 10. 错误处理

### 10.1 错误场景

| 场景 | 错误提示 | 处理方式 |
|------|---------|---------|
| API 密钥格式错误 | "API 密钥格式不正确，应以 sk- 开头" | 内联显示，禁用保存按钮 |
| 端点地址无效 | "请输入有效的 URL 地址" | 内联显示，禁用保存按钮 |
| 网络连接失败 | "网络连接失败，请检查网络设置" | Toast 提示 |
| 测试连接失败 | "连接失败：API 密钥无效或端点地址错误" | Toast 提示 |
| 保存配置失败 | "配置保存失败，请稍后重试" | Toast 提示 |

### 10.2 错误提示样式

```css
/* 内联错误提示 */
.form-item-error {
  color: var(--error-color);
  font-size: 0.875rem;
  margin-top: var(--space-1);
}

/* Toast 提示 */
.ant-message-error {
  background: var(--error-color);
  color: #fff;
}

.ant-message-success {
  background: var(--success-color);
  color: #fff;
}
```

---

## 11. 可访问性

### 11.1 键盘导航

- `Tab`：在表单字段间切换焦点
- `Shift + Tab`：反向切换焦点
- `Enter`：提交表单（当前焦点在保存按钮）
- `Esc`：取消操作

### 11.2 屏幕阅读器支持

```html
<!-- 表单标签关联 -->
<a-form-item :label="t('settingsLLM.apiKey')">
  <a-input
    v-model:value="llmConfig.api_key"
    :placeholder="t('settingsLLM.apiKeyPlaceholder')"
    aria-label="API密钥输入框"
    aria-required="true"
  />
</a-form-item>

<!-- 错误提示关联 -->
<a-form-item
  :validate-status="errors.apiKey ? 'error' : ''"
  :help="errors.apiKey"
>
  <a-input aria-invalid="errors.apiKey ? 'true' : 'false'" />
</a-form-item>
```

---

## 12. 相关文档

- [PRD文档](./openai-01-prd.md) - 产品需求文档
- [架构决策](../../架构决策/AD-20260228-01-OpenAI兼容大模型服务.md) - 架构决策文档
- [技术方案](./openai-03-技术方案.md) - 技术实现方案（待创建）

---

## 13. 后续规划

### 13.1 短期优化

- [ ] 添加常用供应商预设（一键配置）
- [ ] 支持 API 密钥掩码显示
- [ ] 添加使用量统计入口

### 13.2 长期规划

- [ ] 多模型同时配置（高级模式）
- [ ] 模型性能对比测试
- [ ] 智能模型推荐

---

**文档结束**

> **说明**：
> 1. 本原型设计基于 Ant Design Vue 组件库
> 2. 所有交互遵循现有设置页面的设计规范
> 3. 向后兼容，保持原有 Ollama 配置可用
> 4. 支持中英双语国际化
> 5. **本地优先**：默认推荐本地服务，云端服务作为可选增强
> 6. **透明化设计**：清晰说明数据流向，本地文件不会上传
> 7. **尊重用户选择**：提供完全本地化的选项，不强制使用云端服务

> **产品定位说明**：
> 小遥搜索的核心价值是**本地私有化数据搜索**。OpenAI兼容大模型服务作为**可选增强功能**，用于提升语义理解质量。本地文件数据始终存储在用户设备上，只有搜索查询会发送到云端进行处理。
