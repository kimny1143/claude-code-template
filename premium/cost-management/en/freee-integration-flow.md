# freee Integration Flow — AI Team Cost Management Automation

## Overview

A flow for managing AI multi-agent team operational costs through integration with freee accounting software. Minimizes manual data entry and automates cost visibility.

---

## Prerequisites

- freee accounting account (corporate or sole proprietor)
- freee MCP server (`freee-mcp`) set up and running
- freee division (accounting instance) operational

---

## Integration Architecture

```
Each division's API usage
  │
  ├─ End-of-month cost audit → Each division reports
  │
  ├─ freee division aggregates
  │   ├─ Categorize API costs into freee expense categories
  │   ├─ Fixed costs: auto-journalize (same amount monthly)
  │   └─ Variable costs: manual review, then journalize
  │
  ├─ Register journal entries via freee API
  │   ├─ freee_api_post: /api/1/deals (create transaction)
  │   └─ freee_api_get: /api/1/deals (verify)
  │
  └─ Generate monthly report → Report to conductor
```

---

## freee Account Mapping

Primary costs in AI team operations and their corresponding freee account categories:

| Cost Item | freee Account | Sub-Account (recommended) | Notes |
|-----------|--------------|--------------------------|-------|
| Claude Code Max | Communication Expense or Service Fees | AI Infrastructure | Monthly fixed. Largest cost item |
| External APIs (Anthropic, OpenAI, etc.) | Service Fees | API Usage | Usage-based. Watch FX rates for USD billing |
| SaaS Subscriptions (freee, Google One, etc.) | Communication Expense | SaaS Usage | Monthly fixed |
| Domain Costs | Communication Expense | Domain | Annual, prorate monthly |
| Apple Developer Program | Service Fees | App Development | Annual, prorate monthly |
| Hosting (Vercel Pro, etc.) | Communication Expense | Hosting | Starts when free tier is exceeded |
| Video Generation API (fal.ai, Runway, etc.) | Service Fees | Video Production | Usage-based |

### Sub-Account Design Guidelines

- **Don't use division names as sub-accounts** — Categorize by "what it was used for" (more useful for tax purposes)
- **Categorize by usage** — Four categories suffice: "AI Infrastructure", "API Usage", "SaaS", "Hosting"
- **Extend as needed** — Add sub-accounts when new cost types emerge

---

## Monthly Flow

### Week 1 (Start of Month): Finalize Previous Month's Costs

```
1. Check each API dashboard for previous month's usage
   - Anthropic Console → Usage
   - OpenAI Dashboard → Usage
   - fal.ai Dashboard → Billing
   - Each SaaS → Invoices/Receipts

2. Reconcile with credit card statement

3. freee division registers journal entries via freee API
```

#### freee API Transaction Registration Example

```
freee_api_post /api/1/deals
{
  "company_id": [company_id],
  "issue_date": "2026-03-01",
  "type": "expense",
  "details": [
    {
      "account_item_id": [communication_expense_id],
      "tax_code": 2,
      "amount": 30000,
      "description": "Claude Code Max February 2026"
    }
  ],
  "partner_id": [anthropic_partner_id]
}
```

### Week 2-3: Normal Operations

- No special tasks
- Investigate if variable cost anomaly alerts trigger

### Week 4 (End of Month): Cost Audit

```
1. Conductor requests cost reports from all divisions via patrol
2. Each division fills out the survey sheet
3. freee division aggregates → generates monthly cost report
4. Conductor → CEO report
```

---

## Quarterly Flow

### Conducting the Audit

1. **Distribute survey sheets** (using API Cost Inventory Template)
2. **Collect from all divisions** (1-week response deadline)
3. **freee division aggregates**
4. **Generate quarterly comparison report**
5. **Cost optimization proposals**

### Reconciliation with freee Reports

```
freee_api_get /api/1/reports/trial_pl
{
  "company_id": [company_id],
  "fiscal_year": 2026,
  "start_month": 1,
  "end_month": 3
}
```

Verify that the quarterly P&L report's "Communication Expense" and "Service Fees" actuals match the division-by-division aggregated totals.

---

## USD-Denominated Cost Handling

### Applicable Services

- Anthropic API (USD)
- OpenAI API (USD)
- Apple Developer Program (USD)
- fal.ai (USD)
- Vercel (USD)

### Processing Method

1. Use the **exchange rate at credit card settlement date**
2. Do not use freee's "foreign currency transaction" feature — record the **JPY settlement amount** from the card statement
3. FX gains/losses are adjusted annually (ignore at monthly level)

### Notes

- Card statement JPY amount ≠ API dashboard USD amount × spot rate
- If discrepancy is large (>5%), verify the card issuer's exchange rate

---

## Alert Design

### Automated Alerts (recommended)

| Condition | Alert Recipient | Action |
|-----------|----------------|--------|
| Variable costs exceed 150% MoM | Conductor + freee division | Root cause investigation |
| Free tier utilization exceeds 90% | Affected division + freee division | Plan paid tier transition |
| New service cost appears | freee division | Confirm account mapping |
| Total monthly cost exceeds budget | Conductor + CEO | Emergency cost review |

### Implementation

- Set Usage Alerts on each API (where supported)
- Conductor checks twice per month during patrol
- freee division reports anomalies in monthly report

---

## Applying to Your Team

### Step 1: Prepare freee Accounting

- Add sub-accounts (AI Infrastructure, API Usage, SaaS, Hosting)
- Register each service provider in the partner master

### Step 2: Set Up freee MCP

```bash
# freee-mcp setup (see separate README)
npx skills add freee/freee-mcp
```

### Step 3: Deploy Accounting Instance

- Dedicate a freee division, or have the conductor handle it
- Grant freee API operation permissions in CLAUDE.md

### Step 4: Run the Flow

- First month: manually execute the full flow for validation
- Second month: automate routine portions
- Quarterly: start the audit cycle
