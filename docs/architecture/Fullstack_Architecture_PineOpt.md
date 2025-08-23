# PineOpt Full-Stack Architecture

## 1. Introduction

- **Purpose**: Define the end-to-end architecture for PineOpt across frontend, backend, data, conversion engine, backtesting/research, security, and deployment, aligned with current PRDs and epic architecture plans.
- **Scope**:
  - In scope: UI/UX (React/Vite/TS), REST API surface (Flask), Pine conversion engine (Epic 6 AST-based target), backtesting/analysis (Epic 5), market data (Binance/Tardis; TradingView planned), data models, security, observability, deployment topology, and NFRs.
  - Out of scope (now): Exchange execution, enterprise SSO/RBAC, advanced data catalog UI, HFT/ultra-low-latency.
- **Objectives**:
  - Deliver AST-driven Pine→Python conversion with measurable accuracy, feature coverage, and performance targets.
  - Provide robust backtesting/analysis with reproducible research workflows and parameter sweeps.
  - Expose reliable market data ingestion and normalized OHLC APIs with caching.
  - Ensure sandboxed execution, validation, and resource governance.
  - Enable modular components and CI/CD-ready deployment.
- **Product Context & Alignment**:
  - Comprehensive Strategy Analysis Engine PRD: `documentation/PRD_Comprehensive_Strategy_Analysis_Engine.md`
  - Epic 6 Advanced Pine Conversion PRD & Architecture: `documentation/PRD_Epic6_Advanced_Pine_Conversion.md`, `documentation/Epic6_Architecture_Design.md`
  - Epic 5 Strategy Execution & Backtesting: `documentation/Epic5_Architecture_Design.md`, `documentation/PRD_Epic5_Strategy_Execution_Backtesting.md`
  - TradingView Data Integration plan: `documentation/Build_Plan_TradingView_Data_Integration.md`
  - Research skeleton: `documentation/Python_Research_Skeleton_Guide.md`
  - Master Architecture Plan: `documentation/ARCHITECTURE_PLAN_v1.0.md`
- **Stakeholders**: Quant researchers, strategy developers, frontend engineers, backend/infra, PM.
- **Success Metrics**:
  - Conversion: ≥95% semantic equivalence, ≥80% v6 feature coverage, <2× Pine runtime, API <5s.
  - Analysis: reproducible runs; regime-aware reports across ≥3 instruments × ≥3 years.
  - Platform: 99.9% uptime for conversion service; scale to 100+ concurrent conversions.
- **Constraints/Assumptions**: Python 3.10+, Flask backend, React/Vite/TS frontend, OHLC-only baseline features, sandboxed execution.

## 2. High-Level Architecture

- **Frontend (Web UI)**
  - Location: `src/` (React + Vite + TypeScript).
  - Components: e.g., `src/components/AIStrategyDashboard.tsx`, `src/components/AssetChartView.tsx`.
  - Integrates via REST using `src/config/api.ts`; renders charts from normalized OHLC JSON.

- **API Layer (Flask)**
  - Entry: `api/server.py` with Blueprints for modular routing.
  - Registered blueprints (as available):
    - `database_routes`, `enhanced_data_routes`, `futures_routes`
    - `strategy_routes`, `backtest_routes`, `real_backtest_routes`
    - `ai_analysis_routes`, `ai_conversion_routes`, `intelligent_conversion_routes`
    - Market data: `market_routes` under `/api/market/*`
  - Core endpoints (MVP):
    - Conversion: `POST /api/convert-pine`, `POST /api/strategies/upload`
    - Strategy CRUD: `GET/POST /api/strategies`, `GET /api/strategies/<id>`
    - Market data: `GET /api/crypto/ohlc` with compatibility shims under `/api/tv/*`

- **Conversion Engine**
  - Current: template/pattern-based via `pine2py.codegen.PythonCodeGenerator` (invoked in `api/server.py`).
  - Target (Epic 6): AST pipeline (PyNescript → semantic analysis → Python AST → codegen), validation and analytics per `documentation/Epic6_Architecture_Design.md`.

- **Backtesting & Research**
  - Location: `research/` (features, regimes, sweeps, backtest runners).
  - Artifacts under `outputs/` (datasets, features, sweeps, reports); reproducible CLI per `documentation/Python_Research_Skeleton_Guide.md`.

- **Data Providers**
  - Crypto: `research/data/providers/binance_provider.py` (live), `research/data/providers/tardis_provider.py` (fallback).
  - Planned: `research/data/providers/tradingview_provider.py` using `tvdatafeed`, caching to `outputs/datasets/tradingview/`, API `GET /api/tv/ohlc` (compat already routed to `/api/crypto/ohlc`).

- **Storage**
  - Local API DB: `api/strategies.db` (created via `init_database()` in `api/server.py`).
  - Main DB: `database/pineopt.db` (strategy records for backtesting integration).
  - Filesystem artifacts: `outputs/` for caching and reproducibility.

- **Security & Execution**
  - Current: input validation, compile checks; route-level error handling.
  - Planned: sandboxed execution, AST-level security validation, resource limits (CPU/Memory/timeouts) for conversion and strategy runs.

- **Observability**
  - Logging via `logging`; artifact/log storage under `outputs/`.
  - Planned: conversion analytics endpoints, metrics and dashboarding.

- **Primary Flows**
  1) Upload Pine → Convert → Validate → Save → List/View → Backtest → Report
  2) Fetch OHLC (Binance/Tardis → TradingView planned) → Cache → Serve to UI → Chart/Analysis

- **External Integrations**
  - Market data: Binance, Tardis.dev, TradingView (planned per build plan).
  - CI/CD: GitHub Actions (`.github/workflows/ci-cd.yml`).

## 3. Tech Stack & Rationale

- **Frontend**: React + Vite + TypeScript, TailwindCSS
  - Fast dev feedback loop; type-safe UI; suitable for data-heavy dashboards.

- **Backend**: Flask + Blueprints + CORS
  - Matches existing `api/server.py` implementation; lightweight and easy to extend.
  - For heavy I/O/concurrency: add a task queue (RQ/Celery) and/or adjunct async services if needed.

- **Python Libraries**
  - Data/analytics: `pandas`, `numpy`, `scipy`, `scikit-learn` (per `requirements.txt`).
  - Backtesting/reporting: vectorized approaches and QuantStats-style reporting (see research guide).
  - Testing/CI: `pytest` with GitHub Actions.

- **Conversion Engine**
  - Current MVP: `pine2py` codegen templates.
  - Target: PyNescript-driven Pine AST → semantic analysis → Python AST (`ast`/`ast-tools`) → codegen with coverage/accuracy metrics.
  - Rationale: correctness and maintainability across Pine v5/v6.

- **Data Integration**
  - Binance (live) + Tardis.dev (fallback), `tvdatafeed` planned.
  - Normalized OHLC JSON for UI; Parquet cache in `outputs/` for research pipelines.

- **Datastores**
  - SQLite for MVP simplicity (local dev and small-team scale). Future: Postgres when multi-user concurrency grows.

- **Deployment**
  - MVP: docker-compose on a single VM: backend (Flask + Gunicorn), frontend (Vite build behind Nginx), optional worker; bind volumes for `outputs/`.
  - Growth: container images with env-based config; optional K8s for autoscaling conversion workers.

- **Security**
  - Env-based secrets; input validation; basic rate limiting; no secret logging.
  - Planned: sandboxing for user-supplied code; AST checks for unsafe constructs.

- **Observability**
  - Structured logs; conversion analytics endpoints. Future: Prometheus/Grafana, Sentry.

## 4. Data Models (Current DB Schema)

- **Strategies (`strategies`)**
  - Columns: `id`, `name`, `description`, `author`, `language` (pine|python), `file_path`, `parameters_json`, `dependencies_json`, `validation_status`, `usage_stats_json`, `created_at`, `updated_at`.
  - Notes: JSON fields for parameters, dependencies, usage stats; validation status enum.

- **Strategy Parameters (`strategy_parameters`)**
  - Columns: `id`, `strategy_id` FK→`strategies.id`, `name`, `type`, `default_value`, `min_value`, `max_value`, `options_json`, `required`.
  - Notes: Typed parameter definitions with validation ranges/options.

- **Strategy Dependencies (`strategy_dependencies`)**
  - Columns: `id`, `strategy_id` FK, `package`, `version_spec`.

- **Strategy Validations (`strategy_validations`)**
  - Columns: `id`, `strategy_id` FK, `status`, `errors_json`, `warnings_json`, `summary`, `created_at`.

- **Strategy Tags (`strategy_tags`, `tags`)**
  - Join table to many-to-many `tags` for organization and filtering.

- **Backtests (`backtests`)**
  - Columns: `id`, `strategy_id` FK, `engine` (e.g., basic/vectorized), `symbol`, `timeframe`, `start`, `end`, `capital`, `commission`, `slippage`, `risk_config_json`, `params_json`, `status`, `created_at`.

- **Backtest Results (`backtest_results`)**
  - Columns: `id`, `backtest_id` FK, `equity_curve_json`, `performance_json`, `risk_json`, `orders_json`, `metrics_json`, `report_path`, `created_at`.
  - Notes: Stores summary stats and references to artifacts.

- **Backtest Trades (`backtest_trades`)**
  - Columns: `id`, `backtest_id` FK, `timestamp`, `symbol`, `side`, `qty`, `price`, `fee`, `pnl`, `meta_json`.

- **Optimization Campaigns & Iterations (`optimization_campaigns`, `optimization_iterations`)**
  - Campaigns: `id`, `strategy_id` FK, `objective`, `space_json`, `status`, `created_at`.
  - Iterations: `id`, `campaign_id` FK, `params_json`, `metrics_json`, `rank`, `created_at`.

- **Conversions (`conversions`)**
  - Columns: `id`, `source_language`, `target_language`, `input_path`, `output_path`, `analysis_json`, `validation_json`, `score`, `status`, `created_at`.

- **Market Data (`ohlc`)**
  - Columns: `id`, `symbol`, `exchange`, `timeframe`, `timestamp`, `open`, `high`, `low`, `close`, `volume`.
  - Indexes on `(symbol, exchange, timeframe, timestamp)`.

- **Data Sources (`data_sources`)**
  - Columns: `id`, `name`, `type`, `config_json`, `status`, `created_at`.

- **Data Sessions (`data_sessions`)**
  - Columns: `id`, `source_id` FK, `symbol`, `timeframe`, `start`, `end`, `status`, `artifact_path`, `stats_json`.

- **Activity Logs (`activity_logs`)** and **System Stats (`system_stats`)**
  - Structured audit trail and system-level metrics; JSON payloads for flexibility.

References: see `database/schema.sql`, `database/strategy_schema.sql`, and ORM models in `database/models.py` for full definitions, constraints, and indexes.

## 5. API Specification (Current Endpoints)

- **Base**: Flask blueprints under `api/`. Key files: `api/strategy_routes.py`, `api/backtest_routes.py`, `api/ai_conversion_routes.py`, `api/market_routes.py`.

- **Strategy Management (`/api/strategies`)**
  - `POST /api/strategies/upload` — Upload strategy file (.py|.pine). Validates filename, extracts metadata/params.
  - `GET /api/strategies` — List strategies with optional filters.
  - `GET /api/strategies/<id>` — Retrieve strategy details including parameters and validation.
  - `PUT /api/strategies/<id>` — Update metadata/parameters.
  - `DELETE /api/strategies/<id>` — Delete strategy and related records.
  - `POST /api/strategies/<id>/validate` — Run syntax/security/dependency validation.
  - `POST /api/strategies/<id>/profile` — AI-powered profiling/summary for the strategy.
  - `GET /api/strategies/health` — Health check.

- **Backtesting (`/api/backtests`)**
  - `POST /api/backtests/run` — Run backtest with payload: `symbol`, `timeframe`, `start`, `end`, `capital`, `commission`, `slippage`, `risk`, and `strategy_params`.
  - `GET /api/backtests/<id>` — Get backtest results (performance, risk, charts metadata).
  - `GET /api/backtests` — List backtests with filters (by strategy, date range, status).
  - `GET /api/backtests/<id>/stats` — Summary statistics and metrics.
  - `GET /api/backtests/<id>/chart` — Equity curve and charting data.
  - `DELETE /api/backtests/<id>` — Delete backtest.
  - `GET /api/backtests/latest/<strategy_id>` — Latest backtest for a strategy.
  - `POST /api/backtests/attribution` — Performance attribution analysis.
  - `POST /api/backtests/compare` — Compare multiple backtests.

- **AI Conversion & Analysis (`/api/convert`, `/api/ai`)**
  - `GET /api/ai/health` — Health check.
  - `POST /api/ai/analyze` — Analyze Pine script features and complexity.
  - `POST /api/convert-pine` — Convert Pine Script → Python using converter pipeline.
  - `POST /api/ai/validate` — Validate converted code; returns scores and issues.
  - `GET /api/ai/ui-config` — Retrieve UI configuration descriptors for strategy params.
  - `GET /api/ai/capabilities` — Report supported language features and limits.

- **Market Data (`/api/market`)**
  - `GET /api/market/overview` — Market overview snapshot.
  - `GET /api/market/ticker/<symbol>` — Live ticker for a symbol.
  - `POST /api/market/tickers` — Batch tickers for multiple symbols.
  - `GET /api/market/ohlcv` — Historical OHLCV with `symbol`, `timeframe`, `start`, `end`.
  - `GET /api/market/top-pairs` — Top trading pairs.
  - `GET /api/market/status` — Market service status.
  - `GET /api/market/health` — Health check.

Notes:
- Inputs and outputs are JSON. Large payload protections and basic rate limiting exist on AI routes.
- Pagination and filtering supported on list endpoints where applicable.

---

Elicitation checkpoints for next sections:
- Deployment target confirmation: docker-compose MVP on single VM first?
- Initial data defaults: which symbols/exchanges/timeframes for demos?
- AST engine rollout: enable fallback to current converter for unsupported v6 features in Phase 1?
