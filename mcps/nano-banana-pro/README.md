# nano-banana-pro (mcp-image)

Google Gemini の画像生成機能を Claude Code から使える MCP サーバー。
テキストから画像生成、既存画像の編集、プロンプト自動最適化に対応。

推奨実装: [shinpr/mcp-image](https://github.com/shinpr/mcp-image)（Nano Banana 2 / Pro 両対応、プロンプト最適化付き）

## セットアップ

### 1. Gemini API キーの取得

1. [Google AI Studio](https://aistudio.google.com/apikey) にアクセス
2. API キーを作成（無料枠: 500リクエスト/日）

### 2. プロジェクトの `.env.local` に API キーを追加

```bash
# .env.local
GEMINI_API_KEY=your_api_key
IMAGE_OUTPUT_DIR=/path/to/output/images
IMAGE_QUALITY=fast
```

### 3. Claude Code に MCP サーバーを登録

**方法 A: ラッパースクリプト経由（推奨）**

プロジェクトの `.env.local` から自動的に API キーを読み込む：

```bash
claude mcp add mcp-image -s user \
  -- /path/to/claude-code-template/mcps/nano-banana-pro/launch.sh
```

`launch.sh` はプロジェクトの `.env.local` → `.env` の順に `GEMINI_API_KEY` を探す。
プロジェクトごとに異なる API キーや設定を使い分けられる。

**方法 B: 直接指定（全プロジェクト共通の場合）**

```bash
claude mcp add mcp-image -s user \
  -e GEMINI_API_KEY=your_api_key \
  -e IMAGE_OUTPUT_DIR=/path/to/output/images \
  -- npx -y mcp-image
```

### 4. 動作確認

Claude Code で：

```
> テスト画像を生成して。青い山と湖の風景。
```

画像が `IMAGE_OUTPUT_DIR` に保存されれば OK。

## ツール

| ツール | 用途 |
|--------|------|
| `generate_image` | テキストから画像生成（編集・スタイル転写も対応） |

### 主要パラメータ

| パラメータ | 説明 | デフォルト |
|-----------|------|-----------|
| `prompt` | 画像の説明テキスト（必須） | — |
| `quality` | `fast` / `balanced` / `quality` | `fast` |
| `aspectRatio` | `1:1`, `3:4`, `4:3`, `9:16`, `16:9`, `21:9` 等 | `1:1` |
| `imageSize` | `1K`, `2K`, `4K` | 標準 |
| `inputImagePath` | 編集元画像の絶対パス | — |
| `fileName` | 出力ファイル名（**拡張子なしで指定する。`.png` は自動付与されない — 既知の不具合**） | 自動生成 |
| `purpose` | 用途（例: "blog header", "social media"） | — |

## 品質プリセット

| プリセット | モデル | 用途 | 速度 |
|-----------|--------|------|------|
| `fast` | Nano Banana 2 (Gemini 3.1 Flash) | ドラフト、反復作業 | ~30-40秒 |
| `balanced` | Nano Banana 2 + Thinking | 本番用、バランス重視 | 中程度 |
| `quality` | Nano Banana Pro (Gemini 3 Pro) | 最終成果物、最高品質 | 遅め |

## 環境変数

| 変数 | デフォルト | 説明 |
|------|-----------|------|
| `GEMINI_API_KEY` | （必須） | Google Gemini API キー |
| `IMAGE_OUTPUT_DIR` | `./output` | 画像の出力先（絶対パス推奨） |
| `IMAGE_QUALITY` | `fast` | デフォルト品質プリセット |
| `SKIP_PROMPT_ENHANCEMENT` | `false` | プロンプト自動最適化を無効化 |

## プロジェクト側 CLAUDE.md の設定例

```markdown
## 画像生成

このプロジェクトには mcp-image (Nano Banana Pro) MCP サーバーが接続されている。
画像を生成・編集するには `generate_image` ツールを使う。

- `generate_image(prompt, quality, aspectRatio)` — テキストから画像生成
- 編集時は `inputImagePath` で元画像を指定

**品質プリセット:** fast（ドラフト）/ balanced（本番）/ quality（最高品質）
```

## ai-interview-article スキルとの連携

記事内の図解・挿絵を生成する場合、ai-interview-article スキルで定義した基底プロンプトを使う：

```
Flat illustration style, clean lines, warm color palette
(cream, sand beige, terracotta, mustard, soft teal).
No dark backgrounds, no neon glow, no outer space imagery.
Warm, approachable, slightly playful — like an indie magazine infographic.
Aspect ratio 1.91:1.
```

1. `quality: balanced` 以上を推奨（記事用の仕上がり品質）
2. `aspectRatio: "16:9"` を note のサムネイルに合わせて使用
3. `SKIP_PROMPT_ENHANCEMENT=true` にして基底プロンプトをそのまま送る

## 料金

| 利用方法 | 無料枠（1日あたり） |
|---------|-------------------|
| API 経由 | 500 リクエスト/日 |

無料枠超過時の従量課金（1024x1024 の場合）：

| モデル | 1枚あたり |
|--------|----------|
| Nano Banana 2 (fast/balanced) | ~$0.067 |
| Nano Banana Pro (quality) | ~$0.039 |
| Imagen 4 Fast | ~$0.02 |

note 記事の図解用途（1日数枚程度）なら無料枠で十分。

## 代替実装

| パッケージ | 特徴 |
|-----------|------|
| [`@rafarafarafa/nano-banana-pro-mcp`](https://github.com/mrafaeldie12/nano-banana-pro-mcp) | シンプル。生成・編集・分析の3ツール |
| [`nano-banana-mcp`](https://github.com/ConechoAI/Nano-Banana-MCP) | 反復編集に強い。continue_editing あり |
