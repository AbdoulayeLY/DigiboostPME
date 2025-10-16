/**
 * Hook React Query pour l'historique des alertes
 */
import { useQuery } from '@tanstack/react-query';
import { alertsApi, type AlertHistoryFilters } from '@/api/alerts';

/**
 * Hook pour récupérer l'historique des déclenchements d'alertes
 * @param filters - Filtres optionnels (alert_id, alert_type, severity, limit, offset)
 */
export const useAlertHistory = (filters?: AlertHistoryFilters) => {
  return useQuery({
    queryKey: ['alert-history', filters],
    queryFn: () => alertsApi.getHistory(filters),
    refetchInterval: 60 * 1000, // Rafraîchir automatiquement chaque minute
    staleTime: 30 * 1000, // Considérer les données stales après 30s
  });
};
