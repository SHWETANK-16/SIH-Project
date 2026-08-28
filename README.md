# SIH Financial Network Intelligence

A runnable baseline for **Explainable Financial Network Intelligence for Detection and Investigation of Mule Networks**. It is an investigator-facing research prototype built around:

> DISCOVER → CONNECT → TRACE → EXPLAIN → PRIORITIZE

Every account, transaction, signal, explanation, metric, and finding in this repository is **synthetic demonstration data**. Risk is an investigation signal—not a determination of guilt. This project does not replace I4C infrastructure, RBIH MuleHunter.ai, or any government system.

## What is included

- React 19 + TypeScript + Vite command-center interface
- FastAPI modular monolith with versioned, documented contracts
- 40 accounts, 120 connected transactions, 4 networks, 12 cases, and branching flows
- Engine interfaces with deterministic mock implementations
- In-memory repositories behind repository contracts
- Network map, multi-hop trace, case workflow, simulator, metrics, and status views
- Structured errors, logging, CORS, configuration, tests, and Docker support

## Architecture

```text
React UI → /api/v1 routes → application services
                              ├─ FeatureEngine       → MockFeatureEngine
                              ├─ XGBoostEngine       → MockXGBoostEngine
                              ├─ GraphEngine         → MockGraphEngine
                              └─ FraudIntelligence   → MockFraudIntelligenceEngine
                           → Explainability → Investigation response

Repository interfaces → in-memory repositories (database intentionally absent)
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for boundaries and replacement guidance.

New team members should begin with [TEAM_MANUAL.md](TEAM_MANUAL.md), which covers setup, workflows, file ownership, extension points, testing, and troubleshooting.

## Run locally

Backend (Python 3.11+):

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend (Node 20+), in another terminal:

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Open `http://localhost:5173`. API docs are at `http://localhost:8000/docs` and `/redoc`.

Docker alternative: `docker compose up --build` (frontend `:5173`, backend `:8000`). No database container is used.

## API surface

| Area | Endpoints |
|---|---|
| Health | `GET /health`, `GET /api/v1/system/status` |
| Transactions | `GET/POST /api/v1/transactions`, `GET /api/v1/transactions/{id}` |
| Accounts & risk | `GET /api/v1/accounts[/{id}]`, `GET /api/v1/risk/{id}`, `POST /api/v1/risk-check` |
| Networks | `GET /api/v1/networks[/{id}]` |
| Tracing | `GET /api/v1/trace/{transaction_id}` |
| Cases | `GET/POST /api/v1/investigations`, `GET /{case_id}`, `PATCH /{case_id}/status`, `GET /{case_id}/report` |
| Simulation | `POST /api/v1/simulation/start`, `GET /api/v1/simulation/{id}` |
| Metrics | `GET /api/v1/model/metrics` |

## Validation

```powershell
cd backend; pytest
cd ..\frontend; npm run build
```

## Intentionally not implemented

No database, ORM, migrations, real XGBoost model, SHAP, graph database/analytics, feature engineering, real risk fusion, authentication, or production ML pipeline. The simulator and performance metrics are illustrative. These omissions preserve clean integration seams for the next project phase.
