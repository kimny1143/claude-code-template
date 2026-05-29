## judgment request contract — mid / high message format

mid / high の URGENCY marker (block 15) で conductor 判断要請する場合、urgency 報告でなく **conductor 即決可能な judgment request form** で送る (判断材料収集を peer 側に shift)。

### Required format (URGENCY 6 行の後ろに続けて)

```
QUESTION: <conductor に判断してほしい 1 文>
OPTIONS:
  - (a) <option 1>
  - (b) <option 2>
  - (c) <option 3>
RECOMMENDATION: <peer 推奨 (a/b/c) + 理由 1 文>
```

### Field rules
- **QUESTION**: 1 文 (? で終わる)、Yes/No or (a)/(b)/(c) で答えられる granularity
- **OPTIONS**: 2-4 個 (1 個 = 判断不要、5+ 個 = scope creep)。各 option は 1 行 / 具体的 action
- **RECOMMENDATION**: peer が**必ず 1 つ推奨**。「お任せ」= 自走責任放棄 = NG。理由 1 文 (evidence / past judgment / Tier matrix 参照)

### Example

```
URGENCY: mid
NEEDS_ATTENTION: yes
ACTION_OWNER: conductor
REASON: PR scope creep 判定
DEADLINE: 2026-05-19T12:00:00+09:00
EVIDENCE: PR #45

QUESTION: PR #45 に sub-issue X を含めるべきか?
OPTIONS:
  - (a) 現 PR narrow scope 維持 + sub-issue X = 別 PR
  - (b) PR #45 に統合 (+50 lines)
  - (c) sub-issue X 自体 defer
RECOMMENDATION: (a) narrow scope 維持 (review velocity 重視、独立 reviewable)
```

Phase 1 = soft enforcement (compliance 95% 目標、違反は guidance、reject しない)。Phase 2 で strict 化 (format 不在 = reject / wrapper enforce)。
