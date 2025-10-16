/**
 * API calls pour l'authentification
 */
import { apiClient } from './client';
import type { LoginRequest, TokenResponse, User } from '@/types/api.types';

export const authApi = {
  /**
   * Login avec email et password
   */
  login: async (credentials: LoginRequest): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>(
      '/auth/login',
      credentials
    );
    return response.data;
  },

  /**
   * Refresh access token
   */
  refreshToken: async (refreshToken: string): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  /**
   * Recuperer l'utilisateur courant
   */
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },
};

export default authApi;
