# Claude Code Template

Claude Code のベストプラクティスを適用したテンプレート。

Affaan Mustafa の「[Everything Claude Code](https://github.com/affaan-m/everything-claude-code)」ガイドと [Anthropic 公式ベストプラクティス](https://www.anthropic.com/engineering/claude-code-best-practices)を基に構成。

## 含まれるもの

### Commands（スラッシュコマンド）

| コマンド | 用途 |
|---------|------|
| `/commit` | Git コミットワークフロー |
| `/pr` | Pull Request 作成 |
| `/build-fix` | ビルドエラー自動修正 |
| `/security` | セキュリティ監査 |

### Skills（詳細ガイド）

| スキル | 用途 |
|-------|------|
| `tdd` | テスト駆動開発 |
| `backend-patterns` | API/Repository パターン |
| `coding-rules` | コーディング規約 |
| `git-worktree` | Git worktree 操作 |
| `hooks` | Claude Code Hook 作成 |
| `mcp` | MCP サーバー作成 |

### Agents（サブエージェント）

| エージェント | 用途 |
|-------------|------|
| `code-reviewer` | PR/コードレビュー |
| `security-reviewer` | セキュリティ監査 |
| `codebase-optimizer` | コード最適化・重複検出 |
| `docs-curator` | ドキュメント整理 |

### Hooks（自動実行）

| フック | タイミング | 用途 |
|--------|-----------|------|
| `validate-dangerous-ops.sh` | PreToolUse | 危険操作ブロック |
| `suggest-git-cleanup.sh` | Stop | Git 整理提案 |

## 使い方

### 方法 A: シンボリックリンクで共有（推奨）

複数プロジェクトで設定を共有し、一括更新できる方法。

#### 1. テンプレートを配置

```bash
# Dropbox や共有フォルダに配置
git clone https://github.com/kimny1143/claude-code-template.git ~/Dropbox/_DevProjects/claude-code-template
```

#### 2. セットアップスクリプトを実行

```bash
cd /path/to/your/project

# スクリプトをダウンロード（初回のみ）
curl -o setup-claude.sh https://raw.githubusercontent.com/kimny1143/claude-code-template/main/setup.sh
chmod +x setup-claude.sh

# 実行
./setup-claude.sh
```

または手動で:
```bash
TEMPLATE=~/Dropbox/_DevProjects/claude-code-template/.claude
mkdir -p .claude/{commands,skills,agents,hooks}

# コマンドをリンク
ln -s $TEMPLATE/commands/commit.md .claude/commands/
ln -s $TEMPLATE/commands/pr.md .claude/commands/

# スキルをリンク
ln -s $TEMPLATE/skills/tdd .claude/skills/
ln -s $TEMPLATE/skills/coding-rules .claude/skills/
```

#### 3. プロジェクト固有設定を追加

```bash
# プロジェクト固有スキル（シンボリックリンクではなくディレクトリで作成）
mkdir -p .claude/skills/my-database
echo "# Database Skill" > .claude/skills/my-database/index.md
```

#### シンボリックリンク構成のイメージ

```
claude-code-template/          ← 共有設定の原本
├── .claude/
│   ├── commands/
│   │   ├── commit.md          ← 全プロジェクト共通
│   │   └── pr.md
│   └── skills/
│       ├── tdd/               ← 全プロジェクト共通
│       └── coding-rules/

your-project/.claude/
├── commands/
│   ├── commit.md → ~/...template/.claude/commands/commit.md  (symlink)
│   └── my-workflow.md         ← プロジェクト固有
└── skills/
    ├── tdd → ~/...template/.claude/skills/tdd  (symlink)
    └── database/              ← プロジェクト固有
```

#### 共有設定の更新

テンプレートを更新すると、全プロジェクトに自動反映:
```bash
cd ~/Dropbox/_DevProjects/claude-code-template
vim .claude/skills/tdd/index.md  # 編集
# → 全プロジェクトに即反映（シンボリックリンクのため）
```

---

### 方法 B: コピーで使用

独立した設定が必要な場合。

#### 1. このリポジトリをクローン

```bash
git clone https://github.com/kimny1143/claude-code-template.git
cd claude-code-template
```

#### 2. 既存プロジェクトにコピー

```bash
cp -r .claude/ /path/to/your/project/
cp CLAUDE.md.template /path/to/your/project/CLAUDE.md
```

#### 3. CLAUDE.md をカスタマイズ

`CLAUDE.md.template` を `CLAUDE.md` にリネームし、プロジェクト固有の情報を記入。

#### 4. Hooks を設定

`.claude/settings.local.json` のパスをプロジェクトに合わせて更新:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|Bash",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/your/project/.claude/hooks/validate-dangerous-ops.sh"
          }
        ]
      }
    ]
  }
}
```

## 構造

```
.claude/
├── commands/           # スラッシュコマンド
│   ├── commit.md
│   ├── pr.md
│   ├── build-fix.md
│   └── security.md
├── skills/             # 詳細ガイド
│   ├── tdd/
│   ├── backend-patterns/
│   ├── coding-rules/
│   ├── git-worktree/
│   ├── hooks/
│   └── mcp/
├── agents/             # サブエージェント定義
│   ├── code-reviewer.md
│   ├── security-reviewer.md
│   ├── codebase-optimizer.md
│   └── docs-curator.md
├── hooks/              # 自動実行スクリプト
│   ├── validate-dangerous-ops.sh
│   └── suggest-git-cleanup.sh
└── settings.local.json.example

CLAUDE.md.template      # プロジェクト説明テンプレート
```

## カスタマイズ

### プロジェクト固有のスキル追加

```bash
mkdir -p .claude/skills/your-skill
touch .claude/skills/your-skill/SKILL.md
```

### プロジェクト固有のコマンド追加

```bash
touch .claude/commands/your-command.md
```

### Hooks のカスタマイズ

`validate-dangerous-ops.sh` に独自の検証ルールを追加可能。

## 参考資料

- [Affaan Mustafa: Everything Claude Code](https://github.com/affaan-m/everything-claude-code)
- [Anthropic: Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Boris Cherny's Workflow](https://venturebeat.com/technology/the-creator-of-claude-code-just-revealed-his-workflow-and-developers-are)

## License

MIT
