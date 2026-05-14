# Blender MCP — CCO peer setup + swap運用 runbook

最終更新: 2026-05-15
担当: CCO peer (`claude-code-template` workspace)
upstream: [ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp) (community版)
trigger: conductor dispatch #16 (2026-05-14 21:39 JST、 Blender + Claude Desktop sprint 1日目達成を受けた peer化要望)

## 目的

kimny attention workload削減。 Hoo brand identity mapping等の Blender自動化を CCO peer自走で回せるようにする (`feedback_zero_kimny_manual_work.md` 整合)。

## 前提

- macOS (Darwin)
- Blender 3.0+ install済
- `uvx` 利用可能 (本machineは `~/.local/bin/uvx` 0.10.4)
- Claude Desktop に既存 Blender MCP connector (Anthropic公式) active

## 構成 overview

```
                     ┌──────────────────────────┐
                     │  Blender app (kimny GUI) │
                     │  + addon.py (port 9876)  │← socket server
                     └─────────────▲────────────┘
                                   │ TCP localhost
              ┌────────────────────┴────────────────────┐
              │                                         │
      ┌───────┴──────────┐                    ┌─────────┴─────────┐
      │ Claude Desktop   │                    │ CCO peer (CC CLI) │
      │  blender-mcp     │     ✕排他          │  uvx blender-mcp  │
      │  (公式 connector)│ 同時接続不可        │  (community版)   │
      └──────────────────┘                    └───────────────────┘
```

**critical constraint** (upstream README L164):
> ⚠️ Only run one instance of the MCP server (either on Cursor or Claude Desktop), not both

同時接続すると Blender addon の socket server (port 9876) で port衝突 → 後発接続が失敗 or 前者が drop。 必ず swap運用。

## Setup手順

### Step 1: prerequisite verify (CCO自走済)

```bash
uvx --version           # 0.10.4 OK
curl -fsSL -o /dev/null -w "%{http_code}" \
  https://raw.githubusercontent.com/ahujasid/blender-mcp/main/addon.py   # 200
```

### Step 2: addon.py 取得 (CCO自走済)

addon.py は CCO peer workspace の `vendor/blender-mcp/addon.py` に取得済 (111925 bytes, bl_info version 1.2)。

```bash
ls -la /Users/kimny/Dropbox/_DevProjects/claude-code-template/vendor/blender-mcp/addon.py
```

### Step 3: Blender app に addon install (kimny manual必須 — 約3min)

CCO peer から GUI操作不可のため **kimny作業**:

1. Blender app を起動
2. Edit → Preferences → Add-ons
3. 右上 "Install..." button click
4. file picker で `~/Dropbox/_DevProjects/claude-code-template/vendor/blender-mcp/addon.py` を select
5. install後、 "Interface: Blender MCP" の checkbox を ON にして enable
6. Preferences 閉じる
7. 3D Viewport sidebar (`N` key で開閉) → "BlenderMCP" tab が表示されること確認
8. **この段階では "Connect to Claude" は押さない** (CCO peer接続準備完了後に押す)

確認 ack: kimny → CCO peer に「Blender addon enabled、 sidebar tab確認済」 1行返信。

### Step 4: CCO peer に blender MCP server 登録 (実施済 2026-05-15 06:45 JST)

conductor #16 judgment: **option B (project-scope `.mcp.json`) + `.gitignore` (CCO peer local only)** 採用 (2026-05-14 21:42 JST、 Tier 1 self-merge承認)。

#### 実行command (実施済)

```bash
claude mcp add --scope project blender -e DISABLE_TELEMETRY=true -- uvx blender-mcp
```

生成 file: `claude-code-template/.mcp.json`
```json
{
  "mcpServers": {
    "blender": {
      "type": "stdio",
      "command": "uvx",
      "args": ["blender-mcp"],
      "env": { "DISABLE_TELEMETRY": "true" }
    }
  }
}
```

#### `.gitignore` 追加 (実施済)

```
# Blender MCP — CCO peer local setup
.mcp.json
vendor/blender-mcp/
```

検証:
```bash
$ git check-ignore -v .mcp.json vendor/blender-mcp/addon.py
.gitignore:12:.mcp.json        .mcp.json
.gitignore:13:vendor/blender-mcp/    vendor/blender-mcp/addon.py
```

#### scope 選定根拠 (記録)

| option | 場所 | 効果 | swap適合 | 判断 |
|--------|------|------|---------|------|
| A. user (default) | `~/.claude.json` | 全 workspace で起動時接続試行 | ✕ Claude Desktop active 時 全 CC session で port競合 risk | 不採用 |
| B. project | `.mcp.json` (CCO peer workspace) | CCO peer workspace のみ active | ◎ swap = workspace切替で自動排他 | **採用** |
| C. local (manual jsonc) | `.claude/settings.local.json` | **Claude Code仕様外** | — | 不採用 (原 conductor指示、 仕様乖離 catch) |

`.mcp.json` を `.gitignore` 対象とした理由:
- template利用者全員に Blender MCP server config配布 = unintended dependency (Blender install + uvx 必要)
- CCO peer own Blender sprint運用に限定 (5/15-5/22)
- template利用者向け documentation性は 本 doc + 別途 `.mcp.json.example` で「Blender MCP setup optional」として後日明文化 OK (separate task)

### Step 5: Swap手順 (Claude Desktop ↔ CCO peer)

#### Claude Desktop → CCO peer 切替

1. Blender app の BlenderMCP sidebar tab で "Disconnect" click (もしくは Claude Desktop quit)
2. Claude Desktop app を quit (menu bar → Claude → Quit Claude、 Cmd+Q)
3. `ps -ef | grep blender-mcp` で残 process なし確認
4. (CCO peer session) 既に起動中なら restart 不要、 そうでなければ Claude Code CLI 起動
5. Blender app の BlenderMCP sidebar → "Connect to Claude" click
6. CCO peer から `mcp__blender__*` tool で test 接続 (Step 6参照)

#### CCO peer → Claude Desktop 切替

1. CCO peer session 中の blender操作完了確認
2. Blender app の "Disconnect" click
3. (CCO peer 側でなにもしない、 自動で MCP 接続切れる)
4. Claude Desktop 起動 → 自動で公式 connector 再接続

### Step 6: test connection verify

CCO peer 接続後、 簡単な操作で疎通確認:

```
kimny prompt: "Blender の現在 scene info を教えて"
expected: mcp__blender__get_scene_info tool が hammer icon で利用可能、
         tool call成功 + JSON response (objects list / camera position等) 返却
```

応用 test:
```
"原点に半径1の sphere を作成して"
→ mcp__blender__execute_blender_code or 専用 create_sphere tool 経由で生成、
  viewport で確認可
```

## Telemetry policy

upstream addon は anonymized usage data 収集 default ON。 CCO運用 policy として **DISABLE推奨**:

- 環境変数: `DISABLE_TELEMETRY=true` を MCP server config の `env` に追加 (Step 4 command参照)
- Blender app側: Edit → Preferences → Add-ons → Blender MCP の telemetry consent checkbox uncheck

## Security note

upstream README L245 に明記:
> The `execute_blender_code` tool allows running arbitrary Python code in Blender, which can be powerful but potentially dangerous.

CCO peer が `execute_blender_code` 経由で任意 Python実行可能 = Blender process権限で file system access等が走る。 運用時 注意点:
- 作業前に Blender file save必須 (kimny作業時の hint)
- 自走で `execute_blender_code` を多用する skill / workflow を組む際は kimny承認 (Tier 2以上)

## Troubleshooting

| 症状 | 原因 | 対処 |
|------|------|------|
| `uvx blender-mcp` が package fetch遅延 | 初回 PyPI fetch | 30-60sec 待つ、 二回目以降は cache |
| "Connection refused" | Blender addon の "Connect to Claude" 未押下 | Blender sidebar で接続 |
| port 9876 in use | Claude Desktop が既に接続中 | swap手順実行 |
| addon が sidebar に出ない | enable check漏れ | Preferences → Add-ons で "Blender MCP" 検索、 check ON |

## CCO peer 側 daily TODO (sprint 5/15-5/22)

- [x] Step 1-2 完了 (CCO 5/15 06:41 JST)
- [x] Step 4 config登録 (5/15 06:45 JST、 option B + .gitignore)
- [ ] Step 3 addon install (kimny manual、 5/15朝予定)
- [ ] Step 6 test connection (kimny addon enable後 immediate、 Claude Desktop quit前提)
- [ ] sprint中 swap 3回以上 smooth実行確認
- [ ] kimny attention workload削減 measure (sprint EOD report)

## 関連 reference

- upstream repo: https://github.com/ahujasid/blender-mcp
- upstream README: https://raw.githubusercontent.com/ahujasid/blender-mcp/main/README.md
- Anthropic公式 Blender connector (Claude Desktop): kimny既設定済
- handoff: `memory/project_handoff_20260511.md` (CCO 5/10 EOD)
- 整合: `feedback_zero_kimny_manual_work.md` (kimny workload削減 principle)
