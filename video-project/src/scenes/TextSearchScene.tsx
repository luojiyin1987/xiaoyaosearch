/**
 * 语义搜索场景 (18-28秒)
 * 展示语义理解和跨文件类型搜索
 */

import { AbsoluteFill, useCurrentFrame } from 'remotion';
import { BRAND_COLORS, TIME } from '../types/video';
import { fadeIn, slideIn, typewriter, GradientBackground, TextCard } from '../components/animations';

export const TextSearchScene: React.FC = () => {
  const frame = useCurrentFrame();
  const sceneStart = 0;

  // 时间点（帧）
  const t = {
    uiShow: sceneStart,
    inputText: TIME.toFrames(1),
    aiProcessing: TIME.toFrames(3),
    searchResults: TIME.toFrames(5),
    tagline: TIME.toFrames(9),
  };

  // AI处理动画
  const getAIPulse = () => {
    const pulseSpeed = 0.2;
    const pulse = Math.sin((frame - t.aiProcessing) * pulseSpeed);
    return 0.5 + pulse * 0.5;
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
            opacity: fadeIn(frame, t.uiShow, 20),
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
            {typewriter(frame, '用语义，理解意图', t.uiShow, 0.3)}
          </h2>
        </div>

        {/* 主UI界面 */}
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
          {/* 搜索框 */}
          <div
            style={{
              position: 'absolute',
              top: '50px',
              left: '50%',
              transform: 'translateX(-50%)',
              width: '80%',
              height: '60px',
              backgroundColor: '#1E293B',
              borderRadius: '30px',
              border: `2px solid ${BRAND_COLORS.primary}`,
              display: 'flex',
              alignItems: 'center',
              paddingLeft: '25px',
              paddingRight: '25px',
              opacity: fadeIn(frame, t.uiShow, 20),
            }}
          >
            <span
              style={{
                fontSize: '18px',
                color: BRAND_COLORS.text,
                fontFamily: 'sans-serif',
              }}
            >
              {typewriter(frame, '机器学习算法优化的方法', t.inputText, 0.15)}
            </span>
          </div>

          {/* AI处理动画 */}
          {frame >= t.aiProcessing && frame < t.searchResults && (
            <div
              style={{
                position: 'absolute',
                top: '130px',
                left: '50%',
                transform: 'translateX(-50%)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '15px',
              }}
            >
              {/* 神经网络光效 */}
              <div
                style={{
                  width: '100px',
                  height: '100px',
                  borderRadius: '50%',
                  background: `radial-gradient(circle, ${BRAND_COLORS.primary}${Math.floor(getAIPulse() * 99).toString().padStart(2, '0')} 0%, transparent 70%)`,
                  animation: 'pulse 1s ease-in-out infinite',
                }}
              />

              {/* AI处理文字 */}
              <div
                style={{
                  fontSize: '16px',
                  color: BRAND_COLORS.text,
                  fontFamily: 'sans-serif',
                  opacity: 0.8,
                }}
              >
                AI理解中...
              </div>
            </div>
          )}

          {/* 搜索结果 */}
          {frame >= t.searchResults && (
            <div
              style={{
                position: 'absolute',
                top: '150px',
                left: '50%',
                transform: 'translateX(-50%)',
                width: '95%',
                opacity: fadeIn(frame, t.searchResults, 15),
              }}
            >
              {/* 结果瀑布流 */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: '15px',
                }}
              >
                {[
                  {
                    name: '机器学习优化论文.pdf',
                    type: 'pdf',
                    icon: '📄',
                    highlight: '算法优化',
                  },
                  {
                    name: 'ML项目笔记.md',
                    type: 'md',
                    icon: '📝',
                    highlight: '优化方法',
                  },
                  {
                    name: '机器学习教程.mp4',
                    type: 'video',
                    icon: '🎬',
                    highlight: '算法',
                  },
                  {
                    name: '技术讨论录音.mp3',
                    type: 'audio',
                    icon: '🎵',
                    highlight: '优化',
                  },
                ].map((result, index) => (
                  <div
                    key={index}
                    style={{
                      backgroundColor: '#1E293B',
                      borderRadius: '12px',
                      padding: '15px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      opacity: fadeIn(frame, t.searchResults + index * 5, 12),
                      transform: `translateY(${slideIn(frame, t.searchResults + index * 5, 15, 'top')}px)`,
                      border: `1px solid ${BRAND_COLORS.primary}40`,
                    }}
                  >
                    {/* 文件类型图标 */}
                    <div
                      style={{
                        width: '45px',
                        height: '45px',
                        backgroundColor: `${BRAND_COLORS.primary}20`,
                        borderRadius: '10px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <span style={{ fontSize: '22px' }}>{result.icon}</span>
                    </div>

                    {/* 文件信息 */}
                    <div style={{ flex: 1 }}>
                      <div
                        style={{
                          fontSize: '14px',
                          color: BRAND_COLORS.text,
                          fontFamily: 'sans-serif',
                          fontWeight: 'bold',
                        }}
                      >
                        {result.name}
                      </div>
                      <div
                        style={{
                          fontSize: '12px',
                          color: BRAND_COLORS.success,
                          marginTop: '4px',
                          fontFamily: 'sans-serif',
                        }}
                      >
                        匹配: "{result.highlight}"
                      </div>
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
                bottom: '20px',
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
                  语义搜索，跨文件类型
                </span>
              </TextCard>
            </div>
          )}
        </div>
      </AbsoluteFill>
    </GradientBackground>
  );
};
