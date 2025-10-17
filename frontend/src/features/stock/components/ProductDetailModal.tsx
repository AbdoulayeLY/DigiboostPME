/**
 * Modal d'affichage des détails d'un produit
 */
import { X, Package, TrendingUp, TrendingDown, DollarSign, Calendar, AlertCircle } from 'lucide-react';
import { useProductAnalysis } from '../hooks/useStockData';
import type { StockStatus } from '@/types/api.types';

interface ProductDetailModalProps {
  productId: string | null;
  onClose: () => void;
}

export const ProductDetailModal = ({ productId, onClose }: ProductDetailModalProps) => {
  const { data: analysis, isLoading } = useProductAnalysis(productId);

  if (!productId) return null;

  const getStatusBadgeClass = (status: StockStatus): string => {
    const classes: Record<StockStatus, string> = {
      RUPTURE: 'bg-red-100 text-red-800 border-red-200',
      FAIBLE: 'bg-orange-100 text-orange-800 border-orange-200',
      ALERTE: 'bg-amber-100 text-amber-800 border-amber-200',
      SURSTOCK: 'bg-purple-100 text-purple-800 border-purple-200',
      NORMAL: 'bg-green-100 text-green-800 border-green-200',
    };
    return classes[status];
  };

  const getStatusLabel = (status: StockStatus): string => {
    const labels: Record<StockStatus, string> = {
      RUPTURE: 'Rupture de stock',
      FAIBLE: 'Stock faible',
      ALERTE: 'Stock en alerte',
      SURSTOCK: 'Surstock',
      NORMAL: 'Stock normal',
    };
    return labels[status];
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 overflow-y-auto">
        <div className="flex min-h-full items-center justify-center p-4">
          <div className="relative w-full max-w-4xl bg-white rounded-xl shadow-xl">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h2 className="text-2xl font-bold text-gray-900">
                Détails du produit
              </h2>
              <button
                onClick={onClose}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6">
              {isLoading ? (
                <div className="flex items-center justify-center h-64">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Chargement des détails...</p>
                  </div>
                </div>
              ) : analysis ? (
                <div className="space-y-6">
                  {/* Informations générales */}
                  <div className="bg-gray-50 p-6 rounded-lg">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="text-xl font-bold text-gray-900 mb-2">
                          {analysis.product.name}
                        </h3>
                        <p className="text-sm text-gray-600">
                          Code: <span className="font-medium">{analysis.product.code}</span>
                        </p>
                        {analysis.product.category && (
                          <p className="text-sm text-gray-600">
                            Catégorie:{' '}
                            <span className="font-medium">{analysis.product.category}</span>
                          </p>
                        )}
                      </div>
                      <span
                        className={`inline-flex px-3 py-1 text-sm font-medium rounded-md border ${getStatusBadgeClass(
                          analysis.status
                        )}`}
                      >
                        {getStatusLabel(analysis.status)}
                      </span>
                    </div>

                    {analysis.status !== 'NORMAL' && (
                      <div className="flex items-start gap-2 mt-4 p-4 bg-amber-50 border border-amber-200 rounded-lg">
                        <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                        <div className="text-sm text-amber-900">
                          <p className="font-medium mb-1">Attention</p>
                          <p>
                            {analysis.status === 'RUPTURE' &&
                              'Ce produit est en rupture de stock. Réapprovisionnement urgent nécessaire.'}
                            {analysis.status === 'FAIBLE' &&
                              'Le stock de ce produit est faible. Envisagez de réapprovisionner prochainement.'}
                            {analysis.status === 'ALERTE' &&
                              'Le stock de ce produit approche du seuil minimum.'}
                            {analysis.status === 'SURSTOCK' &&
                              'Ce produit est en surstock. Vérifiez les prévisions de vente.'}
                          </p>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Grille de métriques */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {/* Stock actuel */}
                    <div className="bg-white p-4 rounded-lg border border-gray-200">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="bg-blue-100 p-2 rounded-lg">
                          <Package className="w-5 h-5 text-blue-600" />
                        </div>
                        <p className="text-sm text-gray-600 font-medium">Stock actuel</p>
                      </div>
                      <p className="text-2xl font-bold text-gray-900">
                        {analysis.product.current_stock?.toFixed(0) ?? '0'}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">{analysis.product.unit ?? 'unité'}</p>
                    </div>

                    {/* Seuil minimum */}
                    <div className="bg-white p-4 rounded-lg border border-gray-200">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="bg-orange-100 p-2 rounded-lg">
                          <TrendingDown className="w-5 h-5 text-orange-600" />
                        </div>
                        <p className="text-sm text-gray-600 font-medium">Seuil minimum</p>
                      </div>
                      <p className="text-2xl font-bold text-gray-900">
                        {analysis.product.minimum_stock?.toFixed(0) ?? 'N/A'}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">{analysis.product.unit}</p>
                    </div>

                    {/* Couverture */}
                    <div className="bg-white p-4 rounded-lg border border-gray-200">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="bg-purple-100 p-2 rounded-lg">
                          <Calendar className="w-5 h-5 text-purple-600" />
                        </div>
                        <p className="text-sm text-gray-600 font-medium">Couverture</p>
                      </div>
                      <p className="text-2xl font-bold text-gray-900">
                        {analysis.metrics.coverage_days !== null
                          ? `${analysis.metrics.coverage_days.toFixed(0)}`
                          : 'N/A'}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">jours</p>
                    </div>

                    {/* Marge */}
                    <div className="bg-white p-4 rounded-lg border border-gray-200">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="bg-green-100 p-2 rounded-lg">
                          <DollarSign className="w-5 h-5 text-green-600" />
                        </div>
                        <p className="text-sm text-gray-600 font-medium">Marge</p>
                      </div>
                      <p className="text-2xl font-bold text-gray-900">
                        {analysis.metrics.margin_percent?.toFixed(1) ?? '0.0'}%
                      </p>
                      <p className="text-xs text-gray-500 mt-1">brute</p>
                    </div>
                  </div>

                  {/* Ventes et performance */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Ventes 30 jours */}
                    <div className="bg-white p-6 rounded-lg border border-gray-200">
                      <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-blue-600" />
                        Ventes - 30 derniers jours
                      </h4>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Quantité vendue</span>
                          <span className="text-lg font-semibold text-gray-900">
                            {analysis.sales.last_30_days.quantity?.toFixed(0) ?? '0'} {analysis.product.unit ?? 'unité'}
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Chiffre d'affaires</span>
                          <span className="text-lg font-semibold text-gray-900">
                            {(analysis.sales.last_30_days.revenue ?? 0).toLocaleString('fr-FR', {
                              minimumFractionDigits: 0,
                              maximumFractionDigits: 0,
                            })}{' '}
                            FCFA
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Transactions</span>
                          <span className="text-lg font-semibold text-gray-900">
                            {analysis.sales.last_30_days.transactions ?? 0}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Ventes 90 jours */}
                    <div className="bg-white p-6 rounded-lg border border-gray-200">
                      <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-green-600" />
                        Ventes - 90 derniers jours
                      </h4>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Quantité vendue</span>
                          <span className="text-lg font-semibold text-gray-900">
                            {analysis.sales.last_90_days.quantity?.toFixed(0) ?? '0'} {analysis.product.unit ?? 'unité'}
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Chiffre d'affaires</span>
                          <span className="text-lg font-semibold text-gray-900">
                            {(analysis.sales.last_90_days.revenue ?? 0).toLocaleString('fr-FR', {
                              minimumFractionDigits: 0,
                              maximumFractionDigits: 0,
                            })}{' '}
                            FCFA
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Transactions</span>
                          <span className="text-lg font-semibold text-gray-900">
                            {analysis.sales.last_90_days.transactions ?? 0}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Informations commerciales */}
                  <div className="bg-white p-6 rounded-lg border border-gray-200">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4">
                      Informations commerciales
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <p className="text-sm text-gray-600 mb-1">Prix d'achat</p>
                        <p className="text-lg font-semibold text-gray-900">
                          {(analysis.product.purchase_price ?? 0).toLocaleString('fr-FR')} FCFA
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 mb-1">Prix de vente</p>
                        <p className="text-lg font-semibold text-gray-900">
                          {(analysis.product.sale_price ?? 0).toLocaleString('fr-FR')} FCFA
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 mb-1">Fournisseur</p>
                        <p className="text-lg font-semibold text-gray-900">
                          {analysis.product.supplier_name || 'Non défini'}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Rotation */}
                  {analysis.metrics.rotation_annual !== null && (
                    <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                      <div className="flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-blue-600" />
                        <span className="text-sm font-medium text-blue-900">
                          Rotation annuelle:{' '}
                          <span className="text-lg">
                            {analysis.metrics.rotation_annual.toFixed(2)} fois/an
                          </span>
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12">
                  <AlertCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-600">Impossible de charger les détails du produit</p>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="flex justify-end gap-3 p-6 border-t border-gray-200">
              <button
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Fermer
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
