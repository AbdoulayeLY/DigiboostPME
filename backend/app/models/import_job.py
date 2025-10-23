"""
Modèle ImportJob (tracking des jobs d'import asynchrones).
"""
import uuid
from datetime import datetime
from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TenantMixin


class ImportJob(Base, TenantMixin):
    """
    Modèle ImportJob - track l'état d'un job d'import de données.

    Lié à une tâche Celery pour permettre le suivi temps réel de la progression
    de l'import de données (produits, ventes) depuis un fichier Excel.
    """

    __tablename__ = "import_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("onboarding_sessions.id", ondelete="SET NULL"), nullable=True)
    celery_task_id = Column(String(255), unique=True, nullable=True)
    status = Column(String(50), nullable=False)  # pending, running, success, failed
    file_name = Column(String(255), nullable=True)
    file_size_bytes = Column(BigInteger, nullable=True)
    progress_percent = Column(Integer, default=0, nullable=False)
    stats = Column(JSONB, default=dict)  # {products_imported: 100, sales_imported: 500, errors: []}
    error_details = Column(JSONB, nullable=True)
    started_at = Column(TIMESTAMP, nullable=True)
    completed_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    # Relations
    tenant = relationship("Tenant", back_populates="import_jobs")
    session = relationship("OnboardingSession", back_populates="import_jobs")

    def __repr__(self) -> str:
        return f"<ImportJob(id={self.id}, tenant_id={self.tenant_id}, status={self.status}, progress={self.progress_percent}%)>"
