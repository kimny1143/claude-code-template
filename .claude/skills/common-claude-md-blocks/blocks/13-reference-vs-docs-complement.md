## reference memory ≠ docs (structural complement原則)

同じ情報sourceでも reference memory (AI内向け) と `_docs/` ファイル (human/cross-peer accessible) は access path / integration pattern が異なる別 value を持つ。partial overlap時に skip判断は不適切、両方整備して docs PR時に redundant部分 remove判断。

### ルール

1. **reference memory** = `~/.claude/projects/<peer>/memory/` 配下、AI auto-load対象、cross-peer file system Read可能だが auto loadはされない
2. **`_docs/` ファイル** = git repo内、human閲覧可、PR review対象、cross-peer も repoclone経由で access可
3. **同じ情報source** でも上記2形式は access path / integration pattern / 利用者層が異なる = **別 value**
4. **partial overlap時のskip基準**: 「reference memory既存だから docs draft skip」 は判断誤り、両方整備して docs PR時に redundant部分 remove判断 (= 実装段階の natural review)
5. 「装飾を削ぎ落とす」 (= over-prep / decoration回避) と「structural complement (構造的補完)」 は別軸

### 適用方法

- prep work で reference memory + docs draft 両方を作るのは redundant ではなく structural complement
- 「information source 同じだから 1つで十分」 と判断する前に: access path (auto-load? PR review対象?) / 利用者層 (AI peer? human collaborator?) / integration pattern (memory cross-reference? repo clone?) が異なるか確認
- docs PR時に「実装で natural生成された部分と pre-draft の重複」 を見つけたら remove判断
- 装飾削ぎ落とし (decoration removal) は引き続きOK、structural complement は守る

### 他peerへの示唆

- 同様の「reference + docs 両方作るのは redundant?」judgment が出たら本ruleを参考、両方整備 + docs PR時 remove判断 pattern
- 「事実」 と「想定」 を区別する `existing-state-first` ruleと併せて、memory/docs 整合性judgment quality向上

### Why (5/9 evidence)

5/9 conductor (e) override → (i)(j)(k) 推奨 → occur peer は (k) のみ完納 + (i)(j) skip判断 ((e)で `_docs/` 3本既存だが reference_harness_design / reference_abx_evaluation_framework と redundancy感じた) → 後の reverse で (i)(j) 完納確定。reference ≠ docs structural complement原則として明文化された (`feedback_reference_vs_docs_complement.md`)。
