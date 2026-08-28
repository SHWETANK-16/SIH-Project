"""Real statistical and behavioral feature engineering engine."""
from __future__ import annotations

import logging
from app.engines.interfaces.feature_engine import FeatureEngine, FeatureVector
from app.engines.interfaces.graph_engine import GraphEngine
from app.repositories.interfaces.repositories import TransactionRepository
from app.schemas.models import TransactionCreate

log = logging.getLogger(__name__)


class StatisticalFeatureEngine(FeatureEngine):
    """Calculates behavioral, statistical, and graph-derived features for transaction risk scoring."""

    def __init__(self, transaction_repo: TransactionRepository, graph_engine: GraphEngine) -> None:
        self.transaction_repo = transaction_repo
        self.graph_engine = graph_engine

    def extract_features(self, transaction: TransactionCreate) -> FeatureVector:
        """Extract multi-dimensional behavioral and topological feature vector."""
        source_id = transaction.source_account_id
        all_txs = self.transaction_repo.list()

        # Isolate historical transactions for this entity
        incoming_txs = [t for t in all_txs if t.destination_account_id == source_id]
        outgoing_txs = [t for t in all_txs if t.source_account_id == source_id]

        total_incoming = sum(t.amount for t in incoming_txs)
        total_outgoing = sum(t.amount for t in outgoing_txs)

        # 1. Pass-through ratio: outgoing volume relative to incoming volume
        if total_incoming > 0:
            pass_through = min(1.0, round(total_outgoing / total_incoming, 2))
        elif total_outgoing > 0:
            pass_through = 0.85
        else:
            pass_through = 0.50

        # 2. Behavioral deviation: current transfer amount vs historical average
        historical_amounts = [t.amount for t in outgoing_txs]
        if historical_amounts:
            avg_amount = sum(historical_amounts) / len(historical_amounts)
            deviation = round(transaction.amount / max(1.0, avg_amount), 1)
        else:
            deviation = 1.0

        # 3. Transaction velocity and counterparty dispersion
        velocity = float(len(incoming_txs) + len(outgoing_txs))
        unique_destinations = len({t.destination_account_id for t in outgoing_txs})
        counterparty_ratio = (
            round(unique_destinations / max(1, len(outgoing_txs)), 2) if outgoing_txs else 1.0
        )

        # 4. Topological features from Graph Engine
        graph_context = self.graph_engine.get_network_context(source_id)
        if hasattr(self.graph_engine, "get_centrality_metrics"):
            centrality = self.graph_engine.get_centrality_metrics(source_id)
            in_deg = centrality.get("in_degree", 0.0)
            out_deg = centrality.get("out_degree", 0.0)
            pagerank = centrality.get("pagerank", 0.0)
        else:
            in_deg = float(len(incoming_txs))
            out_deg = float(len(outgoing_txs))
            pagerank = 0.01

        network_degree = float(in_deg + out_deg)
        total_deg = in_deg + out_deg + 0.001
        fan_in_score = round(in_deg / total_deg, 2)
        fan_out_score = round(out_deg / total_deg, 2)
        in_cycle = 1.0 if any("Circular" in ind for ind in graph_context.get("indicators", [])) else 0.0

        return {
            "transaction_amount": float(transaction.amount),
            "transaction_velocity": velocity,
            "pass_through_ratio": pass_through,
            "behaviour_deviation": deviation,
            "network_degree": network_degree,
            "fan_in_score": fan_in_score,
            "fan_out_score": fan_out_score,
            "pagerank_score": round(pagerank * 100, 2),
            "new_counterparty_ratio": counterparty_ratio,
            "in_cycle": in_cycle,
        }

    def status(self) -> dict[str, str]:
        """Return feature engine status."""
        return {
            "implementation": "STATISTICAL",
            "status": "READY",
            "version": "1.0.0",
        }

