# distribute-quality-standards.sh DIVISIONS 拡張 設計draft (2026-05-12)

- [x] kimny確認 — 2026-05-26 10:40 JST Q5 (a) ii-a hybrid 採用 GO (trilateral 議論 5 件 batch、 全 conductor 推奨)
- [x] conductor承認 (Tier 3) — 2026-05-12 14:04 JST (A) CCO推奨 ii-a hybrid + 長期(iv) Managed-region marker Phase 2 queue GO
- 実装 PR: `feat/distribute-divisions-extend-occur` (2026-05-26、 occur 既 `feedback_occur_brand_overlay.md` migration 完納確認済、 本 PR は DIVISIONS extend + canonical universal 4 項目反映のみ)

## 1. 背景

2026-05-12 PR #61 (軸1B 65-75% → 50-60% canonical整合) merge後 distribute本実行で 11 peers全UPDATE完納。検証時に以下の構造的問題を発見:

- **cowork** (htctp8z2、 dir `-Users-kimny-Dropbox--DevProjects--cowork`、 2026-05-12 朝新規作成)
- **occur** (57pn53wo、 dir `-Users-kimny-Dropbox--DevProjects--mued-occur`、 2026-05-12 朝新規作成)

両peer の memory dir には `feedback_kimny_quality_standards.md` が既に配置 (5/12朝作成時点で canonical 50-60% 正本値保有)。ただし `scripts/distribute-quality-standards.sh` の DIVISIONS list (11課) に未登録のため、 distribute実行で **構造的にuntouched** = 上書きconflictは回避できたが、 次回 canonical update batch時に両peerが broadcast対象から外れて drift復活リスクが残る。

## 2. 目的

`distribute-quality-standards.sh` の DIVISIONS list に cowork + occur を追加し、 次回以降の canonical broadcast を全13課に届ける。但し occur 既存memoryには peer-specific 拡張が複数含まれており、 そのまま canonical で上書きすると重要な peer文脈が失われる。 trade-offを設計判断する。

## 3. 変更内容 (DIVISIONS extend のみ、 本draft時点で working tree差分)

```diff
-# 全11課: 課名|プロジェクトディレクトリ名
+# 全13課: 課名|プロジェクトディレクトリ名
 DIVISIONS="
 ...
 reserch|-Users-kimny-Dropbox--DevProjects--Reserch
+cowork|-Users-kimny-Dropbox--DevProjects--cowork
+occur|-Users-kimny-Dropbox--DevProjects--mued-occur
 "
```

## 4. dry-run 出力 (13 peers全 [UPDATE])

```
=== kimny判断基準メモリパック配布 ===

  [UPDATE] conductor課 ... (中略 11課) ...
  [UPDATE] cowork課: feedback_kimny_quality_standards.md を上書き
           MEMORY.md エントリ済み
  [UPDATE] occur課: feedback_kimny_quality_standards.md を上書き
           MEMORY.md エントリ済み

==========================================
配布完了
==========================================
```

cowork / occur 両peer に既存ファイル + MEMORY.md entry あり → 全 [UPDATE]、 [CREATE] なし。

## 5. occur 既存memory の peer-specific 拡張 (上書き影響範囲)

`diff cowork/feedback_kimny_quality_standards.md occur/feedback_kimny_quality_standards.md` で確認した occur追加分:

| 種別 | 場所 | 内容 | 性質 |
|------|------|------|------|
| frontmatter | name | `kimny` (短縮) vs canonical 「kimny判断基準 — 全課共通クオリティスタンダード」 | peer-side stylistic |
| frontmatter | description | canonical + 「価格管理policy v2/」 を追記 | universal可 |
| frontmatter | metadata構造 | `metadata: node_type: memory / type: feedback / originSessionId: ...` ネスト | peer-side stylistic |
| 本文lead | 1段落 | 「occur peer は本memoryの『ブランド設計指針』section…で更にoccur固有convention(「リアル/美しい/豊か」禁止、「補う/起こる」優先)を上書き整合させて運用する」 | **peer-specific** (occur固有 brand) |
| サイト section | bullet追加 | 「MUEDoccur = 独立brand (MUEDial / MUEDノートとは別ライン、`_docs/MUEDoccur_brief.md` §9.3)」 | **peer-specific** (occur固有 brand) |
| マネタイズ section | 軸1B行末 | 「+ canonical参照 [[reference_pricing_canonicals_v2]] (本peer未配置時 conductor版直接参照)」 | universal可 |
| 運用 section | 3行に peer-link付与 | `[[feedback_peer_session_continuity]]` / `[[feedback_zero_kimny_manual_work]]` / `[[feedback_mass_production_default]]` | universal可 |
| Why | 拡張 | 「canonical 4件 (`reference_pricing_canonicals_v2.md`) #4 の対象peer群と整合させ、 価格・原価率・業態定義の peer間齟齬を防ぐ」 | universal可 |
| How to apply | 拡張 | 「occur固有のbrand convention ([[reference_brand_language_convention]]) は本基準と並列で同時適用 (上書きではなく上塗り重ね)」 | **peer-specific** |

→ **universal可 5項目** (canonical化候補) + **peer-specific 3項目** (occur固有、 canonical不適切)。

## 6. Trade-off 3案比較

### 案 (i) canonical wins (シンプル、 occur peer-specific 消失)

- 動作: distribute-quality-standards.sh 現状ロジックで 13 peer broadcast、 occur既存 peer-specific 3項目消失
- ✅ メリット: 実装変更ゼロ (DIVISIONS追加のみ)、 全peer完全整合
- ❌ デメリット: occur独立brand宣言・brand overlay説明 (重要なpeer文脈) 消失 = occur peer での content生成時に重大な情報欠落risk
- 判定: **不採用**

### 案 (ii) canonical text に occur追記 反映 (conductor推奨方向)

- 動作: canonical HEREDOC に occur追加分を取り込み、 全13peerに broadcast
- 細分化:
  - **(ii-a) universal可 5項目のみ canonical化**: マネタイズ行末 `[[reference_pricing_canonicals_v2]]` 参照、 運用 peer-link 3件、 Why拡張、 How to apply一部、 description拡張
    - ✅ canonical全体 elevation、 全peerが canonical 4件参照可能化
    - ❌ peer-specific 3項目 (occur独立brand宣言 / occur brand overlay文 / lead段落 occur説明) はoccur側だけ別管理必要 → canonical broadcast後に occurで手動 patchが必要
  - **(ii-b) peer-specific 3項目もcanonical化**: 全peerに occur固有 contextを broadcast
    - ❌ canonical neutrality 破壊 (canonical = peer-neutral の原則違反、 他peer (mued / native等) のcontentで MUEDoccur独立brand宣言が読まれる)
    - 判定: **不採用**
- (ii-a) 判定: **採用 候補** (occur側 patch + 後追い修正必要 = 二段階作業)

### 案 (iii) occur opt-out (DIVISIONS に occur含めず cowork のみ追加)

- 動作: DIVISIONS追加は cowork のみ (12 peers broadcast)、 occur は手動 sync維持
- ✅ メリット: occur peer-specific 3項目 完全保護
- ❌ デメリット: occur側 canonical drift復活 risk (5/12朝作成時点で正本値保有 = 偶然の整合、 次回 canonical update batch時に手動 sync漏れ可能性)、 「DIVISIONS = canonical broadcast対象 全peer」 原則の崩壊
- 判定: **保留** (4案-(iv) が prefer)

### 案 (iv) Managed-region marker導入 (より構造的解決)

- 動作: canonical broadcast対象を 「`<!-- canonical-start -->` 〜 `<!-- canonical-end -->`」 で囲み、 そのregion外の peer追記は保持
- 実装: distribute-quality-standards.sh を sed/awk patch logicに改修 (現行 `echo > target_file` 全置換 → marker内部のみ置換)
- ✅ メリット: 全peer canonical整合 + peer-specific 拡張保持の両立、 occur 以外のpeer (cowork) も将来peer-side 拡張 OK
- ❌ デメリット: scriptロジック改修 (Tier 3、 既存全peerの memory に marker挿入 migration必要)、 implementation cost中
- 判定: **長期推奨** (本PRでは scope外、 Phase 2 改善 task として queue 提案)

## 7. CCO 推奨案

**短期 (本PR): 案 (ii-a) + 案 (iii) hybrid**:

- DIVISIONS に cowork + occur 追加
- canonical HEREDOC に **universal可 5項目のみ** 取り込み (description拡張、 マネタイズ末 canonical参照、 運用 peer-link 3件、 Why拡張、 How to apply 一部)
- distribute実行 **前** に occur側 peer-specific 3項目を別memory (e.g. `feedback_occur_brand_overlay.md`) へ分離 migration、 broadcast後の patch回避
- frontmatter差分 (name短縮、 metadata ネスト構造) は canonical標準形 へ統一 (occur側譲歩)

**長期 (別PR、 Phase 2 改善 queue)**: 案 (iv) Managed-region marker 導入で peer-specific extension を構造的に保護。

## 8. Tier判定 + PR起案 timing

- **Tier 3**: 全課波及 (canonical text変更 + distribute対象拡張)、 conductor approve必須
- 起案 timing: **5/14- launch後 catch-up枠** (5/13 launch GREEN優先、 5/12中はdraft + dry-run まで、 5/14-5/20内完納目標、 次回canonical update batch前)
- 事前作業: occur側 peer-specific 3項目の `feedback_occur_brand_overlay.md` 分離 migration (occur peer dispatchで 5/14- 着手)

## 9. Rollback 手順

DIVISIONS extend後の不具合発覚時:

1. `scripts/distribute-quality-standards.sh` を `git revert` (DIVISIONS list を 11課に戻す)
2. cowork / occur 側 `feedback_kimny_quality_standards.md` は touchedされた直近 canonical で上書き済 = 元のpeer-specific 拡張は git管理外のため復元不可。 occur側は **migration済 `feedback_occur_brand_overlay.md`** から peer文脈は保持される設計
3. 全課 audit: 次回 canonical update batch時に整合再確認

## 10. 5/12中の本draft完納状態

- [x] DIVISIONS extend (working tree差分、 未commit)
- [x] `--dry-run` 13peer [UPDATE] 確認
- [x] occur custom diff capture (項8項目分類)
- [x] 設計draft 起案 (本file)
- [x] working tree revert (PR起案保留のため、 draft完納後 revert完了)
- [x] conductor報告 (本draft URL + dry-run結果、 5/12 14:09 JST)
- [x] conductor承認 (A) ii-a hybrid GO (5/12 14:04 JST)
- [x] occur peer (57pn53wo) 事前作業 dispatch (5/12 14:08 JST)
- [x] occur peer 事前作業完納 (5/12 14:25 JST、 grep verification PASS、 universal可4件 残存OK)
- [ ] PR起案 (5/14-5/20内、 conductor指示時、 5/13 launch GREEN後)

## 11. 参照

- PR #61 軸1B 65-75% → 50-60% canonical整合 (2026-05-12 merge)
- conductor指示 2026-05-12 13:39 JST / 13:44 JST / 13:55 JST (claude-peers)
- canonical memory `feedback_kimny_quality_standards.md` (5/10 19:35 JST CCO完納)
- conductor memory `project_pricing_policy_v2_20260508.md` / `reference_pricing_canonicals_v2.md`
- occur memory `reference_brand_language_convention.md` (occur固有 brand convention)
