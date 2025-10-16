/**
 * Hook React Query pour la gestion des alertes
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { alertsApi, type AlertCreate, type AlertUpdate } from '@/api/alerts';

/**
 * Hook pour gérer les alertes
 */
export const useAlerts = () => {
  const queryClient = useQueryClient();

  // Query: Liste des alertes
  const { data: alerts, isLoading, error, refetch } = useQuery({
    queryKey: ['alerts'],
    queryFn: alertsApi.list,
    staleTime: 30 * 1000, // 30 secondes
  });

  // Mutation: Créer une alerte
  const createMutation = useMutation({
    mutationFn: (data: AlertCreate) => alertsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      toast.success('Alerte créée avec succès');
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Erreur lors de la création';
      toast.error(message);
    },
  });

  // Mutation: Mettre à jour une alerte
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: AlertUpdate }) =>
      alertsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      toast.success('Alerte modifiée avec succès');
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Erreur lors de la modification';
      toast.error(message);
    },
  });

  // Mutation: Supprimer une alerte
  const deleteMutation = useMutation({
    mutationFn: (id: string) => alertsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      toast.success('Alerte supprimée avec succès');
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Erreur lors de la suppression';
      toast.error(message);
    },
  });

  // Mutation: Toggle activation
  const toggleMutation = useMutation({
    mutationFn: (id: string) => alertsApi.toggle(id),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      const status = data.is_active ? 'activée' : 'désactivée';
      toast.success(`Alerte ${status}`);
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Erreur lors du changement de statut';
      toast.error(message);
    },
  });

  // Mutation: Tester une alerte
  const testMutation = useMutation({
    mutationFn: (id: string) => alertsApi.test(id),
    onSuccess: () => {
      toast.success('Test d\'alerte déclenché');
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Erreur lors du test';
      toast.error(message);
    },
  });

  return {
    // Data
    alerts: alerts || [],
    isLoading,
    error,
    refetch,

    // Mutations
    createAlert: createMutation.mutate,
    updateAlert: updateMutation.mutate,
    deleteAlert: deleteMutation.mutate,
    toggleAlert: toggleMutation.mutate,
    testAlert: testMutation.mutate,

    // Mutation states
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
    isToggling: toggleMutation.isPending,
    isTesting: testMutation.isPending,
  };
};
