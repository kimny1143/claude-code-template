# Codex pre-TF QA gate rule — design doc 段階 (P0-2)

- 状態: **design doc 昇格 2026-05-27** (Tier 1 self-review、 full impl = Tier 3 別 PR)
- conductor 5/27 GO: 本 PR では design doc 昇格のみ、 `.claude/rules/` 新設 + setup.sh SHARED_RULES 拡張 + 全 peer 配布は Tier 3 PR で kimny final approval 後 ship
- [ ] kimny確認 (Tier 3、 全 peer 波及 rule のため最終承認必須)
- [x] conductor承認 — 2026-05-26 10:13 JST 頃 (解釈 (ii) 確定、 原本 draft 着手 GO)
- 起源:
  - kimny directive 2026-05-19 14:50 JST 「君たちがチェックできないんだったら、 このチェックをコーデックスに振ろうよ」
  - conductor memory `feedback_codex_pre_tf_qa_gate.md` (5/19 起案、 kimny 承認済)
  - trilateral 議論 P0-2 audit (5/26、 `.claude/rules/codex-pre-tf-qa-gate.md` 全 _DevProjects 配下不在 confirm)
- 配置先想定: `.claude/rules/codex-pre-tf-qa-gate.md` (template repo 正本、 setup.sh SHARED_RULES で全課配布)
- ETA: 5/27 Phase 2 Gate 前 kimny review path

## 0. 本 draft の構成

本 doc は **3 段構成**:
1. **(A) 提案 rule file 本体** — kimny review 後 そのまま `.claude/rules/codex-pre-tf-qa-gate.md` として配置
2. **(B) 配布 infra patch** — `.claude/rules/` dir 新設 + `setup.sh` SHARED_RULES 拡張 diff
3. **(C) Tier 3 escalation + rollout 計画** — kimny final approval → 配布 → 監視 path

---

## (A) 提案 rule file 本体 (`.claude/rules/codex-pre-tf-qa-gate.md`)

```markdown
# Codex pre-TF QA gate

iOS / native app の TestFlight upload 前に、 Codex (GPT-5.4 系) による独立 verify gate を必須として通す rule。 Claude 系 (conductor + native peer) では見逃した基本 UX bug (ボタン見切れ / overflow / 操作不能 area 等) を Codex の独立視点で audit する layer 強制化。

## 起源 + 根拠

- 2026-05-19 14:50 JST kimny directive: 「君たちがチェックできないんだったら、 このチェックをコーデックスに振ろうよ」
- 2026-05-19 Build 78 試遊で 5 ゲーム全部 graphical UI に押されて Next ボタンが画面外で **試遊続行不可** 状態が判明
- 5/17 Build 70 「ハリボテ」 事案で `feedback_simulator_verify_before_tf_upload` memory 起案済だったが、 simulator verify の自走 enforcement が薄く、 「TypeScript 0 errors + GitGuardian SUCCESS + Apple Archive Success = test 通った」 と誤認して kimny に試遊させた
- Codex 経営陣入り (`project_codex_executive_review_role` memory) を UX QA gate として自然 extension、 Claude 系の見落とし risk を Codex で 2nd opinion 強制化

## Layer 構造 (本 rule の位置付け)

| Layer | 対象 | rule / memory | 役割 |
|-------|------|---------------|------|
| Layer 1 | simulator manual テスト | `feedback_simulator_verify_before_tf_upload` (memory) | peer 側 dynamic verify、 1 full cycle + regression verify |
| **Layer 2** | **Codex 独立 UX audit** | **本 rule** | **conductor 側 third-party visual audit、 Claude 盲点 cover** |
| Layer 3 | kimny 実機 final verify | (暗黙、 production deploy 前 kimny 確認) | 最終承認 |

Layer 2 は Layer 1 を skip する代替ではなく、 **Layer 1 + Layer 2 の両方** を必須通過させる。

## 適用 scope

### ✅ 適用対象

- iOS / TestFlight upload を伴う全 PR (現 native peer 範囲)
- React Native / Expo app の TF upload を伴う PR
- (将来) Android / Play Store upload (Phase 拡張 dispatch 時に追加判断)

### ❌ 適用対象外

- peer 内部 PR (test pass + lint clean のみで自走 OK)
- docs-only PR
- CI / linter / dependency update のみ
- schema migration only (UI / business logic 変更なし)
- 緊急 hotfix (production crash 等、 production verify path 優先、 ただし next iteration で本 gate 追完納)

## Protocol — peer 側 (native peer 等)

1. **Layer 1 完納**: simulator verify protocol per `feedback_simulator_verify_before_tf_upload`
   - 1 full cycle テスト (ゲーム選択 → 1 ゲーム → 結果 → 広告 → 次ゲーム連続プレイ → 履歴反映 → 連続 2-3 回)
   - regression verify 明示
   - screenshot 3-5 枚 + console.log 抜粋
   - self-check 4 要素 (A/B/C/D) per `feedback_code_through_vs_mvp_completion`

2. **PR description 記載**:
   - 「実証フェーズ通過 evidence」 section per existing template
   - screenshot 全部 inline
   - self-check 4 要素全て
   - **「pending Codex pre-TF QA gate」 marker 明示** (本 rule 適用 PR の signal)

3. **PR を draft 状態で push**、 TF upload **しない**。 conductor に ping。

4. conductor → Codex 独立 verify → GO ack 受領 **後に** TF upload。

## Protocol — conductor 側

1. **native peer ping 受領**

2. **PR description + screenshot を Codex に dispatch**:

   ```bash
   codex exec --full-auto "
   以下 PR の TestFlight upload 前 UX audit を実施してください。

   PR URL: <pr_url>
   PR description: <pr_body_inline>
   screenshot files: <screenshot_paths_inline>

   検証項目:
   1. ボタン見切れ (画面外 / 部分隠れ)
   2. viewport overflow (横スクロール / 下端切れ)
   3. 操作不能 area (タップ反応なし、 modal blocking)
   4. viz サイズ妥当性 (グラフ / 画像 / icon の相対サイズ)
   5. state 遷移整合性 (画面遷移後の戻り経路、 empty state、 loading state)
   6. 連続操作時の regression (前画面の状態が次画面に正しく反映されるか)

   出力 format:
   - 結論: GO または NG
   - NG の場合: 具体的 issue list (画面名 + 問題 + 影響度 high/mid/low)
   - GO の場合: 確認した evidence 要約 (短く)
   "
   ```

3. **ETA 5-10 分** で Codex GO / NG report

4. **GO の場合**: native peer に TF upload GO relay

5. **NG の場合**: native peer に修正 dispatch:
   - 修正 → 再 Layer 1 simulator verify → 再 Codex review (本 protocol 繰り返し)
   - cycle limit なし (kimny frustration 回避優先 > cycle 短縮)

## トレードオフ

- ⏱ +5-10 分 / TF upload cycle = kimny frustration 回避 + ハリボテ risk 撤廃
- 🎯 Codex は経営陣入り設計 (`project_codex_executive_review_role`) の有効活用、 Claude 系盲点 炙り出し layer 強化
- 💰 Codex CLI 利用コスト (現状 codex CLI 無料 tier 範囲内想定、 月次コスト超過時 conductor escalation)

## 例外 (本 gate skip 可能ケース)

本 rule の「適用対象外」 section と同等。 ただし以下は **明示的に kimny / conductor 承認必要**:
- 緊急 hotfix で本 gate skip → next iteration で追完納 (skip 履歴を memory に記録、 累積 3 回で rule 見直し dispatch)
- production critical 修正で TF expedite review path 経由 → 本 gate skip 可、 ただし post-deploy で同等 audit 実施

## 関連 memory / rule

- `feedback_simulator_verify_before_tf_upload` (memory、 Layer 1 protocol)
- `feedback_code_through_vs_mvp_completion` (memory、 self-check 4 要素 A-D)
- `project_codex_executive_review_role` (memory、 Codex 経営陣入り設計)
- `feedback_zero_kimny_manual_work` (memory、 kimny に基本 UX bug 試遊させない原則)
- `.claude/rules/dispatch-protocol.md` (conductor 課、 dispatch flow 統合)

## 履歴

- 2026-05-19: kimny directive + concept GO (memory 起案)
- 2026-05-26: trilateral 議論 P0-2 audit で rule file 不在 confirm → CCO 原本 draft 着手
- (pending) kimny final approval → 配布
```

---

## (B) 配布 infra patch

### B-1. `.claude/rules/` dir 新設 (template repo)

```
.claude/
├── agents/
├── commands/
├── hooks/
├── rules/                           # 新設
│   └── codex-pre-tf-qa-gate.md     # 本 draft の (A) 部分
├── settings.local.json
├── settings.local.json.example
└── skills/
```

### B-2. `setup.sh` SHARED_RULES 拡張 diff

setup.sh 既存構造 (SHARED_HOOKS / SHARED_SKILLS / SHARED_COMMANDS) と同 pattern で SHARED_RULES を追加:

```diff
+# 共有 rules (全課配布対象)
+# 配布先: 各 peer の .claude/rules/<file>.md
+SHARED_RULES=(
+  "codex-pre-tf-qa-gate.md"
+)
+
 # 既存 SHARED_SKILLS / SHARED_HOOKS / SHARED_COMMANDS の定義
 ...

+# 共有 rules sync (新規 section)
+for rule_file in "${SHARED_RULES[@]}"; do
+  src="$TEMPLATE_ROOT/.claude/rules/$rule_file"
+  if [[ ! -f "$src" ]]; then
+    echo "  [SKIP] template に $rule_file 不在"
+    continue
+  fi
+  dst="$PEER_CLAUDE_DIR/rules/$rule_file"
+  mkdir -p "$PEER_CLAUDE_DIR/rules"
+  cp "$src" "$dst"
+  echo "  [SYNC] rules/$rule_file"
+done
```

note: 実 setup.sh 内 variable 名 (`TEMPLATE_ROOT` 等) は既存実装に合わせて修正。 draft では概念示唆のみ。

### B-3. peer 既存 `.claude/rules/` との整合

現状:
- conductor `.claude/rules/`: 4 files (current-organization / dispatch-protocol / plain-japanese-public / reporting) = **peer 固有 + 全課共有 混在**
- write `.claude/rules/`: 3 files (articles / hoo / ops) = **peer 固有のみ**

設計判断: **SHARED_RULES は「全課共有 rule」 のみ対象**、 peer 固有 rule (conductor 4 / write 3 等) は peer 側 own、 SHARED_RULES に含めない。

将来 plain-japanese-public.md 等が全課共通 rule 化した時 → SHARED_RULES に追加 + conductor から template に正本 promote の dispatch path で対応。

### B-4. Gap 1 audit-peer-drift script への impact

Gap 1 script (本 trilateral input deliverable) の SHARED_HOOKS audit 対象を SHARED_HOOKS + SHARED_RULES に拡張:

```diff
 SHARED_HOOKS=(
   "block-main-push.sh"
 )
+SHARED_RULES=(
+  "codex-pre-tf-qa-gate.md"
+)
 COMMON_SKILLS=(
   "peer-id-lookup"
   "tier-judge"
   "plan-mode-policy"
 )

 # ... audit loop で rules セクション追加
+  for rule in "${SHARED_RULES[@]}"; do
+    audit_item "$division" "rules" "$rule" "$RULES_SRC/$rule" "$peer_base/rules/$rule"
+  done
```

→ Gap 1 と本 P0-2 が **同 cycle で完納すると配布監視 が即 ready** = 効率良し。

---

## (C) Tier 3 escalation + rollout 計画

### C-1. Tier 判定

- **Tier 3 (全課波及 rule + setup.sh 拡張)**
- 理由: 全 peer の `.claude/rules/` dir に新規 file 配布 + setup.sh の SHARED_RULES 機構新設 = 全 peer の rule load 仕組み変更
- kimny 直接承認必須 (CLAUDE.md `PRレビュー権限` 判断フロー Step 1 「template 課からの変更（全課に波及）」)

### C-2. rollout sequence

| step | date 想定 | 担当 | 内容 |
|------|----------|------|------|
| 1 | 5/26 (本日) | CCO | 本 draft 完納 + conductor → kimny notify |
| 2 | 5/27 Phase 2 Gate 前 | kimny | rule 内容 + setup.sh patch + 配布計画 final approve |
| 3 | 5/27 Phase 2 Gate 後 | CCO | feature branch `feat/codex-pre-tf-qa-gate-rule` 起票 (`.claude/rules/` dir + 原本 file + setup.sh patch) |
| 4 | 5/27-5/28 | CCO | PR 起票 + conductor review (Tier 3) |
| 5 | 5/29 | kimny / conductor | PR final approve + merge |
| 6 | 5/29-5/30 | 各 peer | setup.sh 再実行で SHARED_RULES sync (peer 自走 or template 配布 dispatch) |
| 7 | 5/30 以降 | CCO + Gap 1 audit | audit-peer-drift script で SHARED_RULES 配布完納 verify |
| 8 | 6/3 | conductor + native peer | 初回 Codex pre-TF QA gate enforce (次回 TF upload で本 protocol 適用) |

### C-3. monitoring + 振り返り

- **配布完納 monitoring**: Gap 1 audit-peer-drift で SHARED_RULES drift 検知 (5/30 以降 月次 cron 化想定)
- **enforce 振り返り**: 初回適用 (6/3 想定) 後 1 週間で振り返り、 protocol 詳細を peer feedback 受けて update
- **NG 累積 monitoring**: Codex NG 出力 1 ヶ月集計、 同 type (ボタン見切れ / overflow 等) 3 件以上で UI component 設計 review dispatch

### C-4. rollback 想定

万一 rule が peer 自走を過度に阻害する場合:
- (a) scope 縮小 (現 native peer のみ → 一時停止)
- (b) protocol 緩和 (Codex ETA 5-10 分 待ちが TF cadence を妨げる場合、 dispatch async + GO 後追い相互通知化)
- (c) 完全撤回 (kimny directive あれば 即撤回 + memory update)

rollback 判断は kimny 直接、 conductor 1 cycle escalate。

---

## (D) 残 Open Q (kimny + conductor 判断必要)

1. **Codex CLI コスト**: 現状無料 tier 想定だが、 TF upload 頻度上昇時 (Phase 2 以降) 月次コスト超過 escalation 閾値 (例: $10/月超過で kimny notify) は設定すべきか
2. **Layer 2 NG 時の cycle limit**: 現 draft では cycle limit なし (frustration 回避優先)、 ただし 3 cycle 連続 NG なら設計から見直す dispatch path 追加すべきか
3. **iOS 以外 platform 拡張 timing**: Android / Play Store / web release は本 rule 対象外スタート、 拡張 trigger (例: Android TestTrack upload 開始時 自動拡張 vs 個別 dispatch 判断) を明示すべきか
4. **既 peer `.claude/rules/` の正本 promote**: conductor `dispatch-protocol.md` / `plain-japanese-public.md` 等で全課共有化候補があれば、 本 SHARED_RULES 機構を機に template 正本 promote dispatch を別 batch で実施するか
5. **rule load 仕様**: 各 peer の Claude Code session で `.claude/rules/*.md` が auto-load されるかは hook / settings 依存。 setup.sh 配布のみで効くか、 settings.local.json への参照追加も必要か、 verify が必要

## (E) 次 action (本 draft 完納後)

1. conductor へ 本 draft 完納 notify + path 共有 (CCO → n2g8vviw)
2. conductor → kimny short notification ((C-2) step 1 内 conductor 自走分)
3. kimny final approve 受領待ち (5/27 Phase 2 Gate 前想定)
4. 承認後 (C-2) step 3 以降 sequence 着手
