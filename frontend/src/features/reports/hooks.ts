import { useMutation } from '@tanstack/react-query';
import { generateReport } from './api';
export function useGenerateReport() { return useMutation({ mutationFn: generateReport }); }
