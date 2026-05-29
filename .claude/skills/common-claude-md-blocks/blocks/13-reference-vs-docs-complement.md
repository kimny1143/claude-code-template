## reference memory ≠ docs (structural complement原則)

同じ情報 source でも reference memory (AI auto-load 対象) と `_docs/` ファイル (human 閲覧・PR review 対象) は access path / 利用者層 / integration pattern が異なる = **別 value**。

- prep work で reference memory + docs draft 両方を作るのは redundant でなく structural complement
- partial overlap 時に「memory 既存だから docs draft skip」は判断誤り。両方整備し、docs PR 時に redundant 部分を remove (= 実装段階の natural review)
- 「装飾を削ぎ落とす」(over-prep / decoration 回避) と「structural complement」は別軸。前者は引き続き OK、後者は守る
- skip 前に確認: access path (auto-load? PR review?) / 利用者層 (AI peer? human?) / integration pattern が異なるか
