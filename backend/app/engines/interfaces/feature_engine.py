from abc import ABC, abstractmethod
from app.schemas.models import TransactionCreate

FeatureVector = dict[str, float]

class FeatureEngine(ABC):
    @abstractmethod
    def extract_features(self, transaction: TransactionCreate) -> FeatureVector: ...
    @abstractmethod
    def status(self) -> dict[str, str]: ...

