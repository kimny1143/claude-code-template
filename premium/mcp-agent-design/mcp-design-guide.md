# MCP エージェント設計ガイド

> マルチエージェントチームにおける MCP サーバーの設計・配置・運用パターン。
> 単体の MCP サーバー作成方法は無料版の `mcp` スキルを参照。本ガイドは **チーム運用に特化** した設計判断を扱う。

---

## 1. MCP の配置レベル

マルチエージェント環境では、MCP サーバーの配置レベルが設計の起点になる。

| レベル | 設定場所 | 共有範囲 | 例 |
|--------|---------|---------|-----|
| **グローバル** | `~/.claude.json` | 全プロジェクト・全課 | claude-peers（課間通信） |
| **プロジェクト** | `.claude/settings.local.json` | そのプロジェクトの全セッション | freee-mcp（会計API） |
| **セッション** | 起動時フラグ | 単一セッション | 一時的なデバッグ用MCP |

### 判断フロー

```
このMCPは複数プロジェクトで使うか？
├── YES → グローバル（~/.claude.json）
└── NO
    └── 複数セッションで永続的に使うか？
        ├── YES → プロジェクトレベル（settings.local.json）
        └── NO → セッションレベル（起動時追加）
```

### グローバルMCPの登録

```bash
claude mcp add --scope user <mcp-name> -- <command> <args>
```

`~/.claude.json` に書き込まれ、全プロジェクトで自動ロードされる。

### プロジェクトMCPの登録

```bash
claude mcp add --scope project <mcp-name> -- <command> <args>
```

`.claude/settings.local.json` に書き込まれる。

---

## 2. MCP の分類と設計パターン

### パターン A: インフラ MCP（全課共通）

**特徴:** 全エージェントが使用するチーム基盤。グローバル配置。

**例:** claude-peers（インスタンス間通信）

```json
// ~/.claude.json
{
  "mcpServers": {
    "claude-peers": {
      "type": "stdio",
      "command": "bun",
      "args": ["run", "/path/to/claude-peers-mcp/src/index.ts"]
    }
  }
}
```

**設計ポイント:**
- 起動フラグが必要な場合（`--dangerously-load-development-channels` 等）は、エイリアスで対応
- 全課が同一バージョンを使うため、更新時は全セッション再起動が必要
- 障害時の影響範囲が全課に及ぶ → conductor課が管理責任を持つ

### パターン B: ドメイン MCP（特定課専用）

**特徴:** 特定業務の API を扱う。該当プロジェクトのみに配置。

**例:** freee-mcp（会計API）、Stripe MCP

```json
// .claude/settings.local.json（freee課プロジェクト）
{
  "mcpServers": {
    "freee-mcp": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@anthropic-ai/freee-mcp"]
    }
  }
}
```

**設計ポイント:**
- API キーはプロジェクトの `.env.local` で管理（後述）
- 他課が一時的にアクセスする場合は、セッションレベルで追加
- 課の責任範囲 = MCP の管理責任

### パターン C: ツール MCP（機能提供）

**特徴:** 画像生成・検索など、汎用的な機能を提供。必要な課が個別に配置。

**例:** nano-banana-pro（Gemini画像生成）

```bash
# launch.sh で API キーを注入する場合
#!/bin/bash
source "$(pwd)/.env.local" 2>/dev/null
GEMINI_API_KEY="${GEMINI_API_KEY}" npx -y @anthropic-ai/nano-banana-pro
```

**設計ポイント:**
- API キーの課金アカウントを分離したい場合は、課ごとに異なるキーを `.env.local` で管理
- `launch.sh` ラッパーパターンで環境変数を注入
- 利用状況を監査できるよう、API ダッシュボードのプロジェクト粒度を合わせる

---

## 3. API キー管理

### 原則: プロジェクト単位で分離

```
your-project/
├── .env.local          ← APIキーはここ（.gitignore対象）
├── .claude/
│   └── settings.local.json
└── launch.sh           ← .env.localを読んでMCPを起動
```

**なぜ共通化しないか:**
- API ダッシュボードでプロジェクト別の利用量を追跡するため
- 課ごとのコスト配分が明確になる
- キー漏洩時の影響範囲を限定できる

### launch.sh パターン

```bash
#!/bin/bash
# MCP起動ラッパー — cwdの.env.localからAPIキーを読む
set -euo pipefail

ENV_FILE="$(pwd)/.env.local"
if [[ -f "$ENV_FILE" ]]; then
  source "$ENV_FILE"
fi

# 必須キーのチェック
if [[ -z "${GEMINI_API_KEY:-}" ]]; then
  echo "ERROR: GEMINI_API_KEY not set in .env.local" >&2
  exit 1
fi

export GEMINI_API_KEY
exec npx -y @anthropic-ai/nano-banana-pro "$@"
```

### settings.local.json での参照

```json
{
  "mcpServers": {
    "nano-banana-pro": {
      "type": "stdio",
      "command": "bash",
      "args": ["/path/to/claude-code-template/mcps/nano-banana-pro/launch.sh"]
    }
  }
}
```

---

## 4. 権限設計（allow / deny）

MCPツールは `settings.local.json` の `permissions` で制御する。

### 課別の権限設計例

```json
{
  "permissions": {
    "allow": [
      "mcp__claude-peers__list_peers",
      "mcp__claude-peers__send_message",
      "mcp__claude-peers__set_summary",
      "mcp__claude-peers__check_messages",
      "mcp__freee-mcp__freee_api_get",
      "mcp__freee-mcp__freee_api_list_paths"
    ],
    "deny": [
      "mcp__freee-mcp__freee_clear_auth"
    ]
  }
}
```

### 設計原則

| 原則 | 説明 |
|------|------|
| **最小権限** | 各課は必要な MCP ツールのみ allow に追加 |
| **破壊操作の deny** | `clear_auth`, `delete`, `drop` 系は明示的に deny |
| **通信は全課 allow** | claude-peers の 4 ツールは全課共通で許可 |
| **課固有の設定は保持** | テンプレート配布時、課固有の allow/deny は上書きしない |

### テンプレート配布時の注意

`scripts/distribute-settings.sh` などの配布スクリプトでは:

```bash
# 課固有のdeny設定を保持しつつ共通部分だけ更新する
# ❌ cp settings.local.json.example → 課固有設定が消える
# ✅ jqでmerge → 課固有設定が保持される
jq -s '.[0] * .[1]' base.json project-specific.json > merged.json
```

---

## 5. フックとの連携

MCP ツールの呼び出しにフックを掛けることで、安全性を強化できる。

### PreToolUse フックで MCP 操作をガード

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__freee-mcp__freee_api_delete|mcp__freee-mcp__freee_api_put",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/confirm-freee-write.sh"
          }
        ]
      }
    ]
  }
}
```

```bash
#!/bin/bash
# confirm-freee-write.sh — freee への書き込み操作を警告
echo "⚠️ freee API への書き込み操作です。本番データに影響します。"
echo "WARN: この操作はkimny確認を推奨します"
```

### パターン: 監査ログ

```bash
#!/bin/bash
# audit-mcp-calls.sh — MCP呼び出しをログに記録
TOOL_NAME="$1"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "${TIMESTAMP} | ${TOOL_NAME}" >> ~/.claude/logs/mcp-audit.log
```

---

## 6. カスタム MCP の設計チェックリスト

自チーム用のカスタム MCP サーバーを作成する際のチェックリスト。

### ツール設計

- [ ] ツール名は `動詞_名詞` 形式か（`get_users`, `create_invoice`）
- [ ] description はトリガーとなるユーザー発話を含むか
- [ ] 読み取り系と書き込み系を分離しているか
- [ ] エラー時に構造化されたメッセージを返すか（JSON推奨）
- [ ] 1ツールの責務は1つか（巨大な多機能ツールにしない）

### セキュリティ

- [ ] API キーはハードコードしていないか（環境変数 or .env.local）
- [ ] 破壊操作（delete, update, clear）は deny リストに追加したか
- [ ] 入力バリデーションを実装しているか
- [ ] レート制限を考慮しているか

### 運用

- [ ] MCP のオーナー（管理責任者）を決めたか
- [ ] 配置レベル（グローバル/プロジェクト/セッション）を決めたか
- [ ] テンプレートの `mcps/` に README を追加したか
- [ ] 他課への影響を確認したか（グローバルMCPの場合は全課に通知）

### テスト

- [ ] ツール単体での動作確認をしたか
- [ ] 他の MCP と競合しないか確認したか（ツール名の重複等）
- [ ] エラー時のフォールバック動作を確認したか

---

## 7. 共有リソースの排他制御

ブラウザ（chrome拡張）のように **同時に1課しか使えないリソース** がある場合、ロック制を導入する。

### 運用パターン

```
1. 利用課 → conductor課に「[リソース名] 使います」と宣言
2. conductor課 → ロック状態を確認 → 許可 or 待機指示
3. 利用課 → 作業完了後「[リソース名] 解放」を通知
4. conductor課 → ロック解除 → 待機中の課に通知
```

### 適用対象の判断基準

| 基準 | 例 |
|------|-----|
| 同時アクセスで競合する | chrome拡張（タブ操作が衝突） |
| APIレート制限が厳しい | 外部API（1分5リクエスト等） |
| コストが高い | 画像生成API（1回$0.05等） |

通常の MCP（claude-peers, freee-mcp 等）は同時アクセスが可能なので排他制御は不要。

---

## 8. MCP ライフサイクル管理

### 導入フロー

```
1. 要件定義 — 何を解決するか、既存ツールで代替できないか
2. プロトタイプ — 最小限のツールで動作確認
3. Tier 3 レビュー — 新しい外部サービス導入のため conductor レビュー必須
4. テンプレート追加 — mcps/<name>/README.md を作成
5. 配布 — 必要な課に settings.local.json 更新を通知
6. 運用 — オーナー課が管理責任を持つ
```

### 更新・廃止

- **更新:** パッケージバージョンを上げる場合、影響範囲（グローバル/プロジェクト）に応じて通知
- **廃止:** 使用中の課がないことを確認してから削除。`mcps/<name>/` に `DEPRECATED.md` を置いて猶予期間を設ける

### バージョン管理

`skills-lock.json` と同様に、MCP のバージョンを追跡する:

```json
{
  "mcps": {
    "claude-peers": {
      "source": "~/claude-peers-mcp",
      "version": "git:abc1234",
      "scope": "global",
      "owner": "template課"
    },
    "freee-mcp": {
      "source": "npm:@anthropic-ai/freee-mcp",
      "version": "0.3.1",
      "scope": "project",
      "owner": "freee課"
    }
  }
}
```

---

## 付録: 実構成サンプル（10課体制）

| MCP | レベル | オーナー | 用途 |
|-----|--------|---------|------|
| claude-peers | グローバル | template課 | 課間リアルタイム通信 |
| claude-history | プロジェクト | template課 | 会話履歴検索 |
| nano-banana-pro | プロジェクト | template課 | Gemini画像生成 |
| freee-mcp | プロジェクト | freee課 | 会計・人事API |
| claude-in-chrome | グローバル | template課 | ブラウザ自動操作（排他ロック制） |

### 配布テンプレートの構成

```
claude-code-template/
├── mcps/
│   ├── claude-peers/
│   │   └── README.md       ← セットアップ手順
│   ├── claude-history/
│   │   └── README.md
│   └── nano-banana-pro/
│       ├── README.md
│       └── launch.sh       ← APIキー注入ラッパー
```

テンプレートの `mcps/` ディレクトリは **セットアップ手順の告知** であり、MCP サーバー本体は含めない。本体は npm パッケージ or 別リポジトリで管理する。
