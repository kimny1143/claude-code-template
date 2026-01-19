# /commit - Git Commit Workflow

Gitの変更をステージング、コミット、プッシュする。

## 実行手順

1. **状態確認**
   - `git status` で変更ファイルを確認
   - `git diff` でステージされていない変更を確認
   - `git diff --staged` でステージ済みの変更を確認

2. **コミット対象の判断**
   - 関連する変更のみをステージング
   - `.env`、認証情報、シークレットは絶対にコミットしない
   - 不要なファイル（.DS_Store、node_modules等）は除外

3. **コミットメッセージ作成**
   - 最近のコミット履歴（`git log --oneline -10`）を参照してスタイルを合わせる
   - Conventional Commits形式を使用:
     - `feat:` 新機能
     - `fix:` バグ修正
     - `docs:` ドキュメント
     - `refactor:` リファクタリング
     - `test:` テスト追加・修正
     - `chore:` その他

4. **コミット実行**
   ```bash
   git add <files>
   git commit -m "$(cat <<'EOF'
   <type>: <description>

   Co-Authored-By: Claude <noreply@anthropic.com>
   EOF
   )"
   ```

5. **プッシュ**
   - リモートブランチがあれば `git push`
   - なければ `git push -u origin <branch>`

## 引数

- `$ARGUMENTS` が指定された場合、それをコミットメッセージのヒントとして使用

## 注意事項

- pre-commitフックが失敗した場合は修正して再コミット
- `--amend` は使用しない（明示的に指示された場合のみ）
- `--force` プッシュは絶対に行わない
