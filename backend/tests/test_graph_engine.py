"""Unit tests for NetworkXGraphEngine."""
from datetime import datetime, timezone
from app.engines.real.networkx_engine import NetworkXGraphEngine
from app.schemas.models import Transaction, RiskLevel
from app.data.synthetic import TRANSACTIONS

def test_networkx_initialization():
    engine = NetworkXGraphEngine(TRANSACTIONS)
    assert engine.graph.number_of_nodes() >= 40
    assert engine.graph.number_of_edges() >= 40
    status = engine.status()
    assert status["implementation"] == "NETWORKX"
    assert status["status"] == "READY"
    assert int(status["nodes"]) >= 40

def test_networkx_context_connected_node():
    engine = NetworkXGraphEngine(TRANSACTIONS)
    ctx = engine.get_network_context("ACC-0001")
    assert ctx["connected_entities"] > 0
    assert ctx["graph_score"] >= 15.0
    assert len(ctx["indicators"]) >= 1
    assert ctx["network_id"] is not None

def test_networkx_context_isolated_node():
    engine = NetworkXGraphEngine(TRANSACTIONS)
    ctx = engine.get_network_context("ACC-9999")
    assert ctx["connected_entities"] == 0
    assert ctx["network_id"] is None
    assert "Isolated entity" in ctx["indicators"]

def test_networkx_find_paths():
    engine = NetworkXGraphEngine(TRANSACTIONS)
    # In synthetic data trail: ACC-0001 -> ACC-0002 -> ACC-0003 -> ACC-0004
    paths = engine.find_paths("ACC-0001", "ACC-0004")
    assert len(paths) >= 1
    assert paths[0][0] == "ACC-0001"
    assert paths[0][-1] == "ACC-0004"

def test_networkx_dynamic_ingestion():
    engine = NetworkXGraphEngine([])
    assert engine.graph.number_of_nodes() == 0
    txn = Transaction(
        transaction_id="TXN-TEST-1",
        source_account_id="ACC-A",
        destination_account_id="ACC-B",
        amount=25000.0,
        timestamp=datetime.now(timezone.utc),
        transaction_type="UPI",
        risk_score=85.0,
        risk_level=RiskLevel.HIGH,
    )
    engine.ingest_transaction(txn)
    assert engine.graph.number_of_nodes() == 2
    assert engine.graph.number_of_edges() == 1
    assert engine.graph.has_edge("ACC-A", "ACC-B")
    
    ctx_a = engine.get_network_context("ACC-A")
    assert ctx_a["connected_entities"] == 1

def test_networkx_cycle_detection():
    engine = NetworkXGraphEngine([])
    now = datetime.now(timezone.utc)
    # Create cycle: A -> B -> C -> A
    engine.ingest_transaction({"transaction_id": "T1", "source_account_id": "ACC-C1", "destination_account_id": "ACC-C2", "amount": 1000, "timestamp": now, "risk_score": 75})
    engine.ingest_transaction({"transaction_id": "T2", "source_account_id": "ACC-C2", "destination_account_id": "ACC-C3", "amount": 1000, "timestamp": now, "risk_score": 75})
    engine.ingest_transaction({"transaction_id": "T3", "source_account_id": "ACC-C3", "destination_account_id": "ACC-C1", "amount": 1000, "timestamp": now, "risk_score": 75})
    
    cycles = engine.detect_cycles(max_length=4)
    assert len(cycles) >= 1
    ctx = engine.get_network_context("ACC-C1")
    assert any("Circular transaction" in ind for ind in ctx["indicators"])
    assert ctx["graph_score"] >= 70.0

