# settings.json ↔ Claude Code 権限仕様 監査レポート — 2026-07-17

- **起案**: template課 / CCO
- **依頼元**: conductor brief `_conductor/docs/inbox/brief-settings-permission-audit-20260717.md`
- **Tier**: 3 — **kimny 承認前提。適用は承認後。**
- **実行様式**: kimny 指示により Fable サブエージェント (`Agent(model:"fable", subagent_type:"claude-code-guide")`) を起動。**サブエージェントは応答が得られなかった**ため、CCO が同等の一次手法 (導入バイナリの enforcement コード直読 + settings を渡した実挙動観測 + 公式 CHANGELOG) で直接確定した。挙動系の主張は**すべてこの機で実測**。
- **status**: ✅ 調査完了。成果物 (A) 監査レポート = 本ファイル / (B) 修正 diff = §6。適用は **kimny 承認後**。

> **本レポートの方針**: security 案件ゆえ、**一次情報で確定した事実**と**未確定の仮説**を明示的に分離する。断定できない点は「未確定」と書く (§7)。挙動の主張には「実証」と付す = この機で実際に write/read を走らせて観測した。

---

## 0. TL;DR

1. ★**実害の核心を実測で確定**: deny `Write(~/.ssh/**)` の形は**本当に効かない** — sentinel に `--permission-mode acceptEdits` で書込を走らせたら**成功した**。`Edit(~/.ssh/**)` の形に変えると**block された**。→ conductor 分析 (鍵・認証情報への書込/改変/不正鍵設置が permission 層で拒否されていない) は**推測でなく事実**。読取は `Read(...)` deny が有効ゆえ**抜き取りは防げている** (これも実測)。
2. ★risk framing は **「全ピア一律に開いている」ではない**。`validate-dangerous-ops-v2.sh` (PreToolUse) が **CWD 外への Write/Edit を一律 block** するため、**hook が wire されている 8 workspace では塞がっている**。**素で開いているのは hook 未 wire の 7 workspace** (★**_conductor 自身を含む**)。
3. **security fix は global settings.json 1枚で足りる** (deny 側の死にルールは global のみ)。`Write(*)` は**死にルールではなく有効な tool 単位 allow** と実証ゆえ、**配布物の掃除は不要**。
4. **version**: 導入バイナリ = **2.1.212**。死にルール warning は **2.1.210 で追加** (CHANGELOG)。warning を出した 7/17 ピアは ≥2.1.210 稼働 (2.1.203 バイナリに warning 文字列なし=実測)。brief の env `2.1.203` は古い値。
5. ★**path 記法 gotcha (実証)**: deny は必ず `~/...` (tilde) か `//...` で書く。**単一スラッシュ `/Users/...` は settings dir 相対に解決され黙って無効**。修正 diff は tilde 形を使用 (実証済に効く)。
6. 恒久 fix は 2層: **layer1 = global deny 修復** (即効・全 workspace 適用) / **layer2 = hook 配布ムラ解消** (CCO 領域・defense in depth)。

---

## 1. 対象バージョンの確定

| 観測点 | 値 | 根拠 |
|---|---|---|
| 導入バイナリ (現行) | **2.1.212** | `claude --version` + `~/.local/bin/claude` symlink |
| 導入履歴 | 2.1.202 / 2.1.203 / 2.1.212 が併存 | `~/.local/share/claude/versions/` |
| brief 記載の env | 2.1.203 | 稼働プロセス env。**古い値** (下記) |

**解釈**: warning 文字列はバイナリ実測で **2.1.202 / 2.1.203 に無く 2.1.212 に有り** (CHANGELOG では 2.1.210 追加)。→ 7/17 に warning を出したピアは **≥2.1.210 で稼働していた**はずで、env `2.1.203` は auto-update とズレた古い値。**どの版でも結論 (`Write(path)` 死に) は同じ**ゆえ、本監査は現行 **2.1.212 基準**で確定。
**含意 (C 向け)**: 起動時の警告行数は**版によって変わり得る** (2.1.210 で 0→8 に増えた実例そのもの)。起動スクリプト Phase 2 の「`delay 8` + 固定行数前提」は原理的に脆く、settings 整理で警告が消えても**行数依存のままなら別の版で再発し得る**。conductor と独立に確認・合意済 (§C で堅牢化)。

---

## 2. 仕様照合 (一次情報 — 実証済)

> **照合方法**: (1) 導入済バイナリ `~/.local/share/claude/versions/{2.1.202,2.1.203,2.1.212}` の enforcement コードを直接 strings 抽出 (2) **実際に settings を渡して claude を走らせ、write/read が通るか通らないかを観測** (3) 公式 CHANGELOG (`~/.claude/cache/changelog.md`)。
> Fable サブエージェント (`claude-code-guide`) は応答が得られなかったため、CCO が上記一次手法で直接確定した。**推測ではなく、この機で観測した挙動**。

### (a) ★`Write(<path>)` は file permission check で **完全に死んでいる** — 実証

sentinel path で実測。`--permission-mode acceptEdits` 下:

| deny ルール形式 | Write ツールでの書込 | 結果 |
|---|---|---|
| `deny: Write(~/sentinel/**)` (現行の形) | `~/sentinel/A.txt` へ書込 | ★**成功してしまった** (`PWNED` が書かれた)。deny が**効かない** |
| `deny: Edit(~/sentinel/**)` (修正案の形) | `~/sentinel/B.txt` へ書込 | **BLOCKED**。permission 層で拒否 |

→ conductor 分析を**実測で confirm**。`Write(<path>)` は path 単位照合で無視され、deny を書いても鍵書込みは止まらない。`Edit(<path>)` は Write ツールを含む全ファイル編集をカバーし、deny が効く。

コード根拠 (2.1.212 bundle): rule 検証器が `toolName==="Write"||"NotebookEdit"||"MultiEdit" → "Edit"`, `"Glob" → "Read"` の場合に「path 単位は Edit/Read ルールのみが照合する」warning を返す。パーサ `/^([^(]+)\(([^)]+)\)$/` で `Write(~/.ssh/**)` は `{toolName:"Write", ruleContent:"~/.ssh/**"}` になり、file-permission 照合対象から外れる。

### (b) ★bare `Write(*)` は **tool 単位 wildcard = 有効** (死んでいない) — 実証

`Write(*)` と `Glob(*)` は warning を**出さない** (実測: `Write(**/CLAUDE.md)` 等の path 形は warning を出すが `Write(*)` は無警告)。`*` は path glob ではなく tool 全体の wildcard として扱われる。
→ **allow の `Write(*)` `Edit(*)` はどちらも有効**。§4 の「配布物の `Write(*)` 掃除」は**不要** (死にルールではない)。`Edit(*)` があれば Write もカバーされるため `Write(*)` は厳密には冗長だが、有効な allow ゆえ**放置で害なし** (削除は任意・非 security)。

### (c) ★deny は auto-approve モードでも **絶対優先** — 実証

上表 (b) の Edit(path) deny は `--permission-mode acceptEdits` (編集自動承認モード) 下でも **BLOCK した**。→ deny は permission-mode より先に評価され、auto 承認を上書きする。`auto` mode も同じ precedence モデル (deny 最優先) ゆえ、**deny が生きていれば auto でも鍵書込みは止まる**。裏を返すと (a) の実害は「deny が死んでいるから auto で素通り」であって、precedence の問題ではない。

### (d) `Read(<path>)` deny は本変更の**影響なし** — 実証

`deny: Read(~/sentinel2/**)` で sentinel の中身を Read させたところ **BLOCKED**。→ Read は path 単位照合が生きている。brief の「読み取り (抜き取り) は防げている」は正しい。**修正は write 側 (Edit) の追加のみで足り、Read deny は現状維持でよい**。

### (e) 変更導入バージョン = **2.1.210** (CHANGELOG 確定)

> `## 2.1.210` — *Added a startup warning for `Write(path)`, `NotebookEdit(path)`, and `Glob(path)` permission rules — use `Edit(path)` or `Read(path)` instead*

- warning 文字列はバイナリ実測で **2.1.202 / 2.1.203 に無く、2.1.212 に有り** = 2.1.210 で追加、と整合。
- ★注意: 2.1.210 が追加したのは **warning (可視化)**。`Write(path)` が非強制になった**挙動そのものの変更時期は本調査では未特定** (warning より前から死んでいた可能性が高い)。「死にルールは 2.1.210 で生まれた」ではなく「2.1.210 で**見えるようになった**」が正確。
- ★**incident の version 整合**: warning を出したピア (7/17 起動) は **≥2.1.210 で稼働していた**はず (2.1.203 は warning 文字列を持たない)。brief の env `CLAUDE_CODE_VERSION=2.1.203` は**古い値** (auto-update とのズレ)。現行導入 = 2.1.212。

### (f) ★path pattern の silent-miss gotcha — 実証 (監査で最重要級)

deny を書いても**黙って一致しない**書き方がある。sentinel で実測:

| 書き方 | 解決先 | deny 実効 |
|---|---|---|
| `Edit(~/.ssh/**)` (tilde) | `$HOME/.ssh/**` (絶対) | ✅ **効く** (test B で実証) |
| `Edit(//Users/kimny/.ssh/**)` (**先頭スラッシュ2つ**) | `/Users/kimny/.ssh/**` (絶対) | ✅ **効く** (実証) |
| `Edit(/Users/kimny/.ssh/**)` (**先頭スラッシュ1つ**) | **settings dir 相対** に解決 → 実 path と不一致 | ★**効かない** (実証: 書込が landed) |

コード根拠: `xXc(e,t){ if(e.startsWith("//")) return e.slice(1); if(e.startsWith("/")&&!e.startsWith("//")) return resolve(t, e.slice(1)); return e }`。**先頭 `/` 1個 = settings dir 相対 / `//` = 絶対**。
→ **含意1**: 修正の deny は必ず **`~/...` (tilde)** か **`//...`** で書く。`/Users/...` (単一スラッシュ) で絶対パスのつもりで書くと**黙って無効**。
→ **含意2 (conductor への訂正)**: `_conductor` settings の `Read(//Users/kimny/Dropbox/**)` `Read(//tmp/**)` の double-slash は**バグではなく正しい絶対パス記法**。先に「malformed の疑い」と報告したが、**撤回**する。

### (g) `Write(<path>)` 以外の死に / 無効ルール形式

監査で探すべき他の死にルール:
- `NotebookEdit(<path>)` → `Edit(<path>)` に統合 (死。CHANGELOG 明記)
- `Glob(<path>)` → `Read(<path>)` に統合 (死。CHANGELOG 明記)
- `MultiEdit(<path>)` → `Edit` 統合で死。加えて **`MultiEdit` は "matches no known tool" 扱い** (ツール名として廃止・Edit に吸収)
- 単一スラッシュ絶対パス (§f) = 死にはしないが**意図と違う相対解決**で silent-miss
- **kimny の settings には上記のうち `Write(<path>)` のみ存在** (NotebookEdit/Glob/MultiEdit の path 形は無し)

---

## 3. hook backstop の実測 — 「gap は素で開いているか」

conductor 観点1への回答。**settings 仕様と独立に確定できる**ため先行して確定済。

### 3-1. hook は live (path 切れではない)

peer settings が参照する `/Users/kimny/Dropbox/_DevProjects/claude-code-template/.claude/hooks/validate-dangerous-ops-v2.sh` は実在し、`realpath` = `/Volumes/strage/_DevProjects/claude-code-template/.claude/hooks/validate-dangerous-ops-v2.sh`。
→ `~/Dropbox` は `/Volumes/strage` への **symlink**。ハードコード path は解決する。**hook は発火する**。

### 3-2. hook は鍵書込みに対し実効的な backstop

`validate-dangerous-ops-v2.sh` の Write/Edit 検証パス:

| 行 | 制御 | 鍵書込みへの効果 |
|---|---|---|
| L133-139 | **CWD 外への Write/Edit を一律 block** (allowlist / ownership-map 該当時のみ skip) | `~/.ssh` はどの課の CWD 配下でもない → **block** |
| L152 | `credentials\|secrets\|private[._-]?key\|\.pem\|\.key\|\.p12\|\.pfx` を block | 鍵ファイル名で二重に **block** |

exit 2 = 操作中止。**ただし wire されている workspace でのみ発火**。

### 3-3. ★hook 配布ムラ — 実測 (全 workspace 走査)

| backstop | workspace |
|---|---|
| ✅ **WIRED** (dangerous-ops あり) | `claude-code-template` / `freee-MCP` / `_Reserch` / `_cowork` / `_contents-writing` / `_data-analysis` / `_videos` / `Echovna` |
| ★ **未 wire** (PreToolUse なし) | **`_conductor`** / `_mued-occur` / `_growth` / `_mued-dsp` / `_blender` / `livesheet` / `Solid_Staff_Assign_Management` |
| ⚠️ 実質未 wire | `_chief` (PreToolUse はあるが dangerous-ops 参照 0) |

**結論**: latent gap が**素で開いているのは未 wire の層**。conductor が独立検証で confirm 済 (`_conductor` = `Edit(*)`+`Write(*)` allow / hooks は SessionStart のみ / project deny に ssh 系なし)。

### 3-4. ★最privileged な exposed workspace = _conductor

`_conductor/.claude/settings.local.json` の追加所見 (CCO 実読):
- allow に `Edit(/Users/kimny/Dropbox/_DevProjects/*/.claude/settings.local.json)` (+ `*/*/`, `*/*/*/` の3段) = **他 peer の settings を書き換える権限**を持つ
- PreToolUse の dangerous-ops backstop **なし**
- deny は Bash 系のみ (ssh/gnupg/aws なし)
- 付随: `Read(//Users/kimny/...)` `Read(//tmp/**)` の **double slash** = 意図した pattern と一致しない可能性 (要確認・優先度低)

→ layer2 (hook wire) の**最優先対象**。

---

## 4. scope 完全性 — 死にルールの波及範囲

conductor 観点2への回答。全 workspace の `settings*.json*` を機械走査。

| 分類 | 実測 | security 実害 |
|---|---|---|
| **deny 側 `Write(<path>)`** | **global `settings.json` のみ** | ★**あり** (§0-1) |
| allow 側 `Write(<path>)` | 3件のみ: `claude-code-template` ×2 / `mued/threads-api` ×1 | **なし** (allow ゆえ。同等の `Edit(*)` が既にある) = 単なるノイズ |
| bare `Write(*)` | **遍在** — 全課 settings.local.json + ★**配布テンプレ本体** (`.claude/settings.local.json.example` / `docs/templates/settings-local-base.json` / 全 `project-configs/*/settings.local.json.example`) | **未確定** (§2-b の粒度確定待ち。allow 側ゆえ非緊急) |

**結論**: **security fix は global 1枚で足りる**。
`Write(*)` は §2-b で **tool 単位 wildcard = 有効** と実証されたため、**配布物の掃除は不要** (死にルールではない)。allow 側 `Write(<path>)` 3件のみが死にノイズだが、いずれも同等の `Edit(*)` allow に包含され無害ゆえ、除去は任意 (非 security)。

---

## 5. `/Users/kimny/.claude/settings.json` 全ルール対応表 (2.1.212 解釈)

判定: **有効** = 現行版で照合される / **死に** = 無視される (warning 出) / **冗長** = 有効だが他ルールに包含 / **危険** = 保護の穴。

### allow

| ルール | 判定 | 備考 |
|---|---|---|
| `Bash(*)` `Read(*)` `Edit(*)` `Write(*)` `Glob(*)` `Grep(*)` `WebSearch(*)` | 有効 | tool 単位 wildcard。全許可 |
| `Write(*)` | 有効・**冗長** | `Edit(*)` が Write ツールを包含。削除可・非 security |
| `Edit(**/Dropbox/_DevProjects/**)` `Edit(**/.claude/**)` `Edit(**/CLAUDE.md)` | 有効・**冗長** | `Edit(*)` が全 path を包含済 |
| `Write(**/Dropbox/_DevProjects/**)` `Write(**/.claude/**)` `Write(**/CLAUDE.md)` | ★**死に** | warning 3行の出所。同 path の Edit 版あり=無害ノイズ |
| `WebFetch(domain:github.com)` 他 domain / `mcp__...` 各種 | 有効 | tool 単位 allowlist |

### deny

| ルール | 判定 | 備考 |
|---|---|---|
| `Read(~/.ssh/**)` `Read(~/.gnupg/**)` `Read(~/.aws/**)` `Read(~/.azure/**)` `Read(~/.kube/**)` `Read(~/.npmrc)` `Read(~/.git-credentials)` `Read(~/.config/gh/hosts.yml)` | 有効 | 読取保護は生きている (§2-d 実証) |
| `Write(~/.ssh/**)` `Write(~/.gnupg/**)` `Write(~/.aws/**)` | ★**死に + 危険** | 書込保護が**無効** (§2-a 実証)。`Edit()` 版が無い=**穴** |
| `Write(~/.bashrc)` `Write(~/.zshrc)` | **死に** (無害) | 同 path の `Edit()` deny が別途有効ゆえ実害なし・ノイズ |
| `Edit(~/.bashrc)` `Edit(~/.zshrc)` | 有効 | 書込保護が生きている |
| `Bash(rm -rf /)` `Bash(rm -rf ~)` `Bash(rm -rf /*)` / `Bash(git push --force[-with-lease]/-f * main/master)` | 有効 | Bash prefix/wildcard rule。健在 |

**穴の要約**: 読取は ssh/gnupg/aws/azure/kube + 4 credential file で保護。**書込は ssh/gnupg/aws の deny が死に + azure/kube/npmrc/git-credentials/gh-hosts は write 保護が元から無い**。

---

## 6. 修正案 (B) — 最小差分・可逆・diff 形式

対象: `/Users/kimny/.claude/settings.json` の `permissions` のみ。**加算 (deny 追加) を先に、死にルール除去を後に**。両者独立ゆえ段階適用も可。

### B-1. ★必須 (security) — brief スコープ = ssh/gnupg/aws の書込保護復活

```diff
   "deny": [
     "Read(~/.ssh/**)",
     "Read(~/.gnupg/**)",
     "Read(~/.aws/**)",
     "Read(~/.azure/**)",
     "Read(~/.kube/**)",
     "Read(~/.npmrc)",
     "Read(~/.git-credentials)",
     "Read(~/.config/gh/hosts.yml)",
-    "Write(~/.ssh/**)",
-    "Write(~/.gnupg/**)",
-    "Write(~/.aws/**)",
-    "Write(~/.bashrc)",
-    "Write(~/.zshrc)",
+    "Edit(~/.ssh/**)",
+    "Edit(~/.gnupg/**)",
+    "Edit(~/.aws/**)",
     "Edit(~/.bashrc)",
     "Edit(~/.zshrc)",
```

- `Edit(~/.ssh/**)` 等 = §2-a/2-f で **実証済に効く形** (tilde 絶対 + Edit = Write ツール包含)。
- `Write(~/.bashrc/.zshrc)` 除去 = 既存 `Edit(~/.bashrc/.zshrc)` があり**保護は不変** (死にノイズを消すだけ)。
- 効果: 起動 warning 8→3 行に減り、鍵書込みが permission 層で block される。

### B-2. 推奨追加 (security・対称性) — 読取保護がある path に書込保護も

現状「Read は deny だが Edit(write) は素通り」の path を塞ぐ。credential file への**書込=認証情報の注入/上書き**ゆえ Read 同様に危険。

```diff
+    "Edit(~/.azure/**)",
+    "Edit(~/.kube/**)",
+    "Edit(~/.npmrc)",
+    "Edit(~/.git-credentials)",
+    "Edit(~/.config/gh/hosts.yml)",
```

> ★kimny 判断ポイント: これらへの正当な書込 (例: 別ツールでの `~/.npmrc` 更新を Claude にやらせたい等) が運用上あるなら除外。無ければ追加推奨。**deny は正当作業も止める**ため、ここだけ運用実態の確認が要る。

### B-3. 任意 (掃除・非 security) — allow の死にノイズ除去

```diff
   "allow": [
     "Bash(*)",
     "Read(*)",
     "Edit(*)",
     "Write(*)",
     "Edit(**/Dropbox/_DevProjects/**)",
     "Edit(**/.claude/**)",
-    "Write(**/Dropbox/_DevProjects/**)",
-    "Write(**/.claude/**)",
     ...
     "Edit(**/CLAUDE.md)",
-    "Write(**/CLAUDE.md)",
```

- 効果: 残り warning 3行も消え **8→0 = 起動 warning 全消**。§C の起動 timing 副作用の trigger も消える (ただし恒久堅牢化は別途・§C)。
- `Write(*)` 自体は有効ゆえ**残す** (削除は更なる任意)。

### 可逆性

全て `permissions` 配列の要素 add/remove のみ。適用前の settings.json を控えれば 1 コピーで完全復元。スキーマ変更・他キー変更なし。

---

## 7. 未確定事項 (明示)

- **`auto` mode (classifier) の厳密挙動**: deny 絶対優先は `acceptEdits` で実証したが、`--permission-mode auto` の Sonnet classifier 経路まで同一 sentinel で叩いてはいない。deny は mode より前段で評価される設計ゆえ同結論のはずだが、`auto` 経路の直接実測は未。**conductor も独立検証中**、突き合わせ推奨。
- **`Write(path)` 非強制の挙動が始まった正確な version** (§2-e): warning 追加=2.1.210 は確定。非強制そのものの開始時期は未特定 (2.1.210 以前と推定)。fix には影響なし。
- **B-2 の対象 path への正当書込の有無** = kimny 運用判断 (§B-2)。

> ★訂正: interim で「`_conductor` の `Read(//...)` double-slash が malformed の疑い」と報告したが、§2-f の実証で **`//` は正しい絶対パス記法**と判明。**撤回**する。

---

## 8. 参照

- brief: `_conductor/docs/inbox/brief-settings-permission-audit-20260717.md`
- 対象: `/Users/kimny/.claude/settings.json`
- hook: `claude-code-template/.claude/hooks/validate-dangerous-ops-v2.sh`
- ownership map: `claude-code-template/.claude/hooks/ownership-map.tsv`
