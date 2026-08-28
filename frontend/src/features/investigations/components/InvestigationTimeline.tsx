import { useState } from 'react';
import {
  AlertTriangle,
  ArrowRight,
  ArrowRightLeft,
  Calendar,
  CheckCircle2,
  Clock,
  Filter,
  Milestone,
  ShieldAlert,
  Sparkles,
  Zap,
} from 'lucide-react';
import type { InvestigationWorkspace } from '../types';

export function InvestigationTimeline({
  items,
}: {
  items: InvestigationWorkspace['timeline'];
}) {
  const [filterType, setFilterType] = useState<'all' | 'alert' | 'transaction'>('all');

  const filteredItems = items.filter((item) => {
    if (filterType === 'all') return true;
    return item.type === filterType;
  });

  const alertCount = items.filter((i) => i.type === 'alert').length;
  const txnCount = items.filter((i) => i.type === 'transaction').length;

  return (
    <article className="content-card timeline-card" style={{ padding: '22px 24px' }}>
      {/* Header with Title and Status Badges */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          flexWrap: 'wrap',
          gap: '12px',
          borderBottom: '1px solid #162f1e',
          paddingBottom: '16px',
          marginBottom: '20px',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '3px' }}>
            <Milestone size={14} style={{ color: '#4cbf7e' }} />
            <p className="eyebrow" style={{ margin: 0, letterSpacing: '0.08em' }}>
              TEMPORAL AUDIT TRAIL
            </p>
          </div>
          <h2 style={{ fontSize: '1.2rem', margin: 0, color: '#e8f3ea', fontWeight: 600 }}>
            Case Chronology & Money Movement Sequence
          </h2>
          <p style={{ margin: '4px 0 0', fontSize: '0.72rem', color: '#7a9682' }}>
            Reconstructed forensic sequence of transfers, threshold alerts, and network detections.
          </p>
        </div>

        {/* Filter Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <button
            className={`button ${filterType === 'all' ? 'button-primary' : 'button-secondary'}`}
            style={{ fontSize: '0.68rem', padding: '5px 10px', height: '28px', borderRadius: '5px' }}
            onClick={() => setFilterType('all')}
          >
            All Events ({items.length})
          </button>
          <button
            className={`button ${filterType === 'alert' ? 'button-primary' : 'button-secondary'}`}
            style={{ fontSize: '0.68rem', padding: '5px 10px', height: '28px', borderRadius: '5px' }}
            onClick={() => setFilterType('alert')}
          >
            <ShieldAlert size={12} style={{ marginRight: '4px' }} />
            Alerts ({alertCount})
          </button>
          <button
            className={`button ${filterType === 'transaction' ? 'button-primary' : 'button-secondary'}`}
            style={{ fontSize: '0.68rem', padding: '5px 10px', height: '28px', borderRadius: '5px' }}
            onClick={() => setFilterType('transaction')}
          >
            <ArrowRightLeft size={12} style={{ marginRight: '4px' }} />
            Transfers ({txnCount})
          </button>
        </div>
      </div>

      {/* Modern Stepper Timeline List */}
      <div style={{ position: 'relative', paddingLeft: '10px' }}>
        {/* Continuous Gradient Spine */}
        <div
          style={{
            position: 'absolute',
            left: '26px',
            top: '20px',
            bottom: '20px',
            width: '2px',
            background: 'linear-gradient(to bottom, #4cbf7e 0%, #d4ae49 50%, #d55358 100%)',
            opacity: 0.45,
          }}
        />

        <div style={{ display: 'grid', gap: '16px' }}>
          {filteredItems.map((item, idx) => {
            const isAlert = item.type === 'alert';
            const badgeColor = isAlert ? '#eb8c91' : '#4cbf7e';
            const iconBg = isAlert ? '#261214' : '#0e2316';
            const iconBorder = isAlert ? '#5a2228' : '#1d492c';

            return (
              <div
                key={`${item.time}-${item.title}-${idx}`}
                style={{
                  display: 'grid',
                  gridTemplateColumns: '36px 1fr',
                  gap: '16px',
                  alignItems: 'flex-start',
                  position: 'relative',
                }}
              >
                {/* Node Icon Badge */}
                <div
                  style={{
                    width: '34px',
                    height: '34px',
                    borderRadius: '50%',
                    background: iconBg,
                    border: `2px solid ${iconBorder}`,
                    display: 'grid',
                    placeItems: 'center',
                    color: badgeColor,
                    zIndex: 2,
                    boxShadow: isAlert ? '0 0 10px rgba(213, 83, 88, 0.25)' : '0 0 8px rgba(76, 191, 126, 0.2)',
                  }}
                >
                  {isAlert ? <ShieldAlert size={16} /> : <ArrowRightLeft size={15} />}
                </div>

                {/* Event Card */}
                <div
                  style={{
                    background: '#09150e',
                    border: `1px solid ${isAlert ? '#2d1b1e' : '#173322'}`,
                    borderRadius: '8px',
                    padding: '12px 16px',
                    transition: 'border-color 0.2s, transform 0.2s',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      flexWrap: 'wrap',
                      gap: '8px',
                      marginBottom: '6px',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span
                        style={{
                          fontSize: '0.62rem',
                          fontWeight: 700,
                          color: '#76947e',
                          background: '#122519',
                          padding: '2px 7px',
                          borderRadius: '4px',
                          textTransform: 'uppercase',
                          letterSpacing: '0.05em',
                        }}
                      >
                        Step 0{idx + 1}
                      </span>
                      <strong style={{ fontSize: '0.85rem', color: '#e8f3ea' }}>{item.title}</strong>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px',
                          fontSize: '0.67rem',
                          color: '#8ba693',
                          background: '#101d14',
                          padding: '2px 8px',
                          borderRadius: '4px',
                          border: '1px solid #1a3221',
                        }}
                      >
                        <Clock size={11} /> {item.time}
                      </span>
                      <span
                        className={`status-pill ${isAlert ? 'status-critical' : 'status-low'}`}
                        style={{ fontSize: '0.62rem', padding: '2px 7px' }}
                      >
                        {isAlert ? 'Triggered Flag' : 'Transfer Hop'}
                      </span>
                    </div>
                  </div>

                  <p style={{ margin: 0, fontSize: '0.74rem', color: '#97b19e', lineHeight: 1.45 }}>
                    {item.detail}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </article>
  );
}
