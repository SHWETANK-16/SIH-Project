import { AlertTriangle, BadgeIndianRupee, CircleDollarSign, FolderSearch, Landmark } from 'lucide-react';
import { useDashboardStats } from '../hooks';
import { DashboardCharts } from '../components/DashboardCharts';
import { MetricCard } from '../components/MetricCard';
import { ErrorState, LoadingState } from '../../../shared/components/States';

export function DashboardPage() {
  const { data, isLoading, isError, refetch } = useDashboardStats();
  if (isLoading) return <LoadingState />;
  if (isError || !data) return <ErrorState onRetry={() => void refetch()} />;
  const { stats } = data;
  return <div className="page-container"><div className="page-heading"><div><p className="eyebrow">Command center</p><h1>Investigation Dashboard</h1><p>Real-time overview of financial activity and suspicious behavior.</p></div><div className="live-indicator"><i /> Live intelligence feed</div></div><section className="metric-grid"><MetricCard label="Total transactions" value={stats.totalTransactions} delta="8.2%" icon={<CircleDollarSign />} /><MetricCard label="Suspicious transactions" value={stats.suspiciousTransactions} delta="12.5%" icon={<AlertTriangle />} tone="amber" /><MetricCard label="Active investigations" value={stats.activeInvestigations} delta="6.0%" icon={<FolderSearch />} /><MetricCard label="High risk entities" value={stats.highRiskEntities} delta="2.3%" icon={<Landmark />} tone="red" /><MetricCard label="Amount under investigation" value={Math.round(stats.amountUnderInvestigation / 100000)} prefix="₹" suffix=" L" delta="18.4%" icon={<BadgeIndianRupee />} /></section><DashboardCharts data={data} /></div>;
}
