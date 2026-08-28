from datetime import datetime,timezone
from app.engines.mock.engines import MockFeatureEngine,MockXGBoostEngine,MockGraphEngine,MockFraudIntelligenceEngine
from app.schemas.models import TransactionCreate
from app.repositories.memory.repositories import InMemoryAccountRepository

def test_engine_contract_chain_is_deterministic():
    tx=TransactionCreate(source_account_id="ACC-0001",destination_account_id="ACC-0002",amount=50000,timestamp=datetime.now(timezone.utc))
    f=MockFeatureEngine().extract_features(tx); p=MockXGBoostEngine().predict(f); g=MockGraphEngine().get_network_context("ACC-0001"); a=MockFraudIntelligenceEngine().assess(f,p,g)
    assert f==MockFeatureEngine().extract_features(tx) and 0<=a["risk_score"]<=100
def test_repository_returns_synthetic_entities():
    repo=InMemoryAccountRepository(); assert len(repo.list())==40 and repo.get("ACC-0001").synthetic
