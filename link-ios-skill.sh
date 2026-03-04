#!/bin/bash
# link-ios-skill.sh
# iOS App Store submission スキルとコマンドを任意のプロジェクトにリンク
#
# Usage: ./link-ios-skill.sh /path/to/project

TEMPLATE_DIR="/Users/kimny/Dropbox/_DevProjects/claude-code-template"

if [ -z "$1" ]; then
  echo "Usage: $0 /path/to/project"
  echo ""
  echo "Example:"
  echo "  $0 /Users/kimny/Dropbox/_DevProjects/my-app"
  exit 1
fi

PROJECT_DIR="$1"

# Validate project directory
if [ ! -d "$PROJECT_DIR" ]; then
  echo "Error: Directory does not exist: $PROJECT_DIR"
  exit 1
fi

# Create .claude directories if not exist
mkdir -p "$PROJECT_DIR/.claude/commands"
mkdir -p "$PROJECT_DIR/.claude/skills"

# Create symlinks
ln -sf "$TEMPLATE_DIR/.claude/commands/ios.md" "$PROJECT_DIR/.claude/commands/ios.md"
ln -sf "$TEMPLATE_DIR/.claude/skills/ios-app-store-submission" "$PROJECT_DIR/.claude/skills/ios-app-store-submission"

echo "✅ Linked iOS submission skill to: $PROJECT_DIR"
echo ""
echo "Added:"
echo "  - /ios command"
echo "  - ios-app-store-submission skill"
echo ""
echo "Verify:"
ls -la "$PROJECT_DIR/.claude/commands/ios.md"
ls -la "$PROJECT_DIR/.claude/skills/ios-app-store-submission"
