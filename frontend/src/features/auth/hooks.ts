import { useMutation } from '@tanstack/react-query';
import { authenticate } from './api';

export function useLogin() { return useMutation({ mutationFn: authenticate }); }
