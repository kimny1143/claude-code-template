# Claude Code Template Ops Improvement — 2026-05-12

## 実施理由

`CLAUDE.md` が348行まで肥大化し、Claude Code起動時に毎回読むべき内容と、必要時だけ読めばよい配布手順・過去判断ログ・hook/skill詳細が混在していたため整理した。

## 前提

- このワークスペースは Claude Code 主運用
- 全peer共有の `.claude/skills`, `.claude/hooks`, `.claude/agents`, `.claude/commands`, settings template, distribution scripts の正本
- 他peer側の共有物はこのtemplateから配布・参照される派生物
- 他peerワークスペースは変更しない

## 実施内容

- `CLAUDE.md` を常時読むべき内容へ圧縮
- `AGENTS.md` をCodex等の副次利用向け薄いadapterへ変更
- 詳細運用を `docs/template-ops-runbook.md` へ分離
- 事後報告として本ファイルを追加し、`CLAUDE.md` 末尾からimport
- template管理専用skill `common-claude-md-blocks` に `disable-model-invocation: true` を追加

## 追加/変更したtemplate管理専用skills

- 変更: `.claude/skills/common-claude-md-blocks/SKILL.md`
- 追加skillなし。全peerへ不要なtemplate管理手順を誤配布しないため、今回は新規skillではなくdocsに詳細手順を置いた

## 変更したshared skills / hooks / agents / commands

- shared hooks: 今回の整理では変更なし。作業開始時点で `.claude/hooks/block-main-push.sh` に既存未コミット差分あり
- shared agents: 変更なし
- shared commands: 変更なし
- public shared skills: 変更なし
- template管理専用skillのみvisibilityを手動起動専用へ変更

## 変更しなかった共有項目

- `setup.sh` の `SHARED_COMMANDS`, `SHARED_SKILLS`, `SHARED_HOOKS`
- `scripts/distribute-*.sh` の対象範囲
- `.claude/settings.local.json.example`
- `docs/templates/settings-local-base.json`
- `skills-lock.json`
- symlink構成
- `premium/`
- 他peerワークスペース

## 全peerへ波及する可能性

今回の変更はこのrepo内の運用正本整理が中心。自動配布対象のpayloadと配布script対象範囲は変えていないため、即時に他peerへファイル変更は波及しない。

ただし `CLAUDE.md` はtemplate課のClaude Code起動時context、`AGENTS.md` はCodex等副次利用時contextに影響する。`common-claude-md-blocks` は手動起動専用になり、自動選択による配布系操作の誤発火リスクを下げる。

## 配布前に必要な検証

- `git diff --check`
- 変更ファイル一覧の確認
- `.claude/settings.local.json` がignoreされていること
- `.claude/skills` symlink確認
- distribute / sync scripts のdry-runまたはread-only確認
- shared hooks / skills / agents / commands の変更有無確認
- 他peer workspaceを変更していないこと

## 今後検討すべき改善候補

- `README.md` のskills数・配布対象表と実ファイル数の棚卸し
- `note-publish-flow` のfrontmatter整備
- `.codex/` を正本化するか、gitignore/削除候補にするかの判断
- template管理専用skillをdocsのまま維持するか、手動起動専用skillへ分けるかの基準策定
- `.agents/skills` のignore/track混在とCodex mirrorの扱いを整理

## 参照したClaude公式文献

- [Extend Claude Code](https://code.claude.com/docs/en/features-overview)
- [How Claude remembers your project](https://code.claude.com/docs/en/memory)
- [Extend Claude with skills](https://code.claude.com/docs/en/skills)
- [Claude Code settings](https://code.claude.com/docs/en/settings)
- [Hooks reference](https://code.claude.com/docs/en/hooks)
- [Run prompts on a schedule](https://code.claude.com/docs/en/scheduled-tasks)
