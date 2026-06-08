# Template MCP Distribution Manifest — peer → MCP mapping

最終更新: 2026-06-08 (CCO実行、kimny+conductor 承認済)

鍵を要求する MCP（`mcp-image` / `fal-video`）の **per-peer 配布正本**。
どの課にどの MCP を `-s local` で登録するかをここで管理する。

## 背景 / 不変原則

これらの MCP は cwd の `.env.local`/`.env` から API 鍵を読み、無いと `launch.sh` が `exit 1`
（= Claude Code 起動時 "Connection closed" 警告）になる。

- **`-s user`（user scope）で登録してはならない。** user scope は全プロジェクトで毎回ロードされ、
  鍵を持たない大多数の課で毎起動ごとに警告を出す（cosmetic だがノイズ＋有料 API の無駄ロード）。
  2026-06-08 にこの理由で `mcp-image` / `fal-video` を user scope から除去した。
- **`-s project`（`.mcp.json` コミット）も使わない。** リポジトリにコミットされ全クローンへ再伝播し、
  鍵パス露出＋他課への再蔓延で振り出しに戻る。
- **必ず `-s local`**（`~/.claude.json` の `projects[<peer-dir>].mcpServers` に入る。非コミット、当該 peer のみ）。
- **canonical パス = `/Volumes/strage/_DevProjects/claude-code-template/mcps/...`**（Dropbox パスは使わない）。

## 反映タイミング

MCP config はセッション起動時のみ読込。**running 中の peer には即時反映されず、次回再起動でクリーンになる。**
警告は cosmetic ゆえ即時の peer 再起動は不要（次回フル再起動で解消）。

## マッピング（正本）

| MCP | 機能 | 鍵 | 登録する課（`-s local`） |
|-----|------|-----|------------------------|
| `mcp-image` (nano-banana-pro) | Gemini 画像生成 | `GEMINI_API_KEY` | LP / write / SNS |
| `fal-video` | fal.ai 画像＋動画生成 | `FAL_KEY` | （なし — 誰にも登録しない） |

### mcp-image 登録先（3課）

| 課 | peer-dir | 鍵保有 |
|----|----------|--------|
| LP | `/Volumes/strage/_DevProjects/_LandingPage/glasswerks-lp` | `.env.local` GEMINI_API_KEY ✅ |
| write | `/Volumes/strage/_DevProjects/_contents-writing` | `.env.local` GEMINI_API_KEY ✅ |
| SNS | `/Volumes/strage/_DevProjects/mued/threads-api` | `.env` GEMINI_API_KEY ✅ |

**除外**: mued/native は GEMINI 鍵を持つが用途=アプリコード（画像 MCP ではない）→ 登録しない。

### fal-video

- 動画生成を実使用する課が現状存在しない（候補 blender/SNS だが未稼働）ため **誰にも登録しない**。
- occur は `FAL_KEY` を持つが音声用途であり fal-video MCP（画像＋動画）とは無関係 → 登録しない。
- blender は対象外（kimny 判断: Blender + AI3D 中心で Gemini 画像/fal 動画は使わない。鍵追加なし）。
- 将来 blender/SNS 等が動画生成を始める場合のみ、当該 peer-dir に `FAL_KEY` を用意した上で
  下記コマンド（`fal-video` / `mcps/fal-video/launch.sh`）で `-s local` 追加する。

## 再現コマンド集

```bash
CANON="/Volumes/strage/_DevProjects/claude-code-template/mcps/nano-banana-pro/launch.sh"

# user scope に誤登録があれば除去（二度と user scope に入れない）
claude mcp remove mcp-image -s user 2>/dev/null
claude mcp remove fal-video -s user 2>/dev/null

# mcp-image を 3課に local 登録（各 peer-dir で実行）
( cd /Volumes/strage/_DevProjects/_LandingPage/glasswerks-lp && claude mcp add mcp-image -s local -- "$CANON" )
( cd /Volumes/strage/_DevProjects/_contents-writing       && claude mcp add mcp-image -s local -- "$CANON" )
( cd /Volumes/strage/_DevProjects/mued/threads-api        && claude mcp add mcp-image -s local -- "$CANON" )
```

検証:

```bash
python3 -c "import json; d=json.load(open('$HOME/.claude.json')); \
print('root:', list(d.get('mcpServers',{}).keys())); \
[print(p,'->',list((c.get('mcpServers') or {}).keys())) \
 for p,c in d['projects'].items() if (c.get('mcpServers') or {}).get('mcp-image')]"
```

期待: root に `mcp-image`/`fal-video` 無し、上記3 peer-dir のみ `mcp-image` local。

## 注記

- `fal-video` は README 不在（`mcps/fal-video/launch.sh` のみ）。将来配布する場合は README 整備を要す。
- setup.sh の MCP 案内は `-s local` 推奨＋本マニフェスト参照に更新済（2026-06-08）。自動登録(B案)は見送り。
