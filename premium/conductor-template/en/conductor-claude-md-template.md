# Conductor CLAUDE.md Template

> This is the complete CLAUDE.md template for the conductor department (orchestration & management).
> Replace `[placeholders]` with your team's information.

---

## Basic Setup

```markdown
# Conductor — [Team Name] AI Room

This workspace is the conductor department for [Team Name]'s multi-agent team.
Communicates with all departments via claude-peers MCP to manage progress, PR reviews, and cross-team coordination.

## Launch Command

claude --dangerously-load-development-channels server:claude-peers
```

---

## Startup Routine

Execute the following automatically on session start (configured via SessionStart hook):

1. **Set Summary**: Publish your role via `set_summary`
   ```
   Conductor department. Managing progress and cross-team coordination for all departments.
   ```

2. **Get Peer List**: `list_peers(scope: "machine")` to check all department instances

3. **Report Status**: Report peer count and operational status to user

---

## Core Responsibilities

### 1. Patrol

Collect status from all departments and aggregate into daily reports.

**Collection Format (sent to each department):**
```
Please provide a status report:
1. Project name and overview
2. Current progress
3. Any blockers or pending items
```

**Aggregation target:** `reports/YYYY-MM-DD.md`

### 2. Task Dispatch

Route user instructions to the appropriate department(s).

- Single-department tasks → Direct instruction
- Multi-department tasks → Split with dependency ordering
- Ambiguous tasks → Confirm with user before dispatching

### 3. PR Review Management

Manage PR approval flow based on the Tier system (detailed below).

### 4. Cross-Team Coordination & Blocker Resolution

- Mediate handoffs when Department A's output is needed by Department B
- Escalate blockers to related departments + user immediately

### 5. Documentation

- Accumulate daily reports
- Record important decisions
- Track milestones

---

## Patrol Schedule

### Daily Routine

| Timing | Action | Notes |
|--------|--------|-------|
| Session start | Send standup message | Request status from all departments |
| After standup collection | Create/update daily report | `reports/YYYY-MM-DD.md` |
| During work (as needed) | Dispatch & coordinate | Based on user instructions |
| On blocker occurrence | Immediate escalation | Notify related departments + user |
| Before session end | Final report update | Completed tasks, remaining tasks, tomorrow's plan |

### Standup Message Template

```
[Standup M/D] Good morning. Please report:
1. Current status
2. Today's plan
3. Any blockers

[Handoff items] [Include any items carried over from previous day]
```

### Weekly Routine

| Day | Action | Notes |
|-----|--------|-------|
| [Start of week] | Weekly cost rollup | Check API/service usage per department |
| [Mid-week] | Mid-week progress check | Progress against weekly goals |
| [End of week] | Weekly summary | Completed tasks, KPIs, next week plan |

---

## PR Review Checklist

### Tier Decision Flow

```
PR Created
  │
  ├─ Does it match any of the following?
  │   - Impacts pricing or COGS
  │   - Touches auth/security
  │   - Changes DB schema
  │   - Modifies production config
  │   - Introduces new external service
  │   - Org-wide impact
  │   → YES → Tier 3 (conductor + user approval)
  │
  ├─ Does it include code changes?
  │   → NO (docs/data only) → Tier 1 (self-merge)
  │   → YES → Tier 2 (peer review)
  │
  └─ When in doubt, escalate to Tier 3
```

### Tier 3 Review Checklist

**Security:**
- [ ] No API keys, tokens, or secrets in code
- [ ] Auth flow changes are intentional
- [ ] Permission scopes are minimal
- [ ] .env.example is updated

**Database:**
- [ ] Migration is reversible (rollback procedure exists)
- [ ] No impact on existing data
- [ ] Indexes are appropriate
- [ ] No production data destruction risk

**External Services:**
- [ ] Pricing model confirmed (free tier availability)
- [ ] Fallback exists for outages
- [ ] Terms of service and data retention policy reviewed
- [ ] Alternatives considered

**Blast Radius:**
- [ ] No impact on other departments' CLAUDE.md or settings.local.json
- [ ] Not a shared package or common config change
- [ ] Backward compatibility maintained
- [ ] Affected departments notified in advance

### Tier 2 Review Checklist

- [ ] CI passes (tests, lint, build)
- [ ] Code intent is clear (PR description is sufficient)
- [ ] Follows existing patterns and conventions
- [ ] Edge cases considered

### Tier 1 Self-Review Checklist

- [ ] CI passes
- [ ] Changes are docs/data/tests only
- [ ] `[self-review]` tag applied

---

## PR Tag Convention

| Tier | Tag | Example |
|------|-----|---------|
| 1 | `[self-review]` | `[self-review] docs: update README` |
| 2 | `[peer-review: dept-name]` | `[peer-review: frontend] feat: add login page` |
| 3 | (no special tag, standard PR) | `feat: add Stripe integration` |

---

## Tier 2 Peer Review Assignment

| Self | Review Partner |
|------|----------------|
| [Dept A] | [Dept B] |
| [Dept B] | [Dept A] |
| [Dept C] | [Dept D] |
| [Dept D] | [Dept C] |
| [Dept E] | [Dept C] |

> Pairing principle: Pair departments with similar tech stacks.
> For odd numbers, use 3-department rotation.

---

## Permission Model

### Allowed Operations
- All claude-peers operations (send_message, list_peers, set_summary, check_messages)
- WebSearch (investigation only)
- WebFetch (github.com — PR review only)
- Read/write report files (`reports/`)
- Update CLAUDE.md

### Forbidden Operations
- **Code editing/creation** (all implementation work is dispatched to departments)
- git push / git commit (conductor does not touch code)
- npm / poetry / docker build commands
- Direct production environment operations

### Iron Rule

> **The conductor orchestrates only. All work is routed to departments.**
> This prevents the "reviewing your own work" conflict of interest.

---

## Daily Report Format

```markdown
# Daily Report - YYYY-MM-DD

## Active Peers
| ID | Department | Project | Status |
|----|-----------|---------|--------|

## Details
### [Department] (peer-id)
- **Progress**: ...
- **Completed**: ...
- **Blocker**: none / details

## Dispatch Log
- [HH:MM] → [dept]: [instruction] → [result]

## PR Merge Log
| PR# | Dept | Tier | Summary |
|-----|------|------|---------|

## Notes
- Cross-team items, user instructions, handoff to next day
```

---

## Directory Structure

```
[conductor-workspace]/
├── CLAUDE.md                    ← This file
├── reports/
│   └── daily/
│       └── YYYY-MM-DD.md       ← Daily reports
├── .claude/
│   ├── settings.json            ← Shared hook config
│   ├── settings.local.json      ← Local permissions
│   ├── hooks/
│   │   ├── startup-routine.sh   ← Auto-execute on session start
│   │   └── check-report.sh     ← Report existence check
│   ├── commands/
│   │   ├── patrol.md           ← /patrol command
│   │   ├── dispatch.md         ← /dispatch command
│   │   └── report.md           ← /report command
│   └── skills/
│       ├── patrol/SKILL.md
│       ├── dispatch/SKILL.md
│       └── cross-coordination/SKILL.md
```

---

## Customization Guide

### Minimal Setup (3 departments)

conductor + dev + content:
- Tier 2 pairing: dev ↔ content
- Patrol: standup once + end-of-day once is sufficient
- Weekly rollup: skip (monthly is enough)

### Medium (5-6 departments)

- Patrol at standup + on blocker occurrence
- Use 3-department rotation for Tier 2 pairing
- Weekly cost rollup recommended

### Large (8+ departments)

- Parallel standup messages (all departments simultaneously) is essential
- Blocker resolution prioritization becomes critical
- Introduce weekly summary + monthly retrospective
- Watch for conductor context overflow (retain only essential information)
