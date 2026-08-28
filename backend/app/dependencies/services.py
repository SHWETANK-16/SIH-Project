from functools import lru_cache
from app.repositories.memory.repositories import *
from app.engines.mock.engines import *
from app.engines.real.networkx_engine import NetworkXGraphEngine
from app.engines.real.statistical_feature_engine import StatisticalFeatureEngine
from app.engines.real.calibrated_ml_engine import CalibratedMLEngine
from app.engines.real.xgboost_risk_engine import XGBoostRiskEngine
from app.explainability.dynamic_explainability import DynamicExplainabilityService
from app.services.core import *
from app.config.settings import get_settings

@lru_cache
def get_transaction_repository(): return InMemoryTransactionRepository()
@lru_cache
def get_account_repository(): return InMemoryAccountRepository()
@lru_cache
def get_network_repository(): return InMemoryNetworkRepository()
@lru_cache
def get_investigation_repository(): return InMemoryInvestigationRepository()
@lru_cache
def get_graph_engine(): return NetworkXGraphEngine(get_transaction_repository().list())
@lru_cache
def get_feature_engine(): return StatisticalFeatureEngine(get_transaction_repository(), get_graph_engine())
@lru_cache
def get_xgboost_engine():
    # Hybrid: trained XGBoost blended with the calibrated domain rules, which stay
    # in the codebase as both a blend component and an automatic fallback.
    s=get_settings()
    return XGBoostRiskEngine(model_weight=s.ml_model_weight,auto_train=s.ml_auto_train,auto_train_samples=s.ml_auto_train_samples,auto_train_seed=s.ml_seed)
@lru_cache
def get_fraud_intelligence_engine(): return MockFraudIntelligenceEngine()
@lru_cache
def get_explainability_service(): return DynamicExplainabilityService()
def get_transaction_service(): return TransactionService(get_transaction_repository(),get_feature_engine(),get_xgboost_engine(),get_graph_engine(),get_fraud_intelligence_engine(),get_explainability_service())
def get_account_service(): return EntityService(get_account_repository(),"account")
def get_network_service(): return EntityService(get_network_repository(),"network")
def get_investigation_service(): return InvestigationService(get_investigation_repository(),"investigation")
def get_tracing_service(): return TracingService(get_transaction_repository())
@lru_cache
def get_simulation_service(): return SimulationService()
