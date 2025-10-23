"""
Schemas Pydantic pour API Onboarding Admin.
"""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator


# ============================================================
# SCHEMAS CRÉATION TENANT (Étape 1)
# ============================================================

class CreateTenantAdmin(BaseModel):
    """Schema pour création tenant par admin."""

    name: str = Field(..., min_length=2, max_length=255, description="Nom de l'entreprise")
    ninea: Optional[str] = Field(None, max_length=50, description="Numéro NINEA (Sénégal)")
    sector: Optional[str] = Field(None, max_length=50, description="Secteur d'activité")
    country: str = Field(default="SN", max_length=2, description="Code pays ISO")
    email: EmailStr = Field(..., description="Email de contact du tenant")
    phone: Optional[str] = Field(None, max_length=20, description="Téléphone de contact")

    # Informations site principal
    site_name: str = Field(..., min_length=2, max_length=255, description="Nom du site principal")
    site_address: Optional[str] = Field(None, description="Adresse du site")

    # Metadata onboarding
    created_by: str = Field(default="wizard", max_length=100, description="Source de création")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Épicerie Dakar",
                "ninea": "123456789",
                "sector": "Commerce de détail",
                "country": "SN",
                "email": "contact@epicerie-dakar.sn",
                "phone": "+221771234567",
                "site_name": "Magasin Principal",
                "site_address": "Rue 10, Dakar, Sénégal",
                "created_by": "wizard"
            }
        }


class TenantCreationResponse(BaseModel):
    """Réponse après création tenant."""

    tenant_id: UUID
    site_id: UUID
    session_id: UUID
    tenant_name: str
    site_name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# SCHEMAS CRÉATION USERS (Étape 2)
# ============================================================

class CreateUserAdmin(BaseModel):
    """Schema pour création user par admin."""

    email: Optional[EmailStr] = Field(None, description="Email (optionnel si phone fourni)")
    phone: Optional[str] = Field(None, max_length=20, description="Téléphone (optionnel si email fourni)")
    first_name: str = Field(..., min_length=1, max_length=100, description="Prénom")
    last_name: str = Field(..., min_length=1, max_length=100, description="Nom de famille")
    role: str = Field(default="user", max_length=50, description="Rôle: admin, user, viewer")
    whatsapp_number: Optional[str] = Field(None, max_length=20, description="Numéro WhatsApp pour alertes")
    default_password: str = Field(..., min_length=8, description="Mot de passe par défaut")
    must_change_password: bool = Field(default=True, description="Forcer changement MDP 1ère connexion")

    @validator('email', 'phone')
    def check_identifier(cls, v, values):
        """Au moins un identifiant (email ou phone) doit être fourni."""
        if 'email' in values and not values.get('email') and not v:
            raise ValueError("Au moins un identifiant (email ou phone) est requis")
        return v

    @validator('role')
    def validate_role(cls, v):
        """Valider le rôle."""
        allowed_roles = ['admin', 'user', 'viewer']
        if v not in allowed_roles:
            raise ValueError(f"Rôle invalide. Autorisés: {', '.join(allowed_roles)}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "manager@epicerie-dakar.sn",
                "phone": "+221771234567",
                "first_name": "Moussa",
                "last_name": "Diop",
                "role": "admin",
                "whatsapp_number": "+221771234567",
                "default_password": "Digiboost2025",
                "must_change_password": True
            }
        }


class CreateUsersRequest(BaseModel):
    """Requête création multiple users."""

    tenant_id: UUID
    users: List[CreateUserAdmin] = Field(..., min_items=1, max_items=10, description="Liste des users à créer")

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "5864d4f2-8d38-44d1-baad-1caa8f5495bd",
                "users": [
                    {
                        "email": "manager@epicerie-dakar.sn",
                        "phone": "+221771234567",
                        "first_name": "Moussa",
                        "last_name": "Diop",
                        "role": "admin",
                        "whatsapp_number": "+221771234567",
                        "default_password": "Digiboost2025",
                        "must_change_password": True
                    }
                ]
            }
        }


class UserCreationResponse(BaseModel):
    """Réponse après création user."""

    user_id: UUID
    email: Optional[str]
    phone: Optional[str]
    first_name: str
    last_name: str
    role: str
    must_change_password: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UsersCreationResponse(BaseModel):
    """Réponse après création multiple users."""

    tenant_id: UUID
    users_created: List[UserCreationResponse]
    count: int


# ============================================================
# SCHEMAS GÉNÉRATION TEMPLATE (Étape 3)
# ============================================================

class GenerateTemplateRequest(BaseModel):
    """Requête génération template Excel."""

    tenant_id: UUID
    include_categories: bool = Field(default=True, description="Inclure onglet catégories")
    include_suppliers: bool = Field(default=True, description="Inclure onglet fournisseurs")
    sample_data: bool = Field(default=True, description="Inclure lignes d'exemple")


# ============================================================
# SCHEMAS IMPORT DONNÉES (Étape 4)
# ============================================================

class ImportStatusResponse(BaseModel):
    """Réponse statut import."""

    job_id: UUID
    tenant_id: UUID
    status: str  # pending, running, success, failed
    progress_percent: int
    file_name: Optional[str]
    stats: Dict = Field(default_factory=dict)  # products_imported, sales_imported, etc.
    error_details: Optional[Dict] = None
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ImportJobResponse(BaseModel):
    """Réponse après déclenchement import."""

    job_id: UUID
    celery_task_id: str
    tenant_id: UUID
    status: str
    message: str


# ============================================================
# SCHEMAS SESSION ONBOARDING
# ============================================================

class OnboardingSessionSchema(BaseModel):
    """Schema session onboarding."""

    id: UUID
    tenant_id: UUID
    status: str  # in_progress, completed, failed
    current_step: int
    data: Dict = Field(default_factory=dict)
    created_by: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]

    class Config:
        from_attributes = True


class OnboardingSessionUpdateRequest(BaseModel):
    """Requête mise à jour session."""

    current_step: Optional[int] = Field(None, ge=1, le=4)
    status: Optional[str] = Field(None, pattern="^(in_progress|completed|failed)$")
    data: Optional[Dict] = None
    error_message: Optional[str] = None


# ============================================================
# SCHEMAS AUDIT
# ============================================================

class AdminAuditLogSchema(BaseModel):
    """Schema log d'audit admin."""

    id: int
    admin_user_id: Optional[UUID]
    action_type: str
    entity_type: Optional[str]
    entity_id: Optional[UUID]
    details: Dict = Field(default_factory=dict)
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
