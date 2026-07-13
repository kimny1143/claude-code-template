## UI モック忠実性 DoD（新規 UI 面・re-skin・視覚再設計のみ）

承認済みモックが存在する/すべき UI 作業（新規面・re-skin・視覚的再設計）は、以下を DoD とする。
**既存実装の微修正（コピー1行・padding・バグ修正）は対象外**（既存 Tier/review 規律のまま）。

- **mock pin**: 承認 mock を filename/hash 等の一意識別子で pin（「案A/B」等の曖昧ラベル禁止）。mock 無しの UI 実装依頼は禁止。
- **数値移植**: 座標/寸法/色hex/フォント/余白を数値で移植（雰囲気移植禁止）。mock が自作 HTML/CSS なら実 source 値を 1:1 移植。
- **diff 添付**: 完了報告に render×mock の並置 + overlay/pixel-diff を必須添付。
  - **web = pixel-perfect 期待** / **native = 数値一致 + pixel-diff + 許容差明示**。
  - 非再現 flag は真に engine 由来（AA/hinting）のみ。font weight/size/座標 は fixable = 100% 一致必須（立証責任は flag 側）。
- **conductor vet**: 印象評でなくモック実見突合。「近い」却下・「見分けつかない」のみ通過 → kimny push。vet を経ない push 禁止。
- **mock hygiene**: pinned mock は shippable/house 資産（house/OFL font 等）で作る。system/proprietary font 混入禁止。

手順の詳細・技法・例外表 = `ui-mock-fidelity` skill を参照。
忠実性 gate（見分けつかない）は kimny 美的 gate の代替でない（別レイヤー）。
