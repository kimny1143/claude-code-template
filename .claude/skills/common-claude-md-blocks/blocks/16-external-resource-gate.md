## 外部リソース gate — 常に URGENCY: high + kimny / conductor approval 必須

外部リソース新規作成系の不可逆 / 高 blast-radius 操作は、 peer 自走範囲外 = 常に URGENCY: high + kimny または conductor の事前 approval を得てから実行する (Reference: `proposal-conductor-cognitive-load-v3.md` §8.2、 dsp 5/17 型再発防止)。

### Gate 対象操作 (常に high + pre-approval 必須)

- **外部リソース新規作成**: GitHub repo / SaaS account / domain / Org / Cloud project / API key 発行 / Sub-account 作成
- **公開範囲変更**: private → public、 public archive、 visibility 取り消し / 復活、 Org 移転
- **課金 / 契約**: paid plan upgrade、 commit fee、 monthly / annual subscription、 contract signature
- **不可逆操作**: 永久削除、 force push to main、 history rewrite、 production data drop、 token revoke

### Gate 不要 (peer 自走範囲)

- 既存リソース内 sub-resource (例: 既存 repo 内 secret / 既存 Vercel project 内 env var / 既存 Slack channel 内 message) = 事後報告のみ
- ローカル開発リソース (test database、 dev branch、 local CI artifact)
- reversible operations (revert可能 PR、 stash、 branch delete after merge)

### 判定境界が曖昧な case

- **迷ったら gate 適用** (= URGENCY: high で kimny / conductor approval 取得)
- 「不可逆操作か」 判定: 1 click で取り消せる = peer 自走 OK / 取り消しに kimny / conductor / 外部問い合わせ必要 = gate 適用

### 既存 skill との関係

- `.claude/skills/resource-audit/SKILL.md` (既存) = 外部リソース監査 daily / weekly cron
- 本 block = 起案時点の **pre-approval contract** (resource-audit は post-hoc 検出、 本 block は予防 layer)
- 両者組合せ = ① 起案前 gate (本 block) + ② 起案後 audit (resource-audit) で 2 layer defense

### dsp 5/17 incident reference (再発防止 evidence)

dsp peer が 5/17 に外部リソース新規作成 (詳細は dsp peer memory) を URGENCY 不在 / pre-approval 不在 で実行した case が pattern 化。 本 block の明示で 12 peer 横断 prevention layer 確立。

### Tier 判定との整合

CLAUDE.md PR Tier policy「Tier 3 = 新しい外部サービス・APIを導入する」 と整合。 本 block は **起案 / 実行段階の事前 gate**、 Tier policy は **PR review段階の Tier 判定**。 同じ事象を 2 layer で覆う設計。
