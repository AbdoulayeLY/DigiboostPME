/**
 * Composant pour proteger les routes authentifiees
 */
import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';

interface ProtectedRouteProps {
  /**
   * Roles autorises (optionnel)
   * Si specifie, verifie que l'utilisateur a un des roles autorises
   */
  allowedRoles?: string[];
}

export const ProtectedRoute = ({ allowedRoles }: ProtectedRouteProps) => {
  const { isAuthenticated, user } = useAuthStore();

  // Si pas authentifie, rediriger vers login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Si roles specifies, verifier que l'utilisateur a un des roles
  if (allowedRoles && allowedRoles.length > 0) {
    const hasRequiredRole = user?.role && allowedRoles.includes(user.role);

    if (!hasRequiredRole) {
      // Rediriger vers une page d'erreur 403 ou dashboard
      return <Navigate to="/dashboard" replace />;
    }
  }

  // Si tout est OK, afficher la route protegee
  return <Outlet />;
};

export default ProtectedRoute;
