# Trilateral 議論 CCO input — codex report 実務 plan 落とし込み (2026-05-26)

- 状態: **shipped 2026-05-27** (Tier 1 self-review、 docs 正式昇格 = 履歴 record として恒久保存)
- 用途: 2026-05-26 trilateral 議論への CCO 一次 input 記録、 後続 trilateral cycle (6/26 想定) で template として参照可
- conductor: n2g8vviw (`_conductor`)
- codex: separate dispatch (本 doc と並列)
- template / CCO: 本 doc
- 受領 dispatch: 2026-05-26 09:59 JST (UTC 00:59) conductor `trilateral 議論 dispatch`
- 短 reply 既送 (5 key finding、 09:00 JST 台)
- full input ETA: 1-2h 内 (本 doc 完成 = full input 完納)

## 0. scope 明示

template / CCO scope:
- 全 peer 共有正本 (`.claude/skills`, `.claude/hooks`, `.claude/agents`, `.claude/commands`, settings template)
- 配布 scripts (`scripts/distribute-*.sh`)
- migration note / template ops runbook
- shared payload の drift detection / audit / 整合性

scope 外 (本 doc では言及のみ、 implementation 提案なし):
- 価格・原価判断 (CFO peer / kimny 直接)
- peer 別 content 実装 (各 peer 自走)
- conductor monitoring 層 (conductor own scope)

## 1. (a) codex 20項目 ↔ 既 enforced mapping 表

### 10 件 help (短期 codex 提案 vs 現状)

| # | codex 項目 | 既 enforced? | 該当 asset | enforcement gap |
|---|------------|--------------|------------|------------------|
| 1 | 判断待ち 1分化 | △ partial | `feedback_document_submission.md` (kimny 承認依頼 = `- [ ] kimny確認` 形式) | format 自動化なし、 手動付与頼み |
| 2 | peer 状態横断 + 次詰まり先見 | ✅ ほぼ | claude-peers `list_peers` / `set_summary`、 status.md heartbeat protocol (`feedback_heartbeat_operation.md`) | 「次詰まり先見」 = predictive analytics 未 enforce |
| 3 | PR / Tier / release 前 gate | ✅ enforced | `tier-judge` skill、 `plan-mode-policy` skill、 `feedback_tier_classification.md`、 `feedback_find_confirmation_principle.md`、 hooks `block-main-push.sh` / `validate-dangerous-ops-v2.sh` | bypass detection なし (--no-verify 使用検知未 enforce) |
| 4 | 実装代行 | scope 外 | (各 peer 自走) | template 関与なし |
| 5 | GA4 / SNS / 数字 → 施策変換 | scope 外 | (data / SNS peer) | template 関与なし |
| 6 | note / SNS / LP コピー | △ partial | `copywriting` / `lp-optimizer` / `ai-interview-article` / `note-serial-monetization` skills 配布済 | kimny 実体験 + 音楽文脈保護 = skill 内 rule、 但し codex output 直叩き bypass risk |
| 7 | CFO 点検 (無料化・値下げ防止) | ✅ rule 化済 | 「価格変更 = Tier 3 = kimny 直接承認」 (CLAUDE.md `PRレビュー権限`)、 `feedback_kimny_quality_standards.md` (canonical 50-60%) | codex に CFO 役を持たせる場合 Tier 3 escalation prompt 必須 |
| 8 | skills / hooks / scripts / cron / status 集約仕組み化 | ✅ ほぼ | `distribute-skills.sh` / `distribute-settings-allow.sh` / `distribute-claude-md-blocks.sh` / `distribute-quality-standards.sh` (4 scripts、 612 lines)、 `common-claude-md-blocks` skill (18 blocks marker 形式) | inventory script (task #24) 未 implementation、 drift detection (peer → template の reverse direction) なし |
| 9 | memory / inbox / 日報 / dashboard 整理 | △ partial | auto-memory `MEMORY.md` index pattern 確立、 各 peer `memory/` dir 標準化済 | memory bloat archive policy なし、 inbox / 日報 dashboard 未 implementation (conductor scope) |
| 10 | kimny 手作業 → peer / script / 自動化 | △ ongoing | distribute scripts、 hooks、 cron (cowork RemoteTrigger) | 個別 case-by-case、 systematic prioritization なし |

### 10 件 long-term protocol (中長期 codex 提案 vs 現状)

| # | codex 項目 | 既 enforced? | 該当 asset | enforcement gap |
|---|------------|--------------|------------|------------------|
| 1 | 毎朝 dashboard 基準 1分 view | ✗ なし | (status.md は peer 個別) | 統合 dashboard 未 implementation (conductor scope) |
| 2 | 毎日 active peer 棚卸し | △ partial | `set_summary` で peer 状態 readable | 自動棚卸し script なし、 conductor 手動 |
| 3 | 重要判断 form (選択肢・推奨・根拠・締切) | △ partial | `feedback_document_submission.md` 形式、 `plan-mode-policy` 設計 step | form template 化未 enforce (`docs/templates/` 内に判断稟議 template なし) |
| 4 | 週次まとめ (Window B / 収益 / プロダクト / コンテンツ / コスト) | ✗ なし | (個別 status.md / handoff memory) | template 課 scope 外 (conductor scope) |
| 5 | 月次棚卸し (価格・原価・AI コスト・skill) | △ partial | skill 配布履歴は `skills-lock.json` `distributedAt`、 価格は canonical `feedback_kimny_quality_standards.md` | skill 棚卸し script なし、 月次 cadence 未 enforce |
| 6 | release 前 多 gate | ✅ enforced | tier-judge + plan-mode-policy + find-confirmation-principle + hook (block-main-push / validate-dangerous-ops-v2) + dev-flow-gate (PR #73) | UI / 実機 / スクショ / 試聴 / 読者視点 = 個別 skill (verify-app agent、 dsp-rta-comparison、 aax-validator、 i18n-key-diff) で部分 cover、 統合 checklist なし |
| 7 | peer 増加対応 (template 正本 + dispatch + plain Japanese) | ✅ ほぼ | 4 distribute scripts、 `peer-id-lookup` skill、 `common-claude-md-blocks` (18 blocks) | **DIVISIONS list 拡張漏れ (5/12 cowork + occur 追加で 11 → 13、 task #24 = distribute-divisions-extend draft 未 merge)** ← 既知 active gap |
| 8 | kimny 直接判断 vs AI 処理分離 | ✅ rule 化済 | Tier 1/2/3 分離 (CLAUDE.md `PRレビュー権限`)、 価格 / OAuth / API key = Tier 3 強制 | rule のみ、 自動分類 script なし |
| 9 | 成果物残し + 雑音捨て | △ partial | `docs/drafts/` (検討中) / `docs/` (恒久) / `docs/templates/` (再利用) 分離既存 | 雑音 prune cadence なし |
| 10 | kimny 「作る・聴く・決める」 時間増加 | △ ongoing | 全項目の合成効果 | 効果測定 metric 未定義 |

### mapping 集計

- ✅ enforced (or ほぼ): **7 項目** (#2, 3, 6 短期、 #6, 7, 8 長期、 + #7 短期 CFO rule)
- △ partial: **9 項目** (#1, 6, 8, 9, 10 短期、 #2, 3, 5, 9 長期)
- ✗ なし: **2 項目** (#1, 4 長期 = conductor scope)
- scope 外 (template 関与なし): **2 項目** (#4, 5 短期)

→ **新規 build 必要 = ✗ なし 2 項目 のみ (両方 conductor scope)、 template scope では 既 enforced 強化 + △ partial の gap closing が ROI 高い**

## 2. (b) Gap 4件 each script draft outline

### Gap 1: drift detection (peer → template reverse direction)

**現状**: `distribute-*.sh` は template → peer の push のみ。 peer 側で改変された場合の detection なし。
**evidence**: 5/10 19:34 JST `block-main-push.sh` 第三者編集 incident は手動 grep detection (memory `project_handoff_20260511.md` #4)。
**risk**: shared hook / skill / settings が peer 側で divergence しても気付けない → 全 peer の整合性が silent に劣化。

**proposal**: `scripts/audit-peer-drift.sh` (新規)

```bash
#!/bin/bash
# audit-peer-drift.sh
# 全 peer の shared payload (hooks / skills / settings) が template 正本と一致するか audit
# Usage:
#   ./scripts/audit-peer-drift.sh                # 全 peer audit (read-only)
#   ./scripts/audit-peer-drift.sh --peer cowork  # 単 peer
#   ./scripts/audit-peer-drift.sh --json         # 機械可読 output
#
# 対象:
#   - .claude/hooks/*.sh (template と sha256 比較)
#   - .claude/skills/{peer-id-lookup,tier-judge,plan-mode-policy}/SKILL.md (sha256 比較)
#   - .claude/settings.local.json の hooks / mcp section 構造 (key 漏れ検知)
#
# 出力 (text mode):
#   [DRIFT] cowork課: .claude/hooks/block-main-push.sh (sha256 mismatch、 last sync 2026-04-26)
#   [OK]    occur課: 全 7 item 整合
#   [MISS]  reserch課: .claude/skills/plan-mode-policy/SKILL.md 未配置
#
# exit code: 0 = no drift, 1 = drift detected
```

**deliverable timeline**: 5/27 Phase 2 Gate 前 draft 提出 → 1 week dry-run → 6/3 production。

### Gap 2: skills-lock.json enforcement (現状 7/46 tracked、 manual hash 更新)

**現状**: `skills-lock.json` は 7 skill のみ tracked (4 external + 3 internal-common)。 残 39 shared skill は untracked。 `distribute-skills.sh` 内 comment 「skills-lock.json の更新は手動（段階1ではスコープ外）」。
**risk**: shared skill が無断 update されても detection なし、 peer 側で version drift しても trace 不能。

**proposal**: `scripts/audit-skills-lock.sh` (新規) + `distribute-skills.sh` への hash auto-update

```bash
#!/bin/bash
# audit-skills-lock.sh
# .claude/skills/ 全 skill の sha256 を skills-lock.json と照合
# Usage:
#   ./scripts/audit-skills-lock.sh           # audit only
#   ./scripts/audit-skills-lock.sh --update  # hash update + distributedAt 更新
#
# 出力:
#   [TRACKED]   freee-api-skill: hash match
#   [DRIFT]     plan-mode-policy: hash mismatch (locked: c2454..., actual: f3a8b...)
#   [UNTRACKED] aax-validator: skills-lock.json 未登録 (39 件)
#
# exit code: 0 = all tracked + match, 1 = drift, 2 = untracked exists
```

**追加**: `distribute-skills.sh` 末尾に hash 自動 update step 追加 (手動更新の負荷除去)。

**deliverable timeline**: 5/27 までに audit script + distribute-skills.sh patch draft、 6/3 production。

### Gap 3: settings.local.json permission drift (template 反映なし)

**現状**: 各 peer `.claude/settings.local.json` は個別管理、 permission 追加が template `settings-local-base.json` に反映されない。
**risk**: peer 単位で permission 漏れ・過剰付与・矛盾が発生、 全 peer 整合性 silent 劣化。

**proposal**: `scripts/audit-settings-allow.sh` (新規、 既存 `distribute-settings-allow.sh` と pair)

```bash
#!/bin/bash
# audit-settings-allow.sh
# 全 peer の settings.local.json permissions / hooks section を template base と diff
# Usage:
#   ./scripts/audit-settings-allow.sh
#
# 出力:
#   [DRIFT] cowork課: permissions.allow に template 未登録 3 件
#           - "Bash(gh api search/code:*)"
#           - "WebFetch(domain:linear.app)"
#           - "mcp__supabase__execute_sql"
#   [OK]    占cco課: template と整合
#
# 設計上 noop: peer 固有の deny / MCP / WebFetch は audit 対象外 (CLAUDE.md `共有物管理` 原則)
```

**deliverable timeline**: 5/27 までに draft、 6/3 production。

### Gap 4: hook bypass detection (--no-verify, --no-gpg-sign)

**現状**: `CLAUDE.md` rule「NEVER skip hooks unless explicitly requested」 のみ、 enforcement なし。
**risk**: peer が rule 無視で --no-verify commit を作成可能、 hooks の安全制約 silent bypass。

**proposal**: `.claude/hooks/detect-hook-bypass.sh` (PreToolUse hook、 全 peer 配布)

```bash
#!/bin/bash
# detect-hook-bypass.sh
# PreToolUse hook: Bash tool call の command 内に --no-verify / --no-gpg-sign / --no-sign 検知
# stdin: tool call JSON (Claude Code hook spec)
# 検知時: exit 2 で block + reason 出力 (kimny / conductor 承認再依頼を促す)
#
# allowlist:
#   - explicit user request 検出 (前 message に「--no-verify」 含む) は通す (heuristic、 false positive 許容)
#
# 配布: setup.sh SHARED_HOOKS に追加、 全 peer 配布
```

**注意**: heuristic 判定で false positive 許容、 strict blocking よりも 「警告 + 確認」 mode が無難。 hook 仕様 (PreToolUse stdin JSON、 exit code 2 = block) に準拠。

**deliverable timeline**: 5/27 までに proof-of-concept hook + dry-run、 全 peer 配布は 6/20 までに段階展開 (peer 集中作業の妨げ最小化)。

## 3. (c) Timeline 落とし込み

### 5/27 Phase 2 Gate 前 (~5/26 EOD)

- [x] 本 doc 完納 (CCO input 提出)
- [ ] codex 2nd opinion 受領待ち (conductor 集約)
- [ ] conductor integrated proposal first draft 提示待ち

### 5/27 - 6/3 (1 week)

| 項目 | 担当 | 内容 |
|------|------|------|
| Gap 1 audit-peer-drift.sh | CCO | script draft + dry-run、 conductor review |
| Gap 2 audit-skills-lock.sh + distribute-skills.sh patch | CCO | script draft + hash auto-update |
| Gap 3 audit-settings-allow.sh | CCO | script draft + dry-run |
| task #24 (distribute-divisions-extend) | CCO | kimny 確認後 merge → 13 peer 整合復帰 |
| dispatch protocol audit | conductor | peer 1次提示の skill mapping verify enforce |

### 6/4 - 6/20 (Window B 終了まで)

| 項目 | 担当 | 内容 |
|------|------|------|
| Gap 4 detect-hook-bypass.sh | CCO | proof-of-concept → 段階配布 (data / template / dsp 課 先行) |
| status.md protocol 全 peer 配布 verify | conductor + CCO | SNS 課 5/25 skip 経緯 reflection、 framework 再発防止 |
| audit script 月次 cron 化 | CCO + cowork peer | `audit-peer-drift.sh` 月次 RemoteTrigger 設定 |
| memory bloat archive policy 設計 | CCO | draft proposal (policy 設計から必要、 implementation は Q3) |

### 6/20 - 7/31 (中期)

| 項目 | 担当 | 内容 |
|------|------|------|
| peer 増加対応 framework | CCO + conductor | template 正本配布漏れ防止 scripted check (Gap 1-3 統合) |
| hooks / settings 全 peer 配布 audit | CCO | 月次 audit report (前述 cron 結果集約) |
| skill / command 整合性 monthly audit | CCO | `skills-lock.json` 全 39 skill tracked 完納 + 月次 hash drift check |

### Q3-Q4 (長期)

| 項目 | 担当 | 内容 |
|------|------|------|
| 「AI チーム神経系」 concrete implementation | trilateral 共同設計 | codex 抽象提案 → conductor monitoring layer + CCO scripted enforcement + codex CFO/copy 役の framework 化 |
| peer 数増加耐性 (13 → 20+) | CCO + conductor | distribute scripts performance + audit script scaling (現状 13 peer 想定、 20+ で rsync 並列化必要) |
| secret rotation policy | trilateral | reference_gemini_api_key.md 等 + rotation cadence 設計、 vault 候補検討 |
| memory archive policy implementation | CCO | rotation script + archive bucket、 cold storage 戦略 |

## 4. (d) Trilateral 役割分担 proposal

### 役割定義 (codex output の「強み」 と既 enforced rule を踏まえた分担)

| 役割 | 主担当 | 副担当 | scope |
|------|--------|--------|-------|
| **strategic monitoring** | conductor | - | peer 横断状態、 dispatch、 次詰まり予測、 Tier escalation、 kimny 直接判断 routing |
| **scripted enforcement** | template / CCO | conductor | shared payload 配布・audit・drift detection、 hooks / skills / settings 整合、 template runbook 維持 |
| **CFO + copy + 1st draft** | codex | conductor (review) | 価格・原価・粗利点検 (Tier 3 escalation 必須)、 note / SNS / LP copy 1st draft (kimny 実体験 + 音楽文脈保護 rule 適用)、 codex CLI 単発タスク |
| **kimny 直接判断** | kimny | conductor (forward) | 価格変更、 OAuth / API key、 全課波及 rule、 外部公開発言初回承認 |

### codex output 受領時の Tier judge step (重要)

codex に CFO 役・copy 役を持たせる場合、 output を直接実装 / 公開 する前に conductor 側で Tier 振り分け judge step を 1段挟む:

```
codex output → conductor receive →
  Tier 1 (docs / data / コピー only): peer self-merge OK
  Tier 2 (コード変更あり): 該当 peer に dispatch + peer review
  Tier 3 (価格 / OAuth / 全課波及): kimny 直接承認必須
```

これを enforce しないと codex output 直叩き bypass で kimny 承認 step が消失する。

### 月次 trilateral cadence proposal

- 月初 conductor: 前月 status 集約 + 当月 priority 提示
- 月中 CCO: audit script 結果 (drift report) 提出
- 月末 codex: CFO 月次点検 (価格・原価・AI コスト) draft → conductor review → kimny 承認

## 5. 抜け漏れ検出 (conductor blind spots、 技術 area)

| area | 現状 | gap | priority |
|------|------|-----|----------|
| `.codex/` の正本化判断 | untracked dir、 「採用する場合は別途 migration note」 ((CLAUDE.md)) | 5/26 時点で 1 ヶ月以上 untracked stay、 採用 / gitignore / 削除 判断未決 | 中 (5/27 か 6/3 に judge) |
| `.gitignore` 既差分 (`.env*` 追加) | working tree unstaged | 5/26 時点で commit されず stay、 security 改善が放置されている | 低 (即 commit 可、 本 input 完納後 ship 可能) |
| skills-lock.json 7/46 tracked | manual hash 更新前提 | Gap 2 で対処、 但し untracked 39 skill の baseline 一括登録が初手必要 | 中 (Gap 2 と pair) |
| `.claude/hooks/` 6 hooks のうち 1 hook (block-main-push.sh) のみ `setup.sh` SHARED_HOOKS 配布対象 | `validate-dangerous-ops-v2.sh` / `suggest-git-cleanup.sh` / `check-remotion-quality.sh` / `load-handoff-memory.sh` は配布対象外 | 全 peer 配布漏れ、 安全制約が template のみで peer に効かない | 高 (Gap 4 と pair、 setup.sh SHARED_HOOKS 拡張要 plan mode) |
| skill 別 `disable-model-invocation` flag enforcement | `common-claude-md-blocks` のみ明示、 他 template 管理 skill 不明 | 自動選択誤発火 risk | 低 (個別 audit) |
| `docs/drafts/` の pending TODO 棚卸し | `distribute-divisions-extend-20260512.md` 等 stale draft 存在 | 5/12 → 5/26 で 2 週間 stay、 kimny 承認 batch なし | 中 (CCO 自走で kimny 確認 ping 可) |
| memory `MEMORY.md` index 200 行制限 | 現状 24 entries、 線形拡張中 | 200 行到達時 truncation で entry 喪失 risk | 低 (現状余裕、 但し monitoring) |
| handoff memory chain (5/10 → 5/11 → 5/25 → 5/26) | 各 EOD で新規 file 作成、 蓄積中 | archive policy なし、 14 日経過 handoff の retention 判断未定 | 中 (Q3 archive policy 設計内に含める) |

## 6. 次 action (本 input 完納後)

1. **本 doc を conductor に peer message + path 共有** (CCO → n2g8vviw)
2. **conductor 整合 first draft 受領待ち** (codex 2nd opinion + 本 input 集約後)
3. **kimny 確認待ち** (conductor first draft → kimny review)
4. **5/27 Phase 2 Gate 前 actionable item 確認**:
   - `.gitignore` `.env*` commit (即 ship 可)
   - task #24 (distribute-divisions-extend) kimny 確認 ping
   - Gap 1-3 script draft 着手 (kimny 承認後)

## 7. open question (kimny + conductor 判断必要)

1. Gap 4 (detect-hook-bypass.sh) は全 peer 配布で strict block vs 警告 only、 どちらが kimny 運用感覚に合うか
2. `.codex/` 正本化 / gitignore / 削除 の判断
3. trilateral cadence proposal (月次 codex CFO 点検) の頻度 (月 1 / 隔週 / 週 1)
4. peer 数増加耐性 framework の対象 scale (13 → 20 が現実 horizon か、 50+ も視野か)

---

**CCO 一次 input 完納。 conductor integrated proposal first draft 受領後 二次 input or 個別 script draft 着手します。**
