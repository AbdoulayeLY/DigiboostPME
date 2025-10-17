/**
 * Dashboard Prédictions & Recommandations
 * Conforme au Prompt 3.6 avec TOUS les critères d'acceptation
 */
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { predictionsApi } from '@/api/predictions';
import {
  AlertTriangle,
  Clock,
  TrendingDown,
  Package,
  FileText,
} from 'lucide-react';
import { format, parseISO } from 'date-fns';
import { fr } from 'date-fns/locale';

export const PredictionsDashboard = () => {
  const [horizon, setHorizon] = useState(15);

  // Ruptures prévues
  const { data: rupturesData, isLoading: rupturesLoading } = useQuery({
    queryKey: ['ruptures-prevues', horizon],
    queryFn: () => predictionsApi.getRupturesPrevues(horizon),
    staleTime: 60000, // 1 minute
  });

  // Recommandations achat
  const { data: recommandationsData } = useQuery({
    queryKey: ['recommandations', horizon],
    queryFn: () => predictionsApi.getRecommandations(horizon),
    staleTime: 60000,
  });

  const ruptures = rupturesData?.ruptures || [];
  const recommandations = recommandationsData;

  const getUrgencyColor = (days: number) => {
    if (days <= 3) return 'bg-red-100 text-red-800 border-red-300';
    if (days <= 7) return 'bg-orange-100 text-orange-800 border-orange-300';
    return 'bg-amber-100 text-amber-800 border-amber-300';
  };

  const getUrgencyLabel = (days: number) => {
    if (days <= 3) return 'URGENT';
    if (days <= 7) return 'PRIORITAIRE';
    return 'À SURVEILLER';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold">Prédictions & Recommandations</h1>
          <p className="text-gray-600 mt-1">
            Anticipez les ruptures et optimisez vos commandes
          </p>
        </div>
        <select
          value={horizon}
          onChange={(e) => setHorizon(Number(e.target.value))}
          className="w-48 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option value={7}>7 prochains jours</option>
          <option value={15}>15 prochains jours</option>
          <option value={30}>30 prochains jours</option>
        </select>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Ruptures Prévues</p>
              <p className="text-3xl font-bold mt-2 text-red-600">
                {ruptures?.length || 0}
              </p>
            </div>
            <AlertTriangle className="w-10 h-10 text-red-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Urgentes (≤3j)</p>
              <p className="text-3xl font-bold mt-2 text-red-600">
                {ruptures?.filter((r) => r.days_until_rupture <= 3).length || 0}
              </p>
            </div>
            <Clock className="w-10 h-10 text-red-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Fournisseurs</p>
              <p className="text-3xl font-bold mt-2 text-blue-600">
                {recommandations?.total_suppliers || 0}
              </p>
            </div>
            <Package className="w-10 h-10 text-blue-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Produits à Commander</p>
              <p className="text-3xl font-bold mt-2 text-purple-600">
                {recommandations?.total_products || 0}
              </p>
            </div>
            <TrendingDown className="w-10 h-10 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Ruptures prévues */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-lg font-semibold mb-4">
          Ruptures Prévues ({horizon} jours)
        </h2>
        {rupturesLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          </div>
        ) : ruptures && ruptures.length > 0 ? (
          <div className="space-y-3">
            {ruptures.map((rupture) => (
              <div
                key={rupture.product_id}
                className={`border-l-4 p-4 rounded-lg ${getUrgencyColor(
                  rupture.days_until_rupture
                )}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2 flex-wrap">
                      <span className={`px-2 py-1 rounded text-xs font-semibold border ${getUrgencyColor(rupture.days_until_rupture)}`}>
                        {getUrgencyLabel(rupture.days_until_rupture)}
                      </span>
                      <span className="font-semibold text-lg">
                        {rupture.product_name}
                      </span>
                      <span className="text-sm text-gray-600">
                        ({rupture.product_code})
                      </span>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600">Stock actuel</p>
                        <p className="font-medium">
                          {rupture.current_stock.toFixed(1)}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-600">Rupture prévue</p>
                        <p className="font-medium">
                          {format(parseISO(rupture.predicted_rupture_date), 'dd MMM', {
                            locale: fr,
                          })}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-600">Dans</p>
                        <p className="font-medium text-red-600">
                          {rupture.days_until_rupture} jour{rupture.days_until_rupture > 1 ? 's' : ''}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-600">À commander</p>
                        <p className="font-bold text-green-600">
                          {rupture.recommended_quantity} unités
                        </p>
                      </div>
                    </div>

                    {rupture.supplier && (
                      <div className="mt-3 text-sm">
                        <span className="text-gray-600">Fournisseur: </span>
                        <span className="font-medium">{rupture.supplier.name}</span>
                        <span className="text-gray-500 ml-2">
                          (Délai: {rupture.supplier.lead_time_days}j)
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <AlertTriangle className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <p className="text-lg">Aucune rupture prévue</p>
            <p className="text-sm mt-2">
              Votre stock est bien géré pour les {horizon} prochains jours
            </p>
          </div>
        )}
      </div>

      {/* Recommandations par fournisseur */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Recommandations d'Achat</h2>
          <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            <FileText className="w-4 h-4" />
            Générer Bon de Commande
          </button>
        </div>

        {recommandations?.by_supplier && recommandations.by_supplier.length > 0 ? (
          <div className="space-y-4">
            {recommandations.by_supplier.map((supplier) => (
              <div key={supplier.supplier_id} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="font-semibold text-lg">{supplier.supplier_name}</h3>
                    <p className="text-sm text-gray-600">
                      Délai livraison: {supplier.lead_time_days} jours
                    </p>
                  </div>
                  <span className="px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full text-sm font-medium">
                    {supplier.products.length} produits
                  </span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="text-left p-2">Produit</th>
                        <th className="text-right p-2">Quantité</th>
                        <th className="text-center p-2">Urgence</th>
                      </tr>
                    </thead>
                    <tbody>
                      {supplier.products.map((product) => (
                        <tr key={product.product_id} className="border-t">
                          <td className="p-2">{product.product_name}</td>
                          <td className="text-right p-2 font-medium">
                            {product.quantity}
                          </td>
                          <td className="text-center p-2">
                            <span
                              className={`px-2 py-1 rounded text-xs font-medium ${
                                product.urgency === 'HIGH'
                                  ? 'bg-red-100 text-red-800'
                                  : 'bg-amber-100 text-amber-800'
                              }`}
                            >
                              {product.urgency === 'HIGH' ? 'Urgent' : 'Normal'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            Aucune recommandation d'achat
          </div>
        )}
      </div>
    </div>
  );
};
