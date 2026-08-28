"""Dynamic explainability service translating feature and graph signals into investigator narratives.

Two layers are combined. The threshold layer turns individual feature values into
plain-language findings an investigator can act on. The attribution layer, active
whenever the scoring engine supplies TreeSHAP values, reorders those findings by
how much the model actually relied on each feature and surfaces drivers the
threshold rules have no wording for. Without SHAP the service behaves exactly as
before, so mock and rule-only engines are unaffected.
"""
from __future__ import annotations

from typing import Any
from app.schemas.models import Explanation, ExplanationFactor

# Maps a model feature to the threshold factor that already describes it, so the
# two layers can be reconciled instead of duplicating each other.
FEATURE_TO_FACTOR: dict[str, str] = {
    "pass_through_ratio": "Pass-through ratio",
    "behaviour_deviation": "Behaviour deviation",
    "in_cycle": "Circular settlement",
    "fan_in_score": "Fan-in aggregation",
    "fan_out_score": "Fan-out distribution",
    "network_degree": "Network connectivity",
}

# Below this share of total attribution a driver is noise, not a finding.
MIN_ATTRIBUTION_SHARE = 0.08


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

        drivers = assessment.get("shap_top_drivers") or []
        if drivers:
            factors = self._apply_model_attribution(factors, drivers)
            summary = self._augment_summary(summary, assessment, drivers)

        for note in assessment.get("guardrails_applied") or []:
            factors.append(
                ExplanationFactor(
                    name="Investigative guardrail",
                    impact="medium",
                    description=f"Domain rule overrode the model score — {note}.",
                )
            )

        return Explanation(summary=summary, factors=factors, synthetic=True)

    # ------------------------------------------------------------------ #
    # Model attribution layer (active only when TreeSHAP values are supplied)
    # ------------------------------------------------------------------ #
    @staticmethod
    def _apply_model_attribution(
        factors: list[ExplanationFactor],
        drivers: list[dict[str, Any]],
    ) -> list[ExplanationFactor]:
        """Reorder threshold factors by real attribution and add drivers they omit."""
        rank = {
            FEATURE_TO_FACTOR[d["feature"]]: i
            for i, d in enumerate(drivers)
            if d.get("feature") in FEATURE_TO_FACTOR
        }
        # Factors the model leaned on come first, in its order of reliance.
        ordered = sorted(factors, key=lambda f: rank.get(f.name, len(drivers) + 1))

        described = {f.name for f in ordered}
        for driver in drivers:
            factor_name = FEATURE_TO_FACTOR.get(driver.get("feature", ""))
            if factor_name and factor_name in described:
                continue
            share = float(driver.get("share", 0.0))
            if driver.get("direction") != "increases_risk" or share < MIN_ATTRIBUTION_SHARE:
                continue
            ordered.append(
                ExplanationFactor(
                    name=driver.get("label", driver.get("feature", "Model driver")),
                    impact="high" if share >= 0.20 else "medium",
                    description=(
                        f"Observed value {driver.get('value')} pushed the score upward, accounting for "
                        f"{share * 100:.0f}% of the model's attribution for this decision "
                        f"(TreeSHAP {driver.get('contribution'):+.2f} log-odds)."
                    ),
                )
            )
        return ordered

    @staticmethod
    def _augment_summary(summary: str, assessment: dict[str, Any], drivers: list[dict[str, Any]]) -> str:
        """Append the model's confidence and single strongest driver to the narrative."""
        probability = assessment.get("model_probability")
        lead = next((d for d in drivers if d.get("direction") == "increases_risk"), None)
        parts = [summary]
        if probability is not None:
            parts.append(f"The trained model assigns a {float(probability) * 100:.1f}% mule likelihood.")
        if lead is not None:
            parts.append(f"Its strongest driver is {str(lead.get('label', '')).lower()}.")
        return " ".join(parts)

    def status(self) -> dict[str, str]:
        """Return explainability service status."""
        return {
            "implementation": "DYNAMIC",
            "status": "READY",
            "version": "1.0.0",
        }

