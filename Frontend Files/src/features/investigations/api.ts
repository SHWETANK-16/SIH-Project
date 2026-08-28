import { apiClient } from '../../services/api/client';
import type { InvestigationWorkspace } from './types';

const workspace: InvestigationWorkspace = {
  investigation: { id: 'INV-2026-041', title: 'Operation Emerald Trace', status: 'open', risk: { score: 92, level: 'critical', indicators: ['Layered funds transfer', 'Mule account cluster'] }, investigator: 'Aarav Mehta', updatedAt: '27 Aug 2026, 10:02', summary: 'Suspected layering network spanning three banks and seven connected accounts.' },
  nodes: [
    { id: 'main', label: 'Neelam Trading', type: 'account', risk: 'critical', x: 390, y: 205, value: '₹24.5 L' },
    { id: 'orion', label: 'Orion Exports', type: 'account', risk: 'high', x: 160, y: 100, value: '₹24.5 L' },
    { id: 'bank-a', label: 'National Union', type: 'bank', risk: 'low', x: 295, y: 95 },
    { id: 'merchant', label: 'Blue Orbit', type: 'merchant', risk: 'medium', x: 590, y: 115, value: '₹6.8 L' },
    { id: 'rajesh', label: 'Rajesh Kumar', type: 'person', risk: 'high', x: 615, y: 300, value: '₹9.7 L' },
    { id: 'apex', label: 'Apex Bank', type: 'bank', risk: 'low', x: 478, y: 365 },
    { id: 'mule', label: 'Account 3491', type: 'account', risk: 'critical', x: 225, y: 338, value: '₹13.2 L' },
    { id: 'state', label: 'State Trust', type: 'bank', risk: 'medium', x: 100, y: 260 },
  ],
  edges: [
    { id: 'e1', source: 'orion', target: 'bank-a', amount: 2450000, risk: 'high' }, { id: 'e2', source: 'bank-a', target: 'main', amount: 2450000, risk: 'critical' }, { id: 'e3', source: 'main', target: 'merchant', amount: 680000, risk: 'medium' }, { id: 'e4', source: 'main', target: 'rajesh', amount: 970000, risk: 'high' }, { id: 'e5', source: 'main', target: 'apex', amount: 880000, risk: 'critical' }, { id: 'e6', source: 'mule', target: 'main', amount: 1320000, risk: 'critical' }, { id: 'e7', source: 'state', target: 'mule', amount: 1320000, risk: 'high' }, { id: 'e8', source: 'mule', target: 'apex', amount: 640000, risk: 'medium' },
  ],
  timeline: [
    { time: '10:02', title: 'Critical risk score escalated', detail: 'New activity increased confidence from 81 to 92.', type: 'alert' }, { time: '09:41', title: 'Transaction TXN-7A91E flagged', detail: '₹24.5 L transferred to Neelam Trading Co.', type: 'transaction' }, { time: '09:24', title: 'Connected account behavior detected', detail: 'Shared device and IP signature confirmed.', type: 'note' }, { time: 'Yesterday', title: 'Investigation opened', detail: 'Case automatically created from anomaly ruleset.', type: 'alert' },
  ],
};

export async function getInvestigation(_id: string): Promise<InvestigationWorkspace> {
  await new Promise((resolve) => setTimeout(resolve, 460));
  if (import.meta.env.VITE_ENABLE_MOCK_DATA !== 'false') return workspace;
  // BACKEND TODO: Request investigation graph and event timeline from the case service.
  return apiClient.get<InvestigationWorkspace>(`/investigations/${_id}`);
}
