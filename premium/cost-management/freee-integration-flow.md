# freee連携フロー — AIチームのコスト管理自動化

## 概要

AIマルチエージェントチームの運用コストをfreee会計と連携して管理するフロー。
手動入力を最小化し、コスト可視化を自動化する。

---

## 前提

- freee会計のアカウント（法人 or 個人事業主）
- freee MCP サーバー（`freee-mcp`）がセットアップ済み
- freee課（経理担当インスタンス）が稼働中

---

## 連携アーキテクチャ

```
各課のAPI利用
  │
  ├─ 月末にコスト棚卸し → 各課から報告
  │
  ├─ freee課が集計
  │   ├─ APIコストを freee の経費カテゴリに分類
  │   ├─ 固定費は自動仕訳（毎月同額）
  │   └─ 従量費は手動確認後に仕訳
  │
  ├─ freee API で仕訳登録
  │   ├─ freee_api_post: /api/1/deals（取引登録）
  │   └─ freee_api_get: /api/1/deals（確認）
  │
  └─ 月次レポート作成 → conductor課に報告
```

---

## freee勘定科目マッピング

AIチーム運用で発生する主なコストと、freeeでの勘定科目の対応:

| コスト項目 | freee勘定科目 | 補助科目（推奨） | 備考 |
|-----------|-------------|----------------|------|
| Claude Code Max | 通信費 or 支払手数料 | AI基盤 | 月額定額。最大コスト項目 |
| 外部API（Anthropic, OpenAI等） | 支払手数料 | API利用料 | 従量制。USD建ての場合は為替注意 |
| SaaSサブスク（freee, Google One等） | 通信費 | SaaS利用料 | 月額定額 |
| ドメイン費用 | 通信費 | ドメイン | 年額を月割 |
| Apple Developer Program | 支払手数料 | アプリ開発 | 年額を月割 |
| ホスティング（Vercel Pro等） | 通信費 | ホスティング | 無料枠→有料化時に発生 |
| 動画生成API（fal.ai, Runway等） | 支払手数料 | 動画制作 | 従量制 |

### 補助科目の設計ポイント

- **課名を補助科目にしない** — コストは「何に使ったか」で分類する方が税務上有用
- **用途別に分類** — 「AI基盤」「API利用料」「SaaS」「ホスティング」の4カテゴリで十分
- **必要に応じて拡張** — 新しいコスト種別が出たら補助科目を追加

---

## 月次フロー

### Week 1（月初）: 前月コスト確定

```
1. 各APIダッシュボードで前月の利用額を確認
   - Anthropic Console → Usage
   - OpenAI Dashboard → Usage
   - fal.ai Dashboard → Billing
   - 各SaaS → 請求書/領収書

2. クレジットカード明細と突合

3. freee課がfreee APIで仕訳登録
```

#### freee APIでの取引登録例

```
freee_api_post /api/1/deals
{
  "company_id": [事業所ID],
  "issue_date": "2026-03-01",
  "type": "expense",
  "details": [
    {
      "account_item_id": [通信費のID],
      "tax_code": 2,
      "amount": 30000,
      "description": "Claude Code Max 2026年2月分"
    }
  ],
  "partner_id": [Anthropicの取引先ID]
}
```

### Week 2-3: 通常運用

- 特別な作業なし
- 従量費の異常値アラートがあれば確認

### Week 4（月末）: コスト棚卸し

```
1. conductor課がpatrolで各課にコスト報告を依頼
2. 各課がヒアリングシートに回答
3. freee課が集計→月次コストレポート作成
4. conductor課→CEO報告
```

---

## 四半期フロー

### 棚卸しの実施

1. **ヒアリングシート配布**（APIコスト棚卸しテンプレート使用）
2. **全課から回収**（1週間の回答期限）
3. **freee課が集計**
4. **四半期比較レポート作成**
5. **コスト最適化提案**

### freeeレポートとの照合

```
freee_api_get /api/1/reports/trial_pl
{
  "company_id": [事業所ID],
  "fiscal_year": 2026,
  "start_month": 1,
  "end_month": 3
}
```

四半期PLレポートの「通信費」「支払手数料」の実績値と、課別集計の合計が一致することを確認。

---

## USD建てコストの為替処理

### 対象

- Anthropic API（USD）
- OpenAI API（USD）
- Apple Developer Program（USD）
- fal.ai（USD）
- Vercel（USD）

### 処理方法

1. **クレジットカード決済日の為替レート**を使用
2. freeeの「外貨建取引」機能は使わず、**円建て決済額**で仕訳（カード明細の円額）
3. 為替差損益は年次で調整（月次では無視）

### 注意

- カード明細の円額 ≠ APIダッシュボードのUSD額 × 当日レート
- 差異が大きい場合（5%超）はカード会社の為替レートを確認

---

## アラート設計

### 自動アラート（推奨）

| 条件 | アラート先 | アクション |
|------|----------|-----------|
| 従量費が前月比150%超 | conductor課 + freee課 | 原因調査 |
| 無料枠利用率90%超 | 該当課 + freee課 | 有料化計画を策定 |
| 新サービスのコスト発生 | freee課 | 勘定科目マッピング確認 |
| 月間総コストが予算超過 | conductor課 + CEO | 緊急コスト会議 |

### 実装方法

- 各APIのUsage Alertを設定（対応しているサービスのみ）
- conductor課のpatrolで月2回チェック
- freee課が月次レポートで異常値を報告

---

## あなたのチームに適用するには

### ステップ1: freee会計を準備

- 勘定科目に補助科目を追加（AI基盤、API利用料、SaaS、ホスティング）
- 取引先マスタに各サービス提供元を登録

### ステップ2: freee MCPを設定

```bash
# freee-mcp のセットアップ（別途README参照）
npx skills add freee/freee-mcp
```

### ステップ3: 経理担当インスタンスを配置

- 専任のfreee課を置く or conductor課が兼務
- CLAUDE.mdにfreee API操作の権限を付与

### ステップ4: フローを回す

- 初月は手動で全フローを実行して検証
- 2ヶ月目から定型部分を自動化
- 四半期で棚卸しサイクルを開始
