/**
 * Hook React Query pour les données de stock
 */
import { useQuery } from '@tanstack/react-query';
import { analyticsApi, type GetTopProductsParams } from '@/api/analytics';

/**
 * Hook pour récupérer tous les produits avec leurs analyses complètes
 * Pour la page de gestion du stock détaillée
 */
export const useStockData = (days: number = 30) => {
  return useQuery({
    queryKey: ['stock-data', days],
    queryFn: async () => {
      // Récupérer tous les produits via l'endpoint top products
      // avec une limite élevée pour obtenir tous les produits
      const topProducts = await analyticsApi.getTopProducts({
        limit: 1000,
        days,
        order_by: 'revenue',
      });
      return topProducts.products;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchInterval: 5 * 60 * 1000, // Rafraîchir toutes les 5 minutes
  });
};

/**
 * Hook pour récupérer l'analyse détaillée d'un produit spécifique
 */
export const useProductAnalysis = (productId: string | null) => {
  return useQuery({
    queryKey: ['product-analysis', productId],
    queryFn: () => analyticsApi.getProductAnalysis(productId!),
    enabled: !!productId, // Ne faire la requête que si productId est défini
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

/**
 * Hook pour récupérer les top produits
 */
export const useTopProducts = (params: GetTopProductsParams = {}) => {
  return useQuery({
    queryKey: ['top-products', params],
    queryFn: () => analyticsApi.getTopProducts(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook pour récupérer la performance par catégorie
 */
export const useCategoryPerformance = (days: number = 30) => {
  return useQuery({
    queryKey: ['category-performance', days],
    queryFn: () => analyticsApi.getCategoryPerformance(days),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook pour récupérer la classification ABC
 */
export const useABCClassification = (days: number = 90) => {
  return useQuery({
    queryKey: ['abc-classification', days],
    queryFn: () => analyticsApi.getABCClassification(days),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};
