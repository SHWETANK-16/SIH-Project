export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type InvestigationStatus =
  | "NEW"
  | "UNDER_INVESTIGATION"
  | "ESCALATED"
  | "RESOLVED"
  | "FALSE_POSITIVE";
export interface ExplanationFactor {
  name: string;
  impact: "low" | "medium" | "high";
  description: string;
}
export interface Explanation {
  summary: string;
  factors: ExplanationFactor[];
  synthetic: boolean;
}
export interface Transaction {
  transaction_id: string;
  source_account_id: string;
  destination_account_id: string;
  amount: number;
  timestamp: string;
  transaction_type: string;
  risk_score: number;
  risk_level: RiskLevel;
  status: string;
  network_id: string;
  synthetic: boolean;
}
export interface Account {
  account_id: string;
  account_type: string;
  created_at: string;
  transaction_count: number;
  incoming_amount: number;
  outgoing_amount: number;
  beneficiaries: number;
  network_size: number;
  risk_score: number;
  risk_level: RiskLevel;
  status: string;
  synthetic: boolean;
}
export interface NetworkNode {
  id: string;
  label: string;
  risk_score: number;
  risk_level: RiskLevel;
  type: string;
  transaction_count: number;
  incoming: number;
  outgoing: number;
  network_degree: number;
  fan_in: number;
  fan_out: number;
  behaviour_deviation: number;
  indicators: string[];
}
export interface NetworkEdge {
  source: string;
  target: string;
  amount: number;
  timestamp: string;
  transaction_id: string;
  risk_level: RiskLevel;
  hop: number;
}
export interface Network {
  network_id: string;
  name: string;
  risk_score: number;
  risk_level: RiskLevel;
  node_count: number;
  edge_count: number;
  estimated_flow: number;
  key_indicators: string[];
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  discovered_at: string;
  synthetic: boolean;
}
export interface RiskSignal {
  name: string;
  severity: RiskLevel;
  value: string;
}
export interface RiskResult {
  entity_id: string;
  risk_score: number;
  risk_level: RiskLevel;
  priority: RiskLevel;
  signals: RiskSignal[];
  model: { name: string; version: string; implementation: string };
  network: {
    network_id: string | null;
    connected_entities: number;
    graph_score: number;
  };
  explanation: Explanation;
  synthetic: boolean;
}
export interface Investigation {
  case_id: string;
  title: string;
  risk_level: RiskLevel;
  priority: RiskLevel;
  network_id: string;
  network_size: number;
  estimated_suspicious_flow: number;
  related_accounts: string[];
  key_indicators: string[];
  created_at: string;
  updated_at: string;
  status: InvestigationStatus;
  explanation: Explanation;
  transaction_references: string[];
  synthetic: boolean;
}
export interface MoneyFlowHop {
  source: string;
  destination: string;
  amount: number;
  timestamp: string;
  transaction_id: string;
  hop_number: number;
  risk_level: RiskLevel;
  relationship_type: string;
  cumulative_flow: number;
}
export interface MoneyFlow {
  trace_id: string;
  root_transaction_id: string;
  total_traced: number;
  max_depth: number;
  hops: MoneyFlowHop[];
  synthetic: boolean;
}
export interface SimulationRound {
  round_number: number;
  strategy: string;
  detection_rate: number;
  false_positive_rate: number;
  detected_networks: number;
}
export interface Simulation {
  simulation_id: string;
  status: string;
  parameters: {
    fraud_strategy: string;
    mule_count: number;
    transactions: number;
    network_depth: number;
    adaptation_level: number;
  };
  rounds: SimulationRound[];
  created_at: string;
  synthetic: boolean;
}
export interface ModelMetrics {
  precision: number;
  recall: number;
  f1: number;
  pr_auc: number;
  false_positive_rate: number;
  detection_latency_ms: number;
  comparisons: { name: string; score: number }[];
  label: string;
}
export interface SystemStatus {
  overall: string;
  components: {
    component: string;
    status: string;
    implementation: string;
    version: string;
  }[];
  checked_at: string;
  environment: string;
}
