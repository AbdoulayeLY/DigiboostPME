/**
 * Section Performance Ventes du dashboard
 */
import { TrendingUp, ShoppingCart, Calendar } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { KPICard } from './KPICard';
import { RevenueChart } from './RevenueChart';
import type { SalesPerformance } from '@/types/api.types';
import { formatCurrency, formatPercent } from '@/lib/utils';
import { analyticsApi } from '@/api/analytics';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

interface SalesPerformanceSectionProps {
  data: SalesPerformance;
}

export const SalesPerformanceSection = ({
  data,
}: SalesPerformanceSectionProps) => {
  // Récupérer les vraies données d'évolution depuis l'API
  const { data: salesEvolutionData } = useQuery({
    queryKey: ['sales-evolution', 7],
    queryFn: () => analyticsApi.getSalesEvolution(7),
    staleTime: 30000, // 30 secondes
  });

  // Calculer la tendance entre CA 7j et CA 30j
  const avgDaily7 = data.ca_7j / 7;
  const avgDaily30 = data.ca_30j / 30;
  const trend = avgDaily7 > avgDaily30 ? 'up' : 'down';
  const trendPercent =
    ((avgDaily7 - avgDaily30) / avgDaily30) * 100;

  // Préparer les données réelles pour le graphique
  const chartData = salesEvolutionData?.data.map((day) => ({
    date: format(new Date(day.date), 'EEE dd', { locale: fr }),
    revenue: day.revenue,
  })) || [];

  return (
    <div className="space-y-4">
      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <KPICard
          title="CA 7 jours"
          value={formatCurrency(data.ca_7j)}
          subtitle="Chiffre d'affaires"
          icon={<Calendar className="w-6 h-6" />}
          color="blue"
          trend={trend}
          trendValue={formatPercent(trendPercent)}
        />
        <KPICard
          title="CA 30 jours"
          value={formatCurrency(data.ca_30j)}
          subtitle="Chiffre d'affaires"
          icon={<TrendingUp className="w-6 h-6" />}
          color="green"
        />
        <KPICard
          title="Transactions"
          value={data.ventes_30j}
          subtitle="Ventes 30 derniers jours"
          icon={<ShoppingCart className="w-6 h-6" />}
          color="blue"
        />
      </div>

      {/* Graphique */}
      <RevenueChart data={chartData} />
    </div>
  );
};

export default SalesPerformanceSection;
