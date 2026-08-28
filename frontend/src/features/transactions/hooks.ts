import { useQuery } from '@tanstack/react-query';
import { getTransaction, getTransactions } from './api';

export function useTransactions() { return useQuery({ queryKey: ['transactions'], queryFn: getTransactions }); }
export function useTransaction(id: string) { return useQuery({ queryKey: ['transactions', id], queryFn: () => getTransaction(id), enabled: Boolean(id) }); }
