## /plan 発動条件

Opus固定下、/plan は設計段階を明示する cognitive context separator。

### 発動する
- 新規 skill / hook の設計 (SKILL.md・挙動仕様を 0 から書き起こす)
- 既存 skill / hook の**仕様変更**を伴う書き換え (挙動・トリガー・入出力・対象ファイルが変わる)
- 全課配布の設定変更で複数課の運用に影響 (settings.local.json / .mcp.json / validate-dangerous-ops-v2.sh 等)
- 全 peer ガードレール追加・運用ルール策定

### 発動しない
- 誤字・例示・コメント・文言・ログ表現の調整 (仕様非変更)
- skills-lock.json 更新、setup.sh 既定値差し替え、hook 閾値の微調整
- distribute-*.sh の既存ロジック踏襲実行 (--dry-run 含む)
- 既存 command の文言調整 (/commit /pr /ship /build-fix /learn /security /ios)

判定は「新規ファイル作成 or 仕様変更を伴う書き換え」か「誤字・パラメータ・ログ文言・既定値差し替え」かの質的判定で切る。量的閾値は使わない。迷ったら発動なし側に倒す。
