export type ReportSection = 'Investigation Summary' | 'Transaction Summary' | 'Risk Analysis' | 'Network Findings' | 'Evidence' | 'Timeline';
export interface ReportConfig { title: string; caseId: string; sections: ReportSection[]; classification: 'Restricted' | 'Confidential'; }
