import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createContext, useContext, useMemo, useState, type PropsWithChildren } from 'react';
import type { User } from '../types/common';

interface AuthContextValue {
  user: User | null;
  signIn: (user: User) => void;
  signOut: () => void;
}

const queryClient = new QueryClient({ defaultOptions: { queries: { retry: 1, staleTime: 30_000 } } });
const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AppProviders({ children }: PropsWithChildren) {
  const [user, setUser] = useState<User | null>(() => {
    const stored = localStorage.getItem('investigation-user');
    return stored ? (JSON.parse(stored) as User) : null;
  });

  const value = useMemo<AuthContextValue>(() => ({
    user,
    signIn: (nextUser) => { localStorage.setItem('investigation-user', JSON.stringify(nextUser)); setUser(nextUser); },
    signOut: () => { localStorage.removeItem('investigation-user'); setUser(null); },
  }), [user]);

  return <QueryClientProvider client={queryClient}><AuthContext.Provider value={value}>{children}</AuthContext.Provider></QueryClientProvider>;
}

export function useAuthContext() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuthContext must be used within AppProviders');
  return context;
}
