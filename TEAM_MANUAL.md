# Team Manual — SIH Financial Network Intelligence

## 1. What this project is

The project is a baseline investigation platform for:

> **Explainable Financial Network Intelligence for Detection and Investigation of Mule Networks**

Its investigation workflow is:

> **DISCOVER → CONNECT → TRACE → EXPLAIN → PRIORITIZE**

The current repository demonstrates how an investigator could examine potential financial-risk networks. It is a modular engineering foundation, not a finished fraud-detection product.

Important guardrails:

- All accounts, transactions, networks, cases, scores, and metrics are synthetic.
- A risk signal does not establish criminal guilt.
- The project does not replace I4C infrastructure, RBIH MuleHunter.ai, or another government system.
- No database or real machine-learning model is currently connected.

## 2. Current project status

The baseline currently includes:

- React, TypeScript, and Vite frontend
- FastAPI and Python backend
- 40 synthetic accounts
- 120 internally connected transactions
- 4 synthetic potential mule networks
- 12 synthetic investigation cases
- Multi-hop money-flow traces
- Investigation status management
- Demonstration fraud simulation
- Mock model-performance metrics
- System and module status reporting
- Plug-and-play intelligence-engine contracts
- In-memory repository contracts and implementations
- Automated backend tests
- Docker support

The following are intentionally not implemented:

- Real XGBoost model
- Real feature engineering
- Real graph analytics or graph database
- Real risk-fusion logic
- SHAP explanations
- Persistent database
- Authentication and authorization
- Real financial or personal information
- Production fraud-simulation algorithms

## 3. Quick start

### Important: every teammate must start two applications

This repository contains two separate local development processes:

1. The FastAPI backend on port `8000`
2. The React frontend on port `5173`

Starting only the frontend will display:

```text
Intelligence service unavailable
Failed to fetch. Start the FastAPI backend on port 8000, then retry.
```

This is expected when the browser cannot reach the backend. Every teammate must keep both terminal processes running while using the website locally.

Open two PowerShell terminals in the repository root.

### Backend terminal

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

The backend runs at:

- API: `http://localhost:8000`
- Swagger documentation: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/health`

### Frontend terminal

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Open `http://localhost:5173` in a browser.

`npm.cmd` is recommended on Windows because PowerShell execution policy may block `npm.ps1`.

### Confirm both services are working

Before investigating another problem, open these URLs:

- `http://localhost:8000/health` must return a JSON response containing `"status": "healthy"`.
- `http://localhost:5173` must display the investigation dashboard.

If `/health` does not open, the backend is not running correctly. Read the error shown in the backend terminal.

### One-command Docker alternative

If Docker Desktop is installed, both services can be started together from the repository root:

```powershell
docker compose up --build
```

Docker still runs two services internally, but the teammate only needs one command. The frontend is available at `http://localhost:5173` and the backend at `http://localhost:8000`.

## 4. Repository map

```text
MuleDestroyer/
├── backend/
│   ├── app/
│   │   ├── api/                 FastAPI routes and router registration
│   │   ├── config/              Environment settings and logging
│   │   ├── data/                Connected synthetic dataset
│   │   ├── dependencies/        Central dependency wiring
│   │   ├── engines/
│   │   │   ├── interfaces/      Intelligence contracts
│   │   │   └── mock/            Current deterministic implementations
│   │   ├── exceptions/          Structured API error handling
│   │   ├── explainability/      Human-readable explanation boundary
│   │   ├── repositories/
│   │   │   ├── interfaces/      Storage contracts
│   │   │   └── memory/          Current process-local storage
│   │   ├── schemas/             Pydantic API contracts
│   │   ├── services/            Application and workflow logic
│   │   └── main.py              FastAPI application entry point
│   ├── tests/                   API, engine, and repository tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          Reusable layout, UI, and visualizations
│   │   ├── pages/               Route-level screens
│   │   ├── services/            Central API and domain service modules
│   │   ├── types/               TypeScript API contracts
│   │   ├── utils/               Shared helpers
│   │   ├── App.tsx              Route definitions
│   │   ├── main.tsx             React entry point
│   │   └── styles.css           Design system and responsive styling
│   └── package.json
├── ARCHITECTURE.md              Technical boundaries and future adapters
├── CONTRIBUTING.md              Contribution rules
├── TEAM_MANUAL.md               This guide
├── Dockerfile.backend
├── Dockerfile.frontend
└── docker-compose.yml
```

## 5. How a request moves through the system

When a new transaction is submitted, it follows this conceptual path:

```text
React page
    ↓
Frontend domain service
    ↓
FastAPI route
    ↓
TransactionService
    ↓
FeatureEngine interface
    ↓
XGBoostEngine interface
    ↓
GraphEngine interface
    ↓
FraudIntelligenceEngine interface
    ↓
ExplainabilityService
    ↓
Typed RiskResult response
    ↓
Investigation UI
```

The route must not contain intelligence logic. The frontend must not call the API directly from every component. These boundaries allow the mock implementations to be replaced later without redesigning the application.

## 6. Backend guide

### Application entry point

`backend/app/main.py` creates the FastAPI application, configures CORS, logging, request timing, exception handlers, API routes, `/docs`, and `/redoc`.

### API routes

Routes live in `backend/app/api/routes/`. Their job is limited to:

1. Accept and validate a request.
2. Receive a service through FastAPI dependency injection.
3. Call the service.
4. Return a typed response.

Do not place feature extraction, risk calculations, or repository operations directly in a route.

### Schemas

`backend/app/schemas/models.py` defines the public API contracts. Important schemas include:

- `Transaction`
- `Account`
- `Network`, `NetworkNode`, and `NetworkEdge`
- `RiskResult` and `RiskSignal`
- `Investigation`
- `MoneyFlow` and `MoneyFlowHop`
- `Simulation` and `SimulationRound`
- `ModelMetrics`
- `SystemStatus`

Whenever an API contract changes, update the equivalent TypeScript type in `frontend/src/types/index.ts`.

### Services

`backend/app/services/core.py` contains the orchestration and workflow layer. Major services include:

- `TransactionService`
- `EntityService`
- `InvestigationService`
- `TracingService`
- `SimulationService`
- `BehaviourProfiler`
- `NetworkDiscoveryService`
- `InvestigationPriorityService`
- `InvestigationReportService`

Services may coordinate engines and repositories. Routes should delegate to these services.

### Dependency wiring

`backend/app/dependencies/services.py` is the composition root. It decides which implementation is used for every interface.

For example, it currently returns:

```python
def get_graph_engine():
    return MockGraphEngine()
```

This is the main file that will change when real engines or persistent repositories are introduced.

## 7. Synthetic data guide

The connected synthetic dataset is generated in:

```text
backend/app/data/synthetic.py
```

It creates:

- `TRANSACTIONS`
- `ACCOUNTS`
- `NETWORKS`
- `INVESTIGATIONS`
- `EXPLANATION`
- Money-flow traces through `build_trace()`

The data is deterministic, which means restarting the server produces the same baseline records.

### Internal consistency rule

Synthetic data must remain connected:

- A network edge must refer to an existing transaction.
- A transaction source and destination must refer to existing accounts.
- An investigation must refer to existing accounts, transactions, and networks.
- A trace must use valid transaction references.

Do not create separate, unrelated mock arrays inside frontend components. The backend synthetic dataset should remain the primary source of truth.

### Safe identifiers

Continue using identifiers such as:

```text
ACC-0001
TXN-0001
NET-001
CASE-0001
SIM-AB12CD34
```

Never introduce real names, bank-account numbers, UPI IDs, phone numbers, credentials, or financial records.

## 8. Intelligence-engine contracts

The four major contracts live in `backend/app/engines/interfaces/`.

### FeatureEngine

Future responsibility:

- Transaction and behavioral features
- Velocity and frequency
- Incoming/outgoing ratios
- Pass-through behavior
- Graph-derived features

Current implementation: `MockFeatureEngine`.

### XGBoostEngine

Future responsibility:

- Load a trained model
- Score feature vectors
- Return model metadata
- Eventually provide SHAP-compatible information

Current implementation: `MockXGBoostEngine`. XGBoost is not installed.

### GraphEngine

Future responsibility:

- Graph construction and neighborhoods
- Path finding and hop analysis
- Cluster discovery
- Fan-in, fan-out, cycles, and centrality
- Money-flow support

Current implementation: `MockGraphEngine`. No Neo4j or graph database is installed.

### FraudIntelligenceEngine

Future responsibility:

- Combine model, graph, behavioral, and rule signals
- Calculate final risk
- Assign severity and investigation priority
- Connect intelligence results to cases

Current implementation: `MockFraudIntelligenceEngine`.

## 9. Replacing a mock engine

Suppose a team member implements a real graph engine.

1. Create a new implementation package, such as:

   ```text
   backend/app/engines/real/graph_engine.py
   ```

2. Make it inherit from `GraphEngine`.
3. Implement all abstract methods using the existing return contract.
4. Add unit tests for the implementation.
5. Update only the provider in `backend/app/dependencies/services.py`:

   ```python
   def get_graph_engine() -> GraphEngine:
       return RealGraphEngine(...)
   ```

6. Run the API tests and frontend build.

The API routes and frontend should not require changes. Apply the same process to the other engines.

## 10. Repository and database policy

Repository contracts are in:

```text
backend/app/repositories/interfaces/repositories.py
```

Current implementations are in:

```text
backend/app/repositories/memory/repositories.py
```

They store data in application memory. Changes disappear when the backend restarts.

The database is intentionally on hold. Do not independently introduce:

- PostgreSQL
- MySQL
- MongoDB
- Neo4j
- Redis
- SQLAlchemy
- Database migrations

A future storage adapter should implement a repository interface and be selected through dependency wiring. Business services must not depend directly on a database library.

## 11. Frontend guide

### Routing

Routes are defined in `frontend/src/App.tsx`:

| Route | Purpose |
|---|---|
| `/dashboard` | Intelligence overview |
| `/networks` | Discovered network list |
| `/networks/:id` | Interactive network investigation |
| `/tracing` | Multi-hop money-flow tracing |
| `/transactions` | Transaction explorer |
| `/accounts` | Account explorer |
| `/accounts/:id` | Account risk and explanation |
| `/investigations` | Case priority queue |
| `/investigations/:id` | Investigation workspace |
| `/simulation` | Synthetic simulation |
| `/model-performance` | Mock performance metrics |
| `/system-status` | Implementation and readiness status |

### API access

`frontend/src/services/api.ts` is the only low-level HTTP client. Domain services are exported from `frontend/src/services/index.ts`.

Components and pages should call functions such as:

```typescript
accountService.get(accountId)
networkService.get(networkId)
tracingService.trace(transactionId)
investigationService.status(caseId, status)
```

Do not scatter direct `fetch()` calls throughout components.

### Reusable components

Important shared UI components include:

- `AppShell`
- `MetricCard`
- `RiskBadge`
- `DemoLabel`
- `PageHeader`
- `Panel`
- `LoadingState`
- `ErrorState`
- `EmptyState`
- `NetworkGraph`
- `MoneyFlowView`
- Dashboard charts

Use these before creating slightly different copies on individual pages.

### Styling

The baseline design system is in `frontend/src/styles.css`. It defines:

- Color and spacing tokens
- Cards and panels
- Tables and filter bars
- Risk and status badges
- Graph and tracing surfaces
- Desktop, tablet, and mobile breakpoints

Risk colors should stay consistent:

- `LOW`: green
- `MEDIUM`: blue
- `HIGH`: amber
- `CRITICAL`: red

Every mock or simulated result must remain visibly labeled as `DEMO`, `MOCK`, `SYNTHETIC`, or `SIMULATED`.

## 12. Primary demonstration flow

Use this sequence during an SIH demonstration:

1. Open the dashboard and describe the top intelligence metrics.
2. Open **Network Investigation**.
3. Select `NET-001 — Cascade Relay`.
4. Select an account node in the network map.
5. Open the account profile.
6. Explain the synthetic risk factors.
7. Select **Trace Money**.
8. Trace `TXN-0001` to show the branching three-hop flow.
9. Open an investigation from the queue.
10. Review its priority, network, flow, explanation, and evidence.
11. Update the investigation status.
12. Generate the structured demonstration report preview.
13. Run a synthetic fraud simulation.
14. Open model performance and clarify that metrics are placeholders.
15. Open system status and show that every intelligence module is currently `MOCK` or `IN-MEMORY`.

## 13. API reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Basic service health |
| GET | `/api/v1/system/status` | Module implementation status |
| GET | `/api/v1/transactions` | List transactions |
| GET | `/api/v1/transactions/{id}` | Get one transaction |
| POST | `/api/v1/transactions` | Run a transaction through the mock pipeline |
| GET | `/api/v1/accounts` | List accounts |
| GET | `/api/v1/accounts/{id}` | Get one account |
| GET | `/api/v1/networks` | List networks |
| GET | `/api/v1/networks/{id}` | Get a network and graph |
| GET | `/api/v1/risk/{account_id}` | Assess account risk |
| POST | `/api/v1/risk-check` | Assess an account or transaction |
| GET | `/api/v1/trace/{transaction_id}` | Trace money flow |
| GET | `/api/v1/investigations` | List investigations |
| GET | `/api/v1/investigations/{case_id}` | Get one investigation |
| POST | `/api/v1/investigations` | Create an investigation |
| PATCH | `/api/v1/investigations/{case_id}/status` | Update case status |
| GET | `/api/v1/investigations/{case_id}/report` | Generate structured report data |
| POST | `/api/v1/simulation/start` | Run synthetic simulation |
| GET | `/api/v1/simulation/{simulation_id}` | Retrieve a simulation |
| GET | `/api/v1/model/metrics` | Retrieve placeholder metrics |

Use `http://localhost:8000/docs` to inspect request bodies and test endpoints interactively.

## 14. Testing and validation

### Backend

```powershell
cd backend
python -m pytest -q
```

The current suite covers health, transactions, accounts, networks, risk, investigations, tracing, simulation, metrics, engine contracts, and repository behavior.

### Frontend

```powershell
cd frontend
npm.cmd run build
```

This runs strict TypeScript validation and creates the production Vite bundle.

Both commands should pass before code is merged.

## 15. Environment configuration

Example variables are documented in `.env.example`, `backend/.env.example`, and `frontend/.env.example`.

Important values:

```text
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:5173
LOG_LEVEL=INFO
API_PREFIX=/api/v1
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Never commit populated `.env` files or secrets.

## 16. Common troubleshooting

### PowerShell blocks `npm`

Use:

```powershell
npm.cmd install
npm.cmd run dev
```

### Frontend says the intelligence service is unavailable

This normally means the frontend is running but the backend is stopped or unreachable. Start it in a separate terminal:

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Keep that terminal open. Confirm the backend is running at `http://localhost:8000` by testing:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

If the health check succeeds but the frontend still fails, create or check `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Restart `npm.cmd run dev` after changing an environment file.

Also check the frontend terminal. If Vite selected port `5174` because `5173` was occupied, either free port `5173` or start the backend with the matching CORS origin:

```powershell
$env:FRONTEND_URL="http://localhost:5174"
python -m uvicorn app.main:app --reload --port 8000
```

Then open `http://localhost:5174`.

### Browser shows a CORS error

Confirm `FRONTEND_URL` in the backend environment exactly matches the frontend origin, normally `http://localhost:5173`.

### Changes disappear after restarting the backend

This is expected. Repositories are in-memory and intentionally non-persistent.

### A record returns `404`

Check the synthetic identifiers in `backend/app/data/synthetic.py`. API errors use a structured contract:

```json
{
  "error": {
    "code": "ACCOUNT_NOT_FOUND",
    "message": "Account ACC-9999 was not found."
  }
}
```

### Port already in use

Choose another backend port:

```powershell
python -m uvicorn app.main:app --reload --port 8001
```

Then update `VITE_API_BASE_URL` before starting the frontend.

## 17. Team ownership suggestions

The architecture supports parallel ownership without changing the boundaries:

| Area | Suggested ownership |
|---|---|
| Feature extraction and behavior | Feature/behavior team |
| XGBoost model and evaluation | ML team |
| Graph construction and discovery | Graph intelligence team |
| Risk fusion and prioritization | Fraud intelligence team |
| FastAPI contracts and repositories | Backend/platform team |
| Dashboard and investigation UX | Frontend team |
| Test fixtures and scenario quality | QA/simulation team |
| Risk language and evidence policy | Domain/research team |

Teams should integrate through contracts rather than directly importing each other's concrete implementations.

## 18. Contribution rules

- Keep routes thin and services focused.
- Use type hints and Pydantic/TypeScript contracts.
- Do not use real financial data.
- Do not present synthetic metrics as measured results.
- Preserve risk-versus-guilt language.
- Do not add a database without team agreement.
- Do not couple business services to mock implementations.
- Add tests for new API and engine behavior.
- Run backend tests and the frontend build before opening a pull request.
- Update this manual and `ARCHITECTURE.md` when boundaries change.

## 19. Recommended next phases

After the team reviews the baseline, recommended incremental phases are:

1. Improve synthetic scenario generation and test coverage.
2. Formalize feature and behavior contracts.
3. Implement a real feature engine behind `FeatureEngine`.
4. Train and integrate an evaluated model behind `XGBoostEngine`.
5. Add graph algorithms behind `GraphEngine`.
6. Design calibrated risk fusion and explanation contracts.
7. Add authentication and role boundaries.
8. Select storage only after access patterns and data governance are understood.
9. Add production observability and security review.

Each phase should preserve the current public API wherever practical.

## 20. Final reminder

The strongest architectural principle in this repository is separation of concerns:

> The frontend depends on API contracts, routes depend on services, services depend on interfaces, and dependency wiring selects implementations.

Maintaining that separation lets the team replace mock components gradually without rebuilding the entire project.
