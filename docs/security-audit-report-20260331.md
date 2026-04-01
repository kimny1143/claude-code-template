# セキュリティ監査レポート — 2026-03-31

実施者: template課
対象: /Users/kimny/Dropbox/_DevProjects/ 配下の全リポジトリ

---

## 項目1: Next.js バージョン確認（CVE-2025-29927）

**判定: ✅ 全リポジトリ対応済み**

CVE-2025-29927 は Next.js の middleware 認証バイパス脆弱性。修正バージョン: 14.2.25+ / 15.2.3+

| リポジトリ | package.json | 実バージョン | 判定 |
|-----------|-------------|------------|------|
| livesheet | `16.1.6` | 16.1.6 | ✅ SAFE |
| mued/mued_v2 | `^16.2.1` | 16.x | ✅ SAFE |
| hkt-assign-attendance-template | `^14.2.7` | 14.2.32 (lockfile) | ✅ SAFE (≥14.2.25) |

**対応不要。**

---

## 項目2: NEXT_PUBLIC_ 変数のシークレット監査

**判定: ✅ 重大な漏洩なし**

### 検出された NEXT_PUBLIC_ 変数

| 変数名 | 判定 | 理由 |
|--------|------|------|
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | ✅ Safe | Clerk publishable keyは公開前提 |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | ✅ Safe | Stripe publishable keyは公開前提 |
| `NEXT_PUBLIC_STRIPE_PRICE_*` | ✅ Safe | Price IDはシークレットではない |
| `NEXT_PUBLIC_SUPABASE_URL` | ✅ Safe | 公開前提 |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | ✅ Safe | Anon keyは公開前提（RLSで保護） |
| `NEXT_PUBLIC_APP_URL` | ✅ Safe | URL |
| `NEXT_PUBLIC_CLERK_SIGN_*_URL` | ✅ Safe | URLパス |
| `NEXT_PUBLIC_GA_MEASUREMENT_ID` | ✅ Safe | GA計測ID |
| `NEXT_PUBLIC_SENTRY_DSN` | ✅ Safe | クライアント側DSN |
| `NEXT_PUBLIC_UPLOAD_PROXY_URL` | ✅ Safe | URL |
| `NEXT_PUBLIC_VERCEL_ENV` | ✅ Safe | 環境名 |
| `NEXT_PUBLIC_E2E_TEST_MODE` | ✅ Safe | テストフラグ |

### .env ファイルの Git 追跡状況

**全リポジトリで .env ファイルは git 追跡対象外（gitignore適用済み）** ✅

**対応不要。**

---

## 項目3: GitHub Secret Scanning + Push Protection

**判定: ✅ Public リポは既に有効 / Private リポは対応不要**

- Public リポジトリ（4件）: GitHub が自動で Secret Scanning を有効化済み
- Private リポジトリ: GitHub Free プランでは Secret Scanning / Push Protection 利用不可。ただし private のためリスクは低い
- **再検討タイミング**: GitHub Team/Enterprise プランに移行時

→ 参考: `github-secret-scanning-guide.md`（プランアップグレード時に使用）

---

## 項目4: @clerk/nextjs バージョン確認

**判定: ⚠️ 要更新（2リポジトリ）**

最新安定版: **7.0.7**

| リポジトリ | 現在のバージョン | 判定 | 推奨アクション |
|-----------|---------------|------|-------------|
| livesheet | `^6.37.0` | ⚠️ メジャー遅れ | v7系へのメジャーアップデート |
| mued/mued_v2 | `^7.0.0-snapshot.v20260204043403` | ⚠️ snapshot版 | `^7.0.7` 安定版に更新 |

### 推奨対応
1. **mued_v2**（優先度: 高）: snapshot版はセキュリティパッチが含まれない可能性。`npm install @clerk/nextjs@^7.0.7` で安定版に更新
2. **livesheet**（優先度: 中）: v6→v7はbreaking changeあり。マイグレーションガイド確認の上で計画的に更新

---

## 項目5: TruffleHog スキャン

**判定: 下記に結果を記載**

対象リポジトリ（12件）:
- _conductor
- _contents-writing
- _data-analysis
- _videos
- claude-code-action
- claude-code-base-action
- claude-code-template
- Echovna
- glasswerks-claude-skills
- livesheet
- mued-claude-code-template
- mued-zenn-content

### スキャン結果: ✅ 全リポジトリクリーン

TruffleHog v3.94.1 で git 履歴全体をスキャン。verified/unverified 両方で検出ゼロ。

| リポジトリ | 検出数 | 判定 |
|-----------|--------|------|
| _conductor | 0 | ✅ Clean |
| _contents-writing | 0 | ✅ Clean |
| _data-analysis | 0 | ✅ Clean |
| _videos | 0 | ✅ Clean |
| claude-code-action | 0 | ✅ Clean |
| claude-code-base-action | 0 | ✅ Clean |
| claude-code-template | 0 | ✅ Clean |
| Echovna | 0 | ✅ Clean |
| glasswerks-claude-skills | 0 | ✅ Clean |
| livesheet | 0 | ✅ Clean |
| mued-claude-code-template | 0 | ✅ Clean |
| mued-zenn-content | 0 | ✅ Clean |

**対応不要。**

---

## 項目6: Preview環境 Deployment Protection

**判定: ✅ 現時点では対応不要（Vercel Hobby プラン制約）**

- Vercel Hobby プランでは Deployment Protection 機能が利用不可
- Preview URL のリスクは現状低い（ユーザー数が限定的）
- **再検討タイミング**: ユーザー数増加時 / Vercel Pro プランへの移行時

→ 参考: `vercel-deployment-protection-guide.md`（プランアップグレード時に使用）

---

## 定期チェック項目（patrol時に実施）

### 7. 全リポのuntrackedファイル確認

**目的:** .gitignoreされていない予期しないファイル/ディレクトリの検出

**背景:** 2026-03-31に`npx skills add`がAIツール26ディレクトリに同時インストールした事例あり。CIやgit statusだけでは検知できない（untrackedファイルはCI対象外）。

**チェックコマンド:**
```bash
# 各リポで実行: untrackedファイル一覧（.gitignore適用後）
for repo in _conductor _contents-writing _data-analysis _videos _LandingPage/glasswerks-lp freee-MCP mued/mued_v2 mued/threads-api _Reserch _cowork claude-code-template livesheet; do
  echo "=== $repo ==="
  git -C /Users/kimny/Dropbox/_DevProjects/$repo status --short | grep "^??" | head -10
done
```

**注意すべきパターン:**
- `.`で始まる見慣れないディレクトリ（AIツール自動生成の可能性）
- `credentials`, `secrets`, `.env`を含むファイル名
- 大量の同一構造ディレクトリ（npx skills addの副作用）
- `node_modules`以外の巨大なuntrackedディレクトリ

**対処:** 不要なら削除 + `.gitignore`に追加。判断に迷う場合はconductor確認。

---

## サマリー

| 項目 | ステータス | 緊急度 |
|------|----------|--------|
| 1. Next.js CVE | ✅ 対応済み | — |
| 2. NEXT_PUBLIC_ 監査 | ✅ 問題なし | — |
| 3. Secret Scanning | ✅ Public既有効 / Privateはプラン制約で対応不要 | — |
| 4. @clerk/nextjs | ⚠️ mued課に更新指示済み | 高（mued_v2）/ 中（livesheet） |
| 5. TruffleHog | ✅ 全12リポジトリ クリーン | — |
| 6. Deployment Protection | ✅ Hobbyプラン制約で対応不要（増加時再検討） | — |
| 7. Untrackedファイル確認 | 🔄 定期チェック項目（patrol時） | 低（定期） |
