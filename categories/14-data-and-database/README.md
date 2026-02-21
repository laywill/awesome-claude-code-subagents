# Data & Database Subagents

Data & Database subagents work with database schemas, queries, and data pipelines. They modify schema definitions, generate migration scripts, build ETL processes, and optimise query performance. Because schema changes and migrations can affect data integrity, this tier requires more care than pure code changes — always review and test in a non-production environment first.

**Risk Tier: 🟠 Tier 3 — Medium-High** — Modifies database schemas, migration scripts, and data pipeline code. Schema changes can break builds or corrupt local data if applied incorrectly. Test all migrations in development before production.

## When to Use Data & Database Agents

Use these subagents when you need to:
- **Design database schemas** — Create or modify tables, relationships, and constraints
- **Write migration scripts** — Produce safe, reversible database migrations
- **Optimise query performance** — Improve slow queries with indexes and query rewrites
- **Build data pipelines** — Create ETL processes, transformations, and data warehouses
- **Generate test data** — Produce realistic seed data for development and testing
- **Create ORM models** — Generate model definitions from existing schemas

## Available Subagents

### [**data-engineer**](data-engineer.md) — Build data pipelines and ETL processes
Designs and implements data pipelines, ETL/ELT processes, streaming architectures, and data warehouse patterns. Works with dbt, Spark, Airflow, Kafka, and cloud data platforms.

**Use when:** Building data ingestion pipelines, implementing data transformations, or creating a data warehouse layer.

### [**data-validator**](data-validator.md) — Write data validation logic
Writes data validation rules, constraints, sanitisation logic, and schema validators for incoming data. Ensures data quality at system boundaries — API inputs, file imports, and event streams.

**Use when:** Adding input validation to APIs, implementing data quality checks in a pipeline, or hardening data ingestion against malformed inputs.

### [**database-optimizer**](database-optimizer.md) — Optimise query performance
Analyses slow queries, recommends and implements indexes, rewrites inefficient queries, and reviews execution plans. Works across PostgreSQL, MySQL, SQLite, and SQL Server.

**Use when:** Queries are slow, database CPU/IO is high, or you need to prepare a database for higher traffic.

### [**orm-model-builder**](orm-model-builder.md) — Generate ORM models from schemas
Generates ORM model definitions (SQLAlchemy, Prisma, ActiveRecord, Hibernate, GORM, etc.) from database schema definitions or ERDs. Includes relationships, validations, and lifecycle hooks.

**Use when:** Starting a new project with an existing schema, after generating a migration, or when adding a new ORM to a project.

### [**postgres-pro**](postgres-pro.md) — PostgreSQL specialist
Deep PostgreSQL expertise covering advanced features — JSONB, full-text search, window functions, CTEs, partitioning, replication, extensions, and performance tuning specific to PostgreSQL.

**Use when:** You need PostgreSQL-specific features or optimisations beyond general SQL, or are setting up a production PostgreSQL configuration.

### [**schema-migrator**](schema-migrator.md) — Write and validate database migration scripts
Produces safe, idempotent, and reversible database migration scripts with up and down migrations. Validates that migrations are safe to apply and won't cause data loss.

**Use when:** Adding, removing, or modifying database tables, columns, indexes, or constraints in a project that uses migration-based schema management.

### [**seed-data-generator**](seed-data-generator.md) — Generate realistic seed data
Creates realistic, domain-appropriate seed and test data using factories, faker libraries, and relational integrity constraints. Generates SQL seeds, fixture files, or factory definitions.

**Use when:** Setting up a development environment with meaningful data, creating test fixtures, or generating data for demos and staging environments.

## Quick Selection Guide

| Task | Subagent | Notes |
|------|----------|-------|
| Build a data pipeline or ETL | **data-engineer** | dbt, Spark, Airflow, Kafka, cloud data platforms |
| Validate API or pipeline inputs | **data-validator** | Schema validation, sanitisation, quality rules |
| Speed up slow queries | **database-optimizer** | Index recommendations, query rewrites, explain plans |
| Generate ORM models | **orm-model-builder** | Prisma, SQLAlchemy, ActiveRecord, Hibernate, GORM |
| PostgreSQL-specific features | **postgres-pro** | JSONB, partitioning, full-text search, extensions |
| Write database migration scripts | **schema-migrator** | Safe, reversible up/down migrations |
| Create development seed data | **seed-data-generator** | Factories, faker, relational integrity |

## Common Combinations

**"Add a new feature requiring a schema change"**
- **schema-designer** (Architecture category) → ERD → **schema-migrator** → migration script → **orm-model-builder** → updated models → **seed-data-generator** → test data.

**"Optimise a slow reporting query"**
- **database-optimizer** → index and query recommendations → **postgres-pro** → PostgreSQL-specific optimisations → **data-validator** → add query input validation.

**"Build a data warehouse layer"**
- **data-engineer** → pipeline and warehouse design → **schema-migrator** → warehouse schema migrations → **seed-data-generator** → sample data for development.

**"Set up a new project's database"**
- **schema-migrator** → initial schema migrations → **orm-model-builder** → ORM models → **seed-data-generator** → development data → **database-optimizer** → initial index recommendations.

## Getting Started

1. **Always backup before migrating** — Before running any migration, ensure you have a tested backup recovery procedure.
2. **Test migrations in development first** — Run `schema-migrator` output against a dev database before staging or production.
3. **Review execution plans** — For optimisation work, share `EXPLAIN ANALYZE` output with `database-optimizer`.
4. **Keep migrations reversible** — Always write down migrations alongside up migrations to enable rollback.
5. **Use seed data generously** — Rich seed data from `seed-data-generator` makes development and testing far more effective.
