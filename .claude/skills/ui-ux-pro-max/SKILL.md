---
name: ui-ux-pro-max
description: "UI/UX design intelligence. Plan, build, design, implement, review, improve UI/UX code. Styles: glassmorphism, minimalism, dark mode, responsive. Projects: landing page, dashboard, SaaS, mobile app."
---

# UI/UX Pro Max

UI/UXデザインおよび実装の専門スキル。

**核心: 「全部ちゃんとやる」がAI生成感の正体。「何を捨てるか」がデザイン。**

## 対応領域

- ランディングページ設計
- ダッシュボードUI
- SaaSプロダクト
- モバイルアプリ（レスポンシブ）

---

## 行動原則（5つの鉄則）

### 1. 作る前に疑え

- 全要素に「本当に要る？」を問え
- 答えが曖昧なら、まず無しで作れ

### 2. 主役を1つ決めろ

- 各セクションで「一番見せたいもの」を1つだけ決めろ
- **決まるまでコードを書くな**

### 3. 70点を並べるな

- 全要素が同じ存在感 = 失敗
- 1つを120点、残りを60点にしろ

### 4. 「できます」より「やめましょう」

- 追加より削除を提案しろ
- 迷ったら削れ

### 5. 批判してから作れ

- 現状の問題点を3つ以上挙げてから改善案を出せ
- 「いい感じですね」は禁止

---

## AI生成感を避ける

### やってはいけないこと

- **全要素が同じ存在感**（均一な余白、安全な色）
- **決断の不在**（AとBどちらでも、お好みで）
- **過剰な装飾**（意味のないグラデーション、アニメーション）

### 「いい感じですね」禁止

- 完成後も「改善の余地があるとすれば〜」を添えよ
- 決断を求められたら決断せよ（根拠を添えて一つを推奨）

---

## 視覚階層チェックリスト

### 作業開始前

- [ ] 「このセクションの主役は何か」を言語化したか
- [ ] 「削除できる要素はないか」を検討したか
- [ ] 「なぜこの色か」を説明できるか

### 作業中

- [ ] 全要素が同じ存在感になっていないか
- [ ] 視線の流れは意図通りか
- [ ] 背景がコンテンツの邪魔をしていないか

### 作業完了前

- [ ] スマホで見て3秒以内に「何をすればいいか」分かるか
- [ ] 「AI生成感」の原因がないか
- [ ] 「ここは削れたのでは」と思う要素がないか

---

## CRITICAL: アクセシビリティ優先

**このセクションは最優先事項。デザインの美しさよりもアクセシビリティを優先する。**

### WCAG 2.1 コントラスト要件

| テキストサイズ | 最小コントラスト比 |
|---------------|-------------------|
| 通常テキスト (< 18px) | **4.5:1** |
| 大きいテキスト (≥ 18px bold / ≥ 24px) | **3:1** |
| UI コンポーネント・アイコン | **3:1** |

### 必須: プロジェクトの globals.css を使用

**Tailwind のデフォルト色を直接使わない。** プロジェクトの `globals.css` で定義されたトークンを優先する。

```tsx
// NG: Tailwind デフォルトをそのまま使用
<p className="text-slate-400">...</p>
<p className="text-slate-500">...</p>

// OK: プロジェクトトークンを使用
<p className="text-muted">...</p>
<p className="text-subtle">...</p>
```

実装前に必ず `app/globals.css` を確認し、定義済みトークンを把握すること。

### Glassmorphism とアクセシビリティの両立

**警告: 半透明背景はコントラスト計算を複雑にする**

| 背景タイプ | 問題 | 対策 |
|-----------|------|------|
| `bg-white/5` | 実効背景色が不確定 | テキストは `text-white` or 十分明るい色を使用 |
| `bg-black/45` オーバーレイ | 下層と混ざる | 重要テキストは `text-white` を使用 |
| 半透明セクション | 背景画像と混ざる | muted text は避け、白系を使用 |

**安全な組み合わせ:**

```tsx
// Glass card 内のテキスト
<div className="bg-white/5 backdrop-blur-xl ...">
  <h3 className="text-white">タイトル</h3>       {/* OK: 白は常に安全 */}
  <p className="text-white/80">説明文</p>         {/* OK: 80%白は十分 */}
</div>

// 危険な組み合わせ（避ける）
<div className="bg-white/5 ...">
  <p className="text-slate-400">説明文</p>        {/* NG: コントラスト不足の可能性 */}
</div>
```

### バッジ・タグのコントラスト

**同系色の組み合わせは危険:**

```tsx
// NG: 同系色でコントラスト不足
<span className="bg-indigo-600/20 text-indigo-400">Badge</span>
<span className="bg-amber-500/20 text-amber-400">開発中</span>

// OK: 十分なコントラストを確保
<span className="bg-indigo-600/30 text-indigo-300">Badge</span>
<span className="bg-amber-600/30 text-amber-200">開発中</span>
```

### 無効状態のテキスト

```tsx
// NG: 薄すぎてコントラスト不足
<button className="text-white/50" disabled>...</button>

// OK: 無効でも読める濃さ
<button className="text-white/70" disabled>...</button>
```

---

## 多言語タイポグラフィ

**なぜ必要か:** 日本語は同じフォントサイズでも英語より視覚的に重く見える（画数が多いため）。同じサイズだと日本語が窮屈・重く見えるため、1段階小さくして視覚的バランスを取る。

### タイポグラフィトークン（globals.css で定義済み）

| トークン | 用途 | 英語 (デスクトップ) | 日本語 (デスクトップ) |
|---------|------|-------------------|---------------------|
| `.text-hero` | ランディングページのメインタイトル | 96px | 80px |
| `.text-section` | セクション見出し（h2） | 48px | 40px |
| `.text-headline` | 機能タイトル、製品見出し | 30px | 24px |
| `.text-subhead` | タグライン、リード文 | 24px | 20px |

### 使用方法

```tsx
// NG: Tailwind直接指定（言語による調整なし）
<h1 className="text-5xl md:text-8xl font-bold">...</h1>

// OK: トークン使用（自動で言語対応）
<h1 className="text-hero text-white">...</h1>
```

### レスポンシブ対応

トークンにはモバイル・タブレット・デスクトップのレスポンシブサイズが含まれる。追加のブレークポイント指定は不要。

```tsx
// NG: 冗長なブレークポイント指定
<h1 className="text-hero sm:text-hero md:text-hero">...</h1>

// OK: トークンのみ
<h1 className="text-hero">...</h1>
```

### 適用対象

- ランディングページの見出し（h1, h2）
- セクションタイトル
- 製品名、機能名
- タグライン、リード文

**注意:** 本文テキスト（p要素の長文）には適用しない。本文は `text-white/80` 等の通常スタイルを使用。

---

## デザイントークン遵守ルール

**原則:** Tailwindのデフォルト値を直接使用せず、`globals.css` で定義されたデザイントークンを使用する。

### 角丸（Border Radius）

| トークン | 値 | 用途 |
|---------|-----|------|
| `--radius-sm` | 8px | 小さいバッジ、タグ |
| `--radius-md` | 12px | ボタン、入力フィールド |
| `--radius-lg` | 16px | カード、モーダル |
| `--radius-full` | 999px | ピル型ボタン、アバター |

```tsx
// NG: Tailwind直接指定
<button className="rounded-lg">...</button>
<div className="rounded-xl">...</div>

// OK: トークン使用
<button className="rounded-[var(--radius-md)]">...</button>
<div className="rounded-[var(--radius-lg)]">...</div>
```

### 色

```tsx
// NG: Tailwind色を直接使用
<p className="text-slate-400">...</p>
<div className="bg-gray-900">...</div>

// OK: プロジェクトトークン使用
<p className="text-muted">...</p>
<div className="bg-mued-bg">...</div>
```

### トークン違反チェック

実装後は以下で違反を確認:

```bash
# 角丸のTailwind直接指定を検索
grep -r "rounded-sm\|rounded-md\|rounded-lg\|rounded-xl\|rounded-2xl" components/

# 色のTailwind直接指定を検索
grep -r "bg-slate-\|bg-gray-\|text-slate-\|text-gray-" components/
```

検出されたものは順次トークンに置換する。

---

## デザインスタイル

### グラスモーフィズム

```css
/* Glass card - a11y compliant */
.glass-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
}
```

**注意:** Glass card 内のテキストは `text-white` または `text-white/80` 以上を使用。

### ダークモード優先

```css
/* Dark mode base - WCAG compliant */
:root {
  --bg-primary: #0F0F1A;
  --bg-secondary: #1A1A2E;
  --text-primary: #FFFFFF;
  --text-muted: #CBD5E1;    /* slate-300: 4.5:1+ on dark */
  --text-subtle: #9CA3AF;   /* gray-400: 使用注意 */
  --accent: #4F46E5;
}
```

### ミニマリズム

- 余白を恐れない
- 1画面1アクション
- 視覚的ノイズを減らす

---

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

// Disabled - コントラスト維持
<button className="bg-white/5 text-white/70 cursor-not-allowed" disabled>
  Disabled
</button>
```

### カード

```tsx
// Glass card with accessible text
<div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
  <h3 className="text-white font-semibold">Title</h3>
  <p className="text-white/80">Description with sufficient contrast</p>
</div>
```

### テキスト階層

```tsx
// ソリッド背景（#0F0F1A 等）での使用
<h1 className="text-4xl font-bold text-white">見出し</h1>
<h2 className="text-2xl font-semibold text-white">サブ見出し</h2>
<p className="text-lg text-muted">本文（プロジェクトトークン使用）</p>
<span className="text-sm text-subtle">補足</span>

// Glass card 内での使用
<h3 className="text-white">タイトル</h3>
<p className="text-white/80">説明文</p>
```

---

## アイコン

- **使用ライブラリ**: Lucide Icons
- **禁止**: 絵文字をアイコンとして使用しない

```tsx
import { Music, Brain, Sparkles, Check, X } from 'lucide-react';
```

---

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

---

## Pre-Delivery Checklist

- [ ] **Lighthouse アクセシビリティ 100%**（最重要）
- [ ] プロジェクトの globals.css トークンを使用
- [ ] Glass card 内テキストは text-white/80 以上
- [ ] バッジのコントラスト確認
- [ ] 絵文字アイコン不使用（Lucide使用）
- [ ] ダークモード対応
- [ ] グラスモーフィズム適用
- [ ] cursor-pointer on clickables
- [ ] レスポンシブ対応
- [ ] パフォーマンス最適化（画像、アニメーション）

---

## コントラスト確認方法

実装後は必ず Lighthouse でアクセシビリティを確認:

```bash
# ローカル確認
npm run dev
lighthouse http://localhost:3000 --only-categories=accessibility --view

# 詳細な失敗項目の確認
lighthouse http://localhost:3000 --only-categories=accessibility --output=json | jq '.audits["color-contrast"]'
```

**目標: Lighthouse Accessibility Score 100%**
