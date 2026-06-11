# 共通block self-commit チェックリスト (B backlog) — 2026-06-12

## 目的

2026-06-11 の block 15「from_id 正本原則」distribute (PR #112) 実行時に検出した **durability 問題**への今回分 backlog 対応。

`distribute-claude-md-blocks.sh` は各 peer の **working tree を書くだけ**で commit しない。durability は「各 peer が自 repo で self-commit」前提だが未徹底で、過去の canonical 更新 (DoD #109 / org-v2) が複数 peer の **committed CLAUDE.md に不在** = working tree に書かれたまま self-commit されず evaporate していた (branch 操作で revert 推定)。

**conductor 判断 (2026-06-11)**: (A) CCO 直接 cross-repo commit = 不採用 (所有ガード LIVE 直後の境界 + branch protection)。(B) 今回分 = **各 live課が自 repo で /checkout 時に batch self-commit** (本ドキュメント)。(C) 恒久 fix = 各 peer 自走 self-commit 機構を次 session で draft。

> 即時性なし: common block は **次 session 開始時**に効く (CLAUDE.md は起動時ロード)。稼働中の割り込み不要、working tree は canonical-ward で無害ゆえ保持で OK。conductor が各課へ dispatch する用のリスト。

## 対象 live課 + repo (6課)

| 課 | repo (CWD) | 現 branch | CLAUDE.md diff | 他未commit | base |
|----|-----------|----------|----------------|-----------|------|
| freee課 | `freee-MCP` | main | +49/-13 | 4件 | main |
| cowork課 | `_cowork` | main | +49/-13 | 12件 | main |
| mued課 | `mued/mued_v2` | docs/status-mued-20260611 | +49/-13 | 2件 | main |
| insight課 | `_data-analysis` | main | +49/-13 | 0件 | main |
| product課 | `_product` | master | +17 | 0件 | **master** |
| content課 | `_contents-writing` | main | +33/-8 | 0件 | main |
| content課 | `_LandingPage/glasswerks-lp` | feat/hero-remove-free15-campaign | +49/-13 | **42件 WIP** | main |

**反映される canonical 内容** (課により差): block 15 from_id 原則 (全課) + DoD (block 17 #109) + org-v2 (block 04) + 入口絞り (block 15) + block 18 等の累積 drift 再同期。いずれも **canonical-ward** (DO-NOT-EDIT marker section、後退なし)。

## 除外・別扱い

- `mued/mued_v2/apps` (+162/-384) = **native apps stale の別件**。今回の block sync と**混ぜない** (conductor 指示)。別途 apps 再同期として扱う。
- `_Reserch` (+49/-13) = reserch **dormant** (insight課 母体 _data-analysis へ統合)。live peer 不在ゆえ **defer** (次回 reserch spinup 時 or insight課 が必要時)。
- `_conductor` (+1, block 14 正規化) = **conductor が自 repo で self-commit** (block 15 marker 無ゆえ from_id は別途、起案者既知)。

## 各課が自 repo で叩くコマンド (worktree 分離・他 WIP 非干渉)

現 branch や他の未 commit を**一切汚さない**ため、CCO と同型の origin/main worktree 経由。`<REPO>` は自 repo root、`<BASE>` は上表 base (product のみ master)。

```bash
# 自 repo root で:
cd <REPO>
git fetch origin
WT=/tmp/cbsync-$(basename "$PWD")
git worktree add "$WT" origin/<BASE> -b docs/common-block-sync-20260612
cp CLAUDE.md "$WT/CLAUDE.md"          # distribute 済 working tree の CLAUDE.md を持ち込み (CLAUDE.md のみ)
cd "$WT"
# ※ git diff で marker section (COMMON-BLOCK-*) のみか確認。自分が CLAUDE.md を marker 外で編集していた場合はその差分も入る点に留意
git add CLAUDE.md
git commit -m "docs(claude-md): canonical common-block sync (block15 from_id + DoD#109 + org-v2 reconcile) [self-review]

CCO distribute (PR #112 系) の working-tree 書込を durable 化。
共通block marker section のみ、canonical 派生 (DO-NOT-EDIT 区画)。Tier1 [self-review]。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
git push -u origin docs/common-block-sync-20260612
gh pr create --base <BASE> --title "docs(claude-md): 共通block canonical sync [self-review]" \
  --body "CCO distribute の durable 化 (common block marker section のみ・canonical 派生・Tier1)。"
gh pr merge --squash --delete-branch
cd - && git worktree remove "$WT" --force
```

### 注意点

- **CLAUDE.md のみ** add (他の未 commit ファイルは触らない)。glasswerks-lp (42件 WIP) / cowork (12件) でも安全。
- **base branch**: product課 = `master`、他 = `main`。
- marker section 外を自分で編集していた課は、commit 前に `git diff` で確認 (canonical 区画以外の差分が混ざらないこと)。
- 元の作業 branch はそのまま (worktree は別ディレクトリ、現 branch 不変)。

## 恒久 fix (C) との関係

本 backlog は今回分の手当て。根本解決は (C) = distribute が各 peer に commit 指示を emit する / checkin・checkout hygiene step で DO-NOT-EDIT marker section を自動 self-commit する機構。**次 session で CCO が design draft**。本丸理由: 未 commit だと block は restart で旧 CLAUDE.md に戻り、distribute は working tree のみ再 write → 永久に効かない無限ループ。
