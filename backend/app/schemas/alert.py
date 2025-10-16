"""
Schémas Pydantic pour les alertes.
"""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# Sous-schémas pour validation stricte
class AlertConditions(BaseModel):
    """Conditions de déclenchement d'une alerte."""
    threshold: Optional[float] = Field(None, description="Seuil de déclenchement")
    product_ids: Optional[List[UUID]] = Field(None, description="IDs produits concernés")
    category_ids: Optional[List[UUID]] = Field(None, description="IDs catégories concernées")


class AlertChannels(BaseModel):
    """Canaux de notification."""
    whatsapp: bool = Field(default=True, description="Notification WhatsApp")
    email: bool = Field(default=False, description="Notification Email")


class AlertRecipients(BaseModel):
    """Destinataires des notifications."""
    whatsapp_numbers: List[str] = Field(default_factory=list, description="Numéros WhatsApp")
    emails: List[str] = Field(default_factory=list, description="Adresses email")

    @field_validator('whatsapp_numbers')
    def validate_phone_numbers(cls, v):
        """Valider format numéros téléphone."""
        for number in v:
            if not number.startswith('+'):
                raise ValueError(f"Numéro {number} doit commencer par +")
        return v


# Schémas principaux Alert
class AlertBase(BaseModel):
    """Schéma de base pour Alert."""
    name: str = Field(..., min_length=3, max_length=255, description="Nom de l'alerte")
    alert_type: str = Field(..., description="Type d'alerte (RUPTURE_STOCK, LOW_STOCK, BAISSE_TAUX_SERVICE)")
    conditions: Dict = Field(default_factory=dict, description="Conditions de déclenchement")
    channels: Dict = Field(default_factory=dict, description="Canaux de notification")
    recipients: Dict = Field(default_factory=dict, description="Destinataires")

    @field_validator('alert_type')
    def validate_alert_type(cls, v):
        """Valider type d'alerte."""
        valid_types = ['RUPTURE_STOCK', 'LOW_STOCK', 'BAISSE_TAUX_SERVICE']
        if v not in valid_types:
            raise ValueError(f"alert_type doit être l'un de: {', '.join(valid_types)}")
        return v


class AlertCreate(AlertBase):
    """Schéma création Alert."""
    is_active: bool = Field(default=True, description="Activer l'alerte à la création")


class AlertUpdate(BaseModel):
    """Schéma mise à jour Alert (tous champs optionnels)."""
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    alert_type: Optional[str] = None
    conditions: Optional[Dict] = None
    channels: Optional[Dict] = None
    recipients: Optional[Dict] = None
    is_active: Optional[bool] = None

    @field_validator('alert_type')
    def validate_alert_type(cls, v):
        """Valider type d'alerte si fourni."""
        if v is not None:
            valid_types = ['RUPTURE_STOCK', 'LOW_STOCK', 'BAISSE_TAUX_SERVICE']
            if v not in valid_types:
                raise ValueError(f"alert_type doit être l'un de: {', '.join(valid_types)}")
        return v


class AlertResponse(AlertBase):
    """Schéma réponse Alert."""
    id: UUID
    tenant_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator('alert_type', mode='before')
    def migrate_alert_type(cls, v):
        """Migrer anciens types d'alerte vers nouveaux types."""
        migration_map = {
            'OUT_OF_STOCK': 'RUPTURE_STOCK',
            'SALES_TARGET': 'BAISSE_TAUX_SERVICE'
        }
        return migration_map.get(v, v)

    @field_validator('channels', mode='before')
    def migrate_channels(cls, v):
        """Migrer ancien format channels (list) vers nouveau format (dict)."""
        if isinstance(v, list):
            # Ancien format: ['whatsapp', 'email']
            return {
                'whatsapp': 'whatsapp' in v,
                'email': 'email' in v
            }
        return v

    @field_validator('recipients', mode='before')
    def migrate_recipients(cls, v):
        """Migrer ancien format recipients (list) vers nouveau format (dict)."""
        if isinstance(v, list):
            # Séparer numéros de téléphone et emails
            whatsapp_numbers = [r for r in v if r.startswith('+')]
            emails = [r for r in v if '@' in r]
            return {
                'whatsapp_numbers': whatsapp_numbers,
                'emails': emails
            }
        return v


class AlertListResponse(BaseModel):
    """Schéma liste d'alertes."""
    alerts: List[AlertResponse]
    total: int


# Schémas AlertHistory
class AlertHistoryBase(BaseModel):
    """Schéma de base pour AlertHistory."""
    alert_type: str
    severity: str
    message: str
    details: Dict = Field(default_factory=dict)


class AlertHistoryResponse(AlertHistoryBase):
    """Schéma réponse AlertHistory."""
    id: UUID
    alert_id: UUID
    tenant_id: UUID
    triggered_at: datetime
    sent_whatsapp: bool
    sent_email: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AlertHistoryListResponse(BaseModel):
    """Schéma liste historique."""
    history: List[AlertHistoryResponse]
    total: int


# Schémas pour statistiques
class AlertStats(BaseModel):
    """Statistiques alertes."""
    total_alerts: int
    active_alerts: int
    inactive_alerts: int
    total_triggered_today: int
    total_triggered_week: int


class AlertHistoryStats(BaseModel):
    """Statistiques historique."""
    total_triggered: int
    sent_whatsapp_count: int
    sent_email_count: int
    by_severity: Dict[str, int]
    by_type: Dict[str, int]


# Alias pour compatibilité API
AlertRead = AlertResponse
AlertHistoryRead = AlertHistoryResponse


# Schéma pour filtres historique
class AlertHistoryFilters(BaseModel):
    """Filtres pour historique alertes."""
    alert_id: Optional[UUID] = None
    alert_type: Optional[str] = None
    severity: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)
