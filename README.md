# 🛡️ SIH Financial Network Intelligence

### Explainable Financial Network Intelligence for Detection & Investigation of Mule Networks

<p align="center">
<strong>DISCOVER → CONNECT → TRACE → EXPLAIN → PRIORITIZE</strong>
</p>

<p align="center">
An investigator-facing research prototype designed to uncover suspicious financial
networks by combining transaction intelligence, behavioural signals,
multi-hop tracing, explainability, and investigation workflows.
</p>

<p align="center">
<img src="https://img.shields.io/badge/Status-Research%20Prototype-blue" />
<img src="https://img.shields.io/badge/Frontend-React%2019-61DAFB" />
<img src="https://img.shields.io/badge/Backend-FastAPI-009688" />
<img src="https://img.shields.io/badge/Language-TypeScript%20%7C%20Python-blue" />
<img src="https://img.shields.io/badge/Data-Synthetic-orange" />
<img src="https://img.shields.io/badge/License-TBD-lightgrey" />
</p>

---

## 🎯 What is this?

**SIH Financial Network Intelligence** is a research-oriented prototype for
detecting and investigating potential **mule-account networks** within
financial transaction flows.

Instead of treating suspicious transactions as isolated events, the system
is designed around a network-first investigation approach:

> **Discover suspicious behaviour → Connect related accounts → Trace money flows → Explain the signals → Prioritize investigations**

The platform provides investigators with a command-center style interface
for exploring accounts, transactions, networks, multi-hop traces, cases,
simulation scenarios, model metrics, and system status.

---

## ⚠️ Important Disclaimer

> **This project uses synthetic demonstration data only.**

Every account, transaction, risk signal, explanation, metric, network,
case, and finding included in this repository is synthetic.

A risk score represents an **investigation signal**, not a determination
of guilt or criminal activity.

This research prototype does **not** replace, replicate, or claim integration
with:

- I4C infrastructure
- RBIH MuleHunter.ai
- RBI systems
- Any government financial-fraud infrastructure
- Any real banking investigation platform

The system is intended strictly for **research, demonstration, experimentation,
and SIH presentation purposes**.

---

# 🖥️ Command Center Preview

> Add your actual dashboard screenshot or GIF here.

```markdown
![SIH Financial Network Intelligence Dashboard](docs/assets/dashboard-preview.png)
```

A short demo showing:

**select account → detect risk → open network → trace money flow → create case**

would provide a useful visual overview of the prototype.

---

# 🔎 Why Mule Networks?

A suspicious transaction rarely tells the complete story.

Financial fraud can involve multiple intermediary accounts through which
money moves before reaching its eventual destination.

A simplified flow may look like:

```text
Victim
   │
   ▼
Account A
   │
   ▼
Account B
   │
   ▼
Account C
   │
   ▼
Final Destination
```

Looking at one transaction at a time can hide relationships between accounts.

A network-oriented investigation approach instead asks:

```text
Who is connected?
      ↓
How is money moving?
      ↓
How many hops are involved?
      ↓
Which accounts behave unusually?
      ↓
Which networks deserve investigation first?
```

That is the problem this prototype is designed to explore.

---

# 🧠 Core Investigation Philosophy

The system follows five primary stages:

```text
┌────────────┐
│  DISCOVER  │
└─────┬──────┘
      ↓
Identify suspicious behavioural and transactional signals
      ↓
┌────────────┐
│  CONNECT   │
└─────┬──────┘
      ↓
Identify relationships between accounts and transactions
      ↓
┌────────────┐
│   TRACE    │
└─────┬──────┘
      ↓
Reconstruct multi-hop financial flows
      ↓
┌────────────┐
│  EXPLAIN   │
└─────┬──────┘
      ↓
Provide interpretable investigation signals
      ↓
┌────────────┐
│ PRIORITIZE │
└────────────┘
      ↓
Help investigators focus on cases requiring attention
```

---

# ✨ What the Prototype Includes

### 🖥️ Investigator Command Center
A React-based interface designed around financial investigation workflows.

### 👤 Account Intelligence
Explore accounts, associated risk information, and connected activity.

### 💸 Transaction Intelligence
Inspect synthetic transactions and their relationships with other accounts.

### 🕸️ Network Investigation
Visualize connected accounts and investigate suspicious financial networks.

### 🔗 Multi-Hop Tracing
Follow transaction flows across multiple accounts to understand how money
moves through a network.

### 📁 Investigation Cases
Create and manage investigation cases through a structured workflow.

### 🧪 Fraud Simulation
Generate deterministic demonstration scenarios for testing investigation
flows and system behaviour.

### 📊 Model Metrics
Expose illustrative model-performance information through the API and UI.

### ⚙️ System Status
Monitor the state of the prototype's intelligence engines and services.

---

# 🏗️ System Architecture

```text
                         ┌─────────────────────┐
                         │      React UI       │
                         │ React19 + TypeScript│
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    FastAPI API      │
                         │    /api/v1/*        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Application Services│
                         └──────────┬──────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
     Feature Engine          XGBoost Engine         Graph Engine
             │                      │                      │
             ▼                      ▼                      ▼
    MockFeatureEngine      MockXGBoostEngine       MockGraphEngine
             │                      │                      │
             └──────────────────────┼──────────────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────┐
                    │ Fraud Intelligence Engine   │
                    │ Mock implementation         │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                         ┌─────────────────────┐
                         │  Explainability    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                       Investigation Response
```

### Repository Architecture

```text
Repository Interfaces
        │
        ▼
In-Memory Repositories
        │
        └── Database intentionally absent
```

The architecture deliberately separates **interfaces from implementations**,
allowing the deterministic mock engines and in-memory repositories to be
replaced in future development.

For a deeper architectural breakdown, see:

📘 **[ARCHITECTURE.md](ARCHITECTURE.md)**

New team members should begin with:

📘 **[TEAM_MANUAL.md](TEAM_MANUAL.md)**

---

# 📦 Prototype Dataset

The current baseline contains:

| Component | Quantity |
|---|---:|
| 👤 Accounts | **40** |
| 💸 Connected Transactions | **120** |
| 🕸️ Networks | **4** |
| 📁 Investigation Cases | **12** |
| 🔀 Branching Flows | **Included** |

All data is synthetic and intended exclusively for demonstration and
research purposes.

---

# 🧩 Technology Stack

## Frontend
- **React 19**
- **TypeScript**
- **Vite**

## Backend
- **Python 3.11+**
- **FastAPI**
- Modular application-service architecture

## Intelligence Layer
- Feature Engine interface
- XGBoost Engine interface
- Graph Engine interface
- Fraud Intelligence Engine interface
- Deterministic mock implementations

## Data Layer
- Repository interfaces
- In-memory repositories

## Development & Deployment
- Docker
- Docker Compose
- Pytest
- CORS
- Structured logging
- Configuration management

---

# 🔌 API Surface

The backend exposes versioned API contracts under `/api/v1`.

| Domain | Endpoint |
|---|---|
| ❤️ Health | `GET /health` |
| ⚙️ System | `GET /api/v1/system/status` |
| 💸 Transactions | `GET/POST /api/v1/transactions` |
| 💸 Transaction | `GET /api/v1/transactions/{id}` |
| 👤 Accounts | `GET /api/v1/accounts` |
| 👤 Account | `GET /api/v1/accounts/{id}` |
| ⚠️ Risk | `GET /api/v1/risk/{id}` |
| 🔍 Risk Check | `POST /api/v1/risk-check` |
| 🕸️ Networks | `GET /api/v1/networks` |
| 🕸️ Network | `GET /api/v1/networks/{id}` |
| 🔗 Trace | `GET /api/v1/trace/{transaction_id}` |
| 📁 Investigations | `GET/POST /api/v1/investigations` |
| 📁 Case | `GET /api/v1/investigations/{case_id}` |
| 📌 Case Status | `PATCH /api/v1/investigations/{case_id}/status` |
| 📄 Case Report | `GET /api/v1/investigations/{case_id}/report` |
| 🧪 Simulation | `POST /api/v1/simulation/start` |
| 🧪 Simulation Status | `GET /api/v1/simulation/{id}` |
| 📊 Model Metrics | `GET /api/v1/model/metrics` |

Interactive API documentation is available through FastAPI:

```text
http://localhost:8000/docs
http://localhost:8000/redoc
```

---

# 🚀 Run Locally

## Prerequisites

Make sure you have:

- Python **3.11+**
- Node.js **20+**
- npm
- Git

Docker can be used instead if preferred.

## 1️⃣ Start the Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

## 2️⃣ Start the Frontend

Open another terminal:

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

# 🐳 Run with Docker

```powershell
docker compose up --build
```

| Service | Port |
|---|---:|
| Frontend | `5173` |
| Backend | `8000` |

No database container is currently required.

---

# 🧪 Validation

Run backend tests:

```powershell
cd backend
pytest
```

Build the frontend:

```powershell
cd ..rontend
npm run build
```

A successful build and passing backend tests provide the baseline validation
for the current prototype.

---

# 🧱 Current Implementation Status

This repository intentionally represents a **baseline research prototype**.

```text
┌──────────────────────────────────────┐
│          CURRENT BASELINE            │
├──────────────────────────────────────┤
│ ✓ React command center               │
│ ✓ FastAPI modular backend            │
│ ✓ Versioned API contracts            │
│ ✓ Network visualization              │
│ ✓ Multi-hop trace workflow           │
│ ✓ Investigation case workflow        │
│ ✓ Simulation workflow                │
│ ✓ Metrics/status views               │
│ ✓ Repository interfaces              │
│ ✓ Engine interfaces                  │
│ ✓ Deterministic mock engines         │
│ ✓ In-memory repositories             │
└──────────────────────────────────────┘
```

---

# 🚧 Intentionally Not Implemented Yet

The following are **not currently implemented**:

- ❌ Production database
- ❌ ORM
- ❌ Database migrations
- ❌ Real XGBoost model
- ❌ SHAP integration
- ❌ Production graph database
- ❌ Production graph analytics
- ❌ Feature-engineering pipeline
- ❌ Real risk-fusion engine
- ❌ Authentication
- ❌ Production ML pipeline

The simulator and performance metrics are currently illustrative.

These omissions are intentional: the project preserves clean integration
seams so that real implementations can be introduced in the next phase
without restructuring the entire application.

---

# 🔮 Planned Evolution

```text
CURRENT
Mock Engines
     │
     ▼
Integration Seams
     │
     ▼
FUTURE
Real ML + Graph + Feature Pipeline
```

Potential future implementations include:

```text
Synthetic / Real Authorized Data
            │
            ▼
      Feature Pipeline
            │
      ┌─────┴─────┐
      ▼           ▼
  XGBoost     Anomaly Detection
      │           │
      └─────┬─────┘
            ▼
       Risk Fusion
            │
            ▼
      Graph Analytics
            │
            ▼
   Network Investigation
            │
            ▼
       Explainability
            │
            ▼
    Investigator Workflow
```

These are **future development directions**, not claims about the current
implementation.

---

# 📚 Project Documentation

### 📘 [TEAM_MANUAL.md](TEAM_MANUAL.md)

Covers:
- Project setup
- Development workflow
- File ownership
- Extension points
- Testing
- Troubleshooting

### 🏗️ [ARCHITECTURE.md](ARCHITECTURE.md)

Covers:
- System boundaries
- Application architecture
- Engine interfaces
- Repository contracts
- Replacement guidance

---

# 👥 Team Development Philosophy

This project is structured around **replaceable intelligence components**.

Instead of tightly coupling the application to one ML model, graph engine,
or database, the prototype exposes interfaces that allow individual
components to evolve independently.

That means the system can progress from:

```text
Research Prototype
       ↓
Functional Intelligence Layer
       ↓
Validated ML Pipeline
       ↓
Production-Ready Architecture
```

without throwing away the foundation.

---

# 🔐 Data & Responsible AI

Financial intelligence systems operate in a high-impact domain.

### Synthetic by design
No real customer financial information is used.

### Risk ≠ guilt
A risk score is an investigation signal and should never be treated as proof
of criminal activity.

### Explainability
Investigation signals should be understandable to the person reviewing them.

### Human investigation
The system is designed to support investigators, not autonomously determine
criminal liability.

### Clear system boundaries
This prototype does not claim integration with government or banking
infrastructure.

---

# 📈 Project Vision

The long-term research direction is to move from **transaction-level
detection** toward **network-level financial intelligence**.

Instead of asking only:

```text
"Is this transaction suspicious?"
```

the system should help answer:

```text
"Which accounts are connected?"

"How is the money moving?"

"How many hops are involved?"

"Which behavioural signals are unusual?"

"Which network deserves investigation first?"

"Why was this network flagged?"
```

That shift—from isolated transactions to connected financial behaviour—is
the core idea behind this project.

---

# 🧭 The Core Idea

```text
                 FINANCIAL TRANSACTIONS
                          │
                          ▼
                    ┌──────────┐
                    │ DISCOVER │
                    └────┬─────┘
                         ▼
                    ┌──────────┐
                    │ CONNECT  │
                    └────┬─────┘
                         ▼
                    ┌──────────┐
                    │  TRACE   │
                    └────┬─────┘
                         ▼
                    ┌──────────┐
                    │ EXPLAIN  │
                    └────┬─────┘
                         ▼
                    ┌──────────┐
                    │PRIORITIZE│
                    └────┬─────┘
                         ▼
               INVESTIGATION INTELLIGENCE
```

> **Don't just detect the transaction.  
> Understand the network behind it.**

---

# ⭐ SIH Project

This project is being developed as part of **Smart India Hackathon (SIH)**,
with the objective of exploring how explainable financial network
intelligence can support the detection and investigation of potential
mule-account networks.

---

<p align="center">

### DISCOVER. CONNECT. TRACE. EXPLAIN. PRIORITIZE.

<strong>SIH Financial Network Intelligence</strong>

</p>
