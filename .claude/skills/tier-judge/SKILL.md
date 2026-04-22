---
name: tier-judge
description: >
  git diff を解析して PR の Tier（1/2/3）を自動提案する。判定根拠と境界ケース注意も出力。
  使用タイミング: (1) PR作成前にTierを確認したい時 (2) 境界ケースで判断に迷った時
  (3) git diffを見てTier判定してほしい時。
  トリガー例: 「これ何Tier?」「Tier判定して」「このPRはTier何になる?」
  「Tier確認してから PR 作りたい」「git diffを見てTierを教えて」
---

# tier-judge — git diff → Tier 1/2/3 自動判定

`git diff main...HEAD` を解析し、PRのTierを提案する。
判定根拠・境界ケース警告を出力して人間の最終確認を支援する。

---

## 使い方

```
「このブランチのTierを判定して」
「git diffを見てTierを教えて」
「PR作る前にTier確認したい」
```

---

## 判定フロー

### Step 1: Tier 3 チェック（1つでも該当 → Tier 3）

以下のいずれかに変更が含まれるか確認する:

| チェック項目 | 検出パターン例 |
|------------|--------------|
| 価格・原価率 | `price`, `pricing`, `¥`, `$29`, `cost`, `rate`（コード内） |
| 認証・セキュリティ | `.env`編集, `oauth`, `api_key`, `token`, `secret`（コード内） |
| DBスキーマ破壊的変更 | `DROP TABLE`, `RENAME`, `ALTER COLUMN TYPE`, `NOT NULL`追加+backfill |
| 本番環境設定 | `vercel.json`, `wrangler.toml`, `secrets:`, GitHub Actions secrets |
| hook/settings 全課波及 | `validate-dangerous-ops-v2.sh`, `settings.local.json`（配布対象） |
| template課からの変更 | `claude-code-template/` 配下のコード変更（全課波及） |
| 新規外部サービス導入 | 新しいAPIキー設定, 新しい `npm install` パッケージでの外部依存追加 |

### Step 2: Tier 1 チェック（コードなし → Tier 1）

変更ファイルが以下のみの場合:
- `*.md`, `*.txt`, `*.csv`
- テストファイル追加のみ（既存コード無変更）
- コピー・ドキュメント・データファイルのみ

### Step 3: Tier 2（上記以外のコード変更）

コード変更あり + Tier 3条件非該当 → Tier 2

**Tier 2扱い例外**（Tier 3条件に一部該当しても Tier 2）:
- `CREATE TABLE`, `ADD COLUMN nullable`, index追加のみ → 純粋追加DBスキーマ
- hook/settings の変更が自ピア内のみに影響する場合

---

## 出力フォーマット

```
## Tier判定結果: Tier [1/2/3]

**根拠:**
- [判定の主な理由を箇条書き]

**Tier 2の場合 — レビュー担当:**
| 自分 | レビュー依頼先 |
|------|-------------|
| template課 | reserch課 |
| mued課 | native課 |
| native課 | mued課 |
| SNS課 | write課 |
| write課 | SNS課 |
| video課 | SNS課 |
| LP課 | mued課 |
| data課 | mued課 |
| freee課 | LP課 |

**境界ケース注意（該当する場合のみ）:**
- [境界ケースの警告と推奨対応]
```

---

## 境界ケース例示

**`price` 文字列がスラッグに含まれる場合**:
```
⚠ `pricing-page.tsx` の変更を検知しましたが、コード内容はUI文言変更のみです。
価格・原価率への影響はないと判断しますが、確認してください。→ Tier 2のまま
```

**secret関連ファイルへの意図不明な変更**:
```
⚠ `.env.example` に `SECRET_KEY` の追記を検知しました。
.env.example は許容範囲ですが、意図的な変更か確認してください。→ Tier 2のまま
（実際の秘密鍵が混入している場合は Tier 3に上げてください）
```

**settings.local.json の変更**:
```
⚠ `.claude/settings.local.json` の変更を検知しました。
全課配布対象か、自ピア内のみの変更かを確認してください。
- 全課配布対象 → Tier 3
- 自ピア内のみ → Tier 2
```

---

## 注意事項

- キーワードマッチは誤検知あり。判定根拠を必ず確認すること
- 最終判断は人間。「判断に迷ったらTier 3に上げる」が原則
- git diffが大きい場合（100ファイル超）は主要ファイルのみ解析し、その旨を明示する
