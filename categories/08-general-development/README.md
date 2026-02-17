# General Development Subagents

General Development subagents are broad role-based developers who build features end-to-end across different layers and platform types. Unlike language specialists who go deep on a single technology, these agents work across the full stack — from UI to API to database — and cover specialist domains like real-time communication, desktop apps, games, and CLI tools. Changes stay in the local working tree and are reviewable before merging.

**Risk Tier: 🟡 Tier 2 — Medium** — Creates and modifies source code in the working directory; changes are local and reviewable via git diff.

## When to Use General Development Agents

Use these subagents when you need to:
- **Build full-stack features** — Implement across frontend, backend, and data layers
- **Create specialised applications** — Desktop, mobile, CLI, game, or real-time apps
- **Design and implement UIs** — Build user interfaces with design systems
- **Build developer tooling** — MCP servers, extensions, and Claude Code integrations
- **Work across frameworks** — When you need breadth rather than language-specific depth

## Available Subagents

### [**backend-developer**](backend-developer.md) — Build server-side logic and APIs
Implements server-side application logic, REST/GraphQL APIs, background jobs, and data processing pipelines. Works across Node.js, Python, Go, Java, and other backend stacks.

**Use when:** Building API endpoints, background workers, data processing logic, or any server-side feature.

### [**cli-developer**](cli-developer.md) — Build command-line interfaces
Designs and implements command-line tools with ergonomic argument parsing, helpful error messages, shell completion, and cross-platform compatibility. Expert in Click, Cobra, Clap, and other CLI frameworks.

**Use when:** Building developer tools, automation scripts that need a CLI interface, or internal tooling for engineering teams.

### [**electron-pro**](electron-pro.md) — Build cross-platform desktop apps
Creates desktop applications with Electron, managing the main/renderer process boundary, IPC communication, native OS integration, auto-updates, and code signing.

**Use when:** Building a desktop application that needs cross-platform support (macOS, Windows, Linux) with web technologies.

### [**frontend-developer**](frontend-developer.md) — Build user interfaces
Implements user interfaces with modern frontend frameworks, component architecture, state management, and responsive design. Comfortable across React, Vue, Angular, and vanilla JS.

**Use when:** Building web UI components, pages, or frontend features that don't require deep framework specialisation (use language specialists for that).

### [**fullstack-developer**](fullstack-developer.md) — Build features across the full stack
Implements features end-to-end from UI to API to database, coordinating changes across all layers. Avoids handoff friction by implementing the complete vertical slice.

**Use when:** Implementing a complete feature that touches multiple layers and benefits from consistent implementation by a single agent.

### [**game-developer**](game-developer.md) — Build games with engines
Develops games using Unity, Godot, Unreal, or custom engines. Implements game mechanics, physics, AI, asset pipelines, and platform-specific optimisations.

**Use when:** Building or extending a game, implementing game mechanics, or working with game engine tooling and scripting.

### [**mcp-developer**](mcp-developer.md) — Build Model Context Protocol servers
Creates MCP servers that expose tools, resources, and prompts to Claude and other AI agents. Handles MCP protocol compliance, tool schemas, and integration with external systems.

**Use when:** Building custom tools for Claude Code, creating integrations that AI agents can use, or extending the Claude ecosystem.

### [**mobile-app-developer**](mobile-app-developer.md) — Build mobile apps with platform patterns
Implements mobile applications using platform-specific patterns and conventions. Expert in mobile UX patterns, push notifications, offline storage, and app store requirements.

**Use when:** Building mobile features that need to follow platform conventions closely, or when deep mobile expertise is needed.

### [**mobile-developer**](mobile-developer.md) — Build cross-platform mobile applications
Creates mobile applications using cross-platform frameworks like React Native or Flutter. Balances shared code with platform-specific implementations for native look and feel.

**Use when:** Building a mobile app targeting both iOS and Android from a shared codebase.

### [**ui-designer**](ui-designer.md) — Design and implement interfaces with design systems
Creates UI components and layouts using design systems (Tailwind, Material, Chakra, etc.), ensuring consistency, accessibility, and responsiveness across the application.

**Use when:** Implementing UI from design specs, building a component library, or ensuring design system compliance.

### [**websocket-engineer**](websocket-engineer.md) — Build real-time communication
Implements WebSocket servers and clients, event-driven architectures, presence systems, and real-time data synchronisation. Handles connection management, reconnection, and scaling.

**Use when:** Building chat, live collaboration, real-time dashboards, gaming networking, or any feature requiring bidirectional real-time communication.

## Quick Selection Guide

| Task | Subagent | Notes |
|------|----------|-------|
| Full feature across UI + API + DB | **fullstack-developer** | End-to-end vertical slice implementation |
| Server-side API or background job | **backend-developer** | REST/GraphQL endpoints, workers, data processing |
| Web UI components or pages | **frontend-developer** | For framework depth, use language specialists instead |
| UI component from design specs | **ui-designer** | Design system compliance and a11y |
| Cross-platform mobile app | **mobile-developer** | React Native, Flutter — shared codebase |
| Platform-native mobile app | **mobile-app-developer** | iOS/Android platform patterns and conventions |
| Desktop application | **electron-pro** | Cross-platform with Electron |
| CLI tool or dev tool | **cli-developer** | Ergonomic CLI with arg parsing and completion |
| Real-time features | **websocket-engineer** | WebSocket servers, event-driven, presence |
| Game or game mechanics | **game-developer** | Unity, Godot, Unreal, custom engines |
| MCP server or Claude integration | **mcp-developer** | MCP protocol compliance and tool schemas |

## Common Combinations

**"Build a full-stack feature"**
- **solution-architect** (Architecture category) → design → **fullstack-developer** → implementation → **unit-test-writer** (Testing category) → tests.

**"Cross-platform app (web + desktop + mobile)"**
- **frontend-developer** → web → **electron-pro** → desktop wrapper → **mobile-developer** → mobile version.

**"Real-time collaborative feature"**
- **websocket-engineer** → real-time layer → **backend-developer** → persistence API → **frontend-developer** → collaborative UI.

**"Developer tool with CLI and MCP interface"**
- **cli-developer** → CLI interface → **mcp-developer** → MCP server exposing the same functionality to Claude.

## Getting Started

1. **Choose by breadth vs depth** — For language-specific work, use the Language Specialists (category 07); for cross-stack or platform-specific roles, use agents here.
2. **Describe the feature end-to-end** — Share requirements, tech stack, existing patterns, and constraints.
3. **Start with architecture** — Run an Architecture & Design agent first for complex features to get a blueprint.
4. **Follow up with testing** — Pair with Testing & QA agents to write tests after implementation.
5. **Review before merging** — Use Analysis & Review agents to review the generated code.
