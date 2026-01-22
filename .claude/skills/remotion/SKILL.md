---
name: remotion
description: |
  MUEDnote動画制作スキル。プロモーション動画、Hooキャラクターアニメーション、
  LP用動画、アプリ内チュートリアル動画の制作に使用。Remotionベース。
  トリガー: "プロモ動画", "Hooアニメーション", "MUEDnote動画",
  "動画を作って", "アニメーションを作成"
---

# MUEDnote Video Skill (Remotion)

Remotionを使用したMUEDnote動画制作スキル。

## 注意事項

このスキルは**新規Remotionプロジェクト作成時のテンプレート**。
mued_v2にはRemotionは未インストール。動画制作時は別ディレクトリで作業するか、
mued_v2にRemotionをセットアップすること。

### Remotionセットアップ（必要時）

```bash
# 別ディレクトリで新規作成
npx create-video@latest muednote-videos

# または mued_v2 に追加（推奨しない - 依存関係が複雑になる）
npm install remotion @remotion/cli @remotion/player
```

---

## ブランドガイドライン

### カラーパレット
```typescript
// src/styles/theme.ts
export const colors = {
  primary: '#2D3748',      // ダークグレー（メインUI）
  accent: '#6366F1',       // インディゴ（CTAボタン等）
  background: '#1A202C',   // ダークBG
  backgroundLight: '#2D3748',
  text: '#E2E8F0',         // ライトグレー（本文）
  textMuted: '#A0AEC0',    // ミュートテキスト
  hoo: '#FFFFFF',          // Hooは白ラインアート
  success: '#48BB78',      // 成功
  error: '#F56565',        // エラー
};
```

### タイポグラフィ
- 見出し: `Noto Sans JP Bold` / `font-weight: 700`
- 本文: `Noto Sans JP Regular` / `font-weight: 400`
- コード/数字: `JetBrains Mono`

### 動画設定デフォルト
- 解像度: 1920×1080 (16:9)
- FPS: 30
- コーデック: h264

---

## Hooキャラクター仕様

### 基本情報
- 名前: Hoo（フー）
- キャッチフレーズ: "ほほう (Ho Hoo)"
- 役割: MUEDnoteのAIアシスタント、マーケティングマスコット
- **スタイル**: 白いラインアート（モノトーン）
- **ベースカラー**: `#FFFFFF`（白ストローク、塗りなし）
- **参照**: `/public/logo.png`

### 表情・状態
| 状態 | 用途 | アニメーション |
|------|------|--------------|
| idle | 待機 | 呼吸（上下2px、2秒周期） |
| curious | 興味・説明 | 首を右に15度傾ける、目を見開く |
| happy | 喜び・完了 | 羽パタパタ、目を細める |
| thinking | 考え中 | 目を上に向ける、首を左に傾ける |
| pointing | 指し示す | 右羽を前に出す |

### アニメーションコード

```typescript
// 呼吸（常時）
const breathe = Math.sin((frame / fps) * Math.PI) * 2;

// 首傾げ（curious時）
const tilt = spring({
  frame: frame - startFrame,
  fps,
  config: { damping: 15, stiffness: 80 },
}) * 15;

// 羽パタパタ（happy時）
const flapAngle = Math.sin((frame / fps) * Math.PI * 8) * 20;
```

**詳細**: `hoo-animation.md` 参照

---

## 動画テンプレート

### 1. プロモーション動画（30秒）

```
構成:
├── Hook (0-5秒)
│   └── 問題提起テキスト + Hooが右下から登場
├── Problem (5-12秒)
│   └── 課題の可視化 + Hoo心配顔
├── Solution (12-25秒)
│   └── MUEDnote機能デモ + Hooが説明
└── CTA (25-30秒)
    └── ダウンロード促し + Hoo喜び
```

**指示例:**
```
MUEDnoteの30秒プロモ動画を作成。
Hook: "音楽制作、記録してる？"
Problem: アイデアが消えていく様子
Solution: MUEDnoteの3つの機能をハイライト
CTA: App Storeへ誘導
Hooを各シーンで使用。
```

### 2. 機能紹介動画（15秒）

```
構成:
├── タイトル (0-3秒): 機能名 + アイコン
├── デモ (3-12秒): 操作画面のアニメーション
└── 締め (12-15秒): Hoo「ほほう」+ ロゴ
```

### 3. チュートリアル動画（60秒）

```
構成:
├── 導入 (0-5秒): Hoo挨拶「こんにちは！」
├── ステップ1 (5-20秒): 最初の操作説明
├── ステップ2 (20-35秒): 次の操作説明
├── ステップ3 (35-50秒): 最後の操作説明
└── まとめ (50-60秒): Hoo「ほほう、簡単でしょう？」
```

---

## 推奨プロジェクト構造

```
muednote-videos/           # 別ディレクトリ推奨
├── src/
│   ├── Root.tsx
│   ├── compositions/
│   │   ├── PromoVideo.tsx
│   │   ├── FeatureDemo.tsx
│   │   └── Tutorial.tsx
│   ├── components/
│   │   ├── Hoo/
│   │   │   ├── HooCharacter.tsx
│   │   │   ├── HooExpressions.tsx
│   │   │   └── animations.ts
│   │   ├── Text/
│   │   │   ├── TitleText.tsx
│   │   │   ├── TypewriterText.tsx
│   │   │   └── HighlightText.tsx
│   │   ├── Transitions/
│   │   │   ├── FadeSlide.tsx
│   │   │   ├── ScaleIn.tsx
│   │   │   └── WipeTransition.tsx
│   │   └── UI/
│   │       ├── PhoneMockup.tsx
│   │       ├── AppStoreBadge.tsx
│   │       └── Logo.tsx
│   ├── styles/
│   │   └── theme.ts
│   └── utils/
│       └── animations.ts
├── public/
│   └── assets/           # ロゴ、スクリーンショット等
└── out/                  # レンダリング出力
```

---

## よく使うアニメーションパターン

### フェードイン + スライドアップ
```typescript
const FadeSlideIn: React.FC<{children: React.ReactNode; delay?: number}> = ({
  children,
  delay = 0,
}) => {
  const frame = useCurrentFrame();
  const adjustedFrame = frame - delay;

  const opacity = interpolate(adjustedFrame, [0, 20], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const translateY = interpolate(adjustedFrame, [0, 20], [30, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div style={{ opacity, transform: `translateY(${translateY}px)` }}>
      {children}
    </div>
  );
};
```

### タイプライター効果
```typescript
const TypewriterText: React.FC<{text: string; startFrame?: number}> = ({
  text,
  startFrame = 0,
}) => {
  const frame = useCurrentFrame();
  const adjustedFrame = frame - startFrame;

  const charsToShow = Math.floor(
    interpolate(adjustedFrame, [0, text.length * 3], [0, text.length], {
      extrapolateRight: 'clamp',
    })
  );

  return <span>{text.slice(0, charsToShow)}</span>;
};
```

### スケールバウンス（登場演出）
```typescript
const scaleValue = spring({
  frame: frame - delay,
  fps,
  config: {
    damping: 10,
    stiffness: 100,
    mass: 0.5,
  },
});
```

---

## レンダリング

### 標準（YouTube/LP用）
```bash
npx remotion render src/index.ts CompositionName out/video.mp4
```

### 高品質
```bash
npx remotion render src/index.ts CompositionName out/video-hq.mp4 \
  --codec=h264 \
  --quality=100
```

### SNS向け縦型
```bash
# Instagram Reels / TikTok
npx remotion render src/index.ts VerticalComp out/vertical.mp4 \
  --height=1920 --width=1080
```

### GIF（短尺・ループ用）
```bash
npx remotion render src/index.ts ShortLoop out/loop.gif \
  --codec=gif
```

---

## 関連ファイル

- `hoo-animation.md` - Hooアニメーション詳細仕様
- `remotion-handson-glasswerks.md` - Remotionハンズオンメモ
