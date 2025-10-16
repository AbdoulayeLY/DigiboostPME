### 🔧 PROMPT 1.6 : Auth Frontend & Layout Principal

```
CONTEXTE:
Le projet frontend est initialisé. Je dois créer l'interface d'authentification complète et le layout principal de l'application.

OBJECTIF:
Implémenter:
- Page login avec formulaire
- Gestion tokens (access + refresh)
- Hook useAuth
- ProtectedRoute component
- Layout principal (Header + Sidebar + Content)
- Navigation
- Indicateur connexion réseau

SPÉCIFICATIONS:

PAGE LOGIN (src/features/auth/components/LoginForm.tsx):
- Formulaire email + password
- Validation avec react-hook-form + zod
- Appel API /auth/login
- Stockage tokens
- Redirection après login
- Messages d'erreur
- Loading state

HOOK AUTH (src/features/auth/hooks/useAuth.ts):
```typescript
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { authApi } from '@/api/auth';

export const useAuth = () => {
  const navigate = useNavigate();
  const { setAuth, clearAuth, user, accessToken } = useAuthStore();

  const loginMutation = useMutation({
    mutationFn: authApi.login,
    onSuccess: (data) => {
      setAuth(data.user, data.access_token, data.refresh_token);
      navigate('/dashboard');
    },
  });

  const logout = () => {
    clearAuth();
    navigate('/login');
  };

  return {
    login: loginMutation.mutate,
    logout,
    user,
    isAuthenticated: !!accessToken,
    isLoading: loginMutation.isPending,
    error: loginMutation.error,
  };
};
```

PROTECTED ROUTE (src/features/auth/components/ProtectedRoute.tsx):
```typescript
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { accessToken } = useAuthStore();

  if (!accessToken) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};
```

LAYOUT HEADER (src/components/layout/Header.tsx):
- Logo Digiboost
- Nom utilisateur
- Indicateur connexion (online/offline)
- Bouton logout

LAYOUT SIDEBAR (src/components/layout/Sidebar.tsx):
Navigation:
- 📊 Vue d'Ensemble
- 📦 Gestion Stock
- 📈 Analyse Ventes
- 🔮 Prédictions
- 🚨 Alertes
- 📄 Rapports
- ⚙️ Paramètres

MAIN LAYOUT (src/components/layout/MainLayout.tsx):
```typescript
export const MainLayout = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  );
};
```

NETWORK INDICATOR (src/components/common/NetworkIndicator.tsx):
```typescript
import { useNetworkStatus } from '@/hooks/useNetworkStatus';
import { Wifi, WifiOff } from 'lucide-react';

export const NetworkIndicator = () => {
  const { isOnline } = useNetworkStatus();

  return (
    <div className={`flex items-center gap-2 text-sm ${isOnline ? 'text-green-600' : 'text-amber-600'}`}>
      {isOnline ? <Wifi className="w-4 h-4" /> : <WifiOff className="w-4 h-4" />}
      <span>{isOnline ? 'Connecté' : 'Hors ligne'}</span>
    </div>
  );
};
```

ROUTES (src/routes/index.tsx):
```typescript
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LoginForm } from '@/features/auth/components/LoginForm';
import { ProtectedRoute } from '@/features/auth/components/ProtectedRoute';
import { MainLayout } from '@/components/layout/MainLayout';
import { DashboardOverview } from '@/features/dashboard/components/DashboardOverview';

export const AppRoutes = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginForm />} />
        
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <MainLayout>
              <Routes>
                <Route index element={<DashboardOverview />} />
                {/* Autres routes dashboard */}
              </Routes>
            </MainLayout>
          </ProtectedRoute>
        } />
        
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
};
```

CRITÈRES D'ACCEPTATION:
✅ Page login accessible /login
✅ Formulaire validation fonctionne
✅ Login appelle API backend
✅ Tokens stockés après login réussi
✅ Redirection vers /dashboard après login
✅ ProtectedRoute bloque accès si non auth
✅ Layout Header + Sidebar s'affiche
✅ Navigation sidebar fonctionne
✅ Indicateur réseau change état
✅ Logout vide tokens et redirige /login

COMMANDES DE TEST:
```bash
npm run dev
# Tester login avec user créé en backend
# Vérifier tokens dans localStorage dev tools
# Tester navigation
# Tester logout
```
```

---