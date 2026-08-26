"""Canonical feature contract shared by training and inference.

Training-serving skew is the single most common way an ML integration silently
breaks: the trainer sees features in one order, the server sends them in another,
and the model happily returns confident nonsense. This module is the only place
that defines feature order, defaults, and derivations, and both
``app.ml.train_xgboost`` and ``app.engines.real.xgboost_risk_engine`` import from
here. If you add a feature, add it here and retrain — nowhere else.

The base features mirror exactly what ``StatisticalFeatureEngine.extract_features``
produces. Derived features are computed from those base values so the server never
has to send anything the feature engine does not already know.
"""
from __future__ import annotations

import math

# --------------------------------------------------------------------------- #
# Feature order. NEVER reorder without retraining — index position is the
# contract between the saved booster and the live request.
# --------------------------------------------------------------------------- #
FEATURE_NAMES: list[str] = [
    # --- raw behavioural ---
    "transaction_amount",
    "amount_log",
    "transaction_velocity",
    "pass_through_ratio",
    "behaviour_deviation",
    "new_counterparty_ratio",
    # --- graph / topological ---
    "network_degree",
    "fan_in_score",
    "fan_out_score",
    "pagerank_score",
    "in_cycle",
    # --- derived interaction ---
    "flow_asymmetry",
]

# Human-readable labels used for SHAP narratives in the investigator UI.
FEATURE_LABELS: dict[str, str] = {
    "transaction_amount": "Transaction amount",
    "amount_log": "Transaction amount (log scale)",
    "transaction_velocity": "Transaction velocity",
    "pass_through_ratio": "Pass-through ratio",
    "behaviour_deviation": "Behaviour deviation",
    "new_counterparty_ratio": "New counterparty dispersion",
    "network_degree": "Network degree",
    "fan_in_score": "Fan-in aggregation",
    "fan_out_score": "Fan-out distribution",
    "pagerank_score": "PageRank centrality",
    "in_cycle": "Circular settlement loop",
    "flow_asymmetry": "Directional flow asymmetry",
}

# Neutral values used when an upstream feature engine omits a key. Chosen to be
# deliberately un-suspicious so a missing feature can never inflate a risk score.
FEATURE_DEFAULTS: dict[str, float] = {
    "transaction_amount": 10_000.0,
    "transaction_velocity": 2.0,
    "pass_through_ratio": 0.50,
    "behaviour_deviation": 1.0,
    "new_counterparty_ratio": 0.50,
    "network_degree": 2.0,
    "fan_in_score": 0.50,
    "fan_out_score": 0.50,
    "pagerank_score": 1.0,
    "in_cycle": 0.0,
}

# Ablation groups power the "intelligence layer comparison" chart on the Model
# Performance page with genuinely measured uplift instead of invented numbers.
ABLATION_GROUPS: dict[str, list[str]] = {
    "Behaviour only": [
        "transaction_amount",
        "amount_log",
        "pass_through_ratio",
        "behaviour_deviation",
    ],
    "Behaviour + velocity": [
        "transaction_amount",
        "amount_log",
        "pass_through_ratio",
        "behaviour_deviation",
        "transaction_velocity",
        "new_counterparty_ratio",
    ],
    "Behaviour + velocity + graph": FEATURE_NAMES,
}


def _derive(base: dict[str, float]) -> dict[str, float]:
    """Compute derived features from base values. Must be identical in train and serve."""
    amount = max(0.0, float(base.get("transaction_amount", FEATURE_DEFAULTS["transaction_amount"])))
    fan_in = float(base.get("fan_in_score", FEATURE_DEFAULTS["fan_in_score"]))
    fan_out = float(base.get("fan_out_score", FEATURE_DEFAULTS["fan_out_score"]))
    return {
        # Log scale gives the trees a well-conditioned split space across the
        # ₹1k–₹10m range without discarding the raw value.
        "amount_log": round(math.log1p(amount), 4),
        # How lopsided the entity's directional flow is. 0.0 = balanced relay,
        # 1.0 = pure collector or pure distributor.
        "flow_asymmetry": round(abs(fan_in - fan_out), 4),
    }


def to_named_vector(features: dict[str, float]) -> dict[str, float]:
    """Normalise an arbitrary FeatureVector into the full, ordered feature mapping.

    Missing keys fall back to :data:`FEATURE_DEFAULTS`, so the mock feature engine
    (which emits a smaller vector) still produces a valid model input.
    """
    base = {name: float(features.get(name, FEATURE_DEFAULTS.get(name, 0.0))) for name in FEATURE_DEFAULTS}
    base.update(_derive(base))
    return {name: float(base.get(name, 0.0)) for name in FEATURE_NAMES}


def to_vector(features: dict[str, float]) -> list[float]:
    """Flatten a FeatureVector into the ordered list the booster expects."""
    named = to_named_vector(features)
    return [named[name] for name in FEATURE_NAMES]
