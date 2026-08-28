import { apiClient } from '../../services/api/client';
import type { AlertsResponse } from './types';

const mockAlerts: AlertsResponse = { total: 6, items: [
  { id: 'ALT-8921', severity: 'critical', entity: 'Neelam Trading Co.', transactionId: 'TXN-7A91E', reason: 'High-value transfer exhibits rapid pass-through behavior.', timestamp: '2 min ago', status: 'new' },
  { id: 'ALT-8919', severity: 'high', entity: 'Vikram Foundation', transactionId: 'TXN-6N09A', reason: 'Linked to a sanctioned risk cluster through a shared beneficiary.', timestamp: '18 min ago', status: 'reviewing' },
  { id: 'ALT-8916', severity: 'high', entity: 'Rajesh Kumar', transactionId: 'TXN-4C28B', reason: 'Multiple structured transfers detected within a 24-hour period.', timestamp: '42 min ago', status: 'new' },
  { id: 'ALT-8905', severity: 'medium', entity: 'Kaveri Logistics', transactionId: 'TXN-8D56K', reason: 'Payment amount exceeds baseline operational behavior.', timestamp: '1 hr ago', status: 'reviewing' },
  { id: 'ALT-8897', severity: 'medium', entity: 'Nexus Digital Services', transactionId: 'TXN-1F73M', reason: 'Recipient account was established within 14 days.', timestamp: '3 hr ago', status: 'resolved' },
  { id: 'ALT-8889', severity: 'low', entity: 'GlobePay Wallet', transactionId: 'TXN-2Q85S', reason: 'Minor deviation from normal device location pattern.', timestamp: '5 hr ago', status: 'resolved' },
] };

export async function getAlerts(): Promise<AlertsResponse> { await new Promise((resolve) => setTimeout(resolve, 320)); if (import.meta.env.VITE_ENABLE_MOCK_DATA !== 'false') return mockAlerts; // BACKEND TODO: Request monitored alerts with status and severity filters.
  return apiClient.get<AlertsResponse>('/alerts'); }
