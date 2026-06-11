# Chief (参謀) governance 設定 — hook + settings deny (draft) — 2026-06-11

- 起案: CCO、conductor 依頼 (c) / org再編 v2。Codex 実査反映: 「hook だけでは不足 (Bash cp/mv/rm/git・Chrome・send_message が開いたまま)」→ **hook + settings deny の二層**で「書けない・できない構造」を作る。
- 目的: §2.1「参謀は _strategy(_chief) のみ書く / dispatch しない / 指揮権なし」を機構保証。

## 二層構造

| 層 | 何を止めるか | 実装 |
|---|---|---|
| **層1: hook** (作成済) | Write/Edit の cwd 外書込 | `.claude/hooks/chief-cwd-write-guard.sh` (PreToolUse Write\|Edit、cwd外block、core-path allowlist) |
| **層2: settings deny** | Bash 変更系 / git 変更系 / Chrome / 外部write MCP / secrets read | `_chief/.claude/settings.local.json` permissions.deny |

※ **send_message は deny しない**（後述「送信の扱い」。指揮権なしは規約 + 透明性で担保）。

層1だけでは Bash 経由の out-of-cwd 書込・外部アクションが素通り (Codex 指摘) → 層2 で塞ぐ。

## 層1: hook (作成・テスト済)

`.claude/hooks/chief-cwd-write-guard.sh` (template canonical)。挙動テスト (echo JSON) 全 pass:
- cwd 内 Write → 許可 / peer inbox・peer status.md → block (exit2) / `~/.claude/plans/`・自 memory → 許可 (deadlock 回避) / Bash → 対象外 (層2 が担当)。
- ★ fleet の validate-dangerous-ops-v2 と違い **conductor inbox/drafts を allowlist しない** = Chief は運用ファイルに直接書かない。

## 層2: `_chief/.claude/settings.local.json` permissions.deny (設計)

```jsonc
{
  "permissions": {
    "deny": [
      // --- Bash ファイル変更系 (hook の out-of-cwd 書込 gap を塞ぐ) ---
      "Bash(rm:*)", "Bash(cp:*)", "Bash(mv:*)", "Bash(tee:*)",
      "Bash(dd:*)", "Bash(install:*)", "Bash(ln:*)", "Bash(truncate:*)",
      // --- git 変更系 (Chief は commit/push しない = 成果物は _strategy/ ファイルのみ) ---
      "Bash(git push:*)", "Bash(git commit:*)", "Bash(git merge:*)",
      "Bash(git rebase:*)", "Bash(git reset:*)", "Bash(git checkout:*)",
      "Bash(git add:*)", "Bash(git stash:*)", "Bash(git restore:*)",
      // --- Chrome (外部ブラウザ操作 = Chief は思考相手、操作しない) ---
      "mcp__claude-in-chrome__*",
      // --- 外部 write MCP (Gmail送信/Drive作成/Calendar作成/freee書込 = 外部副作用) ---
      "mcp__claude_ai_Gmail__create_draft", "mcp__claude_ai_Gmail__label_message",
      "mcp__claude_ai_Google_Drive__create_file", "mcp__claude_ai_Google_Drive__copy_file",
      "mcp__claude_ai_Google_Calendar__create_event", "mcp__claude_ai_Google_Calendar__update_event",
      "mcp__claude_ai_Google_Calendar__delete_event",
      "mcp__freee-mcp__freee_api_post", "mcp__freee-mcp__freee_api_put",
      "mcp__freee-mcp__freee_api_patch", "mcp__freee-mcp__freee_api_delete",
      // --- send_message は deny しない (allow)。指揮権なしは規約で担保。下記「送信の扱い」参照 ---
      // --- secrets read 除外 (Chief は機密を読まない) ---
      "Read(//**/.env)", "Read(//**/.env.*)", "Read(//**/*credential*)",
      "Read(//**/*secret*)", "Read(//**/*.pem)", "Read(//**/*.key)",
      "Read(//**/id_rsa*)", "Read(//**/.ssh/**)"
    ]
  }
}
```

### ★ send_message の扱い — **allow + no-dispatch 規約 (conductor/kimny 訂正 2026-06-11)**
- **当初案 (deny + file queue) は撤回**。理由 (kimny 指摘): claudepeers 起動 = ネットワーク接続済なのに send_message を全 deny すると「繋がっているのに喋れない」分断状態 = Chief の存在意義 (conductor と情報共有しながら kimny の思考相手をする) を壊す。
- settings は送信先で allow/deny を分けられない (send_message は to_id 引数1つ)。禁止すべきは「Chief が実装ピアに命令する (conductor 二重化)」だけで、**通信遮断ではない**。
- **採用 = `mcp__claude-peers__send_message` を allow** (deny リストから除外)。指揮権なしは下記2点で担保:
  1. **規約**: Chief CLAUDE.md に「send_message は conductor / kimny への質問・ブリーフのみ。実装ピアへの作業指示 (dispatch) は出さない」を明記 (= canonical)。
  2. **透明性**: 受信側は `from_id = Chief (fog4hwch)` を見て、作業指示なら conductor 経由を促せる。
- **`_chief/for-conductor/` file queue は残置** = 送信の代替ではなく**補完** (重いブリーフの durable 置き場)。Chief cwd 内ゆえ層1 hook の cwd-allow に自然に収まる (別途 allowlist 不要)。

### 既知の残課題 (層1+層2 後も残る)
- Bash の任意 redirect (`> /path`, `python -c "open(...,'w')"`) は pattern deny で全網羅困難。→ Chief の Bash 自体を絞る (read-only コマンドのみ allow リスト化) のが最終形。当面は層1(Write/Edit)+層2(主要変更コマンド deny)で実務上の governance は成立、Bash 任意書込は「low-likelihood + conductor 監視」で受容。初週レビューで観測。

## wiring 順序 (conductor/CCO)

1. `_chief` workspace 作成 (git ローカルのみ、外部リソースゼロ)。
2. hook を template から `_chief/.claude/hooks/` へ copy/symlink + settings.local.json に PreToolUse wire。
3. 上記 deny を `_chief/.claude/settings.local.json` に設定。
4. `_chief/for-conductor/` queue ディレクトリ作成 (重いブリーフの durable 置き場・send_message の補完)。
5. Chief CLAUDE.md に役割・読む層・書く層・指揮権なし・kimny relay 経路を明文化。
6. 起動 = `claudepeers --model fable` (on-demand、常時起動群に入れない)。

## CCO 分担確認
- hook 作成・テスト = CCO 済。
- settings deny 設計 = CCO 本書。実 wire は _chief 作成時 (conductor/CCO)。
- `_product` 初期 CLAUDE.md = conductor 朝起草 → CCO が marker 挿入・配布 (別タスク)。
