# growth 課 skill 配布 audit (Phase 1、 2026-05-26)

- 状態: **shipped 2026-05-27** (Tier 1 self-review、 docs 正式昇格)
- [x] conductor承認 (CCO dispatch 5/26 13:33 JST)
- 起源: kimny directive 5/26 13:00 JST「growth 課に template 課から有効性高いスキルは共有済み？」
- ETA Phase 1 = 5/28 sprint #001 active launch 前 → **5/26 中 完納 ✅**
- Phase 2 = 6/3 sprint #001 終了前 marketing skill 市場調査 (別 doc: `docs/drafts/marketing-skill-research-20260526.md`)
- scope discipline: CCO core scope (skill 配布 infrastructure)、 growth own work scope (skill activate / customize / 採用判断) は触らず

## 0. summary

| 区分 | 件数 | detail |
|------|------|--------|
| ✅ 配布完納 | 41 skills + 6 agents + 1 hook + 8 commands + 1 canonical memory | 本 audit cycle で実行 |
| ⏳ 未配布 (intentional) | 18 common-claude-md-blocks | growth CLAUDE.md に marker 未挿入 (5/28 active launch 後別 PR) |
| 🆕 marketing role 特に有効性高い既配布 skill | **15 skills** | growth 着任時 activate / customize 候補 (本 doc Section 3) |

## 1. 配布完納 list (本 audit cycle で executed)

### 1.1 distribute-skills.sh (COMMON_SKILLS、 rsync)

PR #83 branch from 実行、 growth 課新規 target に 3 件 [CREATE]:

| skill | 用途 |
|-------|------|
| peer-id-lookup | claude-peers ID 解決、 dispatch 時必須 |
| tier-judge | PR Tier 自動判定 (1/2/3 自動分類) |
| plan-mode-policy | 異常値検出 → /plan 発動 framework |

### 1.2 setup.sh (SHARED_*、 symlink)

setup.sh 1 回実行で:

**SHARED_SKILLS = 38 skills (template `.claude/skills/` への symlink)**:
- Development (11): tdd / coding-rules / backend-patterns / git-worktree / hooks / mcp / remotion / ios-app-store-submission / vercel-react-best-practices / vercel-react-native-skills / vercel-composition-patterns
- **Marketing & CRO (15)**: lp-optimizer / copywriting / seo-audit / marketing-audit / marketing-psychology / launch-strategy / pricing-strategy / ab-test-setup / analytics-tracking / core-web-vitals / email-sequence / referral-program / signup-flow-cro / onboarding-cro / form-cro
- UX & Product (5): ui-ux-pro-max / ux-psychology / web-design-guidelines / app-onboarding / paywall-upgrade-cro
- **Content & Monetization (4)**: ai-interview-article / note-serial-monetization / freee-api-skill / note-publish-flow
- Payments & Billing (3): stripe-best-practices / stripe-projects / upgrade-stripe

**SHARED_AGENTS = 6 agents** (`.claude/agents/`):
code-reviewer / code-simplifier / codebase-optimizer / docs-curator / security-reviewer / verify-app

**SHARED_HOOKS = 1 hook** (`.claude/hooks/`):
block-main-push.sh

**SHARED_COMMANDS = 8 commands** (`.claude/commands/`):
commit / pr / build-fix / security / ship / learn / codex / ios

### 1.3 distribute-quality-standards.sh (memory canonical)

`feedback_kimny_quality_standards.md` [CREATE] + MEMORY.md エントリ追加 (canonical 50-60% Twilio標準 + 月次COGS上限 $200/月 + 業態定義「API-enabled vertical application」)。

### 1.4 distribute-settings-allow.sh

settings.local.json 既存 (conductor 配置済 placeholder)、 base template と整合確認、 0 changes (NO ACTION required)。

### 1.5 total

- 41 skills (3 internal + 38 SHARED) ✅
- 6 agents ✅
- 1 hook ✅
- 8 commands ✅
- 1 canonical memory ✅

## 2. 未配布 (intentional defer)

### 2.1 common-claude-md-blocks (18 blocks)

`distribute-claude-md-blocks.sh` dry-run 結果: growth CLAUDE.md に **marker 未挿入** = 19 blocks 全 NO CHANGES (script の design = marker 必須 = marker insertion は別 PR)。

- 5/28 active launch 後、 growth 課 own work で「どの block を marker 挿入するか」 own 判断推奨 (Section 0-pre scope discipline 注記 per、 CCO 先回り禁止)
- 経営部 4 課 (conductor / template / freee / cowork) は Phase 2 0.1+0.2 で marker 挿入済 = growth は経営部 layer or マーケ部 layer かで block 選択判断必要 (growth own work)

### 2.2 SHARED_HOOKS 拡張候補 (template 課既知 gap)

template 課 `.claude/hooks/` 6 件中 setup.sh SHARED_HOOKS は 1 件のみ (block-main-push.sh)、 残 5 件未配布:

| hook | 全 peer 配布候補? |
|------|---------------|
| validate-dangerous-ops-v2.sh | ✅ (CWD-外 file 編集 block、 全 peer 適用) |
| validate-dangerous-ops.sh | ⚠️ legacy、 v2 で十分か要判断 |
| suggest-git-cleanup.sh | ⚠️ peer 個別 (適用判断) |
| check-remotion-quality.sh | ❌ video 課固有 |
| load-handoff-memory.sh | ⚠️ session start hook、 全 peer 適用検討 |

**status**: trilateral 議論 P0-2 / Gap 4 で「SHARED_HOOKS 拡張 + Tier 3 plan mode 必要」 既認識、 別 cycle (kimny final approve 後 ship、 6/4-6/20 PoC 段階) で対応。 本 audit cycle scope 外。

## 3. growth role 特に有効性高い既配布 skill 推奨 (15 件、 着任時 activate / customize 候補)

⚠️ **本 list は role-fit suggestion のみ**、 channel 選択 / 適用順序 / customization 内容は growth 着任後 own 判断 (scope discipline 反省 per [[feedback_peer_creation_vs_peer_work_scope]])。

### 3.1 高 priority (Marketing & CRO core、 5 件)

| skill | role fit | growth 着任時 own 判断 |
|-------|---------|---------------------|
| `marketing-audit` | 全マーケティング監査・分析、 全マーケティング関連 skill 統合 hub | growth own work で sprint start 時 1 回実行検討 |
| `lp-optimizer` | LP 第三者視点分析・改善、 CRO + DR 原則統合 | LP 課 ↔ growth 連携時に own use |
| `seo-audit` | technical SEO audit / on-page SEO | growth sprint #001 流入経路設計 own 起案時 |
| `analytics-tracking` | GA4 / GTM / 計測 implementation | data 課 ↔ growth 連携時に own use |
| `ab-test-setup` | 仮説設計 / variant 設計 / 効果測定 | growth conversion funnel design own 起案時 |

### 3.2 中 priority (Funnel & Conversion、 6 件)

| skill | role fit | growth 着任時 own 判断 |
|-------|---------|---------------------|
| `copywriting` | LP / pricing / feature コピー | LP / SNS 連携 |
| `email-sequence` | drip campaign / lifecycle email | newsletter / 顧客リテンション |
| `signup-flow-cro` | signup / activation / trial 最適化 | MUEDial signup funnel 関連 |
| `onboarding-cro` | post-signup activation / time-to-value | MUEDial Hoo Pass D30/D60 関連 |
| `form-cro` | lead / contact form 最適化 | LP form 最適化 |
| `paywall-upgrade-cro` | in-app paywall / upgrade screen | MUEDial Free → Pro upgrade design |

### 3.3 中 priority (Pricing & Launch、 2 件)

| skill | role fit | growth 着任時 own 判断 |
|-------|---------|---------------------|
| `pricing-strategy` | pricing tiers / packaging / Van Westendorp | growth own 起案時、 freee CFO 連携 |
| `launch-strategy` | Product Hunt / 機能 release / momentum | sprint #002+ launch 設計時 |

### 3.4 低 priority (Content & Monetization、 2 件)

| skill | role fit | growth 着任時 own 判断 |
|-------|---------|---------------------|
| `ai-interview-article` | note 記事制作 (kimny ×AI 対話形式) | write 課 ↔ growth 連携、 note 有料化候補 |
| `note-serial-monetization` | note 連載有料化戦略、 価格設定 | write 課 ↔ growth 連携、 note 有料化 candidate 抽出 |

### 3.5 reference (Psychology、 2 件)

| skill | role fit | growth 着任時 own 判断 |
|-------|---------|---------------------|
| `marketing-psychology` | 70+ 心理 model、 マーケ適用 | content brief / CTA copy design reference |
| `ux-psychology` | UX 心理効果、 UI 設計適用 | growth own UI 提案時 reference |

## 4. growth own work で activate / customize 想定 flow

⚠️ **本 flow は reference**、 具体 sprint priority / customization 内容は growth own 判断。

1. **5/28 sprint #001 start 時**: `marketing-audit` skill 1 回実行で全マーケティング状況 audit (CFO baseline `cfo-monetization-baseline-audit-20260526.md` と統合)
2. **流入経路設計 own 起案**: `seo-audit` / `lp-optimizer` reference として use
3. **funnel design own 起案**: `signup-flow-cro` / `paywall-upgrade-cro` reference
4. **measurement own 設計**: `analytics-tracking` / `ab-test-setup` reference
5. **content / copy own 起案**: `copywriting` / `email-sequence` reference
6. **sprint #002+**: `launch-strategy` / `pricing-strategy` 必要時 use

## 5. 配布実行 evidence (verify)

```
$ ls /Users/kimny/Dropbox/_DevProjects/_growth/.claude/
agents  commands  hooks  settings.local.json  skills

$ ls /Users/kimny/Dropbox/_DevProjects/_growth/.claude/skills/ | wc -l
41

$ ls /Users/kimny/Dropbox/_DevProjects/_growth/.claude/agents/
code-reviewer.md  code-simplifier.md  codebase-optimizer.md
docs-curator.md  security-reviewer.md  verify-app.md

$ ls /Users/kimny/Dropbox/_DevProjects/_growth/.claude/hooks/
block-main-push.sh

$ ls /Users/kimny/.claude/projects/-Users-kimny-Dropbox--DevProjects--growth/memory/ | grep quality
feedback_kimny_quality_standards.md
```

## 6. Phase 2 ETA + 次 action

- Phase 1 完納 ✅ (本 doc)
- Phase 2 = market 調査 + 新規 candidate 5-10 件、 reserch 課並列協働 dispatch 既 (conductor から)
- ETA Phase 2 = 6/3 sprint #001 終了前 (5/28-6/3 window)
- 次 doc: `docs/drafts/marketing-skill-research-20260526.md`

## 7. growth 課への通達 (conductor relay 推奨)

informational notify content:

> growth 課 (e59sxr8h) 配布完納:
> - 41 skills (3 internal common + 38 SHARED 内 15 marketing-focused)
> - 6 agents (code-reviewer / code-simplifier / codebase-optimizer / docs-curator / security-reviewer / verify-app)
> - 1 hook (block-main-push.sh)
> - 8 commands (commit / pr / build-fix / security / ship / learn / codex / ios)
> - 1 canonical memory (feedback_kimny_quality_standards.md = 軸1A 58-63% / 軸1B 50-60% / $200/月 COGS cap)
>
> 着任時 own 判断で skill activate / customize / 採用順序 own 起案。 reference 候補 list は `docs/drafts/growth-skill-audit-20260526.md` Section 3 参照、 strategy / sequencing は CCO 立案ではない。
>
> Phase 2 marketing skill 市場調査は 6/3 前完納予定、 sprint #002+ input。
