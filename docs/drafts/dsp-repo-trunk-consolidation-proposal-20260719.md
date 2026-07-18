# Proposal — `mued-dsp` repo trunk 統合 (統合 trunk 不在の解消)

- **起案 / owner**: template課 / CCO
- **依頼元**: conductor (2026-07-18/19)。banner Tier2 review 中に CCO が発見した repo-hygiene finding を CCO owner で proposal 化。
- **扱い (conductor 裁定 2026-07-19)**: **CCO+conductor の技術 conformance**。kimny 戦略 gate では**ない** (価格/認証/DBスキーマ破壊/本番設定/外部サービス/組織/policy 免除のどれにも非該当)。kimny には **FYI awareness のみ**。3案いずれも Branch Protection Policy の「保護 trunk」意図への conformance であって policy 免除ではない。
- **escalation caveat**: 移行手順に (a) shipped plugin / 本番 download への実リスク、または (b) fleet Branch Protection Policy 本体の改訂 (全 dsp 系波及) が出たら、その時点で kimny gate 化。→ 本 proposal は両方に**該当しない** (§5 参照) ので CCO+conductor で確定可。
- **status**: ✅ **conductor 技術 GO 受領 (2026-07-19)**。naming 裁定 = **`main`** (fleet 一貫性・§6-1)。free plugin hermetic 実査で MUEDsp 退行リスク消滅 (§1-3b)。rename mechanical 裏取り済 (§3-2)。→ **Phase 1 を dsp へ実行 dispatch する段階** (CCO 設計 handoff + Tier2 review)。

---

## 0. TL;DR / 推奨

- **問題**: `mued-dsp` は **plugin product source が per-plugin feat branch にしか無く、統合 trunk が不在**。無料2種 (MUEDlim/MUEDsat) が同居する branch がゼロ。`main` は停止した docs fork (release から分岐・65 commit stale)。→ **IP-loss リスク** (feat branch 消滅 = product source 消失) + reviewable trunk 不在 + fleet Branch Protection Policy との乖離。
- **Phase 1 (即時・conductor greenlight 済)**: **統合 branch を確立**し全 plugin source を集約。★**丸 branch merge でなく subdir graft** で行う (feat を丸 merge すると release の新しい MUEDsp core を退行させるため)。**加算的・history 書換なし・feat branch 残置ゆえ現 shipped-build path 不変・可逆**。★ship path は各 plugin 自己完結の **Xcode project** で subdir 内に閉じる (top-level CMake 非依存) ため、subdir graft だけで ship 経路ごと移動する (dsp Q1 確認)。
- **Phase 2 (長期・CCO 推奨)**: **2-(ii) = 統合 branch を正式 protected trunk と宣言**。旧 `main` は docs salvage 後 archive、**統合 branch を `main` に rename** (conductor 裁定 naming=`main`・fleet 一貫)。2-(i) main reconcile は分岐が大きく無益ゆえ非推奨。全 ref 操作・history 不変。
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

### 1-3. 共通 core (MUEDsp) の branch 間差分 — 丸 merge なら退行源 / subdir graft なら無関係

`release/0.1.1-alpha` の MUEDsp は feat 2 branch より**新しい** (`plugin/MUEDsp/scripts/makepkg-mac.sh` +70・`tests/test_glue_compressor.cpp` 差分)。
→ もし **feat branch を丸ごと merge**すれば release の新しい MUEDsp を退行させる ([[feedback_merge_target_duplication_check]])。**丸 merge を避ける根拠**。ただし採用手法 (subdir graft) では plugin/MUEDsp を触らない (release 版維持) ゆえ、この差分は graft に**無関係**になる。

### 1-3b. ★free plugin は hermetic = MUEDsp 依存ゼロ (CCO 実査確認・退行リスク構造的に消滅)

dsp supply → **CCO 実査で確認**: MUEDlim/MUEDsat は **完全自己完結**で `plugin/MUEDsp/` を一切参照しない:
- **MUEDlim**: 自前 `plugin/MUEDlim/dsp/` に muedsp:: core の**コピー10本** (BodyLimiter/BoxcarCascade/EnvelopeFollower/GRReleaseShaper/ISPPeakDetector/LookaheadBuffer/LoudnessMeter/PreLimiterClipper/RunningMinHold/TPLimiter)。
- **MUEDsat**: 自前 `plugin/MUEDsat/dsp/Saturator.h`。
- `git grep` で両 plugin の source/build から `plugin/MUEDsp`・`../MUEDsp` 参照 = **ゼロ** (実査済)。
- これは Chief 北極星#1「DSP surface-independence (header-only muedsp:: を surface 毎コピー)」の帰結 = **設計上 shared linkage を持たない**。

→ ★**release の MUEDsp version は free 2種に無関係**。subdir graft は hermetic subdir を移動するだけ = MUEDsp core に API 差があっても **free plugin は壊れない・reconcile 不要**。§1-3 の退行リスクは subdir graft では**構造的に発生しない**。

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
- GitHub default branch rename の影響範囲 = (a) PR base 既定 (b) branch protection (c) open PR の re-target (d) clone HEAD。いずれも一度きりの設定変更で、既存 shipped artifact には無影響。

### 3-2. ★rename mechanical 裏取り (conductor 依頼・CCO 実査 2026-07-19)

`gh` で `kimny1143/mued-dsp` を実査 → **「旧 main archive → 統合 branch を main に rename」は mechanically clean・ただし 3 点を手順化すれば snag なし** (fallback `develop` は不要):

1. ★**現 `main` は branch protection **無し**** (`gh api .../branches/main/protection` = 404 "Branch not protected")。→ Phase 2 の protection は**移設でなく net-new 設定** (§6-11)。rename は protection に阻まれない。
2. ★**open PR 3件** — うち 2 件が base=`main` (`#201` MuedSteel→MUEDsat rename / `#203` sign-and-package orchestrator)、1 件が base=feat (`#202` muedsat-ui-D→rename-muedsteel branch)。GitHub は base branch rename 時に open PR を**自動 retarget** → 放置すると `main` base の 2 件が archive 先を指す。→ **rename 前に明示処理** (#201 close / #203 retarget or 取り込み / #202 fate 確認)＝§6-7。
3. ★**default は rename 先へ追随**する (現 default=main を archive に rename すると default が archive へ移る) → 統合 branch を main に rename 後、**default を main へ明示再設定**＝§6-9/10。

→ history 書換・force-push は**一切不要** (全て branch rename + tag + 設定変更)。上記 3 点を手順に織り込み済ゆえ **naming=`main` で進行可** (snag なし)。

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
| MUEDsp core 退行 | **構造的に非該当** | ★free plugin は hermetic (自前 dsp/ コピー・plugin/MUEDsp 参照ゼロ・§1-3b 実査)。subdir graft は MUEDsp を触らず、free plugin も MUEDsp に依存しない → 退行経路が存在しない。build-verify は green 実証用 (退行検出用ではない)。 |
| CI 破壊 (rename) | **低** | workflows ref-agnostic。final grep を手順化。 |
| 可逆性 | **完全** | 統合 branch 削除 / default branch を main に戻すだけで復元。feat branch 温存ゆえ source loss 無し。 |
| **escalation caveat (a) 本番 download 実リスク** | **非該当** | download 対象は既存 shipped artifact (feat build 由来)。本 proposal はそれを変えない。 |
| **escalation caveat (b) fleet policy 改訂** | **非該当** | 本件は dsp repo を既存 fleet policy に**適合させる** conformance。policy 本体は改訂しない。 |

→ **両 escalation caveat に非該当** = CCO+conductor で確定可。kimny は FYI awareness のみ。

---

## 6. 移行手順 (conductor 依頼#1・誰が/何を/可逆性/検証)

**実行主体 = dsp課** (自 repo・自 process。CCO は cross-repo write せず設計と検証観点を供給 — 所有境界尊重 [[project_ownership_write_guard_20260611]])。CCO は review。

### Phase 1 — 統合 branch 確立 (即時・IP-loss 窓を閉じる)

1. **base 選定 = `release/0.1.1-alpha`** (最新 MUEDsp core + docs・dsp も推奨)。
   - ★**最終 trunk 名 = `main`** (conductor 裁定 2026-07-19)。CCO の当初 `develop` 推奨 (version 名 branch を trunk にしない) は **`main` でも満たされる** (`main` も version-agnostic) 上、**fleet Branch Protection Policy が全 repo `main`=保護 trunk 標準**ゆえ dsp だけ `develop` は fleet naming 乖離。旧 main は §6-10 で retire ゆえ `main` の名が解放される → 統合 branch を `main` にすれば version-agnostic + fleet 一貫の両取り。
   - **Phase 1 は working 名で作業** (`develop` or `trunk-wip`・dsp/CCO 任意) → build+verify 通過後に Phase 2 で `main` へ rename (§6-8〜)。
2. **MUEDlim graft** (丸 merge しない):
   - `feat/muedlim-productize` から **`plugin/MUEDlim/` subdir のみ**を統合 branch へ持ち込む (`git checkout feat/muedlim-productize -- plugin/MUEDlim` 相当)。★**ship path (Xcode project) はこの subdir 内に自己完結**ゆえ graft だけで ship 用 scheme が揃う (dsp Q1)。
   - MUEDsp は**触らない** (release 版維持)。
   - (任意・dev-convenience) top-level から両 free を CMake 一括 build したいなら `plugin/CMakeLists.txt` に `add_subdirectory(MUEDlim)` 追加。**ship (Xcode) には不要** (dsp Q2 = 現状 top-level 未登録・各 plugin standalone CMake)。
3. **MUEDsat graft**: 同様に `plugin/MUEDsat/` subdir (ship = 自前 Xcode project)。CMake 一括 build 希望時のみ `add_subdirectory(MUEDsat)`。
4. **build-verify (必須・2 面・green 実証用)**:
   - (a) **ship path**: 各 plugin の Xcode scheme (`macOS-VST3`/`AUv2`/`AAX`) を統合 branch 上で build → 既存 shipped と同等を確認。
   - (b) **dev/verify**: CMake APP build + 既存 render-verify 再走。
   - ※ MUEDsp 依存による破壊の心配は §1-3b (free plugin hermetic) で構造的に消滅ゆえ、build-verify は「graft 後に green を実証する」目的 (退行検出ではない)。
   - ★**fresh 統合 worktree build 前提 (dsp Phase1 実行で判明・runbook/CI 必須 2 step)**: `git worktree add` は submodule を自動 init しない → build 前に **(i) `git submodule update --init plugin/iPlug2`** (未 init だと `parse_config` ModuleNotFound で build script 落ち) **(ii) `iPlug2/Dependencies/IPlug/download-vst3-sdk.sh`** (VST3_SDK は submodule 外の別 download・未取得だと VST3 target が SDK not found)。AAX SDK も同様に別配置。→ **Phase 2 の trunk build CI/再現手順にこの 2 step を含める** ([[project_vst3_au_build_phase2a]])。graft 欠陥ではない (hermetic 検証どおり MUEDsp 依存の退行ゼロ・APP/VST3 clean build)。

**✅ Phase 1 実施結果 (2026-07-19・dsp 実行 → CCO Tier2 review APPROVE `ee9f207`)**: `develop` (release/0.1.1-alpha 起点) に MUEDlim/MUEDsat subdir graft 完了。CCO git 裏取り = subdir 加算のみ・**plugin/MUEDsp 変更 0** (release 版維持)・graft tree md5 が feat head と**完全一致** (banner+nit 込み・drift 0)・feat 残置 (可逆)・banner render が pinned `658da78e` 一致 (両プラグイン develop build)。ship=Xcode VST3 + dev=CMake APP green (dsp evidence)。→ **IP-loss 窓が閉じた** (全 plugin source が単一 develop trunk に集約)。
5. **可逆性**: この時点で feat branch は無傷。問題あれば統合 branch を捨てて元に戻る。

### Phase 2 — `main` へ昇格 (long-term・(C)・全 ref 操作・history 不変)

> ★sequence = 旧 main を archive→名を解放→統合 branch を `main` に rename→default+protection。force-push なし。**§3-2 CCO 実査の GitHub mechanical 前提** (open PR 3件・main 無保護) を織り込む。

6. **main の unique docs を salvage**: `release..main` の main-unique commit (gap#10 limiter 診断/決定 ~3 commit: `f732db3`/`a599e46`/`8ba067c` 等) を統合 branch へ cherry-pick (docs のみ・conflict 小)。
7. **★open PR 3件を rename 前に明示処理** (§3-2・auto-retarget 誤爆回避): GitHub は base branch rename 時に open PR を自動 retarget するため、放置すると `main` base の PR が archive 先を指す。→ **rename 前に**: (a) `#201` (MuedSteel→MUEDsat rename・base main) = 統合で MUEDsat 実在ゆえ **superseded 判定→close** (dsp 確認) (b) `#203` (sign-and-package orchestrator・base main・価値あり) = 新 main へ **retarget** (or 統合 branch へ先に取り込み) (c) `#202` (base=feat/rename-muedsteel-to-muedsat) = main rename の影響外だが consolidation stack の一部ゆえ fate を dsp と確認。
8. **final CI grep**: `grep -rn "branches:" .github plugin/.github/workflows` + `grep -rn "github.event.schedule\|\bmain\b" .github plugin/.github/workflows` で `main` 固定依存が無いことを再確認 (§3・実査済だが実行前再走)。
9. **旧 main を archive + 名を解放**: 旧 main を **archive tag `archive/main-pre-consolidation`** で保全 → 旧 main branch を `archive/main-pre-consolidation` に **rename** (名を解放)。★注意: 現 default を rename すると **default が rename 先へ移る**ため一時的に archive が default 化 → 次手で戻す。
10. **統合 branch → `main` に rename** + **default を `main` に設定** (step 9 で移った default を明示的に main へ)。
11. ★**net-new branch protection を `main` に設定** (§3-2 実査: 現 main は**無保護** = 移設でなく新規設定)。fleet Branch Protection Policy 準拠 (PR 必須・main 直 push 禁止)。
12. ★**rename 実効 verify (conductor 依頼)**: default 変更後に **CI を 1 回実走** (`main` への push か workflow_dispatch) し **緑を確認** — rename が CI trigger / PR base を壊していないことを実証。
13. **feat branch 退役**: 新 `main` が build+ship 実証後、`feat/muedlim-productize`/`feat/muedsat-ui-D` を archive tag 化 (source は `main` にあるため安全)。
14. **最終検証**: 新 `main` から (a) 全 plugin build (b) notarize (c) MUEDsat DL manifest 突合 (既存 shipped と同一性) → clean で完了。

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
