# 受託案件 repo/peer ライフサイクル runbook（恒久フロー）— draft 2026-07-03

- [ ] conductor / kimny 確認
- 状態: run #1（初弾案件）で得た手順を汎用化した proposal。実運用で追記する。
- 管理者: **template課（受託テンプレ＋本フローの正本管理者）**
- 正本テンプレ: `gw-contract-template`（恒久 home は本 runbook §6 の open Q）

## 0. 原則（全 stage 共通の厳守事項）

- **案件 repo はクライアント資産。** MUED / glasswerks 系の skill・DS・内部 ops 記述・secrets を、コード・commit 履歴・README のいずれにも持ち込まない。
- **窓口は kimny 一本。** クライアント／デザイナーへの直接連絡・成果物送付はしない。
- **外部リソース（GitHub repo 新設・独自ドメイン・有料アカウント）は kimny gate。** template課／conductor は提案止め。
- **共有 script（`start-all-peers` 等）の変更は conductor / kimny sign-off 前に行わない。**
- credential はクライアント名義環境にのみ置き、MUED 系 vault と分離する。

## 1. Intake（kimny）

1. private な空の client repo を作成（kimny）。
2. `_<project>` workspace を用意し engagement peer を起動（standby）。
3. client repo 用 CLAUDE.md 固有欄（案件名・クライアント・仕様書 path・フェーズ）を記入、spec を `docs/spec/` に seed。

## 2. Scaffold（template課 = setup owner）

1. **`.gitignore` を先に配置**（`.DS_Store` / `.env*.local` 混入防止）。
2. テンプレから未コピー分を配置: `.env.example` / `docs/kickoff-checklist.md` / `docs/handover/ops-manual-template.md`。
3. **README はクライアント資産用に中立化**して配置（テンプレ home 版の内部 ops 記述＝template課管理・advisory 事業サンプル等を client repo 履歴に残さない）。CLAUDE.md・spec は seed 済を尊重。
4. 固有欄の案件名／クライアント表記が kimny 表現と整合するか確認。曖昧なら conductor 経由 kimny へ。
5. `git init -b main` → origin 追加 → **staged 内容を検証**（secrets 無・`.DS_Store` ignored・`.env.local` 未 track）→ initial commit（client-neutral message）→ push。
   - 初回 commit は空 repo bootstrap ゆえ main 直 push が正（PR 対象の base が無い）。以降の変更は branch + PR。

## 3. Skill / MCP provisioning（提案 = template課 / gate = conductor→kimny）

- **Phase 0（中立・無コスト・install 可）**: neutral な web 開発 skill（外部由来のみ）＋ `claude-in-chrome`（モック視覚 QA）。MUED 由来の convention skill・design 系は使わない。
- **Phase 1+（kimny gate・kickoff-checklist の名義 gate 依存）**: 実接続を伴う外部／コスト footprint（Vercel deploy・microCMS/Supabase/Resend の実 key・決済）。クライアント名義アカウント確定後に有効化。
- 詳細な set は案件ごとに judgment-request（OPTIONS/RECOMMENDATION・Phase 分け）で提出。

## 4. Phase 運用

- **Phase 0**: engagement peer 直行可（審議ゲート省略・kimny 承認済）。shadcn-landing-page 標準の中立見た目のまま 1〜2 日でモック。デザイン判断は先行せず `TODO(design):` で止める。
- **Phase 1+**: 標準 claudepeer フロー（conductor 経由）。着手前に kickoff-checklist（名義・secrets 分離）を完了。

## 5. 監視・集約（conductor / cowork）

- engagement peer は標準 status.md 形式を守り、conductor / cowork aggregation が拾える状態にする。
- ただし**時限的な受託案件である旨を status に明示**し、close 時の消滅を「stall」と誤検知させない（真 stall 判定＝未 commit 編集の有無）。
- **restart / `start-all-peers` への取り込みは default しない**（受託ピアは常設しないの原則）。案件中の永続化が要る場合のみ conductor/kimny sign-off の上で個別対応。

## 6. Close（畳み＋還流）

1. handover 完成（`docs/handover/` の運用手順書をスタッフ実地確認まで）。
2. kimny の各サービス権限を棚卸し、repo 移管有無をクライアントと確認。
3. workspace / peer を畳む。
4. **template 還流**: 汎用化できた改善を issue にまとめ template課へ dispatch → template課が `gw-contract-template` に反映（案件 repo を直接テンプレ化しない）。

## Open Questions（conductor / kimny 判断）

1. **テンプレ恒久 home**: (A) private GitHub repo 新設〔推奨・kimny gate〕/ (B) 当面 local tracked git repo / (C) 現状 Dropbox 直管理〔版管理なし・非推奨〕。いずれも前提として、テンプレ内の**実クライアント spec を placeholder 化**し README の案件言及を中立化する「テンプレ化」が必要。
2. engagement peer を restart script に載せるか（推奨: 載せない＝ephemeral 維持）。
3. cowork aggregation への時限案件の載せ方（消滅を stall 誤検知しない標識）。

## テンプレ home 確定時に適用する queued 編集

テンプレ恒久 home（Open Q #1）が確定したら、以下をまとめて「テンプレ化」バッチで適用する。home 決定まで live テンプレ（現 Dropbox 原本）は触らない。

1. **実クライアント spec を placeholder 化**（現テンプレの `docs/spec/` に実案件 spec が残存）。
2. テンプレ home 用 README の案件言及を中立化（reusable テンプレとして client-agnostic に）。
3. **【D3 / 2026-07-04・kimny 批准・Chief 正本 `_chief/decisions/jutaku-web/`】受託テンプレ CLAUDE.md 技術規約に stack 標準 carve-out を1行追記**（Next 指定は既存ゆえ追記が主）。proposed 文言:
   > - **標準 stack は上記 Next.js 構成。WordPress は例外**（客名指し＋予約コア〔審査/仮押さえ〕不要のシンプル案件のみ・都度見積。理由: 予約コアが plugin 型を外れ custom PHP 化し、WP は状態が git 外でエージェント保守モデルが破綻するため）。

   ※ 受託テンプレ共通規約の変更は kimny 承認必須だが本 D3 は kimny 批准済。適用時は Tier3 相当（受託ライン全案件に波及）で conductor 経由。
