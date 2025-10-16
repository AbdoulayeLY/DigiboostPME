"""
Routes API pour gestion des alertes.
"""
import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant_id, get_db
from app.models.alert import Alert
from app.models.alert_history import AlertHistory
from app.schemas.alert import (
    AlertCreate,
    AlertRead,
    AlertUpdate,
    AlertHistoryRead,
    AlertHistoryFilters
)
from app.services.alert_service import AlertService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=List[AlertRead])
async def list_alerts(
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    is_active: Optional[bool] = Query(None, description="Filtrer par statut actif"),
    alert_type: Optional[str] = Query(None, description="Filtrer par type d'alerte")
):
    """
    Liste toutes les alertes configurées pour le tenant.

    Args:
        tenant_id: UUID du tenant (extrait du JWT)
        db: Session database
        is_active: Filtrer par statut actif (optionnel)
        alert_type: Filtrer par type (LOW_STOCK, RUPTURE_STOCK, etc.)

    Returns:
        Liste des alertes configurées
    """
    logger.info(f"Fetching alerts for tenant {tenant_id}")

    query = db.query(Alert).filter(Alert.tenant_id == tenant_id)

    # Filtres optionnels
    if is_active is not None:
        query = query.filter(Alert.is_active == is_active)

    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)

    alerts = query.order_by(Alert.created_at.desc()).all()

    logger.info(f"Found {len(alerts)} alerts for tenant {tenant_id}")
    return alerts


@router.get("/{alert_id}", response_model=AlertRead)
async def get_alert(
    alert_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Récupérer une alerte spécifique par ID.

    Args:
        alert_id: UUID de l'alerte
        tenant_id: UUID du tenant (extrait du JWT)
        db: Session database

    Returns:
        Détails de l'alerte

    Raises:
        HTTPException 404: Si l'alerte n'existe pas
    """
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.tenant_id == tenant_id
    ).first()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found"
        )

    return alert


@router.post("/", response_model=AlertRead, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertCreate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Créer une nouvelle alerte.

    Args:
        alert_data: Données de l'alerte à créer
        tenant_id: UUID du tenant (extrait du JWT)
        db: Session database

    Returns:
        L'alerte créée

    Raises:
        HTTPException 400: Si les données sont invalides
    """
    logger.info(f"Creating alert for tenant {tenant_id}: {alert_data.name}")

    # Validation 1: Type d'alerte valide
    valid_types = ["RUPTURE_STOCK", "LOW_STOCK", "BAISSE_TAUX_SERVICE"]
    if alert_data.alert_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid alert_type. Must be one of: {', '.join(valid_types)}"
        )

    # Validation 2: Au moins un destinataire configuré
    has_whatsapp = alert_data.recipients.get("whatsapp_numbers") and len(alert_data.recipients["whatsapp_numbers"]) > 0
    has_email = alert_data.recipients.get("emails") and len(alert_data.recipients["emails"]) > 0

    if not has_whatsapp and not has_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one recipient (whatsapp_numbers or emails) is required"
        )

    # Validation 3: Au moins un canal activé
    if not alert_data.channels.get("whatsapp") and not alert_data.channels.get("email"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one channel (whatsapp or email) must be enabled"
        )

    try:
        # Créer l'alerte
        alert = Alert(
            tenant_id=tenant_id,
            name=alert_data.name,
            alert_type=alert_data.alert_type,
            conditions=alert_data.conditions,
            channels=alert_data.channels,
            recipients=alert_data.recipients,
            is_active=alert_data.is_active
        )

        db.add(alert)
        db.commit()
        db.refresh(alert)

        logger.info(f"Alert created successfully: {alert.id}")
        return alert

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating alert: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create alert: {str(e)}"
        )


@router.put("/{alert_id}", response_model=AlertRead)
async def update_alert(
    alert_id: UUID,
    alert_data: AlertUpdate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Modifier une alerte existante.

    Args:
        alert_id: UUID de l'alerte à modifier
        alert_data: Nouvelles données de l'alerte
        tenant_id: UUID du tenant (extrait du JWT)
        db: Session database

    Returns:
        L'alerte modifiée

    Raises:
        HTTPException 404: Si l'alerte n'existe pas
        HTTPException 400: Si les données sont invalides
    """
    logger.info(f"Updating alert {alert_id} for tenant {tenant_id}")

    # Récupérer l'alerte
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.tenant_id == tenant_id
    ).first()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found"
        )

    try:
        # Mettre à jour les champs fournis (update partiel)
        update_data = alert_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(alert, field, value)

        db.commit()
        db.refresh(alert)

        logger.info(f"Alert {alert_id} updated successfully")
        return alert

    except Exception as e:
        db.rollback()
        logger.error(f"Error updating alert: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update alert: {str(e)}"
        )


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Supprimer une alerte.

    Args:
        alert_id: UUID de l'alerte à supprimer
        tenant_id: UUID du tenant (extrait du JWT)
        db: Session database

    Raises:
        HTTPException 404: Si l'alerte n'existe pas
    """
    logger.info(f"Deleting alert {alert_id} for tenant {tenant_id}")

    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.tenant_id == tenant_id
    ).first()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found"
        )

    db.delete(alert)
    db.commit()

    logger.info(f"Alert {alert_id} deleted successfully")


@router.patch("/{alert_id}/toggle", response_model=AlertRead)
async def toggle_alert(
    alert_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Activer/désactiver une alerte (toggle is_active).

    Args:
        alert_id: UUID de l'alerte
        tenant_id: UUID du tenant (extrait du JWT)
        db: Session database

    Returns:
        L'alerte avec le statut modifié

    Raises:
        HTTPException 404: Si l'alerte n'existe pas
    """
    logger.info(f"Toggling alert {alert_id} for tenant {tenant_id}")

    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.tenant_id == tenant_id
    ).first()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found"
        )

    # Inverser le statut is_active
    alert.is_active = not alert.is_active
    db.commit()
    db.refresh(alert)

    logger.info(f"Alert {alert_id} toggled to is_active={alert.is_active}")
    return alert


@router.get("/history/", response_model=List[AlertHistoryRead])
async def get_alert_history(
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    alert_id: Optional[UUID] = Query(None, description="Filtrer par alerte spécifique"),
    alert_type: Optional[str] = Query(None, description="Filtrer par type d'alerte"),
    severity: Optional[str] = Query(None, description="Filtrer par sévérité"),
    limit: int = Query(50, ge=1, le=500, description="Nombre maximum de résultats"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """
    Récupérer l'historique des déclenchements d'alertes.

    Args:
        tenant_id: UUID du tenant (extrait du JWT)
        db: Session database
        alert_id: Filtrer par alerte spécifique (optionnel)
        alert_type: Filtrer par type (optionnel)
        severity: Filtrer par sévérité (optionnel)
        limit: Nombre de résultats max
        offset: Offset pour pagination

    Returns:
        Liste des déclenchements d'alertes
    """
    logger.info(f"Fetching alert history for tenant {tenant_id}")

    query = db.query(AlertHistory).filter(AlertHistory.tenant_id == tenant_id)

    # Filtres optionnels
    if alert_id:
        query = query.filter(AlertHistory.alert_id == alert_id)

    if alert_type:
        query = query.filter(AlertHistory.alert_type == alert_type)

    if severity:
        query = query.filter(AlertHistory.severity == severity)

    # Tri par date décroissante et pagination
    history = query.order_by(
        AlertHistory.triggered_at.desc()
    ).limit(limit).offset(offset).all()

    logger.info(f"Found {len(history)} history entries for tenant {tenant_id}")
    return history


@router.post("/{alert_id}/test", response_model=dict)
async def test_alert(
    alert_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Tester manuellement une alerte (déclencher sans conditions).

    Args:
        alert_id: UUID de l'alerte à tester
        tenant_id: UUID du tenant (extrait du JWT)
        db: Session database

    Returns:
        Résultat du test

    Raises:
        HTTPException 404: Si l'alerte n'existe pas
    """
    logger.info(f"Testing alert {alert_id} for tenant {tenant_id}")

    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.tenant_id == tenant_id
    ).first()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found"
        )

    # Utiliser le service pour créer un historique de test
    service = AlertService(db)

    test_result = {
        "alert_type": alert.alert_type,
        "details": {"test": True, "message": "Test manual de l'alerte"},
        "count": 1
    }

    history = service.create_history_entry(alert, test_result)

    # Envoyer la notification de test
    service.send_alert_notifications(alert, test_result, history)

    return {
        "success": True,
        "alert_id": str(alert.id),
        "alert_name": alert.name,
        "history_id": str(history.id),
        "sent_whatsapp": history.sent_whatsapp,
        "sent_email": history.sent_email
    }
