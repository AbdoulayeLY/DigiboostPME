/**
 * Hook pour recuperer les donnees du dashboard
 */
import { useQuery } from '@tanstack/react-query';
import { dashboardsApi } from '@/api/dashboards';

export const useDashboardOverview = () => {
  return useQuery({
    queryKey: ['dashboard', 'overview'],
    queryFn: () => dashboardsApi.getOverview(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 30 * 1000, // Rafraichir toutes les 30s
    refetchOnWindowFocus: true,
  });
};

export default useDashboardOverview;
