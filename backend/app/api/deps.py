"""
Dependances communes pour les routes API.
"""
from typing import Generator
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core import security, tenant_context
from app.db.session import get_db
from app.models.user import User

# Security scheme pour JWT
security_scheme = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> tuple[UUID, UUID]:
    """
    Extrait l'user_id et tenant_id depuis le token JWT.

    Args:
        credentials: Credentials HTTP Bearer

    Returns:
        Tuple (user_id, tenant_id)

    Raises:
        HTTPException: Si le token est invalide
    """
    token = credentials.credentials
    payload = security.verify_token(token, "access")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expire",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    tenant_id = payload.get("tenant_id")

    if not user_id or not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Definir le tenant courant dans le contexte
    tenant_context.set_current_tenant(UUID(tenant_id))

    return UUID(user_id), UUID(tenant_id)


async def get_current_tenant_id(
    user_data: tuple = Depends(get_current_user_id)
) -> UUID:
    """
    Extrait uniquement le tenant_id.

    Args:
        user_data: Tuple (user_id, tenant_id) depuis get_current_user_id

    Returns:
        UUID du tenant
    """
    _, tenant_id = user_data
    return tenant_id


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency pour extraire l'utilisateur courant depuis le JWT.

    - Verifie le token JWT
    - Extrait user_id et tenant_id
    - Set le tenant_id dans le contexte
    - Recupere et retourne l'utilisateur

    Args:
        credentials: Credentials HTTP Bearer contenant le token JWT
        db: Session de base de donnees

    Returns:
        User: L'utilisateur authentifie

    Raises:
        HTTPException: Si le token est invalide ou l'utilisateur n'existe pas
    """
    token = credentials.credentials
    payload = security.verify_token(token, "access")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    tenant_id = payload.get("tenant_id")

    if not user_id or not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Set tenant context pour la requete courante
    tenant_context.set_current_tenant(UUID(tenant_id))

    # Recuperer l'utilisateur
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user


async def get_current_active_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency pour routes admin uniquement.

    Args:
        current_user: Utilisateur courant

    Returns:
        User: L'utilisateur si admin

    Raises:
        HTTPException: Si l'utilisateur n'est pas admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
