# Cost Tracking Sheet — Filled Sample

> This is a filled example of `cost-tracking-template.md`.
> It models a fictional SaaS team "ExampleCorp" with a 10-department structure using realistic figures.

---

## Basic Information

- **Team Name**: ExampleCorp AI Room
- **Reporting Month**: March 2026
- **Departments**: 10 (including conductor)
- **Currency**: USD

---

## 1. Fixed Costs (Monthly)

| Service | Purpose | Monthly | Notes |
|---------|---------|---------|-------|
| Claude Code Max | AI agent platform for all departments | $200 | 5 accounts × $200 = $1,000 if scaled |
| Vercel Pro | Web app + LP hosting | $20 | 1 team plan |
| Supabase Pro | DB + Auth + Realtime | $25 | 1 project |
| GitHub Team | Repositories + Actions | $4/user | Free plan for individuals |
| Cloudflare | CDN + DNS | $0 | Within free tier |
| **Fixed Total** | | **$249** | |

---

## 2. Variable Costs (Monthly)

| Service | Purpose | This Month | Last Month | Change | Notes |
|---------|---------|------------|------------|--------|-------|
| OpenAI API | Summarization, classification | $12.40 | $8.20 | +51% | Video dept subtitle generation increase |
| Stripe | Payment processing fees | $18.60 | $15.30 | +22% | Proportional to transaction growth |
| Gumroad | Sales fees | $2.90 | $0 | New | Template sales started |
| Google Analytics | Analytics | $0 | $0 | - | Within free tier |
| **Variable Total** | | **$33.90** | **$23.50** | +44% | |

---

## 3. Monthly Total Cost

| Item | Amount |
|------|--------|
| Fixed costs | $249.00 |
| Variable costs | $33.90 |
| **Monthly total** | **$282.90** |

---

## 4. Cost Composition Analysis

| Service | Amount | Share | Alert |
|---------|--------|-------|-------|
| Claude Code Max | $200 | 70.7% | :warning: Concentration >60% |
| Supabase Pro | $25 | 8.8% | |
| Vercel Pro | $20 | 7.1% | |
| Stripe fees | $18.60 | 6.6% | |
| OpenAI API | $12.40 | 4.4% | |
| Gumroad fees | $2.90 | 1.0% | |
| Other | $4.00 | 1.4% | |

**Analysis**: Claude Code Max accounts for 70% of all costs. Essential as the AI agent platform, but cost comparison with direct API usage should be conducted quarterly.

---

## 5. Break-Even Calculation

### Product Mix

| Product | Price | COGS % | Gross Margin | Payment Fee | Net Margin |
|---------|-------|--------|-------------|-------------|------------|
| SaaS Plan A (monthly) | $9.99 | 33% | $6.69 | $0.60 | $6.09 |
| SaaS Plan B (monthly) | $29.99 | 33% | $20.09 | $1.20 | $18.89 |
| Template sale (one-time) | $29 | 0% | $29.00 | $2.90 | $26.10 |

### Break-Even Point

| Scenario | Monthly Units Needed | Daily Units Needed |
|----------|---------------------|-------------------|
| Plan A only | 46 | 1.5/day |
| Plan B only | 15 | 0.5/day |
| Mix (A:60% B:30% Template:10%) | 25 | 0.8/day |

**Current status**: Pre-launch phase. Zero paid users. Validating first revenue via template sales.

---

## 6. Free Tier Utilization

| Service | Free Tier Limit | This Month | Usage % | Alert |
|---------|----------------|------------|---------|-------|
| Vercel Hobby | 100GB bandwidth | N/A | - | Upgraded to Pro |
| Supabase Free | 500MB DB | N/A | - | Upgraded to Pro |
| GitHub Free | 2,000 Actions min | 1,240 min | 62% | |
| Cloudflare Free | Unlimited | - | - | |
| Google Analytics | Unlimited | - | - | |

---

## 7. Quarterly Cost Audit Report (Sample)

### 2026 Q1 (January - March)

**Period**: 2026-01-01 to 2026-03-31

#### Fixed Cost Trends

| Service | Jan | Feb | Mar | Q1 Total | Trend |
|---------|-----|-----|-----|----------|-------|
| Claude Code Max | $200 | $200 | $200 | $600 | Flat |
| Vercel Pro | $20 | $20 | $20 | $60 | Flat |
| Supabase Pro | $25 | $25 | $25 | $75 | Flat |

#### Variable Cost Trends

| Service | Jan | Feb | Mar | Q1 Total | Trend |
|---------|-----|-----|-----|----------|-------|
| OpenAI API | $5.10 | $8.20 | $12.40 | $25.70 | :arrow_up: Increasing |
| Stripe | $0 | $15.30 | $18.60 | $33.90 | Transactions started |
| Gumroad | $0 | $0 | $2.90 | $2.90 | New |

#### New Costs Added (Q1)
- March: Gumroad fees (template sales launch)

#### Costs Removed/Reduced (Q1)
- None

#### Q2 Risks
- OpenAI API usage growing at +50% month-over-month. Primary driver: video department subtitle generation. If exceeding $20/month, consider switching to Whisper API batch processing
- Costs are front-loaded before paid user acquisition

#### Next Actions
1. Strengthen OpenAI API usage monitoring ($20/month alert)
2. Recalculate Q2 break-even (post-launch actuals)
3. Compare Claude Code Max multi-account vs direct API usage costs
