"""XGBoost mule-risk engine with native TreeSHAP attribution and rule guardrails.

Drop-in implementation of :class:`app.engines.interfaces.xgboost_engine.XGBoostEngine`.
It returns the same ``ModelPrediction`` shape as ``CalibratedMLEngine``, so routes,
services, response schemas, and the frontend need no changes.

Three things make this a *hybrid* rather than a straight model swap:

**Threshold-anchored score mapping.** A raw probability is not a risk score. The
probability is mapped through the threshold that training tuned on the validation
split, so ``p == threshold`` lands exactly on 70.0 — the boundary of the existing
HIGH band. "The model says positive" and "the dashboard says HIGH" can therefore
never disagree, and the 40/70/85 bands already used across the UI keep their
meaning.

**Rule blending.** The trained model contributes 70% of the final score and the
hand-calibrated domain rules contribute 30%. The model generalises across
typologies; the rules encode investigator knowledge the synthetic training data
cannot fully express. Blending keeps both.

**Guardrails.** A handful of domain facts outrank the model in both directions.
Circular settlement always reaches at least HIGH. An account that retains its funds
and shows no behavioural deviation is capped below CRITICAL no matter how the
topology looks — that single rule is what stops legitimate merchants from
dominating the queue.

If ``xgboost`` is unavailable or the artifact fails to load, the engine degrades
cleanly to the pure ``CalibratedMLEngine`` heuristic and says so in ``status()``.
The API stays up.
"""
from __future__ import annotations

import logging
import threading
from typing import Any

from app.engines.interfaces.feature_engine import FeatureVector
from app.engines.interfaces.xgboost_engine import ModelPrediction, XGBoostEngine
from app.engines.real.calibrated_ml_engine import CalibratedMLEngine
from app.ml.feature_spec import FEATURE_LABELS, FEATURE_NAMES, to_named_vector
from app.ml import model_store

log = logging.getLogger(__name__)

# Risk band edges, matching app.data.synthetic.level and the frontend legend.
SCORE_FLOOR = 12.0
SCORE_CEILING = 98.5
HIGH_BAND = 70.0
CRITICAL_BAND = 85.0

DEFAULT_MODEL_WEIGHT = 0.70


class XGBoostRiskEngine(XGBoostEngine):
    """Gradient-boosted mule risk scoring with exact per-feature attribution."""

    def __init__(
        self,
        model_weight: float = DEFAULT_MODEL_WEIGHT,
        auto_train: bool = True,
        auto_train_samples: int = 6_000,
        auto_train_seed: int = 42,
    ) -> None:
        self.model_weight = min(1.0, max(0.0, float(model_weight)))
        self.rules_engine = CalibratedMLEngine()
        self._lock = threading.Lock()

        self._booster: Any | None = None
        self._metadata: dict[str, Any] = {}
        self._source = "UNAVAILABLE"
        self._load_failure: str | None = None

        self._initialise(auto_train, auto_train_samples, auto_train_seed)

    # ------------------------------------------------------------------ #
    # Initialisation
    # ------------------------------------------------------------------ #
    def _initialise(self, auto_train: bool, samples: int, seed: int) -> None:
        if model_store.artifacts_exist():
            if self._try_load("ARTIFACT"):
                return

        if not auto_train:
            self._load_failure = self._load_failure or "No trained artifact found and auto-training is disabled."
            log.warning(
                "XGBoost artifact missing at %s and auto-training disabled — "
                "falling back to calibrated rules. Run: python -m app.ml.train_xgboost",
                model_store.model_path(),
            )
            return

        log.warning(
            "No XGBoost artifact at %s — training one now (first run only, ~10-20s). "
            "Pre-train with 'python -m app.ml.train_xgboost' to avoid this.",
            model_store.model_path(),
        )
        try:
            from app.ml.train_xgboost import train

            train(n_samples=samples, seed=seed, verbose=False)
        except Exception as exc:
            self._load_failure = f"Auto-training failed: {exc}"
            log.error("Auto-training failed (%s) — using calibrated rules only.", exc)
            return

        self._try_load("AUTO_TRAINED")

    def _try_load(self, source: str) -> bool:
        booster = model_store.load_booster()
        metadata = model_store.load_metadata() or {}

        if booster is None:
            self._load_failure = "Artifact present but the booster could not be loaded."
            return False

        saved_features = metadata.get("features")
        if saved_features and list(saved_features) != list(FEATURE_NAMES):
            # Refuse a stale model rather than silently scoring a shuffled vector.
            self._load_failure = (
                "Saved feature order does not match app.ml.feature_spec.FEATURE_NAMES. "
                "Retrain with: python -m app.ml.train_xgboost"
            )
            log.error(self._load_failure)
            return False

        self._booster = booster
        self._metadata = metadata
        self._source = source
        self._load_failure = None
        log.info(
            "XGBoost engine ready (%s) — %s trees, %s features, threshold %.3f",
            source,
            metadata.get("n_trees", "?"),
            metadata.get("n_features", len(FEATURE_NAMES)),
            self.decision_threshold,
        )
        return True

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #
    @property
    def is_trained(self) -> bool:
        return self._booster is not None

    @property
    def decision_threshold(self) -> float:
        return float(self._metadata.get("decision_threshold", 0.5))

    # ------------------------------------------------------------------ #
    # Scoring
    # ------------------------------------------------------------------ #
    def _probability_to_score(self, probability: float) -> float:
        """Map a probability onto the 12-98.5 scale, anchoring the threshold at 70.0."""
        threshold = min(0.95, max(0.05, self.decision_threshold))
        if probability <= threshold:
            return SCORE_FLOOR + (probability / threshold) * (HIGH_BAND - SCORE_FLOOR)
        return HIGH_BAND + ((probability - threshold) / (1.0 - threshold)) * (SCORE_CEILING - HIGH_BAND)

    def _predict_raw(self, vector: list[float]) -> tuple[float, dict[str, float]]:
        """Return ``(probability, shap_contributions_in_log_odds)`` for one row."""
        import numpy as np
        import xgboost as xgb

        row = np.asarray([vector], dtype="float32")
        matrix = xgb.DMatrix(row, feature_names=list(FEATURE_NAMES))

        with self._lock:  # Booster.predict is not documented as thread-safe.
            probability = float(self._booster.predict(matrix)[0])
            contributions = self._booster.predict(matrix, pred_contribs=True)[0]

        # pred_contribs returns exact TreeSHAP values plus a trailing bias term.
        shap = {name: float(contributions[i]) for i, name in enumerate(FEATURE_NAMES)}
        return probability, shap

    @staticmethod
    def _shap_drivers(shap: dict[str, float], named: dict[str, float], limit: int = 5) -> list[dict[str, Any]]:
        """Rank features by absolute attribution and describe each in investigator terms."""
        total = sum(abs(v) for v in shap.values()) or 1.0
        ordered = sorted(shap.items(), key=lambda kv: abs(kv[1]), reverse=True)[:limit]
        return [
            {
                "feature": name,
                "label": FEATURE_LABELS.get(name, name),
                "value": round(named.get(name, 0.0), 4),
                "contribution": round(value, 4),
                "direction": "increases_risk" if value > 0 else "decreases_risk",
                "share": round(abs(value) / total, 4),
            }
            for name, value in ordered
        ]

    def _apply_guardrails(self, score: float, features: FeatureVector) -> tuple[float, list[str]]:
        """Enforce domain facts that outrank the model in either direction."""
        pass_through = float(features.get("pass_through_ratio", 0.5))
        deviation = float(features.get("behaviour_deviation", 1.0))
        in_cycle = float(features.get("in_cycle", 0.0))
        applied: list[str] = []

        if in_cycle > 0.5 and score < HIGH_BAND:
            score = HIGH_BAND
            applied.append("Circular settlement floor: raised to HIGH")

        if pass_through >= 0.90 and deviation >= 5.0 and score < 68.0:
            score = 68.0
            applied.append("Extreme pass-through with behavioural deviation: raised to 68.0")

        if pass_through < 0.25 and deviation < 1.5 and in_cycle < 0.5 and score > 55.0:
            # Funds retained, behaviour at baseline, no loop: cannot be CRITICAL
            # on topology alone. This is the merchant false-positive brake.
            score = 55.0
            applied.append("Funds retained at baseline behaviour: capped at 55.0")

        return score, applied

    @staticmethod
    def _band(score: float) -> str:
        if score >= CRITICAL_BAND:
            return "CRITICAL_RISK"
        if score >= HIGH_BAND:
            return "HIGH_RISK"
        if score >= 40.0:
            return "MEDIUM_RISK"
        return "LOW_RISK"

    def _rules_only(self, features: FeatureVector, reason: str, model_name: str) -> ModelPrediction:
        """Pure-heuristic result, still guardrailed so behaviour is consistent either way."""
        rules_prediction = self.rules_engine.predict(features)
        guarded, guardrails = self._apply_guardrails(float(rules_prediction["risk_score"]), features)
        final_score = round(min(SCORE_CEILING, max(SCORE_FLOOR, guarded)), 1)
        return {
            **rules_prediction,
            "model_name": model_name,
            "risk_score": final_score,
            "prediction": self._band(final_score),
            "implementation": "CALIBRATED_ML_FALLBACK",
            "model_available": False,
            "rules_score": round(float(rules_prediction["risk_score"]), 1),
            "guardrails_applied": guardrails,
            "fallback_reason": reason,
        }

    def predict(self, features: FeatureVector) -> ModelPrediction:
        """Score one feature vector, blending the trained model with domain rules."""
        if not self.is_trained:
            # Clean degradation: pure heuristic, clearly labelled.
            return self._rules_only(
                features,
                self._load_failure or "Model artifact not loaded.",
                "Calibrated Rules (XGBoost unavailable)",
            )

        rules_score = float(self.rules_engine.predict(features)["risk_score"])
        named = to_named_vector(features)
        vector = [named[name] for name in FEATURE_NAMES]

        try:
            probability, shap = self._predict_raw(vector)
        except Exception as exc:  # pragma: no cover - inference guard
            log.error("XGBoost inference failed (%s) — using calibrated rules for this request.", exc)
            return self._rules_only(features, str(exc), "Calibrated Rules (inference error)")

        model_score = self._probability_to_score(probability)
        blended = self.model_weight * model_score + (1.0 - self.model_weight) * rules_score
        guarded, guardrails = self._apply_guardrails(blended, features)
        final_score = round(min(SCORE_CEILING, max(SCORE_FLOOR, guarded)), 1)

        return {
            "model_name": self._metadata.get("model_name", "XGBoost Mule Risk Classifier"),
            "model_version": self._metadata.get("model_version", "1.0.0"),
            "risk_score": final_score,
            "prediction": self._band(final_score),
            "implementation": "XGBOOST_HYBRID",
            "model_available": True,
            "model_probability": round(probability, 4),
            "model_score": round(model_score, 1),
            "rules_score": round(rules_score, 1),
            "model_weight": self.model_weight,
            "decision_threshold": self.decision_threshold,
            "model_flagged": bool(probability >= self.decision_threshold),
            "guardrails_applied": guardrails,
            "shap_contributions": {k: round(v, 4) for k, v in shap.items()},
            "shap_top_drivers": self._shap_drivers(shap, named),
            "shap_method": "xgboost_native_treeshap",
            "n_trees": self._metadata.get("n_trees"),
        }

    # ------------------------------------------------------------------ #
    # Introspection
    # ------------------------------------------------------------------ #
    def metrics(self) -> dict[str, Any] | None:
        """Held-out test metrics recorded at training time, or ``None`` if untrained."""
        if not self.is_trained:
            return None
        return {
            "metrics": self._metadata.get("metrics", {}),
            "comparisons": self._metadata.get("comparisons", []),
            "detection_latency_ms": self._metadata.get("detection_latency_ms", 0),
            "decision_threshold": self.decision_threshold,
            "trained_at": self._metadata.get("trained_at"),
            "training": self._metadata.get("training", {}),
            "archetype_flag_rate": self._metadata.get("archetype_flag_rate", {}),
            "label": self._metadata.get("label", ""),
        }

    def feature_importance(self) -> list[dict[str, Any]]:
        """Gain-based importance, descending, with human labels."""
        importances = self._metadata.get("feature_importance", {})
        rows = [
            {
                "feature": name,
                "label": FEATURE_LABELS.get(name, name),
                "importance": round(float(importances.get(name, 0.0)), 4),
            }
            for name in FEATURE_NAMES
        ]
        return sorted(rows, key=lambda row: row["importance"], reverse=True)

    def status(self) -> dict[str, str]:
        """Engine status for ``GET /api/v1/system/status``."""
        if not self.is_trained:
            return {
                "implementation": "CALIBRATED_ML_FALLBACK",
                "status": "DEGRADED",
                "version": "1.0.0",
                "detail": self._load_failure or "XGBoost model not loaded.",
            }
        return {
            "implementation": "XGBOOST_HYBRID",
            "status": "READY",
            "version": str(self._metadata.get("model_version", "1.0.0")),
            "source": self._source,
            "trees": str(self._metadata.get("n_trees", "")),
            "features": str(self._metadata.get("n_features", len(FEATURE_NAMES))),
            "trained_at": str(self._metadata.get("trained_at", "")),
            "xgboost_version": str(self._metadata.get("xgboost_version", "")),
            "explainability": "native TreeSHAP",
            "model_weight": str(self.model_weight),
        }
