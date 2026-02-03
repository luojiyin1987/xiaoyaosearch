/**
 * 小遥搜索产品宣传视频
 * 主组合组件 - 使用 TransitionSeries 连接所有场景
 */

import { AbsoluteFill } from 'remotion';
import { TransitionSeries, linearTiming } from '@remotion/transitions';
import { fade } from '@remotion/transitions/fade';
import { OpeningScene } from '../scenes/OpeningScene';
import { VoiceSearchScene } from '../scenes/VoiceSearchScene';
import { TextSearchScene } from '../scenes/TextSearchScene';
import { ImageSearchScene } from '../scenes/ImageSearchScene';
import { TechHighlightsScene } from '../scenes/TechHighlightsScene';
import { CTAScene } from '../scenes/CTAScene';
import { FullAudioTrack } from '../components/AudioTrack';
import { SCENE_DURATIONS } from '../types/video';

/**
 * 产品宣传视频主组合
 * 总时长: 60秒 (1800帧 @ 30fps)
 */
export const ProductPromoVideo: React.FC = () => {
  const transitionDuration = 15; // 转场持续帧数 (0.5秒)

  return (
    <AbsoluteFill>
      {/* 背景音乐音轨 */}
      <FullAudioTrack />

      {/* 视频场景序列 */}
      <TransitionSeries>
      {/* 场景1: 开场钩子 (0-8秒) */}
      <TransitionSeries.Sequence durationInFrames={SCENE_DURATIONS.OPENING}>
        <OpeningScene />
      </TransitionSeries.Sequence>

      {/* 转场 */}
      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: transitionDuration })}
      />

      {/* 场景2: 语音搜索 (8-18秒) */}
      <TransitionSeries.Sequence durationInFrames={SCENE_DURATIONS.VOICE_SEARCH}>
        <VoiceSearchScene />
      </TransitionSeries.Sequence>

      {/* 转场 */}
      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: transitionDuration })}
      />

      {/* 场景3: 语义搜索 (18-28秒) */}
      <TransitionSeries.Sequence durationInFrames={SCENE_DURATIONS.TEXT_SEARCH}>
        <TextSearchScene />
      </TransitionSeries.Sequence>

      {/* 转场 */}
      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: transitionDuration })}
      />

      {/* 场景4: 图片搜索 (28-35秒) */}
      <TransitionSeries.Sequence durationInFrames={SCENE_DURATIONS.IMAGE_SEARCH}>
        <ImageSearchScene />
      </TransitionSeries.Sequence>

      {/* 转场 */}
      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: transitionDuration })}
      />

      {/* 场景5: 技术亮点 (35-50秒) */}
      <TransitionSeries.Sequence durationInFrames={SCENE_DURATIONS.TECH_HIGHLIGHTS}>
        <TechHighlightsScene />
      </TransitionSeries.Sequence>

      {/* 转场 */}
      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: transitionDuration })}
      />

      {/* 场景6: 行动号召 (50-60秒) */}
      <TransitionSeries.Sequence durationInFrames={SCENE_DURATIONS.CTA}>
        <CTAScene />
      </TransitionSeries.Sequence>
    </TransitionSeries>
    </AbsoluteFill>
  );
};

/**
 * 计算视频总时长
 * 考虑转场重叠，总时长 = 各场景时长之和 - 转场时长之和
 */
const calculateTotalDuration = () => {
  const transitionCount = 5; // 5个转场
  const transitionDuration = 15;
  const totalSceneDuration = Object.values(SCENE_DURATIONS).reduce((sum, duration) => sum + duration, 0);
  return totalSceneDuration - transitionCount * transitionDuration;
};

export const VIDEO_TOTAL_DURATION = calculateTotalDuration(); // 1800 - 75 = 1725帧 = 57.5秒
