import { ArrowLeft, BadgeInfo, CircleAlert, FilePlus2, MoreHorizontal, Network, ShieldAlert, UserRound } from 'lucide-react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { ErrorState, LoadingState } from '../../../shared/components/States';
import { StatusPill } from '../../../shared/components/StatusPill';
import { InvestigationGraph } from '../components/InvestigationGraph';
import { InvestigationTimeline } from '../components/InvestigationTimeline';
import { useInvestigation } from '../hooks';
import { XGBoostExplainabilityCard } from '../../../shared/components/XGBoostExplainabilityCard';

const SYNDICATE_NETWORKS = [
  { id: 'NET-001', label: 'NET-001 (Cascade Relay)' },
  { id: 'NET-002', label: 'NET-002 (Fan-Out Smurf)' },
  { id: 'NET-003', label: 'NET-003 (Dormant Reactivation)' },
  { id: 'NET-004', label: 'NET-004 (Circular Settlement)' },
];

const FLAGGED_TRANSACTIONS = [
  { id: 'TXN-7A91E', label: 'TXN-7A91E (₹24.5 L Layering)' },
  { id: 'TXN-4C28B', label: 'TXN-4C28B (₹6.85 L Smurfing)' },
  { id: 'TXN-1F73M', label: 'TXN-1F73M (₹1.25 L Mule Match)' },
  { id: 'TXN-6N09A', label: 'TXN-6N09A (₹36.8 L Charity Diversion)' },
  { id: 'TXN-8D56K', label: 'TXN-8D56K (₹18.7 L Vendor Payment)' },
  { id: 'TXN-0001', label: 'TXN-0001 (5-Hop BFS Trace)' },
];

export function InvestigationPage() {
  const { id = 'NET-001' } = useParams();
  const { data, isLoading, isError, refetch } = useInvestigation(id);
  const [selectedNode, setSelectedNode] = useState('ACC-0001');
  const navigate = useNavigate();

  useEffect(() => {
    if (data?.nodes && data.nodes.length > 0) {
      setSelectedNode(data.nodes[0].id);
    }
  }, [id, data]);

  if (isLoading) return <LoadingState label="Assembling NetworkX investigation intelligence..." />;
  if (isError || !data) return <ErrorState message="Unable to load this investigation." onRetry={() => void refetch()} />;

  const selected = data.nodes.find((node) => node.id === selectedNode) ?? data.nodes[0];

  return (
    <div className="page-container investigation-page">
      <Link to="/transactions" className="back-link in-app">
        <ArrowLeft size={16} /> Transaction Explorer
      </Link>
      <div className="case-header">
        <div style={{ flex: 1, minWidth: 0, maxWidth: '100%' }}>
          <p className="eyebrow">Investigation workspace · {data.investigation.id}</p>
          <h1>{data.investigation.title}</h1>
          <p style={{ maxWidth: '820px' }}>{data.investigation.summary}</p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '14px', width: '100%' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap', width: '100%' }}>
              <span style={{ fontSize: '0.66rem', color: '#789c83', fontWeight: 600, flexShrink: 0, minWidth: '68px', textTransform: 'uppercase' }}>
                Syndicates:
              </span>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
                {SYNDICATE_NETWORKS.map((net) => {
                  const isCurrent = id === net.id;
                  return (
                    <button
                      key={net.id}
                      className={`button ${isCurrent ? 'button-primary' : 'button-secondary'}`}
                      style={{ fontSize: '0.7rem', padding: '4px 9px', borderRadius: '6px', whiteSpace: 'nowrap' }}
                      onClick={() => navigate(`/investigations/${net.id}`)}
                    >
                      <Network size={12} style={{ marginRight: '4px' }} />
                      {net.label}
                    </button>
                  );
                })}
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap', width: '100%' }}>
              <span style={{ fontSize: '0.66rem', color: '#789c83', fontWeight: 600, flexShrink: 0, minWidth: '68px', textTransform: 'uppercase' }}>
                Transactions:
              </span>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
                {FLAGGED_TRANSACTIONS.map((txn) => {
                  const isCurrent = id === txn.id;
                  return (
                    <button
                      key={txn.id}
                      className={`button ${isCurrent ? 'button-primary' : 'button-secondary'}`}
                      style={{ fontSize: '0.7rem', padding: '4px 9px', borderRadius: '6px', whiteSpace: 'nowrap' }}
                      onClick={() => navigate(`/investigations/${txn.id}`)}
                    >
                      <UserRound size={12} style={{ marginRight: '4px' }} />
                      {txn.label}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
        <div className="case-header-actions">
          <StatusPill status={data.investigation.status} />
          <button className="button button-secondary" onClick={() => void refetch()}>
            <FilePlus2 size={16} /> Refresh Graph
          </button>
          <button className="icon-button" aria-label="More investigation actions">
            <MoreHorizontal size={19} />
          </button>
        </div>
      </div>
      <div className="case-meta">
        <span>
          <ShieldAlert size={15} /> Risk score <b className="critical-text">{data.investigation.risk.score}/100</b>
        </span>
        <span>
          <UserRound size={15} /> {data.investigation.investigator}
        </span>
        <span>
          <BadgeInfo size={15} /> {data.investigation.updatedAt}
        </span>
      </div>
      <div className="investigation-grid">
        <InvestigationGraph nodes={data.nodes} edges={data.edges} selectedNode={selected.id} onSelect={setSelectedNode} />
        <aside className="investigation-side">
          <article className="content-card selected-entity">
            <div className="card-heading">
              <div>
                <p className="eyebrow">Selected network object</p>
                <h2>{selected.label}</h2>
              </div>
              <span className={`risk-score risk-${selected.risk}`}>
                <i /> {selected.risk}
              </span>
            </div>
            <span className="selected-node-icon">
              <Network size={22} />
            </span>
            <dl>
              <div>
                <dt>Object type</dt>
                <dd>{selected.type}</dd>
              </div>
              <div>
                <dt>Risk score</dt>
                <dd>{selected.riskScore ?? (selected.risk === 'critical' ? 92 : selected.risk === 'high' ? 78 : 41)} / 100</dd>
              </div>
              <div>
                <dt>Linked flow</dt>
                <dd>{selected.value ?? 'Direct connection'}</dd>
              </div>
              <div>
                <dt>Network links</dt>
                <dd>{data.edges.filter((edge) => edge.source === selected.id || edge.target === selected.id).length} direct connections</dd>
              </div>
            </dl>
            <button className="button button-secondary full-width" onClick={() => navigate(`/entities/${selected.id}`)}>
              View entity profile ({selected.id})
            </button>
          </article>
          <article className="content-card side-alert">
            <CircleAlert size={18} />
            <div>
              <b>Pattern alert</b>
              <p>Topological cycle & high-velocity pass-through identified by NetworkX engine.</p>
            </div>
          </article>
        </aside>
      </div>

      {/* XGBoost Machine Learning Decision Attribution & TreeSHAP Drivers */}
      <XGBoostExplainabilityCard
        summary={`Syndicate network ${id} flagged with multi-hop pass-through and circular routing. The trained XGBoost hybrid engine evaluates 12 graph topology and velocity features with TreeSHAP marginal attributions.`}
        entityId={selected.id}
      />

      <InvestigationTimeline items={data.timeline} />
    </div>
  );
}
