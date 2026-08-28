import { apiClient } from '../../services/api/client';
import type { DashboardData } from './types';

const mockDashboardData: DashboardData = {
  stats: { totalTransactions: 248_563, suspiciousTransactions: 1_276, activeInvestigations: 42, highRiskEntities: 18, amountUnderInvestigation: 78_650_000 },
  timeline: [
    { label: 'Mon', total: 28900, suspicious: 141 }, { label: 'Tue', total: 32400, suspicious: 174 }, { label: 'Wed', total: 29800, suspicious: 136 }, { label: 'Thu', total: 36700, suspicious: 221 }, { label: 'Fri', total: 40200, suspicious: 198 }, { label: 'Sat', total: 31100, suspicious: 167 }, { label: 'Sun', total: 28400, suspicious: 113 },
  ],
  riskDistribution: [{ name: 'Low', value: 62, color: '#1cc86a' }, { name: 'Medium', value: 24, color: '#d7b54b' }, { name: 'High', value: 10, color: '#d8793f' }, { name: 'Critical', value: 4, color: '#c65558' }],
  statusDistribution: [{ name: 'Cleared', value: 68, color: '#45b979' }, { name: 'Review', value: 19, color: '#d7b54b' }, { name: 'Flagged', value: 9, color: '#d8793f' }, { name: 'Blocked', value: 4, color: '#c65558' }],
};

export async function getDashboardData(): Promise<DashboardData> {
  await new Promise((resolve) => setTimeout(resolve, 380));
  if (import.meta.env.VITE_ENABLE_MOCK_DATA !== 'false') return mockDashboardData;
  // BACKEND TODO: Connect dashboard aggregates to the analytics API.
  return apiClient.get<DashboardData>('/dashboard');
}
