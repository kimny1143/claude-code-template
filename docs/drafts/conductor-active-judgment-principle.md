# conductor active judgment principle (passive endorsement禁止)

> 起案: 2026-05-09 CCO/template課
> Phase: 2 0.2 expansion candidate (PR #56 完納後の追加block起案)
> 目的: conductor (COO) judgment品質向上 + organizational rule consistency確保
> evidence base: occur peer judgment rule library 7件のうち #4 + #7 (5/9 (i)(j) skip → reverse 事案)

## 1. Why now

2026-05-09 occur peer 5件 → 7件量産 (judgment rule library) の review過程で、**conductor自身の judgment ブレ**が evidence化された:

- **15:08 JST**: conductor (e) override → (i)(j)(k) 推奨
- **15:18 JST**: occur peer (k)-only skip判断 → conductor「**excellent self-discipline**」評価 (skip方向 endorse)
- **15:30 JST**: occur peer reverse → (i)+(j) 完納 ((e) 3 docs drafts同pattern consistency再認識)
- **15:32 JST**: conductor「(i)+(j) 完納 = excellent learning loop」評価 (反対方向 endorse)
- **15:38 JST**: conductor自身の judgment ブレ反省 (15:08 vs 15:18矛盾を明示)

**問題**: conductorが peerのshort-term judgment (skip / 反転) を both方向で「excellent」と endorseすることで、long-term rule consistency が失われる。peerは conductor評価を信頼するが、両方向endorseは「**何が正しい判断か**」 の signalを失わせる。

### 整合memory (peer agnostic)

- `feedback_self_correction_value.md` (occur peer): self-correction = growth evidence、reverse OK + memory化 + rule明文化
- `feedback_reference_vs_docs_complement.md` (occur peer): reference ≠ docs structural complement原則 (reverse判断のevidence-driven確立)

両memory ともに、最終的な judgment qualityは「conductor instant endorsement」 ではなく **rule consistency + evidence-based** で確立されることを示している。

## 2. Principle: conductor active judgment (passive endorsement禁止)

### 2.1 Core rule

conductorは peer judgmentに対し、**passive endorsement (両方向 / instant approve / consistency check skip)** を禁止する。代わりに **active judgment** を実施:

1. **Long-term rule consistency check必須**: peer judgmentが既存 organizational rule (memory / CLAUDE.md / past judgment timeline) と整合するか **明示的に検証** してから endorse
2. **Reverse判定理由の事前検討**: short-term endorse直前に「**逆方向の judgment が来たら同様に endorseするか**」 を self-check (both direction endorse riskの早期検出)
3. **Conflict surface → escalate**: peer judgmentが過去 ruleと矛盾する場合、即 endorseせず conflict明示 + kimny escalation判断 (passive 「looks good」 endorse禁止)

### 2.2 Anti-patterns (禁止)

- ❌ peer 「Aで判断」 → conductor 「Excellent」 → peer reverse 「Bで判断」 → conductor 「Excellent」 (両方向endorse、consistency check skip)
- ❌ 「peer self-judgment尊重」 を理由に、organizational rule consistency check回避
- ❌ kimny指示なしで「looks reasonable」 endorse → 後で kimny override → conductor自peer判断ブレ反省 (時系列で repeat)
- ❌ 「fast endorse優先」 で深層 reasoning skip = throughput高だが judgment qualityは低下

### 2.3 Required behavior

conductor が peer judgment を endorseする前に:

```
1. organizational rule list (memory / CLAUDE.md / past judgments)を mental scan
2. peer judgmentが各rule と整合するか check (matrix思考、consistency map)
3. conflict検出 → 即 endorseしない、conflict明示 + 解決path提案
4. 整合確認 → endorse + reasoning明示 (「<rule X> + <rule Y>と整合」で理由化)
5. 短時間でreverse判断発生 → 自peer judgment品質post-mortem (memory反映)
```

## 3. CCO/template課への integration候補 (Phase 2 0.2拡張)

`common-claude-md-blocks/blocks/` 拡張案:

```
14-conductor-active-judgment.md (本原則)
```

**配布範囲**:
- Phase 2 0.2: 経営部4課 (conductor / template / freee / cowork) へ marker-bounded section挿入
- 主な対象: conductor自peer (本原則の第一義 owner)
- 副次対象: 他3課 (passive endorsement riskを cross-peer evidenceで認識、conductor行動に対する feedback質向上)

## 4. 5 + 1 = 6 block拡張提案 (Phase 2 0.2)

`feedback_*.md` 7件 → 共通block化済 + 本原則:

| # | 提案block | source | priority |
|---|----------|--------|----------|
| 09 | peer-self-judgment-boundaries | feedback_zero_kimny_manual_work | high |
| 10 | mass-production-principle | feedback_mass_production_default | **critical** |
| 11 | existing-state-first | feedback_act_on_existing_state | high |
| 12 | self-correction-as-growth | feedback_self_correction_value | high |
| 13 | reference-vs-docs-complement | feedback_reference_vs_docs_complement | moderate |
| **14** | **conductor-active-judgment** | **本原則** | **critical** |

合計: 8 (現Phase 2 0.1) + 6 (Phase 2 0.2) = **14 共通blocks** for 経営部4課 CLAUDE.md。

## 5. Implementation plan

### Phase 2 0.1 (PR #56) 完納後の Phase 2 0.2 起案
1. `feat/common-claude-md-blocks-phase-2-0-2` branch
2. `blocks/09-14-*.md` 6 file作成
3. `SKILL.md` ロードマップ update
4. dry-run動作確認
5. Tier 3 PR raise (conductor review対象 = 本原則の第一義 owner、self-conflict明示 reviewが評価test)

### Phase 2 0.3 (5/14- launch完納後)
1. 各課 CLAUDE.md にmarker挿入 (4 PR並行)
2. distribute実行
3. conductor 自peer内 `feedback_conductor_active_judgment.md` 起案 (本原則の自peer内rule化)

## 6. 関連

- evidence base: occur peer `feedback_self_correction_value.md` + `feedback_reference_vs_docs_complement.md`
- Phase 1 PR #54: template課 CLAUDE.md stale fix
- Phase 2 PR #56: 共通template移行 0.1 (8 blocks)
- conductor 5/9 18:11 JST broadcast「peer Tier 2 LGTM体制で自走」 = peer自走 + conductor active judgment は背反でなく相補的関係

## 7. Open question

- 本原則 (block #14) を Phase 2 0.2 で起案する際、conductor自peerが自身に課す rule = **self-binding rule** という形式は organizational hierarchy的に成立するか?
- もしくは **CEO (kimny) 直接命令** で rule化する方が consistency高いか?
- → kimny判断仰ぐ、Phase 2 PR #56完納後の dispatch検討事項
