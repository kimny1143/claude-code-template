# CLAUDE.md — template課

## 役割

このワークスペースは Claude Code 主運用の全peer共有テンプレート正本です。
各peerの実務ではなく、共有される `hooks` / `skills` / `agents` / `commands` / settings template / 運用ドキュメントを管理します。

## 正本

- 共有payload正本: `.claude/skills/`, `.claude/hooks/`, `.claude/agents/`, `.claude/commands/`
- 設定template正本: `.claude/settings.local.json.example`, `docs/templates/settings-local-base.json`
- 配布・同期正本: `setup.sh`, `scripts/distribute-*.sh`, `link-ios-skill.sh`, `skills-lock.json`
- Codex副次利用mirror: `.agents/skills/`。Codex向け互換が必要なskill変更時のみ同期する
- `.codex/` は現時点では正本ではない。採用する場合は別途migration noteを残す
- 他peer側の `.claude/` / `.agents/` はこのtemplateから配布・参照される派生物

## 絶対禁止

- 読んでいないファイルを変更しない
- 他peerワークスペースを直接変更しない。必要な波及作業は `docs/` に配布候補またはmigration noteとして残す
- shared hooks の安全制約を弱めない
- settings template の権限を無確認で広げない
- `availableModels` を `~/.claude/settings.json`, `~/.claude/settings.local.json`, 各peer `.claude/settings.local.json` に追加しない
- skill名の衝突を増やさない
- peer固有事情をshared skillへ混ぜない
- 配布scriptの対象範囲をdry-runなしで変えない
- symlink/path参照を壊さない
- `premium/` はgit管理しない

## 変更安全原則

- 共有payload変更は全peer波及の可能性がある。影響範囲、配布対象、rollback方法を先に確認する
- `setup.sh` の `SHARED_*` 配列変更は public template の配布範囲変更として扱う
- `scripts/distribute-*.sh` は実行前に必ず `--dry-run`。3課以上に意図しない差分が出たら `/plan`
- settings変更は課固有の hooks / deny / MCP / WebFetch domains を保持する
- hooks変更は Claude公式hook仕様、stdin JSON、exit code、絶対path、入力sanitizeを確認する
- 副作用があるtemplate管理用skillは `disable-model-invocation: true` を原則にする
- 価格、公開表現、全peerガードレール変更は conductor / Policy Gate 経由

## 共有物管理

- Shared skills: `setup.sh` の `SHARED_SKILLS` が公開テンプレート配布対象。追加・削除はmigration note必須
- Internal common skills: `scripts/distribute-skills.sh` が `peer-id-lookup`, `tier-judge`, `plan-mode-policy` を対象課へ同期する
- Template管理専用skill: `common-claude-md-blocks`。経営部CLAUDE.md共通block管理用で、手動起動専用
- Targeted / staged skills: `aax-validator`, `dsp-rta-comparison`, `i18n-key-diff`, `source-eval` は配布先確認なしに全peer共有へ昇格しない
- Shared hooks: `.claude/hooks/` が正本。`setup.sh` で自動linkされるhookは現状 `block-main-push.sh`
- Shared agents / commands: `.claude/agents/`, `.claude/commands/` が正本。挙動変更時はREADME/setupとの整合を確認する

## 成果物保存先

- 恒久運用docs: `docs/`
- 提案・検討中docs: `docs/drafts/`
- 再利用template: `docs/templates/`
- migration note / 配布候補: `docs/template-*.md` または `docs/*migration*.md`
- Gumroad Pro版: `premium/`（git管理外）

## 主要コマンド

```bash
git status --short
git diff --check
./scripts/distribute-skills.sh --dry-run
./scripts/distribute-settings-allow.sh --dry-run
./scripts/distribute-claude-md-blocks.sh --dry-run
bash scripts/distribute-quality-standards.sh --dry-run
find .claude/skills -maxdepth 1 -type l -exec ls -l {} \;
git check-ignore -v .claude/settings.local.json
```

## Plan Mode 要約

`/plan` は設計段階の区切りとして使う。新規skill/hook設計、既存skill/hookの仕様変更、全課配布settings/hook変更、Gumroad同梱方針変更、外部best practiceのスキル化判断、全peerガードレール追加で発動する。

誤字修正、例示追加、文言調整、`skills-lock.json` 更新、既存scriptのdry-run、既存commandの軽微調整では発動しない。

## Policy Gate / Peer展開入口

- conductorはTier 1/2 PR、スキルインストール、コンテンツ編集、peer間タスク調整の委任権限を持つ
- kimny直接承認が必要: 認証/OAuth/APIキー、価格変更、外部公開発言の初回承認
- shared canonical変更がwrite課記事・proposal・style-guideに影響する場合は、変更決裁後にwrite課へ通知する
- 全peer展開が必要な変更は、まずこのrepoにmigration noteを残し、dry-run結果を添えてconductorへ渡す

## 詳細運用

詳細手順は常時コンテキストに置かず、必要時に読む。

- Template ops runbook: `docs/template-ops-runbook.md`
- 受託案件 engagement flow runbook (template課=受託テンプレ `gw-contract-template`+本フロー管理者): `docs/drafts/engagement-repo-flow-runbook-20260703.md`。client 資産の中立性 (MUED/glasswerks 参照を client repo に持ち込まない) + secrets 非焼込み + MUED-side に client 情報を書き出さない厳守。詳細=[[project_jutaku_engagement_flow]]
- 最新整理報告:

@docs/claude-code-template-ops-improvement-20260512.md

## Common blocks (source of truth)

共通blockの正本は `.claude/skills/common-claude-md-blocks/blocks/` (20 blocks)、`scripts/distribute-claude-md-blocks.sh` で各peerへ配布する。template課 (CCO) 自身はこれらを CLAUDE.md にロードしない (slim維持 — 2026-05-29 空placeholder marker 削除、behavior変化なし)。`14-conductor-active-judgment` は conductor専用配布。
