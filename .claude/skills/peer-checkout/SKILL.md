---
name: peer-checkout
description: セッションの区切りで durable 層（status.md・git・memory）を現在形に保つ 3 手順。発火点＝handoff / compaction 直前・idle 化の直前・長時間離席の前。
---

# peer-checkout

peer は 24h 連続稼働で「セッションの終了」が曖昧なため、durable 層（`status.md` / git / memory）が現在形から遅れやすい。このスキルは区切りごとに durable 層を現在形へ揃える最小手順。

## いつ走らせるか（発火点 norm）

セッションの「終了」が曖昧なので、以下のどれかが来たら **本作業より先に** これを走らせる：

1. compact / handoff の直前（context が消える前が最後のチャンス）
2. 作業が一段落して idle 化する時（standby 宣言・「〜待ち」に入る時）
3. conductor から restart / checkout 系の指示が来た時

## 3 手順

1. **status.md を現在形 1 枚に**：yaml 全フィールド更新（**last_update 必須**・current_task / next_action は「いま」を書く・終わった話は Recent events へ 1 行で送る。「(旧 …)」地層を作らない）。
2. **WIP を commit + push**：作りかけでも `wip:` で保全（ブランチ可）。**commit できない理由があるなら、その理由を status に一行書く**（例＝「商用素材ゆえリポ格納禁止・ローカルのみ」）。
3. **memory 1 行**：このセッションで確定した判断・教訓が memory 未反映なら 1 行だけ書く（書くほどのものが無ければスキップ可。ただし「次のインスタンスがこの workspace の文書だけで再開できるか」を自問して No なら何かが欠けている）。

## 判定基準（このスキルの合格ライン）

「明日、新しいインスタンスが `status.md` ＋ memory ＋ `CLAUDE.md` **だけ**で、いまの案件を誤りなく再開できるか」（M5 再構築テスト）。

## 関連

- status.md 更新 = タスク完了の定義（DoD）は共通 block 17 参照。
- 成果物ごとの連続トリガー（PR/成果物を出したら同 commit で status を現在形化）が「終了の儀式」より確実。
