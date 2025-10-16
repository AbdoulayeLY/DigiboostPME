/**
 * Carte des Top Produits
 */
import { TrendingUp } from 'lucide-react';
import type { TopProduct } from '@/types/api.types';
import { formatCurrency } from '@/lib/utils';

interface TopProductsCardProps {
  products: TopProduct[];
}

export const TopProductsCard = ({ products }: TopProductsCardProps) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-4">
        <TrendingUp className="w-5 h-5 text-green-600" />
        <h3 className="text-lg font-semibold text-gray-900">
          Top 5 Produits
        </h3>
      </div>

      {products.length === 0 ? (
        <p className="text-sm text-gray-500 text-center py-8">
          Aucune donnee disponible
        </p>
      ) : (
        <div className="space-y-3">
          {products.map((product, index) => (
            <div
              key={product.product_id}
              className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0"
            >
              <div className="flex items-center gap-3 flex-1">
                <div className="flex items-center justify-center w-8 h-8 bg-green-50 text-green-600 rounded-full font-semibold text-sm">
                  {index + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {product.product_name}
                  </p>
                  <p className="text-xs text-gray-500">
                    Code: {product.product_code}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm font-semibold text-gray-900">
                  {formatCurrency(product.total_revenue)}
                </p>
                <p className="text-xs text-gray-500">
                  {product.total_quantity} unites
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TopProductsCard;
