import { Download, Filter, Plus } from 'lucide-react';
import { useMemo, useState } from 'react';
import { ErrorState, LoadingState } from '../../../shared/components/States';
import { TransactionFilters } from '../components/TransactionFilters';
import { TransactionTable } from '../components/TransactionTable';
import { useTransactions } from '../hooks';
import type { TransactionFilters as Filters } from '../types';

const defaultFilters: Filters = { query: '', risk: 'all', status: 'all', dateRange: 'Last 7 days' };

export function TransactionsPage() {
  const [filters, setFilters] = useState(defaultFilters);
  const { data, isLoading, isError, refetch } = useTransactions();
  const filtered = useMemo(() => data?.items.filter((item) => { const query = filters.query.toLowerCase(); return (!query || `${item.id} ${item.sender} ${item.receiver}`.toLowerCase().includes(query)) && (filters.risk === 'all' || item.risk.level === filters.risk) && (filters.status === 'all' || item.status === filters.status); }) ?? [], [data, filters]);
  if (isLoading) return <LoadingState label="Retrieving transaction intelligence..." />;
  if (isError || !data) return <ErrorState message="Unable to load transactions." onRetry={() => void refetch()} />;
  return <div className="page-container"><div className="page-heading"><div><p className="eyebrow">Financial activity</p><h1>Transaction Explorer</h1><p>Search, filter and investigate the movement of funds across connected networks.</p></div><div className="heading-actions"><button className="button button-secondary"><Download size={16} /> Export</button><button className="button button-primary"><Plus size={16} /> Add watchlist</button></div></div><section className="content-card transaction-explorer"><div className="table-toolbar"><div><h2>Transaction intelligence</h2><p>{data.total.toLocaleString()} records in the current investigation window</p></div><span className="table-status"><Filter size={15} /> {filtered.length} matched</span></div><TransactionFilters filters={filters} onChange={setFilters} /><TransactionTable transactions={filtered} /></section></div>;
}
