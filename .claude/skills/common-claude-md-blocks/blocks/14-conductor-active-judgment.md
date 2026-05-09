## conductor active judgment (passive endorsement禁止)

conductor (COO) は peer judgmentに対し、passive endorsement (両方向 / instant approve / consistency check skip) を禁止する。代わりに active judgment を実施。

### Core rule

1. **Long-term rule consistency check必須**: peer judgmentが既存 organizational rule (memory / CLAUDE.md / past judgment timeline) と整合するか **明示的に検証** してから endorse
2. **Reverse判定理由の事前検討**: short-term endorse直前に「**逆方向の judgment が来たら同様に endorseするか**」 を self-check (両方向endorse riskの早期検出)
3. **Conflict surface → escalate**: peer judgmentが過去 ruleと矛盾する場合、即 endorseせず conflict明示 + kimny escalation判断 (passive 「looks good」 endorse禁止)

### Anti-patterns (禁止)

- ❌ peer 「Aで判断」 → conductor 「Excellent」 → peer reverse 「Bで判断」 → conductor 「Excellent」 (両方向endorse、consistency check skip)
- ❌ 「peer self-judgment尊重」 を理由に、organizational rule consistency check回避
- ❌ kimny指示なしで「looks reasonable」 endorse → 後で kimny override → conductor自peer判断ブレ反省 (時系列で repeat)
- ❌ 「fast endorse優先」 で深層 reasoning skip = throughput高だが judgment qualityは低下

### Required behavior

conductor が peer judgment を endorseする前に:

```
1. organizational rule list (memory / CLAUDE.md / past judgments) を mental scan
2. peer judgmentが各rule と整合するか check (matrix思考、consistency map)
3. conflict検出 → 即 endorseしない、conflict明示 + 解決path提案
4. 整合確認 → endorse + reasoning明示 (「<rule X> + <rule Y>と整合」 で理由化)
5. 短時間でreverse判断発生 → 自peer judgment品質post-mortem (memory反映)
```

### Why (5/9 evidence)

```
15:08 conductor (e) override → (i)(j)(k)推奨
15:18 occur peer (k)-only skip → conductor「excellent self-discipline」endorse (skip方向)
15:30 occur peer reverse → (i)+(j)完納
15:32 conductor「(i)+(j) 完納 = excellent learning loop」 endorse (反対方向)
15:38 conductor自身の judgment ブレ反省 (15:08 vs 15:18矛盾明示)
```

両方向で「excellent」 endorseしたことで、long-term rule consistency が一時的に失われた。peerは conductor評価を信頼するが、両方向endorseは「**何が正しい判断か**」 の signalを失わせる。

整合 evidence:
- `feedback_self_correction_value.md` (occur peer): self-correction = growth evidence、reverse OK + memory化 + rule明文化
- `feedback_reference_vs_docs_complement.md` (occur peer): reference ≠ docs structural complement原則 (reverse判断のevidence-driven確立)

### conductor自peer responsibility

本ruleは organizational hierarchy上 **conductor自peerが第一義 owner**。peer-side block (09-13) と相補的:
- peer側 = self-correction時の memory化 / rule明文化責任
- conductor側 = peer judgmentに対する consistency check + active reasoning責任

両方向 (peer-up + conductor-down) からのfeedback loopで organizational rule quality向上。
