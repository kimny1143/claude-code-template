# mued-claude-code-template Pro ($29)

mued-claude-code-template の有料版。無料の公開リポジトリに含まれないノウハウドキュメントを収録。

## 無料版（GitHub公開リポ）に含まれるもの

- 37スキル、7コマンド、6エージェント、4フック
- 3つのMCP設定テンプレート
- setup.sh による自動配布
- CLAUDE.md テンプレート

## Pro版で追加されるもの

### 1. Conductor CLAUDE.md 完全版テンプレート (`conductor-template/`)

指揮課（conductor）のCLAUDE.md完全版。マルチエージェントチームの司令塔として機能するための全設定。

- `conductor-claude-md-template.md` — 巡回スケジュール、PRレビューチェックリスト（Tier別4軸）、権限モデル、コマンド定義、日報フォーマット、カスタマイズガイド（3課〜10課+）

### 2. Tier制度 完全運用マニュアル (`tier-operations-manual/`)

AIマルチエージェントチームのPRレビューを3段階で自律管理する仕組み。

- `overview.md` — Tier制度の全体像、設計原則、導入ステップ
- `tier1-self-review.md` — セルフレビューの対象範囲、手順、判断ミスの事例集
- `tier2-peer-review.md` — ピアレビューのペア設計、依頼〜承認フロー、エスカレーション基準
- `tier3-conductor-review.md` — コンダクターレビューのチェックリスト、緊急時対応

### 3. 巡回（Patrol）レポート (`patrol-reports/`)

conductorが日次巡回で使うレポートのテンプレートとサンプル。

- `patrol-report-template.md` — 巡回レポートの標準フォーマット
- `sample-patrol-normal.md` — 通常日のサンプル（8課稼働、ブロッカーなし、PR 5件）
- `sample-patrol-incident.md` — インシデント日のサンプル（ブロッカー2件発生→解消、コストスパイク対応）

### 4. 日報テンプレート + サンプル3日分 (`daily-reports/`)

- `template.md` — 10課体制で使う日報フォーマット
- `sample-day1.md` 〜 `sample-day3.md` — 実運用を想定した記入例

### 5. 組織図テンプレート + 設計判断メモ (`org-templates/`)

- `organization-chart-template.md` — 課の数の決め方、部署グルーピング、conductor課の設計
- `organization-chart-sample-filled.md` — **記入済みサンプル**: 10課体制の完全な組織図（課一覧、Tier2ペアリング表、ガードレール設定、スケーリング経緯）
- `design-decisions.md` — なぜこの構成にしたか、各課の責任範囲の決め方

### 6. コスト管理テンプレート (`cost-management/`)

- `cost-tracking-template.md` — 月間コスト追跡、損益分岐点計算、四半期棚卸し手順
- `cost-tracking-sample-filled.md` — **記入済みサンプル**: 固定費・変動費・構成比・損益分岐点・四半期監査レポートの記入例
- `freee-integration-flow.md` — freee会計との連携フロー、勘定科目マッピング、USD為替処理

---

全ドキュメント日英バイリンガル対応（`en/` ディレクトリに英語版）。

## セットアップ

1. このzipを解凍
2. 無料版リポ（mued-claude-code-template）をclone済みであることを確認
3. Pro版のドキュメントを参考に、あなたのチーム構成に合わせてカスタマイズ
4. CLAUDE.mdにTier制度の判断フローを追記（`tier-operations-manual/overview.md` 参照）
5. conductor CLAUDE.mdテンプレートを使ってconductor課をセットアップ（`conductor-template/` 参照）

## サポート

- 無料版リポのIssuesで質問可能
- Pro版固有の質問はGumroadのメッセージ機能で対応
