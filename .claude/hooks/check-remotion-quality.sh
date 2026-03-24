#!/bin/bash
# Remotion Anti-Template Quality Check Hook
#
# Trigger: PostToolUse (Write|Edit) on videos/**/*.tsx files
# Action: Run static analysis for anti-template patterns → stderr warning

set -e

# Get the file path from tool input
FILE_PATH=""

if [ -n "$CLAUDE_TOOL_USE_INPUT" ]; then
  FILE_PATH=$(echo "$CLAUDE_TOOL_USE_INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('file_path', ''))
except:
    print('')
" 2>/dev/null || echo "")
fi

# Only check files in videos/ directories with .tsx extension
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

case "$FILE_PATH" in
  */videos/*.tsx|*/videos/*.ts)
    ;;
  *)
    exit 0
    ;;
esac

# Skip theme.ts, index.ts, config files
BASENAME=$(basename "$FILE_PATH")
case "$BASENAME" in
  theme.ts|index.ts|Root.tsx|*.config.ts)
    exit 0
    ;;
esac

# File must exist
if [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

WARNINGS=0
WARN_MSGS=""

warn() {
  WARNINGS=$((WARNINGS + 1))
  WARN_MSGS="${WARN_MSGS}\n  ⚠ $1"
}

# ─── 1. Uniform stagger ───
if grep -qE 'delay.*[=:{]\s*i\s*\*\s*[0-9]+' "$FILE_PATH" 2>/dev/null; then
  warn "UNIFORM_STAGGER: delay={i * N} detected. Use organic delays [0, 5, 13, 21]."
fi

# ─── 2. Same damping value 4+ times ───
DAMPING_COUNTS=$(grep -oE 'damping:\s*[0-9]+' "$FILE_PATH" 2>/dev/null | sort | uniq -c | sort -rn | head -1 || true)
if [ -n "$DAMPING_COUNTS" ]; then
  COUNT=$(echo "$DAMPING_COUNTS" | awk '{print $1}')
  VAL=$(echo "$DAMPING_COUNTS" | awk '{print $NF}')
  if [ "$COUNT" -gt 3 ] 2>/dev/null; then
    warn "UNIFORM_SPRING: Same ${VAL} used ${COUNT}x. Vary by element weight."
  fi
fi

# ─── 3. Only translateY reveals, no alternatives ───
GENERIC=$(grep -cE 'translateY.*spring|translateY.*interpolate' "$FILE_PATH" 2>/dev/null || true)
GENERIC=${GENERIC:-0}
MASK=$(grep -cE 'clipPath|clip-path' "$FILE_PATH" 2>/dev/null || true)
MASK=${MASK:-0}
STAGGER=$(grep -cE 'split.*map|\.charAt|charIndex|wordIndex' "$FILE_PATH" 2>/dev/null || true)
STAGGER=${STAGGER:-0}
if [ "$GENERIC" -gt 2 ] 2>/dev/null && [ "$MASK" -eq 0 ] 2>/dev/null && [ "$STAGGER" -eq 0 ] 2>/dev/null; then
  warn "GENERIC_REVEAL: ${GENERIC}x translateY reveals with no mask/stagger alternative."
fi

# ─── 4. Only WipeTransition ───
WIPE_COUNT=$(grep -c 'WipeTransition' "$FILE_PATH" 2>/dev/null || true)
WIPE_COUNT=${WIPE_COUNT:-0}
if [ "$WIPE_COUNT" -gt 2 ] 2>/dev/null; then
  OTHER=$(grep -cE 'FadeTransition|ScaleTransition|Hard.cut|clipPath.*inset' "$FILE_PATH" 2>/dev/null || true)
  OTHER=${OTHER:-0}
  if [ "$OTHER" -eq 0 ] 2>/dev/null; then
    warn "SINGLE_TRANSITION: WipeTransition used ${WIPE_COUNT}x. Mix transition types."
  fi
fi

# ─── 5. Long scene (>240 frames = 8s) ───
grep -oE 'durationInFrames=\{?[0-9]+' "$FILE_PATH" 2>/dev/null | grep -oE '[0-9]+' | while read -r dur; do
  if [ "$dur" -gt 240 ] 2>/dev/null; then
    SECS=$((dur / 30))
    warn "LONG_SCENE: ${SECS}s scene (${dur} frames). Consider breaking up."
  fi
done

# ─── Output ───
if [ "$WARNINGS" -gt 0 ]; then
  echo "" >&2
  echo "━━━ Remotion Quality Check: ${WARNINGS} warning(s) in $(basename "$FILE_PATH") ━━━" >&2
  echo -e "$WARN_MSGS" >&2
  echo "" >&2
  echo "  📖 .claude/skills/remotion/references/anti-template-checklist.md" >&2
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
  exit 1
fi

exit 0
