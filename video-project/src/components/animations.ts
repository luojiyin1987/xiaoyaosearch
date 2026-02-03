/**
 * Remotion动画辅助函数和组件
 */

import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
  Easing,
  type SpringConfig,
} from 'remotion';
import { BRAND_COLORS } from '../types/video';

// 弹簧动画配置预设
export const SPRING_PRESETS: Record<string, SpringConfig> = {
  smooth: { damping: 200 },                    // 平滑，无弹跳（微妙展示）
  snappy: { damping: 20, stiffness: 200 },     // 清脆，最小弹跳（UI元素）
  bouncy: { damping: 8 },                      // 弹性入场（趣味动画）
  heavy: { damping: 15, stiffness: 80, mass: 2 }, // 沉重，慢速，小弹跳
};

/**
 * 淡入动画
 * @param frame - 当前帧
 * @param startFrame - 开始帧
 * @param duration - 持续时间（帧）
 * @returns 透明度值 (0-1)
 */
export const fadeIn = (
  frame: number,
  startFrame: number,
  duration: number
): number => {
  return interpolate(
    frame,
    [startFrame, startFrame + duration],
    [0, 1],
    { extrapolateRight: 'clamp', extrapolateLeft: 'clamp' }
  );
};

/**
 * 淡出动画
 * @param frame - 当前帧
 * @param startFrame - 开始帧
 * @param duration - 持续时间（帧）
 * @returns 透明度值 (1-0)
 */
export const fadeOut = (
  frame: number,
  startFrame: number,
  duration: number
): number => {
  return interpolate(
    frame,
    [startFrame, startFrame + duration],
    [1, 0],
    { extrapolateRight: 'clamp', extrapolateLeft: 'clamp' }
  );
};

/**
 * 缩放进入动画
 * @param frame - 当前帧
 * @param fps - 帧率
 * @param startFrame - 开始帧
 * @param config - 弹簧配置
 * @returns 缩放值 (0-1)
 */
export const scaleIn = (
  frame: number,
  fps: number,
  startFrame: number,
  config: SpringConfig = SPRING_PRESETS.smooth
): number => {
  return spring({
    frame: frame - startFrame,
    fps,
    config,
  });
};

/**
 * 滑入动画
 * @param frame - 当前帧
 * @param startFrame - 开始帧
 * @param duration - 持续时间（帧）
 * @param direction - 滑入方向
 * @returns 位移值（像素）
 */
export const slideIn = (
  frame: number,
  startFrame: number,
  duration: number,
  direction: 'left' | 'right' | 'top' | 'bottom' = 'left'
): number => {
  const distance = 100; // 滑入距离（像素）
  const progress = interpolate(
    frame,
    [startFrame, startFrame + duration],
    [0, 1],
    {
      extrapolateRight: 'clamp',
      extrapolateLeft: 'clamp',
      easing: Easing.out(Easing.quad),
    }
  );

  const directionMap = {
    left: distance * (1 - progress),
    right: -distance * (1 - progress),
    top: distance * (1 - progress),
    bottom: -distance * (1 - progress),
  };

  return directionMap[direction];
};

/**
 * 打字机效果
 * @param frame - 当前帧
 * @param text - 要显示的文本
 * @param startFrame - 开始帧
 * @param speed - 打字速度（字符/帧，默认每帧1个字符）
 * @returns 当前应该显示的文本
 */
export const typewriter = (
  frame: number,
  text: string,
  startFrame: number,
  speed: number = 1
): string => {
  const charsToShow = Math.max(0, Math.floor((frame - startFrame) * speed));
  return text.slice(0, Math.min(charsToShow, text.length));
};

/**
 * 文本高亮动画
 * @param frame - 当前帧
 * @param startFrame - 开始帧
 * @param duration - 持续时间（帧）
 * @returns 高亮宽度百分比 (0-1)
 */
export const textHighlight = (
  frame: number,
  startFrame: number,
  duration: number
): number => {
  return interpolate(
    frame,
    [startFrame, startFrame + duration],
    [0, 1],
    {
      extrapolateRight: 'clamp',
      extrapolateLeft: 'clamp',
      easing: Easing.out(Easing.quad),
    }
  );
};

/**
 * 脉冲动画（重复放大缩小）
 * @param frame - 当前帧
 * @param startFrame - 开始帧
 * @param minScale - 最小缩放
 * @param maxScale - 最大缩放
 * @param period - 周期（帧）
 * @returns 缩放值
 */
export const pulse = (
  frame: number,
  startFrame: number,
  minScale: number = 1,
  maxScale: number = 1.05,
  period: number = 60
): number => {
  const progress = ((frame - startFrame) % period) / period;
  const sine = Math.sin(progress * Math.PI * 2);
  return minScale + (maxScale - minScale) * ((sine + 1) / 2);
};

/**
 * 旋转进入动画
 * @param frame - 当前帧
 * @param fps - 帧率
 * @param startFrame - 开始帧
 * @param maxRotation - 最大旋转角度
 * @returns 旋转角度
 */
export const rotateIn = (
  frame: number,
  fps: number,
  startFrame: number,
  maxRotation: number = 360
): number => {
  const springValue = spring({
    frame: frame - startFrame,
    fps,
    config: SPRING_PRESETS.bouncy,
  });
  return maxRotation * (1 - springValue);
};

/**
 * 视觉容器组件 - 带动画的容器
 */
interface AnimatedContainerProps {
  children: React.ReactNode;
  style?: React.CSSProperties;
  className?: string;
}

export const AnimatedContainer: React.FC<AnimatedContainerProps> = ({
  children,
  style,
  className,
}) => {
  return (
    <div
      className={className}
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        ...style,
      }}
    >
      {children}
    </div>
  );
};

/**
 * 背景渐变容器
 */
interface GradientBackgroundProps {
  children: React.ReactNode;
  variant?: 'primary' | 'dark' | 'accent';
  className?: string;
}

export const GradientBackground: React.FC<GradientBackgroundProps> = ({
  children,
  variant = 'primary',
  className = '',
}) => {
  const gradients = {
    primary: `linear-gradient(135deg, ${BRAND_COLORS.darkBg} 0%, ${BRAND_COLORS.background} 100%)`,
    dark: `linear-gradient(180deg, ${BRAND_COLORS.darkBg} 0%, ${BRAND_COLORS.background} 100%)`,
    accent: `linear-gradient(135deg, ${BRAND_COLORS.primary} 0%, ${BRAND_COLORS.background} 100%)`,
  };

  return (
    <div
      className={className}
      style={{
        background: gradients[variant],
        width: '100%',
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
      }}
    >
      {children}
    </div>
  );
};

/**
 * 文字卡片组件
 */
interface TextCardProps {
  children: React.ReactNode;
  style?: React.CSSProperties;
  className?: string;
  variant?: 'default' | 'glow' | 'border';
}

export const TextCard: React.FC<TextCardProps> = ({
  children,
  style,
  className = '',
  variant = 'default',
}) => {
  const baseStyle: React.CSSProperties = {
    padding: '20px 40px',
    borderRadius: '12px',
    backgroundColor: 'rgba(15, 23, 42, 0.8)',
    backdropFilter: 'blur(10px)',
    border: variant === 'border' ? `2px solid ${BRAND_COLORS.primary}` : 'none',
    boxShadow: variant === 'glow'
      ? `0 0 30px rgba(37, 99, 235, 0.3)`
      : '0 4px 20px rgba(0, 0, 0, 0.3)',
    ...style,
  };

  return (
    <div className={className} style={baseStyle}>
      {children}
    </div>
  );
};
