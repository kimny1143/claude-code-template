---
name: peer-id-lookup
description: >
  claude-peers で他課にメッセージを送る際に、課名から peer ID を自動解決する。
  使用タイミング: (1) dispatch時に課名でpeer指定したい時 (2) CronCreate内でpeer IDが必要な時
  (3) list_peers + 目視確認のコストを省きたい時。
  トリガー例: 「mued課のIDを調べて」「native課に送って」「conductor課のpeer IDは?」
  「〇〇課にメッセージを送りたい」
---

# peer-id-lookup — 課名 → peer ID 自動解決

課名を指定するだけで `mcp__claude-peers__list_peers` を呼び出し、peer ID を返す。

---

## 使い方

課名（日本語・略称どちらでも可）を渡すと peer ID を返す。

```
「native課に送って」
「mued課のIDを調べて」
「SNS課のpeer IDは?」
```

---

## 解決手順

1. `mcp__claude-peers__list_peers(scope: "machine")` を実行
2. 下記のCWDパターン表で課名 → CWD部分文字列をマッチ
3. 一致したピアのIDを返す
4. オフライン（未検出）の場合は「現在オフライン」と明示

---

## CWD → 課名 マッピング表

| 課名 | CWD部分文字列（いずれか一致） |
|------|------------------------------|
| conductor課 | `_conductor` |
| template課 | `claude-code-template` |
| mued課 | `mued/mued_v2`（`/apps` を含まない） |
| native課 | `mued/mued_v2/apps` |
| SNS課 | `mued/threads-api` |
| write課 | `_contents-writing` |
| data課 | `_data-analysis` |
| LP課 | `_LandingPage` |
| reserch課 | `_Reserch` |
| freee課 | `freee-MCP` |
| cowork課 | `_cowork` |
| video課 | `_videos` |

**注意**: mued課とnative課はCWDが重複する。`/apps` を含むかどうかで区別する。

---

## 出力例

```
native課のpeer ID: fyl8gi3j
CWD: /Users/kimny/Dropbox/_DevProjects/mued/mued_v2/apps
```

複数ヒットした場合（同課が複数起動中）:
```
native課のpeer候補:
- fyl8gi3j (ttys012, last seen: 03:14)
- ab12cd34 (ttys018, last seen: 03:10)
→ より最近のfyl8gi3jを推奨
```

オフラインの場合:
```
video課は現在オフラインです（アクティブなピアなし）。
次回起動時にメッセージを送るか、kimnyに手動対応を依頼してください。
```

---

## 注意事項

- peer IDはセッションごとに変わる。ハードコードしないこと
- `list_peers` はリアルタイム取得のため、結果は呼び出し時点のもの
- CWDパターン表はディレクトリ構成変更時に更新が必要（template課管理）
