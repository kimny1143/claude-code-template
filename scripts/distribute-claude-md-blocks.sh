#!/usr/bin/env bash
# distribute-claude-md-blocks.sh — 経営部4課CLAUDE.md共通block同期script
#
# usage:
#   ./scripts/distribute-claude-md-blocks.sh --dry-run   # 差分確認 (default推奨)
#   ./scripts/distribute-claude-md-blocks.sh             # 実行 (各課CLAUDE.md書き換え)
#
# behavior:
#   - blocks/*.md (template課/.claude/skills/common-claude-md-blocks/) を source of truth として
#   - 各課 CLAUDE.md の <!-- COMMON-BLOCK-START: <id> --> ... <!-- COMMON-BLOCK-END: <id> --> 間を
#     対応する blocks/<id>.md 内容で完全置換する
#   - markerが無い課CLAUDE.mdはskip (Phase 0.2でmarker挿入PR完納後にdistribute有効化)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_REPO="$(cd "$SCRIPT_DIR/.." && pwd)"
BLOCKS_DIR="$TEMPLATE_REPO/.claude/skills/common-claude-md-blocks/blocks"

# 配布対象 (cognitive load v3 rollout 2026-05-18 で全 14 課展開、 marker未挿入 peer は skip logic で no-op)
# - 経営部4課: template / conductor / freee / cowork (Phase 2 0.1+0.2 既配布対象)
# - 残10課: mued / native / dsp / occur / SNS / write / LP / reserch / data / blender (Phase 2 0.3 = cognitive load v3 trial 5/19- 並行 marker挿入 PR)
declare -a TARGET_PEERS=(
    "$TEMPLATE_REPO/CLAUDE.md"
    "$HOME/Dropbox/_DevProjects/_conductor/CLAUDE.md"
    "$HOME/Dropbox/_DevProjects/freee-MCP/CLAUDE.md"
    "$HOME/Dropbox/_DevProjects/_cowork/CLAUDE.md"
    "$HOME/Dropbox/_DevProjects/mued/mued_v2/CLAUDE.md"
    "$HOME/Dropbox/_DevProjects/mued/mued_v2/apps/CLAUDE.md"
    "$HOME/Dropbox/_DevProjects/_mued-dsp/CLAUDE.md"
    "$HOME/Dropbox/_DevProjects/_mued-occur/CLAUDE.md"
    "$HOME/Dropbox/_DevProjects/mued/threads-api/CLAUDE.md"
    "$HOME/Dropbox/_DevProjects/_contents-writing/CLAUDE.md"
    "$HOME/Dropbox/_DevProjects/_LandingPage/glasswerks-lp/CLAUDE.md"
    "$HOME/Dropbox/_DevProjects/_Reserch/CLAUDE.md"
    "$HOME/Dropbox/_DevProjects/_data-analysis/CLAUDE.md"
    "$HOME/Dropbox/_DevProjects/_blender/CLAUDE.md"
)

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
fi

if [[ "$DRY_RUN" == "true" ]]; then
    echo "==> DRY RUN mode (no file changes)"
else
    echo "==> EXECUTE mode (file changes will be made)"
fi
echo ""

if [[ ! -d "$BLOCKS_DIR" ]]; then
    echo "ERROR: blocks dir not found: $BLOCKS_DIR" >&2
    exit 1
fi

# Python helperで marker-bounded section置換
python3 <<PYEOF
import re
import sys
from pathlib import Path

DRY_RUN = "$DRY_RUN" == "true"
BLOCKS_DIR = Path("$BLOCKS_DIR")
TARGETS = [Path(p) for p in [
$(printf '    "%s",\n' "${TARGET_PEERS[@]}")
]]

def block_id(path: Path) -> str:
    """e.g. blocks/04-org-structure.md → '04-org-structure'"""
    return path.stem


def load_blocks(blocks_dir: Path) -> dict[str, str]:
    blocks = {}
    for p in sorted(blocks_dir.glob("*.md")):
        blocks[block_id(p)] = p.read_text(encoding="utf-8").rstrip() + "\n"
    return blocks


def replace_section(content: str, block_id_str: str, block_content: str) -> tuple[str, bool]:
    """marker-bounded section置換、replaced=True if 置換実行された"""
    pattern = re.compile(
        r"(<!-- COMMON-BLOCK-START: " + re.escape(block_id_str) + r" -->.*?\n)"
        r"(.*?)"
        r"(\n<!-- COMMON-BLOCK-END: " + re.escape(block_id_str) + r" -->)",
        re.DOTALL,
    )
    match = pattern.search(content)
    if not match:
        return content, False
    new_section = (
        match.group(1)
        + "<!-- DO NOT EDIT THIS SECTION DIRECTLY. Source: template課/.claude/skills/common-claude-md-blocks/blocks/"
        + block_id_str
        + ".md -->\n"
        + "<!-- Distribute via: scripts/distribute-claude-md-blocks.sh -->\n\n"
        + block_content.rstrip() + "\n"
    )
    return content[:match.start()] + new_section + match.group(3) + content[match.end():], True


def process_target(target: Path, blocks: dict[str, str]) -> tuple[int, int]:
    """returns (n_replaced, n_skipped)"""
    if not target.is_file():
        print(f"  SKIP: {target} (not found)", file=sys.stderr)
        return 0, 0
    content = target.read_text(encoding="utf-8")
    original = content
    n_replaced = 0
    n_skipped = 0
    for bid, bcontent in blocks.items():
        new_content, replaced = replace_section(content, bid, bcontent)
        if replaced:
            n_replaced += 1
            content = new_content
        else:
            n_skipped += 1
    if content != original:
        if DRY_RUN:
            print(f"  WOULD UPDATE: {target} ({n_replaced} blocks)")
        else:
            target.write_text(content, encoding="utf-8")
            print(f"  UPDATED: {target} ({n_replaced} blocks)")
    else:
        print(f"  NO CHANGES: {target} ({n_skipped} blocks have no marker)")
    return n_replaced, n_skipped


blocks = load_blocks(BLOCKS_DIR)
print(f"Loaded {len(blocks)} blocks from {BLOCKS_DIR}:")
for bid in blocks:
    print(f"  - {bid}")
print()
print("Processing targets:")

total_replaced = 0
for target in TARGETS:
    print(f"\n{target}:")
    nr, ns = process_target(target, blocks)
    total_replaced += nr

print(f"\n==> Total: {total_replaced} block replacements across {len(TARGETS)} targets")
PYEOF

echo ""
echo "==> Done."
if [[ "$DRY_RUN" == "true" ]]; then
    echo "    Re-run without --dry-run to apply changes."
fi
