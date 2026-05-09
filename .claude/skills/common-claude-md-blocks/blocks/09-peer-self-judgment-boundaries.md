## peer self-judgment境界 (kimny手動作業ゼロ原則)

peerは可能な限り kimny介在なしで自走完結する。安全側に倒しすぎてkimnyに承認を求めるのも非効率。境界線で判断する。

### peer自走OK (kimny介在不要)

- private GitHub repo作成 (`gh repo create kimny1143/<name> --private`)
- ローカルブランチ作成・PR作成・self-review (Tier 1)
- ローカルfile操作・dependency install
- reversibleなローカル設定変更
- private repo内のCLAUDE.md / docs / コード変更 commit & push

### Escalation対象 (kimny or conductor承認必要)

- 外部公開発言 (twitter / public docs / blog)
- 本番環境設定 (Vercel / Cloudflare / GitHub Actions secrets)
- public repo化 / public release
- 認証・セキュリティ (OAuth、API Key、トークン)
- 価格・原価率変更
- 破壊的DBスキーマ変更
- 新規外部サービス・API導入

### 判定3軸

何かを「kimnyに確認すべきか」迷ったら、まず以下3軸で判定:

1. **reversible** か (簡単に元に戻せるか)
2. **外部公開** か (kimny以外の第三者の目に触れるか)
3. **本番影響** か (本番環境/データ/設定への波及があるか)

→ 3軸とも安全側ならpeer自走OK。1つでも該当ならconductor or kimnyに上げる。

### Why

2026-05-09 conductor判断で確立。occur peerが「GitHub repo作成はkimny手動か」と質問した際、conductorが「private repo + reversible は peer自走OK」と回答。安全側に倒しすぎてkimnyに承認を求めるのは「kimny手動作業ゼロ原則」に反する。
