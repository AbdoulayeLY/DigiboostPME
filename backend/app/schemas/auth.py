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


class ChangePasswordFirstLoginRequest(BaseModel):
    """Schema pour le changement de mot de passe à la première connexion."""
    old_password: str
    new_password: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "old_password": "Digiboost2025",
                "new_password": "MonNouveauMotDePasse123!"
            }
        }
    }


class LoginResponse(BaseModel):
    """Schema pour la réponse de login (peut inclure must_change_password)."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    must_change_password: bool = False
    temp_token: str | None = None  # Token temporaire pour changement MDP

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "must_change_password": False,
                "temp_token": None
            }
        }
    }
