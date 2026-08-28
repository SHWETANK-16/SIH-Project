"""Temporal money flow tracing service with path-aware traversal and safety limits."""
from __future__ import annotations

from collections import deque
from datetime import timedelta
import logging

from app.exceptions.handlers import NotFoundError
from app.repositories.interfaces.repositories import TransactionRepository
from app.schemas.models import MoneyFlow, MoneyFlowHop, Transaction

log = logging.getLogger(__name__)


class TemporalTracingService:
    """Reconstructs dynamic, time-consistent multi-hop money flow trails across financial accounts."""

    def __init__(self, transaction_repo: TransactionRepository) -> None:
        self.transaction_repo = transaction_repo

    def trace(
        self,
        identifier: str,
        max_hops: int = 5,
        max_transactions: int = 50,
        max_branches: int = 4,
        time_window_hours: int = 72,
    ) -> MoneyFlow:
        """Trace downstream fund movement forward in time with explicit safety bounds.

        Args:
            identifier: Transaction ID (e.g. TXN-0001) or Account ID (e.g. ACC-0001).
            max_hops: Maximum path depth / traversal hops from root (default: 5).
            max_transactions: Global safety limit on total explored transactions (default: 50).
            max_branches: Maximum downstream child branches evaluated per node (default: 4).
            time_window_hours: Maximum forward time horizon in hours (default: 72).
        """
        id_clean = identifier.strip().upper()
        all_txs = self.transaction_repo.list()

        # 1. Resolve Root Transaction
        root_txn = next((t for t in all_txs if t.transaction_id == id_clean), None)
        if not root_txn:
            # If account ID provided, select its highest risk/amount transaction
            account_txs = [t for t in all_txs if id_clean in (t.source_account_id, t.destination_account_id)]
            if account_txs:
                outgoing = [t for t in account_txs if t.source_account_id == id_clean]
                root_txn = max(outgoing or account_txs, key=lambda t: t.amount)
            else:
                raise NotFoundError(
                    "TRANSACTION_NOT_FOUND",
                    f"Entity or transaction reference '{identifier}' was not found for money-flow tracing.",
                )

        # 2. Path-Aware Breadth-First Traversal with Global & Path Visited Sets
        # Tracking transaction IDs and path lineages allows accounts to be legitimately revisited
        # across distinct transaction paths in a MultiDiGraph while preventing circular re-entry on the same path.
        visited_txns: set[str] = {root_txn.transaction_id}
        hops: list[MoneyFlowHop] = []
        cumulative_flow = root_txn.amount

        hops.append(
            MoneyFlowHop(
                source=root_txn.source_account_id,
                destination=root_txn.destination_account_id,
                amount=root_txn.amount,
                timestamp=root_txn.timestamp,
                transaction_id=root_txn.transaction_id,
                hop_number=1,
                risk_level=root_txn.risk_level,
                relationship_type="INITIAL_TRANSFER",
                cumulative_flow=cumulative_flow,
            )
        )

        # Queue contains: (curr_txn, current_hop_number, path_transaction_ids)
        queue: deque[tuple[Transaction, int, tuple[str, ...]]] = deque(
            [(root_txn, 1, (root_txn.transaction_id,))]
        )

        while queue and len(hops) < max_transactions:
            curr_tx, hop_num, path_txns = queue.popleft()
            if hop_num >= max_hops:
                continue

            next_hop = hop_num + 1
            curr_dest = curr_tx.destination_account_id
            curr_time = curr_tx.timestamp

            # Find valid downstream transfers:
            # 1. Source matches destination of current hop
            # 2. Timestamp is at or after current transfer (time-forward propagation)
            # 3. Within the configurable time window
            # 4. Transaction not already in current lineage path
            candidates = [
                t
                for t in all_txs
                if t.source_account_id == curr_dest
                and t.timestamp >= curr_time
                and (t.timestamp - curr_time).total_seconds() <= time_window_hours * 3600
                and t.transaction_id not in path_txns
                and t.transaction_id not in visited_txns
            ]

            candidates.sort(key=lambda t: t.timestamp)

            # Bounded branch expansion (smurfing / fan-out cap)
            for child_tx in candidates[:max_branches]:
                if len(hops) >= max_transactions:
                    break

                visited_txns.add(child_tx.transaction_id)
                time_diff_sec = (child_tx.timestamp - curr_time).total_seconds()

                if len(candidates) > 1:
                    rel_type = "SPLIT_FAN_OUT"
                elif time_diff_sec <= 1800:
                    rel_type = "RAPID_RELAY"
                else:
                    rel_type = "TRANSFER"

                cumulative_flow += child_tx.amount
                hops.append(
                    MoneyFlowHop(
                        source=child_tx.source_account_id,
                        destination=child_tx.destination_account_id,
                        amount=child_tx.amount,
                        timestamp=child_tx.timestamp,
                        transaction_id=child_tx.transaction_id,
                        hop_number=next_hop,
                        risk_level=child_tx.risk_level,
                        relationship_type=rel_type,
                        cumulative_flow=cumulative_flow,
                    )
                )

                if next_hop < max_hops:
                    queue.append((child_tx, next_hop, path_txns + (child_tx.transaction_id,)))

        total_traced = sum(h.amount for h in hops)
        max_d = max((h.hop_number for h in hops), default=1)

        return MoneyFlow(
            trace_id=f"TRACE-{id_clean}",
            root_transaction_id=root_txn.transaction_id,
            total_traced=total_traced,
            max_depth=max_d,
            hops=hops,
            synthetic=True,
        )

