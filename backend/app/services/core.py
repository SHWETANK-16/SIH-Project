import logging
from datetime import datetime, timezone
from uuid import uuid4
from app.engines.interfaces.feature_engine import FeatureEngine
from app.engines.interfaces.xgboost_engine import XGBoostEngine
from app.engines.interfaces.graph_engine import GraphEngine
from app.engines.interfaces.fraud_intelligence_engine import FraudIntelligenceEngine
from app.explainability.explainability_service import ExplainabilityService
from app.repositories.interfaces.repositories import *
from app.schemas.models import *
from app.data.synthetic import build_trace, EXPLANATION
from app.exceptions.handlers import NotFoundError

log=logging.getLogger(__name__)

class TransactionService:
    def __init__(self,repo:TransactionRepository,feature:FeatureEngine,model:XGBoostEngine,graph:GraphEngine,fraud:FraudIntelligenceEngine,explain:ExplainabilityService): self.repo,self.feature,self.model,self.graph,self.fraud,self.explain=repo,feature,model,graph,fraud,explain
    def list(self): return self.repo.list()
    def get(self,id):
        item=self.repo.get(id)
        if not item: raise NotFoundError("TRANSACTION_NOT_FOUND",f"Transaction {id} was not found.")
        return item
    def create(self,data:TransactionCreate)->RiskResult:
        log.info("Executing mock intelligence pipeline")
        features=self.feature.extract_features(data); prediction=self.model.predict(features); graph=self.graph.get_network_context(data.source_account_id); assessment=self.fraud.assess(features,prediction,graph)
        tid=data.transaction_id or f"TXN-{len(self.repo.list())+1:04d}"; risk_level=RiskLevel(assessment["risk_level"])
        tx_obj = Transaction(**data.model_dump(exclude={"transaction_id"}),transaction_id=tid,risk_score=assessment["risk_score"],risk_level=risk_level,status="FLAGGED" if assessment["risk_score"]>=70 else "MONITORED",network_id=graph["network_id"])
        self.repo.add(tx_obj)
        if hasattr(self.graph, "ingest_transaction"):
            self.graph.ingest_transaction(tx_obj)
        return self._result(tid,assessment,prediction,graph,features)
    def assess_account(self,id:str)->RiskResult:
        tx=next((x for x in self.repo.list() if id in (x.source_account_id,x.destination_account_id)),None)
        if not tx: raise NotFoundError("ACCOUNT_NOT_FOUND",f"Account {id} was not found.")
        data=TransactionCreate(**tx.model_dump(include={"transaction_id","source_account_id","destination_account_id","amount","timestamp","transaction_type"})); f=self.feature.extract_features(data); p=self.model.predict(f); g=self.graph.get_network_context(id); a=self.fraud.assess(f,p,g); return self._result(id,a,p,g,f)
    def _result(self,id,a,p,g,f):
        return RiskResult(entity_id=id,risk_score=a["risk_score"],risk_level=RiskLevel(a["risk_level"]),priority=RiskLevel(a["priority"]),signals=[RiskSignal(name=s,severity=RiskLevel(a["risk_level"]),value="Synthetic signal") for s in a["signals"]],model=ModelInfo(name=p["model_name"],version=p["model_version"],implementation=p.get("implementation","CALIBRATED_ML")),network=NetworkSummary(network_id=g["network_id"],connected_entities=g["connected_entities"],graph_score=g["graph_score"]),explanation=self.explain.explain(a,f,g))

class EntityService:
    def __init__(self,repo,kind:str): self.repo,self.kind=repo,kind
    def list(self): return self.repo.list()
    def get(self,id):
        item=self.repo.get(id)
        if not item: raise NotFoundError(f"{self.kind.upper()}_NOT_FOUND",f"{self.kind.title()} {id} was not found.")
        return item

class InvestigationService(EntityService):
    def create(self,data:InvestigationCreate):
        now=datetime.now(timezone.utc); case=Investigation(case_id=f"CASE-{len(self.repo.list())+1:04d}",title=data.title,risk_level=data.risk_level,priority=data.risk_level,network_id=None,network_size=len(data.related_accounts),estimated_suspicious_flow=0,related_accounts=data.related_accounts,key_indicators=["Manual review requested"],created_at=now,updated_at=now,status=InvestigationStatus.NEW,explanation=EXPLANATION,transaction_references=data.transaction_references); return self.repo.add(case)
    def update_status(self,id,status):
        item=self.get(id); updated=item.model_copy(update={"status":status,"updated_at":datetime.now(timezone.utc)}); log.info("Investigation status updated: %s",id); return self.repo.update(updated)

from app.services.temporal_tracing import TemporalTracingService

class TracingService:
    def __init__(self, repo: TransactionRepository | None = None):
        self.tracer = TemporalTracingService(repo or InMemoryTransactionRepository())
    def trace(self, id: str):
        return self.tracer.trace(id)

class SimulationService:
    def __init__(self): self.items={}
    def start(self,p:SimulationRequest):
        sid=f"SIM-{uuid4().hex[:8].upper()}"; strategies=["Rapid transfer","Delayed transfer","Split transfer","Distributed mule network"]
        rounds=[SimulationRound(round_number=i,strategy=strategies[i-1],detection_rate=round(.88-i*.055+p.adaptation_level*.008,3),false_positive_rate=round(.05+i*.007,3),detected_networks=max(1,p.mule_count//(i+2))) for i in range(1,5)]
        sim=Simulation(simulation_id=sid,status="COMPLETED",parameters=p,rounds=rounds,created_at=datetime.now(timezone.utc)); self.items[sid]=sim; return sim
    def get(self,id):
        if id not in self.items: raise NotFoundError("SIMULATION_NOT_FOUND",f"Simulation {id} was not found.")
        return self.items[id]

class BehaviourProfiler:
    def profile(self,account_id): return {"account_id":account_id,"baseline_amount":1600,"current_amount":50000,"deviation":8.1,"implementation":"MOCK"}
class NetworkDiscoveryService:
    def __init__(self,repo): self.repo=repo
    def discover(self): return self.repo.list()
class InvestigationPriorityService:
    def prioritize(self,risk_score): return RiskLevel.CRITICAL if risk_score>=85 else RiskLevel.HIGH if risk_score>=70 else RiskLevel.MEDIUM
class InvestigationReportService:
    def generate(self,case:Investigation): return {"case_id":case.case_id,"risk":case.risk_level,"key_indicators":case.key_indicators,"flow":" → ".join(case.related_accounts),"synthetic":True}
