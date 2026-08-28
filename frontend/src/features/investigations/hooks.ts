import { useQuery } from '@tanstack/react-query';
import { getInvestigation } from './api';
export function useInvestigation(id: string) { return useQuery({ queryKey: ['investigation', id], queryFn: () => getInvestigation(id), enabled: Boolean(id) }); }
