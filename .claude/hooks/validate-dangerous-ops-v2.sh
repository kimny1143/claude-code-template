#!/bin/bash
# PreToolUse Hook: 危険な操作の事前検証 v2
#
# 発火条件: PreToolUse (Write, Edit, Bash)
# 動作: 危険なパターンを検知 → stderrに警告/ブロック
#
# Exit codes:
#   0 = 許可（警告メッセージ付きの場合もある）
#   2 = ブロック（操作を中止）
#
# 入力: stdin から JSON（Claude Code標準）
#   {"tool_name": "...", "tool_input": {...}}

set -euo pipefail

# --- 入力取得 ---
INPUT=$(cat)

# jqがない場合はフェイルセーフで許可
if ! command -v jq &> /dev/null; then
  exit 0
fi

TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null)
TOOL_INPUT=$(echo "$INPUT" | jq -r '.tool_input // empty' 2>/dev/null)

# 入力不正の場合は許可
if [ -z "$TOOL_NAME" ] || [ -z "$TOOL_INPUT" ]; then
  exit 0
fi

# --- ヘルパー関数 ---
block() {
  echo "" >&2
  echo "BLOCKED: $1" >&2
  if [ -n "${2:-}" ]; then
    echo "   $2" >&2
  fi
  echo "" >&2
  exit 2
}

warn() {
  echo "" >&2
  echo "WARNING: $1" >&2
  if [ -n "${2:-}" ]; then
    echo "   $2" >&2
  fi
  echo "" >&2
  # 警告のみ、ブロックしない
}

# =====================
# Write / Edit 検証
# =====================
if [ "$TOOL_NAME" = "Write" ] || [ "$TOOL_NAME" = "Edit" ]; then
  FILE_PATH=$(echo "$TOOL_INPUT" | jq -r '.file_path // empty' 2>/dev/null)

  if [ -z "$FILE_PATH" ]; then
    exit 0
  fi

  # CWDチェックのallowlist判定（.env/credentials等のセキュリティチェックはこの後も実行される）
  # - auto-memory: セッション跨ぎの文脈継承に必要（~/.claude/projects/<id>/memory/）
  # - conductor drafts: 課間承認依頼の正規投函先（feedback_document_submission）
  IS_ALLOWLIST=0
  if echo "$FILE_PATH" | grep -qE "^$HOME/\.claude/projects/[^/]+/memory/"; then
    IS_ALLOWLIST=1
  fi
  if echo "$FILE_PATH" | grep -qE "^$HOME/Dropbox/_DevProjects/_conductor/docs/drafts/"; then
    IS_ALLOWLIST=1
  fi

  # CWD外へのWrite/Editをブロック（allowlist該当時はスキップ）
  # 絶対パスに正規化してCWD配下かチェック
  if [ "$IS_ALLOWLIST" = "0" ]; then
    RESOLVED_PATH=$(cd "$(dirname "$FILE_PATH")" 2>/dev/null && echo "$(pwd)/$(basename "$FILE_PATH")" || echo "$FILE_PATH")
    CWD="$PWD"
    if [ "${RESOLVED_PATH#$CWD/}" = "$RESOLVED_PATH" ] && [ "$RESOLVED_PATH" != "$CWD" ]; then
      block "CWD外のファイル編集はブロックされています" "CWD: $CWD / ファイル: $FILE_PATH"
    fi
  fi

  BASENAME=$(basename "$FILE_PATH")

  # .env ファイルへの書き込みをブロック（.env.example, .env.sample は除外）
  if echo "$BASENAME" | grep -qE '^\.env($|\.)'; then
    if echo "$BASENAME" | grep -qE '\.(example|sample|template)$'; then
      exit 0
    fi
    block ".env ファイルの編集はブロックされています" "ファイル: $FILE_PATH"
  fi

  # credentials / secrets / 秘密鍵ファイルをブロック
  if echo "$FILE_PATH" | grep -qiE '(credentials|secrets|private[._-]?key|\.pem|\.key|\.p12|\.pfx)'; then
    block "機密情報ファイルの編集はブロックされています" "ファイル: $FILE_PATH"
  fi

  # グローバル設定ファイルの編集を警告
  if echo "$FILE_PATH" | grep -qE '(^|/)\.claude/settings\.json$'; then
    warn "Claude Code設定ファイルを編集しようとしています" "ファイル: $FILE_PATH"
  fi

  exit 0
fi

# =====================
# Bash 検証
# =====================
if [ "$TOOL_NAME" = "Bash" ]; then
  COMMAND=$(echo "$TOOL_INPUT" | jq -r '.command // empty' 2>/dev/null)

  if [ -z "$COMMAND" ]; then
    exit 0
  fi

  # --- テキスト引数を含むコマンドはスキップ ---
  # コミットメッセージやPR本文に危険パターンの文字列が含まれていても誤検知しない
  if echo "$COMMAND" | grep -qE '^(git\s+commit|git\s+tag|gh\s+pr\s+create|gh\s+issue\s+create)\s'; then
    exit 0
  fi

  # --- ブロック対象 ---

  # git push --force / -f を main/master へ
  if echo "$COMMAND" | grep -qE 'git\s+push\s+.*(-f|--force|--force-with-lease)'; then
    if echo "$COMMAND" | grep -qE '\s(main|master)(\s|$)'; then
      block "main/masterへのforce pushは禁止されています" "コマンド: $COMMAND"
    fi
  fi

  # rm -rf / ~ .. /* （ルート・ホーム・上位ディレクトリの削除）
  if echo "$COMMAND" | grep -qE 'rm\s+(-[a-zA-Z]*r[a-zA-Z]*f|(-[a-zA-Z]*f[a-zA-Z]*r))\s+(/|~|\.\.)(\s|$)'; then
    block "危険なディレクトリ削除は禁止されています" "コマンド: $COMMAND"
  fi

  # rm -rf * （ワイルドカード全削除、node_modules/dist/build/.next/out は除外）
  if echo "$COMMAND" | grep -qE 'rm\s+(-[a-zA-Z]*r[a-zA-Z]*f|(-[a-zA-Z]*f[a-zA-Z]*r))\s+\*'; then
    block "ワイルドカード全削除は禁止されています" "コマンド: $COMMAND"
  fi
  if echo "$COMMAND" | grep -qE 'rm\s+(-[a-zA-Z]*r[a-zA-Z]*f|(-[a-zA-Z]*f[a-zA-Z]*r))\s+\./\*'; then
    block "ワイルドカード全削除は禁止されています" "コマンド: $COMMAND"
  fi

  # rm -rf で安全な対象は許可（node_modules, dist, build, .next, out, coverage, tmp, __pycache__）
  # ↑ これらは上のワイルドカードチェックより先にrmコマンドで個別ディレクトリ名が指定されるため、
  #    ワイルドカード(*) が含まれず上のチェックに引っかからない → 自然に許可される

  # DROP DATABASE / DROP TABLE をブロック
  if echo "$COMMAND" | grep -qiE 'DROP\s+(DATABASE|TABLE|SCHEMA)'; then
    block "データベース/テーブル/スキーマの削除は禁止されています" "コマンド: $COMMAND"
  fi

  # curl/wget で .env や credentials の外部送信をブロック
  if echo "$COMMAND" | grep -qE '(curl|wget)\s'; then
    if echo "$COMMAND" | grep -qiE '(@\.env|\.env|credentials|secrets|private.key|\.pem)'; then
      block "機密ファイルの外部送信は禁止されています" "コマンド: $COMMAND"
    fi
  fi

  # --- 警告対象 ---

  # chmod 777
  if echo "$COMMAND" | grep -qE 'chmod\s+777'; then
    warn "chmod 777 は過剰な権限設定です。最小権限の原則を検討してください" "コマンド: $COMMAND"
  fi

  # git reset --hard （ローカル破壊）
  if echo "$COMMAND" | grep -qE 'git\s+reset\s+--hard'; then
    warn "git reset --hard はコミットされていない変更をすべて失います" "コマンド: $COMMAND"
  fi

  exit 0
fi

# =====================
# デフォルト: 許可
# =====================
exit 0
