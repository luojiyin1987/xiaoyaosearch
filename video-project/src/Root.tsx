import "./index.css";
import { Composition, Folder } from "remotion";
import { ProductPromoVideo, VIDEO_TOTAL_DURATION } from "./compositions/ProductPromoVideo";
import { OpeningScene } from "./scenes/OpeningScene";
import { VoiceSearchScene } from "./scenes/VoiceSearchScene";
import { TextSearchScene } from "./scenes/TextSearchScene";
import { ImageSearchScene } from "./scenes/ImageSearchScene";
import { TechHighlightsScene } from "./scenes/TechHighlightsScene";
import { CTAScene } from "./scenes/CTAScene";
import { VIDEO_CONFIG } from "./types/video";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* 主视频：产品宣传视频 (完整版) */}
      <Composition
        id="ProductPromo"
        component={ProductPromoVideo}
        durationInFrames={VIDEO_TOTAL_DURATION}
        fps={VIDEO_CONFIG.fps}
        width={VIDEO_CONFIG.width}
        height={VIDEO_CONFIG.height}
        defaultProps={{}}
      />

      {/* 场景文件夹 - 用于单独预览每个场景 */}
      <Folder name="独立场景">
        <Composition
          id="OpeningScene"
          component={OpeningScene}
          durationInFrames={240}
          fps={VIDEO_CONFIG.fps}
          width={VIDEO_CONFIG.width}
          height={VIDEO_CONFIG.height}
        />

        <Composition
          id="VoiceSearchScene"
          component={VoiceSearchScene}
          durationInFrames={300}
          fps={VIDEO_CONFIG.fps}
          width={VIDEO_CONFIG.width}
          height={VIDEO_CONFIG.height}
        />

        <Composition
          id="TextSearchScene"
          component={TextSearchScene}
          durationInFrames={300}
          fps={VIDEO_CONFIG.fps}
          width={VIDEO_CONFIG.width}
          height={VIDEO_CONFIG.height}
        />

        <Composition
          id="ImageSearchScene"
          component={ImageSearchScene}
          durationInFrames={210}
          fps={VIDEO_CONFIG.fps}
          width={VIDEO_CONFIG.width}
          height={VIDEO_CONFIG.height}
        />

        <Composition
          id="TechHighlightsScene"
          component={TechHighlightsScene}
          durationInFrames={450}
          fps={VIDEO_CONFIG.fps}
          width={VIDEO_CONFIG.width}
          height={VIDEO_CONFIG.height}
        />

        <Composition
          id="CTAScene"
          component={CTAScene}
          durationInFrames={300}
          fps={VIDEO_CONFIG.fps}
          width={VIDEO_CONFIG.width}
          height={VIDEO_CONFIG.height}
        />
      </Folder>
    </>
  );
};
