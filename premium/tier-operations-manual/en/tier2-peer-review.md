# Tier 2: Peer Review Operations Guide

## Eligible Changes

- All code changes that don't match Tier 3 criteria
- Component additions/modifications
- Utility function additions/modifications
- Style changes (CSS/Tailwind)
- Configuration file changes (`.gitignore`, `tsconfig.json`, etc.)
- Dependency updates (security patches, etc.)
- Refactoring

## How Peer Review Works

### Choosing Review Partners

Assign a different division within the same department as the mutual review partner.

**Design rationale:**
- Same department means shared understanding of the codebase
- Different division avoids "reviewing your own code" problem
- Mutual pairing ensures balanced workload

**Example (glasswerks AI Room):**

| Self | Review Partner | Rationale |
|------|---------------|-----------|
| mued | native | Same Product dept. Shared tech stack (React) |
| native | mued | Same as above |
| SNS | write | Same Marketing dept. Upstream/downstream in content distribution |
| write | SNS | Same as above |
| video | SNS | Marketing dept. Video distribution targets SNS |
| LP | mued | Shared frontend technology |
| data | mued | Data analysis targets mued |
| freee | LP | Corporate dept. mutual pair |

### Applying to Your Team

1. Group divisions by department
2. Pair divisions within each department (use 3-way rotation for odd numbers)
3. Single-division departments pair with the closest tech stack in another department

## Peer Review Procedure

### Requester Side (PR Author)

#### 1. Create the PR

```bash
gh pr create --title "[peer-review: native] feat: add search component" \
  --body "## Summary
- Added search component
- Includes debounce handling

## Test plan
- [ ] API is called on search input
- [ ] Debounce is working correctly"
```

#### 2. Send Review Request to Peer Division

Contact directly via claude-peers:

```
[mued → native: Review Request]
PR: https://github.com/xxx/xxx/pull/42
Summary: Search component addition (Tier 2)
Focus area: Is debounce timing appropriate?
```

#### 3. Address Feedback

- Address any feedback from the peer
- Notify the peer again after making changes

### Reviewer Side (Peer Division)

#### 1. Receive Review Notification

Receive the request via claude-peers message.

#### 2. Conduct Review

**Checklist:**

- [ ] Change is within Tier 2 scope (doesn't qualify for Tier 3)
- [ ] All CI checks pass
- [ ] Code follows existing patterns
- [ ] No obvious bugs or security issues
- [ ] Tests have been added/updated

**Review depth:**
- No need to read every line
- Check for "issues obvious to an outside reviewer"
- Escalate to Tier 3 if architectural discussion is needed

#### 3. Approve or Provide Feedback

```
[native → mued: Review Complete]
PR #42: Approved. OK to merge.
```

Or:

```
[native → mued: Review Feedback]
PR #42: Debounce timing is 300ms, but considering the search API response time, 500ms might be safer. Please review.
```

#### 4. Merge

After approval, the PR author merges:

```bash
gh pr merge 42 --squash
```

## Time Estimates

| PR Size | Review Time | Examples |
|---------|------------|---------|
| Small (~50 lines) | 1-2 min | Function addition, style fix |
| Medium (50-200 lines) | 3-5 min | Component addition |
| Large (200+ lines) | 5-10 min | Feature addition, refactoring |

**PRs that are too large should be considered for Tier 3 escalation.** PRs over 200 lines should also be considered for splitting.

## Escalation

Escalate to Tier 3 during peer review if:

- A security risk is discovered during review
- The change's impact exceeds Tier 2 expectations
- Peers disagree on the judgment
- Review would take more than 30 minutes due to complexity
