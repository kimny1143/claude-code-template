# Tier System — Complete Operations Manual

## Introduction

This manual is the complete guide to the **3-tier review system** that enables multiple Claude Code instances (divisions) to autonomously manage PR reviews.

At glasswerks AI Room, we process 100+ PRs per month across a 10-division structure. Having the CEO review every PR is unrealistic. But giving AI instances unlimited merge permissions is too risky.

The Tier system resolves this contradiction.

---

## Tier System Overview

```
PR Created
  │
  ├─ Impact Assessment (run decision flow)
  │
  ├─ Tier 1: Self-Review → Self-Merge
  │   Scope: docs, data files, copy-only, test additions only
  │   Requirement: All CI checks pass
  │
  ├─ Tier 2: Peer Review → Merge after peer approval
  │   Scope: Code changes (not matching Tier 3 criteria)
  │   Requirement: All CI checks pass + designated peer division approval
  │
  └─ Tier 3: Conductor Review → Merge after CEO approval
      Scope: Security / DB / pricing / external services / org-wide impact
      Requirement: All CI checks pass + conductor approval + CEO approval
```

### Why Three Tiers?

- **Tier 1** prioritizes speed. No need to block everyone for a documentation fix
- **Tier 2** ensures quality. Code changes need a second pair of eyes, but not everything should bottleneck
- **Tier 3** is the safety valve. High-impact changes require caution

### Design Principles

1. **Default to Tier 3** — When in doubt, escalate to the safe side
2. **No merge without CI pass, regardless of tier** — Automated tests are the minimum gatekeeper
3. **Include in patrol reports** — All merges are tracked in the conductor's patrol reports

---

## Implementation Steps (Applying to Your Team)

### Step 1: Classify Your Divisions

List each instance (division) in your team and define:

| Decision | Description |
|----------|-------------|
| Division name | Role name for each instance |
| Workspace | Directory each division owns |
| Tier 2 peer | Partner division for mutual review |

**Choosing Tier 2 peers:**
- Same department, different division is optimal (close context)
- For odd numbers, use a 3-division rotation
- Never pair a division with itself (defeats the purpose)

### Step 2: Add the Decision Flow to CLAUDE.md

Add the following to each division's CLAUDE.md:

```markdown
## PR Review Permissions

### Decision Flow (run for every PR)

1. Does this change match any of the following?
   - Affects pricing or cost ratios
   - Touches authentication or security
   - Modifies DB schema
   - Changes production environment settings
   - Introduces a new external service
   - [Changes that affect all divisions]
   → YES → Tier 3

2. Does it include code changes?
   → NO → Tier 1
   → YES → Tier 2
```

### Step 3: Add the Tier 2 Peer Table

```markdown
### Tier 2 Review Assignments

| Self | Review Partner |
|------|---------------|
| Division A | Division B |
| Division B | Division A |
| Division C | Division D |
| Division D | Division C |
```

### Step 4: Set PR Tag Rules

| Tier | PR Tag | Example |
|------|--------|---------|
| Tier 1 | `[self-review]` | `[self-review] docs: update README` |
| Tier 2 | `[peer-review: {division}]` | `[peer-review: native] feat: add button component` |
| Tier 3 | (no tag, standard PR) | `feat: add Stripe webhook handler` |

### Step 5: Include in Patrol Reports

Include the following in the conductor's (or management instance's) patrol report:

```
## Merged PRs
| PR# | Tier | Division | Summary |
|-----|------|----------|---------|
| #42 | 1 | write | docs update |
| #43 | 2 | mued | add button component |
```
