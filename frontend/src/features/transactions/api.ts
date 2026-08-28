import { apiClient } from '../../services/api/client';
import type { Transaction } from '../../types/common';
import type { TransactionResponse } from './types';

export const KNOWN_TRANSACTIONS: Transaction[] = [
  { id: 'TXN-7A91E', sender: 'Orion Exports Pvt Ltd', receiver: 'Neelam Trading Co.', amount: 2_450_000, date: '2026-08-27T09:41:00', status: 'flagged', risk: { score: 92, level: 'critical', indicators: ['Rapid pass-through transfer', 'New beneficiary', 'Unusual counterparty geography'] }, senderBank: 'National Union Bank', receiverBank: 'Apex Commercial Bank', category: 'Cross-border trade' },
  { id: 'TXN-4C28B', sender: 'Rajesh Kumar', receiver: 'Blue Orbit Retail', amount: 685_000, date: '2026-08-27T09:24:00', status: 'pending', risk: { score: 74, level: 'high', indicators: ['Structuring pattern', 'High velocity'] }, senderBank: 'National Union Bank', receiverBank: 'Meridian Bank', category: 'Merchant transfer' },
  { id: 'TXN-8D56K', sender: 'Kaveri Logistics', receiver: 'M/s Aranya Metals', amount: 1_872_000, date: '2026-08-27T08:56:00', status: 'completed', risk: { score: 47, level: 'medium', indicators: ['Amount outside usual range'] }, senderBank: 'State Trust Bank', receiverBank: 'Apex Commercial Bank', category: 'Vendor payment' },
  { id: 'TXN-1F73M', sender: 'Aditi Shah', receiver: 'Nexus Digital Services', amount: 125_000, date: '2026-08-27T08:35:00', status: 'blocked', risk: { score: 96, level: 'critical', indicators: ['Watchlist match', 'Known mule account'] }, senderBank: 'Meridian Bank', receiverBank: 'Apex Commercial Bank', category: 'Online payment' },
  { id: 'TXN-3P44L', sender: 'Vajra Construction', receiver: 'Riya Enterprises', amount: 920_000, date: '2026-08-26T18:08:00', status: 'completed', risk: { score: 35, level: 'low', indicators: ['Normal operational pattern'] }, senderBank: 'People’s Bank', receiverBank: 'National Union Bank', category: 'Business transfer' },
  { id: 'TXN-6N09A', sender: 'Vikram Foundation', receiver: 'Sparrow Advisory', amount: 3_680_000, date: '2026-08-26T16:50:00', status: 'flagged', risk: { score: 81, level: 'high', indicators: ['Charity fund diversion', 'Linked high-risk entity'] }, senderBank: 'State Trust Bank', receiverBank: 'Meridian Bank', category: 'Institutional transfer' },
  { id: 'TXN-5R22J', sender: 'Nexora Traders', receiver: 'Amaya Textile Works', amount: 448_000, date: '2026-08-26T15:16:00', status: 'pending', risk: { score: 58, level: 'medium', indicators: ['Recipient account recently opened'] }, senderBank: 'Apex Commercial Bank', receiverBank: 'People’s Bank', category: 'Trade payment' },
  { id: 'TXN-2Q85S', sender: 'Ashwin Verma', receiver: 'GlobePay Wallet', amount: 78_600, date: '2026-08-26T13:30:00', status: 'completed', risk: { score: 22, level: 'low', indicators: ['Standard account behavior'] }, senderBank: 'Meridian Bank', receiverBank: 'GlobePay', category: 'Wallet load' },
];

export async function getTransactions(): Promise<TransactionResponse> {
  await new Promise((resolve) => setTimeout(resolve, 400));
  if (import.meta.env.VITE_ENABLE_MOCK_DATA !== 'false') return { items: KNOWN_TRANSACTIONS, total: KNOWN_TRANSACTIONS.length };
  // BACKEND TODO: Send server-side filters, sort, and pagination parameters to the KNOWN_TRANSACTIONS API.
  return apiClient.get<TransactionResponse>('/transactions');
}

export async function getTransaction(id: string): Promise<Transaction> {
  await new Promise((resolve) => setTimeout(resolve, 320));
  if (import.meta.env.VITE_ENABLE_MOCK_DATA !== 'false') return KNOWN_TRANSACTIONS.find((item) => item.id === id) ?? KNOWN_TRANSACTIONS[0];
  // BACKEND TODO: Replace local transaction fallback with API record lookup.
  return apiClient.get<Transaction>(`/transactions/${id}`);
}
