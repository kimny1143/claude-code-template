# audit-settings-allow.sh — peer settings drift detection (Gap 3、 design doc 段階)

- 状態: **design doc 昇格 2026-05-27** (Tier 1 self-review、 full impl 別 PR)
- conductor 5/27 GO: design doc 昇格のみ、 full impl は kimny pattern baseline 承認後 別 PR (Tier 3 候補)
- 次 step: 「peer 固有 pattern baseline 確定」 QA draft 起案 → conductor relay → kimny PWA QA queue (5/28-29 visible 化 target) → judgment 受領 → CCO full impl 着手 (5/30-6/2)
- 起源: 2026-05-26 trilateral 議論 CCO input Gap 3

## 1. 問題定義

`distribute-settings-allow.sh` (template → peer push) は既存だが、 peer 側で permissions が個別追加された場合の detection なし:
- peer ごとに permission 追加 (例 cowork が `mcp__supabase__execute_sql` 追加) しても template 未反映
- template ↔ peer の整合性 silent 劣化
- 同 permission を別 peer が独自追加で重複 (audit なしには気付けない)

**対象範囲明示** (CLAUDE.md `共有物管理` 原則 per):
- ✅ audit 対象: `permissions.allow` 共通部分
- ❌ audit 対象外: peer 固有の `permissions.deny`, `mcpServers`, `WebFetch(domain:*peer-specific*)`

## 2. 設計概要

### 段 1: `scripts/audit-settings-allow.sh` (新規、 read-only audit)

```bash
#!/bin/bash
# audit-settings-allow.sh
# 全 peer の settings.local.json permissions.allow を template base と diff
#
# Usage:
#   ./scripts/audit-settings-allow.sh                # text mode 全 peer
#   ./scripts/audit-settings-allow.sh --json         # 機械可読
#   ./scripts/audit-settings-allow.sh --peer cowork  # 単 peer
#
# 出力 (text mode):
#   [EXTRA]   cowork課: permissions.allow に template 未登録 3 件
#             - "Bash(supabase *)"
#             - "WebFetch(domain:linear.app)"
#             - "mcp__supabase__execute_sql"
#   [MISSING] reserch課: template にあって peer にない 1 件
#             - "Bash(poetry *)"
#   [OK]      occur課: template と整合
#
# exit code: 0 = clean, 1 = drift (extra or missing exists)
#
# 設計上 ignore: deny / mcpServers / hooks / peer 固有 WebFetch domain
```

### 段 2: jq による JSON diff 実装核心

```bash
# template_allow と peer_allow を取得
template_allow=$(jq -r '.permissions.allow[]?' docs/templates/settings-local-base.json | sort)
peer_allow=$(jq -r '.permissions.allow[]?' "$peer_settings" | sort)

# diff
extra=$(comm -23 <(echo "$peer_allow") <(echo "$template_allow"))
missing=$(comm -13 <(echo "$peer_allow") <(echo "$template_allow"))

# peer-specific filter (Open Q3 参照)
filtered_extra=$(echo "$extra" | grep -vE "$PEER_SPECIFIC_PATTERN")
```

### 段 3: peer 固有 pattern (ignore 用 regex)

```bash
# PEER_SPECIFIC_PATTERN: peer 固有として ignore する permission の regex
# 例:
#   WebFetch(domain:.+-specific-domain) — peer 専用ドメイン
#   mcp__<peer-name>__<tool>            — peer 専用 MCP
#   Bash(<peer-tool> *)                 — peer 専用 CLI
#
# 初期 baseline:
PEER_SPECIFIC_PATTERN='^(WebFetch\(domain:linear\.app|WebFetch\(domain:notion\.so|mcp__(supabase|firebase|growthbook|prisma)__)'
# ↑ baseline は kimny + conductor 判断、 本 draft では placeholder
```

## 3. 出力 mode

- **text (default)**: human readable、 EXTRA / MISSING / OK
- **`--json`**: 機械可読 (cowork RemoteTrigger 集約 → conductor dashboard)
- **`--peer <name>`**: 単 peer audit
- **`--verbose`**: OK item も全表示

## 4. Gap 1 / Gap 2 との関係

| 項目 | Gap 1 (peer-drift) | Gap 2 (skills-lock) | Gap 3 (settings-allow) |
|------|--------------------|---------------------|-----------------------|
| 比較対象 | template skill/hook ↔ peer | template skill ↔ lock JSON | template settings ↔ peer settings |
| diff 方法 | sha256 | sha256 + JSON lookup | JSON set diff (jq + comm) |
| update 機能 | なし | あり (`--update`) | なし (audit only) |
| ignore filter | なし | なし | あり (peer 固有 pattern) |

**共通化候補**:
- `scripts/lib/peer-targets.sh` (peer 一覧、 Gap 1 + Gap 3 で再利用) → 本 PR で確立
- `scripts/lib/escalation.sh` (drift 検出時 conductor escalation message format、 Gap 1/2/3/4 共通) → Gap 4 (hook bypass) 段階で設計

## 5. minimal draft 範囲限定

本 draft = **設計 doc only**:
- script 本体 full LOC (約 150 LOC 想定、 Gap 1/2 より小さめ = JSON diff の jq 依存で簡潔)
- peer 固有 pattern baseline 確定
- escalation path 設計

後続 PR で実装、 Gap 1 + Gap 2 PR 承認後 sequencing。

## 6. Open Q

1. **EXTRA detection 時の action**:
   - (a) ignore (peer 自由裁量、 audit 出力のみ)
   - (b) template 取り込み propose (kimny / conductor 判断後 distribute-settings-allow.sh で broadcast)
   - (c) peer に削除 dispatch (rare、 セキュリティ問題 only)
   推奨: default (a)、 高頻度発生 permission は (b) で正本 promote

2. **MISSING detection 時の action**:
   - (a) ignore (peer 意図的最小化、 例 video peer に Bash(turbo *) 不要)
   - (b) `distribute-settings-allow.sh` 再実行で sync
   推奨: peer 自走で `distribute-settings-allow.sh --peer <name>` 再実行可、 強制 sync しない

3. **peer 固有 pattern の baseline 確定**:
   - 現状 各 peer の peer 固有 permission を grep + 集約必要
   - kimny / conductor 判断: 一括 grep audit → pattern 決定
   推奨: PR 起票前 audit 1 回実行 + pattern doc 起案 → kimny 承認

4. **hooks section の audit 対象化**:
   - 現 settings-local-base.json は permissions のみ、 hooks section なし
   - peer 側で hooks 設定 (PreToolUse / Stop 等) が drift しても detect 不能
   - 段 4 として hooks audit 追加すべきか (Gap 4 hook bypass detection と重複)
   推奨: Gap 4 (hook bypass detection) が PreToolUse 検知 cover、 settings hooks section は別 audit (本 script 対象外 keep)

5. **MCP server section の audit**:
   - mcpServers は完全 peer 固有 (各 peer の MCP 設定は独立)
   - 全 peer 共通の MCP (claude-peers / claude-in-chrome 等) 整合 check 必要か
   推奨: 共通 MCP の自動 audit は別 PR、 本 script は permissions.allow only に集中

## 7. timeline

- 5/26 本 minimal draft 完納
- 5/27-6/3: peer 固有 pattern baseline 確定 (kimny + conductor 判断)
- 6/3-6/10: full script 実装 + PR 起票 (Tier 2、 LP/native peer review)
- 6/10-6/20: 月次 cron 化 (cowork RemoteTrigger)、 Gap 1/2/3 統合 audit report

## 8. Tier 判定

- audit script 単独 = **Tier 2** (新規 read-only script、 全課波及なし)
- peer 固有 pattern doc = **Tier 3** (全課判断 必要、 kimny 直接承認)

分割 PR 推奨:
- PR-A: peer 固有 pattern baseline 確定 doc (Tier 3、 kimny 承認)
- PR-B: audit script 本体 (Tier 2、 LP/native peer review)
