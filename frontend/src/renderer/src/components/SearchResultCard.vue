<template>
  <div class="result-card">
    <!-- 文件头部信息 -->
    <div class="card-header">
      <div class="file-info">
        <!-- 文件图标 -->
        <div class="file-icon" :class="`file-type-${result.file_type}`">
          <FileTextOutlined v-if="result.file_type === 'document'" />
          <AudioOutlined v-else-if="result.file_type === 'audio'" />
          <VideoCameraOutlined v-else-if="result.file_type === 'video'" />
          <PictureOutlined v-else-if="result.file_type === 'image'" />
          <FileOutlined v-else />
        </div>

        <!-- 文件名称和路径 -->
        <div class="file-details">
          <h4 class="file-name" @click="$emit('open', result)">
            {{ result.file_name }}
          </h4>
          <div class="file-path" :title="result.file_path">
            <FolderOutlined />
            {{ displayPath }}
          </div>
        </div>
      </div>

      <!-- 相关性评分 -->
      <div class="relevance-score">
        <a-progress
          type="circle"
          :percent="Math.round(result.relevance_score * 100)"
          :size="60"
          :stroke-color="getScoreColor(result.relevance_score)"
          :width="60"
          class="score-circle"
        >
          <template #format="percent">
            <span class="score-text">{{ percent }}%</span>
          </template>
        </a-progress>
        <div class="score-label">{{ t('searchResult.matchDegree') }}</div>
      </div>
    </div>

    <!-- 文件内容预览 -->
    <div class="card-content">
      <div class="preview-text" v-html="result.highlight"></div>

      <!-- 文件元信息 -->
      <div class="file-metadata">
        <div class="metadata-row">
          <!-- 文件来源类型 -->
          <span class="metadata-item source-type" :class="`source-${result.source_type || 'filesystem'}`">
            <component :is="getSourceIcon(result.source_type)" />
            {{ getSourceTypeLabel(result.source_type) }}
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
            {{ getMatchTypeLabel(result.match_type) }}
          </span>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="card-actions">
      <a-button type="text" size="small" @click="$emit('open', result)">
        <FolderOpenOutlined />
        {{ t('searchResult.open') }}
      </a-button>
      <a-button
        v-if="isValidSourceUrl"
        type="text"
        size="small"
        @click="openSourceUrl"
        class="open-link-btn"
      >
        <LinkOutlined />
        {{ t('searchResult.openLink') }}
      </a-button>
      <a-button type="text" size="small" @click="copyFilePath">
        <CopyOutlined />
        {{ t('searchResult.copyPath') }}
      </a-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { message } from 'ant-design-vue'
import type { SearchResult } from '@/types/api'
import {
  FileTextOutlined,
  AudioOutlined,
  VideoCameraOutlined,
  PictureOutlined,
  FileOutlined,
  FolderOutlined,
  FolderOpenOutlined,
  CopyOutlined,
  CalendarOutlined,
  HddOutlined,
  TagOutlined,
  CloudOutlined,
  DatabaseOutlined,
  LinkOutlined
} from '@ant-design/icons-vue'

const { t } = useI18n()

// Props
interface Props {
  result: SearchResult
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  open: [result: SearchResult]
}>()

// 计算属性
const getScoreColor = (score: number) => {
  if (score >= 0.9) return '#52c41a'
  if (score >= 0.7) return '#1890ff'
  if (score >= 0.5) return '#faad14'
  return '#ff4d4f'
}

const getMatchTypeLabel = (type: string) => {
  const typeMap: Record<string, string> = {
    semantic: t('searchResult.semanticMatch'),
    fulltext: t('searchResult.fulltextMatch'),
    hybrid: t('searchResult.hybridMatch')
  }
  return typeMap[type] || type
}

// 获取来源类型标签
const getSourceTypeLabel = (sourceType: string | null) => {
  const typeMap: Record<string, string> = {
    filesystem: t('searchResult.sourceFilesystem'),
    yuque: t('searchResult.sourceYuque'),
    feishu: t('searchResult.sourceFeishu'),
    notion: t('searchResult.sourceNotion'),
    github: t('searchResult.sourceGithub'),
    confluence: t('searchResult.sourceConfluence'),
    wordpress: t('searchResult.sourceWordpress'),
    obsidian: t('searchResult.sourceObsidian'),
    dropbox: t('searchResult.sourceDropbox'),
    googledrive: t('searchResult.sourceGoogleDrive'),
    onedrive: t('searchResult.sourceOneDrive'),
    figma: t('searchResult.sourceFigma'),
    gitlab: t('searchResult.sourceGitlab')
  }
  // 如果是预定义类型，显示翻译文本；否则显示原始值
  if (sourceType && sourceType in typeMap) {
    return typeMap[sourceType]
  }
  // 如果是null、undefined或未定义类型，显示原始值或默认为filesystem
  return sourceType || 'filesystem'
}

// 获取来源类型图标
const getSourceIcon = (sourceType: string | null) => {
  const iconMap: Record<string, any> = {
    filesystem: DatabaseOutlined,
    yuque: CloudOutlined,
    feishu: CloudOutlined,
    notion: CloudOutlined,
    github: LinkOutlined,
    confluence: CloudOutlined,
    wordpress: FileTextOutlined,
    obsidian: DatabaseOutlined,
    dropbox: CloudOutlined,
    googledrive: CloudOutlined,
    onedrive: CloudOutlined,
    figma: PictureOutlined,
    gitlab: LinkOutlined
  }
  return iconMap[sourceType || 'filesystem'] || DatabaseOutlined
}

const copyFilePath = async () => {
  try {
    await navigator.clipboard.writeText(props.result.file_path)
    message.success(t('searchResult.copySuccess'))
  } catch (error) {
    message.error(t('searchResult.copyFailed'))
  }
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) {
    const hours = Math.floor(diff / (1000 * 60 * 60))
    if (hours === 0) {
      const minutes = Math.floor(diff / (1000 * 60))
      return minutes <= 1 ? t('searchResult.justNow') : t('searchResult.minutesAgo', { minutes })
    }
    return t('searchResult.hoursAgo', { hours })
  } else if (days === 1) {
    return t('searchResult.yesterday')
  } else if (days < 7) {
    return t('searchResult.daysAgo', { days })
  } else {
    return date.toLocaleDateString(t('common.localeCode'))
  }
}

// 缩短路径显示
import { computed } from 'vue'

const displayPath = computed(() => {
  const path = props.result.file_path
  const maxLength = 60 // 最大显示长度

  if (path.length <= maxLength) {
    return path
  }

  // 保留开头和结尾，中间用省略号
  const startLength = 25
  const endLength = 25

  return `${path.substring(0, startLength)}...${path.substring(path.length - endLength)}`
})

// 判断 source_url 是否为有效 URL
const isValidSourceUrl = computed(() => {
  const url = props.result.source_url
  if (!url) return false
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
})

// 打开来源链接
const openSourceUrl = async () => {
  const url = props.result.source_url
  if (!url) return

  try {
    // 使用 shell.openExternal 在默认浏览器中打开 URL
    const api = (window as any).api
    if (api && typeof api.openExternal === 'function') {
      await api.openExternal(url)
      message.success(t('searchResult.linkOpened'))
    } else {
      // 备用方案：使用 window.open
      window.open(url, '_blank')
      message.success(t('searchResult.linkOpened'))
    }
  } catch (error) {
    message.error(t('searchResult.linkOpenFailed'))
    console.error('打开链接失败:', error)
  }
}
</script>

<style scoped>
.result-card {
  background: var(--surface-01);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  box-shadow: var(--shadow-base);
  transition: all var(--transition-base);
  margin-bottom: var(--space-4);
  position: relative;
  overflow: hidden;
}

.result-card:hover {
  border-color: var(--primary-200);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}


.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: var(--space-4);
}

.file-info {
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
  flex: 1;
}

.file-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  font-size: 24px;
  color: white;
  flex-shrink: 0;
}

.file-type-document {
  background: linear-gradient(135deg, #1890ff, #40a9ff);
}

.file-type-audio {
  background: linear-gradient(135deg, #faad14, #ffc53d);
}

.file-type-video {
  background: linear-gradient(135deg, #ff4d4f, #ff7875);
}

.file-type-image {
  background: linear-gradient(135deg, #52c41a, #73d13d);
}

.file-details {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--space-1);
  cursor: pointer;
  transition: color var(--transition-base);
  word-break: break-word;
}

.file-name:hover {
  color: var(--primary-600);
}

.file-path {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: 0.875rem;
  color: var(--text-tertiary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.relevance-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  margin-left: var(--space-4);
}

.score-circle {
  font-weight: 600;
}

.score-text {
  font-size: 0.875rem;
  font-weight: 600;
}

.score-label {
  font-size: 0.75rem;
  color: var(--text-tertiary);
}

.card-content {
  margin-bottom: var(--space-4);
}

.preview-text {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: var(--space-3);
  word-break: break-word;
}

.preview-text :deep(em) {
  background: rgba(245, 158, 11, 0.2);
  color: #d97706;
  padding: 2px 4px;
  border-radius: 4px;
  font-style: normal;
  font-weight: 500;
}

.file-metadata {
  border-top: 1px solid var(--border-light);
  padding-top: var(--space-3);
}

.metadata-row {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  flex-wrap: wrap;
}

.metadata-item {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: 0.75rem;
  color: var(--text-tertiary);
  white-space: nowrap;
}

/* 来源类型样式 - 默认使用filesystem颜色 */
.source-type {
  padding: 2px 8px;
  border-radius: var(--radius-md);
  font-weight: 500;
  /* 默认蓝色（filesystem颜色） */
  color: #1890ff;
  background: rgba(24, 144, 255, 0.1);
}

.source-type.source-filesystem {
  color: #1890ff;
  background: rgba(24, 144, 255, 0.1);
}

.source-type.source-yuque {
  color: #52c41a;
  background: rgba(82, 196, 26, 0.1);
}

.source-type.source-feishu {
  color: #722ed1;
  background: rgba(114, 46, 209, 0.1);
}

.source-type.source-notion {
  color: #fa541c;
  background: rgba(250, 84, 28, 0.1);
}

/* 新增数据源类型样式 */
.source-type.source-github {
  color: #24292e;
  background: rgba(36, 41, 46, 0.1);
}

.source-type.source-gitlab {
  color: #FC6D26;
  background: rgba(252, 109, 38, 0.1);
}

.source-type.source-confluence {
  color: #0052CC;
  background: rgba(0, 82, 204, 0.1);
}

.source-type.source-wordpress {
  color: #21759b;
  background: rgba(33, 117, 155, 0.1);
}

.source-type.source-obsidian {
  color: #7c3aed;
  background: rgba(124, 58, 237, 0.1);
}

.source-type.source-dropbox {
  color: #0061FE;
  background: rgba(0, 97, 254, 0.1);
}

.source-type.source-googledrive {
  color: #4285F4;
  background: rgba(66, 133, 244, 0.1);
}

.source-type.source-onedrive {
  color: #0078D4;
  background: rgba(0, 120, 212, 0.1);
}

.source-type.source-figma {
  color: #F24E1E;
  background: rgba(242, 78, 30, 0.1);
}

.card-actions {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  flex-wrap: wrap;
}

.card-actions .ant-btn {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
}

.card-actions .ant-btn:hover {
  background: var(--surface-02);
  transform: translateY(-1px);
}

/* 打开链接按钮特殊样式 */
.card-actions .open-link-btn {
  color: #1890ff;
}

.card-actions .open-link-btn:hover {
  color: #40a9ff;
  background: rgba(24, 144, 255, 0.1);
}



/* 响应式设计 */
@media (max-width: 768px) {
  .result-card {
    padding: var(--space-4);
  }

  .card-header {
    flex-direction: column;
    gap: var(--space-3);
    align-items: stretch;
  }

  .relevance-score {
    align-self: flex-end;
    margin-left: 0;
  }

  .file-info {
    gap: var(--space-3);
  }

  .card-actions {
    justify-content: center;
  }

  .metadata-row {
    justify-content: center;
    gap: var(--space-2);
  }
}
</style>