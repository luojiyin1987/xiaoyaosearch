/**
 * 开场钩子场景 (0-8秒)
 * 痛点场景 + 问题提出 + Logo展示
 */

import { AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { BRAND_COLORS, TIME } from '../types/video';
import { fadeIn, fadeOut, scaleIn, SPRING_PRESETS, typewriter, GradientBackground, TextCard } from '../components/animations';

export const OpeningScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // 时间点（帧）
  const t = {
    questionStart: 0,
    painPointsStart: TIME.toFrames(2),
    questionTextStart: TIME.toFrames(5),
    logoStart: TIME.toFrames(7),
  };

  return (
    <GradientBackground variant="dark">
      <AbsoluteFill style={{ backgroundColor: 'transparent' }}>
        {/* 镜号01: 问题文字 (0-2秒) */}
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            opacity: fadeOut(frame, t.questionStart, TIME.toFrames(0.5)),
          }}
        >
          <h1
            style={{
              fontSize: '48px',
              fontWeight: 'bold',
              color: BRAND_COLORS.text,
              textAlign: 'center',
              fontFamily: 'sans-serif',
            }}
          >
            {typewriter(frame, '你是否经历过这样的时刻？', t.questionStart, 0.5)}
          </h1>
        </div>

        {/* 镜号02: 痛点场景快速切换 (2-5秒) */}
        {frame >= t.painPointsStart && frame < t.questionTextStart && (
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              opacity: fadeIn(frame, t.painPointsStart, 15),
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '30px',
            }}
          >
            {/* 痛点图标组 */}
            <div
              style={{
                display: 'flex',
                gap: '60px',
                alignItems: 'center',
              }}
            >
              {/* 文件夹图标 */}
              <div
                style={{
                  width: '120px',
                  height: '120px',
                  backgroundColor: BRAND_COLORS.primary,
                  borderRadius: '20px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  opacity: fadeIn(frame, t.painPointsStart, 10),
                }}
              >
                <span
                  style={{
                    fontSize: '48px',
                    color: BRAND_COLORS.text,
                  }}
                >
                  📁
                </span>
              </div>

              {/* 搜索转圈图标 */}
              <div
                style={{
                  width: '120px',
                  height: '120px',
                  backgroundColor: BRAND_COLORS.accent,
                  borderRadius: '20px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  opacity: fadeIn(frame, t.painPointsStart + 5, 10),
                  animation: 'spin 1s linear infinite',
                }}
              >
                <span
                  style={{
                    fontSize: '48px',
                    color: BRAND_COLORS.text,
                  }}
                >
                  🔍
                </span>
              </div>

              {/* 焦虑表情 */}
              <div
                style={{
                  width: '120px',
                  height: '120px',
                  backgroundColor: '#EF4444',
                  borderRadius: '20px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  opacity: fadeIn(frame, t.painPointsStart + 10, 10),
                }}
              >
                <span
                  style={{
                    fontSize: '48px',
                  }}
                >
                  😰
                </span>
              </div>
            </div>

            {/* 痛点文字 */}
            <p
              style={{
                fontSize: '28px',
                color: BRAND_COLORS.text,
                textAlign: 'center',
                marginTop: '20px',
              }}
            >
              杂乱的文件 · 转圈的搜索 · 找不到的内容
            </p>
          </div>
        )}

        {/* 镜号03: 核心问题 (5-7秒) */}
        {frame >= t.questionTextStart && (
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              opacity: fadeOut(frame, t.questionTextStart, TIME.toFrames(2)),
            }}
          >
            <TextCard variant="glow">
              <h2
                style={{
                  fontSize: '56px',
                  fontWeight: 'bold',
                  color: BRAND_COLORS.text,
                  textAlign: 'center',
                  fontFamily: 'sans-serif',
                }}
              >
                {typewriter(frame, '记得内容，找不到文件？', t.questionTextStart, 0.4)}
              </h2>
            </TextCard>
          </div>
        )}

        {/* 镜号04: Logo展示 (7-8秒) */}
        {frame >= t.logoStart && (
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
            }}
          >
            <Img
              src={staticFile('images/logo.png')}
              style={{
                width: '300px',
                height: 'auto',
                opacity: fadeIn(frame, t.logoStart, 15),
                transform: `scale(${scaleIn(frame, fps, t.logoStart, SPRING_PRESETS.bouncy)})`,
                filter: `drop-shadow(0 0 ${30 * fadeIn(frame, t.logoStart, 15)}px rgba(37, 99, 235, 0.5))`,
              }}
            />
          </div>
        )}

        {/* Logo光效 */}
        {frame >= t.logoStart && (
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              width: '400px',
              height: '400px',
              borderRadius: '50%',
              background: `radial-gradient(circle, ${BRAND_COLORS.primary}40 0%, transparent 70%)`,
              opacity: fadeIn(frame, t.logoStart, 20) * 0.5,
              pointerEvents: 'none',
            }}
          />
        )}
      </AbsoluteFill>
    </GradientBackground>
  );
};
