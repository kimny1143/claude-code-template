---
name: ui-mock-fidelity
description: >
  承認済みモックと UI 実装を「1ミリもずらさず同一」にするための忠実性照合の規律・手順。
  native/plugin UI で反復した「承認 mock ≠ 実装（雰囲気移植で "近い" 止まり）」事故の再発防止機構。
  使用タイミング: (1) 新規 UI 面・re-skin・視覚的再設計を実装する時 (2) 承認モックから実装する時
  (3) 完了報告に render×mock の diff を添付する時 (4) conductor がモック忠実性を vet する時。
  トリガー例: 「モック通りに実装」「UI をモックと同一に」「pixel-diff」「overlay で照合」
  「mock に合わせて」「忠実性チェック」「これモックと違う」「1ミリもずらさず」
  ※既存実装の微修正（コピー1行・padding・バグ修正）は対象外。
---

# ui-mock-fidelity — UI モック忠実性の機構

承認済みモックと UI 実装を **1ミリもずらさず同一** にするための規律。
契機 = native/plugin（dsp）で反復した「承認 mock ≠ 実装」事故（雰囲気移植で "近い" 止まり）。
実証 = MUEDlim UI（CSS 実値 1:1 移植 → conductor overlay/pixel-diff で 100% verify → notarized build sha `a832976a…` bit-identical）。

正本 = このスキル。課ローカル memory（dsp `feedback_render_verify_visual_fidelity` /
`feedback_design_to_native_exact_pixel_transplant`）と差分が出たら **このスキルを正** とする。

---

## 0. 適用境界（最初に判定する — 官僚化 creep 回避）

**IN（本機構の対象）**: 承認モックが**存在する/すべき**作業。
- 新規 UI 面の実装
- re-skin（既存 UI の視覚的な貼り替え）
- 視覚的再設計

**OUT（対象外・既存 Tier/review 規律のまま）**:
- 既存実装の**微修正**: コピー1行の変更 / padding・margin 微調整 / バグ修正
- モックが承認物として存在しない・不要な作業

> 全課に薄く官僚を撒くのが目的ではない。**起きている native/plugin を厳格化**するのが目的。
> pattern は native/plugin UI（dsp）に集中し、web UI（React）は該当が薄い（§7 較正）。

---

## 1. rule 1 — pinned mock = 単一の正

- UI dispatch は必ず**承認済みモックを pin** して行う。**モック無しの UI 実装依頼を禁止**。
- pin は **filename / hash 等の一意識別子**で行う。**「案A」「案B」等の曖昧ラベル禁止**
  （段階で再利用され衝突する。実際に初稿が「案A」参照で衝突した＝この rule の live 例）。
- 例: `muedlim_ui_lufs_hero_mockA_v2_20260713.png`（○） / 「案A の方向で」（×）。

---

## 2. rule 2 — 数値仕様抽出（雰囲気移植 禁止）

モックから以下を**数値表**として抽出し、そのまま移植する。**「雰囲気で寄せる」を禁止**。

- 座標（x/y）・寸法（w/h）・アスペクト比
- 色（hex）
- フォント（種類・weight・size・字間）
- 余白（padding / margin / gap）

> ★**モックが自作 HTML/CSS なら、実 source 値を 1:1 移植する**（eyeball 不要で exact 到達可能
> ＝dsp の core insight）。「同じ CSS でやっていて同じものを使えない環境はあり得ない」（kimny）。

---

## 3. rule 3 — 完了報告に diff 必須添付

完了報告には **render × mock の並置 + overlay / pixel-diff** を必須で添付する。

| 種別 | 期待 |
|------|------|
| **web（React）** | **pixel-perfect**（Playwright スクショ一致で足る） |
| **native/plugin** | **数値一致 + pixel-diff + 許容差 明示 + 非再現点 flag**（silently approximate 禁止） |

### 非再現 flag の扱い（厳格）
- **flag してよいのは真に engine 由来のものだけ**: sub-pixel AA・hinting 等。
- **font weight 未同梱 / size・座標の概算は fixable ゆえ flag 不可 = 100% 一致必須**。
  「native だから」を許容差の言い訳にしない。
- ★**『非再現』の立証責任は flag する側にある**（engine 由来と示せない限り fixable 扱い）。
  例: Sora を単 weight と思い込み立証せず flag したのは故障（実際は house font 統一で解消）。
- 真に再現不能な要素が残るなら **webview（mock の HTML/CSS 直描画）を fallback に検討**。

### render の条件
- render は **editor 部分のみ**（standalone のウィンドウ枠を crop ＝モックと同条件で照合）。

---

## 4. rule 4 — 二重 gate（vet なし push 経路 封鎖）

1. peer が diff 添付。
2. **conductor が印象評「clean」でなく、モック突合を実見して vet**。
   - 「近い」は**却下**。**「見分けつかない」のみ通す**。
   - conductor vet は **font weight + 全 component size を overlay/diff で 100% 照合**。
3. → kimny push。
- **vet を経ない kimny push を禁止**（conductor の『clean』過大評価がこの穴の実例）。

---

## 5. rule 0 — mock hygiene（上流欠陥の予防）

pinned mock は **shippable / house 資産で作る**。

- system / proprietary font（例: Helvetica Neue）等の**同梱不可な資産の混入を禁止**。
  → impl が shippable build で 100% 一致できない構造欠陥になる（今日の実例 → house Sora 統一で fix）。
- mock 側で「impl が 100% 一致 shippable にできる」前提を保証する（house / OFL font 等を使う）。

> ※ モック**設計品質**（mock 自体の文法/方向の誤り。例: progress-bar で GR 文法誤り）は
> 別対策（実物リファレンスにグラウンドする `feedback_design_reference_real_convention_not_invented`）。
> mock hygiene（資産の shippability）とは切り分ける。

---

## 6. 例外表（append-only・明示列挙制）

暗黙の例外を作らない。承認された例外のみをここに列挙する。

| # | 例外 | 承認 |
|---|------|------|
| 1 | version 文字列表示（mock に無いが実 plugin 情報として許容） | kimny 2026-07-13 |

---

## 7. calibration（偏在対応 — blanket 官僚化を避ける）

- pattern は **native/plugin UI（dsp）に集中**。web UI（React）は該当薄い
  （product課 creators = Playwright 12/12 で mock 一致・mued hero は copy 問題で mock-fidelity ではない）。
- ∴ **universal 原則 + native 厳格 calibration**: 全課に薄く撒くのでなく、native/plugin を厳格化する。

---

## 8. gate の役割分離（重要）

- **忠実性 gate（見分けつかない）は kimny 美的 gate の代替でない**。
- 忠実性 =「承認 mock **通りか**」／ 美的 =「kimny が最終的に**良い**と判断するか」＝別レイヤー。
- 実装中に別レイヤーの design 原則変更（例: GR-hero → LUFS-hero）が来たら
  **mock 差替 → 再実装で吸収**する（機構=忠実性 / doctrine=design 原則 の分離が機能する）。

---

## 参照

- 正本 proposal: `_conductor/docs/inbox/proposal-ui-mock-fidelity-mechanism-20260713.md`
- 実証記録（dsp）: `dsp_muedlim_ui_lufs_hero_impl_plan_20260713.md` /
  `dsp_muedlim_ui_A_size_audit_pixeldiff_20260713.md` /
  memory `feedback_design_to_native_exact_pixel_transplant`（iPlug2 移植 8技法）
- DoD の常時 on 版 = 各課 CLAUDE.md 共通ブロック `20-ui-mock-fidelity`
