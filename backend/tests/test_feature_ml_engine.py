"""Unit tests for StatisticalFeatureEngine, CalibratedMLEngine, and DynamicExplainabilityService."""
from datetime import datetime, timezone
from app.engines.real.networkx_engine import NetworkXGraphEngine
from app.engines.real.statistical_feature_engine import StatisticalFeatureEngine
from app.engines.real.calibrated_ml_engine import CalibratedMLEngine
from app.explainability.dynamic_explainability import DynamicExplainabilityService
from app.repositories.memory.repositories import InMemoryTransactionRepository
from app.schemas.models import TransactionCreate

def test_statistical_feature_extraction():
    repo = InMemoryTransactionRepository()
    graph = NetworkXGraphEngine(repo.list())
    feature_engine = StatisticalFeatureEngine(repo, graph)

    txn = TransactionCreate(
        source_account_id="ACC-0001",
        destination_account_id="ACC-0002",
        amount=50000.0,
        timestamp=datetime.now(timezone.utc),
        transaction_type="IMPS",
    )
    features = feature_engine.extract_features(txn)

    assert "pass_through_ratio" in features
    assert "behaviour_deviation" in features
    assert "network_degree" in features
    assert "fan_in_score" in features
    assert "fan_out_score" in features
    assert "pagerank_score" in features
    assert features["transaction_amount"] == 50000.0
    assert feature_engine.status()["implementation"] == "STATISTICAL"

def test_calibrated_ml_scoring_high_risk():
    ml_engine = CalibratedMLEngine()
    mule_features = {
        "pass_through_ratio": 0.95,
        "behaviour_deviation": 8.5,
        "network_degree": 8.0,
        "in_cycle": 1.0,
        "fan_in_score": 0.8,
        "fan_out_score": 0.2,
        "transaction_velocity": 12.0,
        "new_counterparty_ratio": 0.9,
    }
    prediction = ml_engine.predict(mule_features)
    assert prediction["risk_score"] >= 85.0
    assert prediction["prediction"] == "CRITICAL_RISK"
    assert prediction["implementation"] == "CALIBRATED_ML"

def test_calibrated_ml_scoring_low_risk():
    ml_engine = CalibratedMLEngine()
    normal_features = {
        "pass_through_ratio": 0.20,
        "behaviour_deviation": 1.0,
        "network_degree": 2.0,
        "in_cycle": 0.0,
        "fan_in_score": 0.5,
        "fan_out_score": 0.5,
        "transaction_velocity": 1.0,
        "new_counterparty_ratio": 0.3,
    }
    prediction = ml_engine.predict(normal_features)
    assert prediction["risk_score"] < 50.0
    assert prediction["prediction"] in ("LOW_RISK", "MEDIUM_RISK")

def test_dynamic_explainability_factors():
    explainer = DynamicExplainabilityService()
    assessment = {"risk_score": 88.0, "risk_level": "CRITICAL", "signals": ["Pass-through", "Deviation"]}
    features = {
        "pass_through_ratio": 0.92,
        "behaviour_deviation": 5.4,
        "in_cycle": 1.0,
        "fan_in_score": 0.85,
        "network_degree": 6.0,
    }
    graph_ctx = {"network_id": "NET-001", "connected_entities": 7, "indicators": ["Circular cycle"]}

    explanation = explainer.explain(assessment, features, graph_ctx)
    factor_names = [f.name for f in explanation.factors]

    assert "Pass-through ratio" in factor_names
    assert "Behaviour deviation" in factor_names
    assert "Circular settlement" in factor_names
    assert "Fan-in aggregation" in factor_names
    assert "Network connectivity" in factor_names
    assert "high-severity mule indicators" in explanation.summary

