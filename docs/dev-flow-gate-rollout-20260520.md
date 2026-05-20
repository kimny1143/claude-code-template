# Dev Flow Gate Rollout — 2026-05-20

開発フロー改善 MTG (`_conductor/docs/inbox/dev-flow-improvement-mtg-20260520.md`、 kimny 5/20 GO) 論点1 のうち、 CCO 担当 Workstream 3 (全課共通 gate 定義 + PR テンプレ) の template課 canonical artifact 起案。

## 実施理由

MUEDear Build 78 事故 — 5 ゲーム全部「次へ」ボタン見切れで試遊不可、 が TypeScript エラー 0 + Tier 2 LGTM + Apple Archive 成功で「テスト通過」と誤認され TestFlight まで素通り。

MTG 全 13 ピア + Codex 一致の診断: 「テスト通過」の意味が「コードが壊れていない」に偏り「成果物が実際に使える」を含まない。 機械チェック (型 / lint / build / コードレビュー) と人間チェック (実機で遊べる / 試聴 / 読者視点) が同じ「通過」語で曖昧化していた。

## 前提

- このワークスペースは Claude Code 主運用 (template課 CCO peer)
- CCO scope = 全課共通の gate 定義 + PR テンプレ。 native `verify-ui.sh` (Workstream 1) / LP gw-dash スクショフロー (Workstream 2) は各自課実装、 conductor が整合
- 「他peerワークスペースを直接変更しない」 template課 protocol 厳守 = canonical template + conductor relay 経由 peer 自走着手 path
- kimny 判断: A=gate 優先 / B=再発防止 gate 最優先 / C=承認 (CCO 主導 Tier 3 GO)
- conductor 承認 (5/20、 SP1 条件付き + SP2/3/4 accept): SP1 = Phase 1 soft enforcement、 条件(1) tier-judge warning 確実発火、 条件(2) Phase 2 評価期限明記

## 実施内容

### A. 新規 files (4 件)

1. `docs/templates/pull-request-template.base.md` — 共通 PR テンプレ base。 機械チェック section と成果物 verify section を別見出しで分離 (MTG 工程名分離原則)。 成果物 verify = キャラクター gate 確認 + スクショ/録画 添付。 「証拠なしには通過と書けない」原則を「証拠」section に明記
2. `.github/pull_request_template.md` — template課自身の PR テンプレ。 base からキャラクター gate 行 (= distribute dry-run 目視確認) のみ fill
3. `.claude/skills/common-claude-md-blocks/blocks/19-character-gate.md` — キャラクター gate 概念 + 工程名分離 + 証拠原則 + dsp「ツール化できない一線」但し書き
4. `docs/dev-flow-gate-rollout-20260520.md` (本 file) — migration note

### B. 修正 files (2 件)

5. `.claude/skills/tier-judge/SKILL.md` — 判定フローに Step 4 (UI/成果物変更検出) 追加。 検出時は出力フォーマットの固定 section として evidence 必須 warning を無条件発火 (SP1 条件1)。 Tier 数値判定 (1/2/3) は不変
6. `.claude/skills/common-claude-md-blocks/SKILL.md` — Phase 2 0.4 section 追加 (block 19) + 18→19 blocks + description update + ロードマップ 1.3 追加

## 変更したファイル

合計 6 files (4 新規 + 2 修正)。

```
新規:
  docs/templates/pull-request-template.base.md
  .github/pull_request_template.md
  .claude/skills/common-claude-md-blocks/blocks/19-character-gate.md
  docs/dev-flow-gate-rollout-20260520.md (本 file)

修正:
  .claude/skills/tier-judge/SKILL.md
  .claude/skills/common-claude-md-blocks/SKILL.md
```

## 変更しなかったファイル / 範囲

- 他 peer workspace の `CLAUDE.md` / `.github/pull_request_template.md` / `status.md` (= cross-peer write 絶対禁止、 各 peer 自走着手は conductor relay 経由)
- `scripts/distribute-claude-md-blocks.sh` (TARGET_PEERS 不変 14 paths、 block 19 は既存 script で自動配布対象)
- `scripts/distribute-skills.sh` (tier-judge は既に `COMMON_SKILLS` 内、 script 自体は不変)
- native `verify-ui.sh` / LP gw-dash スクショフロー (別 Workstream、 各自課実装)
- 既存 blocks 01-18 content (本 PR 影響なし)

## 全 peer 波及範囲

### CCO PR merge後の直接影響 (即時)

- template repo 内 block 19 + PR テンプレ base + template課 PR テンプレ + tier-judge Step 4 + SKILL.md update + migration note = template課 canonical artifact 更新
- block 19 は `distribute-claude-md-blocks.sh` の既存 14 課対象に自動的に含まれる (ただし marker 未挿入 peer は skip logic で no-op、 即時影響なし)
- tier-judge は `distribute-skills.sh` 既存対象、 次回 distribute production run で全課に Step 4 反映

### conductor relay経由 各 peer dispatch後の波及

各 peer (13 peer):
1. `docs/templates/pull-request-template.base.md` を自 repo の `.github/pull_request_template.md` に copy
2. 「成果物 verify」section のキャラクター gate 行を自課のもの 1 行に fill (例: native = 実機で実際に遊べる、 dsp = 試聴)
3. 自 CLAUDE.md に block 19 用 marker `<!-- COMMON-BLOCK-START: 19-character-gate -->` 挿入 (cognitive load v3 step 10 と同 pattern、 Tier 2 [peer-review: 自課])
4. 自 git repo に commit + push (自 peer repo のみ)
5. `distribute-claude-md-blocks.sh` production run で block 19 content + tier-judge Step 4 が全課 sync

### Phase 1 trial — soft enforcement (5/20-)

- enforcement = Phase 1 soft: PR テンプレ checkbox + tier-judge Step 4 warning + reviewer 義務
- 「evidence なし = merge 不可」の全課共通 hard CI gate は Phase 2 follow-up
- Build 78 型 UI バグの hard gate は native `verify-ui.sh` (Workstream 1) が担う = 二層
- **Phase 2 評価期限** (SP1 条件2): 論点1 完了 (本 PR merge + WS1 + WS2 完了) から 1 週間以内、 target 2026-05-27 JST。 評価 metric = UI/成果物変更 PR のうち成果物 verify section が evidence 添付済の割合 (目標 95%)。 WS1/WS2 完了遅延時は完了日 +7 日に conductor 再設定

## 配布前 verification (dry-run結果)

### Step 1: block 19 syntax verify

```bash
head -1 .claude/skills/common-claude-md-blocks/blocks/19-character-gate.md
```

期待: `## キャラクター gate — 機械テストで拾えない人間判断の合格基準` (`## ` heading 開始、 frontmatter なし、 既存 blocks 01-18 整合)

### Step 2: distribute-claude-md-blocks.sh dry-run

```bash
bash scripts/distribute-claude-md-blocks.sh --dry-run
```

期待: `Loaded 19 blocks`、 14 target peer paths は marker 未挿入で `NO CHANGES` または既挿入 peer で `WOULD UPDATE`、 Python traceback なし、 exit 0

### Step 3: distribute-skills.sh dry-run

```bash
bash scripts/distribute-skills.sh --dry-run
```

期待: tier-judge の差分が Step 4 追加分のみ、 exit 0

### Step 4: git diff --check + status

```bash
git diff --check
git status --short
```

期待: whitespace error / merge marker なし、 本 PR 関連 files のみ staged (gate 実装 6 + plan draft 1 = 7 files、 pre-existing unstaged 別 file は除外)

注: `blocks/19-character-gate.md` は `.gitignore` の過剰広域 `skills/` パターン (本来 `.agents/skills/` broken symlink 用) に該当するため `git add -f` で明示追加する。 blocks 01-18 も同状況下で tracked 済 (gitignore 整理は 5/12 ops improvement「今後検討」項目)。

## rollback path

### Step 1: template repo rollback

```bash
git log --oneline main | head -5
git revert <pr-merge-commit-sha> --no-edit
git push origin main
```

### Step 2: distribute rollback (任意)

- block 19 を `blocks/` から削除 → `distribute-claude-md-blocks.sh` production run で marker section を空に戻す
- tier-judge Step 4 を revert → `distribute-skills.sh` production run で各課 sync

### Step 3: 各 peer self-revert (peer responsibility)

```bash
git rm .github/pull_request_template.md
git revert <marker-insertion-pr-merge-commit>
git commit -m "revert: dev flow gate rollout (template課 PR revert per)"
git push
```

## 今後検討すべき改善候補

### Phase 2 評価 (target 2026-05-27)

- soft enforcement compliance 測定 → hard CI gate (PR body grep) 要否判定
- hard 化する場合は各 peer repo への GitHub Actions workflow 追加設計

### 論点2-4 後続 (B=再発防止優先 per)

- 論点2: 正本 3 文書集約 (Release Gates / QA Protocol / Peer Dispatch Protocol) + 知識配置ガイド (memory/docs/skill/rule 4象限) — CCO scope。 memory 索引漏れ点検は conductor 先行実施済 (MEMORY.md 6 件追加)
- 論点3: skill inventory 週次自動 export (`docs/skill-inventory.md`) — cowork 主担当
- 論点4: context 負担作業の新規ツール逃し (heartbeat 自動化 / 重い検証 script 化)

## 参照 file

- spec source: `/Users/kimny/Dropbox/_DevProjects/_conductor/docs/inbox/dev-flow-improvement-mtg-20260520.md`
- Plan: `docs/drafts/dev-flow-gate-plan-20260520.md` (draft 0.2、 conductor 承認済)
- 既存 pattern reference:
  - `.claude/skills/common-claude-md-blocks/SKILL.md` (Phase 2 0.1-0.3 設計)
  - `.claude/skills/tier-judge/SKILL.md` (Tier 判定フロー)
  - `docs/cognitive-load-v3-rollout-20260519.md` (migration note 構造)
- conductor approval: 2026-05-20 (SP1 条件付き accept + SP2/3/4 accept)
