# claude-history-mcp

claude.ai の会話履歴を Claude Code から検索できる MCP サーバー。
TF-IDF ベースの全文検索で、日本語・英語の会話を横断的に検索可能。

## セットアップ

### 1. 会話データのエクスポート

1. [claude.ai](https://claude.ai) にログイン
2. Settings → Account → Export Data
3. メールで届く ZIP を展開
4. `conversations.json` を `data/` ディレクトリに配置

### 2. 依存関係のインストール

```bash
pip install "mcp[cli]>=1.0.0"
```

### 3. Claude Code に MCP サーバーを登録

```bash
claude mcp add -s user claude-history \
  -e CLAUDE_HISTORY_DIR=/path/to/claude-code-template/mcps/claude-history/data \
  -- python /path/to/claude-code-template/mcps/claude-history/server.py
```

`-s user` でユーザーレベル登録すると、どのプロジェクトからでも使える。

### 4. 動作確認

Claude Code で：

```
> history_stats でデータの読み込み状況を確認して
```

会話数・メッセージ数が表示されれば OK。

## ツール一覧

| ツール | 用途 |
|--------|------|
| `conversation_search(query, max_results)` | キーワードで会話を検索 |
| `recent_chats(n, before, after)` | 最近の会話を時系列取得 |
| `get_conversation(conversation_id)` | 特定の会話の全文取得 |
| `history_stats()` | インデックス統計の確認 |

## プロジェクト側 CLAUDE.md の設定例

MCP ツールをプロジェクトの CLAUDE.md に記載しておくと、Claude Code が適切なタイミングでツールを使える。

```markdown
## 会話履歴の検索

このプロジェクトには claude-history MCP サーバーが接続されている。
claude.ai での過去の会話を検索するには以下のツールを使う：

- `conversation_search(query, max_results)` — キーワードで会話を検索
- `recent_chats(n, before, after)` — 最近の会話を時系列取得
- `get_conversation(conversation_id)` — 特定の会話の全文取得
- `history_stats()` — インデックスの統計確認

**過去の議論や決定事項を参照する際は、これらのツールで会話を検索すること。**
```

## データの更新

claude.ai のデータは自動同期されない。
新しい会話を反映するには再度エクスポート → `data/conversations.json` を上書き。

## 環境変数

| 変数 | デフォルト | 説明 |
|------|-----------|------|
| `CLAUDE_HISTORY_DIR` | `./data` | conversations.json の配置ディレクトリ |

## 検索の仕組み

- 日本語: unigram + bigram でトークン化（MeCab 不要）
- 英語: 単語分割
- TF-IDF スコアリングで関連度順に返す
- 外部ライブラリは `mcp[cli]` のみ（remote MCP 化する時のみ `uvicorn` / `starlette` を追加）

## iOS / リモート MCP として公開する

iOS / iPhone の Claude アプリから同じ履歴を検索したい場合は、 `streamable-http` transport + Cloudflare Tunnel + Bearer トークンの組合せで公開できる。 環境変数 `MCP_TRANSPORT=streamable-http` を指定したときだけ HTTP server 化するので、 Claude Code / Claude Desktop 向けの既存の stdio 動作は影響を受けない。

詳細手順は [`docs/claude-history-remote-mcp-setup.md`](../../docs/claude-history-remote-mcp-setup.md) を参照。 Cloudflare Tunnel 用の設定 template は [`cloudflared-config.example.yml`](./cloudflared-config.example.yml) にある。

| 環境変数 | 用途 |
|----------|------|
| `MCP_TRANSPORT` | `stdio` (既定) / `streamable-http` |
| `MCP_AUTH_TOKEN` | streamable-http 時の Bearer トークン (32 文字以上必須、 `openssl rand -hex 32` 推奨) |
| `MCP_HTTP_HOST` | listen するアドレス (既定 `127.0.0.1`、 Cloudflare Tunnel の origin 以外には公開しない) |
| `MCP_HTTP_PORT` | listen するポート (既定 `8000`) |
