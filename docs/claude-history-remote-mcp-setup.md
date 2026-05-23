# claude-history を iOS / iPhone の Claude アプリから使えるようにする設定手順

最終更新: 2026-05-24

このドキュメントは、 kimny の Mac 上で動いている `claude-history` MCP server を、 iOS や iPhone の Claude アプリ (Anthropic 公式) からも使えるように公開する手順をまとめたものです。

## やりたいこと (1 行)

iOS Claude アプリで会話しているときに、 過去の Claude Code セッションや claude.ai の履歴を検索したい (`conversation_search` / `recent_chats` / `get_conversation` / `history_stats`)。

## 全体像

```
iPhone (Claude アプリ)
  ↓ Custom Connector で登録した URL
Anthropic クラウド
  ↓ HTTPS (公開)
Cloudflare Edge (claude-history.<your-domain>)
  ↓ Cloudflare Tunnel (Mac 起動中のみ)
kimny Mac (127.0.0.1:8000) で動く claude-history server
  ↓ ローカルファイル読込
~/.claude/projects/**/*.jsonl  (Claude Code 履歴)
~/Dropbox/.../mcps/claude-history/data/*.json  (claude.ai export)
```

要点:

- server は kimny Mac でだけ動く (Claude Code 履歴は home dir 配下、 Dropbox 同期外のため)
- Cloudflare Tunnel が **Mac を直接インターネット公開せず**、 Cloudflare エッジ経由で安全に外部から到達できるようにする
- Bearer トークン (約 64 文字) で認証する。 トークンを知らないリクエストは server 側で 401 拒否

## 前提

- kimny の Cloudflare アカウント (gw-dash で利用中のものを流用可)
- 独自ドメイン or Cloudflare で管理しているサブドメイン (例: `<your-domain>` の下に `claude-history.<your-domain>` を生やす)
- macOS で `cloudflared` CLI が install 済 (`brew install cloudflared`)
- kimny Mac が常時起動していること (Mac sleep 中は iOS から接続不可)

## 手順 (約 30 分)

### 1. Bearer トークンを生成する

ターミナルで:

```bash
openssl rand -hex 32
```

64 文字の hex 文字列が出力される。 これが Bearer トークン本体。 **絶対に他者に教えない / git に commit しない**。

例: `a3f5...省略...c9d2`

トークンを下記 2 箇所で同じ値を使う:

- Mac 側 server 起動時の env var `MCP_AUTH_TOKEN`
- claude.ai → Settings → Connectors の URL に query 付与、 または "Headers" 設定 (後述)

### 2. server を streamable-http モードで起動する

Mac 上で:

```bash
cd /Users/kimny/Dropbox/_DevProjects/claude-code-template/mcps/claude-history

# 必要なら: pip install "mcp[cli]>=1.0.0" uvicorn starlette

export MCP_TRANSPORT=streamable-http
export MCP_AUTH_TOKEN="ここに 1. で生成した 64 文字を貼る"
export CLAUDE_HISTORY_DIR=/Users/kimny/Dropbox/_DevProjects/claude-code-template/mcps/claude-history/data

python3 server.py
```

成功時:

```
claude-history MCP listening on http://127.0.0.1:8000/mcp (bearer auth enabled, expose via Cloudflare Tunnel)
INFO:     Uvicorn running on http://127.0.0.1:8000
```

別ターミナルで動作確認:

```bash
# token なし → 401 が返ること
curl -i -X POST http://127.0.0.1:8000/mcp

# token あり → 通る (MCP プロトコルの POST なのでレスポンス内容は気にしなくて OK)
curl -i -X POST http://127.0.0.1:8000/mcp \
  -H "Authorization: Bearer $MCP_AUTH_TOKEN"
```

問題なければ Ctrl+C で止めて、 後で常駐化する。

#### stdio との backward compat 確認 (任意)

env var を解除すれば従来通り stdio 起動になり、 Claude Code / Claude Desktop で `~/.claude.json` および `~/Library/Application Support/Claude/claude_desktop_config.json` 経由で動くままです。

```bash
unset MCP_TRANSPORT MCP_AUTH_TOKEN
python3 server.py   # stdin/stdout 待ちで黙る = stdio モード OK
```

### 3. Cloudflare Tunnel を作成する

Cloudflare アカウントにログインしている前提。

```bash
# 認証 (ブラウザが開き Cloudflare login)
cloudflared tunnel login

# tunnel 作成
cloudflared tunnel create claude-history
# → "Created tunnel claude-history with id ..." と表示される。 UUID をメモ。

# DNS route 設定 (Cloudflare で管理しているドメインを使う)
cloudflared tunnel route dns claude-history claude-history.<your-domain>
```

### 4. cloudflared config を配置する

このリポジトリの `mcps/claude-history/cloudflared-config.example.yml` を `~/.cloudflared/config.yml` にコピーして、 以下を埋める:

- `tunnel: REPLACE_WITH_TUNNEL_UUID` → 手順 3 で出力された UUID
- `credentials-file: ...REPLACE_WITH_TUNNEL_UUID.json` → 同 UUID
- `hostname: claude-history.REPLACE_WITH_YOUR_DOMAIN` → 手順 3 で設定したホスト名

### 5. tunnel を起動して試す

```bash
# foreground で起動 (動作確認用)
cloudflared tunnel run claude-history
```

別ターミナルで:

```bash
curl -i -X POST https://claude-history.<your-domain>/mcp \
  -H "Authorization: Bearer $MCP_AUTH_TOKEN"
# → 200 (MCP プロトコル POST) が返れば 経路 OK

curl -i -X POST https://claude-history.<your-domain>/mcp
# → 401 (token なし) が返れば auth OK
```

問題なければ tunnel を常駐化:

```bash
sudo cloudflared service install
```

(常駐化したくない場合は `brew services start cloudflared` でも可)

### 6. claude.ai に Custom Connector を登録する

ブラウザで [claude.ai](https://claude.ai/settings/connectors) を開く:

1. Settings → Connectors → **Add custom connector** をクリック
2. 入力欄:
   - **Name**: `claude-history` (任意の表示名)
   - **URL**: `https://claude-history.<your-domain>/mcp`
3. **Advanced** を開き、 Authentication で Bearer Token を指定する画面が出る場合は手順 1 のトークンを貼る。

> note: claude.ai の Custom Connector UI は Anthropic 側の更新で項目名が変わる場合がある。 「Authorization Header」 や 「Bearer Token」 等の input があればそこにトークンを貼る。 OAuth しか選べない場合は、 server 側の auth を OAuth フローに置き換える必要があるが、 現状の Bearer token サポート前提で進めて問題ない。

4. **Add** → connector が一覧に出れば成功

### 7. iOS Claude アプリで動作確認する

1. iPhone Claude アプリを再起動
2. claude.ai 側の設定が **自動同期** される (mobile 側で個別設定は不要)
3. 任意のチャットで以下を試す:

```
claude-history で過去会話の statistics を見せて
```

→ `history_stats` が呼ばれ、 conversation 件数 + index size 等が返ってくれば成功。

```
claude-history で MUEDear ASC 提出について話したやり取りを検索して
```

→ `conversation_search` が呼ばれ、 関連 conversation の snippet が返る。

## トラブルシューティング

| 症状 | 原因と対処 |
|------|----------|
| iOS app で connector が見えない | claude.ai 側で connector 追加直後は同期に数十秒。 iOS アプリ完全終了 → 再起動。 |
| 401 unauthorized | トークン不一致。 Mac 側 env var と claude.ai 設定のトークンを再確認。 余分な空白や改行が混入していないか。 |
| 502 / 504 Cloudflare error | server (uvicorn) が止まっている、 または cloudflared が停止。 `lsof -i:8000` と `cloudflared tunnel list` を確認。 |
| `history_stats` で `total_conversations: 0` | Mac 側 `~/.claude/projects/` が読めていない。 server 起動 user の権限を確認。 |
| ツールが呼ばれない | tool name の prompt 表現が曖昧。 「claude-history という connector を使って...」 と explicit に呼ぶ。 |
| 再起動後 server が落ちている | uvicorn を `launchd` plist or `brew services` で常駐化する余地。 本書 scope 外、 必要なら別 issue 起案。 |

## セキュリティに関する注意

- Claude Code 履歴には project secrets / proprietary code / financial discussion 等のセンシティブ情報が含まれる可能性が高い
- Bearer トークンを定期的に rotation する (推奨: 3 ヶ月毎)
- トークンを git に commit しない (`.env` ファイルは `.gitignore` 配下にあることを確認)
- Cloudflare Tunnel は origin IP (kimny Mac) を隠すが、 トークンが漏れれば誰でも履歴を読める。 漏れたと思ったら即時 rotation
- 将来検討: Cloudflare Access (zero-trust SSO で Google account 必須化) を被せると、 トークン漏洩時も外部からは到達不可になる

## 廃止 / rollback

iOS 統合を止めたい場合:

1. claude.ai → Settings → Connectors → claude-history → Remove
2. `cloudflared tunnel delete claude-history`
3. Mac 側 server を `export MCP_TRANSPORT=stdio` (または env 解除) で起動し直す → 通常の Claude Code / Claude Desktop 統合に戻る

## 関連

- [Anthropic: Get started with custom connectors using remote MCP](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp)
- [Anthropic: Building Custom Integrations via Remote MCP Servers](https://support.anthropic.com/en/articles/11503834-building-custom-integrations-via-remote-mcp-servers)
- `mcps/claude-history/README.md` — local stdio 設定手順 (Claude Code / Claude Desktop)
- `mcps/claude-history/cloudflared-config.example.yml` — Cloudflare Tunnel 設定 template
