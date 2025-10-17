"""
Schémas Pydantic pour les endpoints Prédictions.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


# ============================================================================
# SCHÉMAS POUR RUPTURES PRÉVUES
# ============================================================================

class SupplierInfoSchema(BaseModel):
    """Informations du fournisseur."""
    id: str
    name: str
    lead_time_days: int = Field(description="Délai de livraison en jours")


class RupturePrevueSchema(BaseModel):
    """Une rupture prévue."""
    product_id: str
    product_code: str
    product_name: str
    current_stock: float
    min_stock: float
    predicted_rupture_date: str = Field(description="Date prévue au format ISO")
    days_until_rupture: int = Field(description="Nombre de jours avant rupture")
    recommended_quantity: float = Field(description="Quantité recommandée à commander")
    supplier: Optional[SupplierInfoSchema] = None


class RupturesPrevuesResponse(BaseModel):
    """Réponse liste ruptures prévues."""
    horizon_days: int = Field(description="Horizon de prédiction en jours")
    count: int = Field(description="Nombre de produits en alerte")
    ruptures: List[RupturePrevueSchema]


# ============================================================================
# SCHÉMAS POUR RECOMMANDATIONS D'ACHAT
# ============================================================================

class ProductRecommendationSchema(BaseModel):
    """Produit à commander."""
    product_id: str
    product_code: str
    product_name: str
    quantity: float
    urgency: str = Field(description="Niveau d'urgence: HIGH, MEDIUM, LOW")
    days_until_rupture: int


class SupplierOrderSchema(BaseModel):
    """Commande groupée par fournisseur."""
    supplier_id: str
    supplier_name: str
    lead_time_days: int
    products: List[ProductRecommendationSchema]


class RecommandationsAchatResponse(BaseModel):
    """Réponse recommandations d'achat."""
    horizon_days: int
    total_products: int = Field(description="Total produits à commander")
    total_suppliers: int = Field(description="Nombre de fournisseurs concernés")
    by_supplier: List[SupplierOrderSchema] = Field(description="Commandes groupées par fournisseur")
    without_supplier: List[RupturePrevueSchema] = Field(description="Produits sans fournisseur défini")
