/**
 * API calls pour les dashboards
 */
import { apiClient } from './client';
import type { DashboardOverview } from '@/types/api.types';

export const dashboardsApi = {
  /**
   * Recuperer le dashboard Vue d'Ensemble
   */
  getOverview: async (): Promise<DashboardOverview> => {
    const response = await apiClient.get<DashboardOverview>(
      '/dashboards/overview'
    );
    return response.data;
  },

  /**
   * Rafraichir les vues materialisees
   */
  refreshViews: async (): Promise<{ status: string; message: string }> => {
    const response = await apiClient.post<{ status: string; message: string }>(
      '/dashboards/refresh-views'
    );
    return response.data;
  },
};

export default dashboardsApi;
