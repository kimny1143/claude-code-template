# MCP Agent Design Guide

> Design, placement, and operational patterns for MCP servers in multi-agent teams.
> For basic MCP server creation, see the free `mcp` skill. This guide focuses on **team-specific design decisions**.

---

## 1. MCP Placement Levels

In multi-agent environments, the placement level is the starting point of MCP design.

| Level | Config Location | Shared Scope | Example |
|-------|----------------|-------------|---------|
| **Global** | `~/.claude.json` | All projects, all agents | claude-peers (inter-agent comms) |
| **Project** | `.claude/settings.local.json` | All sessions in that project | freee-mcp (accounting API) |
| **Session** | Startup flags | Single session only | Temporary debug MCPs |

### Decision Flow

```
Will this MCP be used across multiple projects?
├── YES → Global (~/.claude.json)
└── NO
    └── Persistent across multiple sessions?
        ├── YES → Project level (settings.local.json)
        └── NO → Session level (add at startup)
```

### Registering a Global MCP

```bash
claude mcp add --scope user <mcp-name> -- <command> <args>
```

Written to `~/.claude.json`, auto-loaded in all projects.

### Registering a Project MCP

```bash
claude mcp add --scope project <mcp-name> -- <command> <args>
```

Written to `.claude/settings.local.json`.

---

## 2. MCP Categories and Design Patterns

### Pattern A: Infrastructure MCP (All Agents)

**Characteristics:** Team-wide foundation used by every agent. Global placement.

**Example:** claude-peers (inter-instance communication)

```json
// ~/.claude.json
{
  "mcpServers": {
    "claude-peers": {
      "type": "stdio",
      "command": "bun",
      "args": ["run", "/path/to/claude-peers-mcp/src/index.ts"]
    }
  }
}
```

**Design Points:**
- If startup flags are required (e.g., `--dangerously-load-development-channels`), use shell aliases
- All agents share the same version — updates require restarting all sessions
- Failure affects all agents → conductor owns maintenance responsibility

### Pattern B: Domain MCP (Department-Specific)

**Characteristics:** Handles domain-specific APIs. Placed only in relevant projects.

**Example:** freee-mcp (accounting API), Stripe MCP

```json
// .claude/settings.local.json (accounting dept project)
{
  "mcpServers": {
    "freee-mcp": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@anthropic-ai/freee-mcp"]
    }
  }
}
```

**Design Points:**
- API keys managed in project `.env.local` (see Section 3)
- If other departments need temporary access, add at session level
- Department ownership = MCP management responsibility

### Pattern C: Tool MCP (Capability Provider)

**Characteristics:** Provides general capabilities like image generation or search. Departments add individually as needed.

**Example:** nano-banana-pro (Gemini image generation)

```bash
# launch.sh for API key injection
#!/bin/bash
source "$(pwd)/.env.local" 2>/dev/null
GEMINI_API_KEY="${GEMINI_API_KEY}" npx -y @anthropic-ai/nano-banana-pro
```

**Design Points:**
- To isolate billing accounts, use different API keys per department via `.env.local`
- Use `launch.sh` wrapper pattern for environment variable injection
- Align API dashboard project granularity for usage auditing

---

## 3. API Key Management

### Principle: Isolate Per Project

```
your-project/
├── .env.local          ← API keys here (.gitignore'd)
├── .claude/
│   └── settings.local.json
└── launch.sh           ← Reads .env.local and starts MCP
```

**Why Not Centralize:**
- Enables per-project usage tracking in API dashboards
- Clear cost allocation per department
- Limits blast radius if a key is compromised

### launch.sh Pattern

```bash
#!/bin/bash
# MCP startup wrapper — reads API keys from cwd's .env.local
set -euo pipefail

ENV_FILE="$(pwd)/.env.local"
if [[ -f "$ENV_FILE" ]]; then
  source "$ENV_FILE"
fi

# Check required keys
if [[ -z "${GEMINI_API_KEY:-}" ]]; then
  echo "ERROR: GEMINI_API_KEY not set in .env.local" >&2
  exit 1
fi

export GEMINI_API_KEY
exec npx -y @anthropic-ai/nano-banana-pro "$@"
```

### Referencing in settings.local.json

```json
{
  "mcpServers": {
    "nano-banana-pro": {
      "type": "stdio",
      "command": "bash",
      "args": ["/path/to/claude-code-template/mcps/nano-banana-pro/launch.sh"]
    }
  }
}
```

---

## 4. Permission Design (allow / deny)

Control MCP tool access via `permissions` in `settings.local.json`.

### Per-Department Permission Example

```json
{
  "permissions": {
    "allow": [
      "mcp__claude-peers__list_peers",
      "mcp__claude-peers__send_message",
      "mcp__claude-peers__set_summary",
      "mcp__claude-peers__check_messages",
      "mcp__freee-mcp__freee_api_get",
      "mcp__freee-mcp__freee_api_list_paths"
    ],
    "deny": [
      "mcp__freee-mcp__freee_clear_auth"
    ]
  }
}
```

### Design Principles

| Principle | Description |
|-----------|-------------|
| **Least privilege** | Each department only allows the MCP tools it needs |
| **Deny destructive ops** | Explicitly deny `clear_auth`, `delete`, `drop` operations |
| **Allow comms for all** | claude-peers' 4 tools are universally allowed |
| **Preserve dept-specific config** | Template distribution must not overwrite department-specific allow/deny |

### Distribution Caution

When distributing via `scripts/distribute-settings.sh`:

```bash
# Preserve department-specific deny settings while updating common sections
# ❌ cp settings.local.json.example → dept-specific config lost
# ✅ jq merge → dept-specific config preserved
jq -s '.[0] * .[1]' base.json project-specific.json > merged.json
```

---

## 5. Hook Integration

Pair MCP tool invocations with hooks for enhanced safety.

### PreToolUse Hook to Guard MCP Operations

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__freee-mcp__freee_api_delete|mcp__freee-mcp__freee_api_put",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/confirm-freee-write.sh"
          }
        ]
      }
    ]
  }
}
```

```bash
#!/bin/bash
# confirm-freee-write.sh — warn on freee write operations
echo "⚠️ This is a write operation to the freee API. Production data will be affected."
echo "WARN: Consider getting approval before proceeding"
```

### Pattern: Audit Logging

```bash
#!/bin/bash
# audit-mcp-calls.sh — log MCP tool invocations
TOOL_NAME="$1"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "${TIMESTAMP} | ${TOOL_NAME}" >> ~/.claude/logs/mcp-audit.log
```

---

## 6. Custom MCP Design Checklist

Use this checklist when building custom MCP servers for your team.

### Tool Design

- [ ] Tool names follow `verb_noun` format (`get_users`, `create_invoice`)
- [ ] Descriptions include trigger phrases users would say
- [ ] Read and write operations are separated
- [ ] Errors return structured messages (JSON preferred)
- [ ] Each tool has a single responsibility (no monolithic multi-function tools)

### Security

- [ ] API keys are not hardcoded (use env vars or .env.local)
- [ ] Destructive operations (delete, update, clear) are added to the deny list
- [ ] Input validation is implemented
- [ ] Rate limiting is considered

### Operations

- [ ] MCP owner (responsible department) is designated
- [ ] Placement level (global/project/session) is decided
- [ ] README added to template's `mcps/` directory
- [ ] Cross-department impact assessed (notify all departments for global MCPs)

### Testing

- [ ] Each tool tested individually
- [ ] No conflicts with other MCPs (tool name collisions, etc.)
- [ ] Error fallback behavior verified

---

## 7. Shared Resource Locking

When a resource can only be used by **one agent at a time** (e.g., browser extension), implement a locking mechanism.

### Operational Pattern

```
1. Requesting dept → Notify conductor: "[Resource] requesting access"
2. Conductor → Check lock status → Grant or queue
3. Requesting dept → Complete work → Notify: "[Resource] released"
4. Conductor → Release lock → Notify queued departments
```

### When to Apply

| Criteria | Example |
|----------|---------|
| Concurrent access causes conflicts | Chrome extension (tab operations collide) |
| Strict API rate limits | External API (5 req/min, etc.) |
| High per-call cost | Image generation API ($0.05/call, etc.) |

Standard MCPs (claude-peers, freee-mcp, etc.) support concurrent access and don't require locking.

---

## 8. MCP Lifecycle Management

### Introduction Flow

```
1. Requirements — What problem does it solve? Can existing tools substitute?
2. Prototype — Verify with minimal tool set
3. Tier 3 Review — New external service = conductor review required
4. Template Addition — Create mcps/<name>/README.md
5. Distribution — Notify relevant departments of settings.local.json updates
6. Operations — Owner department holds management responsibility
```

### Updates and Deprecation

- **Updates:** When bumping package versions, notify based on scope (global = all departments)
- **Deprecation:** Confirm no departments are actively using it before removal. Place `DEPRECATED.md` in `mcps/<name>/` with a grace period

### Version Tracking

Track MCP versions similar to `skills-lock.json`:

```json
{
  "mcps": {
    "claude-peers": {
      "source": "~/claude-peers-mcp",
      "version": "git:abc1234",
      "scope": "global",
      "owner": "template dept"
    },
    "freee-mcp": {
      "source": "npm:@anthropic-ai/freee-mcp",
      "version": "0.3.1",
      "scope": "project",
      "owner": "accounting dept"
    }
  }
}
```

---

## Appendix: Real Configuration Sample (10-Department Setup)

| MCP | Level | Owner | Purpose |
|-----|-------|-------|---------|
| claude-peers | Global | template dept | Real-time inter-department communication |
| claude-history | Project | template dept | Conversation history search |
| nano-banana-pro | Project | template dept | Gemini image generation |
| freee-mcp | Project | accounting dept | Accounting & HR APIs |
| claude-in-chrome | Global | template dept | Browser automation (exclusive lock) |

### Distribution Template Structure

```
claude-code-template/
├── mcps/
│   ├── claude-peers/
│   │   └── README.md       ← Setup instructions
│   ├── claude-history/
│   │   └── README.md
│   └── nano-banana-pro/
│       ├── README.md
│       └── launch.sh       ← API key injection wrapper
```

The template's `mcps/` directory serves as **setup instruction hub** — it does not include MCP server source code. Server code lives in npm packages or separate repositories.
