# Hoo投稿 型変更スキーマ設計・移行仕様書

> conductor承認済み（2026-04-11）。template課作成 → SNS課実装。

---

## 変更概要

| # | 変更 | 内容 |
|---|------|------|
| A | `ad` → `product-story` | 型名リネーム + コンテンツ方針変更 |
| B | `question` 型新設 | エンゲージメント促進用 |
| C | 投稿ミックス比率 | 推奨比率の明文化（観測結果で調整可） |

---

## 1. 新スキーマ定義

### hoo-posts.json

```json
{
  "id": "h001",
  "type": "product-story | tech-log | observation | question | article-announce",
  "post_text": "string",
  "topic_tag": "string",
  "self_reply": "string | null"
}
```

**変更点:**
- `type` の有効値: `ad` を削除、`product-story` と `question` を追加
- フィールド構成は変更なし（id, type, post_text, topic_tag, self_reply）

### 型の定義

| 型 | 目的 | 特徴 | 例 |
|----|------|------|-----|
| `product-story` | プロダクトの背景を語る | 宣伝ではなくストーリー。「なぜ作ったか」「どう考えたか」 | 「MUEDialを作ったきっかけは、自分のミックスに自信が持てなかったから。」 |
| `tech-log` | 開発・技術の記録 | 試行錯誤、発見、技術的な気づき | 「ステム分離モデルと格闘中。ハイハットとシェイカー、AIには同じに聴こえるらしい。」 |
| `observation` | 開発プロセスの観察 | 制作者視点の気づき。Hooの強み（高エンゲージメント） | 「『完成』のタイミングがわからない、という相談がいちばん多い。」 |
| `question` | フォロワーとの対話 | 問いかけ形式。リプライを促す | 「曲を作ってて『これもう完成？』って迷う瞬間、どうしてますか？」 |
| `article-announce` | note記事の告知 | 記事URLを含む。公開タイミングに連動 | 「noteに記事が出ています。『メロディが降りてくる』は嘘だった——」 |

### post-log.json（ログエントリ）

```json
{
  "type": "hoo",
  "hoo_type": "product-story | tech-log | observation | question | article-announce",
  "id": "h001",
  "topic_tag": "MUED",
  "timestamp": "2026-04-11T10:00:00.000Z",
  "success": true,
  "post_id": "18051587018491189",
  "container_id": "17857390596618818",
  "user_id": "25523322837363960"
}
```

**変更点:**
- `hoo_type` の有効値に `product-story` と `question` を追加
- 過去ログの `hoo_type: "ad"` はそのまま保持（履歴データは書き換えない）

---

## 2. 投稿ミックス比率

### 推奨比率（週4回投稿の場合）

| 型 | 頻度 | 割合 |
|----|------|------|
| `product-story` | 1回/週 | 25% |
| `tech-log` | 1回/週 | 25% |
| `observation` | 1回/週 | 25% |
| `question` | 1回/週 | 25% |
| `article-announce` | 記事公開時 | 比率外 |

**注意:** data課分析でobservation型（h003）が320viewsと突出。observationはHooの強みなので、効果を見ながら observation の比率を上げる調整を推奨。

### 比率の実装方法

`post-to-threads.js` の `selectNextItem()` は現在、未投稿アイテムを順に選択する方式。比率制御を入れるなら、以下の2案:

**案1: データ順制御（推奨）**
hoo-posts.json のデータ順を型が交互になるよう配置。selectNextItem はそのまま。

**案2: ロジック制御**
selectNextItem に型別の投稿カウントを参照する重み付けロジックを追加。

案1がシンプルで推奨。write課が投稿文を追加する際に、型のバランスを意識して配置すればよい。

---

## 3. 実装変更箇所

### ファイル別の変更内容

| ファイル | 変更内容 | 担当 |
|---------|---------|------|
| `hoo-posts.json` | `type: "ad"` → `type: "product-story"` リネーム + question型追加 | 移行スクリプト + write課 |
| `post-to-threads.js` | ラベル表示の型名対応（行434）。ロジック変更は不要 | SNS課 |
| `self-reply.js` | 型固有の処理がないため変更不要 | — |
| `post-log.json` | 過去ログはそのまま。新規ログは新型名で記録 | 自動 |
| `.github/workflows/` | スケジュール変更なし（週4回は既存のまま） | — |
| `CLAUDE.md` | 型定義の更新 | SNS課 |
| `README.md` | 投稿タイプの説明更新 | SNS課 |

### post-to-threads.js の変更箇所

行434のラベル生成部分のみ:
```javascript
// 変更不要 — targetItem.type をそのまま使用しているため
// product-story / question も自動的にラベルに反映される
const label = `[hoo/${targetItem.type}] ${targetItem.id}: ...`;
```

型の判定ロジック（行403-459）は `type` フィールドの値を直接参照していないため、**コード変更は実質不要**。データファイルの型名変更のみで動作する。

---

## 4. 移行スクリプト

`scripts/migrate-hoo-types.js` として提供。SNS課が threads-api リポで実行。

**実行方法:**
```bash
cd /path/to/threads-api
node /path/to/migrate-hoo-types.js
```

**動作:**
1. `hoo-posts.json` をバックアップ（`hoo-posts.json.bak`）
2. `type: "ad"` → `type: "product-story"` に一括変更
3. question型のサンプル3件を末尾に追加（write課が本番コンテンツに差し替え）
4. 変更結果のサマリーを表示

---

## 5. question型の投稿文ガイドライン（write課向け）

### 原則
- 問いかけ形式で終わる（「〜ですか？」「〜どうしてますか？」）
- Hooの人格（フクロウ、観察者、少し距離を置いた視点）を保つ
- 正解がない問いを選ぶ（議論が生まれやすい）
- self_reply は必ず設定する（フォロワーのリプライがなくても対話が成立するように）

### テーマ候補
- 制作プロセスの判断（「完成のタイミング」「やめどき」「始めどき」）
- 音楽と技術の境界（「AIと人間の違い」「ツールの選び方」）
- クリエイターの習慣（「朝型/夜型」「ルーティン」「道具へのこだわり」）

### NG
- 答えが1つしかない質問（クイズになる）
- 過度に個人的な質問（プライバシー）
- 批判を誘発する質問（「〜はダメだと思いませんか？」）
