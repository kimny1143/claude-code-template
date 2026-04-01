# Vercel Preview環境 Deployment Protection 有効化手順

kimny操作用の手順書です。

---

## なぜ必要か

Preview デプロイメントはデフォルトで公開アクセス可能です。これにより:
- 未リリース機能の漏洩リスク
- Preview 環境の API エンドポイントへの不正アクセス
- テスト用シークレットやデータの露出

Deployment Protection を有効にすることで、認証済みユーザーのみがPreview環境にアクセスできるようになります。

---

## 前提条件

- Vercel ダッシュボードへのアクセス（Admin権限）
- Vercel Pro プラン以上（一部機能はFreeでも利用可能）

---

## 手順

### Step 1: 対象プロジェクト確認

Vercel にデプロイされているプロジェクトを確認:
1. [Vercel Dashboard](https://vercel.com/dashboard) を開く
2. 対象となるプロジェクトを特定

### Step 2: Deployment Protection の有効化

各プロジェクトで:

1. Vercel Dashboard → 対象プロジェクトを選択
2. **Settings** タブ
3. 左メニュー **Deployment Protection**
4. 以下を設定:

#### Standard Protection（推奨設定）

| 設定 | 推奨値 | 説明 |
|------|--------|------|
| **Vercel Authentication** | ✅ Enabled | Vercelアカウントでのログインを要求 |
| **Protection Bypass for Automation** | 状況に応じて | CI/CDやE2Eテストで必要な場合のみ有効化 |
| **Shareable Links** | ❌ Disabled（推奨） | 共有リンクによるバイパスを無効化 |

#### 設定手順

1. **"Standard Protection"** を選択
2. **"Vercel Authentication"** のトグルを ON にする
3. **"Only members of [Team Name]"** を選択（チームメンバーのみ許可）
4. **Save** をクリック

### Step 3: 確認

1. 新しいPreviewデプロイを作成（PRを作成するか、featureブランチにpush）
2. Preview URL にアクセス
3. Vercel のログイン画面が表示されることを確認

---

## プロジェクトごとの設定チェックリスト

| プロジェクト | Deployment Protection | 確認日 |
|------------|----------------------|--------|
| mued_v2 | ☐ 設定完了 | |
| livesheet | ☐ 設定完了 | |
| (他プロジェクト) | ☐ 設定完了 | |

---

## 注意事項

### E2E テストとの連携

Playwright 等のE2Eテストを CI で実行している場合、Preview 環境へのアクセスにバイパストークンが必要です:

1. **Settings** → **Deployment Protection** → **Protection Bypass for Automation**
2. **Generate Secret** をクリック
3. 生成されたシークレットを CI 環境変数に設定:
   - GitHub Actions: `VERCEL_AUTOMATION_BYPASS_SECRET`
   - テストスクリプトで Cookie `_vercel_jwt` にトークンをセット

### OGP/SNSクローラーへの影響

Deployment Protection を有効にすると、SNS のリンクプレビュー（OGP）がPreview環境では動作しなくなります。Production 環境には影響しません。

### Vercel CLI での確認

```bash
# プロジェクト設定を確認
vercel inspect <deployment-url>
```

---

## トラブルシューティング

- **"403 Forbidden" でPreviewが見られない**: 正常動作。Vercelアカウントでログインが必要
- **CI/CDが失敗する**: Protection Bypass for Automation の設定を確認
- **設定項目が表示されない**: Vercel Free プランでは一部制限あり。Pro プランへのアップグレードを検討
