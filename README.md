# Claude Code Template

**38 skills. 8 commands. 6 agents. 3 MCPs. One setup script.**

Claude Code のベストプラクティスを凝縮したテンプレート。`setup.sh` を実行するだけで、テスト駆動開発からマーケティング監査まで、38 のスキルがプロジェクトに即座に適用される。

> **[Pro版 ($29)](https://glasswerks.gumroad.com/l/claude-code-template-pro)** — AIマルチエージェントチーム運用テンプレート。Conductor設定・Tier制PRレビュー・巡回レポート・コスト管理の実運用ノウハウを収録。[Free vs Pro 比較 →](#free-vs-pro)

---

## Before / After

### Before: テンプレートなし

```
You: "Write tests first, then implement"
Claude: *writes tests with random patterns, inconsistent structure*

You: "Review this PR for security issues"
Claude: *generic checklist, misses project-specific risks*

You: "Set up analytics tracking"
Claude: *starts from scratch every time*
```

毎回ゼロから指示。プロジェクトが変わるたびに同じ説明を繰り返す。

### After: テンプレート適用後

```
You: /tdd
Claude: *RED-GREEN-REFACTOR cycle with your project's test framework*

You: /security
Claude: *OWASP Top 10 + dependency audit + your CI pipeline integration*

You: "Set up analytics"
Claude: → analytics-tracking skill auto-loaded
       *GA4 setup, event taxonomy, UTM strategy, tag manager config*
```

スキルが自動ロードされ、ベストプラクティスに沿った出力が即座に得られる。

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/kimny1143/claude-code-template.git ~/claude-code-template

# 2. Setup (any project)
cd /path/to/your/project
curl -o setup-claude.sh https://raw.githubusercontent.com/kimny1143/claude-code-template/main/setup.sh
chmod +x setup-claude.sh && ./setup-claude.sh

# Done. All skills, commands, agents, hooks are symlinked.
```

テンプレートを更新すれば全プロジェクトに即反映（シンボリックリンク方式）。

---

## What's Included

### Commands（8 スラッシュコマンド）

| コマンド | 用途 | 使いどころ |
|---------|------|-----------|
| `/commit` | Git コミットワークフロー | 変更をコミットする時 |
| `/pr` | Pull Request 作成 | PRを作成する時 |
| `/ship` | Commit → Push → PR 一括 | 実装完了後の一括処理 |
| `/build-fix` | ビルドエラー自動修正 | CI/ビルドが壊れた時 |
| `/security` | セキュリティ監査 | リリース前チェック |
| `/learn` | CLAUDE.md 育成 | プロジェクト設定の学習・更新 |
| `/codex` | OpenAI Codex CLI 委譲 | Codex CLIにタスクを渡す時 |
| `/ios` | iOS ビルド & 提出 | App Store提出ワークフロー |

### Skills（38 スキル）

#### Development（11）

| スキル | 用途 |
|-------|------|
| `tdd` | テスト駆動開発（RED-GREEN-REFACTOR） |
| `backend-patterns` | API / Repository / バリデーションパターン |
| `coding-rules` | TypeScript / 命名規則 / 関数設計 |
| `git-worktree` | Git worktree 並行開発 |
| `hooks` | Claude Code Hook 作成・管理 |
| `mcp` | MCP サーバー作成・設定 |
| `remotion` | Remotion 動画制作 |
| `ios-app-store-submission` | iOS App Store 提出ワークフロー |
| `vercel-react-best-practices` | React / Next.js パフォーマンス最適化 |
| `vercel-react-native-skills` | React Native / Expo ベストプラクティス |
| `vercel-composition-patterns` | React コンポジションパターン |

#### Marketing & CRO（15）

| スキル | 用途 |
|-------|------|
| `lp-optimizer` | LP / ページ分析・改善 |
| `copywriting` | マーケティングコピー作成 |
| `seo-audit` | SEO 監査・診断 |
| `marketing-audit` | マーケティング総合監査 |
| `marketing-psychology` | 心理学ベースのマーケティング |
| `launch-strategy` | ローンチ / GTM 戦略 |
| `pricing-strategy` | 価格設定・パッケージング |
| `ab-test-setup` | A/B テスト設計・実装 |
| `analytics-tracking` | アナリティクス計測・実装 |
| `core-web-vitals` | Core Web Vitals 計測・改善 |
| `email-sequence` | メールシーケンス作成 |
| `referral-program` | リファラルプログラム設計 |
| `signup-flow-cro` | サインアップフロー最適化 |
| `onboarding-cro` | オンボーディング最適化 |
| `form-cro` | フォーム最適化 |

#### UX & Product（5）

| スキル | 用途 |
|-------|------|
| `ui-ux-pro-max` | UI/UX 設計・実装・レビュー |
| `ux-psychology` | UX 心理学効果の適用 |
| `web-design-guidelines` | Web Interface Guidelines 準拠レビュー |
| `app-onboarding` | アプリオンボーディング設計・改善 |
| `paywall-upgrade-cro` | ペイウォール・アップグレード最適化 |

#### Payments & Billing（3）

| スキル | 用途 |
|-------|------|
| `stripe-best-practices` | Stripe 統合ガイド（API選択・Connect・課金・Treasury） |
| `stripe-projects` | Stripe Projects CLI でのスタック構築 |
| `upgrade-stripe` | Stripe API バージョン・SDK アップグレード |

#### Content & Monetization（4）

| スキル | 用途 |
|-------|------|
| `ai-interview-article` | インタビュー形式 note 記事作成 |
| `note-serial-monetization` | note 連載の有料/無料設計 |
| `freee-api-skill` | freee API 操作ガイド |
| `note-publish-flow` | note 記事公開フロー（公開前チェック・重複照合・通知） |
### Agents（6 サブエージェント）

| エージェント | 用途 |
|-------------|------|
| `code-reviewer` | PR / コードレビュー |
| `security-reviewer` | セキュリティ監査 |
| `codebase-optimizer` | コード最適化・重複検出 |
| `docs-curator` | ドキュメント整理 |
| `code-simplifier` | コード簡素化 |
| `verify-app` | アプリ動作検証 |

### Hooks（自動実行）

| フック | タイミング | 用途 |
|--------|-----------|------|
| `validate-dangerous-ops.sh` | PreToolUse | 危険操作（rm -rf, DROP TABLE 等）ブロック |
| `block-main-push.sh` | PreToolUse | main ブランチへの直接 push 防止 |
| `suggest-git-cleanup.sh` | Stop | セッション終了時の Git 整理提案 |

### MCPs（MCP サーバー）

| MCP | 用途 |
|-----|------|
| `claude-history` | claude.ai 会話履歴の検索（Python） |
| `nano-banana-pro` | Gemini 画像生成・編集（npx） |
| `claude-peers` | 複数 Claude Code インスタンス間のリアルタイム連携 |

---

## Setup Details

### 方法 A: シンボリックリンクで共有（推奨）

複数プロジェクトで設定を共有し、テンプレート更新が全プロジェクトに即反映。

```bash
# テンプレートを配置
git clone https://github.com/kimny1143/claude-code-template.git ~/claude-code-template

# 任意のプロジェクトにセットアップ
cd /path/to/your/project
curl -o setup-claude.sh https://raw.githubusercontent.com/kimny1143/claude-code-template/main/setup.sh
chmod +x setup-claude.sh && ./setup-claude.sh
```

手動で個別にリンクする場合:
```bash
TEMPLATE=~/claude-code-template/.claude
mkdir -p .claude/{commands,skills,agents,hooks}

# コマンドをリンク
ln -s $TEMPLATE/commands/commit.md .claude/commands/
ln -s $TEMPLATE/commands/pr.md .claude/commands/

# スキルをリンク
ln -s $TEMPLATE/skills/tdd .claude/skills/
ln -s $TEMPLATE/skills/coding-rules .claude/skills/
# ... 必要なスキルを選択
```

#### 構成イメージ

```
claude-code-template/              ← 共有設定の原本
├── .claude/
│   ├── commands/commit.md         ← 全プロジェクト共通
│   ├── skills/tdd/                ← 全プロジェクト共通
│   └── agents/code-reviewer.md

your-project/.claude/
├── commands/
│   ├── commit.md → symlink        ← テンプレートから
│   └── deploy.md                  ← プロジェクト固有
└── skills/
    ├── tdd → symlink              ← テンプレートから
    └── my-database/               ← プロジェクト固有
```

### 方法 B: コピーで使用

独立した設定が必要な場合。

```bash
git clone https://github.com/kimny1143/claude-code-template.git
cp -r claude-code-template/.claude/ /path/to/your/project/
cp claude-code-template/CLAUDE.md.template /path/to/your/project/CLAUDE.md
```

---

## Customization

### プロジェクト固有のスキル追加

```bash
mkdir -p .claude/skills/your-skill
cat > .claude/skills/your-skill/SKILL.md << 'EOF'
Your skill instructions here.
Trigger: "your keyword"
EOF
```

### Hooks のカスタマイズ

`.claude/settings.local.json` でフックのパスとマッチャーを設定:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|Bash",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/validate-dangerous-ops.sh"
          }
        ]
      }
    ]
  }
}
```

---

## Free vs Pro

| | Free（このリポジトリ） | [Pro ($29)](https://glasswerks.gumroad.com/l/claude-code-template-pro) |
|---|---|---|
| **Skills** | 38 スキル | 38 スキル |
| **Commands** | 8 コマンド | 8 コマンド |
| **Agents** | 6 エージェント | 6 エージェント |
| **Hooks** | 6 フック | 6 フック |
| **MCPs** | 3 MCP設定 | 3 MCP設定 |
| **Conductor テンプレート** | - | 指揮エージェントの完全版 CLAUDE.md（巡回スケジュール・権限モデル） |
| **Tier制 PRレビュー** | - | 3段階レビューシステム運用マニュアル（Tier 1: セルフマージ / Tier 2: ピアレビュー / Tier 3: 承認制） |
| **巡回レポート** | - | テンプレート + 通常日・インシデント日の実サンプル 2 種 |
| **日報テンプレート** | - | フォーマット + 3 日分のリアルなサンプル |
| **組織図テンプレート** | - | 記入式 + 10 課体制の記入済みサンプル + 設計判断メモ |
| **コスト管理** | - | 月次追跡 + 損益分岐点計算 + 四半期監査レポート + 記入済みサンプル |
| **言語** | 日本語 | 日英バイリンガル |

**Free = ツール。Pro = ツール + 運用ノウハウ。**

Claude Code を 1 人で使うなら Free で十分。複数エージェントをチームとして運用するなら、Pro の運用テンプレートで立ち上げ時間を大幅に短縮できる。

**[$29 — Gumroad で購入](https://glasswerks.gumroad.com/l/claude-code-template-pro)**

---

## References

- [Affaan Mustafa: Everything Claude Code](https://github.com/affaan-m/everything-claude-code)
- [Anthropic: Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)

## License

MIT
