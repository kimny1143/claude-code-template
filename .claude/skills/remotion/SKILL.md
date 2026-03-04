---
name: remotion
description: |
  汎用Remotion動画制作スキル。プロモーション動画、マスコットアニメーション、
  LP用動画、チュートリアル動画、SNS短尺動画の制作に使用。
  トリガー: "プロモ動画", "アニメーション", "動画を作って", "Remotion",
  "動画コンテンツ", "ビデオ制作", "モーショングラフィックス",
  "LP動画", "チュートリアル動画", "OGP動画", "動画素材"
  Remotionを使ったReactベースの動画生成全般でこのスキルを使うこと。
  プロモーション映像やアニメーション素材の話が出たら積極的にこのスキルを参照すること。
---

# Remotion Video Skill

Reactで動画を生成する Remotion を使い、動画コンテンツを制作する汎用スキル。

## ブランド設定について

> **カラーパレット、フォント、マスコットキャラクターの仕様は、各プロジェクトの `CLAUDE.md` で定義すること。**
> このスキルにはブランド固有の情報を含めない。
> プロジェクト側に以下のようなセクションを用意する想定：
>
> ```markdown
> ## Video Branding
> - Primary: #XXXXXX
> - Accent: #XXXXXX
> - Background: #XXXXXX
> - Font Heading: ...
> - Font Body: ...
> - Mascot: （キャラ名、デザイン仕様、アニメーションパターン等）
> ```

## クイックスタート

```bash
# 1. プロジェクト初期化（スキル付属スクリプト）
bash <path-to-skill>/scripts/init-remotion.sh <project-name>

# 2. プレビュー
cd <project-name> && npx remotion studio

# 3. レンダリング
npx remotion render src/index.ts <CompositionId> out/video.mp4
```

### 手動セットアップ

```bash
# 新規作成
npx create-video@latest my-video

# 既存プロジェクトに追加（依存関係が複雑になるため別ディレクトリ推奨）
npm install remotion @remotion/cli @remotion/player
```

## 動画テンプレート

### 1. プロモーション動画（30秒）
```
0-5秒   : Hook — 問題提起 + キャッチーなビジュアル
5-10秒  : Problem — 課題の可視化
10-20秒 : Solution — プロダクトの世界観・機能デモ
20-28秒 : Social Proof — 数字 or ユーザーの声
28-30秒 : CTA — ロゴ + URL
```

コンポジション設定:
- 解像度: 1920x1080（16:9）
- FPS: 30
- 総フレーム数: 900

### 2. 機能紹介動画（15秒）
```
0-3秒   : 機能名タイトル（テキストアニメーション）
3-12秒  : 実演デモ（スクリーンキャプチャ or モック）
12-15秒 : 締めのメッセージ + 次のアクション誘導
```

コンポジション設定:
- 解像度: 1080x1080（1:1、SNS向け）or 1080x1920（9:16、リール向け）
- FPS: 30

### 3. チュートリアル動画（60秒）
```
0-5秒   : 導入 — タイトル + 挨拶
5-50秒  : ステップ1-3 — 操作説明（画面録画 + オーバーレイ）
50-58秒 : まとめ — 要点の振り返り
58-60秒 : CTA
```

### 4. SNS短尺動画（5-10秒）
```
0-2秒   : アイキャッチ（動き or テキスト）
2-8秒   : ワンポイント情報
8-10秒  : ロゴ + CTA
```

コンポジション設定:
- 解像度: 1080x1920（9:16）
- FPS: 30

## プロジェクト構成

```
my-video/
├── src/
│   ├── Root.tsx                    # コンポジション登録
│   ├── compositions/
│   │   ├── Promo.tsx               # 30秒プロモ
│   │   ├── FeatureIntro.tsx        # 15秒機能紹介
│   │   ├── Tutorial.tsx            # 60秒チュートリアル
│   │   └── SnsShort.tsx            # 5-10秒SNS
│   ├── components/
│   │   ├── Character/              # マスコット / キャラクター
│   │   │   ├── CharacterBase.tsx
│   │   │   ├── Expressions.tsx
│   │   │   └── Animations.tsx
│   │   ├── Typography/
│   │   │   ├── TitleReveal.tsx
│   │   │   └── SubtitleFade.tsx
│   │   ├── Transitions/
│   │   │   ├── WipeTransition.tsx
│   │   │   └── FadeTransition.tsx
│   │   └── Branding/
│   │       ├── Logo.tsx
│   │       └── CallToAction.tsx
│   └── styles/
│       └── theme.ts                # カラー・フォント定義
├── public/
│   ├── fonts/
│   ├── images/
│   └── audio/
├── remotion.config.ts
└── package.json
```

## 開発ルール

### コンポジション
- 1ファイル1コンポーネント
- アニメーションパラメータは props で外出し（後で調整しやすく）
- `<Sequence>` でシーンを時間管理

### アニメーション
- `interpolate()` でスムーズな値の補間
- `spring()` で自然な物理アニメーション
- キャラクターの動きは `spring({ damping: 12 })` ベースで統一感を出す

### 音声
- BGMは `/public/audio/` に配置
- `<Audio>` コンポーネントで同期再生

### テーマ（theme.ts テンプレート）
```typescript
export const theme = {
  colors: {
    primary: '#XXXXXX',       // メインカラー
    accent: '#XXXXXX',        // アクセントカラー
    background: '#XXXXXX',    // 背景色
    text: '#XXXXXX',          // テキスト色
    subAccent: '#XXXXXX',     // サブアクセント
  },
  fonts: {
    heading: 'Your Heading Font',
    body: 'Your Body Font',
    mono: 'JetBrains Mono',
  },
  animation: {
    characterSpring: { damping: 12, mass: 0.5 },
    textReveal: { damping: 15, mass: 0.8 },
    fadeIn: { durationInFrames: 15 },
  },
} as const;

export type Theme = typeof theme;
```

> プロジェクトの `CLAUDE.md` に定義したブランドカラー・フォントで上記プレースホルダーを埋めること。

## マスコットキャラクター汎用パターン

プロジェクトにマスコットキャラクターがある場合の汎用アニメーションパターン。
キャラクター名や見た目はプロジェクトごとに異なるため、ここではモーションパターンのみ定義する。

### 状態別アニメーション
| 状態 | 用途 | アニメーション |
|------|------|--------------|
| idle | 待機 | 軽い呼吸（上下2px、2秒周期） + まばたき |
| curious | 興味・説明 | 首を傾ける + 目を見開く |
| happy | 喜び・完了 | バウンス + 表情変化 |
| pointing | 指し示す | 体を向ける + 腕/羽を伸ばす |

### 登場・退場アニメーション
```typescript
// 登場: 画面外からspring付きスライドイン
const entrance = (
  frame: number, fps: number,
  from: 'left' | 'right' | 'bottom' = 'right'
) => {
  const progress = spring({ frame, fps, config: { damping: 12, stiffness: 80 } });
  const offsets = { left: { x: -300, y: 0 }, right: { x: 300, y: 0 }, bottom: { x: 0, y: 200 } };
  const dir = offsets[from];
  return {
    translateX: dir.x * (1 - progress),
    translateY: dir.y * (1 - progress),
    opacity: progress,
    scale: 0.5 + progress * 0.5,
  };
};
```

## レンダリング

```bash
# MP4（汎用）
npx remotion render src/index.ts Promo out/promo.mp4

# 高品質
npx remotion render src/index.ts Promo out/promo-hq.mp4 --codec=h264 --quality=100

# GIF（短尺・ループ用）
npx remotion render src/index.ts SnsShort out/short.gif --codec=gif

# SNS向け縦型（9:16）
npx remotion render src/index.ts VerticalComp out/vertical.mp4 --height=1920 --width=1080

# 一括レンダリング
bash <path-to-skill>/scripts/render-all.sh
```

### SNS別推奨設定
- Twitter/X: 1280x720, 30fps, 最大140秒
- Instagram Reels: 1080x1920 (9:16), 30fps
- TikTok: 1080x1920 (9:16), 30fps

## @remotion/player でアプリ内埋め込み

事前レンダリング不要でインタラクティブに再生できる。

```tsx
import { Player } from '@remotion/player';
import { FeatureIntro } from './compositions/FeatureIntro';

<Player
  component={FeatureIntro}
  durationInFrames={450}
  fps={30}
  compositionWidth={1080}
  compositionHeight={1080}
  style={{ width: '100%' }}
  controls
/>
```

### 動的 props で制御
```tsx
<Player
  component={Tutorial}
  inputProps={{
    message: "操作してみましょう",
    stepNumber: 1,
  }}
  durationInFrames={300}
  fps={30}
  compositionWidth={1920}
  compositionHeight={1080}
  controls
  autoPlay
  loop
/>
```

## ライセンス

Remotionは **3人以下の会社は無料**（商用利用OK）。
4人以上になった場合は Company License（$25/開発者/月）が必要。
詳細: https://www.remotion.dev/license

## 参考リソース

- Remotion公式ドキュメント: https://www.remotion.dev/docs
- Remotion + AI ガイド: https://www.remotion.dev/docs/ai/
- Remotion公式スキル: `npx add-skill remotion-dev/skills`
- アニメーションパターン集: `references/animation-patterns.md`
