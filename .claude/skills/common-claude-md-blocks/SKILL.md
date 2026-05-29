---
name: common-claude-md-blocks
disable-model-invocation: true
description: >
  経営部4課 (template/conductor/freee/cowork) → 5/18 cognitive load v3 rollout で全14課に展開された CLAUDE.md 共通block管理 skill (19 blocks)。
  source of truth: blocks/*.md、各課CLAUDE.mdへ marker-bounded section置換でdistribute。
  使用タイミング: (1) 共通block仕様変更時 (2) 14課横断 policy 同期時 (3) cognitive load v3 trial期間 (5/19-5/29) で各 peer marker 挿入 PR 完納時。
---

# common-claude-md-blocks — 経営部4課CLAUDE.md共通block管理

## 概要

経営部4課 (template/conductor/freee/cowork) CLAUDE.md間の重複block (Codex 5/9診断 8項目、約248行重複) を **single source of truth** で管理するskill。各課CLAUDE.mdは marker-bounded section内に共通blockがcopy-pasteされ、`distribute-claude-md-blocks.sh` で同期。

**位置付け**: Codex 5/9 診断結果のPhase 2対応。Phase 1 (template課CLAUDE.md stale fix、PR #54) で修正済 → Phase 2 (本skill、共通block化) → 5/22以降に残10課展開検討。

## なぜ必要か

- **stale drift防止**: 4課 CLAUDE.mdに同じ内容を copy & paste で運用 → 1箇所更新時に他3箇所が stale化 (実例: `feedback_stale_source_retirement.md` 参照)
- **整合性確保**: kimny判断 (例: 5/9 13:45 JST 「peer dormant 自己宣言禁止」) を 4課に同時適用するinfra確立
- **diff PRサイズ削減**: 共通block変更時に 1 PR (template課) だけでmaintainance完納、各課PRは distribute実行のみ
- **5/14 launch期との整合**: 5/13 launch期間中は変更最小化、Phase 2 完納で post-launch 運用負荷低減

## blocks/*.md (19 共通blocks)

### Phase 2 0.1 (PR #56): 基盤 8 blocks

| block | source 4課 | 内容 |
|-------|------------|------|
| `01-operational-premise.md` | 稼働の前提 | "Claudeは休まない" + 24時間稼働 + dormant自己宣言禁止 |
| `02-memory-cleanup.md` | メモリ棚卸し | セッション開始時 stale削除 + MEMORY.md整合 |
| `03-chrome-lock.md` | Chrome拡張ロック制 | 共有リソース先着制 |
| `04-org-structure.md` | 組織体制 | 4部制 + 14課 (dsp/occur含む) + 役職対応 |
| `05-opus-fixed-plan-mode.md` | plan mode discipline | Opus固定 + plan mode cognitive context separator役割 |
| `06-plan-trigger-conditions.md` | /plan 発動条件 | 発動条件 + 判断指針 |
| `07-available-models-rule.md` | availableModels運用 | settings.json追加禁止 |
| `08-conductor-delegation.md` | conductor委任権限 | Tier 1/2 merge等 + 対象外 |

### Phase 2 0.2 (5/9 conductor 19:34 JST承認): judgment quality 6 blocks

| block | source memory | 内容 |
|-------|--------------|------|
| `09-peer-self-judgment-boundaries.md` | feedback_zero_kimny_manual_work (occur peer) | peer自走OK + escalation対象 + 判定3軸 (reversible/外部公開/本番影響) |
| `10-mass-production-principle.md` | feedback_mass_production_default (occur peer) | 量産default + stand-by禁止 + 「ひたすら産み続ける」 (kimny 5/9 broadcast) |
| `11-existing-state-first.md` | feedback_act_on_existing_state (occur peer) | cold-start実態確認 + assumption禁止 + destructive op前のverify |
| `12-self-correction-as-growth.md` | feedback_self_correction_value (occur peer) | judgment reverse OK + 学習loop + memory化 |
| `13-reference-vs-docs-complement.md` | feedback_reference_vs_docs_complement (occur peer) | reference memory ≠ docs structural complement原則 |
| `14-conductor-active-judgment.md` | docs/drafts/conductor-active-judgment-principle.md (CCO PR #58) | passive endorsement禁止 + consistency check必須 + reverse事前検討。**conductor専用配布** (organizational hierarchy 上 conductor が第一義 owner、非conductor peer には marker を置かない / 2026-05-29 再配置) |

### Phase 2 0.3 (PR #N、 2026-05-18 cognitive load v3 rollout): communication 4 blocks

proposal `proposal-conductor-cognitive-load-v3.md` (c) hybrid path、 kimny 5/18 全採用 GO 受領後の 12 peer 横断 communication infra。

| block | source spec | 内容 |
|-------|-------------|------|
| `15-urgency-marker.md` | proposal v3 §4.4 | URGENCY marker 6行 format + 基準 (high/mid/low) + 議論レーン protocol + post-hoc audit category |
| `16-external-resource-gate.md` | proposal v3 §8.2 | 外部リソース新規作成 / 公開範囲変更 / 課金契約 / 不可逆操作 = 常に URGENCY: high + kimny/conductor pre-approval (dsp 5/17 incident 再発防止) |
| `17-status-md-self-drive.md` | proposal v3 §4.3 | 各 peer 自走 status.md update protocol + cowork cron aggregation 統合 (5-15分間隔) |
| `18-judgment-request-contract.md` | proposal v3 §4.6 | mid/high message に QUESTION + OPTIONS + RECOMMENDATION 追加 (Phase 1 soft enforcement、 Phase 2 strict) |

関連 artifacts:
- `docs/templates/peer-status-md.template.md` (各 peer 配布用 status.md template、 frontmatter YAML 13 fields)
- `docs/cognitive-load-v3-rollout-20260519.md` (migration note)
- `scripts/distribute-claude-md-blocks.sh` (TARGET_PEERS 4 → 14 paths 拡張)

### Phase 2 0.4 (PR #N、 2026-05-20 開発フロー改善 MTG): quality gate 1 block

開発フロー改善 MTG (`dev-flow-improvement-mtg-20260520.md`、 kimny 5/20 GO) 論点1 = MUEDear Build 78 事故 (基本 UI バグが TestFlight 素通り) 起点の再発防止 gate。 CCO Workstream 3。

| block | source spec | 内容 |
|-------|-------------|------|
| `19-character-gate.md` | MTG §2 | キャラクター gate 概念 (機械テストで拾えない人間判断の合格基準) + 工程名分離 + 証拠なしには「通過」と書けない原則 + ツール化できない一線 |

関連 artifacts:
- `docs/templates/pull-request-template.base.md` (共通 PR テンプレ base、 機械チェック / 成果物 verify 別 section)
- `docs/dev-flow-gate-rollout-20260520.md` (migration note)
- `.claude/skills/tier-judge/SKILL.md` (Step 4 = UI/成果物変更検出 + evidence 必須 warning)

### evidence base (Phase 2 0.2)

5/9 occur peer judgment rule library 7件構築 + conductor自身の judgment ブレ反省 (15:08 vs 15:18矛盾) + kimny 5/9 17:55 JST「全部前倒し」 + 18:00 JST「ひたすら産み続けろ」 broadcast。

## marker-bounded section形式 (各課CLAUDE.md内)

```markdown
<!-- COMMON-BLOCK-START: 04-org-structure -->
<!-- DO NOT EDIT THIS SECTION DIRECTLY. Source: template課/.claude/skills/common-claude-md-blocks/blocks/04-org-structure.md -->
<!-- Distribute via: scripts/distribute-claude-md-blocks.sh -->

## 組織体制（2026-04-04改定）

### 経営体制
| 役職 | 課 | 機能 |
|------|-----|------|
| ...

<!-- COMMON-BLOCK-END: 04-org-structure -->
```

`distribute-claude-md-blocks.sh` は marker間を sed/python で完全置換。手動編集はmarker内禁止 (script実行で上書きされるため)。

## distribute手順

### dry-run (差分確認)
```bash
cd template課/
./scripts/distribute-claude-md-blocks.sh --dry-run
```

### 実行
```bash
./scripts/distribute-claude-md-blocks.sh
```

各課 CLAUDE.md の marker-bounded sectionが blocks/*.md内容で上書きされる。実行後 git diff で確認 → 各課PR (Tier 3、conductor承認後merge) → distribute記録 (template課にcommit、各課にdistribute)。

## 配布範囲

### Phase 2 0.1+0.2 (5/14 launch完納後): 経営部4課
- template / conductor / freee / cowork (基盤 8 blocks + judgment quality 6 blocks 配布対象)

### Phase 2 0.3 (5/18 cognitive load v3 rollout): 全14課展開
- 4 new blocks (15-18 communication infra) + status.md 自走 protocol
- TARGET_PEERS 14 paths 拡張 (`scripts/distribute-claude-md-blocks.sh` per)
- 各 peer marker挿入 PR は trial開始期 (5/19-5/22) と並行で各 peer 自 git repo に起案 (Tier 2 [peer-review: 自課])
- distribute production run = 全 peer marker挿入完納後、 1 commit で 14 paths 同期

## 各課固有section (共通blockの外)

各課CLAUDE.md冒頭の以下sectionは **共通block化対象外** (課固有):
- 課ミッション / 担当領域 / コマンド一覧 / Tier判定表 / 課固有policy

共通block化対象は「全課で同一policy/同じ表記が必要なもの」のみ。

## 関連skill

- `mcp` — MCP server作成 (本skillはskill側だがdistribute scriptはscripts/配下)
- `hooks` — Hook作成
- `tier-judge` — PR Tier判定 (本PRはTier 3想定)
- `plan-mode-policy` — /plan発動 (本skillの 06-plan-trigger-conditions block整合)

## ロードマップ

| Phase | 機能 | 完納目処 |
|-------|------|---------|
| 0.1 | SKILL.md設計 + 8 blocks/*.md 抽出 + distribute script frame | 5/9 EOD (本) |
| 0.2 | 4課 CLAUDE.md にmarker-bounded section挿入 (各課PR) | 5/14- launch完納後 |
| 0.3 | distribute実行 + 4課同期確認 + commit記録 | 5/14- |
| 1.0 | cognitive load v3 rollout (proposal v3 (c) hybrid path、 4 new blocks 15-18 + status.md template + 全14課 TARGET_PEERS 拡張) | 5/18 |
| 1.1 | 各 peer marker挿入 PR (5/19-5/22 trial開始期と並行、 各 peer Tier 2 [peer-review: 自課]) | 5/19-5/22 |
| 1.2 | distribute production run で全14課 marker-bounded sections sync | 5/22+ |
| 1.3 | 開発フロー改善 MTG 論点1 quality gate (block 19-character-gate + 共通 PR テンプレ + tier-judge Step 4) | 5/20 |
| 2.0 | cognitive load 圧縮 (19 block source を 582→312行へ圧縮 = 散文/履歴/Why削減・format+ルール core 保持。block14 conductor専用再配置。後続: block16 hook 化 PR-B) | 5/29 |

## 関連リソース

- Codex 5/9 診断結果 (conductor自peer内 dispatch)
- Phase 1 修正PR #54 (template課CLAUDE.md stale fix、`996220e` 整合)
- conductor authorization: 5/9 18:00 JST量産原則 + 18:11 JST intermediate ping ack
- `feedback_stale_source_retirement.md` (CFO起案、stale drift防止principle)
- `feedback_continuous_operation.md` + `feedback_peer_session_continuity.md` (Phase 2 backlog追加対象、5/14- 検討)
