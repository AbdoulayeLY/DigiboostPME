"""
Schémas Pydantic pour les endpoints Analytics.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ============================================================================
# SCHÉMAS POUR ANALYSE PRODUIT
# ============================================================================

class ProductInfoSchema(BaseModel):
    """Informations de base du produit."""
    id: str
    code: str
    name: str
    current_stock: float
    min_stock: float
    max_stock: float
    purchase_price: float
    sale_price: float
    unit: str


class SalesMetrics30DaysSchema(BaseModel):
    """Métriques ventes 30 derniers jours."""
    transactions: int
    quantity: float
    revenue: float
    avg_daily: float


class SalesMetrics90DaysSchema(BaseModel):
    """Métriques ventes 90 derniers jours."""
    transactions: int
    quantity: float
    avg_daily: float


class SalesMetricsSchema(BaseModel):
    """Métriques de ventes pour différentes périodes."""
    last_30_days: SalesMetrics30DaysSchema
    last_90_days: SalesMetrics90DaysSchema


class ProductMetricsSchema(BaseModel):
    """Métriques calculées du produit."""
    coverage_days: Optional[float] = Field(None, description="Couverture stock en jours")
    rotation_annual: Optional[float] = Field(None, description="Rotation stock annuelle")
    margin: float = Field(description="Marge unitaire")
    margin_percent: float = Field(description="Pourcentage de marge")


class ProductAnalysisResponse(BaseModel):
    """Réponse complète analyse produit."""
    product: ProductInfoSchema
    sales: SalesMetricsSchema
    metrics: ProductMetricsSchema
    status: str = Field(description="Statut stock: RUPTURE, FAIBLE, ALERTE, SURSTOCK, NORMAL")


# ============================================================================
# SCHÉMAS POUR ÉVOLUTION VENTES
# ============================================================================

class DailySalesSchema(BaseModel):
    """Ventes d'une journée."""
    date: str = Field(description="Date au format ISO (YYYY-MM-DD)")
    transactions: int
    revenue: float
    units_sold: float


class SalesEvolutionResponse(BaseModel):
    """Réponse évolution ventes."""
    period_days: int
    data: List[DailySalesSchema]


# ============================================================================
# SCHÉMAS POUR TOP PRODUITS
# ============================================================================

class TopProductSchema(BaseModel):
    """Produit dans le top."""
    product_id: str
    code: str
    name: str
    unit: str
    current_stock: float
    category: Optional[str]
    transactions: int
    quantity: float
    revenue: float
    avg_price: float
    coverage_days: Optional[float] = Field(None, description="Couverture stock en jours")
    status: str = Field(description="Statut: RUPTURE, FAIBLE, ALERTE, SURSTOCK, NORMAL")


class TopProductsResponse(BaseModel):
    """Réponse top produits."""
    period_days: int
    order_by: str = Field(description="Critère de tri: revenue, quantity, transactions")
    count: int
    products: List[TopProductSchema]


# ============================================================================
# SCHÉMAS POUR PERFORMANCE CATÉGORIES
# ============================================================================

class CategoryPerformanceSchema(BaseModel):
    """Performance d'une catégorie."""
    category_id: str
    category_name: str
    product_count: int
    transactions: int
    quantity_sold: float
    revenue: float
    avg_price: float


class CategoryPerformanceResponse(BaseModel):
    """Réponse performance catégories."""
    period_days: int
    categories: List[CategoryPerformanceSchema]


# ============================================================================
# SCHÉMAS POUR CLASSIFICATION ABC
# ============================================================================

class ABCClassificationResponse(BaseModel):
    """Réponse classification ABC."""
    period_days: int
    class_a: List[str] = Field(description="Produits classe A (80% CA)")
    class_b: List[str] = Field(description="Produits classe B (15% CA)")
    class_c: List[str] = Field(description="Produits classe C (5% CA)")
    total_products: int
