# API & Service Integration Subagents

API and Service Integration agents handle the critical task of connecting your application to external services, payment platforms, message brokers, and third-party APIs. These subagents ensure integrations are secure, resilient, type-safe, and maintainable — protecting your application from vendor lock-in, handling credential hygiene, and implementing production-grade reliability patterns.

**Risk Tier: 🔴 Tier 4 — High** — These agents work with external dependencies and shared infrastructure. Integration changes may affect service availability, incur costs, or leak credentials if mishandled. Always verify changes against sandbox/staging before production deployment. Follow the Approval Gates checklist in each agent definition before proceeding to live environments.

## When to Use API & Service Integration Agents

Use these subagents when you need to:
- **Generate typed API clients** from OpenAPI, Swagger, or GraphQL specifications
- **Configure message brokers and event-driven systems** with reliable delivery guarantees
- **Integrate with external services** (Stripe, Auth0, SendGrid, Shopify, etc.)
- **Build wrapper libraries** that isolate vendor dependencies and add resilience
- **Set up webhook endpoints** with signature verification and idempotency handling
- **Implement credential management** safely without hardcoding secrets
- **Add retry logic and circuit breakers** to external service calls
- **Design message queue topologies** with dead-letter handling and consumer groups

## Available Subagents

### [**api-client-generator**](api-client-generator.md) — Generate typed API clients from specifications
Generates production-quality, type-safe API clients from OpenAPI, Swagger, and GraphQL specifications. Handles authentication configuration, retry logic, error normalization, and post-generation patching to ensure generated code compiles cleanly and integrates with your application's error handling patterns.

**Use when:** You have a machine-readable API specification and need auto-generated client code with proper type safety, authentication, and resilience patterns rather than hand-rolling fetch calls or SDK wrappers.

### [**message-queue-configurator**](message-queue-configurator.md) — Configure message brokers and event-driven systems
Designs and implements reliable message queue topologies across Kafka, RabbitMQ, SQS/SNS, Redis Streams, and NATS. Configures dead-letter queues, retry policies, consumer groups, and idempotency patterns to ensure at-least-once or exactly-once delivery semantics based on your requirements.

**Use when:** You need to set up message broker infrastructure, implement dead-letter handling, design consumer group layouts, or migrate message queue topologies across different broker technologies while preserving delivery and ordering guarantees.

### [**sdk-wrapper-builder**](sdk-wrapper-builder.md) — Build wrapper libraries around third-party SDKs
Creates clean abstraction layers around vendor SDKs using the adapter pattern. Isolates vendor-specific types and error codes, adds resilience patterns (retry, timeout, circuit breaker), and provides test doubles so your application stays vendor-neutral and unit-testable.

**Use when:** You're integrating a third-party SDK but want to avoid hardcoding vendor types throughout the codebase, or you need to retrofit consistent error handling, retry logic, and testability onto existing scattered SDK usage.

### [**third-party-integrator**](third-party-integrator.md) — Integrate external services and APIs
Integrates your application with external platforms including payment providers (Stripe, PayPal), email services (SendGrid, Mailgun), authentication platforms (Auth0, Okta), analytics, cloud storage, and communication APIs. Ensures sandbox-first development, credential hygiene, webhook handling, and resilient fallback behavior.

**Use when:** You need to connect your application to a new third-party service, ensure all integrations follow your codebase's patterns for credential management and error handling, or audit existing integrations for security vulnerabilities and resilience gaps.

### [**webhook-configurator**](webhook-configurator.md) — Set up and configure webhook endpoints
Designs event-driven pipelines between your service and external providers. Implements HMAC signature verification, idempotency handling, dead-letter queues, and retry policies. Handles both endpoint implementation and provider-side webhook registration, with support for local development tunnels via ngrok.

**Use when:** You need to receive real-time events from an external platform (GitHub, Stripe, Shopify), test webhook flows locally before deployment, or retrofit reliability and observability onto existing webhook infrastructure.

## Quick Selection Guide

| Task | Subagent | Notes |
|------|----------|-------|
| Generate typed REST/GraphQL client | **api-client-generator** | From OpenAPI, Swagger, or GraphQL specs |
| Set up Kafka topics and consumer groups | **message-queue-configurator** | Partition sizing, replication, DLQ configuration |
| Configure RabbitMQ exchanges and bindings | **message-queue-configurator** | Policy-based DLX/TTL, dead-letter routing |
| Create message queue on SQS/SNS | **message-queue-configurator** | FIFO queues, visibility timeout, redrive policy |
| Build wrapper around AWS SDK | **sdk-wrapper-builder** | Isolate S3, DynamoDB, or other AWS service usage |
| Integrate Stripe payments | **third-party-integrator** | SDK setup, webhook handling, sandbox validation |
| Add Auth0 authentication | **third-party-integrator** | OAuth2/OIDC flow, token refresh, RBAC |
| Integrate SendGrid email | **third-party-integrator** | Transactional emails, delivery tracking |
| Set up GitHub webhook | **webhook-configurator** | Push events, CI triggers, signature verification |
| Receive Stripe payment events | **webhook-configurator** | HMAC validation, idempotency, DLQ |
| Retrofit error handling on SDK calls | **sdk-wrapper-builder** | Add retry, timeout, circuit breaker patterns |
| Migrate RabbitMQ to SQS/SNS | **message-queue-configurator** | Preserve fan-out and retry semantics |

## Common Combinations

**Building a Payment Integration:**
- **third-party-integrator** + **webhook-configurator** — Set up the payment SDK, credential management, and sandbox testing; then configure webhook endpoints for payment status notifications with signature verification and idempotency

**Event-Driven Microservices Architecture:**
- **message-queue-configurator** + **api-client-generator** — Design the message broker topology (topics, consumer groups, DLQs); then auto-generate clients for service-to-service REST/gRPC calls

**Refactoring Vendor Lock-In:**
- **sdk-wrapper-builder** + **api-client-generator** — Identify scattered SDK usage and wrap it behind a vendor-neutral interface; optionally generate a typed client for internal service endpoints to replace direct SDK calls

**Third-Party Service Integration with Reliability:**
- **third-party-integrator** + **sdk-wrapper-builder** + **webhook-configurator** — Integrate a new third-party service (e.g., Auth0), wrap the SDK to add retry/timeout logic, and configure webhooks for real-time updates (e.g., user provisioning events)

**Data Pipeline with Async Processing:**
- **message-queue-configurator** + **webhook-configurator** — Set up Kafka or RabbitMQ to handle async job processing; wire webhooks from external systems (e.g., Shopify orders) to trigger pipeline jobs with idempotent delivery

## Getting Started

1. **Assess your integration needs**: Do you need to generate clients, configure message brokers, wrap SDKs, integrate third-party services, or set up webhooks?
2. **Check sandbox and credentials**: Ensure all credentials are in a sandbox/test environment first. Never use production keys in development.
3. **Validate specifications and endpoints**: Confirm API specs are valid and target endpoints are reachable before generation or integration.
4. **Follow the Approval Gates**: Review the security checklist in each agent definition. For staging/production, ensure all gates are checked before proceeding.
5. **Document your rollback path**: Every integration change must have a tested rollback procedure that executes in under 10 minutes.
6. **Test end-to-end in a safe environment**: Complete all integration work in a local, staging, or sandbox environment before touching production.
7. **Communicate scope and blast radius**: Document which features and users are affected if the external service becomes unavailable.

## Best Practices

- **Sandbox-first development**: Always start integration work in a vendor's sandbox/test environment. Never commit live credentials.
- **Environment variables for secrets**: Store API keys, tokens, and signing secrets exclusively in environment variables or a secrets manager — never hardcoded.
- **Validate inputs strictly**: Reject API keys, URLs, identifiers, and credential names that don't match expected formats before passing to external systems.
- **Implement idempotency**: For webhook and async message handling, use idempotency keys or delivery IDs to prevent duplicate processing.
- **Map vendor errors to domain errors**: Catch provider-specific exceptions at the adapter boundary and re-throw as application-level error types.
- **Add resilience patterns**: Exponential backoff with jitter for transient failures, circuit breakers for high-frequency calls, timeouts at multiple layers.
- **Test with mocks and doubles**: Use vendor sandbox/test mode in CI; mock at the SDK boundary for unit tests; provide in-memory adapters for testing.
- **Document and monitor**: Include API version pinning, signing secret rotation procedures, and structured logging of webhook/API metrics.
- **Version control as source of truth**: Store all integration code, configuration files, and rollback procedures in version control — enable fast recovery if something goes wrong.
- **Rotate credentials regularly**: Set up a schedule to rotate API keys and signing secrets quarterly, and have a procedure to rotate immediately if a credential is suspected to be compromised.

Choose your API & Service Integration agent and connect your systems with confidence!