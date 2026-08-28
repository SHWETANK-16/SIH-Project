export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';
export type TransactionStatus = 'completed' | 'pending' | 'flagged' | 'blocked';

export interface RiskScore {
  score: number;
  level: RiskLevel;
  indicators: string[];
}

export interface Transaction {
  id: string;
  sender: string;
  receiver: string;
  amount: number;
  date: string;
  status: TransactionStatus;
  risk: RiskScore;
  senderBank: string;
  receiverBank: string;
  category: string;
}

export interface Investigation {
  id: string;
  title: string;
  status: 'open' | 'monitoring' | 'closed';
  risk: RiskScore;
  investigator: string;
  updatedAt: string;
  summary: string;
}

export interface Entity {
  id: string;
  name: string;
  type: 'Individual' | 'Business' | 'Bank' | 'Merchant';
  accountNumber: string;
  risk: RiskScore;
  location: string;
  transactionCount: number;
  totalVolume: number;
}

export interface Alert {
  id: string;
  severity: RiskLevel;
  entity: string;
  transactionId: string;
  reason: string;
  timestamp: string;
  status: 'new' | 'reviewing' | 'resolved';
}

export interface NetworkNode {
  id: string;
  label: string;
  type: 'account' | 'person' | 'bank' | 'merchant' | 'transaction' | 'origin' | 'hub';
  risk: RiskLevel;
  riskScore?: number;
  x: number;
  y: number;
  value?: string;
}

export interface NetworkEdge {
  id: string;
  source: string;
  target: string;
  amount: number;
  risk: RiskLevel;
}

export interface DashboardStats {
  totalTransactions: number;
  suspiciousTransactions: number;
  activeInvestigations: number;
  highRiskEntities: number;
  amountUnderInvestigation: number;
}

export interface User {
  id: string;
  name: string;
  role: string;
  initials: string;
}
