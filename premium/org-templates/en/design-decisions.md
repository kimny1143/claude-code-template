# Design Decisions: 10-Department AI Agent Organization

This document explains why the glasswerks AI Room is structured the way it is — the reasoning behind each department, the trade-offs we considered, and guidance for adapting this structure to your own team.

---

## 1. Why departments at all?

### The problem with a single agent

A single Claude Code instance handling everything — code, content, deployments, marketing — hits practical limits fast:

- **Context window pollution.** A 200K-token conversation fills up when you're juggling Next.js components, Threads API calls, and article drafts in the same session. The agent starts losing track of earlier decisions.
- **Conflicting instructions.** "Write concise, technical code comments" and "Write warm, conversational marketing copy" are contradictory style guides. One CLAUDE.md can't serve both well.
- **No parallelism.** One agent means sequential work. While it writes a blog post, the bug fix waits.

### The department model

Each department (課) is a separate Claude Code instance with:
- Its own CLAUDE.md (tailored instructions, tools, and tone)
- Its own working directory (or a specific scope within the monorepo)
- Communication via claude-peers (message passing, not shared state)

This gives you **specialization** (each agent is good at one thing), **parallelism** (multiple agents work simultaneously), and **isolation** (a mistake in one department doesn't corrupt another's context).

---

## 2. The 10 departments and why each exists

### Product development (3 departments)

| Department | Responsibility | Why it's separate |
|-----------|---------------|-------------------|
| **mued課** | Web application (Next.js, Prisma, Supabase) | Frontend + backend + DB migrations is a full workload. Needs deep context on the data model and UI patterns. |
| **native課** | Native/mobile applications | Different toolchain (Swift/Kotlin vs TypeScript), different deployment pipeline, different review cadence. Sharing a context with web would be wasteful. |
| **template課** | Reusable templates, boilerplate, shared configs | Changes here affect ALL other departments. Needs its own review process (always Tier 3) and careful versioning. |

**Why not merge mued and native?** They share a product but not a stack. A single agent switching between Next.js and Swift loses efficiency. Separate agents can work in parallel on the same feature (e.g., mued builds the API, native builds the mobile client).

### Content & marketing (4 departments)

| Department | Responsibility | Why it's separate |
|-----------|---------------|-------------------|
| **write課** | Long-form content: articles, documentation, App Store copy | Writing quality requires a dedicated CLAUDE.md with tone guides, style rules, and editorial workflow. Mixing this with code-generation instructions degrades both. |
| **SNS課** | Social media operations: scheduling, posting, analytics integration | Operational focus — managing JSON data files, cron schedules, API integrations. Different rhythm than content creation. |
| **video課** | Video scripts, thumbnails, visual assets | Image/video generation is token-expensive. Isolating it prevents cost spikes from affecting other departments. |
| **LP課** | Landing pages and conversion optimization | Sits between code (building pages) and marketing (optimizing copy/layout). Needs both CRO frameworks and frontend skills in its context. |

**Why separate write and SNS?** Writing an article and scheduling a Threads post are different workflows. Write課 focuses on quality and editorial process; SNS課 focuses on delivery infrastructure and timing. The handoff point (write課 drafts → SNS課 publishes) is clean and auditable.

### Operations & data (3 departments)

| Department | Responsibility | Why it's separate |
|-----------|---------------|-------------------|
| **conductor課** | Orchestration: PR review, task allocation, cross-team blocker resolution, daily digests | The conductor never writes production code. Its job is coordination. Mixing coordination with implementation creates conflicts of interest (reviewing your own code). |
| **data課** | Analytics, metrics, dashboards, data pipeline | Specialized tooling (Snowflake, data visualization). Needs its own schema knowledge and query patterns. |
| **freee課** | Accounting integration (freee API) | Financial data requires strict access control. Isolating it limits the blast radius of mistakes and keeps financial API credentials out of other departments' contexts. |

**Why is conductor a department, not just a workflow?** Because coordination is continuous work, not a one-time step. The conductor tracks blockers across all departments, produces daily digests, manages the Tier review system, and escalates cost concerns. Making it a department gives it persistent context and a clear communication channel.

---

## 3. How we decided responsibility boundaries

### The boundary test

For each piece of work, we asked: **"If this agent's context window were completely reset, would it be able to resume this work from its CLAUDE.md and the repo state alone?"**

If yes → it belongs in this department.
If no → either the CLAUDE.md needs more context, or the work belongs in a different department.

### The handoff test

When two departments need to collaborate: **"Is there a clean artifact that passes between them?"**

- write課 → SNS課: a text draft (Markdown string via claude-peers)
- mued課 → data課: an analytics event schema (a committed spec file)
- LP課 → write課: a copy brief (structured request with constraints)

If the "artifact" would be a vague verbal instruction ("make it better"), the boundary is in the wrong place.

### The cost isolation test

**"If this department spends 3x its normal budget, does it affect other departments?"**

Isolating image-generation-heavy work (video課) and data-pipeline work (data課) into their own departments means a cost spike in one doesn't starve the others. The conductor monitors total spend and flags anomalies.

---

## 4. Decisions we debated

### Should LP課 be part of mued課?

**Argument for merging:** LP pages are technically part of the web application. Same stack, same deployment.

**Argument against (our choice):** LP work is driven by marketing metrics (conversion rate, bounce rate), not product metrics (feature completeness, bug count). The CLAUDE.md for LP課 includes CRO frameworks, A/B testing patterns, and copywriting principles that would clutter mued課's instructions. The boundary is clean: mued課 owns the application, LP課 owns the marketing site.

### Should there be a dedicated QA/testing department?

**Argument for:** Centralized test strategy, consistent coverage standards.

**Argument against (our choice):** Each department writes its own tests because they have the deepest context on what to test. The conductor enforces "CI must pass before merge" as a universal rule. A separate QA department would create handoff overhead without adding proportional value at this scale.

### Should conductor課 be allowed to write code?

**Argument for:** Sometimes the fastest way to unblock a team is to write the 5-line fix yourself.

**Argument against (our choice):** Separation of concerns. The conductor reviews code; it doesn't write it. If the conductor both writes and reviews, you lose independent verification. The cost is occasional slowness; the benefit is trust in the review process.

### 10 departments — is that too many?

At first glance, 10 feels heavy. But:
- Each department is a Claude Code instance, not a human hire. The marginal cost of adding a department is ~$0/month in salaries.
- The real cost is **coordination overhead** (claude-peers messages, PR reviews, blocker resolution). The conductor exists specifically to manage this.
- We found that **under-splitting** (e.g., one "marketing" department handling write + SNS + LP + video) led to context window exhaustion and conflicting instructions. Over-splitting into 10 was cheaper than the debugging time lost to context pollution.

---

## 5. Adapting this for your team

Not every team needs 10 departments. Here's how to right-size.

### Start with 3 (minimum viable organization)

| Department | Covers |
|-----------|--------|
| **conductor** | Orchestration, reviews, daily digest |
| **dev** | All product development |
| **content** | All content, marketing, and communications |

This works for a solo founder or a small product with one codebase and light marketing needs.

### Scale to 5 when you feel the pain

Split when you notice:
- **dev** context is overflowing → split by stack (frontend/backend) or by product area
- **content** is juggling too many formats → split write (long-form) from ops (scheduling, posting)
- A specific integration (payments, analytics, accounting) needs isolated credentials → give it a department

### Scale to 10 when you have multiple products or surfaces

The 10-department structure fits when you have:
- 2+ products or platforms (web + mobile)
- Active content marketing (articles + social + video)
- Financial/compliance integrations that need isolation
- Enough daily work that a single conductor is busy just coordinating

### What to change first

1. **Department names.** Use names that match your domain. "mued課" is specific to our product; yours might be "api-team" or "dashboard-dept."
2. **Tier thresholds.** Our Tier 3 includes "new external API" — yours might include "changes to billing logic" or "modifies user-facing email templates."
3. **Peer review pairs.** The Tier 2 review table should match your team topology. Pair departments that understand each other's context.
4. **Conductor scope.** In a 3-department setup, the conductor can also handle ops tasks. At 10, the conductor should do nothing but coordinate.

### Signs you've split wrong

- Two departments constantly need each other's files → merge them
- One department is idle most days → merge it into a neighbor
- The conductor is spending more time routing messages than reviewing PRs → you may have too many departments, or boundaries are unclear
- A department's CLAUDE.md is over 500 lines → it may be covering too many concerns; consider splitting

---

## 6. Principles behind the structure

1. **Specialize the CLAUDE.md, not the model.** Every department runs the same Claude model. The differentiation is in the instructions, tools, and context — not the capability.

2. **Communicate through artifacts, not conversations.** Departments exchange files, PR reviews, and structured messages — not freeform chat. This keeps handoffs auditable and resumable.

3. **The conductor doesn't build; builders don't coordinate.** Separation of implementation and orchestration prevents conflicts of interest and keeps review quality high.

4. **Isolate by blast radius, not by convenience.** Financial integrations and cross-department templates get their own departments not because the work is complex, but because mistakes are expensive.

5. **Add departments when context overflows, not when headcount grows.** The trigger for splitting is "this agent keeps forgetting earlier decisions" or "these instructions contradict each other" — not "we have more work."
