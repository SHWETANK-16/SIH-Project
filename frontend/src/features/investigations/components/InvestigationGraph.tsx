import { Maximize2, Minus, MousePointer2, Plus, RotateCcw } from 'lucide-react';
import { useState, useEffect, type PointerEvent } from 'react';
import type { NetworkEdge, NetworkNode } from '../../../types/common';

const riskColor = { low: '#4cbf7e', medium: '#d4ae49', high: '#dd8143', critical: '#d55358' } as const;

interface Viewport {
  x: number;
  y: number;
  scale: number;
}

interface DraggedNodeState {
  id: string;
  startX: number;
  startY: number;
  nodeStartX: number;
  nodeStartY: number;
}

export function InvestigationGraph({
  nodes,
  edges,
  selectedNode,
  onSelect,
}: {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  selectedNode: string;
  onSelect: (id: string) => void;
}) {
  const [view, setView] = useState<Viewport>({ x: 0, y: 0, scale: 1 });
  const [dragCanvasStart, setDragCanvasStart] = useState<{ x: number; y: number; view: Viewport } | null>(null);
  const [draggedNode, setDraggedNode] = useState<DraggedNodeState | null>(null);

  // Dynamic position state for individual draggable nodes
  const [nodePositions, setNodePositions] = useState<Record<string, { x: number; y: number }>>({});

  // Sync positions when nodes prop changes or on new network load
  useEffect(() => {
    const initial: Record<string, { x: number; y: number }> = {};
    nodes.forEach((n) => {
      initial[n.id] = { x: n.x, y: n.y };
    });
    setNodePositions(initial);
  }, [nodes]);

  const getNodePos = (id: string): { x: number; y: number } | null => {
    if (nodePositions[id]) return nodePositions[id];
    const n = nodes.find((node) => node.id === id);
    return n ? { x: n.x, y: n.y } : null;
  };

  const zoom = (delta: number) =>
    setView((current) => ({ ...current, scale: Math.min(1.55, Math.max(0.62, current.scale + delta)) }));


  const onPointerDownCanvas = (event: PointerEvent<SVGSVGElement>) => {
    setDragCanvasStart({ x: event.clientX, y: event.clientY, view });
  };

  const onPointerMove = (event: PointerEvent<SVGSVGElement>) => {
    if (draggedNode) {
      // Zoom-compensated drag delta for the individual node
      const dx = (event.clientX - draggedNode.startX) / view.scale;
      const dy = (event.clientY - draggedNode.startY) / view.scale;
      const newX = Math.round(Math.max(30, Math.min(730, draggedNode.nodeStartX + dx)));
      const newY = Math.round(Math.max(30, Math.min(410, draggedNode.nodeStartY + dy)));

      setNodePositions((prev) => ({
        ...prev,
        [draggedNode.id]: { x: newX, y: newY },
      }));
    } else if (dragCanvasStart) {
      setView({
        ...dragCanvasStart.view,
        x: dragCanvasStart.view.x + event.clientX - dragCanvasStart.x,
        y: dragCanvasStart.view.y + event.clientY - dragCanvasStart.y,
      });
    }
  };

  const onPointerUp = () => {
    setDraggedNode(null);
    setDragCanvasStart(null);
  };

  const resetGraph = () => {
    setView({ x: 0, y: 0, scale: 1 });
    const initial: Record<string, { x: number; y: number }> = {};
    nodes.forEach((n) => {
      initial[n.id] = { x: n.x, y: n.y };
    });
    setNodePositions(initial);
  };

  return (
    <article className="content-card graph-card">
      <div className="card-heading">
        <div>
          <p className="eyebrow">Relationship mapping</p>
          <h2>Financial intelligence network</h2>
        </div>
        <span className="graph-hint">
          <MousePointer2 size={14} /> Drag nodes to reposition · Drag canvas to pan
        </span>
      </div>
      <div className="graph-canvas">
        <svg
          className="investigation-graph"
          viewBox="0 0 760 440"
          onPointerDown={onPointerDownCanvas}
          onPointerMove={onPointerMove}
          onPointerUp={onPointerUp}
          onPointerLeave={onPointerUp}
        >
          <defs>
            <marker id="arrow" markerWidth="8" markerHeight="8" refX="5" refY="3" orient="auto">
              <path d="M0,0 L0,6 L6,3 z" fill="#5b936b" />
            </marker>
            <filter id="nodeglow">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          <g transform={`translate(${view.x} ${view.y}) scale(${view.scale})`}>
            {edges.map((edge) => {
              const sourcePos = getNodePos(edge.source);
              const targetPos = getNodePos(edge.target);
              if (!sourcePos || !targetPos) return null;
              return (
                <line
                  key={edge.id}
                  x1={sourcePos.x}
                  y1={sourcePos.y}
                  x2={targetPos.x}
                  y2={targetPos.y}
                  className={`network-edge edge-${edge.risk}`}
                  markerEnd="url(#arrow)"
                />
              );
            })}
            {nodes.map((node) => {
              const pos = getNodePos(node.id) || { x: node.x, y: node.y };
              const active = selectedNode === node.id;
              const isFocal = node.id === 'main' || node.id === 'ACC-0001' || node.type === 'origin';
              const radius = isFocal ? 28 : node.type === 'bank' ? 16 : 21;
              const isBeingDragged = draggedNode?.id === node.id;

              return (
                <g
                  key={node.id}
                  className={`network-graph-node ${active ? 'selected' : ''}`}
                  style={{ cursor: isBeingDragged ? 'grabbing' : 'grab' }}
                  onPointerDown={(event) => {
                    event.stopPropagation();
                    setDraggedNode({
                      id: node.id,
                      startX: event.clientX,
                      startY: event.clientY,
                      nodeStartX: pos.x,
                      nodeStartY: pos.y,
                    });
                    onSelect(node.id);
                  }}
                  onClick={(event) => {
                    event.stopPropagation();
                    onSelect(node.id);
                  }}
                  role="button"
                  tabIndex={0}
                  aria-label={`Select and drag ${node.label}`}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter') onSelect(node.id);
                  }}
                >
                  <circle
                    cx={pos.x}
                    cy={pos.y}
                    r={radius + (active ? 6 : 0)}
                    fill={active ? `${riskColor[node.risk]}26` : 'transparent'}
                  />
                  <circle
                    cx={pos.x}
                    cy={pos.y}
                    r={radius}
                    fill="#10261a"
                    stroke={riskColor[node.risk]}
                    strokeWidth={isFocal ? 3 : 2}
                    filter={isFocal ? 'url(#nodeglow)' : undefined}
                  />
                  <circle cx={pos.x} cy={pos.y} r={isFocal ? 8 : 5} fill={riskColor[node.risk]} />
                  <text x={pos.x} y={pos.y + radius + 15} textAnchor="middle">
                    {node.label}
                  </text>
                  {node.value && (
                    <text className="node-value" x={pos.x} y={pos.y + radius + 28} textAnchor="middle">
                      {node.value}
                    </text>
                  )}
                </g>
              );
            })}
          </g>
        </svg>
        <div className="graph-controls">
          <button className="icon-button" onClick={() => zoom(0.1)} aria-label="Zoom in">
            <Plus size={16} />
          </button>
          <button className="icon-button" onClick={() => zoom(-0.1)} aria-label="Zoom out">
            <Minus size={16} />
          </button>
          <button className="icon-button" onClick={resetGraph} aria-label="Reset graph layout">
            <RotateCcw size={15} />
          </button>
          <button className="icon-button" aria-label="Fullscreen graph">
            <Maximize2 size={15} />
          </button>
        </div>
      </div>
      <div className="network-legend">
        <span>
          <i className="legend-dot low" /> Low risk
        </span>
        <span>
          <i className="legend-dot medium" /> Medium risk
        </span>
        <span>
          <i className="legend-dot high" /> High risk
        </span>
        <span>
          <i className="legend-dot critical" /> Critical risk
        </span>
      </div>
    </article>
  );
}
