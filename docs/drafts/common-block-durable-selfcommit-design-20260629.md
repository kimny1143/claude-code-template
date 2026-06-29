# 共通block distribute durability 恒久fix (C) — 設計draft 2026-06-29

> status: **draft / conductor review 待ち**。hygiene queue #3「本丸」(C) の起案。
> Tier 想定: **Tier 3** (全peer波及の hook/script 機構 + branch protection/所有ガードと相互作用)。
> 関連: [[project_next_session_hygiene_queue]] #3 / `docs/drafts/common-block-self-commit-checklist-20260612.md` (B backlog/PR#114) / `scripts/distribute-claude-md-blocks.sh`。

## 1. 問題 (durability infinite-loop)

`scripts/distribute-claude-md-blocks.sh` は各peer の **working tree CLAUDE.md を Python `write_text` で上書きするだけで commit しない**。

durability は「各peer が自repo で self-commit」前提だが未徹底で、結果として:

1. distribute が peer working tree を書く。
2. peer が未commit のまま branch 操作 (checkout/switch) または restart。
3. 未commit の working-tree 変更が失われ、CLAUDE.md は **committed (旧) 版に戻る**。
4. 次 distribute も working tree を再write するだけ → **永久に commit されない無限ループ**。

実証 (2026-06-11, block15 distribute 時): marker有ほぼ全課の committed CLAUDE.md に、過去「distribute 済」報告分の DoD(block17 #109) / org-v2(block04) が **不在**だった = working tree に書かれたまま evaporate していた。from_id silent-partition と同類の「サイレント非伝播」。

→ B backlog (PR#114) で今回分は手動 self-commit で landing 済 (2026-06-29 時点 7 repo/6課+conductor 全 ✅ クローズ)。本draft はその **恒久 fix (C)**。

## 2. 制約 (設計が満たすべき条件)

| # | 制約 | 出典 |
|---|------|------|
| C1 | **CCO は peer repo へ cross-repo commit しない** (所有ガード LIVE 直後の境界 + branch protection) | conductor 判断 2026-06-11 ((A)不採用) |
| C2 | **main 直push 禁止** — self-commit も branch+PR 経由 (docs-only でも) | `block-main-push.sh` / branch protection policy |
| C3 | **peer の他WIP を汚さない** — CLAUDE.md の、しかも **marker section のみ** commit | #114 注意点 (glasswerks-lp 42WIP / cowork 12WIP) |
| C4 | **remote 有無で commit 戦略分岐** — product は remote 無 local-only repo (push/PR 不可、local commit のみ) | #114 ★product finding |
| C5 | **marker 外の peer 自編集を巻き込まない** — #114 は CLAUDE.md 全体 copy ゆえ「marker 外編集も入る」警告付きだった。恒久版は **marker section だけ抽出**して this 弱点を解消 | #114 注意点の改善 |
| C6 | **冪等** — 既 sync 済なら no-op | distribute 既存設計と同じ規律 |

## 3. 不採用案 (なぜ peer-self-driven か)

- **(A) CCO が distribute 内で各peer repo を直接 commit** → C1 違反。conductor 既に不採用。
- **(D) distribute が各peer repo に worktree add → marker copy → commit → push → PR → squash-merge を CCO プロセスから実行** → 実体は (A) と同じ cross-repo commit。C1 違反。不採用。
- 結論: **commit は必ず peer 自身のプロセスから発火させる**。distribute は「working tree write + commit すべき signal の提示」までを担う。

## 4. 推奨設計 (peer-self-driven + distribute signal)

### 4.1 中核: 共有script `scripts/selfcommit-common-block.sh`

各peer が **自repo root を CWD として** 実行する冪等 script。#114 の手動コマンド列を再利用可能化し、C5(marker-only) と C4(remote分岐) を織り込む。

擬似ロジック:

```
selfcommit-common-block.sh  (CWD = peer repo root)
  1. CLAUDE.md が無ければ exit 0 (対象外)。
  2. HEAD:CLAUDE.md と working-tree CLAUDE.md の COMMON-BLOCK marker section 群を抽出・比較。
     - marker section に diff 無し → "already in sync" exit 0 (C6 冪等)。
     - marker 外にのみ diff → common-block 同期対象外、exit 0 (peer 自編集は触らない)。
  3. remote 有無判定 (`git remote` 空か):
     ┌ remote 有 (通常課):
     │   a. git fetch origin
     │   b. WT=worktree add origin/<default-branch> -b docs/common-block-sync-<date>
     │   c. WT 側 CLAUDE.md の **marker section のみ** を working-tree 版で patch
     │      (= 全file copy でなく marker 区間だけ移植 → C5。distribute と同じ
     │        COMMON-BLOCK-START/END 正規表現で区間置換)
     │   d. git add CLAUDE.md → marker 区間以外に diff が無いこと assert (安全弁)
     │   e. commit [self-review] → push → gh pr create --base <default> → gh pr merge --squash --delete-branch
     │   f. worktree remove
     └ remote 無 (product 等 local-only):
         a. 現 working tree の marker section drift を、現 branch ではなく
            **local default branch (master/main) へ** commit。
            worktree 分離 (local default base) で他WIP非干渉を維持し、merge は fast-forward/直commit。
            push/PR は skip (C4)。
```

ポイント:
- **marker section のみ移植** (C5): distribute と同一の `COMMON-BLOCK-START:<id> ... END:<id>` 区間ロジックを共有。peer が marker 外で CLAUDE.md を編集していても、その差分は commit に入らない。
- **worktree 分離** (C3): 現 branch / 他 WIP を一切汚さない。#114 と同型。
- **Tier 1 [self-review]** (C2): docs-only・canonical 派生 (DO-NOT-EDIT 区画) ゆえ branch+PR+self-merge で branch protection 遵守。
- **冪等** (C6): marker section 一致なら no-op。何度走っても安全 → hygiene step に組み込み可。

### 4.2 distribute 側: commit signal の emit

`distribute-claude-md-blocks.sh` 末尾に、**実際に working tree を更新した peer の一覧** + 各peer が叩くべきコマンド (`scripts/selfcommit-common-block.sh`) を出力する。さらに `docs/` 配下に **sync manifest** (更新 peer / canonical source hash / 日時) を1ファイル emit し、conductor が dispatch / patrol で landing 照合できるようにする (B coordination で手動 tally したものを構造化)。

→ これで conductor の (C) 要件「distribute が各peer に commit 指示を emit」を満たす。

### 4.3 発火タイミング: 手動 → hygiene step (段階導入)

| 段階 | 発火方法 | 評価 |
|------|---------|------|
| **Phase 1 (推奨初手)** | peer が **手動** で `selfcommit-common-block.sh` 実行 (distribute 後 conductor dispatch、または checkin/checkout/status-save hygiene の手順に明記) | 低リスク・可観測・script の挙動を実地検証してから自動化 |
| **Phase 2 (検証後)** | 既存 hygiene step (checkin / status-save / `/checkout`) に script 呼び出しを **明示組込** (peer が hygiene を回すと自動で marker drift を self-commit) | 中リスク・冪等ゆえ安全だが PR 自動発行の頻度に注意 |
| **Phase 3 (defer/要再判断)** | **SessionStart hook で完全自動** (`load-handoff-memory.sh` と同列に CWD 検出 → 自動 self-commit) | **invasive**: 毎セッション開始で git/PR 自動操作・peer の現 branch state に介入。初期は採らない。Phase 2 実績後に conductor/kimny 判断 |

Phase 3 を初手で採らない理由: SessionStart 自動 commit は「毎起動で勝手に PR を立てて merge する」挙動になり、(1) peer の意図しない branch 汚染リスク、(2) PR スパム、(3) ownership/branch-protection hook との相互作用が読みきれない。**冪等 script を手動/hygiene-step で回す Phase 1→2 で十分 durability を確保**でき、自動化は実績を見てから。

## 5. 残課題 / open questions (conductor / kimny 判断点)

1. **★最大の判断点 = 発火の自動度**: Phase 1 (手動) スタートで合意か、それとも最初から Phase 2 (hygiene step 組込) まで行くか。Phase 3 (SessionStart 完全自動) は初手では非推奨で合意か。
2. **marker section patch の安全弁**: §4.1-d の「marker 区間以外 diff 無し assert」が false positive (peer が marker 直前後の空行等を触った) を起こさないか。distribute の正規化ロジックと完全一致させる必要。
3. **default branch 検出**: product=master / 他=main。`git symbolic-ref refs/remotes/origin/HEAD` で動的検出するか、manifest にハードコードするか (conductor ID 動的解決と同じ「ハードコード回避」方針なら前者)。
4. **SHARED_HOOKS/COMMON_SKILLS 昇格**: script を `setup.sh` 配布対象 (全peer の `scripts/` または `.claude/`) に載せるか、common skill 化するか。配布チャネル選定は [[feedback_shared_vs_common_skill_channel]] の区別に従う (内部運用 → COMMON、公開 → SHARED)。
5. **apps stale (mued_v2/apps +162/-384)** は本 sync と別件 (#114 除外通り)。(C) 機構の対象外として明記するか、別途 reconcile タスクにするか。

## 6. 段階的 rollout 案

1. 本draft を conductor review → §5-1 の自動度方針を確定 (必要なら kimny 判断: 全peer hook 機構 = Tier 3)。
2. `scripts/selfcommit-common-block.sh` 実装 (template課) + `--dry-run` 必須。CCO 自repo で marker-only/remote分岐/local-only(product相当) を単体検証。
3. `distribute-claude-md-blocks.sh` に signal emit + manifest 出力を追加 (既存挙動は不変、末尾出力のみ追加)。
4. Phase 1 配布: distribute 後 conductor dispatch で各peer が手動実行 → landing tally (manifest で照合)。次の canonical 更新サイクルで durability を実地検証。
5. 検証 OK なら Phase 2 (hygiene step 組込) を別PRで。

## 7. 成功条件

canonical block を更新 → distribute → 各peer self-commit → **次の restart 後も committed CLAUDE.md に block が残存** (working tree write のみで evaporate しない)。B coordination で手動確認した「各 repo default branch の sync commit」が、機構として自動的に landing する状態。
