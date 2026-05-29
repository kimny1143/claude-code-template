## 既存 state 優先 (assumption禁止)

memory / draft に記載した前提と repo / file system / git の実態にズレがある場合、**実態を優先**して memory を更新する。

- cold-start 後の最初の tool calls で `git status` / `git remote -v` / `gh repo view` 等の実態確認を必ず実施
- 「assume」系前提 (例:「リモートまだない」「ブランチ A」) を action 前に検証
- 特に `gh repo create` / `git push --force` / `rm -rf` 等 destructive / hard-to-reverse op は実態確認必須
- memory 基盤構築時は「事実」(1次 source を都度確認) と「想定」(draft 化のみ) を区別する
