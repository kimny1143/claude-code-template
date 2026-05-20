<!--
template課 PR テンプレート。 base = docs/templates/pull-request-template.base.md
キャラクター gate 行のみ template課用に fill 済。 base 改訂時は本 file も同期する。
-->

## Summary

<!-- 何を・なぜ変えたか 1-3 行 -->

## Tier

<!-- tier-judge skill で判定。 該当する 1 つを残す -->

- [ ] Tier 1 — docs / データ / コピー / テスト追加のみ → `[self-review]` セルフマージ
- [ ] Tier 2 — コード変更あり・Tier 3 非該当 → `[peer-review: {課名}]` 同部署ピアレビュー
- [ ] Tier 3 — 価格 / 認証 / 破壊的スキーマ / 本番設定 / 外部サービス / template課 / 全課波及 hook → conductor 提出

## 機械チェック

<!-- ツールが判定する工程。 全て pass を確認 -->

- [ ] 型チェック通過 (該当する場合)
- [ ] lint 通過 (該当する場合)
- [ ] ビルド成功 (該当する場合)
- [ ] テスト通過 (該当する場合)

## 成果物 verify

<!--
機械チェックとは別工程。 「コードが壊れていない」 と 「成果物が実際に使える」 は別物。
UI / 成果物変更を含む PR は本 section を必須で埋める。 証拠なしには「通過」と書けない。
-->

- [ ] キャラクター gate 確認 — distribute 系 script の `--dry-run` 出力を目視し、 全配布対象課で意図通りの差分か (誤配布・clobber なし) を確認した
- [ ] スクショ / dry-run 出力 を添付した (配布物 / script / skill 変更 PR は必須)

## 証拠

<!--
dry-run 出力 / 配布差分 / 実行ログ のリンクや貼り付け。
「見た」 と書くだけ・証拠が残っていない = 未検証扱い。 evidence なしの「通過」記載は無効。
-->

## Test plan

<!-- 確認手順を箇条書き。 reviewer が再現できるレベルで -->
