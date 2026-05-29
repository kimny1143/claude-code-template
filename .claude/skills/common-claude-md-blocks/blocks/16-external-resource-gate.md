## 外部リソース gate — 常に URGENCY: high + pre-approval 必須

外部リソース新規作成系の不可逆 / 高 blast-radius 操作は peer 自走範囲外 = 常に URGENCY: high + kimny または conductor の事前 approval を得てから実行 (dsp 5/17 型再発防止)。

### Gate 対象 (常に high + pre-approval)
- **外部リソース新規作成**: GitHub repo / SaaS account / domain / Org / Cloud project / API key 発行 / sub-account
- **公開範囲変更**: private → public、public archive、visibility 取消 / 復活、Org 移転
- **課金 / 契約**: paid plan upgrade、subscription、contract signature
- **不可逆操作**: 永久削除、force push to main、history rewrite、production data drop、token revoke

### Gate 不要 (peer 自走)
- 既存リソース内 sub-resource (既存 repo の secret / 既存 project の env var / 既存 channel の message) = 事後報告のみ
- ローカル開発リソース (test db、dev branch、local CI artifact) / reversible op (revert 可能 PR、stash、merge 後 branch delete)

### 判定境界が曖昧な case
- **迷ったら gate 適用**。1 click で取り消せる = 自走 OK / 取り消しに kimny・conductor・外部問い合わせ必要 = gate 適用
- 起案前 gate (本 block) + 起案後 audit (`resource-audit` skill cron) の 2 layer。PR Tier policy「Tier 3 = 新外部サービス導入」と整合
