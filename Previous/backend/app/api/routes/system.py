from datetime import datetime,timezone
from fastapi import APIRouter
from app.schemas.models import ModelMetrics,SystemStatus,ComponentStatus
router=APIRouter(tags=["System"])
@router.get("/model/metrics",response_model=ModelMetrics)
def metrics():
    return ModelMetrics(precision=.89,recall=.84,f1=.865,pr_auc=.91,false_positive_rate=.047,detection_latency_ms=138,comparisons=[{"name":"Baseline ML","score":.71},{"name":"ML + Behaviour","score":.82},{"name":"ML + Behaviour + Graph","score":.91}])
@router.get("/system/status",response_model=SystemStatus)
def status():
    names=[("API","READY","FASTAPI"),("Feature Engine","READY","MOCK"),("XGBoost Engine","READY","MOCK"),("Graph Engine","READY","MOCK"),("Fraud Intelligence Engine","READY","MOCK"),("Explainability Service","READY","MOCK"),("Repository / Storage","READY","IN-MEMORY")]
    return SystemStatus(overall="READY",components=[ComponentStatus(component=n,status=s,implementation=i,version="0.1.0") for n,s,i in names],checked_at=datetime.now(timezone.utc),environment="baseline-demo")
