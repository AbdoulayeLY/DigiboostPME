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
}

export interface RefreshTokenRequest {
  refresh_token: string;
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
