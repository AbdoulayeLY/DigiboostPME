"""
Gestion de la sécurité: JWT, hashing de mots de passe.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# Configuration du hashing des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Algorithme JWT
ALGORITHM = "HS256"


def create_access_token(
    subject: str,
    tenant_id: UUID,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crée un token JWT d'accès.

    Args:
        subject: Identifiant de l'utilisateur (user_id)
        tenant_id: Identifiant du tenant
        expires_delta: Durée de validité personnalisée (optionnel)

    Returns:
        Token JWT encodé
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "tenant_id": str(tenant_id),
        "type": "access"
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(subject: str, tenant_id: UUID) -> str:
    """
    Crée un token JWT de rafraîchissement.

    Args:
        subject: Identifiant de l'utilisateur (user_id)
        tenant_id: Identifiant du tenant

    Returns:
        Token JWT encodé
    """
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "tenant_id": str(tenant_id),
        "type": "refresh"
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str, expected_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Vérifie et décode un token JWT.

    Args:
        token: Token JWT à vérifier
        expected_type: Type de token attendu ('access' ou 'refresh')

    Returns:
        Payload du token si valide, None sinon
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        # Vérifier le type de token
        token_type: str = payload.get("type")
        if token_type != expected_type:
            return None

        return payload

    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie qu'un mot de passe correspond à son hash.

    Args:
        plain_password: Mot de passe en clair
        hashed_password: Hash du mot de passe

    Returns:
        True si le mot de passe correspond, False sinon
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Génère le hash d'un mot de passe.

    Args:
        password: Mot de passe en clair

    Returns:
        Hash du mot de passe
    """
    return pwd_context.hash(password)


def create_temp_token(subject: str, tenant_id: UUID) -> str:
    """
    Crée un token JWT temporaire pour changement de mot de passe.

    Ce token a une validité de 15 minutes et est utilisé uniquement
    pour l'endpoint de changement de mot de passe à la première connexion.

    Args:
        subject: Identifiant de l'utilisateur (user_id)
        tenant_id: Identifiant du tenant

    Returns:
        Token JWT encodé temporaire
    """
    expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "tenant_id": str(tenant_id),
        "type": "temp"
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt
