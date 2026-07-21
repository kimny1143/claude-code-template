# peer-raw-status 集約 CronCreate → launchd 移行 設計 (draft)

- 起案: CCO (template課) × cowork 協働 / kimny 6/10 指示
- フロー: 本設計 → conductor review → kimny 承認 → cowork が _cowork repo に適用
- **制約 (kimny): GitHub Actions は使わない** (gw-dash $20 爆発の轍)。ローカル launchd 限定。
- CCO scope: 設計 + plist/wrapper 雛形提供 (本doc)。実ファイル配置・適用は cowork が _cowork repo 内で行う (CCO は他peer workspace を直接変更しない)。

## 背景 (一次情報, cowork 6/10 提供 + CCO がスクリプト実読)

- 集約コア = `/Volumes/strage/_DevProjects/_cowork/scripts/aggregate_peer_status.py`
  - 10分毎 (`*/10`)。全15 peer の status.md を git fetch → slim 整形 → `_conductor/docs/inbox/peer-raw-status.md` に **commit + push**。
  - stale 検出 + stale-ack.json 抑制 + commit-recency override 付き。exit 常に0。
  - stdout: `PUSHED`/`NO_CHANGE`/`DRY_RUN` + `STALE:`/`SUPPRESSED:` 行。
- 第2対象 = `heartbeat-update.py` (`0 */3` = 3時間毎、cowork 自身の heartbeat)。
- 現状の脆さ: MCP CronCreate は session-only。再起動で全消失 → cowork が毎起動後に手動 14件再登録 → **再起動〜再登録完了まで最長数分の集約空白**。SessionStart hook (`reregister-session-crons.sh`) は advisory (手動再登録の案内) 止まり。
- 既知前提: CronCreate session-only 挙動は CCO memory `reference_croncreate_session_only_behavior` に既知。真 durable は Routines / launchd / cowork python cron / Mac launchd 経由。

## 設計判断

### D1. LaunchDaemon ではなく **LaunchAgent** (user-level)
- 配置: `~/Library/LaunchAgents/`。ユーザーログインで起動し、**Claude セッションのライフサイクルから独立** → 再起動耐性を獲得 (本移行の目的)。
- Daemon (root, pre-login) を選ばない理由: git push の認証 (SSH 鍵 / osxkeychain credential helper) と Dropbox sync は **user セッション資産**。root daemon では push 認証が通らない。

### D2. ProgramArguments は python 直叩きせず **wrapper shell 経由**
理由: launchd のプロセス環境は極小 (PATH 不足・SSH agent なし)。wrapper で (a) PATH 整備 (b) flock 多重起動防止 (c) timestamp 付きログ追記 (d) サイズ rotation を吸収する。

### D3. 周期
- aggregate: `StartInterval = 600` (10分) + `RunAtLoad = true` (load 即時1回)。壁時計整列不要なので StartInterval で十分。
- heartbeat: cron `0 */3` 相当 → `StartCalendarInterval` を 0,3,6,9,12,15,18,21時の配列で指定 (StartInterval=10800 はload時刻基準でずれるため非採用)。

### D4. ログと rotation
- `StandardOutPath`/`StandardErrorPath` を `~/Library/Logs/glasswerks/` 配下に。
- launchd は rotation しない → wrapper 側でサイズ上限 (例 5MB) 超過時に `.1` へ mv する簡易 rotation。

## git push 認証 (cowork 6/10 確認で risk 低下、ただし dry-run gate は維持)

CronCreate は **Claude セッション内**で実行されユーザー完全 env を継承していた。launchd はこれを継承しない。当初は最大リスクとしたが、cowork 確認で条件が判明し risk は下がった:

- remote = **HTTPS** (`https://github.com/kimny1143/{conductor,gw-cowork}.git`)。SSH 未使用。
- ~~credential.helper = **osxkeychain**~~ → **2026-07-21 実査で訂正 (下記 §認証経路 訂正 を参照)。実効 helper は `gh auth git-credential`。**
- **user-level LaunchAgent は login keychain にアクセス可** (ユーザーログイン後 keychain unlock 済) → HTTPS は launchd でも push 認証が通る見込み。SSH agent 依存問題は発生しない。

残る注意点 (dry-run gate で潰す):
1. `RunAtLoad=true` の **起動直後**は keychain unlock タイミング次第で初回失敗の可能性 → StartInterval(600s)で次サイクル自動復帰するため致命でない。ログで初回挙動を観察。
2. `python3` / `git` 絶対パスを wrapper で固定: python=`/opt/homebrew/bin/python3` (3.14.3, stdlib のみ依存ゆえ poetry venv 不要)、git=`/opt/homebrew/bin/git`。launchd PATH に依存しない。
3. 初回は **`--dry-run` を launchd で1サイクル回し** (push せず materialize のみ)、ログに期待 stdout・パス解決を確認 → その後 push 有効化。

### 認証経路 訂正 (2026-07-21 実査・conductor 提供出力)

起案時 (6/10) の「credential.helper = osxkeychain」という断定は**不正確**だった。kimny の Fine-grained PAT 再発行 (7/21) を機に conductor がローカル git 認証経路を実査し、以下が確定した。

**(1) helper は矛盾でなく同居していた。実効は gh 側。**

```
credential.helper osxkeychain                                                    ← global (6/10 記述はこれ)
credential.https://github.com.helper                                             ← 空でリセット
credential.https://github.com.helper !/opt/homebrew/bin/gh auth git-credential   ← ホスト別 (優先)
credential.helper osxkeychain
```

`gh auth setup-git` は `credential.https://github.com.helper` を**ホスト別**に書く。global の osxkeychain と併存し、github.com への push では**ホスト別設定が優先**される。よって 6/10 の記述は「global 設定としては事実だが、実効経路の記述としては誤り」。

**(2) `~/.git-credentials` 不在は「PAT が平文保存されていない」ことしか意味しない。** 実効 credential は gh の token。

**(3) token source = keyring 内の classic token。今回の PAT 失効とは別物。**

```
✓ Logged in to github.com account kimny1143 (keyring)
  Token scopes: 'gist', 'read:org', 'repo'
```

classic 形式の scope を持つ token が keyring に格納されている。7/21 に kimny が再発行した **Fine-grained PAT (scope でなく per-repo permission 制) とは別物**であり、**gh のログイン token は当該 PAT 失効の影響を受けない**。

**(4) ★本 draft が懸念した「launchd 下で環境が痩せる」問題は、config 推論でなく実績で解消済。**

cowork の launchd aggregation は **PAT 失効期間中 (7/19 以降) かつ鍵更新 (7/21 13:17 JST) より前**に conductor repo へ push し続けていた:

```
07-19 13:43 / 13:54 / 14:04 / 14:15  chore(cowork-aggregation): peer status ...
```

= keychain unlock / PATH / HOME が痩せる問題も含め、**実環境で通ることが既存 2 job により経験的に実証済**。上記「残る注意点 1.」の懸念は、設計時点では妥当だったが**実運用で潰れた**と記録する。新設 job も同一 host・同一 helper・同一 remote 種別であれば、移行当日に認証で詰まる公算は低い。

**(5) fleet 横断の認証正本 doc は作らない (conductor 推奨・CCO 同意)。** 実態は「gh helper が実効 / token は keyring / launchd で実証済」の 3 行で尽きており、正本を 1 枚起こすと更新されない stale source を増やす側のコストが上回る。本節の記録で足りる。

## ★ 設計上の劣化点: stale 通知の Claude-in-the-loop 喪失

現状、`STALE:` stdout は cowork の Claude セッションが cron 出力として受け取り、必要なら conductor へ能動通知できていた。**launchd には Claude が居ない** → STALE stdout はログファイルに落ちるだけ。

緩和 (設計に含める):
- **materialize 自体は無劣化**: `peer-raw-status.md` の `## Audit` セクションが既に `stale_count` / `stale_peers` / `new_stale_count` を保持 → **conductor はファイルを読めば stale を把握できる** (能動 push に依存しない)。よって致命ではなく「能動通知の喪失」に留まる。
- 能動通知が要るなら: launchd は機械的 materialize (durable) を担い、**軽量な Claude 側 cron / SessionStart が出力ログの `STALE:` 行だけを読んで conductor へ通知**する 2層構成にする (launchd=durable materialize / Claude=intelligent notify)。この2層分離が本移行の肝。

## ★ 多重実行ハザード: SessionStart 再登録 hook との二重起動

launchd が10分毎に aggregate を回す一方で、cowork の Claude セッションが従来通り CronCreate で同 job を再登録すると、**同一ファイルへ2系統が commit/push → git 競合・無駄 push**。

必須の同時対応 (cowork):
- 移行する2 job (aggregate / heartbeat) を `.claude/cron-manifest.json` から **除外** → SessionStart hook が再登録を案内しなくなる。
- cowork は当該2 job を以後 CronCreate しない。残る cron (日次/週次/月次) のみ manifest 管理を継続。
- wrapper の flock は同一 launchd job の重複起動防止用 (10分内に終わらない場合の coalesce 保険)。クロス機構の二重起動は manifest 除外で根治する。

## パス整合 (Volumes vs Dropbox) — 確定

cowork 確認: `/Volumes/strage/_DevProjects` と `/Users/kimny/Dropbox/_DevProjects` は **inode 一致 (9388573) = 完全同一ディレクトリ** (Dropbox が /Volumes/strage に sync)。launchd からは両パスで解決可だが、**ボリュームマウント依存のない `/Users/kimny/Dropbox/...` を全パスで固定採用** (plist の ProgramArguments / WorkingDirectory、wrapper の SCRIPT、スクリプト内 hardcode 出力先すべてと整合)。

## 雛形 (cowork が _cowork repo に配置・適用)

### plist: `~/Library/LaunchAgents/com.glasswerks.cowork.peer-status-aggregate.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.glasswerks.cowork.peer-status-aggregate</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>/Users/kimny/Dropbox/_DevProjects/_cowork/scripts/launchd/run-aggregate.sh</string>
  </array>
  <key>StartInterval</key>
  <integer>600</integer>
  <key>RunAtLoad</key>
  <true/>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
  </dict>
  <key>WorkingDirectory</key>
  <string>/Users/kimny/Dropbox/_DevProjects/_cowork</string>
  <key>StandardOutPath</key>
  <string>/Users/kimny/Library/Logs/glasswerks/peer-status-aggregate.out.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/kimny/Library/Logs/glasswerks/peer-status-aggregate.err.log</string>
  <key>ProcessType</key>
  <string>Background</string>
</dict>
</plist>
```

### wrapper: `_cowork/scripts/launchd/run-aggregate.sh`

```bash
#!/bin/bash
# launchd wrapper for aggregate_peer_status.py
# - PATH/env 整備、mkdir-lock 多重起動防止、timestamp ログ、簡易 rotation
set -u

PY=/opt/homebrew/bin/python3   # 3.14.3 / stdlib のみ依存 → poetry venv 不要
SCRIPT=/Users/kimny/Dropbox/_DevProjects/_cowork/scripts/aggregate_peer_status.py
LOG=/Users/kimny/Library/Logs/glasswerks/peer-status-aggregate.run.log
LOCKDIR=/tmp/cowork-aggregate.lock.d
MAX=5242880                    # 5MB rotation

export PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
mkdir -p "$(dirname "$LOG")"

# size rotation
if [ -f "$LOG" ] && [ "$(stat -f%z "$LOG" 2>/dev/null || echo 0)" -gt "$MAX" ]; then
  mv -f "$LOG" "$LOG.1"
fi

# mkdir-lock (flock は macOS 標準に無い): 前サイクル走行中ならスキップ
if ! mkdir "$LOCKDIR" 2>/dev/null; then
  echo "$(date '+%Y-%m-%dT%H:%M:%S') SKIP: previous run still active" >> "$LOG"
  exit 0
fi
trap 'rmdir "$LOCKDIR" 2>/dev/null' EXIT

TS=$(date '+%Y-%m-%dT%H:%M:%S')
OUT=$("$PY" "$SCRIPT" 2>>"$LOG")
echo "$TS $OUT" >> "$LOG"

# STALE: 行をログに明示 (将来 Claude 側 notify cron が grep する想定)
echo "$OUT" | grep -E '^(STALE|SUPPRESSED):' >> "$LOG" 2>/dev/null
exit 0
```

> ※ mkdir-lock は異常終了で `$LOCKDIR` が残置すると全 run が SKIP する → trap で EXIT 時 rmdir。万一残置時は stale lock 検出 (mtime 古ければ強制 rmdir) を足しても良いが、aggregate は数十秒で終わるため当面 trap で十分。

### load / unload (cowork が実行)

```bash
# load (登録 + 即時起動)
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.glasswerks.cowork.peer-status-aggregate.plist
launchctl enable gui/$(id -u)/com.glasswerks.cowork.peer-status-aggregate
launchctl kickstart -k gui/$(id -u)/com.glasswerks.cowork.peer-status-aggregate   # 即時1回

# 確認
launchctl list | grep peer-status
tail -f ~/Library/Logs/glasswerks/peer-status-aggregate.run.log

# unload (rollback)
launchctl bootout gui/$(id -u)/com.glasswerks.cowork.peer-status-aggregate
```

## 適用手順 (段階・cowork)

1. dry-run gate: wrapper の python 引数に `--dry-run` を一時付与 → load → 1サイクルのログ確認 (materialize されるが push されない)。git 認証・パス解決・stdout を検証。
2. push 有効化: `--dry-run` 除去 → kickstart → `peer-raw-status.md` が実際に push されるか git log で確認。
3. 二重起動根治: `.claude/cron-manifest.json` から aggregate (と heartbeat) を除外 → 以後 CronCreate しない。
4. heartbeat も同型 plist (StartCalendarInterval 0/3/6/.../21時) で追加。
5. 監視: 数サイクル分のログで PUSHED/NO_CHANGE の周期性と STALE 行を確認。

## rollback

- `launchctl bootout` で launchd job を即停止。
- cron-manifest.json に2 job を戻し、CronCreate 再登録の従来運用へ復帰。
- materialize 出力ファイルは同一形式ゆえ、機構を戻しても conductor 側の読み取りは不変。

## conductor / kimny 確認ポイント

- [ ] stale 能動通知を 2層 (launchd materialize + Claude notify cron) にするか、当面 `## Audit` ファイル読みで足りるとするか ← **方針判断要**
- [ ] heartbeat も同時移行か、aggregate のみ先行か
- [ ] 残りの日次/週次/月次 cron は launchd 化せず CronCreate 運用維持で良いか (cowork は一部 RemoteTrigger/Routine 移行が適切と示唆。ただし Routine=クラウド実行で GitHub Actions 制約とは別物。要 kimny 判断)
- git push 認証は HTTPS + osxkeychain + user-level LaunchAgent で **通る見込みに確度が上がった** (旧最大リスクは低下)。初回 keychain unlock タイミングのみ dry-run gate で観察。

## 環境前提 (cowork 6/10 確定 — 全4点 resolved)

| 項目 | 確定値 |
|---|---|
| python3 | `/opt/homebrew/bin/python3` (3.14.3 / stdlib のみ依存、poetry venv 不要) |
| git | `/opt/homebrew/bin/git` |
| パス | `/Volumes/strage` = `/Users/kimny/Dropbox` 同一 inode。**Dropbox パスを全採用** (マウント非依存) |
| lock | flock 無し → **mkdir-lock** 採用 |
| git auth | HTTPS remote + osxkeychain。LaunchAgent から login keychain アクセス可 |

→ 環境固定値で plist/wrapper 確定済。残るは上記 conductor/kimny 方針判断のみ。承認後 cowork が段階適用 (dry-run gate → push 有効化 → manifest 除外)。
