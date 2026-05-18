# Template Ops Runbook

この文書は `CLAUDE.md` から外した詳細運用の置き場です。Claude Code起動時に毎回読む必要はありません。

## 参照順序

1. 変更対象ファイルを読む
2. 変更が shared payload / internal common / template管理専用 / docs のどれか分類する
3. 配布範囲を確認する
4. dry-runまたはread-only確認を実行する
5. 変更後に `git diff --check` と変更ファイル一覧を確認する

## Source Of Truth

| 領域 | 正本 | 配布・参照 |
|---|---|---|
| Shared skills | `.claude/skills/` | `setup.sh` の `SHARED_SKILLS` |
| Internal common skills | `.claude/skills/` | `scripts/distribute-skills.sh` |
| Template管理専用skill | `.claude/skills/common-claude-md-blocks` | 手動起動のみ。全peerへ自動配布しない |
| Codex mirror | `.agents/skills/` | Codex互換が必要なskillのみ同期 |
| Commands | `.claude/commands/` | `setup.sh` の `SHARED_COMMANDS` |
| Agents | `.claude/agents/` | `setup.sh` が全ファイルをlink |
| Hooks | `.claude/hooks/` | `setup.sh` は現状 `block-main-push.sh` のみlink |
| Settings example | `.claude/settings.local.json.example` | public example |
| Settings base | `docs/templates/settings-local-base.json` | `scripts/distribute-settings-allow.sh` |
| Skill lock | `skills-lock.json` | 配布記録・source hash |

`.claude/settings.local.json` はlocal設定です。global gitignoreで無視されており、正本としてcommitしません。

## Skill Classification

### Public shared skills

`setup.sh` の `SHARED_SKILLS` が公開テンプレートの通常配布対象です。ここに追加すると新規導入プロジェクトへsymlinkされるため、README、setup表示、必要なら `skills-lock.json` とmigration noteを合わせます。

現在のpublic shared群:

`tdd`, `coding-rules`, `backend-patterns`, `git-worktree`, `hooks`, `mcp`, `remotion`, `ios-app-store-submission`, `vercel-react-best-practices`, `vercel-react-native-skills`, `vercel-composition-patterns`, `lp-optimizer`, `copywriting`, `seo-audit`, `marketing-audit`, `marketing-psychology`, `launch-strategy`, `pricing-strategy`, `ab-test-setup`, `analytics-tracking`, `core-web-vitals`, `email-sequence`, `referral-program`, `signup-flow-cro`, `onboarding-cro`, `form-cro`, `ui-ux-pro-max`, `ux-psychology`, `web-design-guidelines`, `app-onboarding`, `paywall-upgrade-cro`, `ai-interview-article`, `note-serial-monetization`, `freee-api-skill`, `note-publish-flow`, `stripe-best-practices`, `stripe-projects`, `upgrade-stripe`.

### Internal common skills

`scripts/distribute-skills.sh` が明示配布する共有必須skillです。

- `peer-id-lookup`
- `tier-judge`
- `plan-mode-policy`

この3件を変更した場合は、`./scripts/distribute-skills.sh --dry-run` で対象課差分を確認してから配布候補を作ります。

### Template管理専用skill

- `common-claude-md-blocks`: 経営部CLAUDE.md共通block管理。配布script実行を含むため `disable-model-invocation: true` を維持します。

Template管理専用skillを追加する場合は、原則として `disable-model-invocation: true` を付け、`setup.sh` の `SHARED_SKILLS` へ入れません。全peerが使う必要のない手順はdocsへ置く方を優先します。

### Targeted / staged skills

以下は特定peerや検討段階の用途です。全peer配布に昇格する前にowner、対象課、dry-run、migration noteを確認します。

- `aax-validator`
- `dsp-rta-comparison`
- `i18n-key-diff`
- `source-eval`

## Distribution Playbook

### Shared template setup

`setup.sh` は任意プロジェクトの `.claude/` に共有 commands / skills / agents / hooks をsymlinkします。

変更時の確認:

```bash
grep -n "SHARED_COMMANDS\|SHARED_SKILLS\|SHARED_HOOKS" setup.sh
find .claude/skills -maxdepth 1 -type l -exec ls -l {} \;
```

### Internal skill distribution

```bash
./scripts/distribute-skills.sh --dry-run
```

本番実行はconductor確認後。対象skillディレクトリ内では `rsync --delete` が効くため、対象名の取り違えに注意します。

### Settings allow distribution

```bash
./scripts/distribute-settings-allow.sh --dry-run
```

base allow/denyは `docs/templates/settings-local-base.json`。課固有 hooks / deny / MCP / WebFetch domains を保持する設計を崩さないこと。

### CLAUDE.md common blocks

```bash
./scripts/distribute-claude-md-blocks.sh --dry-run
```

sourceは `.claude/skills/common-claude-md-blocks/blocks/*.md`。marker-bounded section外の課固有内容は触らないこと。

### Quality standards memory pack

```bash
bash scripts/distribute-quality-standards.sh --dry-run
```

このscriptは `~/.claude/projects/.../memory` を対象にするため、dry-run結果を必ず残してから配布候補にします。

## Hook Safety

- HookはClaudeの判断ではなくクライアント側で実行されるガードレールです
- command hookはユーザー権限で動くため、入力を信用せずsanitizeします
- stdin JSONから `tool_name` / `tool_input` を読む実装に揃えます
- blockはexit code `2`、警告は非破壊にする
- pathは絶対pathまたは `"$CLAUDE_PROJECT_DIR"` を優先します
- `.env`, credentials, private keys, path traversal, destructive shellは弱めない

Hook変更後の最低確認:

```bash
bash -n .claude/hooks/<hook>.sh
git diff -- .claude/hooks/<hook>.sh
```

## Skill Authoring

- nameは既存skillと衝突させない
- descriptionはトリガーを明確にし、過剰に広げない
- 長い手順、履歴、migration detailsは `docs/` に置き、SKILL.mdは入口に留める
- 副作用があるskillは `disable-model-invocation: true`
- `.claude/skills` と `.agents/skills` の両方が必要かを判断してから同期する

## Settings Management

- `availableModels` は追加しない
- denyを弱めない
- allowを広げる場合は理由、対象peer、代替案、rollbackを記録する
- `.claude/settings.local.json.example` と `docs/templates/settings-local-base.json` の役割を混同しない
- local実験値をtemplateへ昇格する場合はdiffで不要な個人設定が混ざっていないか確認する

## Release Check

変更完了後:

```bash
git diff --check
git status --short --untracked-files=all
git check-ignore -v .claude/settings.local.json
find .claude/skills -maxdepth 1 -type l -exec ls -l {} \;
./scripts/distribute-skills.sh --dry-run
./scripts/distribute-settings-allow.sh --dry-run
./scripts/distribute-claude-md-blocks.sh --dry-run
```

共有payloadを変更していない場合でも、dry-runまたはread-only確認で配布体制が壊れていないことを確認します。

## Migration Note Template

```markdown
# Migration Note: <title>

## Reason
## Changed canonical
## Distribution target
## Peer impact
## Dry-run result
## Rollback
## Policy Gate / conductor status
```
