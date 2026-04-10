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

# リモートブランチ削除（--delete）は許可
if [[ "$COMMAND" == *"--delete"* ]]; then
  exit 0
fi

# コマンド内に git -C <path> がある場合、そのリポのブランチを取得
# git -C /path/to/repo push ... のパターンを検出
GIT_DIR_FLAG=""
if [[ "$COMMAND" =~ git[[:space:]]+-C[[:space:]]+([^[:space:]]+) ]]; then
  GIT_DIR_FLAG="${BASH_REMATCH[1]}"
fi

# cd <path> && git push ... のパターンを検出
if [[ -z "$GIT_DIR_FLAG" && "$COMMAND" =~ cd[[:space:]]+([^[:space:];&]+).*git[[:space:]]+push ]]; then
  GIT_DIR_FLAG="${BASH_REMATCH[1]}"
fi

# 対象リポのブランチを取得
if [[ -n "$GIT_DIR_FLAG" ]]; then
  CURRENT_BRANCH=$(git -C "$GIT_DIR_FLAG" rev-parse --abbrev-ref HEAD 2>/dev/null)
else
  CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
fi

# mainブランチへのpushをブロック
if [[ "$CURRENT_BRANCH" == "main" || "$CURRENT_BRANCH" == "master" ]]; then
  echo "BLOCKED: mainへの直接pushはブロックされています。featureブランチからPRを作成してください。"
  exit 2
fi

exit 0
