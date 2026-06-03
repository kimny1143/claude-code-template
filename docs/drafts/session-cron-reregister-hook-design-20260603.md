# SessionStart cron 自動再登録 hook — CCO 雛形設計 (2026-06-03)

## 経緯

cowork (k0cnj3sj) の「CronCreate 再起動耐性化 proposal」を CCO が feasibility review。
proposal Option(i)「durable CronCreate」は前提崩れと確定:

- `durable:true` は session-only (2026-05-26 reserch finding = CCO memory `reference-croncreate-session-only-behavior`)
- ライブ確認: `~/.claude/scheduled_tasks.json` も `_cowork/.claude/scheduled_tasks.json` も **ファイル不在**(cowork 16件稼働中なのに)= disk 永続化せず full restart で消失

conductor (va5mgfxg) 判断 (hybrid 確定・total +$7/月・COGS$200内):

1. **aggregation / ratelimit / 日次週次月次 = SessionStart hook 自動再登録 (無料)**。$26/月 RemoteTrigger は不採用 (aggregation の監視対象 = ローカル peer。PC-off 中は peer も全停止＝監視対象ゼロゆえ「何も無い時間の監視」に課金する no-mamagoto 違反)。今朝86分ブラインドの真因は「Mac 起動中の再起動でクローン消失」= hook 再登録で直撃解決。
2. **watchdog A+B = RemoteTrigger ($7/月) approve** (critical + 低頻度 + sleep/restart 耐性の価値が勝つ)。
3. **value-add**: その durable watchdog に **aggregation 鮮度チェック** を持たせる (期待 active 帯で peer-raw-status の最新 commit が >20-30分 途絶えたら alert)。「cowork が死んで aggregation が silent 停止」を $7/月 で検知＝"監視の監視"。

## 役割分担

| 項目 | owner |
|------|-------|
| 汎用 SessionStart cron 再登録 hook 雛形 (本書) | **CCO** (template canonical scope) |
| cron manifest (cowork の 16 crons 定義) | cowork |
| cowork settings.local.json SessionStart 配線 | cowork |
| RemoteTrigger watchdog A+B 登録 + aggregation 鮮度チェック | cowork |

→ 鮮度チェックの実装ロジックは cowork own work (peer-raw-status データ所有・freshness 判定は cowork domain)。CCO は hook 雛形のみ提供。

## 機構 (load-handoff-memory.sh 同型・実証済)

`.claude/hooks/load-handoff-memory.sh` は SessionStart hook で stdout を session 開始 context に注入する汎用 hook。同じ仕組みで「再登録すべき cron 一覧」を注入 → model が起動時に CronCreate を実行する。

**重要 (正直な制約)**: hook は MCP tool (CronCreate) を**直接呼べない**。hook は context を注入するだけで、実際の登録は model が注入 context を読んで CronCreate を呼ぶ **advisory 方式**。ハードな cron daemon ではない。手動再登録 (cowork が今回 16件手動でやった作業) を automate するもので、現状より厳密に改善するが「100%機械保証」ではない (model compliance 依存)。CronList 検証ステップを必須化して緩和する。

## 雛形 (reference 実装)

`.claude/hooks/reregister-session-crons.sh`:

```bash
#!/bin/bash
# SessionStart Hook: session-only cron 自動再登録プロンプト注入
#
# 動作: peer-local の cron manifest を読み、session 開始 context として
#       「以下の cron を CronCreate で再登録せよ」を stdout 出力。
#       MCP CronCreate は session-only ゆえ full restart で消える →
#       手動再登録を automate する (load-handoff-memory.sh 同型)。
#
# 制約: hook は CronCreate を直接呼べない。context 注入 → model 実行 の advisory 方式。
# 汎用: CWD ベースで manifest を探すのでどの peer でも動作。

CWD=$(pwd)
MANIFEST="$CWD/.claude/cron-manifest.json"

# manifest が無ければ何もしない (opt-in)
[ -f "$MANIFEST" ] || exit 0

echo ""
echo "=========================================="
echo "[session-only cron 自動再登録]"
echo "MCP CronCreate は session-only。前回 session の cron は full restart で消えています。"
echo "手順:"
echo " 1. CronList で現在の登録状況を確認 (resume/--continue 時は生存している場合あり)"
echo " 2. 下記 manifest のうち未登録の entry のみ CronCreate で登録 (重複登録回避)"
echo " 3. 完了後 CronList で件数照合"
echo "=========================================="
cat "$MANIFEST"
echo ""
echo "=========================================="
```

`.claude/cron-manifest.json` (cowork が定義する peer-local ファイル・例):

```json
[
  { "name": "aggregation", "schedule": "*/10 * * * *", "prompt": "..." },
  { "name": "ratelimit",   "schedule": "7 * * * *",    "prompt": "..." }
]
```

cowork settings.local.json の `hooks.SessionStart` に hook path を追加して配線。

## 設計上の注意 (cowork 実装時)

1. **冪等性必須**: SessionStart は resume / `--continue` でも発火しうる。その時 cron がまだ生存していると CronCreate が重複登録になる。→ manifest 一括登録でなく「**CronList で既存確認 → 未登録のみ登録**」を hook 指示文 + model 運用で担保 (雛形の手順1-2 がこれ)。
2. **PC-off は対象外**: Mac 停止中は hook も走らない。だが監視対象 peer も停止しているので機能要件上は問題なし (conductor 判断の通り)。「Mac 起動中の restart でクローン消失」が解く対象。
3. **鮮度チェックは hook でなく RemoteTrigger 側**: 「cowork session 自体が落ちて再登録もされない」silent death は hook では検知不能 (落ちた session は hook も動かさない)。これは cowork の durable watchdog (RemoteTrigger) の aggregation 鮮度チェックが担当 = 層が違う。両者は補完関係。

## 配布 / Tier

- 本 hook は**新規 shared hook**。`setup.sh` の `SHARED_HOOKS` に載せ全 peer 自動 link すると**全課波及 = Tier 3** → conductor review + migration note 必須。
- **初期段階 = cowork-local** (cowork が hook を自 workspace に置き settings に配線) で運用 = cowork own work・軽量。
- **推奨**: まず cowork で実証 → 他 peer も session-only cron を持つなら、その時点で `/plan` + conductor review (migration note 添付) を経て `SHARED_HOOKS` へ昇格。**今は自動配布しない** (template「全peer展開は migration note + dry-run + conductor」原則)。

## status

- 本書 = CCO 設計 draft (Tier 1 docs)。実 hook ファイル作成 / setup.sh 配線は cowork 統合タイミング or 全peer昇格判断時。
- cowork へ本書 hand over 済 → cowork 統合時に雛形調整相談を受ける。
- 完了 (cowork 統合稼働) 時に conductor へ 1 行報告。
