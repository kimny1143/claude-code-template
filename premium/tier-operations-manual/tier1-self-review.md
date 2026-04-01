# Tier 1: セルフレビュー運用ガイド

## 対象となる変更

- ドキュメントの修正・追加（`.md` ファイル）
- データファイルの更新（JSON、CSV、YAML等の設定データ）
- コピー修正（UI上のテキスト変更のみ）
- テストの追加（既存コードに変更なし）
- コメント・JSDocの追加修正

## 対象にならない変更（Tier 2以上に上げる）

- テストの修正（既存テストのロジック変更は「テストコード」の変更）
- ドキュメント+コード変更のセット（コード部分がある時点でTier 2）
- CI/CDパイプラインの設定ファイル変更（Tier 3）
- `.env.example` の変更（環境変数追加はTier 3の可能性）

## セルフレビュー手順

### 1. CI全通過を確認

```bash
# ローカルチェック
npm run lint        # or turbo run lint
npm run typecheck   # or turbo run typecheck
npm run test        # or turbo run test

# CIで確認
gh pr checks <PR番号>
```

**CIが通らない場合 → マージ禁止。** Tier 1でも例外なし。

### 2. セルフレビューチェックリスト

PRを作成したら、以下を自分で確認:

- [ ] 変更内容がTier 1の対象範囲に収まっているか
- [ ] タイポや誤記がないか
- [ ] リンク切れがないか（ドキュメントの場合）
- [ ] 不要なファイルが含まれていないか
- [ ] `.env` や認証情報が含まれていないか

### 3. PRタイトルにタグを付与

```
[self-review] docs: update API documentation
[self-review] test: add unit tests for UserService
```

### 4. マージ

```bash
gh pr merge <PR番号> --squash
```

### 5. patrol報告

次回のコンダクター巡回時に報告:

```
マージ済み: #42 [Tier 1] docs: update README
```

## よくある判断ミス

| ケース | 誤った判断 | 正しい判断 |
|--------|-----------|-----------|
| READMEにコード例を追加 | Tier 1（ドキュメントだから） | **Tier 1でOK**（コード例はドキュメントの一部） |
| package.jsonのdescription変更 | Tier 1（テキスト変更だから） | **Tier 2**（package.jsonはコード） |
| `.gitignore` の追加 | Tier 1（設定だから） | **Tier 2**（リポジトリの挙動が変わる） |
| テストのスナップショット更新 | Tier 1（テストだから） | **Tier 2**（既存テストの変更） |
| 翻訳ファイル（i18n）の追記 | Tier 1（コピーだから） | **Tier 1でOK**（UIテキストのみ） |
