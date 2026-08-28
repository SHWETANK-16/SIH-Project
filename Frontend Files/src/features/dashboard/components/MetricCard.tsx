import { useEffect, useState, type ReactNode } from 'react';

function useCountUp(target: number) { const [value, setValue] = useState(0); useEffect(() => { const start = performance.now(); const timer = window.setInterval(() => { const progress = Math.min((performance.now() - start) / 850, 1); setValue(Math.round(target * (1 - (1 - progress) ** 3))); if (progress === 1) window.clearInterval(timer); }, 16); return () => window.clearInterval(timer); }, [target]); return value; }

export function MetricCard({ label, value, suffix = '', prefix = '', delta, icon, tone = 'green' }: { label: string; value: number; suffix?: string; prefix?: string; delta: string; icon: ReactNode; tone?: 'green' | 'amber' | 'red'; }) {
  const displayed = useCountUp(value);
  return <article className={`metric-card metric-${tone}`}><div className="metric-top"><span>{label}</span><span className="metric-icon">{icon}</span></div><strong>{prefix}{displayed.toLocaleString('en-IN')}{suffix}</strong><small><b>↑ {delta}</b> vs. last 7 days</small></article>;
}
