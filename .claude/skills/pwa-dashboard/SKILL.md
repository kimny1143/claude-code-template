---
name: pwa-dashboard
description: >
  kimny の iPhone PWA `gw-dash` 用の QA を、全課が PWA-ready な形式で書くための共通規約。
  分担 = 各課が正しい形式で QA を書く / conductor が PWA に load する。
  使用タイミング: (1) kimny 判断が必要な質問を QA バッチとして書く時 (2) 試聴/レビュー deck を
  PWA QA タブに載せたい時 (3) 「推奨でOK」運用で回答が壊れないか確認したい時。
  トリガー例: 「kimny に PWA で聞きたい」「QA バッチを作る」「PWA-ready な形式で」
  「推奨でOK の質問にしたい」「gw-dash に載せる質問」
---

# pwa-dashboard — PWA (gw-dash) QA 作成規約 + conductor load 運用

kimny の判断 trigger は **PWA QA タブ経由に統一**されている（チャットは補助）。
質問を PWA に出すには 2 つの役割がある:

| 役割 | 担当 | このskillの該当節 |
|---|---|---|
| QA を **PWA-ready な形式で書く** | 質問を起案する各課（content / dsp / occur 等） | §1（全課共通・必読） |
| QA を **PWA に load / deploy する** | conductor（gw-dash 運用課） | §2（load 担当のみ・他課は読み飛ばし可） |

**最重要**: チャットに質問を書くだけでは PWA には出ない。QA は §1 の形式で書き、conductor が §2 で load して初めて kimny の手元に届く。

---

## §1 全課共通 — QA を PWA-ready な形式で書く

質問を起案する課は、kimny 判断が必要な問いを次の形式の Markdown で用意する。これを conductor に渡す（または各課が `drafts/inbox/*_qa_batch.md` 等に先回り準備しておくと load が速い）。

### QA 形式（`parseQA` が解釈する）

```
## Q: <題>
<body（背景・選択肢はここに書く）>
推奨: <単一の推奨回答>
---
## Q: <次の問い>
...
```

- 複数問は `---`（前後に空行）で区切る。
- 試聴ペアを出す時は `AUDIO: label|input|output` 行を使う。
- `### 推奨` セクション形式も可。

### ⚠️ 最重要ルール: `推奨:` 行は「単一の推奨回答」にする（選択肢を並べない）

PWA 側で kimny が「推奨でOK」を押すと、**`推奨:` に書いた文字列がそのまま回答として保存される**仕様（gw-dash `TabQA.tsx` の `handleSubmit` が `item.recommendation` を回答に転記）。

そのため `推奨:` に "OK / 言い換えたい / 平易に" のような**選択肢を並べると、回答が選択肢の羅列のまま保存され判別不能**になる。

- ❌ `推奨: OK / 言い換えたい / もっと平易に`
- ✅ `推奨: OK（そのまま使う）`

選択肢を提示したい時は **body に選択肢を書き、`推奨:` には推した 1 案だけ**書く。

### QA 作成時の品質チェック（起案課の責任）

- 1 問は 1 つの判断に絞る（複合質問にしない）。
- 平易な日本語・1 問 1 フォーム。専門用語は body で補足。
- 試聴/知覚テストの候補に **期待値の pre-label（アンカリング）を付けない**（「事象性候補」等のラベルは kimny の素の判断を誘導する。中立記述にする）。

---

## §2 conductor 運用 — QA / dashboard を PWA に load する（load 担当のみ）

> このセクションは gw-dash を運用する課（conductor）向け。QA を書くだけの課は読み飛ばしてよい。

- gw-dash repo: `/Volumes/strage/_DevProjects/gw-dash`
- 本番 = Cloudflare Pages（`deploy.yml` が gw-dash main push で発火）
- **2 系統あり、混同しない**:

### 系統1: dashboard 源 = runtime fetch（push だけで反映・gw-dash build 不要）

`gw-dash/functions/api/conductor.ts` の `FILE_MAP` が conductor repo を GitHub から runtime 取得する。対象:

| PWA タブ | conductor ファイル |
|---|---|
| TOP 要約 | `docs/inbox/dashboard-top-summary.md` |
| 詳細 | `docs/inbox/kimny-pending-active.md` |
| 履歴 | `reports/daily/*` |
| RateLimit | `docs/inbox/ratelimit-status.md` |
| peer raw | `docs/inbox/peer-raw-status.md` |
| 他 | `next-milestone.md` / `peer-goals-board.md` / `launch_day_playbook_*.md` |

**手順 = conductor repo に push するだけ**（feature branch + Tier1 `[self-review]` self-merge、main 直 push 禁止）。gw-dash の rebuild は不要。

### 系統2: QA 質問 = gw-dash バンドル（deploy 要・push やチャットでは出ない）

QA タブの質問は `gw-dash/src/data/conductor/*-qa.md` を `App.tsx` が `?raw` import → `QA_SOURCES` 配列に**手動登録**して初めて出る。

手順:

1. **質問素材を読む**（§1 形式で各課が準備済の場合が多い）。逐語で。
2. **QA ファイル作成**: `gw-dash/src/data/conductor/<slug>-qa.md`（§1 の形式・`推奨:` は単一回答）。
3. **App.tsx に登録**（`gw-dash/src/App.tsx`）:
   - import: `import xQa from './data/conductor/<slug>-qa.md?raw'`
   - `QA_SOURCES` **先頭**に: `{ label: '絵文字+短題', raw: xQa, sourceSlug: '<slug>' }`（新しい順）
4. **build 検証**: `cd gw-dash && npm run build`（`tsc -b && vite build`）。
5. **git（必ず `main` 基点で！）**: `git checkout main && git pull` → `git checkout -b feat/<slug>-qa` → add 2 ファイル → commit → push → PR → **diff verify**（該当 QA ファイルのみ・mergeable CLEAN）→ `gh pr merge --squash`。
6. **deploy 確認**: `gh run list --branch main --limit 1`（Deploy to Cloudflare Pages → success）。反映は ~1-3 分。

#### ⚠️ Gotchas（実際に踏んだ）

- **branch は必ず `main` 基点で切る**。前の QA branch から切ると、squash 済み前 QA のファイルが重複して `CONFLICTING` になる。復旧 = `gh pr close` → `git checkout main -f && pull` → 新 branch → `git checkout <bad-branch> -- <変更ファイル>` で変更だけ拾う → diff verify。
- **build を必ず先に**（壊れた状態を deploy しない）。
- **merge 前に diff verify**（`gh pr view N --json files,mergeable,mergeStateStatus`）。

### QA 回答の取得（kimny が PWA で回答した後）

kimny が PWA で回答 → `gw-dash/functions/api/qa-answer.ts`(POST) → **conductor repo** `docs/inbox/qa-answers/YYYY-MM-DD-<slug>-qN.md`（1 問 1 ファイル）に Q+推奨+回答を commit。

- **手順**: conductor repo で `git pull` → `cat docs/inbox/qa-answers/*<slug>*.md` で**逐語**確認 → 担当課に**逐語中継**（要約禁止）。
- **回答欄が選択肢のまま = 明示選択なし**の場合あり。断定せず kimny に 1 行確認 or 声チェック。
- `?kind=qa-index`(conductor.ts) が回答済み slug 一覧を返し、TabQA が pending/answered を区別。
- 完了済 QA は `/checkout` で `qa-answers/archive/` へ（newest 3 保持）。

### その他のタブ

- comparisons / screenshots / visual-review = `*-manifest.json` 方式（別系統・gw-dash build+deploy 要）。

---

## 原則

- kimny 判断 QA は**最初から PWA に load**（チャットは補助）。
- dashboard 源（系統1）は push だけで反映、QA 質問（系統2）は deploy 要 — この差を毎回意識する。
- 各課は §1 を守って書く / conductor が §2 で load する、の分担を崩さない。
