# CCO review — freee PR #28 CFO Monetization Baseline Audit (2026-05-26)

- review 対象: https://github.com/kimny1143/gw-freee-mcp/pull/28
- review focus per conductor dispatch (2026-05-26 11:06 JST): 4 軸 (quick-win 候補 / growth baseline 整備性 / 未解決 7 件 dispatch / 3 軸 canonical 整合)
- output: 本 doc (CCO 課 traceability) + PR #28 review comment (concise version)

## 0. Overall assessment

**LGTM with 2 actionable + 3 informational comments**。 391 行 audit doc は growth 課着任時 baseline material として **substantially ready** ✅、 critical finding (末端 ready / 入口死蔵) は CCO 観点でも整合、 codex「First Paid Signal Sprint」 提案と clean alignment evidence。 minor 修正候補は launch cycle 内 sequencing で吸収可能、 5/28 active launch blocker なし。

## 1. 3 軸 quick-win 候補 整合性 (focus 1)

audit doc §3.3 + §5.3 priority 表で挙げた 3 候補は CCO 観点でも妥当:

| 候補 | CCO assessment | rationale |
|------|---------------|-----------|
| Gumroad Template Pro reach 流量設計 | ✅ **最優先 confirm** | template 課 own product (`project_premium_content.md` memory)、 構造 + 価格 + 経路全揃い、 reach 不在のみ。 template 課直接関与可能 = sprint sub-task として CCO drive 候補 |
| MUEDial Hoo Pass post-research beta reach 設計 | ⚠️ **sequence 推奨** | data 課 scorecard v3 連携前提 = 5/13+ 実データ shipping 待ち = parallel ではなく sequential (Gumroad 後着手) 推奨、 growth 着任直後 2 並行は bandwidth overload risk |
| note 有料記事 candidate 抽出 | ✅ **write 課協働で並行可** | CCO scope 外 (write peer 主管)、 ただし `ai-interview-article` / `note-serial-monetization` / `copywriting` skill 全 template 配布済 = growth 課 (skill 配布対象、 PR #83 経由) で skill 即利用可 |

### actionable comment #1 (growth 課 sprint sequence 推奨)

`§5.3 Window B sprint 設計 input` 表で 🔴 高 = 2 件 (Gumroad + Hoo Pass) 並列扱い → growth 着任直後 7 日 ramp-up bandwidth 考慮、 **🔴 高は Gumroad 単独**、 **Hoo Pass は 5/13+ data scorecard v3 shipping trigger 待ちで 2nd wave** に sequence 表記推奨。 audit doc 内 1 行修正で吸収可能 ([ESTIMATE] 表現を「Phase 1 (week 1)」「Phase 2 (data ready 後)」 split)。

## 2. growth 課着任時 baseline material 整備性 (focus 2)

### 2.1 distribute scripts (PR #82 + PR #83) との連動

- PR #82 (task #24 ii-a hybrid、 13 peer canonical 配布) 既 merge ✅ = growth 課 (5/28 launch 後) も canonical broadcast 対象 (PR #83 経由)
- PR #83 (growth onboarding、 14 peer 体制) conductor review 待ち = merge 後 distribute scripts 14 peer 整合
- audit doc 内 canonical 参照 = `[[project_phase_2_4_completion_20260508]]` / `reference_pricing_facts_hub` 等 conductor + freee 課 memory 中心、 growth 課 memory 直接配布対象は **canonical pricing block (PR #82 universal items)** のみ
- → audit doc 自体は freee 課 `docs/inbox/` 配置で OK、 growth 課への複製不要 (sync protocol cadence で monthly review 内参照)

### 2.2 4 軸 product / channel → growth task list mapping

audit doc §5.3 Window B sprint priority 表は growth task list source として **直接利用可能** ✅:
- 🔴 高 2 件 → growth 課 first 7 days sprint backlog (上記 sequence 推奨適用後)
- 🟡 中 2 件 → growth 課 2-3 week backlog
- 🟢 低 2 件 → growth 課 month 1 backlog
- ⚫ defer / ❌ excluded → backlog 除外 (Phase 5 商用 beta 待ち / kimny 明示指示待ち)

audit doc § 5.3 表をそのまま growth `CLAUDE.md` Section 4 or task list initial seeding 推奨。

### 2.3 sync protocol cadence (PR #83 設計 doc Section 6-1 整合)

PR #83 設計 doc で proposal 済 sync cadence:
- **freee ↔ growth**: monthly = P&L review + 死蔵商品 retention 進捗
- 初回 baseline material = 本 audit doc + 6/30 月次 update (sprint 1 結果込み)
- audit doc §5.2 「growth 課が CFO に依頼可能な作業」 5 項目 = sync 議題 standing item 候補

### informational comment #2 (sync protocol 整合)

audit doc に明示なし、 PR #83 設計 doc Section 6-1 で確立済 monthly freee↔growth cadence と整合済 = 修正不要、 informational only。 audit doc 末尾「next action」 に「6/30 month-end update 配信 (growth 課 sprint 1 結果反映)」 1 行追加で sync visible 化可。

## 3. 未解決 7 件 dispatch path (focus 3)

CCO 視点 dispatch path 分類 + 5/28 active launch 前完納目標 priority:

| # | 項目 | dispatch 主体 | path | launch 前完納 |
|---|------|------|------|--------------|
| 1 | MUEDnote 現状照会 (native 課) | **conductor → native** | 即 dispatch、 公開状態 / monetization 候補 1 cycle 確認 | **必須** (growth 着任時「MUEDnote status 不明」 では sprint design 不可) |
| 2 | Ko-fi bundle (kimny 直接) | **conductor → kimny** | kimny 1 cmd (page URL + 現状商品 list 共有)、 audit 不可 = canonical 不在 confirmed | 推奨 (canonical 確立で audit scope 拡張) |
| 3 | kimny 個人 music revenue (CFO scope) | **conductor → kimny** | 1 質問 (scope 内/外 判断のみ) | 推奨 (audit scope clarity) |
| 4 | MUEDear iOS monetization (A/B/C/D) | **conductor → growth+native+mued 3 者協議** | 5/28 active launch 後 dispatch (growth 着任直後 first batch 過剰、 6 月中旬決定目標 audit per) | **不要** (sprint 内処理) |
| 5 | Cryo Mix subscribe (kimny 残作業) | **conductor → kimny reminder** | kimny attention 1 cycle | 任意 (MUEDial Mastering 品質競争力 trigger、 急ぐ場合のみ) |
| 6 | AAX Phase 5 launch (Avid 返信待ち) | **freee 課 self-monitoring** | external dependency、 dispatch 不要 | **不要** (external、 待ち) |
| 7 | note 有料記事 candidate 抽出 (write 課) | **conductor → write** | dispatch、 既存無料記事 audit + 候補 list 起案 | 推奨 (growth 着任時 sprint 第 3 候補 ready 化) |

### actionable comment #3 (launch 前必須 1 件)

**#1 MUEDnote 現状照会のみ launch 前必須**、 残 6 件は launch 後 / 待ち / 任意。 conductor → native 1 cycle dispatch 推奨 (1 質問 + 1 cycle 返答で完納可能)。

### informational comment #4 (CCO drive 不要 confirm)

7 件いずれも CCO drive 範囲外 (conductor / kimny / freee / native / write / growth scope)。 CCO は本 audit doc review + growth `CLAUDE.md` 設計 doc 整合のみ責任範囲、 dispatch は conductor 主導で OK。

## 4. 3 軸 canonical 整合性 (focus 4)

### 4.1 数値整合 verify

template repo canonical (PR #82 merged、 `scripts/distribute-quality-standards.sh` HEREDOC) vs audit doc 数値:

| 項目 | template canonical | audit doc | 整合 |
|------|-------------------|-----------|------|
| 軸1A render 系粗利率 | 58-63% | 58-63% (§2.1 + §2.3) | ✅ |
| 軸1B 縦SaaS系粗利率 (Twilio標準) | 50-60% (5/10 kimny判断A) | 50-60% (5/10 kimny判断A、 §2.1 + §1.1 + §1.4) | ✅ |
| 月次COGS上限 | $200/月 (research beta 期間限定) | $200/月 (§2.2 + §4.1) | ✅ |
| 業態定義 | API-enabled vertical application | (明示なし、 含意整合) | ✅ (省略 OK) |

### 4.2 軸1C 95-100% の template canonical 未収録 (既知 gap)

audit doc §2.1 で **軸1C AAX 商用販売 95-100% binding final** 言及あり、 ただし template canonical (`feedback_kimny_quality_standards.md`) には 軸1A / 軸1B のみ収録、 軸1C 未収録。

**判定**: ✅ **意図的、 修正不要**
- 軸1C は dsp 課固有 (MUEDsp v1 AAX 専用) = 全課共通 quality standard ではなく peer-specific reference
- 全課 broadcast 対象に含めると noise (dsp 課以外 actionable なし)
- conductor `docs/financials/aax-pricing.md` (Phase B 予定) で peer-specific canonical 保持 OK

### 4.3 撤退判定 monitor 4 項目 整合

audit doc §4.3 で 4 項目掲載 ([[project_phase_2_4_completion_20260508]] per):
1. 6 ヶ月で raw 30 未満 → ユーザー獲得失敗
2. 12 ヶ月で qualified 5 未満 → PMF 未達
3. 受託売上¥150K/月以下 → 全社財務リスク
4. Hoo Pass 継続率 D30<30% / D60<15% → 軸1B 縦 SaaS 基準維持困難

→ template canonical 未収録 (CCO 観点では peer-specific = freee 課 reference)、 modify 不要。 ただし growth 課 sprint 評価軸 (audit doc §6) と直接 link するため、 growth `CLAUDE.md` で「撤退判定 monitor 4 項目は freee 課 audit doc §4.3 参照」 cross-reference 推奨。

### informational comment #5 (canonical 整合 confirm)

3 軸 policy (軸1A / 軸1B / 月次COGS上限 / 業態定義) は template canonical (PR #82) と完全整合 ✅、 軸1C は dsp peer-specific として template 未収録は意図的、 修正不要。

## 5. CCO observations (追加 informational)

### 5.1 audit doc §9 「CFO 提案 3 件」 = growth 着任 OUT OF SCOPE

- 軸1C policy v2 拡張 / 学習 signal 混雑 monitor / conductor 巡回 capacity monitor の 3 件は **freee 課自走 / conductor scope**、 growth 課着任時 baseline material としては不要
- → audit doc 内に含まれる必要なし、 別 dispatch (freee 課 → conductor 提案 batch) 推奨
- 修正必要 (audit doc §9 削除 or footnote 化、 「growth 着任 baseline と直接関係なし、 CFO 自走 proposal」 と framing)

### actionable comment #6 (§9 framing 微修正)

audit doc §9 「CFO 提案 3 件」 を「growth 着任 baseline 関連なし、 CFO 自走 dispatch 候補」 と framing 修正 (1 行追記 or section header rename) 推奨。 現状の章順だと growth 課 reviewer が §9 まで読んで自分の sprint scope か CFO 自走か境界不明瞭。

### 5.2 priority 順「2nd opinion + 反証係」 protocol との連動

trilateral 議論 5 件 batch (kimny 5/26 GO) で確立した「全 3 者一致原則 #5 反証係 (Codex / 一次ソース)」 = audit doc は **freee 課単独 audit、 codex 2nd opinion 未実施**。 5/28 active launch 前に codex 2nd opinion 1 cycle (codex に audit doc → 末端 ready 構造 + 入口設計 fact check) 推奨。

### informational comment #7 (反証係 codex 2nd opinion 推奨)

audit doc final approve 前に codex 2nd opinion 1 cycle 推奨 (trilateral 反証係 protocol per)。 conductor drive、 ETA 5-10 分想定。

### 5.3 fact-check runbook v3 §8.0 適用 確認

audit doc frontmatter で `fact_check_runbook: docs/glasswerks/cfo-fact-check-runbook.md v3 §8.0 適用` 明示 ✅、 全数値に [FACT] / [CONFIG] / [ESTIMATE] / [FORECAST] label 付与 ✅、 Edit 直後 grep verify 完納 ✅ = freee 課 internal release gate clean。

## 6. PR #28 review verdict

- **LGTM (Tier 2 audit doc、 構造 + canonical 整合 perfect)** ✅
- 2 actionable + 5 informational comments
- self-merge GO (Tier 2 ペアレビュー = LP 課 既 並列 dispatch、 conductor own review 並列) recommend
- launch 前必須 dispatch = 未解決 #1 MUEDnote 現状照会 1 件のみ (conductor → native dispatch path)

## 7. 5/28 active launch 前 sequencing 提案 (CCO 視点)

| date | action | 主体 |
|------|--------|------|
| 5/26 EOD | PR #28 conductor + LP + CCO review 完納 → minor 修正 1 cycle | freee |
| 5/27 朝 | MUEDnote 現状照会 conductor → native dispatch | conductor |
| 5/27 朝 | PR #28 codex 2nd opinion dispatch | conductor |
| 5/27 昼 | PR #28 final approve + merge | kimny + conductor |
| 5/27 昼 | audit doc §5.3 priority 表 → growth `CLAUDE.md` Section 4 反映 | conductor (growth `CLAUDE.md` 自走 path per) |
| 5/28 active launch | growth 着任 → audit doc baseline material 直接利用 | growth peer |

## 8. CCO review summary

audit doc 391 行は freee 課 high quality deliverable ✅、 PR #28 LGTM、 5/28 active launch baseline material として ready。 minor 修正 2 件 (sprint sequence + §9 framing) + dispatch 1 件 (MUEDnote 照会) で 5/28 launch blocker 解消。 codex 2nd opinion は trilateral 反証係 protocol per recommend。
