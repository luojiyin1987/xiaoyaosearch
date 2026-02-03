/**
 * 图片搜索场景 (28-35秒)
 * 展示图片上传和视觉理解搜索
 */

import { AbsoluteFill, Img, staticFile, useCurrentFrame } from 'remotion';
import { BRAND_COLORS, TIME } from '../types/video';
import { fadeIn, slideIn, typewriter, GradientBackground, TextCard } from '../components/animations';

export const ImageSearchScene: React.FC = () => {
  const frame = useCurrentFrame();
  const sceneStart = 0;

  // 时间点（帧）
  const t = {
    uiShow: sceneStart,
    uploadImage: TIME.toFrames(1),
    scanning: TIME.toFrames(2.5),
    searchResults: TIME.toFrames(4.5),
    tagline: TIME.toFrames(6),
  };

  // 扫描线动画
  const getScanLinePosition = () => {
    if (frame < t.scanning || frame >= t.searchResults) return null;

    const duration = t.searchResults - t.scanning;
    const progress = (frame - t.scanning) / duration;
    return 20 + progress * 260; // 从20px到280px
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
            {typewriter(frame, '用图片，寻找关联', t.uiShow, 0.3)}
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
            height: '450px',
          }}
        >
          {/* 图片上传区域 */}
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: '25%',
              transform: 'translate(-50%, -50%)',
              width: '300px',
              height: '300px',
              backgroundColor: '#1E293B',
              borderRadius: '20px',
              border: `2px dashed ${BRAND_COLORS.primary}`,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              opacity: fadeIn(frame, t.uiShow, 20),
            }}
          >
            {/* 上传图标 */}
            {frame < t.uploadImage && (
              <>
                <div
                  style={{
                    width: '80px',
                    height: '80px',
                    backgroundColor: `${BRAND_COLORS.primary}30`,
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: '15px',
                  }}
                >
                  <span style={{ fontSize: '40px' }}>📤</span>
                </div>
                <span
                  style={{
                    fontSize: '16px',
                    color: BRAND_COLORS.text,
                    fontFamily: 'sans-serif',
                  }}
                >
                  拖拽图片上传
                </span>
              </>
            )}

            {/* 上传的图片 */}
            {frame >= t.uploadImage && (
              <div style={{ position: 'relative', width: '100%', height: '100%' }}>
                <Img
                  src={staticFile('images/logo.png')}
                  style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'contain',
                    padding: '20px',
                    opacity: fadeIn(frame, t.uploadImage, 15),
                  }}
                />

                {/* 扫描线效果 */}
                {getScanLinePosition() !== null && (
                  <>
                    <div
                      style={{
                        position: 'absolute',
                        left: '10px',
                        right: '10px',
                        top: getScanLinePosition()!,
                        height: '3px',
                        background: `linear-gradient(90deg, transparent, ${BRAND_COLORS.success}, transparent)`,
                        boxShadow: `0 0 10px ${BRAND_COLORS.success}`,
                      }}
                    />
                    <div
                      style={{
                        position: 'absolute',
                        left: '10px',
                        right: '10px',
                        top: 0,
                        bottom: 0,
                        background: `linear-gradient(180deg, ${BRAND_COLORS.primary}10 0%, transparent ${getScanLinePosition()!}px)`,
                        pointerEvents: 'none',
                      }}
                    />
                  </>
                )}
              </div>
            )}
          </div>

          {/* 搜索结果区域 */}
          {frame >= t.searchResults && (
            <div
              style={{
                position: 'absolute',
                top: '50%',
                left: '70%',
                transform: 'translate(-50%, -50%)',
                width: '320px',
                opacity: fadeIn(frame, t.searchResults, 20),
              }}
            >
              <div
                style={{
                  fontSize: '16px',
                  color: BRAND_COLORS.text,
                  marginBottom: '10px',
                  fontFamily: 'sans-serif',
                  opacity: 0.8,
                }}
              >
                相关文件 (3)
              </div>

              {/* 结果卡片 */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {[
                  { name: 'Logo设计稿.fig', type: 'design', icon: '🎨' },
                  { name: '品牌规范文档.pdf', type: 'pdf', icon: '📄' },
                  { name: '设计参考图.png', type: 'image', icon: '🖼️' },
                ].map((result, index) => (
                  <div
                    key={index}
                    style={{
                      backgroundColor: '#1E293B',
                      borderRadius: '10px',
                      padding: '12px 15px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      opacity: fadeIn(frame, t.searchResults + index * 5, 12),
                      transform: `translateX(${slideIn(frame, t.searchResults + index * 5, 15, 'right')}px)`,
                    }}
                  >
                    <div
                      style={{
                        width: '35px',
                        height: '35px',
                        backgroundColor: `${BRAND_COLORS.primary}20`,
                        borderRadius: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <span style={{ fontSize: '18px' }}>{result.icon}</span>
                    </div>

                    <div>
                      <div
                        style={{
                          fontSize: '14px',
                          color: BRAND_COLORS.text,
                          fontFamily: 'sans-serif',
                        }}
                      >
                        {result.name}
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
                  图片搜索，视觉理解
                </span>
              </TextCard>
            </div>
          )}
        </div>
      </AbsoluteFill>
    </GradientBackground>
  );
};
