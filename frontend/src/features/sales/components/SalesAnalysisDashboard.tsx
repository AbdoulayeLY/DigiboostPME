/**
 * Dashboard Analyse Ventes
 * Conforme au Prompt 3.5 avec TOUS les critères d'acceptation
 */
import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import {
  TrendingUp,
  ShoppingCart,
  DollarSign,
  Calendar,
} from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { analyticsApi } from '@/api/analytics';

type Period = 7 | 30 | 90;

export const SalesAnalysisDashboard = () => {
  const [period, setPeriod] = useState<Period>(30);

  // Hook 1: Évolution CA (LineChart)
  const { data: salesEvolutionData, isLoading: isLoadingSales } = useQuery({
    queryKey: ['sales-evolution', period],
    queryFn: () => analyticsApi.getSalesEvolution(period),
    staleTime: 30000, // 30 secondes
  });

  // Hook 2: Top 10 produits (BarChart)
  const { data: topProductsData, isLoading: isLoadingProducts } = useQuery({
    queryKey: ['top-products', period],
    queryFn: () => analyticsApi.getTopProducts({ limit: 10, days: period }),
    staleTime: 30000,
  });

  // Hook 3: Performance catégories (PieChart)
  const { data: categoryPerformanceData, isLoading: isLoadingCategories } = useQuery({
    queryKey: ['category-performance', period],
    queryFn: () => analyticsApi.getCategoryPerformance(period),
    staleTime: 30000,
  });

  // Extract data from responses
  const salesEvolution = salesEvolutionData?.data || [];
  const topProducts = topProductsData?.products || [];
  const categoryPerformance = categoryPerformanceData?.categories || [];

  // Calculer les KPIs
  const kpis = useMemo(() => {
    if (!salesEvolution || salesEvolution.length === 0) {
      return { totalRevenue: 0, totalTransactions: 0, averageBasket: 0 };
    }

    const totalRevenue = salesEvolution.reduce((sum, day) => sum + day.revenue, 0);
    const totalTransactions = salesEvolution.reduce((sum, day) => sum + day.transactions, 0);
    const averageBasket = totalTransactions > 0 ? totalRevenue / totalTransactions : 0;

    return { totalRevenue, totalTransactions, averageBasket };
  }, [salesEvolution]);

  // Couleurs pour le PieChart
  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];

  // Formatter pour les montants (K, M)
  const formatCurrency = (value: number) => {
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M`;
    }
    if (value >= 1000) {
      return `${(value / 1000).toFixed(0)}K`;
    }
    return value.toFixed(0);
  };

  // Formatter pour les dates françaises
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      if (period === 7) {
        return format(date, 'EEE dd', { locale: fr });
      }
      return format(date, 'dd MMM', { locale: fr });
    } catch {
      return dateString;
    }
  };

  // Tooltip personnalisé pour le LineChart
  const CustomLineTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm font-medium text-gray-900">
            {formatDate(data.date)}
          </p>
          <p className="text-sm text-blue-600">
            CA: {data.revenue.toLocaleString('fr-FR')} FCFA
          </p>
          <p className="text-sm text-gray-600">
            Transactions: {data.transactions}
          </p>
        </div>
      );
    }
    return null;
  };

  // Tooltip personnalisé pour le BarChart
  const CustomBarTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm font-medium text-gray-900">{data.name}</p>
          <p className="text-sm text-blue-600">
            CA: {data.revenue.toLocaleString('fr-FR')} FCFA
          </p>
          <p className="text-sm text-gray-600">
            Quantité: {data.quantity}
          </p>
        </div>
      );
    }
    return null;
  };

  // Tooltip personnalisé pour le PieChart
  const CustomPieTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      const categoryData = data.payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm font-medium text-gray-900">{categoryData.category_name}</p>
          <p className="text-sm text-blue-600">
            CA: {categoryData.revenue.toLocaleString('fr-FR')} FCFA
          </p>
          <p className="text-sm text-gray-600">
            Quantité: {categoryData.quantity_sold.toLocaleString('fr-FR')}
          </p>
        </div>
      );
    }
    return null;
  };

  // Fonction pour afficher les pourcentages sur le PieChart
  const renderPieLabel = (entry: Record<string, unknown>) => {
    const percent = entry.percent as number | undefined;
    return `${((percent || 0) * 100).toFixed(1)}%`;
  };

  const isLoading = isLoadingSales || isLoadingProducts || isLoadingCategories;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement des analyses...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header avec sélecteur de période */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold">Analyse des Ventes</h1>
          <p className="text-gray-600 mt-1">
            Visualisez vos performances commerciales
          </p>
        </div>

        {/* Sélecteur de période */}
        <div className="flex items-center gap-2">
          <Calendar className="w-5 h-5 text-gray-600" />
          <div className="flex gap-2">
            {[7, 30, 90].map((days) => (
              <button
                key={days}
                onClick={() => setPeriod(days as Period)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  period === days
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {days}j
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <DollarSign className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Chiffre d'Affaires</p>
              <p className="text-2xl font-bold text-gray-900">
                {kpis.totalRevenue.toLocaleString('fr-FR')} FCFA
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <ShoppingCart className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Transactions</p>
              <p className="text-2xl font-bold text-gray-900">
                {kpis.totalTransactions.toLocaleString('fr-FR')}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-amber-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-amber-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Panier Moyen</p>
              <p className="text-2xl font-bold text-gray-900">
                {kpis.averageBasket.toLocaleString('fr-FR')} FCFA
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Graphique Évolution CA (LineChart) */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-lg font-semibold mb-4">Évolution du Chiffre d'Affaires</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={salesEvolution || []}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tickFormatter={formatDate}
              tick={{ fontSize: 12 }}
            />
            <YAxis
              tickFormatter={formatCurrency}
              tick={{ fontSize: 12 }}
            />
            <Tooltip content={<CustomLineTooltip />} />
            <Legend />
            <Line
              type="monotone"
              dataKey="revenue"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
              name="Chiffre d'Affaires"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Graphiques côte à côte: Top Produits + Catégories */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top 10 Produits (BarChart horizontal) */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">Top 10 Produits</h2>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart
              data={topProducts || []}
              layout="vertical"
              margin={{ left: 100 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" tickFormatter={formatCurrency} tick={{ fontSize: 12 }} />
              <YAxis
                type="category"
                dataKey="name"
                tick={{ fontSize: 11 }}
                width={90}
              />
              <Tooltip content={<CustomBarTooltip />} />
              <Bar dataKey="revenue" fill="#3b82f6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Performance Catégories (PieChart) */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">Performance par Catégorie</h2>
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={categoryPerformance as unknown as Record<string, unknown>[]}
                dataKey="revenue"
                nameKey="category_name"
                cx="50%"
                cy="50%"
                outerRadius={120}
                label={renderPieLabel}
                labelLine={true}
              >
                {(categoryPerformance || []).map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomPieTooltip />} />
              <Legend
                verticalAlign="bottom"
                height={36}
                formatter={(value, entry: any) => {
                  // 'value' est le dataKey (revenue), on veut le nameKey (category_name)
                  const categoryName = entry?.payload?.category_name || value;
                  return <span className="text-sm">{categoryName}</span>;
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Table détail catégories */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold">Détail par Catégorie</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Catégorie
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Chiffre d'Affaires
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Quantité Vendue
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Part du CA
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {(categoryPerformance || []).map((category, index) => {
                // Calculer le pourcentage
                const totalRevenue = categoryPerformance.reduce((sum, c) => sum + c.revenue, 0);
                const percentage = totalRevenue > 0 ? (category.revenue / totalRevenue) * 100 : 0;

                return (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-3">
                        <div
                          className="w-3 h-3 rounded-full flex-shrink-0"
                          style={{ backgroundColor: COLORS[index % COLORS.length] }}
                        />
                        <span className="text-sm font-medium text-gray-900">
                          {category.category_name || 'Sans catégorie'}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-semibold text-gray-900">
                      {category.revenue.toLocaleString('fr-FR')} FCFA
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-600">
                      {category.quantity_sold.toLocaleString('fr-FR')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-600">
                      {percentage.toFixed(1)}%
                    </td>
                  </tr>
                );
              })}
              {(!categoryPerformance || categoryPerformance.length === 0) && (
                <tr>
                  <td colSpan={4} className="px-6 py-8 text-center text-gray-500">
                    Aucune donnée disponible pour cette période
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
