#!/bin/bash
# PreToolUse Hook (Chief / 参謀 _chief 専用): _chief cwd 外への Write/Edit をブロック
#
# 目的: 組織再編 v2 (2026-06-11) の「参謀は _strategy(_chief) のみ書く / 運用ファイルは
#       conductor single writer」を **規約 prose でなく機構で強制**する (CCO governance 条件2)。
#       Chief は同一マシン・同一 git 権限ゆえ、規約だけでは peer の status.md/inbox に
#       誤書込しても何も止まらない → 本 hook で「書かない約束」を「書けない構造」にする。
#
# 発火: PreToolUse (Write, Edit)。Exit: 0=許可 / 2=ブロック。入力: stdin JSON
#       {"tool_name":"...", "tool_input":{"file_path":"..."}}
#
# allowlist (Claude Code core path のみ — bootstrap deadlock 回避。
#            cf. memory feedback_hook_allowlist_core_path_check):
#   - ~/.claude/plans/             : EnterPlanMode が ~/.claude/plans/<random>.md を強制指定。
#                                    無いと Plan mode bootstrap deadlock。
#   - ~/.claude/projects/*/memory/ : Chief 自身のセッション跨ぎ continuity memory。
#   - ~/.claude/todos/ , ~/.claude/*.jsonl : Claude Code 内部状態 (todo/audit ログ)。
#
# ★ conductor inbox/drafts は **allowlist しない** (fleet 共通 validate-dangerous-ops-v2 と
#   異なる点)。Chief の kimny 提示は conductor 経由 relay = Chief は運用ファイルに直接書かない。
#
# 配布: 本 hook は template canonical。Chief workspace (_chief) の settings.local.json に
#       のみ wire する (他 peer には配布しない)。wiring 例は本 hook 末尾コメント参照。

set -euo pipefail

INPUT=$(cat)

# jq が無い場合はフェイルセーフで許可 (他 hook と同方針)
command -v jq &>/dev/null || exit 0

TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null)

# Write / Edit 以外は対象外
if [ "$TOOL_NAME" != "Write" ] && [ "$TOOL_NAME" != "Edit" ]; then
  exit 0
fi

TOOL_INPUT=$(echo "$INPUT" | jq -r '.tool_input // empty' 2>/dev/null)
FILE_PATH=$(echo "$TOOL_INPUT" | jq -r '.file_path // empty' 2>/dev/null)
[ -n "$FILE_PATH" ] || exit 0

# --- allowlist (core path のみ) ---
if echo "$FILE_PATH" | grep -qE "^$HOME/\.claude/plans/"; then exit 0; fi
if echo "$FILE_PATH" | grep -qE "^$HOME/\.claude/projects/[^/]+/memory/"; then exit 0; fi
if echo "$FILE_PATH" | grep -qE "^$HOME/\.claude/todos/"; then exit 0; fi
if echo "$FILE_PATH" | grep -qE "^$HOME/\.claude/[^/]+\.jsonl$"; then exit 0; fi

# --- CWD 外への Write/Edit をブロック ---
# 絶対パスに正規化して CWD 配下かチェック (realpath 無い環境は python3 fallback)
RESOLVED_PATH=$(realpath "$FILE_PATH" 2>/dev/null || python3 -c "import os,sys; print(os.path.realpath(sys.argv[1]))" "$FILE_PATH" 2>/dev/null || (cd "$(dirname "$FILE_PATH")" 2>/dev/null && echo "$(pwd)/$(basename "$FILE_PATH")") || echo "$FILE_PATH")
CWD=$(realpath "$PWD" 2>/dev/null || python3 -c "import os,sys; print(os.path.realpath(sys.argv[1]))" "$PWD" 2>/dev/null || echo "$PWD")

if [ "${RESOLVED_PATH#$CWD/}" = "$RESOLVED_PATH" ] && [ "$RESOLVED_PATH" != "$CWD" ]; then
  echo "" >&2
  echo "BLOCKED (Chief governance): _chief cwd 外への Write/Edit は禁止です。" >&2
  echo "   Chief(参謀) は _strategy(_chief) のみ書く。運用ファイルは conductor single writer。" >&2
  echo "   kimny 提示・peer 連携は conductor 経由 relay (inbox/dashboard/status.md に直接書かない)。" >&2
  echo "   CWD: $CWD" >&2
  echo "   file: $FILE_PATH" >&2
  echo "" >&2
  exit 2
fi

exit 0

# ─────────────────────────────────────────────────────────────────────────────
# wiring 例 (_chief/.claude/settings.local.json):
#   "hooks": {
#     "PreToolUse": [
#       { "matcher": "Write|Edit",
#         "hooks": [ { "type": "command",
#                      "command": "$HOME/Dropbox/_DevProjects/_chief/.claude/hooks/chief-cwd-write-guard.sh" } ] }
#     ]
#   }
# ※ _chief は git ローカルのみ (外部リソースゼロ)。hook 本体は template から symlink or copy。
#
# 既知の限界 (Bash 経由の out-of-cwd 書込):
#   本 hook は Write/Edit のみ。Bash の `echo > /other/path` 等の out-of-cwd 書込は
#   検知しない (fleet の validate-dangerous-ops-v2 も同スコープ)。Chief の Bash 権限を
#   settings の permissions で絞る (read-only 系のみ allow) ことで補完するのを推奨。
# ─────────────────────────────────────────────────────────────────────────────
