#!/bin/bash
# audit-skills-lock.sh
# .claude/skills/ 全 skill の sha256 を skills-lock.json と照合し、 drift / untracked を検出。
# --update --confirm 指定時のみ skills-lock.json に書き戻し (auto backup あり)。
#
# Usage:
#   ./scripts/audit-skills-lock.sh                          # audit only (default)
#   ./scripts/audit-skills-lock.sh --json                   # 機械可読
#   ./scripts/audit-skills-lock.sh --skill <name>           # 単 skill audit
#   ./scripts/audit-skills-lock.sh --verbose                # match item も表示
#   ./scripts/audit-skills-lock.sh --update --confirm       # baseline 一括登録 + hash 更新 (write)
#
# exit code:
#   0 = all tracked + hash match
#   1 = hash drift (locked vs actual mismatch)
#   2 = untracked skill exists (lock 未登録)
#
# sourceType default = "local" (per conductor 5/27 GO、 個別分類は後続 task)。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/.claude/skills"
LOCK_FILE="$REPO_ROOT/skills-lock.json"

# parse args
SKILL_FILTER=""
JSON_MODE=false
VERBOSE=false
UPDATE_MODE=false
CONFIRM=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --skill)
      SKILL_FILTER="${2:-}"
      if [[ -z "$SKILL_FILTER" ]]; then
        echo "--skill requires argument" >&2
        exit 2
      fi
      shift 2
      ;;
    --json) JSON_MODE=true; shift ;;
    --verbose) VERBOSE=true; shift ;;
    --update) UPDATE_MODE=true; shift ;;
    --confirm) CONFIRM=true; shift ;;
    -h|--help)
      sed -n '2,17p' "$0"
      exit 0
      ;;
    *)
      echo "unknown option: $1" >&2
      exit 2
      ;;
  esac
done

if $UPDATE_MODE && ! $CONFIRM; then
  echo "[ERROR] --update は --confirm との 2 flag 必須 (誤実行防止)" >&2
  exit 2
fi

# 事前確認
if [[ ! -d "$SKILLS_DIR" ]]; then
  echo "[ERROR] skills dir 不在: $SKILLS_DIR" >&2
  exit 2
fi
if [[ ! -f "$LOCK_FILE" ]]; then
  echo "[ERROR] lock file 不在: $LOCK_FILE" >&2
  exit 2
fi
if ! command -v jq >/dev/null 2>&1; then
  echo "[ERROR] jq が PATH にない (--update mode + JSON parse に必須)" >&2
  exit 2
fi

# sha256 helper (dir 全体 hash、 LC_ALL=C で sort order 固定、 macOS shasum / Linux sha256sum 両対応想定)
sha256_of_dir() {
  local target="$1"
  (cd "$target" && find . -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256) \
    | shasum -a 256 \
    | awk '{print $1}'
}

TRACKED_COUNT=0
DRIFT_COUNT=0
UNTRACKED_COUNT=0
UPDATED_COUNT=0
ADDED_COUNT=0
UNCHANGED_COUNT=0
JSON_ENTRIES=()

emit_entry() {
  local skill="$1" status="$2" locked_hash="${3:-}" actual_hash="${4:-}"
  if $JSON_MODE; then
    JSON_ENTRIES+=("{\"skill\":\"$skill\",\"status\":\"$status\",\"locked_sha256\":\"$locked_hash\",\"actual_sha256\":\"$actual_hash\"}")
  else
    case "$status" in
      TRACKED)
        if [[ $VERBOSE == true ]]; then
          echo "  [TRACKED]   $skill"
        fi
        ;;
      DRIFT)     echo "  [DRIFT]     $skill (locked:${locked_hash:0:8} actual:${actual_hash:0:8})" ;;
      UNTRACKED) echo "  [UNTRACKED] $skill: lock 未登録" ;;
      ADDED)     echo "  [ADDED]     $skill: hash=${actual_hash:0:12} sourceType=local" ;;
      UPDATED)   echo "  [UPDATED]   $skill: hash ${locked_hash:0:8}→${actual_hash:0:8}" ;;
      UNCHANGED)
        if [[ $VERBOSE == true ]]; then
          echo "  [UNCHANGED] $skill: hash unchanged"
        fi
        ;;
    esac
  fi
}

# 全 skill entry を enumerate
# -type d = 通常 skill dir、 -type l = .agents/skills/ への symlink (Codex mirror、 freee-api-skill 等)
list_skills() {
  find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 \( -type d -o -type l \) \
    | sed "s|^$SKILLS_DIR/||" \
    | LC_ALL=C sort
}

# audit mode: 各 skill の actual hash vs lock の computedHash 照合
audit_skills() {
  while IFS= read -r skill; do
    [[ -z "$skill" ]] && continue
    if [[ -n "$SKILL_FILTER" && "$skill" != "$SKILL_FILTER" ]]; then
      continue
    fi

    local actual_hash locked_hash
    actual_hash=$(sha256_of_dir "$SKILLS_DIR/$skill")
    locked_hash=$(jq -r --arg s "$skill" '.skills[$s].computedHash // ""' "$LOCK_FILE")

    if [[ -z "$locked_hash" ]]; then
      UNTRACKED_COUNT=$((UNTRACKED_COUNT + 1))
      emit_entry "$skill" "UNTRACKED" "" "$actual_hash"
    elif [[ "$locked_hash" == "$actual_hash" ]]; then
      TRACKED_COUNT=$((TRACKED_COUNT + 1))
      emit_entry "$skill" "TRACKED" "$locked_hash" "$actual_hash"
    else
      DRIFT_COUNT=$((DRIFT_COUNT + 1))
      emit_entry "$skill" "DRIFT" "$locked_hash" "$actual_hash"
    fi
  done < <(list_skills)
}

# update mode: lock file を rewrite (backup あり)
update_skills() {
  local timestamp
  timestamp=$(date +%Y%m%d-%H%M%S)
  local backup="$LOCK_FILE.bak.$timestamp"
  cp "$LOCK_FILE" "$backup"
  echo "  [BACKUP]    $backup"

  local today
  today=$(date +%Y-%m-%d)
  local tmp="$LOCK_FILE.tmp.$$"

  cp "$LOCK_FILE" "$tmp"

  while IFS= read -r skill; do
    [[ -z "$skill" ]] && continue
    if [[ -n "$SKILL_FILTER" && "$skill" != "$SKILL_FILTER" ]]; then
      continue
    fi

    local actual_hash locked_hash exists
    actual_hash=$(sha256_of_dir "$SKILLS_DIR/$skill")
    exists=$(jq -r --arg s "$skill" '.skills | has($s) | tostring' "$tmp")
    locked_hash=$(jq -r --arg s "$skill" '.skills[$s].computedHash // ""' "$tmp")

    if [[ "$exists" == "false" ]]; then
      # 新規 entry 追加 (sourceType=local default)
      jq --arg s "$skill" --arg h "$actual_hash" --arg d "$today" '
        .skills[$s] = {
          "source": "claude-code-template",
          "sourceType": "local",
          "computedHash": $h,
          "distributedAt": $d,
          "distributedBy": "scripts/audit-skills-lock.sh --update"
        }
      ' "$tmp" > "$tmp.new" && mv "$tmp.new" "$tmp"
      ADDED_COUNT=$((ADDED_COUNT + 1))
      emit_entry "$skill" "ADDED" "" "$actual_hash"
    elif [[ "$locked_hash" != "$actual_hash" ]]; then
      # hash 更新 (distributedAt は維持、 audit hash 更新は distributedBy で履歴明示)
      jq --arg s "$skill" --arg h "$actual_hash" --arg d "$today" '
        .skills[$s].computedHash = $h
        | .skills[$s].lastAuditedAt = $d
        | .skills[$s].lastAuditedBy = "scripts/audit-skills-lock.sh --update"
      ' "$tmp" > "$tmp.new" && mv "$tmp.new" "$tmp"
      UPDATED_COUNT=$((UPDATED_COUNT + 1))
      emit_entry "$skill" "UPDATED" "$locked_hash" "$actual_hash"
    else
      UNCHANGED_COUNT=$((UNCHANGED_COUNT + 1))
      emit_entry "$skill" "UNCHANGED" "$locked_hash" "$actual_hash"
    fi
  done < <(list_skills)

  mv "$tmp" "$LOCK_FILE"
}

if ! $JSON_MODE; then
  if $UPDATE_MODE; then
    echo "=== skills-lock.json update (--confirm) ==="
  else
    echo "=== skills-lock.json audit ==="
  fi
  [[ -n "$SKILL_FILTER" ]] && echo "  filter: $SKILL_FILTER"
  echo ""
fi

if $UPDATE_MODE; then
  update_skills
else
  audit_skills
fi

if $JSON_MODE; then
  printf '{"summary":{"tracked":%d,"drift":%d,"untracked":%d,"updated":%d,"added":%d,"unchanged":%d},"entries":[' \
    "$TRACKED_COUNT" "$DRIFT_COUNT" "$UNTRACKED_COUNT" "$UPDATED_COUNT" "$ADDED_COUNT" "$UNCHANGED_COUNT"
  for i in "${!JSON_ENTRIES[@]}"; do
    [[ $i -gt 0 ]] && printf ','
    printf '%s' "${JSON_ENTRIES[$i]}"
  done
  printf ']}\n'
else
  echo ""
  echo "=========================================="
  if $UPDATE_MODE; then
    echo "summary: ADDED=${ADDED_COUNT}, UPDATED=${UPDATED_COUNT}, UNCHANGED=${UNCHANGED_COUNT}"
  else
    echo "summary: TRACKED=${TRACKED_COUNT}, DRIFT=${DRIFT_COUNT}, UNTRACKED=${UNTRACKED_COUNT}"
  fi
  echo "=========================================="
fi

# exit code は audit mode 時のみ意味あり (update mode は常 0)
if ! $UPDATE_MODE; then
  if [[ $DRIFT_COUNT -gt 0 ]]; then
    exit 1
  elif [[ $UNTRACKED_COUNT -gt 0 ]]; then
    exit 2
  fi
fi
exit 0
