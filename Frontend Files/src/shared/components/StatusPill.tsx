import type { RiskLevel, TransactionStatus } from '../../types/common';

type Status = RiskLevel | TransactionStatus | 'open' | 'monitoring' | 'closed' | 'new' | 'reviewing' | 'resolved';

export function StatusPill({ status }: { status: Status }) {
  return <span className={`status-pill status-${status}`}>{status.replace('-', ' ')}</span>;
}
