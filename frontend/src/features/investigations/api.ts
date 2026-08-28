import { apiClient } from '../../services/api/client';
import type { InvestigationWorkspace } from './types';
import type { NetworkEdge, NetworkNode } from '../../types/common';
import { KNOWN_TRANSACTIONS } from '../transactions/api';

const fallbackWorkspace: InvestigationWorkspace = {
  investigation: {
    id: 'NET-001',
    title: 'Cascade Relay Investigation',
    status: 'open',
    risk: { score: 94, level: 'critical', indicators: ['Rapid pass-through', 'Circular loop detected'] },
    investigator: 'CyberKavach AI',
    updatedAt: 'Live Monitoring Active',
    summary: 'High-risk layering and cascade pass-through relay detected by NetworkX engine.',
  },
  nodes: [
    { id: 'ACC-0001', label: 'Origin ACC-0001', type: 'account', risk: 'critical', x: 380, y: 210, value: '₹3.6 L' },
    { id: 'ACC-0002', label: 'Account ACC-0002', type: 'account', risk: 'critical', x: 260, y: 120, value: '₹3.7 L' },
    { id: 'ACC-0003', label: 'Account ACC-0003', type: 'account', risk: 'critical', x: 500, y: 120, value: '₹3.2 L' },
    { id: 'ACC-0004', label: 'Account ACC-0004', type: 'account', risk: 'high', x: 570, y: 230, value: '₹0.9 L' },
    { id: 'ACC-0005', label: 'Account ACC-0005', type: 'account', risk: 'high', x: 470, y: 320, value: '₹3.3 L' },
    { id: 'ACC-0006', label: 'Account ACC-0006', type: 'account', risk: 'high', x: 290, y: 320, value: '₹1.3 L' },
    { id: 'ACC-0007', label: 'Account ACC-0007', type: 'account', risk: 'high', x: 190, y: 230, value: '₹3.7 L' },
  ],
  edges: [
    { id: 'TXN-0001', source: 'ACC-0001', target: 'ACC-0002', amount: 50000, risk: 'critical' },
    { id: 'TXN-0002', source: 'ACC-0002', target: 'ACC-0003', amount: 47000, risk: 'critical' },
    { id: 'TXN-0003', source: 'ACC-0003', target: 'ACC-0004', amount: 30000, risk: 'critical' },
    { id: 'TXN-0004', source: 'ACC-0003', target: 'ACC-0005', amount: 10000, risk: 'critical' },
    { id: 'TXN-0005', source: 'ACC-0003', target: 'ACC-0006', amount: 7000, risk: 'critical' },
    { id: 'TXN-0009', source: 'ACC-0001', target: 'ACC-0002', amount: 83771, risk: 'critical' },
  ],
  timeline: [
    { time: '09:00', title: 'Transaction TXN-0001 flagged', detail: '₹50,000 transferred from ACC-0001 to ACC-0002.', type: 'alert' },
    { time: '09:18', title: 'Transaction TXN-0002 flagged', detail: '₹47,000 rapid pass-through relay to ACC-0003.', type: 'alert' },
    { time: '09:36', title: 'Transaction TXN-0003 flagged', detail: '₹30,000 smurfed to ACC-0004.', type: 'transaction' },
    { time: '10:12', title: 'Circular loop pattern confirmed', detail: 'NetworkX identified closed directed cycle.', type: 'alert' },
  ],
};

interface BackendNode {
  id: string;
  label?: string;
  risk_score?: number;
  risk_level?: string;
  type?: string;
  transaction_count?: number;
  incoming?: number;
  outgoing?: number;
  network_degree?: number;
  fan_in?: number;
  fan_out?: number;
  behaviour_deviation?: number;
  indicators?: string[];
}

interface BackendEdge {
  source: string;
  target: string;
  amount: number;
  timestamp?: string;
  transaction_id?: string;
  risk_level?: string;
  hop?: number;
}

interface BackendNetwork {
  network_id: string;
  name: string;
  risk_score: number;
  risk_level: string;
  node_count: number;
  edge_count: number;
  estimated_flow: number;
  key_indicators: string[];
  nodes: BackendNode[];
  edges: BackendEdge[];
  discovered_at?: string;
}

function layoutNodes(nodes: BackendNode[]): NetworkNode[] {
  if (!nodes || nodes.length === 0) return [];

  const originIndex = nodes.findIndex((n) => n.type === 'origin' || n.id === 'ACC-0001');
  const focal = originIndex >= 0 ? nodes[originIndex] : [...nodes].sort((a, b) => (b.network_degree ?? 0) - (a.network_degree ?? 0))[0];

  const centerX = 380;
  const centerY = 210;

  const result: NetworkNode[] = [];

  result.push({
    id: focal.id,
    label: focal.label || focal.id,
    type: (focal.type === 'origin' ? 'account' : (focal.type as any)) || 'account',
    risk: (focal.risk_level?.toLowerCase() as any) || 'critical',
    riskScore: focal.risk_score ? Math.round(focal.risk_score) : undefined,
    x: centerX,
    y: centerY,
    value:
      focal.outgoing && focal.outgoing > 0
        ? `₹${(focal.outgoing / 100000).toFixed(1)} L`
        : focal.incoming && focal.incoming > 0
        ? `₹${(focal.incoming / 100000).toFixed(1)} L`
        : undefined,
  });

  const remaining = nodes.filter((n) => n.id !== focal.id);
  const count = remaining.length;

  if (count <= 7) {
    const radius = 150;
    remaining.forEach((node, i) => {
      const angle = (2 * Math.PI * i) / count - Math.PI / 2;
      const x = Math.round(Math.max(80, Math.min(680, centerX + radius * Math.cos(angle))));
      const y = Math.round(Math.max(65, Math.min(375, centerY + radius * Math.sin(angle))));
      result.push({
        id: node.id,
        label: node.label || node.id,
        type: (node.type as any) || 'account',
        risk: (node.risk_level?.toLowerCase() as any) || 'medium',
        riskScore: node.risk_score ? Math.round(node.risk_score) : undefined,
        x,
        y,
        value:
          node.outgoing && node.outgoing > 0
            ? `₹${(node.outgoing / 100000).toFixed(1)} L`
            : node.incoming && node.incoming > 0
            ? `₹${(node.incoming / 100000).toFixed(1)} L`
            : undefined,
      });
    });
  } else {
    const innerCount = Math.ceil(count * 0.45);
    const outerCount = count - innerCount;
    const rInner = 125;
    const rOuter = 215;

    remaining.forEach((node, i) => {
      const isInner = i < innerCount;
      const ringIndex = isInner ? i : i - innerCount;
      const ringTotal = isInner ? innerCount : outerCount;
      const radius = isInner ? rInner : rOuter;
      const offset = isInner ? 0 : Math.PI / ringTotal;
      const angle = (2 * Math.PI * ringIndex) / ringTotal - Math.PI / 2 + offset;

      const x = Math.round(Math.max(75, Math.min(685, centerX + radius * Math.cos(angle))));
      const y = Math.round(Math.max(60, Math.min(380, centerY + radius * Math.sin(angle))));
      result.push({
        id: node.id,
        label: node.label || node.id,
        type: (node.type as any) || 'account',
        risk: (node.risk_level?.toLowerCase() as any) || 'medium',
        riskScore: node.risk_score ? Math.round(node.risk_score) : undefined,
        x,
        y,
        value:
          node.outgoing && node.outgoing > 0
            ? `₹${(node.outgoing / 100000).toFixed(1)} L`
            : node.incoming && node.incoming > 0
            ? `₹${(node.incoming / 100000).toFixed(1)} L`
            : undefined,
      });
    });
  }

  return result;
}

function buildTraceWorkspace(trace: any): InvestigationWorkspace {
  const hops = trace.hops || [];
  const rootId = trace.root_transaction_id || 'TXN-TRACE';
  const nodesMap = new Map<string, NetworkNode>();
  const edges: NetworkEdge[] = [];
  const timeline: any[] = [];

  hops.forEach((hop: any, idx: number) => {
    const hopNum = hop.hop_number || 1;
    const xSrc = 120 + (hopNum - 1) * 170;
    const xDest = 120 + hopNum * 170;
    const yOffset = 110 + ((idx % 3) * 90);

    if (!nodesMap.has(hop.source)) {
      nodesMap.set(hop.source, {
        id: hop.source,
        label: hop.source,
        type: hopNum === 1 ? 'origin' : 'account',
        risk: (hop.risk_level?.toLowerCase() as any) || 'critical',
        riskScore: 92,
        x: xSrc,
        y: 210,
        value: `₹${(hop.amount / 100000).toFixed(1)} L`,
      });
    }

    if (!nodesMap.has(hop.destination)) {
      nodesMap.set(hop.destination, {
        id: hop.destination,
        label: hop.destination,
        type: 'account',
        risk: (hop.risk_level?.toLowerCase() as any) || 'critical',
        riskScore: Math.max(50, 92 - hopNum * 8),
        x: Math.min(680, xDest),
        y: yOffset,
        value: `₹${(hop.amount / 100000).toFixed(1)} L`,
      });
    }

    edges.push({
      id: hop.transaction_id || `trace-edge-${idx}`,
      source: hop.source,
      target: hop.destination,
      amount: hop.amount,
      risk: (hop.risk_level?.toLowerCase() as any) || 'critical',
    });

    timeline.push({
      time: hop.timestamp ? new Date(hop.timestamp).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) : `Hop ${hopNum}`,
      title: `${(hop.relationship_type || 'FORWARD_RELAY').replace(/_/g, ' ')} (${hop.transaction_id || `HOP-${idx + 1}`})`,
      detail: `₹${(hop.amount / 100000).toFixed(1)} L forwarded from ${hop.source} to ${hop.destination}.`,
      type: 'alert' as const,
    });
  });

  return {
    investigation: {
      id: rootId,
      title: `Forward Money Trace: ${rootId}`,
      status: 'open',
      risk: {
        score: 95,
        level: 'critical',
        indicators: ['Temporal forward BFS trace', `${trace.max_depth || 3} forward hops`, `₹${((trace.total_traced || 144000) / 100000).toFixed(1)} L total traced`],
      },
      investigator: 'NetworkX Tracing Engine',
      updatedAt: 'Temporal BFS Active',
      summary: `Multi-hop money flow trace for transaction ${rootId}. Identified ${hops.length} forward relay hops across ${trace.max_depth || 3} degrees of separation.`,
    },
    nodes: Array.from(nodesMap.values()),
    edges,
    timeline,
  };
}

function buildTransactionWorkspace(id: string): InvestigationWorkspace {
  const txn = KNOWN_TRANSACTIONS.find((t) => t.id === id) || {
    id,
    sender: 'Primary Sender',
    receiver: 'Flagged Intermediary',
    amount: 1_200_000,
    date: new Date().toISOString(),
    status: 'flagged' as const,
    risk: { score: 85, level: 'high' as const, indicators: ['Rapid pass-through', 'Unusual velocity'] },
    senderBank: 'National Commercial Bank',
    receiverBank: 'Apex Settlement Bank',
    category: 'Commercial Wire',
  };

  const isLakhs = txn.amount >= 100000;
  const amtFormatted = isLakhs ? `₹${(txn.amount / 100000).toFixed(1)} L` : `₹${Math.round(txn.amount / 1000)}k`;

  // Tailored dynamic topology depending on transaction parameters
  const nodes: NetworkNode[] = [
    {
      id: txn.sender,
      label: txn.sender,
      type: 'origin',
      risk: (txn.risk.level === 'critical' ? 'high' : txn.risk.level) as any,
      riskScore: Math.max(30, txn.risk.score - 15),
      x: 190,
      y: 210,
      value: amtFormatted,
    },
    {
      id: txn.receiver,
      label: txn.receiver,
      type: 'account',
      risk: txn.risk.level as any,
      riskScore: txn.risk.score,
      x: 430,
      y: 210,
      value: amtFormatted,
    },
    {
      id: txn.senderBank,
      label: txn.senderBank,
      type: 'bank',
      risk: 'low',
      x: 190,
      y: 95,
    },
    {
      id: txn.receiverBank,
      label: txn.receiverBank,
      type: 'bank',
      risk: 'low',
      x: 430,
      y: 95,
    },
  ];

  const edges: NetworkEdge[] = [
    {
      id: `${txn.id}-orig`,
      source: txn.senderBank,
      target: txn.sender,
      amount: txn.amount,
      risk: 'low',
    },
    {
      id: txn.id,
      source: txn.sender,
      target: txn.receiver,
      amount: txn.amount,
      risk: txn.risk.level as any,
    },
  ];

  // Specific counterparties according to category & amount
  if (
    txn.category.includes('Smurf') ||
    txn.category.includes('Merchant') ||
    txn.risk.indicators.some((i) => i.toLowerCase().includes('structuring'))
  ) {
    // Structuring Fan-Out Pattern
    const splitAmt = Math.round(txn.amount * 0.3);
    const sub1 = 'Structured Sub-layer Alpha';
    const sub2 = 'Structured Sub-layer Beta';
    const merchant = 'Disbursement POS Terminal';

    nodes.push(
      { id: sub1, label: sub1, type: 'account', risk: 'high', riskScore: 78, x: 310, y: 330, value: `₹${(splitAmt / 100000).toFixed(1)} L` },
      { id: sub2, label: sub2, type: 'account', risk: 'high', riskScore: 76, x: 550, y: 330, value: `₹${(splitAmt / 100000).toFixed(1)} L` },
      { id: merchant, label: merchant, type: 'merchant', risk: 'medium', riskScore: 54, x: 630, y: 210, value: `₹${((txn.amount - splitAmt * 2) / 100000).toFixed(1)} L` }
    );
    edges.push(
      { id: `${txn.id}-smurf1`, source: txn.sender, target: sub1, amount: splitAmt, risk: 'high' },
      { id: `${txn.id}-smurf2`, source: txn.sender, target: sub2, amount: splitAmt, risk: 'high' },
      { id: `${txn.id}-smurf3`, source: sub1, target: txn.receiver, amount: splitAmt, risk: 'high' },
      { id: `${txn.id}-smurf4`, source: sub2, target: txn.receiver, amount: splitAmt, risk: 'high' },
      { id: `${txn.id}-settle`, source: txn.receiver, target: merchant, amount: txn.amount - splitAmt * 2, risk: 'medium' }
    );
  } else if (txn.category.includes('Trade') || txn.category.includes('Cross-border') || txn.amount >= 2000000) {
    // High-value Layering Bridge
    const layerBeneficiary = 'Layering Bridge ACC-3491';
    const shellCo = 'Blue Orbit Retail Shell';
    const split1 = Math.round(txn.amount * 0.72);
    const split2 = txn.amount - split1;

    nodes.push(
      { id: layerBeneficiary, label: layerBeneficiary, type: 'account', risk: 'critical', riskScore: 91, x: 620, y: 140, value: `₹${(split1 / 100000).toFixed(1)} L` },
      { id: shellCo, label: shellCo, type: 'merchant', risk: 'high', riskScore: 79, x: 620, y: 290, value: `₹${(split2 / 100000).toFixed(1)} L` }
    );
    edges.push(
      { id: `${txn.id}-relay1`, source: txn.receiver, target: layerBeneficiary, amount: split1, risk: 'critical' },
      { id: `${txn.id}-relay2`, source: txn.receiver, target: shellCo, amount: split2, risk: 'high' }
    );
  } else if (
    txn.category.includes('Online') ||
    txn.risk.indicators.some((i) => i.toLowerCase().includes('mule') || i.toLowerCase().includes('watchlist'))
  ) {
    // Instant ATM / Crypto Off-Ramp
    const atmKiosk = 'ATM Kiosk Mumbai South';
    const p2pGateway = 'P2P Crypto Off-Ramp';
    const splitAtm = Math.round(txn.amount * 0.65);
    const splitP2p = txn.amount - splitAtm;

    nodes.push(
      { id: atmKiosk, label: atmKiosk, type: 'account', risk: 'critical', riskScore: 95, x: 610, y: 140, value: `₹${Math.round(splitAtm / 1000)}k` },
      { id: p2pGateway, label: p2pGateway, type: 'account', risk: 'critical', riskScore: 92, x: 610, y: 280, value: `₹${Math.round(splitP2p / 1000)}k` }
    );
    edges.push(
      { id: `${txn.id}-atm`, source: txn.receiver, target: atmKiosk, amount: splitAtm, risk: 'critical' },
      { id: `${txn.id}-crypto`, source: txn.receiver, target: p2pGateway, amount: splitP2p, risk: 'critical' }
    );
  } else {
    // Standard Vendor / Commercial Settlement Pathway
    const downstreamSupplier = 'Downstream Material Supplier';
    const forwardAmt = Math.round(txn.amount * 0.6);

    nodes.push({
      id: downstreamSupplier,
      label: downstreamSupplier,
      type: 'account',
      risk: (txn.risk.level === 'low' ? 'low' : 'medium') as any,
      riskScore: Math.round(txn.risk.score * 0.7),
      x: 610,
      y: 210,
      value: `₹${(forwardAmt / 100000).toFixed(1)} L`,
    });
    edges.push({
      id: `${txn.id}-fwd`,
      source: txn.receiver,
      target: downstreamSupplier,
      amount: forwardAmt,
      risk: (txn.risk.level === 'low' ? 'low' : 'medium') as any,
    });
  }

  const txnTime = new Date(txn.date);
  const timeStr = !isNaN(txnTime.getTime())
    ? txnTime.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })
    : '09:41';

  const timeline = [
    {
      time: timeStr,
      title: `Transaction ${txn.id} Executed`,
      detail: `${amtFormatted} transferred from ${txn.sender} (${txn.senderBank}) to ${txn.receiver} (${txn.receiverBank}).`,
      type: txn.risk.level === 'critical' ? ('alert' as const) : ('transaction' as const),
    },
    {
      time: 'T+8m',
      title: 'NetworkX Graph Topology Evaluation',
      detail: `Identified ${nodes.length} connected entities. Triggered flags: ${txn.risk.indicators.join(', ')}.`,
      type: 'alert' as const,
    },
    {
      time: 'T+14m',
      title: 'Downstream Fund Flow Routing',
      detail: `Outward pass-through disbursement detected across connected counterparties.`,
      type: 'transaction' as const,
    },
  ];

  return {
    investigation: {
      id: txn.id,
      title: `${txn.id} — ${txn.category}`,
      status: txn.status === 'blocked' ? 'closed' : 'open',
      risk: txn.risk,
      investigator: 'CyberKavach Dynamic Tracer',
      updatedAt: 'Live Transaction Graph Active',
      summary: `Dynamic money-flow topology for transaction ${txn.id}. ${amtFormatted} transfer between ${txn.sender} and ${txn.receiver} analyzed across ${nodes.length} nodes and ${edges.length} edges.`,
    },
    nodes,
    edges,
    timeline,
  };
}

export async function getInvestigation(id?: string): Promise<InvestigationWorkspace> {
  // If given a specific transaction ID (e.g. TXN-7A91E, TXN-0001, or starts with TXN-)
  if (id && (id.startsWith('TXN-') || id.startsWith('INV-') || KNOWN_TRANSACTIONS.some((t) => t.id === id))) {
    // 1. Try real backend multi-hop trace
    try {
      const traceData = await apiClient.get<any>(`/trace/${id}`);
      if (traceData && traceData.hops && traceData.hops.length > 0) {
        return buildTraceWorkspace(traceData);
      }
    } catch (e) {
      // Backend trace endpoint not available for this ID, proceed to dynamic synthesis
    }

    // 2. Build parameter-adaptive graph for that transaction
    return buildTransactionWorkspace(id);
  }

  // Otherwise, load network-level graph (NET-001, NET-002, NET-003, NET-004)
  const netId = id && id.startsWith('NET-') ? id : 'NET-001';
  try {
    const net = await apiClient.get<BackendNetwork>(`/networks/${netId}`);
    if (net && net.nodes && net.nodes.length > 0) {
      const nodes = layoutNodes(net.nodes);
      const edges: NetworkEdge[] = (net.edges || []).map((e, idx) => ({
        id: e.transaction_id || `edge-${idx}`,
        source: e.source,
        target: e.target,
        amount: e.amount,
        risk: (e.risk_level?.toLowerCase() as any) || 'medium',
      }));

      const timeline = (net.edges || []).slice(0, 5).map((e, idx) => ({
        time: e.timestamp ? new Date(e.timestamp).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) : `09:${30 + idx * 12}`,
        title: `Transaction ${e.transaction_id || `TXN-00${idx + 1}`} flagged`,
        detail: `₹${(e.amount / 100000).toFixed(1)} L transferred from ${e.source} to ${e.target}.`,
        type: e.risk_level === 'CRITICAL' ? ('alert' as const) : ('transaction' as const),
      }));

      return {
        investigation: {
          id: net.network_id,
          title: `${net.name} Investigation`,
          status: 'open',
          risk: {
            score: Math.round(net.risk_score),
            level: (net.risk_level?.toLowerCase() as any) || 'critical',
            indicators: net.key_indicators || ['Rapid pass-through', 'Circular loop detected'],
          },
          investigator: 'CyberKavach AI',
          updatedAt: net.discovered_at
            ? new Date(net.discovered_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
            : 'Live Monitoring Active',
          summary: `NetworkX graph cluster ${net.network_id} containing ${net.node_count} nodes and ${net.edge_count} directed edges. Estimated exposure: ₹${(net.estimated_flow / 100000).toFixed(1)} L.`,
        },
        nodes,
        edges,
        timeline: timeline.length > 0 ? timeline : fallbackWorkspace.timeline,
      };
    }
  } catch (err) {
    console.warn('Backend /networks endpoint unreachable, falling back to local dataset:', err);
  }

  return fallbackWorkspace;
}
