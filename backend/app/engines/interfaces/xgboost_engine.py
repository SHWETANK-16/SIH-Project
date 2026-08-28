from abc import ABC, abstractmethod
from typing import TypedDict
from app.engines.interfaces.feature_engine import FeatureVector

class ModelPrediction(TypedDict):
    model_name: str
    model_version: str
    risk_score: float
    prediction: str

class XGBoostEngine(ABC):
    @abstractmethod
    def predict(self, features: FeatureVector) -> ModelPrediction: ...
    @abstractmethod
    def status(self) -> dict[str, str]: ...

