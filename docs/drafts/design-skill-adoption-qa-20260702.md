# デザインスキル採否 — PWA-ready QA draft (2026-07-02)

- 起案: CCO (template課)。conductor endorse 済 (2026-07-02)。
- 用途: gw-dash QA タブへ conductor が load するための PWA-ready 素材 (pwa-dashboard §1 形式)。
- framing: 「採用: frontend-design + ui-design-brain / 見送り: clone-website + brand-design-md / theme-factory は任意」。plain-japanese-public 準拠 (専門用語を日本語化)。
- 根拠 = `docs/drafts/design-skill-acceptance-audit-20260702.md` (supply-chain 6-gate 監査)。

---

## Q: LPデザインを強化する「デザインスキル」4件の採否（外部スキルの安全監査 完了）

LPデザインをAI（Claude Code）側で強化するため、外部で公開されているデザイン用スキルを探し、安全性を精査しました。1件ずつ実物のファイルを読んで確認しています（インストールや実行は一切せず、中身だけを確認）。結果、次の採否を提案します。

【入れる（採用）を提案】
・frontend-design（Anthropic公式）… 「テンプレっぽい見た目を避けて意図的なデザインを作る」ための手引き文書。動作するコードは一切なく、手引きの文章だけ＝リスク最小。今ある ui-ux-pro-max を「美的な方向づけ」の面で補います。
・ui-design-brain（MITライセンスの公開スキル）… ボタン・表・フォームなど60種類以上のUI部品の作法集。これも動作コードなしの資料のみ＝安全。付属の部品一覧を一度通読してから入れます。

【入れない（見送り）を提案】
・clone-website … 他人のサイトを丸ごとそっくり複製するツール。技術的な不正コードはありませんが、他社サイトの複製は著作権・利用規約に触れるおそれがあり、MUEDの使い方に合いません。参照デザインの取り込みは Claude Design（製品）側で足りるため、今は不要と判断。
・brand-design-md … 有名ブランド風デザインを作るスキルですが、使うたびに外部パッケージを「最新版」で自動的に取ってきて実行する作り。中身を固定できず、将来もし悪意ある版に差し替わっても自動で動いてしまう危険（＝導入時に外部から引き込むコードの安全性を担保できない）があるため不採用。

【任意】
・theme-factory（Anthropic公式）… 色＋フォントの既製セット10種。安全ですが価値は限定的。入れても入れなくてもOK。

急ぎではありません（LP再挑戦の本筋は Claude Design 製品の再走で、この導入はそれを止めない並行作業です）。この採否でよければ「推奨でOK」を押してください。個別に変えたい点があれば教えてください。
推奨: この採否でOK（採用: frontend-design と ui-design-brain ／ 見送り: clone-website と brand-design-md ／ theme-factory は任意）
