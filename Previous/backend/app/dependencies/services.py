from functools import lru_cache
from app.repositories.memory.repositories import *
from app.engines.mock.engines import *
from app.explainability.explainability_service import ExplainabilityService
from app.services.core import *

@lru_cache
def get_transaction_repository(): return InMemoryTransactionRepository()
@lru_cache
def get_account_repository(): return InMemoryAccountRepository()
@lru_cache
def get_network_repository(): return InMemoryNetworkRepository()
@lru_cache
def get_investigation_repository(): return InMemoryInvestigationRepository()
@lru_cache
def get_feature_engine(): return MockFeatureEngine()
@lru_cache
def get_xgboost_engine(): return MockXGBoostEngine()
@lru_cache
def get_graph_engine(): return MockGraphEngine()
@lru_cache
def get_fraud_intelligence_engine(): return MockFraudIntelligenceEngine()
@lru_cache
def get_explainability_service(): return ExplainabilityService()
def get_transaction_service(): return TransactionService(get_transaction_repository(),get_feature_engine(),get_xgboost_engine(),get_graph_engine(),get_fraud_intelligence_engine(),get_explainability_service())
def get_account_service(): return EntityService(get_account_repository(),"account")
def get_network_service(): return EntityService(get_network_repository(),"network")
def get_investigation_service(): return InvestigationService(get_investigation_repository(),"investigation")
@lru_cache
def get_simulation_service(): return SimulationService()
