# Data Science & AI/ML Subagents

Data Science & AI/ML subagents build and operate machine learning models, data analysis workflows, and AI-powered systems. They cover the full ML lifecycle from exploration and modelling through to production deployment and monitoring. Because these agents deal with model training, data pipelines, and AI system design, their outputs should be reviewed carefully — model bugs can silently produce incorrect results.

**Risk Tier: 🟠 Tier 3 — Medium-High** — Builds ML models, data pipelines, and AI systems that affect data quality and model outputs. Review model behaviour and evaluation metrics before deployment.

## When to Use Data Science & AI/ML Agents

Use these subagents when you need to:
- **Build AI features** — Integrate LLMs, computer vision, or ML models into applications
- **Analyse data** — Explore datasets, produce insights, and create visualisations
- **Train ML models** — Design, implement, and evaluate machine learning models
- **Design AI architectures** — Plan LLM systems, RAG pipelines, and agent architectures
- **Operationalise ML** — Deploy models, manage lifecycles, and monitor drift
- **Build NLP systems** — Implement text classification, extraction, generation, and search

## Available Subagents

### [**ai-engineer**](ai-engineer.md) — Build AI-powered features and applications
Integrates AI capabilities (LLMs, computer vision, speech, recommendation) into applications. Handles API integration, prompt management, output parsing, error handling, and cost optimisation.

**Use when:** Adding AI features to a product — chatbots, content generation, image analysis, semantic search, or recommendation systems.

### [**data-analyst**](data-analyst.md) — Analyse datasets and produce insights
Explores and analyses datasets to produce actionable insights, statistical summaries, and visualisations. Works with pandas, R, SQL, and BI tools to answer business questions with data.

**Use when:** You have data and questions — revenue trends, user behaviour, A/B test results, cohort analysis, or ad hoc exploratory analysis.

### [**data-scientist**](data-scientist.md) — Statistical modelling and hypothesis testing
Applies statistical methods to design experiments, test hypotheses, build predictive models, and quantify uncertainty. Expert in experimental design, significance testing, and Bayesian methods.

**Use when:** Running A/B tests, validating product hypotheses, building statistical models, or conducting rigorous quantitative analysis.

### [**llm-architect**](llm-architect.md) — Design LLM-based systems and RAG pipelines
Designs system architectures for LLM-powered applications — RAG pipelines, agent frameworks, multi-modal systems, fine-tuning strategies, and evaluation frameworks.

**Use when:** Building a complex AI system involving retrieval, agents, tool use, or multi-step reasoning and you need architectural guidance.

### [**machine-learning-engineer**](machine-learning-engineer.md) — Build, train, and deploy ML models
Implements end-to-end ML solutions — feature engineering, model selection, training pipelines, hyperparameter tuning, and deployment. Works with scikit-learn, PyTorch, TensorFlow, and XGBoost.

**Use when:** Building a custom ML model for classification, regression, clustering, or ranking tasks.

### [**ml-engineer**](ml-engineer.md) — End-to-end ML pipeline development
Focuses on the engineering quality of ML systems — reproducibility, testing, versioning, and scalable training pipelines. Applies software engineering best practices to ML code.

**Use when:** Your ML code needs engineering rigour — proper testing, versioning, reproducibility, and pipeline architecture.

### [**mlops-engineer**](mlops-engineer.md) — ML model lifecycle and monitoring
Manages the operational aspects of ML — model serving, versioning, A/B testing, drift detection, retraining pipelines, and monitoring. Works with MLflow, Seldon, BentoML, and cloud ML platforms.

**Use when:** Deploying models to production, setting up monitoring for model drift, or building automated retraining pipelines.

### [**nlp-engineer**](nlp-engineer.md) — Natural language processing models and pipelines
Implements NLP systems — text classification, named entity recognition, sentiment analysis, summarisation, translation, and semantic search. Works with Hugging Face, spaCy, and LLM APIs.

**Use when:** Building any system that processes, understands, or generates natural language text.

## Quick Selection Guide

| Task | Subagent | Notes |
|------|----------|-------|
| Add AI features to an app | **ai-engineer** | LLM/CV/speech integration, cost-effective |
| Analyse a dataset for insights | **data-analyst** | Pandas, R, SQL, visualisations |
| Run A/B tests or experiments | **data-scientist** | Experimental design, significance testing |
| Design an LLM or RAG system | **llm-architect** | Architecture for complex AI systems |
| Train a custom ML model | **machine-learning-engineer** | Feature engineering, model training, deployment |
| Make ML code production-ready | **ml-engineer** | Testing, reproducibility, pipeline quality |
| Deploy and monitor ML in production | **mlops-engineer** | Serving, drift detection, retraining |
| Build NLP text processing | **nlp-engineer** | Classification, NER, semantic search |

## Common Combinations

**"Build an AI-powered search feature"**
- **llm-architect** → RAG pipeline design → **ai-engineer** → implementation → **nlp-engineer** → embedding and retrieval → **data-analyst** → evaluate relevance metrics.

**"Ship an ML model to production"**
- **machine-learning-engineer** → model development → **ml-engineer** → production engineering → **mlops-engineer** → serving and monitoring.

**"Run a product experiment"**
- **data-scientist** → experimental design → **data-analyst** → results analysis → **business-analyst** (Business category) → business impact assessment.

**"Build a chatbot feature"**
- **llm-architect** → conversation architecture → **ai-engineer** → implementation → **prompt-engineer** (DX category) → optimise prompts → **data-analyst** → monitor conversation quality.

## Getting Started

1. **Define your evaluation metric** — Before building any ML system, decide how you'll measure success.
2. **Start with analysis** — Use **data-analyst** to understand your data before training models.
3. **Design before building** — Use **llm-architect** for complex AI systems before implementation.
4. **Always evaluate models** — Never ship an ML model without baseline evaluation metrics.
5. **Monitor after deployment** — Use **mlops-engineer** to set up drift detection and performance monitoring.
