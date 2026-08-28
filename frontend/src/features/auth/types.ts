import type { User } from '../../types/common';

export interface LoginCredentials {
  identifier: string;
  password: string;
  remember: boolean;
}

export type AuthenticatedUser = User;
