#!/bin/bash
# audit-peer-drift.sh
# 全 peer の shared payload (hooks / common skills) が template 正本と整合するか audit。
# Read-only、 peer file には触らない。
#
# Usage:
#   ./scripts/audit-peer-drift.sh                  # text output, 全 peer
#   ./scripts/audit-peer-drift.sh --peer cowork    # 単 peer audit
#   ./scripts/audit-peer-drift.sh --json           # 機械可読 output
#   ./scripts/audit-peer-drift.sh --verbose        # 一致した item も出力
#
# exit code:
#   0 = 全 peer drift / miss なし
#   1 = drift 検出 (sha256 mismatch、 miss と同時発生時も 1 を返す)
#   2 = drift なし、 配布対象 item 未配置 (MISS) のみ

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# template 正本 source
HOOKS_SRC="$REPO_ROOT/.claude/hooks"
SKILLS_SRC="$REPO_ROOT/.claude/skills"

# 監査対象 (setup.sh SHARED_HOOKS + distribute-skills.sh COMMON_SKILLS と整合)
SHARED_HOOKS=(
  "block-main-push.sh"
)
COMMON_SKILLS=(
  "peer-id-lookup"
  "tier-judge"
  "plan-mode-policy"
)

# peer ターゲット: 課名|.claude ベースパス
# conductor + template は audit 対象外 (audit consumer + source 自己ループ回避)。
# occur課 2026-06-11 closed (Q3=a 組織再編 v2) → audit 対象から除外 (drift false-positive 回避)。
#   再開時は下記リストへ復活: occur|/Users/kimny/Dropbox/_DevProjects/_mued-occur/.claude
TARGETS="
write|/Users/kimny/Dropbox/_DevProjects/_contents-writing/.claude
SNS|/Users/kimny/Dropbox/_DevProjects/mued/threads-api/.claude
data|/Users/kimny/Dropbox/_DevProjects/_data-analysis/.claude
reserch|/Users/kimny/Dropbox/_DevProjects/_Reserch/.claude
LP|/Users/kimny/Dropbox/_DevProjects/_LandingPage/glasswerks-lp/.claude
blender|/Users/kimny/Dropbox/_DevProjects/_blender/.claude
mued|/Users/kimny/Dropbox/_DevProjects/mued/mued_v2/.claude
native|/Users/kimny/Dropbox/_DevProjects/mued/mued_v2/apps/.claude
freee|/Users/kimny/Dropbox/_DevProjects/freee-MCP/.claude
cowork|/Users/kimny/Dropbox/_DevProjects/_cowork/.claude
dsp|/Users/kimny/Dropbox/_DevProjects/_mued-dsp/.claude
growth|/Users/kimny/Dropbox/_DevProjects/_growth/.claude
"

# parse args
PEER_FILTER=""
JSON_MODE=false
VERBOSE=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --peer)
      PEER_FILTER="${2:-}"
      if [[ -z "$PEER_FILTER" ]]; then
        echo "--peer requires argument" >&2
        exit 2
      fi
      shift 2
      ;;
    --json) JSON_MODE=true; shift ;;
    --verbose) VERBOSE=true; shift ;;
    -h|--help)
      sed -n '2,16p' "$0"
      exit 0
      ;;
    *)
      echo "unknown option: $1" >&2
      exit 2
      ;;
  esac
done

# sha256 helper (macOS shasum / Linux sha256sum 両対応)
sha256_of() {
  local target="$1"
  if [[ -d "$target" ]]; then
    (cd "$target" && find . -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256) \
      | shasum -a 256 \
      | awk '{print $1}'
  elif [[ -f "$target" ]]; then
    shasum -a 256 "$target" | awk '{print $1}'
  else
    echo "MISSING"
  fi
}

DRIFT_COUNT=0
MISS_COUNT=0
OK_COUNT=0
JSON_ENTRIES=()

emit_entry() {
  local division="$1" item="$2" status="$3" src_hash="${4:-}" dst_hash="${5:-}"
  if $JSON_MODE; then
    if [[ -n "$src_hash" && -n "$dst_hash" ]]; then
      JSON_ENTRIES+=("{\"peer\":\"$division\",\"item\":\"$item\",\"status\":\"$status\",\"template_sha256\":\"$src_hash\",\"peer_sha256\":\"$dst_hash\"}")
    else
      JSON_ENTRIES+=("{\"peer\":\"$division\",\"item\":\"$item\",\"status\":\"$status\"}")
    fi
  else
    case "$status" in
      OK)
        if [[ $VERBOSE == true ]]; then
          echo "  [OK]    ${division}課: $item"
        fi
        ;;
      DRIFT) echo "  [DRIFT] ${division}課: $item (template:${src_hash:0:8} peer:${dst_hash:0:8})" ;;
      MISS)  echo "  [MISS]  ${division}課: $item 未配置" ;;
    esac
  fi
}

audit_item() {
  local division="$1" item_kind="$2" item_name="$3" src="$4" dst="$5"
  local item_label="${item_kind}/${item_name}"

  if [[ ! -e "$dst" ]]; then
    MISS_COUNT=$((MISS_COUNT + 1))
    emit_entry "$division" "$item_label" "MISS"
    return
  fi

  local src_hash dst_hash
  src_hash=$(sha256_of "$src")
  dst_hash=$(sha256_of "$dst")

  if [[ "$src_hash" == "$dst_hash" ]]; then
    OK_COUNT=$((OK_COUNT + 1))
    emit_entry "$division" "$item_label" "OK" "$src_hash" "$dst_hash"
  else
    DRIFT_COUNT=$((DRIFT_COUNT + 1))
    emit_entry "$division" "$item_label" "DRIFT" "$src_hash" "$dst_hash"
  fi
}

audit_peer() {
  local division="$1" peer_base="$2"

  if [[ ! -d "$peer_base" ]]; then
    if ! $JSON_MODE; then
      echo "  [SKIP] ${division}課: .claude dir なし ($peer_base)"
    fi
    return
  fi

  for hook in "${SHARED_HOOKS[@]}"; do
    audit_item "$division" "hooks" "$hook" "$HOOKS_SRC/$hook" "$peer_base/hooks/$hook"
  done

  for skill in "${COMMON_SKILLS[@]}"; do
    audit_item "$division" "skills" "$skill" "$SKILLS_SRC/$skill" "$peer_base/skills/$skill"
  done
}

# 事前確認: template 正本 source 存在
for hook in "${SHARED_HOOKS[@]}"; do
  if [[ ! -f "$HOOKS_SRC/$hook" ]]; then
    echo "[ERROR] template hook 不在: $HOOKS_SRC/$hook" >&2
    exit 2
  fi
done
for skill in "${COMMON_SKILLS[@]}"; do
  if [[ ! -d "$SKILLS_SRC/$skill" ]]; then
    echo "[ERROR] template skill 不在: $SKILLS_SRC/$skill" >&2
    exit 2
  fi
done

if ! $JSON_MODE; then
  echo "=== peer shared payload drift audit ==="
  echo "  hooks:  ${SHARED_HOOKS[*]}"
  echo "  skills: ${COMMON_SKILLS[*]}"
  [[ -n "$PEER_FILTER" ]] && echo "  filter: $PEER_FILTER"
  echo ""
fi

# here-string で subshell 化を回避 (counter 保持)
while IFS='|' read -r division peer_base; do
  [[ -z "$division" ]] && continue
  if [[ -n "$PEER_FILTER" && "$division" != "$PEER_FILTER" ]]; then
    continue
  fi
  audit_peer "$division" "$peer_base"
done <<< "$TARGETS"

if $JSON_MODE; then
  printf '{"summary":{"ok":%d,"drift":%d,"miss":%d},"entries":[' \
    "$OK_COUNT" "$DRIFT_COUNT" "$MISS_COUNT"
  for i in "${!JSON_ENTRIES[@]}"; do
    [[ $i -gt 0 ]] && printf ','
    printf '%s' "${JSON_ENTRIES[$i]}"
  done
  printf ']}\n'
else
  echo ""
  echo "=========================================="
  echo "summary: OK=${OK_COUNT}, DRIFT=${DRIFT_COUNT}, MISS=${MISS_COUNT}"
  echo "=========================================="
fi

if [[ $DRIFT_COUNT -gt 0 ]]; then
  exit 1
elif [[ $MISS_COUNT -gt 0 ]]; then
  exit 2
fi
exit 0
