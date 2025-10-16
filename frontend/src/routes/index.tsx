/**
 * Configuration des routes React Router
 */
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { LoginForm } from '@/features/auth/components/LoginForm';
import { ProtectedRoute } from '@/features/auth/components/ProtectedRoute';
import { MainLayout } from '@/components/layout/MainLayout';
import DashboardPage from '@/pages/DashboardPage';
import ProduitsPage from '@/pages/ProduitsPage';
import VentesPage from '@/pages/VentesPage';
import FournisseursPage from '@/pages/FournisseursPage';
import PrevisionsPage from '@/pages/PrevisionsPage';
import AlertesPage from '@/pages/AlertesPage';
import AlertHistoryPage from '@/pages/AlertHistoryPage';
import ParametresPage from '@/pages/ParametresPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/dashboard" replace />,
  },
  {
    path: '/login',
    element: <LoginForm />,
  },
  {
    // Routes protegees avec layout
    element: <ProtectedRoute />,
    children: [
      {
        element: <MainLayout />,
        children: [
          {
            path: '/dashboard',
            element: <DashboardPage />,
          },
          {
            path: '/produits',
            element: <ProduitsPage />,
          },
          {
            path: '/ventes',
            element: <VentesPage />,
          },
          {
            path: '/fournisseurs',
            element: <FournisseursPage />,
          },
          {
            path: '/previsions',
            element: <PrevisionsPage />,
          },
          {
            path: '/alertes',
            element: <AlertesPage />,
          },
          {
            path: '/alertes/history',
            element: <AlertHistoryPage />,
          },
          {
            path: '/parametres',
            element: <ParametresPage />,
          },
        ],
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/dashboard" replace />,
  },
]);

export default router;
