# claude-peers

複数の Claude Code インスタンスがリアルタイムでメッセージをやり取りできる MCP サーバー。
異なるプロジェクトで動いている Claude Code 同士が互いを発見し、協調作業できる。

**これはグローバルツールであり、プロジェクトごとのセットアップは不要。**

ソース: [louislva/claude-peers-mcp](https://github.com/louislva/claude-peers-mcp)

## ツール一覧

| ツール | 用途 |
|--------|------|
| `list_peers` | 同一マシン上の Claude Code インスタンスを発見 |
| `send_message` | 他のインスタンスにメッセージを送信（即時配信） |
| `set_summary` | 自分の作業内容を他のインスタンスに公開 |
| `check_messages` | 受信メッセージを確認 |

## グローバルセットアップ（1回だけ）

### 1. Bun のインストール

```bash
brew install oven-sh/bun/bun
```

### 2. リポジトリのクローン

```bash
git clone https://github.com/louislva/claude-peers-mcp.git ~/claude-peers-mcp
cd ~/claude-peers-mcp
bun install
```

### 3. MCP サーバーを登録

```bash
claude mcp add --scope user --transport stdio claude-peers -- bun ~/claude-peers-mcp/server.ts
```

### 4. チャネル対応で起動（必須）

**通常の `claude` 起動ではメッセージの即時配信が動作しない。** 必ずチャネルフラグ付きで起動すること：

```bash
claude --dangerously-load-development-channels server:claude-peers
```

> **検証結果（2026-03-24）:** 通常起動 + `check_messages` 手動ポーリングではメッセージが届かなかった。チャネルフラグ付きで起動した場合のみ即時プッシュ配信が正常に動作。

エイリアスを作ると便利（実質必須のため推奨）：

```bash
# .zshrc に追加
alias claudepeers='claude --dangerously-load-development-channels server:claude-peers'
```

### 5. 動作確認

ターミナルを2つ開き、それぞれで Claude Code を起動。
片方で「List all peers on this machine」と聞く。

## 要件

- Bun ランタイム
- Claude Code v2.1.80 以降
- claude.ai ログイン（API キーでは不可 — チャネルプロトコルに必要）

## 環境変数

| 変数 | デフォルト | 説明 |
|------|-----------|------|
| `CLAUDE_PEERS_PORT` | `7899` | ブローカーデーモンのポート |
| `CLAUDE_PEERS_DB` | `~/.claude-peers.db` | SQLite DB の場所 |
| `OPENAI_API_KEY` | （任意） | 自動サマリー生成（gpt-5.4-nano） |

## プロジェクト側 CLAUDE.md の設定例

```markdown
## マルチインスタンス連携

このマシンには claude-peers MCP がグローバルインストールされている。
複数の Claude Code インスタンスが同時に動いている場合、以下のツールで連携できる：

- `list_peers()` — 同一マシン上の他インスタンスを一覧
- `send_message(peer_id, message)` — 他インスタンスにメッセージ送信
- `set_summary(summary)` — 自分の作業内容を公開
- `check_messages()` — 受信メッセージを確認

**活用例：**
- 別プロジェクトの Claude に調査を依頼
- 並行作業の進捗を共有
- 依存関係のあるプロジェクト間で変更を通知
```

## CLI ツール

```bash
cd ~/claude-peers-mcp
bun cli.ts status          # ブローカーとピアの状態確認
bun cli.ts peers           # アクティブなピア一覧
bun cli.ts send <id> <msg> # ピアにメッセージ送信
bun cli.ts kill-broker     # ブローカーデーモン停止
```
