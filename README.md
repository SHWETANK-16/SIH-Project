# SIH Financial Network Intelligence

A runnable baseline for **Explainable Financial Network Intelligence for Detection and Investigation of Mule Networks**. It is an investigator-facing research prototype built around:

> DISCOVER → CONNECT → TRACE → EXPLAIN → PRIORITIZE

Every account, transaction, signal, explanation, metric, and finding in this repository is **synthetic demonstration data**. Risk is an investigation signal—not a determination of guilt. This project does not replace I4C infrastructure, RBIH MuleHunter.ai, or any government system.

## What is included

- React 19 + TypeScript + Vite command-center interface
- FastAPI modular monolith with versioned, documented contracts
- 40 accounts, 120 connected transactions, 4 networks, 12 cases, and branching flows
- Engine interfaces with swappable implementations (NetworkX graph, statistical features, trained XGBoost)
- Trained XGBoost mule-risk model with exact TreeSHAP explanations and measured held-out metrics
- In-memory repositories behind repository contracts
- Network map, multi-hop trace, case workflow, simulator, metrics, and status views
- Structured errors, logging, CORS, configuration, tests, and Docker support

## Architecture

```text
React UI → /api/v1 routes → application services
                              ├─ FeatureEngine       → StatisticalFeatureEngine
                              ├─ XGBoostEngine       → XGBoostRiskEngine  (trained model + rules)
                              ├─ GraphEngine         → NetworkXGraphEngine
                              └─ FraudIntelligence   → MockFraudIntelligenceEngine
                           → Explainability → Investigation response

Repository interfaces → in-memory repositories (database intentionally absent)
```

Every engine sits behind an ABC, and each is swapped in exactly one place —
`app/dependencies/services.py`. That seam is how the mock implementations were
replaced without touching a route, and it is how the remaining mock would be.

See [ARCHITECTURE.md](ARCHITECTURE.md) for boundaries and replacement guidance.

**[OPERATING_GUIDE.md](OPERATING_GUIDE.md)** is the practical walkthrough: how to
start both halves, how to verify the whole stack, what every page does (and which
controls are decorative), how to create a case through the API, and troubleshooting.

New team members should begin with [TEAM_MANUAL.md](TEAM_MANUAL.md), which covers setup, workflows, file ownership, extension points, testing, and troubleshooting.

## Run locally

Backend (Python 3.11+):

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.ml.train_xgboost
uvicorn app.main:app --reload
```

The training step takes ~15-30s and writes `backend/model/`. You can skip it — the
engine trains itself on first boot if the artifact is missing, and falls back to
calibrated rules if `xgboost` isn't installed at all.

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
| Metrics | `GET /api/v1/model/metrics`, `GET /api/v1/model/features` |

## Validation

```powershell
cd backend; pytest
cd ..\frontend; npm run build
```

## Intentionally not implemented

No database, ORM, migrations, graph database, authentication, or production ML
pipeline. The simulator remains illustrative. These omissions preserve clean
integration seams for the next project phase.

The machine learning layer is no longer among them — see
[XGBOOST_INTEGRATION.md](XGBOOST_INTEGRATION.md). Risk scores come from a trained
XGBoost classifier blended with calibrated domain rules, explained with exact
TreeSHAP attribution, and `/api/v1/model/metrics` reports measured held-out
performance rather than placeholders. The model is trained on **synthetic
archetypes**, so the architecture is production-shaped while the numbers are not
production numbers — every response carries that caveat in its label.
