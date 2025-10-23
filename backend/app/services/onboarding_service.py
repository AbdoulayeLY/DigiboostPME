"""
Service Onboarding - Logique métier du wizard d'onboarding admin.
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.audit_log import AdminAuditLog
from app.models.onboarding import OnboardingSession
from app.models.site import Site
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.onboarding import (
    CreateTenantAdmin,
    CreateUserAdmin,
    TenantCreationResponse,
    UserCreationResponse,
)

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class OnboardingService:
    """
    Service pour gérer le processus d'onboarding des nouveaux tenants.

    Responsabilités:
    - Créer tenant + site principal (Étape 1)
    - Créer users avec login flexible (Étape 2)
    - Gérer sessions onboarding
    - Logger toutes les actions admin
    """

    def __init__(self, db: Session):
        self.db = db

    def create_tenant_with_site(
        self,
        data: CreateTenantAdmin,
        admin_user_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TenantCreationResponse:
        """
        Créer un nouveau tenant avec son site principal et session onboarding.

        Args:
            data: Données du tenant à créer
            admin_user_id: ID de l'admin qui crée le tenant
            ip_address: IP de la requête (audit)
            user_agent: User agent (audit)

        Returns:
            TenantCreationResponse avec IDs créés

        Raises:
            IntegrityError: Si email/ninea déjà existant
        """
        try:
            # 1. Créer le tenant
            tenant = Tenant(
                name=data.name,
                ninea=data.ninea,
                sector=data.sector,
                country=data.country,
                email=data.email,
                phone=data.phone,
                created_by=data.created_by,
                is_active=False,  # Sera activé après import données
                settings={},
            )
            self.db.add(tenant)
            self.db.flush()  # Pour obtenir l'ID

            logger.info(f"Tenant créé: {tenant.id} - {tenant.name}")

            # 2. Créer le site principal
            site = Site(
                tenant_id=tenant.id,
                name=data.site_name,
                address=data.site_address,
                type="main",
                is_active=True,
            )
            self.db.add(site)
            self.db.flush()

            logger.info(f"Site principal créé: {site.id} - {site.name}")

            # 3. Créer session onboarding
            session = OnboardingSession(
                tenant_id=tenant.id,
                status="in_progress",
                current_step=1,
                data={
                    "tenant_name": tenant.name,
                    "site_name": site.name,
                    "created_via": "wizard",
                },
                created_by=f"admin:{admin_user_id}" if admin_user_id else "system",
            )
            self.db.add(session)
            self.db.flush()

            logger.info(f"Session onboarding créée: {session.id}")

            # 4. Logger action admin (audit)
            self._log_admin_action(
                admin_user_id=admin_user_id,
                action_type="create_tenant",
                entity_type="tenant",
                entity_id=tenant.id,
                details={
                    "tenant_name": tenant.name,
                    "tenant_email": tenant.email,
                    "site_name": site.name,
                    "ninea": tenant.ninea,
                },
                ip_address=ip_address,
                user_agent=user_agent,
            )

            # 5. Commit transaction
            self.db.commit()

            return TenantCreationResponse(
                tenant_id=tenant.id,
                site_id=site.id,
                session_id=session.id,
                tenant_name=tenant.name,
                site_name=site.name,
                is_active=tenant.is_active,
                created_at=tenant.created_at,
            )

        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Erreur création tenant: {str(e)}")
            raise ValueError("Un tenant avec cet email ou NINEA existe déjà")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur inattendue création tenant: {str(e)}")
            raise

    def create_users(
        self,
        tenant_id: UUID,
        users_data: List[CreateUserAdmin],
        admin_user_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> List[UserCreationResponse]:
        """
        Créer plusieurs users pour un tenant.

        Args:
            tenant_id: ID du tenant
            users_data: Liste des données users
            admin_user_id: ID de l'admin créateur
            ip_address: IP requête
            user_agent: User agent

        Returns:
            Liste des users créés

        Raises:
            ValueError: Si tenant inexistant ou email/phone déjà utilisé
        """
        # Vérifier que le tenant existe
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} introuvable")

        created_users = []

        try:
            for user_data in users_data:
                # Hasher le mot de passe par défaut
                hashed_password = pwd_context.hash(user_data.default_password)

                # Créer user
                user = User(
                    tenant_id=tenant_id,
                    email=user_data.email,
                    phone=user_data.phone,
                    hashed_password=hashed_password,
                    first_name=user_data.first_name,
                    last_name=user_data.last_name,
                    full_name=f"{user_data.first_name} {user_data.last_name}",  # Pour compatibilité
                    role=user_data.role,
                    whatsapp_number=user_data.whatsapp_number,
                    is_active=True,
                    email_verified=False,
                    must_change_password=user_data.must_change_password,
                )
                self.db.add(user)
                self.db.flush()

                logger.info(f"User créé: {user.id} - {user.email or user.phone}")

                # Logger action audit
                self._log_admin_action(
                    admin_user_id=admin_user_id,
                    action_type="create_user",
                    entity_type="user",
                    entity_id=user.id,
                    details={
                        "tenant_id": str(tenant_id),
                        "email": user.email,
                        "phone": user.phone,
                        "role": user.role,
                        "must_change_password": user.must_change_password,
                    },
                    ip_address=ip_address,
                    user_agent=user_agent,
                )

                created_users.append(
                    UserCreationResponse(
                        user_id=user.id,
                        email=user.email,
                        phone=user.phone,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        role=user.role,
                        must_change_password=user.must_change_password,
                        created_at=user.created_at,
                    )
                )

            # Mettre à jour session onboarding (étape 2 complétée)
            session = (
                self.db.query(OnboardingSession)
                .filter(OnboardingSession.tenant_id == tenant_id)
                .order_by(OnboardingSession.created_at.desc())
                .first()
            )
            if session:
                session.current_step = 2
                session.data["users_created"] = len(created_users)
                self.db.add(session)

            self.db.commit()

            logger.info(f"{len(created_users)} users créés pour tenant {tenant_id}")
            return created_users

        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Erreur création users: {str(e)}")
            raise ValueError("Un user avec cet email ou téléphone existe déjà")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur inattendue création users: {str(e)}")
            raise

    def update_onboarding_session(
        self,
        session_id: UUID,
        current_step: Optional[int] = None,
        status: Optional[str] = None,
        data: Optional[Dict] = None,
        error_message: Optional[str] = None,
    ) -> OnboardingSession:
        """
        Mettre à jour une session d'onboarding.

        Args:
            session_id: ID session
            current_step: Nouvelle étape (1-4)
            status: Nouveau statut (in_progress, completed, failed)
            data: Données à merger avec existantes
            error_message: Message d'erreur si failed

        Returns:
            Session mise à jour

        Raises:
            ValueError: Si session introuvable
        """
        session = self.db.query(OnboardingSession).filter(OnboardingSession.id == session_id).first()
        if not session:
            raise ValueError(f"Session {session_id} introuvable")

        if current_step is not None:
            session.current_step = current_step

        if status is not None:
            session.status = status
            if status == "completed":
                session.completed_at = datetime.utcnow()

        if data is not None:
            # Merger avec données existantes
            session.data.update(data)

        if error_message is not None:
            session.error_message = error_message

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        logger.info(f"Session {session_id} mise à jour: step={current_step}, status={status}")
        return session

    def get_onboarding_session(self, tenant_id: UUID) -> Optional[OnboardingSession]:
        """
        Récupérer la session d'onboarding d'un tenant.

        Args:
            tenant_id: ID du tenant

        Returns:
            Session onboarding la plus récente ou None
        """
        session = (
            self.db.query(OnboardingSession)
            .filter(OnboardingSession.tenant_id == tenant_id)
            .order_by(OnboardingSession.created_at.desc())
            .first()
        )
        return session

    def _log_admin_action(
        self,
        action_type: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        details: Optional[Dict] = None,
        admin_user_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """
        Logger une action admin dans admin_audit_logs.

        Args:
            action_type: Type d'action (create_tenant, create_user, etc.)
            entity_type: Type d'entité affectée
            entity_id: ID de l'entité
            details: Détails additionnels
            admin_user_id: ID admin qui effectue l'action
            ip_address: IP de la requête
            user_agent: User agent
        """
        try:
            log = AdminAuditLog(
                admin_user_id=admin_user_id,
                action_type=action_type,
                entity_type=entity_type,
                entity_id=entity_id,
                details=details or {},
                ip_address=ip_address,
                user_agent=user_agent,
            )
            self.db.add(log)
            # Ne pas commit ici, sera fait avec la transaction principale
        except Exception as e:
            logger.error(f"Erreur logging action admin: {str(e)}")
            # Ne pas faire échouer l'opération principale si logging échoue
