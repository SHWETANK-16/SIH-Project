"""Tests for the XGBoost mule-risk engine, feature contract, and training pipeline.

Skipped wholesale when xgboost/scikit-learn are absent, so the suite still passes
on a minimal install where the engine degrades to calibrated rules.
"""
import pytest

xgboost = pytest.importorskip("xgboost", reason="xgboost is not installed")
pytest.importorskip("sklearn", reason="scikit-learn is not installed")

from app.engines.real.xgboost_risk_engine import XGBoostRiskEngine
from app.ml.dataset import generate_dataset
from app.ml.feature_spec import FEATURE_NAMES, to_named_vector, to_vector

# Trained once for the whole module — training is the slow part, not inference.
ENGINE = XGBoostRiskEngine(auto_train=True, auto_train_samples=4_000)

MULE = {
    "transaction_amount": 480_000.0,
    "transaction_velocity": 14.0,
    "pass_through_ratio": 0.97,
    "behaviour_deviation": 22.0,
    "new_counterparty_ratio": 0.95,
    "network_degree": 11.0,
    "fan_in_score": 0.18,
    "fan_out_score": 0.82,
    "pagerank_score": 3.4,
    "in_cycle": 0.0,
}

NORMAL = {
    "transaction_amount": 8_500.0,
    "transaction_velocity": 6.0,
    "pass_through_ratio": 0.16,
    "behaviour_deviation": 1.1,
    "new_counterparty_ratio": 0.20,
    "network_degree": 4.0,
    "fan_in_score": 0.48,
    "fan_out_score": 0.52,
    "pagerank_score": 0.9,
    "in_cycle": 0.0,
}

# The hard negative the model exists to get right: a merchant with mule-like
# topology (heavy fan-in, high velocity, dense network) that retains its funds.
MERCHANT = {
    "transaction_amount": 62_000.0,
    "transaction_velocity": 71.0,
    "pass_through_ratio": 0.22,
    "behaviour_deviation": 1.2,
    "new_counterparty_ratio": 0.18,
    "network_degree": 44.0,
    "fan_in_score": 0.89,
    "fan_out_score": 0.11,
    "pagerank_score": 7.8,
    "in_cycle": 0.0,
}


# --------------------------------------------------------------------------- #
# Feature contract
# --------------------------------------------------------------------------- #
def test_vector_length_and_order_match_the_spec():
    vector = to_vector(MULE)
    assert len(vector) == len(FEATURE_NAMES)
    named = to_named_vector(MULE)
    assert list(named.keys()) == FEATURE_NAMES


def test_missing_features_fall_back_to_neutral_defaults():
    """A partial vector (e.g. from MockFeatureEngine) must never inflate risk."""
    sparse = {"transaction_amount": 5_000.0, "pass_through_ratio": 0.3}
    named = to_named_vector(sparse)
    assert named["in_cycle"] == 0.0
    assert named["behaviour_deviation"] == 1.0
    assert all(isinstance(v, float) for v in named.values())


def test_derived_features_are_computed_not_passed_in():
    named = to_named_vector({"transaction_amount": 100_000.0, "fan_in_score": 0.9, "fan_out_score": 0.1})
    assert named["amount_log"] == pytest.approx(11.5129, abs=1e-3)
    assert named["flow_asymmetry"] == pytest.approx(0.8, abs=1e-6)


# --------------------------------------------------------------------------- #
# Dataset
# --------------------------------------------------------------------------- #
def test_dataset_shape_and_class_balance():
    X, y, archetypes = generate_dataset(n_samples=1_500, seed=7)
    assert X.shape == (1_500, len(FEATURE_NAMES))
    assert len(y) == 1_500 and len(archetypes) == 1_500
    assert 0.20 < y.mean() < 0.50, "positive rate should be imbalanced but learnable"


def test_dataset_includes_hard_negatives():
    """Legitimate merchant and payroll archetypes must be present, or the model
    learns to flag volume alone."""
    _, _, archetypes = generate_dataset(n_samples=2_000, seed=7)
    present = set(archetypes.tolist())
    assert {"merchant_collector", "payroll_distributor"} <= present


def test_dataset_is_reproducible():
    a, ya, _ = generate_dataset(n_samples=400, seed=11)
    b, yb, _ = generate_dataset(n_samples=400, seed=11)
    assert (a == b).all() and (ya == yb).all()


# --------------------------------------------------------------------------- #
# Engine
# --------------------------------------------------------------------------- #
def test_engine_loads_a_trained_model():
    assert ENGINE.is_trained
    status = ENGINE.status()
    assert status["implementation"] == "XGBOOST_HYBRID"
    assert status["status"] == "READY"
    assert status["explainability"] == "native TreeSHAP"


def test_prediction_satisfies_the_existing_contract():
    prediction = ENGINE.predict(MULE)
    for key in ("model_name", "model_version", "risk_score", "prediction"):
        assert key in prediction
    assert 12.0 <= prediction["risk_score"] <= 98.5
    assert prediction["prediction"].endswith("_RISK")


def test_mule_scores_above_normal():
    assert ENGINE.predict(MULE)["risk_score"] > ENGINE.predict(NORMAL)["risk_score"]


def test_mule_reaches_high_band():
    prediction = ENGINE.predict(MULE)
    assert prediction["risk_score"] >= 70.0
    assert prediction["prediction"] in ("HIGH_RISK", "CRITICAL_RISK")


def test_legitimate_merchant_is_not_escalated_to_critical():
    """The guardrail that keeps the investigator queue usable."""
    prediction = ENGINE.predict(MERCHANT)
    assert prediction["risk_score"] < 85.0, "high-volume merchant must not be CRITICAL"


def test_circular_settlement_always_reaches_high_band():
    """A settlement loop must land at HIGH or above, whether the model or the
    guardrail is what gets it there."""
    looped = {**NORMAL, "in_cycle": 1.0}
    prediction = ENGINE.predict(looped)
    assert prediction["risk_score"] >= 70.0
    assert prediction["prediction"] in ("HIGH_RISK", "CRITICAL_RISK")


def test_circular_guardrail_floor_fires_when_the_blend_falls_short():
    """The floor mechanism itself, exercised directly.

    The test above can pass without the guardrail ever firing — the model weights
    ``in_cycle`` heavily enough to clear 70 unaided, which makes the floor
    redundant rather than broken. Asserting on ``guardrails_applied`` there would
    be testing which component happened to win, not the behaviour we care about.
    So the mechanism is verified here, with a score low enough to force it to act.
    """
    score, notes = ENGINE._apply_guardrails(30.0, {**NORMAL, "in_cycle": 1.0})
    assert score == 70.0
    assert any("Circular" in note for note in notes)


def test_retained_funds_guardrail_caps_below_critical():
    """The merchant brake, also exercised directly against a high input score."""
    merchant_like = {**MERCHANT, "pass_through_ratio": 0.20, "behaviour_deviation": 1.1}
    score, notes = ENGINE._apply_guardrails(92.0, merchant_like)
    assert score == 55.0
    assert any("retained" in note.lower() for note in notes)


def test_guardrails_leave_an_ordinary_score_untouched():
    """No guardrail should fire on a row that trips none of the conditions.

    Mid-range pass-through is the point: NORMAL itself would trip the
    retained-funds cap, which is correct behaviour but useless for this assertion.
    """
    ordinary = {**NORMAL, "pass_through_ratio": 0.50, "behaviour_deviation": 2.0}
    score, notes = ENGINE._apply_guardrails(64.0, ordinary)
    assert score == 64.0
    assert notes == []


def test_threshold_anchoring_keeps_bands_and_model_agreeing():
    """If the model flags a row as positive, the score must land in HIGH or above."""
    prediction = ENGINE.predict(MULE)
    if prediction["model_flagged"]:
        assert prediction["model_score"] >= 70.0


def test_shap_contributions_are_returned_for_every_feature():
    prediction = ENGINE.predict(MULE)
    assert prediction["shap_method"] == "xgboost_native_treeshap"
    assert set(prediction["shap_contributions"]) == set(FEATURE_NAMES)
    drivers = prediction["shap_top_drivers"]
    assert 1 <= len(drivers) <= 5
    # Drivers must be ordered by descending attribution magnitude.
    shares = [d["share"] for d in drivers]
    assert shares == sorted(shares, reverse=True)
    assert all(d["direction"] in ("increases_risk", "decreases_risk") for d in drivers)


def test_blend_weight_is_respected():
    """model_weight=0 must reproduce the calibrated rules score exactly."""
    rules_only = XGBoostRiskEngine(model_weight=0.0, auto_train=False)
    if not rules_only.is_trained:
        pytest.skip("no artifact available for a blend comparison")
    prediction = rules_only.predict(NORMAL)
    assert prediction["risk_score"] == pytest.approx(prediction["rules_score"], abs=0.15)


def test_metrics_report_is_honest():
    report = ENGINE.metrics()
    assert report is not None
    metrics = report["metrics"]
    for key in ("precision", "recall", "f1", "pr_auc", "roc_auc", "false_positive_rate"):
        assert 0.0 <= metrics[key] <= 1.0
    # A perfect score on synthetic data signals leakage, not quality.
    assert metrics["pr_auc"] < 0.999, "suspiciously perfect PR-AUC — check for leakage"
    assert metrics["pr_auc"] > 0.70, "model should clearly beat chance on its own archetypes"


def test_ablation_shows_graph_layer_adding_signal():
    comparisons = ENGINE.metrics()["comparisons"]
    assert len(comparisons) == 3
    scores = [c["score"] for c in comparisons]
    assert scores[-1] >= scores[0], "full feature set should not underperform behaviour alone"


def test_feature_importance_is_sorted_and_complete():
    rows = ENGINE.feature_importance()
    assert len(rows) == len(FEATURE_NAMES)
    assert [r["importance"] for r in rows] == sorted((r["importance"] for r in rows), reverse=True)
    assert all(r["label"] for r in rows)


def test_engine_degrades_cleanly_without_an_artifact(tmp_path, monkeypatch):
    """Point the store at an empty directory with auto-train off: rules only, API alive."""
    monkeypatch.setenv("ML_MODEL_DIR", str(tmp_path))
    engine = XGBoostRiskEngine(auto_train=False)
    assert not engine.is_trained
    assert engine.status()["status"] == "DEGRADED"
    prediction = engine.predict(MULE)
    assert prediction["implementation"] == "CALIBRATED_ML_FALLBACK"
    assert 0.0 <= prediction["risk_score"] <= 100.0
    assert prediction["model_available"] is False
