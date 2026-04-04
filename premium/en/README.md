# mued-claude-code-template Pro ($29)

The premium edition of mued-claude-code-template. Includes operational know-how documentation not available in the free public repository.

## What's Included in the Free Version (GitHub Public Repo)

- 37 skills, 7 commands, 6 agents, 4 hooks
- 3 MCP configuration templates
- setup.sh for automated distribution
- CLAUDE.md template

## What Pro Adds

### 1. Conductor CLAUDE.md — Complete Template (`conductor-template/en/`)

The full CLAUDE.md template for the conductor (orchestration) department. Everything needed to serve as the command center for a multi-agent team.

- `conductor-claude-md-template.md` — Patrol schedule, PR review checklists (4-axis per Tier), permission model, command definitions, daily report format, customization guide (3 to 10+ departments)

### 2. Tier System — Complete Operations Manual (`tier-operations-manual/en/`)

A 3-tier system that enables AI multi-agent teams to autonomously manage PR reviews.

- `overview.md` — System overview, design principles, implementation steps
- `tier1-self-review.md` — Scope, procedures, common judgment mistakes
- `tier2-peer-review.md` — Peer pairing design, request-to-approval flow, escalation criteria
- `tier3-conductor-review.md` — Review checklists, emergency response procedures

### 3. Patrol Reports (`patrol-reports/en/`)

Templates and samples for the conductor's daily patrol reports.

- `patrol-report-template.md` — Standard patrol report format
- `sample-patrol-normal.md` — Normal day sample (8 departments active, no blockers, 5 PRs)
- `sample-patrol-incident.md` — Incident day sample (2 blockers occurred and resolved, cost spike response)

### 4. Daily Report Template + 3-Day Samples (`daily-reports/en/`)

- `daily-report-template.md` — Report format for a 10-division structure
- `sample-day-1.md` through `sample-day-3.md` — Realistic examples from actual operations

### 5. Organization Chart Template + Design Decisions (`org-templates/en/`)

- `organization-chart-template.md` — How to decide division count, department grouping, conductor design
- `organization-chart-sample-filled.md` — **Filled sample**: Complete 10-department org chart (department list, Tier 2 pairings, guardrails, scaling history)
- `design-decisions.md` — Why this structure, how responsibility boundaries were set

### 6. Cost Management Template (`cost-management/en/`)

- `cost-tracking-template.md` — Monthly tracking, break-even calculation, quarterly audit procedure
- `cost-tracking-sample-filled.md` — **Filled sample**: Fixed/variable costs, composition analysis, break-even calculation, quarterly audit report
- `freee-integration-flow.md` — freee accounting integration, account mapping, USD/FX handling

---

All documents available in both Japanese (root directories) and English (`en/` subdirectories).

## Setup

1. Extract this zip
2. Confirm you've already cloned the free repo (mued-claude-code-template)
3. Use Pro documentation as reference to customize for your team structure
4. Add the Tier system decision flow to your CLAUDE.md (see `tier-operations-manual/en/overview.md`)
5. Set up your conductor department using the conductor CLAUDE.md template (see `conductor-template/en/`)

## Support

- Questions: free repo Issues on GitHub
- Pro-specific questions: Gumroad messaging
