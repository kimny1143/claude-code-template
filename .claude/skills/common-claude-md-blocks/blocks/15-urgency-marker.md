## URGENCY marker — peer → conductor send_message 先頭 6 行 format

peer → conductor の claude-peers send_message の message 先頭に固定 format で記入 (conductor 認知負荷削減の判断契約中核)。

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
| **high** | security/secret、外部リソース新規作成、公開範囲変更、課金/契約、production outage、data loss、kimny Tier 3、不可逆判断、当日 hard deadline |
| **mid** | conductor 判断必要、scope drift、cross-peer conflict、skill stale、PR review 方針、kimny 判断候補だが即時でない |
| **low** | progress、done、routine PR、FYI、dormant update |

### 運用 rules

- **迷ったら `mid`** (fallback)
- **`high` は REASON + EVIDENCE 必須** (EVIDENCE 不在の high は audit で `evidence_missing` 分類)
- **議論レーン** (kimny ↔ conductor 対話中) では low / mid 送信禁止。conductor `set_summary` の hold 表示を peer 側 read で判定
