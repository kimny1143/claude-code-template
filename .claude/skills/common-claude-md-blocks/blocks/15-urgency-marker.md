## URGENCY marker — peer 自己申告 6 行 format

peer → conductor の `send_message` (claude-peers MCP) の message 先頭に固定 format で記入する。 conductor の認知負荷削減 (proposal v3 (c) hybrid path、 2026-05-18 kimny GO) における判断契約の中核 (Reference: `proposal-conductor-cognitive-load-v3.md` §4.4)。

### Required format

```
URGENCY: high|mid|low
NEEDS_ATTENTION: yes|no
ACTION_OWNER: peer|conductor|kimny
REASON: <one line>
DEADLINE: <ISO8601|null>
EVIDENCE: <PR# | file | commit>
```

### urgency 基準

| 区分 | 例 |
|------|---|
| **high** | security/secret、 外部リソース新規作成、 公開範囲変更、 課金 / 契約、 production outage、 data loss、 kimny Tier 3、 不可逆判断、 当日 hard deadline |
| **mid** | conductor 判断必要、 scope drift、 cross-peer conflict、 skill stale、 PR review 方針、 kimny 判断候補だが即時ではない |
| **low** | progress、 done、 routine PR、 FYI、 dormant update |

### 運用 rules

- **迷ったら `mid`** (fallback)。 後から audit (`reports/daily/YYYY-MM-DD.md` audit section per proposal v3 §8.1) で `false_low` / `false_high` 検知。
- **`high` は REASON + EVIDENCE 必須**。 EVIDENCE 不在の high は audit で `evidence_missing` 分類。
- **議論レーン** (kimny ↔ conductor 対話中) では low / mid 送信禁止。 conductor `set_summary` の「kimny 議論中、 URGENCY: high 以外 hold」 を peer 側 read で判定 (Phase 1 protocol 依存、 Phase 2 wrapper / Phase 3 broker priority queue で physical enforcement)。

### 認知負荷削減効果

- conductor #2 (深さ): 自己申告 urgency で first-pass scan 加速、 「念のため確認」 ping 削減
- conductor #4 (stale governance): post-hoc audit で `false_low` / `false_high` 統計化 → memory governance health metric
- kimny: 議論中割り込み消滅 + 必要時 gw-dash PWA pull で確認

### post-hoc audit category (`reports/daily/YYYY-MM-DD.md`)

- `false_low`: low marked だが high 案件 (= 1 件で proposal v3 §6.3 Phase 3 trigger)
- `false_high`: high marked だが low / mid 案件
- `missing_marker`: URGENCY marker 不在 message
- `stale`: `expected_next_check_at` 超過 (status.md側 field、 block 17 参照)
- `evidence_missing`: EVIDENCE field 不在 high message
