"""
Schemas Pydantic pour les utilisateurs.
"""
from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Schema de base pour User."""
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "user"
    whatsapp_number: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Schema pour creer un utilisateur."""
    password: str
    tenant_id: UUID


class UserUpdate(BaseModel):
    """Schema pour mettre a jour un utilisateur."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    whatsapp_number: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    """Schema pour la reponse utilisateur."""
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "admin@digiboost.sn",
                "full_name": "Amadou Diallo",
                "role": "admin",
                "whatsapp_number": "+221771234567",
                "is_active": True,
                "tenant_id": "123e4567-e89b-12d3-a456-426614174001",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
    }
