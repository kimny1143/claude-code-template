# Tier 3: Conductor Review Operations Guide

## Eligible Changes

All PRs matching any of the following criteria are Tier 3:

| Criteria | Examples |
|----------|----------|
| **Affects pricing or cost ratios** | Stripe pricing changes, cost ratio parameter changes, plan restructuring |
| **Authentication/Security** | OAuth configuration, API key management, token handling, CORS settings, RLS changes |
| **DB schema changes** | Migration additions, table create/alter/drop, index changes |
| **Production environment settings** | Vercel environment variables, Cloudflare Workers config, GitHub Actions secrets |
| **New external service integration** | New API integrations, new SaaS adoption, new payment methods |
| **Org-wide impact changes** | Changes from the template division (setup.sh, shared skills, shared config) |

## Why Tier 3 Exists

Even with Tier 1/2 delegation, the changes above carry **extremely high cost of judgment errors**:

- Pricing mistakes → direct revenue impact
- Security holes → data breach risk
- DB schema corruption → service outage
- Template division changes → affects all divisions' behavior

These are protected by a double-check from the conductor (management instance) + CEO (human).

## Tier 3 PR Flow

```
Division creates PR
  │
  ├─ Notify conductor of PR URL via claude-peers
  │
  ├─ Conductor reviews
  │   ├─ All CI checks pass
  │   ├─ Change validity assessment
  │   ├─ Impact scope identification
  │   └─ Notify affected divisions (as needed)
  │
  ├─ Conductor approves or provides feedback
  │
  ├─ CEO (kimny) gives final approval
  │
  └─ Merge
```

### 1. PR Creation and Notification

```bash
# Create PR
gh pr create --title "feat: add Stripe webhook handler" \
  --body "## Summary
- Added Stripe Webhook endpoint
- Handles subscription.created / subscription.updated / subscription.deleted

## Tier 3 Reason
- New external service integration (Stripe Webhook)
- Authentication handling (webhook signature verification)

## Test plan
- [ ] Local testing with Stripe CLI
- [ ] Signature verification works correctly
- [ ] Each event is handled properly"
```

```
# Notify conductor via claude-peers
[mued → conductor: Tier 3 PR Submission]
PR: https://github.com/xxx/xxx/pull/55
Tier 3 reason: Stripe Webhook integration (external service + auth)
Focus area: Webhook signature verification implementation, error handling
```

### 2. Conductor Review Checklist

The conductor verifies the following:

#### Security
- [ ] No hardcoded credentials
- [ ] If new secrets are needed in `.env`, is `.env.example` updated?
- [ ] No API key or token exposure risk
- [ ] Input validation is adequate

#### Database
- [ ] Migration is reversible (rollback script exists)
- [ ] No impact on existing data
- [ ] Index performance implications considered

#### External Services
- [ ] Cost impact estimate provided
- [ ] Within free tier limits, or cost at overage identified
- [ ] Alternative services considered
- [ ] Fallback for service outages

#### Org-wide Impact (Template Division Changes)
- [ ] Backward compatible
- [ ] Impact scope for each division is clear
- [ ] Gradual rollout is possible

### 3. CEO Approval

After conductor approval, the CEO (kimny) performs final review:

- Review PR content (`gh pr view <number>`)
- Business validity assessment
- Merge approval

### 4. Post-Merge

- Conductor records in patrol report
- Notify affected divisions (all divisions for template changes)

## Tier 3 → Tier 2 Downgrade

The conductor may downgrade to Tier 2 if **all** conditions are met:

1. The change is trivial (typo-level configuration changes, etc.)
2. Impact scope is clearly limited
3. Change is reversible (can be reverted immediately)

Record downgrades in the patrol report as well.

## Emergency Response

### When a Hotfix Is Needed

1. Create PR + notify conductor with **[URGENT]** tag
2. Conductor reviews immediately
3. If CEO is unavailable: conductor approval is sufficient for merge (post-report required)

### When a Rollback Is Needed

1. Division that discovers the issue reports to conductor immediately
2. Conductor creates a revert PR
3. Revert PRs are Tier 3 but can be merged immediately as emergency
