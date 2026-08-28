import type { InvestigationWorkspace } from '../types';

export function InvestigationTimeline({ items }: { items: InvestigationWorkspace['timeline'] }) {
  return <article className="content-card timeline-card"><div className="card-heading"><div><p className="eyebrow">Case chronology</p><h2>Investigation timeline</h2></div><button className="text-button">View full timeline</button></div><div className="timeline-list">{items.map((item) => <div className={`timeline-item timeline-${item.type}`} key={`${item.time}-${item.title}`}><span className="timeline-marker" /><div><strong>{item.title}</strong><p>{item.detail}</p></div><time>{item.time}</time></div>)}</div></article>;
}
