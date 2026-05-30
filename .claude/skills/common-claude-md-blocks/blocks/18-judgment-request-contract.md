## judgment request contract — judgment request form

conductor 判断要請は urgency 報告でなく **conductor 即決可能な judgment request form** で渡す (判断材料収集を peer 側に shift)。

**チャネル (入口絞り block 15 準拠)**: **high** の判断要請のみ send_message に下記 form を添付。**mid** の判断要請は send_message せず status.md の `next_action` / `## Notes` に form を記入し、conductor が `peer-raw-status.md` を FIFO で拾って即決する。いずれも form 構造は同一。

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

high の例 (send_message)。mid なら同 form を status.md `next_action` / `Notes` に記入:

```
URGENCY: high
NEEDS_ATTENTION: yes
ACTION_OWNER: conductor
REASON: 外部リソース新規作成の可否判定 (不可逆)
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
