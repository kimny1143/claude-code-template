# AGENTS.md — Codex adapter for claude-code-template

このワークスペースは Claude Code 主運用です。正本は `CLAUDE.md` です。

Codex等の副次利用で作業する場合も、まず `CLAUDE.md` を読んでください。ここは全peer共有templateの正本であり、`.claude/skills`, `.claude/hooks`, `.claude/agents`, `.claude/commands`, settings template, distribution scripts の変更は全peerへ波及し得ます。

## Codexでの扱い

- shared hooks / skills / agents / commands の変更は慎重に扱う
- 他peerワークスペースを直接変更しない
- 配布・同期・settings変更はdry-runまたはread-only確認を先に行う
- Claude Code向けの詳細運用はこのファイルに複製しない

詳細は `CLAUDE.md` と `docs/template-ops-runbook.md` を参照してください。
