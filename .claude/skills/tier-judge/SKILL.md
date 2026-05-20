---
name: tier-judge
description: >
  git diff を解析して PR の Tier（1/2/3）を自動提案する。判定根拠・境界ケース注意に加え、
  UI / 成果物変更を検出した場合は成果物 evidence 必須 warning も出力。
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

### Step 4: UI / 成果物変更検出（Tier 数値とは独立して必ず実行）

Tier 1/2/3 の数値判定とは別に、変更が **UI / 成果物の見た目・挙動** に影響するかを判定する。
以下のいずれかに該当 → 「成果物 evidence 必須」。

| チェック項目 | 検出パターン例 |
|------------|--------------|
| フロントUI | `*.tsx`, `*.jsx`, `*.vue`, `*.css`, `*.scss`, component / layout / viewport file |
| ネイティブUI | `*.swift`, `*.kt`, Storyboard, Compose 画面 file |
| LP / Webページ | LP page, ランディング HTML / テンプレート |
| 3D / グラフィック | `*.blend`, シーン / レンダリング設定 |
| CLI / 出力成果物 | CLI 出力 format, 生成物 (WAV / 画像 / レポート) のフォーマット変更 |

検出時は、Tier 判定結果に **必ず** 「成果物 evidence 必須」 section を付けて出力する（Step 4
は条件分岐ではなく常時実行。検出が真なら出力は無条件で発火する = MUEDear Build 78 型の素通りを
構造で防ぐ最低ライン）。

- evidence = スクショ / 録画 / 実機操作ログ + 自課キャラクター gate の確認結果
- evidence なしの PR は Tier 1/2/3 いずれであっても merge 不可
- 「型エラー 0」「ビルド成功」「コード LGTM」 は機械チェックであり、成果物 verify を兼ねない
- 詳細は共通 block `19-character-gate` + `.github/pull_request_template.md` の「成果物 verify」section

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

**成果物 evidence 必須（Step 4 で UI / 成果物変更を検出した場合は必ず出力）:**
⚠ この PR は UI / 成果物変更を含みます。
→ スクショ / 録画 + 自課キャラクター gate の確認結果を PR の「成果物 verify」section に必須添付。
→ evidence なしの PR は Tier 1/2/3 いずれであっても merge 不可（機械チェック通過 ≠ 成果物 verify）。

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
