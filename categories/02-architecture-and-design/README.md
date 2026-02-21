# Architecture & Design Subagents

Architecture & Design subagents produce designs, diagrams, API contracts, and structural decisions without writing implementation code. They help you think through systems before building them — capturing trade-offs, identifying failure modes, and ensuring your architecture can scale and evolve. All outputs are advisory documents, making this one of the safest categories to use freely.

**Risk Tier: 🟢 Tier 1 — Low** — Produces design artefacts only; no code, infrastructure, or configuration is modified.

## When to Use Architecture & Design Agents

Use these subagents when you need to:
- **Design system architecture** — Define components, boundaries, and interactions before implementation
- **Create API contracts** — Specify REST, GraphQL, or gRPC interfaces before writing code
- **Model data structures** — Design database schemas, ERDs, and data flows
- **Review architectural decisions** — Get expert critique of proposed designs and trade-offs
- **Produce design diagrams** — Generate C4, sequence, ER, or data-flow diagrams
- **Document architectural choices** — Capture why decisions were made with full context

## Available Subagents

### [**api-designer**](api-designer.md) — Design REST/GraphQL/gRPC API contracts
Produces API contracts, OpenAPI/Swagger specifications, and GraphQL schemas before any implementation begins. Evaluates versioning strategies, pagination patterns, and error handling conventions.

**Use when:** Starting a new API or extending an existing one and you want a well-structured contract before writing code.

### [**architect-reviewer**](architect-reviewer.md) — Critique architectural decisions
Reviews proposed architectures, identifies risks, scalability concerns, and anti-patterns, and provides structured feedback with alternatives. Acts as a senior architecture sanity check.

**Use when:** You've drafted an architectural proposal and need an expert second opinion before committing to implementation.

### [**data-flow-designer**](data-flow-designer.md) — Map data flows and pipelines
Traces how data moves through systems — from ingestion through transformation to consumption. Produces data-flow diagrams, identifies bottlenecks, and documents transformation steps and ownership.

**Use when:** Designing data pipelines, ETL processes, or event-driven systems where understanding data movement is critical.

### [**graphql-architect**](graphql-architect.md) — Design GraphQL schemas and federation
Designs GraphQL schemas, resolver strategies, federation plans, and subscription patterns. Addresses N+1 query problems, schema stitching, and Apollo Federation configuration.

**Use when:** Building a GraphQL API or federated graph and need expert schema design and resolver planning.

### [**microservices-architect**](microservices-architect.md) — Design distributed service architectures
Defines service boundaries, communication patterns (sync/async), data ownership, and deployment topology for microservices systems. Addresses distributed systems challenges like eventual consistency and service discovery.

**Use when:** Breaking a monolith into services or designing a new distributed system and need guidance on boundaries and communication.

### [**schema-designer**](schema-designer.md) — Design database schemas and ERDs
Creates normalised database schemas, entity-relationship diagrams, and data model designs. Considers indexing strategies, constraints, and evolution patterns.

**Use when:** Designing a new database or significantly changing an existing schema, especially before writing migration scripts.

### [**solution-architect**](solution-architect.md) — Design end-to-end system architectures
Produces holistic architecture designs encompassing frontend, backend, data, infrastructure, and integration layers. Creates component diagrams and documents architectural decisions with rationale.

**Use when:** Starting a new system or product and need a comprehensive architecture blueprint covering all layers.

### [**system-modeler**](system-modeler.md) — Create C4, sequence, and state diagrams
Produces formal system models using C4, UML sequence diagrams, state machines, or other modelling notations. Captures runtime behaviour, state transitions, and component interactions.

**Use when:** You need precise, formal diagrams to communicate system behaviour to stakeholders, auditors, or engineering teams.

## Quick Selection Guide

| Task | Subagent | Notes |
|------|----------|-------|
| Design a new REST or GraphQL API | **api-designer** or **graphql-architect** | api-designer for REST/gRPC; graphql-architect for GraphQL federation |
| Design end-to-end system architecture | **solution-architect** | Covers all layers with component diagrams |
| Break a monolith into microservices | **microservices-architect** | Defines service boundaries and communication patterns |
| Design or review a database schema | **schema-designer** | ERDs, normalisation, indexing strategies |
| Map data flows through a pipeline | **data-flow-designer** | Ingestion → transformation → consumption flows |
| Get critique on a proposed design | **architect-reviewer** | Identifies risks and anti-patterns |
| Produce C4 or sequence diagrams | **system-modeler** | Formal notation for stakeholder communication |

## Common Combinations

**"Design a new microservices platform end-to-end"**
- **solution-architect** → high-level blueprint → **microservices-architect** → service boundaries → **api-designer** → API contracts → **schema-designer** → data models.

**"Review and improve our current architecture"**
- **codebase-explorer** (from Research category) → maps current state → **architect-reviewer** → critique and recommendations → **system-modeler** → updated diagrams.

**"Design a data-intensive application"**
- **data-flow-designer** → data movement map → **schema-designer** → data models → **api-designer** → query/mutation contracts.

**"Build a GraphQL federation"**
- **graphql-architect** → schema and federation plan → **system-modeler** → service interaction diagrams → **api-designer** → REST fallback contracts.

## Getting Started

1. **Define the scope** — Clarify whether you need a full system design or a targeted decision (API contract, schema, service boundaries).
2. **Start with solution-architect** for new systems, or **architect-reviewer** when critiquing existing designs.
3. **Specialise from there** — Use focused agents (api-designer, schema-designer) to drill into specific areas.
4. **Document decisions** — Use **adr-author** (Documentation category) to capture the rationale alongside design artefacts.
5. **Hand off to implementation** — Pass design artefacts to Tier 2 agents (language specialists, general development) for implementation.
