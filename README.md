<div align="center">
    <strong>An awesome collection of Claude Code subagents.</strong>
    <br />
    <br />
</div>

<div align="center">

![Subagent Count](https://img.shields.io/badge/subagents-179+-blue?style=flat-square)
[![Last Update](https://img.shields.io/github/last-commit/laywill/awesome-claude-code-subagents?label=Last%20update&style=flat-square)](https://github.com/laywill/awesome-claude-code-subagents)
[![GitHub forks](https://img.shields.io/github/forks/laywill/awesome-claude-code-subagents?style=social)](https://github.com/laywill/awesome-claude-code-subagents/network/members)

</div>

# Awesome Claude Code Subagents

This repository serves as the definitive collection of Claude Code subagents, specialized AI assistants designed for specific development tasks. Organized into 25 categories with a risk-tiered structure for production-safe automation.

## Installation

### As Claude Code Plugin (Recommended)

```bash
claude plugin marketplace add laywill/awesome-claude-code-subagents
claude plugin install <plugin-name>
```

Examples:

```bash
claude plugin install laywill-language-specialists    # Language experts
claude plugin install laywill-infrastructure-code     # Infrastructure & IaC
claude plugin install laywill-meta-orchestration      # Multi-agent coordination
```

See [Categories](#-categories) below for all available plugins.

> **Note**: The `laywill-meta-orchestration` agents work best when other categories are installed.

### Option 1: Manual Installation

1. Clone this repository
2. Copy desired agent files to:
   - `~/.claude/agents/` for global access
   - `.claude/agents/` for project-specific use
3. Customize based on your project requirements

### Option 2: Interactive Installer

```bash
git clone https://github.com/laywill/awesome-claude-code-subagents.git
cd awesome-claude-code-subagents
./install-agents.sh
```

This interactive script lets you browse categories, select agents, and install/uninstall them with a single command.

### Option 3: Standalone Installer (no clone required)

```bash
curl -sO https://raw.githubusercontent.com/laywill/awesome-claude-code-subagents/main/install-agents.sh
chmod +x install-agents.sh
./install-agents.sh
```

Downloads agents directly from GitHub without cloning the repository. Requires `curl`.

### Option 4: Agent Installer (use Claude Code to install agents)

```bash
curl -s https://raw.githubusercontent.com/laywill/awesome-claude-code-subagents/main/categories/00-meta-and-orchestration/agent-installer.md -o ~/.claude/agents/agent-installer.md
```

Then in Claude Code: "Use the agent-installer to show me available categories" or "Find TypeScript agents and install typescript-pro globally".

<br />

## 🔒 Risk Tiers at a Glance

| Tier | Icon | Categories | Risk Level | Key Characteristics |
|------|------|-----------|------------|-------------------|
| 0 | ⚪ | 00 | Meta | Orchestration and coordination only |
| 1 | 🟢 | 01–06 | Low (Read-Only/Advisory) | Analysis, research, planning, documentation |
| 2 | 🟡 | 07–13 | Medium (Local Code) | Development, testing, refactoring |
| 3 | 🟠 | 14–17 | Medium-High (Data/Deps/Build) | Database, dependencies, CI/CD |
| 4 | 🔴 | 18–21 | High (External Systems) | APIs, infrastructure, security |
| 5 | ⛔ | 22–24 | Critical (Production) | Deployment, operations, data migration |

<br />

## 📚 Categories

### ⚪ 00. [Meta and Orchestration](categories/00-meta-and-orchestration/)

**Plugin:** `laywill-meta-orchestration`

Meta and orchestration subagents coordinate and manage other subagents rather than performing work directly. They decompose complex tasks, distribute work to specialists, synthesize outputs, and handle errors across multi-agent workflows.

- [**agent-installer**](categories/00-meta-and-orchestration/agent-installer.md) - Browse and install agents from this repository
- [**agent-organizer**](categories/00-meta-and-orchestration/agent-organizer.md) - Multi-agent coordinator
- [**context-manager**](categories/00-meta-and-orchestration/context-manager.md) - Context optimization expert
- [**error-coordinator**](categories/00-meta-and-orchestration/error-coordinator.md) - Error handling and recovery specialist
- [**it-ops-orchestrator**](categories/00-meta-and-orchestration/it-ops-orchestrator.md) - IT operations workflow orchestration
- [**knowledge-synthesizer**](categories/00-meta-and-orchestration/knowledge-synthesizer.md) - Knowledge aggregation expert
- [**multi-agent-coordinator**](categories/00-meta-and-orchestration/multi-agent-coordinator.md) - Advanced multi-agent orchestration
- [**performance-monitor**](categories/00-meta-and-orchestration/performance-monitor.md) - Agent performance optimization
- [**task-distributor**](categories/00-meta-and-orchestration/task-distributor.md) - Task allocation specialist
- [**workflow-orchestrator**](categories/00-meta-and-orchestration/workflow-orchestrator.md) - Complex workflow automation

### 🟢 01. [Research and Discovery](categories/01-research-and-discovery/)

**Plugin:** `laywill-research-discovery`

Research and discovery subagents explore new technologies, assess feasibility, analyze markets and trends, and conduct deep investigations. They help teams understand the landscape before committing to major decisions.

- [**codebase-explorer**](categories/01-research-and-discovery/codebase-explorer.md) - Codebase analysis and exploration
- [**competitive-analyst**](categories/01-research-and-discovery/competitive-analyst.md) - Competitive intelligence specialist
- [**data-researcher**](categories/01-research-and-discovery/data-researcher.md) - Data discovery and analysis expert
- [**feasibility-assessor**](categories/01-research-and-discovery/feasibility-assessor.md) - Technical feasibility assessment
- [**market-researcher**](categories/01-research-and-discovery/market-researcher.md) - Market analysis and consumer insights
- [**research-analyst**](categories/01-research-and-discovery/research-analyst.md) - Comprehensive research specialist
- [**search-specialist**](categories/01-research-and-discovery/search-specialist.md) - Advanced information retrieval expert
- [**technology-researcher**](categories/01-research-and-discovery/technology-researcher.md) - Technology landscape explorer
- [**trend-analyst**](categories/01-research-and-discovery/trend-analyst.md) - Emerging trends and forecasting expert

### 🟢 02. [Architecture and Design](categories/02-architecture-and-design/)

**Plugin:** `laywill-architecture-design`

Architecture and design subagents design systems, APIs, databases, and data flows. They create blueprints for scalable, maintainable solutions before implementation begins.

- [**api-designer**](categories/02-architecture-and-design/api-designer.md) - REST and GraphQL API architect
- [**architect-reviewer**](categories/02-architecture-and-design/architect-reviewer.md) - Architecture review specialist
- [**data-flow-designer**](categories/02-architecture-and-design/data-flow-designer.md) - Data flow and pipeline designer
- [**graphql-architect**](categories/02-architecture-and-design/graphql-architect.md) - GraphQL schema and federation expert
- [**microservices-architect**](categories/02-architecture-and-design/microservices-architect.md) - Distributed systems designer
- [**schema-designer**](categories/02-architecture-and-design/schema-designer.md) - Database schema architect
- [**solution-architect**](categories/02-architecture-and-design/solution-architect.md) - End-to-end solution design specialist
- [**system-modeler**](categories/02-architecture-and-design/system-modeler.md) - System design and modeling expert

### 🟢 03. [Analysis and Review](categories/03-analysis-and-review/)

**Plugin:** `laywill-analysis-review`

Analysis and review subagents audit code quality, security, performance, accessibility, and compliance. They identify risks and improvements before code reaches production.

- [**accessibility-tester**](categories/03-analysis-and-review/accessibility-tester.md) - A11y compliance expert
- [**code-reviewer**](categories/03-analysis-and-review/code-reviewer.md) - Code quality guardian
- [**compliance-auditor**](categories/03-analysis-and-review/compliance-auditor.md) - Regulatory compliance expert
- [**complexity-analyzer**](categories/03-analysis-and-review/complexity-analyzer.md) - Code complexity analysis specialist
- [**dependency-auditor**](categories/03-analysis-and-review/dependency-auditor.md) - Dependency audit and risk assessment
- [**performance-engineer**](categories/03-analysis-and-review/performance-engineer.md) - Performance optimization expert
- [**qa-expert**](categories/03-analysis-and-review/qa-expert.md) - Test automation specialist
- [**security-auditor**](categories/03-analysis-and-review/security-auditor.md) - Security vulnerability expert

### 🟢 04. [Documentation](categories/04-documentation/)

**Plugin:** `laywill-documentation`

Documentation subagents create and maintain API docs, ADRs, runbooks, READMEs, changelogs, and technical guides. They ensure knowledge is captured and accessible.

- [**adr-author**](categories/04-documentation/adr-author.md) - Architecture decision record writer
- [**api-documenter**](categories/04-documentation/api-documenter.md) - API documentation specialist
- [**changelog-generator**](categories/04-documentation/changelog-generator.md) - Changelog creation expert
- [**documentation-engineer**](categories/04-documentation/documentation-engineer.md) - Technical documentation expert
- [**readme-generator**](categories/04-documentation/readme-generator.md) - README creation specialist
- [**runbook-writer**](categories/04-documentation/runbook-writer.md) - Operations runbook author
- [**technical-writer**](categories/04-documentation/technical-writer.md) - Technical writing specialist

### 🟢 05. [Planning and Estimation](categories/05-planning-and-estimation/)

**Plugin:** `laywill-planning-estimation`

Planning and estimation subagents help teams scope work, estimate effort, plan migrations and releases, and assess risks. They enable better project management and delivery confidence.

- [**effort-estimator**](categories/05-planning-and-estimation/effort-estimator.md) - Work effort estimation specialist
- [**migration-planner**](categories/05-planning-and-estimation/migration-planner.md) - Migration project planning expert
- [**product-manager**](categories/05-planning-and-estimation/product-manager.md) - Product strategy expert
- [**project-manager**](categories/05-planning-and-estimation/project-manager.md) - Project management specialist
- [**release-planner**](categories/05-planning-and-estimation/release-planner.md) - Release planning expert
- [**risk-assessor**](categories/05-planning-and-estimation/risk-assessor.md) - Risk assessment specialist
- [**scrum-master**](categories/05-planning-and-estimation/scrum-master.md) - Agile methodology expert
- [**task-planner**](categories/05-planning-and-estimation/task-planner.md) - Task decomposition and planning

### 🟢 06. [Business and Product](categories/06-business-and-product/)

**Plugin:** `laywill-business-product`

Business and product subagents support business strategy, market analysis, UX research, legal compliance, content marketing, and financial modeling. They bridge technology and business decisions.

- [**business-analyst**](categories/06-business-and-product/business-analyst.md) - Requirements and business analysis specialist
- [**content-marketer**](categories/06-business-and-product/content-marketer.md) - Content marketing specialist
- [**customer-success-manager**](categories/06-business-and-product/customer-success-manager.md) - Customer success expert
- [**legal-advisor**](categories/06-business-and-product/legal-advisor.md) - Legal and compliance specialist
- [**quant-analyst**](categories/06-business-and-product/quant-analyst.md) - Quantitative analysis specialist
- [**risk-manager**](categories/06-business-and-product/risk-manager.md) - Risk assessment and management expert
- [**sales-engineer**](categories/06-business-and-product/sales-engineer.md) - Technical sales expert
- [**seo-specialist**](categories/06-business-and-product/seo-specialist.md) - Search engine optimization expert
- [**ux-researcher**](categories/06-business-and-product/ux-researcher.md) - User research expert

### 🟡 07. [Language and Framework Specialists](categories/07-language-and-framework-specialists/)

**Plugin:** `laywill-language-specialists`

Language and framework specialists provide expert knowledge for specific programming languages and frameworks. They handle language-specific idioms, best practices, and optimization techniques.

**34 language specialists including:** Angular, C++, C#, Django, .NET Core, .NET Framework, Elixir, Flutter, F#, Go, Haskell, Java, JavaScript, Kotlin, Laravel, Lua, Next.js, OCaml, PHP, PowerShell (5.1, 7, modules, UI), Python, R, Rails, React, Rust, Spring Boot, SQL, Swift, TypeScript, Vue, WordPress

[View all 34 language specialists →](categories/07-language-and-framework-specialists/)

### 🟡 08. [General Development](categories/08-general-development/)

**Plugin:** `laywill-general-development`

General development subagents handle core development roles including backend, frontend, fullstack, mobile, CLI, game, and UI development. They provide broad development expertise across platforms.

- [**backend-developer**](categories/08-general-development/backend-developer.md) - Server-side expert for scalable APIs
- [**cli-developer**](categories/08-general-development/cli-developer.md) - Command-line tool creator
- [**electron-pro**](categories/08-general-development/electron-pro.md) - Desktop application expert
- [**frontend-developer**](categories/08-general-development/frontend-developer.md) - UI/UX specialist for React, Vue, and Angular
- [**fullstack-developer**](categories/08-general-development/fullstack-developer.md) - End-to-end feature development
- [**game-developer**](categories/08-general-development/game-developer.md) - Game development expert
- [**mcp-developer**](categories/08-general-development/mcp-developer.md) - Model Context Protocol specialist
- [**mobile-app-developer**](categories/08-general-development/mobile-app-developer.md) - Mobile application specialist
- [**mobile-developer**](categories/08-general-development/mobile-developer.md) - Cross-platform mobile specialist
- [**ui-designer**](categories/08-general-development/ui-designer.md) - Visual design and interaction specialist
- [**websocket-engineer**](categories/08-general-development/websocket-engineer.md) - Real-time communication specialist

### 🟡 09. [Testing and QA](categories/09-testing-and-qa/)

**Plugin:** `laywill-testing-qa`

Testing and QA subagents create automated tests, chaos experiments, fixtures, and coverage reports. They ensure code quality through comprehensive testing strategies.

- [**chaos-engineer**](categories/09-testing-and-qa/chaos-engineer.md) - System resilience testing expert
- [**coverage-gap-filler**](categories/09-testing-and-qa/coverage-gap-filler.md) - Test coverage improvement specialist
- [**e2e-test-writer**](categories/09-testing-and-qa/e2e-test-writer.md) - End-to-end test automation expert
- [**integration-test-writer**](categories/09-testing-and-qa/integration-test-writer.md) - Integration test specialist
- [**snapshot-updater**](categories/09-testing-and-qa/snapshot-updater.md) - Snapshot test management
- [**test-automator**](categories/09-testing-and-qa/test-automator.md) - Test automation framework expert
- [**test-fixture-generator**](categories/09-testing-and-qa/test-fixture-generator.md) - Test fixture and mock data creator
- [**unit-test-writer**](categories/09-testing-and-qa/unit-test-writer.md) - Unit test specialist

### 🟡 10. [Refactoring and Modernization](categories/10-refactoring-and-modernization/)

**Plugin:** `laywill-refactoring-modernization`

Refactoring and modernization subagents improve code quality by reducing technical debt, applying design patterns, upgrading frameworks, and modernizing language features.

- [**framework-upgrader**](categories/10-refactoring-and-modernization/framework-upgrader.md) - Framework upgrade and migration expert
- [**language-modernizer**](categories/10-refactoring-and-modernization/language-modernizer.md) - Language feature modernization specialist
- [**legacy-modernizer**](categories/10-refactoring-and-modernization/legacy-modernizer.md) - Legacy code modernization specialist
- [**linter-fixer**](categories/10-refactoring-and-modernization/linter-fixer.md) - Linting and code style automation
- [**pattern-migrator**](categories/10-refactoring-and-modernization/pattern-migrator.md) - Design pattern migration expert
- [**refactoring-specialist**](categories/10-refactoring-and-modernization/refactoring-specialist.md) - Code refactoring expert
- [**tech-debt-reducer**](categories/10-refactoring-and-modernization/tech-debt-reducer.md) - Technical debt elimination specialist

### 🟡 11. [Bug Fixing and Debugging](categories/11-bug-fixing-and-debugging/)

**Plugin:** `laywill-bug-fixing-debugging`

Bug fixing and debugging subagents diagnose and fix bugs, analyze logs and stack traces, and hunt regressions. They help teams resolve production issues quickly.

- [**bug-fixer**](categories/11-bug-fixing-and-debugging/bug-fixer.md) - Bug resolution and fixing specialist
- [**debugger**](categories/11-bug-fixing-and-debugging/debugger.md) - Advanced debugging specialist
- [**error-detective**](categories/11-bug-fixing-and-debugging/error-detective.md) - Error analysis and resolution expert
- [**log-analyzer**](categories/11-bug-fixing-and-debugging/log-analyzer.md) - Log analysis and diagnostics expert
- [**regression-hunter**](categories/11-bug-fixing-and-debugging/regression-hunter.md) - Regression detection specialist
- [**stack-trace-interpreter**](categories/11-bug-fixing-and-debugging/stack-trace-interpreter.md) - Stack trace analysis expert

### 🟡 12. [Frontend and UI](categories/12-frontend-and-ui/)

**Plugin:** `laywill-frontend-ui`

Frontend and UI subagents build responsive components, manage themes, handle internationalization, and refactor styles. They ensure polished, accessible user interfaces.

- [**i18n-extractor**](categories/12-frontend-and-ui/i18n-extractor.md) - Internationalization extraction specialist
- [**responsive-adapter**](categories/12-frontend-and-ui/responsive-adapter.md) - Responsive design adaptation expert
- [**style-refactorer**](categories/12-frontend-and-ui/style-refactorer.md) - CSS and styling refactoring expert
- [**theme-generator**](categories/12-frontend-and-ui/theme-generator.md) - Theme system creation specialist
- [**ui-component-builder**](categories/12-frontend-and-ui/ui-component-builder.md) - Reusable component creation expert

### 🟡 13. [Developer Experience and Tooling](categories/13-developer-experience-and-tooling/)

**Plugin:** `laywill-developer-experience`

Developer experience and tooling subagents improve build processes, optimize git workflows, manage team communication, and enhance prompt engineering. They make development faster and smoother.

- [**build-engineer**](categories/13-developer-experience-and-tooling/build-engineer.md) - Build system specialist
- [**dx-optimizer**](categories/13-developer-experience-and-tooling/dx-optimizer.md) - Developer experience optimization specialist
- [**git-workflow-manager**](categories/13-developer-experience-and-tooling/git-workflow-manager.md) - Git workflow and branching expert
- [**prompt-engineer**](categories/13-developer-experience-and-tooling/prompt-engineer.md) - Prompt optimization specialist
- [**slack-expert**](categories/13-developer-experience-and-tooling/slack-expert.md) - Slack platform and integration specialist
- [**tooling-engineer**](categories/13-developer-experience-and-tooling/tooling-engineer.md) - Developer tooling specialist

### 🟠 14. [Data and Database](categories/14-data-and-database/)

**Plugin:** `laywill-data-database`

Data and database subagents design schemas, optimize queries, manage migrations, generate test data, and validate data integrity. They ensure reliable data layer performance.

- [**data-engineer**](categories/14-data-and-database/data-engineer.md) - Data pipeline architect
- [**data-validator**](categories/14-data-and-database/data-validator.md) - Data integrity and validation specialist
- [**database-optimizer**](categories/14-data-and-database/database-optimizer.md) - Database performance specialist
- [**orm-model-builder**](categories/14-data-and-database/orm-model-builder.md) - ORM and model architecture specialist
- [**postgres-pro**](categories/14-data-and-database/postgres-pro.md) - PostgreSQL database expert
- [**schema-migrator**](categories/14-data-and-database/schema-migrator.md) - Database schema migration expert
- [**seed-data-generator**](categories/14-data-and-database/seed-data-generator.md) - Test data generation specialist

### 🟠 15. [Data Science and AI](categories/15-data-science-and-ai/)

**Plugin:** `laywill-data-science-ai`

Data science and AI subagents build machine learning models, analyze data, architect LLM solutions, and handle MLOps. They bring intelligent capabilities to applications.

- [**ai-engineer**](categories/15-data-science-and-ai/ai-engineer.md) - AI system design and deployment expert
- [**data-analyst**](categories/15-data-science-and-ai/data-analyst.md) - Data insights and visualization specialist
- [**data-scientist**](categories/15-data-science-and-ai/data-scientist.md) - Analytics and insights expert
- [**llm-architect**](categories/15-data-science-and-ai/llm-architect.md) - Large language model architect
- [**machine-learning-engineer**](categories/15-data-science-and-ai/machine-learning-engineer.md) - Machine learning systems expert
- [**ml-engineer**](categories/15-data-science-and-ai/ml-engineer.md) - Machine learning specialist
- [**mlops-engineer**](categories/15-data-science-and-ai/mlops-engineer.md) - MLOps and model deployment expert
- [**nlp-engineer**](categories/15-data-science-and-ai/nlp-engineer.md) - Natural language processing expert

### 🟠 16. [Dependency and Package Management](categories/16-dependency-and-package-management/)

**Plugin:** `laywill-dependency-management`

Dependency and package management subagents manage dependencies, handle upgrades, patch vulnerabilities, resolve lockfiles, publish packages, and manage monorepos.

- [**dependency-manager**](categories/16-dependency-and-package-management/dependency-manager.md) - Package and dependency specialist
- [**dependency-upgrader**](categories/16-dependency-and-package-management/dependency-upgrader.md) - Dependency upgrade automation specialist
- [**lockfile-resolver**](categories/16-dependency-and-package-management/lockfile-resolver.md) - Lockfile conflict resolution expert
- [**monorepo-manager**](categories/16-dependency-and-package-management/monorepo-manager.md) - Monorepo architecture and management
- [**package-publisher**](categories/16-dependency-and-package-management/package-publisher.md) - Package publishing and release specialist
- [**vulnerability-patcher**](categories/16-dependency-and-package-management/vulnerability-patcher.md) - Security vulnerability patching

### 🟠 17. [Build and CI/CD](categories/17-build-and-ci-cd/)

**Plugin:** `laywill-build-ci-cd`

Build and CI/CD subagents design pipelines, write workflows, configure environments, optimize builds, and publish artifacts. They automate and accelerate software delivery.

- [**artifact-publisher**](categories/17-build-and-ci-cd/artifact-publisher.md) - Build artifact publishing specialist
- [**build-optimizer**](categories/17-build-and-ci-cd/build-optimizer.md) - Build performance optimization expert
- [**environment-configurator**](categories/17-build-and-ci-cd/environment-configurator.md) - Build environment setup specialist
- [**pipeline-builder**](categories/17-build-and-ci-cd/pipeline-builder.md) - CI/CD pipeline design expert
- [**workflow-author**](categories/17-build-and-ci-cd/workflow-author.md) - GitHub Actions and workflow automation

### 🔴 18. [API and Service Integration](categories/18-api-and-service-integration/)

**Plugin:** `laywill-api-service-integration`

API and service integration subagents generate API clients, integrate third-party services, build SDK wrappers, configure webhooks, and set up message queues.

- [**api-client-generator**](categories/18-api-and-service-integration/api-client-generator.md) - API client code generation specialist
- [**message-queue-configurator**](categories/18-api-and-service-integration/message-queue-configurator.md) - Message queue setup and configuration
- [**sdk-wrapper-builder**](categories/18-api-and-service-integration/sdk-wrapper-builder.md) - SDK wrapper and abstraction builder
- [**third-party-integrator**](categories/18-api-and-service-integration/third-party-integrator.md) - Third-party service integration expert
- [**webhook-configurator**](categories/18-api-and-service-integration/webhook-configurator.md) - Webhook setup and management specialist

### 🔴 19. [Infrastructure as Code](categories/19-infrastructure-as-code/)

**Plugin:** `laywill-infrastructure-code`

Infrastructure as code subagents manage cloud infrastructure, Kubernetes, containerization, networking, and platform engineering. They ensure reliable, scalable infrastructure.

- [**azure-infra-engineer**](categories/19-infrastructure-as-code/azure-infra-engineer.md) - Azure infrastructure and automation expert
- [**cloud-architect**](categories/19-infrastructure-as-code/cloud-architect.md) - AWS/GCP/Azure specialist
- [**cloudformation-builder**](categories/19-infrastructure-as-code/cloudformation-builder.md) - AWS CloudFormation expert
- [**devops-engineer**](categories/19-infrastructure-as-code/devops-engineer.md) - DevOps and automation expert
- [**docker-composer**](categories/19-infrastructure-as-code/docker-composer.md) - Docker and containerization specialist
- [**helm-chart-builder**](categories/19-infrastructure-as-code/helm-chart-builder.md) - Helm chart creation and packaging expert
- [**kubernetes-specialist**](categories/19-infrastructure-as-code/kubernetes-specialist.md) - Container orchestration master
- [**network-engineer**](categories/19-infrastructure-as-code/network-engineer.md) - Network infrastructure specialist
- [**platform-engineer**](categories/19-infrastructure-as-code/platform-engineer.md) - Platform architecture expert
- [**terraform-engineer**](categories/19-infrastructure-as-code/terraform-engineer.md) - Infrastructure as Code expert
- [**windows-infra-admin**](categories/19-infrastructure-as-code/windows-infra-admin.md) - Active Directory and Windows infrastructure expert

### 🔴 20. [Security and Secrets](categories/20-security-and-secrets/)

**Plugin:** `laywill-security-secrets`

Security and secrets subagents harden systems, conduct penetration testing, manage secrets and certificates, handle IAM policies, and configure CORS. They protect applications and data.

- [**ad-security-reviewer**](categories/20-security-and-secrets/ad-security-reviewer.md) - Active Directory security expert
- [**certificate-manager**](categories/20-security-and-secrets/certificate-manager.md) - SSL/TLS certificate management specialist
- [**cors-policy-manager**](categories/20-security-and-secrets/cors-policy-manager.md) - CORS policy configuration expert
- [**iam-policy-author**](categories/20-security-and-secrets/iam-policy-author.md) - IAM policy creation and management
- [**penetration-tester**](categories/20-security-and-secrets/penetration-tester.md) - Ethical hacking specialist
- [**powershell-security-hardening**](categories/20-security-and-secrets/powershell-security-hardening.md) - PowerShell security hardening expert
- [**secret-rotator**](categories/20-security-and-secrets/secret-rotator.md) - Secret rotation and management specialist
- [**security-engineer**](categories/20-security-and-secrets/security-engineer.md) - Infrastructure security specialist
- [**vault-configurator**](categories/20-security-and-secrets/vault-configurator.md) - Secrets vault setup and management

### 🔴 21. [Specialized Domains](categories/21-specialized-domains/)

**Plugin:** `laywill-specialized-domains`

Specialized domains subagents handle blockchain, embedded systems, fintech, IoT, Microsoft 365, and payment integration. They bring domain-specific expertise to niche areas.

- [**blockchain-developer**](categories/21-specialized-domains/blockchain-developer.md) - Web3 and crypto specialist
- [**embedded-systems**](categories/21-specialized-domains/embedded-systems.md) - Embedded and real-time systems expert
- [**fintech-engineer**](categories/21-specialized-domains/fintech-engineer.md) - Financial technology specialist
- [**iot-engineer**](categories/21-specialized-domains/iot-engineer.md) - IoT systems developer
- [**m365-admin**](categories/21-specialized-domains/m365-admin.md) - Microsoft 365 administration specialist
- [**payment-integration**](categories/21-specialized-domains/payment-integration.md) - Payment systems expert

### ⛔ 22. [Deployment and Release](categories/22-deployment-and-release/)

**Plugin:** `laywill-deployment-release`

Deployment and release subagents manage deployments, handle blue-green and canary strategies, manage feature flags, and control rollbacks. They enable safe, controlled releases.

- [**blue-green-switcher**](categories/22-deployment-and-release/blue-green-switcher.md) - Blue-green deployment automation
- [**canary-release-controller**](categories/22-deployment-and-release/canary-release-controller.md) - Canary release management expert
- [**deployer**](categories/22-deployment-and-release/deployer.md) - Deployment automation specialist
- [**deployment-engineer**](categories/22-deployment-and-release/deployment-engineer.md) - Deployment automation specialist
- [**feature-flag-manager**](categories/22-deployment-and-release/feature-flag-manager.md) - Feature flag management specialist
- [**rollback-manager**](categories/22-deployment-and-release/rollback-manager.md) - Deployment rollback management expert

### ⛔ 23. [Production Ops and Observability](categories/23-production-ops-and-observability/)

**Plugin:** `laywill-production-ops`

Production ops and observability subagents manage incidents, configure monitoring and logging, build dashboards, manage SLAs, and handle scaling. They ensure systems run smoothly in production.

- [**alert-configurator**](categories/23-production-ops-and-observability/alert-configurator.md) - Alert and notification configuration expert
- [**dashboard-builder**](categories/23-production-ops-and-observability/dashboard-builder.md) - Monitoring dashboard creation specialist
- [**database-administrator**](categories/23-production-ops-and-observability/database-administrator.md) - Database management expert
- [**devops-incident-responder**](categories/23-production-ops-and-observability/devops-incident-responder.md) - DevOps incident management
- [**incident-responder**](categories/23-production-ops-and-observability/incident-responder.md) - System incident response expert
- [**log-pipeline-manager**](categories/23-production-ops-and-observability/log-pipeline-manager.md) - Logging infrastructure specialist
- [**scaling-manager**](categories/23-production-ops-and-observability/scaling-manager.md) - Auto-scaling configuration expert
- [**sla-monitor**](categories/23-production-ops-and-observability/sla-monitor.md) - SLA monitoring and enforcement
- [**sre-engineer**](categories/23-production-ops-and-observability/sre-engineer.md) - Site reliability engineering expert

### ⛔ 24. [Production Data Ops](categories/24-production-data-ops/)

**Plugin:** `laywill-production-data-ops`

Production data ops subagents manage data migrations, anonymization, backup and restore, replication, and retention policies. They ensure data safety and compliance in production.

- [**backup-restore-manager**](categories/24-production-data-ops/backup-restore-manager.md) - Backup and recovery specialist
- [**data-anonymizer**](categories/24-production-data-ops/data-anonymizer.md) - Data privacy and anonymization expert
- [**data-migrator**](categories/24-production-data-ops/data-migrator.md) - Data migration specialist
- [**replication-configurator**](categories/24-production-data-ops/replication-configurator.md) - Database replication setup specialist
- [**retention-policy-enforcer**](categories/24-production-data-ops/retention-policy-enforcer.md) - Data retention policy management

<br />

## 🤖 Understanding Subagents

Subagents are specialized AI assistants that enhance Claude Code's capabilities by providing task-specific expertise. They act as dedicated helpers that Claude Code can call upon when encountering particular types of work.

### What Makes Subagents Special?

**Independent Context Windows**
Every subagent operates within its own isolated context space, preventing cross-contamination between different tasks and maintaining clarity in the primary conversation thread.

**Domain-Specific Intelligence**
Subagents come equipped with carefully crafted instructions tailored to their area of expertise, resulting in superior performance on specialized tasks.

**Shared Across Projects**
After creating a subagent, you can utilize it throughout various projects and distribute it among team members to ensure consistent development practices.

**Granular Tool Permissions**
You can configure each subagent with specific tool access rights, enabling fine-grained control over which capabilities are available for different task types.

### Core Advantages

- **Memory Efficiency**: Isolated contexts prevent the main conversation from becoming cluttered with task-specific details
- **Enhanced Accuracy**: Specialized prompts and configurations lead to better results in specific domains
- **Workflow Consistency**: Team-wide subagent sharing ensures uniform approaches to common tasks
- **Security Control**: Tool access can be restricted based on subagent type and purpose

### Getting Started with Subagents

**1. Access the Subagent Manager**

```bash
/agents
```

**2. Create Your Subagent**

- Choose between project-specific or global subagents
- Let Claude generate an initial version, then refine it to your needs
- Provide detailed descriptions of the subagent's purpose and activation triggers
- Configure tool access (leave empty to inherit all available tools)
- Customize the system prompt using the built-in editor (press `e`)

**3. Deploy and Utilize**
Your subagent becomes immediately available. Claude Code will automatically engage it when suitable, or you can explicitly request its help:

```
> Have the code-reviewer subagent analyze my latest commits
```

### Subagent Storage Locations

| Type              | Path                | Availability         | Precedence |
| ----------------- | ------------------- | -------------------- | ---------- |
| Project Subagents | `.claude/agents/`   | Current project only | Higher     |
| Global Subagents  | `~/.claude/agents/` | All projects         | Lower      |

Note: When naming conflicts occur, project-specific subagents override global ones.

## 📖 Subagent Structure

Each subagent follows a standardized template:

```yaml
---
name: subagent-name
description: When this agent should be invoked
tools: Read, Write, Edit, Bash, Glob, Grep
model: sonnet
---

You are a [role description]...

[Agent-specific checklists, patterns, guidelines]

## Communication Protocol
[Inter-agent communication specs]

## Development Workflow
[Structured implementation phases]
```

## 📝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **New Subagent**: Create a new `.md` file in the appropriate category directory
2. **Update Category README**: Add your subagent to the category's `README.md`
3. **Update Main README**: Add a link in this file under the correct category
4. **Plugin Update**: Verify the `.claude-plugin/plugin.json` includes your agent
5. **Test**: Verify the agent works as intended in Claude Code

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

- **Questions?** Open an issue on GitHub
- **Found a bug?** Report it with a detailed example
- **Want to suggest improvements?** We'd love to hear your ideas!

---

**Built with ❤️ by the Claude Code community**
