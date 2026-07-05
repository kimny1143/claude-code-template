# デザインスキル 深掘り brief — 中身の実体 + before/after 実例 + 代替候補 — 2026-07-05

- 状態: **draft (kimny 理解・採否用 / conductor 経由依頼)**
- 起案: CCO (template課)
- 依頼: kimny「良いデザインスキルは欲しいが、**採用前に深く理解して自分で決めたい**」(conductor relay 2026-07-05)
- 前段: `docs/drafts/design-skill-acceptance-audit-20260702.md` (supply-chain 安全監査・7-gate)。本 doc は**安全**の次の問い=「中身は何で、入れると出力がどう変わるか」に答える
- 手法: skill 本体 3 ファイルを public GitHub から re-fetch し**全文精読**(frontend-design SKILL.md / ui-design-brain SKILL.md + **components.md 全1263行**)。代替候補は source-eval 的に repo 構造 + license + 実行面を確認
- 視覚版 (kimny 提示用 before/after): 別途 Artifact

---

## 0. 3行サマリ

1. **frontend-design (公式)** = 「AI っぽい没個性な見た目」を避け、案件ごとに意図的なデザイン判断をさせる**手引き文書**。動くコードゼロ=最安全。**本命 (ADOPT)**。
2. **ui-design-brain (MIT community)** = ボタン/表/フォーム等 60 部品の**作法カンペ**。品質の下限を上げるが、既導入の `ui-ux-pro-max` と役割が重なる。**入れてよいが「重複確認」が条件**。
3. **代替**: Taste Skill (community・より高機能だが script/画像生成で実行面が広い) / brand-guidelines (公式だが中身は "Anthropic 社のブランド" 専用=そのままでは MUED に無価値・雛形としてのみ有用)。

---

## 1. 中身の実体 — 各スキルが peer に「何を注入するか」

### 1-A. frontend-design (Anthropic 公式・`anthropics/skills`)

**物理的実体**: `SKILL.md` (約 8.3KB / 56 行) + `LICENSE.txt` の**2ファイルのみ**。スクリプト・バイナリ・ネットワーク呼び出し・npx 一切なし=**純粋な散文の手引き**。読み込むと Claude の「頭の中の作り方」が変わるだけで、何も実行されない。

**注入される中身 (実際の指示の骨子)**:

| セクション | 何を指示しているか |
|-----------|-----------------|
| 冒頭 role | 「小さなスタジオのデザインリード。**どのクライアントにも "他と見分けがつかない見た目" を出さない**。templated な提案は既に却下されている。意図的で意見のあるパレット/タイポ/レイアウト判断をし、**正当化できるリスクを1つ取れ**」 |
| Ground it | brief に主題が無ければ**まず主題・想定読者・そのページの唯一の仕事を自分で確定**してから設計。memory にユーザー好みの記録があればヒントに。「主題の世界・素材・専門用語」から固有の判断を引く |
| Design principles | **hero は主張(thesis)**。「大きな数字 + 小ラベル + グラデアクセント」は**テンプレ回答=真に最善の時だけ**。タイポは個性の担体(display/body を毎回同じ手癖で選ぶな)。番号 01/02/03 は**本当に順序が情報を持つ時だけ**。装飾のためのモーションは "AI 製っぽさ" を増やす |
| Process (2-pass) | **① brainstorm**: color(4-6 の命名 hex) / type(2+ 役割の書体) / layout(ASCII ワイヤー) / **signature(そのページが記憶される唯一の要素)** の token 体系を先に作る → **② 自己批判**: 「これは似た依頼なら誰にでも出す generic default か?」を検証し、該当箇所を改訂・変更理由を明記 → その後にコード化 |
| Restraint | 大胆さは1箇所に集中(signature)、周りは静かに。**Chanel の教え「出かける前に鏡でアクセサリを1つ外せ」**。品質下限(モバイル対応/フォーカス可視/reduced-motion)は宣言せず満たす。スクショで自己批判 |
| Writing | UI コピーも設計材料。**能動態("Save changes" not "Submit")・動作名は全フロー通し一貫("Publish"→toast"Published")・エラーは謝らず何が起きたか具体的に・空画面は行動への招待** |

**要は**: 「作る前に主題を掴み、token 体系と signature を先に決め、"AI の定番3クラスタ" を避け、自己批判してから初めてコードを書け」という**プロセスと美学の規律**を注入する。実装力ではなく**方向性の言語化**を与えるスキル。

**AI 定番3クラスタ (これを避けろ、と名指しされている)**:
1. 温かいクリーム背景 (≈#F4F1EA) + 高コントラスト serif 見出し + テラコッタのアクセント
2. ほぼ黒背景 + 単色の派手なアシッドグリーン/朱のアクセント
3. broadsheet 風 (hairline 罫線・角丸ゼロ・新聞的な密な段組)
→ 「どれも一部の brief には正当。だが主題に関係なく現れるなら "選択" でなく "既定値"。自由な軸をこの既定値に費やすな」

### 1-B. ui-design-brain (community・`carmahhawwari/ui-design-brain`・MIT・830★)

**物理的実体**: `SKILL.md` (約 8.3KB) + **`components.md` (約 44KB / 1263 行)** + `LICENSE.txt` + README。**全文精読の結果、実行面ゼロを最終確認** (監査時の唯一の residual = components.md 未通読 → 本 deepdive で解消。純粋な reference 散文で、埋め込みコード/ネットワーク/injection なし)。

**注入される中身**:

- **SKILL.md** = 設計哲学 + ワークフロー。核の原則6つ: ①装飾より抑制(余白は機能) ②タイポで階層(display×body の weight 差) ③強い色は1つだけ(neutral 先行+自信ある accent 1色) ④8px グリッド ⑤アクセシビリティ非交渉(WCAG AA/フォーカス/セマンティック HTML) ⑥**generic AI 美学を避ける**(purple-on-white グラデ・Inter/Roboto 既定・等間隔カードグリッド禁止)。加えて5つのスタイル preset (Modern SaaS / Apple-level Minimal / Enterprise / Creative / Data Dashboard) と、コード生成時の stack ルール (React+Tailwind / 8px / hover-focus-active-disabled 全実装 / 375-768-1440 で responsive)。
- **components.md** = **60 部品の作法カンペ**。各部品に「別名 / 定義 / best-practices 5-6項 / common-layouts 3-4例」。例:
  - **Button**: primary(filled)/secondary(outlined)/tertiary(text) の階層 / 動詞始まりラベル / 最小 44×44px / 非同期時は内部 spinner + disable で二度押し防止 / 1画面に primary 1つ
  - **Form**: 単一カラム / label は input の上 / **blur 時にインライン検証(毎キーストロークでない)** / 必要な項目だけ
  - **Table**: sticky ヘッダ / 数値は右寄せ / ソート可能 / モバイルは横スクロール(列を隠さない)
  - **Empty state**: イラスト + 助けになる見出し + CTA / 非難しない("No projects yet" not "You have no projects")
  - **Skeleton > Spinner**: 予測可能なレイアウトは skeleton (300ms 遅延後表示)
- **末尾**: 15 部品の quick table + **Anti-Patterns**(絶対に生成するな): rainbow badge / modal-in-modal / 理由なし disabled submit / 予測可能レイアウトへの spinner / "Click here" リンク / desktop でのハンバーガー / 自動送りカルーセル / placeholder のみのフォーム / 等 weight ボタン / 12px 未満の極小文字

**要は**: 「コードを書く前に、各 UI 部品の "senior SaaS デザイナーなら知っている作法" を参照させ、典型的な素人ミス(a11y 欠落・状態欠落・no hierarchy)を潰す」**品質の下限引き上げ**スキル。

### 1-C. 2つの役割の違い (重要)

| | frontend-design | ui-design-brain |
|--|----------------|-----------------|
| 与えるもの | **美的方向性 / プロセス規律** (このページを "どう見せるか" の判断力) | **部品の作法 / 品質下限** (各部品を "どう正しく作るか" の知識) |
| 効く場面 | 0→1 の見た目・個性・記憶に残るか | 実装の正しさ・アクセシビリティ・状態網羅 |
| 希少性 | 高 (方向性を言語化する skill は少ない) | 中 (作法系は既存 skill と重なる) |
| 既存資産との関係 | `ui-ux-pro-max` の実装力に**方向性**を補完 | `web-design-guidelines`(準拠レビュー) / `ui-ux-pro-max` と**役割が重複** |

---

## 2. before/after — 入れると出力が具体的にどう変わるか

> ※ 実際の live LP を peer repo から引くのは所有境界を跨ぐため、**代表的な画面 archetype で機構を実演**する (skill 有無で Claude の出力がどう分岐するかを忠実に再現)。視覚レンダリング版は Artifact 参照。

### 例1: advisory LP の hero (frontend-design の効果)

**BEFORE (skill 無し = 素の Claude が出しがちな default)**:
- フォント: Inter / system-ui (無選択)
- hero: 中央寄せ H1「Strategic advisory for modern teams」+ subtext + 紫→青のグラデ CTA「Get Started」
- その下: 等間隔の3カードグリッド(アイコン+見出し+2行)
- stats: 「500+ Clients / 10+ Years / 24/7 Support」の大数字トリオ
- → **どの advisory/SaaS の LP とも見分けがつかない**。主題(この advisory の固有性)がどこにも出ていない

**AFTER (frontend-design 適用)**:
- Claude はまず主題を確定させる (例: 「音楽制作スタジオ向けの事業顧問」→ 想定読者・ページの唯一の仕事=「戦略相談の予約」)
- token 体系を先出し: 4-6 の命名 hex / display×body を主題に合わせ意図的にペア / **signature = スタジオの素材・専門用語から引いた1要素** (例: ミキサーのフェーダーを模した進捗表現、譜面的なグリッド 等)
- hero は「大数字テンプレ」を却下し、主題の最も特徴的なものを主張として置く
- CTA は動詞始まり「戦略相談を予約」、押した後の toast も「相談を予約しました」で一貫
- 「AI 定番3クラスタ」に寄っていないか自己批判 → 該当なら改訂
- → **この advisory 固有の point of view を持つ hero**。他社の LP と入れ替え不能

**正直な注記**: frontend-design は「良いデザインを保証する」ものではない。**templated から遠ざけ、意図的判断へ寄せる bias** を与えるだけ。brief が薄ければ効果も薄い。保守的な B2B で「1つのリスクを取れ」が外すこともある(=tradeoff)。

### 例2: MUEDear の1画面 — オンボーディング/フォーム (ui-design-brain の効果)

**BEFORE (skill 無し)**:
- 入力欄が placeholder のみ(ラベル無し) → 入力すると何の欄か消える + a11y NG
- ボタンが全部同じ見た目(primary/secondary の区別なし)
- 読み込み中は中央 spinner
- ステータス badge が項目ごとに違う派手色(意味と無関係)
- ボタン文言「Submit」、リンク「Click here」
- 空状態は白紙、エラーは「Something went wrong」

**AFTER (ui-design-brain 適用)**:
- ラベルは input の**上**に常設 / placeholder は書式ヒントのみ / 検証は blur 時にインライン
- primary は1画面1つ + secondary/tertiary の階層 / 44px タッチターゲット / フォーカスリング可視
- 予測可能な画面は **skeleton (300ms 後)** で spinner を置換
- badge は限定パレット + セマンティック(active/pending/archived)
- 文言は動詞始まり / 空状態は「イラスト + 見出し + CTA」で行動へ誘導 / エラーは何が起きたか具体的に
- → **素人ミスが消え、"senior SaaS デザイナー" の下限に届く**

**正直な注記**: この効果の多くは既導入の `ui-ux-pro-max` / `web-design-guidelines` でも部分的に得られる。ui-design-brain の**限界利益 = 「コードを書く前に参照する 60 部品の事前知識」**(既存はレビュー=事後寄り)。重複度が高ければ限界利益は小さい。

---

## 3. 代替候補 (source-eval・他サイト複製系は除外)

| 候補 | 出所/license | 実体 | 実行面 | 評価 |
|------|------------|------|-------|------|
| **Taste Skill** (`Leonxlnx/taste-skill`) | community / **MIT** / ~37-55k★ | 「anti-slop」frontend skill 群 (11 variant + 画像生成3)。core `SKILL.md` は brief 推論 + **3ダイヤル(DESIGN_VARIANCE / MOTION_INTENSITY / VISUAL_DENSITY)** の equalizer 方式。core 散文は frontend-design より**操作的で richer** | **広い**: repo に `scripts/` `skill.sh` + `imagegen-frontend-web/mobile`(外部画像 API 呼び出し) | **core 散文のみ採るなら低リスク**(frontend-design と哲学重複=限界利益小)。**suite 全体採用は full 監査要**(実行面) |
| **brand-guidelines** (公式 `anthropics/skills`) | Anthropic / 公式 | ★中身は **"Anthropic 社の" ブランド専用**(orange #d97757 / Poppins・Lora / pptx 24pt+ 向け)。汎用ブランド skill では**ない** | ゼロ(散文) | **そのままでは MUED に無価値**(出力が Anthropic 色になる)。**MUED 独自ブランド token skill の "雛形" としてのみ有用**(hex/font を差替) → G4 gap は "内製の踏み台" としてのみ埋まる |
| **ui-ux-pro-max** (`88k★`) | community | 50+ UI style / 161 palette / 57 font の "推論エンジン" | (別途) | ★**template課に既導入済** (skill 一覧に存在)。= frontend-design/ui-design-brain が**補完する既存の主力**。新規採用ではないが「既に最大手は持っている」事実は判断の前提 |
| emilkowalski/skill, pbakaus/impeccable, Ilm-Alan/frontend-design(8 aesthetic anchor 版) | community | 著名デザイナー由来の taste 系 / 公式 frontend-design の prescriptive fork | 概ね散文 | 上記と哲学重複。**単独採用の限界利益は薄い**。参考どまり |
| clone-website / brand-design-md | (前監査済) | — | — | 前監査通り **見送り**(法務 / 未pin npx)。除外指示にも合致 |

**補足**: frontend-design は公式 `anthropics/skills` 版に加え、`anthropics/claude-code` の**バンドル plugin** としても配布されている。= Anthropic 純正配布ゆえ、有効化の supply-chain 懸念は極小 (theme-factory も同 repo)。

---

## 4. 正直な推奨 (tradeoff 明示・過剰推し回避・"入れない" も提示)

### 推奨 A (本命・低リスク高価値): **frontend-design を採用**
- 理由: 公式・実行面ゼロ=最安全 / 既存資産に無い「**美的方向性の言語化**」を埋める(希少) / 2ファイル hash-lock 容易。
- tradeoff: 良デザインを**保証しない**(bias を与えるだけ)。保守 B2B で "risk を1つ取れ" が過剰な場面はプロンプトで抑制可。
- 導入経路: shared 配布なら Tier3(全課波及)。**template課 local 試験導入なら Tier2**(実行面ゼロで特に低リスク)。まず local で 1-2 案件試すのが理解にも最適。

### 推奨 B (条件付き): **ui-design-brain は "重複確認 → 採用"**
- 理由: 品質下限を上げる良質な部品カンペ・実行面ゼロ確認済。
- tradeoff: **既導入 `ui-ux-pro-max` / `web-design-guidelines` と役割重複**。限界利益が小さければ入れる価値も小さい。→ 「同じ1画面を ui-ux-pro-max のみ / +ui-design-brain で出し比べ、差が出るか」を**先に1回試す**べき。差が薄ければ**見送りも正当**。

### 見送り / 保留
- **Taste Skill**: 欲しくなったら **core `taste-skill/SKILL.md` の散文だけ** vendoring(MIT・監査容易)。suite 全体(script+画像生成)は現時点 need 薄く実行面広い→**非採用**。
- **brand-guidelines (公式)**: as-is は無価値。**MUED 独自ブランド skill を内製する時の雛形**として参照(採用ではない)。
- **clone-website / brand-design-md**: 前監査通り**見送り**継続。

### "全部入れない" という選択肢
- 妥当。理由: (1) LP 再挑戦の本筋は **Claude Design 製品の再走**(skill 導入はそれを止めない**並行の補強**であって critical path でない)。(2) 最大手 `ui-ux-pro-max` は既にある。→ **「今は何も足さず、frontend-design だけ local で1件試して体感してから決める」**が、理解重視の kimny には最も負荷が低く後悔しない道。

### CCO の一本推奨
> **frontend-design を template課 local で Tier2 試験導入 → 実案件1件で before/after を体感 → 良ければ shared(Tier3)昇格を conductor/kimny へ。ui-design-brain は "出し比べ1回" で限界利益を確認してから。Taste/brand-guidelines/clone 系は今回見送り。**
> 理由: 最安全(公式・実行ゼロ)× 既存に無い価値(方向性)× 体感してから広げる=理解重視の kimny 方針と整合。

---

## 5. kimny 提示用 brief (平易・PWA-ready)

> 別途 Artifact に視覚版(before/after レンダリング)。以下はテキスト版。

**何の話か**: LP や MUEDear の見た目を、Claude(AI)側で底上げする「デザインスキル」を入れるか、の検討です。実物のファイルを全部読んで、中身と "入れると何が変わるか" を確かめました(インストール・実行は一切していません)。

**候補は主に2つ、役割が違います**:
- **frontend-design(Anthropic 公式)** … 「AI が作るとどれも同じ顔になる」問題を避け、**その案件だけの意図的なデザイン**を作らせる手引き。動くコードはゼロ=最も安全。今ある道具に無い「**見た目の方向づけ**」を足します。
- **ui-design-brain(公開・MIT)** … ボタン・表・フォームなど**60部品の正しい作法集**。素人っぽいミス(ラベル無しの入力欄・全部同じボタン・派手なだけの色分け)を消します。ただし**既に入っている大きな道具(ui-ux-pro-max)と役割が重なる**ので、"入れて差が出るか1回試してから" が正直なところ。

**入れると何がどう良くなるか(一言で)**:
- frontend-design → 「どのサイトとも見分けがつく、この案件だけの見た目」に寄る
- ui-design-brain → 「作りが丁寧で、使いやすさの下限が上がる」

**正直な話(過剰に推しません)**:
- frontend-design は "良いデザインを保証" はしません。「AI っぽい没個性」から遠ざける効き方です。それでも**安全で希少な価値**なので、まず**社内で1案件だけ試す**のが一番わかりやすい。
- ui-design-brain は良いものですが、**今ある道具と重複**します。**1回出し比べて差が薄ければ、入れない判断も正しい**。
- 他の候補(Taste Skill=高機能だが実行部分が多い / brand-guidelines=中身は "Anthropic 社専用" でそのままでは無意味 / サイト複製系=法務リスク)は**今回は見送り**を推奨。
- そもそも**「今は何も足さない」も妥当**。LP の本筋は Claude Design 製品の再走で、これはそれを止めない**おまけの補強**です。

**CCO の推奨**: まず **frontend-design だけ、社内で1案件お試し** → 体感して良ければ全課へ。ui-design-brain は "出し比べ1回" で要否を判断。急ぎではありません。

**判断の選択肢**:
- (a) 推奨どおり(frontend-design を社内お試し / ui-design-brain は出し比べ後 / 他は見送り)
- (b) frontend-design を最初から全課へ
- (c) 今は何も足さない(Claude Design 再走に集中)
- (d) もっと詳しく知りたい点がある

---

## 6. 次アクション

1. 本 deepdive + 視覚 Artifact を conductor 経由で kimny PWA QA へ (pwa-dashboard 形式)。
2. kimny 判断待ち。(a) なら frontend-design を template課 local へ Tier2 試験導入(hash-lock → 1案件試行 → before/after 記録)。
3. ui-design-brain は "ui-ux-pro-max のみ vs +ui-design-brain" 出し比べ1回を実施し限界利益を実測してから採否。
4. 前監査 doc (`design-skill-acceptance-audit-20260702.md`) は安全面の正本として併存。本 doc は "中身と効果" の正本。
