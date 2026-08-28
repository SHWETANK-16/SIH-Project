"""Deterministic demonstrations. No trained model or graph analytics live here."""
from app.engines.interfaces.feature_engine import FeatureEngine, FeatureVector
from app.engines.interfaces.xgboost_engine import XGBoostEngine, ModelPrediction
from app.engines.interfaces.graph_engine import GraphEngine, GraphContext
from app.engines.interfaces.fraud_intelligence_engine import FraudIntelligenceEngine, IntelligenceAssessment
from app.schemas.models import TransactionCreate

class MockFeatureEngine(FeatureEngine):
    def extract_features(self, transaction: TransactionCreate) -> FeatureVector:
        seed = sum(ord(c) for c in transaction.source_account_id) % 17
        return {"transaction_amount": transaction.amount, "transaction_velocity": round(.62 + seed/100, 2), "pass_through_ratio": round(.73 + seed/100, 2), "behaviour_deviation": round(3.1 + seed/2, 1), "network_degree": float(6 + seed), "fan_in_score": .72, "fan_out_score": .76}
    def status(self): return {"implementation": "MOCK", "status": "READY", "version": "0.1.0"}

class MockXGBoostEngine(XGBoostEngine):
    def predict(self, features: FeatureVector) -> ModelPrediction:
        score = min(98.0, round(42 + features["pass_through_ratio"]*30 + min(features["behaviour_deviation"], 10)*2.4, 1))
        return {"model_name": "Mock XGBoost", "model_version": "0.1.0", "risk_score": score, "prediction": "HIGH_RISK" if score >= 70 else "MEDIUM_RISK"}
    def status(self): return {"implementation": "MOCK", "status": "READY", "version": "0.1.0"}

class MockGraphEngine(GraphEngine):
    def get_network_context(self, entity_id: str) -> GraphContext:
        n = int(''.join(filter(str.isdigit, entity_id)) or 1)
        return {"network_id": f"NET-{((n-1)//10)+1:03d}" if n <= 40 else None, "connected_entities": 6 + n % 8, "graph_score": float(68 + n % 25), "indicators": ["Dense transaction neighbourhood", "Rapid multi-hop movement"]}
    def find_paths(self, source: str, destination: str | None = None): return [[source, "ACC-0002", destination or "ACC-0006"]]
    def status(self): return {"implementation": "MOCK", "status": "READY", "version": "0.1.0"}

class MockFraudIntelligenceEngine(FraudIntelligenceEngine):
    def assess(self, features: FeatureVector, model: ModelPrediction, graph: GraphContext) -> IntelligenceAssessment:
        score = round(model["risk_score"]*.65 + graph["graph_score"]*.35, 1)
        level = "CRITICAL" if score >= 85 else "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
        return {"risk_score": score, "risk_level": level, "priority": level, "signals": ["High pass-through ratio", "Behaviour deviation", "High network connectivity", "Rapid transaction movement"]}
    def status(self): return {"implementation": "MOCK", "status": "READY", "version": "0.1.0"}
