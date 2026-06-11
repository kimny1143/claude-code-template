## status.md 自走 update protocol

各 peer は自 workspace の `status.md` (root 推奨、`docs/status.md` 許容・peer 内で path 統一) を直接記入 + 自 git repo に commit & push。cowork peer の cron (5-15 分間隔) が各 peer repo から fetch し `_conductor/docs/inbox/peer-raw-status.md` に集約する (peer 側操作不要)。

- format: `docs/templates/peer-status-md.template.md` (frontmatter YAML 13 fields)

### update timing (必須)
- **task accept** (dispatch / review request 受領) / **blocked** (外部依存・kimny 待ち・cross-peer 停滞) / **PR submit** / **done**
- **low / mid の連絡は status.md のみ** (send_message しない = 入口絞り block 15)。progress / done / routine PR / FYI / conductor 判断候補だが即時でない 等はここに集約され、cowork が `peer-raw-status.md` へ、conductor が FIFO で拾う
- **high urgency 発生時のみ**: 即 status.md update + URGENCY: high send_message 並行
- **1 日 1 回 minimum heartbeat**: 朝の自走開始時 + EOD 区切り

### DoD: status.md 更新 = タスク完了の定義 (必須)

- **task done / milestone 到達 / blocked / PR submit / high urgency の各区切りで、status.md を更新してから「完了」とする。status.md 未更新の完了報告は未完扱い**。
- **live session で conductor / kimny と直接やり取りした作業も同じ**。区切りごとに status.md へ反映し、conductor が後から状態を再構築する状況を作らない (= cowork aggregation を常に最新に保つ。conductor の手作業 reconstruct を増やさない)。
- 狙い: conductor は checkout 時に `peer-raw-status.md` aggregation を読むだけで全課 EOD が揃う (手作業 reconstruct 不要)。
- 起案根拠: 2026-06-11 — live session 中に複数 peer (dsp/SNS/insight) が status.md 未更新のまま作業 → conductor が状態を手作業再構築する事案が発生 (kimny 指摘)。

### 並行 update
- `set_summary` (current_task + next_action) も同時更新。status.md = 機械可読 raw、set_summary = peer list 表示用。両者整合必須

### push policy
- **自 peer repo のみ** に push (conductor repo には push しない)
- main 直接 push 禁止 peer は feature branch + PR (docs only = Tier 1 self-merge OK)

### 統合
- `urgency` field は URGENCY marker (block 15) と同一 vocabulary (high / mid / low)。**high 時のみ send_message 並行、low / mid は status.md 記入のみ** (入口絞り)
- `current_task` / `next_action` に外部リソース新規作成 (block 16 対象) を含む場合、pre-approval URGENCY: high send_message を必ず並行
- stale 判定 (cowork cron): active 6h / blocked-waiting 2h / dormant 72h 超 (`expected_next_check_at` 優先) → conductor alert + ping
