# 云端嵌入模型 - 全量重建索引实施方案

> **文档类型**：实施方案
> **特性状态**：规划中
> **创建时间**：2026-03-26
> **预计工期**：2 小时
> **参考决策**：[AD-20260326-01](../../../架构决策/AD-20260326-01-云端嵌入模型与索引重建方案.md)

---

## 变更历史

| 版本 | 日期 | 变更内容 |
|-----|------|---------|
| v1.0 | 2026-03-26 | 初始版本 - 简化方案：复用现有索引任务系统 |

---

## 1. 设计概述

### 1.1 设计目标

为用户提供切换嵌入模型后的全量重建索引能力，采用简化实现方案：**复用现有索引任务系统**。

### 1.2 设计原则

- **简化实现**：复用现有的 `run_full_index_task` 和 `IndexJobModel`
- **按任务重建**：为每个历史任务的 folder_path 创建新任务
- **排队执行**：利用 BackgroundTasks 自动排队机制
- **职责分离**：设置页仅做引导，索引管理页负责重建操作

---

## 2. 核心流程

### 2.1 全量重建流程

```
用户点击"全量重建索引"
    ↓
确认对话框
    ↓
POST /api/index/rebuild-all
    ↓
清空 indexes 文件夹（删除所有 .index 和 whoosh 文件）
    ↓
查询历史已完成任务（按 folder_path 去重）
    ↓
为每个 folder_path 创建新的 IndexJob 记录
    ↓
添加到后台任务队列（自动排队执行）
    ↓
返回任务列表
    ↓
前端并行轮询所有任务进度
    ↓
全部完成 → 提示成功
```

### 2.2 数据流

```
清空索引
  ├─ 删除 Faiss 索引文件（*.index）
  ├─ 删除 Whoosh 索引目录
  └─ 重置内存中的索引对象

创建任务
  ├─ 查询：SELECT * FROM index_jobs WHERE status = 'completed'
  ├─ 去重：按 folder_path 分组
  ├─ 创建：INSERT INTO index_jobs (新记录)
  └─ 排队：background_tasks.add_task(run_full_index_task, ...)
```

---

## 3. 后端实现

### 3.1 API 端点

**文件**：`backend/app/api/index.py`

```python
@router.post("/rebuild-all")
async def rebuild_all_indexes(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    locale: str = Depends(get_locale)
):
    """
    全量重建所有索引

    流程：
    1. 清空 indexes 文件夹
    2. 查询所有历史索引任务（按 folder_path 去重）
    3. 为每个 folder_path 创建新的重建任务
    4. 任务排队执行
    """
    logger.info("开始全量重建所有索引")

    try:
        # 1. 清空索引
        index_service = get_file_index_service()
        index_service.clear_index()

        # 2. 查询所有已完成的历史任务（去重 folder_path）
        completed_jobs = db.query(IndexJobModel).filter(
            IndexJobModel.status == get_enum_value(JobStatus.COMPLETED)
        ).all()

        # 去重：每个 folder_path 只取一个（最新的）
        unique_paths = {}
        for job in completed_jobs:
            if job.folder_path not in unique_paths:
                unique_paths[job.folder_path] = job

        folder_paths = list(unique_paths.keys())

        if not folder_paths:
            raise ValidationException(
                i18n.t('index.no_completed_jobs', locale)
            )

        logger.info(f"找到 {len(folder_paths)} 个需要重建的路径")

        # 3. 为每个路径创建新的重建任务
        created_jobs = []
        for folder_path in folder_paths:
            # 创建新任务记录
            index_job = IndexJobModel(
                folder_path=folder_path,
                job_type=JobType.CREATE,
                status=get_enum_value(JobStatus.PENDING)
            )
            db.add(index_job)
            db.commit()
            db.refresh(index_job)

            created_jobs.append(index_job)

            # 4. 添加到后台任务队列（自动排队）
            background_tasks.add_task(
                run_full_index_task,
                index_job.id,
                folder_path,
                recursive=True,
                file_types=None
            )

            logger.info(f"重建任务已创建: id={index_job.id}, path={folder_path}")

        return {
            "success": True,
            "data": [IndexJobInfo(**job.to_dict()) for job in created_jobs],
            "message": i18n.t('index.rebuild_all_started', locale, count=len(created_jobs))
        }

    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"全量重建失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=i18n.t('index.rebuild_all_failed', locale) + f": {str(e)}"
        )
```

### 3.2 清空索引方法

**文件**：`backend/app/services/file_index_service.py`

在 `FileIndexService` 类中添加方法：

```python
def clear_index(self):
    """
    清空 indexes 文件夹下的所有索引数据

    删除所有 Faiss 索引文件和 Whoosh 索引目录
    重置内存中的索引对象
    """
    import os
    import shutil
    import glob

    logger.info("开始清空 indexes 文件夹")

    # 1. 删除所有 Faiss 索引文件
    faiss_dir = os.path.dirname(self.faiss_index_path)
    if os.path.exists(faiss_dir):
        faiss_files = glob.glob(os.path.join(faiss_dir, "*.index"))
        for faiss_file in faiss_files:
            try:
                os.remove(faiss_file)
                logger.info(f"已删除: {faiss_file}")
            except Exception as e:
                logger.warning(f"删除失败: {faiss_file}, {e}")

    # 2. 删除 Whoosh 索引目录
    if os.path.exists(self.whoosh_index_path):
        try:
            shutil.rmtree(self.whoosh_index_path)
            logger.info(f"已删除 Whoosh 索引: {self.whoosh_index_path}")
        except Exception as e:
            logger.warning(f"删除 Whoosh 失败: {e}")

    # 3. 重置内存中的索引对象
    self._faiss_index = None
    self._whoosh_index = None

    logger.info("indexes 文件夹清空完成")
```

---

## 4. 前端实现

### 4.1 索引管理页面

**文件**：`frontend/src/renderer/src/views/IndexManagement.vue`

```vue
<template>
  <a-card title="索引管理">
    <!-- 统计信息 -->
    <a-row :gutter="16" style="margin-bottom: 16px;">
      <a-col :span="8">
        <a-statistic title="索引文件" :value="status.indexed_files || 0" />
      </a-col>
      <a-col :span="8">
        <a-statistic title="索引任务" :value="status.total_jobs || 0" />
      </a-col>
    </a-row>

    <!-- 操作按钮 -->
    <a-space style="margin-bottom: 16px;">
      <a-button @click="handleAddFiles">
        <PlusOutlined />
        添加文件
      </a-button>

      <a-button @click="handleUpdateIndex">
        <SyncOutlined />
        更新索引
      </a-button>

      <!-- 全量重建索引按钮 -->
      <a-button
        type="primary"
        danger
        @click="handleRebuildAll"
        :loading="isRebuilding"
      >
        <RebuildOutlined />
        {{ t('index.rebuildAll') }}
      </a-button>
    </a-space>

    <!-- 重建进度列表 -->
    <a-card
      v-if="rebuildJobs.length > 0"
      :title="t('index.rebuildProgress')"
      size="small"
    >
      <a-list
        :data-source="rebuildJobs"
        size="small"
      >
        <template #renderItem="{ item }">
          <a-list-item>
            <template #actions>
              <a-tag :color="getStatusColor(item.status)">
                {{ getStatusText(item.status) }}
              </a-tag>
            </template>
            <a-list-item-meta>
              <template #title>
                <a-typography-text ellipsis :content="item.folder_path" style="max-width: 500px;" />
              </template>
              <template #description>
                <a-space>
                  <span>{{ t('index.processed') }}: {{ item.processed_files }} / {{ item.total_files }}</span>
                  <a-progress
                    :percent="item.progress"
                    size="small"
                    :status="getProgressStatus(item.status)"
                    style="width: 150px;"
                  />
                </a-space>
              </template>
            </a-list-item-meta>
          </a-list-item>
        </template>
      </a-list>
    </a-card>
  </a-card>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Modal, message } from 'ant-design-vue'
import { RebuildOutlined, PlusOutlined, SyncOutlined } from '@ant-design/icons-vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const isRebuilding = ref(false)
const rebuildJobs = ref([])
const status = ref({})

let pollTimer = null

// 全量重建
const handleRebuildAll = () => {
  Modal.confirm({
    title: t('index.rebuildAllConfirm'),
    content: t('index.rebuildAllWarning'),
    okText: t('common.confirm'),
    cancelText: t('common.cancel'),
    okButtonProps: { danger: true },
    onOk: async () => {
      isRebuilding.value = true
      try {
        const response = await fetch('/api/index/rebuild-all', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
        const result = await response.json()

        if (result.success) {
          message.success(t('index.rebuildAllStarted', { count: result.data.length }))
          rebuildJobs.value = result.data

          // 开始轮询所有任务的进度
          startPolling()
        }
      } catch (error) {
        message.error(t('index.rebuildAllFailed'))
      } finally {
        isRebuilding.value = false
      }
    }
  })
}

// 轮询所有重建任务的进度
const startPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
  }

  pollTimer = setInterval(async () => {
    try {
      // 并行查询所有任务状态
      const promises = rebuildJobs.value.map(job =>
        fetch(`/api/index/status/${job.index_id}`)
          .then(res => res.json())
      )

      const results = await Promise.all(promises)

      rebuildJobs.value = results.map(r => r.data)

      // 检查是否全部完成
      const allCompleted = rebuildJobs.value.every(
        job => job.status === 'completed' || job.status === 'failed'
      )

      if (allCompleted) {
        clearInterval(pollTimer)
        pollTimer = null

        const completed = rebuildJobs.value.filter(
          j => j.status === 'completed'
        ).length
        const failed = rebuildJobs.value.filter(
          j => j.status === 'failed'
        ).length

        if (failed > 0) {
          message.warning(t('index.rebuildAllPartial', { completed, failed }))
        } else {
          message.success(t('index.rebuildAllComplete', { count: completed }))
        }

        // 刷新状态
        await fetchStatus()
      }
    } catch (error) {
      console.error('轮询失败:', error)
    }
  }, 2000)
}

// 获取状态
const fetchStatus = async () => {
  try {
    const response = await fetch('/api/index/status')
    const result = await response.json()
    if (result.success) {
      status.value = result.data
    }
  } catch (error) {
    console.error('获取状态失败:', error)
  }
}

const getStatusColor = (status: string) => {
  const colors = {
    pending: 'default',
    processing: 'processing',
    completed: 'success',
    failed: 'error'
  }
  return colors[status] || 'default'
}

const getStatusText = (status: string) => {
  return t(`index.jobStatus.${status}`)
}

const getProgressStatus = (status: string) => {
  const statusMap = {
    processing: 'active',
    completed: 'success',
    failed: 'exception'
  }
  return statusMap[status] || null
}

onMounted(() => {
  fetchStatus()
})

onUnmounted(() => {
  if (pollTimer) {
    clearInterval(pollTimer)
  }
})
</script>
```

### 4.2 设置页面引导

**文件**：`frontend/src/renderer/src/views/Settings.vue`

```vue
<!-- 切换模型后的引导提示 -->
<a-alert
  v-if="showModelChangeWarning"
  type="warning"
  show-icon
  closable
  @close="showModelChangeWarning = false"
  style="margin-bottom: 16px;"
>
  <template #message>
    {{ t('settingsEmbedding.modelChanged') }}
  </template>
  <template #description>
    <p>{{ t('settingsEmbedding.rebuildTip') }}</p>
    <a-space>
      <a-button type="primary" size="small" @click="restartApp">
        <ReloadOutlined />
        {{ t('common.restartApp') }}
      </a-button>
      <a-button size="small" @click="goToIndexManagement">
        <FolderOpenOutlined />
        {{ t('settingsEmbedding.goToIndex') }}
      </a-button>
    </a-space>
  </template>
</a-alert>

<script setup lang="ts">
const showModelChangeWarning = ref(false)

// 保存配置后检测模型变化
const handleSaveConfig = async () => {
  // ... 保存逻辑 ...

  const response = await updateAIModelConfig(config)

  if (response.requires_rebuild) {
    showModelChangeWarning.value = true
  }
}

const restartApp = () => {
  window.location.reload()
}

const goToIndexManagement = () => {
  router.push('/index-management')
}
</script>
```

---

## 5. 国际化

### 5.1 后端翻译

**文件**：`backend/app/locales/zh_CN.json`

```json
{
  "index": {
    "rebuild_all_started": "已启动 {count} 个重建任务",
    "rebuild_all_failed": "全量重建失败",
    "rebuild_all_partial": "重建完成：成功 {completed} 个，失败 {failed} 个",
    "rebuild_all_complete": "全量重建完成！成功完成 {count} 个任务",
    "no_completed_jobs": "未找到已完成的历史索引任务，无法重建",
    "rebuild_all_warning": "将清空所有索引并按历史任务逐一重建，预计耗时较长，是否继续？"
  }
}
```

**文件**：`backend/app/locales/en_US.json`

```json
{
  "index": {
    "rebuild_all_started": "Started {count} rebuild tasks",
    "rebuild_all_failed": "Full rebuild failed",
    "rebuild_all_partial": "Rebuild completed: {completed} succeeded, {failed} failed",
    "rebuild_all_complete": "Full rebuild completed! {count} tasks succeeded",
    "no_completed_jobs": "No completed index jobs found, cannot rebuild",
    "rebuild_all_warning": "This will clear all indexes and rebuild by historical tasks, taking a long time, continue?"
  }
}
```

### 5.2 前端翻译

**文件**：`frontend/src/renderer/src/locales/zh-CN.ts`

```typescript
index: {
  rebuildAll: '全量重建索引',
  rebuildAllConfirm: '确认全量重建',
  rebuildAllWarning: '将清空所有索引并按历史任务逐一重建，预计耗时较长',
  rebuildAllStarted: '已启动 {count} 个重建任务',
  rebuildAllComplete: '全量重建完成！成功完成 {count} 个任务',
  rebuildAllPartial: '重建完成：成功 {completed} 个，失败 {failed} 个',
  rebuildProgress: '重建进度',
  processed: '已处理',

  jobStatus: {
    pending: '等待中',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
}
```

**文件**：`frontend/src/renderer/src/locales/en-US.ts`

```typescript
index: {
  rebuildAll: 'Rebuild All Indexes',
  rebuildAllConfirm: 'Confirm Full Rebuild',
  rebuildAllWarning: 'This will clear all indexes and rebuild by historical tasks, taking a long time',
  rebuildAllStarted: 'Started {count} rebuild tasks',
  rebuildAllComplete: 'Full rebuild completed! {count} tasks succeeded',
  rebuildAllPartial: 'Rebuild completed: {completed} succeeded, {failed} failed',
  rebuildProgress: 'Rebuild Progress',
  processed: 'Processed',

  jobStatus: {
    pending: 'Pending',
    processing: 'Processing',
    completed: 'Completed',
    failed: 'Failed'
  }
}
```

---

## 6. 用户流程

### 6.1 切换模型流程

```
用户在设置页切换嵌入模型
    ↓
保存配置
    ↓
显示引导提示
┌─────────────────────────────────────────┐
│ ⚠️ 嵌入模型已更改                       │
│                                         │
│ 建议重启应用后在索引管理中重建索引        │
│                                         │
│ [重启应用] [前往索引管理]               │
└─────────────────────────────────────────┘
    ↓
用户选择"前往索引管理"
    ↓
跳转到索引管理页面
```

### 6.2 重建索引流程

```
用户在索引管理页点击"全量重建索引"
    ↓
确认对话框
┌─────────────────────────────────────────┐
│ 确认全量重建                             │
│                                         │
│ 将清空所有索引并按历史任务逐一重建      │
│ 预计耗时较长，是否继续？                 │
│                                         │
│                    [取消] [确认]        │
└─────────────────────────────────────────┘
    ↓
用户确认
    ↓
清空索引 + 创建重建任务
    ↓
显示重建进度列表
┌─────────────────────────────────────────┐
│ 重建进度                                │
│                                         │
│ D:\Documents                     [处理中]│
│ ████████████░░░░░░░░░░░░░░░  60%               │
│ 已处理: 600 / 1000                      │
│                                         │
│ E:\Projects                      [等待中]│
│ ░░░░░░░░░░░░░░░░░░░░░░░░  0%                │
│                                         │
│ C:\Work                         [等待中]│
│ ░░░░░░░░░░░░░░░░░░░░░░░░  0%                │
└─────────────────────────────────────────┘
    ↓
全部完成
    ↓
显示成功提示
┌─────────────────────────────────────────┐
│ ✅ 全量重建完成！                        │
│ 成功完成 3 个任务                       │
│                                         │
│                    [确定]              │
└─────────────────────────────────────────┘
```

---

## 7. 技术要点

### 7.1 方案对比

| 对比项 | 原方案（独立重建服务） | 简化方案（复用现有系统） |
|--------|------------------------|------------------------|
| 代码量 | ~500 行 | ~150 行 |
| 数据表 | 不需要 | 复用 IndexJobModel |
| 进度查询 | 新端点 | 复用 `/api/index/status/{id}` |
| 任务排队 | 需要实现 | 已有！系统自动排队 |
| 错误处理 | 需要实现 | 已有！ |
| 实施时间 | 7 小时 | 2 小时 |

### 7.2 关键设计决策

#### 决策 1：创建新任务记录（方案 A）

**决策**：为每个 folder_path 创建新的 IndexJob 记录

**理由**：
- 新旧任务独立，互不干扰
- 保留历史记录完整性
- 避免处理复杂的重置逻辑
- 可以同时查看历史统计和重建进度

#### 决策 2：按任务重建

**决策**：按历史任务的 folder_path 重建，而不是按文件

**理由**：
- 符合用户使用习惯（一个任务对应一个文件夹）
- 减少任务数量，提升效率
- 复用现有的 `run_full_index_task`，无需修改

#### 决策 3：职责分离

**决策**：设置页仅做引导，索引管理页负责重建操作

**理由**：
- 职责分离清晰
- 用户心智模型更自然
- 索引相关操作集中在一处

---

## 8. 实施步骤

### 步骤 1：后端清空索引方法（30 分钟）

**文件**：`backend/app/services/file_index_service.py`

在 `FileIndexService` 类中添加 `clear_index()` 方法

### 步骤 2：后端重建 API 端点（30 分钟）

**文件**：`backend/app/api/index.py`

添加 `POST /api/index/rebuild-all` 端点

### 步骤 3：后端国际化（15 分钟）

**文件**：`backend/app/locales/zh_CN.json` 和 `en_US.json`

添加重建相关翻译键

### 步骤 4：前端重建按钮和进度（45 分钟）

**文件**：`frontend/src/renderer/src/views/IndexManagement.vue`

添加重建按钮和进度列表

### 步骤 5：设置页面引导（15 分钟）

**文件**：`frontend/src/renderer/src/views/Settings.vue`

添加模型切换后的引导提示

### 步骤 6：前端国际化（15 分钟）

**文件**：`frontend/src/renderer/src/locales/zh-CN.ts` 和 `en-US.ts`

添加重建相关翻译键

### 步骤 7：测试验证（30 分钟）

- 切换模型 → 检查引导提示
- 点击重建 → 检查确认对话框
- 确认重建 → 检查任务创建
- 轮询进度 → 检查进度显示
- 全部完成 → 检查成功提示

---

## 9. 验收标准

### 功能验收

- [ ] 设置页切换模型后显示引导提示
- [ ] 索引管理页显示"全量重建索引"按钮
- [ ] 点击按钮显示确认对话框
- [ ] 确认后清空索引文件
- [ ] 为每个历史任务创建新任务
- [ ] 任务排队执行（不并行）
- [ ] 前端显示所有任务的进度
- [ ] 全部完成后显示成功提示
- [ ] 部分失败时显示统计信息

### 性能验收

- [ ] 清空索引时间 < 5 秒
- [ ] 任务创建时间 < 2 秒
- [ ] 轮询间隔 2 秒
- [ ] 不影响现有索引功能

---

## 10. 相关文档

- [云端嵌入模型 PRD](./embedding-openai-01-prd.md)
- [云端嵌入模型原型](./embedding-openai-02-原型.md)
- [云端嵌入模型技术方案](./embedding-openai-03-技术方案.md)
- [架构决策 AD-20260326-01](../../../架构决策/AD-20260326-01-云端嵌入模型与索引重建方案.md)
- [实施步骤文档](./embedding-openai-06-实施步骤.md)

---

**文档版本**：v1.0
**创建时间**：2026-03-26
**预计工期**：2 小时
**维护者**：AI助手
