#!/bin/bash
# distribute-settings-allow.sh
# Base templateのallowルールを全課のsettings.local.jsonにマージ配布する
# 課固有のルール（hooks, deny, 固有allow, enabledMcpjsonServers等）は保持
#
# Usage:
#   ./scripts/distribute-settings-allow.sh --dry-run   # 差分プレビュー
#   ./scripts/distribute-settings-allow.sh              # 本番実行

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BASE_TEMPLATE="$REPO_ROOT/docs/templates/settings-local-base.json"

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
  echo "=== DRY RUN MODE ==="
  echo ""
fi

# 全課のsettings.local.jsonパス（経営部4課+プロダクト部2課+マーケ部4課+分析研究部2課 = 12課構成、うち_cowork/mued_v2は複数ディレクトリ未統合のため個別追加）
TARGETS=(
  "/Users/kimny/Dropbox/_DevProjects/_conductor/.claude/settings.local.json"
  "/Users/kimny/Dropbox/_DevProjects/_contents-writing/.claude/settings.local.json"
  "/Users/kimny/Dropbox/_DevProjects/_cowork/.claude/settings.local.json"
  "/Users/kimny/Dropbox/_DevProjects/_data-analysis/.claude/settings.local.json"
  "/Users/kimny/Dropbox/_DevProjects/_LandingPage/glasswerks-lp/.claude/settings.local.json"
  "/Users/kimny/Dropbox/_DevProjects/_Reserch/.claude/settings.local.json"
  "/Users/kimny/Dropbox/_DevProjects/_videos/.claude/settings.local.json"
  "/Users/kimny/Dropbox/_DevProjects/claude-code-template/.claude/settings.local.json"
  "/Users/kimny/Dropbox/_DevProjects/freee-MCP/.claude/settings.local.json"
  "/Users/kimny/Dropbox/_DevProjects/mued/mued_v2/.claude/settings.local.json"
  "/Users/kimny/Dropbox/_DevProjects/mued/threads-api/.claude/settings.local.json"
)

# 課名抽出（パスから）
get_division_name() {
  local path="$1"
  # _DevProjects/ 以降から .claude/ 手前まで
  echo "$path" | sed 's|.*/Dropbox/_DevProjects/||; s|/\.claude/.*||'
}

TOTAL_UPDATED=0
TOTAL_SKIPPED=0

for target in "${TARGETS[@]}"; do
  division=$(get_division_name "$target")

  if [[ ! -f "$target" ]]; then
    echo "[$division] SKIP: ファイルが存在しません: $target"
    TOTAL_SKIPPED=$((TOTAL_SKIPPED + 1))
    continue
  fi

  echo "[$division] 処理中..."

  # Python3でJSON変換
  result=$(python3 -c '
import json
import sys
import re

base_path = sys.argv[1]
target_path = sys.argv[2]
dry_run = sys.argv[3] == "true"

with open(base_path) as f:
    base = json.load(f)

with open(target_path) as f:
    target = json.load(f)

base_allow = base["permissions"]["allow"]
target_allow = target.get("permissions", {}).get("allow", [])

# --- 置換対象パターン ---
# git個別サブコマンド → Bash(git *) で統一
git_subcmd_pattern = re.compile(r"^Bash\(git [a-z-]+ \*\)$")
# gh個別サブコマンド → Bash(gh *) で統一
gh_subcmd_pattern = re.compile(r"^Bash\(gh [a-z-]+ \*\)$")
# npm個別サブコマンド → Bash(npm *) で統一
npm_subcmd_pattern = re.compile(r"^Bash\(npm [a-z]+ [\*:].*\)$")

# --- 課固有ルールを抽出 ---
# base templateに含まれるルール（変換前の旧ルール含む）を特定し、
# それ以外を課固有として保持する

# 旧base templateにあったルール（git/gh個別、共通ユーティリティ等）
base_allow_set = set(base_allow)

removed = []
kept_custom = []

for rule in target_allow:
    if git_subcmd_pattern.match(rule):
        removed.append(rule)
    elif gh_subcmd_pattern.match(rule):
        removed.append(rule)
    elif npm_subcmd_pattern.match(rule):
        removed.append(rule)
    elif rule in base_allow_set:
        # base templateに既にあるのでスキップ（重複回避）
        pass
    else:
        kept_custom.append(rule)

# --- 新しいallowリスト構築 ---
# base template + 課固有（baseに含まれないもの）
new_allow = list(base_allow) + kept_custom

# --- 結果構築 ---
target["permissions"]["allow"] = new_allow

# deny はbase templateのものを確実に含める（課固有denyも保持）
base_deny = base["permissions"]["deny"]
target_deny = target.get("permissions", {}).get("deny", [])
base_deny_set = set(base_deny)
extra_deny = [d for d in target_deny if d not in base_deny_set]
target["permissions"]["deny"] = base_deny + extra_deny

# --- レポート ---
added_count = len([r for r in base_allow if r not in set(target_allow)])
removed_count = len(removed)

report_lines = []
report_lines.append(f"  removed: {removed_count} (git/gh/npm個別ルール)")
report_lines.append(f"  added:   {added_count} (baseから新規追加)")
report_lines.append(f"  custom:  {len(kept_custom)} (課固有ルール保持)")

if removed:
    report_lines.append("  --- 削除されるルール ---")
    for r in removed:
        report_lines.append(f"    - {r}")

new_rules = [r for r in base_allow if r not in set(target_allow)]
if new_rules:
    report_lines.append("  --- 追加されるルール ---")
    for r in new_rules:
        report_lines.append(f"    + {r}")

if kept_custom:
    report_lines.append("  --- 課固有ルール（保持） ---")
    for r in kept_custom:
        report_lines.append(f"    ~ {r}")

if extra_deny:
    report_lines.append("  --- 課固有deny（保持） ---")
    for d in extra_deny:
        report_lines.append(f"    ! {d}")

print("\n".join(report_lines))

if not dry_run:
    with open(target_path, "w") as f:
        json.dump(target, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("  => WRITTEN")
else:
    print("  => DRY RUN (書き込みスキップ)")

# Exit code: 1 if changes, 0 if no changes
sys.exit(1 if (removed_count > 0 or added_count > 0) else 0)
' "$BASE_TEMPLATE" "$target" "$DRY_RUN" 2>&1) || true

  echo "$result"

  if echo "$result" | grep -q "WRITTEN\|changes"; then
    TOTAL_UPDATED=$((TOTAL_UPDATED + 1))
  fi

  echo ""
done

echo "=== 完了 ==="
echo "更新: $TOTAL_UPDATED 課"
echo "スキップ: $TOTAL_SKIPPED 課"

if $DRY_RUN; then
  echo ""
  echo "本番実行するには: ./scripts/distribute-settings-allow.sh"
fi
