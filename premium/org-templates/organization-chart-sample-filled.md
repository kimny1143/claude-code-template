# 組織図 — 記入済みサンプル（10課体制）

> このファイルは `organization-chart-template.md` の記入例です。
> 実際に10課体制で運用しているAIマルチエージェントチームの構成をモデルにしています。

---

## 基本情報

- **チーム名**: glasswerks AI Room
- **オーナー**: 個人（1人運営）
- **インスタンス数**: 11（conductor + 10課）
- **月額基盤コスト**: 約$250（Claude Code Max + インフラ）

---

## 課一覧

### Management

| 課名 | ワークスペース | 担当領域 |
|------|---------------|---------|
| **conductor課** | `_conductor/` | 進捗管理、PRレビュー、横連携、朝礼運営、日報作成 |

### Product（2課）

| 課名 | ワークスペース | 担当領域 | 技術スタック |
|------|---------------|---------|-------------|
| **mued課** | `mued/mued_v2/` | Webアプリ開発 | Next.js 15, Drizzle ORM, Supabase, Stripe, GA4 |
| **native課** | `mued/mued_v2/apps/` | モバイルアプリ開発 | Expo, React Native |

### Marketing（4課）

| 課名 | ワークスペース | 担当領域 | 技術スタック |
|------|---------------|---------|-------------|
| **SNS課** | `mued/threads-api/` | SNS自動投稿、スケジューリング、分析 | Threads API, Instagram API |
| **write課** | `_contents-writing/` | 記事執筆、コピーライティング | Markdown, note.com |
| **video課** | `_videos/` | 動画制作（プロモ、チュートリアル） | Remotion, React |
| **LP課** | `_LandingPage/glasswerks-lp/` | ランディングページ、CRO | Vite, Vercel, GA4 |

### Operations（3課）

| 課名 | ワークスペース | 担当領域 | 技術スタック |
|------|---------------|---------|-------------|
| **freee課** | `freee-MCP/` | 会計自動化 | freee API, MCP |
| **data課** | `_data-analysis/` | GA4分析、コンバージョン分析、A/Bテスト | Python, GA4 API |
| **template課** | `claude-code-template/` | 共有設定一元管理（スキル/フック/コマンド） | Shell, JSON |

---

## 通信ルール

| ルール | 詳細 |
|--------|------|
| 課間通信 | claude-peers メッシュで直接メッセージOK |
| 状況報告 | 朝礼でconductorに報告 |
| ブロッカー | conductor + 関連課にCC |
| PR提出 | conductor経由 → オーナー承認 → マージ |

---

## Tier 2 ピアレビュー担当表

| 自分 | レビュー依頼先 | 理由 |
|------|---------------|------|
| mued課 | native課 | 同一プロダクト、技術スタック近い |
| native課 | mued課 | 同上 |
| SNS課 | write課 | コンテンツ系同士 |
| write課 | SNS課 | 同上 |
| video課 | SNS課 | マーケティング系 |
| LP課 | mued課 | フロントエンド系 |
| data課 | mued課 | データ↔プロダクト連携 |
| freee課 | LP課 | 独立性高い課同士 |

---

## ガードレール

### 1. ポリシー（CLAUDE.md）

全課共通のCLAUDE.mdに以下を記載:
- Branch Protection Policy（mainへの直接push禁止）
- Work Continuation Policy（ユーザー指示まで作業継続）
- Plan Mode Policy（3ファイル以上変更時はPlan必須）
- PRレビュー権限（Tier判定フロー）

### 2. ローカルフック（settings.local.json）

| フック | 対象 | 機能 |
|--------|------|------|
| `block-main-push.sh` | PreToolUse:Bash | mainブランチへのpushをブロック |
| `validate-dangerous-ops-v2.sh` | PreToolUse:Bash/Write/Edit | 危険操作の検出・警告 |
| `load-handoff-memory.sh` | SessionStart | 前セッションの引き継ぎメモリを自動読み込み |

### 3. リモートガードレール（GitHub）

| 設定 | 内容 |
|------|------|
| Branch Protection | mainブランチはPR必須 |
| Required Reviews | 最低1レビュー |
| Status Checks | CI通過必須 |

---

## 運営原則

1. **原価率33%基準** — 全商品の原価率は33%以下を目標
2. **メインプロダクト優先** — 最もバイラル性の高い無料プロダクトを最優先
3. **マスコットはコミュニケーション担当** — 広告媒体としてではなくブランドの顔として運用
4. **計測なきものは存在しない** — GA4、コンバージョン追跡、コスト追跡を全活動に適用
5. **ユーザー指示まで作業継続** — 自己判断で切り上げない（Work Continuation Policy）

---

## スケーリングの経緯

### Phase 1: 3課体制（初期）
```
conductor → dev課 → content課
```
- 全開発を1課で担当、コンテンツも1課
- コンテキストウィンドウの枯渇が頻発

### Phase 2: 6課体制（成長期）
```
conductor → mued課, native課, SNS課, write課, LP課
```
- プロダクト系を技術スタックで分割
- マーケティング系をコンテンツ種別で分割

### Phase 3: 10課体制（現在）
```
+ video課, freee課, data課, template課
```
- video課: トークンコストが大きく分離が必要
- freee課: 金融データのアクセス制御
- data課: 分析専門スキルの集約
- template課: 全課に波及する変更の集中管理

### 分割のトリガーになったシグナル

| シグナル | 対応 |
|---------|------|
| 1課のPR数が週10件超え | 課を分割 |
| CLAUDE.mdが500行を超えた | 責務を分割 |
| コンテキストリセットで作業再開が困難 | 責務範囲を狭める |
| コストスパイクの原因特定が困難 | 高コスト作業を分離 |
