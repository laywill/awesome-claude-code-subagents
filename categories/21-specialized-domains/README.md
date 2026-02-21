# Specialised Domains Subagents

Specialised Domains subagents provide deep expertise in industry-specific and niche technology areas — blockchain, embedded systems, financial technology, IoT, Microsoft 365, and payment processing. These domains carry their own specific risk profiles: financial and payment agents touch real money flows, blockchain agents deploy immutable code, and embedded agents modify firmware on physical hardware.

**Risk Tier: 🔴 Tier 4 — High** — Specialised domains involve external services, financial systems, or physical hardware. Risk profiles vary by domain — always consult domain experts and test thoroughly before production use.

## When to Use Specialised Domain Agents

Use these subagents when you need to:
- **Build on blockchain** — Develop smart contracts, DeFi protocols, or Web3 integrations
- **Program hardware** — Write firmware, RTOS code, or hardware-interface software
- **Build financial systems** — Implement payment rails, trading systems, or financial data processing
- **Work with IoT** — Connect and manage IoT devices, gateways, and edge systems
- **Administer Microsoft 365** — Manage M365 tenants, Exchange, SharePoint, and Teams
- **Integrate payments** — Connect to Stripe, Adyen, or other payment gateways

## Available Subagents

### [**blockchain-developer**](blockchain-developer.md) — Smart contracts, DeFi, and Web3
Develops Ethereum/EVM smart contracts in Solidity, DeFi protocol integrations, and Web3 frontend connections. Understands gas optimisation, contract security patterns, and audit considerations.

**Use when:** Building dApps, writing smart contracts, integrating with DeFi protocols, or implementing NFT contracts. **Smart contracts are immutable once deployed — audit carefully.**

### [**embedded-systems**](embedded-systems.md) — Firmware and hardware-interface programming
Writes firmware for microcontrollers (ARM Cortex, AVR, ESP32), RTOS implementations, hardware abstraction layers, and device drivers. Handles memory constraints, real-time requirements, and hardware-software interfaces.

**Use when:** Programming microcontrollers, implementing RTOS-based firmware, writing device drivers, or working with embedded Linux systems.

### [**fintech-engineer**](fintech-engineer.md) — Financial systems and regulatory compliance
Builds financial systems — trading platforms, portfolio management, regulatory reporting (MiFID II, Basel III), accounting systems, and financial data pipelines. Expert in precision arithmetic, audit trails, and compliance requirements.

**Use when:** Building any financial system where data accuracy, auditability, and regulatory compliance are critical.

### [**iot-engineer**](iot-engineer.md) — IoT device management and edge computing
Implements IoT solutions — device provisioning and management, MQTT/CoAP protocols, edge computing (AWS Greengrass, Azure IoT Edge), OTA firmware updates, and IoT security.

**Use when:** Connecting IoT devices to cloud platforms, implementing device management at scale, or building edge computing solutions.

### [**m365-admin**](m365-admin.md) — Microsoft 365 administration and automation
Administers Microsoft 365 tenants — Exchange Online, SharePoint, Teams, Azure AD, and Intune. Automates M365 management with PowerShell, Microsoft Graph API, and Power Automate.

**Use when:** Managing M365 tenant configurations, automating user provisioning, building Teams apps, or integrating with Microsoft Graph.

### [**payment-integration**](payment-integration.md) — Payment gateway integration
Implements payment processing integrations — Stripe, Adyen, Braintree, and PayPal. Handles payment flows, refunds, disputes, PCI-DSS compliance considerations, and webhook event handling.

**Use when:** Adding payment processing to an application, implementing subscription billing, or integrating with a new payment provider.

## Quick Selection Guide

| Task | Subagent | Notes |
|------|----------|-------|
| Write or audit smart contracts | **blockchain-developer** | Solidity, EVM, gas optimisation, DeFi |
| Write microcontroller firmware | **embedded-systems** | ARM, AVR, ESP32, RTOS, device drivers |
| Build financial/trading systems | **fintech-engineer** | Precision arithmetic, audit trails, compliance |
| Connect IoT devices | **iot-engineer** | MQTT, edge computing, OTA updates |
| Manage Microsoft 365 | **m365-admin** | Exchange, SharePoint, Teams, Microsoft Graph |
| Integrate Stripe or Adyen | **payment-integration** | Payment flows, webhooks, PCI considerations |

## Common Combinations

**"Launch a DeFi protocol"**
- **blockchain-developer** → smart contracts → **security-auditor** (Analysis category) → contract audit → **api-designer** (Architecture category) → Web3 API design → **blockchain-developer** → frontend integration.

**"Build an IoT product"**
- **embedded-systems** → device firmware → **iot-engineer** → cloud connectivity and OTA → **security-engineer** (Security category) → device security → **data-engineer** (Data category) → IoT data pipeline.

**"Add subscription payments"**
- **payment-integration** → Stripe subscription integration → **webhook-configurator** (API Integration category) → payment event handling → **fintech-engineer** → billing ledger and audit trail.

**"Automate M365 onboarding"**
- **m365-admin** → user provisioning automation → **security-engineer** (Security category) → conditional access policies → **iam-policy-author** (Security category) → Azure AD role assignments.

## Getting Started

> **Domain expertise matters here** — these specialised areas carry real-world risk. Always validate outputs with domain experts.

1. **Smart contracts are immutable** — Thoroughly test and audit smart contracts before deploying to mainnet; consider professional audits for high-value contracts.
2. **Test payment flows in sandbox** — Use payment provider sandbox/test modes exclusively until full integration testing is complete.
3. **Financial precision is critical** — Never use floating-point arithmetic for financial calculations; use decimal or integer arithmetic.
4. **IoT security requires defence in depth** — IoT devices are often difficult to patch; design security in from the start.
5. **M365 changes affect entire organisations** — Test tenant configuration changes in a dev tenant before applying to production.
