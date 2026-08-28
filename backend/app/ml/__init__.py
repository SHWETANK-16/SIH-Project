"""Machine learning layer: feature contract, synthetic training data, and XGBoost training.

This package is deliberately import-light at module level so that ``app.main`` can
start even when ``xgboost``/``scikit-learn`` are not installed. Heavy imports live
inside the functions that need them.
"""
from app.ml.feature_spec import (
    FEATURE_NAMES,
    FEATURE_LABELS,
    FEATURE_DEFAULTS,
    ABLATION_GROUPS,
    to_vector,
    to_named_vector,
)

__all__ = [
    "FEATURE_NAMES",
    "FEATURE_LABELS",
    "FEATURE_DEFAULTS",
    "ABLATION_GROUPS",
    "to_vector",
    "to_named_vector",
]
