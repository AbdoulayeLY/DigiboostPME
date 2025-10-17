"""
Routes API pour Prédictions - Anticipation ruptures et recommandations d'achat.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_current_tenant_id
from app.db.session import get_db
from app.services.prediction_service import PredictionService
from app.schemas.prediction import (
    RupturesPrevuesResponse,
    RecommandationsAchatResponse
)

router = APIRouter()


@router.get(
    "/ruptures",
    response_model=RupturesPrevuesResponse,
    summary="Ruptures de stock prévues",
    description="""
    Liste des produits dont la rupture de stock est prévue dans les X prochains jours.

    La prédiction est basée sur :
    - Stock actuel
    - Ventes moyennes quotidiennes (30 derniers jours)

    Les résultats sont triés par urgence (date de rupture la plus proche en premier).
    """
)
async def get_ruptures_prevues(
    horizon_days: int = Query(
        15,
        ge=1,
        le=30,
        description="Horizon de prédiction en jours"
    ),
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Récupérer la liste des ruptures de stock prévues."""
    service = PredictionService(db)
    ruptures = service.get_ruptures_prevues(tenant_id, horizon_days=horizon_days)

    return {
        "horizon_days": horizon_days,
        "count": len(ruptures),
        "ruptures": ruptures
    }


@router.get(
    "/recommandations",
    response_model=RecommandationsAchatResponse,
    summary="Recommandations d'achat",
    description="""
    Recommandations d'achat groupées par fournisseur.

    Facilite la création de bons de commande en regroupant les produits
    à commander par fournisseur, avec les quantités recommandées et le niveau d'urgence.

    **Niveaux d'urgence** :
    - HIGH : Rupture dans moins de 7 jours
    - MEDIUM : Rupture entre 7 et 15 jours

    Les produits sans fournisseur défini sont listés séparément.
    """
)
async def get_recommandations_achat(
    horizon_days: int = Query(
        15,
        ge=1,
        le=30,
        description="Horizon de prédiction en jours"
    ),
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Récupérer les recommandations d'achat groupées par fournisseur."""
    service = PredictionService(db)
    recommandations = service.get_recommandations_achat(
        tenant_id,
        horizon_days=horizon_days
    )

    return {
        "horizon_days": horizon_days,
        **recommandations
    }
