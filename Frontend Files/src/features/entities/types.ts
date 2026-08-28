import type { Entity, NetworkEdge, NetworkNode } from '../../types/common';
export interface EntityProfile { entity: Entity; users: string[]; connectedEntities: { name: string; type: string; risk: string; relationship: string }[]; activity: { date: string; label: string; amount: string }[]; nodes: NetworkNode[]; edges: NetworkEdge[]; }
