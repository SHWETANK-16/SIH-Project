# XGBoost Integration Guide

The `XGBoostEngine` interface is now backed by a real trained gradient-boosted
classifier instead of the mock. Nothing about the API contract changed, so the
frontend, routes, and response schemas work exactly as before — the numbers behind
them are simply measured now rather than invented.

---

## 1. Quick start

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python -m app.ml.train_xgboost      # ~15-30s, writes backend/model/
uvicorn app.main:app --reload
```

Then check that the model actually loaded:

```powershell
curl http://localhost:8000/api/v1/system/status
```

`XGBoost Engine` should report `XGBOOST_HYBRID` / `READY`. If it says
`CALIBRATED_ML_FALLBACK` / `DEGRADED`, the `detail` field tells you why in plain
English, and the API keeps serving from the calibrated rules in the meantime.

Docker needs no extra steps — `Dockerfile.backend` trains the model at image build
time, so containers start with the artifact already present:

```powershell
docker compose up --build
```

**You never strictly have to run the training command.** If the artifact is missing
on first boot, the engine trains one itself (see §4). The explicit command exists so
that first request isn't the one that pays for it.

---

## 2. What was added

| File | Role |
|---|---|
| `app/ml/feature_spec.py` | The feature contract. Single source of truth for names, order, labels, and neutral defaults. |
| `app/ml/dataset.py` | Labelled synthetic training data built from 9 documented behavioural archetypes. |
| `app/ml/train_xgboost.py` | Training entry point. Writes the booster and its metadata. |
| `app/ml/model_store.py` | Artifact paths, save/load, `ML_MODEL_DIR` override. |
| `app/engines/real/xgboost_risk_engine.py` | The serving engine. Implements `XGBoostEngine`. |
| `tests/test_xgboost_engine.py` | 18 tests covering the contract, guardrails, SHAP, and degradation. |

Files that changed, and how little:

- `app/dependencies/services.py` — one function body, `get_xgboost_engine()`
- `app/config/settings.py` — four new `ml_*` settings
- `app/api/routes/system.py` — `/model/metrics` reads real numbers; new `/model/features`
- `app/schemas/models.py` — new optional response fields (all backwards-compatible)
- `app/services/core.py` — passes SHAP attribution through to explainability
- `app/explainability/dynamic_explainability.py` — orders factors by model reliance
- `requirements.txt`, `Dockerfile.backend`

Artifacts land in `backend/model/` (git-ignore them; they're reproducible from the
seed):

```
model/xgboost_mule_risk.json    the booster, portable JSON
model/model_metadata.json       features, threshold, metrics, importances
```

---

## 3. How it scores

A raw probability is not a risk score, and swapping a tuned rule set for a model
trained on synthetic data would have been a downgrade. So three things sit between
the booster and the number your UI displays.

**Threshold anchoring.** Training tunes a decision threshold on the validation
split (F1-max). At serving time the probability is mapped so that
`p == threshold` lands on exactly **70.0** — the existing HIGH band edge. Below
that it scales down to a 12.0 floor, above it up to a 98.5 ceiling. The
consequence: "the model flagged this" and "the dashboard says HIGH" can never
disagree, and your existing 40/70/85 bands keep their meaning.

**Rule blending.** The final score is `0.70 × model + 0.30 × CalibratedMLEngine`.
The model generalises across typologies; the hand-calibrated rules encode
investigator knowledge that synthetic data can't fully express. `CalibratedMLEngine`
was not deleted — it is a live component of every score.

**Guardrails**, which override both, in both directions:

| Condition | Effect |
|---|---|
| `in_cycle` | floor at 70.0 — circular settlement is always at least HIGH |
| `pass_through ≥ 0.90` and `deviation ≥ 5.0` | floor at 68.0 |
| `pass_through < 0.25`, `deviation < 1.5`, no cycle | **cap at 55.0** |

That last row is the one that matters most. An account that receives money and
*keeps* it cannot be CRITICAL on topology alone, no matter how dense its graph
neighbourhood looks. It is what stops legitimate high-volume merchants from
flooding the investigator queue. Anything a guardrail touches is named in
`guardrails_applied` on the response, so it's auditable rather than mysterious.

---

## 4. Configuration

Environment variables, all optional:

| Variable | Default | Meaning |
|---|---|---|
| `ML_MODEL_WEIGHT` | `0.70` | Model's share of the blend. `0.0` = rules only, `1.0` = model only. |
| `ML_AUTO_TRAIN` | `true` | Train on first boot if no artifact exists. |
| `ML_AUTO_TRAIN_SAMPLES` | `6000` | Samples for auto-training. The explicit script uses 12,000. |
| `ML_SEED` | `42` | Reproducibility. |
| `ML_MODEL_DIR` | `backend/model` | Where artifacts live. |

In production, set `ML_AUTO_TRAIN=false` and ship a pre-trained artifact. You want a
deploy to fail loudly on a missing model, not silently train a fresh one.

Training options:

```powershell
python -m app.ml.train_xgboost --samples 20000 --seed 7
python -m app.ml.train_xgboost --print-metadata     # dump the JSON
python -m app.ml.train_xgboost --quiet              # for CI / Docker
```

---

## 5. What the API returns now

`GET /api/v1/risk/ACC-0001` gains model attribution alongside the existing fields:

```json
{
  "risk_score": 82.4,
  "model": {
    "name": "XGBoost Mule Risk Classifier",
    "version": "1.0.0",
    "implementation": "XGBOOST_HYBRID",
    "probability": 0.7412,
    "model_score": 85.1,
    "rules_score": 76.2,
    "model_weight": 0.7,
    "decision_threshold": 0.49,
    "flagged": true,
    "guardrails_applied": [],
    "shap_method": "xgboost_native_treeshap",
    "top_drivers": [
      {
        "feature": "pass_through_ratio",
        "label": "Pass-through ratio",
        "value": 0.94,
        "contribution": 1.8241,
        "direction": "increases_risk",
        "share": 0.31
      }
    ]
  }
}
```

Everything from `probability` down is `null` or empty for engines with no model
attribution, so the contract is unchanged if you swap the engine back out.

`top_drivers` are **exact** TreeSHAP values from XGBoost's own
`pred_contribs=True`, not approximations, and they cost no extra dependency — the
`shap` library is not installed. `contribution` is in log-odds; `share` is the
normalised magnitude, which is the friendlier number for a UI bar.

`GET /api/v1/model/metrics` now carries `measured: true` plus `roc_auc`,
`decision_threshold`, `confusion`, `trained_at`, and `archetype_flag_rate`. Every
value is read from the artifact's metadata, so the dashboard cannot drift from the
model actually serving traffic. The `comparisons` array that feeds your
`ComparisonChart` is a real ablation study — three separately trained models
(behaviour only / + velocity / + graph) scored on the same held-out split.

`GET /api/v1/model/features` is new: gain-based importance across the whole model,
sorted descending. Use it for a global "what does this model rely on" panel;
use `top_drivers` for per-decision explanation.

---

## 6. Testing

```powershell
cd backend
pytest                                   # whole suite
pytest tests/test_xgboost_engine.py -v   # ML only
```

The ML tests `importorskip` on xgboost and scikit-learn, so a minimal install still
passes cleanly — it just exercises the fallback path instead.

Two tests are deliberately adversarial and worth knowing about. One asserts
`pr_auc < 0.999`, because a near-perfect score on synthetic data means the generator
leaked the label, not that the model is good. The other feeds in a high-volume
merchant — 71 transactions/day, fan-in 0.89, 44 counterparties — and asserts it does
**not** reach CRITICAL. That's the false-positive behaviour that decides whether an
investigator trusts the queue.

---

## 7. The one rule that will bite you

**If you change the features, retrain.**

Adding, removing, or reordering anything in `FEATURE_NAMES` invalidates the
artifact. The engine checks the saved feature order against the current spec on
load and *refuses* a mismatched model rather than silently scoring a shuffled
vector — a failure that would otherwise produce plausible-looking garbage. You'll
see the reason in `/system/status`. Fix it by retraining:

```powershell
python -m app.ml.train_xgboost
```

Same applies if you change how `StatisticalFeatureEngine` computes a feature. The
training data has to be generated the same way the live features are computed, or
the model is answering a different question than the one you're asking.

---

## 8. Notes

**Docker image size.** `xgboost` pulls in CUDA libraries you don't need for CPU
inference. Swapping `xgboost>=2.1` for `xgboost-cpu>=2.1` in `requirements.txt`
saves roughly 200 MB.

**Thread safety.** `Booster.predict` isn't documented as thread-safe, so inference
is wrapped in a lock. Single-row latency is ~1-3 ms; the lock is not your bottleneck
at demo scale, but it would need revisiting under real concurrency.

**Honesty about the data.** The model is trained on synthetic archetypes, and its
metadata says so in every response: `"TRAINED ON SYNTHETIC DATA — INVESTIGATION
SIGNAL, NOT PROOF"`. The architecture is production-shaped; the numbers are not
production numbers. Keep that label in the UI. It's the difference between a
credible prototype and an overclaim, and judges notice which one they're looking at.
