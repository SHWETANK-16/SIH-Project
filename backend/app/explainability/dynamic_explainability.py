"""Dynamic explainability service translating feature and graph signals into investigator narratives."""
from __future__ import annotations

from typing import Any
from app.schemas.models import Explanation, ExplanationFactor


class DynamicExplainabilityService:
    """Generates human-interpretable investigation rationales from multi-factor signals."""

    def explain(
        self,
        assessment: dict[str, Any],
        features: dict[str, float],
        graph_context: dict[str, Any],
    ) -> Explanation:
        """Construct detailed explanation factors derived from feature anomalies and topological flags."""
        factors: list[ExplanationFactor] = []

        pass_through = features.get("pass_through_ratio", 0.5)
        deviation = features.get("behaviour_deviation", 1.0)
        in_cycle = features.get("in_cycle", 0.0)
        fan_in = features.get("fan_in_score", 0.5)
        fan_out = features.get("fan_out_score", 0.5)
        degree = features.get("network_degree", 0.0)
        net_id = graph_context.get("network_id") or "observed cluster"

        # 1. Pass-through velocity
        if pass_through >= 0.75:
            factors.append(
                ExplanationFactor(
                    name="Pass-through ratio",
                    impact="high",
                    description=f"Rapid fund pass-through observed ({int(pass_through * 100)}% of incoming funds transferred onward).",
                )
            )
        elif pass_through >= 0.60:
            factors.append(
                ExplanationFactor(
                    name="Pass-through ratio",
                    impact="medium",
                    description=f"Elevated fund pass-through velocity ({int(pass_through * 100)}% transferred onward).",
                )
            )

        # 2. Behavioral deviation
        if deviation >= 3.0:
            factors.append(
                ExplanationFactor(
                    name="Behaviour deviation",
                    impact="high",
                    description=f"Transaction volume is {deviation}× higher than the account's historical baseline.",
                )
            )
        elif deviation >= 1.5:
            factors.append(
                ExplanationFactor(
                    name="Behaviour deviation",
                    impact="medium",
                    description=f"Moderate deviation ({deviation}× baseline) from established transaction profile.",
                )
            )

        # 3. Circular transaction routing
        if in_cycle > 0.5:
            factors.append(
                ExplanationFactor(
                    name="Circular settlement",
                    impact="high",
                    description="Entity is involved in a closed circular money-laundering loop across connected counterparties.",
                )
            )

        # 4. Topology asymmetry
        if fan_in >= 0.70:
            factors.append(
                ExplanationFactor(
                    name="Fan-in aggregation",
                    impact="high",
                    description="Disproportionate number of source accounts funneling funds to this collection point.",
                )
            )
        elif fan_out >= 0.70:
            factors.append(
                ExplanationFactor(
                    name="Fan-out distribution",
                    impact="high",
                    description="Funds rapidly fragmented across multiple outward beneficiaries (smurfing pattern).",
                )
            )

        # 5. Network connectivity
        connected = graph_context.get("connected_entities", int(degree))
        if connected >= 4:
            factors.append(
                ExplanationFactor(
                    name="Network connectivity",
                    impact="medium",
                    description=f"Entity exhibits high connectivity, linked to {connected} active accounts in {net_id}.",
                )
            )

        if not factors:
            factors.append(
                ExplanationFactor(
                    name="Baseline activity",
                    impact="low",
                    description="Standard transaction metrics with no significant deviations detected.",
                )
            )

        risk_score = assessment.get("risk_score", 50.0)
        if risk_score >= 80:
            summary = "Multiple high-severity mule indicators detected requiring priority investigator review."
        elif risk_score >= 60:
            summary = "Elevated network and behavioral patterns warrant closer monitoring and verification."
        else:
            summary = "Transaction activity aligns closely with normal baseline behaviors."

        return Explanation(summary=summary, factors=factors, synthetic=True)

    def status(self) -> dict[str, str]:
        """Return explainability service status."""
        return {
            "implementation": "DYNAMIC",
            "status": "READY",
            "version": "1.0.0",
        }

