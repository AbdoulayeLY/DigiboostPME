"""
Router API pour l'authentification.
Endpoints: login, refresh token, get current user.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token
)
from app.models.user import User
from app.schemas.auth import LoginRequest, Token, RefreshTokenRequest
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authentification par email et mot de passe.

    - Verifie les credentials
    - Genere access token (15 min) et refresh token (7 jours)
    - Retourne les deux tokens

    Args:
        login_data: Email et mot de passe
        db: Session de base de donnees

    Returns:
        Token: Access token et refresh token

    Raises:
        HTTPException: Si les credentials sont invalides
    """
    # Rechercher l'utilisateur par email
    user = db.query(User).filter(User.email == login_data.email).first()

    # Verifier que l'utilisateur existe et que le mot de passe est correct
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verifier que l'utilisateur est actif
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    # Generer les tokens
    access_token = create_access_token(
        subject=str(user.id),
        tenant_id=user.tenant_id
    )

    refresh_token = create_refresh_token(
        subject=str(user.id),
        tenant_id=user.tenant_id
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Rafraichir les tokens avec un refresh token.

    - Verifie le refresh token
    - Genere nouveaux access token et refresh token

    Args:
        refresh_data: Refresh token
        db: Session de base de donnees

    Returns:
        Token: Nouveaux access token et refresh token

    Raises:
        HTTPException: Si le refresh token est invalide
    """
    # Verifier le refresh token
    payload = verify_token(refresh_data.refresh_token, "refresh")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    tenant_id = payload.get("tenant_id")

    if not user_id or not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # Verifier que l'utilisateur existe toujours et est actif
    user = db.query(User).filter(User.id == user_id).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Generer de nouveaux tokens
    access_token = create_access_token(
        subject=user_id,
        tenant_id=user.tenant_id
    )

    new_refresh_token = create_refresh_token(
        subject=user_id,
        tenant_id=user.tenant_id
    )

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Recuperer l'utilisateur courant.

    Route protegee necessitant un access token valide.

    Args:
        current_user: Utilisateur courant extrait du token JWT

    Returns:
        UserResponse: Informations de l'utilisateur courant
    """
    return current_user
