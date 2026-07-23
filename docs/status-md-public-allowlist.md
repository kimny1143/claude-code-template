# status.md 公開許可リスト (allow-list)

- 制定: CCO (template課) / conductor 承認 2026-07-23
- 対象: `claude-code-template/status.md` (**このリポジトリは PUBLIC**)
- 位置づけ: status.md を公開のまま運用する (判断2 = (c) 恒久化) ための**許可列挙**規約

## なぜ許可列挙か (禁止列挙でない)

粒度を落とす運用は、**禁止列挙だと必ず drift する**（「これくらいなら」が積み上がる）。だから「**書いてよいもの**」を先に固定し、**それ以外は書かない**。判断に迷ったら「許可リストに無い＝書かない」。

status.md は cowork の集約器が READ して private (`_conductor/docs/inbox/peer-raw-status.md`) へ slim copy を push する。**詳細な作業記録は private 側 or untracked のローカルメモに置き、公開 status.md には下記だけを書く。**

## 書いてよいもの (allow)

| フィールド | 許可される粒度 |
|---|---|
| `status` | `clean` / `active` 等の状態語のみ |
| `current_task` | **課名 + 工程名まで**（例「dsp trunk 統合 Phase2 待機」「他課 PR レビュー中」）。何を/どの段階か、まで |
| `next_action` | 次の工程名 + 手番の所在（誰待ちか）。**動作の種類まで**（例「kimny 判断待ち」「CI 緑待ち」「review 返却待ち」） |
| `blocked_by` | **ブロックの有無と種別だけ**（例「kimny 判断待ち」「CI 待ち」）。**理由の中身は書かない** |
| `urgency` / `confidence` / `lane` | 語のみ |
| 日付・PR 番号 | 公開 repo 内の PR 番号・merge 済 commit は可（公開情報） |
| Recent events | **何をしたか + どこで止まっているか**まで。工程名と手番の所在 |

## 書いてはいけないもの (禁止・許可リストに無いものは全て禁止だが、特に)

- **金額・原価・売上目標・価格**（¥・cr・%・monetization 数値）
- **顧客名・取引先名・個人情報**（メール・氏名）
- **鍵・トークン・認証経路の実査出力**（`gh auth status` の生ログ・scope・保管場所）
- **未公開製品の内部名・仕様・出荷前の弱点**（他 repo の private な脆弱性・未検証経路・課金バイパスの具体）
- **セキュリティ監査結果**（どの deny が死んでいるか・防御機構の穴の場所）
- **他課 private repo の内部状態**（レビューで見た製品固有の詳細・実測ログ）

## 迷ったときの原則

- **「durable に記録すべき」と「公開してよい」は別の問い**（[[feedback_publication_vs_durability]]）。前者が真でも後者が偽なら、詳細は untracked のローカルメモ or private 側へ。公開 status.md には工程名だけ
- **公開 repo は一度きりでなく、書くたびに公開判断をやり直す**。過去の Recent events も、この allow-list で見直す価値がある（本 PR では今日分のみ適用・過去分は別途）
- 一次記録は各 repo の PR コメント / private 集約にある。**公開 status.md に写しを持つ必要はない**
