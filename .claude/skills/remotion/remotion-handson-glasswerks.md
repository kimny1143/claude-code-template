# Remotion × Claude Code ハンズオン
## glasswerks / MUEDnote / Hoo 向けカスタムガイド

このハンズオンでは、Claude CodeでRemotionスキルを活用し、MUEDnoteのプロモーション動画やHooのキャラクターアニメーションを制作するフローを学びます。

---

## 目次

1. [環境セットアップ](#1-環境セットアップ)
2. [Remotion公式スキルのインストール](#2-remotion公式スキルのインストール)
3. [基本的な動画プロジェクト作成](#3-基本的な動画プロジェクト作成)
4. [glasswerks用カスタムスキル作成](#4-glasswerks用カスタムスキル作成)
5. [実践：Hooアニメーション制作](#5-実践hooアニメーション制作)
6. [実践：MUEDnoteプロモ動画制作](#6-実践muednoteプロモ動画制作)
7. [応用：@remotion/player でアプリ内埋め込み](#7-応用remotionplayer-でアプリ内埋め込み)

---

## 1. 環境セットアップ

### 前提条件

```bash
# Node.js 18以上
node -v

# Claude Code インストール済み
claude --version
```

### 作業ディレクトリの準備

```bash
mkdir ~/glasswerks-videos
cd ~/glasswerks-videos
```

---

## 2. Remotion公式スキルのインストール

### Claude Code内でスキルをインストール

```bash
# Claude Codeを起動
claude

# Remotion公式スキルをインストール
/plugin marketplace add remotion-dev/skills
```

または、npxを使用：

```bash
npx add-skill remotion-dev/skills -a claude-code -g
```

### インストール確認

```bash
# スキルが認識されているか確認
ls ~/.claude/skills/
```

### 補足：他の有用なスキルも追加

```bash
# Vercelのフロントエンドベストプラクティス
npx add-skill vercel-labs/agent-skills --skill frontend-design -a claude-code -g
```

---

## 3. 基本的な動画プロジェクト作成

### Claude Codeでプロジェクト初期化

Claude Codeを起動して以下のプロンプトを実行：

```
Remotionで新しい動画プロジェクトを作成して。
プロジェクト名: muednote-promo
```

Claude Codeが自動的に以下を実行：

```bash
npx create-video@latest muednote-promo
cd muednote-promo
```

### プロジェクト構造の確認

```
muednote-promo/
├── src/
│   ├── Root.tsx           # コンポジション登録
│   ├── Composition.tsx    # メインコンポジション
│   └── ...
├── public/                # 静的アセット
├── remotion.config.ts
└── package.json
```

### プレビュー起動

```bash
npx remotion studio
```

ブラウザで `http://localhost:3000` が開き、リアルタイムプレビューが可能。

---

## 4. glasswerks用カスタムスキル作成

Remotion公式スキルだけでは足りない「glasswerks固有のニーズ」をカスタムスキルとして作成します。

### 4.1 スキルディレクトリ作成

```bash
mkdir -p ~/.claude/skills/glasswerks-video
cd ~/.claude/skills/glasswerks-video
```

### 4.2 SKILL.md 作成

以下の内容で `SKILL.md` を作成：

```markdown
---
name: glasswerks-video
description: |
  glasswerks専用の動画制作スキル。MUEDnoteプロモーション、Hooキャラクターアニメーション、
  LP用動画、アプリ内チュートリアル動画の制作に使用。
  トリガー: "プロモ動画", "Hooアニメーション", "MUEDnote動画", "glasswerks動画"
---

# glasswerks Video Skill

## ブランドガイドライン

### カラーパレット
- Primary: #2D3748 (ダークグレー)
- Accent: #F6AD55 (オレンジ - Hooの色)
- Background: #1A202C (ダークBG)
- Text: #E2E8F0 (ライトグレー)

### タイポグラフィ
- 見出し: Noto Sans JP Bold
- 本文: Noto Sans JP Regular
- コード: JetBrains Mono

### Hooキャラクター仕様
- キャッチフレーズ: "ほほう (Ho Hoo)"
- 性格: 知的で親しみやすい、音楽制作のガイド役
- アニメーションスタイル: 
  - 首を傾げる動作（興味を示す）
  - 羽をパタパタ（喜び/説明時）
  - 目を細める（納得/承認）

## 動画テンプレート

### 1. プロモーション動画（30秒）
```
シーン構成:
1. Hook (0-5秒): 問題提起 + Hooが登場
2. Problem (5-10秒): 音楽制作の課題を可視化
3. Solution (10-20秒): MUEDnoteの機能デモ
4. CTA (20-30秒): ダウンロードを促すHoo
```

### 2. 機能紹介動画（15秒）
```
シーン構成:
1. 機能名タイトル (0-3秒)
2. 実演デモ (3-12秒)
3. Hooのコメント "ほほう" (12-15秒)
```

### 3. チュートリアル動画（60秒）
```
シーン構成:
1. 導入: Hooが挨拶 (0-5秒)
2. ステップ1-3: 操作説明 (5-50秒)
3. まとめ: Hooが締めくくり (50-60秒)
```

## アニメーションパターン

### フェードイン + スライド
```typescript
const opacity = interpolate(frame, [0, 20], [0, 1], {
  extrapolateRight: 'clamp',
});
const translateY = interpolate(frame, [0, 20], [20, 0], {
  extrapolateRight: 'clamp',
});
```

### バウンス効果（Hooの動き用）
```typescript
const bounce = spring({
  frame,
  fps,
  config: {
    damping: 10,
    stiffness: 100,
    mass: 0.5,
  },
});
```

### テキストタイプライター
```typescript
const text = "ほほう、これは便利ですね";
const charsToShow = Math.floor(interpolate(frame, [0, 60], [0, text.length]));
const displayText = text.slice(0, charsToShow);
```

## ファイル構成推奨

```
src/
├── compositions/
│   ├── PromoVideo.tsx      # 30秒プロモ
│   ├── FeatureDemo.tsx     # 機能紹介
│   └── Tutorial.tsx        # チュートリアル
├── components/
│   ├── Hoo/
│   │   ├── HooCharacter.tsx
│   │   ├── HooTalking.tsx
│   │   └── HooAnimations.ts
│   ├── Text/
│   │   ├── TitleText.tsx
│   │   └── TypewriterText.tsx
│   └── Transitions/
│       ├── FadeSlide.tsx
│       └── ScaleIn.tsx
├── styles/
│   └── theme.ts            # ブランドカラー定義
└── assets/
    ├── hoo-base.svg
    ├── muednote-logo.svg
    └── fonts/
```

## 使用例

### Claude Codeへの指示例

```
MUEDnoteの30秒プロモ動画を作って。
- Hook: "音楽制作、記録してる？"
- Problem: アイデアが消えていく様子
- Solution: MUEDnoteで簡単ログ
- CTA: "今すぐダウンロード"

Hooキャラクターを要所で登場させて。
```

```
Hooが「ほほう」と言いながら首を傾げるアニメーションコンポーネントを作って。
2秒のループアニメーションで。
```

## レンダリング設定

### 標準設定
- 解像度: 1920x1080 (16:9)
- FPS: 30
- コーデック: h264

### SNS向け設定
- Twitter/X: 1280x720, 30fps, 最大140秒
- Instagram Reels: 1080x1920 (9:16), 30fps
- TikTok: 1080x1920 (9:16), 30fps

### レンダリングコマンド
```bash
# 標準MP4
npx remotion render src/index.ts PromoVideo out/promo.mp4

# 高品質
npx remotion render src/index.ts PromoVideo out/promo-hq.mp4 --quality=100

# GIF（短尺用）
npx remotion render src/index.ts FeatureDemo out/feature.gif --codec=gif
```
```

### 4.3 アセットディレクトリの準備

```bash
mkdir -p ~/.claude/skills/glasswerks-video/assets
mkdir -p ~/.claude/skills/glasswerks-video/references
```

### 4.4 references/hoo-animation.md 作成

詳細なHooアニメーションパターンを別ファイルに：

```markdown
# Hooアニメーション詳細リファレンス

## 基本ポーズ

### 待機状態
- 体は正面向き
- 目は半開き（落ち着いた表情）
- 軽い呼吸アニメーション（上下2px、2秒周期）

### 興味を示す
- 首を右に15度傾ける
- 目を見開く
- "ほほう" のセリフ

### 説明モード
- 羽を広げる
- 目線は視聴者（カメラ目線）
- 口パクアニメーション

### 喜び
- 羽をパタパタ（上下に振る）
- 目を細める（笑顔）
- 軽くジャンプ（上下5px）

## アニメーションコード例

### 呼吸アニメーション
```typescript
export const breathingAnimation = (frame: number, fps: number) => {
  const breathCycle = Math.sin((frame / fps) * Math.PI) * 2;
  return {
    translateY: breathCycle,
  };
};
```

### 首傾げ
```typescript
export const headTilt = (frame: number, fps: number, startFrame: number) => {
  const progress = spring({
    frame: frame - startFrame,
    fps,
    config: { damping: 15, stiffness: 80 },
  });
  return {
    rotate: `${progress * 15}deg`,
  };
};
```

### 羽パタパタ
```typescript
export const wingFlap = (frame: number, fps: number) => {
  const flapSpeed = 8; // 1秒に8回
  const angle = Math.sin((frame / fps) * Math.PI * flapSpeed) * 20;
  return {
    leftWing: -angle,
    rightWing: angle,
  };
};
```
```

---

## 5. 実践：Hooアニメーション制作

### Claude Codeでの実行

```bash
cd ~/glasswerks-videos/muednote-promo
claude
```

### プロンプト例

```
Hooキャラクターのアニメーションコンポーネントを作成して。

要件:
- SVGベースのフクロウキャラクター
- 待機、興味、喜びの3つの状態
- propsで状態を切り替え可能
- glasswerks-videoスキルのブランドカラーを使用

src/components/Hoo/HooCharacter.tsx に配置して。
```

Claude Codeが生成するコード例：

```typescript
// src/components/Hoo/HooCharacter.tsx
import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate, spring } from 'remotion';

type HooState = 'idle' | 'curious' | 'happy';

interface HooProps {
  state?: HooState;
  scale?: number;
}

export const HooCharacter: React.FC<HooProps> = ({ 
  state = 'idle', 
  scale = 1 
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // 呼吸アニメーション
  const breathe = Math.sin((frame / fps) * Math.PI) * 2;

  // 状態別アニメーション
  const getStateAnimation = () => {
    switch (state) {
      case 'curious':
        return {
          headRotate: spring({ frame, fps, config: { damping: 15 } }) * 15,
          eyeScale: 1.2,
        };
      case 'happy':
        return {
          headRotate: 0,
          eyeScale: 0.8,
          wingFlap: Math.sin((frame / fps) * Math.PI * 8) * 20,
        };
      default:
        return {
          headRotate: 0,
          eyeScale: 1,
        };
    }
  };

  const anim = getStateAnimation();

  return (
    <div
      style={{
        transform: `scale(${scale}) translateY(${breathe}px)`,
      }}
    >
      <svg viewBox="0 0 200 200" width={200} height={200}>
        {/* Body */}
        <ellipse cx="100" cy="120" rx="60" ry="70" fill="#F6AD55" />
        
        {/* Head */}
        <g style={{ transform: `rotate(${anim.headRotate}deg)`, transformOrigin: '100px 80px' }}>
          <circle cx="100" cy="60" r="50" fill="#F6AD55" />
          
          {/* Eyes */}
          <ellipse 
            cx="80" cy="55" 
            rx={12 * anim.eyeScale} ry={15 * anim.eyeScale} 
            fill="#2D3748" 
          />
          <ellipse 
            cx="120" cy="55" 
            rx={12 * anim.eyeScale} ry={15 * anim.eyeScale} 
            fill="#2D3748" 
          />
          
          {/* Eye highlights */}
          <circle cx="85" cy="50" r="4" fill="white" />
          <circle cx="125" cy="50" r="4" fill="white" />
          
          {/* Beak */}
          <polygon points="100,65 90,80 110,80" fill="#2D3748" />
        </g>
        
        {/* Wings */}
        <ellipse 
          cx="45" cy="110" rx="20" ry="35" fill="#E08D3C"
          style={{ transform: `rotate(${anim.wingFlap || 0}deg)`, transformOrigin: '60px 110px' }}
        />
        <ellipse 
          cx="155" cy="110" rx="20" ry="35" fill="#E08D3C"
          style={{ transform: `rotate(${-(anim.wingFlap || 0)}deg)`, transformOrigin: '140px 110px' }}
        />
      </svg>
    </div>
  );
};
```

### プレビュー確認

```bash
npx remotion studio
```

---

## 6. 実践：MUEDnoteプロモ動画制作

### Claude Codeへの指示

```
MUEDnoteの30秒プロモーション動画を作成して。

構成:
1. Hook (0-5秒): 
   - 暗い背景に「音楽制作、記録してる？」のテキスト
   - Hooが画面右下から登場

2. Problem (5-12秒):
   - アイデアのメモが消えていくアニメーション
   - Hooが心配そうな表情

3. Solution (12-25秒):
   - MUEDnoteのUI画面を表示
   - 機能ハイライト（ログ記録、タグ付け、検索）
   - Hooが各機能を指し示す

4. CTA (25-30秒):
   - "今すぐダウンロード" + App Storeバッジ
   - Hooが「ほほう！」と喜ぶ

glasswerks-videoスキルのブランドガイドラインに従って。
src/compositions/PromoVideo.tsx に作成。
```

### 生成されるプロジェクト構造

```
src/
├── compositions/
│   └── PromoVideo.tsx
├── components/
│   ├── Hoo/
│   │   └── HooCharacter.tsx
│   ├── scenes/
│   │   ├── HookScene.tsx
│   │   ├── ProblemScene.tsx
│   │   ├── SolutionScene.tsx
│   │   └── CTAScene.tsx
│   └── ui/
│       ├── AnimatedText.tsx
│       └── AppStoreBadge.tsx
└── styles/
    └── theme.ts
```

### レンダリング

```bash
# プレビュー確認後
npx remotion render src/index.ts PromoVideo out/muednote-promo.mp4

# 高品質版
npx remotion render src/index.ts PromoVideo out/muednote-promo-hq.mp4 \
  --codec=h264 \
  --quality=100
```

---

## 7. 応用：@remotion/player でアプリ内埋め込み

MUEDnoteアプリ内でチュートリアルアニメーションを再生する場合。

### インストール

```bash
npm install @remotion/player
```

### React/Next.jsでの使用

```typescript
// app/components/TutorialPlayer.tsx
'use client';

import { Player } from '@remotion/player';
import { HooTutorial } from '@/remotion/compositions/HooTutorial';

export const TutorialPlayer = () => {
  return (
    <Player
      component={HooTutorial}
      durationInFrames={300} // 10秒 @ 30fps
      fps={30}
      compositionWidth={1920}
      compositionHeight={1080}
      style={{
        width: '100%',
        maxWidth: 800,
      }}
      controls
      autoPlay
      loop
    />
  );
};
```

### Hooガイドの動的制御

```typescript
// propsで動的にコンテンツを変更
<Player
  component={HooTutorial}
  inputProps={{
    message: "ログを記録してみましょう",
    hooState: "curious",
    stepNumber: 1,
  }}
  // ...
/>
```

---

## チートシート

### よく使うClaude Codeプロンプト

| 目的 | プロンプト |
|------|-----------|
| 新規プロジェクト | `Remotionで新しい動画プロジェクトを作成して。プロジェクト名: xxx` |
| シーン追加 | `src/compositions/に新しいシーンを追加して。内容: xxx` |
| Hooアニメーション | `Hooが「ほほう」と言いながら首を傾げるアニメーションを作って` |
| プレビュー | `Remotion Studioを起動して` |
| レンダリング | `PromoVideoコンポジションをMP4でレンダリングして` |
| SNS用リサイズ | `縦型動画（1080x1920）バージョンを作成して` |

### よく使うコマンド

```bash
# プレビュー
npx remotion studio

# 静止画出力（確認用）
npx remotion still src/index.ts PromoVideo --frame=150 --output=preview.png

# MP4レンダリング
npx remotion render src/index.ts PromoVideo out/video.mp4

# GIF出力
npx remotion render src/index.ts ShortClip out/clip.gif --codec=gif

# 縦型動画
npx remotion render src/index.ts VerticalPromo out/vertical.mp4 \
  --height=1920 --width=1080
```

---

## トラブルシューティング

### スキルが認識されない

```bash
# スキルディレクトリを確認
ls -la ~/.claude/skills/

# Claude Codeを再起動
claude --restart
```

### Remotion Studioが起動しない

```bash
# 依存関係を再インストール
rm -rf node_modules package-lock.json
npm install
```

### レンダリングが遅い

```bash
# 並列処理を有効化
npx remotion render src/index.ts PromoVideo out/video.mp4 --concurrency=4
```

---

## 次のステップ

1. **Hooのキャラクターアセット作成**: Figma/Illustratorでベクターデータを作成し、`public/assets/`に配置
2. **音声同期**: Hooの口パクを音声に同期させる（`@remotion/media-utils`）
3. **Lambda連携**: 大量レンダリング用にAWS Lambda設定
4. **CI/CD**: GitHub Actionsで自動レンダリングパイプライン構築

---

## 参考リンク

- [Remotion公式ドキュメント](https://www.remotion.dev/docs/)
- [Remotion + AI ガイド](https://www.remotion.dev/docs/ai/)
- [remotion-dev/skills](https://github.com/remotion-dev/skills)
- [awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills)
