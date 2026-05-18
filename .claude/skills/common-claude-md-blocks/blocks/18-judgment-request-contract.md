## judgment request contract — mid / high message format

mid / high の URGENCY marker (block 15) で conductor 判断要請する場合、 単なる urgency 報告ではなく **conductor 即決可能な judgment request form** で送る (Reference: `proposal-conductor-cognitive-load-v3.md` §4.6)。 conductor 認知負荷削減の中核 = 判断材料収集を peer 側に shift。

### Phase 1: soft enforcement (本 block 適用範囲)

- compliance 目標 = 95% (post-hoc audit per、 違反は warning + 改善要請)
- 違反時 (= QUESTION / OPTIONS / RECOMMENDATION 不在の mid/high message) は conductor から peer に「次回から本 format で」 と guidance、 reject はしない
- Phase 2 で strict 化 (= format 不在 = 受信 reject、 cowork wrapper / broker priority queue で physical enforce、 proposal v3 §6.2 / §8.4 per)

### Required format (mid / high message body)

URGENCY marker 6 行 (block 15) の **後ろに続けて**:

```
QUESTION: <conductor に判断してほしい 1 文>
OPTIONS:
  - (a) <option 1>
  - (b) <option 2>
  - (c) <option 3>
RECOMMENDATION: <peer 推奨 (a/b/c) + 理由 1 文>
```

### Field rules

- **QUESTION**: 1 文 (Question mark で終わる)、 conductor が「Yes/No」 or 「(a)/(b)/(c) 選択」 で答えられる granularity
- **OPTIONS**: 2-4 個 (1 個 = 判断不要、 5+ 個 = scope creep)。 各 option は 1 行 / 1 文 / 具体的 action
- **RECOMMENDATION**: peer が **必ず 1 つ推奨**。 「conductor 判断にお任せ」 = peer 自走責任放棄 = NG (= proposal v3 §4.6 「judgment debt の core = 判断材料収集を peer 側に shift」 違反)
- 理由 1 文 = recommendation の根拠 (evidence / past judgment / Tier matrix 等 reference)

### Example

```
URGENCY: mid
NEEDS_ATTENTION: yes
ACTION_OWNER: conductor
REASON: PR scope creep 判定、 narrow scope 維持 vs 統合 efficiency
DEADLINE: 2026-05-19T12:00:00+09:00
EVIDENCE: PR #45

QUESTION: PR #45 に sub-issue X (cross-file refactor) を含めるべきか?
OPTIONS:
  - (a) 現 PR #45 narrow scope 維持 + sub-issue X = 別 PR #46 起案
  - (b) PR #45 に sub-issue X 統合 (+50 lines、 narrow scope expand)
  - (c) sub-issue X 自体 defer (Phase 2 候補化)
RECOMMENDATION: (a) narrow scope 維持 (Tier 2 PR review velocity 重視、 sub-issue X は dependency なしで独立 reviewable)
```

### 認知負荷削減効果

- conductor #1 (広さ): OPTIONS で判断空間を peer 側で narrow 化、 conductor は select のみ
- conductor #2 (深さ): RECOMMENDATION で peer 推奨見えるため、 conductor は agreement check focus
- peer 側 self-judgment 強化 (judgment hesitation reduction): 「迷ったら投げる」 → 「迷っても推奨 1 つ決めてから投げる」 規律

### audit 統合

post-hoc audit (`reports/daily/YYYY-MM-DD.md` audit section per proposal v3 §8.1) で:
- `missing_question`: QUESTION 不在の mid/high message
- `missing_options`: OPTIONS 不在 or 1 個のみの mid/high message
- `missing_recommendation`: RECOMMENDATION 不在 (= judgment debt 放棄)
- Phase 1 = 統計化 + improvement guidance、 Phase 2 = reject / wrapper enforce
