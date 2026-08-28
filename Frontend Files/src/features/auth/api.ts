import { apiClient } from '../../services/api/client';
import type { AuthenticatedUser, LoginCredentials } from './types';

const mockUser: AuthenticatedUser = { id: 'USR-023', name: 'Aarav Mehta', role: 'Lead Investigator', initials: 'AM' };

export async function authenticate(credentials: LoginCredentials): Promise<AuthenticatedUser> {
  await new Promise((resolve) => setTimeout(resolve, 700));
  if (!credentials.identifier.trim() || !credentials.password.trim()) throw new Error('Enter your investigator credentials to continue.');
  if (import.meta.env.VITE_ENABLE_MOCK_DATA !== 'false') return mockUser;
  // BACKEND TODO: Replace mock authentication with real authentication API.
  return apiClient.post<AuthenticatedUser>('/auth/login', credentials);
}
