/**
 * 技术亮点场景 (35-50秒)
 * 展示本地AI引擎、隐私安全等核心优势
 */

import { AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { BRAND_COLORS, TIME } from '../types/video';
import { fadeIn, slideIn, scaleIn, SPRING_PRESETS, typewriter, GradientBackground, TextCard } from '../components/animations';

export const TechHighlightsScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sceneStart = 0;

  // 时间点（帧）
  const t = {
    architecture: sceneStart,
    localEngine: TIME.toFrames(3),
    privacy: TIME.toFrames(5),
    features: TIME.toFrames(7),
    modelSwitch: TIME.toFrames(10),
    indexManagement: TIME.toFrames(12),
    languageSwitch: TIME.toFrames(13.5),
  };

  // 技术栈组件
  const techStack = [
    { name: 'Faiss向量索引', color: '#3B82F6', icon: '🔵' },
    { name: 'Whoosh全文搜索', color: '#10B981', icon: '🟢' },
    { name: 'BGE-M3文本嵌入', color: '#F59E0B', icon: '🟡' },
    { name: 'FasterWhisper语音识别', color: '#EF4444', icon: '🔴' },
    { name: 'CN-CLIP图像理解', color: '#8B5CF6', icon: '🟣' },
  ];

  // 核心功能
  const coreFeatures = [
    { name: '隐私保护', icon: '🔒' },
    { name: '本地运行', icon: '⚡' },
    { name: '多模态支持', icon: '🌐' },
    { name: '精准搜索', icon: '🎯' },
  ];

  return (
    <GradientBackground variant="dark">
      <AbsoluteFill style={{ backgroundColor: 'transparent' }}>
        {/* 场景标题 */}
        <div
          style={{
            position: 'absolute',
            top: '50px',
            left: '50%',
            transform: 'translateX(-50%)',
            opacity: fadeIn(frame, t.architecture, 20),
          }}
        >
          <h2
            style={{
              fontSize: '40px',
              fontWeight: 'bold',
              color: BRAND_COLORS.text,
              textAlign: 'center',
              fontFamily: 'sans-serif',
            }}
          >
            {typewriter(frame, '强大的本地AI引擎', t.architecture, 0.2)}
          </h2>
        </div>

        {/* 系统架构图 */}
        <div
          style={{
            position: 'absolute',
            top: '120px',
            left: '50%',
            transform: 'translateX(-50%)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '15px',
          }}
        >
          {techStack.map((tech, index) => {
            const showFrame = t.architecture + index * 8;
            return (
              <div
                key={index}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '15px',
                  opacity: fadeIn(frame, showFrame, 15),
                  transform: `translateX(${slideIn(frame, showFrame, 20, 'left')}px)`,
                }}
              >
                <div
                  style={{
                    width: '45px',
                    height: '45px',
                    backgroundColor: tech.color,
                    borderRadius: '10px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '22px',
                  }}
                >
                  {tech.icon}
                </div>
                <div
                  style={{
                    fontSize: '20px',
                    color: BRAND_COLORS.text,
                    fontFamily: 'sans-serif',
                    fontWeight: '500',
                  }}
                >
                  {tech.name}
                </div>
              </div>
            );
          })}
        </div>

        {/* 本地运行强调 */}
        {frame >= t.localEngine && (
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              opacity: fadeOut(frame, t.localEngine, TIME.toFrames(2)),
            }}
          >
            <TextCard variant="glow">
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '20px',
                }}
              >
                <span style={{ fontSize: '48px' }}>🛡️</span>
                <span
                  style={{
                    fontSize: '32px',
                    fontWeight: 'bold',
                    color: BRAND_COLORS.text,
                    fontFamily: 'sans-serif',
                  }}
                >
                  数据不离开你的电脑
                </span>
              </div>
            </TextCard>
          </div>
        )}

        {/* 核心功能展示 */}
        {frame >= t.features && (
          <div
            style={{
              position: 'absolute',
              bottom: frame >= t.modelSwitch ? '180px' : '120px',
              left: '50%',
              transform: 'translateX(-50%)',
              display: 'flex',
              gap: '30px',
            }}
          >
            {coreFeatures.map((feature, index) => {
              const showFrame = t.features + index * 5;
              return (
                <div
                  key={index}
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '10px',
                    opacity: fadeIn(frame, showFrame, 15),
                    transform: `scale(${scaleIn(frame, fps, showFrame, SPRING_PRESETS.snappy)})`,
                  }}
                >
                  <div
                    style={{
                      width: '70px',
                      height: '70px',
                      backgroundColor: `${BRAND_COLORS.primary}20`,
                      borderRadius: '15px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '32px',
                      border: `2px solid ${BRAND_COLORS.primary}`,
                    }}
                  >
                    {feature.icon}
                  </div>
                  <div
                    style={{
                      fontSize: '16px',
                      color: BRAND_COLORS.text,
                      fontFamily: 'sans-serif',
                      fontWeight: '500',
                    }}
                  >
                    {feature.name}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* 云端本地切换演示 */}
        {frame >= t.modelSwitch && (
          <div
            style={{
              position: 'absolute',
              bottom: '80px',
              left: '50%',
              transform: 'translateX(-50%)',
              opacity: fadeIn(frame, t.modelSwitch, 20),
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '30px',
                backgroundColor: '#1E293B',
                padding: '15px 30px',
                borderRadius: '30px',
                border: `2px solid ${BRAND_COLORS.primary}`,
              }}
            >
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                }}
              >
                <span style={{ fontSize: '24px' }}>☁️</span>
                <span
                  style={{
                    fontSize: '18px',
                    color: BRAND_COLORS.text,
                    fontFamily: 'sans-serif',
                  }}
                >
                  云端API
                </span>
              </div>

              {/* 切换按钮 */}
              <div
                style={{
                  width: '50px',
                  height: '26px',
                  backgroundColor: BRAND_COLORS.success,
                  borderRadius: '13px',
                  position: 'relative',
                }}
              >
                <div
                  style={{
                    position: 'absolute',
                    right: '3px',
                    top: '3px',
                    width: '20px',
                    height: '20px',
                    backgroundColor: 'white',
                    borderRadius: '50%',
                  }}
                />
              </div>

              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                }}
              >
                <span style={{ fontSize: '24px' }}>💻</span>
                <span
                  style={{
                    fontSize: '18px',
                    color: BRAND_COLORS.text,
                    fontFamily: 'sans-serif',
                  }}
                >
                  本地Ollama
                </span>
              </div>

              <span
                style={{
                  fontSize: '16px',
                  color: BRAND_COLORS.success,
                  fontFamily: 'sans-serif',
                  marginLeft: '10px',
                  fontWeight: 'bold',
                }}
              >
                自由切换
              </span>
            </div>
          </div>
        )}

        {/* 索引管理和语言切换 */}
        {frame >= t.indexManagement && (
          <div
            style={{
              position: 'absolute',
              bottom: '20px',
              left: '50%',
              transform: 'translateX(-50%)',
              display: 'flex',
              gap: '20px',
              opacity: fadeIn(frame, t.indexManagement, 20),
            }}
          >
            <div
              style={{
                backgroundColor: '#1E293B',
                padding: '10px 20px',
                borderRadius: '20px',
                border: `1px solid ${BRAND_COLORS.primary}50`,
              }}
            >
              <span style={{ fontSize: '16px', color: BRAND_COLORS.text, fontFamily: 'sans-serif' }}>
                📁 一键索引，智能管理
              </span>
            </div>
            <div
              style={{
                backgroundColor: '#1E293B',
                padding: '10px 20px',
                borderRadius: '20px',
                border: `1px solid ${BRAND_COLORS.primary}50`,
              }}
            >
              <span style={{ fontSize: '16px', color: BRAND_COLORS.text, fontFamily: 'sans-serif' }}>
                🌐 中英双语，全球通用
              </span>
            </div>
          </div>
        )}
      </AbsoluteFill>
    </GradientBackground>
  );
};
