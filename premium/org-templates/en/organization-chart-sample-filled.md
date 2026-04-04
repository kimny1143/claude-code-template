# Organization Chart — Filled Sample (10-Department Structure)

> This is a filled example of `organization-chart-template.md`.
> It models an actual 10-department AI multi-agent team in production.

---

## Basic Information

- **Team Name**: glasswerks AI Room
- **Owner**: Individual (solo operator)
- **Instances**: 11 (conductor + 10 departments)
- **Monthly Platform Cost**: ~$250 (Claude Code Max + infrastructure)

---

## Department List

### Management

| Department | Workspace | Responsibilities |
|-----------|-----------|-----------------|
| **conductor** | `_conductor/` | Progress management, PR review, cross-team coordination, standup facilitation, daily reports |

### Product (2 departments)

| Department | Workspace | Responsibilities | Tech Stack |
|-----------|-----------|-----------------|------------|
| **mued** | `mued/mued_v2/` | Web app development | Next.js 15, Drizzle ORM, Supabase, Stripe, GA4 |
| **native** | `mued/mued_v2/apps/` | Mobile app development | Expo, React Native |

### Marketing (4 departments)

| Department | Workspace | Responsibilities | Tech Stack |
|-----------|-----------|-----------------|------------|
| **sns** | `mued/threads-api/` | Social media automation, scheduling, analytics | Threads API, Instagram API |
| **write** | `_contents-writing/` | Article writing, copywriting | Markdown, note.com |
| **video** | `_videos/` | Video production (promos, tutorials) | Remotion, React |
| **lp** | `_LandingPage/glasswerks-lp/` | Landing pages, CRO | Vite, Vercel, GA4 |

### Operations (3 departments)

| Department | Workspace | Responsibilities | Tech Stack |
|-----------|-----------|-----------------|------------|
| **freee** | `freee-MCP/` | Accounting automation | freee API, MCP |
| **data** | `_data-analysis/` | GA4 analytics, conversion analysis, A/B testing | Python, GA4 API |
| **template** | `claude-code-template/` | Shared config management (skills/hooks/commands) | Shell, JSON |

---

## Communication Rules

| Rule | Details |
|------|---------|
| Inter-department | Direct messaging OK via claude-peers mesh |
| Status reports | Report to conductor during standup |
| Blockers | CC conductor + related departments |
| PR submission | Via conductor → owner approval → merge |

---

## Tier 2 Peer Review Assignment

| Self | Review Partner | Reason |
|------|----------------|--------|
| mued | native | Same product, similar tech stack |
| native | mued | Same as above |
| sns | write | Both content-focused |
| write | sns | Same as above |
| video | sns | Marketing cluster |
| lp | mued | Both frontend-focused |
| data | mued | Data ↔ product integration |
| freee | lp | Both highly independent |

---

## Guardrails

### 1. Policy (CLAUDE.md)

Shared CLAUDE.md across all departments includes:
- Branch Protection Policy (no direct push to main)
- Work Continuation Policy (continue until user instructs stop)
- Plan Mode Policy (Plan required for 3+ file changes)
- PR Review Permissions (Tier decision flow)

### 2. Local Hooks (settings.local.json)

| Hook | Target | Function |
|------|--------|----------|
| `block-main-push.sh` | PreToolUse:Bash | Block pushes to main branch |
| `validate-dangerous-ops-v2.sh` | PreToolUse:Bash/Write/Edit | Detect and warn on dangerous operations |
| `load-handoff-memory.sh` | SessionStart | Auto-load previous session handoff memory |

### 3. Remote Guardrails (GitHub)

| Setting | Details |
|---------|---------|
| Branch Protection | PR required for main |
| Required Reviews | Minimum 1 review |
| Status Checks | CI must pass |

---

## Operating Principles

1. **33% COGS Standard** — Target cost of goods sold at 33% or below for all products
2. **Main Product First** — Prioritize the free product with highest viral potential
3. **Mascot is Communication, Not Advertising** — Brand face, not ad vehicle
4. **What Isn't Measured Doesn't Exist** — GA4, conversion tracking, cost tracking on all activities
5. **Work Until User Says Stop** — Never self-terminate work sessions (Work Continuation Policy)

---

## Scaling History

### Phase 1: 3 Departments (Initial)
```
conductor → dev → content
```
- Single dev department for all development, single content department
- Frequent context window exhaustion

### Phase 2: 6 Departments (Growth)
```
conductor → mued, native, sns, write, lp
```
- Split product by tech stack
- Split marketing by content type

### Phase 3: 10 Departments (Current)
```
+ video, freee, data, template
```
- video: High token cost required isolation
- freee: Financial data access control
- data: Specialized analytics skills concentration
- template: Centralized management of org-wide changes

### Signals That Triggered Splits

| Signal | Response |
|--------|----------|
| Department PR count exceeded 10/week | Split department |
| CLAUDE.md exceeded 500 lines | Split responsibilities |
| Context reset made work resumption difficult | Narrow scope |
| Cost spike root cause hard to identify | Isolate high-cost work |
