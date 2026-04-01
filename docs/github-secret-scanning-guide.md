# GitHub Secret Scanning + Push Protection 有効化手順

kimny操作用の手順書です。

---

## 前提条件

- GitHubリポジトリのAdmin権限が必要
- GitHub Free プランでも public リポジトリでは利用可能
- Private リポジトリの場合は GitHub Advanced Security（GHAS）が必要（GitHub Team/Enterprise）

---

## 手順

### Step 1: 対象リポジトリ一覧

以下のリポジトリ全てに対して設定を行います:

| リポジトリ | 公開/非公開 |
|-----------|-----------|
| claude-code-template | 確認要 |
| mued-claude-code-template | 確認要 |
| livesheet | 確認要 |
| mued-zenn-content | 確認要 |
| glasswerks-claude-skills | 確認要 |
| claude-code-action | 確認要 |
| claude-code-base-action | 確認要 |

※ ローカルのみのリポジトリ（_conductor, _videos等）はGitHub上にない場合スキップ

### Step 2: Secret Scanning の有効化

各リポジトリで以下を実行:

1. GitHub でリポジトリページを開く
2. **Settings** タブ → 左メニュー **Code security** (旧: Security & analysis)
3. **Secret scanning** セクションを見つける
4. **Enable** をクリック

### Step 3: Push Protection の有効化

Secret Scanning を有効化した後:

1. 同じ **Code security** ページ内
2. **Push protection** セクション
3. **Enable** をクリック

これにより、シークレットを含むpushが自動的にブロックされます。

### Step 4: 組織レベルでの一括設定（推奨）

GitHub Organizationを使用している場合:

1. Organization の **Settings** を開く
2. **Code security** → **Global settings**
3. **Secret scanning** と **Push protection** を Organization レベルで有効化
4. "Automatically enable for new repositories" にチェック

### Step 5: 確認

設定完了後、各リポジトリの **Security** タブで:
- Secret scanning alerts が表示されること
- Push protection が "Enabled" になっていること

を確認してください。

---

## 既存シークレットの確認

有効化後、GitHubが過去のコミット履歴をスキャンします。
**Security** タブ → **Secret scanning alerts** にアラートが表示された場合:

1. 各アラートを確認
2. 漏洩したシークレットをローテーション（再発行）
3. アラートを "Revoked" としてクローズ

---

## CLI での一括確認コマンド

```bash
# gh CLI でリポジトリのセキュリティ設定を確認
gh api repos/kimny1143/{REPO_NAME} --jq '{
  secret_scanning: .security_and_analysis.secret_scanning.status,
  push_protection: .security_and_analysis.secret_scanning_push_protection.status
}'
```

確認対象リポジトリを一括チェック:
```bash
for repo in claude-code-template mued-claude-code-template livesheet mued-zenn-content glasswerks-claude-skills claude-code-action claude-code-base-action; do
  echo "=== $repo ==="
  gh api repos/kimny1143/$repo --jq '{
    secret_scanning: .security_and_analysis.secret_scanning.status,
    push_protection: .security_and_analysis.secret_scanning_push_protection.status
  }' 2>/dev/null || echo "Not found on GitHub or no access"
done
```

---

## トラブルシューティング

- **"Secret scanning is not available"**: Private リポジトリでGHASが無効。Public に変更するか、GitHub Team以上のプランが必要
- **Push が reject された**: 意図的にシークレットを含める場合は `git push` 時の URL に表示されるバイパスリンクから許可可能（非推奨）
