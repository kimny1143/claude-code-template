# グローバル allowlist 拡張 設計案 — 2026-05-29

**起案**: CCO / **dispatch**: conductor Tier 3 (kimny GO 2026-05-29) / **目的**: peer 許可待ち stuck 解消 (完全 bypass はしない、安全網維持)
**process**: 設計先行 → conductor review → 適用。`~/.claude/settings.json` は user-global = backup 推奨。

## 1. find 確認 (現状実態)

### 現 `~/.claude/settings.json` allow (抜粋)
- 広域: `Bash(*)` `Read(*)` `Edit(*)` `Write(*)` `Glob(*)` `Grep(*)` `WebSearch(*)`
- WebFetch: **3 domain のみ** (github.com / modelcontextprotocol.io / code.claude.com)
- MCP: **server 別 enumerate** (claude-peers/claude-in-chrome/mcp-image/freee-mcp/mued-hoo/scheduled-tasks/mued_material_generator/tokoroten/dropbox/github/mcp-registry = `mcp__server__*`)。ただし **Gmail は個別2 tool のみ** (`gmail_search_messages`/`gmail_read_message`)、Calendar/Drive/blender/claude-history は **未登録**
- **Task/Agent/TodoWrite/NotebookEdit = なし**

### deny (global 12 件)
- Read: ~/.ssh ~/.gnupg ~/.aws ~/.azure ~/.kube ~/.npmrc ~/.git-credentials gh/hosts.yml
- Write/Edit: ~/.ssh ~/.gnupg ~/.aws ~/.bashrc ~/.zshrc
- Bash: rm -rf / ~ /* / git push --force(-f/--force-with-lease) main・master
- (conductor 言及の「24件」= global 12 + template/conductor local 各 8 + validate-dangerous-ops hook 内部 pattern の合算と推定)

### ⚠️ 重要 finding: validate-dangerous-ops hook は **template 課のみ**
- PreToolUse の `validate-dangerous-ops-v2.sh` は **template の `.claude/settings.local.json` にのみ wired**。
- **dsp / occur = hooks 空 ([])**、conductor = SessionStart のみ。→ 大半の peer に **validate-dangerous-ops の安全網が存在しない**。
- global `~/.claude/settings.json` の PreToolUse は **audit ログ hook のみ** (tool-audit.jsonl 追記、block 機能なし)。
- = conductor 依頼の「PreToolUse hook の安全網は維持」は、**そもそも fleet 全体には存在していない**。allow を広げる今こそ、安全網を実体化すべき。

### thin peer
- occur local allow=2 / dsp=20 / blender=10。だが **global allow が全 peer に union 適用**されるため、stuck の原因は global 側の穴 (MCP 未網羅 / WebFetch domain / Task・Agent 無) → **global 拡張で thin peer も同時に解消** (top-up 不要)。

## 2. Claude Code 公式仕様確認 (claude-code-guide 照会済)

| 項目 | 結論 |
|------|------|
| **permission hot-reload** | **YES** — `permissions`/`hooks` は file watcher で **即時反映、restart 不要** (docs 明記)。conductor の restart 回避要件 = **クリア** |
| `mcp__*` (全 server wildcard) | **無効**。server 別 `mcp__<server>__*` を enumerate する (現 config と同形式) |
| `WebFetch(*)` | 無効。正しくは **`WebFetch(domain:*)`** (全 domain) |
| Task/Agent | subagent spawn = **`Agent`** (`Task` は deprecated alias)。bare `Agent` で全許可 |
| TodoWrite | **deprecated** (v2.1.142~) → `TaskCreate`/`TaskGet`/`TaskList`/`TaskUpdate` |
| NotebookEdit | 有効な tool 名 |
| merge | user < project < local < managed、allow/deny とも **union**。**deny 優先** (deny→ask→allow、first match) |
| deny の挙動 | **hard silent block** (prompt でなく完全遮断)。→ deny した tool は peer が **一切使えない** |

## 3. 提案: allow 追加エントリ (`~/.claude/settings.json` permissions.allow)

```
"WebFetch(domain:*)",            // 3 domain → 全 domain (列挙運用負荷を解消)
"Agent",                          // subagent spawn (Task の正式名)
"NotebookEdit",                   // .ipynb 編集
"TaskCreate", "TaskGet", "TaskList", "TaskUpdate", "TaskStop", "TaskOutput",  // 新 task tool 群
"TodoWrite",                      // 旧版互換 (deprecated だが無害)
"mcp__claude_ai_Gmail__*",        // 現状 2 tool のみ → 全 tool
"mcp__claude_ai_Google_Calendar__*",
"mcp__claude_ai_Google_Drive__*",
"mcp__blender__*",
"mcp__claude-history__*"
```

- 既存の個別 Gmail 2 エントリ (`gmail_search_messages`/`gmail_read_message`) は `mcp__claude_ai_Gmail__*` に包含 → 重複だが無害 (残置可)。
- 既存の他 server `mcp__<server>__*` は維持。
- **`mcp__*` 単一 wildcard は使わない** (公式無効)。= 将来新規 MCP server は 1 行追加が必要 (low-freq、許容)。periodic に `claude mcp list` と allow の差分を確認する運用を recommend。

## 4. 安全網の維持・強化 (conductor 「deny + hook 維持」への回答)

1. **deny 12 件 = 不変** (削らない)。
2. **MCP destructive tool を deny に追加しない** — deny = hard block ゆえ、`freee_api_delete` 等を deny すると当該 peer が正当な削除も**一切できなくなり新たな stuck/block 化**。不可逆 MCP op は block16 external-resource-gate (将来 hook) + peer judgment + 起案 gate で覆う方針。allow 拡張では deny を増やさない。
3. **★recommend: validate-dangerous-ops-v2.sh を global PreToolUse に wiring** — 現状 template のみ → global 化で **全 peer に Bash/Write/Edit 安全 block を付与**。allow を広げる今、これが「安全網維持」の実体。hook も hot-reload 対象 (restart 不要)。別 step / 慎重適用 (絶対 path 確認、stdin JSON、exit code)。

## 5. 反映方法

- **restart 不要** (hot-reload)。手順: ① `cp ~/.claude/settings.json ~/.claude/settings.json.bak-20260529` (backup)、② allow に §3 追記、③ JSON 妥当性確認 (`python3 -m json.tool`)、④ 直前 stuck だった 1 tool で live 反映確認。
- deny / hook は §4-3 を採用する場合のみ別 step。

## 6. ⚠️ validate-dangerous-ops global 化の rollout 診断 (naive fleet apply 不可)

global wiring すると、hook の **「CWD 外 Write/Edit block」が全 peer に適用**される。現 allowlist 例外 (CWD 外でも許可) = `~/.claude/projects/*/memory/` + conductor `docs/drafts/`・`docs/inbox/` + contents-writing `drafts/` + videos + `~/.claude/plans/`。

正当 pattern の被覆:
- ✅ cowork cron → conductor inbox / peers → conductor drafts・inbox / memory / plans = allowlist 済
- ✅ 各 peer の自 repo 内 Write = CWD 内ゆえ block されない
- ⚠️ **monorepo sub-peer の親 dir write**: native は CWD=`mued_v2/apps/`。親 `mued_v2/` 配下への Write は CWD 外 → **block される**。native が親 level file を触る pattern があれば破綻。
- ⚠️ allowlist 外の共有 dir / tmp への Write tool 利用がある peer も block 対象

→ **global hook wiring は naive fleet apply 不可**。phased rollout 推奨: ① allow 拡張のみ先行 (安全・即効)、② validate-dangerous-ops は (i) 各 peer の cross-dir write pattern を監査 → (ii) 必要な allowlist path を追補 → (iii) 1-2 peer trial → (iv) fleet。特に native(apps/) 監査必須 (`feedback_hook_allowlist_core_path_check` 型 deadlock 回避)。

→ option 修正: **(a') allow 拡張は即適用可 / validate-dangerous-ops global 化は別 step で phased**。allow と hook を厳密に「同時セット」にこだわらず、安全網は phased で確実に。

## 7. apply 手順 appendix (GO 後実行用、確定)

### 7.1 allow 拡張 (即効・安全)
~/.claude/settings.json は CWD 外ゆえ Edit tool は自 hook で block → **Bash + python で適用**:
```bash
cp ~/.claude/settings.json ~/.claude/settings.json.bak-20260529   # backup
python3 - <<'PY'
import json,os
p=os.path.expanduser("~/.claude/settings.json")
d=json.load(open(p)); allow=d["permissions"]["allow"]
add=["WebFetch(domain:*)","Agent","NotebookEdit",
     "TaskCreate","TaskGet","TaskList","TaskUpdate","TaskStop","TaskOutput","TodoWrite",
     "mcp__claude_ai_Gmail__*","mcp__claude_ai_Google_Calendar__*",
     "mcp__claude_ai_Google_Drive__*","mcp__blender__*","mcp__claude-history__*"]
for a in add:
    if a not in allow: allow.append(a)
json.dump(d,open(p,"w"),ensure_ascii=False,indent=2)
print("allow:",len(allow))
PY
python3 -m json.tool ~/.claude/settings.json >/dev/null && echo "JSON OK"
```
→ hot-reload (restart 不要)。直前 stuck だった 1 tool で live 確認。

### 7.2 validate-dangerous-ops global 化 (§6 phased、別 step)
§6 の監査 → allowlist 追補 → trial 後に global PreToolUse へ追加 (絶対 path、matcher "*")。本 step は allow 拡張完了後に別途。

## 8. conductor への確認事項

§3 allow 追加 (即適用 candidate) + §6 の hook phased 方針 + §7 apply 手順で、kimny GO 後に進めてよいか。allow と hook を strict セットにせず allow 先行・hook phased を推奨 (§6)。
