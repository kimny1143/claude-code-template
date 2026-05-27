# audit-skills-lock.sh — skills-lock.json drift detection + baseline registration (Gap 2)

- 状態: **shipped 2026-05-27** (Tier 2、 conductor peer review path、 sourceType=local default)
- conductor 5/27 GO: B 案要素 (full impl) 採用、 段 1 (audit) + 段 2 (--update mode) 同 PR
- 段 3 (`distribute-skills.sh` patch) は **別 PR (Tier 3 候補、 後続)**
- 起源: 2026-05-26 trilateral 議論 CCO input Gap 2
- evidence: ship 前 `skills-lock.json` 7 / 46 tracked (15% カバー)、 ship 後 baseline 一括登録で 46 / 46 (100%)

## Ship 時点 dry-run + baseline 登録 結果 (2026-05-27)

### 段 1 audit (baseline 登録前)

```
$ ./scripts/audit-skills-lock.sh
summary: TRACKED=0, DRIFT=7, UNTRACKED=39
```

- DRIFT 7: 既登録 7 件すべて hash drift (= 配布後の version up が lock 未反映)
- UNTRACKED 39: 残 39 件 lock 未登録 (symlink 5 件 = .agents/skills/ 経由 Codex mirror 含む)

### 段 2 --update --confirm 一括登録

```
$ ./scripts/audit-skills-lock.sh --update --confirm
summary: ADDED=39, UPDATED=7, UNCHANGED=0
```

backup: `skills-lock.json.bak.<timestamp>` 自動作成 (PR には含めず、 local 一時 artifact)
sourceType default = "local" (個別分類は後続 task で github / well-known / internal-common に修正)

### 段 1 再 audit (baseline 登録後)

```
$ ./scripts/audit-skills-lock.sh
summary: TRACKED=46, DRIFT=0, UNTRACKED=0
```

## 1. 問題定義

```bash
$ ls .claude/skills | wc -l
46
$ jq '.skills | keys | length' skills-lock.json
7
```

**diff**: 39 skill (84%) が skills-lock.json 未登録 = hash trace 不能 = 配布履歴・version drift・無断 update detection 全空白。

加えて `distribute-skills.sh` source comment:
```
#   - skills-lock.json の更新は手動（段階1ではスコープ外）
```

= 既 tracked 7 skill も distribute 時に hash 自動更新されない = `computedHash` が distribute 時点 snapshot で固定化 → 内容 update 時 silent stale。

## 2. 設計概要 (3 段構成)

### 段 1: `scripts/audit-skills-lock.sh` (新規、 read-only audit)

```bash
#!/bin/bash
# audit-skills-lock.sh — .claude/skills 全 skill の sha256 を skills-lock.json と照合
# Usage:
#   ./scripts/audit-skills-lock.sh                   # audit only (default, exit 0/1/2)
#   ./scripts/audit-skills-lock.sh --json            # 機械可読
#   ./scripts/audit-skills-lock.sh --skill <name>    # 単 skill audit
#
# exit code:
#   0 = all tracked + hash match
#   1 = hash drift (locked vs actual mismatch)
#   2 = untracked skill exists (lock 未登録)

# 主要 logic:
# 1. .claude/skills/<name>/ の sha256 (dir 全体 hash、 Gap 1 と同 sha256_of helper 再利用)
# 2. skills-lock.json[<name>].computedHash と照合
# 3. 未登録は [UNTRACKED] 出力
# 4. mismatch は [DRIFT] 出力 (locked:<short> actual:<short>)
# 5. match は [TRACKED] 出力 (--verbose 時のみ)
```

### 段 2: `scripts/audit-skills-lock.sh --update` mode (一括 baseline + 継続 hash 更新)

```bash
# --update mode:
# 1. 全 .claude/skills/<name>/ の hash 計算
# 2. skills-lock.json 既登録 → computedHash 更新 (+ distributedAt 維持)
# 3. 未登録 skill → 新規 entry 追加 (sourceType は "local" default、 Open Q1 参照)
# 4. .gitignore / hidden file 除外 (.DS_Store 等)
# 5. 出力: [UPDATED] / [ADDED] / [UNCHANGED] 各 count
#
# 安全装置:
# - --update 単独実行禁止、 必ず --update --confirm の 2 flag 必要 (誤実行防止)
# - JSON write 前に backup (skills-lock.json.bak.<timestamp>) 自動作成
```

### 段 3: `scripts/distribute-skills.sh` patch (hash auto-update)

```bash
# 既 distribute-skills.sh 末尾に追加:
#
# 配布完納後、 配布対象 skill の computedHash を skills-lock.json で更新
# (手動更新負荷除去、 distribute と lock の整合性保証)
#
# patch logic (簡易):
#   for skill in "${COMMON_SKILLS[@]}"; do
#     hash=$(compute_skill_hash "$SKILLS_BASE/$skill")
#     jq --arg name "$skill" --arg h "$hash" --arg d "$(date +%Y-%m-%d)" '
#       .skills[$name].computedHash = $h |
#       .skills[$name].distributedAt = $d |
#       .skills[$name].distributedBy = "scripts/distribute-skills.sh"
#     ' skills-lock.json > skills-lock.json.tmp && mv skills-lock.json.tmp skills-lock.json
#   done
#
# 安全装置:
# - --dry-run 時は jq 実行せず diff のみ表示
# - 失敗時 backup file 残置
```

## 3. baseline 一括登録 計画 (initial run)

```bash
# step 1: backup (手動)
cp skills-lock.json skills-lock.json.bak.20260527

# step 2: dry-run で全 untracked detect
./scripts/audit-skills-lock.sh
# 期待出力:
#   [UNTRACKED] ai-interview-article: lock 未登録
#   [UNTRACKED] aax-validator: lock 未登録
#   ... (39 件)
#   summary: TRACKED=7, DRIFT=0, UNTRACKED=39

# step 3: --update --confirm で baseline 一括登録
./scripts/audit-skills-lock.sh --update --confirm
# 期待出力:
#   [ADDED]    ai-interview-article: hash=8f3a... sourceType=local
#   ... (39 件)
#   [UPDATED]  freee-api-skill: hash unchanged
#   ...
#   summary: ADDED=39, UPDATED=7 (hash 再計算)、 UNCHANGED=0

# step 4: verify
./scripts/audit-skills-lock.sh
# 期待出力: summary: TRACKED=46, DRIFT=0, UNTRACKED=0 (exit 0)
```

## 4. Gap 1 (audit-peer-drift) との関係

| 項目 | Gap 1 (audit-peer-drift) | Gap 2 (audit-skills-lock) |
|------|--------------------------|---------------------------|
| 比較対象 | template ↔ 全 peer | template skill ↔ skills-lock.json |
| 方向性 | peer 側 drift detect | template 内 lock 整合性 |
| sha256 helper | `sha256_of` 関数 | **共通化候補** (両 script で再利用) |
| exit code 設計 | 同型 (0/1/2) | 同型 (0/1/2) |
| update 機能 | なし (read-only only) | あり (`--update` mode) |

**統合 path**: `scripts/lib/sha256.sh` (新規) に `sha256_of` 関数を切り出し、 両 script で source。 Gap 1 PR で sha256_of inline、 Gap 2 PR で lib 切り出し migration。

## 5. minimal draft 範囲限定 (full PR は後続)

本 draft = **設計 doc only**、 以下は後続 PR で実装:
- script 本体 full LOC (Gap 1 と同程度 = 約 180 LOC 想定)
- distribute-skills.sh patch
- skills-lock.json baseline 一括登録 (39 件追加)
- README / docs update

task #24 完納 + Gap 1 PR 承認 sequencing 後、 conductor + kimny 承認 GO 受領で feature branch `feat/audit-skills-lock` 起票予定。

## 6. Open Q

1. **untracked 39 skill の sourceType 分類**:
   - (a) 一律 "local" default、 後で個別 update
   - (b) 起源 inference (github / well-known / internal-common / local) で自動分類
   - (c) CCO 一回手動分類 + 以降 distribute 時 hash 更新のみ
   推奨: (a) 一律 "local" → 後続 individual update task

2. **distribute-skills.sh patch 範囲**:
   - 現状 distribute-skills.sh は COMMON_SKILLS 3 件のみ配布
   - SHARED_SKILLS (setup.sh) の全 skill にも hash 自動更新を拡張すべきか
   推奨: COMMON_SKILLS only から開始、 SHARED_SKILLS 拡張は別 PR

3. **internal-common 以外 (github / well-known) の update cadence**:
   - 現 `freee-api-skill` (github) / `stripe-*` (well-known) は手動 fetch → 配置
   - hash 更新は手動 fetch 時点で `--update` 走らせる pattern か
   推奨: 現状維持 (手動 fetch 時に `--update` 必須化を README に明記)

4. **drift detect 時 conductor escalation path**:
   - DRIFT detect = skill 内容が無断 update されている = 重大 incident
   - immediate escalation 必要 (Gap 1 の peer drift と同等 severity)
   推奨: Gap 1 + Gap 2 共通の `scripts/escalate-drift.sh` (新規候補) を Gap 4 (hook bypass) 段階で同時設計

5. **cron 化**:
   - Gap 1 と同様 cowork RemoteTrigger 候補
   - 月次 audit で全 46 skill drift check
   推奨: Gap 1 cron 化と pair で 1 cron 内 2 script 連続実行 (cowork peer dispatch 時に提案)

## 7. timeline

- 5/26 本 minimal draft 完納
- 5/27-6/3: task #24 完納確認後 + Gap 1 PR 承認後、 Gap 2 full draft (script 本体) 着手 + PR 起票
- 6/3-6/10: PR review + baseline 一括登録 (39 件追加)
- 6/10-6/20: distribute-skills.sh patch + 月次 cron 化検討

## 8. Tier 判定 想定

- **audit script 単独** = Tier 2 (新規 read-only script、 全課波及なし)
- **distribute-skills.sh patch** = Tier 3 (既存配布 script 変更 + 全課影響)
- **baseline 一括登録** = Tier 2 (skills-lock.json のみ変更、 distribute 影響なし)

分割 PR 推奨:
- PR-A: audit-skills-lock.sh 単独 (Tier 2、 LP/native peer review)
- PR-B: baseline 一括登録 (Tier 2、 PR-A merge 後)
- PR-C: distribute-skills.sh patch (Tier 3、 conductor + kimny review)
