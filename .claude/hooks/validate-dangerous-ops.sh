#!/bin/bash
# PreToolUse Hook: 危険な操作の事前検証
#
# 発火条件: PreToolUse (Write, Edit, Bash)
# 動作: 危険なパターンを検知 → stderrに警告 → exit 2 (ブロック)
#
# 環境変数:
#   TOOL_NAME: ツール名 (Write, Edit, Bash)
#   TOOL_INPUT: JSON形式の入力パラメータ

set -e

# 入力がない場合は許可
if [ -z "$TOOL_INPUT" ]; then
  exit 0
fi

# jqがない場合は許可（フェイルセーフ）
if ! command -v jq &> /dev/null; then
  exit 0
fi

# ツール別の検証
case "$TOOL_NAME" in
  "Write"|"Edit")
    # ファイルパスを取得
    FILE_PATH=$(echo "$TOOL_INPUT" | jq -r '.file_path // empty' 2>/dev/null)

    if [ -z "$FILE_PATH" ]; then
      exit 0
    fi

    # .env ファイルへの書き込み警告
    if echo "$FILE_PATH" | grep -qE '\.env($|\.local|\.production|\.development)'; then
      echo "" >&2
      echo "⚠️  警告: 環境変数ファイルを編集しようとしています" >&2
      echo "   ファイル: $FILE_PATH" >&2
      echo "   このファイルはGitにコミットされるべきではありません。" >&2
      echo "" >&2
      # 警告のみ、ブロックはしない
      exit 0
    fi

    # credentials/secrets ファイルへの書き込み警告
    if echo "$FILE_PATH" | grep -qiE '(credentials|secrets|private.*key|\.pem|\.key)'; then
      echo "" >&2
      echo "🔐 警告: 機密情報ファイルを編集しようとしています" >&2
      echo "   ファイル: $FILE_PATH" >&2
      echo "" >&2
      exit 0
    fi
    ;;

  "Bash")
    # コマンドを取得
    COMMAND=$(echo "$TOOL_INPUT" | jq -r '.command // empty' 2>/dev/null)

    if [ -z "$COMMAND" ]; then
      exit 0
    fi

    # git push --force をブロック (main/master)
    if echo "$COMMAND" | grep -qE 'git\s+push\s+.*--force.*\s+(main|master)'; then
      echo "" >&2
      echo "🚫 ブロック: main/masterへのforce pushは禁止されています" >&2
      echo "   コマンド: $COMMAND" >&2
      echo "" >&2
      exit 2  # ブロック
    fi

    # git push -f も同様
    if echo "$COMMAND" | grep -qE 'git\s+push\s+-f.*\s+(main|master)'; then
      echo "" >&2
      echo "🚫 ブロック: main/masterへのforce pushは禁止されています" >&2
      echo "   コマンド: $COMMAND" >&2
      echo "" >&2
      exit 2  # ブロック
    fi

    # rm -rf / または重要ディレクトリの削除をブロック
    if echo "$COMMAND" | grep -qE 'rm\s+-rf?\s+/($|\s)'; then
      echo "" >&2
      echo "🚫 ブロック: ルートディレクトリの削除は禁止されています" >&2
      echo "" >&2
      exit 2  # ブロック
    fi

    # DROP DATABASE / DROP TABLE を警告
    if echo "$COMMAND" | grep -qiE 'DROP\s+(DATABASE|TABLE)'; then
      echo "" >&2
      echo "⚠️  警告: データベース削除コマンドを実行しようとしています" >&2
      echo "   コマンド: $COMMAND" >&2
      echo "   本番環境でないことを確認してください。" >&2
      echo "" >&2
      exit 0  # 警告のみ
    fi
    ;;
esac

# デフォルトは許可
exit 0
