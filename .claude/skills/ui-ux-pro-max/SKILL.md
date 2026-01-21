---
name: ui-ux-pro-max
description: "UI/UX design intelligence. Plan, build, design, implement, review, improve UI/UX code. Styles: glassmorphism, minimalism, dark mode, responsive. Projects: landing page, dashboard, SaaS, mobile app."
---

# UI/UX Pro Max

UI/UXデザインおよび実装の専門スキル。

## 対応領域

- ランディングページ設計
- ダッシュボードUI
- SaaSプロダクト
- モバイルアプリ（レスポンシブ）

## デザインスタイル

### グラスモーフィズム

```css
/* Glass card */
.glass-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
}
```

### ダークモード優先

```css
/* Dark mode base */
:root {
  --bg-primary: #0F0F1A;
  --bg-secondary: #1A1A2E;
  --text-primary: #FFFFFF;
  --text-muted: #94A3B8;
  --accent: #4F46E5;
}
```

### ミニマリズム

- 余白を恐れない
- 1画面1アクション
- 視覚的ノイズを減らす

## コンポーネント規約

### ボタン

```tsx
// Primary CTA
<button className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg transition-colors cursor-pointer">
  CTA
</button>

// Secondary
<button className="bg-white/10 hover:bg-white/20 text-white px-6 py-3 rounded-lg transition-colors cursor-pointer">
  Secondary
</button>
```

### カード

```tsx
// Glass card
<div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
  ...
</div>
```

### テキスト階層

```tsx
<h1 className="text-4xl font-bold text-white">見出し</h1>
<h2 className="text-2xl font-semibold text-white">サブ見出し</h2>
<p className="text-lg text-slate-400">本文</p>
<span className="text-sm text-slate-500">補足</span>
```

## アイコン

- **使用ライブラリ**: Lucide Icons
- **禁止**: 絵文字をアイコンとして使用しない

```tsx
import { Music, Brain, Sparkles, Check, X } from 'lucide-react';
```

## レスポンシブブレークポイント

```css
/* Mobile first */
/* sm: 640px */
/* md: 768px */
/* lg: 1024px */
/* xl: 1280px */
/* 2xl: 1536px */
```

検証すべき画面幅:
- 320px (最小モバイル)
- 768px (タブレット)
- 1024px (デスクトップ)
- 1440px (大画面)

## アクセシビリティ

- セマンティックHTML
- 適切なARIAラベル
- キーボードナビゲーション対応
- 十分なコントラスト比
- フォーカス状態の可視化

## Pre-Delivery Checklist

- [ ] 絵文字アイコン不使用（Lucide使用）
- [ ] ダークモード対応
- [ ] グラスモーフィズム適用
- [ ] cursor-pointer on clickables
- [ ] レスポンシブ対応
- [ ] アクセシビリティ確認
- [ ] パフォーマンス最適化（画像、アニメーション）
