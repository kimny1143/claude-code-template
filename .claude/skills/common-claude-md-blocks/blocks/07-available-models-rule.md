## 運用ルール: `availableModels` は settings.json に追加しない

2026-04-14 確立、Opus固定移行後も継続の全課共通ルール。

- `~/.claude/settings.json` / `~/.claude/settings.local.json` / 各peer `.claude/settings.local.json` いずれにも `availableModels` を追加しない
- 理由: [anthropics/claude-code#41720](https://github.com/anthropics/claude-code/issues/41720) — `availableModels` をカスタム追加した環境で `/model opus` 等に戻れなくなるバグ。追加しなければ踏まない
- モデル切替は起動時の `--model` フラグで行う (経営部4課は Opus固定)。実行中の手動切替は非推奨
- 将来 `availableModels` が必要になった場合は本ルール改定を policy-gate 経由で
