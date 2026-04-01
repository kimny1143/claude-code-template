# Template Repo 公開化 企画草案

> 作成日: 2026-03-30
> 更新日: 2026-03-30（kimnyレビュー反映 — 双リポ構成に方針変更）
> ステータス: 草案v2（方針変更反映済み・conductor最終確認待ち）
> 優先度: 低（草案先行で固める段階）

---

## 0. 基本方針: 双リポ構成（private + public 並行運用）

### 変更前の想定
既存の `claude-code-template`（private）をクリーンアップして Public に切り替える。

### 変更後の方針（kimny決定 2026-03-30）
**publicリポは新規に独立して作る。既存のprivateリポはそのまま自社運用として維持する。**

```
┌─────────────────────────────┐     ┌──────────────────────────────────┐
│  claude-code-template       │     │  mued-claude-code-template       │
│  (private / 自社運用)        │     │  (public / OSS)                  │
│                             │     │                             │
│  ・課固有の設定              │ ──→ │  ・汎用スキル/コマンド        │
│  ・内部知見・実験的スキル     │     │  ・OSS向けREADME/FAQ         │
│  ・実パス含む設定ファイル     │ ←── │  ・コミュニティcontribution   │
│  ・claude-history MCP本体   │     │  ・MCP セットアップ手順       │
│                             │     │                             │
│  「試して良かったもの」を     │     │  「コミュニティ改善」を       │
│   publicに移す               │     │   privateに取り込む          │
└─────────────────────────────┘     └─────────────────────────────┘
```

### この方針のメリット
1. **差分分析**: private と public の差分を随時比較し、知見の流れを可視化できる
2. **安全性**: 既存リポのgit履歴・内部設定を一切触らない。秘匿漏れリスクがゼロ
3. **双方向フロー**: 自社→OSS（実証済みプラクティス）、OSS→自社（コミュニティ改善）

---

## 1. publicリポに含めるファイルの選定

### publicリポに含める（privateからコピー or 新規作成）

| カテゴリ | 対象 | 作業 | 備考 |
|---------|------|------|------|
| **Core** | `setup.sh` | そのままコピー | パスはenv変数/引数で設定可能 |
| | `CLAUDE.md.template` | そのままコピー | プレースホルダーのみ。汎用的 |
| | `README.md` | **新規作成** | OSS向けに書き下ろし（後述の構成案） |
| | `LICENSE` | 要確認 | 現在MIT。継続 or 変更の判断 |
| | `CONTRIBUTING.md` | **新規作成** | コントリビューション方針（後述） |
| **Commands** | `.claude/commands/commit.md` | そのままコピー | |
| | `.claude/commands/pr.md` | そのままコピー | |
| | `.claude/commands/ship.md` | そのままコピー | |
| | `.claude/commands/build-fix.md` | そのままコピー | |
| | `.claude/commands/security.md` | そのままコピー | |
| | `.claude/commands/learn.md` | そのままコピー | |
| **Skills (34+)** | `.claude/skills/*/SKILL.md` | そのままコピー | 全スキル公開。最大の差別化ポイント |
| **Agents** | `.claude/agents/*.md` | そのままコピー | code-reviewer, security-reviewer, codebase-optimizer, docs-curator, code-simplifier, verify-app |
| **Hooks** | `.claude/hooks/block-main-push.sh` | そのままコピー | ブランチ保護 |
| | `.claude/hooks/validate-dangerous-ops.sh` | そのままコピー | 危険操作ブロック |
| | `.claude/hooks/suggest-git-cleanup.sh` | そのままコピー | Git整理提案 |
| | `.claude/hooks/check-remotion-quality.sh` | そのままコピー | Remotion品質チェック |
| **Settings** | `.claude/settings.local.json.example` | そのままコピー | 権限テンプレート。パスはプレースホルダー済み |
| **MCP** | `mcps/claude-peers/README.md` | そのままコピー | セットアップ手順のみ |
| | `mcps/nano-banana-pro/README.md` | そのままコピー | セットアップ手順 |
| | `mcps/nano-banana-pro/launch.sh` | そのままコピー | APIキーは.env.localから読む設計 |
| | `mcps/fal-video/launch.sh` | そのままコピー | 同上 |
| **Docs** | `docs/templates/` | そのままコピー | ドキュメントテンプレート |
| **Config** | `project-configs/` | **パス置換してコピー** | フルパスをプレースホルダーに |

### publicリポに含めない（privateのみに残る）

| 対象 | 理由 |
|------|------|
| `.claude/settings.local.json` | 実パス（`/Users/kimny/...`）含む実設定 |
| `mcps/claude-history/` 全体 | 自作MCPサーバー本体 + 会話データ。公開するなら別リポジトリ |
| `files.zip` | 内容未確認。内部用 |
| `skills-lock.json` | 自動生成メタデータ |
| `link-ios-skill.sh` | ローカルパス含む可能性 |
| `.DS_Store` | macOS固有 |
| `.adal/`, `.augment/`, `.codebuddy/` 等30+ディレクトリ | 各種AIエディタの自動生成設定 |
| `docs/template-repo-publication-plan.md` | この草案自体（内部企画書） |

---

## 2. publicリポ作成手順

新規リポジトリとして独立作成する。既存privateリポのクリーンアップは不要。

### Phase 1: publicリポの初期化

- [ ] GitHub上で新規リポジトリを作成
  - 命名候補: `claude-code-template-oss` / `claude-code-starter` / `claude-code-toolkit`（後述の命名検討参照）
  - Visibility: **Public**
  - Description / Topics を設定（`claude-code`, `ai-coding`, `template`, `skills` 等）
- [ ] ローカルに clone
- [ ] LICENSE ファイル配置（MIT継続 or 変更の最終判断）

### Phase 2: コンテンツ移行

- [ ] セクション1の「publicリポに含める」リストに基づき、privateリポからファイルをコピー
- [ ] `project-configs/*/settings.local.json.example` 内のフルパスをプレースホルダーに置換
  - `/Users/kimny/...` → `/path/to/your/project/...`
- [ ] コピーしたファイル全体で秘密情報チェック:
  - `grep -r "/Users/kimny" .`
  - `grep -r "API_KEY\|SECRET\|TOKEN\|PASSWORD" .`
- [ ] `mcps/claude-history/` は README.md のみコピー（概要と「別リポで公開予定」の記載）

### Phase 3: OSS向けコンテンツ作成

- [ ] README.md を新規作成（後述の構成案に基づく）
- [ ] CONTRIBUTING.md を新規作成（後述のコントリビューション方針に基づく）
- [ ] `.gitignore` を適切に設定:
  ```
  # OS
  .DS_Store

  # Claude Code local config
  .claude/settings.local.json
  skills-lock.json

  # AI editor configs (contributors may have various editors)
  .adal/
  .augment/
  .codebuddy/
  .commandcode/
  .continue/
  .cortex/
  .crush/
  .factory/
  .goose/
  .iflow/
  .junie/
  .kilocode/
  .kiro/
  .kode/
  .mcpjam/
  .mux/
  .neovate/
  .openhands/
  .pi/
  .pochi/
  .qoder/
  .qwen/
  .roo/
  .trae/
  .vibe/
  .windsurf/
  .zencoder/
  ```

### Phase 4: 初回コミット・公開

- [ ] 全ファイルをステージング、初回コミット
- [ ] GitHub に push
- [ ] README内のリンク（Zenn記事、note等）が正しいか確認
- [ ] リポジトリの Settings > Features で Discussions を有効化（任意）

---

## 3. private↔public 差分分析の仕組み

双リポ構成の最大の価値は、private（自社知見）とpublic（コミュニティ知見）の差分を可視化し、双方向に知見を流すこと。

### 差分の種類

| 方向 | 内容 | 頻度 |
|------|------|------|
| **private → public** | 自社で実証済みのスキル・パターンを公開 | 随時（安定したら） |
| **public → private** | コミュニティからのPR・Issue知見を取り込む | PR/Issueマージ時 |
| **private only** | 課固有設定・内部知見・実験的スキル | 公開しない |
| **public only** | コミュニティ発のスキル（自社では不要なもの） | 取り込み不要 |

### 差分分析の手段

#### 案A: 手動比較（初期推奨）
- 月次で `diff -rq` や `git diff --no-index` でファイル差分を確認
- 差分リストをスプレッドシート or Issue で管理
- 移行判断はconductor課 + kimny

```bash
# privateとpublicの差分確認（スキルディレクトリの例）
diff -rq private-repo/.claude/skills/ public-repo/.claude/skills/
```

#### 案B: 同期スクリプト（将来）
- `scripts/sync-to-public.sh`: private→publicの選択的コピー
- `scripts/diff-report.sh`: 差分レポート生成
- 対象ディレクトリ・ファイルをホワイトリストで管理

#### 案C: git remote（将来・上級）
- publicリポを private の remote として追加
- cherry-pick で個別コミットを移行
- ただしgit履歴の混在リスクがあるため、初期は非推奨

### 移行判断基準

privateからpublicに移す際の判断基準:

| 基準 | 条件 |
|------|------|
| **汎用性** | 特定プロジェクト・課に依存しない |
| **安定性** | 2週間以上の実運用で問題なし |
| **秘匿性** | 内部パス・APIキー・固有名称を含まない |
| **価値** | OSSユーザーにとって有用（自社固有の運用知見は除外） |

---

## 4. publicリポの命名検討

| 候補 | メリット | デメリット |
|------|---------|----------|
| `claude-code-template` | シンプル。検索しやすい | privateと同名（GitHub上は別org/userで区別可能） |
| `claude-code-template-oss` | privateとの区別が明確 | `-oss` が冗長 |
| `claude-code-starter` | 「始める」ニュアンスで初心者に親切 | テンプレート以上の内容がある |
| `claude-code-toolkit` | 包括的な印象 | ツールキットというほどの規模か |
| `claude-code-recipes` | スキル中心の印象 | コマンド・hooks等も含む |

**最終決定（kimny確定 2026-03-30）:**

- **public**: `mued-claude-code-template` — 新規作成。remote: https://github.com/kimny1143/mued-claude-code-template.git
- **private**: `claude-code-template` — そのまま維持（リネームなし）

この方式のメリット:
- 既存のprivateリポに一切影響なし（symlink・remote URL変更不要）
- `mued-` プレフィックスでブランド識別が明確

---

## 5. 差分同期の定常タスク（運用サイクル）

双リポ構成の維持には、定期的な同期作業が不可欠。放置すると private と public が乖離し、双方向フローの価値が失われる。

### サイクル概要

```
┌────────────────────────────────────────────────────────┐
│              隔週 差分同期サイクル                        │
│                                                        │
│  ① 棚卸し   privateで直近に追加・改善されたものを一覧化   │
│      ↓                                                 │
│  ② 選定     公開に適するか判断（汎用性・秘匿チェック）    │
│      ↓                                                 │
│  ③ 反映     publicリポにPR経由で追加                     │
│      ↓                                                 │
│  ④ 取り込み  publicのIssues/PRから有用なものをprivateへ   │
│      ↓                                                 │
│  ⑤ 記録     何を出した/取り込んだ/見送った+理由を記録     │
│                                                        │
│  ※ この記録自体がZenn/noteのコンテンツ素材になる          │
└────────────────────────────────────────────────────────┘
```

### 実施要領

| 項目 | 内容 |
|------|------|
| **頻度** | 隔週（月2回）。初期は週次で回し、安定したら隔週に移行 |
| **担当** | template課が実施、conductor課が確認 |
| **記録先** | publicリポの `docs/sync-log.md` |
| **所要時間目安** | 30分〜1時間/回 |

### 各ステップの詳細

#### ① 棚卸し
```bash
# privateリポで直近2週間の変更を確認
cd claude-code-template  # private
git log --since="2 weeks ago" --name-only --pretty=format:"%h %s"
```
- 対象: `.claude/skills/`, `.claude/commands/`, `.claude/hooks/`, `.claude/agents/`
- 新規追加・既存改善・削除をリスト化

#### ② 選定（公開判断）
セクション3の「移行判断基準」に基づき判断:
- 汎用性: 特定課に依存しないか
- 安定性: 2週間以上の実運用で問題ないか
- 秘匿性: 内部パス・APIキー・固有名称を含まないか
- 価値: OSSユーザーにとって有用か

#### ③ publicリポへの反映
- featureブランチで作業し、PR経由でマージ
- コミットメッセージに `[sync from private]` プレフィックスを付与
- PR description に変更理由・privateでの実績を記載

#### ④ publicからの取り込み
- publicリポのIssues / Pull Requests を確認
- 有用なcontribution（スキル改善、バグ修正等）をprivateに反映
- コミットメッセージに `[sync from public]` プレフィックスを付与

#### ⑤ 記録（sync-log.md）

```markdown
## 2026-W14 (03-30)

### private → public
- [追加] skills/xxx: 〇〇スキルを公開（3課で2週間運用、問題なし）
- [見送り] skills/yyy: 課固有の設定に依存。汎用化が必要

### public → private
- [取り込み] PR#12: コマンドのtypo修正
- [見送り] Issue#8: 要望として記録、優先度低

### 所感
（Zenn/note記事のネタになりそうな気づき）
```

### Zenn/note連動ポイント

この差分記録は三層導線（セクション7）のコンテンツ素材として活用:

| 記録内容 | 活用先 | 記事テーマ例 |
|---------|--------|------------|
| 公開判断の理由 | note（有料） | 「なぜこのスキルは公開し、あれは公開しなかったか」 |
| コミュニティPRの分析 | Zenn（無料） | 「OSSにして最初の1ヶ月で何が起きたか」 |
| private/publicの乖離パターン | Zenn（無料） | 「自社テンプレートとOSSテンプレートの育て方の違い」 |

---

## 6. README.md OSS向けガイド構成案

現在のREADME.mdをベースに、以下の構成に改訂する。

```markdown
# Claude Code Template

Claude Code のベストプラクティスを構造化したテンプレート。
個人開発者・小規模チームが Claude Code を実務で運用するための
commands / skills / agents / hooks を体系的にまとめたもの。

## What's Inside

### 概要表（現在のREADMEと同等、スキル一覧含む）

## Quick Start

### 方法A: fork して使う（推奨）
1. このリポジトリを fork
2. CLAUDE.md.template → CLAUDE.md にリネーム
3. プロジェクト情報を記入
4. settings.local.json.example → settings.local.json にコピーしパス修正

### 方法B: シンボリックリンクで共有
（現在のREADMEの内容を維持）

### 方法C: 必要なものだけコピー
（現在のREADMEの内容を維持）

## 運用例: マルチエージェント体制

> この運用例は glasswerks inc. での実績に基づいています。
> 詳細は [Zenn記事シリーズ](link) で解説しています。

### 課（部署）構成の設計
- 1エージェント = 1課（1つのワークスペース）
- 課の分割基準: リポジトリ境界 or 機能ドメイン

### Tier制度（PRレビュー権限の段階的委譲）
| Tier | 対象 | フロー |
|------|------|--------|
| T1 | docs・データのみ | セルフマージ |
| T2 | コード変更 | ピアレビュー |
| T3 | セキュリティ・DB・外部サービス | 人間レビュー |

### ブランチ保護
- block-main-push.sh の仕組み
- settings.local.json での権限設計パターン

## MCP Servers
（各MCPのセットアップ手順）

## カスタマイズ
（プロジェクト固有のスキル・コマンド追加方法）

## FAQ
（後述のFAQ内容）

## 参考資料
（現在のREADMEの内容を維持）

## License
MIT
```

**ポイント:**
- 「運用例」セクションを新設し、Tier制度・課構成を具体例として紹介
- Quick Start に「fork して使う」を最初に配置（OSSの標準的な使い方）
- 技術詳細は各ファイル内に任せ、READMEは概要とナビゲーションに徹する

---

## 7. Zenn記事との連動設計

### 三層導線: Zenn → GitHub fork → note

```
┌─────────────────────────────────────────────────────┐
│                    読者のジャーニー                     │
│                                                       │
│  Zenn（無料）          GitHub（無料）      note（有料）  │
│  ┌─────────────┐     ┌──────────────┐   ┌──────────┐ │
│  │ 何をやっている │ ──→ │ 自分で試す    │ ─→ │ なぜそう  │ │
│  │ かを見せる    │     │ （fork/clone）│    │ したかを  │ │
│  │              │     │              │    │ 売る     │ │
│  │ ・体制の全体像│     │ ・setup.sh   │    │          │ │
│  │ ・数字で実証  │     │ ・SKILL.md群 │    │ ・判断理由│ │
│  │ ・設定の抜粋  │     │ ・hooks      │    │ ・失敗談  │ │
│  │              │     │ ・settings   │    │ ・設計変更│ │
│  └──────┬───────┘     └──────┬───────┘   └──────────┘ │
│         │                    │                         │
│    信用構築              再現・応用               課金     │
│   （エンジニア信頼）     （実務で使う）        （深い知見） │
└─────────────────────────────────────────────────────┘
```

### 各層の役割と相互参照ルール

| 層 | プラットフォーム | 内容 | 課金 | 他層への導線 |
|----|----------------|------|------|-------------|
| **Layer 1** | Zenn | 技術記事。体制・コスト・運用の事実を数字で | 無料 | 記事末尾でGitHubリンク + note導線 |
| **Layer 2** | GitHub | テンプレートリポジトリ。fork/cloneで再現可能 | 無料 | README内でZenn記事シリーズとnoteへリンク |
| **Layer 3** | note | AIインタビュー形式。判断プロセスと失敗の深掘り | 有料（¥300〜） | 記事内でGitHub/Zennへの逆参照 |

### Zenn記事でのGitHub参照パターン

```markdown
## 実際の設定ファイル

Tier制度のルールは CLAUDE.md に定義している。

\```yaml:CLAUDE.md（抜粋）
## PRレビュー権限
- Tier 1: docs・データのみ → セルフマージ
- Tier 2: コード変更 → ピアレビュー
- Tier 3: セキュリティ・DB → 人間レビュー
\```

完全なテンプレートは GitHub で公開している:
→ [claude-code-template](https://github.com/kimny1143/claude-code-template)

fork して自分のチームに合わせてカスタマイズできる。
```

### GitHub READMEからの逆参照パターン

```markdown
## 運用例

この構成で実際に運用した結果を Zenn で公開しています:
- [作曲家がClaude Code 10課体制を月4万円で回している](link)

設計判断の背景は note のインタビューシリーズで詳しく:
- [AIに部下ができた日](https://note.com/mued_glasswerks/n/...)
```

### 記事ネタとテンプレート機能の対応表

| Zenn記事テーマ | テンプレートの該当部分 | 読者が試せること |
|---------------|---------------------|----------------|
| Tier制度の設計と運用 | CLAUDE.md.template, settings.local.json.example | 自チームのTierルール定義 |
| ブランチ保護の自動化 | block-main-push.sh, hooks設定 | main直pushブロックの導入 |
| 34スキルの体系化 | .claude/skills/*, setup.sh | スキルのsymlink共有 |
| マルチエージェント間通信 | mcps/claude-peers/README.md | claude-peersの導入 |
| コスト管理 | docs/templates/api-cost-inventory-template.md | APIコスト棚卸しの実施 |

---

## 8. 公開後の想定FAQ

### ライセンス

**Q: ライセンスは？**
A: MIT License。商用利用・改変・再配布すべて自由。

**Q: 社内テンプレートとして使ってよいか？**
A: はい。fork して自社向けにカスタマイズしてください。クレジット表記は不要（MITなので）。

**Q: スキルの内容を自分のテンプレートに含めて再配布してよいか？**
A: はい。MITライセンスに基づき自由に利用可能。

### サポート範囲

**Q: バグ報告や機能リクエストはどこに？**
A: GitHub Issues。ただし以下の制約を明示:
- このリポジトリは glasswerks の実運用テンプレートがベース
- Issue対応・PR対応は best-effort（保証なし）
- Claude Code 本体のバグは Anthropic に報告してください

**Q: 質問はどこに？**
A: GitHub Discussions（有効化する場合）。または Zenn 記事のコメント欄。

**Q: 特定のスキルが動かない**
A: スキルは Claude Code のバージョンに依存する場合がある。動作確認済みのバージョンを README に記載する。

### コントリビューション方針

**Q: PR を出してよいか？**
A: 歓迎。ただし以下のガイドラインに従ってください:
- 新スキルの追加: SKILL.md のフォーマットに従い、description にトリガー例を含める
- 既存スキルの改善: 変更理由を PR の description に明記
- バグ修正: Issue を先に立てて、修正 PR で参照する

**Q: 新しいスキルをコントリビュートしたい**
A: 以下の基準を満たすスキルを歓迎:
1. 汎用的（特定プロジェクトに依存しない）
2. 再現可能（読者が自分の環境で使える）
3. SKILL.md のフォーマット（frontmatter + description + トリガー例）に準拠

**Q: glasswerks 固有の運用ルール（課名・Tier制度の詳細）は変更してよいか？**
A: 「運用例」セクションは参考情報。自チームに合わせて自由にカスタマイズしてください。

### その他

**Q: Claude Code 以外のAIコーディングツールでも使える？**
A: スキルの内容（SKILL.md）は汎用的な知識だが、commands / hooks / settings.json は Claude Code 固有の仕組み。他ツールには直接適用できない。

**Q: Claude Code Max（$200/月）でないと使えないか？**
A: テンプレート自体はどのプランでも使える。ただし、マルチエージェント体制（claude-peers）は複数インスタンスの同時実行が前提なので、Max プランの固定料金が実質的に必要。

---

## 補足: 公開タイミングの検討

| タイミング | メリット | リスク |
|-----------|---------|--------|
| Zenn記事と同時公開 | 記事の説得力が最大化。「今すぐ試せる」 | 記事公開前の準備工数 |
| Zenn記事の後に公開 | 記事への反応を見てから判断可能 | 「テンプレートはどこ？」の問い合わせ |
| 先にGitHub公開 | 記事の参照先が先に存在する安心感 | 初動の注目を分散させる |

**推奨:** Zenn第1弾記事と同日公開。記事内でリンクし、読者が即座にforkできる状態にする。

---

## 次のステップ

1. [ ] conductor最終確認（この草案v2）
2. [ ] publicリポの命名決定
3. [ ] ライセンス・コントリビューション方針の最終決定
4. [ ] claude-history MCP の取り扱い決定（別repo化 or README参照のみ）
5. [ ] Phase 1〜4 の実施（publicリポ作成 → コンテンツ移行 → OSS向け作成 → 公開）
6. [ ] 差分同期サイクルの初回実施（publicリポ公開後）
7. [ ] Zenn第1弾記事の公開タイミングと連動
