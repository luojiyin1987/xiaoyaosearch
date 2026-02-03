/**
 * 语音搜索场景 (8-18秒)
 * 展示语音输入搜索功能
 */

import { AbsoluteFill, useCurrentFrame, useVideoConfig } from 'remotion';
import { BRAND_COLORS, TIME } from '../types/video';
import { fadeIn, fadeOut, slideIn, typewriter, GradientBackground, TextCard, pulse } from '../components/animations';

export const VoiceSearchScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sceneStart = 0; // 这个场景在自己的序列中从0开始

  // 时间点（帧）
  const t = {
    uiShow: sceneStart,
    clickMic: TIME.toFrames(1),
    recording: TIME.toFrames(2),
    searchResults: TIME.toFrames(5),
    audioPreview: TIME.toFrames(7),
    tagline: TIME.toFrames(8.5),
  };

  // 录音波形动画
  const getWaveformBar = (index: number, total: number) => {
    const baseHeight = 20;
    const waveSpeed = 0.3;
    const waveOffset = (index / total) * Math.PI * 2;
    const wave = Math.sin((frame - t.recording) * waveSpeed + waveOffset);
    const height = baseHeight + Math.abs(wave) * 40;

    return {
      height: `${height}px`,
      opacity: fadeOut(frame, t.recording, TIME.toFrames(1)),
    };
  };

  return (
    <GradientBackground variant="primary">
      <AbsoluteFill style={{ backgroundColor: 'transparent' }}>
        {/* 场景标题 */}
        <div
          style={{
            position: 'absolute',
            top: '60px',
            left: '50%',
            transform: 'translateX(-50%)',
            opacity: fadeOut(frame, t.uiShow, TIME.toFrames(1.5)),
          }}
        >
          <h2
            style={{
              fontSize: '36px',
              fontWeight: 'bold',
              color: BRAND_COLORS.text,
              textAlign: 'center',
              fontFamily: 'sans-serif',
            }}
          >
            {typewriter(frame, '用语音，搜索记忆', t.uiShow, 0.3)}
          </h2>
        </div>

        {/* 主UI界面展示 */}
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: '900px',
            height: '500px',
          }}
        >
          {/* UI背景 */}
          <div
            style={{
              position: 'absolute',
              width: '100%',
              height: '100%',
              backgroundColor: 'rgba(15, 23, 42, 0.9)',
              borderRadius: '20px',
              border: `2px solid ${BRAND_COLORS.primary}`,
              boxShadow: '0 10px 40px rgba(0, 0, 0, 0.5)',
              opacity: fadeIn(frame, t.uiShow, 20),
            }}
          />

          {/* 搜索框 */}
          <div
            style={{
              position: 'absolute',
              top: '80px',
              left: '50%',
              transform: `translateX(-50%)`,
              width: '80%',
              height: '60px',
              backgroundColor: '#1E293B',
              borderRadius: '30px',
              border: `2px solid ${BRAND_COLORS.primary}`,
              display: 'flex',
              alignItems: 'center',
              paddingLeft: '20px',
              opacity: fadeIn(frame, t.uiShow + 5, 15),
            }}
          >
            {/* 麦克风图标 */}
            <div
              style={{
                width: '40px',
                height: '40px',
                backgroundColor: BRAND_COLORS.primary,
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transform: `scale(${frame >= t.clickMic ? pulse(frame, t.clickMic, 1, 1.2, 30) : 1})`,
              }}
            >
              <span style={{ fontSize: '20px' }}>🎤</span>
            </div>

            {/* 录音文字 */}
            {frame >= t.recording && frame < t.searchResults && (
              <span
                style={{
                  marginLeft: '15px',
                  fontSize: '18px',
                  color: BRAND_COLORS.text,
                  fontFamily: 'sans-serif',
                }}
              >
                {typewriter(frame, '"我昨天录的那个关于AI的讨论"', t.recording, 0.2)}
              </span>
            )}
          </div>

          {/* 录音波形动画 */}
          {frame >= t.recording && frame < t.searchResults && (
            <div
              style={{
                position: 'absolute',
                top: '160px',
                left: '50%',
                transform: 'translateX(-50%)',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                height: '80px',
              }}
            >
              {Array.from({ length: 20 }).map((_, index) => (
                <div
                  key={index}
                  style={{
                    width: '6px',
                    backgroundColor: BRAND_COLORS.success,
                    borderRadius: '3px',
                    ...getWaveformBar(index, 20),
                  }}
                />
              ))}
            </div>
          )}

          {/* 搜索结果 */}
          {frame >= t.searchResults && (
            <div
              style={{
                position: 'absolute',
                top: '180px',
                left: '50%',
                transform: 'translateX(-50%)',
                width: '85%',
                opacity: fadeIn(frame, t.searchResults, 15),
              }}
            >
              {/* 结果标题 */}
              <div
                style={{
                  fontSize: '16px',
                  color: BRAND_COLORS.text,
                  marginBottom: '10px',
                  fontFamily: 'sans-serif',
                  opacity: 0.7,
                }}
              >
                搜索结果 (3)
              </div>

              {/* 结果卡片 */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {[
                  { name: 'AI技术讨论录音.mp3', type: 'audio', time: '昨天 14:30' },
                  { name: 'AI项目会议记录.mp3', type: 'audio', time: '昨天 10:15' },
                  { name: 'AI产品构思录音.mp3', type: 'audio', time: '前天 16:45' },
                ].map((result, index) => (
                  <div
                    key={index}
                    style={{
                      backgroundColor: '#1E293B',
                      borderRadius: '10px',
                      padding: '15px 20px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '15px',
                      opacity: fadeIn(frame, t.searchResults + index * 5, 10),
                      transform: `translateX(${slideIn(frame, t.searchResults + index * 5, 15, 'left')}px)`,
                    }}
                  >
                    {/* 文件类型图标 */}
                    <div
                      style={{
                        width: '40px',
                        height: '40px',
                        backgroundColor: BRAND_COLORS.primary,
                        borderRadius: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <span style={{ fontSize: '20px' }}>
                        {result.type === 'audio' ? '🎵' : '📄'}
                      </span>
                    </div>

                    {/* 文件信息 */}
                    <div style={{ flex: 1 }}>
                      <div
                        style={{
                          fontSize: '16px',
                          color: BRAND_COLORS.text,
                          fontFamily: 'sans-serif',
                        }}
                      >
                        {result.name}
                      </div>
                      <div
                        style={{
                          fontSize: '12px',
                          color: BRAND_COLORS.text,
                          opacity: 0.6,
                          fontFamily: 'sans-serif',
                        }}
                      >
                        {result.time}
                      </div>
                    </div>

                    {/* 播放按钮 */}
                    <div
                      style={{
                        width: '36px',
                        height: '36px',
                        backgroundColor: BRAND_COLORS.success,
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <span style={{ fontSize: '16px', marginLeft: '2px' }}>▶</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 底部标签 */}
          {frame >= t.tagline && (
            <div
              style={{
                position: 'absolute',
                bottom: '30px',
                left: '50%',
                transform: 'translateX(-50%)',
                opacity: fadeIn(frame, t.tagline, 20),
              }}
            >
              <TextCard variant="border">
                <span
                  style={{
                    fontSize: '28px',
                    fontWeight: 'bold',
                    color: BRAND_COLORS.text,
                    fontFamily: 'sans-serif',
                  }}
                >
                  语音搜索，直达内容
                </span>
              </TextCard>
            </div>
          )}
        </div>
      </AbsoluteFill>
    </GradientBackground>
  );
};
