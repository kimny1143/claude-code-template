# /learn - CLAUDE.md育成コマンド

失敗パターン、ベストプラクティス、学習事項をCLAUDE.mdに追記する。

## 使い方

```
/learn                          # 直近の作業から学習を抽出
/learn "Stripeのwebhookは署名検証必須"  # 特定の学習を追記
/learn mistake                  # 失敗パターンを記録
```

## 目的

> "Each team at Anthropic maintains a CLAUDE.md in git to document mistakes, so Claude can improve over time."
> — Boris Cherny

PRごと、セッションごとに学んだことを蓄積し、Claudeが同じ過ちを繰り返さないようにする。

## 実行手順

### Step 1: 学習の特定

引数がある場合:
- そのまま学習事項として使用

引数がない場合:
- 直近のコミット、会話履歴から学習を抽出
- 「最初は間違えたが修正した」パターンを探す
- エラー→修正のサイクルを分析

### Step 2: カテゴリ分類

| カテゴリ | 内容 |
|---------|------|
| `mistakes` | 避けるべきパターン、過去の失敗 |
| `patterns` | 推奨パターン、ベストプラクティス |
| `gotchas` | 落とし穴、注意点 |
| `decisions` | 設計判断とその理由 |

### Step 3: CLAUDE.mdに追記

CLAUDE.mdの適切なセクションに追記。
セクションがなければ「## 学習メモ」セクションを作成。

```markdown
## 学習メモ

### Mistakes（避けるべきパターン）
- Stripeのwebhookで署名検証を忘れると本番で事故る (2026-01-20)
- Server ComponentでuseStateを使うとエラー (2026-01-15)

### Patterns（推奨パターン）
- API routeでは必ずzodでバリデーション
- 認証チェックはmiddlewareで一元化

### Gotchas（落とし穴）
- next/imageはローカルでは動くがVercelでsrc指定ミスるとエラー
- Drizzleのpush:pgはmigration生成しない（開発用）
```

### Step 4: コミット提案

```bash
git add CLAUDE.md
git commit -m "docs(claude): add learning - <summary>"
```

## 引数

- `$ARGUMENTS`: 追記する学習内容、または `mistake`/`pattern`/`gotcha` キーワード

## 自動抽出のヒント

以下のパターンを会話履歴から探す:
- 「あ、間違えた」「修正します」
- エラーメッセージ → 修正
- 「実は...」「注意点として...」
- ユーザーからの訂正フィードバック

## 注意事項

- 機密情報（APIキー、パスワード等）は絶対に含めない
- 具体的で再現可能な記述にする
- 日付を添えて追記（いつの学習か分かるように）
- 長くなりすぎたら整理・統合を提案
