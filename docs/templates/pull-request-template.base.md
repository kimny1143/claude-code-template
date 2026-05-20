<!--
共通 PR テンプレート (base)。
source of truth = claude-code-template/docs/templates/pull-request-template.base.md

各 peer は本 base を自 repo の `.github/pull_request_template.md` に copy し、
「成果物 verify」 section のキャラクター gate 行を自課のものに 1 行 fill する。
改訂時は conductor relay 経由で再配布。
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

- [ ] 型チェック通過
- [ ] lint 通過
- [ ] ビルド成功
- [ ] テスト通過 (該当する場合)

## 成果物 verify

<!--
機械チェックとは別工程。 「コードが壊れていない」 と 「成果物が実際に使える」 は別物。
UI / 成果物変更を含む PR は本 section を必須で埋める。 証拠なしには「通過」と書けない。
-->

- [ ] キャラクター gate 確認 — <!-- 自課のキャラクター gate を 1 つ明記。 例: 実機で実際に遊べる / 試聴で音のキャラクター / 外部読者として読める / 実 URL で表示・操作できる -->
- [ ] スクショ / 録画 を添付した (UI / 成果物変更 PR は必須)

## 証拠

<!--
スクショ / 録画 / 実行ログ のリンクや画像を貼る。
「見た」 と書くだけ・証拠が残っていない = 未検証扱い。 evidence なしの「通過」記載は無効。
-->

## Test plan

<!-- 確認手順を箇条書き。 reviewer が再現できるレベルで -->
