# Frontend & UI Subagents

Frontend & UI subagents specialise in building and refining user interface code. They handle the visual and interaction layer of applications — building accessible components, refactoring styles, adapting layouts for different screens, generating design system tokens, and extracting strings for internationalisation. All changes are local source code modifications reviewable before merging.

**Risk Tier: 🟡 Tier 2 — Medium** — Creates and modifies UI source files in the working directory; changes are local and reviewable via git diff.

## When to Use Frontend & UI Agents

Use these subagents when you need to:
- **Build UI components** — Create accessible, responsive components from scratch or designs
- **Refactor styles** — Migrate CSS/SCSS to modules, utility classes, or a new approach
- **Adapt for screen sizes** — Make layouts responsive across mobile, tablet, and desktop
- **Generate design tokens** — Create or update theme files, colour palettes, and spacing scales
- **Internationalise strings** — Extract hardcoded text into translation files for i18n support

## Available Subagents

### [**i18n-extractor**](i18n-extractor.md) — Extract strings for internationalisation
Scans source files for hardcoded user-facing strings, extracts them into i18n translation files (JSON, YAML, etc.), and replaces inline strings with translation function calls. Supports React-i18next, Vue-i18n, Angular i18n, and others.

**Use when:** Adding internationalisation support to an existing application or ensuring new features use the i18n system rather than hardcoded strings.

### [**responsive-adapter**](responsive-adapter.md) — Adapt layouts for different screen sizes
Reviews and updates layouts to be responsive across breakpoints — mobile, tablet, and desktop. Uses CSS Grid, Flexbox, and responsive utilities to create fluid, adaptive interfaces.

**Use when:** A layout looks broken on mobile or tablet, when adding mobile support to a desktop-only interface, or when implementing a responsive design from specs.

### [**style-refactorer**](style-refactorer.md) — Refactor CSS and style architecture
Migrates CSS from one approach to another — global CSS to modules, plain SCSS to utility-first (Tailwind), inline styles to design system classes. Improves organisation, removes duplication, and enforces consistency.

**Use when:** Migrating to a new styling approach, cleaning up accumulated CSS debt, or standardising style patterns across a codebase.

### [**theme-generator**](theme-generator.md) — Generate design system tokens and themes
Creates design system token files with colour palettes, typography scales, spacing systems, and component variants. Produces theme configuration for Tailwind, MUI, Chakra UI, Styled Components, or custom systems.

**Use when:** Establishing a design system, implementing a brand refresh, or generating dark/light mode themes from a design spec.

### [**ui-component-builder**](ui-component-builder.md) — Build accessible, responsive UI components
Implements UI components from scratch or from Figma/design specs, ensuring accessibility (ARIA, keyboard navigation, screen reader support), responsiveness, and integration with the project's design system.

**Use when:** Building new UI components, implementing a design from Figma, or adding missing components to a design system.

## Quick Selection Guide

| Task | Subagent | Notes |
|------|----------|-------|
| Build a new UI component | **ui-component-builder** | Accessible, responsive, design-system integrated |
| Make a layout responsive | **responsive-adapter** | CSS Grid/Flexbox, breakpoint adaptation |
| Migrate to utility-first CSS | **style-refactorer** | Global CSS → Tailwind, modules, or similar |
| Create a theme or design tokens | **theme-generator** | Colour palette, spacing, typography scales |
| Extract strings for i18n | **i18n-extractor** | React-i18next, Vue-i18n, Angular i18n |

## Common Combinations

**"Build a new feature with design system"**
- **theme-generator** → establish/update tokens → **ui-component-builder** → implement components → **responsive-adapter** → ensure mobile support.

**"Add i18n to an existing app"**
- **i18n-extractor** → extract all strings → **ui-component-builder** → update any components with dynamic string handling → **technical-writer** (Documentation category) → document translation workflow.

**"CSS migration to Tailwind"**
- **style-refactorer** → convert global CSS to Tailwind → **theme-generator** → update theme tokens → **ui-component-builder** → update component implementations.

**"Implement a brand refresh"**
- **theme-generator** → new design tokens → **style-refactorer** → apply across existing components → **responsive-adapter** → verify all breakpoints → **accessibility-tester** (Analysis category) → check colour contrast.

## Getting Started

1. **Specify your design system** — Tell the agent which framework (Tailwind, MUI, Chakra, etc.) and component library you're using.
2. **Provide design context** — Share Figma links, screenshots, or design specs for component implementation.
3. **Verify accessibility** — After building components, run **accessibility-tester** (Analysis & Review category) to catch a11y issues.
4. **Test across browsers** — Use **e2e-test-writer** (Testing category) to write cross-browser tests for critical UI flows.
5. **Keep design tokens centralised** — Use **theme-generator** to maintain a single source of truth for all visual tokens.
