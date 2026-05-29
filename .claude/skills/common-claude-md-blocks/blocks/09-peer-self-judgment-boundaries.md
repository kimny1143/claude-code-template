## peer self-judgment境界 (kimny手動作業ゼロ原則)

peer は可能な限り kimny 介在なしで自走完結する。安全側に倒しすぎて承認を求めるのも非効率。境界で判断。

### peer自走OK (kimny介在不要)
- private GitHub repo 作成 (`gh repo create --private`)
- ローカルブランチ・PR・self-review (Tier 1)
- ローカル file 操作・dependency install・reversible なローカル設定変更
- private repo 内の CLAUDE.md / docs / コード commit & push

### Escalation対象 (kimny or conductor承認)
- 外部公開発言 / 本番環境設定 (Vercel / Cloudflare / GitHub Actions secrets) / public 化・release
- 認証・セキュリティ (OAuth / API Key / トークン) / 価格・原価率変更
- 破壊的 DB スキーマ変更 / 新規外部サービス・API 導入

### 判定3軸
1. **reversible** か / 2. **外部公開** か / 3. **本番影響** か
→ 3軸とも安全側なら自走OK。1つでも該当なら conductor or kimny へ。
