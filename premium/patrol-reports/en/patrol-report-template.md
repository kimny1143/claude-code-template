# Patrol Report Template

> Template for the daily report created by the conductor during patrol.
> Aggregate information collected from all departments during standup into this format.

---

## Usage

1. Request status reports from all departments during standup
2. Collect responses and fill in the format below
3. Save to `reports/daily/YYYY-MM-DD.md`
4. Append events throughout the session (dispatches, PRs, blockers)
5. Final update before session end

---

```markdown
# Daily Report - YYYY-MM-DD

## Summary

- **Active departments**: ____ / [total]
- **Blockers**: yes / no
- **Merged PRs**: ____ count
- **Key achievement**: [one-line summary]

---

## Active Peers

| ID | Department | Project | Status |
|----|-----------|---------|--------|
| [peer-id] | [dept name] | [project name] | Active / Idle / Unresponsive |

---

## Department Details

### [Department Name] (peer-id)
- **Today's plan**: 
- **Progress**: 
- **Completed**: 
- **Blocker**: none / [details]
- **Handoff to tomorrow**: 

<!-- Repeat for each department -->

---

## Blocker List

| # | Dept | Description | Impact | Status | Owner |
|---|------|-------------|--------|--------|-------|
| 1 | [dept] | [blocker details] | [affected depts] | In progress / Resolved / Escalated | [owner] |

> If no blockers, write "No blockers today."

---

## Dispatch Log

| Time | Target | Instruction | Result |
|------|--------|------------|--------|
| [HH:MM] | [dept] | [instruction] | Done / In progress / On hold |

---

## PR Merge Log

| PR# | Dept | Tier | Summary | Review |
|-----|------|------|---------|--------|
| #[num] | [dept] | 1/2/3 | [summary] | self / [reviewer dept] / conductor |

---

## Cost & Anomalies

| Item | Details | Action |
|------|---------|--------|
| [API usage spike, etc.] | [details] | [response] |

> If no anomalies, write "No cost anomalies."

---

## Notes & Handoff

- [Cross-team coordination items]
- [User instruction log]
- [Handoff to next day]
- [Long-term items to remember]
```
