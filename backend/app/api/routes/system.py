from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from app.schemas.models import ModelMetrics, ModelFeatures, FeatureImportance, SystemStatus, ComponentStatus
from app.dependencies.services import (
    get_graph_engine,
    get_feature_engine,
    get_xgboost_engine,
    get_explainability_service,
    get_fraud_intelligence_engine,
)
from app.engines.interfaces.graph_engine import GraphEngine
from app.engines.interfaces.feature_engine import FeatureEngine
from app.engines.interfaces.xgboost_engine import XGBoostEngine
from app.explainability.dynamic_explainability import DynamicExplainabilityService
from app.engines.interfaces.fraud_intelligence_engine import FraudIntelligenceEngine

router = APIRouter(tags=["System"])

# Served only when no trained artifact is loaded, so the dashboard degrades to
# clearly-labelled placeholders instead of breaking.
FALLBACK_METRICS = ModelMetrics(
    precision=.89, recall=.84, f1=.865, pr_auc=.91, false_positive_rate=.047, detection_latency_ms=138,
    comparisons=[{"name": "Baseline ML", "score": .71}, {"name": "ML + Behaviour", "score": .82}, {"name": "ML + Behaviour + Graph", "score": .91}],
    label="MOCK METRICS — NOT MEASURED PERFORMANCE", measured=False, implementation="CALIBRATED_ML",
)


@router.get("/model/metrics", response_model=ModelMetrics)
def metrics(model: XGBoostEngine = Depends(get_xgboost_engine)):
    """Held-out test metrics from the loaded model artifact, or labelled placeholders."""
    report = model.metrics() if hasattr(model, "metrics") else None
    if not report:
        return FALLBACK_METRICS

    m = report.get("metrics", {})
    training = report.get("training", {})
    return ModelMetrics(
        precision=m.get("precision", 0.0),
        recall=m.get("recall", 0.0),
        f1=m.get("f1", 0.0),
        pr_auc=m.get("pr_auc", 0.0),
        false_positive_rate=m.get("false_positive_rate", 0.0),
        detection_latency_ms=report.get("detection_latency_ms", 0),
        # Real ablation study: each entry is a separately trained model scored on
        # the same held-out split.
        comparisons=report.get("comparisons", []),
        label=report.get("label", "TRAINED ON SYNTHETIC DATA"),
        measured=True,
        implementation="XGBOOST_HYBRID",
        roc_auc=m.get("roc_auc"),
        decision_threshold=report.get("decision_threshold"),
        trained_at=report.get("trained_at"),
        training_samples=training.get("n_samples"),
        test_samples=training.get("test_size"),
        confusion={
            k: int(m.get(k, 0))
            for k in ("true_positives", "false_positives", "true_negatives", "false_negatives")
        },
        archetype_flag_rate=report.get("archetype_flag_rate", {}),
    )


@router.get("/model/features", response_model=ModelFeatures)
def model_features(model: XGBoostEngine = Depends(get_xgboost_engine)):
    """Gain-based feature importance for the loaded model."""
    rows = model.feature_importance() if hasattr(model, "feature_importance") else []
    trained = bool(getattr(model, "is_trained", False))
    return ModelFeatures(
        implementation=model.status().get("implementation", "UNKNOWN"),
        measured=trained,
        n_features=len(rows),
        importances=[FeatureImportance(**row) for row in rows],
        note=(
            "Gain-based importance across the whole model. Per-decision attribution is "
            "returned as TreeSHAP values on each risk result."
            if trained
            else "No trained model loaded — run: python -m app.ml.train_xgboost"
        ),
    )


@router.get("/system/status", response_model=SystemStatus)
def status(
    graph: GraphEngine = Depends(get_graph_engine),
    feature: FeatureEngine = Depends(get_feature_engine),
    model: XGBoostEngine = Depends(get_xgboost_engine),
    fraud: FraudIntelligenceEngine = Depends(get_fraud_intelligence_engine),
    explain: DynamicExplainabilityService = Depends(get_explainability_service),
):
    g_status = graph.status()
    f_status = feature.status()
    m_status = model.status()
    fr_status = fraud.status()
    e_status = explain.status()

    names = [
        ("API", "READY", "FASTAPI", "0.1.0"),
        ("Feature Engine", f_status.get("status", "READY"), f_status.get("implementation", "STATISTICAL"), f_status.get("version", "0.1.0")),
        ("XGBoost Engine", m_status.get("status", "READY"), m_status.get("implementation", "CALIBRATED_ML"), m_status.get("version", "0.1.0")),
        ("Graph Engine", g_status.get("status", "READY"), g_status.get("implementation", "NETWORKX"), g_status.get("version", "0.1.0")),
        ("Fraud Intelligence Engine", fr_status.get("status", "READY"), fr_status.get("implementation", "MOCK"), fr_status.get("version", "0.1.0")),
        ("Explainability Service", e_status.get("status", "READY"), e_status.get("implementation", "DYNAMIC"), e_status.get("version", "0.1.0")),
        ("Repository / Storage", "READY", "IN-MEMORY", "0.1.0"),
    ]
    overall = "DEGRADED" if any(s != "READY" for _, s, _, _ in names) else "READY"
    return SystemStatus(
        overall=overall,
        components=[ComponentStatus(component=n, status=s, implementation=i, version=v) for n, s, i, v in names],
        checked_at=datetime.now(timezone.utc),
        environment="baseline-demo",
    )
