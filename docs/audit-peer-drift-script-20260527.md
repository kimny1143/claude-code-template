# audit-peer-drift.sh — peer shared payload drift detection (Gap 1)

- 状態: **shipped 2026-05-27** (Tier 2、 conductor peer review path)
- conductor 5/27 GO: 14 peer 体制 から conductor + template 除外 = 13 peer audit
- 起源: 2026-05-26 trilateral 議論 CCO input Gap 1
- evidence: 2026-05-10 19:34 JST `block-main-push.sh` 第三者編集 incident 手動 detection (memory `project_handoff_20260511.md` #4)

## Ship 時点 dry-run 結果 (2026-05-27)

```
$ ./scripts/audit-peer-drift.sh
summary: OK=36, DRIFT=3, MISS=13
```

- DRIFT 3: SNS課 (hooks/block-main-push.sh + skills/tier-judge)、 LP課 (skills/tier-judge) = peer 側で 改変
- MISS 13: reserch (hooks 1)、 blender / occur / dsp 各 4 = 配布漏れ
- 後続 dispatch 候補 = drift = conductor escalation、 miss = `distribute-skills.sh` TARGETS 拡張 (blender / occur / dsp 追加判断)

## draft → ship 時の主要差分

| item | draft 想定 | ship 実装 |
|------|------------|-----------|
| TARGETS peer 数 | 11 peer (旧 distribute-skills.sh 構成 + occur 先取り、 growth抜け) | **13 peer** (conductor + template 除く全 peer、 conductor 5/27 GO per) |
| emit_entry OK branch | `[[ $VERBOSE == true ]] && echo ...` (`set -e` 下 false 時 関数戻り値 1 で script kill する bug) | `if [[ ... ]]; then echo ...; fi` 形式に修正 |

## 1. 設計目的

`scripts/distribute-*.sh` は template → peer の **push 方向のみ** で、 peer 側で shared payload が改変された場合の自動 detection なし。 本 script は逆方向 (peer → template 整合性 audit) を read-only で提供し、 silent drift を可視化する。

## 2. 監査対象 (現状 baseline)

| 種別 | item | 起源 |
|------|------|------|
| hook | `block-main-push.sh` | `setup.sh` SHARED_HOOKS |
| skill | `peer-id-lookup` | `scripts/distribute-skills.sh` COMMON_SKILLS |
| skill | `tier-judge` | 同上 |
| skill | `plan-mode-policy` | 同上 |

将来拡張 (Gap 検出時の `setup.sh` SHARED_HOOKS 拡張 → 5/6 hook 配布漏れ解消) で対象が増えても、 array 追加のみで対応可能な設計。

## 3. peer target (11 peer、 task #24 整合)

`distribute-skills.sh` TARGETS (10 peer) + `distribute-divisions-extend-20260512.md` 草案 で追加予定の occur (cowork は既存 TARGETS に含まれる)。

| division | .claude path |
|----------|--------------|
| conductor | `/Users/kimny/Dropbox/_DevProjects/_conductor/.claude` |
| write | `/Users/kimny/Dropbox/_DevProjects/_contents-writing/.claude` |
| cowork | `/Users/kimny/Dropbox/_DevProjects/_cowork/.claude` |
| data | `/Users/kimny/Dropbox/_DevProjects/_data-analysis/.claude` |
| LP | `/Users/kimny/Dropbox/_DevProjects/_LandingPage/glasswerks-lp/.claude` |
| reserch | `/Users/kimny/Dropbox/_DevProjects/_Reserch/.claude` |
| freee | `/Users/kimny/Dropbox/_DevProjects/freee-MCP/.claude` |
| mued | `/Users/kimny/Dropbox/_DevProjects/mued/mued_v2/.claude` |
| native | `/Users/kimny/Dropbox/_DevProjects/mued/mued_v2/apps/.claude` |
| SNS | `/Users/kimny/Dropbox/_DevProjects/mued/threads-api/.claude` |
| occur | `/Users/kimny/Dropbox/_DevProjects/mued-occur/.claude` |

note: template (self) は audit 対象外 (正本側)。 task #24 merge 後 occur dir path を verify (`mued-occur` 想定だが kimny / conductor 確認推奨)。

## 4. exit code 仕様

| code | 意味 | next action |
|------|------|-------------|
| 0 | 全 peer drift なし、 全 item 配置済 | 通常 cron 継続 |
| 1 | drift 検出 (sha256 mismatch) | conductor escalation、 該当 peer に dispatch |
| 2 | 配布対象 item 未配置 (MISS) | `distribute-skills.sh` 再実行検討、 peer 起動状態確認 |

drift と miss が同時発生時は exit 1 優先 (drift の方が severity 高)。

## 5. output mode

- **text (default)**: human-readable、 cron log / 手動実行向け
- **`--json`**: 機械可読 (cowork peer の RemoteTrigger 集約 → conductor dashboard 候補)
- **`--peer <name>`**: 単 peer audit、 incident 調査時
- **`--verbose`**: OK item も全表示 (通常は drift / miss のみ表示)

## 6. script 本体 draft

```bash
#!/bin/bash
# audit-peer-drift.sh
# 全 peer の shared payload (hooks / common skills) が template 正本と整合するか audit
# Read-only、 peer file には触らない
#
# Usage:
#   ./scripts/audit-peer-drift.sh                  # text output, 全 peer
#   ./scripts/audit-peer-drift.sh --peer cowork    # 単 peer audit
#   ./scripts/audit-peer-drift.sh --json           # 機械可読 output
#   ./scripts/audit-peer-drift.sh --verbose        # 一致した item も出力
#
# exit code:
#   0 = 全 peer drift なし
#   1 = drift 検出 (sha256 mismatch、 miss と同時発生時も 1 を返す)
#   2 = drift なし、 配布対象 item 未配置のみ

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# template 正本 source
HOOKS_SRC="$REPO_ROOT/.claude/hooks"
SKILLS_SRC="$REPO_ROOT/.claude/skills"

# 監査対象 (setup.sh SHARED_HOOKS + distribute-skills.sh COMMON_SKILLS と整合)
SHARED_HOOKS=(
  "block-main-push.sh"
)
COMMON_SKILLS=(
  "peer-id-lookup"
  "tier-judge"
  "plan-mode-policy"
)

# peer ターゲット: 課名|.claude ベースパス
# distribute-skills.sh TARGETS + task #24 (cowork+occur 追加) と整合
TARGETS="
conductor|/Users/kimny/Dropbox/_DevProjects/_conductor/.claude
write|/Users/kimny/Dropbox/_DevProjects/_contents-writing/.claude
cowork|/Users/kimny/Dropbox/_DevProjects/_cowork/.claude
data|/Users/kimny/Dropbox/_DevProjects/_data-analysis/.claude
LP|/Users/kimny/Dropbox/_DevProjects/_LandingPage/glasswerks-lp/.claude
reserch|/Users/kimny/Dropbox/_DevProjects/_Reserch/.claude
freee|/Users/kimny/Dropbox/_DevProjects/freee-MCP/.claude
mued|/Users/kimny/Dropbox/_DevProjects/mued/mued_v2/.claude
native|/Users/kimny/Dropbox/_DevProjects/mued/mued_v2/apps/.claude
SNS|/Users/kimny/Dropbox/_DevProjects/mued/threads-api/.claude
occur|/Users/kimny/Dropbox/_DevProjects/mued-occur/.claude
"

# parse args
PEER_FILTER=""
JSON_MODE=false
VERBOSE=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --peer)
      PEER_FILTER="${2:-}"
      if [[ -z "$PEER_FILTER" ]]; then
        echo "--peer requires argument" >&2
        exit 2
      fi
      shift 2
      ;;
    --json) JSON_MODE=true; shift ;;
    --verbose) VERBOSE=true; shift ;;
    -h|--help)
      sed -n '2,16p' "$0"
      exit 0
      ;;
    *)
      echo "unknown option: $1" >&2
      exit 2
      ;;
  esac
done

# sha256 helper (macOS shasum / Linux sha256sum 両対応)
sha256_of() {
  local target="$1"
  if [[ -d "$target" ]]; then
    # dir: 中身全 file の sorted hash を集約
    (cd "$target" && find . -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256) \
      | shasum -a 256 \
      | awk '{print $1}'
  elif [[ -f "$target" ]]; then
    shasum -a 256 "$target" | awk '{print $1}'
  else
    echo "MISSING"
  fi
}

DRIFT_COUNT=0
MISS_COUNT=0
OK_COUNT=0
JSON_ENTRIES=()

emit_entry() {
  local division="$1" item="$2" status="$3" src_hash="${4:-}" dst_hash="${5:-}"
  if $JSON_MODE; then
    if [[ -n "$src_hash" && -n "$dst_hash" ]]; then
      JSON_ENTRIES+=("{\"peer\":\"$division\",\"item\":\"$item\",\"status\":\"$status\",\"template_sha256\":\"$src_hash\",\"peer_sha256\":\"$dst_hash\"}")
    else
      JSON_ENTRIES+=("{\"peer\":\"$division\",\"item\":\"$item\",\"status\":\"$status\"}")
    fi
  else
    case "$status" in
      OK)    [[ $VERBOSE == true ]] && echo "  [OK]    ${division}課: $item" ;;
      DRIFT) echo "  [DRIFT] ${division}課: $item (template:${src_hash:0:8} peer:${dst_hash:0:8})" ;;
      MISS)  echo "  [MISS]  ${division}課: $item 未配置" ;;
    esac
  fi
}

audit_item() {
  local division="$1" item_kind="$2" item_name="$3" src="$4" dst="$5"
  local item_label="${item_kind}/${item_name}"

  if [[ ! -e "$dst" ]]; then
    MISS_COUNT=$((MISS_COUNT + 1))
    emit_entry "$division" "$item_label" "MISS"
    return
  fi

  local src_hash dst_hash
  src_hash=$(sha256_of "$src")
  dst_hash=$(sha256_of "$dst")

  if [[ "$src_hash" == "$dst_hash" ]]; then
    OK_COUNT=$((OK_COUNT + 1))
    emit_entry "$division" "$item_label" "OK" "$src_hash" "$dst_hash"
  else
    DRIFT_COUNT=$((DRIFT_COUNT + 1))
    emit_entry "$division" "$item_label" "DRIFT" "$src_hash" "$dst_hash"
  fi
}

audit_peer() {
  local division="$1" peer_base="$2"

  if [[ ! -d "$peer_base" ]]; then
    if ! $JSON_MODE; then
      echo "  [SKIP] ${division}課: .claude dir なし ($peer_base)"
    fi
    return
  fi

  for hook in "${SHARED_HOOKS[@]}"; do
    audit_item "$division" "hooks" "$hook" "$HOOKS_SRC/$hook" "$peer_base/hooks/$hook"
  done

  for skill in "${COMMON_SKILLS[@]}"; do
    audit_item "$division" "skills" "$skill" "$SKILLS_SRC/$skill" "$peer_base/skills/$skill"
  done
}

# 事前確認: template 正本 source 存在
for hook in "${SHARED_HOOKS[@]}"; do
  if [[ ! -f "$HOOKS_SRC/$hook" ]]; then
    echo "[ERROR] template hook 不在: $HOOKS_SRC/$hook" >&2
    exit 2
  fi
done
for skill in "${COMMON_SKILLS[@]}"; do
  if [[ ! -d "$SKILLS_SRC/$skill" ]]; then
    echo "[ERROR] template skill 不在: $SKILLS_SRC/$skill" >&2
    exit 2
  fi
done

if ! $JSON_MODE; then
  echo "=== peer shared payload drift audit ==="
  echo "  hooks:  ${SHARED_HOOKS[*]}"
  echo "  skills: ${COMMON_SKILLS[*]}"
  [[ -n "$PEER_FILTER" ]] && echo "  filter: $PEER_FILTER"
  echo ""
fi

# here-string で subshell 化を回避 (counter 保持)
while IFS='|' read -r division peer_base; do
  [[ -z "$division" ]] && continue
  if [[ -n "$PEER_FILTER" && "$division" != "$PEER_FILTER" ]]; then
    continue
  fi
  audit_peer "$division" "$peer_base"
done <<< "$TARGETS"

if $JSON_MODE; then
  printf '{"summary":{"ok":%d,"drift":%d,"miss":%d},"entries":[' \
    "$OK_COUNT" "$DRIFT_COUNT" "$MISS_COUNT"
  for i in "${!JSON_ENTRIES[@]}"; do
    [[ $i -gt 0 ]] && printf ','
    printf '%s' "${JSON_ENTRIES[$i]}"
  done
  printf ']}\n'
else
  echo ""
  echo "=========================================="
  echo "summary: OK=${OK_COUNT}, DRIFT=${DRIFT_COUNT}, MISS=${MISS_COUNT}"
  echo "=========================================="
fi

if [[ $DRIFT_COUNT -gt 0 ]]; then
  exit 1
elif [[ $MISS_COUNT -gt 0 ]]; then
  exit 2
fi
exit 0
```

## 7. 設計判断 note

### 7.1 sha256 source: shasum (macOS / Linux 両対応)

`shasum -a 256` は macOS デフォルト、 Linux でも widely available (perl 依存)。 `sha256sum` は Linux のみ。 portability 優先で shasum 採用。

### 7.2 dir 全体 hash の実装

```bash
(cd "$target" && find . -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256) | shasum -a 256
```

- `LC_ALL=C` で sort order 固定 (locale 依存防止)
- `find -print0` + `sort -z` + `xargs -0` で空白 / 改行を含む file 名対応
- 各 file の hash を集約 → 全体 hash を取り直しで dir hash 化
- file 追加 / 削除 / 中身変更 すべて検知

### 7.3 subshell 化回避

`distribute-skills.sh` line 69 は `echo "$TARGETS" | while ...` で **pipe → subshell** になり、 counter 変数が parent shell に伝わらない問題あり (UPDATED/CREATED/SKIPPED は宣言されているが、 末尾で参照されていないので問題顕在化していない)。

本 script は summary を末尾で必ず出力するため、 `while ... done <<< "$TARGETS"` (here-string) で同一 shell 内に保持。

### 7.4 read-only 保証

- file write 操作なし (`>` `>>` `mkdir` `rsync` `sed -i` 等すべて未使用)
- `shasum` / `find` / `xargs` / `awk` のみ使用
- peer file への副作用ゼロ、 cron 実行で安全

### 7.5 exit code design

drift と miss の同時発生時に 1 (drift) を優先する理由:
- drift = peer 側 改変による silent divergence (root cause 調査必須)
- miss = 配布漏れ (機械的に再配布で復旧可)
- drift の方が severity 高、 conductor escalation priority も上

## 8. dry-run 計画 (5/27 Phase 2 Gate 後想定)

```bash
# 1. template 課で全 peer audit (text mode)
./scripts/audit-peer-drift.sh

# 2. 機械可読出力で集約候補確認
./scripts/audit-peer-drift.sh --json | jq .

# 3. 単 peer 確認 (cowork で task #24 整合 verify)
./scripts/audit-peer-drift.sh --peer cowork --verbose
./scripts/audit-peer-drift.sh --peer occur --verbose
```

期待結果:
- 全 peer OK: 11 peer × 4 item = 44 OK
- もし occur dir path が `mued-occur` でなければ SKIP detection (TARGETS 修正必要)
- cowork / occur で common skill 未配置あれば distribute-skills.sh 再実行検討

## 9. 5/27-6/3 timeline 落とし込み

| date | step |
|------|------|
| 5/26 | 本 draft 完納、 kimny + conductor review 依頼 |
| 5/27 Phase 2 Gate 後 | 承認後 feature branch `feat/audit-peer-drift` 作成、 `scripts/audit-peer-drift.sh` 配置 |
| 5/28 | dry-run 実行、 全 peer baseline 取得 + drift / miss list 化 |
| 5/29 | drift 検出時 conductor escalation path 設計 (incident response runbook) |
| 5/30-6/2 | PR review + 修正 |
| 6/3 | merge + production 化、 cowork peer に月次 cron 提案 dispatch |

## 10. 拡張 path (Gap 2 / Gap 3 と接続)

- **Gap 2 (skills-lock.json enforcement)**: 本 script の sha256 計算ロジックを再利用、 `skills-lock.json` の `computedHash` と比較で hash drift 検知に転用可能
- **Gap 3 (settings.local.json permission drift)**: 本 script の TARGETS と JSON 出力 pattern を踏襲、 hooks/skills の audit に並列で permissions audit を追加 (別 script 推奨、 結合は monthly report layer で)

## 11. 残 Open Q (kimny + conductor 判断)

1. **TARGETS の正本化場所**: 各 distribute script で TARGETS が散在 (distribute-skills.sh 10 peer、 distribute-quality-standards.sh 11 peer、 distribute-claude-md-blocks.sh は ?)、 本 audit script でも独自 TARGETS → 統一 source (`scripts/peer-targets.sh` 等) に切り出すべきか。 本 draft では distribute-skills.sh パターン踏襲のみ。
2. **task #24 merge 前後どちらで dry-run するか**: task #24 merge 後 (cowork+occur 整合復帰後) が望ましいが、 task #24 検証 evidence として dry-run 結果を添えるなら merge 前にも有用。 conductor 判断。
3. **occur dir 実 path**: 上記 TARGETS で `mued-occur` 想定、 kimny 確認推奨。
4. **cron 化担当**: cowork RemoteTrigger 枠 vs template 課 cron vs conductor `/checkout` step、 5/10 trilateral 4本柱 修正提案 3 と整合させる必要 (cron `wjqx_repo_audit` 配置代替の議論延長)。
