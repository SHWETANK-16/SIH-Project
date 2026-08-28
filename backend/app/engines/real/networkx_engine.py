"""Real graph intelligence engine using NetworkX for dynamic graph analytics."""
from __future__ import annotations

import logging
from typing import Any, Sequence
import networkx as nx

from app.engines.interfaces.graph_engine import GraphEngine, GraphContext
from app.schemas.models import Transaction, TransactionBase, TransactionCreate

log = logging.getLogger(__name__)


class NetworkXGraphEngine(GraphEngine):
    """Production-ready in-memory Graph Intelligence Engine backed by NetworkX."""

    def __init__(self, initial_transactions: Sequence[Transaction | TransactionBase | dict] | None = None) -> None:
        self.graph: nx.DiGraph = nx.DiGraph()
        if initial_transactions:
            for txn in initial_transactions:
                self.ingest_transaction(txn)
            log.info(
                "NetworkXGraphEngine initialized with %d nodes and %d edges",
                self.graph.number_of_nodes(),
                self.graph.number_of_edges(),
            )

    def ingest_transaction(self, txn: Transaction | TransactionBase | TransactionCreate | dict) -> None:
        """Dynamically add or update directed transaction edges in the graph."""
        if isinstance(txn, dict):
            source = txn.get("source_account_id")
            dest = txn.get("destination_account_id")
            amount = float(txn.get("amount", 0.0))
            txn_id = txn.get("transaction_id")
            timestamp = txn.get("timestamp")
            risk_score = float(txn.get("risk_score", 0.0))
        else:
            source = txn.source_account_id
            dest = txn.destination_account_id
            amount = float(txn.amount)
            txn_id = getattr(txn, "transaction_id", None)
            timestamp = getattr(txn, "timestamp", None)
            risk_score = float(getattr(txn, "risk_score", 0.0))

        if not source or not dest:
            return

        if not self.graph.has_node(source):
            self.graph.add_node(source, entity_type="account")
        if not self.graph.has_node(dest):
            self.graph.add_node(dest, entity_type="account")

        # Track transactions on edge
        if self.graph.has_edge(source, dest):
            edge_data = self.graph[source][dest]
            edge_data["transactions"].append(
                {"transaction_id": txn_id, "amount": amount, "timestamp": timestamp, "risk_score": risk_score}
            )
            edge_data["total_amount"] += amount
            edge_data["count"] += 1
        else:
            self.graph.add_edge(
                source,
                dest,
                total_amount=amount,
                count=1,
                transactions=[
                    {"transaction_id": txn_id, "amount": amount, "timestamp": timestamp, "risk_score": risk_score}
                ],
            )

    def get_network_context(self, entity_id: str) -> GraphContext:
        """Compute real topological metrics, PageRank, cycle detection, and risk indicators."""
        if not self.graph.has_node(entity_id):
            return {
                "network_id": None,
                "connected_entities": 0,
                "graph_score": 25.0,
                "indicators": ["Isolated entity", "No recorded transaction connections"],
            }

        in_degree = self.graph.in_degree(entity_id)
        out_degree = self.graph.out_degree(entity_id)
        predecessors = set(self.graph.predecessors(entity_id))
        successors = set(self.graph.successors(entity_id))
        direct_neighbors = predecessors | successors

        # 2-hop ego neighborhood size
        ego_nodes = set(direct_neighbors)
        ego_nodes.add(entity_id)
        for neighbor in direct_neighbors:
            ego_nodes.update(self.graph.predecessors(neighbor))
            ego_nodes.update(self.graph.successors(neighbor))

        # Check for directed cycle participation (A -> ... -> A)
        in_cycle = any(nx.has_path(self.graph, succ, entity_id) for succ in successors)

        # PageRank computation
        try:
            pr_scores = nx.pagerank(self.graph, alpha=0.85, max_iter=100)
            entity_pr = pr_scores.get(entity_id, 0.0)
            avg_pr = sum(pr_scores.values()) / max(1, len(pr_scores))
            pr_ratio = entity_pr / avg_pr if avg_pr > 0 else 1.0
        except Exception:
            pr_ratio = 1.0

        # Dynamic Indicators based on topological patterns
        indicators: list[str] = []
        if in_cycle:
            indicators.append("Circular transaction cycle detected")
        if in_degree >= 3 and in_degree > out_degree * 1.5:
            indicators.append("High fan-in aggregation node")
        elif out_degree >= 3 and out_degree > in_degree * 1.5:
            indicators.append("High fan-out smurfing/distribution pattern")
        if in_degree >= 2 and out_degree >= 2:
            indicators.append("High velocity pass-through relay")
        if len(direct_neighbors) >= 5 or pr_ratio > 1.8:
            indicators.append("High PageRank central network hub")
        if len(ego_nodes) > 8:
            indicators.append("Dense transaction neighbourhood")
        if not indicators:
            indicators.append("Standard network connectivity")

        # Weakly connected component for network assignment
        components = sorted(nx.weakly_connected_components(self.graph), key=len, reverse=True)
        network_id: str | None = None
        for idx, comp in enumerate(components):
            if entity_id in comp:
                network_id = f"NET-{idx + 1:03d}"
                break

        # Compute composite graph risk score (0 - 100)
        base_score = 45.0
        if in_cycle:
            base_score += 30.0
        if in_degree >= 3 and in_degree > out_degree * 1.5:
            base_score += 18.0
        if out_degree >= 3 and out_degree > in_degree * 1.5:
            base_score += 18.0
        if len(direct_neighbors) >= 5:
            base_score += 12.0
        if pr_ratio > 1.5:
            base_score += min(15.0, (pr_ratio - 1.0) * 10.0)

        graph_score = min(98.5, max(15.0, round(base_score, 1)))

        return {
            "network_id": network_id,
            "connected_entities": len(ego_nodes) - 1,
            "graph_score": graph_score,
            "indicators": indicators,
        }

    def find_paths(self, source: str, destination: str | None = None) -> list[list[str]]:
        """Find real directed money-flow paths between nodes in the graph."""
        if not self.graph.has_node(source):
            return []

        if destination and self.graph.has_node(destination):
            try:
                paths_gen = nx.all_simple_paths(self.graph, source, destination, cutoff=5)
                paths = []
                for idx, path in enumerate(paths_gen):
                    paths.append(path)
                    if idx >= 5:  # Limit top 5 paths
                        break
                return paths if paths else []
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                return []

        # If no destination specified, discover downstream outgoing paths from source
        paths = []
        for succ in list(self.graph.successors(source))[:4]:
            two_hops = list(self.graph.successors(succ))[:3]
            if two_hops:
                for two_hop in two_hops:
                    paths.append([source, succ, two_hop])
            else:
                paths.append([source, succ])
        return paths or [[source]]

    def detect_cycles(self, max_length: int = 6) -> list[list[str]]:
        """Identify circular transaction loops up to max_length."""
        try:
            cycles = [c for c in nx.simple_cycles(self.graph) if 2 <= len(c) <= max_length]
            return cycles[:10]
        except Exception:
            return []

    def get_centrality_metrics(self, entity_id: str) -> dict[str, float]:
        """Compute granular node centrality metrics."""
        if not self.graph.has_node(entity_id):
            return {"in_degree": 0.0, "out_degree": 0.0, "pagerank": 0.0, "betweenness": 0.0}

        in_deg = float(self.graph.in_degree(entity_id))
        out_deg = float(self.graph.out_degree(entity_id))
        try:
            pr = float(nx.pagerank(self.graph).get(entity_id, 0.0))
        except Exception:
            pr = 0.0
        try:
            bw = float(nx.betweenness_centrality(self.graph).get(entity_id, 0.0))
        except Exception:
            bw = 0.0

        return {"in_degree": in_deg, "out_degree": out_deg, "pagerank": pr, "betweenness": bw}

    def status(self) -> dict[str, str]:
        """Return engine status and graph scale metadata."""
        return {
            "implementation": "NETWORKX",
            "status": "READY",
            "version": "1.0.0",
            "nodes": str(self.graph.number_of_nodes()),
            "edges": str(self.graph.number_of_edges()),
        }

