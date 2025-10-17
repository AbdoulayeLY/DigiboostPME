/**
 * API calls pour les analytics
 */
import { apiClient } from './client';
import type {
  ProductAnalysis,
  SalesEvolution,
  TopProductsResponse,
  CategoryPerformanceResponse,
  ABCClassification,
} from '@/types/api.types';

export interface GetTopProductsParams {
  limit?: number;
  days?: number;
  order_by?: 'revenue' | 'quantity' | 'transactions';
}

export const analyticsApi = {
  /**
   * Récupérer l'analyse détaillée d'un produit
   */
  getProductAnalysis: async (productId: string): Promise<ProductAnalysis> => {
    const response = await apiClient.get<ProductAnalysis>(
      `/analytics/products/${productId}`
    );
    return response.data;
  },

  /**
   * Récupérer l'évolution des ventes quotidiennes
   */
  getSalesEvolution: async (days: number = 30): Promise<SalesEvolution> => {
    const response = await apiClient.get<SalesEvolution>(
      '/analytics/sales/evolution',
      { params: { days } }
    );
    return response.data;
  },

  /**
   * Récupérer le top des produits
   */
  getTopProducts: async (
    params: GetTopProductsParams = {}
  ): Promise<TopProductsResponse> => {
    const { limit = 10, days = 30, order_by = 'revenue' } = params;
    const response = await apiClient.get<TopProductsResponse>(
      '/analytics/products/top',
      { params: { limit, days, order_by } }
    );
    return response.data;
  },

  /**
   * Récupérer la performance par catégorie
   */
  getCategoryPerformance: async (
    days: number = 30
  ): Promise<CategoryPerformanceResponse> => {
    const response = await apiClient.get<CategoryPerformanceResponse>(
      '/analytics/categories/performance',
      { params: { days } }
    );
    return response.data;
  },

  /**
   * Récupérer la classification ABC des produits
   */
  getABCClassification: async (
    days: number = 90
  ): Promise<ABCClassification> => {
    const response = await apiClient.get<ABCClassification>(
      '/analytics/products/abc',
      { params: { days } }
    );
    return response.data;
  },
};

export default analyticsApi;
