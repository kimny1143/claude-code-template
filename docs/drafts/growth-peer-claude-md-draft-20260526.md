# growth 課 (新設) CLAUDE.md 原本 + onboarding 計画 draft (2026-05-26)

- [ ] kimny確認 (Tier 3、 新 peer workspace + 全課波及 distribute scripts patches)
- [x] conductor承認 — 2026-05-26 10:58 JST 頃 (A 案採用 dispatch、 14 peer 体制)
- [x] kimny 直接承認 (A 案 GO、 2026-05-26 11:00 JST 頃、 conductor relay 経由 報告済)
- ETA: 5/26 EOD まで本 doc + feature branch 完納 → 5/27 Phase 2 Gate 並行 kimny final approve → 5/28 active launch

## 0. CCO hook 制約による executor 役割分担

CCO `.claude/hooks/validate-dangerous-ops-v2.sh` が CWD-外 file 編集 (本 CCO session の場合 `_growth/*`) を block 設計 (CLAUDE.md「他peerワークスペースを直接変更しない」 rule の enforcement)。

**directory + git init** までは Bash で完納 (file write でない subprocess) ✅
- `mkdir -p /Users/kimny/Dropbox/_DevProjects/_growth` ✅
- `git init` + `git symbolic-ref HEAD refs/heads/main` ✅

**_growth/ 内 file 配置** は CCO scope では block されるため、 以下のいずれかで execution 必要:
- (a) **kimny 直接実行** (recommend、 `!` prefix で本 doc 内 file content を copy-paste 配置)
- (b) **conductor session 実行** (conductor 側 hook 設定次第)
- (c) **CCO 一時的 cwd 切替** (危険、 hook 無効化 risk = 不採用)

→ (a) kimny 直接実行が cleanest path、 本 doc Section 2 に file content inline。

## 1. growth 課 役割定義 (kimny dispatch + conductor 整理)

### 主軸 mission

「**集客 + 売上**」 主軸 peer。 既 13 peer がほぼ全部「内向き」 (build / maintenance / governance) 設計の reality check confirmed (kimny 5/26 指摘「色々やってるけど、 まったく収益生む匂いがしない」)。

### 担当 scope

1. **流入経路設計**: SEO / paid ad (Google Ads / Meta) / referral / partnerships / コンテンツマーケ
2. **conversion funnel design + A/B test**: LP optimization / signup CRO / paywall design / upgrade flow
3. **acquisition cadence + budget management**: 月次 acquisition target + budget tracking + ROI 監視
4. **死蔵商品 (Gumroad / Ko-fi) 再起動**: Pro$29 / 旧テンプレ商品の retention strategy + relaunch campaign
5. **既 peer 横串 acquisition layer**: LP / SNS / data peer の output を funnel 観点で統合

### 既 peer との分担境界 (重複 / drift 防止)

| 既 peer | 既 scope | growth scope | sync point |
|---------|---------|-------------|-----------|
| **LP** (`_LandingPage/glasswerks-lp`) | 製品サイト integrity 維持、 デザイン、 page 構築 | paid CTR / acquisition page A/B test, copy 改善 propose | weekly LP↔growth ペア review |
| **SNS** (`mued/threads-api`) | post 作成、 engagement、 voice 維持 | SNS channel strategy、 paid promotion 設計、 acquisition KPI 提示 | weekly SNS↔growth dispatch |
| **data** (`_data-analysis`) | 観測、 metric 計測、 dashboard 構築 | experiment design、 funnel metric 統合、 A/B test 設計委託 | data → growth 月次 acquisition report |
| **freee** (`freee-MCP`) | 会計、 原価、 CFO 領域 | revenue strategy、 死蔵商品 retention、 価格-粗利連動 | freee↔growth 月次 P&L review |
| **write** (`_contents-writing`) | コンテンツ品質、 voice 維持、 note / Zenn 記事 | SEO content brief、 acquisition keyword strategy、 content gap audit | write↔growth coordination |
| **mued / native** | プロダクト本体 | 直接関与なし (LP / SNS 経由) | growth 関与なし |
| **conductor / template / freee / cowork** (経営部) | governance / 配布 / CFO / orchestration | growth は経営部 layer ではなく **マーケ部 + 横串 acquisition** layer 想定 | conductor 経由 dispatch / weekly sync |

### 死蔵商品 audit 範囲 (conductor 同時 dispatch freee で着手中)

- Gumroad Pro$29 (template repo Premium 商品、 公開済)
- 旧テンプレ商品 (記憶 `project_premium_content`)
- Ko-fi (未確認、 freee 側 audit 待ち)
- → freee audit 結果受領後、 growth 着任 (5/28-) で relaunch strategy 設計

### 反 over-engineering 原則

- 「ままごと dashboard」 禁止 (codex 出力 + CCO Q3 cadence 共通)
- 「精度より傾向」 (15 分未満記録禁止、 codex output 採用)
- 「kimny に試遊させない」 = kimny に test 数字確認させない、 growth 内自走で acquisition number 提示

## 2. growth 課 file content (kimny 配置 用 inline content)

### 2-1. `/Users/kimny/Dropbox/_DevProjects/_growth/CLAUDE.md` (final 版、 placeholder 上書き)

```markdown
# CLAUDE.md — growth 課

集客 + 売上主軸 peer (2026-05-28 active launch、 14 peer 体制)。

## 主軸 mission

既 13 peer が build / maintenance / governance に偏った reality check (kimny 5/26 指摘) から、 「外向き acquisition + revenue」 を専門で受け持つ peer として新設。

## 担当 scope

1. 流入経路設計 (SEO / paid ad / referral / partnerships / コンテンツマーケ)
2. conversion funnel design + A/B test (LP / signup / paywall / upgrade)
3. acquisition cadence + budget management (月次 target + ROI 監視)
4. 死蔵商品再起動 (Gumroad / Ko-fi、 freee CFO audit 連携)
5. 既 peer 横串 acquisition layer (LP / SNS / data / write の output 統合)

## 既 peer との分担境界

→ template repo `docs/drafts/growth-peer-claude-md-draft-20260526.md` Section 1 表参照 (恒久 doc 化は 5/28 active launch 後 `docs/peer-boundaries.md` 候補)

## Tier 判定 + PR レビュー権限

template repo CLAUDE.md `PRレビュー権限` 共通基準 per:
- Tier 1: docs / data / コピーのみ → セルフマージ
- Tier 2: コード変更あり → ペアレビュー (推奨先: LP 課)
- Tier 3: 価格 / 認証 / 全課波及 → conductor + kimny 直接承認

## 共通 rule

- `feedback_kimny_quality_standards.md` 全課共通 quality standard (memory 経由配布済)
- `feedback_zero_kimny_manual_work.md` (kimny 工数ゼロ原則)
- `plan-mode-policy` skill (異常値検出 → /plan 発動 共通 framework)
- `tier-judge` skill (PR Tier 自動提案)
- `peer-id-lookup` skill (peer ID 解決)

## 起源

- 2026-05-26 kimny Tier 3 承認 (A 案 = growth 課 1 peer 新設)
- 詳細起源 + onboarding 計画: template repo `docs/drafts/growth-peer-claude-md-draft-20260526.md`

## Common blocks (cognitive load v3、 5/28 active launch 後 marker 挿入予定)

5/28 active launch 後、 `scripts/distribute-claude-md-blocks.sh` で経営部 + マーケ部共通 18 blocks を本 file 末尾に marker 挿入で fill する (Phase 2 0.3 fanout の一環)。
```

### 2-2. `/Users/kimny/Dropbox/_DevProjects/_growth/README.md`

```markdown
# _growth — growth 課 workspace

集客 + 売上主軸 peer (14 peer 体制、 2026-05-26 新設、 5/28 active launch)。

## 設計起源

- kimny 5/26 directive: 「色々やってるけど、 まったく収益生む匂いがしない」 + 「収益や集客について専門部署が必要なんじゃないの？」
- conductor 5/26 三者議論 critical finding: 既 13 peer = 内向き設計、 外向き専門 peer 不在
- 採用案: A 案 (growth 課 1 peer 新設、 14 peer 体制)

## scope

- 流入経路設計 / conversion funnel / acquisition cadence / 死蔵商品再起動 / 既 peer 横串 acquisition layer

詳細は `CLAUDE.md` + template repo `docs/drafts/growth-peer-claude-md-draft-20260526.md` 参照。
```

### 2-3. `/Users/kimny/Dropbox/_DevProjects/_growth/.gitignore`

```
.DS_Store
.env*
node_modules/
__pycache__/
*.pyc
.venv/
venv/
.vscode/
.idea/
*.log

.claude/settings.local.json
.claude/projects/
```

### 2-4. `/Users/kimny/Dropbox/_DevProjects/_growth/.claude/settings.local.json` (5/28 launch 時)

template `docs/templates/settings-local-base.json` を base に、 growth 固有 permission (なし、 launch 後 段階追加) で開始。

```bash
# kimny 配置時 cmd:
mkdir -p /Users/kimny/Dropbox/_DevProjects/_growth/.claude
cp /Users/kimny/Dropbox/_DevProjects/claude-code-template/docs/templates/settings-local-base.json \
   /Users/kimny/Dropbox/_DevProjects/_growth/.claude/settings.local.json
```

または kimny 直接実行で `distribute-settings-allow.sh` 再実行 (本 doc Section 3 patches 適用後)。

## 3. distribute scripts patches (feature branch `feat/growth-peer-onboarding`)

CCO scope 内で直接 patch 可能。 feature branch + PR + kimny + conductor 承認後 merge。

### 3-1. `scripts/distribute-quality-standards.sh`

```diff
 # 全13課: 課名|プロジェクトディレクトリ名
 # 2026-05-26 task #24 ii-a hybrid: cowork + occur 追加 (kimny Q5 GO、 conductor 承認 5/12 14:04 JST)
+# 2026-05-26 growth 課新設 (A 案、 kimny 直接承認 + conductor relay)、 14 peer 体制
 DIVISIONS="
 conductor|-Users-kimny-Dropbox--DevProjects--conductor
 ... (中略) ...
 cowork|-Users-kimny-Dropbox--DevProjects--cowork
 occur|-Users-kimny-Dropbox--DevProjects--mued-occur
+growth|-Users-kimny-Dropbox--DevProjects--growth
 "
```

→ 14 peer broadcast。 注: growth の `~/.claude/projects/<encoded>/memory/` dir は kimny が `_growth` で claudepeers 1 回起動した時点で自動作成 (Claude Code 仕様)、 distribute 実行はその後。

### 3-2. `scripts/distribute-skills.sh`

```diff
 TARGETS="
 conductor|/Users/kimny/Dropbox/_DevProjects/_conductor/.claude/skills
 ... (中略) ...
 SNS|/Users/kimny/Dropbox/_DevProjects/mued/threads-api/.claude/skills
+growth|/Users/kimny/Dropbox/_DevProjects/_growth/.claude/skills
 "
```

### 3-3. `scripts/distribute-settings-allow.sh`

```diff
 TARGETS=(
   "/Users/kimny/Dropbox/_DevProjects/_conductor/.claude/settings.local.json"
   ... (中略) ...
   "/Users/kimny/Dropbox/_DevProjects/mued/threads-api/.claude/settings.local.json"
+  "/Users/kimny/Dropbox/_DevProjects/_growth/.claude/settings.local.json"
 )
```

### 3-4. `scripts/distribute-claude-md-blocks.sh`

```diff
 declare -a TARGET_PEERS=(
     "$TEMPLATE_REPO/CLAUDE.md"
     ... (中略) ...
     "$HOME/Dropbox/_DevProjects/_blender/CLAUDE.md"
+    "$HOME/Dropbox/_DevProjects/_growth/CLAUDE.md"
 )
```

## 4. 起動 script patches (conductor side、 CCO suggest only)

`_conductor/scripts/start-all-peers-ghostty.sh` + `reconnect-all-peers-ghostty.sh` は CCO CWD-外 で modify 不可。 conductor session で適用必要。

### 4-1. start-all-peers-ghostty.sh 追加 location 候補

**Option (A)**: Window 1 (経営部) に追加 → 4 タブ (CCO template / CFO freee / cowork / **growth**)
**Option (B)**: Window 3 (マーケティング部) に追加 → 4 タブ (SNS / write / LP / **growth**)

conductor 推奨: growth role が "外向き acquisition + revenue" = マーケ部 + 横串 acquisition layer → **(B) Window 3 マーケティング部** が妥当 (本 doc Section 1 分担境界表と整合)。

```diff
 -- Window 3: マーケティング部 (3タブ: SNS課, write課, LP課) ※video課クローズ(4/11)
 ... (中略 SNS / write / LP 既存タブ) ...

+        -- growth課: 2026-05-26 kimny判断でOpus固定（acquisition + revenue 主軸、 LP / SNS / data / write 横串 layer）
+        set cfg to new surface configuration
+        set initial working directory of cfg to base & "/_growth"
+        set initial input of cfg to "claudepeers --model opus\n"
+        new tab in mktWin with configuration cfg
+        delay 1
```

### 4-2. Window 3 タイトル / comment 更新

```diff
- -- Window 3: マーケティング部 (3タブ: SNS課, write課, LP課) ※video課クローズ(4/11)
+ -- Window 3: マーケティング部 (4タブ: SNS課, write課, LP課, growth課) ※video課クローズ(4/11)、 growth課追加(5/26)
```

### 4-3. reconnect-all-peers-ghostty.sh 同等 patch

reconnect script も start script と同 structure 想定 (CCO 未 verify、 conductor 確認推奨)。

## 5. peer ID assign + claude-peers 統合

5/28 active launch flow:
1. kimny `_growth` で `claudepeers --model opus` 起動
2. 初回起動で `~/.claude/projects/-Users-kimny-Dropbox--DevProjects--growth/` 自動作成
3. claude-peers 自動 enroll → peer ID 自動 assign (例: `g7xy8k0z` 等)
4. CCO + conductor が `mcp__claude-peers__list_peers` で新 peer ID 確認
5. CCO 側 `peer-id-lookup` skill source (`peer_aliases.json` or 同等) 更新 (もしあれば)
6. `set_summary` template 設計 (growth peer 推奨 summary format):
   ```
   growth課。 集客 + 売上主軸 (acquisition + revenue)、 LP / SNS / data 横串 layer、 死蔵商品再起動担当。
   ```

## 6. sync protocol 設計 (weekly cadence、 drift 防止)

### 6-1. 既 peer ↔ growth sync 議事録 (weekly)

| sync pair | cadence | format | inbox |
|-----------|---------|--------|-------|
| LP ↔ growth | weekly | LP page A/B test 結果 + growth acquisition data | conductor `docs/sync/` |
| SNS ↔ growth | weekly | post engagement + growth channel strategy | conductor `docs/sync/` |
| data ↔ growth | monthly | acquisition report (funnel metric 統合) | conductor `docs/sync/` |
| freee ↔ growth | monthly | P&L review + 死蔵商品 retention 進捗 | conductor `docs/sync/` |
| write ↔ growth | bi-weekly | SEO content brief + content gap audit | conductor `docs/sync/` |

5/27 sync framework に integrate 候補 (conductor 提案)。 本 doc 5/28 launch 後実体化。

### 6-2. drift 防止 mechanism

- weekly conductor 全 peer status patrol で growth peer も対象化
- growth peer 内 status.md (heartbeat protocol、 memory `feedback_heartbeat_operation.md` per) で active state 可視化
- Gap 1 audit-peer-drift script に growth peer 追加 (TARGETS extend、 本 onboarding PR で同時 patch 候補)

## 7. Tier 判定 + PR sequence

- **本 onboarding PR** (feature branch `feat/growth-peer-onboarding`) = **Tier 3** (新 peer 追加 + 4 distribute scripts patch + 全課波及)
- 承認: kimny 直接 GO 受領済 (5/26) → conductor review → CCO self-merge GO 想定

PR 内容:
1. 本 design doc (`docs/drafts/growth-peer-claude-md-draft-20260526.md`)
2. 4 distribute scripts patches (Section 3 per)
3. README or implementation notes doc (optional)

起動 script patches は **本 PR 対象外** (conductor repo)。 conductor session で別 PR 起票推奨。

## 8. Open Q (kimny + conductor 判断)

1. **growth peer 配置 Window**: (A) 経営部 vs (B) マーケティング部 — CCO 推奨 (B) per Section 4-1
2. **growth peer 初期 budget**: 月次 ad spend 上限 (例: $500/月) 設定すべきか
3. **死蔵商品 retention threshold**: 月次売上 $X 未満で archive 判断 (例: $10/月) 設定すべきか
4. **growth ↔ kimny 直接 channel**: revenue 数字 / 流入 metric は conductor 経由か growth 直接 kimny 報告か
5. **launch 後 30 日 review**: acquisition impact 0 なら scope 縮小 / 解体 判断 cadence 設定すべきか

## 9. timeline

- ✅ 5/26 10:58 JST conductor dispatch 受領
- ✅ 5/26 11:00 JST kimny A 案 GO (conductor relay)
- ✅ 5/26 (本 doc 完納時刻) CCO 着手:
  - workspace dir + git init ✅
  - 本 doc 完納 ✅
  - feature branch + 4 distribute scripts patches ⏳
- ⏳ 5/26 EOD kimny `_growth/` 内 file 配置 (Section 2 inline content から copy-paste)
- ⏳ 5/27 Phase 2 Gate 並行 kimny final approve + PR merge
- ⏳ 5/27-5/28 conductor 起動 script patch (Section 4)
- ⏳ 5/28 active launch: kimny `claudepeers --model opus` 起動 → peer ID assign → distribute scripts 本実行 → 14 peer 整合

## 10. 次 action (本 doc 完納後)

1. CCO: feature branch `feat/growth-peer-onboarding` で 4 distribute scripts patches commit + PR 起票
2. CCO → conductor: 本 doc + PR notify
3. conductor → kimny: short report (workspace + draft 完納、 5/27 review path)
4. kimny: Section 2 inline content を `_growth/` に配置 (CCO hook 制約により kimny 直接 OR conductor session 経由)
5. kimny + conductor: 5/27 Phase 2 Gate 並行 review + final approve
6. CCO: PR merge + distribute scripts 本実行 + active launch verify
