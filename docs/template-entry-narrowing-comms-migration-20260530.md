# Migration note — 入口絞り (URGENCY:high のみ send_message) 全ピア展開

- 日付: 2026-05-30
- 起案: template課 (CCO)
- 承認 gate: conductor (lv3h0a6c) Tier 3 review → 承認後 SHARED 配布
- 状態: **draft / 承認前 (distribute 未実行)**

## 1. 背景

2026-05-30 の conductor 捏造連発 (kimny 試聴#4 回答を読まず戦略捏造、1日4回) を受け、conductor 側で **FIFO 受信バッファ化フロー** を確立 (`_conductor/.claude/rules/conductor-fifo-flow.md`、main merged)。その peer 側対応として kimny が決定した運用ルール「入口絞り」を全ピアの共通 CLAUDE.md に展開する (handoff #44 残タスク)。

中核ルール (FIFO flow doc「入口の絞り」節より逐語):
- peer は **`URGENCY: high` 以外 send_message しない**。low / mid は自 `status.md` に記入するだけ (cowork が `peer-raw-status.md` に集約)。
- conductor は raw-status を checkin/checkout/patrol/自ターン頭で読んで FIFO 処理。
- proposal v3 communication lanes (reporting.md) の厳格版。

## 2. find 確認結果 (架空起案回避)

既存資産を先に検出し、新規 block 追加でなく既存 block の整合修正に落とした:

| 既存資産 | 役割 | 本変更との関係 |
|---|---|---|
| `blocks/15-urgency-marker.md` | peer→conductor send_message の URGENCY format + high/mid/low 基準 | **核**: send_message gate を high のみに絞る |
| `blocks/17-status-md-self-drive.md` | status.md 自走 + cowork→`peer-raw-status.md` 集約 (既存インフラ) | **補完**: low/mid は status.md のみと明記 |
| `blocks/18-judgment-request-contract.md` | mid/high の judgment request form | **整合 ripple**: mid 判断要請は status.md へ、high のみ send_message |
| `scripts/distribute-claude-md-blocks.sh` | blocks/*.md を 14 課 CLAUDE.md の marker 間へ配布 | 配布機構 (既存、marker-skip logic 有) |
| `docs/templates/peer-status-md.template.md` | status.md 13 field (urgency/action_owner/lane 等) | mid 判断要請の置き場 = `next_action`/`Notes` (専用 field なし) |

**設計判断**: 集約インフラ (cowork cron → raw-status) は block 17 に既存。本ルールは新インフラでなく既存 send_message 契約の tightening ゆえ、**新 block 20 を足さず blocks 15/17/18 を整合修正** (2026-05-29 共通block圧縮の slim 方針を維持、新 marker 挿入 PR も不要)。

## 3. 変更内容 (canonical source = blocks/)

新 block 追加なし。3 block を最小整合修正:

- **block 15**: 冒頭に「入口絞り」必読注記 (high のみ send / low・mid は status.md)。運用 rules に「迷ったら mid → send せず status.md」「議論レーン中は high も抑制」「mid を high に誤昇格しない」を追記。6 行 format は high send 用と明記。
- **block 17**: update timing に「low/mid は status.md のみ (send しない)」を追加、`urgency` field 注記を「high のみ send 並行、low/mid は記入のみ」に更新。
- **block 18**: 「チャネル」節を追加 (high=send_message に form 添付 / mid=status.md `next_action`/`Notes` に form 記入、form 構造は同一)。example を mid→high (有効な send 例) に修正。

distribute は marker 間置換ゆえ、上記 3 block の編集はそのまま各課へ反映される (新 marker 不要)。

## 4. 展開先リスト + 実 marker 被覆 (dry-run 実測 2026-05-30)

`distribute-claude-md-blocks.sh` TARGET_PEERS は 14 だが、**blocks 15/17/18 の marker を実際に持つのは 8 課のみ**。dry-run + marker grep 実測:

| 区分 | 課 | distribute 到達 |
|---|---|---|
| **marker 有 (15/17/18)** | freee / cowork / mued_v2 / mued_v2/apps / write / LP / reserch / data (8) | ✅ distribute で配布される |
| **marker 無 (全 marker 0)** | **dsp / occur / SNS(threads-api) / blender (4)** | ❌ distribute は no-op = **未到達** |
| author-native | conductor (15/17/18 marker 無、FIFO doc 起案元) / template (slim・CCO は common block 非ロード) | 起案元ゆえ既に遵守 |

### 4.1 ⚠️ 被覆ギャップ (conductor 判断要) — 全ピア展開の前提条件

**(A) 未到達 4 課 (dsp/occur/SNS/blender) の周知経路**: これらは common-block marker 未挿入 (Phase 2 0.3 marker 挿入 PR 未完分)。distribute では届かない。本ルールは**行動規約**ゆえ CLAUDE.md block なしでも遵守可能。推奨 = **conductor が 4 課へ dispatch で周知** (即時遵守) + marker 挿入 PR は各課 own work として後続 (block 化は遅延 OK)。CCO は marker 挿入を 4 課 workspace に直接行わない (他 peer workspace 不可侵)。

**(B) 8 課の 18-block drift**: marker 有 8 課は dry-run で「18 blocks WOULD UPDATE」= 圧縮後 canonical を未同期 (post-compression sync 未適用)。distribute を素で回すと **entry-narrowing (3 block) + 保留中の圧縮同期 (残 15 block) を同時適用**してしまう。conductor 判断 = (a) 全 resync を許容 (canonical = 正・どのみち同期すべき) / (b) entry-narrowing のみ surgical 適用 (script は per-peer 全 marker 置換ゆえ surgical 不可 → 別途手段要)。CCO 推奨 = **(a) 全 resync 許容** (圧縮 canonical は merged 正本、drift 解消も兼ねる)。ただし dry-run 差分を 8 課分 conductor が目視確認後に。

※ 実展開前に再 dry-run で marker 有無と差分を全課確認 (3 課以上に意図しない差分 → `/plan`)。

## 5. 5-step 周知計画 (CLAUDE.md discipline)

1. **draft** (本 PR): blocks 15/17/18 整合修正 + 本 migration note。← 現在地
2. **conductor Tier 3 review**: 全ピア波及ガードレール変更ゆえ conductor(lv3h0a6c) 承認必須。承認まで distribute 実行しない。
3. **dry-run**: `./scripts/distribute-claude-md-blocks.sh --dry-run` で 14 課差分確認 (3 課以上に意図しない差分 → `/plan`)。
4. **配布 (marker 有 8 課)**: 承認 + dry-run clean 後に CCO が distribute 実行 (§4.1(B) の resync 方針を conductor が確定後)。
5. **未到達 4 課 + 全ピア通知**: dsp/occur/SNS/blender は §4.1(A) のとおり conductor が dispatch で行動規約として周知 (marker 化は後続)。**通知自体も入口絞り準拠** — CCO→conductor は status.md 集約 (high でない)、各 peer への周知は conductor が raw-status / patrol / dispatch 経由で行う。

## 6. 検証 (配布前必須)

- `git diff --check`
- blocks 15/17/18 のみ変更、新 block / 新 marker なしを確認
- `./scripts/distribute-claude-md-blocks.sh --dry-run` clean (意図した 3 block のみ各課で差分)
- `.claude/settings.local.json` ignore 維持 / 他 peer workspace 未変更

## 7. rollback

blocks 15/17/18 を本 PR 前の版に revert → 再 distribute で各課を旧版へ戻す (marker 置換ゆえ可逆)。配布前なら PR close のみ。

## 8. Tier 3 理由

全ピア共通 CLAUDE.md ガードレール (peer↔conductor 通信契約) の変更 = 全課波及。template課 CLAUDE.md「全peerガードレール追加」「shared canonical 変更」に該当し conductor 承認 gate を通す。
