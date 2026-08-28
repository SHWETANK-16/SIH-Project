from abc import ABC, abstractmethod
from typing import TypedDict
from app.engines.interfaces.feature_engine import FeatureVector
from app.engines.interfaces.xgboost_engine import ModelPrediction
from app.engines.interfaces.graph_engine import GraphContext

class IntelligenceAssessment(TypedDict):
    risk_score: float
    risk_level: str
    priority: str
    signals: list[str]

class FraudIntelligenceEngine(ABC):
    @abstractmethod
    def assess(self, features: FeatureVector, model: ModelPrediction, graph: GraphContext) -> IntelligenceAssessment: ...
    @abstractmethod
    def status(self) -> dict[str, str]: ...

