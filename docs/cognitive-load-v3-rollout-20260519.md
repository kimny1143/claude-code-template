# Cognitive Load v3 Rollout — 2026-05-18

## 実施理由

`/Users/kimny/Dropbox/_DevProjects/_conductor/docs/inbox/proposal-conductor-cognitive-load-v3.md` (約 486行、 (c) hybrid path 反映) で起案された conductor 認知負荷軽減 proposal v3 の Phase 1 implementation。 kimny 2026-05-18 全採用 GO 受領 (trial 1 週間 + 開始今すぐ + judgment Phase 1 soft enforcement + Codex drafts 必要時のみ)。

12 peer 横断で **情報経路 + 状態契約 + 判断契約 + stale governance** の 4 軸再設計を同時着手。 中間管理職は採用せず、 軽い階層化 (peer cluster 表示 + cowork ops aggregator + CCO governance steward) を導入。

本 PR scope = step 4 (status.md template 作成 + 12 peer 配布) + step 10 (12 peer CLAUDE.md 横断 update: URGENCY marker / 基準 / 外部リソース gate / status.md 自走 / judgment request contract) の template/CCO 担当部分。

## 前提

- このワークスペースは Claude Code 主運用 (template課 CCO peer)
- proposal v3 §10 「採用しない案」 整合: CLAUDE.md 大規模追記なし (200行 framework keep)、 詳細は `.claude/rules/` + `.claude/skills/` + 共通 blocks に分散
- 既存 `common-claude-md-blocks` skill + `distribute-claude-md-blocks.sh` pattern 踏襲 (Phase 2 0.1+0.2 既配布 14 blocks に 4 blocks 追加 + TARGET_PEERS 4→14 拡張)
- 「他peerワークスペースを直接変更しない」 template課 protocol 厳守 = canonical template + conductor relay 経由 peer 自走着手 path
- 各 peer の CLAUDE.md marker挿入 PR は本 PR merge 後 conductor relay 経由 dispatch (peer responsibility、 Tier 2 [peer-review: 自課])

## 実施内容

### A. 新規 files (6 件)

1. `.claude/skills/common-claude-md-blocks/blocks/15-urgency-marker.md` — URGENCY marker 6行 format + 基準 (high/mid/low) + 議論レーン protocol + post-hoc audit category (proposal v3 §4.4 + §8.1 統合)
2. `.claude/skills/common-claude-md-blocks/blocks/16-external-resource-gate.md` — 外部リソース新規作成 / 公開範囲変更 / 課金契約 / 不可逆操作 = 常に URGENCY: high + kimny/conductor pre-approval gate (proposal v3 §8.2、 dsp 5/17 incident 再発防止)
3. `.claude/skills/common-claude-md-blocks/blocks/17-status-md-self-drive.md` — 各 peer 自走 status.md update protocol + cowork cron aggregation 統合 (proposal v3 §4.3)
4. `.claude/skills/common-claude-md-blocks/blocks/18-judgment-request-contract.md` — mid/high message に QUESTION + OPTIONS + RECOMMENDATION 追加 (Phase 1 soft enforcement、 proposal v3 §4.6)
5. `docs/templates/peer-status-md.template.md` — 各 peer 配布用 status.md template (frontmatter YAML 13 fields + Recent events + Notes、 proposal v3 §4.2.1)
6. `docs/cognitive-load-v3-rollout-20260519.md` (本 file) — migration note

### B. 修正 files (2 件)

7. `scripts/distribute-claude-md-blocks.sh` — TARGET_PEERS 拡張 (4 paths → 14 paths)
   - 追加 10 paths: mued main / mued apps (native) / dsp / occur / threads-api (SNS) / write / LP / reserch / data / blender
   - skip logic 既存 (`NO CHANGES (X blocks have no marker)`) で marker未挿入 peer は no-op 動作
8. `.claude/skills/common-claude-md-blocks/SKILL.md` — Phase 2 0.3 section 追加 (4 new blocks 15-18) + 配布範囲 update (経営部4課 → 全14課) + description update (8 項目 → 18 blocks) + ロードマップ Phase 1.0/1.1/1.2 追加

## 変更したファイル

合計 8 files (6 新規 + 2 修正)。

```
新規:
  .claude/skills/common-claude-md-blocks/blocks/15-urgency-marker.md
  .claude/skills/common-claude-md-blocks/blocks/16-external-resource-gate.md
  .claude/skills/common-claude-md-blocks/blocks/17-status-md-self-drive.md
  .claude/skills/common-claude-md-blocks/blocks/18-judgment-request-contract.md
  docs/templates/peer-status-md.template.md
  docs/cognitive-load-v3-rollout-20260519.md (本 file)

修正:
  scripts/distribute-claude-md-blocks.sh
  .claude/skills/common-claude-md-blocks/SKILL.md
```

## 変更しなかったファイル / 範囲

- 他 peer workspace の `CLAUDE.md` / `status.md` (= cross-peer write 絶対禁止 protocol per、 各 peer 自走着手は conductor relay 経由)
- `.claude/hooks/block-main-push.sh` (5/10 LP/kimny 直接編集 carry-over、 別 PR 対象 per memory `project_handoff_20260511.md`)
- `CLAUDE.md` 本体 (template課) (5/12 ops improvement carry-over、 別 PR 対象)
- 他 distribute scripts (`distribute-skills.sh` / `distribute-settings-allow.sh` / `distribute-quality-standards.sh`)
- 既存 14 blocks (01-14) content (Phase 2 0.1+0.2 既配布対象、 本 PR 影響なし)

## 全 peer 波及範囲

### CCO PR merge後の直接影響 (即時)

- template repo 内 4 new blocks + template + script 拡張 + SKILL.md update + migration note = template課 canonical artifact 更新
- distribute script TARGET_PEERS 拡張 = 全 14 peer paths が distribute candidate に追加 (ただし marker未挿入 peer は skip logic で no-op、 即時影響なし)

### conductor relay経由 各 peer dispatch後の波及 (5/19-5/22 trial期間中)

各 peer (13 peer = conductor + mued main + mued apps + freee + cowork + dsp + occur + threads-api + write + LP + reserch + data + blender):
1. 自 workspace に `docs/templates/peer-status-md.template.md` を copy → `status.md` (or `docs/status.md`) として peer 情報 fill
2. 自 CLAUDE.md に COMMON-BLOCK markers (新 4 + 既 14 = 計 18 markers) 挿入 PR 起案 (Tier 2 [peer-review: 自課])
3. 自 git repo に commit + push (自 peer repo のみ、 conductor repo には push しない)
4. cowork peer cron が 5-15 分間隔で status.md fetch + `_conductor/docs/inbox/peer-raw-status.md` 集約 (step 5、 cowork peer 担当)

### Phase 1 trial開始後 (5/19-5/29)

- proposal v3 §5.2 success metric 8項目で trial進捗 measurement
- proposal v3 §6.3 failure 検知 = Phase 3 着手 trigger (low/mid 割り込み週 2件以上 / false_low 1件 / 等)

## 配布前 verification (dry-run結果)

### Step 1: block file syntax verify

```bash
for f in .claude/skills/common-claude-md-blocks/blocks/15-*.md \
         .claude/skills/common-claude-md-blocks/blocks/16-*.md \
         .claude/skills/common-claude-md-blocks/blocks/17-*.md \
         .claude/skills/common-claude-md-blocks/blocks/18-*.md; do
  head -1 "$f"
done
```

期待 output:
```
## URGENCY marker — peer 自己申告 6 行 format
## 外部リソース gate — 常に URGENCY: high + kimny / conductor approval 必須
## status.md 自走 update protocol
## judgment request contract — mid / high message format
```

= 各 block `## ` heading 開始、 frontmatter なし、 existing blocks (01-14) 整合 ✅

### Step 2: distribute script dry-run

```bash
bash scripts/distribute-claude-md-blocks.sh --dry-run
```

期待 output:
- `Loaded 18 blocks from .../blocks` (14 既存 + 4 新規)
- 14 target peer paths 全てで `NO CHANGES (18 blocks have no marker)` (= marker 未挿入 peer は skip logic で no-op) または `WOULD UPDATE: N blocks` (= 既 marker 挿入済 peer の新規 blocks 同期候補)
- `==> Total: N block replacements across 14 targets`
- ERROR / Exception / Python traceback 含まない
- exit code 0

### Step 3: git diff --check

```bash
git diff --check
```

期待: whitespace error / merge marker 検出なし

### Step 4: git status --short verify

```bash
git status --short
```

期待: 本 PR 対象 8 files のみ staged (+ pre-existing uncommitted 別 file unstaged)

## rollback path

本 PR merge 後に重大 issue 発覚した場合の rollback:

### Step 1: template repo rollback

```bash
# 本 PR merge commit を identify
git log --oneline main | head -5

# revert commit
git revert <pr-merge-commit-sha> --no-edit
git push origin main
```

### Step 2: distribute script rollback (任意)

各 peer の CLAUDE.md に既に marker 挿入 + content sync済 case:
- distribute script を pre-PR version (TARGET_PEERS 4 paths) に revert
- 4 new blocks (15-18) を blocks/ から削除
- 再度 distribute production run で marker section を空 marker に戻す (= 各 peer CLAUDE.md sync removes block content)

### Step 3: 各 peer self-revert (peer responsibility)

各 peer は本 PR 影響で挿入した CLAUDE.md markers + status.md を自 repo で revert:
```bash
git revert <marker-insertion-pr-merge-commit>
git rm status.md
git commit -m "revert: cognitive load v3 rollout (template課 PR revert per)"
git push
```

## 今後検討すべき改善候補

### Phase 1 trial 5/19-5/29 期間中の monitoring

- proposal v3 §5.2 success metric 8項目 daily check (`reports/daily/YYYY-MM-DD.md` audit section per)
- false_low / false_high / missing_marker / stale / evidence_missing / missing_question / missing_options / missing_recommendation 統計化
- 1件でも閾値超過 → proposal v3 §6.3 Phase 3 trigger

### Phase 2 0.4+ 着手 candidate (5/29 trial 完納後)

- judgment request contract Phase 2 strict 化 (wrapper script / broker priority queue)
- discussion_lock physical enforcement (cowork wrapper, proposal v3 §6.2)
- stale governance audit cycle 強化 (memory 70+件 monthly refresh)
- CCO governance steward role 着手 (rules / skill / memory canonical 管理)

### proposal v3 §11 期待効果 measurement

- conductor 認知負荷低下: 情報運搬 → 判断 + audit + meta-coordination shift evidence
- Kimny 認知負荷低下: 議論中割り込み消滅 evidence
- 日報生成コスト低下: peer broadcast 不要 (raw status から conductor 整形) evidence

## 参照 file

- spec source: `/Users/kimny/Dropbox/_DevProjects/_conductor/docs/inbox/proposal-conductor-cognitive-load-v3.md` (§4-§8 全 reference)
- 既存 pattern reference:
  - `.claude/skills/common-claude-md-blocks/SKILL.md` (Phase 2 0.1+0.2 設計)
  - `scripts/distribute-claude-md-blocks.sh` (TARGET_PEERS + Python helper)
  - `docs/templates/api-cost-inventory-template.md` (template format)
  - `docs/claude-code-template-ops-improvement-20260512.md` (migration note 構造)
- kimny GO timestamps:
  - 2026-05-18: cognitive load v3 全採用 GO (trial 1週間 + 開始今すぐ + Phase 1 soft + Codex drafts 必要時のみ)
- conductor approval timestamps:
  - 2026-05-18 15:03 JST: CCO Plan mode entry path approve (5 項目 + canonical + relay path + Tier 2 self-merge OK)
