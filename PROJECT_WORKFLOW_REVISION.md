# CyberKavach: Quick Revision & Workflow Cheat Sheet
> **AI-Driven Mule Account Network Intelligence & Investigation Platform**  
> *Target: Smart India Hackathon (SIH) | Executive Pitch & Viva Revision Guide*

---

## 1. Problem & Core Concept in 30 Seconds

### The Problem
* Cyber fraud syndicates (Digital Arrests, Fake Investment Telegram groups, Phishing APKs) do not withdraw victim money directly.
* They funnel money through **multi-layered money mule accounts** (Layer 1 $\to$ Layer 2 $\to$ Layer 3 $\to$ Crypto/ATM cash-out).
* **The Isolation Paradox:** Evaluated individually, a single mule account looks like an ordinary student or retail account. The fraud is **only visible in network relationships, velocity, and flow topology**.

### The Solution: CyberKavach
An end-to-end financial graph intelligence platform that ingests raw banking transactions, constructs real-time directed transaction graphs, scores mule likelihood with an **XGBoost + Rule hybrid**, explains decisions via **TreeSHAP**, and traces multi-hop fund leakages via **temporal BFS**.

---

## 2. The 5-Stage Operational Doctrine

$$\mathbf{DISCOVER} \longrightarrow \mathbf{CONNECT} \longrightarrow \mathbf{TRACE} \longrightarrow \mathbf{EXPLAIN} \longrightarrow \mathbf{PRIORITIZE}$$

| Stage | What Happens | Core Technology |
|---|---|---|
| **1. DISCOVER** | Ingests transaction streams, detects sudden velocity spikes and behavioral deviations. | Rolling in-memory statistical window |
| **2. CONNECT** | Links sender, receiver, devices, and UPI IDs into an active transaction network. | **NetworkX Graph Engine** (`nx.DiGraph`) |
| **3. TRACE** | Traverses forward in time across multiple bank hops to reveal where stolen money went. | **Temporal BFS Multi-Hop Tracer** |
| **4. EXPLAIN** | Computes mathematical feature contributions ($+\Delta / -\Delta$) for legal compliance. | **Native TreeSHAP** (`pred_contribs=True`) |
| **5. PRIORITIZE**| Ranks cases by stolen amount, syndicate size, and velocity so officers act on high-impact rings first. | Priority Case Scoring Engine |

---

## 3. End-to-End System Workflow

```
[ Financial Transaction Event ] (Source, Dest, Amount, Timestamp, Channel)
             │
             ▼
[ 1. Ingestion & Validation ] (FastAPI + Pydantic V2 Schemas)
             │
             ▼
[ 2. Feature Extraction ] ──► Calculates 12 features:
   • 4 Behavioural (Amount, Amount_Log, Pass-through, Historical Deviation)
   • 2 Velocity    (Transaction count, New counterparty ratio)
   • 6 Graph       (Degree, Fan-In, Fan-Out, PageRank, Cycle Flag, Flow Asymmetry)
             │
             ▼
[ 3. Dual Inference Pipeline ]
   ├── XGBoost Booster (12 features)  ──► Probability P(mule)
   └── Calibrated Domain Rules        ──► Rules Score
             │
             ▼
[ 4. Hybrid Risk Calibration & Guardrails ]
   • Score = 0.70 × ML_Score + 0.30 × Rules_Score
   • Threshold Anchoring (F1-optimal θ = 0.49 maps to Score = 70.0)
   • Hard Guardrails:
     - in_cycle = 1            ──► Score Floor = 70.0 (High Risk)
     - passthrough≥90% + spike ──► Score Floor = 68.0
     - clean personal history  ──► Score Cap   = 55.0
             │
             ▼
[ 5. Native TreeSHAP Attribution ]
   • Calculates exact log-odds contribution for all 12 features.
   • Normalizes to percentage share for UI waterfall bars.
             │
             ▼
[ 6. Investigator Presentation ] (React 18 / Vite 6 CyberKavach UI)
   • Interactive Network Graph with cycle highlights.
   • Multi-Hop Tracing Timeline (INITIAL ➔ RELAY ➔ SPLIT).
   • Prioritized Case Dossier for Law Enforcement / Bank Compliance.
```

---

## 4. Machine Learning & Graph Specifications (At a Glance)

### The 12 Canonical Features
1. `transaction_amount`: Raw inbound amount (₹).
2. `amount_log`: $\ln(1 + \text{amount})$ to stabilize variance.
3. `transaction_velocity`: Total transaction count in sliding window.
4. `pass_through_ratio`: Outflow volume / Inflow volume (mules typically move $\ge 90\%$).
5. `behaviour_deviation`: Current amount / Historical mean amount ($>5\times$ is anomalous).
6. `new_counterparty_ratio`: Unique destinations / Total outgoing transfers.
7. `network_degree`: Total incoming + outgoing connections.
8. `fan_in_score`: Ratio of incoming senders (aggregators).
9. `fan_out_score`: Ratio of outgoing recipients (smurfs).
10. `pagerank_score`: Network prestige and bridge centrality ($\alpha = 0.85$).
11. `in_cycle`: $1.0$ if entity is inside a closed money loop ($A \to B \to C \to A$), else $0.0$.
12. `flow_asymmetry`: $\| \text{fan\_in} - \text{fan\_out} \|$ directional imbalance.

### Key ML Numbers & Hyperparameters
* **Algorithm:** Gradient Boosted Decision Trees (`XGBClassifier`, histogram method `tree_method="hist"`).
* **Dataset:** 12,000 synthetic records with **9 behavioral archetypes**:
  * **4 Legitimate (Hard Negatives):** `retail_salaried`, `merchant_collector` (high fan-in/velocity), `payroll_distributor` (high fan-out), `high_value_one_off`.
  * **5 Mule Archetypes:** `rapid_relay`, `fanout_smurf`, `fanin_aggregator`, `circular_layering`, `dormant_reactivated`.
  * **Realism:** **3% label noise** injected to prevent artificial 100% metric leakage.
* **Held-Out Test Results (2,400 samples):**
  * **Precision:** $95.17\%$
  * **Recall:** $94.15\%$
  * **F1-Score:** $0.9465$
  * **PR-AUC:** $0.9599$
  * **Inference Latency:** $\sim 4\text{ ms}$ per transaction.

---

## 5. Temporal Multi-Hop Money Flow Tracer

* **Core Algorithm:** Forward Breadth-First Search (BFS) in temporal sequence.
* **Temporal Validity:** Only follows transactions where $T_{\text{next}} \ge T_{\text{current}}$ within a **72-hour window**.
* **Loop Protection:** Path-visited lineage tracking allows an account to appear across different branches while strictly preventing infinite circular loops.
* **Relationship Classification:**
  * `INITIAL_TRANSFER`: First jump from source/victim.
  * `RAPID_RELAY`: Rapid full pass-through to single downstream account.
  * `SPLIT_FAN_OUT`: One account disbursing into multiple sub-transfers (smurfing).

---

## 6. Architecture & Tech Stack

```text
CyberKavach Platform
│
├── frontend/  ──► React 18 + TypeScript + Vite 6
│                  • TanStack Query (server state & caching)
│                  • Recharts (analytics & trend visualization)
│                  • Lucide React (cyber-slate investigation UI)
│                  • Canvas 3D Network Sphere
│
└── backend/   ──► Python 3.11+ / FastAPI Modular Monolith
                   • XGBoost 3.4.1 (Trained ML booster + TreeSHAP)
                   • NetworkX 3.6+ (Real-time directed graph algorithms)
                   • Pydantic V2 (Strict request/response contracts)
                   • Clean Architecture (Routes ➔ Services ➔ Engines ➔ Repos)
```

---

## 7. Hackathon Judge Q&A Cheat Sheet

**Q1: How is this different from existing bank rule engines?**  
*Answer:* Static rules only look at isolated thresholds (e.g., "flag if $> \text{₹}50,000$"), which fraudsters easily bypass by smurfing $\text{₹}49,000$. CyberKavach looks at **graph topology** (closed cycles, fan-in/fan-out asymmetry) and **velocity** combined with calibrated machine learning.

**Q2: Why use a Hybrid model (70% ML + 30% Rules) instead of pure ML?**  
*Answer:* Pure ML can overfit or behave unpredictably on edge cases. Domain rules guarantee compliance guardrails (e.g., an account in a confirmed circular loop is *always* held at a minimum score of 70, regardless of model score).

**Q3: How do you prevent false positives on genuine merchants and payrolls?**  
*Answer:* We deliberately trained our model on **hard negatives** (`merchant_collector` and `payroll_distributor`). Merchants have high incoming velocity but low pass-through and a stable customer base; payroll accounts have high fan-out but predictable monthly counterparty stability.

**Q4: What makes this Explainable (XAI)?**  
*Answer:* We don't just output a black-box probability. We run **TreeSHAP** directly inside XGBoost (`pred_contribs=True`), calculating the exact mathematical positive and negative contribution of every feature, translated into plain-English legal findings for investigators.

**Q5: Can it run in real time?**  
*Answer:* Yes. Feature extraction and XGBoost inference take under **4 milliseconds** per transaction. Expensive graph operations are bounded to 2-hop ego networks around the target account.

---

## 8. Essential Terminal Commands

| Action | Command |
|---|---|
| **Run Backend** | `cd backend` <br> `python -m uvicorn app.main:app --reload --port 8000` |
| **Run Frontend** | `cd frontend` <br> `npm run dev` |
| **Run All 50 Tests** | `cd backend` <br> `python -m pytest` |
| **Re-build Frontend** | `cd frontend` <br> `npm run build` |
| **Swagger Docs** | Open browser at `http://localhost:8000/docs` |
| **Live UI** | Open browser at `http://localhost:5173` |

