# デザイン系スキル 在庫棚卸し + 外部スキル受け入れ手順 — 2026-07-02

- 状態: **draft (conductor review 待ち)**
- 起票: CCO (template課)、conductor dispatch (Chief 起票・kimny 指示「デザイン系スキルを固めてから LP デザイン再挑戦」) 受領
- 手番順: insight が design skill 候補を recon → **CCO が受け入れ監査** → kimny 採否 → 導入
- 本 draft = 候補到着**前**の 2 準備物: **Part 1 = 在庫棚卸し(分類表)** / **Part 2 = 外部スキル受け入れ手順(default-deny + supply-chain 監査)**
- 監査対象データ源: `skills-lock.json` (全47 skill tracked) + `scripts/audit-skills-lock.sh --json`

---

## Part 0. TL;DR / 診断の訂正

Chief 見立て「デザイン系スキルゼロ・freee/stripe/internal-common 系のみ」は **事実誤認**。実在庫を読むと、UI/UX 実装・デザインレビュー・UX 心理・パフォーマンス・CRO(ページ設計)・モーションの各軸に **design 隣接スキルが 15+ 件存在**する。

正しい gap は「デザイン系ゼロ」ではなく、**3 領域に絞られる**:

1. **純粋なビジュアルデザイン制作** — デザインシステム / デザイントークン(色・タイポ・余白の体系)、ブランド/ビジュアルアイデンティティ、イラスト/アイコン方向性
2. **デザインシステム構築** — component library (shadcn/Tailwind 等) の体系的生成、テーマ設計
3. **参照移植** — 既存デザインを reference として再現・翻案する workflow、Figma → code / デザインハンドオフ

さらに **第 2 診断軸**を分離: **在庫 gap ≠ 適用 gap**。第一挑戦は ClaudeDesign(claude.ai)上で、これは **Claude Code skill を構造的に load しない**(効かせる場所が無い)ゆえ第一挑戦の skill 活用は**構造的にゼロ = 見落としではない**(Chief 構造点)。再挑戦は **org 側 peer(Claude Code が動く)で design skill を効かせて**行う方針。∴ axis は「過去活用の有無」ではなく「**再挑戦を担う org 側 peer が使える既存 design skill はどれか + 何が不足か**」。→ Part 1-C 参照。

---

## Part 1. 在庫棚卸し (分類表)

### 1-A. design/frontend 隣接スキル(**在庫あり**) — 能力軸別

| 軸 | skill | カバー範囲 | source |
|----|-------|-----------|--------|
| **UI/UX 実装・design intelligence** | `ui-ux-pro-max` | ★中核。plan/build/design/implement/review/improve UI/UX code。styles: image-first / editorial / minimalism / dark mode / responsive。対象: landing page / dashboard / SaaS / mobile app | local |
| UI 実装パターン | `vercel-composition-patterns` | React composition (compound components, render props, context, React 19 API) | local |
| UI 実装パターン | `vercel-react-best-practices` | React/Next.js perf 最適化パターン | local |
| UI 実装パターン | `vercel-react-native-skills` | React Native / Expo モバイル UI | local |
| オンボーディング UI | `app-onboarding` | オンボーディング設計(ワイヤーフレーム指示 + React/SwiftUI codegen + フロー図) | local |
| **デザインレビュー/QA** | `web-design-guidelines` | Web Interface Guidelines 準拠レビュー(a11y / UX / 設計監査) | local |
| パフォーマンス計測 | `core-web-vitals` | Lighthouse / Bundle Analyzer / CWV 診断 | local |
| **UX 心理・説得** | `ux-psychology` | UX 心理効果を UI 設計へ適用(価格表 / オンボーディング / CTA) | local |
| UX 心理・説得 | `marketing-psychology` | 70+ mental models / cognitive bias / 説得 | local |
| **ページ設計(CRO/LP)** | `lp-optimizer` | ★LP 第三者視点分析・改善。CRO + direct response (Schwartz/Hopkins/Ogilvy)。hero / 価格 / CTA / A/B 設計 | local |
| ページ設計(CRO) | `copywriting` | homepage / LP / pricing / feature / about ページのコピー | local |
| ページ設計(CRO) | `signup-flow-cro` / `onboarding-cro` / `form-cro` / `paywall-upgrade-cro` | 各コンバージョンフローの設計・最適化 | local |
| ページ設計 支援 | `seo-audit` / `marketing-audit` / `ab-test-setup` / `analytics-tracking` | SEO / 監査 / 実験 / 計測 | local |
| **モーション/動画** | `remotion` | React ベース動画(promo / LP 動画 / motion graphics / OGP 動画) | local |

**小計: design/frontend 直接関連 ≒ 15〜20 skill(周辺 CRO 含む)。「ゼロ」は誤り。**

### 1-B. gap(**在庫が薄い/無い** — 「LP デザイン再挑戦」の核心)

| # | 不足領域 | 現状 | 近い既存 skill(部分カバー) |
|---|---------|------|--------------------------|
| G1 | **デザインシステム / デザイントークン** — 色システム、タイポスケール、spacing token、テーマ設計の体系化 | **無** | `ui-ux-pro-max`(styles は触れるが token 体系構築はしない) |
| G2 | **component library 生成** — shadcn/Tailwind 等のデザインシステム scaffolding | **無**(実装パターンはあるがビジュアル DS ではない) | `vercel-*`(patterns/perf のみ) |
| G3 | **参照移植 / デザインハンドオフ** — 既存デザインを reference に再現・翻案、Figma → code | **無** | `ui-ux-pro-max`(image-first だが専用 workflow 無) |
| G4 | **ブランド/ビジュアルアイデンティティ** — logo / iconography / illustration 方向性 | **無** | なし |
| G5 | **ビジュアル参照/moodboard ideation** — 視覚素材からの発想支援 | **薄** | `ui-ux-pro-max`(image-first) |

→ **insight の recon はこの G1〜G5 を候補領域とすべき**(既存でカバー済の UI 実装 / レビュー / CRO を重複提案しないよう本表を共有)。

> ★caveat (2026-07-02 conductor heads-up・insight 中間報告): **G3「参照移植」は diagnosis reframe 中** — これは Claude Design(製品)側の機能であり Claude Code skill の不足ではない可能性(Chief/insight reconcile 中)。確定まで G3 は候補領域として**仮置き**扱い。skill 導入の中心性が変わりうるが、**本 draft(分類表 + 受け入れ手順)自体は診断結果と独立の資産ゆえ valid・維持**。

### 1-C. ★第 2 診断軸: 在庫 gap ≠ 適用 gap (org 側再挑戦 前提)

**構造前提(Chief 構造点)**: 第一挑戦の ClaudeDesign(claude.ai)は **Claude Code skill を load しない** — 効かせる場所が構造的に無い。∴ 第一挑戦での skill 活用は**ゼロ = 見落としではなく構造的必然**。「skill 不足」診断とも矛盾しない。過去活用の確認 Q は **moot(不要)**。

再挑戦は **org 側 peer(Claude Code が動く環境)で design skill を効かせて**実施する方針。ゆえに診断軸は:

- **在庫 gap** = そもそも skill が無い領域 → G1〜G5(Part 1-B)の補充が正
- **適用 gap** = 在庫がある(1-A)のに org 側再挑戦がそれを **invoke しない**リスク → 再挑戦の実施 peer に「1-A の既存 design skill を適用させる」運用設計が必要

∴ 再挑戦 = 「**既存 skill(1-A)適用 + 不足分(G1〜G5)補充**」の**両輪**。候補を導入するだけでは適用 gap は埋まらない。**どの peer が実施し、1-A のどれを効かせるか**は本 draft の scope 外(conductor / 実施 peer 側の運用設計)だが、分類表(1-A)がその「効かせる候補リスト」を提供する。

---

## Part 2. 外部スキル受け入れ手順 (default-deny + supply-chain 監査)

現状 `docs/` に外部スキル受け入れの明文フローは**未整備**(audit-skills-lock.sh は hash drift 検出のみ、sourceType 分類は `docs/audit-skills-lock-script-20260527.md` Open Q1 で「後続 task」として defer 済)。本 Part がその後続。既存インフラ(`skills-lock.json` の sourceType / `audit-skills-lock.sh`)に接続する形で定義する。

### 2-0. 脅威モデル (なぜ skill は default-deny か)

Claude Code の skill は 2 つの攻撃面を持つ:

- **SKILL.md = プロンプトインジェクション面**: Claude が従う指示そのもの。悪性 SKILL.md は「secret を送信せよ」「ガードレールを無視せよ」「破壊的コマンドを実行せよ」を Claude に指示しうる。
- **同梱スクリプト/バイナリ = コード実行面**: `.sh`/`.js`/`.py`、`curl|bash`、認証情報窃取、難読化、opaque binary。

→ **信頼できると確認できるまで拒否 (default-deny)**。「有名そう」「便利そう」は受け入れ理由にならない。

### 2-1. 受け入れフロー (候補 1 件ごと)

```
候補到着 (insight recon)
  │
  ├─ [Gate 0] 出所確認 (provenance)
  │     出所不明 / 匿名 gist / 検証不能 origin → REJECT
  │     OK → sourceType 仮判定 (github / well-known / local)
  │
  ├─ [Gate 1] 全ファイル精読 (content inspection)
  │     - SKILL.md 全行: guardrail 弱化 / 秘密送信 / 破壊操作 / 権限拡大 指示の有無
  │     - 同梱 script 全行: network 送信先 / 認証情報アクセス / rm -rf / git push / eval / base64 / 難読化
  │     - opaque binary: 原則 REJECT (正当理由 + 再現ビルド手順が無い限り)
  │     疑わしい 1 点でも → HOLD (kimny/conductor escalate)
  │
  ├─ [Gate 2] 権限スコープ (least privilege)
  │     要求 tool / allowed-tools / MCP / WebFetch domain を確認
  │     auth・secret・billing・push に触る → Tier 3 固定 + kimny 承認必須
  │
  ├─ [Gate 3] 静的スキャン (機械 grep)
  │     curl|bash, wget, eval, exec, base64 -d, ENV secret 読取, 外部 exfil endpoint,
  │     rm -rf, sudo, chmod +x, npx <unknown pkg>, >/dev/tcp
  │
  ├─ [Gate 4] サンドボックス試行 (実行 script がある場合)
  │     隔離環境 (worktree / 一時 dir) で dry-run。副作用を観察してから本採用
  │
  ├─ [Gate 5] hash lock 登録
  │     skills-lock.json に正しい sourceType + pinned hash + provenance で登録
  │     (audit-skills-lock.sh --update --confirm、以降 drift 検出で改竄検知)
  │
  └─ [Gate 6] Tier 判定 → 承認 → 導入
        外部 skill 導入 = 「新しい外部サービス・ライブラリ導入」+ shared 配布なら「全課波及」
        → 原則 Tier 3 (conductor + kimny)。Part 2-3 参照
```

### 2-2. sourceType 分類基準 (skills-lock.json)

| sourceType | 定義 | 現行例 | 受け入れ厳格度 |
|-----------|------|--------|--------------|
| `local` | template課 自作・自管理 | 39 件(ui-ux-pro-max 等) | 内製ゆえ供給網リスク低 |
| `internal-common` | 内製 + distribute-skills.sh で全課配布 | peer-id-lookup / tier-judge / plan-mode-policy / pwa-dashboard | 内製だが波及大 → 変更は Tier 慎重 |
| `well-known` | 公式 vendor doc 由来 (信頼済 origin) | stripe-best-practices / stripe-projects / upgrade-stripe | origin 信頼。fetch 時 hash 更新 |
| `github` | 外部 GitHub repo 由来 | freee-api-skill (`freee/freee-mcp`) | ★供給網リスク最大 → 全 Gate 必須 |

→ **外部候補は原則 `github` or 新設 `community` 相当**。`well-known` を名乗れるのは公式 vendor(Anthropic/Vercel/Stripe 等)一次配布のみ。出所が個人/コミュニティなら `github` 扱いで全 Gate。

### 2-3. Tier 判定 (導入時)

- 外部 skill を **shared (SHARED_SKILLS / COMMON_SKILLS) へ入れる** → 全課波及 + 外部依存導入 → **Tier 3** (conductor + kimny 承認)
- 外部 skill を **template課 local のみ試験導入 (配布しない)** → コード/実行面を含むなら **Tier 2**(peer review: template課 → conductor/Codex)、docs/データのみなら Tier 1
- **auth/secret/billing/push に触る skill** → 内容問わず **Tier 3 固定**

判定は `tier-judge` skill と本手順を併用。迷ったら Tier 3 に上げる(全課共通原則)。

### 2-4. 継続監視

導入後も `audit-skills-lock.sh`(drift 検出)が改竄・無断 update を検知。DRIFT = 内容が lock と不一致 = 重大 incident として conductor escalate(既存設計 Open Q4)。月次 cron audit 候補(cowork RemoteTrigger)も既存で検討中。

---

## Part 3. 運用メモ / follow-up

- **export-skill-inventory.sh は不在**。inventory 源は `audit-skills-lock.sh --json`(全47 skill tracked、機械可読)で代替。専用 export が要れば別途軽量 script 起票。
- **hygiene 所見(非ブロッキング)**: 現在 2 skill が hash DRIFT = `common-claude-md-blocks`(block 編集で想定内)/ `peer-id-lookup`(internal-common、要確認)。意図的変更の確認後に `audit-skills-lock.sh --update --confirm` で再 baseline。**未確認のまま自動再baseline はしない**(改竄と正当変更の区別が付かなくなるため)。
- **Part 2 の昇格先**: 承認後、Part 2(受け入れ手順)は恒久ガードレールとして `docs/template-ops-runbook.md` の Skill 節へ promote 想定 = **全peerガードレール追加 = Tier 3**。Part 1(在庫表)は時点スナップショットゆえ本 draft 据え置き。

## Part 4. 次アクション

1. 本 draft を conductor / insight / kimny / Chief へ共有(分類表 1-A = org 側再挑戦が「効かせる候補」、gap = recon スコープを G1〜G5 に絞る)
2. insight から候補リスト到着 → 本 Part 2 のフローで 1 件ずつ受け入れ監査 → kimny 採否
3. 再挑戦の実施 peer / 運用設計(1-A のどれをどう効かせるか)は conductor / 実施 peer 側 — 本 draft は 1-A(候補リスト)を提供して接続
4. (承認後) Part 2 を runbook へ promote(Tier 3)
