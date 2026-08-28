import { apiClient } from '../../services/api/client';
import type { EntityProfile } from './types';

const profile: EntityProfile = {
  entity: { id: 'ENT-102', name: 'Neelam Trading Co.', type: 'Business', accountNumber: '•••• 4831', risk: { score: 92, level: 'critical', indicators: ['Connected to active case', 'Rapid movement of funds'] }, location: 'Mumbai, Maharashtra', transactionCount: 247, totalVolume: 15_600_000 },
  users: ['N. Shah — Director', 'D. Shah — Authorized Signatory', 'R. Patel — Account Operator'],
  connectedEntities: [{ name: 'Orion Exports Pvt Ltd', type: 'Business', risk: 'high', relationship: 'Primary sender' }, { name: 'Account 3491', type: 'Individual', risk: 'critical', relationship: 'Common beneficiary' }, { name: 'Apex Commercial Bank', type: 'Bank', risk: 'low', relationship: 'Receiving institution' }, { name: 'Blue Orbit Retail', type: 'Merchant', risk: 'medium', relationship: 'Outgoing counterparty' }],
  activity: [{ date: '27 Aug, 09:41', label: 'Incoming high-value transfer', amount: '+ ₹24.5 L' }, { date: '26 Aug, 16:21', label: 'Outgoing merchant transfer', amount: '− ₹6.8 L' }, { date: '25 Aug, 11:15', label: 'Associated with active case', amount: 'INV-2026-041' }], nodes: [], edges: [],
};
export async function getEntity(id: string): Promise<EntityProfile> { await new Promise((resolve) => setTimeout(resolve, 350)); if (import.meta.env.VITE_ENABLE_MOCK_DATA !== 'false') return profile; // BACKEND TODO: Request the entity profile, relationships, and investigation history.
  return apiClient.get<EntityProfile>(`/entities/${id}`); }
