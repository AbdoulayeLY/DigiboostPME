### 🔧 PROMPT 1.7 : Dashboard Vue d'Ensemble Frontend

```
CONTEXTE:
L'authentification et le layout sont fonctionnels. Je dois créer le dashboard "Vue d'Ensemble" frontend qui affiche les KPIs du backend.

OBJECTIF:
Créer dashboard responsive avec:
- 3 sections: Santé Stock, Performance Ventes, Top/Flop
- KPI Cards avec icônes
- Graphiques (Recharts)
- Loading states
- Error handling
- Responsive mobile
- Rafraîchissement automatique

SPÉCIFICATIONS:

HOOK DASHBOARD (src/features/dashboard/hooks/useDashboardData.ts):
```typescript
import { useQuery } from '@tanstack/react-query';
import { dashboardsApi } from '@/api/dashboards';

export const useDashboardOverview = () => {
  return useQuery({
    queryKey: ['dashboard', 'overview'],
    queryFn: () => dashboardsApi.getOverview(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 30 * 1000, // Rafraîchir toutes les 30s
    refetchOnWindowFocus: true,
  });
};
```

API CLIENT (src/api/dashboards.ts):
```typescript
import { apiClient } from './client';

export const dashboardsApi = {
  getOverview: async () => {
    const { data } = await apiClient.get('/dashboards/overview');
    return data;
  },
};
```

COMPOSANT KPI CARD (src/features/dashboard/components/KPICard.tsx):
```typescript
interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  color?: 'green' | 'red' | 'blue' | 'amber';
}

export const KPICard = ({ title, value, subtitle, icon, trend, trendValue, color = 'blue' }: KPICardProps) => {
  // Implémenter card avec styles Tailwind
  // Afficher icône, titre, valeur, trend
};
```

SECTION SANTÉ STOCK (src/features/dashboard/components/StockHealthSection.tsx):
```typescript
export const StockHealthSection = ({ data }: { data: any }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <KPICard
        title="Total Produits"
        value={data.total_products}
        icon={<Package className="w-6 h-6" />}
        color="blue"
      />
      <KPICard
        title="Ruptures"
        value={data.rupture_count}
        subtitle="Produits en rupture"
        icon={<AlertTriangle className="w-6 h-6" />}
        color="red"
      />
      <KPICard
        title="Stock Faible"
        value={data.low_stock_count}
        subtitle="À réapprovisionner"
        icon={<AlertCircle className="w-6 h-6" />}
        color="amber"
      />
      <KPICard
        title="Valorisation"
        value={`${(data.total_stock_value / 1000000).toFixed(1)}M FCFA`}
        subtitle="Stock total"
        icon={<DollarSign className="w-6 h-6" />}
        color="green"
      />
    </div>
  );
};
```

SECTION PERFORMANCE VENTES (src/features/dashboard/components/SalesPerformanceSection.tsx):
- CA 7 jours (KPI Card)
- CA 30 jours (KPI Card)
- Graphique évolution CA (Line Chart Recharts)
- Nombre transactions

GRAPHIQUE CA (src/features/dashboard/components/RevenueChart.tsx):
```typescript
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export const RevenueChart = ({ data }: { data: any[] }) => {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="revenue" stroke="#4F46E5" strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  );
};
```

DASHBOARD PRINCIPAL (src/features/dashboard/components/DashboardOverview.tsx):
```typescript
import { useDashboardOverview } from '../hooks/useDashboardData';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { StockHealthSection } from './StockHealthSection';
import { SalesPerformanceSection } from './SalesPerformanceSection';

export const DashboardOverview = () => {
  const { data, isLoading, error, refetch } = useDashboardOverview();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="text-center p-8">
        <p className="text-red-600">Erreur de chargement</p>
        <button onClick={() => refetch()} className="mt-4 btn-primary">
          Réessayer
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Vue d'Ensemble</h1>
        <button onClick={() => refetch()} className="btn-secondary">
          Actualiser
        </button>
      </div>

      {/* Santé Stock */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Santé Stock</h2>
        <StockHealthSection data={data.stock_health} />
      </section>

      {/* Performance Ventes */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Performance Ventes</h2>
        <SalesPerformanceSection data={data.sales_performance} />
      </section>

      {/* Top/Flop Produits */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TopProductsCard products={data.top_products} />
        <DormantProductsCard products={data.dormant_products} />
      </div>
    </div>
  );
};
```

RESPONSIVE DESIGN:
- Mobile (< 768px): Cards empilées verticalement
- Tablet (768-1024px): 2 colonnes
- Desktop (> 1024px): 4 colonnes

CRITÈRES D'ACCEPTATION:
✅ Dashboard affiche données backend
✅ KPI Cards affichent valeurs correctes
✅ Graphiques Recharts fonctionnels
✅ Loading spinner pendant chargement
✅ Message erreur si API échoue
✅ Bouton "Actualiser" rafraîchit données
✅ Rafraîchissement auto 30s
✅ Responsive mobile/tablet/desktop
✅ Performance < 3s chargement
✅ Tests: Login → Dashboard affiche KPIs

COMMANDES DE TEST:
```bash
npm run dev
# Login → Dashboard
# Vérifier KPIs affichés
# Tester responsive (Chrome DevTools)
# Vérifier rafraîchissement auto (Network tab)
```
```
