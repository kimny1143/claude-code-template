## URGENCY marker — peer → conductor send_message 先頭 6 行 format

peer → conductor の claude-peers send_message の message 先頭に固定 format で記入 (conductor 認知負荷削減の判断契約中核)。

**入口絞り (2026-05-30 kimny 決定 / 必読)**: peer は **`URGENCY: high` のみ send_message する**。low / mid は send_message せず自 `status.md` に記入する (block 17、cowork が `peer-raw-status.md` に集約 → conductor が checkin/checkout/patrol/自ターン頭で FIFO 読取り処理)。これにより conductor へのプッシュ割り込みを最小化し、件取り違えによる捏造を防ぐ。下記 6 行 format は high send_message 用。urgency vocabulary (high/mid/low) は status.md `urgency` field 含む全分類に適用。proposal v3 communication lanes (reporting.md) の厳格版。

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

- **迷ったら `mid`** (fallback) → 入口絞り下では send_message せず status.md 記入 (high のみ send)
- **`high` は REASON + EVIDENCE 必須** (EVIDENCE 不在の high は audit で `evidence_missing` 分類)
- **議論レーン** (kimny ↔ conductor 対話中) では high も送信抑制。conductor `set_summary` の hold 表示を peer 側 read で判定し、解除まで status.md 集約に寄せる
- **誤判定で mid を high にしない**: high は不可逆/当日 hard deadline/security/secret/外部リソース新規作成/課金・契約/production outage/data loss/kimny Tier 3 に限定 (上表 high 基準)。判断要請は block 18 form を high send_message or status.md に記入
