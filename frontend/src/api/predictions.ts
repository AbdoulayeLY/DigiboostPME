/**
 * API calls pour les prédictions de ruptures de stock
 */
import { apiClient } from './client';
import type {
  RupturesPrevuesResponse,
  RecommandationsAchatResponse,
} from '@/types/api.types';

export const predictionsApi = {
  /**
   * Récupérer les ruptures de stock prévues
   */
  getRupturesPrevues: async (horizonDays: number = 15): Promise<RupturesPrevuesResponse> => {
    const response = await apiClient.get<RupturesPrevuesResponse>(
      '/predictions/ruptures',
      { params: { horizon_days: horizonDays } }
    );
    return response.data;
  },

  /**
   * Récupérer les recommandations d'achat groupées par fournisseur
   */
  getRecommandations: async (horizonDays: number = 15): Promise<RecommandationsAchatResponse> => {
    const response = await apiClient.get<RecommandationsAchatResponse>(
      '/predictions/recommandations',
      { params: { horizon_days: horizonDays } }
    );
    return response.data;
  },
};

export default predictionsApi;
