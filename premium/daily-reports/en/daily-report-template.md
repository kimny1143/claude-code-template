# Daily Report Template — glasswerks AI Room

## Format

```markdown
# Daily Report: {課名} — {YYYY-MM-DD}

## Today's Summary
<!-- 1-2 sentences: what was the main focus today? -->

## Completed
<!-- Bullet list of completed work items -->
-

## PRs
| PR | Status | Tier | Description |
|----|--------|------|-------------|
|    |        |      |             |

- PRs created:
- PRs merged:
- PRs pending review:

## Blockers
<!-- Things preventing progress. "None" if clear. -->
-

## API / Cost
<!-- Token usage, API calls, or other measurable costs -->
| Model | Input tokens | Output tokens | Est. cost |
|-------|-------------|---------------|-----------|
|       |             |               |           |

Total estimated cost today: $

## Tomorrow's Plan
<!-- 1-3 items for next session -->
1.

## Notes
<!-- Anything not captured above: decisions made, context for future sessions, etc. -->
```

---

## Usage Guide

### Who fills this out?

Each 課 (department) fills out one daily report per active session. The conductor課 aggregates these into a summary for the human operator.

### When to write it

Write the report at the **end of each session**, before signing off. If a session spans multiple days, write one report per calendar day.

### Key principles

1. **Be specific, not vague.** "Implemented user auth flow" > "Worked on auth."
2. **Include PR numbers.** This is the primary audit trail.
3. **Tier matters.** Always note the Tier level (1/2/3) for each PR — this determines the review workflow.
4. **Cost tracking is non-optional.** Even rough estimates help. If you can't measure tokens, note the number of tool calls or API requests.
5. **Blockers should name the blocking party.** "Waiting on mued課 for API schema" > "Blocked."
6. **Tomorrow's Plan is a commitment.** The conductor uses this to allocate priorities.

### Aggregation by conductor課

The conductor課 collects all daily reports and produces:
- A **daily digest** (cross-department summary, total cost, blockers)
- A **weekly rollup** (trends, velocity, cost trajectory)

Reports can be submitted via claude-peers message or committed to the repo.
