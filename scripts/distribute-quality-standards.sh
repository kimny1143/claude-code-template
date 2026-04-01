#!/bin/bash
# kimny判断基準メモリパック配布スクリプト
# 全課のメモリディレクトリに feedback_kimny_quality_standards.md を配布し、
# MEMORY.md にインデックスエントリを追加する。
#
# Usage: bash scripts/distribute-quality-standards.sh [--dry-run]

set -eo pipefail

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
  echo "[DRY RUN] 実際のファイル変更は行いません"
fi

PROJECTS_BASE="/Users/kimny/.claude/projects"
MEMORY_FILENAME="feedback_kimny_quality_standards.md"
MEMORY_INDEX_ENTRY="- [feedback_kimny_quality_standards.md](feedback_kimny_quality_standards.md) — kimny判断基準（声チェック/15年禁止/サイト分離/Hoo IP/運用ルール）"

# 全11課: 課名|プロジェクトディレクトリ名
DIVISIONS="
conductor|-Users-kimny-Dropbox--DevProjects--conductor
mued|-Users-kimny-Dropbox--DevProjects-mued-mued-v2
native|-Users-kimny-Dropbox--DevProjects-mued-mued-v2-apps
SNS|-Users-kimny-Dropbox--DevProjects-mued-threads-api
write|-Users-kimny-Dropbox--DevProjects--contents-writing
video|-Users-kimny-Dropbox--DevProjects--videos
LP|-Users-kimny-Dropbox--DevProjects--LandingPage-glasswerks-lp
freee|-Users-kimny-Dropbox--DevProjects-freee-MCP
data|-Users-kimny-Dropbox--DevProjects--data-analysis
template|-Users-kimny-Dropbox--DevProjects-claude-code-template
reserch|-Users-kimny-Dropbox--DevProjects--Reserch
"

# メモリファイルの内容（frontmatter付き）
read -r -d '' MEMORY_CONTENT << 'MEMEOF' || true
---
name: kimny判断基準 — 全課共通クオリティスタンダード
description: 声チェック/15年禁止/サイト分離/Hoo IP/運用ルール等。全課が共有すべきkimnyの判断基準
type: feedback
---

全課共通のkimny判断基準。詳細は `claude-code-template/docs/templates/kimny-quality-standards.md` を参照。

## コンテンツ品質
- **AI生成感排除**: 投稿はkimny声チェック必須。ドラフトは `_conductor/docs/drafts/` に格納
- **「15年」禁止**: キャリア年数を具体的数字で使わない。「ずっと」「手を動かしてきた」に置換
- **事実のみ**: 実名なし、比喩のこじつけなし
- **kimny=制作者**: 「発注者」と呼ばない

## サイト・プロダクト
- **glasswerks.jp=受託名刺** / **mued.jp=プロダクトファネル** — 混在させない
- **プロダクトサイトに開発プロセスのコピーを入れない** — 発信者プロフィール（Zenn/X/note/GitHub）とは別
- **MUEDは常に日英対応**

## マネタイズ
- **体験談=無料、テンプレ/手順書=有料**
- **原価率33%統一**（粗利67%）

## Hoo IP不変の骨子
1. フクロウ  2. 目がアナログテープ+メガネ  3. 線描  4. 「Hoo」  5. 「ほほう」

## 運用
- **kimnyへの質問はconductor経由**
- **勝手に切り上げない** — 終了タイミングは100% kimnyが決める
- **ユーザーに作業させない** — 各ピアが最大限を極める
- **全力で出し切る** — MAXプラン。トークン節約するな
- **シンプルな解決策を先に試す** — 構造的議論は問題解決後
- **SendMessage ≠ mcp__claude-peers__send_message** — 他課通信は後者

**Why:** 課によってkimnyの意図の理解度に差がある。全課が同じ判断基準を共有すべき
**How to apply:** コンテンツ作成・コピーライティング・設計判断・運用の全場面でこの基準を参照する
MEMEOF

UPDATED=0
SKIPPED=0

echo ""
echo "=== kimny判断基準メモリパック配布 ==="
echo ""

echo "$DIVISIONS" | while IFS='|' read -r division project_dir; do
  # 空行スキップ
  [[ -z "$division" ]] && continue

  memory_dir="${PROJECTS_BASE}/${project_dir}/memory"

  if [[ ! -d "$memory_dir" ]]; then
    echo "  [SKIP] ${division}課: メモリディレクトリなし"
    continue
  fi

  target_file="${memory_dir}/${MEMORY_FILENAME}"
  memory_index="${memory_dir}/MEMORY.md"

  # メモリファイルの配布
  if [[ -f "$target_file" ]]; then
    echo "  [UPDATE] ${division}課: ${MEMORY_FILENAME} を上書き"
  else
    echo "  [CREATE] ${division}課: ${MEMORY_FILENAME} を新規作成"
  fi

  if [[ "$DRY_RUN" == false ]]; then
    echo "$MEMORY_CONTENT" > "$target_file"
  fi

  # MEMORY.md にインデックスエントリを追加（未登録の場合のみ）
  if [[ -f "$memory_index" ]]; then
    if grep -q "feedback_kimny_quality_standards" "$memory_index"; then
      echo "           MEMORY.md エントリ済み"
    else
      echo "           MEMORY.md にエントリ追加"
      if [[ "$DRY_RUN" == false ]]; then
        if grep -q "^## Feedback" "$memory_index"; then
          # Feedbackセクションの直後に追加
          sed -i '' "/^## Feedback/a\\
${MEMORY_INDEX_ENTRY}
" "$memory_index"
        else
          # Feedbackセクションがなければ末尾に追加
          printf '\n## Feedback (共通)\n%s\n' "$MEMORY_INDEX_ENTRY" >> "$memory_index"
        fi
      fi
    fi
  else
    echo "           MEMORY.md 新規作成"
    if [[ "$DRY_RUN" == false ]]; then
      cat > "$memory_index" << INDEXEOF
# Memory Index

## Feedback
${MEMORY_INDEX_ENTRY}
INDEXEOF
    fi
  fi

done

echo ""
echo "=========================================="
echo "配布完了"
echo "=========================================="
