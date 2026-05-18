## status.md 自走 update protocol

各 peer は自 workspace の `status.md` (or `docs/status.md` ─ peer 内で path 統一) を直接記入 + 自 git repo に commit + push する。 cowork peer の cron aggregation (5-15 分間隔) が各 peer git repo から status.md を fetch + `_conductor/docs/inbox/peer-raw-status.md` に集約する (Reference: `proposal-conductor-cognitive-load-v3.md` §4.3、 (c) hybrid path)。

### file path

- 推奨: workspace root の `status.md`
- 許容: `docs/status.md` (peer 判断、 但し peer 内で path 統一)
- format: `docs/templates/peer-status-md.template.md` (template課配布) per

### update timing (peer 必須)

- **task accept**: conductor / kimny / 他 peer から dispatch / review request 受領時
- **blocked**: 外部依存 / kimny judgment 待ち / cross-peer dependency で work 停滞時
- **PR submit**: PR open / draft → ready / re-push 等の status change時
- **done**: task complete / dispatch acceptance complete時
- **high urgency 発生時**: 即時 status.md update + URGENCY: high `send_message` 並行
- **1 日 1 回 minimum heartbeat**: 朝の自走開始時 + EOD 区切り時 (active peer は最低 1 update/日)

### 並行 update (claude-peers MCP)

- `set_summary` (1-2 文の current_task + next_action) も同時更新
- status.md = 機械可読 raw source、 set_summary = peer list 表示用 human readable summary
- 両者整合 (= 同じ task / next_action を describe) 必須

### push policy

- **自 peer repo のみ** に push (conductor repo には push しない、 merge conflict 回避)
- branch protection 適用は各 peer repo の policy 次第 (= 一部 peer は main 直接 push 可、 一部 peer は PR必須)
- main 直接 push 禁止 peer は feature branch + PR (Tier 1 self-merge OK、 = docs only、 audio character touch なし)

### cowork cron aggregation (peer 側で操作不要)

- cowork peer が 5-15 分間隔で各 peer git repo を `git fetch` + `status.md` 内容取得
- `_conductor/docs/inbox/peer-raw-status.md` に各 peer section 集約 + commit + push (single writer = cowork、 merge conflict なし)
- 各 peer は **「自 repo に push さえすれば cowork が自動 aggregation」** と認識して OK

### stale 判定 (cowork cron 内)

- active 6h 超 / blocked-waiting 2h 超 / dormant 72h 超 (ただし `expected_next_check_at` 優先)
- stale 検出 → conductor `set_summary` に alert + `reports/daily/YYYY-MM-DD.md` audit section 反映
- stale violation peer に conductor から ping (proposal v3 §12 R7 mitigation per)

### frontmatter YAML 13 fields

`docs/templates/peer-status-md.template.md` per:
- peer / department / activity / status / current_task / next_action
- blocked_by / urgency / action_owner / deadline / expected_next_check_at
- last_update / evidence / confidence / lane

### URGENCY marker (block 15) 統合

`urgency` field は status.md frontmatter + send_message URGENCY marker (block 15) で **同一 vocabulary** (high / mid / low) を使う。 status.md の urgency が high の場合、 並行で URGENCY marker 付き send_message を conductor に送る。

### 外部リソース gate (block 16) 統合

status.md `current_task` / `next_action` に 外部リソース新規作成系 (block 16 対象) が含まれる場合、 status.md update と pre-approval URGENCY: high send_message を **必ず並行**。
