# Hooアニメーション詳細リファレンス

このファイルはHooキャラクターのアニメーション実装の詳細を記載。

## SVG構造

```svg
<svg viewBox="0 0 200 200" width="200" height="200">
  <!-- 背景レイヤー（影） -->
  <ellipse class="shadow" cx="100" cy="185" rx="40" ry="10" fill="rgba(0,0,0,0.2)" />
  
  <!-- ボディ -->
  <g class="body">
    <ellipse cx="100" cy="130" rx="55" ry="65" fill="#F6AD55" />
    <!-- 胸の模様 -->
    <ellipse cx="100" cy="145" rx="35" ry="45" fill="#FAD9A8" />
  </g>
  
  <!-- 左羽 -->
  <g class="left-wing" transform-origin="70 120">
    <ellipse cx="50" cy="120" rx="22" ry="40" fill="#E08D3C" />
  </g>
  
  <!-- 右羽 -->
  <g class="right-wing" transform-origin="130 120">
    <ellipse cx="150" cy="120" rx="22" ry="40" fill="#E08D3C" />
  </g>
  
  <!-- 頭部 -->
  <g class="head" transform-origin="100 80">
    <circle cx="100" cy="65" r="48" fill="#F6AD55" />
    
    <!-- 耳（羽角） -->
    <polygon class="left-ear" points="60,30 70,55 55,50" fill="#E08D3C" />
    <polygon class="right-ear" points="140,30 130,55 145,50" fill="#E08D3C" />
    
    <!-- 顔の模様 -->
    <ellipse cx="100" cy="70" rx="38" ry="35" fill="#FAD9A8" />
    
    <!-- 左目 -->
    <g class="left-eye">
      <ellipse cx="80" cy="60" rx="14" ry="18" fill="#2D3748" />
      <ellipse cx="80" cy="60" rx="10" ry="14" fill="#1A202C" />
      <circle cx="84" cy="55" r="5" fill="white" />
      <circle cx="78" cy="63" r="2" fill="white" opacity="0.5" />
    </g>
    
    <!-- 右目 -->
    <g class="right-eye">
      <ellipse cx="120" cy="60" rx="14" ry="18" fill="#2D3748" />
      <ellipse cx="120" cy="60" rx="10" ry="14" fill="#1A202C" />
      <circle cx="124" cy="55" r="5" fill="white" />
      <circle cx="118" cy="63" r="2" fill="white" opacity="0.5" />
    </g>
    
    <!-- くちばし -->
    <polygon class="beak" points="100,72 88,90 112,90" fill="#2D3748" />
  </g>
  
  <!-- 足 -->
  <g class="feet">
    <ellipse cx="85" cy="190" rx="12" ry="6" fill="#E08D3C" />
    <ellipse cx="115" cy="190" rx="12" ry="6" fill="#E08D3C" />
  </g>
</svg>
```

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
