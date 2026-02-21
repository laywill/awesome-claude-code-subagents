# Business & Product Subagents

Business & Product subagents provide advisory expertise across the commercial, legal, marketing, and product dimensions of software development. They help translate business context into technical requirements, evaluate market opportunities, ensure legal and regulatory compliance, and communicate technical work to non-technical stakeholders. These are purely advisory agents — they produce analysis and recommendations without modifying code or systems.

**Risk Tier: 🟢 Tier 1 — Low** — Advisory outputs only; no code, data, or infrastructure changes.

## When to Use Business & Product Agents

Use these subagents when you need to:
- **Translate requirements** — Convert business needs into technical specifications
- **Research users** — Gather insights to inform product and design decisions
- **Evaluate market opportunities** — Assess feasibility, sizing, and competitive dynamics
- **Manage legal risk** — Understand licensing, compliance, and regulatory constraints
- **Create marketing content** — Produce product messaging, copy, and content strategy
- **Support sales** — Prepare technical responses for RFPs, demos, and POCs
- **Quantify risk** — Model financial exposure, business risk, and mitigation value

## Available Subagents

### [**business-analyst**](business-analyst.md) — Translate business requirements to technical specs
Analyses business requirements, translates them into structured technical specifications, and identifies gaps or contradictions. Produces user stories, acceptance criteria, and functional requirements documents.

**Use when:** You have business requirements that need to be turned into something engineering can implement, or when requirements are ambiguous and need clarification.

### [**content-marketer**](content-marketer.md) — Create marketing content and messaging
Produces product marketing content including landing page copy, blog posts, email campaigns, and content strategy. Adapts messaging for different audiences and channels.

**Use when:** You need marketing content that accurately represents technical capabilities without overselling or underselling the product.

### [**customer-success-manager**](customer-success-manager.md) — Manage customer relationships and success metrics
Develops customer success playbooks, onboarding flows, health scoring models, and escalation procedures. Identifies churn risks and expansion opportunities.

**Use when:** Building or improving customer success processes, defining onboarding journeys, or identifying at-risk customer segments.

### [**legal-advisor**](legal-advisor.md) — Advise on legal and licensing considerations
Provides guidance on software licensing (open source and commercial), data privacy regulations (GDPR, CCPA), terms of service drafting, and IP considerations. Always advisory — complex decisions should involve qualified legal counsel.

**Use when:** Evaluating licence compatibility for dependencies, understanding data privacy obligations, or drafting terms for a new product or API.

### [**quant-analyst**](quant-analyst.md) — Quantitative analysis and financial modelling
Builds financial models, pricing analyses, ROI calculations, and risk quantification frameworks. Applies statistical methods to business problems.

**Use when:** You need rigorous quantitative analysis to support pricing decisions, investment cases, or business risk assessments.

### [**risk-manager**](risk-manager.md) — Identify and mitigate business risks
Identifies, assesses, and prioritises business risks across commercial, operational, technical, and regulatory dimensions. Produces risk registers and mitigation strategies.

**Use when:** Before launching a new product, entering a new market, or when significant business uncertainty exists that needs to be structured and addressed.

### [**sales-engineer**](sales-engineer.md) — Support technical sales
Prepares technical responses for RFPs, builds proof-of-concept outlines, creates demo scripts, and translates product capabilities into customer value propositions.

**Use when:** Responding to an RFP, preparing a technical demo, or helping sales teams explain complex technical capabilities to prospects.

### [**seo-specialist**](seo-specialist.md) — Optimise for search engine visibility
Analyses content and site structure for SEO opportunities, produces keyword research, and provides technical SEO recommendations. Aligns content strategy with search intent.

**Use when:** Launching content or improving organic search visibility for a product, documentation site, or blog.

### [**ux-researcher**](ux-researcher.md) — Conduct user research and translate insights
Designs research plans, synthesises user feedback, identifies usability issues, and translates findings into actionable design and product recommendations.

**Use when:** Before building a new feature, validating assumptions about user behaviour, or when user feedback suggests a product isn't meeting needs.

## Quick Selection Guide

| Task | Subagent | Notes |
|------|----------|-------|
| Translate business requirements to specs | **business-analyst** | User stories, acceptance criteria, functional specs |
| Write landing page or marketing copy | **content-marketer** | Product messaging, blog posts, email campaigns |
| Build customer onboarding playbooks | **customer-success-manager** | Health scoring, escalation procedures |
| Understand licensing or data privacy obligations | **legal-advisor** | Advisory only — consult lawyers for binding decisions |
| Model ROI or pricing scenarios | **quant-analyst** | Financial modelling, statistical analysis |
| Identify and rank business risks | **risk-manager** | Risk register with likelihood, impact, mitigations |
| Respond to an RFP or prepare a demo | **sales-engineer** | Technical sales support and value propositions |
| Improve search rankings | **seo-specialist** | Keyword research, technical and content SEO |
| Understand user behaviour and needs | **ux-researcher** | Research plans, usability synthesis, recommendations |

## Common Combinations

**"Launch a new product feature"**
- **ux-researcher** → user insights → **business-analyst** → functional requirements → **content-marketer** → launch messaging → **seo-specialist** → content optimisation.

**"Enter a new market"**
- **market-researcher** (Research category) → market sizing → **risk-manager** → business risks → **quant-analyst** → financial model → **business-analyst** → go-to-market requirements.

**"Win an enterprise RFP"**
- **sales-engineer** → technical response → **legal-advisor** → compliance and licensing review → **quant-analyst** → commercial modelling.

**"Improve product retention"**
- **ux-researcher** → churn drivers → **customer-success-manager** → success playbook → **business-analyst** → feature requirements to address gaps.

## Getting Started

1. **Identify the business question** — Is it about requirements, market, legal, sales, or users? Choose the agent that matches.
2. **Provide business context** — Share product details, target market, constraints, and goals so outputs are relevant and actionable.
3. **Bridge to engineering** — Use **business-analyst** to translate business outputs into engineering-ready specs.
4. **Validate with stakeholders** — Business advisory outputs should be reviewed by domain experts before acting on them.
5. **Combine perspectives** — Business decisions are complex; combining ux-researcher + risk-manager + quant-analyst gives a richer picture than any single agent.
