# Tier 2 レビューマトリクス 再設計 (draft) — 組織再編 v2 (2026-06-11)

- 起案: CCO (template課)、conductor 依頼 (b) / kimny org再編 v2 (Q1-Q7 確定)。
- 区分: 全課波及の review governance 変更 = canonical (経営部 CLAUDE.md `PRレビュー権限` 表)。**conductor review → /plan 要否判断 → 反映 → 配布**。
- 根拠: v2 §50「畳み込み・スピンアウトのたびに Tier2 マトリクスを CCO が再設計（必須）」。
- ★保護条件 (v2 §63-②): **native の畳み込みは本 matrix が main に入ってから**。= 本 matrix merge 前は native を reviewer/reviewee として残す (transition 中の review 断絶回避)。

## 組織変更の写像 (旧→新)

| 旧 | 新 | 備考 |
|---|---|---|
| native (mued/apps) | **product課** に畳む | product課 = native/occur の畳み先・製品横断統括。畳込は本matrix main後 |
| occur | closed (product課 に記憶) | 配布除外済 PR#104 |
| write / LP / blender | **content課** (母体 `_contents-writing`) | 制作・配信統合 |
| reserch / data | **insight課** (母体 `_data-analysis`) | reserch dormant化、free15計測は母体継続=無断絶 |
| (新設) | **product課** `_product` / **Chief** `_chief` (on-demand) | |

常時起動 code-producing 課: mued / dsp / product課 / content課 / SNS / insight課 / growth / freee / cowork / CCO。Chief は `_strategy/_chief` のみ書く=**コードPR出さない→matrix対象外**。

## 新 Tier2 レビューマトリクス (reviewee → reviewer)

| reviewee | reviewer | dept ロジック / 旧マトリクスからの継承 |
|---|---|---|
| **mued** | **product課** | 旧 mued↔native の継承 (product課 が ex-native/apps を保持・最も文脈濃い)。product核 相互 |
| **product課** | **mued** | 同上・相互 |
| **dsp** | **CCO/template** | 旧 dsp→template/CCO を踏襲 (build/AAX/infra 競合性) |
| **content課** | **SNS** | 旧 write↔SNS の継承 (marketing 制作↔social 隣接)。相互 |
| **SNS** | **content課** | 同上・相互 (旧 SNS→write) |
| **insight課** | **freee** | 数値/計測↔会計の隣接。相互 (旧 data→mued を mued 過負荷回避で再割当) |
| **freee** | **insight課** | 旧 freee→LP (LP消滅) を数値隣接で再割当・相互 |
| **growth** | **content課** | 戦略↔制作 隣接。growth は「機械持たない」純化ゆえ主に Tier1/docs、コード時のみ |
| **cowork** | **CCO/template** | infra↔infra (cowork集約 ↔ template配布正本) |
| **CCO/template** | **conductor + Codex** | shared canonical = Tier3 寄り。従来通り conductor 提出 + Codex 2nd-eye |

### 負荷バランス
- CCO: dsp + cowork (2) + 自canonical。content課: SNS + growth (2)。mued↔product課 / insight課↔freee は各1相互。
- dsp は reviewed のみ (review 役0) = 音質詰め熱の専属を保護 (意図的)。
- mued は product課1本のみ (free15 専属熱を保護、旧 data→mued の負荷を insight↔freee へ移譲)。

## 据え置く一般ルール (変更なし)

- DBスキーマ純粋追加 (CREATE TABLE / ADD COLUMN nullable / index) = Tier2。
- hook/settings 変更が自peer内のみ = Tier2 / 全課波及 = Tier3。
- 価格・認証・破壊的スキーマ・本番設定・新外部サービス・template波及・全課波及hook = Tier3 (conductor)。
- CI 不通過 PR は Tier 問わず merge 禁止。

## 移行手順 (承認後)

1. 経営部 CLAUDE.md の `PRレビュー権限` 表を本 matrix に差し替え (canonical)。
2. `distribute-claude-md-blocks.sh` で配布 (content課/insight課/product課 が marker 有か確認 — 母体 `_contents-writing`/`_data-analysis` は既存 marker 継承、`_product` は新規ゆえ marker 挿入要)。
3. **本 matrix が main + 配布完了を確認してから** native 畳み込み実行 (保護条件)。
4. §9 初週レビューで content/insight/product課 の review が回るか実績確認 → 必要なら再調整。

## 未確定 / conductor 判断

- product課 `_product` は新規 workspace = marker 未挿入。配布前に marker 挿入 or 初期 CLAUDE.md 整備が要る (CCO が cowork/conductor と)。
- growth が「機械持たない」なら growth は reviewee として登場頻度低 (主に Tier1)。reviewer 割当 (content課) は念のため。
- insight課↔freee の相互は新ペア = 初週で competence 適合を観察 (data/分析 PR を freee が、freee-MCP を insight課が、互いにレビューできるか)。不適なら insight課→CCO 等へ再割当候補。
