import type { Investigation, NetworkEdge, NetworkNode } from '../../types/common';

export interface InvestigationWorkspace {
  investigation: Investigation;
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  timeline: { time: string; title: string; detail: string; type: 'alert' | 'transaction' | 'note' }[];
}
