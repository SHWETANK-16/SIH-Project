import type { DashboardStats } from '../../types/common';

export interface TimelinePoint { label: string; total: number; suspicious: number; }
export interface RiskSlice { name: string; value: number; color: string; }
export interface StatusSlice { name: string; value: number; color: string; }
export interface DashboardData { stats: DashboardStats; timeline: TimelinePoint[]; riskDistribution: RiskSlice[]; statusDistribution: StatusSlice[]; }
