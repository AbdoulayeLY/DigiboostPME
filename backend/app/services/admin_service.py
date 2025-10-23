"""
Service Admin - Utilities pour vérifications et audit des actions admin.

Ce service fournit des fonctions utilitaires pour:
- Vérification des permissions admin
- Logging d'audit des actions admin
- Validation des opérations sensibles
"""
import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit_log import AdminAuditLog
from app.models.user import User

logger = logging.getLogger(__name__)


class AdminService:
    """
    Service pour opérations et vérifications admin.

    Fournit des utilities pour:
    - Vérifier les permissions admin
    - Logger les actions dans admin_audit_logs
    - Valider les opérations sensibles
    """

    def __init__(self, db: Session):
        """
        Initialiser le service admin.

        Args:
            db: Session SQLAlchemy
        """
        self.db = db

    def verify_admin_role(self, user: User) -> bool:
        """
        Vérifier qu'un utilisateur a le rôle admin.

        Args:
            user: Utilisateur à vérifier

        Returns:
            True si admin, False sinon
        """
        return user.role == "admin" and user.is_active

    def log_admin_action(
        self,
        admin_user_id: UUID,
        action_type: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AdminAuditLog:
        """
        Logger une action admin dans admin_audit_logs.

        Args:
            admin_user_id: ID de l'admin qui effectue l'action
            action_type: Type d'action (create_tenant, create_user, etc.)
            entity_type: Type d'entité affectée (tenant, user, etc.)
            entity_id: ID de l'entité affectée
            details: Détails additionnels de l'action
            ip_address: Adresse IP de l'admin
            user_agent: User-Agent du navigateur

        Returns:
            Log d'audit créé
        """
        audit_log = AdminAuditLog(
            admin_user_id=admin_user_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.utcnow(),
        )

        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)

        logger.info(
            f"Admin action logged: {action_type} by admin {admin_user_id} "
            f"on {entity_type} {entity_id}"
        )

        return audit_log

    def get_admin_audit_logs(
        self,
        admin_user_id: Optional[UUID] = None,
        action_type: Optional[str] = None,
        entity_type: Optional[str] = None,
        limit: int = 100,
    ) -> list[AdminAuditLog]:
        """
        Récupérer les logs d'audit admin avec filtres optionnels.

        Args:
            admin_user_id: Filtrer par admin
            action_type: Filtrer par type d'action
            entity_type: Filtrer par type d'entité
            limit: Nombre maximum de logs à retourner

        Returns:
            Liste de logs d'audit
        """
        query = self.db.query(AdminAuditLog)

        if admin_user_id:
            query = query.filter(AdminAuditLog.admin_user_id == admin_user_id)

        if action_type:
            query = query.filter(AdminAuditLog.action_type == action_type)

        if entity_type:
            query = query.filter(AdminAuditLog.entity_type == entity_type)

        return query.order_by(AdminAuditLog.created_at.desc()).limit(limit).all()

    def verify_tenant_exists(self, tenant_id: UUID) -> bool:
        """
        Vérifier qu'un tenant existe.

        Args:
            tenant_id: ID du tenant à vérifier

        Returns:
            True si le tenant existe, False sinon
        """
        from app.models.tenant import Tenant

        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        return tenant is not None

    def verify_user_belongs_to_tenant(self, user_id: UUID, tenant_id: UUID) -> bool:
        """
        Vérifier qu'un utilisateur appartient à un tenant.

        Args:
            user_id: ID de l'utilisateur
            tenant_id: ID du tenant

        Returns:
            True si l'utilisateur appartient au tenant, False sinon
        """
        user = self.db.query(User).filter(
            User.id == user_id,
            User.tenant_id == tenant_id
        ).first()

        return user is not None

    def get_tenant_statistics(self, tenant_id: UUID) -> dict:
        """
        Obtenir des statistiques sur un tenant.

        Args:
            tenant_id: ID du tenant

        Returns:
            Dictionnaire avec statistiques (users count, products count, etc.)
        """
        from app.models.product import Product
        from app.models.sale import Sale

        stats = {
            "tenant_id": str(tenant_id),
            "users_count": self.db.query(User).filter(
                User.tenant_id == tenant_id
            ).count(),
            "products_count": self.db.query(Product).filter(
                Product.tenant_id == tenant_id
            ).count(),
            "sales_count": self.db.query(Sale).filter(
                Sale.tenant_id == tenant_id
            ).count(),
        }

        return stats

    def validate_admin_operation(
        self,
        admin_user: User,
        operation: str,
        target_tenant_id: Optional[UUID] = None,
    ) -> bool:
        """
        Valider qu'une opération admin est autorisée.

        Args:
            admin_user: Utilisateur admin
            operation: Type d'opération à valider
            target_tenant_id: ID du tenant cible (optionnel)

        Returns:
            True si opération autorisée, False sinon

        Raises:
            ValueError: Si l'opération n'est pas autorisée
        """
        # Vérifier que l'utilisateur est admin
        if not self.verify_admin_role(admin_user):
            raise ValueError("User is not an admin")

        # Pour l'instant, tous les admins peuvent tout faire
        # Dans le futur, on pourra ajouter une logique de permissions plus fine
        # (ex: super_admin vs admin, permissions par tenant, etc.)

        logger.info(
            f"Admin operation validated: {operation} by admin {admin_user.id}"
        )

        return True
