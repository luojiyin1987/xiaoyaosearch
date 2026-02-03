/**
 * 音频配置组件
 * 用于产品宣传视频的背景音乐和音效
 */

import { Audio } from '@remotion/media';
import { staticFile, interpolate } from 'remotion';
import { VIDEO_TOTAL_DURATION } from '../compositions/ProductPromoVideo';

/**
 * 背景音乐组件
 * 根据不同场景调整音乐情绪
 */
export const BackgroundMusic: React.FC = () => {
  // 音乐情绪调整
  const getVolume = (f: number) => {
    const totalFrames = VIDEO_TOTAL_DURATION;

    // 开场（0-8s）：悬疑、探索感 - 音量渐入
    const introVolume = interpolate(f, [0, 60], [0, 0.3], {
      extrapolateRight: 'clamp',
      extrapolateLeft: 'clamp',
    });

    // 展示阶段（8-35s）：轻快、愉悦 - 中等音量
    const showcaseVolume = interpolate(f, [240, 270], [0.3, 0.4], {
      extrapolateRight: 'clamp',
      extrapolateLeft: 'clamp',
    });

    // 技术亮点（35-50s）：科技、专业 - 稳定音量
    const techVolume = interpolate(f, [900, 1050], [0.4, 0.35], {
      extrapolateRight: 'clamp',
      extrapolateLeft: 'clamp',
    });

    // 结尾（50-60s）：激昂、号召性 - 音量渐强后渐弱
    const ctaVolumeIn = interpolate(f, [1050, 1140], [0.35, 0.5], {
      extrapolateRight: 'clamp',
      extrapolateLeft: 'clamp',
    });
    const ctaVolumeOut = interpolate(f, [1140, totalFrames - 30], [0.5, 0.2], {
      extrapolateRight: 'clamp',
      extrapolateLeft: 'clamp',
    });

    // 根据当前帧选择合适的音量
    if (f < 240) return introVolume;
    if (f < 900) return showcaseVolume;
    if (f < 1050) return techVolume;
    if (f < 1140) return ctaVolumeIn;
    return ctaVolumeOut;
  };

  return (
    <Audio
      src={staticFile('audio/background-music.mp3')}
      volume={getVolume}
      loop={false}
    />
  );
};

/**
 * 音效组件
 * 关键时刻的音效提示
 */
export const SoundEffects: React.FC = () => {
  return (
    <>
      {/* Logo展示音效 (7-8秒) */}
      {/* 需要7秒的音频文件，在第7秒播放"叮"声 */}
      {/* <Audio src={staticFile('audio/logo-reveal.mp3')} /> */}

      {/* 搜索执行音效 (每个搜索场景) */}
      {/* <Audio src={staticFile('audio/search-swish.mp3')} /> */}

      {/* 确认/成功音效 */}
      {/* <Audio src={staticFile('audio/success-ding.mp3')} /> */}
    </>
  );
};

/**
 * 配音组件
 * 旁白/解说音轨
 */
export const VoiceOver: React.FC = () => {
  return (
    <Audio
      src={staticFile('audio/voiceover.mp3')}
      volume={0.8}
    />
  );
};

/**
 * 完整音频组合
 * 包含背景音乐、音效和配音
 */
export const FullAudioTrack: React.FC = () => {
  return (
    <>
      <BackgroundMusic />
      {/* 配音音轨 - 可选，根据制作需求添加 */}
      {/* <VoiceOver /> */}
      {/* 音效音轨 - 可选，根据制作需求添加 */}
      {/* <SoundEffects /> */}
    </>
  );
};
