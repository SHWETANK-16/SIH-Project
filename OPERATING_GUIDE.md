# Operating Guide

Everything you need to run this software, confirm it works, understand what each
screen does, and create a case end to end.

All data is synthetic. Risk scores are investigation signals, not determinations of
guilt.

---

## Part 1 — What this software actually does

The mental model is five stages, and the sidebar is ordered to follow them:

**DISCOVER** suspicious accounts → **CONNECT** them into networks → **TRACE** where
money went → **EXPLAIN** why it looks suspicious → **PRIORITIZE** which cases an
investigator opens first.

Under that sits a scoring pipeline. When any account is assessed, four things happen
in order: `StatisticalFeatureEngine` computes 10 behavioural and topological features
from the transaction history; `XGBoostRiskEngine` scores them with a trained
gradient-boosted model blended 70/30 with calibrated domain rules; guardrails
override the result where a domain fact outranks the model; and
`DynamicExplainabilityService` turns the outcome into readable factors ordered by
what the model actually weighted.

The result is a 0-100 score in one of four bands: LOW below 40, MEDIUM 40-70, HIGH
70-85, CRITICAL 85+.

---

## Part 2 — Running it

### Step 1 — Backend

```
cd backend
pip install -r requirements.txt
python -m app.ml.train_xgboost
python -m uvicorn app.main:app --reload
```

The training step takes 15-30 seconds and writes `backend/model/`. You only need it
once — not every time you start the server.

Use `python -m uvicorn`, not bare `uvicorn`. On Windows the `uvicorn.exe` shim lands
in Python's `Scripts\` folder, which usually isn't on PATH. The `python -m` form
always works. Same for `python -m pytest`.

Leave this terminal running. You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Step 2 — Frontend, in a second terminal

```
cd frontend
npm install
npm run dev
```

If `frontend\.env` doesn't exist yet, create it once: `Copy-Item .env.example .env`

### Step 3 — Open it

| What | Where |
|---|---|
| The website | http://localhost:5173 |
| Swagger API explorer | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

Keep both terminals open the whole time. Closing the backend makes every page show
"Start the FastAPI backend on port 8000, then retry."

---

## Part 3 — Verifying everything works

Three layers, cheapest first. Do all three the first time; layer 1 alone is enough
after that.

### Layer 1 — Automated check (30 seconds)

With the server running, in a **third terminal**:

```
cd backend
python verify_integration.py
```

Roughly 30 checks across seven areas. Read the summary line at the bottom: `N passed
· 0 failed` means you're good. Exit code is 0 on success, so this works in CI later.

Two of its checks matter more than the rest, because **the website cannot show you
either problem**:

*Is the trained model actually serving?* If the artifact fails to load, the engine
falls back to pure rules and keeps working perfectly — every page still renders,
every score still appears. You'd never notice from the UI. The script checks
`implementation == "XGBOOST_HYBRID"` and tells you if you're on the fallback.

*Do the model's verdict and the displayed band agree?* If the model flags a row as
positive, the score must land at 70+ (HIGH). If those ever disagree, the dashboard
is misrepresenting the model.

### Layer 2 — Test suite (1 minute)

```
cd backend
python -m pytest -v
```

All tests should pass, and the 18 in `test_xgboost_engine.py` should **run**, not
skip. If they skip, xgboost isn't installed in the interpreter running pytest.

Two are deliberately adversarial and worth understanding. `test_metrics_report_is_honest`
asserts PR-AUC is *below* 0.999, because a near-perfect score on synthetic data means
the generator leaked the label rather than that the model is good.
`test_legitimate_merchant_is_not_escalated_to_critical` feeds in a high-volume
merchant — 71 transactions/day, fan-in 0.89, 44 counterparties — and asserts it does
**not** reach CRITICAL. That's the behaviour that decides whether an investigator
trusts the queue.

### Layer 3 — Manual walkthrough (5 minutes)

Work down the sidebar. Expected result for each:

| Page | What confirms it works |
|---|---|
| Overview | Six metric cards with non-zero numbers; recent cases table populated |
| Network Investigation | Four network cards; click one → graph renders; click a node → inspector panel opens with that account's features |
| Money Flow | Enter `TXN-0001`, press Trace money → hop cards appear |
| Transactions | 120+ rows; type in search and rows filter; change risk dropdown and rows filter |
| Accounts | 40 cards; click one → snapshot plus a "Risk explanation" with a summary and factors |
| Investigations | 12 case cards; click one → KPIs, explanation, network map, money flow; change the status dropdown and it persists on reload |
| Fraud Simulation | Submit the form → four round cards appear |
| Model Performance | Six metric cards populated (see the caveat in Part 6) |
| System Status | XGBoost Engine shows `XGBOOST_HYBRID` / READY |

On System Status, **overall status will read DEGRADED, and that is correct.**
`MockFraudIntelligenceEngine` is still a mock, and the status endpoint reports
honestly instead of hardcoding READY. Only worry if the XGBoost row itself is not
READY.

### The 20-second sanity check

Once you know the app, this is the fastest meaningful test:

```
curl http://localhost:8000/api/v1/system/status
```

`XGBOOST_HYBRID` in the response = model loaded. `CALIBRATED_ML_FALLBACK` = it
didn't; run the training command and restart.

---

## Part 4 — Guide to every page

### Overview (`/dashboard`)

Portfolio summary: total accounts, high-risk accounts, networks, flagged
transactions, open cases, and total suspicious flow, plus the six most recent cases.

Read-only. The only interactions are links — case IDs go to case detail, network IDs
go to the network map.

Be aware the volume chart, the risk donut, and the risk-legend percentages
(Critical 12 / High 23 / Medium 41 / Low 24) are **hardcoded constants**, not live
data. So is "Updated 2 min ago." The six metric cards *are* live.

### Network Investigation (`/networks`)

Card per network; click through for the graph. This page has the richest interaction
in the app:

- Zoom in / out / reset buttons
- Drag the background to pan
- Drag a node to reposition it
- Click a node (or Tab to it and press Enter) to open the inspector

The inspector is the useful part — it shows that account's risk score, transaction
count, network degree, in/out flow, fan-in/fan-out, and behaviour deviation, with
links to the account page and to a pre-seeded money trace. Selecting a node also
reveals amount labels on its edges.

Rendering caps at 50 nodes; you'll see a "Capped at 50" pill when it's truncating.

### Money Flow (`/tracing`)

Enter a transaction ID and press Trace money to walk the chain hop by hop. Input
auto-uppercases. `TXN-0001` is offered as a shortcut in the empty state. Arriving via
"Trace money" from an account or node pre-fills the entity.

### Transactions (`/transactions`)

Searchable, filterable table. The search box matches against every field, and the
risk-level dropdown filters.

Two controls here do nothing: the **transaction-type dropdown** (UPI/IMPS/NEFT/RTGS)
has no handler, and **Export view** has no click handler. Table is limited to 50 rows
with no pagination.

### Accounts (`/accounts`)

Searchable list by account ID; click for detail. Detail shows the account snapshot
and a risk explanation with narrative factors.

Worth knowing: the detail page calls `GET /risk/{id}`, which returns the full
assessment — score, band, priority, signals, network summary, and all the model
attribution — but the page **only renders the explanation**. The numeric score, SHAP
drivers, and guardrail notes are in the response, unused. See Part 6.

### Investigations (`/investigations`)

The case queue, and the only place you can change persistent state. Case detail gives
you KPIs, the risk explanation, indicator tags, evidence references, a network map
with the case's traced hops highlighted and numbered, and the money-flow trail.

The **status dropdown** is a real mutation — NEW, UNDER_INVESTIGATION, ESCALATED,
RESOLVED, FALSE_POSITIVE. It PATCHes the backend and survives a reload.

**Generate investigation report** calls the API successfully but only prints "Report
preview generated" — the report body is never displayed or downloaded. To actually
see it, use the API (Part 5, step 5).

There is **no button to create a case.** That's Part 5.

### Fraud Simulation (`/simulation`)

Pick a strategy and four parameters, submit, and get four adversarial rounds with
detection rate, false-positive rate, and networks detected. These numbers come from
a formula in `SimulationService`, not from the model — the page labels them MOCK
METRICS, which is accurate.

### Model Performance (`/model-performance`)

Precision, recall, F1, PR-AUC, false-positive rate, latency, and the intelligence
layer comparison chart. These are now **real measured numbers** from the held-out
test split. The page's own captions have not caught up — see Part 6.

### System Status (`/system-status`)

Live status per component, auto-refreshing every 30 seconds. The only page that
polls. Fully read-only.

---

## Part 5 — Adding a new case and getting output

The frontend has no create-case form, so this goes through the API. Swagger is the
easiest route — no curl quoting problems.

### Step 1 — Pick accounts and transactions to attach

Open http://localhost:5173/accounts and note two or three account IDs you want in the
case, e.g. `ACC-0003`, `ACC-0007`. Grab a transaction ID from
http://localhost:5173/transactions, e.g. `TXN-0004`.

Attaching at least one transaction reference matters — it's what makes the money-flow
panel appear on the case.

### Step 2 — Open Swagger

Go to http://localhost:8000/docs and find **POST /api/v1/investigations**. Click it,
then **Try it out**.

### Step 3 — Fill in the body

Replace the example with:

```json
{
  "title": "Suspected layering across three accounts",
  "related_accounts": ["ACC-0003", "ACC-0007", "ACC-0012"],
  "transaction_references": ["TXN-0004"],
  "risk_level": "HIGH"
}
```

Only `title` and `related_accounts` are required. `risk_level` accepts LOW, MEDIUM,
HIGH, or CRITICAL and defaults to MEDIUM.

### Step 4 — Execute

Press **Execute**. A `201` response means it worked, and the response body contains
your new case with a generated `case_id` like `CASE-0013`.

The server assigns `key_indicators: ["Manual review requested"]`,
`network_size` equal to your account count, `estimated_suspicious_flow: 0`, and
`network_id: null`.

### Step 5 — See it in the website

Open http://localhost:5173/investigations. Your case is in the queue. Click it and
you'll get the case detail view, where you can change its status.

Two panels will be missing compared to the seeded cases, and this is expected rather
than broken. **Network map** never appears on a manually created case, because the
backend sets `network_id: null` — cases aren't auto-linked to a discovered network.
**Money flow** appears only if you supplied `transaction_references`.

### Step 6 — Get the report output

In Swagger, use **GET /api/v1/investigations/{case_id}/report** with your case ID.
Or directly in a browser:

```
http://localhost:8000/api/v1/investigations/CASE-0013/report
```

Returns:

```json
{
  "case_id": "CASE-0013",
  "risk": "HIGH",
  "key_indicators": ["Manual review requested"],
  "flow": "ACC-0003 → ACC-0007 → ACC-0012",
  "synthetic": true
}
```

### PowerShell alternative

If you'd rather not use Swagger:

```powershell
$body = @{
  title = "Suspected layering across three accounts"
  related_accounts = @("ACC-0003","ACC-0007","ACC-0012")
  transaction_references = @("TXN-0004")
  risk_level = "HIGH"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/api/v1/investigations `
  -Method Post -Body $body -ContentType "application/json"
```

### Other outputs worth pulling

| Command | What you get |
|---|---|
| `GET /api/v1/risk/ACC-0001` | Full assessment: score, band, model probability, SHAP drivers, guardrails, explanation |
| `GET /api/v1/model/metrics` | Real held-out precision/recall/F1/PR-AUC, confusion matrix, per-typology flag rates |
| `GET /api/v1/model/features` | Which features the model relies on overall |
| `GET /api/v1/trace/TXN-0001` | Multi-hop money trail as JSON |
| `PATCH /api/v1/investigations/{id}/status` | Move a case through the workflow, body `{"status":"ESCALATED"}` |

`GET /api/v1/risk/ACC-0001` is the single most informative call in the system — it's
the whole pipeline's output for one entity, including the per-decision TreeSHAP
attribution that the UI doesn't yet display.

---

## Part 6 — Known gaps

Not bugs you introduced. Worth knowing before a demo, because someone will click one.

**Controls that exist but do nothing:** the top-bar search box (no input element at
all), the transaction-type dropdown, and Export view. The report button works but
discards its result.

**Model Performance captions are stale.** The page still shows a "MOCK METRICS · NOT
MEASURED" badge, labels every card "Example value," calls the comparison chart
"Illustrative uplift only," and states the numbers "are not results from XGBoost."
All four are now false — the API returns `measured: true` with real held-out numbers.
The backend is right and the captions are out of date.

**The frontend can't see the model's attribution yet.** `RiskResult.model` in
`frontend/src/types/index.ts` is typed as only `{name, version, implementation}`. The
backend now also returns `probability`, `model_score`, `rules_score`,
`model_weight`, `decision_threshold`, `flagged`, `guardrails_applied`,
`top_drivers`, and `shap_method`. The data arrives and is discarded. Widening that
type and rendering `top_drivers` as contribution bars is the single highest-value
frontend change available.

**The ablation chart is flat.** Behaviour-only scores 0.9539 PR-AUC; adding velocity
gets 0.9599; adding all graph features also gets 0.9599. The graph layer contributes
nothing measurable, because `new_counterparty_ratio` (38% importance) and `in_cycle`
(22%) already encode most of that signal. If you present that chart as "graph
intelligence adds uplift," the chart will contradict you. Either explain why, or
acknowledge the synthetic data is too easy for the graph layer to matter.

**Cases aren't linked to networks.** Manually created cases always get
`network_id: null`, so no network map.

---

## Part 7 — Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `'uvicorn' is not recognized` | Python's `Scripts\` not on PATH | `python -m uvicorn app.main:app --reload` |
| `'pytest' is not recognized` | Same | `python -m pytest` |
| Every page: "Start the FastAPI backend" | Backend not running, or crashed | Check terminal 1; restart it |
| XGBoost Engine shows `CALIBRATED_ML_FALLBACK` | Artifact missing or unreadable | `python -m app.ml.train_xgboost`, then restart the server. The `detail` field in `/system/status` says why |
| ML tests skip | xgboost missing from the interpreter running pytest | `python -m pip install -r requirements.txt` |
| Overall status DEGRADED | Correct — fraud intelligence engine is still a mock | Nothing to fix |
| Metrics show `measured: false` | No model loaded | Same as the fallback fix above |
| Model refuses to load, mentions feature order | Features changed since training | `python -m app.ml.train_xgboost` |
| Frontend blank / module errors | Dependencies not installed | `cd frontend && npm install` |
| CORS error in console | `frontend_url` doesn't match the dev server | Check `backend/.env.example` against the Vite port |
| Port 8000 in use | Old server still running | `netstat -ano \| findstr :8000`, then `taskkill /PID <pid> /F` |

**When a change doesn't seem to apply:** `--reload` picks up backend Python changes
automatically, but the engine is cached with `lru_cache` and the model loads once at
startup. After retraining, fully restart the backend — Ctrl+C and start it again.
