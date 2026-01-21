# /ship - Commit, Push, and Create PR

変更をコミット、プッシュし、PRを作成する統合コマンド。
Boris Cherny流の「inner-loop」を高速化するためのワンストップコマンド。

## 使い方

```
/ship                    # 自動でタイトル・本文生成
/ship fix login bug      # ヒントを指定
```

## 実行手順

### Step 1: 状態確認（並列実行）

```bash
git status
git diff
git diff --staged
git log --oneline -5
```

### Step 2: 変更の分析

- 変更ファイルを把握
- コミット対象を判断
- `.env`、シークレット、不要ファイルは除外

### Step 3: コミット

```bash
git add <relevant-files>
git commit -m "$(cat <<'EOF'
<type>: <description>

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Conventional Commits形式**:
- `feat:` 新機能
- `fix:` バグ修正
- `docs:` ドキュメント
- `refactor:` リファクタリング
- `test:` テスト
- `chore:` その他

### Step 4: プッシュ

```bash
git push -u origin <current-branch>
```

### Step 5: PR作成

```bash
gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
- <変更点1>
- <変更点2>

## Test plan
- [ ] <テスト項目1>
- [ ] <テスト項目2>

---
Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### Step 6: 結果報告

- 作成されたPRのURLを表示
- 次のアクション（レビュー依頼等）を提案

## 引数

- `$ARGUMENTS`: PRタイトル・本文のヒントとして使用

## 注意事項

- mainブランチからは実行しない（警告して停止）
- 未コミットの変更がなければスキップ
- pre-commitフック失敗時は修正して再実行
- `--force` プッシュは絶対に行わない
- PRが既に存在する場合は更新のみ（`gh pr edit`）

## このコマンドの思想

> "I use slash commands for every 'inner loop' workflow I do many times a day."
> — Boris Cherny

1日に何十回も実行することを想定。迷わず、速く、確実に。
