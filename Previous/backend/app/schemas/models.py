"""Strongly typed public API contracts. All financial data is synthetic."""
from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class InvestigationStatus(str, Enum):
    NEW = "NEW"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"
    FALSE_POSITIVE = "FALSE_POSITIVE"


class RiskSignal(BaseModel):
    name: str
    severity: RiskLevel
    value: str


class ExplanationFactor(BaseModel):
    name: str
    impact: Literal["low", "medium", "high"]
    description: str


class Explanation(BaseModel):
    summary: str
    factors: list[ExplanationFactor]
    synthetic: bool = True


class TransactionBase(BaseModel):
    source_account_id: str
    destination_account_id: str
    amount: float = Field(gt=0)
    timestamp: datetime
    transaction_type: str = "IMPS"


class TransactionCreate(TransactionBase):
    transaction_id: str | None = None


class Transaction(TransactionBase):
    transaction_id: str
    risk_score: float = Field(ge=0, le=100)
    risk_level: RiskLevel
    status: str = "REVIEWED"
    network_id: str | None = None
    synthetic: bool = True


class Account(BaseModel):
    account_id: str
    account_type: str
    created_at: datetime
    transaction_count: int
    incoming_amount: float
    outgoing_amount: float
    beneficiaries: int
    network_size: int
    risk_score: float
    risk_level: RiskLevel
    status: str
    synthetic: bool = True


class NetworkNode(BaseModel):
    id: str
    label: str
    risk_score: float
    risk_level: RiskLevel
    type: str
    transaction_count: int = 0
    incoming: float = 0
    outgoing: float = 0
    network_degree: int = 0
    fan_in: float = 0
    fan_out: float = 0
    behaviour_deviation: float = 0
    indicators: list[str] = []


class NetworkEdge(BaseModel):
    source: str
    target: str
    amount: float
    timestamp: datetime
    transaction_id: str
    risk_level: RiskLevel
    hop: int = 1


class Network(BaseModel):
    network_id: str
    name: str
    risk_score: float
    risk_level: RiskLevel
    node_count: int
    edge_count: int
    estimated_flow: float
    key_indicators: list[str]
    nodes: list[NetworkNode]
    edges: list[NetworkEdge]
    discovered_at: datetime
    synthetic: bool = True


class RiskCheckRequest(BaseModel):
    account_id: str | None = None
    transaction: TransactionCreate | None = None


class ModelInfo(BaseModel):
    name: str
    version: str
    implementation: str = "MOCK"


class NetworkSummary(BaseModel):
    network_id: str | None
    connected_entities: int
    graph_score: float


class RiskResult(BaseModel):
    entity_id: str
    risk_score: float
    risk_level: RiskLevel
    priority: RiskLevel
    signals: list[RiskSignal]
    model: ModelInfo
    network: NetworkSummary
    explanation: Explanation
    synthetic: bool = True


class InvestigationCreate(BaseModel):
    title: str
    related_accounts: list[str]
    transaction_references: list[str] = []
    risk_level: RiskLevel = RiskLevel.MEDIUM


class StatusUpdate(BaseModel):
    status: InvestigationStatus


class Investigation(BaseModel):
    case_id: str
    title: str
    risk_level: RiskLevel
    priority: RiskLevel
    network_id: str | None
    network_size: int
    estimated_suspicious_flow: float
    related_accounts: list[str]
    key_indicators: list[str]
    created_at: datetime
    updated_at: datetime
    status: InvestigationStatus
    explanation: Explanation
    transaction_references: list[str]
    synthetic: bool = True


class MoneyFlowHop(BaseModel):
    source: str
    destination: str
    amount: float
    timestamp: datetime
    transaction_id: str
    hop_number: int
    risk_level: RiskLevel
    relationship_type: str
    cumulative_flow: float


class MoneyFlow(BaseModel):
    trace_id: str
    root_transaction_id: str
    total_traced: float
    max_depth: int
    hops: list[MoneyFlowHop]
    synthetic: bool = True


class SimulationRequest(BaseModel):
    fraud_strategy: str = "Rapid Pass-Through"
    mule_count: int = Field(default=20, ge=1, le=100)
    transactions: int = Field(default=50000, ge=1)
    network_depth: int = Field(default=4, ge=1, le=10)
    adaptation_level: int = Field(default=3, ge=1, le=5)


class SimulationRound(BaseModel):
    round_number: int
    strategy: str
    detection_rate: float
    false_positive_rate: float
    detected_networks: int


class Simulation(BaseModel):
    simulation_id: str
    status: str
    parameters: SimulationRequest
    rounds: list[SimulationRound]
    created_at: datetime
    synthetic: bool = True


class ModelMetrics(BaseModel):
    precision: float
    recall: float
    f1: float
    pr_auc: float
    false_positive_rate: float
    detection_latency_ms: int
    comparisons: list[dict[str, str | float]]
    label: str = "MOCK METRICS — NOT MEASURED PERFORMANCE"


class ComponentStatus(BaseModel):
    component: str
    status: str
    implementation: str
    version: str


class SystemStatus(BaseModel):
    overall: str
    components: list[ComponentStatus]
    checked_at: datetime
    environment: str

