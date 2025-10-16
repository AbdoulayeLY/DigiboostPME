"""
Router API pour les dashboards.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import DashboardOverviewResponse
from app.models.user import User

router = APIRouter(prefix="/dashboards", tags=["dashboards"])


@router.get("/overview", response_model=DashboardOverviewResponse)
async def get_dashboard_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dashboard Vue d'Ensemble.

    Retourne les KPIs principaux:
    - Sante du stock (total produits, ruptures, stock faible, valorisation)
    - Performance ventes (CA 7j/30j, evolution, nombre ventes)
    - Top 5 produits par CA
    - 5 produits dormants
    - Taux de service

    **Requiert**: Token JWT valide

    **Returns**: JSON avec toutes les donnees du dashboard
    """
    service = DashboardService(db)
    return service.get_overview(current_user.tenant_id)


@router.post("/refresh-views")
async def refresh_dashboard_views(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Rafraichir les vues materialisees du dashboard.

    Utile apres avoir ajoute/modifie beaucoup de donnees.

    **Requiert**: Token JWT valide

    **Returns**: Status du rafraichissement
    """
    service = DashboardService(db)
    return service.refresh_views()
