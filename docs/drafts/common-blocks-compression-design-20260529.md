# 共通ブロック群 fleet-wide 圧縮設計案 — 2026-05-29

**起案**: CCO (template課) / **dispatch**: conductor Tier 3 fleet-wide (kimny GO 2026-05-29)
**process**: 設計先行 (project-root-claudemd-discipline)。本案 → conductor review → 実装 → 全 peer 通知。一括変更しない。

## 1. find 確認結果 (実態 grounding)

canonical source = `.claude/skills/common-claude-md-blocks/blocks/` に **19 blocks / 計 582 行 / ~38KB**。
`distribute-claude-md-blocks.sh` が marker-bounded section 置換で 14 peer の CLAUDE.md へ同期。

- dispatch の「12 blocks」は judgment-quality + communication 群 (09-18) の体感サブセット。canonical 実数は **01-19**。
- 5/20 に `19-character-gate` 追加済 (SKILL.md は「19 blocks」反映済、CLAUDE.md 本文は「18」と stale → 別途修正)。
- 14 peer 全てが全 19 block を載せる設計 (TARGET_PEERS 14 paths)。1 peer 起動あたり ~38KB ≈ 約 10-12k tokens がこの群だけで占有 → 40k 警告の主要因と整合。

## 2. 設計判断: 「再配置」は per-peer context をほぼ削減しない (conductor 想定の補正)

dispatch actionable #3 (上位階層への再配置) を find 結果に照らして補正する。

- **@path import**: 取り込み時に content が展開される = context 削減ゼロ (conductor 既認識通り)。
- **階層継承 (親 CLAUDE.md auto-load)**: 各 peer の起動 context = 親 (1回) + 自分。共通ブロックを親へ hoist して各 peer から除いても、**per-peer の総 context は不変** (親で 1回 load されるだけ)。階層 hoist は「ファイル間重複の解消 (保守)」と「native/mued の二重 load 解消」には効くが、**起動時トークン削減の lever ではない**。
- **例外 = native**: native (apps/) は親 mued_v2 を階層 load するので、自分で共通ブロックを持つのは二重保持。削除＝正しい dedup (inheritance 健全)。これは mued 課並行作業で処理 (dispatch 整合)。

→ **per-peer 起動トークンを削る実 lever は (A) 圧縮 と (B) hook 化の 2 つ。** 加えて (C) selective distribution (peer が要らない block を配らない) が小さく効く。再配置は保守 dedup として副次的に扱う。

## 3. ブロック別 振り分け (圧縮 / hook / 維持 / 再配置)

| # | block | 現行 | 分類 | 後(目安) | 根拠 |
|---|-------|-----:|------|------:|------|
|01|operational-premise|13|維持(微圧縮)|11|core culture。dormant 括弧日付を trim|
|02|memory-cleanup|8|維持|8|既 minimal|
|03|chrome-lock|11|維持|11|既 minimal。全 peer 認知が lock 制に必要|
|04|org-structure|19|維持(微圧縮)|17|table 必須。改定日付括弧 trim|
|05|opus-fixed-plan-mode|31|**圧縮(大)**|10|opusplan 時代の「背景」= obsolete (Opus 固定済) 全削除。具体運用/禁止パターンを 1 リストに集約|
|06|plan-trigger-conditions|24|圧縮|16|発動 list 保持、「判断に迷ったとき」散文を 2 行に|
|07|available-models-rule|14|圧縮|9|理由散文 trim、bug issue URL は残す|
|08|conductor-delegation|15|維持|13|core 権限境界|
|09|peer-self-judgment|35|圧縮|20|Why (occur 事例) 削除、判定3軸 + list 保持|
|10|mass-production|35|**圧縮(大)**|14|履歴 timeline + 適用方法の重複散文削除、ルール core 保持|
|11|existing-state-first|25|圧縮|10|Why (occur 長例) + 他peer示唆 削除|
|12|self-correction|43|**圧縮(大)**|15|Why timeline + 他peer示唆 削除、ルール+境界 保持|
|13|reference-vs-docs|27|圧縮|12|Why (5/9 evidence) 削除|
|14|conductor-active-judgment|52|**再配置 + 圧縮**|0(13peer)/20(conductor)|block 自身が「conductor 自peer が第一義 owner」と明記。他 13 peer に不要 → conductor のみ配布、本体は圧縮|
|15|urgency-marker|42|圧縮|22|format + 基準 table 保持、認知負荷効果 + audit category (conductor 側知識) 削除|
|16|external-resource-gate|35|**hook 化 + slim pointer**|5|「毎回必ずの gate」= 機械強制が適。`validate-dangerous-ops-v2.sh` 拡張、CLAUDE.md は 5 行 pointer のみ|
|17|status-md-self-drive|57|**圧縮(大)**|22|cowork cron 内部仕様 + frontmatter 13 fields 詳細を template ref へ、peer 必須 timing + path + push policy 保持|
|18|judgment-request-contract|61|**圧縮(大)**|25|format + example 保持、認知負荷効果 + audit 統合 + Phase 詳細 削除|
|19|character-gate|35|圧縮|18|MUEDear incident 詳細削除、課別 gate table + 3 原則 保持|

### 想定削減量

- **非 conductor peer (13課)**: 582 → **~258 行** (≈ **56% 削減**)、~38KB → ~17KB、起動時 約 9-10k tokens 相当削減。
- **conductor peer**: block 14 を保持 → ~278 行。
- 内訳: 圧縮で ~280 行削減 + block16 hook 化で ~30 行 + block14 再配置で 13 peer から ~52 行除去。

## 4. hook 化の詳細 (block 16)

`16-external-resource-gate` は「外部リソース新規作成 / 公開範囲変更 / 課金 / 不可逆操作 = 常に pre-approval」という **毎回必ず検査** ルール。conductor 構造ルール「必ず毎回の検査は hook に」に合致。

- **対象**: 既存 `.claude/hooks/validate-dangerous-ops-v2.sh` (PreToolUse / Bash) を拡張。
  - 検知パターン: `gh repo create` / `gh repo edit --visibility public` / `gh repo archive` / `gh repo delete` / `git push --force|-f` (main) / history rewrite。
  - match 時: block + メッセージ「外部リソース gate: URGENCY: high + kimny/conductor pre-approval 必須 (CLAUDE.md 16)」。
- **CLAUDE.md 側**: 5 行 pointer に縮約 (「gate 対象操作は hook が機械強制。詳細は resource-audit skill + hook 参照」)。
- **重要 caveat**: validate-dangerous-ops-v2.sh 変更は **全課波及 hook = それ自体が独立 Tier 3 + セキュリティ感受性**。圧縮 PR と **束ねず別 PR / 別レビュー**。stdin JSON / exit code / 絶対 path / 安全制約を弱めないことを verify。圧縮 PR 先行、hook PR は後続 sequence。

他に hook 化を検討したが見送る block:
- 07 (availableModels) — settings.json 編集時の PostToolUse check は可能だが低頻度。圧縮で十分、将来候補。
- 17 (status.md heartbeat) — 行動規律で blockable でない。cowork cron stale 検出が既に後追い enforcement。圧縮で対応。

## 5. 適用方針 (再配布 vs 個別 PR)

ブロックは単一 source から script 配布される構造のため:

1. **PR-A (template課 / 本 repo / Tier 3, kimny GO 済)**: 19 block source の圧縮 + block14 を非 conductor target から除外 + SKILL.md/CLAUDE.md の「18→19」stale 修正。**source of truth のみ変更**。
2. **fanout**: `distribute-claude-md-blocks.sh --dry-run` で 14 peer 差分確認 → 各 peer が自 repo で再生成 section を commit。CLAUDE.md のみ変更 = docs = **Tier 1 (peer self / conductor 代行 merge)**。「他 peer workspace を直接変更しない」原則に従い、distribute 結果は各 peer 自 repo の PR で commit (conductor fanout 調整)。
3. **PR-B (hook, 別 sequence / 独立 Tier 3)**: block16 の validate-dangerous-ops-v2.sh 拡張。PR-A 完納後。
4. **block14 再配置**: 非 conductor peer の CLAUDE.md から block14 marker を除去 (marker 無 = distribute skip = 自動的に配らない)。selective distribution は marker 有無で既に実現可能、script 改修不要。

## 6. conductor への確認事項

本振り分け (圧縮 11 / hook 1 / 維持 4 / 再配置 1 / 微圧縮含む) と sequence (PR-A 圧縮先行 → fanout → PR-B hook 後続) で実装に進めてよいか。
