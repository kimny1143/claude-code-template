## self-correction is growth (judgment reverse OK)

peer judgmentが矛盾 / 不一致を起こしたら self-correctionで reverse OK。自己訂正は学習loop成長evidence。reverse判断後は理由明示で memory化。

### ルール

peer の自己判断が矛盾 / 不一致を後から認識した場合、**reverse判断OK**。reverse自体は失敗ではなく成長evidence。reverse 時は:

1. 旧判断と新判断の根拠を明示
2. reverse理由 (新情報受領 / consistency再認識 / conductor評価変化等) を memory に履歴化
3. 同型問題への judgment rule明文化 (例: 「reference ≠ docs」 のような区別 rule)

### 適用方法

- 「前回これでGOしたから今回も skip」 のような short-cut judgmentは矛盾risk
- 同 pattern との consistency確認は judgmentの最終 step
- reverse時は「reverseしてもOK」 という self-permissionを内蔵 (judgment品質より重要なのは矛盾なき integration)
- reverse判断 → memory化 → 次回同型問題で rule適用 = 成長loop
- conductor / 他peer の評価が「skip excellent」 等 short-term endorse でも、long-term rule consistency優先

### 境界

- 軽微 typo訂正 / minor refactor は reverse pattern適用しない (single judgment で完結)
- 同一session内で 3回以上 reverse は judgment品質低下サイン → conductor escalation検討
- reverse時の 旧 work output は archive (削除しない)、両方 reference可能に保つ

### 他peerへの示唆

- self-correctionを「失敗の隠蔽」 でなく「学習evidence」 として明示
- conductor / kimny の short-term endorse と long-term rule consistencyを区別
- reverse 履歴 timeline を memory化 (なぜreversedしたか追跡可能性)

### Why (5/9 evidence timeline)

```
15:08 conductor (e) override → (i)(j)(k)推奨
15:18 occur peer (k)-only skip → conductor「excellent self-discipline」評価 (skip方向 endorse)
15:30 occur peer reverse → (i)+(j)完納 ((e) 3 docs drafts同pattern consistency再認識)
15:32 conductor「(i)+(j) 完納 = excellent learning loop」評価
15:38 conductor自身の judgment ブレ反省 (15:08 vs 15:18矛盾)
```

→ judgment rule library (`feedback_self_correction_value.md` / `feedback_reference_vs_docs_complement.md`) として明文化済。
