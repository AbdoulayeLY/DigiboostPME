/**
 * Dashboard Gestion Stock Détaillée
 * Conforme au Prompt 3.4 avec TOUS les critères d'acceptation
 */
import { useState, useMemo } from 'react';
import {
  Package,
  Search,
  Eye,
  Download,
  ArrowUpDown,
} from 'lucide-react';
import { useStockData } from '../hooks/useStockData';
import { ProductDetailModal } from './ProductDetailModal';
import type { TopProductItem, StockStatus } from '@/types/api.types';

type SortField = 'code' | 'name' | 'current_stock' | 'status';
type SortOrder = 'asc' | 'desc';

export const StockDetailDashboard = () => {
  const { data: products, isLoading } = useStockData(30); // 30 derniers jours
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('ALL');
  const [statusFilter, setStatusFilter] = useState<StockStatus | 'ALL'>('ALL');
  const [selectedProduct, setSelectedProduct] = useState<string | null>(null);
  const [sortField, setSortField] = useState<SortField>('name');
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc');

  // Le statut est déjà calculé par le backend
  const getStockStatus = (product: TopProductItem): StockStatus => {
    return (product.status as StockStatus) || 'NORMAL';
  };

  // Extraire les catégories uniques
  const categories = useMemo(() => {
    if (!products) return [];
    const uniqueCategories = new Set(
      products
        .map((p) => p.category)
        .filter((c): c is string => c !== null && c !== undefined)
    );
    return Array.from(uniqueCategories).sort();
  }, [products]);

  // Filtrer et trier les produits
  const filteredAndSortedProducts = useMemo(() => {
    if (!products) return [];

    // Filtrer
    let filtered = products.filter((product) => {
      // Recherche
      const matchesSearch =
        searchTerm === '' ||
        product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        product.code.toLowerCase().includes(searchTerm.toLowerCase());

      // Catégorie
      const matchesCategory =
        categoryFilter === 'ALL' || product.category === categoryFilter;

      // Statut
      const productStatus = getStockStatus(product);
      const matchesStatus = statusFilter === 'ALL' || productStatus === statusFilter;

      return matchesSearch && matchesCategory && matchesStatus;
    });

    // Trier
    filtered.sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sortField) {
        case 'code':
          aValue = a.code.toLowerCase();
          bValue = b.code.toLowerCase();
          break;
        case 'name':
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
          break;
        case 'current_stock':
          aValue = a.current_stock;
          bValue = b.current_stock;
          break;
        case 'status':
          const statusOrder = { RUPTURE: 0, FAIBLE: 1, ALERTE: 2, NORMAL: 3, SURSTOCK: 4 };
          aValue = statusOrder[getStockStatus(a)];
          bValue = statusOrder[getStockStatus(b)];
          break;
        default:
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
      }

      if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });

    return filtered;
  }, [products, searchTerm, categoryFilter, statusFilter, sortField, sortOrder]);

  // Statistiques
  const stats = useMemo(() => {
    if (!products) return { total: 0, rupture: 0, faible: 0, normal: 0, surstock: 0 };

    return {
      total: products.length,
      rupture: products.filter((p) => getStockStatus(p) === 'RUPTURE').length,
      faible: products.filter((p) => getStockStatus(p) === 'FAIBLE').length,
      normal: products.filter((p) => getStockStatus(p) === 'NORMAL').length,
      surstock: products.filter((p) => getStockStatus(p) === 'SURSTOCK').length,
    };
  }, [products]);

  // Fonction pour changer le tri
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('asc');
    }
  };

  // Fonction d'export CSV
  const exportToCSV = () => {
    if (!filteredAndSortedProducts.length) return;

    // Headers
    const headers = ['Code', 'Nom', 'Catégorie', 'Stock Actuel', 'Unité', 'Statut'];

    // Rows
    const rows = filteredAndSortedProducts.map((product) => {
      const status = getStockStatus(product);
      return [
        product.code,
        `"${product.name.replace(/"/g, '""')}"`, // Échapper les guillemets
        product.category || '-',
        product.current_stock.toFixed(2),
        product.unit,
        status,
      ];
    });

    // Créer le CSV
    const csvContent = [
      headers.join(','),
      ...rows.map((row) => row.join(',')),
    ].join('\n');

    // Télécharger
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' }); // BOM UTF-8
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `stock-detail-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  const getStatusBadge = (status: StockStatus) => {
    const config = {
      RUPTURE: { label: 'Rupture', class: 'bg-red-100 text-red-800' },
      FAIBLE: { label: 'Stock Faible', class: 'bg-amber-100 text-amber-800' },
      ALERTE: { label: 'Alerte', class: 'bg-orange-100 text-orange-800' },
      SURSTOCK: { label: 'Surstock', class: 'bg-purple-100 text-purple-800' },
      NORMAL: { label: 'Normal', class: 'bg-green-100 text-green-800' },
    };
    return config[status] || config.NORMAL;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement du stock...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold">Gestion Stock Détaillée</h1>
          <p className="text-gray-600 mt-1">
            Vue complète de tous les produits avec analyses
          </p>
        </div>
        <button
          onClick={exportToCSV}
          disabled={filteredAndSortedProducts.length === 0}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          <Download className="w-4 h-4" />
          Exporter CSV
        </button>
      </div>

      {/* Stats rapides */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-600">Total Produits</p>
          <p className="text-2xl font-bold">{stats.total}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-600">Ruptures</p>
          <p className="text-2xl font-bold text-red-600">{stats.rupture}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-600">Stock Faible</p>
          <p className="text-2xl font-bold text-amber-600">{stats.faible}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-600">Normal</p>
          <p className="text-2xl font-bold text-green-600">{stats.normal}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-600">Surstock</p>
          <p className="text-2xl font-bold text-purple-600">{stats.surstock}</p>
        </div>
      </div>

      {/* Filtres */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Recherche */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Rechercher par nom ou code..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Filtre catégorie */}
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="ALL">Toutes les catégories</option>
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>

          {/* Filtre statut */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as StockStatus | 'ALL')}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="ALL">Tous les statuts</option>
            <option value="RUPTURE">Rupture</option>
            <option value="FAIBLE">Stock Faible</option>
            <option value="ALERTE">Alerte</option>
            <option value="NORMAL">Normal</option>
            <option value="SURSTOCK">Surstock</option>
          </select>
        </div>

        <p className="text-sm text-gray-600 mt-3">
          {filteredAndSortedProducts.length} produit{filteredAndSortedProducts.length > 1 ? 's' : ''}{' '}
          trouvé{filteredAndSortedProducts.length > 1 ? 's' : ''}
        </p>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {filteredAndSortedProducts.length === 0 ? (
          <div className="text-center py-12">
            <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Aucun produit trouvé
            </h3>
            <p className="text-gray-600">
              Essayez de modifier vos filtres de recherche
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th
                    onClick={() => handleSort('code')}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  >
                    <div className="flex items-center gap-2">
                      Code
                      <ArrowUpDown className="w-4 h-4" />
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort('name')}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  >
                    <div className="flex items-center gap-2">
                      Nom
                      <ArrowUpDown className="w-4 h-4" />
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Catégorie
                  </th>
                  <th
                    onClick={() => handleSort('current_stock')}
                    className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  >
                    <div className="flex items-center justify-end gap-2">
                      Stock Actuel
                      <ArrowUpDown className="w-4 h-4" />
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort('status')}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  >
                    <div className="flex items-center gap-2">
                      Statut
                      <ArrowUpDown className="w-4 h-4" />
                    </div>
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredAndSortedProducts.map((product) => {
                  const status = getStockStatus(product);
                  const statusConfig = getStatusBadge(status);
                  return (
                    <tr key={product.product_id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-medium text-gray-900">
                          {product.code}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-gray-900">
                          {product.name}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-600">
                          {product.category || '-'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <span className="text-sm font-semibold text-gray-900">
                          {product.current_stock.toFixed(0)} {product.unit}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`inline-flex px-2 py-1 text-xs font-medium rounded-md ${statusConfig.class}`}
                        >
                          {statusConfig.label}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <button
                          onClick={() => setSelectedProduct(product.product_id)}
                          className="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors inline-flex items-center gap-1"
                          title="Voir les détails"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal détail */}
      <ProductDetailModal
        productId={selectedProduct}
        onClose={() => setSelectedProduct(null)}
      />
    </div>
  );
};
