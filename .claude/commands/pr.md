# /pr - Pull Request作成

現在のブランチからPull Requestを作成する。

## 実行手順

1. **事前確認**
   - `git status` で未コミットの変更がないか確認
   - 未コミットがあれば先に `/commit` を提案
   - 現在のブランチ名を確認

2. **差分分析**
   - `git log main..HEAD --oneline` でコミット一覧を取得
   - `git diff main...HEAD` で全体の変更内容を把握
   - 変更の目的・影響範囲を理解

3. **PRタイトル生成**
   - 変更内容を端的に表現（50文字以内）
   - Conventional Commits形式に準拠

4. **PR本文生成**
   以下の形式で作成:
   ```markdown
   ## Summary
   - <変更点1>
   - <変更点2>
   - <変更点3>

   ## Test plan
   - [ ] <テスト項目1>
   - [ ] <テスト項目2>

   ---
   Generated with [Claude Code](https://claude.ai/code)
   ```

5. **PR作成実行**
   ```bash
   git push -u origin <branch>  # リモートにプッシュ
   gh pr create --title "<title>" --body "$(cat <<'EOF'
   <body>
   EOF
   )"
   ```

6. **結果報告**
   - 作成されたPRのURLを表示

## 引数

- `$ARGUMENTS` が指定された場合、PRの説明のヒントとして使用

## 注意事項

- mainブランチから直接PRを作成しない
- Draft PRが必要な場合は `--draft` フラグを追加
- レビュアーの指定が必要な場合はユーザーに確認
