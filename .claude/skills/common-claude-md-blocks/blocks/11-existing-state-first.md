## 既存state優先 (assumption禁止)

cold-start時に repo / git / configを実態確認してから動く。memory drafts に書いた前提が実態と乖離する場合は実態を優先。

### ルール

peer のmemoryやdraftに記載された前提と repo / file system / git の実態にズレがある場合、**実態を優先**して memory drafts を更新する。

### 適用方法

- cold-start 後の最初のtool calls で `git status` / `git remote -v` / `gh repo view` 等の **実態確認** を必ず実施
- memory drafts と実態に gap があれば実態を採用、memory側を update
- 「assume」 系の前提 (例: 「リモートまだない」「ブランチ A」) を action前に検証
- 特に `gh repo create` / `git push --force` / `rm -rf` 等の destructive / hard-to-reverse op は実態確認必須

### Why

2026-05-09 17:58 JST のPhase 0 bootstrap着手時、occur peer memory drafts に「`kimny1143/muedoccur` (no hyphen)」と記載していたが、実態は `kimny1143/mued-occur` (hyphen)。`gh repo create` を実行する前に `gh repo view` / `git remote -v` で実態確認 → 実態に合わせて draft更新で対応した。

memory draftに `gh repo create kimny1143/muedoccur --private` と書いていた手順を盲目的に実行していたら新規repo (空) が作成され、既存repo (initial commit済) と乖離する事故になっていた可能性。

### 他peerへの示唆

- memory基盤を構築するときは「事実」と「想定」を区別、事実は1次source (実態) を都度確認、想定は draft化のみ
- cold-start judgment の最初の3-5 tool callsで実態vs想定 gap detectionを習慣化
