# Workstream 3 — 共通 PR テンプレ + キャラクター gate 定義 Plan (draft 0.2)

- [x] conductor 承認 (5/20、 SP1 条件付き + SP2/3/4 accept)

## Context

開発フロー改善 MTG (`_conductor/docs/inbox/dev-flow-improvement-mtg-20260520.md`、 kimny 5/20 GO) 論点1 の全課波及部分。 起点 = MUEDear Build 78 事故 (基本 UI 見切れバグが TypeScript 0 error + Tier 2 LGTM + Apple Archive 成功で「テスト通過」と誤認され TestFlight 素通り)。

kimny 判断: A=gate 優先 / B=再発防止 gate 最優先 / **C=承認 (CCO 主導 Tier 3 GO)**。

CCO scope = **全課共通の gate 定義 + PR テンプレ**。 native verify-ui.sh (Workstream 1) / LP gw-dash スクショフロー (Workstream 2) は自課実装、 conductor が整合。

## 診断 (MTG 全員一致)

「テスト通過」の意味が「コードが壊れていない」に偏り「成果物が実際に使える」を含んでいない。 機械チェック (型/lint/build/コード LGTM) と人間チェック (実機で遊べる/試聴/読者視点) が同じ「通過」語で曖昧化 = 誤認の温床。

## Approach

既存 distribution pattern 踏襲、 「他peerワークスペースを直接変更しない」 template課 protocol 厳守。 deliverable 3 件:

1. **共通 PR テンプレート** — `docs/templates/` canonical + 各 peer 自走 copy
2. **キャラクター gate** — common block 19 (`distribute-claude-md-blocks.sh` 既存 14課 pattern)
3. **tier-judge skill 拡張** — UI/成果物変更検出 branch (`distribute-skills.sh` 既存 pattern)

## Deliverable 詳細

### D1. 共通 PR テンプレート

**canonical**: `docs/templates/pull-request-template.base.md` (新規)

PR body section 構成:
- `## Summary`
- `## Tier` — [self-review] / [peer-review: 課名] / [Tier 3] タグ判定
- `## 機械チェック` — `[ ] 型チェック通過` `[ ] lint 通過` `[ ] ビルド成功`
- `## 成果物 verify` (MTG 工程名分離 per、 機械チェックと**別セクション**)
  - `[ ] キャラクター gate 確認 (自課の人間判断 gate を 1 つ)`
  - `[ ] スクショ / 録画 添付` ← UI/成果物変更 PR は必須
- `## 証拠` — スクショ/録画 リンク。 **証拠なしには「通過」と書けない原則** 明記 (「見た」だけ・証拠なし = 未検証扱い)

**配布方式**: 各 peer 自走 copy (auto-distribute script は作らない)。 理由:
- `.github/pull_request_template.md` は peer repo 固有 file、 auto-overwrite は各課のキャラクター gate 記述を clobber する
- PR テンプレは継続 sync 不要 (CLAUDE.md block と違い頻繁に変わらない)、 改訂時は conductor relay 再 dispatch で足りる
- → 本 PR merge 後 conductor relay 経由で「base を `.github/pull_request_template.md` に copy + 自課キャラクター gate 1 行 fill」を各 peer dispatch (peer responsibility)

template課自身の `.github/pull_request_template.md` は本 PR 内で作成。

### D2. キャラクター gate — common block 19

**新規**: `.claude/skills/common-claude-md-blocks/blocks/19-character-gate.md`

内容 (common、 peer-fill なし):
- キャラクター gate 概念 = 機械テストで構造的に拾えない、 人間が知覚して初めて分かる合格基準。 各課が 1 つ名指しする
- 工程名分離原則 (「ビルド成功 ✓」と「実機で遊べた ✓」を別チェックボックスに)
- 証拠なしには「通過」と書けない原則
- ツール化できない一線 (dsp 但し書き): 最終的なキャラクター判断は構造的に人間のもの。 ツールは段取りを減らせるが判断自体は代替不可
- 自課の具体的 gate 名は各 peer CLAUDE.md / PR テンプレに記述 (block 自体は common のまま)

**配布**: 既存 `distribute-claude-md-blocks.sh` (TARGET_PEERS 14課 不変)。 block 19 用 marker `<!-- COMMON-BLOCK-START: 19-character-gate -->` の各 peer CLAUDE.md 挿入は peer responsibility (cognitive load v3 step 10 と同 pattern、 conductor relay dispatch)。

### D3. tier-judge skill 拡張

**修正**: `.claude/skills/tier-judge/SKILL.md`

判定フロー Step 3 の後に **「UI / 成果物変更検出」** branch 追加:
- 検出パターン例: `*.tsx` `*.jsx` `*.css` `*.scss` `*.swift` `*.blend`、 viewport/layout/component file、 LP page、 CLI 出力 format 変更
- 検出時の出力: 「この PR は UI / 成果物変更を含む → 成果物 evidence (スクショ/録画 + キャラクター gate 確認) 必須。 evidence なし PR は Tier 問わず merge 不可」
- Tier 数値判定 (1/2/3) は不変、 evidence requirement を追加 warning として出す
- **SP1 条件(1) 反映**: UI/成果物変更検出時の evidence 必須 warning は出力フォーマットの**固定 section** とし、 該当 PR で必ず発火する (条件付き表示でなく検出時 unconditional)。 Build 78 教訓「ルールはあるが強制 gate でなかった」 = soft でも素通り不可の最低ラインを skill 出力構造で担保

**配布**: 既存 `distribute-skills.sh` (`tier-judge` 既に `COMMON_SKILLS` 内、 全課対象)。

## 変更ファイル (本 CCO PR、 template repo、 Tier 3)

```
新規 (4):
  docs/templates/pull-request-template.base.md
  .github/pull_request_template.md           (template課自身用、 base から)
  .claude/skills/common-claude-md-blocks/blocks/19-character-gate.md
  docs/dev-flow-gate-rollout-20260520.md      (migration note)

修正 (2):
  .claude/skills/tier-judge/SKILL.md          (UI evidence branch 追加)
  .claude/skills/common-claude-md-blocks/SKILL.md  (block 19 登録、 18→19 blocks)
```

計 6 files。 **Tier 3** (template課変更 = 全課波及)。

## Out of scope (他 Workstream / 後続)

- native `verify-ui.sh` (Workstream 1、 native 自課) — iPhone SE 自動操作 + 色判定 hard gate
- LP gw-dash スクショフロー (Workstream 2、 LP 自課)
- Codex 事前 QA gate / Playwright スクショ差分 CI (論点1 #3 #4、 別 Workstream)
- 論点2-4 (ナレッジ集約 / skill inventory / context 逃し) — B=再発防止優先 per 後続。 skill inventory 整理は CCO scope だが順次
- 各 peer の `.github/pull_request_template.md` copy + キャラクター gate fill (peer responsibility、 本 PR merge 後 conductor relay)
- 各 peer CLAUDE.md の block 19 marker 挿入 PR (peer responsibility、 同上)

## conductor への scope 調整提案

**SP1 — enforcement は Phase 1 soft** (conductor 条件付き accept): 「evidence なし = merge 不可」 の全課共通 hard 強制 (PR body grep の CI gate) は Phase 2 follow-up。 Phase 1 = PR テンプレ checkbox + tier-judge warning + reviewer 義務 (soft、 cognitive load v3 Phase 1 soft enforcement と同方針)。 理由: 全課共通 hard CI gate は各 peer repo に GitHub Actions workflow 追加が要り Build 79 を block しうる。 Build 78 型バグの hard gate は native verify-ui.sh が担う = 二層で十分。

conductor 承認条件 2 点 (本 draft 0.2 で反映済):
- **条件(1)** — soft でも形骸化させない。 tier-judge warning は UI/成果物変更 PR で**確実に発火** (D3 に反映: 出力フォーマット固定 section 化、 検出時 unconditional)。 素通り不可の最低ライン。
- **条件(2)** — Phase 2 を曖昧にしない。 **論点1 完了 (本 PR merge + WS1 native verify-ui.sh + WS2 LP gw-dash 完了) から 1 週間以内に soft enforcement の compliance を測定して Phase 2 (hard CI gate) 要否を評価**。 target 期限 = **2026-05-27 JST** (WS1/WS2 完了が遅延する場合は完了日 +7 日に conductor が再設定)。 評価 metric: UI/成果物変更 PR のうち成果物 verify section が evidence 添付済の割合 (目標 95%、 cognitive load v3 Phase 1 soft 基準と整合)。

**SP2 — PR テンプレは peer 自走 copy**: auto-distribute script を作らず conductor relay 1 回 dispatch。 理由は D1 記載 (`.github/` overwrite が各課キャラクター gate を clobber)。

**SP3 — キャラクター gate は block 19 (概念) + PR テンプレ (具体 gate 名) で非重複**: block は common 概念のみ、 自課 gate 名は PR テンプレ 1 行。 2 箇所に同内容を持たせない。

**SP4 — 論点2 後続確認**: ナレッジ集約は本 Plan scope 外、 B=再発防止優先 per 後続着手で合意確認。

## Verification (実装後 self-verify)

1. block 19 syntax: `head -1` で `## ` heading 開始、 frontmatter なし (既存 blocks 01-18 整合)
2. `bash scripts/distribute-claude-md-blocks.sh --dry-run` — `Loaded 19 blocks`、 14課で marker 未挿入 = `NO CHANGES`、 Python traceback なし、 exit 0
3. `bash scripts/distribute-skills.sh --dry-run` — tier-judge 差分が UI branch 追加分のみ、 exit 0
4. `git diff --check` — whitespace / merge marker なし
5. `git status --short` — 6 files のみ (pre-existing unstaged 別 file 除く)
6. PR テンプレ base — 機械チェック section と成果物 verify section が**別見出し**で分離 (工程名分離原則の遵守 self-check)

## rollback path

1. template repo: `git revert <merge-commit>` + push
2. block 19 削除 + 再 distribute production run で空 marker 化
3. 各 peer: `.github/pull_request_template.md` 削除 + block 19 marker revert (peer self-revert)

## ETA

- Plan → conductor 承認: ~10 min (本 doc)
- 実装 (4 新規 + 2 修正): 1.5-2 h
- verification (dry-run 2 本 + diff): ~20 min
- PR + 承認後 self-merge: ~15 min
- **合計 ~2.5-3 h**

## Acceptance criteria

- PR テンプレ base に機械チェック / 成果物 verify が別 section で分離
- block 19 = キャラクター gate 概念 + 工程名分離 + 証拠原則 + ツール化できない一線
- tier-judge に UI/成果物変更検出 branch + evidence 必須 warning
- distribute 2 script dry-run pass (traceback なし、 exit 0)
- migration note 7 section + rollback path + peer 自走 handoff 明示
- 6 files、 全課波及 Tier 3、 conductor 承認後 self-merge
