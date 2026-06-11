# CCO 検証 — 組織再編 統合提案 v1 (2026-06-11)

- 依頼: conductor (8yy1az2f) / kimny 起案 policy-gate (Tier3)。締切 2026-06-11 09:00 JST。
- 対象: `_conductor/docs/inbox/proposal-org-restructure-20260611.md`
- 形式: RECOMMENDATION (exec_proposal_no_rubber_stamp 適用 = 反証必須)。CCO scope = governance / template配布正本 / cowork集約。

## 総合 RECOMMENDATION: **条件付き承認** (Q1=a / Q3=a / Q4=a に賛成、下記3条件 + 反証1)

提案は real problem (判断の濁流) を解き、on-demand + 可逆 + 外部リソースゼロで downside 有界。CCO scope の懸念は (b) occur クローズ手順の**配布側 解除漏れ** (要修正) と (a) 参謀の書込分離が**規約のみで機構未裏打ち** (強く推奨)。

---

## (b) occur クローズ §3.2 の漏れ — CCO 実 grep で確定 ★最重要

§3.2 step4 は「cowork 集約から除外」のみ。だが occur は **template 配布スクリプトの ACTIVE WRITER 対象**として3箇所残存。クローズ後も除外しないと、将来の distribute 実行が**閉じた occur workspace に canonical を push** → (i) dormant peer のファイルを silently 再生成 (ii) 再開時に配布済 canonical が handoff memory の前提と乖離 (iii) 無駄書込。

| ref | 種別 | クローズ時の扱い |
|---|---|---|
| `scripts/distribute-skills.sh:53` | **ACTIVE writer** (skills push) | **除外/guard 必須** |
| `scripts/distribute-quality-standards.sh:35` | **ACTIVE writer** | **除外/guard 必須** |
| `scripts/distribute-claude-md-blocks.sh:31` | **ACTIVE writer** (CLAUDE.md push) | **除外/guard 必須** |
| `scripts/audit-peer-drift.sh:46` | read-only audit | 除外 (drift false-positive ノイズ消し、§3.2 step4 と同趣旨) |
| `_cowork/aggregate_peer_status.py:45` | 集約 | §3.2 step4 が既にカバー ✅ |
| `.claude/skills/peer-id-lookup/SKILL.md:52` | passive lookup | **残置推奨** (再開時の課名→path 解決に有用、§4 risk#4 「5分で再開」を助ける)。annotate「closed」のみ |

→ **修正条件1**: §3.2 step4 を「cowork 集約 + template 配布3スクリプト + audit-peer-drift から occur 除外」に拡張。**CCO が --dry-run 付きで実施担当**可 (distribute-*.sh の対象範囲変更ゆえ dry-run 必須 = template CLAUDE.md 規律)。peer-id-lookup は残置。
- 補足: setup.sh の SHARED_* には occur ハードコードなし (grep 0) ＝ public template 配布範囲は無影響。閉鎖は targeted distribute スクリプト側のみの作業。

## (a) 参謀 governance — 書込分離が規約のみ・機構未裏打ち

§2.1/§5-1 は「参謀は `_strategy/` のみ書く、運用ファイルは conductor single writer」を**CLAUDE.md 規約**で定める。だが現状この single-writer 不変条件は **hook 等で機構的に強制されていない**。Fable 参謀は同一マシン・同一 git 権限ゆえ、誤って peer の status.md / inbox に書いても**何も止めない**。新規 writer を系に入れる以上、規約 prose でなく構造で閉じるべき (billing 監査で学んだ「convention は draft、enforce が合格」と同型)。

→ **推奨条件2**: 参謀を **`_strategy` cwd 限定起動 + CCO の CWD-write-guard hook (out-of-CWD write block) を適用** → 「書かない約束」を「書けない構造」に。併せて `feedback_hook_allowlist_core_path_check` 適用 (Claude core path = plans/projects/settings を allowlist して bootstrap deadlock 回避)。これで §5-1 のリスクが机上保証→機構保証に。

## (c) §2.2「中間管理職不採用」整合 — 論理は成立、ただし主張が片側のみ

§2.2 の「v1 は下向き階層(conductor→peer 伝言ゲーム/規約摩耗)を退けた、参謀は kimny↔組織の上向きインターフェースで指揮権なし=摩耗するものがない」は **下向き規約摩耗の不在については正しい**。だが「摩耗するものがない」は**片側のみ**。参謀は peer語彙→平易ブリーフへ**翻訳 + 束ね直し + 優先順位付け**する = kimny が組織を見る**上向きの解釈レイヤ**を新設する。v1 が嫌った下向き伝言ゲームの**上向き対称形(組織→参謀→kimny の解釈歪み)**が生じうる。

→ **推奨条件3**: §2.2 に上向き解釈歪みリスクを明記 + de-bias 手順 (kimny が定期的に**生 status を直接サンプリング**し参謀フレーミングを較正)。可逆性 ("重複観測で畳む") の前提=「歪みは観測可能」が、framing bias には成り立ちにくい点 (下記反証) への対策にもなる。

## (d) 反証 (exec_proposal_no_rubber_stamp) ★

**single-point-of-upward-framing リスク**: 参謀は kimny と組織の間の**唯一の解釈レイヤ**になる。Codex は「点の独立検証」で kimny が結果を spot-verify できる (会計値/コード行を自分で照合可)。だが参謀の「線で並走するフレーミング」は連続的・包括的で、**独立検証しにくい**。

提案の安全弁「重複が観測されたら畳む」(§5-5・可逆) は **失敗が観測可能**であることを前提とする。しかし framing bias はまさに**内側から観測しにくい**失敗モード — kimny は組織を参謀**越しに**見るので、系統的なフレーミング偏りは「参謀の欠陥」でなく「組織の状態そのもの」に見える。= 可逆性が効くのは「明白な重複・形骸化」には対してだが、「静かな解釈偏り」には効きにくい。

これは提案を**否決する理由ではない** (de-bias 手順=条件3で緩和可、価値 > リスク) が、提案が「downside は小さい (可逆ゆえ)」と評価する箇所の**過小評価点**。条件3 (生 status 直接サンプリング) を可逆性の前提を成立させる必須要件として組み込むべき。

## (Q4) §4 default 宣言 — CCO 視点で妥当 (補足のみ)

- native active 維持 / blender pull-based dormant / reserch active-low = 妥当。CCO 自身 §4 で「変更なし」。
- 補足: blender は **cowork `aggregate_peer_status.py` の `STALE_EXCEPTION_PEERS={"blender"}` で既に stale 除外済** → pull-based dormant 宣言は集約側で部分的に先行実装済 (整合)。blender は dormant ≠ closed ゆえ配布対象のままで問題なし (occur と扱いが違う点を明確化)。
- 大型統合 (reserch+data 等) を campaign 中は見送る判断 (§4 ※) に同意 (事故リスク > 節約)。

## (G6) 即時移行への CCO 明示追認 (2026-06-11、Codex 指摘で追記) ★gate record

Codex 指摘が正当: 本 review の初版 (Q4) は「campaign 中の大型統合は事故リスク > 節約ゆえ見送り」に**同意**と記録していた。v2 はこれを kimny 裁定で**撤回し即時統合**する。よって私の「了解」は v2 即時移行の gate record として弱い (旧 defer 前提のまま)。明示追認する:

**CCO は v2 の即時移行に賛成 (追認)。** ただし下記を必須条件とする。

理由 (前 stance の更新): 私の「見送り」懸念は「**campaign-critical な熱い文脈に触れる事故リスク**」だった。v2 §63 の保護3点が、まさにその risk を firewall する:
- ① free15 計測 = insight課 母体 `_data-analysis` 継続 = **無断絶** (計測母体に触れない)。
- ② native 畳み込み = **CCO matrix が main 入り後** (review 断絶回避)。
- ③ **mued・dsp・SNS は一切触らない** (campaign 執行核を凍結)。

= 即時移行が touch するのは **WIP ゼロの非 critical peer (write/LP/blender/reserch/data) の統合のみ**。私が懸念した「熱い文脈への介入」は v2 が構造的に除外している。risk-specific だった懸念が、その risk を除く設計で解消された → stance を「見送り」から「条件付き賛成」へ**更新する** (rubber-stamp でなく、risk 評価の更新)。

**必須条件 (追認の前提)**:
1. 保護3点が各ステップで**実際に enforce** されること。特に (i) insight課統合で free15 日次計測が1回も欠測しないことを cutover 前後で確認 (ii) native 畳込は matrix main+配布完了を確認してから (iii) mued/dsp/SNS の workspace/settings/hook を移行作業で触らない。
2. matrix の main 反映は native だけでなく **content/insight 統合分も cutover 前必須** (G2。本 review の matrix draft は全課 cover 済 = 順序条件の明文化のみ)。
3. 移行は WIP ゼロ確認後 (write/LP/blender/reserch/data の未 push 差分ゼロ) に実行。

→ 3条件充足を前提に、即時移行を**追認**。1つでも崩れたら該当ステップを停止し再評価。

## まとめ (conductor §7 追記用 1段落)

CCO = **条件付き承認**。①occur §3.2 step4 を template 配布3スクリプト + audit-peer-drift の occur 除外まで拡張 (CCO が --dry-run で担当、peer-id-lookup は再開用残置)②参謀の書込分離を `_strategy` cwd + CWD-write-guard hook で機構化③§2.2 に上向き解釈歪みリスク明記 + kimny 生status 直接サンプリングの de-bias 手順。反証 = 参謀が唯一の上向き解釈レイヤになる single-point-of-framing リスク (可逆性は「明白な重複」には効くが「静かな解釈偏り」には効きにくい → ③を可逆性成立の必須要件に)。3条件充足なら Q1=a/Q3=a/Q4=a 承認。
