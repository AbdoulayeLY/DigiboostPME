/**
 * Section Sante Stock du dashboard
 */
import { Package, AlertTriangle, AlertCircle, DollarSign } from 'lucide-react';
import { KPICard } from './KPICard';
import type { StockHealth } from '@/types/api.types';
import { formatCurrency } from '@/lib/utils';

interface StockHealthSectionProps {
  data: StockHealth;
}

export const StockHealthSection = ({ data }: StockHealthSectionProps) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <KPICard
        title="Total Produits"
        value={data.total_products}
        subtitle="Produits actifs"
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
        subtitle="A reapprovisionner"
        icon={<AlertCircle className="w-6 h-6" />}
        color="amber"
      />
      <KPICard
        title="Valorisation"
        value={formatCurrency(data.total_stock_value)}
        subtitle="Valeur stock total"
        icon={<DollarSign className="w-6 h-6" />}
        color="green"
      />
    </div>
  );
};

export default StockHealthSection;
