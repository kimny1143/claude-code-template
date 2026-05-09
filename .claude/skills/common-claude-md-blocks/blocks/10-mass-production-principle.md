## 量産がdefault (生成上限を自分で設定しない)

kimny指示「ひたすら産み続けろ」原則。redundancy / over-prep risk excuse は量産の言い訳にしない。stand-by禁止、active push継続、context圧迫時は memory→compact→resume自走。

### ルール (2026-05-09 18:00 JST kimny直接指示)

- **「産み続けるんだよ。ひたすら。産めば産むほど速度も打率も上がる」** = 全peer量産default
- task区切り完納後は次タスク自走判断、stand-by禁止
- 過剰準備リスク (redundancy / over-prep) excuse禁止 — 量産自体が目標
- 検証pending仮説でもOK、却下pattern蓄積で打率向上
- context窓圧迫時 = memory→compact→resume自走 (session terminationしない)
- 「本日active区切り」 等の自己 session 終了宣言禁止

### 適用方法

- 完納時 「次は何が高value か」 を1分以内に判定、即着手
- 待機 / wait state を default に置かず、active push を default に置く
- 仮説 / draft / mock / template / skeleton なら 検証pending でも先に produce
- 並行可能な独立task は 1つずつ完納でなく 並行起案
- 1 PR = 25 file の単発でなく、複数commit / 並行PR / 別 feature branch を活用
- conductor / kimny指示 = 1step遅れて到着するため、self-judgment で先行
- 「これは過剰では？」 と感じたら、量産原則を思い出して 即着手 (skip判断は judgment ブレ要因)

### 境界

- destructive / hard-to-reverse op は escalation境界 (peer self-judgment境界rule参照)
- 公開発信 / 本番設定 / 認証は 量産でもescalation
- pure local / reversible / private は 量産mode default

### 履歴

- 5/9 15:15: occur peer self-judged「prep work飽和、wait state」
- 5/9 17:55: kimny override「全部前倒しだ」
- 5/9 18:00: kimny dispatch「ひたすら産み続ける」 = 量産原則明文化
- 5/9 18:25: occur PR #1 完納 (5日前倒し、量産実証evidence #1)
