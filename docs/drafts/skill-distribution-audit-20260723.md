# スキル配布監査 — 全 workspace 実測マトリクス + 3分類 (2026-07-23)

- 契機: kimny 直接報告「Chief 新設(6/11)頃から『えっ、このスキル使えないの？』が増えている」→ conductor escalate → CCO/template 領域
- 手法: 全 workspace の `.claude/skills` を read-only 実測（symlink/copy 区別込み）+ 配布正本 (setup.sh SHARED_SKILLS / distribute-skills.sh COMMON_SKILLS) と突合

## 0. 配布は2チャネル（conductor の「44」は合算）

| チャネル | 正本 | 件数 | 機構 | 対象 |
|---|---|---|---|---|
| **SHARED_SKILLS** | `setup.sh` | 38 | symlink・**手動 per-workspace 実行** | PUBLIC template (Gumroad) + fleet |
| **COMMON_SKILLS** | `distribute-skills.sh` | 6 | symlink・**TARGETS へ一括配布** | 内部運用 (peer-checkout/peer-id-lookup/plan-mode-policy/pwa-dashboard/tier-judge/ui-mock-fidelity) |

conductor の「SHARED 44」= 38(SHARED) + 6(COMMON) の**2チャネル合算**。分けて扱う。

## 1. (a) 実測マトリクス（symlink/copy 区別）

| workspace | total | symlink | copy | COMMON(6) | universal(5)† | 判定 |
|---|---|---|---|---|---|---|
| **_chief** | **NO-DIR** | — | — | — | — | ★setup 未実行・skills dir 無 |
| _product | 6 | 0 | 6 | 6/6 | **0/5** | ★leak + 全 copy(stale) |
| _mued-dsp | 7 | 1 | 6 | 6/6 | **0/5** | ★leak |
| _conductor | 17 | 1 | 16 | 6/6 | **0/5** | ★leak |
| _Reserch | 13 | 0 | 13 | 6/6 | **0/5** | ★leak + 全 copy(stale) |
| mued/threads-api | 20 | 0 | 20 | 6/6 | 1/5 | ★leak + 全 copy(stale・更新不達) |
| _cowork | 18 | 11 | 7 | 6/6 | 5/5 | OK |
| _contents-writing | 23 | 16 | 7 | 6/6 | 5/5 | OK |
| freee-MCP | 23 | 14 | 9 | 6/6 | 5/5 | OK |
| _data-analysis | 27 | 16 | 11 | 6/6 | 5/5 | OK |
| mued/mued_v2 | 33 | 16 | 17 | 6/6 | 5/5 | OK |
| _growth | 44 | 38 | 6 | 6/6 | 5/5 | OK (SHARED 38/38 唯一の full) |
| _mued-occur | 3 | 0 | 3 | 3/6 | 0/5 | **意図的除外**(下記・leak でない) |

† universal(5) = dev-workflow cross-cutting 候補 = `tdd` `coding-rules` `git-worktree` `hooks` `mcp`

## 2. (b) 3分類（漏れ vs 意図の分離）

### universal（全 active peer が要る = leak 候補）
- **dev-workflow 5件**: `tdd` `coding-rules` `git-worktree` `hooks` `mcp`。SHARED_SKILLS に在るが setup.sh 未実行の peer に届いていない。
- **内部運用 6件 (COMMON)**: 既に distribute-skills.sh で配布済 (6/6 ほぼ全 peer)。**このチャネルは機能している**。
- 現状 user scope (`~/.claude/skills`) = 4件のみ (`asc-metadata-sync` `peer-id-lookup` `tier-judge` `web-scraping`)。**dev-workflow 5件は user scope に不在** → 経路は生きているがほぼ未使用。

### domain（一部 peer のみ = 不在は正しい・leak でない）
- Marketing/CRO 15件・UX/Product 5件・Content 4件・Payments 3件・Vercel/React 3件・remotion・ios。
- 例: `copywriting`/`email-sequence` が _mued-dsp に無いのは**正しい**（DSP repo に不要）。「0/38 SHARED = 全 bug」ではない。

### ★intentional-deny（意図的除外・是正対象外）
- **_mued-occur**: distribute-skills.sh L60「2026-06-11 closed (組織再編 v2)・配布対象から除外」。**dormant ゆえの effort-based 除外**（「これらの skill が occur に禁忌」ではない）。→ 是正しない。
- **_chief**: distribute-skills.sh TARGETS に**未登録**・skills dir 自体無し。6/11 新設で**どのチャネルにも登録されなかった** = ★これは意図でなく **leak**（新設時の登録漏れ）。

## 3. 根本原因（確定）

1. **SHARED チャネル (setup.sh) が _product/_mued-dsp/_conductor/_Reserch/_chief で未実行** → universal dev-workflow 5件が不達。COMMON は届く(distribute-skills.sh)が SHARED は手動 setup 依存ゆえ漏れた。
2. **copy-not-symlink** (threads-api/_product/_Reserch/_mued-occur = symlink 0) → 持っている skill も**更新不達 (stale)**。「入っているのに古い」＝気づきにくい。
3. **_chief 登録漏れ** (6/11 新設・どのチャネルにも未登録)。kimny の体感「Chief 新設の頃から」と一致。

## 4. (c) 是正提案（★plan + conductor/kimny gate 要・未実行）

**Chief 提案「universal を `~/.claude/skills` (user scope) へ」を採用推奨。ただし設計を精密化:**

- **移す = dev-workflow 5件 (`tdd` `coding-rules` `git-worktree` `hooks` `mcp`) を `~/.claude/skills` に追加**。全 session 自動適用 → 0/5 の leak peer が構造的に解消・新設 peer も自動取得 → **配布漏れの class 自体が消える**。
- ★**PUBLIC template の SHARED_SKILLS からは削除しない**。Gumroad 買い手は `~/.claude/skills` を持たず setup.sh 依存ゆえ、削除すると買い手が tdd/hooks 等を失う。→ **fleet 内部への user-scope 追加であって public template 配布範囲の変更ではない**（= setup.sh 不変ゆえ public 配布 gate 非該当）。
- ★**intentional-deny (occur) は violate しない**: occur 除外は effort-based (dormant) であって content-based でない。user-scope 追加で dormant occur も持つが無害。
- ★**所有ガード準拠**: user-scope 追加は kimny home への変更で、他 peer workspace への cross-repo write ではない → CCO 領域内。ただし fleet 全 session 影響ゆえ **conductor + kimny gate**。
- **copy-not-symlink の stale**: universal を user-scope 化すれば universal については copy が無関係化。domain skill の stale copy は別問題（各 peer が setup.sh 再実行 or symlink 化・所有ガードゆえ各 peer 手番）。
- **_chief**: skills dir 新設 + 両チャネル登録（distribute-skills.sh TARGETS 追加 + universal は user-scope で自動）。

**DoD (conductor)**: (a)マトリクス実測✅ / (b)3分類 repo land (本 doc) / (c)是正後 全 workspace で実測 verify（「配ったつもり」でなく各 workspace で実際に見える=今日の「上流修正≠下流到達」型）。

## 5. (c) 是正 — ★実行済み (2026-07-23・conductor GO・5条件遵守)

**足したもの**: `~/.claude/skills/` に universal 5件を **canonical への symlink** で追加（copy でなく symlink＝§3-2 の stale 問題を自作しない・canonical 単一 source で常時 current）:
```
~/.claude/skills/tdd          -> /Volumes/strage/_DevProjects/claude-code-template/.claude/skills/tdd
~/.claude/skills/coding-rules -> …/coding-rules
~/.claude/skills/git-worktree -> …/git-worktree
~/.claude/skills/hooks        -> …/hooks
~/.claude/skills/mcp          -> …/mcp
```

**★戻し方（可逆・条件4）**: `rm ~/.claude/skills/{tdd,coding-rules,git-worktree,hooks,mcp}`（symlink 削除のみ・canonical 実体は不変）。

**条件遵守**: ①追加のみ・既存4件 (`asc-metadata-sync`/`peer-id-lookup`/`tier-judge`/`web-scraping`) 不触 ✅ ②`setup.sh` 不変 ✅ ③`distribute-skills.sh` occur 除外 (L60-61) 不触 ✅ ④本節で what+revert 記録 ✅ ⑤verify（下記）。

**verify（条件5・DoD「上流≠下流」）**:
- ✅ 5 symlink 全て resolve + `SKILL.md` 読取可（実測）
- ✅ user scope の既存 `peer-id-lookup`/`tier-judge` が fleet 全 session で機能している実績 = 同一機構ゆえ 5件も全 session 適用
- ★**射程**: 「各 leak peer の live session で実際に tdd が出る」の runtime 確認は本 session から他 workspace を起動できず未実施。機構（user scope は CWD 非依存で全 session 適用・既存 user-scope skill で実証済）は健全ゆえ、**次回各 peer session で自動適用される見込み**。conductor/各 peer の次 session で最終確認。

## 6. 残: copy-not-symlink の stale (conductor 指摘・別項目・急がない)
`threads-api`/`_product`/`_Reserch` = symlink 0 ＝ **持っている domain skill も更新不達 (stale)**。**user-scope 追加では未解決**（それらは workspace 内 copy として残る）。「入っているが古い」は「入っていない」より気づきにくい。→ **(c) の後の別項目**: stale copy を symlink 張替 or user-scope 一本化で workspace 実体退役。所有ガードゆえ各 peer 手番 or conductor dispatch。今日はやらない。
