"""
Gestion du contexte multi-tenant.
Utilise contextvars pour gérer le tenant_id courant dans chaque requête.
"""
from contextvars import ContextVar
from typing import Optional
from uuid import UUID

# Variable de contexte pour stocker le tenant_id de la requête courante
current_tenant_id: ContextVar[Optional[UUID]] = ContextVar(
    'current_tenant_id',
    default=None
)


def set_current_tenant(tenant_id: UUID) -> None:
    """
    Définit le tenant_id pour la requête courante.

    Args:
        tenant_id: UUID du tenant à définir
    """
    current_tenant_id.set(tenant_id)


def get_current_tenant() -> Optional[UUID]:
    """
    Récupère le tenant_id de la requête courante.

    Returns:
        UUID du tenant courant ou None
    """
    return current_tenant_id.get()


def clear_current_tenant() -> None:
    """Nettoie le tenant_id courant."""
    current_tenant_id.set(None)
