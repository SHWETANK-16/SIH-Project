import { apiClient } from '../../services/api/client';
import type { ReportConfig } from './types';

export async function generateReport(config: ReportConfig): Promise<{ reportId: string }> {
  await new Promise((resolve) => setTimeout(resolve, 650));
  if (import.meta.env.VITE_ENABLE_MOCK_DATA !== 'false') return { reportId: 'RPT-2026-128' };
  // BACKEND TODO: Connect report generation to backend service.
  return apiClient.post<{ reportId: string }>('/reports', config);
}
