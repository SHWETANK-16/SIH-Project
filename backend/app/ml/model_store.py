"""Model artifact location, loading, and save helpers.

Kept separate from the training script so the serving engine never has to import
scikit-learn — inference needs only ``xgboost``.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

MODEL_FILENAME = "xgboost_mule_risk.json"
METADATA_FILENAME = "model_metadata.json"

# backend/app/ml/model_store.py -> parents[2] == backend/
_BACKEND_ROOT = Path(__file__).resolve().parents[2]


def model_dir() -> Path:
    """Directory holding the trained artifacts. Override with ``ML_MODEL_DIR``."""
    override = os.getenv("ML_MODEL_DIR")
    return Path(override).expanduser().resolve() if override else _BACKEND_ROOT / "model"


def model_path() -> Path:
    return model_dir() / MODEL_FILENAME


def metadata_path() -> Path:
    return model_dir() / METADATA_FILENAME


def artifacts_exist() -> bool:
    return model_path().is_file() and metadata_path().is_file()


def save_artifacts(booster: Any, metadata: dict[str, Any]) -> tuple[Path, Path]:
    """Persist the booster and its metadata side by side."""
    target = model_dir()
    target.mkdir(parents=True, exist_ok=True)

    booster.save_model(str(model_path()))
    metadata_path().write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    log.info("Saved model artifacts to %s", target)
    return model_path(), metadata_path()


def load_metadata() -> dict[str, Any] | None:
    path = metadata_path()
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        log.warning("Model metadata at %s is unreadable: %s", path, exc)
        return None


def load_booster() -> Any | None:
    """Load the saved booster, or ``None`` if xgboost is missing or the file is absent."""
    path = model_path()
    if not path.is_file():
        return None
    try:
        import xgboost as xgb
    except ImportError:
        log.warning("xgboost is not installed — cannot load %s", path)
        return None
    try:
        booster = xgb.Booster()
        booster.load_model(str(path))
        return booster
    except Exception as exc:  # pragma: no cover - corrupt artifact guard
        log.error("Failed to load booster from %s: %s", path, exc)
        return None
