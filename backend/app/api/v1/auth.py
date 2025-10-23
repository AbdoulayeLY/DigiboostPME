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
    create_temp_token,
    verify_token,
    get_password_hash
)
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    Token,
    RefreshTokenRequest,
    LoginResponse,
    ChangePasswordFirstLoginRequest
)
from app.schemas.user import UserResponse
from app.utils.validators import validate_password_strength

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authentification par email et mot de passe.

    - Verifie les credentials
    - Genere access token (15 min) et refresh token (7 jours)
    - Si must_change_password=True, retourne temp_token au lieu des tokens normaux

    Args:
        login_data: Email et mot de passe
        db: Session de base de donnees

    Returns:
        LoginResponse: Access token, refresh token, et flag must_change_password

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

    # Si l'utilisateur doit changer son mot de passe
    if user.must_change_password:
        # Generer un token temporaire (15 min) pour le changement de MDP
        temp_token = create_temp_token(
            subject=str(user.id),
            tenant_id=user.tenant_id
        )

        return LoginResponse(
            access_token="",  # Pas d'access token
            refresh_token="",  # Pas de refresh token
            token_type="bearer",
            must_change_password=True,
            temp_token=temp_token
        )

    # Generer les tokens normaux
    access_token = create_access_token(
        subject=str(user.id),
        tenant_id=user.tenant_id
    )

    refresh_token = create_refresh_token(
        subject=str(user.id),
        tenant_id=user.tenant_id
    )

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        must_change_password=False,
        temp_token=None
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


@router.post("/change-password-first-login", response_model=LoginResponse)
async def change_password_first_login(
    password_data: ChangePasswordFirstLoginRequest,
    temp_token: str,
    db: Session = Depends(get_db)
):
    """
    Changer le mot de passe à la première connexion.

    Utilisé lorsqu'un utilisateur créé par l'admin doit changer son mot de passe
    par défaut lors de sa première connexion.

    - Vérifie le temp_token (15 min de validité)
    - Vérifie l'ancien mot de passe
    - Valide la force du nouveau mot de passe
    - Met à jour le mot de passe et must_change_password = False
    - Retourne des tokens normaux pour accéder à l'application

    Args:
        password_data: Ancien et nouveau mot de passe
        temp_token: Token temporaire reçu au login
        db: Session de base de données

    Returns:
        LoginResponse: Access token et refresh token normaux

    Raises:
        HTTPException: Si temp_token invalide, ancien MDP incorrect, ou nouveau MDP faible
    """
    # Vérifier le temp_token
    payload = verify_token(temp_token, "temp")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired temporary token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    tenant_id = payload.get("tenant_id")

    if not user_id or not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # Récupérer l'utilisateur
    user = db.query(User).filter(User.id == user_id).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Vérifier que l'utilisateur doit vraiment changer son mot de passe
    if not user.must_change_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not need to change password"
        )

    # Vérifier l'ancien mot de passe
    if not verify_password(password_data.old_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect old password"
        )

    # Valider la force du nouveau mot de passe
    is_valid, error_message = validate_password_strength(password_data.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    # Mettre à jour le mot de passe
    user.hashed_password = get_password_hash(password_data.new_password)
    user.must_change_password = False

    db.commit()
    db.refresh(user)

    # Générer des tokens normaux
    access_token = create_access_token(
        subject=str(user.id),
        tenant_id=user.tenant_id
    )

    refresh_token = create_refresh_token(
        subject=str(user.id),
        tenant_id=user.tenant_id
    )

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        must_change_password=False,
        temp_token=None
    )
