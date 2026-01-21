#!/bin/bash
# Claude Code 共有設定のシンボリックリンクを作成
# Usage: ./setup.sh [--template /path/to/template]

set -e

# デフォルトテンプレートパス
TEMPLATE="${CLAUDE_TEMPLATE:-$HOME/Dropbox/_DevProjects/claude-code-template/.claude}"
TARGET=".claude"

# 引数解析
while [[ $# -gt 0 ]]; do
  case $1 in
    --template|-t)
      TEMPLATE="$2/.claude"
      shift 2
      ;;
    --help|-h)
      echo "Usage: $0 [--template /path/to/template]"
      echo ""
      echo "Options:"
      echo "  -t, --template PATH  Path to claude-code-template directory"
      echo "  -h, --help           Show this help message"
      echo ""
      echo "Environment variables:"
      echo "  CLAUDE_TEMPLATE      Default template .claude path"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo "╔════════════════════════════════════════════╗"
echo "║  Claude Code Shared Configuration Setup   ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "Template: $TEMPLATE"
echo "Target:   $(pwd)/$TARGET"
echo ""

# テンプレート存在確認
if [ ! -d "$TEMPLATE" ]; then
  echo "❌ Error: Template not found at $TEMPLATE"
  echo ""
  echo "Please either:"
  echo "  1. Set CLAUDE_TEMPLATE environment variable"
  echo "  2. Use --template flag: $0 --template /path/to/claude-code-template"
  exit 1
fi

# ディレクトリ作成
mkdir -p "$TARGET"/{commands,skills,agents,hooks}

# 共有コマンドをリンク
echo "📁 Linking commands..."
SHARED_COMMANDS=(commit pr build-fix security ship learn)
for cmd in "${SHARED_COMMANDS[@]}"; do
  src="$TEMPLATE/commands/$cmd.md"
  dst="$TARGET/commands/$cmd.md"
  if [ -f "$src" ]; then
    rm -f "$dst"
    ln -s "$src" "$dst"
    echo "   ✓ $cmd.md"
  else
    echo "   ⚠ $cmd.md (not in template)"
  fi
done

# 共有スキルをリンク
echo ""
echo "📁 Linking skills..."
SHARED_SKILLS=(
  tdd
  coding-rules
  backend-patterns
  ui-ux-pro-max
  mcp
  hooks
  git-worktree
  lp-optimizer
  ux-psychology
  marketing-audit
  pricing-strategy
)
for skill in "${SHARED_SKILLS[@]}"; do
  src="$TEMPLATE/skills/$skill"
  dst="$TARGET/skills/$skill"
  if [ -d "$src" ]; then
    # シンボリックリンクの場合は削除して再作成
    if [ -L "$dst" ]; then
      rm -f "$dst"
      ln -s "$src" "$dst"
      echo "   ✓ $skill"
    # ディレクトリが存在する場合はスキップ（プロジェクト固有）
    elif [ -d "$dst" ]; then
      echo "   ⊘ $skill (local directory exists)"
    else
      ln -s "$src" "$dst"
      echo "   ✓ $skill"
    fi
  else
    echo "   ⚠ $skill (not in template)"
  fi
done

# 共有エージェントをリンク
if [ -d "$TEMPLATE/agents" ] && [ "$(ls -A "$TEMPLATE/agents" 2>/dev/null)" ]; then
  echo ""
  echo "📁 Linking agents..."
  for agent in "$TEMPLATE/agents"/*; do
    [ -e "$agent" ] || continue
    name=$(basename "$agent")
    src="$agent"
    dst="$TARGET/agents/$name"
    if [ -L "$dst" ]; then
      rm -f "$dst"
      ln -s "$src" "$dst"
      echo "   ✓ $name"
    elif [ -e "$dst" ]; then
      echo "   ⊘ $name (local exists)"
    else
      ln -s "$src" "$dst"
      echo "   ✓ $name"
    fi
  done
fi

echo ""
echo "════════════════════════════════════════════"
echo "✅ Setup complete!"
echo ""
echo "Linked: Shared commands, skills, agents from template"
echo "Preserved: Project-specific configurations"
echo ""
echo "Next steps:"
echo "  1. Add project-specific skills to $TARGET/skills/"
echo "  2. Configure $TARGET/settings.local.json"
echo "  3. Create CLAUDE.md from CLAUDE.md.template"
