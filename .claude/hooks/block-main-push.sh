#!/bin/bash
# Pre-push hook: mainブランチへの直接pushをブロック
# Claude Code の PreToolUse(Bash) フックとして使用

# stdin から tool_input を読み取る
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# git push コマンドかチェック
if [[ "$COMMAND" != *"git push"* ]]; then
  exit 0
fi

# 現在のブランチを取得
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)

# mainブランチへのpushをブロック
if [[ "$CURRENT_BRANCH" == "main" || "$CURRENT_BRANCH" == "master" ]]; then
  echo "BLOCKED: mainへの直接pushはブロックされています。featureブランチからPRを作成してください。"
  exit 2
fi

exit 0
