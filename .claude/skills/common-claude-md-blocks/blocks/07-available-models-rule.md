## 運用ルール: `availableModels` は settings.json に追加しない

2026-04-14 (opusplan運用開始時) に確立された全課共通ルール。Opus固定移行 (2026-04-23〜) 後も継続。

### ルール
`~/.claude/settings.json` / `~/.claude/settings.local.json` / 各peer の `.claude/settings.local.json` いずれにも `availableModels` 項目を追加しない。

### 理由
GitHub issue [anthropics/claude-code#41720](https://github.com/anthropics/claude-code/issues/41720) で、`availableModels` をカスタマイズした環境で `sonnet[1m]` / `opus[1m]` / `haiku` などを経由すると `/model opusplan` (opusplan運用peer) や `/model opus` (Opus固定peer) に戻れなくなるバグが報告されている。発動条件は `availableModels` のカスタム追加のみ。追加しなければこのバグ面を踏まない。

### 運用
- モデル切替は起動時の `--model` フラグで行う (経営部4課は `claudepeers --model opus` Opus固定。他peerは opusplan 等運用ありうる)。実行中の手動モデル切替は Opus固定運用整合のため推奨しない
- 将来 `availableModels` が必要になるユースケースが出た場合は、本ルール改定を伴う承認フロー（policy-gate）を通すこと
- Claude Code update（`claude update`）でバグ修正が取り込まれた後も、代替手段が十分機能しているため、`availableModels` の追加は原則継続して行わない
