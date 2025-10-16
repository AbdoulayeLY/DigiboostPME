/**
 * Section Performance Ventes du dashboard
 */
import { TrendingUp, ShoppingCart, Calendar } from 'lucide-react';
import { KPICard } from './KPICard';
import { RevenueChart } from './RevenueChart';
import type { SalesPerformance } from '@/types/api.types';
import { formatCurrency, formatPercent } from '@/lib/utils';

interface SalesPerformanceSectionProps {
  data: SalesPerformance;
}

export const SalesPerformanceSection = ({
  data,
}: SalesPerformanceSectionProps) => {
  // Calculer la tendance entre CA 7j et CA 30j
  const avgDaily7 = data.ca_7j / 7;
  const avgDaily30 = data.ca_30j / 30;
  const trend = avgDaily7 > avgDaily30 ? 'up' : 'down';
  const trendPercent =
    ((avgDaily7 - avgDaily30) / avgDaily30) * 100;

  // Preparer les donnees pour le graphique (simulees pour l'instant)
  // Dans une version future, le backend pourrait fournir ces donnees
  const chartData = [
    { date: 'J-7', revenue: data.ca_7j * 0.12 },
    { date: 'J-6', revenue: data.ca_7j * 0.14 },
    { date: 'J-5', revenue: data.ca_7j * 0.13 },
    { date: 'J-4', revenue: data.ca_7j * 0.15 },
    { date: 'J-3', revenue: data.ca_7j * 0.16 },
    { date: 'J-2', revenue: data.ca_7j * 0.14 },
    { date: 'J-1', revenue: data.ca_7j * 0.16 },
  ];

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
