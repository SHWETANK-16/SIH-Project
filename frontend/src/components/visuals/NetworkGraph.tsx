import { useEffect, useMemo, useRef, useState } from 'react';
import { ExternalLink, Focus, ScanSearch, Waypoints, ZoomIn, ZoomOut } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { MoneyFlow, Network, NetworkEdge, NetworkNode } from '../../types';
import { money, RiskBadge } from '../ui';

interface NodePos {
  x: number;
  y: number;
}

export interface NetworkGraphProps {
  network: Network;
  traceOverlay?: MoneyFlow | null;
  maxRenderNodes?: number;
}

// Deterministic, perfectly balanced static coordinates
const DEFAULT_PRESETS: [number, number][] = [
  [18, 50], // Origin (Node 0)
  [36, 26], // Node 1
  [36, 74], // Node 2
  [52, 44], // Node 3
  [54, 78], // Node 4
  [68, 22], // Node 5
  [70, 58], // Node 6
  [85, 38], // Node 7
  [85, 76], // Node 8
  [52, 16], // Node 9
  [22, 22], // Node 10
  [22, 78], // Node 11
  [68, 88], // Node 12
  [88, 16], // Node 13
  [38, 50], // Node 14
];

function computeStaticPositions(nodes: NetworkNode[]): Map<string, NodePos> {
  const map = new Map<string, NodePos>();
  const count = nodes.length;

  nodes.forEach((n, i) => {
    if (i < DEFAULT_PRESETS.length) {
      map.set(n.id, { x: DEFAULT_PRESETS[i][0], y: DEFAULT_PRESETS[i][1] });
    } else {
      const angle = (i / Math.max(1, count)) * 2 * Math.PI;
      map.set(n.id, {
        x: Math.max(8, Math.min(92, 50 + Math.cos(angle) * 35)),
        y: Math.max(8, Math.min(92, 50 + Math.sin(angle) * 35)),
      });
    }
  });

  return map;
}

export function NetworkGraph({
  network,
  traceOverlay = null,
  maxRenderNodes = 50,
}: NetworkGraphProps) {
  const [selected, setSelected] = useState<NetworkNode | null>(network.nodes[0] || null);
  const [scale, setScale] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });

  const containerRef = useRef<HTMLDivElement>(null);
  const draggingNodeRef = useRef<string | null>(null);

  // 1. Filter visible nodes
  const visibleNodes = useMemo(() => {
    if (network.nodes.length <= maxRenderNodes) return network.nodes;
    return [...network.nodes]
      .sort((a, b) => (b.type === 'origin' ? 1 : 0) - (a.type === 'origin' ? 1 : 0) || b.risk_score - a.risk_score)
      .slice(0, maxRenderNodes);
  }, [network.nodes, maxRenderNodes]);

  const visibleNodeIds = useMemo(() => new Set(visibleNodes.map((n) => n.id)), [visibleNodes]);
  const nodeLookup = useMemo(() => new Map(visibleNodes.map((n) => [n.id, n])), [visibleNodes]);

  const visibleEdges = useMemo(() => {
    return network.edges.filter((e) => visibleNodeIds.has(e.source) && visibleNodeIds.has(e.target));
  }, [network.edges, visibleNodeIds]);

  // 2. Static positions state
  const [positions, setPositions] = useState<Map<string, NodePos>>(() =>
    computeStaticPositions(visibleNodes)
  );

  useEffect(() => {
    setPositions(computeStaticPositions(visibleNodes));
  }, [visibleNodes]);

  // 3. Multi-edge grouping
  const edgeGroups = useMemo(() => {
    const groups = new Map<string, NetworkEdge[]>();
    for (const edge of visibleEdges) {
      const pairKey = [edge.source, edge.target].sort().join(':::');
      if (!groups.has(pairKey)) groups.set(pairKey, []);
      groups.get(pairKey)!.push(edge);
    }
    return groups;
  }, [visibleEdges]);

  // 4. Trace overlay map
  const traceNodeHopMap = useMemo(() => {
    if (!traceOverlay) return new Map<string, number>();
    const map = new Map<string, number>();
    for (const hop of traceOverlay.hops) {
      if (!map.has(hop.source)) map.set(hop.source, hop.hop_number);
      if (!map.has(hop.destination)) map.set(hop.destination, hop.hop_number + 1);
    }
    return map;
  }, [traceOverlay]);

  const traceEdgeSet = useMemo(() => {
    if (!traceOverlay) return new Set<string>();
    return new Set(traceOverlay.hops.map((h) => h.transaction_id));
  }, [traceOverlay]);

  // 5. Drag & Drop Handlers
  const handleNodeMouseDown = (e: React.MouseEvent, nodeId: string) => {
    e.stopPropagation();
    draggingNodeRef.current = nodeId;
  };

  const handleStageMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (draggingNodeRef.current) {
      const rect = e.currentTarget.getBoundingClientRect();
      const clientX = Math.max(6, Math.min(94, ((e.clientX - rect.left) / rect.width) * 100));
      const clientY = Math.max(6, Math.min(94, ((e.clientY - rect.top) / rect.height) * 100));

      setPositions((prev) => {
        const next = new Map(prev);
        next.set(draggingNodeRef.current!, { x: clientX, y: clientY });
        return next;
      });
    } else if (isPanning) {
      setPan({
        x: e.clientX - panStart.x,
        y: e.clientY - panStart.y,
      });
    }
  };

  const handleStageMouseUp = () => {
    draggingNodeRef.current = null;
    setIsPanning(false);
  };

  const handleStageMouseDown = (e: React.MouseEvent) => {
    setIsPanning(true);
    setPanStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const resetView = () => {
    setScale(1);
    setPan({ x: 0, y: 0 });
    setPositions(computeStaticPositions(visibleNodes));
  };

  return (
    <div className="network-workspace" ref={containerRef}>
      {/* Top Toolbar */}
      <div className="graph-toolbar">
        <span>
          <ScanSearch size={14} /> {network.network_id} · {visibleNodes.length} of {network.node_count} entities
          {network.node_count > maxRenderNodes && <small className="trunc-pill">Capped at {maxRenderNodes}</small>}
        </span>
        <div className="graph-controls">
          <button onClick={() => setScale((s) => Math.max(0.65, s - 0.15))} aria-label="Zoom out" title="Zoom Out">
            <ZoomOut />
          </button>
          <button onClick={resetView} aria-label="Reset view" title="Reset Layout & Positions">
            <Focus />
          </button>
          <button onClick={() => setScale((s) => Math.min(2.0, s + 0.15))} aria-label="Zoom in" title="Zoom In">
            <ZoomIn />
          </button>
        </div>
      </div>

      {/* SVG Canvas Stage */}
      <div
        className={`graph-stage ${isPanning ? 'grabbing' : ''}`}
        onMouseDown={handleStageMouseDown}
        onMouseMove={handleStageMouseMove}
        onMouseUp={handleStageMouseUp}
        onMouseLeave={handleStageMouseUp}
      >
        <svg
          viewBox="0 0 100 100"
          role="img"
          aria-label={`Network graph for ${network.name}`}
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${scale})`,
            cursor: draggingNodeRef.current ? 'grabbing' : isPanning ? 'grabbing' : 'grab',
          }}
        >
          {/* High-visibility, compact directional arrowheads */}
          <defs>
            <marker
              id="arrow-std"
              viewBox="0 0 6 6"
              refX="5"
              refY="3"
              markerWidth="2.8"
              markerHeight="2.8"
              orient="auto"
            >
              <path d="M 0 1.2 L 5 3 L 0 4.8 z" fill="#4bd8a0" />
            </marker>
            <marker
              id="arrow-critical"
              viewBox="0 0 6 6"
              refX="5"
              refY="3"
              markerWidth="3.2"
              markerHeight="3.2"
              orient="auto"
            >
              <path d="M 0 1.2 L 5 3 L 0 4.8 z" fill="#fb5f68" />
            </marker>
            <marker
              id="arrow-traced"
              viewBox="0 0 6 6"
              refX="5"
              refY="3"
              markerWidth="3.4"
              markerHeight="3.4"
              orient="auto"
            >
              <path d="M 0 1.2 L 5 3 L 0 4.8 z" fill="#38ef7d" />
            </marker>
          </defs>

          {/* Render Directed Edges with Shortened Endpoints so Arrowheads are 100% Visible */}
          {Array.from(edgeGroups.entries()).map(([pairKey, edges]) => {
            return edges.map((e, edgeIdx) => {
              const src = positions.get(e.source);
              const dst = positions.get(e.target);
              if (!src || !dst) return null;

              const srcNode = nodeLookup.get(e.source);
              const dstNode = nodeLookup.get(e.target);
              const srcRadius = srcNode?.type === 'origin' ? 4.6 : 3.6;
              const dstRadius = dstNode?.type === 'origin' ? 4.6 : 3.6;

              const isSelected = selected && (selected.id === e.source || selected.id === e.target);
              const isTraced = traceEdgeSet.has(e.transaction_id);
              const isCritical = e.risk_level === 'CRITICAL';

              // Curve offset for parallel edges
              const totalInGroup = edges.length;
              const curveOffset = (edgeIdx - (totalInGroup - 1) / 2) * 4.5;
              const midX = (src.x + dst.x) / 2;
              const midY = (src.y + dst.y) / 2;

              const dx = dst.x - src.x;
              const dy = dst.y - src.y;
              const len = Math.sqrt(dx * dx + dy * dy) || 1;
              const nx = -dy / len;
              const ny = dx / len;

              const cx = midX + nx * curveOffset;
              const cy = midY + ny * curveOffset;

              // Compute shortened target endpoint so arrow tip lands outside target circle
              let startX = src.x;
              let startY = src.y;
              let endX = dst.x;
              let endY = dst.y;

              if (totalInGroup > 1) {
                // Tangent at source (from start to control point)
                const sDx = cx - src.x;
                const sDy = cy - src.y;
                const sDist = Math.sqrt(sDx * sDx + sDy * sDy) || 1;
                startX = src.x + (sDx / sDist) * srcRadius;
                startY = src.y + (sDy / sDist) * srcRadius;

                // Tangent at target (from control point to end)
                const tDx = dst.x - cx;
                const tDy = dst.y - cy;
                const tDist = Math.sqrt(tDx * tDx + tDy * tDy) || 1;
                endX = dst.x - (tDx / tDist) * (dstRadius + 0.8);
                endY = dst.y - (tDy / tDist) * (dstRadius + 0.8);
              } else {
                const ux = dx / len;
                const uy = dy / len;
                startX = src.x + ux * srcRadius;
                startY = src.y + uy * srcRadius;
                endX = dst.x - ux * (dstRadius + 0.8);
                endY = dst.y - uy * (dstRadius + 0.8);
              }

              const pathD = totalInGroup > 1
                ? `M ${startX} ${startY} Q ${cx} ${cy} ${endX} ${endY}`
                : `M ${startX} ${startY} L ${endX} ${endY}`;

              const markerId = isTraced ? 'url(#arrow-traced)' : isCritical ? 'url(#arrow-critical)' : 'url(#arrow-std)';

              return (
                <g key={`${pairKey}-${e.transaction_id}-${edgeIdx}`} className="edge-group">
                  <path
                    d={pathD}
                    className={`edge ${isCritical ? 'critical-edge' : ''} ${isSelected ? 'selected-edge' : ''} ${isTraced ? 'traced-edge' : ''}`}
                    markerEnd={markerId}
                  />
                  {isSelected && (
                    <text x={cx} y={cy - 1.2} className="edge-label">
                      {money(e.amount)}
                    </text>
                  )}
                </g>
              );
            });
          })}

          {/* Render Nodes */}
          {visibleNodes.map((n) => {
            const pos = positions.get(n.id);
            if (!pos) return null;

            const isSelected = selected?.id === n.id;
            const hopNumber = traceNodeHopMap.get(n.id);
            const isTraced = hopNumber !== undefined;
            const isOrigin = n.type === 'origin';
            const radius = isOrigin ? 4.6 : 3.6;

            return (
              <g
                key={n.id}
                className={`node ${isSelected ? 'selected' : ''} ${isTraced ? 'traced-node' : ''} ${isOrigin ? 'origin-node' : ''}`}
                transform={`translate(${pos.x}, ${pos.y})`}
                onClick={() => setSelected(n)}
                onMouseDown={(e) => handleNodeMouseDown(e, n.id)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && setSelected(n)}
              >
                {/* Outer Glow Halo */}
                {(n.risk_level === 'CRITICAL' || isOrigin || isTraced) && (
                  <circle
                    className={`node-pulse ${isTraced ? 'pulse-traced' : n.risk_level === 'CRITICAL' ? 'pulse-critical' : 'pulse-origin'}`}
                    r={radius * 1.35}
                  />
                )}

                {/* Main Node Circle */}
                <circle
                  className={`node-core risk-${n.risk_level.toLowerCase()}`}
                  r={radius}
                />

                {/* Node Label */}
                <text y={radius + 2.8} className="node-text">
                  {n.id.replace('ACC-', 'A')}
                </text>

                {/* Trace Sequence Badge */}
                {isTraced && (
                  <g transform={`translate(${radius * 0.75}, -${radius * 0.75})`}>
                    <circle r={2.0} className="trace-badge-bg" />
                    <text className="trace-badge-text" y={0.7}>#{hopNumber}</text>
                  </g>
                )}
              </g>
            );
          })}
        </svg>

        {/* Legend */}
        <div className="graph-legend">
          <span><i className="critical-dot" />Critical</span>
          <span><i className="high-dot" />High risk</span>
          <span><i className="origin-dot" />Origin</span>
          {traceOverlay && <span><i className="traced-dot" />Traced flow</span>}
        </div>
      </div>

      {/* Selected Entity Inspector Panel */}
      {selected && (
        <aside className="node-panel">
          <header>
            <div>
              <small>SELECTED ENTITY</small>
              <h3>{selected.id}</h3>
            </div>
            <RiskBadge level={selected.risk_level} />
          </header>

          <div className="risk-score">
            <span>Risk score</span>
            <strong>
              {selected.risk_score.toFixed(0)}
              <small>/100</small>
            </strong>
            <div>
              <i style={{ width: `${selected.risk_score}%` }} />
            </div>
          </div>

          <dl>
            <div>
              <dt>Transactions</dt>
              <dd>{selected.transaction_count}</dd>
            </div>
            <div>
              <dt>Network degree</dt>
              <dd>{selected.network_degree}</dd>
            </div>
            <div>
              <dt>Incoming</dt>
              <dd>{money(selected.incoming)}</dd>
            </div>
            <div>
              <dt>Outgoing</dt>
              <dd>{money(selected.outgoing)}</dd>
            </div>
            <div>
              <dt>Fan-in / Fan-out</dt>
              <dd>{selected.fan_in} / {selected.fan_out}</dd>
            </div>
            <div>
              <dt>Behaviour dev</dt>
              <dd>{selected.behaviour_deviation}×</dd>
            </div>
          </dl>

          <div className="indicators">
            {selected.indicators.map((ind) => (
              <span key={ind}>{ind}</span>
            ))}
          </div>

          <div className="node-actions">
            <Link to={`/accounts/${selected.id}`}>
              View account <ExternalLink size={12} />
            </Link>
            <Link className="primary" to={`/tracing?entity=${selected.id}`}>
              <Waypoints size={12} /> Trace money
            </Link>
          </div>
        </aside>
      )}
    </div>
  );
}
