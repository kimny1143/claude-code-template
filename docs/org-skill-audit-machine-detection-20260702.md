# 全 workspace 横断 skill 棚卸し — 機械検出レポート (2026-07-02)

- 担当: CCO (template課) / Chief brief `_chief/for-conductor/brief-memory-skill-audit-20260702.md` アクション #4
- スコープ: **skill の機械検出のみ** (①未登録 ②hash drift ③残登録 ④課間重複)。memory/durable 層監査 (#1) は Chief/Fable 担当ゆえ**本レポート対象外**。design gap 採否 (kimny QA 待ち) とも**別線**。
- 手法: 既存 script (`audit-skills-lock.sh` / `audit-peer-drift.sh`) + read-only enumeration (find/shasum、**新規 script 開発ゼロ・commit なし・peer file 不変更**)。対象 = template + 15 workspace。
- 前提確認: `/Users/kimny/Dropbox/_DevProjects` は `/Volumes/strage/_DevProjects` への symlink = 両 script のパス解決 OK (パス不整合は finding でない)。
- ★owner 訂正 (2026-07-02 conductor): 本文中の **「LP」= `glasswerks-lp` workspace (物理実体) を指すが、旧 LP 課は 2026-06-11 に content 課へ統合済** (`current-organization.md`)。F2/F4 の LP divergent skill = content の LP spinup 文脈ゆえ、intent 確認は **content 課経由** (旧 LP peer は非存在)。findings 自体は有効・owner ラベルのみ訂正。

---

## サマリ (4 検出項目)

| 項目 | 結果 |
|------|------|
| ③ 残登録 (lock に有るが実体無し) | **なし** (template lock 47 = 実体 47・1:1) |
| ① 未登録 (canonical 外の realdir skill) | 多数だが**大半は正当な課固有 skill**。要注意 3 件のみ (下記 F4) |
| ② hash drift | **SNS 2件 + LP 4件 + lock 未更新 2件** (下記 F1/F2/F3) |
| ④ 課間重複 | 健全 distribute 2件 + **divergent 6件** (下記 F1/F2/F4) |
| broken symlink / 構造異常 | broken symlink **なし**。chief/product は `.claude/skills` 未設置 (F5) |

**要対応 finding = 5 件 (F1〜F5)**。いずれも**修正は各 peer / conductor 側** (CCO は cross-repo write 不可・所有ガード)。CCO は機械検出のみ。

---

## Findings

### F1. peer-id-lookup / tier-judge — lock 未更新 + SNS 未同期 (② + ④)
- **peer-id-lookup**: template master + 12 peer = `bbd30e17` (現行) だが **skills-lock.json = `3368e437` (旧・再lock されず)**、かつ **SNS のみ `3368e437` (旧のまま = 再配布を取りこぼし)**。
- **tier-judge**: template + 大半 peer = `dd339bd2`、**SNS のみ `a3e75eab` (divergent)**。
- 解釈: 両 skill は編集・再配布されたが (a) `skills-lock.json` の再lock 漏れ (b) **SNS が配布を取りこぼし** (SNS=threads-api は marker 無・from_id silent-partition の常連課、既知パターンと一致)。
- 対応: (a) 意図確認後 `audit-skills-lock.sh --update --confirm` で再lock (CCO 可・template 内) (b) SNS へ再配布 = conductor dispatch。
- ★intent verify 済 (2026-07-02): template on-disk `peer-id-lookup` = **意図的 commit の結果** (#88 "sync mapping table from conductor PR #294"・未commit 変更なし) → **再lock 安全** (lock が意図的編集に lag しているだけ)。`tier-judge` は template では lock と一致 (dd339bd2) = drift なし → template 再lock 不要、SNS のみ再同期対象。conductor workspace の tier-judge 未commit 変更は conductor-local ゆえ conductor が commit/discard 判断。**推奨 sequencing = 再lock (現行版へ) と SNS 再配布を同時に** (旧版で lock しない)。

### F2. LP — 共有 skill 4件の divergent copy (②)
- LP (glasswerks-lp) は **全 realdir (symlink ゼロ)**。共有 skill を**コピー保持**しており `copywriting` `lp-optimizer` `remotion` `seo-audit` の 4件が canonical から drift。
- ★**audit-peer-drift.sh では不可視** (同 script は共通4 skill しか見ない)。今回の全 skill enumeration で初検出。
- 対応: ローカル編集か旧コピーかを **content 課** (glasswerks-lp 所有・旧 LP 統合先) で intent 確認 → canonical へ戻すか、意図的差分なら canonical 側へ反映。conductor→content dispatch。

### F3. common-claude-md-blocks — lock drift (② 想定内)
- template の `common-claude-md-blocks` が lock と drift = block 編集で想定内 (既知)。意図確認後 `--update --confirm` で再lock (CCO 可)。
- ★intent verify 済 (2026-07-02): 現行 on-disk = **意図的 commit の結果** (#112 block15 等・未commit 変更なし) → **再lock 安全**。

### F4. 同名 divergent 重複 + renamed fork (① + ④)
- **note-article-post**: `SNS` と `conductor` に**別内容の同名 skill** (distinct-hash=2)。同名衝突 → 参照混乱リスク。命名 disambiguate or 統合を要検討。
- **LP `ui-ux-pro-max-skill` / `ux-psychology-skill`**: canonical `ui-ux-pro-max` / `ux-psychology` の **"-skill" 付き rename ローカル fork**。stale fork の疑い → LP課で現行性確認 (canonical を symlink 参照に寄せるか、意図的 fork なら明記)。

### F5. 構造 (③関連)
- **broken symlink = ゼロ** (全 workspace)。
- **chief / product = `.claude/skills` 未設置** (新設 peer・skill 未配布)。意図的なら OK、共通 skill を効かせたいなら setup/distribute 要 → Chief/conductor 判断。

---

## 健全な点 (対応不要)

- **③ 残登録 = ゼロ** (template lock/実体 1:1)。
- **pwa-dashboard (14 copy) / plan-mode-policy (14 copy) = 全 hash 一致** = distribute 健全。
- ① の大半 = 正当な**課固有 skill** (conductor の checkin/checkout/dispatch/patrol 等、data/freee/mued/native/reserch/SNS の課ops skill、reserch aristotle-first-principles 等) = canonical 外で正しい。
- broken symlink ゼロ。

---

## ★ツール側 finding (機械検出の盲点 = 恒久化候補)

今回「既存 script のみでは 4 項目を全カバーできない」ことが判明。今後の org-wide 定期監査には下記が要る (別途 conductor 判断・本 dispatch は検出のみ):

1. **`audit-peer-drift.sh` の COMMON_SKILLS が stale** — `{peer-id-lookup, tier-judge, plan-mode-policy}` のみで **pwa-dashboard (6/13 配布追加) を含まない** + SHARED_SKILLS の peer コピー (LP の drift 等) を**一切見ない**。→ F2 は同 script では永久に不可視だった。
2. **`audit-skills-lock.sh` は残登録 (stale lock) を検出しない** — 実体 dir を iterate するため lock 側の孤児 entry を拾えない (今回 0 ゆえ顕在化せず)。
3. 全 workspace の**全 skill** を canonical と hash 突合する機構が存在しない (今回は ad-hoc enumeration で代替)。

→ これらは Fable 不在後の再発防止機構 (brief #5) の入力として有用。

---

## 数値 (per-workspace skill 数: total / realdir / symlink)

template 47/42/5・conductor 15/14/1・write 21/5/16・cowork 16/5/11・data 25/9/16・LP 15/15/0・reserch 11/11/0・freee 21/7/14・growth 42/4/38・blender 4/4/0・mued 31/15/16・native 11/10/1・SNS 14/14/0・dsp 5/4/1。chief/product = `.claude/skills` 無。
(realdir 多 = コピー保持 = drift しやすい / symlink 多 = canonical 参照 = 同期維持。LP/reserch/SNS/blender は all-realdir ゆえ drift 監視要。)
