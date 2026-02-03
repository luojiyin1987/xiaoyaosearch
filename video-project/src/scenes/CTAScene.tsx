/**
 * 行动号召场景 (50-60秒)
 * 品牌强化 + 下载引导
 */

import { AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { BRAND_COLORS, TIME } from '../types/video';
import { fadeIn, scaleIn, SPRING_PRESETS, typewriter, GradientBackground, pulse } from '../components/animations';

export const CTAScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sceneStart = 0;

  // 时间点（帧）
  const t = {
    logo: sceneStart,
    slogan: TIME.toFrames(1),
    download: TIME.toFrames(3),
    users: TIME.toFrames(6),
    final: TIME.toFrames(8),
  };

  // 用户场景
  const userScenarios = [
    { name: '内容创作者', icon: '✍️' },
    { name: '研究员', icon: '🔬' },
    { name: '开发者', icon: '💻' },
  ];

  return (
    <GradientBackground variant="dark">
      <AbsoluteFill style={{ backgroundColor: 'transparent' }}>
        {/* Logo展示 */}
        <div
          style={{
            position: 'absolute',
            top: '35%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            opacity: fadeIn(frame, t.logo, 30),
          }}
        >
          <Img
            src={staticFile('images/logo.png')}
            style={{
              width: '200px',
              height: 'auto',
              transform: `scale(${scaleIn(frame, fps, t.logo, SPRING_PRESETS.smooth)})`,
              filter: `drop-shadow(0 0 ${40 * fadeIn(frame, t.logo, 30)}px rgba(37, 99, 235, 0.6))`,
            }}
          />
        </div>

        {/* Slogan */}
        {frame >= t.slogan && (
          <div
            style={{
              position: 'absolute',
              top: '52%',
              left: '50%',
              transform: 'translateX(-50%)',
              opacity: fadeIn(frame, t.slogan, 25),
            }}
          >
            <h1
              style={{
                fontSize: '48px',
                fontWeight: 'bold',
                color: BRAND_COLORS.text,
                textAlign: 'center',
                fontFamily: 'sans-serif',
                textShadow: `0 0 30px ${BRAND_COLORS.primary}80`,
              }}
            >
              {typewriter(frame, '小遥搜索 - 重新定义本地搜索', t.slogan, 0.15)}
            </h1>
          </div>
        )}

        {/* 下载引导 */}
        {frame >= t.download && (
          <div
            style={{
              position: 'absolute',
              top: '65%',
              left: '50%',
              transform: 'translateX(-50%)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '20px',
              opacity: fadeIn(frame, t.download, 25),
            }}
          >
            {/* 下载按钮 */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '15px',
                backgroundColor: BRAND_COLORS.primary,
                padding: '15px 40px',
                borderRadius: '35px',
                transform: `scale(${pulse(frame, t.download, 1, 1.05, 45)})`,
                boxShadow: `0 10px 40px ${BRAND_COLORS.primary}60`,
              }}
            >
              <span style={{ fontSize: '28px' }}>⬇️</span>
              <span
                style={{
                  fontSize: '24px',
                  fontWeight: 'bold',
                  color: BRAND_COLORS.text,
                  fontFamily: 'sans-serif',
                }}
              >
                立即免费下载体验
              </span>
            </div>

            {/* 二维码 */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '20px',
              }}
            >
              <Img
                src={staticFile('images/qrcode.png')}
                style={{
                  width: '100px',
                  height: '100px',
                  borderRadius: '10px',
                  border: `2px solid ${BRAND_COLORS.primary}`,
                }}
              />
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px',
                }}
              >
                <div
                  style={{
                    fontSize: '18px',
                    color: BRAND_COLORS.text,
                    fontFamily: 'sans-serif',
                  }}
                >
                  扫码访问 GitHub
                </div>
                <div
                  style={{
                    fontSize: '14px',
                    color: BRAND_COLORS.text,
                    opacity: 0.7,
                    fontFamily: 'sans-serif',
                  }}
                >
                  github.com/xiaoyaosearch
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 用户场景快速回顾 */}
        {frame >= t.users && frame < t.final && (
          <div
            style={{
              position: 'absolute',
              bottom: '80px',
              left: '50%',
              transform: 'translateX(-50%)',
              display: 'flex',
              gap: '40px',
              opacity: fadeOut(frame, t.users, TIME.toFrames(2)),
            }}
          >
            {userScenarios.map((user, index) => (
              <div
                key={index}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: '8px',
                  opacity: fadeIn(frame, t.users + index * 3, 10),
                }}
              >
                <div
                  style={{
                    width: '60px',
                    height: '60px',
                    backgroundColor: `${BRAND_COLORS.primary}20`,
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '28px',
                    border: `2px solid ${BRAND_COLORS.primary}`,
                  }}
                >
                  {user.icon}
                </div>
                <div
                  style={{
                    fontSize: '14px',
                    color: BRAND_COLORS.text,
                    fontFamily: 'sans-serif',
                  }}
                >
                  {user.name}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* 最终画面 */}
        {frame >= t.final && (
          <div
            style={{
              position: 'absolute',
              bottom: '30px',
              left: '50%',
              transform: 'translateX(-50%)',
              opacity: fadeIn(frame, t.final, 30),
            }}
          >
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '10px',
              }}
            >
              <div
                style={{
                  fontSize: '16px',
                  color: BRAND_COLORS.text,
                  opacity: 0.8,
                  fontFamily: 'sans-serif',
                }}
              >
                支持 Windows / macOS
              </div>
              <div
                style={{
                  fontSize: '14px',
                  color: BRAND_COLORS.primary,
                  fontFamily: 'sans-serif',
                  fontWeight: 'bold',
                }}
              >
                开源 · 免费 · 安全
              </div>
            </div>
          </div>
        )}

        {/* 装饰光效 */}
        {frame >= t.logo && (
          <>
            <div
              style={{
                position: 'absolute',
                top: '35%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                width: '400px',
                height: '400px',
                borderRadius: '50%',
                background: `radial-gradient(circle, ${BRAND_COLORS.primary}30 0%, transparent 70%)`,
                opacity: fadeIn(frame, t.logo, 40) * 0.4,
                pointerEvents: 'none',
              }}
            />
            <div
              style={{
                position: 'absolute',
                top: '35%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                width: '600px',
                height: '600px',
                borderRadius: '50%',
                background: `radial-gradient(circle, ${BRAND_COLORS.success}20 0%, transparent 70%)`,
                opacity: fadeIn(frame, t.logo, 50) * 0.3,
                pointerEvents: 'none',
              }}
            />
          </>
        )}
      </AbsoluteFill>
    </GradientBackground>
  );
};
