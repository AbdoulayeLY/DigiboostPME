"""
Routes API pour Analytics - Analyses avancées et KPIs.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_current_tenant_id
from app.db.session import get_db
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    ProductAnalysisResponse,
    SalesEvolutionResponse,
    TopProductsResponse,
    CategoryPerformanceResponse,
    ABCClassificationResponse
)

router = APIRouter()


@router.get(
    "/sales/evolution",
    response_model=SalesEvolutionResponse,
    summary="Évolution des ventes quotidiennes",
    description="""
    Retourne l'évolution quotidienne des ventes sur une période donnée.
    Utile pour créer des graphiques de tendance.
    """
)
async def get_sales_evolution(
    days: int = Query(30, ge=1, le=365, description="Nombre de jours à analyser"),
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Récupérer l'évolution quotidienne des ventes."""
    service = AnalyticsService(db)
    evolution = service.get_sales_evolution(tenant_id, days=days)

    return {
        "period_days": days,
        "data": evolution
    }


@router.get(
    "/products/top",
    response_model=TopProductsResponse,
    summary="Top produits",
    description="""
    Liste des meilleurs produits selon un critère de tri :
    - revenue : Par chiffre d'affaires (défaut)
    - quantity : Par quantité vendue
    - transactions : Par nombre de transactions

    Note: Pour récupérer tous les produits, utilisez limit=1000 ou plus.
    """
)
async def get_top_products(
    limit: int = Query(10, ge=1, le=10000, description="Nombre de produits à retourner"),
    days: int = Query(30, ge=1, le=365, description="Période d'analyse en jours"),
    order_by: str = Query(
        "revenue",
        regex="^(revenue|quantity|transactions)$",
        description="Critère de tri"
    ),
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Récupérer le top des produits."""
    service = AnalyticsService(db)
    products = service.get_top_products(
        tenant_id,
        limit=limit,
        days=days,
        order_by=order_by
    )

    return {
        "period_days": days,
        "order_by": order_by,
        "count": len(products),
        "products": products
    }


@router.get(
    "/categories/performance",
    response_model=CategoryPerformanceResponse,
    summary="Performance par catégorie",
    description="""
    Statistiques de vente par catégorie de produits :
    - Nombre de produits
    - Transactions
    - Quantité vendue
    - Chiffre d'affaires
    """
)
async def get_category_performance(
    days: int = Query(30, ge=1, le=365, description="Période d'analyse en jours"),
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Récupérer la performance par catégorie."""
    service = AnalyticsService(db)
    categories = service.get_category_performance(tenant_id, days=days)

    return {
        "period_days": days,
        "categories": categories
    }


@router.get(
    "/products/abc",
    response_model=ABCClassificationResponse,
    summary="Classification ABC des produits",
    description="""
    Classification ABC selon la méthode Pareto :
    - Classe A : 80% du CA (produits stratégiques)
    - Classe B : 15% du CA (produits intermédiaires)
    - Classe C : 5% du CA (produits faible rotation)

    Permet de prioriser la gestion des stocks.
    """
)
async def get_abc_classification(
    days: int = Query(90, ge=30, le=365, description="Période d'analyse en jours"),
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Récupérer la classification ABC des produits."""
    service = AnalyticsService(db)
    classification = service.classify_products_abc(tenant_id, days=days)

    total_products = (
        len(classification["A"]) +
        len(classification["B"]) +
        len(classification["C"])
    )

    return {
        "period_days": days,
        "class_a": classification["A"],
        "class_b": classification["B"],
        "class_c": classification["C"],
        "total_products": total_products
    }


@router.get(
    "/products/{product_id}",
    response_model=ProductAnalysisResponse,
    summary="Analyse détaillée d'un produit",
    description="""
    Analyse complète d'un produit incluant :
    - Stock actuel et seuils
    - Ventes 30/90 derniers jours
    - Métriques (couverture, rotation, marge)
    - Statut stock
    """
)
async def get_product_analysis(
    product_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Récupérer l'analyse détaillée d'un produit."""
    service = AnalyticsService(db)
    analysis = service.get_product_analysis(tenant_id, product_id)

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=f"Produit {product_id} non trouvé"
        )

    return analysis
