# /build-fix - ビルドエラー自動修正

ビルドエラーを検出し、自動で修正するループを実行する。

## 実行手順

### Phase 1: 初回ビルド

1. **TypeScript型チェック**
   ```bash
   npm run typecheck 2>&1
   ```

2. **ESLint**
   ```bash
   npm run lint 2>&1
   ```

3. **Next.js ビルド**
   ```bash
   npm run build 2>&1
   ```

### Phase 2: エラー修正ループ

エラーがある場合、以下を繰り返す（最大5回）:

1. **エラー解析**
   - TypeScriptエラー: 型の不一致、missing imports、undefined変数
   - ESLintエラー: unused vars、missing deps、formatting
   - ビルドエラー: モジュール解決、設定問題

2. **修正実行**
   - 該当ファイルを読み込み
   - エラーの原因を特定
   - 最小限の修正を適用
   - 変更内容を報告

3. **再チェック**
   - 修正したチェックを再実行
   - 新たなエラーがあれば次のループへ

### Phase 3: 完了確認

すべてのチェックがパスしたら:
- 修正したファイル一覧を表示
- 変更内容のサマリーを報告

## エラー種別と対応

| エラー種別 | 自動修正 | 例 |
|-----------|---------|-----|
| 型エラー | ✅ | 型アノテーション追加、型キャスト |
| unused import | ✅ | インポート削除 |
| missing import | ✅ | インポート追加 |
| unused variable | ✅ | 変数削除または `_` プレフィックス |
| missing dependency | ✅ | useEffect依存配列修正 |
| formatting | ✅ | Prettier適用 |
| ロジックエラー | ❌ | 報告のみ（手動修正必要） |

## 引数

- `$ARGUMENTS`: 特定のチェックのみ実行
  - `types` - TypeScriptのみ
  - `lint` - ESLintのみ
  - `build` - ビルドのみ

## 使用例

```
/build-fix           # フルチェック＆修正
/build-fix types     # 型エラーのみ修正
/build-fix lint      # Lintエラーのみ修正
```

## 注意事項

- 5回のループで解決しない場合は停止して報告
- ロジックに影響する変更は確認を求める
- node_modules、生成ファイルは修正しない
- 修正後は必ず変更内容を説明する

## 修正しない項目

以下は自動修正せず、報告のみ:
- ビジネスロジックの変更が必要なエラー
- 設計判断が必要なエラー
- 外部ライブラリのバグ
- 環境変数の問題
