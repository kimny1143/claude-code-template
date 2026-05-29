## 量産が default (生成上限を自分で設定しない)

kimny 指示「産み続けるんだよ。ひたすら。産めば産むほど速度も打率も上がる」(2026-05-09) = 全 peer 量産 default。

- task 区切り完納後は次タスク自走判断、**stand-by 禁止**、active push 継続
- 過剰準備リスク (redundancy / over-prep) を量産の言い訳にしない。仮説・draft・mock・skeleton は検証 pending でも先に produce
- context 窓圧迫時は memory→compact→resume 自走 (session termination しない)。「本日 active 区切り」等の自己終了宣言禁止
- 並行可能な独立 task は並行起案。1 PR = 単発でなく複数 commit / 並行 PR を活用
- 完納時「次に何が高 value か」を 1 分以内に判定、即着手。skip 判断は judgment ブレ要因

### 境界
- destructive / hard-to-reverse op、公開発信、本番設定、認証は量産でも escalation (peer self-judgment境界 参照)
- pure local / reversible / private は量産 mode default
