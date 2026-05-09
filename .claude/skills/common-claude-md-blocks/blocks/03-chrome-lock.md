## Chrome拡張ロック制

chrome拡張（claude-in-chrome）は共有リソース。同時に1課しか使えない。

**利用フロー（先着制 / 2026-04-22〜）:**
1. 使いたい課がconductorに「Chrome使います」と宣言
2. conductorが即時許可（先着順・確認不要）。ロック中の場合のみ待機を伝える
3. 使用完了後、conductorに「Chrome解放」を通知
4. conductorがロックを解除・次の待機課に通知

**ロック中に別の課がリクエストした場合:** 待機。先行課の完了を待つ（conductorが通知）。
