# 开发任务清单：云端嵌入模型调用能力

> **文档类型**：开发任务清单
> **特性状态**：规划中
> **创建时间**：2026-03-26
> **最后更新**：2026-03-26
> **预计总工期**：2-3天

---

## 设计原则：类型互斥 + 统一接口 + 维度兼容

本特性采用**类型互斥**设计，用户只能选择本地或云端嵌入模型其中一种：
- **类型互斥**：前端配置表单互斥显示，后端根据 provider 创建对应服务
- **统一接口**：两种服务继承同一基类 `BaseAIModel`
- **原始维度**：使用模型的原始向量维度，不做归一化处理
- **向后兼容**：保持现有本地嵌入模型可用，不破坏现有功能
- **安全优先**：API 密钥加密存储，日志脱敏处理
- **通用兼容**：支持所有 OpenAI Embeddings API 兼容的服务

---

## 任务清单总览

| 阶段 | 任务数 | 预计时间 | 优先级 |
|------|--------|----------|--------|
| 一、后端服务实现 | 4 | 1-1.5天 | P0 |
| 二、前端界面修改 | 3 | 0.5-1天 | P0 |
| 三、国际化更新 | 2 | 1天 | P0 |
| 四、测试与验证 | 3 | 0.5-1天 | P0 |
| **总计** | **12** | **3-4.5天** | - |

---

## 一、后端服务实现（1-1.5天）

### 1.1 OpenAI 兼容嵌入服务（新建）

| 任务 | 预计时间 | 优先级 | 状态 | 依赖 |
|------|----------|--------|------|------|
| 创建 `openai_embedding_service.py` 文件 | 0.5小时 | P0 | ⬜ | 无 |
| 实现 `OpenAIEmbeddingService` 类 | 2小时 | P0 | ⬜ | 1.1 |
| 实现 `load_model()` 方法 | 1小时 | P0 | ⬜ | 1.1 |
| 实现 `unload_model()` 方法 | 0.5小时 | P0 | ⬜ | 1.1 |
| 实现 `predict()` 核心方法 | 2小时 | P0 | ⬜ | 1.1 |
| 实现 `_call_embeddings_api()` 方法 | 1.5小时 | P0 | ⬜ | 1.1 |
| 实现 `_normalize_dimension()` 方法 | 1小时 | P0 | ⬜ | 1.1 |
| 实现 `_test_connection()` 验证方法 | 1小时 | P0 | ⬜ | 1.1 |
| 实现 `get_model_info()` 信息方法 | 0.5小时 | P1 | ⬜ | 1.1 |
| 添加批处理支持 | 1小时 | P0 | ⬜ | 1.1 |
| 添加错误重试机制（tenacity） | 1小时 | P0 | ⬜ | 1.1 |
| 添加错误处理和日志记录 | 1小时 | P0 | ⬜ | 1.1 |
| **小计** | **13.5小时** | | | |

**核心方法**：
- `load_model()`: 创建 HTTP 会话并验证 API 连接
- `predict()`: 调用 OpenAI 兼容 Embeddings API
- `_call_embeddings_api()`: 调用 `/v1/embeddings` 端点
- `_test_connection()`: 测试连接
- `get_model_info()`: 获取模型信息

**验收标准**：
- [ ] 支持所有兼容 OpenAI Embeddings API 标准的服务
- [ ] API 密钥通过参数传入，验证非空
- [ ] 端点地址可选，默认 OpenAI 官方地址
- [ ] 模型名称必填
- [ ] 向量维度可配置（默认 1024）
- [ ] 维度处理模式支持：truncate（截断）、project（投影）、native（原生）
- [ ] 批处理支持（默认 batch_size=100）
- [ ] 异常处理完善，错误信息清晰
- [ ] 重试机制正常工作（默认重试 3 次）

**文件位置**: `backend/app/services/openai_embedding_service.py`

---

### 1.2 AI 模型管理器扩展（修改）

| 任务 | 预计时间 | 优先级 | 状态 | 依赖 |
|------|----------|--------|------|------|
| 修改 `_create_default_models()` 方法 | 1小时 | P0 | ⬜ | 1.1 |
| 添加云端嵌入服务注册逻辑 | 1.5小时 | P0 | ⬜ | 1.1 |
| 导入 `create_openai_embedding_service` | 0.5小时 | P0 | ⬜ | 1.1 |
| 更新 `register_model()` 调用逻辑 | 1小时 | P0 | ⬜ | 无 |
| 实现嵌入模型类型互斥切换 | 1.5小时 | P0 | ⬜ | 1.1, 1.2 |
| 测试本地和云端嵌入模型切换 | 1小时 | P0 | ⬜ | 1.1, 1.2 |
| **小计** | **6.5小时** | | | |

**修改逻辑**：
```python
# 在 _create_default_models() 中添加
if model_type == "embedding":
    provider = model_config.get("provider", "local")

    if provider == "local":
        # 现有逻辑：创建本地嵌入服务
        from app.services.bge_embedding_service import create_bge_service
        embedding_service = create_bge_service(config)
        self.model_manager.register_model(model_id, embedding_service)

    elif provider == "cloud":
        # 新增逻辑：创建云端嵌入服务
        from app.services.openai_embedding_service import create_openai_embedding_service
        embedding_service = create_openai_embedding_service(config)
        self.model_manager.register_model(model_id, embedding_service)
```

**验收标准**：
- [ ] 能够正确创建本地嵌入服务
- [ ] 能够正确创建云端嵌入服务
- [ ] 支持两种类型模型互斥切换
- [ ] 切换时自动卸载旧模型，加载新模型
- [ ] 模型加载和卸载正常工作

**文件位置**: `backend/app/services/ai_model_manager.py`

---

### 1.3 工厂函数创建（新建）

| 任务 | 预计时间 | 优先级 | 状态 | 依赖 |
|------|----------|--------|------|------|
| 创建 `create_openai_embedding_service()` 函数 | 0.5小时 | P0 | ⬜ | 1.1 |
| 添加配置验证逻辑 | 1小时 | P0 | ⬜ | 1.1 |
| 添加错误处理 | 0.5小时 | P0 | ⬜ | 1.1 |
| **小计** | **2小时** | | | |

**函数签名**：
```python
def create_openai_embedding_service(config: Dict[str, Any]) -> OpenAIEmbeddingService:
    """
    工厂函数：创建OpenAI兼容嵌入服务

    Args:
        config: 配置字典

    Returns:
        OpenAIEmbeddingService: 嵌入服务实例

    Raises:
        AIModelException: 配置验证失败
    """
    # 验证必需参数
    # 创建服务实例
    # 返回实例
```

**验收标准**：
- [ ] 验证 api_key 必填
- [ ] 验证 model 必填
- [ ] 参数类型验证（embedding_dim 为整数等）
- [ ] 异常处理完善

**文件位置**: `backend/app/services/openai_embedding_service.py`

---

### 1.4 单元测试（新建）

| 任务 | 预计时间 | 优先级 | 状态 | 依赖 |
|------|----------|--------|------|------|
| 创建 `test_openai_embedding_service.py` 文件 | 0.5小时 | P0 | ⬜ | 1.1 |
| 编写服务创建测试 | 1小时 | P0 | ⬜ | 1.1 |
| 编写批处理测试 | 1小时 | P0 | ⬜ | 1.1 |
| 编写错误处理测试 | 1小时 | P0 | ⬜ | 1.1 |
| Mock API 调用 | 1.5小时 | P0 | ⬜ | 1.1 |
| **小计** | **4.5小时** | | | |

**测试用例**：
- [ ] 测试服务创建成功
- [ ] 测试服务创建失败（缺少 api_key）
- [ ] 测试服务创建失败（缺少 model）
- [ ] 测试批处理嵌入
- [ ] 测试 API 调用失败重试
- [ ] 测试错误日志记录

**文件位置**: `backend/tests/test_openai_embedding_service.py`

---

## 二、前端界面修改（0.5-1天）

### 2.1 内嵌模型配置选项卡修改

| 任务 | 预计时间 | 优先级 | 状态 | 依赖 |
|------|----------|--------|------|------|
| 扩展 `embeddingConfig` reactive 状态 | 0.5小时 | P0 | ⬜ | 无 |
| 添加 `provider` 字段（'local'/'cloud'） | 0.5小时 | P0 | ⬜ | 无 |
| 添加 `cloudConfig` 云端配置状态 | 0.5小时 | P0 | ⬜ | 无 |
| 添加模型类型下拉选择器 | 1小时 | P0 | ⬜ | 无 |
| 创建本地配置表单（v-if） | 0.5小时 | P0 | ⬜ | 无 |
| 创建云端配置表单（v-else） | 1.5小时 | P0 | ⬜ | 无 |
| 实现切换确认对话框 | 1小时 | P0 | ⬜ | 无 |
| 实现 `handleProviderChange` 方法 | 1小时 | P0 | ⬜ | 无 |
| 实现 `handleTestConnection` 方法 | 1小时 | P0 | ⬜ | 无 |
| 修改 `saveEmbeddingConfig()` 支持不同 provider | 1.5小时 | P0 | ⬜ | 无 |
| 修改 `loadEmbeddingModels()` 解析不同配置 | 1小时 | P0 | ⬜ | 无 |
| 添加测试连接按钮状态反馈 | 1小时 | P0 | ⬜ | 无 |
| 添加样式（config-form、form-actions） | 1小时 | P1 | ⬜ | 无 |
| **小计** | **13小时** | | | |

**云端配置表单字段**：
- API 密钥（a-input-password，必填）
- 端点地址（a-input，可选，默认 OpenAI 官方）
- 模型名称（a-input，必填）
- 向量维度（a-input-number，默认 1024，范围 128-4096）
- 维度处理模式（a-select，选项：truncate/project/native）

**验收标准**：
- [ ] 模型类型下拉选择器显示"本地"和"OpenAI 兼容（云端）"
- [ ] 选择"本地"时显示本地配置表单
- [ ] 选择"云端"时显示云端配置表单
- [ ] 切换到云端时显示隐私确认对话框
- [ ] 云端配置表单包含所有必需字段
- [ ] 测试连接按钮状态正常（未测试/测试中/成功/失败）
- [ ] 保存后端 API 调用成功
- [ ] 本地/云端切换正常工作
- [ ] 样式与大语言模型配置保持一致

**文件位置**: `frontend/src/views/Config.vue`（内嵌模型选项卡部分）

---

### 2.2 组件样式优化

| 任务 | 预计时间 | 优先级 | 状态 | 依赖 |
|------|----------|--------|------|------|
| 添加 config-form 样式类 | 0.5小时 | P1 | ⬜ | 2.1 |
| 添加 form-item-tip 样式类 | 0.5小时 | P1 | ⬜ | 2.1 |
| 添加 cloud-service-info 样式类 | 0.5小时 | P1 | ⬜ | 2.1 |
| 添加按钮状态样式（loading/success/error） | 1小时 | P1 | ⬜ | 2.1 |
| 添加淡入淡出动画效果 | 0.5小时 | P2 | ⬜ | 2.1 |
| **小计** | **3小时** | | | |

**验收标准**：
- [ ] 配置表单有灰色背景
- [ ] 提示信息使用灰色小字
- [ ] 云端服务说明卡片有蓝色边框
- [ ] 测试连接按钮状态颜色正确（未测试：蓝色、成功：绿色、失败：红色）
- [ ] 表单切换有淡入淡出动画

**文件位置**: `frontend/src/views/Config.vue`（`<style scoped>` 部分）

---

## 三、国际化更新（1天）

### 3.1 后端国际化（新增）

| 任务 | 预计时间 | 优先级 | 状态 | 依赖 |
|------|----------|--------|------|------|
| 更新 `zh_CN.json` 添加云端嵌入模型翻译 | 0.5小时 | P0 | ⬜ | 无 |
| 更新 `en_US.json` 添加云端嵌入模型翻译 | 0.5小时 | P0 | ⬜ | 3.1 |
| 添加索引重建相关翻译键 | 1小时 | P0 | ⬜ | 无 |
| 修改 API 端点支持 i18n | 1.5小时 | P0 | ⬜ | 1.2 |
| 修改配置测试接口支持 i18n | 1小时 | P0 | ⬜ | 1.2 |
| **小计** | **4.5小时** | | | |

**新增后端翻译键**（约 30 个）：
```json
{
  "model": {
    "cloud_embedding_success": "云端嵌入模型测试成功，向量维度: {dimension}",
    "cloud_embedding_failed": "云端嵌入模型测试失败：{error}",
    "cloud_connection_timeout": "云端API连接超时",
    "cloud_auth_failed": "云端API认证失败：{error}",
    "rebuild_already_running": "重建任务正在进行中，进度：{progress}%",
    "rebuild_no_current_model": "没有当前嵌入模型配置",
    "rebuild_backup_failed": "索引备份失败：{error}",
    // ... 更多翻译键
  },
  "index_rebuild": {
    "title": "索引重建",
    "status_running": "重建中",
    "success": "索引重建成功",
    // ... 更多翻译键
  }
}
```

**API 端点修改示例**：
```python
from app.core.i18n import i18n, get_locale_from_header

@router.post("/start")
async def start_rebuild(request: RebuildRequest, accept_language: str = Header(None)):
    locale = get_locale_from_header(accept_language)
    # 错误处理时使用 i18n
    raise HTTPException(
        status_code=409,
        detail={
            "message": i18n.t("model.rebuild_already_running", locale, progress=50)
        }
    )
```

**验收标准**：
- [ ] `zh_CN.json` 包含所有云端嵌入模型翻译键
- [ ] `en_US.json` 包含对应的英文翻译
- [ ] API 端点支持 `Accept-Language` 头
- [ ] 错误消息根据语言环境返回对应语言
- [ ] 支持参数化翻译（如 `{dimension}`、`{progress}`）

**文件位置**:
- `backend/app/locales/zh_CN.json`
- `backend/app/locales/en_US.json`
- `backend/app/api/index_rebuild.py`
- `backend/app/api/config.py`

---

### 3.2 前端国际化（zh-CN）

| 任务 | 预计时间 | 优先级 | 状态 | 依赖 |
|------|----------|--------|------|------|
| 添加嵌入模型相关翻译键 | 1小时 | P0 | ⬜ | 无 |
| 添加云端配置相关翻译 | 1小时 | P0 | ⬜ | 无 |
| 添加向量维度相关翻译 | 0.5小时 | P0 | ⬜ | 无 |
| 添加错误提示相关翻译 | 0.5小时 | P0 | ⬜ | 无 |
| **小计** | **3小时** | | | |

**新增翻译键**（约 20 个）：
```yaml
embedding:
  title: 内嵌模型
  providerType: 模型类型
  modelTypeLocal: 本地
  modelTypeCloud: OpenAI 兼容（云端）

  # 本地配置
  localModelInfo: 本地嵌入模型
  localModelDesc: 使用本地部署的嵌入模型进行文本向量转换

  # 云端配置
  cloudConfig:
    title: 云端配置
    apiKey: API 密钥
    apiKeyPlaceholder: 请输入 API 密钥
    endpoint: 端点地址
    endpointPlaceholder: 请输入端点地址
    endpointTip: 可选，默认为 OpenAI 官方 API 地址
    model: 模型名称
    modelPlaceholder: 请输入模型名称
    modelTip: 如 text-embedding-3-small、bge-large-zh 等
    timeout: 超时时间（秒）
    timeoutPlaceholder: 请输入超时时间
    timeoutTip: API 请求超时时间
    batchSize: 批处理大小
    batchSizePlaceholder: 请输入批处理大小
    batchSizeTip: 批处理请求大小

  # 云端服务说明
  cloudServiceInfo:
    title: 云端服务使用说明
    description: 使用云端嵌入模型时：
    localDataSafe: ✅ 您的本地文件和索引数据存储在本地，不会上传
    querySent: ⚠️ 搜索查询会发送到云端服务进行嵌入
    betterUnderstanding: 💡 支持所有兼容 OpenAI Embeddings API 标准的服务
    needRebuildIndex: 💡 切换模型需要重建索引（不同模型的向量空间不兼容）

  # 测试连接
  testConnection: 测试连接
  testing: 测试中...
  testSuccess: 连接成功
  testFailed: 连接失败
  testSuccessMessage: 连接成功！模型响应正常
  testFailedMessage: 连接失败：{error}

  # 切换确认
  switchToCloudConfirm:
    title: 切换到云端嵌入模型服务
    content: 您即将切换到云端嵌入模型服务，请注意：...
    okText: 我已了解，继续切换

  # 保存
  saveSuccessCloud: 设置已保存，您的搜索将使用云端嵌入模型
  saveSuccessLocal: 设置已保存，本地嵌入模型将在下次搜索时加载
  saveFailed: 保存失败：{error}

  # 验证
  validation:
    required: 请输入 {field}
    apiKeyRequired: 请输入 API 密钥
    modelRequired: 请输入模型名称
    apiKeyFormat: API 密钥格式不正确
    embeddingDimRange: 向量维度必须在 {min} 到 {max} 之间
```

**文件位置**: `frontend/src/locales/zh-CN.ts`

---

### 3.3 前端英文翻译（en-US）

| 任务 | 预计时间 | 优先级 | 状态 | 依赖 |
|------|----------|--------|------|------|
| 翻译所有新增前端翻译键 | 2小时 | P1 | ⬜ | 3.2 |
| **小计** | **2小时** | | | |

**验收标准**：
- [ ] 所有新增翻译键都有英文翻译
- [ ] 翻译准确、简洁、专业
- [ ] 与中文翻译键一一对应

**文件位置**: `frontend/src/locales/en-US.ts`

---

## 四、索引重建功能（1-1.5天）

### 4.1 后端索引重建服务

| 任务 | 预计时间 | 优先级 | 状态 | 依赖 |
|------|----------|--------|------|------|
| 创建索引重建服务类 | 2小时 | P0 | ⬜ | 一、4.3 |
| 实现进度跟踪机制 | 1.5小时 | P0 | ⬜ | 一、4.3 |
| 实现备份和回滚逻辑 | 1.5小时 | P0 | ⬜ | 一、4.3 |
| 实现批量文件嵌入 | 2小时 | P0 | ⬜ | 一、4.3 |
| 实现进度查询接口 | 1小时 | P0 | ⬜ | 一、4.3 |
| 实现重建控制接口 | 1.5小时 | P0 | ⬜ | 一、4.3 |
| **小计** | **9.5小时** | | | |

**核心类设计**：

```python
# backend/app/services/index_rebuild_service.py
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from pathlib import Path
import shutil
import logging

logger = logging.getLogger(__name__)

class RebuildStatus(Enum):
    """索引重建状态"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class RebuildTask:
    """索引重建任务（内存状态，不持久化）"""
    task_id: str                              # 任务ID
    status: RebuildStatus                      # 当前状态
    total_files: int                           # 总文件数
    processed_files: int = 0                   # 已处理文件数
    failed_files: int = 0                      # 失败文件数
    start_time: datetime = None                # 开始时间
    current_file: str = ""                      # 当前文件
    error_message: str = ""                     # 错误信息

    # 模型信息
    previous_model: Dict[str, Any] = None       # 原模型配置
    new_model: Dict[str, Any] = None            # 新模型配置

    # 备份信息
    backup_path: Path = None                    # 备份目录

    @property
    def progress_percent(self) -> float:
        """进度百分比"""
        if self.total_files == 0:
            return 0.0
        return (self.processed_files / self.total_files) * 100

    @property
    def elapsed_seconds(self) -> int:
        """已用时间（秒）"""
        if not self.start_time:
            return 0
        return int((datetime.now() - self.start_time).total_seconds())

    @property
    def estimated_remaining_seconds(self) -> int:
        """预计剩余时间（秒）"""
        if self.processed_files == 0:
            return 0
        elapsed = self.elapsed_seconds
        per_file_time = elapsed / self.processed_files
        remaining = self.total_files - self.processed_files
        return int(remaining * per_file_time)


class IndexRebuildService:
    """索引重建服务（独立状态管理）"""

    def __init__(self):
        # 内存状态，不写数据库
        self.current_task: Optional[RebuildTask] = None
        self.backup_path = Path("index.backup")
        self.index_path = Path("index")

    async def start_rebuild(
        self,
        new_model_config: Dict[str, Any],
        force: bool = False
    ) -> dict:
        """开始索引重建"""
        # 1. 检查是否已有任务
        if self.current_task and self.current_task.status == RebuildStatus.RUNNING:
            raise RuntimeError("已有重建任务正在进行")

        # 2. 获取当前模型配置
        current_model = await self._get_current_model()

        # 3. 备份当前索引
        await self._backup_index()

        # 4. 获取文件列表（从当前索引元数据，不扫描）
        files = await self._get_indexed_files()

        # 5. 创建内存任务（不写数据库）
        self.current_task = RebuildTask(
            task_id=f"rebuild_{int(datetime.now().timestamp())}",
            status=RebuildStatus.RUNNING,
            total_files=len(files),
            start_time=datetime.now(),
            previous_model=current_model,
            new_model=new_model_config,
            backup_path=self.backup_path
        )

        # 6. 异步执行重建
        asyncio.create_task(self._execute_rebuild(files))

        return {
            "task_id": self.current_task.task_id,
            "status": "running",
            "total_files": len(files),
            "previous_model": current_model["model_name"],
            "new_model": new_model_config["model"]
        }

    async def _get_current_model(self) -> Dict[str, Any]:
        """获取当前嵌入模型配置"""
        from app.services.ai_model_manager import ai_model_manager
        model = ai_model_manager.get_model("embedding")
        return {
            "provider": model.provider,
            "model_name": model.model_name,
            "config": model.config
        }

    async def _get_indexed_files(self) -> list:
        """获取当前索引的文件列表（不扫描）"""
        # 从索引元数据获取
        metadata_path = self.index_path / "metadata.json"
        if metadata_path.exists():
            import json
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                return metadata.get("files", [])
        return []

    async def _backup_index(self):
        """备份当前索引"""
        if self.backup_path.exists():
            shutil.rmtree(self.backup_path)
        shutil.copytree(self.index_path, self.backup_path)
        logger.info(f"索引已备份到: {self.backup_path}")

    async def _execute_rebuild(self, files: list):
        """执行索引重建"""
        try:
            # 批量嵌入文件
            batch_size = 100
            for i in range(0, len(files), batch_size):
                batch = files[i:i + batch_size]

                # 调用嵌入服务
                embeddings = await self._embed_batch(batch)

                # 更新进度
                self.current_task.processed_files += len(batch)
                self.current_task.current_file = batch[-1] if batch else ""

                logger.info(f"重建进度: {self.current_task.progress_percent:.1f}%")

            # 构建新索引
            await self._build_new_index()

            # 更新系统配置
            await self._update_system_model()

            # 标记完成
            self.current_task.status = RebuildStatus.COMPLETED
            logger.info(f"索引重建完成: {self.current_task.task_id}")

        except Exception as e:
            logger.error(f"索引重建失败: {e}")
            self.current_progress.status = RebuildStatus.FAILED
            self.current_progress.error_message = str(e)
            # 自动回滚
            await self.rollback()

    async def cancel_rebuild(self) -> dict:
        """取消索引重建"""
        if not self.current_progress:
            raise RuntimeError("当前无重建任务")

        self.current_progress.status = RebuildStatus.CANCELLED

        # 回滚到备份
        await self.rollback()

        return {
            "rebuild_id": self.current_progress.rebuild_id,
            "status": "cancelled",
            "rollback_success": True
        }

    async def rollback(self):
        """回滚到备份索引"""
        if self.backup_path.exists():
            if self.index_path.exists():
                shutil.rmtree(self.index_path)
            shutil.copytree(self.backup_path, self.index_path)
            logger.info("已回滚到备份索引")

        # 恢复原模型配置
        await self._restore_previous_model()

    def get_status(self) -> dict:
        """获取重建状态"""
        if not self.current_progress:
            return {"status": "none"}

        return {
            "rebuild_id": self.current_progress.rebuild_id,
            "status": self.current_progress.status.value,
            "total_files": self.current_progress.total_files,
            "processed_files": self.current_progress.processed_files,
            "failed_files": self.current_progress.failed_files,
            "progress_percent": self.current_progress.progress_percent,
            "current_file": self.current_progress.current_file,
            "start_time": self.current_progress.start_time.isoformat(),
            "error_message": self.current_progress.error_message
        }
```

**文件位置**: `backend/app/services/index_rebuild_service.py`

---

### 4.2 后端索引重建API（独立端点，方案B）

| 任务 | 预计时间 | 优先级 | 状态 | 依赖 |
|------|----------|--------|------|------|
| 实现开始重建接口 | 0.5小时 | P0 | ⬜ | 4.1 |
| 实现状态查询接口 | 0.5小时 | P0 | ⬜ | 4.1 |
| 实现取消重建接口 | 1小时 | P0 | ⬜ | 4.1 |
| 扩展配置保存接口返回need_rebuild | 0.5小时 | P0 | ⬜ | 4.1 |
| 实现系统配置更新 | 0.5小时 | P0 | ⬜ | 4.1 |
| **小计** | **3小时** | | | |

**API端点（独立于索引任务系统）**：

```python
# backend/app/api/index.py（扩展现有）

# ===== 现有索引任务接口（保持不变）=====
@router.post("/create")
async def create_index(folder_path: str, ...):
    """创建新索引（写入数据库）"""
    # 保持现有逻辑不变，不修改
    ...

@router.get("/status/{index_id}")
async def get_index_status(index_id: int):
    """查询索引任务状态（从数据库）"""
    # 保持现有逻辑不变，不修改
    ...

@router.get("/list")
async def list_index_tasks(...):
    """查询索引任务列表（从数据库）"""
    # 保持现有逻辑不变，不修改
    ...


# ===== 新增：索引重建接口（独立端点，内存状态）=====
from app.services.index_rebuild_service import IndexRebuildService

rebuild_service = IndexRebuildService()

@router.post("/rebuild/start")
async def start_rebuild(request: RebuildRequest):
    """开始索引重建（内存状态，不写数据库）"""
    try:
        result = await rebuild_service.start_rebuild(
            new_model_config=request.model_config,
            force=request.force
        )
        return {"success": True, "data": result}
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.get("/rebuild/status")
async def get_rebuild_status():
    """查询重建状态（内存状态）"""
    status = rebuild_service.get_status()
    return {"success": True, "data": status}

@router.post("/rebuild/cancel")
async def cancel_rebuild():
    """取消重建（内存状态，自动回滚）"""
    try:
        result = await rebuild_service.cancel()
        return {"success": True, "message": "已取消", "data": result}
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

**接口隔离说明**：

| 功能 | 索引任务系统 | 索引重建系统 | 隔离方式 |
|------|-------------|-------------|---------|
| 开始任务 | `POST /api/index/create` | `POST /api/index/rebuild/start` | 不同路径 |
| 查询状态 | `GET /api/index/status/{id}` | `GET /api/index/rebuild/status` | 不同路径 |
| 取消任务 | `DELETE /api/index/{id}` | `POST /api/index/rebuild/cancel` | 不同路径 |
| 任务列表 | `GET /api/index/list` | - | 重建无列表 |
| 数据来源 | 扫描文件夹 | 当前索引元数据 | 不同来源 |
| 状态存储 | 数据库表 | 内存（不持久化） | 不同存储 |

**文件位置**: `backend/app/api/index.py`（扩展现有文件）

**核心设计原则**：
- **不修改**现有的索引任务接口
- **不污染**数据库（不创建任务记录）
- **独立端点**：`/api/index/rebuild/*`
- **内存状态**：重启后自动清除

**前端调用示例**：

```typescript
// ===== 索引任务系统（保持不变）=====
// 创建新索引
const createIndex = async (folderPath: string) => {
  const response = await api.post('/api/index/create', {
    folder_path: folderPath,
    file_types: ['pdf', 'txt', 'md'],
    recursive: true
  });
  const result = await response.json();
  // result.data.index_id: 数据库生成的ID
  return result.data.index_id;
};

// 查询索引任务状态
const getIndexStatus = async (indexId: number) => {
  const response = await api.get(`/api/index/status/${indexId}`);
  return await response.json();
};

// 索引任务列表
const listIndexes = async () => {
  const response = await api.get('/api/index/list?status=completed');
  return await response.json();
};


// ===== 索引重建系统（独立端点）=====
// 1. 保存嵌入模型配置
const saveConfig = async (config: AIModelConfig) => {
  const response = await api.put('/api/config/ai-model', config);
  const result = await response.json();

  if (result.data.need_rebuild) {
    // 显示确认对话框
    showRebuildConfirm(result.data.rebuild_info);
  }
};

// 2. 开始重建
const startRebuild = async () => {
  const response = await api.post('/api/index/rebuild/start', {
    model_config: newConfig,
    force: false
  });
  const result = await response.json();
  // result.data.task_id: "rebuild_1711478400"
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
```

---

### 4.3 前端索引重建UI

| 任务 | 预计时间 | 优先级 | 状态 | 依赖 |
|------|----------|--------|------|------|
| 创建重建确认对话框 | 1小时 | P0 | ⬜ | 4.2 |
| 创建重建进度弹窗 | 1.5小时 | P0 | ⬜ | 4.2 |
| 实现进度轮询逻辑 | 1小时 | P0 | ⬜ | 4.2 |
| 实现后台运行通知 | 0.5小时 | P1 | ⬜ | 4.2 |
| **小计** | **4小时** | | | |

**Vue组件**（与原型设计章节10.4一致，此处略）

**文件位置**:
- `frontend/src/views/Config.vue`（重建确认和进度）
- `frontend/src/components/IndexRebuildProgress.vue`（独立进度组件）

---

### 4.4 i18n翻译更新

| 任务 | 预计时间 | 优先级 | 状态 | 依赖 |
|------|----------|--------|------|------|
| 添加索引重建翻译键 | 0.5小时 | P0 | ⬜ | 4.3 |
| 翻译成英文 | 0.5小时 | P1 | ⬜ | 4.3 |
| **小计** | **1小时** | | | |

**新增翻译键**（约 20 个）：

```yaml
indexRebuild:
  title: 正在重建索引
  confirmTitle: 切换嵌入模型
  required: 切换后需要重建索引
  switchingTo: 即将切换到
  estimatedTime: 预计耗时
  cloudCostWarning: ⚠️ 云端API调用将产生费用
  unavailableWarning: ⚠️ 重建期间搜索功能暂时不可用
  confirm: 确认并重建
  processed: 已处理
  failed: 失败
  remainingTime: 预计剩余时间
  currentFile: 当前文件
  warning: 重建期间请勿关闭应用
  runInBackground: 后台运行
  completed: 索引重建完成
  failed: 索引重建失败
  cancelled: 已取消重建
  runningInBackground: 索引正在后台重建
  cancelFailed: 取消失败
  rollback: 已恢复到原模型配置
  startFailed: 启动重建失败
  lessThanMinute: 少于1分钟
```

**文件位置**: `frontend/src/locales/zh-CN.ts`、`frontend/src/locales/en-US.ts`

---

### 4.5 集成与测试

| 任务 | 预计时间 | 优先级 | 状态 | 依赖 |
|------|----------|--------|------|------|
| 集成重建服务到配置保存流程 | 1小时 | P0 | ⬜ | 4.1、4.2、4.3 |
| 测试完整重建流程 | 1.5小时 | P0 | ⬜ | 4.1、4.2、4.3 |
| 测试取消和回滚 | 1小时 | P0 | ⬜ | 4.1、4.2、4.3 |
| 测试进度跟踪和通知 | 0.5小时 | P1 | ⬜ | 4.1、4.2、4.3 |
| **小计** | **4小时** | | | |

**测试场景**：
- [ ] 切换本地→云端，弹出确认对话框
- [ ] 确认后开始重建，显示进度弹窗
- [ ] 进度正确更新（百分比、文件数、剩余时间）
- [ ] 点击后台运行，弹窗关闭，后台继续重建
- [ ] 重建完成，显示通知，搜索功能可用
- [ ] 重建中途取消，成功回滚到原模型
- [ ] 重建失败，自动回滚并显示错误
- [ ] 刷新页面，重建状态保持

---

## 五、测试与验证（0.5-1天）

### 4.1 功能测试

| 任务 | 预计时间 | 优先级 | 状态 | 依赖 |
|------|----------|--------|------|------|
| 测试本地嵌入模型配置 | 0.5小时 | P0 | ⬜ | 一、二 |
| 测试云端嵌入模型配置 | 1小时 | P0 | ⬜ | 一、二 |
| 测试本地/云端模型切换 | 1小时 | P0 | ⬜ | 一、二 |
| 测试向量维度归一化 | 1.5小时 | P0 | ⬜ | 一、二 |
| 测试批处理嵌入 | 1小时 | P0 | ⬜ | 一、二 |
| 测试错误重试机制 | 1小时 | P0 | ⬜ | 一、二 |
| 测试 API 密钥加密存储 | 0.5小时 | P0 | ⬜ | 一、二 |
| 测试日志脱敏 | 0.5小时 | P1 | ⬜ | 一、二 |
| **小计** | **7小时** | | | |

**测试场景**：
- [ ] 配置云端嵌入模型（API Key、端点、模型、超时、批处理）
- [ ] 测试连接成功
- [ ] 测试连接失败（错误的 API Key）
- [ ] 保存配置成功
- [ ] 从本地切换到云端
- [ ] 从云端切换回本地
- [ ] 使用云端嵌入进行搜索
- [ ] 批量文本嵌入（100 条）
- [ ] API 调用失败自动重试 3 次
- [ ] API 密钥在数据库中加密存储
- [ ] 日志中 API 密钥被脱敏

**文件位置**: 手动测试 + 自动化测试

---

### 4.2 集成测试

| 任务 | 预计时间 | 优先级 | 状态 | 依赖 |
|------|----------|--------|------|------|
| 编写端到端测试用例 | 1.5小时 | P0 | ⬜ | 一、二 |
| 测试与搜索服务集成 | 1.5小时 | P0 | ⬜ | 一、二 |
| 测试与 Faiss 索引集成 | 1小时 | P0 | ⬜ | 一、二 |
| 测试并发场景 | 1小时 | P1 | ⬜ | 一、二 |
| **小计** | **5小时** | | | |

**测试场景**：
- [ ] 端到端：配置 → 测试 → 保存 → 搜索
- [ ] 云端嵌入服务与现有搜索服务集成
- [ ] 多用户并发配置和搜索

---

### 4.3 性能测试

| 任务 | 预计时间 | 优先级 | 状态 | 依赖 |
|------|----------|--------|------|------|
| 测试 API 响应时间 | 1小时 | P1 | ⬜ | 一 |
| 测试批处理吞吐量 | 1小时 | P1 | ⬜ | 一 |
| 测试并发处理能力 | 1小时 | P2 | ⬜ | 一 |
| **小计** | **3小时** | | | |

**性能指标**：
| 指标 | 目标值 | 测试方法 |
|------|--------|----------|
| API 响应时间 | < 2s | 单次嵌入请求 |
| 批处理吞吐量 | > 100 texts/min | 批量嵌入请求 |
| 并发处理能力 | > 10 req/s | 并发嵌入请求 |

---

## 六、文档更新

### 5.1 技术文档

| 任务 | 预计时间 | 优先级 | 状态 | 依赖 |
|------|----------|--------|------|------|
| 更新 API 接口文档 | 1小时 | P0 | ⬜ | 一 |
| 更新数据库设计文档 | 0.5小时 | P1 | ⬜ | 一 |
| 更新代码架构文档 | 0.5小时 | P1 | ⬜ | 一 |
| **小计** | **2小时** | | | |

**验收标准**：
- [ ] API 接口文档反映最新的嵌入模型配置接口
- [ ] 数据库设计文档反映云端嵌入模型配置
- [ ] 代码架构文档反映 OpenAIEmbeddingService 类

---

### 5.2 用户文档

| 任务 | 预计时间 | 优先级 | 状态 | 依赖 |
|------|----------|--------|------|------|
| 更新用户手册 | 1小时 | P0 | ⬜ | 一、二 |
| 更新配置说明 | 0.5小时 | P0 | ⬜ | 一、二 |
| 添加云端嵌入模型配置说明 | 1小时 | P0 | ⬜ | 一、二 |
| **小计** | **2.5小时** | | | |

**验收标准**：
- [ ] 用户手册包含云端嵌入模型配置步骤
- [ ] 配置说明包含各个参数的解释
- [ ] 有常见问题解答（FAQ）

---

## 七、代码审查清单

### 6.1 后端代码审查

| 审查项 | 说明 | 负责人 | 状态 |
|--------|------|--------|------|
| 代码风格 | 符合 PEP 8 规范 | 开发者 | ⬜ |
| 异常处理 | 所有异常都被正确捕获和处理 | 开发者 | ⬜ |
| 日志记录 | 关键操作有日志记录，API 密钥脱敏 | 开发者 | ⬜ |
| 类型注解 | 函数参数和返回值有类型注解 | 开发者 | ⬜ |
| 文档字符串 | 所有类和方法有 docstring | 开发者 | ⬜ |
| 单元测试 | 核心逻辑有单元测试覆盖 | 开发者 | ⬜ |
| 安全性 | API 密钥加密存储，日志脱敏 | 开发者 | ⬜ |

### 6.2 前端代码审查

| 审查项 | 说明 | 负责人 | 状态 |
|--------|------|--------|------|
| 代码风格 | 符合 Vue/TypeScript 规范 | 开发者 | ⬜ |
| 错误处理 | 表单验证完善，错误提示清晰 | 开发者 | ⬜ |
| 国际化 | 所有用户可见文本使用 i18n | 开发者 | ⬜ |
| 样式一致性 | 与大语言模型配置样式一致 | 开发者 | ⬜ |
| 文档注释 | 关键组件和逻辑有注释 | 开发者 | ⬜ |

---

## 八、上线检查清单

### 7.1 上线前检查

- [ ] 所有代码审查通过
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 性能测试通过
- [ ] 文档更新完成
- [ ] 国际化翻译完成
- [ ] 配置默认值正确
- [ ] API 密钥加密存储验证
- [ ] 日志脱敏验证

### 7.2 上线后验证

- [ ] 配置云端嵌入模型成功
- [ ] 测试连接成功
- [ ] 使用云端嵌入搜索成功
- [ ] 从云端切换回本地成功
- [ ] 错误处理正常（API 失败重试）
- [ ] 日志记录正常
- [ ] 性能指标达标

---

## 九、风险与应对

| 风险项 | 风险等级 | 影响 | 应对措施 | 负责人 |
|--------|---------|------|---------|--------|
| API 调用失败 | 中 | 搜索功能中断 | 自动重试 + 降级到本地 | 开发者 |
| 开发延期 | 低 | 交付时间推迟 | 采用敏捷开发 + MVP 优先 | 产品经理 |

---

## 十、成功指标

| 指标类型 | 指标名称 | 目标值 | 测量方式 |
|---------|---------|-------|----------|
| 功能 | 云端嵌入配置成功率 | > 90% | 日志统计 |
| 功能 | API 调用成功率 | > 99% | 监控统计 |
| 性能 | API 响应时间 | < 2s | 监控统计 |
| 质量 | 单元测试覆盖率 | > 80% | 测试报告 |

---

## 十一、任务优先级说明

| 优先级 | 说明 | 任务示例 |
|--------|------|----------|
| P0 | 核心功能，必须完成 | OpenAIEmbeddingService 实现、前端配置界面 |
| P1 | 重要功能，提升体验 | 样式优化、性能测试 |
| P2 | 可选功能，锦上添花 | 并发测试优化 |

---

**文档结束**

> **使用说明**：
> 1. 本任务清单基于技术方案文档，将开发工作分解为具体任务
> 2. 任务时间估算基于熟悉项目的开发者，实际时间可能因人而异
> 3. 优先级：P0（必须有）> P1（应该有）> P2（可以有）
> 4. 每个任务完成后，在"状态"列打勾标记
> 5. 建议按照任务顺序依次完成，避免遗漏
