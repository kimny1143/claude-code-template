# 所有ベース write-guard 一般化 — 設計 (Tier 3, /plan) — 2026-06-11

- 起案: CCO (template課)。Chief 起案 + kimny 承認 (b-2) → conductor 実装振り。
- ブリーフ正本: `_chief/for-conductor/brief-ownership-guard-20260611.md`。
- 区分: **Tier 3**（全 peer 波及の security hook 改修）。CCO 設計 → conductor レビュー → merge（=live hook 編集）。
- ★急がない（free15 LP 撤去は流入ほぼゼロ・note 並行）。丁寧に。

## 0. 一行要約

`validate-dangerous-ops-v2.sh` の Write/Edit CWD ガードを「**CWD 基準**」から「**CWD + 所有マップ基準**」へ一般化する。所有マップ (`ownership-map.tsv`) は **claude-code-template 内 (CCO 所有)** に置き、これ自身が同じ guard で他 peer から保護されることで「所有の自己昇格」を構造的に塞ぐ。**完全に加算的** = 既存の allow/block 挙動は不変、所有リポへの書込のみ新たに許可。

## 1. 問題 (なぜ CWD 基準が崩れたか)

- 組織再編 v2 の温度ルールで **multi-repo 所有 peer** が構造的に発生: content課 (`_contents-writing`) が `_LandingPage/glasswerks-lp`・`_blender` を所有、今後 product課/insight課 も同型。
- 現 guard は「CWD 配下のみ Write/Edit 許可」。multi-repo 所有 peer は所有リポを触るたびに別セッション起動 (cwd 切替) が必要 = セッション増コスト。
- 「純粋 CWD ベース」は既に破綻: fleet hook の allowlist に CWD 外例外が**ハードコード5件**ある (`validate-dangerous-ops-v2.sh:89-107` = memory / conductor drafts / conductor inbox / `_contents-writing/drafts` / `_videos` / plans)。本件は緩和ではなく、積み増した例外を「**所有**」概念へ整理・一般化するもの。

## 2. 設計 (Chief 提案・kimny 同意・conductor 指定の骨子に忠実)

### 2.1 所有マップ — `claude-code-template/.claude/hooks/ownership-map.tsv`

- **形式 = TSV (機械可読)**。1 行 = 1 (owner workspace, owned repo) ペア。`#` 始まりはコメント。
- **置き場所 = claude-code-template 内 (CCO 所有) — これが安全性のキモ**:
  - peer workspace 内 (例 `.claude/owned-repos`) に置くと peer が自分の所有を自己編集可能 = **任意リポ書込権の自己付与穴**。
  - template 置きなら所有変更 = template 変更 = **同じ guard が他 peer の自己改変を block** → CCO/conductor レビュー必須。**ガード自身がガバナンスを強制する構造**。
- **所有の正本 = 本マップ** (機械可読・guard が強制する権限の正本)。handoff 文書 = justification (各行に Evidence コメントで参照)。← ブリーフ「未決: 所有の正本どこに置くか」への回答。

初期データ (最小権限):
```
# ownership-map.tsv — 所有ベース write-guard の所有マップ (canonical = 権限の正本)
# 形式: <owner workspace realpath> <TAB> <owned repo realpath>   ※ # はコメント
# 編集は CCO のみ (本ファイルは template 内 = 他 peer は guard で block)。
# 各行 justification = related handoff を Evidence コメント併記。
#
# content課 (_contents-writing) ← 組織再編v2 LP統合
#   Evidence: _LandingPage/glasswerks-lp/docs/handoff-lp-to-content-20260611.md (WIP=0, prod=Vercel main自動deploy)
/Volumes/strage/_DevProjects/_contents-writing	/Volumes/strage/_DevProjects/_LandingPage/glasswerks-lp
```

- パスは **realpath 正規化形 (`/Volumes/strage/...`)** で記載。peer の $PWD は Dropbox symlink 形 (`$HOME/Dropbox/_DevProjects/...`) のこともあるため、**hook 側で owner/CWD/file 全てを realpath 正規化してから比較** (symlink 差異を吸収)。

### 2.2 hook 一般化 (Write/Edit ブロック直前に所有判定を挿入)

現行 `validate-dangerous-ops-v2.sh:109-117` の CWD ブロック直前に、所有マップ参照を追加する。**既存 allowlist 5件・CWD ブロック・.env/secrets ブロックは一切変更しない**。

```bash
  # --- 所有マップ判定 (CWD 基準 → 所有リポ基準への一般化) ---
  # template 内 ownership-map.tsv を読み、現 CWD が所有する追加リポへの書込を許可。
  # マップは template 内 (CCO所有) = peer は自己所有を増やせない (guard が自己昇格を block)。
  OWNERSHIP_MAP="$HOME/Dropbox/_DevProjects/claude-code-template/.claude/hooks/ownership-map.tsv"
  if [ "$IS_ALLOWLIST" = "0" ] && [ -f "$OWNERSHIP_MAP" ]; then
    CWD_REAL=$(realpath "$PWD" 2>/dev/null || echo "$PWD")
    FP_REAL=$(realpath "$FILE_PATH" 2>/dev/null || python3 -c "import os,sys;print(os.path.realpath(sys.argv[1]))" "$FILE_PATH" 2>/dev/null || echo "$FILE_PATH")
    while IFS=$'\t' read -r OWNER REPO; do
      case "$OWNER" in ''|\#*) continue;; esac      # blank / comment skip
      [ -n "$REPO" ] || continue
      OWNER_REAL=$(realpath "$OWNER" 2>/dev/null || echo "$OWNER")
      REPO_REAL=$(realpath "$REPO" 2>/dev/null || echo "$REPO")
      if [ "$CWD_REAL" = "$OWNER_REAL" ]; then
        if [ "$FP_REAL" = "$REPO_REAL" ] || [ "${FP_REAL#$REPO_REAL/}" != "$FP_REAL" ]; then
          IS_ALLOWLIST=1
          break
        fi
      fi
    done < "$OWNERSHIP_MAP"
  fi
```

- **fail-safe**: マップ不在なら no-op = 現行 CWD-only 挙動 (退行ゼロ)。
- **owner 一致 = realpath 完全一致** (CWD が所有者本人の時のみ展開)。**repo 一致 = realpath prefix** (所有リポ配下のみ)。
- hook コード自体は安定 (所有の増減 = データ行の追加のみ、コード再変更不要)。

### 2.3 Chief 専用 hook は対象外

`_chief/.claude/hooks/chief-cwd-write-guard.sh` は変更しない。Chief は所有リポを持たない設計 (write は `_chief` 内のみ)。本一般化は fleet 共通 `validate-dangerous-ops-v2.sh` のみ。

## 3. セキュリティ分析 (自己昇格穴の閉鎖)

| 攻撃面 | 結果 |
|--------|------|
| peer が自分の所有を増やそうと `ownership-map.tsv` を Write/Edit | **block** — map は template 内 = peer の CWD 外 + 所有外。CCO (cwd=template) のみ編集可 → conductor レビュー必須 |
| peer が template repo を所有マップに足そうとする | 同上 block (map 編集自体が block) |
| CWD spoof | $PWD = session 起動時 cwd。Write は file_path 指定、PWD は不変。spoof 不可 |
| Bash 経由 out-of-cwd 書込 (`echo > /other`) | **既知の限界 (現行と同じ)**。hook は Write/Edit のみ。本件は事故防止ガードであって対敵境界ではない (ブリーフ明記)。main 直 push 禁止 + PR レビューの下流層で有界化 |

★ 不変条件: **どの peer の所有リポにも `claude-code-template` を含めない**。初期データは content課 → glasswerks-lp のみ = 満たす。

## 4. 影響範囲 (blast radius)

`validate-dangerous-ops-v2.sh` を絶対パス参照する **10 workspace**: `_contents-writing` / `_data-analysis` / `claude-code-template` / `_cowork` / `_Reserch` / `_videos` / `freee-MCP` / `mued/threads-api` / `mued/mued_v2` / `mued/mued_v2/apps`。
→ live working-tree ファイル参照ゆえ **編集 = 即時全 peer 反映** (deploy/merge 不要)。= **承認前に live hook を触らない**。承認後に編集 + commit。

## 5. テスト計画 (承認後・実装時) — ★ロジックは prototype 検証済 7/7 pass

§2.2 ブロックを移植した standalone prototype を `/tmp` で実行し、下記 7 ケース全 pass を確認済 (live hook は未編集)。実装時は live hook で同テストを再実行し証跡化する。

echo JSON を hook に流す単体テスト (現行 chief hook テストと同型):
1. content課 cwd で glasswerks-lp 配下 Write → **allow** (所有マップ hit)
2. content課 cwd で 非所有リポ (例 `_data-analysis`) Write → **block** (退行なし)
3. 任意 cwd で `_contents-writing` cwd 外から glasswerks-lp Write (owner 不一致) → **block** (所有は owner 限定)
4. マップ削除時 content課→glasswerks-lp Write → **block** (fail-safe = 現行挙動)
5. 既存 allowlist (memory / conductor drafts / plans) → **allow** (不変確認)
6. .env / secrets Write → **block** (不変確認)
7. peer cwd から `ownership-map.tsv` 自体を Write → **block** (自己昇格閉鎖確認)

## 6. Tier ガバナンス (conductor 裁定の明文化)

- **初回の仕組み導入 (本設計 = hook 改修 + マップ新設)** = 全 peer 波及 = **Tier 3** (本書 → conductor レビュー → merge)。
- **以後の所有行追加** = 1 peer のみに効く加算的データ変更 = **Tier 2** (CCO がマップ行追加 → conductor レビュー & merge。guard で peer 自己編集不可)。
- **例外**: 付与先が **本番 / 課金 / secret に触れるリポ** なら **Tier 3 に上げて kimny ゲート**。

## 7. 初期データの裏取り・要確認 (conductor へ)

1. **glasswerks-lp (content課)**: handoff `handoff-lp-to-content-20260611.md` 確認済 (WIP=0)。⚠️ **ただし glasswerks-lp は本番に触れる** (Vercel `main` マージ = `www.glasswerks.jp` 自動 deploy、Env=`ADMIN_PASSWORD`/`BLOB_READ_WRITE_TOKEN` は Vercel 側)。§6 例外則では本来 Tier3+kimny ゲート対象。今回は kimny b-2 承認 + conductor 初期データ指定の範囲内と理解。**下流防御**: `block-main-push.sh` で main 直 push 物理 block + PR レビュー必須ゆえ「編集可」≠「本番 deploy 可」。この理解で進めてよいか確認願います。
2. **`_blender` (content課)**: ⚠️ **所有移転 handoff / justification doc が見当たらない** (`_blender` 配下に handoff 系ファイル無し)。「handoff = justification」原則 + 最小権限ゆえ、**初期マップから blender 行は defer**。blender→content課 の handoff が起きてから Tier 2 で行追加を提案。conductor 異議あれば指定 Evidence を教えてください。
3. product課 / insight課 の所有は実際に書込が必要になった時に Tier 2 で行追加 (今は事前付与しない = ブリーフ最小権限方針どおり)。

## 8. ロールアウト手順 (conductor 承認後)

1. `ownership-map.tsv` を template に新設 (content課→glasswerks-lp の1行)。
2. `validate-dangerous-ops-v2.sh` に §2.2 ブロックを挿入 (= live 反映)。
3. §5 単体テスト全 pass を証跡化。
4. template repo にコミット (org-restructure ブランチ or 専用ブランチ)。conductor が PR レビュー。
5. README / `setup.sh` の hook 説明に ownership-map の存在を追記 (整合)。
6. memory に Tier2 昇格ルール (所有行追加手順) を記録。

## 9. 据え置く既存挙動 (本設計では触らない)

- 既存 allowlist 5件 (memory / conductor drafts / inbox / `_contents-writing/drafts` / `_videos` / plans) は不変。`_videos` workspace は現存ゆえ例外維持。
- 将来整理候補 (別 /plan): delivery 系例外 (conductor drafts/inbox) を「global owner」概念へ統合するか、`_contents-writing/drafts` 例外が content課 in-cwd 化で不要になったか — 本件スコープ外、退行回避のため現状維持。
