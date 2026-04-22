---
name: i18n-key-diff
description: >
  en.json と ja.json のキー差分を検出して不足翻訳を報告する。
  使用タイミング: (1) EN追加後にJAが追いついているか確認したい時 (2) i18n漏れビルドエラーが出た時
  (3) 翻訳作業の完了確認をしたい時。
  トリガー例: 「i18nの差分を確認して」「翻訳キーが足りてるか調べて」「en.jsonとja.jsonを比較して」
  「翻訳漏れを教えて」「missing translationを確認して」
---

# i18n-key-diff — en.json ↔ ja.json キー差分検出

`en.json` と `ja.json` のペアをスキャンし、一方にしか存在しないキーを列挙する。
next-intl（`messages/` 配下）と content JSON（`content/` 配下）の両方に対応。

---

## 使い方

```
「i18nの差分を確認して」
「翻訳キーが全部揃ってるか確認して」
「en.jsonにあってja.jsonにないキーを教えて」
```

---

## 実行手順

### Step 1: 対象ファイルペアを検索

プロジェクトルートから以下のコマンドで en.json/ja.json ペアを列挙する（node_modules除外）:

```bash
find . -name "en.json" -not -path "*/node_modules/*" | sort
find . -name "ja.json" -not -path "*/node_modules/*" | sort
```

同一ディレクトリに en.json と ja.json が両方存在するものをペアとして処理する。

### Step 2: キー差分を抽出

以下の Python スクリプトで各ペアのキー差分を取得する:

```python
import json, os, sys

def get_flat_keys(obj, prefix=''):
    keys = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            full = f'{prefix}.{k}' if prefix else k
            if isinstance(v, dict):
                keys |= get_flat_keys(v, full)
            else:
                keys.add(full)
    return keys

def diff_pair(en_path, ja_path):
    with open(en_path) as f:
        en_keys = get_flat_keys(json.load(f))
    with open(ja_path) as f:
        ja_keys = get_flat_keys(json.load(f))
    return en_keys - ja_keys, ja_keys - en_keys

# 使用例
only_en, only_ja = diff_pair('messages/en.json', 'messages/ja.json')
```

### Step 3: 結果を整理して報告

---

## 出力フォーマット

```
## i18n キー差分レポート

### messages/en.json ↔ ja.json
- EN総キー数: 1220 / JA総キー数: 1220
- **ENにあってJAにない（翻訳追加が必要）**: 3件
  - `landing.products.muednote.features.newBadge`
  - `onboarding.step3.title`
  - `auth.errors.tokenExpired`
- **JAにあってENにない（削除済みor余剰）**: 0件

### content/stories/muedear/en.json ↔ ja.json
- EN総キー数: 45 / JA総キー数: 45
- 差分なし ✅

---
**要対応**: 3キー（messages/ja.json への追記が必要）
**問題なし**: 1ペア
```

---

## 対応ガイド

**ENにあってJAにない場合（翻訳追加が必要）**:
1. 該当キーを `ja.json` の対応箇所に追記する
2. 値は日本語訳を入れる（仮訳でも可、後で精査）
3. 再度このスキルで差分がゼロになることを確認

**JAにあってENにない場合（余剰キー）**:
- ENから削除済みのキーが残っている可能性がある
- 意図的に残している場合は無視して可
- 不要であれば `ja.json` から削除

---

## 対象プロジェクト

主な使用想定:
- `mued/mued_v2` — `messages/en.json` + `messages/ja.json`（next-intl）
- content ディレクトリ配下の en/ja JSONペア

他プロジェクトでも en.json/ja.json ペアがあれば同様に動作する。

---

## 注意事項

- `node_modules/` 配下は必ず除外する
- キーの「値が空文字列」は差分として検出しない（キーが存在すればOK）
- ネストの深さに制限なし（フラット化して比較するため）
- JSON の配列値（`[]`）配下のキーは比較対象外（構造が動的なため）
