"""
Schemas Pydantic pour l'authentification.
"""
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Schema pour la requete de login."""
    email: EmailStr
    password: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "admin@digiboost.sn",
                "password": "password123"
            }
        }
    }


class Token(BaseModel):
    """Schema pour la reponse avec tokens JWT."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    }


class RefreshTokenRequest(BaseModel):
    """Schema pour la requete de refresh token."""
    refresh_token: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    }


class TokenPayload(BaseModel):
    """Schema pour le payload d'un token JWT."""
    sub: str  # user_id
    tenant_id: str
    exp: int
    type: str  # 'access' ou 'refresh'
