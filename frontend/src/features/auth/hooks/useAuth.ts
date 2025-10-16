/**
 * Hook personnalise pour l'authentification
 */
import { useMutation, useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { authApi } from '@/api/auth';
import type { LoginRequest } from '@/types/api.types';

export const useAuth = () => {
  const navigate = useNavigate();
  const { setAuth, clearAuth, user, isAuthenticated } =
    useAuthStore();

  /**
   * Mutation pour le login
   */
  const loginMutation = useMutation({
    mutationFn: authApi.login,
    onSuccess: async (tokenData) => {
      // Sauvegarder les tokens temporairement
      localStorage.setItem('access_token', tokenData.access_token);
      localStorage.setItem('refresh_token', tokenData.refresh_token);

      // Recuperer l'utilisateur avec le nouveau token
      try {
        const userData = await authApi.getCurrentUser();

        // Sauvegarder tout dans le store
        setAuth(userData, tokenData.access_token, tokenData.refresh_token);

        // Rediriger vers le dashboard
        navigate('/dashboard');
      } catch (error) {
        // Si echec recuperation user, nettoyer
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        throw error;
      }
    },
  });

  /**
   * Fonction de logout
   */
  const logout = () => {
    clearAuth();
    navigate('/login');
  };

  /**
   * Query pour recuperer l'utilisateur au chargement de l'app
   * (si token existe deja dans le store)
   */
  const { refetch: refetchUser } = useQuery({
    queryKey: ['currentUser'],
    queryFn: authApi.getCurrentUser,
    enabled: false, // Ne pas executer automatiquement
    retry: false,
  });

  return {
    // Fonctions
    login: (credentials: LoginRequest) => loginMutation.mutate(credentials),
    logout,
    refetchUser,

    // Etat
    user,
    isAuthenticated,
    isLoading: loginMutation.isPending,
    error: loginMutation.error,
  };
};

export default useAuth;
