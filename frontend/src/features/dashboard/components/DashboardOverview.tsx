/**
 * Dashboard Vue d'Ensemble principal
 */
import { RefreshCw, Award } from 'lucide-react';
import { useDashboardOverview } from '../hooks/useDashboardData';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { StockHealthSection } from './StockHealthSection';
import { SalesPerformanceSection } from './SalesPerformanceSection';
import { TopProductsCard } from './TopProductsCard';
import { DormantProductsCard } from './DormantProductsCard';
import { KPICard } from './KPICard';

export const DashboardOverview = () => {
  const { data, isLoading, error, refetch, isFetching } =
    useDashboardOverview();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner text="Chargement du dashboard..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <div className="text-center">
          <p className="text-red-600 font-medium mb-2">
            Erreur de chargement du dashboard
          </p>
          <p className="text-sm text-gray-600 mb-4">
            {error instanceof Error
              ? error.message
              : 'Une erreur est survenue'}
          </p>
          <button
            onClick={() => refetch()}
            className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
          >
            Reessayer
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center p-8">
        <p className="text-gray-600">Aucune donnee disponible</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Vue d'Ensemble</h1>
          <p className="text-sm text-gray-600 mt-1">
            Dernier rafraichissement:{' '}
            {new Date(data.generated_at).toLocaleTimeString('fr-FR')}
          </p>
        </div>
        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <RefreshCw
            className={`w-4 h-4 ${isFetching ? 'animate-spin' : ''}`}
          />
          Actualiser
        </button>
      </div>

      {/* Taux de Service */}
      {data.kpis && (
        <div className="max-w-md">
          <KPICard
            title="Taux de Service"
            value={`${data.kpis.taux_service}%`}
            subtitle="Commandes completees / Total commandes"
            icon={<Award className="w-6 h-6" />}
            color={data.kpis.taux_service >= 95 ? 'green' : 'amber'}
            trend={data.kpis.taux_service >= 95 ? 'up' : 'neutral'}
          />
        </div>
      )}

      {/* Sante Stock */}
      <section>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Sante Stock
        </h2>
        <StockHealthSection data={data.stock_health} />
      </section>

      {/* Performance Ventes */}
      <section>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Performance Ventes
        </h2>
        <SalesPerformanceSection data={data.sales_performance} />
      </section>

      {/* Top/Flop Produits */}
      <section>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Analyse Produits
        </h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <TopProductsCard products={data.top_products} />
          <DormantProductsCard products={data.dormant_products} />
        </div>
      </section>
    </div>
  );
};

export default DashboardOverview;
