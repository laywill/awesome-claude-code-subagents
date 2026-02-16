# Architecture & Design Subagents

Architecture & Design subagents are your strategic thinking partners for making high-level technical decisions. These specialists focus on system structure, API contracts, visual design, and architectural review before and during implementation. They help ensure your systems are scalable, maintainable, and well-designed from the ground up.

## When to Use Architecture & Design Subagents

Use these subagents when you need to:
- **Design API contracts** before implementation begins
- **Define visual design systems** and interaction patterns
- **Architect GraphQL schemas** and federation strategies
- **Review architectural decisions** for soundness and scalability
- **Plan system structure** at the macro level
- **Evaluate technology choices** and trade-offs
- **Ensure design consistency** across applications

## Available Subagents

### [**api-designer**](api-designer.md) - REST and GraphQL API architect
The architect who designs beautiful, intuitive, and scalable APIs. Expert in RESTful principles, GraphQL schemas, API versioning, and documentation. Ensures your APIs are developer-friendly and future-proof.

**Use when:** Designing new APIs, refactoring existing endpoints, implementing API standards, or creating comprehensive API documentation.

### [**architect-reviewer**](architect-reviewer.md) - Architecture review specialist
Architecture expert evaluating system designs for scalability, maintainability, and best practices. Identifies architectural risks and suggests improvements. Ensures long-term system health.

**Use when:** Reviewing architecture designs, evaluating technical decisions, identifying architectural debt, planning refactoring, or validating system design.

### [**graphql-architect**](graphql-architect.md) - GraphQL schema and federation expert
Specialized in GraphQL ecosystem, from schema design to federation strategies. Masters resolver optimization, subscription patterns, and GraphQL best practices. Perfect for building flexible, efficient data layers.

**Use when:** Implementing GraphQL APIs, designing schemas, optimizing resolvers, setting up federation, or migrating from REST to GraphQL.

### [**ui-designer**](ui-designer.md) - Visual design and interaction specialist
Master of visual design who creates beautiful, intuitive, and accessible user interfaces. Expert in design systems, typography, color theory, and interaction patterns. Transforms ideas into polished designs that balance aesthetics with functionality while maintaining brand consistency.

**Use when:** Creating visual designs, building design systems, defining interaction patterns, establishing brand identity, or preparing design handoffs for development.

## Quick Selection Guide

| If you need to... | Use this subagent |
|-------------------|-------------------|
| Design a new API structure | **api-designer** |
| Review a system architecture | **architect-reviewer** |
| Implement GraphQL | **graphql-architect** |
| Design user interfaces | **ui-designer** |

## Common Architecture Patterns

**API-First Development:**
- Start with **api-designer** for API contracts
- Use **graphql-architect** if adopting GraphQL
- Follow up with **architect-reviewer** to validate design

**Design System Creation:**
- Begin with **ui-designer** for visual language and components
- Use **api-designer** for any backend API contracts

**Architecture Review:**
- Use **architect-reviewer** for macro-level design evaluation
- Pair with **api-designer** for API-specific concerns

**GraphQL Migration:**
- Start with **graphql-architect** for schema design
- Use **architect-reviewer** to validate federation strategy
- Pair with **api-designer** for migration planning from REST

## Getting Started

1. **Choose the right subagent** based on your design challenge
2. **Provide clear context** about your project and constraints
3. **Share existing designs** or codebase context if available
4. **Specify your goals** (scalability, developer experience, performance)
5. **Let the subagent guide you** through best practices

## Best Practices

- **Design before implementing:** Use these agents early in the process
- **Review iteratively:** Architecture decisions deserve multiple passes
- **Think long-term:** Consider how designs will evolve over time
- **Document decisions:** Capture architectural rationale for future teams
- **Validate with reviewers:** Use architect-reviewer to sanity-check designs

Choose your architecture & design specialist and build systems that stand the test of time!
