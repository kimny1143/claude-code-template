#!/bin/bash
# Stop Hook: セッション終了時の Git 整理提案
#
# 発火条件: Stop (会話終了時)
# 動作: マージ済みブランチ・古いworktreeを検知 → stderrに提案

set -e

# Git リポジトリでない場合は終了
if ! git rev-parse --git-dir > /dev/null 2>&1; then
  exit 0
fi

declare -a SUGGESTIONS=()

# 1. マージ済みのローカルブランチを検出
MERGED_BRANCHES=$(git branch --merged main 2>/dev/null | grep -v '^\*' | grep -v 'main' | grep -v 'master' | tr -d ' ' || true)

if [ -n "$MERGED_BRANCHES" ]; then
  BRANCH_COUNT=$(echo "$MERGED_BRANCHES" | wc -l | tr -d ' ')
  SUGGESTIONS+=("🌿 マージ済みブランチが ${BRANCH_COUNT} 件あります: $(echo $MERGED_BRANCHES | tr '\n' ' ') → git branch -d <branch> で削除を検討")
fi

# 2. リモートで削除済みのブランチを検出
git fetch --prune 2>/dev/null || true
GONE_BRANCHES=$(git branch -vv 2>/dev/null | grep ': gone]' | awk '{print $1}' || true)

if [ -n "$GONE_BRANCHES" ]; then
  SUGGESTIONS+=("🗑️ リモートで削除済みのブランチ: $(echo $GONE_BRANCHES | tr '\n' ' ') → git branch -D <branch> で削除を検討")
fi

# 3. 古い worktree を検出
if command -v git-worktree &> /dev/null || git worktree list &> /dev/null; then
  WORKTREE_COUNT=$(git worktree list 2>/dev/null | wc -l | tr -d ' ')
  if [ "$WORKTREE_COUNT" -gt 1 ]; then
    SUGGESTIONS+=("📁 Worktree が ${WORKTREE_COUNT} 個あります → git worktree list で確認、不要なものは git worktree remove で削除")
  fi
fi

# 提案があれば出力
if [ ${#SUGGESTIONS[@]} -gt 0 ]; then
  echo "" >&2
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
  echo "🧹 Git 整理提案" >&2
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
  for suggestion in "${SUGGESTIONS[@]}"; do
    echo "" >&2
    echo "$suggestion" >&2
  done
  echo "" >&2
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
  exit 1
fi

exit 0
