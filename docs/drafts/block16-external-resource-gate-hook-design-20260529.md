# block16 外部リソース gate hook 化 — PR-B 設計draft (2026-05-29)

**位置付け**: 共通ブロック圧縮 PR-A (#90) の後続。独立 Tier 3 (全課波及 hook + セキュリティ感受性)。PR-A merge 後に /plan → conductor/kimny 承認 → 実装。

## 目的

block16 (外部リソース gate) の「毎回必ず守る」ルールを `.claude/hooks/validate-dangerous-ops-v2.sh` (PreToolUse / Bash) に機械強制として実装し、CLAUDE.md 側は slim pointer (~5行) に縮約する。conductor 構造ルール「必ず毎回の検査は hook に」準拠。

## 既存 hook の構造 (find 確認済)

- `validate-dangerous-ops-v2.sh` 214行。stdin JSON → `tool_name`/`tool_input` parse。exit 2 = block / exit 0 = allow。`block()` / `warn()` / `log_block()` helper 完備 (tool-audit.jsonl 記録)。
- Bash section に既存検知: force push to main (済) / rm -rf 危険系 / DROP DATABASE / 機密ファイル外部送信。
- text引数コマンド (`git commit`/`gh pr create`/`gh issue create`) は誤検知回避で先頭 skip。

## ⚠️ 最重要: block09 ↔ block16 の境界 conflict (実装前に要解決)

- **block09** (peer self-judgment境界): 「private GitHub repo 作成 (`gh repo create --private`) = peer自走OK (kimny介在不要)」
- **block16** (外部リソース gate): 「外部リソース新規作成: GitHub repo ... = 常に URGENCY: high + pre-approval」

→ **private repo 作成について両 block が矛盾**。hook が `gh repo create --private` を block すると block09 の「kimny手動作業ゼロ」flow を破壊する。

**解決案 (conductor/kimny 判断要)**:
- (A) block16 を「**public** repo 作成 / visibility public 化 / 既存 repo の公開操作」に限定し、private repo 作成は block09 通り自走OK (hook 非対象)。← 推奨。reversible (private repo は削除容易) + 既存運用維持
- (B) 全 repo 作成を gate (block09 を tighten)。← kimny手動ゼロ原則と逆行、非推奨
- 圧縮 PR-A は両 block の現行文言を faithful に保持 (conflict は PR-A 起因でなく既存)。hook 化が顕在化させた = ここで解決すべき

## hook 検知パターン案 (解決案 A 前提)

Bash section に追加 (block = exit 2):

| 操作 | パターン (grep -E) | 挙動 |
|------|-------------------|------|
| repo public 化 | `gh\s+repo\s+(create.*--public|edit.*--visibility\s+public)` | **block** |
| repo archive | `gh\s+repo\s+archive` | **block** |
| repo delete | `gh\s+repo\s+delete` | **block** |
| history rewrite | `git\s+(rebase\s+-i|filter-branch|filter-repo)` / `git\s+push\s+.*--mirror` | **block** |
| (force push main) | 既存実装済 | block (済) |

- private repo 作成 (`gh repo create` + `--private` or visibility 指定なし default private) = **非対象** (block09 自走OK)
- text引数 skip と同様、`gh pr create` 等の本文に文字列が来ても誤検知しないよう既存 skip パターンを踏襲
- block メッセージ: `外部リソース gate (CLAUDE.md 16): URGENCY: high + kimny/conductor pre-approval 必須。承認後に再実行。`

## SAaS account / domain / 課金 / API key の扱い

- これらは CLI コマンド形が多様 (`gcloud`/`aws`/`vercel`/`stripe` 等) で網羅的 grep は誤検知 risk 大。
- hook では **GitHub 操作 (パターンが安定) のみ機械強制**。他は CLAUDE.md slim pointer のテキスト contract + `resource-audit` cron (後追い検出) の 2 layer 継続。
- = hook は「安定して検知できる高頻度 op」に絞る。over-reach で誤 block すると peer 作業を止める害が大きい。

## 安全制約 (CCO 原則)

- shared hook の安全制約を**弱めない** (追加のみ、既存 block 条件は不変)
- stdin JSON / exit code / 絶対 path / 入力 sanitize を Claude 公式 hook 仕様で再確認
- fail-safe: jq 不在時 exit 0 (既存挙動踏襲)
- 全課波及 hook = dry-run 相当の手動テスト (各検知パターンに対し block/allow を擬似 stdin で確認) を test plan に含める

## CLAUDE.md slim pointer (PR-B 同時、hook が live になってから)

```
## 外部リソース gate
外部リソース新規作成 / 公開範囲変更 / 課金・契約 / 不可逆操作は常に URGENCY: high + kimny/conductor pre-approval。
- GitHub の public 化 / archive / delete / history rewrite / force push(main) は hook が機械 block (validate-dangerous-ops-v2.sh)
- private repo 作成は peer 自走OK (self-judgment境界 参照)
- 起案後 audit = resource-audit skill cron
```

## sequence

1. PR-A (#90) merge
2. block09/16 conflict の解決を conductor/kimny に判断要請 (解決案 A 推奨)
3. /plan で hook 仕様確定 → 実装 (validate-dangerous-ops-v2.sh 追記 + CLAUDE.md slim pointer + block16 source 再圧縮)
4. 手動テスト (擬似 stdin で block/allow 検証) → PR-B 起案 (Tier 3) → conductor review → kimny approval → merge → distribute fanout
