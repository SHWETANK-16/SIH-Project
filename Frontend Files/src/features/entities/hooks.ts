import { useQuery } from '@tanstack/react-query';
import { getEntity } from './api';
export function useEntity(id: string) { return useQuery({ queryKey: ['entity', id], queryFn: () => getEntity(id), enabled: Boolean(id) }); }
