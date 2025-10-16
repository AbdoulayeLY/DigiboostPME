"""
Schemas Pydantic pour les dashboards.
"""
from pydantic import BaseModel
from typing import List
from datetime import datetime


class StockHealthResponse(BaseModel):
    """Schema pour la sante du stock."""
    total_products: int
    rupture_count: int
    low_stock_count: int
    alert_count: int
    total_stock_value: float


class SalesPerformanceResponse(BaseModel):
    """Schema pour la performance des ventes."""
    ca_7j: float
    ca_30j: float
    evolution_ca: float
    ventes_7j: int
    ventes_30j: int


class TopProductResponse(BaseModel):
    """Schema pour un produit top/dormant."""
    product_id: str
    product_name: str
    product_code: str
    total_revenue: float = 0.0
    total_quantity: float = 0.0
    current_stock: float = 0.0
    immobilized_value: float = 0.0


class KPIsResponse(BaseModel):
    """Schema pour les KPIs supplementaires."""
    taux_service: float


class DashboardOverviewResponse(BaseModel):
    """Schema pour le dashboard Vue d'Ensemble complet."""
    stock_health: StockHealthResponse
    sales_performance: SalesPerformanceResponse
    top_products: List[TopProductResponse]
    dormant_products: List[TopProductResponse]
    kpis: KPIsResponse
    generated_at: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "stock_health": {
                    "total_products": 50,
                    "rupture_count": 2,
                    "low_stock_count": 5,
                    "alert_count": 7,
                    "total_stock_value": 2500000.0
                },
                "sales_performance": {
                    "ca_7j": 350000.0,
                    "ca_30j": 1500000.0,
                    "evolution_ca": 12.5,
                    "ventes_7j": 45,
                    "ventes_30j": 180
                },
                "top_products": [
                    {
                        "product_id": "uuid",
                        "product_name": "Riz 50kg",
                        "product_code": "RIZ001",
                        "total_revenue": 150000.0,
                        "total_quantity": 50.0
                    }
                ],
                "dormant_products": [],
                "kpis": {
                    "taux_service": 95.5
                },
                "generated_at": "2024-01-01T00:00:00"
            }
        }
    }
