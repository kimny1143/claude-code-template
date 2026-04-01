# Organization Chart Template — AI Multi-Agent Team

Customize this template for your project.

---

## Basic Information

**Team Name**: [Your team name]
**Owner**: [Your name / organization]
**Number of Instances**: [N] divisions
**Monthly Cost**: $[XXXXX]

---

## Organization Structure

A self-operating team of Claude Code instances. Each division has its own workspace, with a conductor overseeing the entire organization.

---

## Departments & Divisions

### [Department A] (e.g., Executive)

| Division | Workspace | Scope |
|----------|-----------|-------|
| [Division name] | `[directory]` | [Description of responsibilities] |

### [Department B] (e.g., Product)

| Division | Workspace | Scope |
|----------|-----------|-------|
| [Division name] | `[directory]` | [Description of responsibilities] |
| [Division name] | `[directory]` | [Description of responsibilities] |

### [Department C] (e.g., Marketing)

| Division | Workspace | Scope |
|----------|-----------|-------|
| [Division name] | `[directory]` | [Description of responsibilities] |

---

## Communication Rules

- **Direct peer communication**: [OK / Requires conductor relay]
- **Reporting obligations**: [On patrol / Daily / Real-time]
- **When blocked**: [CC conductor + related divisions]
- **PR submission**: [Review flow]

---

## PR Review Tier System

### Tier 2 Review Assignments

| Self | Review Partner |
|------|---------------|
| [Division A] | [Division B] |
| [Division B] | [Division A] |

---

## Guardrails

1. **Policy**: Branch Protection Policy + Work Continuation Policy in shared CLAUDE.md
2. **Local**: pre-push hook (block-main-push.sh) prevents direct push to main
3. **Remote**: GitHub Rulesets (PR required, repo owner bypass)

---

## Operating Principles

1. [Principle 1: e.g., 33% cost ratio: universal pricing standard across all products]
2. [Principle 2: e.g., Don't do what you can't measure]
3. [Principle 3: e.g., Never stop working without explicit user instruction]

---

# Customization Guide

## Deciding the Number of Divisions

### Recommended Patterns

| Team Size | Divisions | Example Setup |
|-----------|-----------|---------------|
| **Minimal (solo developer)** | 3 | conductor + app + content |
| **Standard (small team)** | 5-6 | conductor + frontend + backend + content + infra |
| **Full (organizational)** | 8-12 | glasswerks pattern (10 divisions + extensions) |

### When to Add Divisions

- A single division exceeds 10+ PRs per week → consider splitting
- One division handles two different tech stacks → split
- Review queue becomes a bottleneck → split for parallel processing

### When to Consolidate Divisions

- A division produces only 1-2 PRs per week → consider merging
- Two divisions share the same tech stack → merge
- Communication overhead exceeds productivity gains → merge

## Department Grouping

### By Function (recommended)

```
Executive: conductor
Product: frontend, backend, mobile
Marketing: SNS, content
Corporate: LP, accounting
```

### By Project

```
Project A: frontend, backend
Project B: app
Shared: conductor, infra
```

## Designing the Conductor Division

The conductor division is mandatory. It handles:

1. **Patrol**: Periodically check all divisions' status
2. **Task dispatch**: Assign new tasks to appropriate divisions
3. **PR review**: Review Tier 3 PRs
4. **Cross-division coordination**: Resolve dependencies and blockers between divisions
5. **Reporting**: Daily/weekly progress summaries

### Conductor CLAUDE.md Must Include

- Complete list of all division workspaces
- Patrol schedule and procedures
- PR review checklists
- Escalation criteria

## Setting Up Tier 2 Pairs

### 2-Division Pairs (default)

```
A ←→ B
C ←→ D
```

### 3-Division Rotation (for odd numbers)

```
A → requests review from B
B → requests review from C
C → requests review from A
```

### Single-Division Departments (no pair available)

Pair with the closest tech stack from another department.
