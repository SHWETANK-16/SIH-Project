import type { Transaction } from '../../types/common';

export interface TransactionFilters {
  query: string;
  risk: string;
  status: string;
  dateRange: string;
}

export interface TransactionResponse {
  items: Transaction[];
  total: number;
}
