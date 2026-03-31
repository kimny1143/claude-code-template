#!/bin/bash
# SessionStart Hook: 前回の引き継ぎメモリを強制読み込み
#
# 動作: CWDからClaude Codeメモリディレクトリを特定し、
#       最新のhandoff/sessionファイルの内容をstdoutに出力。
#       Claude Codeはこの出力をセッション開始時のコンテキストとして受け取る。
#
# 汎用: どのプロジェクトでも動作（CWDベースで自動判定）

# --- CWDからメモリディレクトリを特定 ---
CWD=$(pwd)
# Claude Codeのメモリディレクトリ命名規則: / と _ を - に置換
MEMORY_DIR_NAME=$(echo "$CWD" | tr '/_' '--')
MEMORY_DIR="/Users/kimny/.claude/projects/${MEMORY_DIR_NAME}/memory"

if [ ! -d "$MEMORY_DIR" ]; then
  exit 0
fi

# --- 最新のhandoff/sessionファイルを検索 ---
# project*handoff* または project*session* にマッチするファイルを更新日時順で取得
HANDOFF=$(ls -t "$MEMORY_DIR"/project*handoff*.md "$MEMORY_DIR"/project*session*.md 2>/dev/null | head -1)

if [ -z "$HANDOFF" ]; then
  exit 0
fi

# --- 内容を出力 ---
echo ""
echo "=========================================="
echo "[引き継ぎメモリ自動読み込み]"
echo "ファイル: $(basename "$HANDOFF")"
echo "=========================================="
cat "$HANDOFF"
echo ""
echo "=========================================="
echo "上記の引き継ぎ事項を確認し、未着手タスクを把握してから作業を開始してください。"
echo "=========================================="
