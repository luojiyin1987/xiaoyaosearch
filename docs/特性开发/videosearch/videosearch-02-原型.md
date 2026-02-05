# 视频画面搜索 - 原型设计

> **文档类型**：原型设计文档
> **基础版本**：基于 [视频画面搜索PRD](./videosearch-01-prd.md)
> **设计状态**：设计中
> **创建时间**：2026-02-05
> **最后更新**：2026-02-05

---

## 1. 设计概述

### 1.1 设计原则
- **复用现有设计**：基于现有图片搜索结果卡片样式，保持界面一致性
- **清晰区分**：视频画面匹配与图片匹配通过图标和标签清晰区分
- **信息完整**：展示关键帧缩略图、时间戳、相似度等关键信息
- **简洁高效**：不增加额外的配置界面，配置通过后端文件管理

### 1.2 设计范围
| 模块 | 设计内容 | 优先级 |
|------|---------|-------|
| 搜索结果展示 | 视频画面匹配卡片 | P0 |
| 搜索输入 | 复用现有图片输入界面 | - |
| 搜索选项 | 复用现有搜索选项 | - |
| 配置界面 | 无（后端配置文件） | - |

---

## 2. 用户界面设计

### 2.1 搜索结果卡片设计

#### 视频画面匹配卡片

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ┌─────┐                                                                      │
│ │图标 │  tutorial.mp4                                              相似度 88% │
│ └─────┘  D:\videos\course\tutorial.mp4                                    │
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────┐    │
│ │                                                                     │    │
│ │                    [关键帧缩略图]                                    │    │
│ │                                                                     │    │
│ │                        1280 x 720                                    │    │
│ └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│ 📍 时间戳: 00:02:30  │  📅 2026-01-15  │  💾 256 MB  │  🏷️ 画面匹配        │
│                                                                             │
│ [打开文件]  [复制路径]  [跳转到位置]                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 设计说明

**卡片头部**：
- **文件图标**：视频图标（`VideoCameraOutlined`），红色渐变背景（与现有视频文件类型一致）
- **文件名**：视频文件名称，可点击打开
- **文件路径**：完整文件路径，悬停显示完整路径
- **相似度分数**：圆形进度条显示，绿色（≥90%）、蓝色（≥70%）、黄色（≥50%）、红色（<50%）

**关键帧预览**：
- **缩略图**：匹配的关键帧画面，最大宽度400px，自动居中
- **分辨率标注**：关键帧分辨率信息
- **边框高亮**：相似度越高，边框颜色越明显

**元数据信息**：
- **时间戳**：匹配位置的时间戳（格式：HH:MM:SS）
- **修改日期**：视频文件修改时间
- **文件大小**：视频文件大小
- **匹配类型**：画面匹配（区别于语义匹配、全文匹配等）

**操作按钮**：
- **打开文件**：使用系统默认播放器打开视频
- **复制路径**：复制视频文件路径到剪贴板
- **跳转到位置**：在播放器中跳转到匹配时间戳位置（可选功能，后续迭代）

### 2.2 混合搜索结果展示

当图片搜索同时返回图片匹配和视频画面匹配时，结果按相似度排序混合展示：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 搜索结果                                     共 45 个结果  ·  耗时 0.23秒    │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────┐                                                                      │
│ │📷图片│  screenshot_001.png                                    相似度 92% │
│ └─────┘  D:\images\screenshots\screenshot_001.png                             │
│ ┌─────────────────────────────────────────────────────────────────────┐    │
│ │                    [图片预览]                                        │    │
│ └─────────────────────────────────────────────────────────────────────┘    │
│ 📅 2026-01-10  │  💾 2.1 MB  │  🏷️ 语义匹配                               │
│                                                                             │
│ [打开文件]  [复制路径]                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────┐                                                                      │
│ │🎬视频│  tutorial.mp4                                        相似度 88% │
│ └─────┘  D:\videos\course\tutorial.mp4                                    │
│ ┌─────────────────────────────────────────────────────────────────────┐    │
│ │                    [关键帧缩略图]                                    │    │
│ └─────────────────────────────────────────────────────────────────────┘    │
│ 📍 时间戳: 00:02:30  │  📅 2026-01-15  │  💾 256 MB  │  🏷️ 画面匹配        │
│                                                                             │
│ [打开文件]  [复制路径]  [跳转到位置]                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────┐                                                                      │
│ │📷图片│  reference_image.jpg                                   相似度 85% │
│ └─────┘  D:\references\reference_image.jpg                                   │
│ ┌─────────────────────────────────────────────────────────────────────┐    │
│ │                    [图片预览]                                        │    │
│ └─────────────────────────────────────────────────────────────────────┘    │
│ 📅 2026-01-08  │  💾 1.8 MB  │  🏷️ 画面匹配                               │
│                                                                             │
│ [打开文件]  [复制路径]                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 交互设计

### 3.1 图片搜索流程（复用现有）

```
用户操作流程：
1. 用户点击图片输入图标（PictureOutlined）
2. 切换到图片输入模式
3. 用户拖拽或点击上传图片
4. 显示图片预览
5. 点击"开始分析"按钮
6. 执行多模态搜索（包含图片和视频画面匹配）
7. 展示搜索结果（混合图片和视频画面匹配）
```

### 3.2 视频画面匹配结果交互

**点击文件名**：
- 使用系统默认播放器打开视频文件

**点击关键帧缩略图**：
- 放大显示关键帧（模态框）
- 显示完整关键帧信息和时间戳

**点击"跳转到位置"按钮**（可选功能）：
- 调用系统播放器并跳转到指定时间戳
- 需要播放器支持命令行参数（如 VLC、MPC-HC）

**点击"复制路径"按钮**：
- 复制视频文件路径到剪贴板
- 显示成功提示

### 3.3 空状态提示

当视频画面搜索功能未启用时，图片搜索结果中不显示视频匹配，并在结果底部显示提示：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 💡 提示                                                                     │
│ 当前仅搜索图片文件。如需搜索视频画面，请联系管理员启用视频画面搜索功能。          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. 组件设计

### 4.1 VideoFrameResultCard 组件

**组件路径**：`frontend/src/renderer/src/components/VideoFrameResultCard.vue`

**Props 接口**：
```typescript
interface VideoFrameResult {
  file_id: number
  file_name: string
  file_path: string
  timestamp: number          // 时间戳（秒）
  similarity: number         // 相似度分数（0-1）
  frame_preview?: string     // 关键帧预览图URL（可选）
  frame_width: number        // 关键帧宽度
  frame_height: number       // 关键帧高度
  file_size: number          // 文件大小（字节）
  modified_at: string        // 修改时间
  match_type: 'frame'        // 匹配类型
}

interface Props {
  result: VideoFrameResult
}
```

**Events 接口**：
```typescript
interface Emits {
  open: [result: VideoFrameResult]      // 打开文件
  copy: [path: string]                  // 复制路径
  jump: [filePath: string, timestamp: number]  // 跳转到位置
}
```

### 4.2 组件结构

```vue
<template>
  <div class="video-frame-result-card">
    <!-- 卡片头部 -->
    <div class="card-header">
      <div class="file-info">
        <div class="file-icon file-type-video">
          <VideoCameraOutlined />
        </div>
        <div class="file-details">
          <h4 class="file-name">{{ result.file_name }}</h4>
          <div class="file-path">{{ result.file_path }}</div>
        </div>
      </div>
      <div class="relevance-score">
        <a-progress
          type="circle"
          :percent="Math.round(result.similarity * 100)"
          :stroke-color="getScoreColor(result.similarity)"
        />
      </div>
    </div>

    <!-- 关键帧预览 -->
    <div class="card-content">
      <div class="frame-preview">
        <img
          :src="result.frame_preview"
          :alt="`关键帧 ${formatTimestamp(result.timestamp)}`"
          @click="showFullscreen"
        />
        <div class="frame-info">
          {{ result.frame_width }} x {{ result.frame_height }}
        </div>
      </div>
    </div>

    <!-- 元数据 -->
    <div class="file-metadata">
      <div class="metadata-row">
        <span class="metadata-item">
          <ClockCircleOutlined />
          {{ t('searchResult.timestamp') }}: {{ formatTimestamp(result.timestamp) }}
        </span>
        <span class="metadata-item">
          <CalendarOutlined />
          {{ formatDate(result.modified_at) }}
        </span>
        <span class="metadata-item">
          <HddOutlined />
          {{ formatFileSize(result.file_size) }}
        </span>
        <span class="metadata-item">
          <TagOutlined />
          {{ t('searchResult.frameMatch') }}
        </span>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="card-actions">
      <a-button type="text" size="small" @click="$emit('open', result)">
        <FolderOpenOutlined />
        {{ t('searchResult.open') }}
      </a-button>
      <a-button type="text" size="small" @click="$emit('copy', result.file_path)">
        <CopyOutlined />
        {{ t('searchResult.copyPath') }}
      </a-button>
      <a-button
        type="text"
        size="small"
        @click="$emit('jump', result.file_path, result.timestamp)"
        :disabled="!canJumpTo"
      >
        <PlayCircleOutlined />
        {{ t('searchResult.jumpTo') }}
      </a-button>
    </div>
  </div>
</template>
```

### 4.3 样式设计

**关键帧预览样式**：
```css
.frame-preview {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--surface-02);
  border-radius: var(--radius-lg);
  overflow: hidden;
  margin-bottom: var(--space-4);
  cursor: pointer;
  transition: all var(--transition-base);
}

.frame-preview:hover {
  transform: scale(1.02);
  box-shadow: var(--shadow-md);
}

.frame-preview img {
  max-width: 100%;
  max-height: 300px;
  object-fit: contain;
}

.frame-info {
  position: absolute;
  bottom: var(--space-2);
  right: var(--space-2);
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-base);
  font-size: 0.75rem;
}
```

**相似度边框高亮**：
```css
.video-frame-result-card {
  border: 2px solid transparent;
  transition: border-color var(--transition-base);
}

.video-frame-result-card.high-similarity {
  border-color: rgba(82, 196, 26, 0.3);
}

.video-frame-result-card.medium-similarity {
  border-color: rgba(24, 144, 255, 0.3);
}

.video-frame-result-card.low-similarity {
  border-color: rgba(250, 173, 20, 0.3);
}
```

---

## 5. 响应式设计

### 5.1 桌面端（>768px）

- 关键帧预览最大高度：300px
- 卡片内边距：24px
- 元信息横向排列

### 5.2 移动端（≤768px）

- 关键帧预览最大高度：200px
- 卡片内边距：16px
- 元信息换行显示
- 操作按钮垂直排列

---

## 6. 国际化设计

### 6.1 新增翻译键

```yaml
# zh-CN
searchResult:
  frameMatch: 画面匹配
  timestamp: 时间戳
  jumpTo: 跳转到位置
  jumpToNotSupported: 播放器不支持跳转

# en-US
searchResult:
  frameMatch: Frame Match
  timestamp: Timestamp
  jumpTo: Jump to
  jumpToNotSupported: Player does not support jumping
```

### 6.2 时间戳格式化

根据用户语言环境自动格式化：
- 中文：`00时02分30秒` 或 `00:02:30`
- 英文：`00:02:30`

---

## 7. 可访问性设计

### 7.1 键盘导航

- `Tab`：在结果卡片间切换焦点
- `Enter`：打开聚焦的文件
- `Space`：放大聚焦的关键帧

### 7.2 屏幕阅读器支持

- 关键帧图片添加 `alt` 属性：`"视频 tutorial.mp4 在 00:02:30 的关键帧"`
- 时间戳使用 `<time>` 标签
- 相似度分数使用 `aria-label` 描述

---

## 8. 技术实现要点

### 8.1 组件复用

- 复用现有 `SearchResultCard` 的样式和布局
- 创建 `VideoFrameResultCard` 组件继承基础样式
- 共享元数据展示和操作按钮逻辑

### 8.2 性能优化

- 关键帧缩略图使用懒加载
- 缩略图缓存到本地存储
- 列表虚拟滚动（结果数量>100时）

### 8.3 错误处理

**关键帧加载失败**：
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ┌─────┐                                                                      │
│ │🎬视频│  tutorial.mp4                                        相似度 88% │
│ └─────┘  D:\videos\course\tutorial.mp4                                    │
│ ┌─────────────────────────────────────────────────────────────────────┐    │
│ │                     ⚠️ 关键帧加载失败                                  │    │
│ └─────────────────────────────────────────────────────────────────────┘    │
│ 📍 时间戳: 00:02:30  │  📅 2026-01-15  │  💾 256 MB  │  🏷️ 画面匹配        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. 后续迭代规划

### 9.1 短期优化（V1.1）
- [ ] 关键帧预览图全屏查看
- [ ] 多个视频画面匹配聚合展示（同一视频的多个时间戳）
- [ ] 相似度阈值滑动条

### 9.2 中期规划（V1.2）
- [ ] 视频片段预览（匹配时间戳前后5秒）
- [ ] 视频内时间轴标记所有匹配位置
- [ ] 批量导出匹配的关键帧

### 9.3 长期愿景（V2.0）
- [ ] AI生成视频摘要
- [ ] 相似场景智能分组
- [ ] 跨视频场景追踪

---

## 10. 相关资源

### 10.1 设计参考
- [现有搜索结果卡片](../../frontend/src/renderer/src/components/SearchResultCard.vue)
- [Ant Design Vue - Card](https://antdv.com/components/card-cn)
- [Ant Design Vue - Progress](https://antdv.com/components/progress-cn)

### 10.2 图标资源
- `VideoCameraOutlined`：视频文件图标
- `ClockCircleOutlined`：时间戳图标
- `PlayCircleOutlined`：跳转播放图标

---

**文档结束**

> **设计说明**：
> 1. 本原型设计专注于视频画面搜索的结果展示部分
> 2. 复用现有图片搜索界面和结果卡片样式，保持一致性
> 3. 配置通过后端 .env 文件管理，无需前端配置界面
> 4. 后续迭代可根据用户反馈逐步完善
