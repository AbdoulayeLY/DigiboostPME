/**
 * Types pour l'API backend
 */

// Auth types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  must_change_password?: boolean;
  temp_token?: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface ChangePasswordFirstLoginRequest {
  old_password: string;
  new_password: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
  whatsapp_number: string | null;
  is_active: boolean;
  tenant_id: string;
  created_at: string;
  updated_at: string;
}

// Dashboard types
export interface StockHealth {
  total_products: number;
  rupture_count: number;
  low_stock_count: number;
  alert_count: number;
  total_stock_value: number;
}

export interface SalesPerformance {
  ca_7j: number;
  ca_30j: number;
  evolution_ca: number;
  ventes_7j: number;
  ventes_30j: number;
}

export interface TopProduct {
  product_id: string;
  product_name: string;
  product_code: string;
  total_revenue: number;
  total_quantity: number;
  current_stock: number;
  immobilized_value: number;
}

export interface KPIs {
  taux_service: number;
}

export interface DashboardOverview {
  stock_health: StockHealth;
  sales_performance: SalesPerformance;
  top_products: TopProduct[];
  dormant_products: TopProduct[];
  kpis: KPIs;
  generated_at: string;
}

// API Response wrapper
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}

// API Error
export interface ApiError {
  detail: string;
  status: number;
}

// Analytics types
export interface ProductInfo {
  id: string;
  name: string;
  code: string;
  category: string | null;
  current_stock: number;
  unit: string;
  minimum_stock: number;
  maximum_stock: number;
  purchase_price: number;
  sale_price: number;
  supplier_name: string | null;
}

export interface SalesPeriod {
  quantity: number;
  revenue: number;
  transactions: number;
}

export interface SalesMetrics {
  last_30_days: SalesPeriod;
  last_90_days: SalesPeriod;
}

export interface ProductMetrics {
  coverage_days: number | null;
  rotation_annual: number | null;
  margin_percent: number;
}

export type StockStatus = 'RUPTURE' | 'FAIBLE' | 'ALERTE' | 'SURSTOCK' | 'NORMAL';

export interface ProductAnalysis {
  product: ProductInfo;
  sales: SalesMetrics;
  metrics: ProductMetrics;
  status: StockStatus;
}

export interface DailySales {
  date: string;
  transactions: number;
  revenue: number;
  units_sold: number;
}

export interface SalesEvolution {
  period_days: number;
  data: DailySales[];
}

export interface TopProductItem {
  product_id: string;
  name: string;
  code: string;
  category: string | null;
  quantity: number;
  revenue: number;
  transactions: number;
  current_stock: number;
  avg_price: number;
  coverage_days: number | null;
  status: StockStatus;
  unit: string;
}

export interface TopProductsResponse {
  period_days: number;
  order_by: string;
  count: number;
  products: TopProductItem[];
}

export interface CategoryPerformance {
  category_name: string;
  product_count: number;
  transactions: number;
  quantity_sold: number;
  revenue: number;
  avg_price: number;
}

export interface CategoryPerformanceResponse {
  period_days: number;
  categories: CategoryPerformance[];
}

export interface ABCProduct {
  product_id: string;
  product_name: string;
  revenue: number;
  cumulative_percent: number;
}

export interface ABCClassification {
  period_days: number;
  class_a: ABCProduct[];
  class_b: ABCProduct[];
  class_c: ABCProduct[];
  total_products: number;
}

// Predictions types
export interface SupplierInfo {
  id: string;
  name: string;
  lead_time_days: number;
}

export interface RupturePrevue {
  product_id: string;
  product_code: string;
  product_name: string;
  current_stock: number;
  min_stock: number;
  predicted_rupture_date: string;
  days_until_rupture: number;
  recommended_quantity: number;
  supplier: SupplierInfo | null;
}

export interface RupturesPrevuesResponse {
  horizon_days: number;
  count: number;
  ruptures: RupturePrevue[];
}

export interface RecommandationProduct {
  product_id: string;
  product_name: string;
  quantity: number;
  urgency: 'HIGH' | 'MEDIUM';
}

export interface RecommandationSupplier {
  supplier_id: string;
  supplier_name: string;
  lead_time_days: number;
  products: RecommandationProduct[];
}

export interface RecommandationsAchatResponse {
  horizon_days: number;
  by_supplier: RecommandationSupplier[];
  without_supplier: RupturePrevue[];
  total_products: number;
  total_suppliers: number;
}
