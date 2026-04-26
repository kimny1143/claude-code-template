#!/bin/bash
# distribute-skills.sh
# 全課共通必須スキル3件（peer-id-lookup / tier-judge / plan-mode-policy）を配布する
# 課固有 skill は触らず、配布対象 skill のみ rsync で同期
# 既存 distribute-quality-standards.sh / distribute-settings-allow.sh と同パターン
#
# Usage:
#   ./scripts/distribute-skills.sh --dry-run   # 差分プレビュー（rsync -n）
#   ./scripts/distribute-skills.sh              # 本番実行
#
# 仕様:
#   - 配布対象 skill が template 課マスタに無い場合は SKIP
#   - 配布先課に対象 skill ディレクトリが無い場合は新規作成
#   - rsync --delete は対象 skill ディレクトリ内に限定（他 skill には影響なし）
#   - skills-lock.json の更新は手動（段階1ではスコープ外）

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_BASE="$REPO_ROOT/.claude/skills"

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
  echo "=== DRY RUN MODE ==="
  echo ""
fi

# 配布対象 skill（共通必須のみ、課固有は対象外）
COMMON_SKILLS=(
  "peer-id-lookup"
  "tier-judge"
  "plan-mode-policy"
)

# 配布対象課（template課自身は除外、全10課）
# 課名|.claude/skills絶対パス
TARGETS="
conductor|/Users/kimny/Dropbox/_DevProjects/_conductor/.claude/skills
write|/Users/kimny/Dropbox/_DevProjects/_contents-writing/.claude/skills
cowork|/Users/kimny/Dropbox/_DevProjects/_cowork/.claude/skills
data|/Users/kimny/Dropbox/_DevProjects/_data-analysis/.claude/skills
LP|/Users/kimny/Dropbox/_DevProjects/_LandingPage/glasswerks-lp/.claude/skills
reserch|/Users/kimny/Dropbox/_DevProjects/_Reserch/.claude/skills
freee|/Users/kimny/Dropbox/_DevProjects/freee-MCP/.claude/skills
mued|/Users/kimny/Dropbox/_DevProjects/mued/mued_v2/.claude/skills
native|/Users/kimny/Dropbox/_DevProjects/mued/mued_v2/apps/.claude/skills
SNS|/Users/kimny/Dropbox/_DevProjects/mued/threads-api/.claude/skills
"

UPDATED=0
CREATED=0
SKIPPED=0

echo "=== 共通必須スキル配布 ==="
echo "配布対象: ${COMMON_SKILLS[*]}"
echo ""

# 配布対象 skill のソース存在確認（事前チェック）
for skill in "${COMMON_SKILLS[@]}"; do
  if [[ ! -d "$SKILLS_BASE/$skill" ]]; then
    echo "  [ERROR] template課マスタに $skill が存在しません: $SKILLS_BASE/$skill"
    echo "  処理を中断します"
    exit 1
  fi
done

echo "$TARGETS" | while IFS='|' read -r division target_dir; do
  # 空行スキップ
  [[ -z "$division" ]] && continue

  if [[ ! -d "$target_dir" ]]; then
    echo "  [SKIP] ${division}課: skills ディレクトリなし ($target_dir)"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  echo "→ ${division}課 ($target_dir)"

  for skill in "${COMMON_SKILLS[@]}"; do
    src="$SKILLS_BASE/$skill"
    dst="$target_dir/$skill"

    if [[ -d "$dst" ]]; then
      action="UPDATE"
    else
      action="CREATE"
    fi

    if $DRY_RUN; then
      # dry-run: rsync -n で差分のみ表示
      # 配布先ディレクトリが無い場合は新規作成相当の差分として表示
      if [[ ! -d "$dst" ]]; then
        echo "  [${action} DRY] $skill （新規作成、$(find "$src" -type f | wc -l | tr -d ' ') ファイル予定）"
      else
        # rsync -avn の出力から実差分行を抽出（grep失敗時は0件として扱う）
        diff_lines=$(rsync -avn --delete "$src/" "$dst/" 2>/dev/null | grep -E '^>f|^cd|^deleting' || true)
        diff_count=$(printf '%s' "$diff_lines" | grep -c . || true)
        echo "  [${action} DRY] $skill （差分件数: ${diff_count:-0}）"
        if [[ -n "$diff_lines" ]]; then
          printf '%s\n' "$diff_lines" | sed 's/^/    /'
        fi
      fi
    else
      mkdir -p "$dst"
      rsync -av --delete "$src/" "$dst/" > /dev/null
      echo "  [${action}] $skill"
    fi
  done
  echo ""
done

echo "=========================================="
if $DRY_RUN; then
  echo "DRY RUN 完了"
  echo ""
  echo "実行する場合: $0  （--dry-run なし）"
else
  echo "配布完了"
  echo ""
  echo "次の手動アクション:"
  echo "  1. skills-lock.json のバージョン記録更新（必要に応じて）"
  echo "  2. 配布結果を conductor へ報告（claude-peers）"
fi
echo "=========================================="
