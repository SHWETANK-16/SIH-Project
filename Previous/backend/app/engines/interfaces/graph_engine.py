from abc import ABC, abstractmethod
from typing import TypedDict

class GraphContext(TypedDict):
    network_id: str | None
    connected_entities: int
    graph_score: float
    indicators: list[str]

class GraphEngine(ABC):
    @abstractmethod
    def get_network_context(self, entity_id: str) -> GraphContext: ...
    @abstractmethod
    def find_paths(self, source: str, destination: str | None = None) -> list[list[str]]: ...
    @abstractmethod
    def status(self) -> dict[str, str]: ...

