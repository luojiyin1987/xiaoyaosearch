# 云端嵌入模型调用能力 - 原型设计

> **文档类型**：原型设计说明
> **特性状态**：规划中
> **创建时间**：2026-03-26
> **最后更新**：2026-03-26

---

## 变更历史

| 版本 | 日期 | 变更内容 |
|-----|------|---------|
| v1.0 | 2026-03-26 | 初始版本 |
| v1.1 | 2026-03-26 | 修改为与大语言模型一致的UI&UX，使用下拉选择器而非单选按钮组 |
| v1.2 | 2026-03-26 | 移除提供商预设，支持所有OpenAI兼容API；添加向量维度配置选项 |

---

## 1. 设计概述

### 1.1 设计目标

为小遥搜索的"内嵌模型"配置选项卡添加本地/云端互斥选择功能，支持用户在本地模型和云端API之间切换配置。

**设计一致性**：与大语言模型的UI&UX保持完全一致，使用相同的交互模式和布局结构。

### 1.2 设计原则

- **类型互斥**：用户只能选择一种嵌入模型类型，不能同时配置
- **配置简化**：使用下拉选择器切换类型，配置表单动态显示
- **即时验证**：支持测试连接功能，验证配置正确性
- **向后兼容**：保持原有本地配置可用
- **隐私透明**：明确告知用户云端服务的隐私影响，推荐使用本地模型
- **一致性优先**：与大语言模型配置保持相同的交互模式

---

## 2. 页面结构

### 2.1 内嵌模型选项卡布局

**默认状态（选择本地）**：

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
│  │ 内嵌模型设置                                                  │  │
│  ├───────────────────────────────────────────────────────────────┤  │
│  │                                                                 │  │
│  │  模型类型                                                       │  │
│  │  ┌─────────────────────────────────────────────────────────┐   │  │
│  │  │ [ 本地                                    ▼ ]        │   │  │
│  │  └─────────────────────────────────────────────────────────┘   │  │
│  │                                                                 │  │
│  │  ┌─ 本地 配置 ─────────────────────────────────────┐    │  │
│  │  │                                                            │    │  │
│  │  │  ℹ️ 本地嵌入模型                                    │    │  │
│  │  │     使用本地部署的嵌入模型进行文本向量转换                │    │  │
│  │  │     • 完全离线，保护隐私                                  │    │  │
│  │  │     • 无需网络连接                                        │    │  │
│  │  │     • 免费使用                                            │    │  │
│  │  │                                                            │    │  │
│  │  │  模型名称                                                 │    │  │
│  │  │  ┌────────────────────────────────────────────────────┐  │    │  │
│  │  │  │ BAAI/bge-m3                                         │  │    │  │
│  │  │  └────────────────────────────────────────────────────┘  │    │  │
│  │  │                                                            │    │  │
│  │  │  运行设备                                                 │    │  │
│  │  │  ┌────────────────────────────────────────────────────┐  │    │  │
│  │  │  │ CPU（自动检测CUDA）                                  │  │    │  │
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

**选择云端API时**：

```
┌─────────────────────────────────────────────────────────────────────┐
│ 设置                                                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ 内嵌模型设置                                                  │  │
│  ├───────────────────────────────────────────────────────────────┤  │
│  │                                                                 │  │
│  │  模型类型                                                       │  │
│  │  ┌─────────────────────────────────────────────────────────┐   │  │
│  │  │ [ OpenAI 兼容（云端）                       ▼ ]        │   │  │
│  │  └─────────────────────────────────────────────────────────┘   │  │
│  │                                                                 │  │
│  │  ┌─ ℹ️ 云端服务使用说明 ─────────────────────────────────┐    │  │
│  │  │                                                       │    │  │
│  │  │ 使用云端嵌入模型时：                                  │    │  │
│  │  │                                                       │    │  │
│  │  │ ✅ 您的本地文件和索引数据存储在本地，不会上传          │    │  │
│  │  │ ⚠️ 搜索查询会发送到云端服务进行嵌入                    │    │  │
│  │  │ 💡 支持所有兼容OpenAI Embeddings API标准的服务         │    │  │
│  │  │ 💡 切换模型需要重建索引（不同模型的向量空间不兼容）      │    │  │
│  │  │                                                       │    │  │
│  │  │ 如需完全隐私保护，请使用本地模型                │    │  │
│  │  └──────────────────────────────────────────────────────┘    │  │
│  │                                                                 │  │
│  │  ┌─ OpenAI 兼容配置 ──────────────────────────────────────┐    │  │
│  │  │                                                            │    │  │
│  │  │  ℹ️ OpenAI兼容嵌入服务                                    │    │  │
│  │  │     使用兼容OpenAI Embeddings API标准的云端服务           │    │  │
│  │  │     支持所有OpenAI兼容的嵌入API                          │    │  │
│  │  │                                                            │    │  │
│  │  │  API 密钥  *                                              │    │  │
│  │  │  ┌────────────────────────────────────────────────────┐  │    │  │
│  │  │  │ sk-*****************************************      │  │    │  │
│  │  │  └────────────────────────────────────────────────────┘  │    │  │
│  │  │                                                            │    │  │
│  │  │  端点地址                                                  │    │  │
│  │  │  ┌────────────────────────────────────────────────────┐  │    │  │
│  │  │  │ https://api.openai.com/v1                          │  │    │  │
│  │  │  └────────────────────────────────────────────────────┘  │    │  │
│  │  │  💡 可选，默认为官方 API 地址                             │    │  │
│  │  │                                                            │    │  │
│  │  │  模型名称  *                                                │    │  │
│  │  │  ┌────────────────────────────────────────────────────┐  │    │  │
│  │  │  │ text-embedding-3-small                             │  │    │  │
│  │  │  └────────────────────────────────────────────────────┘  │    │  │
│  │  │  💡 如 text-embedding-3-small、bge-large-zh 等         │    │  │
│  │  │                                                            │    │  │
│  │  │  超时时间（秒）                                           │    │  │
│  │  │  ┌────────────────────────────────────────────────────┐  │    │  │
│  │  │  │ 30                                                 │  │    │  │
│  │  │  └────────────────────────────────────────────────────┘  │    │  │
│  │  │                                                            │    │  │
│  │  │  批处理大小                                               │    │  │
│  │  │  ┌────────────────────────────────────────────────────┐  │    │  │
│  │  │  │ 100                                                │  │    │  │
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

### 2.2 云端API配置字段说明

| 字段 | 说明 | 默认值 | 是否必填 |
|------|------|--------|----------|
| API密钥 | OpenAI兼容API的密钥 | 空 | 是 |
| 端点地址 | OpenAI兼容API的端点URL | `https://api.openai.com/v1` | 否 |
| 模型名称 | 要使用的嵌入模型名称 | 空 | 是 |
| 超时时间 | API请求超时时间（秒） | 30 | 否 |
| 批处理大小 | 批处理请求大小 | 100 | 否 |

**说明**：
- 支持所有兼容OpenAI Embeddings API标准的服务
- 用户需自行填写API密钥、端点地址和模型名称
- 切换模型需要重建索引（不同模型的向量空间不兼容）

---

## 3. 交互设计

### 3.1 模型类型切换

**交互流程**：

```
用户点击模型类型下拉框
    ↓
显示选项列表：
    • 本地 ✓ 推荐使用
    • OpenAI 兼容（云端）⚠️ 有隐私风险
    ↓
用户选择"OpenAI 兼容"
    ↓
┌─ [重要提示] 隐私风险确认对话框 ───────────────────┐
│                                                     │
│  🔒 切换到云端嵌入模型服务                            │
│                                                     │
│  您即将切换到云端嵌入模型服务，请注意：                │
│                                                     │
│  ⚠️ 搜索查询会发送到第三方云端服务进行嵌入            │
│  ⚠️ 搜索内容可能会被云端服务商记录                    │
│  ⚠️ 需要网络连接，无法离线使用                        │
│  ⚠️ API调用可能产生费用                               │
│                                                     │
│  💡 本地文件数据仍存储在您的设备上，不会上传          │
│  💡 本地模型将被卸载，释放内存                  │
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
展开隐私警告卡片（蓝色边框）
    ↓
表单字段自动聚焦
```

**下拉选项设计**：
```
模型类型：[ 本地（本地）               ▼ ]

下拉列表：
  ✓ 本地（推荐，免费离线）
  ⚠️ OpenAI 兼容（云端，有隐私风险）
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
| 超时时间 | 云端选填 | 1-120 | 请输入有效的超时时间 |
| 批处理大小 | 云端选填 | 1-1000 | 请输入有效的批处理大小 |

**验证时机**：
- 失焦验证：字段失去焦点时验证
- 提交验证：点击保存时全量验证
- 实时提示：错误信息实时显示

### 3.3 API密钥显示/隐藏

```
API密钥输入框默认显示：sk*******************
    ↓
用户点击"👁️ 显示"按钮
    ↓
切换为明文显示：sk-abcdefghijklmnopqrstuvwxyz1234567890
    ↓
按钮文本变为"🔒 隐藏"
    ↓
用户点击"🔒 隐藏"按钮
    ↓
切换回掩码显示
```

**输入框状态**：

| 状态 | 显示内容 | 按钮文本 |
|------|----------|----------|
| 隐藏（默认） | `sk*******************` | 👁️ 显示 |
| 显示 | `sk-abcdefghijklmnopqrstuvwxyz1234567890` | 🔒 隐藏 |
| 空白 | （空） | 👁️ 显示 |

### 3.4 测试连接功能

**交互流程**：

```
用户点击"测试连接"
    ↓
验证必填字段（API密钥、模型名称）
    ↓
    ├─ 验证失败 → 显示错误提示，终止流程
    │
    └─ 验证成功 → 按钮显示加载状态
                      ↓
                  按钮文本："测试中..." + 转圈动画
                      ↓
                  发送测试请求到后端
                      ↓
                  POST /api/config/ai-model/{id}/test
                      ↓
                      ├─ 成功 → 按钮变绿
                      │           显示：✓ 连接成功
                      │           显示成功提示："连接成功！模型响应正常"
                      │           3秒后按钮恢复原状
                      │
                      └─ 失败 → 按钮变红
                                  显示：✗ 连接失败
                                  显示错误提示："连接失败：{错误信息}"
                                  错误提示不自动消失，需手动关闭
```

**按钮状态样式**：

```css
/* 正常状态 */
.btn-test {
  background: #1890ff;
  color: #fff;
}

/* 加载状态 */
.btn-test.loading {
  background: #1890ff;
  opacity: 0.7;
  cursor: not-allowed;
}
.btn-test.loading::after {
  content: "";
  display: inline-block;
  width: 14px;
  height: 14px;
  margin-left: 8px;
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

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

### 3.5 保存设置流程

```
用户点击"保存设置"
    ↓
前端验证所有必填项
    ↓
    ├─ 验证失败 → 显示错误提示，高亮错误字段
    │
    └─ 验证成功 → 检查provider类型
                   │
                   ├─ provider = 'local' → 直接保存
                   │                       ↓
                   │              构建 API 请求体
                   │              {
                   │                "model_type": "embedding",
                   │                "provider": "local",
                   │                "model_name": "BAAI/bge-m3",
                   │                "config": {
                   │                  "device": "cpu"
                   │                }
                   │              }
                   │                       ↓
                   │              发送 PUT /api/config/ai-model
                   │                       ↓
                   │              ┌─ 成功 → 显示成功提示
                   │              │          "设置已保存"
                   │              │          "本地模型将在下次搜索时加载"
                   │              │
                   │              └─ 失败 → 显示错误提示
                   │                          "保存失败：{错误信息}"
                   │
                   └─ provider = 'cloud' → 再次确认
                                        ↓
                        ┌─ [确认对话框] 保存云端配置 ───────────────────┐
                        │                                              │
                        │  🔒 确认保存云端嵌入模型配置                   │
                        │                                              │
                        │  您即将保存云端嵌入模型配置，确认使用吗？       │
                        │                                              │
                        │  ⚠️ 搜索查询将发送到云端服务进行嵌入          │
                        │  ⚠️ API调用可能产生费用                        │
                        │  💡 本地文件数据不会上传，仍在您设备上          │
                        │                                              │
                        │  [ 取消 ]  [ 确认保存 ]                       │
                        │                                              │
                        └──────────────────────────────────────────────┘
                                        ↓
                        ├─ 取消 → 终止流程
                        │
                        └─ 确认保存 → 发送请求
                                        ↓
                              发送 PUT /api/config/ai-model
                                        ↓
                              ┌─ 成功 → 显示成功提示
                              │          "设置已保存"
                              │          "您的搜索将使用云端嵌入模型"
                              │          "本地模型已卸载"
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
- **关闭按钮**：支持用户手动关闭

**内容结构**：
```
┌─ ℹ️ 云端服务使用说明 ─────────────────────┐
│                                            │
│ 使用云端嵌入模型时：                         │
│                                            │
│ ✅ 您的本地文件和索引数据存储在本地，不会上传 │
│ ⚠️ 搜索查询会发送到云端服务进行嵌入        │
│ 💡 云端模型可提供更好的语义理解和多语言支持 │
│                                            │
│ 如需完全隐私保护，请使用本地模型     │
│                                            │
│                            [ ✕ 关闭 ]      │
│                                            │
└────────────────────────────────────────────┘
```

**交互行为**：
- 默认展开，用户可通过关闭按钮收起
- 收起后显示"ℹ️ 云端服务说明"折叠按钮
- 点击折叠按钮重新展开

### 4.2 切换确认对话框

**触发时机**：用户从"本地"切换到"云端API"时（仅首次）

**对话框设计**：
```
┌─ 切换到云端嵌入模型服务 ─────────────────────┐
│                                              │
│  🔒 切换到云端嵌入模型服务                    │
│                                              │
│  您即将切换到云端嵌入模型，请注意：            │
│                                              │
│  ⚠️ 搜索查询会发送到云端服务进行嵌入          │
│  ⚠️ 搜索内容可能会被云端服务商记录            │
│  ⚠️ 需要网络连接，无法离线使用                │
│  ⚠️ API调用可能产生费用                       │
│                                              │
│  💡 本地文件数据仍存储在您的设备上，不会上传  │
│  💡 本地模型将被卸载，释放内存          │
│                                              │
│        [ 取消 ]  [ 我已了解，继续切换 ]       │
│                                              │
└──────────────────────────────────────────────┘
```

**行为规则**：
- 必须主动点击"我已了解，继续切换"才能继续
- 点击"取消"保持当前选择（本地）
- 对话框不可绕过，确保用户知情
- 用户已确认过一次后，后续切换不再显示此对话框

### 4.3 保存确认对话框

**触发时机**：用户保存云端嵌入模型配置时

**对话框设计**：
```
┌─ 确认保存云端嵌入模型配置 ─────────────────────┐
│                                              │
│  您即将保存云端嵌入模型配置，确认使用吗？       │
│                                              │
│  ⚠️ 搜索查询将发送到云端服务进行嵌入          │
│  ⚠️ API调用可能产生费用                       │
│  💡 本地文件数据不会上传，仍在您设备上         │
│  💡 保存后本地模型将被卸载              │
│                                              │
│        [ 取消 ]  [ 确认保存 ]                 │
│                                              │
└──────────────────────────────────────────────┘
```

### 4.4 类型选择器标识

**下拉选项设计**：
```
模型类型：[ 请选择 ▼ ]

下拉列表：
  ✓ 本地（推荐，免费离线）
  ⚠️ OpenAI 兼容（云端，有隐私风险）
```

**视觉标识**：
- 本地选项：绿色 ✓ 图标 + "推荐使用"标签
- 云端选项：橙色 ⚠️ 图标 + "有隐私风险"标签

### 4.5 默认配置策略

**默认选择**：
- 首次使用：默认选择"本地"
- 升级用户：保持原有配置不变

**配置持久化**：
- 保存用户最后一次的选择
- 重启应用后恢复上次的选择
- 不自动切换到云端服务

---

## 5. 组件设计

### 5.1 EmbeddingSettingsCard 组件

**组件结构**：

```vue
<template>
  <div class="embedding-settings-card">
    <!-- 类型选择器 -->
    <a-form-item :label="t('settingsEmbedding.modelType')">
      <a-select
        v-model:value="embeddingConfig.provider"
        style="width: 200px"
        @change="handleProviderChange"
      >
        <a-select-option value="local">
          <CheckCircleOutlined style="color: #52c41a; margin-right: 8px;" />
          {{ t('settingsEmbedding.modelTypeLocal') }}
        </a-select-option>
        <a-select-option value="cloud">
          <WarningOutlined style="color: #faad14; margin-right: 8px;" />
          {{ t('settingsEmbedding.modelTypeCloud') }}
        </a-select-option>
      </a-select>
    </a-form-item>

    <!-- 本地 配置表单 -->
    <div v-if="embeddingConfig.provider === 'local'" class="config-form">
      <a-alert
        :message="t('settingsEmbedding.localModelInfo')"
        :description="t('settingsEmbedding.localModelDesc')"
        type="info"
        show-icon
      />

      <a-form-item :label="t('settingsEmbedding.modelName')">
        <a-input
          v-model:value="embeddingConfig.model_name"
          :placeholder="t('settingsEmbedding.modelNamePlaceholder')"
        />
      </a-form-item>

      <a-form-item :label="t('settingsEmbedding.device')">
        <a-input
          v-model:value="embeddingConfig.config.device"
          :placeholder="t('settingsEmbedding.devicePlaceholder')"
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
          <span>{{ t('settingsEmbedding.cloudServiceInfo.title') }}</span>
        </template>
        <template #description>
          <div class="cloud-service-info-content">
            <p>{{ t('settingsEmbedding.cloudServiceInfo.description') }}</p>
            <ul class="info-list">
              <li class="info-item-success">
                <CheckCircleOutlined />
                <span>{{ t('settingsEmbedding.cloudServiceInfo.localDataSafe') }}</span>
              </li>
              <li class="info-item-warning">
                <WarningOutlined />
                <span>{{ t('settingsEmbedding.cloudServiceInfo.querySent') }}</span>
              </li>
              <li class="info-item-tip">
                <BulbOutlined />
                <span>{{ t('settingsEmbedding.cloudServiceInfo.betterUnderstanding') }}</span>
              </li>
            </ul>
          </div>
        </template>
      </a-alert>

      <a-form-item
        :label="t('settingsEmbedding.apiKey')"
        :rules="[{ required: true, message: t('settingsEmbedding.apiKeyRequired') }]"
      >
        <a-input-password
          v-model:value="cloudConfig.api_key"
          :placeholder="t('settingsEmbedding.apiKeyPlaceholder')"
        />
      </a-form-item>

      <a-form-item :label="t('settingsEmbedding.endpoint')">
        <a-input
          v-model:value="cloudConfig.endpoint"
          :placeholder="t('settingsEmbedding.endpointPlaceholder')"
        />
        <div class="form-item-tip">
          <BulbOutlined />
          {{ t('settingsEmbedding.endpointTip') }}
        </div>
      </a-form-item>

      <a-form-item
        :label="t('settingsEmbedding.modelName')"
        :rules="[{ required: true, message: t('settingsEmbedding.modelNameRequired') }]"
      >
        <a-input
          v-model:value="cloudConfig.model"
          :placeholder="t('settingsEmbedding.modelNamePlaceholder')"
        />
        <div class="form-item-tip">
          <BulbOutlined />
          {{ t('settingsEmbedding.modelNameTip') }}
        </div>
      </a-form-item>

      <a-form-item :label="t('settingsEmbedding.embeddingDim')">
        <a-input-number
          v-model:value="cloudConfig.embedding_dim"
          :min="128"
          :max="4096"
          :step="128"
          style="width: 100%"
        />
        <div class="form-item-tip">
          <BulbOutlined />
          {{ t('settingsEmbedding.embeddingDimTip') }}
        </div>
      </a-form-item>
    </div>

    <!-- 操作按钮 -->
    <div class="form-actions">
      <a-button
        type="default"
        @click="handleTestConnection"
        :loading="testingConnection"
      >
        {{ t('settingsEmbedding.testConnection') }}
      </a-button>
      <a-button type="primary" @click="handleSave">
        {{ t('common.saveSettings') }}
      </a-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { message, Modal } from 'ant-design-vue';
import {
  CheckCircleOutlined,
  WarningOutlined,
  BulbOutlined
} from '@ant-design/icons-vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const embeddingConfig = reactive({
  provider: 'local',
  model_name: 'BAAI/bge-m3',
  config: {
    device: 'cpu'
  }
});

const cloudConfig = reactive({
  api_key: '',
  endpoint: 'https://api.openai.com/v1',
  model: 'text-embedding-3-small',
  timeout: 30,
  batch_size: 100
});

const testingConnection = ref(false);
const hasConfirmedSwitch = ref(false);

const handleProviderChange = (value: string) => {
  if (value === 'cloud' && !hasConfirmedSwitch.value) {
    Modal.confirm({
      title: t('settingsEmbedding.switchToCloudConfirm.title'),
      content: t('settingsEmbedding.switchToCloudConfirm.content'),
      okText: t('settingsEmbedding.switchToCloudConfirm.okText'),
      cancelText: t('common.cancel'),
      onOk: () => {
        hasConfirmedSwitch.value = true;
      },
      onCancel: () => {
        embeddingConfig.provider = 'local';
      }
    });
  }
};

const handleTestConnection = async () => {
  testingConnection.value = true;
  // 测试连接逻辑...
  setTimeout(() => {
    testingConnection.value = false;
    message.success(t('settingsEmbedding.testSuccess'));
  }, 1000);
};

const handleSave = () => {
  // 保存配置逻辑...
  message.success(t('settingsEmbedding.saveSuccess'));
};
</script>

<style scoped lang="less">
.embedding-settings-card {
  .config-form {
    margin-top: 16px;
    animation: fadeIn 0.2s ease-in-out;
  }

  .cloud-service-info {
    margin-bottom: 24px;
  }

  .cloud-service-info-content {
    .info-list {
      list-style: none;
      padding: 0;
      margin: 8px 0 0 0;

      li {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;

        &:last-child {
          margin-bottom: 0;
        }
      }

      .info-item-success { color: #52c41a; }
      .info-item-warning { color: #faad14; }
      .info-item-tip { color: #1890ff; }
    }
  }

  .form-item-tip {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: #999;
    margin-top: 4px;
  }

  .form-actions {
    margin-top: 24px;
    display: flex;
    gap: 8px;
    justify-content: flex-end;
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
```

---

## 6. 响应式设计

### 6.1 断点规范

| 断点 | 屏幕宽度 | 布局调整 |
|------|----------|----------|
| xs | < 576px | 单列布局，全宽表单 |
| sm | ≥ 576px | 单列布局，表单宽度100% |
| md | ≥ 768px | 单列布局，表单最大宽度600px |
| lg | ≥ 992px | 单列布局，表单最大宽度700px |
| xl | ≥ 1200px | 单列布局，表单最大宽度800px |

### 6.2 移动端适配

**小屏幕布局（< 576px）**：

```
┌─────────────────────────┐
│ ← 设置                 │
├─────────────────────────┤
│ 内嵌模型设置            │
├─────────────────────────┤
│ 模型类型                │
│ ┌─────────────────────┐ │
│ │ [本地 ▼]     │ │
│ └─────────────────────┘ │
│                         │
│ [配置表单 - 全宽]        │
│                         │
│ [测试连接] [保存设置]    │
└─────────────────────────┘
```

**移动端交互优化**：
- 下拉选择器全宽显示
- 表单字段全宽显示
- 按钮垂直排列，便于触控
- 对话框宽度90%，最大宽度400px

---

## 7. 状态设计

### 7.1 配置状态

| 状态 | 描述 | 视觉表现 |
|------|------|----------|
| 未配置 | 首次使用，未保存任何配置 | 显示默认本地配置，提示用户保存 |
| 已配置本地 | 已保存本地配置 | 显示本地配置表单，显示"当前使用：本地" |
| 已配置云端 | 已保存云端API配置 | 显示云端配置表单，显示"当前使用：云端API" |
| 配置错误 | 配置验证失败 | 高亮错误字段，显示错误提示 |

### 7.2 连接状态

| 状态 | 描述 | 视觉表现 |
|------|------|----------|
| 未测试 | 未进行连接测试 | 按钮显示"测试连接"，蓝色 |
| 测试中 | 正在测试连接 | 按钮显示"测试中..."，转圈动画 |
| 测试成功 | 连接测试成功 | 按钮显示"✓ 连接成功"，绿色，3秒后恢复 |
| 测试失败 | 连接测试失败 | 按钮显示"✗ 连接失败"，红色，保持状态 |

### 7.3 保存状态

| 状态 | 描述 | 视觉表现 |
|------|------|----------|
| 未保存 | 配置未保存 | 保存按钮可点击 |
| 保存中 | 正在保存配置 | 保存按钮显示加载状态 |
| 保存成功 | 配置保存成功 | 显示成功提示，保存按钮恢复 |
| 保存失败 | 配置保存失败 | 显示错误提示，保存按钮恢复 |

---

## 8. 无障碍设计

### 8.1 键盘导航

- **Tab键**：在表单字段间导航
- **Enter键**：提交表单
- **Esc键**：关闭对话框
- **方向键**：在单选按钮组内导航
- **空格键**：选中/取消选中单选按钮

### 8.2 屏幕阅读器支持

- 表单字段正确关联label
- 错误提示使用aria-live区域
- 对话框使用role="dialog"
- 加载状态使用aria-busy

### 8.3 焦点管理

- 对话框打开时，焦点移至对话框内
- 对话框关闭时，焦点返回触发元素
- 表单切换时，焦点移至新表单的第一个字段

---

## 9. 错误处理

### 9.1 表单验证错误

| 错误类型 | 显示方式 | 消息示例 |
|---------|---------|---------|
| API密钥为空 | 字段下方红色文字 | "请输入API密钥" |
| API密钥格式错误 | 字段下方红色文字 | "API密钥格式不正确" |
| 模型名称为空 | 字段下方红色文字 | "请输入模型名称" |
| 端点地址格式错误 | 字段下方红色文字 | "请输入有效的URL" |

### 9.2 连接测试错误

| 错误类型 | 显示方式 | 处理方式 |
|---------|---------|---------|
| 网络错误 | 按钮变红，显示错误提示 | 提示检查网络连接 |
| API密钥错误 | 按钮变红，显示错误提示 | 提示检查API密钥 |
| 模型不存在 | 按钮变红，显示错误提示 | 提示检查模型名称 |
| 服务器错误 | 按钮变红，显示错误提示 | 提示稍后重试 |

### 9.3 保存错误

| 错误类型 | 显示方式 | 处理方式 |
|---------|---------|---------|
| 网络错误 | 全局错误提示 | 提示检查网络连接 |
| 服务器错误 | 全局错误提示 | 提示稍后重试 |
| 配置冲突 | 全局错误提示 | 提示检查配置项 |

---

## 10. 索引重建进度UI

### 10.1 设计概述

当用户切换嵌入模型时，系统需要重建索引。本节描述索引重建进度的UI设计。

### 10.2 确认对话框

**本地 → 云端确认对话框**：

```
┌─────────────────────────────────────────────────────────┐
│ 切换嵌入模型                                              │
│                                                         │
│ 即将切换到云端嵌入模型：text-embedding-3-small            │
│                                                         │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ ⚠️ 切换后需要重建索引                                │ │
│ │ ⚠️ 预计耗时：5-10 分钟（取决于文件数量）               │ │
│ │ ⚠️ 云端API调用将产生费用                             │ │
│ │ ⚠️ 重建期间搜索功能暂时不可用                        │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│                                    [取消]  [确认并重建]  │
└─────────────────────────────────────────────────────────┘
```

**云端 → 本地确认对话框**：

```
┌─────────────────────────────────────────────────────────┐
│ 切换嵌入模型                                              │
│                                                         │
│ 即将切换到本地嵌入模型：BAAI/bge-m3                       │
│                                                         │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ ⚠️ 切换后需要重建索引                                │ │
│ │ ⚠️ 预计耗时：10-20 分钟（本地计算较慢）                │ │
│ │ ⚠️ 重建期间搜索功能暂时不可用                        │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│                                    [取消]  [确认并重建]  │
└─────────────────────────────────────────────────────────┘
```

---

### 10.3 重建进度弹窗

**进度弹窗设计**：

```
┌─────────────────────────────────────────────────────────┐
│ 正在重建索引                            ✕ (不可关闭)      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ████████████████░░░░░░░░░░░░░░░░░░░░░░░  45%          │
│                                                         │
│  📊 进度统计                                            │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 已处理：     4,500 / 10,000 文件                 │   │
│  │ 失败：       5 个文件                             │   │
│  │ 预计剩余：   3 分钟                               │   │
│  │ 当前文件：   /path/to/document.pdf                │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ⚠️ 重建期间请勿关闭应用                                 │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                    [后台运行]  [取消]    │
└─────────────────────────────────────────────────────────┘
```

---

### 10.4 Vue 组件实现

```vue
<template>
  <!-- 索引重建确认对话框 -->
  <a-modal
    v-model:open="showConfirmDialog"
    :title="$t('indexRebuild.confirmTitle')"
    :okText="$t('indexRebuild.confirm')"
    :cancelText="$t('common.cancel')"
    @ok="startRebuild"
  >
    <div class="rebuild-confirm">
      <p>{{ $t('indexRebuild.switchingTo') }}: {{ newModelName }}</p>

      <a-alert
        type="warning"
        show-icon
        style="margin-top: 16px"
      >
        <template #message>
          <p>{{ $t('indexRebuild.needRebuild') }}</p>
          <p>{{ $t('indexRebuild.estimatedTime') }}: {{ estimatedTime }}</p>
          <p v-if="isCloudModel">{{ $t('indexRebuild.cloudCostWarning') }}</p>
          <p>{{ $t('indexRebuild.unavailableWarning') }}</p>
        </template>
      </a-alert>
    </div>
  </a-modal>

  <!-- 索引重建进度弹窗 -->
  <a-modal
    v-model:open="showProgressDialog"
    :title="$t('indexRebuild.title')"
    :closable="false"
    :maskClosable="false"
  >
    <div class="rebuild-progress">
      <!-- 进度条 -->
      <a-progress
        :percent="progress.percent"
        :status="progress.status"
        :stroke-color="{
          '0%': '#108ee9',
          '100%': '#87d068'
        }"
      />

      <!-- 进度统计 -->
      <a-descriptions
        :column="1"
        size="small"
        style="margin-top: 16px"
      >
        <a-descriptions-item :label="$t('indexRebuild.processed')">
          {{ progress.processed.toLocaleString() }} /
          {{ progress.total.toLocaleString() }}
        </a-descriptions-item>

        <a-descriptions-item :label="$t('indexRebuild.failed')">
          <span v-if="progress.failed > 0" style="color: #ff4d4f">
            {{ progress.failed }}
          </span>
          <span v-else>{{ progress.failed }}</span>
        </a-descriptions-item>

        <a-descriptions-item :label="$t('indexRebuild.remainingTime')">
          {{ progress.remainingTime }}
        </a-descriptions-item>

        <a-descriptions-item :label="$t('indexRebuild.currentFile')">
          <span style="font-size: 12px; word-break: break-all">
            {{ progress.currentFile }}
          </span>
        </a-descriptions-item>
      </a-descriptions>

      <!-- 警告提示 -->
      <a-alert
        v-if="progress.status === 'active'"
        type="warning"
        :message="$t('indexRebuild.warning')"
        show-icon
        style="margin-top: 16px"
      />
    </div>

    <template #footer>
      <a-button
        @click="runInBackground"
        :disabled="progress.status === 'success' || progress.status === 'exception'"
      >
        {{ $t('indexRebuild.runInBackground') }}
      </a-button>
      <a-button
        danger
        @click="cancelRebuild"
        :disabled="progress.status === 'success' || progress.status === 'exception'"
      >
        {{ $t('common.cancel') }}
      </a-button>
    </template>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue';
import { message, Modal } from 'ant-design-vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

// 对话框状态
const showConfirmDialog = ref(false);
const showProgressDialog = ref(false);

// 模型信息
const newModelName = ref('');
const newModelProvider = ref<'local' | 'cloud'>('local');
const isCloudModel = ref(false);
const estimatedTime = ref('');

// 进度数据
const progress = reactive({
  percent: 0,
  status: 'active' as 'active' | 'success' | 'exception',
  processed: 0,
  total: 0,
  failed: 0,
  remainingTime: '',
  currentFile: ''
});

// 轮询定时器
let statusTimer: number | null = null;

// 预估时间计算
const calculateEstimatedTime = (fileCount: number, provider: string) => {
  const cloudRate = 100; // 每分钟100个文件（云端）
  const localRate = 50;  // 每分钟50个文件（本地）
  const rate = provider === 'cloud' ? cloudRate : localRate;
  const minutes = Math.ceil(fileCount / rate);

  if (minutes < 1) {
    return t('indexRebuild.lessThanMinute');
  } else if (minutes < 60) {
    return `${minutes} ${t('common.minute')}`;
  } else {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours} ${t('common.hour')} ${mins} ${t('common.minute')}`;
  }
};

// 显示确认对话框
const showRebuildConfirm = (modelProvider: string, modelName: string, fileCount: number) => {
  newModelProvider.value = modelProvider as 'local' | 'cloud';
  newModelName.value = modelName;
  isCloudModel.value = modelProvider === 'cloud';
  estimatedTime.value = calculateEstimatedTime(fileCount, modelProvider);
  showConfirmDialog.value = true;
};

// 开始重建
const startRebuild = async () => {
  showConfirmDialog.value = false;
  showProgressDialog.value = true;

  try {
    // 调用开始重建API
    const response = await fetch('/api/index/rebuild/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });

    if (!response.ok) {
      throw new Error('启动重建失败');
    }

    // 开始轮询状态
    startPolling();
  } catch (error) {
    message.error(t('indexRebuild.startFailed'));
    showProgressDialog.value = false;
  }
};

// 开始轮询
const startPolling = () => {
  statusTimer = window.setInterval(async () => {
    try {
      const response = await fetch('/api/index/rebuild/status');
      const data = await response.json();

      // 更新进度
      progress.percent = Math.round(data.data.progress_percent);
      progress.processed = data.data.processed_files;
      progress.total = data.data.total_files;
      progress.failed = data.data.failed_files;
      progress.currentFile = data.data.current_file || '';
      progress.remainingTime = formatTime(data.data.estimated_remaining_seconds);

      // 更新状态
      if (data.data.status === 'completed') {
        progress.status = 'success';
        stopPolling();
        message.success(t('indexRebuild.completed'));
        setTimeout(() => {
          showProgressDialog.value = false;
        }, 2000);
      } else if (data.data.status === 'failed') {
        progress.status = 'exception';
        stopPolling();
        message.error(t('indexRebuild.failed') + ': ' + data.data.error_message);
      } else if (data.data.status === 'cancelled') {
        progress.status = 'exception';
        stopPolling();
        message.info(t('indexRebuild.cancelled'));
        showProgressDialog.value = false;
      }
    } catch (error) {
      console.error('获取重建状态失败:', error);
    }
  }, 1000); // 每秒更新一次
};

// 停止轮询
const stopPolling = () => {
  if (statusTimer) {
    clearInterval(statusTimer);
    statusTimer = null;
  }
};

// 格式化时间
const formatTime = (seconds: number) => {
  if (seconds < 60) {
    return `${seconds}${t('common.second')}`;
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}${t('common.minute')}${secs}${t('common.second')}`;
  } else {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}${t('common.hour')}${minutes}${t('common.minute')}`;
  }
};

// 后台运行
const runInBackground = () => {
  showProgressDialog.value = false;
  message.info(t('indexRebuild.runningInBackground'));
};

// 取消重建
const cancelRebuild = async () => {
  Modal.confirm({
    title: t('indexRebuild.cancelConfirm'),
    content: t('indexRebuild.cancelConfirmMessage'),
    onOk: async () => {
      try {
        await fetch('/api/index/rebuild/cancel', { method: 'POST' });
        stopPolling();
        message.info(t('indexRebuild.cancelling'));
      } catch (error) {
        message.error(t('indexRebuild.cancelFailed'));
      }
    }
  });
};

// 组件挂载时检查是否有正在进行的重建
onMounted(async () => {
  try {
    const response = await fetch('/api/index/rebuild/status');
    const data = await response.json();

    if (data.data.status === 'running') {
      showProgressDialog.value = true;
      startPolling();
    }
  } catch (error) {
    console.error('检查重建状态失败:', error);
  }
});

// 组件卸载时停止轮询
onUnmounted(() => {
  stopPolling();
});

// 暴露方法供父组件调用
defineExpose({
  showRebuildConfirm
});
</script>

<style scoped lang="less">
.rebuild-confirm {
  p {
    margin-bottom: 8px;
  }
}

.rebuild-progress {
  :deep(.ant-descriptions-item-label) {
    font-weight: 500;
  }

  :deep(.ant-progress-text) {
    font-size: 14px;
  }
}
</style>
```

---

### 10.5 交互流程

```
用户点击"保存设置"
    ↓
检测到模型变更
    ↓
┌─────────────────────────────────────────┐
│ 后端返回: {                              │
│   "need_rebuild": true,                 │
│   "new_model": "text-embedding-3-small", │
│   "new_provider": "cloud",              │
│   "file_count": 10000,                  │
│   "estimated_time": "5-10分钟"          │
│ }                                        │
└─────────────────────────────────────────┘
    ↓
前端弹出确认对话框
    ↓
用户点击"确认并重建"
    ↓
调用 POST /api/index/rebuild/start
    ↓
前端弹出进度弹窗，开始轮询状态
    ↓
┌─────────────────────────────────────────┐
│ 每秒轮询 GET /api/index/rebuild/status  │
│ 更新进度条和统计信息                     │
└─────────────────────────────────────────┘
    ↓
重建完成
    ↓
显示成功提示，2秒后自动关闭弹窗
```

---

### 10.6 状态设计

| 重建状态 | 进度条状态 | 用户操作 |
|---------|-----------|---------|
| pending | 不显示进度条 | 可取消 |
| running | 蓝色进度条动画 | 可后台运行/取消 |
| paused | 黄色进度条 | 可继续/取消 |
| completed | 绿色100% | 只能关闭 |
| failed | 红色进度条 | 显示错误，只能关闭 |
| cancelled | 红色进度条 | 显示已取消，只能关闭 |

---

### 10.7 后台运行通知

**通知栏设计**：

```
┌─────────────────────────────────────────────────────────┐
│ ℹ️ 索引正在后台重建中，完成后将通知您                     │
└─────────────────────────────────────────────────────────┘
```

**完成后通知**：

```
┌─────────────────────────────────────────────────────────┐
│ ✅ 索引重建完成！新模型已生效                            │
│                                    [查看]  [关闭]        │
└─────────────────────────────────────────────────────────┘
```

---

## 11. 图标资源

### 10.1 Ant Design Icons

| 图标 | 用途 | 组件名 |
|------|------|--------|
| ✓ | 成功状态 | CheckCircleOutlined |
| ⚠️ | 警告状态 | WarningOutlined |
| ✗ | 失败状态 | CloseCircleOutlined |
| ℹ️ | 信息提示 | InfoCircleOutlined |
| 💡 | 提示信息 | BulbOutlined |
| 👁️ | 显示密码 | EyeOutlined |
| 🔒 | 隐藏密码 | EyeInvisibleOutlined |

---

**文档结束**

> **使用说明**：
> 1. 本原型设计文档基于Ant Design Vue组件库
> 2. 所有交互遵循项目现有设计规范
> 3. **与大语言模型配置保持完全一致的UI&UX**
> 4. 使用下拉选择器而非单选按钮组，与大语言模型交互模式一致
> 5. 支持所有兼容OpenAI Embeddings API标准的服务
> 6. 向量维度配置用于后端归一化处理，确保与本地索引兼容
> 7. 优先使用本地，保护用户隐私
