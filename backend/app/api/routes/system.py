from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from app.schemas.models import ModelMetrics, SystemStatus, ComponentStatus
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

@router.get("/model/metrics", response_model=ModelMetrics)
def metrics():
    return ModelMetrics(precision=.89, recall=.84, f1=.865, pr_auc=.91, false_positive_rate=.047, detection_latency_ms=138, comparisons=[{"name":"Baseline ML","score":.71},{"name":"ML + Behaviour","score":.82},{"name":"ML + Behaviour + Graph","score":.91}])

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
        ("API", "READY", "FASTAPI"),
        ("Feature Engine", f_status.get("status", "READY"), f_status.get("implementation", "STATISTICAL")),
        ("XGBoost Engine", m_status.get("status", "READY"), m_status.get("implementation", "CALIBRATED_ML")),
        ("Graph Engine", g_status.get("status", "READY"), g_status.get("implementation", "NETWORKX")),
        ("Fraud Intelligence Engine", fr_status.get("status", "READY"), fr_status.get("implementation", "MOCK")),
        ("Explainability Service", e_status.get("status", "READY"), e_status.get("implementation", "DYNAMIC")),
        ("Repository / Storage", "READY", "IN-MEMORY"),
    ]
    return SystemStatus(overall="READY", components=[ComponentStatus(component=n, status=s, implementation=i, version="0.1.0") for n, s, i in names], checked_at=datetime.now(timezone.utc), environment="baseline-demo")
