"""Train the XGBoost mule-risk classifier and write versioned artifacts.

Run it directly::

    cd backend
    python -m app.ml.train_xgboost

Outputs into ``backend/model/``:

* ``xgboost_mule_risk.json``  — the booster, in XGBoost's portable JSON format
* ``model_metadata.json``     — feature order, tuned threshold, held-out metrics,
                                gain importances, per-typology recall, ablation
                                results, and a training fingerprint

Everything the serving engine and the ``/model/metrics`` endpoint report is read
from those two files, so the dashboard can never drift from the model actually in
use. Nothing here is imported at request time — this module pulls in scikit-learn,
the serving path does not.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone
from typing import Any

from app.ml.dataset import LABEL_NOISE, POSITIVE_RATE, generate_dataset
from app.ml.feature_spec import ABLATION_GROUPS, FEATURE_NAMES
from app.ml.model_store import model_dir, save_artifacts

log = logging.getLogger(__name__)

MODEL_VERSION = "1.0.0"
MODEL_NAME = "XGBoost Mule Risk Classifier"

# Deliberately shallow and well-regularised. The feature space is 12-dimensional
# and partly synthetic; deep trees would memorise the generator instead of
# learning the typology boundaries, and the ablation uplift would collapse.
HYPERPARAMETERS: dict[str, Any] = {
    "n_estimators": 600,
    "max_depth": 4,
    "learning_rate": 0.06,
    "subsample": 0.9,
    "colsample_bytree": 0.85,
    "min_child_weight": 3,
    "reg_lambda": 1.6,
    "reg_alpha": 0.1,
    "gamma": 0.1,
    "objective": "binary:logistic",
    "eval_metric": "aucpr",
    "tree_method": "hist",
}


def _build_classifier(seed: int, scale_pos_weight: float, early_stopping: int = 50):
    import xgboost as xgb

    return xgb.XGBClassifier(
        **HYPERPARAMETERS,
        random_state=seed,
        scale_pos_weight=scale_pos_weight,
        early_stopping_rounds=early_stopping,
    )


def _tune_threshold(y_true, probabilities) -> tuple[float, float]:
    """Pick the probability cut-off that maximises F1 on the validation split.

    Tuning on validation rather than test is what keeps the reported test metrics
    honest — the threshold never sees the data it is scored on.
    """
    import numpy as np
    from sklearn.metrics import f1_score

    best_threshold, best_f1 = 0.5, -1.0
    for candidate in np.linspace(0.05, 0.95, 91):
        score = f1_score(y_true, (probabilities >= candidate).astype(int), zero_division=0)
        if score > best_f1:
            best_threshold, best_f1 = float(candidate), float(score)
    return round(best_threshold, 3), round(best_f1, 4)


def _evaluate(y_true, probabilities, threshold: float) -> dict[str, float]:
    from sklearn.metrics import (
        average_precision_score,
        confusion_matrix,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )

    predictions = (probabilities >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, predictions, labels=[0, 1]).ravel()

    return {
        "precision": round(float(precision_score(y_true, predictions, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, predictions, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, predictions, zero_division=0)), 4),
        "pr_auc": round(float(average_precision_score(y_true, probabilities)), 4),
        "roc_auc": round(float(roc_auc_score(y_true, probabilities)), 4),
        "false_positive_rate": round(float(fp / (fp + tn)) if (fp + tn) else 0.0, 4),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "false_negatives": int(fn),
    }


def _ablation_scores(X_train, y_train, X_val, y_val, X_test, y_test, seed: int) -> list[dict[str, Any]]:
    """Measure real PR-AUC uplift as each intelligence layer is added.

    This is what feeds the "intelligence layer comparison" chart. Every number is
    a trained model evaluated on the same held-out split — not an illustration.
    """
    from sklearn.metrics import average_precision_score

    positives = max(1, int(y_train.sum()))
    spw = float((len(y_train) - positives) / positives)

    results: list[dict[str, Any]] = []
    for label, feature_subset in ABLATION_GROUPS.items():
        indices = [FEATURE_NAMES.index(name) for name in feature_subset]
        model = _build_classifier(seed, spw, early_stopping=40)
        model.fit(
            X_train[:, indices],
            y_train,
            eval_set=[(X_val[:, indices], y_val)],
            verbose=False,
        )
        probabilities = model.predict_proba(X_test[:, indices])[:, 1]
        results.append(
            {
                "name": label,
                "score": round(float(average_precision_score(y_test, probabilities)), 4),
                "features": len(feature_subset),
            }
        )
    return results


def _per_archetype_recall(archetypes, y_true, probabilities, threshold: float) -> dict[str, float]:
    """Recall broken down by behavioural typology, plus false-positive rate per legitimate archetype."""
    import numpy as np

    predictions = (probabilities >= threshold).astype(int)
    breakdown: dict[str, float] = {}
    for name in sorted(set(archetypes.tolist())):
        mask = archetypes == name
        if not mask.any():
            continue
        # For mule archetypes this is recall; for legitimate ones it is the
        # false-positive rate on the hardest negatives we could construct.
        breakdown[name] = round(float(predictions[mask].mean()), 4)
    return breakdown


def _measure_latency(booster, X_sample, repeats: int = 200) -> int:
    """Single-row inference latency in milliseconds, as the API would experience it."""
    import xgboost as xgb

    started = time.perf_counter()
    for i in range(repeats):
        row = X_sample[i % len(X_sample)].reshape(1, -1)
        booster.predict(xgb.DMatrix(row, feature_names=FEATURE_NAMES))
    elapsed_ms = (time.perf_counter() - started) * 1000 / repeats
    return max(1, int(round(elapsed_ms)))


def train(n_samples: int = 12_000, seed: int = 42, verbose: bool = True) -> dict[str, Any]:
    """Train, evaluate, and persist the classifier. Returns the metadata dict."""
    try:
        import numpy as np
        import xgboost as xgb
        from sklearn.model_selection import train_test_split
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise RuntimeError(
            "Training requires xgboost, scikit-learn and numpy. "
            "Install them with: pip install -r requirements.txt"
        ) from exc

    def say(message: str) -> None:
        if verbose:
            print(message)

    say(f"Generating {n_samples:,} labelled synthetic samples (seed={seed}) ...")
    X, y, archetypes = generate_dataset(n_samples=n_samples, seed=seed)

    # 60 / 20 / 20 stratified. Validation drives early stopping and threshold
    # tuning; test is touched exactly once, at the end.
    X_train, X_hold, y_train, y_hold, arch_train, arch_hold = train_test_split(
        X, y, archetypes, test_size=0.4, random_state=seed, stratify=y
    )
    X_val, X_test, y_val, y_test, _, arch_test = train_test_split(
        X_hold, y_hold, arch_hold, test_size=0.5, random_state=seed, stratify=y_hold
    )
    say(f"Split: train={len(y_train):,}  val={len(y_val):,}  test={len(y_test):,}")

    positives = max(1, int(y_train.sum()))
    scale_pos_weight = float((len(y_train) - positives) / positives)

    say("Training primary model ...")
    classifier = _build_classifier(seed, scale_pos_weight)
    classifier.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)

    booster = classifier.get_booster()
    best_iteration = int(getattr(classifier, "best_iteration", 0) or 0)

    # Early stopping leaves the extra rounds inside the booster. The sklearn
    # wrapper silently ignores them at predict time, but the raw Booster used for
    # serving does not — so we physically truncate to the best iteration. Without
    # this, reported metrics come from a different model than the one that scores
    # live requests.
    total_rounds = int(booster.num_boosted_rounds())
    if best_iteration and best_iteration + 1 < total_rounds:
        booster = booster[: best_iteration + 1]
        say(f"Truncated booster {total_rounds} -> {booster.num_boosted_rounds()} rounds (best iteration)")
    booster.feature_names = list(FEATURE_NAMES)
    say(f"Best iteration: {best_iteration} (early stopping on validation PR-AUC)")

    def predict_proba(matrix) -> Any:
        """Score exactly the way the serving engine does — same booster, same DMatrix."""
        return booster.predict(xgb.DMatrix(matrix, feature_names=list(FEATURE_NAMES)))

    val_probabilities = predict_proba(X_val)
    threshold, val_f1 = _tune_threshold(y_val, val_probabilities)
    say(f"Tuned decision threshold: {threshold} (validation F1 {val_f1})")

    test_probabilities = predict_proba(X_test)
    metrics = _evaluate(y_test, test_probabilities, threshold)
    say(
        "Held-out test — precision {precision} · recall {recall} · F1 {f1} · "
        "PR-AUC {pr_auc} · ROC-AUC {roc_auc} · FPR {false_positive_rate}".format(**metrics)
    )

    say("Running ablation study (behaviour / +velocity / +graph) ...")
    comparisons = _ablation_scores(X_train, y_train, X_val, y_val, X_test, y_test, seed)
    for entry in comparisons:
        say(f"  {entry['name']:<32} PR-AUC {entry['score']}  ({entry['features']} features)")

    gain = booster.get_score(importance_type="gain")
    total_gain = sum(gain.values()) or 1.0
    importances = {
        name: round(float(gain.get(name, 0.0)) / total_gain, 4) for name in FEATURE_NAMES
    }

    latency_ms = _measure_latency(booster, X_test)
    say(f"Single-row inference latency: ~{latency_ms} ms")

    metadata: dict[str, Any] = {
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "implementation": "XGBOOST",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "xgboost_version": xgb.__version__,
        "python_version": sys.version.split()[0],
        "features": list(FEATURE_NAMES),
        "n_features": len(FEATURE_NAMES),
        "n_trees": int(booster.num_boosted_rounds()),
        "best_iteration": best_iteration,
        "decision_threshold": threshold,
        "validation_f1": val_f1,
        "hyperparameters": HYPERPARAMETERS,
        "scale_pos_weight": round(scale_pos_weight, 4),
        "training": {
            "n_samples": int(n_samples),
            "seed": int(seed),
            "train_size": int(len(y_train)),
            "validation_size": int(len(y_val)),
            "test_size": int(len(y_test)),
            "positive_rate": POSITIVE_RATE,
            "label_noise": LABEL_NOISE,
            "data_source": "SYNTHETIC_ARCHETYPES",
        },
        "metrics": metrics,
        "comparisons": comparisons,
        "feature_importance": importances,
        "archetype_flag_rate": _per_archetype_recall(arch_test, y_test, test_probabilities, threshold),
        "detection_latency_ms": latency_ms,
        "label": "TRAINED ON SYNTHETIC DATA — INVESTIGATION SIGNAL, NOT PROOF",
    }

    save_artifacts(booster, metadata)
    say(f"\nArtifacts written to {model_dir()}")
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description="Train the FraudTracer XGBoost mule-risk model.")
    parser.add_argument("--samples", type=int, default=12_000, help="Number of synthetic samples to generate.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress output.")
    parser.add_argument("--print-metadata", action="store_true", help="Dump the metadata JSON on completion.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")

    try:
        metadata = train(n_samples=args.samples, seed=args.seed, verbose=not args.quiet)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.print_metadata:
        print(json.dumps(metadata, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
