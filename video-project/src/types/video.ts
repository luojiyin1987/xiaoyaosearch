/**
 * 视频通用类型定义
 */

// 品牌颜色配置
export const BRAND_COLORS = {
  primary: '#2563EB',    // 科技蓝
  success: '#10B981',    // 成功绿
  accent: '#F59E0B',     // 活力橙
  background: '#0F172A', // 深空蓝
  text: '#F8FAFC',       // 亮白
  darkBg: '#020617',     // 更深色背景
} as const;

// 视频配置常量
export const VIDEO_CONFIG = {
  fps: 30,
  width: 1920,
  height: 1080,
} as const;

// 时间转换常量
export const TIME = {
  FPS: VIDEO_CONFIG.fps,
  SECOND: VIDEO_CONFIG.fps,     // 1秒 = 30帧
  toFrames: (seconds: number) => Math.floor(seconds * VIDEO_CONFIG.fps),
} as const;

// 场景持续时间（帧数）
export const SCENE_DURATIONS = {
  OPENING: TIME.toFrames(8),      // 0-8秒: 开场钩子
  VOICE_SEARCH: TIME.toFrames(10), // 8-18秒: 语音搜索
  TEXT_SEARCH: TIME.toFrames(10), // 18-28秒: 语义搜索
  IMAGE_SEARCH: TIME.toFrames(7), // 28-35秒: 图片搜索
  TECH_HIGHLIGHTS: TIME.toFrames(15), // 35-50秒: 技术亮点
  CTA: TIME.toFrames(10),         // 50-60秒: 行动号召
} as const;

// 总时长（帧数）
export const TOTAL_DURATION = Object.values(SCENE_DURATIONS).reduce((sum, duration) => sum + duration, 0);
