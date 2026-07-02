# デザイン系スキル 受け入れ監査 (supply-chain audit) — 2026-07-02

- 状態: **draft (kimny 採否用・conductor 経由)**
- 監査者: CCO (template課)
- 入力: insight recon (`gw-data-analysis` PR#217 `reports/design-skills-recon-20260702.md`)
- 監査基準: `docs/drafts/design-skill-inventory-and-acceptance-flow-20260702.md` Part2 (default-deny + supply-chain 7-gate)
- 監査手法: **default-deny で各候補の実ファイルを read-only 精読**(二次サマリで判定せず・SKILL.md + 同梱script + npm registry メタを GitHub API/npm registry から取得して実物確認・**一切 install/実行していない**)
- 優先度: **非緊急 / 並行 narrow-gap fill** (LP 再挑戦の critical path = Claude Design 製品の 15分再走であり skill 導入ではない = Chief reconcile。本監査は org 側 Claude Code で design を強化する並行トラック)

---

## TL;DR — 採否 recommendation

| 候補 | gap | 出所 | 監査結論 | 推奨 |
|------|-----|------|---------|------|
| **frontend-design** | G1 | Anthropic 公式 (anthropics/skills) | 全 gate PASS・実行面ゼロ | ★**ADOPT** (最優先・最安全) |
| **ui-design-brain** | G2 | community (carmahhawwari, MIT, 830★) | SKILL.md clean・実行面ゼロ | **CONDITIONAL ADOPT** (components.md 通読後) |
| theme-factory | G1 | Anthropic 公式 | PASS (価値=10 preset のみ) | ADOPT 可 (任意・補助) |
| **clone-website** | G3 | community (JCodesMore, MIT, 24.6k★) | 技術面 clean・**法務/利用規約リスク大** | ⚠**HOLD (kimny/法務 gate)** |
| **brand-design-md** | G2 | community (zephyrwang6, 94★, **license無**) | **Gate3 FAIL** (未pin npx 二段依存) | ✕**REJECT as-is** (代替=直 vendor) |
| canvas-design | (G1隣接) | Anthropic 公式 | clean だが静的画像専用=LP非該当 | SKIP (scope外) |
| G4 / G5 候補 | G4/G5 | — | insight recon で**候補なし** | 未充足のまま記録 |

**核心推奨**: **frontend-design (G1) + ui-design-brain (G2)** の 2 件が「高価値 × 低リスク × org 側 Claude Code で即効く」= LP 再挑戦の並行 narrow-gap fill として最適。clone-website は技術的には clean だが用途が「他サイト pixel-perfect 複製」ゆえ**自社/許諾サイト限定の利用規約 gate が kimny 必須**。brand-design-md は現状 reject。

---

## 各候補 Gate 別監査

### ★ADOPT: frontend-design (G1 デザインシステム/美的方向性) — Anthropic 公式

`anthropics/skills` `skills/frontend-design/SKILL.md` (+ LICENSE.txt のみ)

| Gate | 判定 | 根拠 |
|------|------|------|
| G0 出所 | **PASS** | Anthropic 一次配布 (公式 repo 157k★)。sourceType=**well-known** (Stripe docs と同格の最高信頼) |
| G1 精読 | **PASS** | 純粋な design-guidance prose のみ。ガードレール弱化/秘密送信/破壊操作 指示なし。「memory を hint に」「screenshot を撮る」は通常の skill 挙動 |
| G2 権限 | **PASS** | `allowed-tools` 拡張なし・tool 要求なし。指示文のみ |
| G3 静的scan | **PASS** | script/binary ゼロ・network ゼロ・npx ゼロ・eval ゼロ。**実行面ゼロ** |
| G4 sandbox | N/A | 実行物なし |
| G5 lock | 可 | SKILL.md + LICENSE.txt のみ・hash lock 容易 |
| G6 Tier | Tier3 (shared配布) だが **リスク最小** | 公式・実行面ゼロ |

**内容の質**: 「templated default を避け brief 固有の意図的選択をする」設計思想 + 2-pass (brainstorm token system → self-critique → build → critique) + AI 臭い 3 クラスタ (cream/serif、near-black/acid、broadsheet) の明示回避。既存 `ui-ux-pro-max` の実装力に対し「美的方向性の言語化」を補完。**G1 の本命。ADOPT 推奨。**

### CONDITIONAL ADOPT: ui-design-brain (G2 component library / UI パターン)

`carmahhawwari/ui-design-brain` (SKILL.md + components.md + LICENSE.txt + README)

| Gate | 判定 | 根拠 |
|------|------|------|
| G0 出所 | PASS (個人・中信頼) | 830★・MIT (★GitHub の NOASSERTION は誤検出、LICENSE.txt 実物は正規 MIT と確認)・直近 commit 2026-07-01 活発 |
| G1 精読 | **PASS (SKILL.md)** / ⚠residual | SKILL.md = clean な UI-guidance (60+ component の best practice 参照指示)。**残: components.md (60+ パターンの静的 ref) 未通読** → 埋め込み injection 有無を導入前に通読必須 (可能性低・reference doc) |
| G2 権限 | PASS | tool 拡張なし |
| G3 静的scan | **PASS** | script/network/npx ゼロ。SKILL.md + components.md は doc のみ=実行面ゼロ |
| G6 Tier | Tier3 (community) | 実行面ゼロゆえリスク低〜中 |

**内容の質**: component.gallery 由来 60+ パターン・8px グリッド・WCAG AA・anti-pattern 集。`web-design-guidelines` (準拠レビュー) を「実装前の component 選定知識」で補完。**G2 の実務本命。components.md 通読を条件に ADOPT 推奨。**

### ADOPT 可 (任意): theme-factory (G1 補助) — Anthropic 公式

`anthropics/skills` `skills/theme-factory/SKILL.md` + themes/*.md (10) + theme-showcase.pdf

- G0-G3 **PASS** (公式・実行面ゼロ)。★`theme-showcase.pdf` = opaque binary だが **display 専用** (この文脈で実行不能・導入前に render 確認推奨、リスク極小)。
- 価値限定: 「10 の色+フォント preset 適用」止まり (insight 評=本格 token 体系構築ではない)。frontend-design と併用で slide/LP の quick styling に。**任意 ADOPT。**

### ⚠HOLD (kimny / 法務 gate 必須): clone-website (G3 参照移植)

`JCodesMore/ai-website-cloner-template` `.claude/skills/clone-website/SKILL.md`

| Gate | 判定 | 根拠 |
|------|------|------|
| G0 出所 | PASS | 24.6k★・MIT・直近 commit 2026-07-02 活発。良質 template |
| G1 精読 | **PASS (技術)** | 473行 workflow。browser MCP で DOM を **read-only 抽出** (getComputedStyle/textContent/querySelectorAll)。injection/ガードレール弱化なし |
| G2 権限 | ⚠**CAUTION** | browser MCP 必須 (claude-in-chrome で代替可) + 並列 builder subagent を worktree に dispatch + 対象サイト資産の **download script を生成・実行** (network)。全て clone 本来の挙動で exfil ではないが**能力が広い** |
| G3 静的scan | **PASS (技術)** | curl\|bash / eval / secret アクセス / ハードコード exfil 先 なし。同梱 script (sync-agent-rules.sh / sync-skills.mjs) = benign な local codegen (node:fs のみ・skill payload 外)。package.json deps = 全て mainstream (next/react/shadcn/tailwind) |
| G4 sandbox | 要 (heavy) | 採用検討時は worktree subagent 生成 + download を隔離試行 |
| **G6 Tier / ★GOVERNANCE** | **Tier3 + kimny 明示承認必須** | 下記 2 点 |

**★非技術リスク (これが HOLD 理由)**:
1. **法務/利用規約**: 用途 = 「任意サイトを text+資産+デザイン込み pixel-perfect 複製」。**第三者サイトへ向けると著作権/IP/ToS 違反リスク**。repo README も phishing/なりすまし/デザイン盗用/ToS 違反を明示禁止。→ **自社/許諾済みサイト限定**でのみ許容。「競合 LP を複製して自社 LP として出す」用途は不可 (IP 侵害)。「参照からデザインパターンを**抽象的に**学ぶ」用途なら本 skill は過剰かつ不適 (本 skill は verbatim 複製ツール)。
2. **導入フットプリント**: 単体では非機能 — Next.js+shadcn+Tailwind scaffold 前提。採用 = template 全体統合 or 大幅 adapt + npm deps 継承。

**推奨**: **verbatim 複製目的では ADOPT せず kimny/法務 gate へ**。「デザイン参照抽出」が欲しいなら skillui (DOM→token 抽出・verbatim 複製しない・insight recon 記載) 等の方が用途適合。そもそも G3「参照移植」は Claude Design 製品側の機能で skill 不足でない可能性 (Chief reconcile 中) = 本 skill の中心性自体が低下しうる。

### ✕REJECT as-is: brand-design-md (G2 ブランド token)

`zephyrwang6/brand-design-md` (SKILL.md + README、**LICENSE 無**)

| Gate | 判定 | 根拠 |
|------|------|------|
| G0 出所 | ⚠ | 94★・**LICENSE ファイル無** = 既定で全権利留保 = 再配布可否不明 (要解決) |
| G1 精読 | PASS (skill text) | 62 ブランド slug registry + 指示。injection なし |
| G3 静的scan | **FAIL (as-is)** | Step2 が `npx getdesign@latest add <slug>` を指示 = **未pin の実行時二段 supply-chain**。getdesign 自体は legit (VoltAgent/awesome-design-md・MIT・postinstall 無・deps:null) だが **`@latest` = 将来の任意 version が自動実行**。かつ design token は repo 外 (getdesign.md service) に存在=skill 単体で価値完結しない |

**推奨**: **現状 REJECT**。採用するなら (a) LICENSE 無を解決 (b) getdesign を監査済 version に pin + bin/cli.mjs 監査 (c) 望むブランド DESIGN.md を **VoltAgent/awesome-design-md (MIT) から直接 vendor** する方が clean。労力対効果低ゆえ**非採用推奨**、ブランド preset が欲しければ直 vendor で代替。

### SKIP: canvas-design (scope 外)

Anthropic 公式・clean だが**静的 PDF/PNG アート専用** (Web/HTML 非対応) ゆえ LP 制作に直接使えない。多数 .ttf font binary 同梱 (OFL・標準フォント)。必要が出れば安全に採用可だが今回 scope 外。

### 未充足: G4 (ブランド/ビジュアル ID) / G5 (moodboard ideation)

insight recon で **候補なし (空振り)**。該当領域は skill で埋まらないまま。canvas-design が G4 に隣接するが ID 体系化ではない。→ **gap として記録・現時点アクションなし**。

---

## sourceType 分類 (採用時 skills-lock.json)

| 候補 | sourceType | 理由 |
|------|-----------|------|
| frontend-design / theme-factory | **well-known** | Anthropic 一次配布 (公式・最高信頼) |
| ui-design-brain / clone-website | **github** | community 外部 = 全 gate 対象 |
| brand-design-md | github (採用時) | 未採用推奨 |

## Tier / 導入経路

- いずれも **shared 配布 = Tier3** (全課波及 + 外部依存導入) → conductor + kimny 承認。
- **template課 local のみ試験導入**なら Tier2 (実行面ゼロの frontend-design/ui-design-brain は特に低リスク)。
- clone-website = 内容問わず **kimny 明示承認** (法務/利用規約 gate)。

## 次アクション

1. 本監査を conductor へ → **kimny 採否**へ (PWA QA 経路。推奨 = frontend-design + ui-design-brain 採用 / clone-website HOLD / brand-design-md 非採用)
2. kimny GO の候補: ui-design-brain は components.md 通読 → 実ファイル取得 → sourceType=github/well-known で skills-lock.json 登録 (hash lock) → Tier に応じ配布
3. G4/G5 は未充足として据え置き (将来 recon 再試 or 内製検討)
