# Tier 1: Self-Review Operations Guide

## Eligible Changes

- Documentation additions/edits (`.md` files)
- Data file updates (JSON, CSV, YAML configuration data)
- Copy changes (UI text changes only)
- Test additions (no changes to existing code)
- Comment/JSDoc additions and edits

## Ineligible Changes (Escalate to Tier 2+)

- Test modifications (changing existing test logic counts as "code change")
- Documentation + code changes bundled together (code portion makes it Tier 2)
- CI/CD pipeline configuration changes (Tier 3)
- `.env.example` changes (adding environment variables may require Tier 3)

## Self-Review Procedure

### 1. Confirm All CI Checks Pass

```bash
# Local checks
npm run lint        # or turbo run lint
npm run typecheck   # or turbo run typecheck
npm run test        # or turbo run test

# CI verification
gh pr checks <PR_NUMBER>
```

**If CI fails → no merge.** No exceptions, even for Tier 1.

### 2. Self-Review Checklist

After creating the PR, verify the following:

- [ ] Changes fall within Tier 1 scope
- [ ] No typos or errors
- [ ] No broken links (for documentation)
- [ ] No unnecessary files included
- [ ] No `.env` files or credentials included

### 3. Add Tag to PR Title

```
[self-review] docs: update API documentation
[self-review] test: add unit tests for UserService
```

### 4. Merge

```bash
gh pr merge <PR_NUMBER> --squash
```

### 5. Patrol Report

Report during the next conductor patrol:

```
Merged: #42 [Tier 1] docs: update README
```

## Common Judgment Mistakes

| Case | Wrong Call | Correct Call |
|------|-----------|-------------|
| Adding code examples to README | Tier 1 (it's documentation) | **Tier 1 is correct** (code examples are part of documentation) |
| Changing package.json description | Tier 1 (it's a text change) | **Tier 2** (package.json is code) |
| Adding `.gitignore` | Tier 1 (it's configuration) | **Tier 2** (changes repository behavior) |
| Updating test snapshots | Tier 1 (it's tests) | **Tier 2** (modifying existing tests) |
| Adding translation entries (i18n) | Tier 1 (it's copy) | **Tier 1 is correct** (UI text only) |
