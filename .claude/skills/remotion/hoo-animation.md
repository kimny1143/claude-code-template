# Hooアニメーション詳細リファレンス

このファイルはHooキャラクターのアニメーション実装の詳細を記載。

## デザインコンセプト

**Hoo = フクロウ + オープンリールテープレコーダー**

- **メインモチーフ**: フクロウ
- **目**: オープンリールのテープリール（2つの円）
- **テープ**: リール間を繋ぐテープ（8の字/波線）
- **音楽記録アプリ**としての象徴的デザイン

## デザイン仕様

- **スタイル**: 白いラインアート（モノトーン）
- **カラー**: 白 (`#FFFFFF`) のストローク、塗りつぶしなし
- **背景**: 透明（ダークBG上で使用）
- **参照**: `/public/logo.png`

## SVG構造（アニメーション用レイヤー分け）

```svg
<svg viewBox="0 0 200 200" width="200" height="200">
  <!--
    スタイル: stroke="#FFFFFF" stroke-width="2" fill="none"
    全てラインアートで構成
  -->

  <!-- フクロウ本体の輪郭 -->
  <g class="body-outline">
    <!-- 頭 + ボディのシルエット -->
  </g>

  <!-- 耳（羽角） -->
  <g class="ears">
    <path class="left-ear" />
    <path class="right-ear" />
  </g>

  <!-- 左リール（左目） -->
  <g class="left-reel" transform-origin="center">
    <circle class="reel-outer" />  <!-- 外円 -->
    <circle class="reel-inner" />  <!-- 内円/ハブ -->
    <!-- リールのスポーク等あれば -->
  </g>

  <!-- 右リール（右目） -->
  <g class="right-reel" transform-origin="center">
    <circle class="reel-outer" />
    <circle class="reel-inner" />
  </g>

  <!-- テープ（リール間を繋ぐ） -->
  <g class="tape">
    <path class="tape-path" />  <!-- 8の字 or 波線 -->
  </g>

  <!-- くちばし（あれば） -->
  <g class="beak">
    <path />
  </g>
</svg>
```

## アニメーションパターン

### idle（待機）- リール回転
```typescript
export const idleAnimation = (frame: number, fps: number) => {
  // リールがゆっくり回転（録音中のイメージ）
  const rotation = (frame / fps) * 30; // 1秒で30度回転

  return {
    leftReel: { rotate: rotation },
    rightReel: { rotate: -rotation }, // 逆回転
    body: { translateY: Math.sin((frame / fps) * Math.PI) * 2 }, // 軽い呼吸
  };
};
```

### recording（録音中）- リール高速回転
```typescript
export const recordingAnimation = (frame: number, fps: number) => {
  // リールが速く回転
  const rotation = (frame / fps) * 180; // 1秒で180度

  // テープが流れるアニメーション（dashoffset）
  const tapeOffset = (frame / fps) * 50;

  return {
    leftReel: { rotate: rotation },
    rightReel: { rotate: -rotation },
    tape: { strokeDashoffset: -tapeOffset },
  };
};
```

### curious（興味）- 首傾げ
```typescript
export const curiousAnimation = (frame: number, fps: number, startFrame: number = 0) => {
  const progress = spring({
    frame: frame - startFrame,
    fps,
    config: { damping: 15, stiffness: 80 },
  });

  return {
    body: { rotate: progress * 15 }, // 首を傾ける
    leftReel: { rotate: (frame / fps) * 30 },
    rightReel: { rotate: -(frame / fps) * 30 },
  };
};
```

### happy（喜び）- リール高速 + 揺れ
```typescript
export const happyAnimation = (frame: number, fps: number) => {
  const bounce = Math.sin((frame / fps) * Math.PI * 4) * 5;
  const fastRotation = (frame / fps) * 360;

  return {
    body: { translateY: -Math.abs(bounce) },
    leftReel: { rotate: fastRotation },
    rightReel: { rotate: -fastRotation },
  };
};
```

## SVG作成手順

1. `/public/logo.png` をFigmaにインポート
2. Image Trace または手動でパスをトレース
3. **重要**: 以下のパーツを個別レイヤーに分離:
   - 本体輪郭 (`body-outline`)
   - 左リール (`left-reel`) - 回転の中心点を設定
   - 右リール (`right-reel`) - 回転の中心点を設定
   - テープ (`tape`)
   - 耳 (`ears`)
4. 各パーツの `transform-origin` を適切に設定
5. SVGとしてエクスポート

## 状態別アニメーション詳細

### idle（待機）

```typescript
export const idleAnimation = (frame: number, fps: number) => {
  // 呼吸：2秒周期で上下2px
  const breathCycle = (frame / fps) * Math.PI;
  const breathY = Math.sin(breathCycle) * 2;
  
  // まばたき：4秒に1回、0.2秒間
  const blinkCycle = frame % (fps * 4);
  const isBlinking = blinkCycle >= 0 && blinkCycle < fps * 0.2;
  const eyeScaleY = isBlinking ? 0.1 : 1;
  
  return {
    body: { translateY: breathY },
    head: { translateY: breathY * 0.5 },
    leftEye: { scaleY: eyeScaleY },
    rightEye: { scaleY: eyeScaleY },
  };
};
```

### curious（興味・説明）

```typescript
export const curiousAnimation = (
  frame: number, 
  fps: number, 
  startFrame: number = 0
) => {
  const progress = spring({
    frame: frame - startFrame,
    fps,
    config: {
      damping: 15,
      stiffness: 80,
      mass: 0.8,
    },
  });
  
  // 首を右に15度傾ける
  const headRotate = progress * 15;
  
  // 目を見開く
  const eyeScale = 1 + progress * 0.2;
  
  // 軽く前傾
  const bodyLean = progress * 3;
  
  return {
    head: { 
      rotate: headRotate,
      translateY: -bodyLean,
    },
    leftEye: { scale: eyeScale },
    rightEye: { scale: eyeScale },
    body: { translateY: bodyLean },
  };
};
```

### happy（喜び）

```typescript
export const happyAnimation = (frame: number, fps: number) => {
  // 羽パタパタ：1秒に8回
  const flapSpeed = 8;
  const flapAngle = Math.sin((frame / fps) * Math.PI * flapSpeed) * 25;
  
  // 軽くジャンプ：0.5秒周期
  const jumpCycle = (frame / fps) * Math.PI * 4;
  const jumpY = Math.abs(Math.sin(jumpCycle)) * 8;
  
  // 目を細める（笑顔）
  const eyeScaleY = 0.6;
  const eyeScaleX = 1.1;
  
  // くちばしを開く
  const beakOpen = 5;
  
  return {
    leftWing: { rotate: -flapAngle },
    rightWing: { rotate: flapAngle },
    body: { translateY: -jumpY },
    head: { translateY: -jumpY },
    leftEye: { scaleX: eyeScaleX, scaleY: eyeScaleY },
    rightEye: { scaleX: eyeScaleX, scaleY: eyeScaleY },
    beak: { translateY: beakOpen },
  };
};
```

### thinking（考え中）

```typescript
export const thinkingAnimation = (
  frame: number, 
  fps: number, 
  startFrame: number = 0
) => {
  const progress = spring({
    frame: frame - startFrame,
    fps,
    config: { damping: 20, stiffness: 60 },
  });
  
  // 首を左に傾ける
  const headRotate = progress * -10;
  
  // 目を上に向ける
  const eyeLookUp = progress * -5;
  
  // 右羽を顎に当てる仕草
  const rightWingRotate = progress * -30;
  const rightWingTranslate = progress * 20;
  
  return {
    head: { rotate: headRotate },
    leftEye: { translateY: eyeLookUp },
    rightEye: { translateY: eyeLookUp },
    rightWing: { 
      rotate: rightWingRotate,
      translateX: -rightWingTranslate,
      translateY: -rightWingTranslate,
    },
  };
};
```

### pointing（指し示す）

```typescript
export const pointingAnimation = (
  frame: number, 
  fps: number, 
  direction: 'left' | 'right' = 'right',
  startFrame: number = 0
) => {
  const progress = spring({
    frame: frame - startFrame,
    fps,
    config: { damping: 12, stiffness: 100 },
  });
  
  const isRight = direction === 'right';
  
  // 体を指す方向に向ける
  const bodyRotate = progress * (isRight ? 10 : -10);
  
  // 羽を伸ばす
  const wingRotate = progress * (isRight ? 45 : -45);
  const wingExtend = progress * 30;
  
  // 目を指す方向に向ける
  const eyeLook = progress * (isRight ? 8 : -8);
  
  return {
    body: { rotate: bodyRotate },
    [isRight ? 'rightWing' : 'leftWing']: {
      rotate: wingRotate,
      translateX: isRight ? wingExtend : -wingExtend,
    },
    leftEye: { translateX: eyeLook },
    rightEye: { translateX: eyeLook },
  };
};
```

## 口パクアニメーション（リップシンク）

```typescript
interface LipSyncProps {
  text: string;
  startFrame: number;
  charsPerSecond?: number;
}

export const lipSyncAnimation = (
  frame: number,
  fps: number,
  { text, startFrame, charsPerSecond = 10 }: LipSyncProps
) => {
  const adjustedFrame = frame - startFrame;
  if (adjustedFrame < 0) return { beakOpen: 0 };
  
  const currentCharIndex = Math.floor((adjustedFrame / fps) * charsPerSecond);
  
  if (currentCharIndex >= text.length) return { beakOpen: 0 };
  
  const currentChar = text[currentCharIndex];
  
  // 母音で口を開く
  const vowels = ['a', 'i', 'u', 'e', 'o', 'あ', 'い', 'う', 'え', 'お'];
  const isVowel = vowels.includes(currentChar.toLowerCase());
  
  // 口の開き具合
  const beakOpen = isVowel ? 8 : 2;
  
  return { beakOpen };
};
```

## トランジション

### Hooの登場

```typescript
export const hooEntrance = (
  frame: number,
  fps: number,
  from: 'left' | 'right' | 'bottom' = 'right'
) => {
  const progress = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 80 },
  });
  
  const directions = {
    left: { x: -300, y: 0 },
    right: { x: 300, y: 0 },
    bottom: { x: 0, y: 200 },
  };
  
  const dir = directions[from];
  
  return {
    translateX: dir.x * (1 - progress),
    translateY: dir.y * (1 - progress),
    opacity: progress,
    scale: 0.5 + progress * 0.5,
  };
};
```

### Hooの退場

```typescript
export const hooExit = (
  frame: number,
  fps: number,
  startFrame: number,
  to: 'left' | 'right' | 'top' = 'right'
) => {
  const adjustedFrame = frame - startFrame;
  if (adjustedFrame < 0) return { translateX: 0, translateY: 0, opacity: 1 };
  
  const progress = spring({
    frame: adjustedFrame,
    fps,
    config: { damping: 15, stiffness: 100 },
  });
  
  const directions = {
    left: { x: -300, y: 0 },
    right: { x: 300, y: 0 },
    top: { x: 0, y: -200 },
  };
  
  const dir = directions[to];
  
  return {
    translateX: dir.x * progress,
    translateY: dir.y * progress,
    opacity: 1 - progress,
  };
};
```

## 使用例：完全なコンポーネント

```typescript
// src/components/Hoo/HooCharacter.tsx
import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate, spring } from 'remotion';
import {
  idleAnimation,
  curiousAnimation,
  happyAnimation,
  thinkingAnimation,
  pointingAnimation,
} from './animations';

type HooState = 'idle' | 'curious' | 'happy' | 'thinking' | 'pointing';

interface HooProps {
  state?: HooState;
  scale?: number;
  position?: { x: number; y: number };
  enterFrom?: 'left' | 'right' | 'bottom' | null;
  enterDelay?: number;
}

export const HooCharacter: React.FC<HooProps> = ({
  state = 'idle',
  scale = 1,
  position = { x: 0, y: 0 },
  enterFrom = null,
  enterDelay = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  
  // 登場アニメーション
  const entranceAnim = enterFrom
    ? hooEntrance(frame - enterDelay, fps, enterFrom)
    : { translateX: 0, translateY: 0, opacity: 1, scale: 1 };
  
  // 状態別アニメーション
  const stateAnims = {
    idle: idleAnimation(frame, fps),
    curious: curiousAnimation(frame, fps),
    happy: happyAnimation(frame, fps),
    thinking: thinkingAnimation(frame, fps),
    pointing: pointingAnimation(frame, fps, 'right'),
  };
  
  const anim = stateAnims[state];
  
  return (
    <div
      style={{
        position: 'absolute',
        left: position.x,
        top: position.y,
        transform: `
          translate(${entranceAnim.translateX}px, ${entranceAnim.translateY}px)
          scale(${scale * entranceAnim.scale})
        `,
        opacity: entranceAnim.opacity,
      }}
    >
      {/* SVG実装 */}
      <svg viewBox="0 0 200 200" width={200} height={200}>
        {/* ... SVG内容（上記参照） ... */}
      </svg>
    </div>
  );
};
```

## パフォーマンス最適化

### メモ化

```typescript
import { useMemo } from 'react';

// 重い計算はメモ化
const animationValues = useMemo(() => {
  return calculateComplexAnimation(frame, fps);
}, [frame, fps]);
```

### 条件付きレンダリング

```typescript
// 画面外の要素はレンダリングしない
const isVisible = frame >= enterDelay && frame <= exitFrame;
if (!isVisible) return null;
```
