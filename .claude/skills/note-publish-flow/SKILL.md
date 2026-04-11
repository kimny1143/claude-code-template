# note-publish-flow

note記事の公開フロー全体を管理するスキル。
下書き投稿（note-article-post）の後工程として、公開前チェック・公開・公開後処理を担当する。

## トリガー

「note記事を公開して」「note公開フロー」「記事の公開前チェック」
「articles.json照合」「ですます調チェック」「公開完了通知」

## 前提条件

- note-article-post スキルで下書き保存済み
- `articles.json` にアクセス可能（SNS課管理: `/mued/threads-api/articles.json`）
- 記事のMarkdownファイルが存在
- conductor から公開GOが出ていること

## フロー全体像

```
write課ドラフト受領
  → conductor公開GO
  → [Phase 1] 公開前チェック（自動）
  → [Phase 2] 下書き投稿（note-article-post スキル）
  → [Phase 3] kimny確認・公開（手動）
  → [Phase 4] 公開後処理（自動+手動）
```

---

## Phase 1: 公開前チェック（自動）

Phase 1 は記事ファイルに対して実行する。Chrome不要。

### 1-1. articles.json 重複チェック

`articles.json` の `articles` 配列と照合し、同一タイトル or 類似タイトルの既存記事がないか確認する。

```
チェック項目:
- タイトル完全一致 → BLOCK（重複）
- タイトル類似度 80%以上 → WARNING（要確認）
- note_id 一致 → BLOCK（再投稿）

照合対象: status が "published" または "unpublished" の記事
"draft" や "deleted" は照合対象外
```

**articles.json スキーマ:**
```json
{
  "articles": [
    {
      "note_id": "nxxxxxxxx",
      "title": "記事タイトル",
      "url": "https://note.com/mued_glasswerks/n/nxxxxxxxx",
      "category": "interview",
      "status": "published|unpublished|draft|deleted",
      "views": 0,
      "likes": 0,
      "comments": 0,
      "published_date": "2026-04-10"
    }
  ]
}
```

### 1-2. ですます調チェック（Cat1ルール）

Cat1（AIトレンド/Claude Code運用）カテゴリの記事は以下をチェック:

```
必須ルール:
- ですます調で統一（だ・である調が混在していないか）
- kimnyの一人称トーン（インタビュー形式）
- キャリア年数を具体的数字で使っていないか（「15年」→「ずっと」「長いこと」に置換）
- 「スタートアップ創業者」口調になっていないか
- MUEDはブランド名として使っているか（単体アプリ名として使っていないか）
- 架空エピソードが含まれていないか

チェック方法:
1. 記事全文を読み込み
2. 文末パターンを正規表現で抽出:
   - ですます調: /です[。\n]|ます[。\n]|ません[。\n]|でしょう[。\n]|ました[。\n]/
   - だ・である調: /[^い]だ[。\n]|である[。\n]|ではない[。\n]|だった[。\n]/
3. 混在があれば WARNING + 該当行を報告
4. キャリア年数パターン: /\d{1,2}年[間以上]/
5. 禁止フレーズ: /スタートアップ創業者|シリアルアントレプレナー/
```

### 1-3. h2見出し整合性チェック

ProseMirrorエディタのペースト時に h2 が段落に結合されるバグへの対策。

```
チェック項目:
- Markdown中の ## 見出しが正しいフォーマットか（## の後にスペース+テキスト）
- 見出し直前に空行があるか（ないとProseMirrorで段落結合される）
- 見出し直後に空行があるか
- 見出しのネスト構造が正しいか（h2→h3の順序）

修正提案:
- 空行不足があれば自動挿入を提案
- セクション分割ポイントを明示（長文ペースト時の分割単位）
```

### Phase 1 レポート出力

```
=== note公開前チェックレポート ===
記事: {タイトル}
ファイル: {パス}
カテゴリ: {Cat番号}

[重複チェック] ✅ PASS / ❌ BLOCK / ⚠️ WARNING
  - {詳細}

[ですます調] ✅ PASS / ⚠️ WARNING
  - {該当行リスト}

[h2見出し] ✅ PASS / ⚠️ WARNING
  - {修正提案}

判定: GO / NEEDS FIX
================================
```

**NEEDS FIX の場合:** 修正内容を提示し、修正後に再チェック。
**GO の場合:** Phase 2（下書き投稿）に進む。

---

## Phase 2: 下書き投稿

`note-article-post` スキルに委譲。詳細はそちらを参照。

---

## Phase 3: kimny確認・公開（手動）

以下はkimnyが手動で行う。スキルからは確認リストとして提示する。

```
kimny確認チェックリスト:
- [ ] ヘッダー画像の確認・アップロード
- [ ] h2見出しが正しく表示されているか（目次が生成されているか）
- [ ] 本文の表示確認（改行・太字・リンク）
- [ ] マガジンへの追加（該当マガジンを選択）
- [ ] ハッシュタグの設定
- [ ] 有料ライン設定（該当する場合）
- [ ] 公開ボタン押下
```

**絶対ルール:** スキルから公開ボタンを押してはならない。公開はkimny手動。

---

## Phase 4: 公開後処理

### 4-1. write課への公開完了通知

claude-peers で write課に通知を送信する。

```
フォーマット:
【SNS課 → write課】公開完了通知

{記事タイトル}
- URL: {note URL}
- マガジン: {マガジン名}
- 公開日時: {YYYY-MM-DD HH:MM}
```

### 4-2. articles.json 更新

公開された記事を articles.json に追加する。

```json
{
  "note_id": "{note記事ID}",
  "title": "{タイトル}",
  "url": "https://note.com/mued_glasswerks/n/{note_id}",
  "category": "{カテゴリ}",
  "status": "published",
  "views": 0,
  "likes": 0,
  "comments": 0,
  "published_date": "{YYYY-MM-DD}"
}
```

### 4-3. Chrome解放

Chrome拡張のロックを解放し、conductorに通知する。

```
conductor通知:
【{課名}】Chrome解放しました。note記事公開完了: {タイトル}
```

---

## 制約・注意事項

1. **公開禁止**: Phase 3（公開ボタン）はkimny手動。スキルからは絶対に公開しない
2. **ヘッダー画像**: kimny手動が安定（CSPブロック問題あり）
3. **ProseMirror h2バグ**: 長文ペーストでh2が段落に結合される → セクション分割で軽減
4. **マガジン・ハッシュタグ**: kimny手動で設定
5. **Chrome拡張ロック**: 使用前にconductorに宣言、使用後に解放通知
6. **articles.json**: SNS課管理。更新時は既存エントリを壊さないこと

## カテゴリ定義

| Cat | カテゴリ | ですます調ルール |
|-----|---------|----------------|
| Cat1 | AIトレンド/Claude Code運用 | ですます調必須。kimnyトーン。年数禁止 |
| Cat2 | 音楽制作/調音 | 記事ごとに判断 |
| Cat3 | Hoo/キャラクター | 記事ごとに判断 |

## 変更履歴

- 2026-04-11: 初版作成。SNS課の実運用フローを基にtemplate課でスキル化
