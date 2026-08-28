import { Brain, Cpu, TrendingDown, TrendingUp, Sparkles } from 'lucide-react';

export interface ShapDriver {
  feature: string;
  label: string;
  value: number;
  contribution: number;
  direction: 'increases_risk' | 'decreases_risk';
  share: number;
}

export interface ModelInfo {
  name: string;
  version: string;
  implementation: string;
  probability: number;
  model_score: number;
  rules_score: number;
  model_weight?: number;
  decision_threshold?: number;
  top_drivers: ShapDriver[];
  guardrails_applied?: string[];
  shap_method?: string;
}

export interface ExplanationFactor {
  name: string;
  impact: 'low' | 'medium' | 'high';
  description: string;
}

export interface XGBoostProps {
  model?: ModelInfo;
  factors?: ExplanationFactor[];
  summary?: string;
  entityId?: string;
}

export const defaultModelData: ModelInfo = {
  name: 'XGBoost Mule Risk Classifier',
  version: '1.2.0',
  implementation: 'XGBOOST_HYBRID',
  probability: 0.8796,
  model_score: 91.8,
  rules_score: 79.0,
  model_weight: 0.70,
  decision_threshold: 0.49,
  top_drivers: [
    {
      feature: 'in_cycle',
      label: 'Circular settlement loop participation',
      value: 1.0,
      contribution: 1.308,
      direction: 'increases_risk',
      share: 0.417,
    },
    {
      feature: 'new_counterparty_ratio',
      label: 'New counterparty dispersion',
      value: 0.60,
      contribution: 0.625,
      direction: 'increases_risk',
      share: 0.199,
    },
    {
      feature: 'behaviour_deviation',
      label: 'Historical amount deviation',
      value: 0.70,
      contribution: -0.468,
      direction: 'decreases_risk',
      share: 0.149,
    },
    {
      feature: 'pass_through_ratio',
      label: 'Rapid pass-through velocity',
      value: 1.00,
      contribution: 0.362,
      direction: 'increases_risk',
      share: 0.115,
    },
    {
      feature: 'transaction_amount',
      label: 'Transaction volume exposure',
      value: 50000,
      contribution: 0.165,
      direction: 'increases_risk',
      share: 0.053,
    },
  ],
  shap_method: 'xgboost_native_treeshap',
};

export function XGBoostExplainabilityCard({
  model = defaultModelData,
  summary,
}: XGBoostProps) {
  const probPercent = (model.probability * 100).toFixed(1);

  return (
    <article className="content-card xgboost-explainability-card">
      <div className="card-heading" style={{ padding: '8px 4px 14px 4px', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div
            style={{
              display: 'grid',
              placeItems: 'center',
              width: '38px',
              height: '38px',
              background: '#122e20',
              border: '1px solid #245738',
              borderRadius: '9px',
              color: '#4cbf7e',
              flexShrink: 0,
            }}
          >
            <Cpu size={20} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <p className="eyebrow" style={{ margin: 0, letterSpacing: '0.06em', fontSize: '0.68rem', color: '#789c83' }}>
              Machine Learning Decision Attribution
            </p>
            <h2 style={{ fontSize: '1.08rem', margin: 0, fontWeight: 600, color: '#e8f3ea', lineHeight: 1.25 }}>
              XGBoost + Native TreeSHAP Engine
            </h2>
          </div>
        </div>
        <span className="status-pill status-high" style={{ fontSize: '0.68rem', padding: '5px 12px' }}>
          <Sparkles size={13} style={{ marginRight: '5px' }} />
          {model.implementation || 'XGBOOST_HYBRID'}
        </span>
      </div>

      {/* Probability and Hybrid Split Bar */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
          gap: '10px',
          background: '#0a1711',
          border: '1px solid #1a3824',
          borderRadius: '8px',
          padding: '12px',
          margin: '14px 0',
        }}
      >
        <div>
          <small style={{ color: '#7a9682', fontSize: '0.65rem', display: 'block' }}>Mule Probability</small>
          <strong style={{ fontSize: '1.25rem', color: model.probability >= 0.5 ? '#eb8c91' : '#4cbf7e' }}>
            {probPercent}%
          </strong>
          <small style={{ color: '#78937e', fontSize: '0.62rem', display: 'block' }}>
            Threshold: θ = {model.decision_threshold ?? 0.49}
          </small>
        </div>

        <div>
          <small style={{ color: '#7a9682', fontSize: '0.65rem', display: 'block' }}>Pure ML Score</small>
          <strong style={{ fontSize: '1.1rem', color: '#c4d8c8' }}>
            {model.model_score.toFixed(1)} <small style={{ fontSize: '0.68rem', color: '#78937e' }}>/ 100</small>
          </strong>
          <small style={{ color: '#78937e', fontSize: '0.62rem', display: 'block' }}>Weight: 70%</small>
        </div>

        <div>
          <small style={{ color: '#7a9682', fontSize: '0.65rem', display: 'block' }}>Rule Engine Score</small>
          <strong style={{ fontSize: '1.1rem', color: '#c4d8c8' }}>
            {model.rules_score.toFixed(1)} <small style={{ fontSize: '0.68rem', color: '#78937e' }}>/ 100</small>
          </strong>
          <small style={{ color: '#78937e', fontSize: '0.62rem', display: 'block' }}>Weight: 30%</small>
        </div>

        <div>
          <small style={{ color: '#7a9682', fontSize: '0.65rem', display: 'block' }}>SHAP Attribution</small>
          <strong style={{ fontSize: '0.85rem', color: '#4cbf7e', display: 'flex', alignItems: 'center', gap: '4px', marginTop: '4px' }}>
            <Brain size={14} /> TreeSHAP
          </strong>
          <small style={{ color: '#78937e', fontSize: '0.62rem', display: 'block' }}>12 Graph Features</small>
        </div>
      </div>

      {/* TreeSHAP Feature Drivers Waterfall */}
      <div style={{ marginTop: '18px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 2px 10px 2px' }}>
          <h3 style={{ fontSize: '0.8rem', color: '#c4d8c8', margin: 0, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Top TreeSHAP Feature Drivers
          </h3>
          <span style={{ fontSize: '0.66rem', color: '#7a9682' }}>Marginal Log-Odds Contribution (ϕ)</span>
        </div>

        <div style={{ display: 'grid', gap: '8px' }}>
          {model.top_drivers.map((driver) => {
            const isIncrease = driver.direction === 'increases_risk';
            const sharePercent = Math.round(driver.share * 100);
            const barColor = isIncrease ? '#d55358' : '#4cbf7e';

            return (
              <div
                key={driver.feature}
                style={{
                  background: '#0c1a13',
                  border: '1px solid #162f1e',
                  borderRadius: '6px',
                  padding: '8px 10px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', marginBottom: '4px' }}>
                  <span style={{ color: '#d5e4d8', display: 'flex', alignItems: 'center', gap: '5px' }}>
                    {isIncrease ? (
                      <TrendingUp size={13} style={{ color: '#eb8c91' }} />
                    ) : (
                      <TrendingDown size={13} style={{ color: '#4cbf7e' }} />
                    )}
                    <b>{driver.label}</b>
                  </span>
                  <span style={{ color: isIncrease ? '#eb8c91' : '#4cbf7e', fontWeight: 600 }}>
                    {driver.contribution > 0 ? `+${driver.contribution.toFixed(2)}` : driver.contribution.toFixed(2)} ϕ
                    <span style={{ color: '#7a9682', marginLeft: '6px', fontWeight: 'normal' }}>({sharePercent}%)</span>
                  </span>
                </div>

                {/* Relative Share Bar */}
                <div
                  style={{
                    height: '4px',
                    background: '#152c1d',
                    borderRadius: '2px',
                    overflow: 'hidden',
                    width: '100%',
                  }}
                >
                  <div
                    style={{
                      height: '100%',
                      width: `${Math.min(100, Math.max(5, sharePercent))}%`,
                      background: barColor,
                      borderRadius: '2px',
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Summary / Reasoning */}
      {summary && (
        <div
          style={{
            marginTop: '14px',
            background: '#112217',
            borderLeft: '3px solid #4cbf7e',
            borderRadius: '4px',
            padding: '8px 12px',
            fontSize: '0.7rem',
            color: '#98b29f',
            lineHeight: 1.45,
          }}
        >
          <b style={{ color: '#c4d8c8' }}>AI Executive Finding: </b>
          {summary}
        </div>
      )}
    </article>
  );
}

