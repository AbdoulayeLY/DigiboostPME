"""
Exceptions personnalisées pour l'application Digiboost PME.
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class DigiboostException(Exception):
    """Exception de base pour toutes les exceptions métier."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class TenantNotFoundException(DigiboostException):
    """Exception levée quand un tenant n'est pas trouvé."""
    pass


class UnauthorizedException(DigiboostException):
    """Exception levée pour les problèmes d'authentification."""
    pass


class ForbiddenException(DigiboostException):
    """Exception levée pour les problèmes d'autorisation."""
    pass


class ResourceNotFoundException(DigiboostException):
    """Exception levée quand une ressource n'est pas trouvée."""
    pass


class ValidationException(DigiboostException):
    """Exception levée pour les erreurs de validation métier."""
    pass


class DuplicateResourceException(DigiboostException):
    """Exception levée quand on tente de créer une ressource déjà existante."""
    pass


def create_http_exception(
    status_code: int,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """
    Crée une HTTPException avec un format standardisé.

    Args:
        status_code: Code HTTP
        message: Message d'erreur
        details: Détails additionnels optionnels

    Returns:
        HTTPException configurée
    """
    return HTTPException(
        status_code=status_code,
        detail={
            "message": message,
            "details": details or {}
        }
    )


# Exceptions HTTP pré-configurées
def unauthorized_exception(message: str = "Non authentifié") -> HTTPException:
    """Exception pour authentification échouée."""
    return create_http_exception(status.HTTP_401_UNAUTHORIZED, message)


def forbidden_exception(message: str = "Accès interdit") -> HTTPException:
    """Exception pour autorisation refusée."""
    return create_http_exception(status.HTTP_403_FORBIDDEN, message)


def not_found_exception(
    resource: str = "Ressource",
    identifier: Any = None
) -> HTTPException:
    """Exception pour ressource non trouvée."""
    message = f"{resource} non trouvé(e)"
    if identifier:
        message += f": {identifier}"
    return create_http_exception(status.HTTP_404_NOT_FOUND, message)


def validation_exception(
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """Exception pour erreur de validation."""
    return create_http_exception(status.HTTP_422_UNPROCESSABLE_ENTITY, message, details)


def duplicate_exception(resource: str = "Ressource") -> HTTPException:
    """Exception pour ressource dupliquée."""
    return create_http_exception(
        status.HTTP_409_CONFLICT,
        f"{resource} existe déjà"
    )
