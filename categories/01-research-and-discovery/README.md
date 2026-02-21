# Research & Discovery Subagents

Research & Discovery subagents help you navigate complexity, evaluate options, and make informed decisions by gathering, analysing, and synthesising information. From exploring unfamiliar codebases to researching market opportunities and assessing technical feasibility, these agents excel at turning raw information into actionable insights—without making changes to your systems or code.

**Risk Tier: 🟢 Tier 1 — Low** — Read-only analysis with no system, code, or infrastructure changes; findings are advisory.

## When to Use Research & Discovery Agents

Use these subagents when you need to:
- **Understand complex codebases** — Explore unfamiliar repositories, map architecture, and surface key patterns
- **Evaluate technologies** — Compare frameworks, tools, and libraries to find the best fit for your use case
- **Assess technical feasibility** — Validate whether a proposed approach is viable before committing resources
- **Research market opportunities** — Analyse trends, size opportunities, and evaluate competitive landscapes
- **Gather structured information** — Conduct deep research on datasets, data sources, and external information
- **Make informed decisions** — Synthesise findings into clear recommendations and trade-off analyses

## Available Subagents

### [**codebase-explorer**](codebase-explorer.md) — Map unfamiliar repositories
Navigates large or complex codebases, identifies architectural patterns, documents key components, and produces summaries of how the system works. Excellent for onboarding, due diligence, or understanding dependencies before making changes.

**Use when:** You need to quickly understand how an unfamiliar codebase is structured or want to surface potential issues before integration or refactoring.

### [**competitive-analyst**](competitive-analyst.md) — Compare competing solutions
Researches competing products, libraries, and frameworks, evaluates their strengths and weaknesses, and produces side-by-side comparisons. Helps identify trade-offs, feature gaps, and market positioning.

**Use when:** You're deciding between multiple tools or technologies and need a detailed, objective comparison of their capabilities and limitations.

### [**data-researcher**](data-researcher.md) — Investigate data sources and quality
Researches available datasets, evaluates data quality and completeness, identifies data sources relevant to your domain, and assesses fitness for use. Useful for data engineering, ML projects, and analytics initiatives.

**Use when:** You need to find reliable datasets, validate data quality, or assess whether a data source meets your project requirements.

### [**feasibility-assessor**](feasibility-assessor.md) — Validate technical approach
Evaluates whether a proposed technical approach is realistic, identifies potential blockers, estimates effort and complexity, and recommends alternatives if needed. Works across architecture, infrastructure, and implementation domains.

**Use when:** You have a proposed solution and need an honest assessment of its viability before investing engineering effort.

### [**market-researcher**](market-researcher.md) — Analyse market opportunities
Researches market size, growth trends, customer segments, and competitive positioning in your domain. Produces insights on TAM, adoption patterns, and emerging opportunities.

**Use when:** You're evaluating a new product idea, entering a new market, or need data to support business decisions.

### [**research-analyst**](research-analyst.md) — Conduct structured research
Conducts systematic research on complex topics, synthesises findings from multiple sources, and produces comprehensive reports with citations and recommendations.

**Use when:** You need a deep investigation into a specific topic with well-organised findings and clear recommendations.

### [**search-specialist**](search-specialist.md) — Find and synthesise information
Performs targeted searches across public sources, synthesises information from multiple results, and identifies patterns and trends. Excellent for quick lookups and rapid research.

**Use when:** You need to find specific information quickly or understand what's publicly available on a topic.

### [**technology-researcher**](technology-researcher.md) — Evaluate frameworks and tools
Researches technologies, frameworks, and tools in depth, evaluates them against your specific requirements, and produces detailed assessments including maturity, community, and real-world usage.

**Use when:** You're evaluating a new technology stack or need a detailed assessment of whether a tool fits your constraints.

### [**trend-analyst**](trend-analyst.md) — Track emerging trends
Identifies and analyses emerging technology and market trends, assesses their relevance to your domain, and forecasts potential impact. Tracks GitHub stars, adoption curves, and technical direction.

**Use when:** You want to stay ahead of the curve and understand which emerging technologies or market shifts are worth monitoring.

## Quick Selection Guide

| Task | Subagent | Notes |
|------|----------|-------|
| Understand a new codebase before integrating or refactoring | **codebase-explorer** | Best for architecture discovery and pattern identification |
| Decide between 3+ competing libraries or frameworks | **competitive-analyst** or **technology-researcher** | Use competitive-analyst for market context, technology-researcher for technical fit |
| Find suitable datasets for a data project | **data-researcher** | Includes data quality and fitness-for-use assessment |
| Validate a proposed architecture or approach | **feasibility-assessor** | Identifies risks, effort, and alternatives before implementation |
| Understand market size and opportunity | **market-researcher** | TAM sizing, segment analysis, competitive positioning |
| Deep-dive research on a specific technology | **research-analyst** | Full structured investigation with synthesised findings |
| Quick lookup of specific information | **search-specialist** | Fast research, pattern identification across sources |
| Detailed framework/tool evaluation for your use case | **technology-researcher** | Maturity, community, real-world usage against your requirements |
| Track emerging technologies or market shifts | **trend-analyst** | GitHub momentum, adoption curves, strategic relevance |

## Common Combinations

**"Should we adopt this framework?"**
- **feasibility-assessor** + **technology-researcher** — Technology-researcher produces detailed evaluation; feasibility-assessor assesses integration risk and effort for your architecture.

**"Is this market opportunity real?"**
- **market-researcher** + **trend-analyst** — Market-researcher sizes the opportunity; trend-analyst tracks whether adoption is accelerating or slowing.

**"Integrate a new library — how big a change is it?"**
- **codebase-explorer** + **feasibility-assessor** — Codebase-explorer maps your current architecture; feasibility-assessor estimates the effort and risk of integration.

**"Deep competitive analysis for a product decision"**
- **competitive-analyst** + **market-researcher** + **technology-researcher** — Competitive-analyst compares feature sets; market-researcher assesses addressable market; technology-researcher evaluates technical maturity and community.

## Getting Started

1. **Identify your question** — Is it about code understanding, technology evaluation, market opportunity, or feasibility? This guides your agent choice.
2. **Choose your agent** — Use the Quick Selection Guide to find the right fit, or combine agents for complex questions.
3. **Provide context** — Share your constraints (tech stack, timeline, budget, performance requirements) so the agent can tailor its research.
4. **Review findings** — Research & Discovery agents produce analysis and recommendations; decide how to act on them with other agent types.
5. **Follow up** — Use findings to inform decisions with product managers, architects, or engineers working on implementation.
