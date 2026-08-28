import { useQuery } from '@tanstack/react-query';
import { getDashboardData } from './api';

export function useDashboardStats() { return useQuery({ queryKey: ['dashboard'], queryFn: getDashboardData }); }
