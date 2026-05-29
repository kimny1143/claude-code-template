# 共通ブロック圧縮 fanout dry-run レポート — 2026-05-29

PR #90 (source 圧縮 582→312行) merge 後の fanout 前 read-only 検証。各 peer CLAUDE.md に対し distribute 置換ロジックを **in-memory simulation**（peer repo 未書き込み）した結果。

## per-peer dry-run summary

| peer | markers | before | after | net |
|------|---------|-------:|------:|----:|
| **freee** | 18 filled | 786 | 528 | **-258** ✅圧縮 |
| **cowork** | 18 filled | 785 | 527 | **-258** ✅ |
| **mued** | 18 filled | 1010 | 752 | **-258** ✅(※mued slim 並行) |
| **write** | 18 filled | 802 | 544 | **-258** ✅ |
| **LP** | 18 filled | 776 | 518 | **-258** ✅ |
| **reserch** | 18 filled | 755 | 497 | **-258** ✅ |
| **data** | 18 filled | 802 | 544 | **-258** ✅ |
| template | 18 **空** | 166 | 509 | +343 ⚠️bloat |
| dsp | 18 **空** | 130 | 491 | +361 ⚠️bloat |
| occur | 18 **空** | 226 | 569 | +343 ⚠️bloat |
| conductor | 0 marker | 96 | 96 | 0 (no-op) |
| native(apps) | 0 marker | 159 | 159 | 0 (親継承) |
| SNS(threads) | 0 marker | 632 | 632 | 0 (no-op) |
| blender | 0 marker | 58 | 58 | 0 (no-op) |

## ⚠️ 最重要発見: 3 つの fanout カテゴリ + 空 marker bloat trap

distribute は全 14 TARGET_PEERS を一律処理するため、**blanket execute は危険**。3 群で挙動が真逆:

### 群A: filled marker 7課 (freee/cowork/mued/write/LP/reserch/data) → 圧縮 ✅
- 旧 verbose block が入った状態 (各 ~786行) → 圧縮 block で置換 → **-258行/課**。conductor 当初監査の「7 peer 40k超」= この群。**これが本施策の本命 win**。

### 群B: 空 marker 3課 (template/dsp/occur) → ⚠️ bloat (anti-goal)
- marker は挿入済だが**中身が空** (block01 marker内 実コンテンツ 0 行で検証済)。= 現状これらは共通ブロックを **load していない** (conductor 監査の「slim・共通ブロック非保持」と一致)。
- distribute execute すると空 marker が**埋まり +343〜361行 bloat** → slim peer を太らせる = 施策目的と真逆。
- **対処案**: distribute 対象から除外し、**空 marker を削除して slim 維持** (推奨)。または load させたいなら fill だが、監査方針 (slim 維持) と矛盾。
  - template は CCO 自 workspace → CCO が空 marker 削除可 (自走)。
  - dsp/occur は他 peer workspace → dsp/occur 課 or conductor 調整で空 marker 削除。

### 群C: marker なし 4課 (conductor/native/SNS/blender) → no-op
- native は親 mued_v2 継承で対象外 (正しい)。conductor/SNS/blender は共通ブロック marker なし。
- **block14 (conductor専用)**: conductor に marker **追加**して fill が必要 (現状 conductor は active-judgment block を CLAUDE.md に持たない)。

## 推奨 fanout 実行計画

1. **群A 7課のみ distribute execute** → -258/課。各 peer 自 repo で CLAUDE.md commit (conductor 調整、他 workspace 直接変更しない)。
   - ※ mued は slim PR と順序 coordinate (conductor が mued課に声かけ済)。
2. **群B 3課**: 空 marker 削除で slim 維持 (template = CCO 自走、dsp/occur = 課/conductor)。
3. **block14 再配置**: conductor に marker 追加 + fill / 群A の 9課除去対象は…実は群A peer の block14 marker は filled。これらから block14 marker 除去 (conductor-only 化)。
4. **block19 marker**: 群A は 18 marker = block19 (character-gate) marker 未挿入。character gate を全課 load させる方針なら marker 挿入 fanout 別途。
5. **群C**: no-op (native 親継承 OK)。

## block15 audit taxonomy 確認 (conductor minor 指摘への回答)

block15 から削った `false_low` / `false_high` / `evidence_missing` / `missing_marker` taxonomy は **conductor 側に保持済** を確認:
- `_conductor/.claude/skills/checkout/SKILL.md`, `patrol/SKILL.md`
- `_conductor/docs/inbox/proposal-conductor-cognitive-load-v3.md`
- `_conductor/reports/daily/2026-05-{20,27,28}.md`
→ audit を実行する conductor 側に残るため、peer 配布 block15 から削除しても運用に支障なし。圧縮判断は妥当。

## fanout 実行 recipe (conductor (a) 承認後、conductor 調整用)

CCO は他 peer workspace を直接変更しない。以下は conductor が各 peer に dispatch する手順。distribute は既存 marker を fill するのみ (marker の追加/削除はしない) ため、marker 構造変更は手動 step。

### 完了済 (CCO 自走)
- ✅ **template課 (group B)**: 空 marker 18 削除 → slim pointer (166→94行)。PR #91 merged。
- ✅ source 圧縮 (PR #90 merged)、dry-run 検証、block15 taxonomy 保持確認。

### group B 残: dsp / occur (各 peer or conductor)
- 各自 repo の CLAUDE.md から共通 block marker 18 を削除 (空＝未ロードゆえ behavior 変化なし、stale 一掃)。template と同じ slim pointer 推奨。

### group A 7課 (freee/cowork/mued/write/LP/reserch/data) — 各 peer 自 repo で:
1. template repo 最新 (圧縮 block) を参照
2. **block14 marker 除去** (conductor 専用化): 自 CLAUDE.md から `COMMON-BLOCK-START/END: 14-conductor-active-judgment` の marker pair を削除
3. **block19 marker 挿入**: block18 marker の後に `COMMON-BLOCK-START/END: 19-character-gate` の空 marker pair を追加
4. `distribute-claude-md-blocks.sh` で自 CLAUDE.md の marker を fill (01-13,15-19 が圧縮 block で再生成、14 は marker なしで skip)
5. 自 repo で CLAUDE.md commit (Tier 1 docs) → self-merge / conductor merge
- ※ **mued は slim PR を先行** → その上に圧縮 fanout (conflict 回避、conductor が mued課と順序 coordinate)

### conductor 自 repo:
- **block14 marker 追加 + fill**: conductor CLAUDE.md に `14-conductor-active-judgment` marker pair を挿入 → distribute で fill (現状 conductor は active-judgment を CLAUDE.md に持たない)

## projected 削減 (group A、最終確定は各課 commit 後)

- compression baseline: **-258 行/課** (verbose→圧縮、block14 在・block19 不在の sim 値)
- 最終調整: block14 marker 除去 (約 -20行) + block19 marker 挿入 (圧縮 character-gate 約 +25行) ≈ 差し引き **-253行/課 前後**
- 7課合計 ≈ **-1,770行** + token 換算 約 9-10k tokens/課 削減

## 検証メタ

- 全 simulation は read-only (peer repo 未書き込み)。full per-peer unified diff = `/tmp/fanout-full-diffs.txt` (5731行)。
- 群A の diff は全課ほぼ同一 (同じ圧縮 block が verbose block を置換)。
