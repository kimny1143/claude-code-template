#!/usr/bin/env bash
# fanout-apply.sh — group A peer の CLAUDE.md に共通ブロック圧縮 fanout を適用する。
#
# cognitive load 圧縮 (PR #90) 後の fanout 専用ヘルパー。各 group A peer が自 repo で叩く想定。
# 機械的・同一の marker 手術を 1 本に集約し、手編集 drift / ミスを防止する (conductor 2026-05-29 (a)+(c))。
#
# 適用内容 (冪等):
#   1. block14 (14-conductor-active-judgment) marker pair を除去   — conductor 専用化
#   2. block18 の後に block19 (19-character-gate) marker pair を挿入 — 未挿入なら
#   3. CLAUDE.md 内の全 COMMON-BLOCK marker を圧縮 block 内容で fill
#   4. diff を表示する。 ★auto-commit はしない★ (peer が確認して自分で commit)
#
# usage:
#   ./scripts/fanout-apply.sh --dry-run                  # 書き込まず diff のみ (推奨: 最初に確認)
#   ./scripts/fanout-apply.sh                            # working tree に適用 + diff 表示 (commit は手動)
#   ./scripts/fanout-apply.sh --target /path/CLAUDE.md   # 対象 CLAUDE.md を明示 (default: $PWD/CLAUDE.md)
#   ./scripts/fanout-apply.sh --blocks-dir /path/blocks  # 圧縮 block source を明示 (default: 自動解決)
#
# 冪等性: 再実行しても同結果。block14 marker が既に無ければ skip、block19 marker が既に有れば挿入 skip、
#         fill は deterministic。 → 何度叩いても安全。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DRY_RUN=false
TARGET=""
BLOCKS_DIR=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run) DRY_RUN=true; shift ;;
        --target) TARGET="${2:-}"; shift 2 ;;
        --blocks-dir) BLOCKS_DIR="${2:-}"; shift 2 ;;
        -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) echo "ERROR: unknown arg: $1" >&2; exit 1 ;;
    esac
done

# --- 対象 CLAUDE.md 解決 ---
if [[ -z "$TARGET" ]]; then
    TARGET="$PWD/CLAUDE.md"
fi
if [[ ! -f "$TARGET" ]]; then
    echo "ERROR: target CLAUDE.md not found: $TARGET" >&2
    exit 1
fi

# --- 圧縮 block source 解決 (--blocks-dir > script相対 > fallback候補) ---
if [[ -z "$BLOCKS_DIR" ]]; then
    for cand in \
        "$SCRIPT_DIR/../.claude/skills/common-claude-md-blocks/blocks" \
        "$HOME/Dropbox/_DevProjects/claude-code-template/.claude/skills/common-claude-md-blocks/blocks" \
        "/Volumes/strage/_DevProjects/claude-code-template/.claude/skills/common-claude-md-blocks/blocks"; do
        if [[ -d "$cand" ]]; then BLOCKS_DIR="$(cd "$cand" && pwd)"; break; fi
    done
fi
if [[ -z "$BLOCKS_DIR" || ! -d "$BLOCKS_DIR" ]]; then
    echo "ERROR: blocks dir not found. --blocks-dir で明示してください" >&2
    exit 1
fi

echo "==> target:     $TARGET"
echo "==> blocks-dir: $BLOCKS_DIR"
echo "==> mode:       $([[ "$DRY_RUN" == true ]] && echo 'DRY RUN (no write)' || echo 'APPLY (write working tree, no commit)')"
echo ""

python3 - "$TARGET" "$BLOCKS_DIR" "$DRY_RUN" <<'PYEOF'
import re, sys, difflib
from pathlib import Path

TARGET = Path(sys.argv[1])
BLOCKS_DIR = Path(sys.argv[2])
DRY_RUN = sys.argv[3] == "true"

BLOCK14 = "14-conductor-active-judgment"
BLOCK18 = "18-judgment-request-contract"
BLOCK19 = "19-character-gate"

DO_NOT_EDIT = (
    "<!-- DO NOT EDIT THIS SECTION DIRECTLY. Source: "
    "template課/.claude/skills/common-claude-md-blocks/blocks/{bid}.md -->\n"
    "<!-- Distribute via: scripts/distribute-claude-md-blocks.sh -->\n\n"
)

def load_blocks():
    return {p.stem: p.read_text(encoding="utf-8").rstrip() + "\n"
            for p in sorted(BLOCKS_DIR.glob("*.md"))}

def remove_block14(content):
    """block14 marker pair (+間の content + 末尾の余分な空行) を除去。無ければ no-op。"""
    pat = re.compile(
        r"\n?<!-- COMMON-BLOCK-START: " + re.escape(BLOCK14) + r" -->.*?"
        r"<!-- COMMON-BLOCK-END: " + re.escape(BLOCK14) + r" -->\n?",
        re.DOTALL)
    new, n = pat.subn("\n", content)
    return new, n > 0

def insert_block19(content):
    """block18 END の後に block19 の空 marker pair を挿入。既に block19 marker があれば no-op。"""
    if re.search(r"COMMON-BLOCK-START: " + re.escape(BLOCK19), content):
        return content, False
    end18 = "<!-- COMMON-BLOCK-END: " + BLOCK18 + " -->"
    idx = content.find(end18)
    if idx == -1:
        return content, False  # block18 marker が無い peer は対象外
    insert_at = idx + len(end18)
    snippet = ("\n\n<!-- COMMON-BLOCK-START: " + BLOCK19 + " -->\n\n"
               "<!-- COMMON-BLOCK-END: " + BLOCK19 + " -->")
    return content[:insert_at] + snippet + content[insert_at:], True

def fill_marker(content, bid, body):
    """distribute-claude-md-blocks.sh と同一の置換ロジック (format 互換)。"""
    pat = re.compile(
        r"(<!-- COMMON-BLOCK-START: " + re.escape(bid) + r" -->.*?\n)"
        r"(.*?)"
        r"((?:\n)?<!-- COMMON-BLOCK-END: " + re.escape(bid) + r" -->)",
        re.DOTALL)
    m = pat.search(content)
    if not m:
        return content, False
    new_section = m.group(1) + DO_NOT_EDIT.format(bid=bid) + body.rstrip() + "\n"
    normalized_end = "\n<!-- COMMON-BLOCK-END: " + bid + " -->"
    return content[:m.start()] + new_section + normalized_end + content[m.end():], True

original = TARGET.read_text(encoding="utf-8")
content = original
blocks = load_blocks()

c14, did14 = remove_block14(content); content = c14
c19, did19 = insert_block19(content); content = c19
filled = []
for bid, body in blocks.items():
    if bid == BLOCK14:
        continue  # conductor 専用、group A には fill しない
    content, ok = fill_marker(content, bid, body)
    if ok:
        filled.append(bid.split("-")[0])

# レポート
print(f"  block14 marker 除去:   {'実施' if did14 else 'skip (既に無し)'}")
print(f"  block19 marker 挿入:   {'実施' if did19 else 'skip (既に有り or block18 marker 無し)'}")
print(f"  fill した marker:      {len(filled)} 個 ({','.join(filled) if filled else 'なし'})")
print("")

if content == original:
    print("  → 変更なし (既に適用済 = 冪等)。")
    sys.exit(0)

before, after = original.splitlines(), content.splitlines()
diff = list(difflib.unified_diff(before, after, lineterm="",
            fromfile=str(TARGET) + " (before)", tofile=str(TARGET) + " (after)"))
adds = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
dels = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
print(f"  行数: {len(before)} → {len(after)} (net {len(after)-len(before):+d}, -{dels}/+{adds})")
print("")
print("\n".join(diff))
print("")

if DRY_RUN:
    print("  [DRY RUN] 書き込みは行いませんでした。適用するには --dry-run を外して再実行。")
else:
    TARGET.write_text(content, encoding="utf-8")
    print("  [APPLIED] working tree を更新しました。★まだ commit していません★")
    print("  確認後: git add CLAUDE.md && git commit (Tier 1 docs) → merge → 行数を conductor に報告。")
PYEOF
