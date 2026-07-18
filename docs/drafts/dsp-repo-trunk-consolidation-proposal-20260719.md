# Proposal — `mued-dsp` repo trunk 統合 (統合 trunk 不在の解消)

- **起案 / owner**: template課 / CCO
- **依頼元**: conductor (2026-07-18/19)。banner Tier2 review 中に CCO が発見した repo-hygiene finding を CCO owner で proposal 化。
- **扱い (conductor 裁定 2026-07-19)**: **CCO+conductor の技術 conformance**。kimny 戦略 gate では**ない** (価格/認証/DBスキーマ破壊/本番設定/外部サービス/組織/policy 免除のどれにも非該当)。kimny には **FYI awareness のみ**。3案いずれも Branch Protection Policy の「保護 trunk」意図への conformance であって policy 免除ではない。
- **escalation caveat**: 移行手順に (a) shipped plugin / 本番 download への実リスク、または (b) fleet Branch Protection Policy 本体の改訂 (全 dsp 系波及) が出たら、その時点で kimny gate 化。→ 本 proposal は両方に**該当しない** (§5 参照) ので CCO+conductor で確定可。
- **status**: ✅ 完成 (dsp Q1-Q3 回答反映済・§9) → conductor 技術 go 待ち。残 open = 統合 branch naming の最終確定 (CCO 推奨 `develop`・conductor 確認)。

---

## 0. TL;DR / 推奨

- **問題**: `mued-dsp` は **plugin product source が per-plugin feat branch にしか無く、統合 trunk が不在**。無料2種 (MUEDlim/MUEDsat) が同居する branch がゼロ。`main` は停止した docs fork (release から分岐・65 commit stale)。→ **IP-loss リスク** (feat branch 消滅 = product source 消失) + reviewable trunk 不在 + fleet Branch Protection Policy との乖離。
- **Phase 1 (即時・conductor greenlight 済)**: **統合 branch を確立**し全 plugin source を集約。★**丸 branch merge でなく subdir graft** で行う (feat を丸 merge すると release の新しい MUEDsp core を退行させるため)。**加算的・history 書換なし・feat branch 残置ゆえ現 shipped-build path 不変・可逆**。★ship path は各 plugin 自己完結の **Xcode project** で subdir 内に閉じる (top-level CMake 非依存) ため、subdir graft だけで ship 経路ごと移動する (dsp Q1 確認)。
- **Phase 2 (長期・CCO 推奨)**: **2-(ii) = 統合 branch を正式 protected trunk と宣言 + default branch rename、`main` は docs salvage 後 retire**。2-(i) main reconcile は分岐が大きく無益ゆえ非推奨。
- **CI 破壊リスク低**: workflows は ref-agnostic (`branches:[main]` 固定 filter 無し) を実査確認。

---

## 1. Finding (git 実査・CCO 直接調査 + dsp supply cross-check = 一致)

### 1-1. plugin product source の所在 (source home)

| plugin | 所在 branch | trunk (main/release) に有? |
|---|---|---|
| **MUEDsp** (flagship 有料) | **全 branch 共通** | ✅ 有 (共通 core) |
| **MUEDlim** (無料) | **`feat/muedlim-productize` 単独** | ❌ 無 |
| **MUEDsat** (無料) | **`feat/muedsat-ui-D` 単独** | ❌ 無 |
| MuedSteel (MUEDsat 旧名) | main + muedlim-productize + sign-orchestrator | main のみ (stale) |

- ★**両無料 plugin が同居する branch はゼロ** → どの単一 branch からも無料2種を同時 build できない。
- `plugin/` は iPlug2 プロジェクト全体 (CMake / iPlug2 submodule / build config は全 branch 共通)。各 feat branch は**自身の plugin については独立 build 可**。

### 1-2. branch 台帳 (commits ahead of `main`)

| branch | ahead | 内容 |
|---|---|---|
| `release/0.1.1-alpha` | +66 | MUEDsp のみ (最新 core)・de-facto release 準備 branch |
| `feat/muedsat-ui-D` | +23 | MUEDsat + MUEDsp |
| `feat/muedlim-productize` | +17 | MUEDlim + MUEDsp + MuedSteel |
| `feat/sign-package-orchestrator` | +2 | MUEDsp + MuedSteel (sign 手順) |

- `main` ↔ `release`: **分岐** (release は main から +66 ahead、main は release から +6 ahead = 互いに相手に無い commit を持つ非 linear)。`main` = docs 主体で **2026-07-10 停止**。
- 両 feat の merge-base = `dec2b93` (#200・dist gitignore hardening)。muedlim +17 / muedsat +23。

### 1-3. ★共通 core (MUEDsp) の branch 間差分 = 退行リスク源

`release/0.1.1-alpha` の MUEDsp は feat 2 branch より**新しい**:
- `plugin/MUEDsp/scripts/makepkg-mac.sh` (+70 行差)
- `plugin/MUEDsp/tests/test_glue_compressor.cpp` (差分)

→ **feat branch を丸ごと merge すると release の新しい MUEDsp を退行させる** ([[feedback_merge_target_duplication_check]] の典型)。移行手法の設計上の肝 (§6)。

### 1-4. CI / build tooling 所在 (dsp Q1/Q2 回答で確定)

- ★**ship path は各 plugin 自己完結の Xcode project** (`MUEDlim-macOS.xcodeproj` の scheme `macOS-VST3`/`macOS-AUv2`/`macOS-AAX`)。`makedist-mac.sh` が xcconfig の *_PATH から拾い → PACE wraptool codesign → `sign-and-package.sh` orchestrator で notarize/pkg。**top-level CMake 非依存**。→ **plugin subdir を graft すれば ship 用 Xcode scheme がそのまま効く** (統合に top-level CMake 登録は ship には不要)。
- `plugin/CMakeLists.txt` (top-level) は `add_subdirectory(MUEDsp)` + `add_subdirectory(MuedSteel)` のみ = **MUEDlim/MUEDsat は未登録**。各 plugin は自前 `CMakeLists.txt` (standalone `iplug_add_plugin`) を持ち個別 invoke。CMake build は **APP + MINIMAL_PLUGINS の dev/verify 用** (render-verify もこれ)。→ top-level から両 free を CMake で一括 build したい場合のみ `add_subdirectory` 追加 (dev-convenience・ship 非必須)。
- packaging = `plugin/MUEDsp/scripts/makepkg-mac.sh` (全 branch)。`sign-and-package.sh` は `feat/sign-package-orchestrator` 側で未統合 (統合時に併せて集約検討)。
- workflows (`plugin/.github/workflows/*`, `.github/workflows/ctest-unit-tests.yml`): **ref-agnostic** = `branches:[main]` 固定 filter **無し**・concurrency は `${{github.ref}}`・`release-native.yml` は tag driven。→ default branch rename の CI 破壊リスク低。

---

## 2. 3案 技術比較

| | (A) 統合 branch 確立 | (B) main reconcile | (C) release 系を protected trunk 宣言 |
|---|---|---|---|
| 概要 | 全 plugin source を1 branch に集約 | release→main を戻し main を trunk 化 | 統合 branch を default/protected trunk にし main retire |
| IP-loss 即時解消 | ✅ | △ (reconcile 完了まで開いたまま) | ✅ (A の上に成立) |
| history 書換/force-push | 不要 (加算 merge/graft) | main が分岐ゆえ conflict 大・場合により rebase | 不要 (rename のみ) |
| shipped-build path | 不変 (feat 残置) | 不変 | 不変 |
| fleet policy 適合 | 部分 (trunk 確立) | ✅ (main=trunk 復帰) | ✅ (実態を trunk 宣言) |
| コスト | 低 | 高 (66 commit 分の conflict 解消) | 低 (A + GitHub 設定変更) |
| 無益さ | — | ★高 (誰も main から build しない・stale docs fork に product を押し戻す) | — |

**関係整理**: (A) は即時安全化 (Phase 1)。(B)/(C) は長期 trunk model の二択 (Phase 2) で、(C) は (A) の統合 branch をそのまま trunk 昇格する自然な延長。

### CCO 推奨

- **Phase 1 = (A)** を即実施 (conductor greenlight 済)。
- **Phase 2 = (C)** を推奨。**(B) は非推奨** — main↔release が分岐しており、停止した docs fork に product 66 commit を押し戻すのは大規模 conflict の割に得るものが無い (誰も main から build しない)。実態 (release 系が真の trunk) を宣言する (C) が最小コストで policy 意図に適合。main の unique docs は §6 で salvage。

---

## 3. なぜ (C) か (default branch rename の妥当性)

- `main` は「保護された trunk」の実質を**既に失っている** (docs 停止 fork・product .cpp 不在)。名ばかり main を残すと「main から clone/build すると plugin が無い」誤解を再生産する。
- **CI 破壊リスク低** (§1-4): workflows に `main` 固定 filter 無しを実査確認。default branch 変更で壊れる hardcoded 依存が薄い。→ ただし実行時に `grep -rn "branches:" .github plugin/.github` と `grep -rn "github.event.schedule\|'main'\|\"main\"" .github plugin/.github` の **final scan を手順に含める** (CLAUDE.md の GitHub Actions branch/schedule filter gotcha discipline)。
- GitHub default branch rename の影響範囲 = (a) PR base 既定 (b) branch protection ルールの移設 (c) open PR の re-target (d) clone HEAD。いずれも一度きりの設定変更で、既存 shipped artifact には無影響。

---

## 4. 3案の選定根拠まとめ

- (A) 即時・非破壊・低リスク → Phase 1 で確定。
- (C) 実態宣言・低コスト・policy 適合 → Phase 2 推奨。
- (B) 高コスト・無益 → reject。

---

## 5. ★移行リスク評価 (conductor 依頼#2)

| リスク | 評価 | 根拠 |
|---|---|---|
| shipped build path 破壊 | **無** | 移行は加算 (graft + 新 branch)。feat branch は残置 → 現 build+notarize+ship は移行中も不変。★ship path (各 plugin 自己完結 Xcode project) は **subdir 内に閉じる**ゆえ subdir graft で ship 経路ごと移動 (top-level CMake 非依存・dsp Q1)。統合 branch が build+ship 実証されるまで feat を退役させない。 |
| force-push / history 書換 | **不要** | subdir graft + merge commit のみ。rename も履歴不変。 |
| MUEDsp core 退行 | **回避可** | ★丸 merge を避け subdir graft (MUEDsp は release 版維持)。§6 手順で担保 + build-verify。 |
| CI 破壊 (rename) | **低** | workflows ref-agnostic。final grep を手順化。 |
| 可逆性 | **完全** | 統合 branch 削除 / default branch を main に戻すだけで復元。feat branch 温存ゆえ source loss 無し。 |
| **escalation caveat (a) 本番 download 実リスク** | **非該当** | download 対象は既存 shipped artifact (feat build 由来)。本 proposal はそれを変えない。 |
| **escalation caveat (b) fleet policy 改訂** | **非該当** | 本件は dsp repo を既存 fleet policy に**適合させる** conformance。policy 本体は改訂しない。 |

→ **両 escalation caveat に非該当** = CCO+conductor で確定可。kimny は FYI awareness のみ。

---

## 6. 移行手順 (conductor 依頼#1・誰が/何を/可逆性/検証)

**実行主体 = dsp課** (自 repo・自 process。CCO は cross-repo write せず設計と検証観点を供給 — 所有境界尊重 [[project_ownership_write_guard_20260611]])。CCO は review。

### Phase 1 — 統合 branch 確立 (即時・IP-loss 窓を閉じる)

1. **base 選定 = `release/0.1.1-alpha`** (最新 MUEDsp core + docs・dsp も推奨)。統合 branch 名 = **CCO 推奨: release から新 `develop` を切り trunk にする** (下記理由)。dsp は「base=release の内容」が要件で naming は従う。
   - *naming 理由*: `release/0.1.1-alpha` を default/trunk に昇格すると「version 名 branch が trunk」= 次版 0.1.2 で trunk 名を変える羽目になり semantically 混乱。**安定名 `develop` (or `trunk`) を release 内容から切り default 化**すれば trunk 名が版に依存しない。最小コスト志向なら release 昇格も可 — conductor 確認事項。
2. **MUEDlim graft** (丸 merge しない):
   - `feat/muedlim-productize` から **`plugin/MUEDlim/` subdir のみ**を統合 branch へ持ち込む (`git checkout feat/muedlim-productize -- plugin/MUEDlim` 相当)。★**ship path (Xcode project) はこの subdir 内に自己完結**ゆえ graft だけで ship 用 scheme が揃う (dsp Q1)。
   - MUEDsp は**触らない** (release 版維持)。
   - (任意・dev-convenience) top-level から両 free を CMake 一括 build したいなら `plugin/CMakeLists.txt` に `add_subdirectory(MUEDlim)` 追加。**ship (Xcode) には不要** (dsp Q2 = 現状 top-level 未登録・各 plugin standalone CMake)。
3. **MUEDsat graft**: 同様に `plugin/MUEDsat/` subdir (ship = 自前 Xcode project)。CMake 一括 build 希望時のみ `add_subdirectory(MUEDsat)`。
4. **build-verify (必須・2 面)**:
   - (a) **ship path**: 各 plugin の Xcode scheme (`macOS-VST3`/`AUv2`/`AAX`) を統合 branch 上で build → 既存 shipped と同等を確認。
   - (b) **dev/verify**: CMake APP build + 既存 render-verify 再走。
   - 特に **feat の plugin が release の新しい MUEDsp core (共通 DSP) に依存して壊れないか**を確認 (API 差あれば reconcile)。
5. **可逆性**: この時点で feat branch は無傷。問題あれば統合 branch を捨てて元に戻る。

### Phase 2 — trunk 宣言 (long-term・(C))

6. **main の unique docs を salvage**: `release..main` の main-unique commit (gap#10 limiter 診断/決定 ~3 commit: `f732db3`/`a599e46`/`8ba067c` 等) を統合 branch へ cherry-pick (docs のみ・conflict 小)。
7. **final CI grep**: `grep -rn "branches:" .github plugin/.github/workflows` + `grep -rn "github.event.schedule\|\bmain\b" .github plugin/.github/workflows` で `main` 固定依存が無いことを再確認 (§3)。ヒットあれば統合 branch 名へ更新。
8. **GitHub default branch を統合 branch に変更** + branch protection ルールを移設 (main→統合)。
9. ★**rename 実効 verify (conductor 依頼)**: default 変更後に **CI を 1 回実走** (統合 branch への push か workflow_dispatch) し **緑を確認** — rename が CI trigger を壊していないことを実証してから次へ進む。
10. **`main` retire**: docs salvage 後、main を archive tag (`archive/main-pre-consolidation`) で残し branch は非保護化 (削除は任意・履歴保全のため tag 推奨)。
11. **feat branch 退役**: 統合 branch が build+ship 実証後、`feat/muedlim-productize`/`feat/muedsat-ui-D` を archive tag 化 (source は統合 branch にあるため安全)。
12. **最終検証**: 統合 branch から (a) 全 plugin build (b) notarize (c) MUEDsat DL manifest 突合 (既存 shipped と同一性) → clean で完了。

### Tier / review

- Phase 1 graft = **Tier 2** (dsp 自 repo・build 影響あり CCO peer-review)。
- Phase 2 default-branch rename + protection 移設 = dsp 実行・**CCO+conductor 確認** (本番設定 GitHub secrets には非該当ゆえ Tier3 kimny gate 不要 — conductor 裁定準拠)。

---

## 7. kimny FYI (awareness・adjudication させない)

conductor が proposal 確定後に **1 FYI** で渡す想定 (文案):
> dsp repo の無料 plugin source が feat branch のみに存在して脆弱だった (branch 消滅 = source 消失リスク)。統合 trunk に集約して安全化し、以後は単一 trunk から全 plugin を build する。中長期は release 系を正式 trunk に。**判断は不要・awareness のみ**。

---

## 8. escalation 監視 (proposal 内で継続チェック)

移行実行中に次が出たら kimny gate 化:
- (a) 統合が現 shipped MUEDsat/MUEDlim の DL artifact / 本番 download を変える兆候 → 現状**非該当** (§5)。
- (b) この trunk model 標準を全 dsp 系 (将来の他 plugin repo 等) へ波及させ、fleet Branch Protection Policy 本体を改訂する話に発展 → その時点で fleet 波及ゆえ kimny gate。**本 proposal は dsp repo 単体の conformance に限定**。

---

## 9. dsp 確認事項 (✅ 回答済 2026-07-19・手順に反映済)

- **Q1 → ✅**: ship = 各 plugin 自己完結の **Xcode project** (scheme `macOS-VST3/AUv2/AAX`) + `makedist-mac.sh` + PACE wraptool + `sign-and-package.sh`。**top-level CMake 非依存**。CMake は APP+MINIMAL_PLUGINS の dev/verify 用。→ subdir graft で ship 経路ごと移動 (§1-4, §6-2)。
- **Q2 → ✅**: MUEDlim/MUEDsat は top-level `plugin/CMakeLists.txt` に**未登録** (各 plugin standalone CMake)。→ ship に CMake 登録不要・top-level 一括 CMake build 希望時のみ `add_subdirectory` 追加 (§6-2 任意)。
- **Q3 → ✅**: dsp 推奨 base = `release/0.1.1-alpha`。naming は CCO+conductor へ委任。→ **CCO 推奨 = release から新 `develop` を trunk 化** (version 名 branch を trunk にしない・§6-1)。最小コスト志向なら release 昇格も可 = conductor 確認事項。

---

## 10. 参照

- banner review (本 finding の発見元): status.md 2026-07-19 / PR#160
- fleet Branch Protection Policy: 経営部 CLAUDE.md
- 退行回避原則: [[feedback_merge_target_duplication_check]]
- 所有境界 (CCO は cross-repo write せず): [[project_ownership_write_guard_20260611]]
- GitHub Actions branch/schedule filter gotcha: CLAUDE.md Gotchas
