# UI モック忠実性機構 — vessel 案 + 配布計画（CCO → conductor 返送）

*2026-07-13 / template課(CCO) / 契機 = kimny 直命「再発防止を全課配布」（Tier3 gate 通過済）*
*正本 proposal = `_conductor/docs/inbox/proposal-ui-mock-fidelity-mechanism-20260713.md`（Chief 設計・実証 sha a832976a）*
*本書の位置づけ = 配布実行前に conductor へ返す vessel 設計 + 配布計画。**本書 confirm 後に実装（skill/block 作成 + script 変更 + dry-run → 配布）**。*

---

## 0. 結論（先出し）

**vessel = ハイブリッド**（conductor の lean と一致）:

| 器 | 中身 | 配布経路 | 到達範囲 |
|----|------|----------|----------|
| **A. 内部共通 skill `ui-mock-fidelity`（新規・正本）** | 手順の本体（5 rule + native 較正 + mock hygiene + 数値移植技法 + diff/overlay 仕様 + 二重 gate + scope 境界 + 例外表） | `distribute-skills.sh` の **COMMON_SKILLS**（rsync・marker gate 無し） | **全 14 課（dsp 含む）** |
| **B. 共通ブロック `20-ui-mock-fidelity.md`（新規・薄い pointer）** | 常時 on の DoD 1 段落（pin→数値移植→diff→vet・scope 境界・native/web 較正・skill へのポインタ） | `distribute-claude-md-blocks.sh`（marker 置換） | **marker 有課のみ**（mued/product/LP 等 11・dsp/SNS/blender は no-op） |

**なぜハイブリッドか**: 手順性ゆえ本体は skill が最適（on-demand で UI 作業時に surface）。ただし skill は on-demand ゆえ DoD 強制力が弱い → 常時 on の薄い共通ブロックで DoD を規律化。conductor 提示の「skill 寄り + CLAUDE.md 短ポインタ」を素直に実装。

**Gumroad SHARED_SKILLS には入れない**: 本機構は conductor vet / kimny push / dsp native 文脈を含む **内部運用規律**であり、公開 product skill ではない。`[[feedback_shared_vs_common_skill_channel]]`（内部 = COMMON_SKILLS / 公開 = SHARED_SKILLS の区別）に従い **COMMON_SKILLS 一択**。

---

## 1. 器 A: skill `ui-mock-fidelity`（正本・単一 source of truth）

**配置**: `claude-code-template/.claude/skills/ui-mock-fidelity/SKILL.md`
**auto-invocation**: **有効**（`disable-model-invocation` は付けない）。UI 作業開始時に peer が自動 surface すべき working skill（template 管理用 skill とは別分類）。trigger 記述で「新規 UI 面 / re-skin / 視覚再設計 / モック実装 / 忠実性照合」を拾う。

**SKILL.md 章立て案**:
1. **適用境界（最上部・官僚化 creep 回避）**
   - IN: モックが承認物として存在する/すべき作業 = **新規 UI 面・re-skin・視覚的再設計**。
   - OUT: **既存実装の微修正（コピー1行・padding・バグ修正）は対象外**（既存 Tier/review 規律のまま）。
2. **rule 1 — pinned mock = 単一の正**: mock 無し UI 実装依頼を禁止。pin は **filename/hash 等の一意識別子**（「案A/B」等の曖昧ラベル禁止＝段階で衝突する）。
3. **rule 2 — 数値仕様抽出（雰囲気移植 禁止）**: 座標/寸法/色hex/フォント/余白の数値表を抽出移植。**モックが自作 HTML/CSS なら実 source 値を 1:1 移植**（eyeball 不要で exact 到達可能）。
4. **rule 3 — 完了報告に diff 必須**: render×mock 並置 + overlay/pixel-diff 添付。**web = pixel-perfect 期待 / native = 数値一致 + pixel-diff + 許容差明示 + 非再現 flag**。
   - **非再現 flag は真に engine 由来のみ許容**（sub-pixel AA・hinting）。font weight 未同梱 / size・座標 概算は fixable ゆえ **flag 不可 = 100% 一致必須**。**立証責任は flag する側**。
   - render は editor 部分のみ（standalone 枠 crop）。
5. **rule 4 — 二重 gate**: peer が diff 添付 → **conductor がモック突合を実見 vet**（「近い」却下・「見分けつかない」のみ通す）→ kimny push。**vet を経ない kimny push 禁止**。
6. **mock hygiene（rule 0 相当・上流欠陥予防）**: pinned mock は **shippable/house 資産（house/OFL font 等）で作る**。system/proprietary font（Helvetica Neue 等・同梱不可）混入禁止（impl が 100% 一致 shippable にできる前提を mock 側で保証）。
7. **calibration（偏在対応）**: pattern は native/plugin 集中・web は Playwright 一致で足る。→ **universal 原則 + native 厳格較正**。「native だから」を許容差の言い訳にしない。
8. **例外表（append-only・明示列挙制）**: #1 = version 文字列表示（kimny 2026-07-13 承認・mock 外だが実 plugin 情報として許容）。
9. **gate の役割分離**: 忠実性 gate（見分けつかない）≠ kimny 美的 gate（最終的に良いか）。別レイヤー。
10. **参照**: 実証記録 = dsp drafts/memory（`feedback_render_verify_visual_fidelity` / `feedback_design_to_native_exact_pixel_transplant`）。

---

## 2. 器 B: 共通ブロック `20-ui-mock-fidelity.md`（薄い DoD pointer・ドラフト全文）

```markdown
## UI モック忠実性 DoD（新規 UI 面・re-skin・視覚再設計のみ）

承認済みモックが存在する/すべき UI 作業（新規面・re-skin・視覚的再設計）は、以下を DoD とする。
**既存実装の微修正（コピー1行・padding・バグ修正）は対象外**（既存 Tier/review 規律のまま）。

- **mock pin**: 承認 mock を filename/hash 等の一意識別子で pin（「案A/B」等の曖昧ラベル禁止）。mock 無し UI 実装依頼は禁止。
- **数値移植**: 座標/寸法/色hex/フォント/余白を数値で移植（雰囲気移植禁止）。mock が自作 HTML/CSS なら実 source 値を 1:1 移植。
- **diff 添付**: 完了報告に render×mock の並置 + overlay/pixel-diff を必須添付。
  - **web = pixel-perfect 期待** / **native = 数値一致 + pixel-diff + 許容差明示**。
  - 非再現 flag は真に engine 由来（AA/hinting）のみ。font weight/size/座標 は fixable = 100% 一致必須（立証責任は flag 側）。
- **conductor vet**: 印象評でなくモック実見突合。「近い」却下・「見分けつかない」のみ通過 → kimny push。vet を経ない push 禁止。
- **mock hygiene**: pinned mock は shippable/house 資産（house/OFL font 等）で作る。system/proprietary font 混入禁止。

手順の詳細・技法・例外表 = `ui-mock-fidelity` skill を参照。
忠実性 gate（見分けつかない）は kimny 美的 gate の代替でない（別レイヤー）。
```

（約 16 行。既存 block 17 の DoD ブロックと同粒度・常時 on 前提の薄さ。）

---

## 3. 配布計画

### 3-1. 経路と対象
| # | 経路 | 追加操作 | 対象 |
|---|------|----------|------|
| A | `distribute-skills.sh` | `COMMON_SKILLS` に `ui-mock-fidelity` 追加 | 全 14 課（**dsp 到達・marker gate 無し**） |
| B | `distribute-claude-md-blocks.sh` | `blocks/20-ui-mock-fidelity.md` 追加（TARGET_PEERS は現状のまま） | marker 有 11 課（dsp/SNS/blender は no-op skip） |

### 3-2. dsp（主対象）の到達（★要 conductor 判断）
dsp は **共通ブロック marker が 0**（実測: dsp/SNS/blender=0、mued/product/LP=18）。ゆえに器 B（DoD block）は dsp に**届かない**。dsp カバーは:
- **器 A（skill）が rsync で dsp に到達**（marker 不要）＝主カバー。
- **dsp local memory 還流**（§3-4）で共通正本へ link。
- dsp は native ゆえ web 較正（Playwright）非該当・そもそも本機構の主対象で**既に local memory 保有**。

→ **CCO 推奨 = 上記で dsp カバー十分**。共通ブロック marker の dsp 挿入は別 hygiene follow-up（[[project_next_session_hygiene_queue]] #1）として分離。**marker 挿入は dsp CLAUDE.md（他 peer workspace）編集ゆえ CCO 直接不可 → dsp/conductor 手番**。conductor 判断で「今 marker も入れる」なら dsp へ dispatch。

### 3-3. DoD 組込み（rule 4）
器 B（block 20）自体が各課 UI DoD 行。marker 有課へは配布で自動 land。文言は §2 ドラフト参照。

### 3-4. 還流規律（二重正本防止・proposal 明記）
dsp local memory `feedback_render_verify_visual_fidelity` / `feedback_design_to_native_exact_pixel_transplant` へ **共通正本（`ui-mock-fidelity` skill）への link を還流**（単一正本・地層化防止）。
- **CCO は dsp memory を直接編集しない**（他 peer 領域）。**還流文を CCO が用意 → dsp/conductor が dsp 側で適用**。
- 還流文案: 「本 memory の規律は全課共通 `ui-mock-fidelity` skill に正本化された。差分が出たら skill を正とする（[[ui-mock-fidelity]]）。」

### 3-5. 実行順（confirm 後）
1. feature branch 作成（`feat/ui-mock-fidelity-mechanism`）。
2. skill `ui-mock-fidelity/SKILL.md` + `blocks/20-ui-mock-fidelity.md` 作成。
3. `distribute-skills.sh` COMMON_SKILLS に 1 行追加。
4. **両 script を `--dry-run`**（差分確認・意図外の課に diff が出ないこと）。
5. PR 作成 → conductor review（Tier3・fleet-wide canonical）→ merge。
6. merge 後に配布実行（skill rsync + block distribute）。
7. dsp 還流文 + （採否次第で）dsp marker 挿入を conductor 経由 dispatch。
8. 配布結果を conductor へ報告・patrol 記録。

### 3-6. 既知の耐久性 caveat（hygiene #3・block でも同型）
配布は各 peer **working tree を書くだけで commit しない**。durability は各 peer の checkout 時 self-commit 前提（[[project_next_session_hygiene_queue]] #3 = 恒久 fix 設計 draft 済・conductor review 待ち）。skill rsync も同型。→ 配布後、各 live 課の self-commit を checkout hygiene で担保（従来通り）。恒久 fix 完成を**待たずに進める**（待つと機構導入が遅延）。

### 3-7. rollback
- 器 A: COMMON_SKILLS から 1 行除去 + 各課 `.claude/skills/ui-mock-fidelity` 手動/rsync--delete 除去。
- 器 B: `blocks/20-*.md` 削除 + marker 間を空 placeholder 化して再 distribute。
- いずれも additive ゆえ低リスク・独立可逆。

---

## 4. Tier / gate 判断
- kimny 直命で **機構導入自体は承認済**（fleet-wide Tier3 gate 通過）。
- 本書 = 器/配布の**実装前 conductor confirm**（高影響ゆえ conductor 要望通り 1 度返す）。
- confirm 後の実装 = feature branch + PR + conductor merge（branch protection 準拠）。

---

## 5. conductor への確認事項（decision points）
1. **skill 名 `ui-mock-fidelity`** で可か（既存衝突無し確認済）。
2. **dsp marker gap の扱い**: (a) skill rsync + memory 還流でカバー〔CCO 推奨・最小〕 / (b) 加えて dsp CLAUDE.md へ marker 挿入も今回実施（dsp/conductor 手番）。
3. **skill auto-invocation 有効**（`disable-model-invocation` 無し・UI 作業で自動 surface）で可か。
4. **耐久性**: 恒久 self-commit fix を**待たず**、暫定 self-commit-at-checkout 依存で今進める方針で可か。
5. 器 B（DoD block）を **新規 block 20** として立てる方針で可か（既存 block への混載はしない）。

→ 上記 confirm 後、CCO が実装 → dry-run → PR → conductor merge → 配布。
