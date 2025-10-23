"""
Routes API Admin - Onboarding Wizard.

Endpoints protégés par authentification admin pour créer et configurer
de nouveaux tenants via le wizard d'onboarding.
"""
import logging
from typing import List
from uuid import UUID

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_admin, get_db
from app.models.user import User
from app.schemas.onboarding import (
    CreateTenantAdmin,
    CreateUsersRequest,
    TenantCreationResponse,
    UsersCreationResponse,
    UserCreationResponse,
    GenerateTemplateRequest,
    ImportJobResponse,
    ImportStatusResponse,
)
from app.services.onboarding_service import OnboardingService
from app.services.template_service import TemplateService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/onboarding", tags=["Admin Onboarding"])


@router.post("/create-tenant", response_model=TenantCreationResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    data: CreateTenantAdmin,
    request: Request,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """
    **[ADMIN ONLY]** Créer un nouveau tenant avec son site principal (Étape 1 wizard).

    Crée:
    - Un tenant (entreprise cliente)
    - Un site principal
    - Une session d'onboarding

    Tous les événements sont loggés dans admin_audit_logs pour traçabilité.

    **Permissions:** Admin uniquement

    **Returns:**
    - tenant_id: UUID du tenant créé
    - site_id: UUID du site principal
    - session_id: UUID de la session onboarding
    """
    try:
        service = OnboardingService(db)

        # Extraire IP et User-Agent pour audit
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        tenant_response = service.create_tenant_with_site(
            data=data,
            admin_user_id=current_admin.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        logger.info(
            f"Tenant créé par admin {current_admin.id}: {tenant_response.tenant_id}"
        )
        return tenant_response

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur création tenant: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création du tenant",
        )


@router.post("/create-users", response_model=UsersCreationResponse, status_code=status.HTTP_201_CREATED)
async def create_users(
    data: CreateUsersRequest,
    request: Request,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """
    **[ADMIN ONLY]** Créer plusieurs utilisateurs pour un tenant (Étape 2 wizard).

    Permet de créer de 1 à 10 utilisateurs avec:
    - Identifiant flexible (email OU téléphone)
    - Mot de passe par défaut
    - Flag must_change_password pour forcer changement à la 1ère connexion

    **Permissions:** Admin uniquement

    **Returns:**
    - Liste des utilisateurs créés avec leurs IDs
    """
    try:
        service = OnboardingService(db)

        # Extraire contexte pour audit
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        users = service.create_users(
            tenant_id=data.tenant_id,
            users_data=data.users,
            admin_user_id=current_admin.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        logger.info(
            f"{len(users)} users créés par admin {current_admin.id} pour tenant {data.tenant_id}"
        )

        return UsersCreationResponse(
            tenant_id=data.tenant_id,
            users_created=users,
            count=len(users),
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur création users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création des utilisateurs",
        )


@router.get("/generate-template/{tenant_id}")
async def generate_template(
    tenant_id: UUID,
    include_categories: bool = True,
    include_suppliers: bool = True,
    sample_data: bool = True,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """
    **[ADMIN ONLY]** Générer un template Excel personnalisé pour import (Étape 3 wizard).

    Génère un fichier Excel avec:
    - Onglet "Produits" (code, nom, catégorie, prix, stock)
    - Onglet "Ventes" (code_produit, date, quantité, prix)
    - Onglet "Instructions" (guide de remplissage)
    - Headers formatés
    - Lignes d'exemple (optionnel)

    **Note:** Implémentation basique pour Sprint 1.
    Sprint 2 ajoutera validation Excel intégrée, formules, etc.

    **Permissions:** Admin uniquement

    **Returns:**
    - Fichier Excel (.xlsx) en téléchargement
    """
    try:
        service = TemplateService(db)

        # Générer le template Excel
        excel_file = service.generate_template(
            tenant_id=tenant_id,
            include_categories=include_categories,
            include_suppliers=include_suppliers,
            sample_data=sample_data,
        )

        # Nom du fichier
        filename = f"template_digiboost_{tenant_id}.xlsx"

        logger.info(f"Template généré pour tenant {tenant_id} par admin {current_admin.id}")

        # Retourner en streaming
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error(f"Erreur génération template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la génération du template",
        )


@router.post("/upload-template/{tenant_id}", response_model=ImportJobResponse)
async def upload_template(
    tenant_id: UUID,
    file: UploadFile = File(...),
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """
    **[ADMIN ONLY]** Upload et importer les données d'un tenant depuis Excel (Étape 4 wizard).

    Sprint 2: Implémentation complète avec:
    1. Validation format fichier (.xlsx uniquement)
    2. Sauvegarde fichier dans storage/uploads/
    3. Création ImportJob
    4. Déclenchement tâche Celery asynchrone
    5. Retour task_id pour tracking

    **Permissions:** Admin uniquement

    **Returns:**
    - ImportJobResponse avec job_id, celery_task_id, status
    """
    import os
    from pathlib import Path
    import uuid
    from app.tasks.onboarding import import_tenant_data
    from app.models.import_job import ImportJob
    from app.schemas.onboarding import ImportJobResponse

    try:
        # 1. Valider format fichier
        if not file.filename.endswith('.xlsx'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format fichier invalide. Seul .xlsx est accepté"
            )

        # 2. Sauvegarder fichier
        storage_dir = Path("storage/uploads")
        storage_dir.mkdir(parents=True, exist_ok=True)

        file_id = uuid.uuid4()
        file_name = f"{tenant_id}_{file_id}_{file.filename}"
        file_path = storage_dir / file_name

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        logger.info(f"Fichier sauvegardé: {file_path} ({len(content)} bytes)")

        # 3. Créer ImportJob
        import_job = ImportJob(
            tenant_id=tenant_id,
            file_name=file.filename,
            file_size_bytes=len(content),
            status="pending",
            progress_percent=0,
            stats={"file_path": str(file_path)},  # Store file_path in stats
        )
        db.add(import_job)
        db.commit()
        db.refresh(import_job)

        # 4. Lancer tâche Celery
        task = import_tenant_data.delay(str(import_job.id), str(file_path))

        # 5. Update import_job avec celery_task_id
        import_job.celery_task_id = task.id
        import_job.status = "running"
        import_job.started_at = datetime.utcnow()
        db.commit()

        logger.info(
            f"Import lancé pour tenant {tenant_id} - Job: {import_job.id}, Task: {task.id}"
        )

        return ImportJobResponse(
            job_id=import_job.id,
            celery_task_id=task.id,
            tenant_id=tenant_id,
            status="running",
            message="Import démarré avec succès",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'upload: {str(e)}",
        )


@router.get("/import-status/{import_job_id}", response_model=ImportStatusResponse)
async def get_import_status(
    import_job_id: UUID,
    current_admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """
    **[ADMIN ONLY]** Récupérer le statut d'un import en cours.

    Sprint 2: Tracking en temps réel avec:
    - Statut (pending/running/success/failed)
    - Progression (0-100%)
    - Statistiques (produits/ventes importés)
    - Erreurs détaillées si échec

    Utilisé pour polling frontend (toutes les 2 secondes).

    **Permissions:** Admin uniquement

    **Returns:**
    - ImportStatusResponse avec progression et stats
    """
    from app.models.import_job import ImportJob

    try:
        # Récupérer ImportJob
        import_job = db.query(ImportJob).filter(ImportJob.id == import_job_id).first()

        if not import_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Import job {import_job_id} introuvable"
            )

        return ImportStatusResponse(
            job_id=import_job.id,
            tenant_id=import_job.tenant_id,
            status=import_job.status,
            progress_percent=import_job.progress_percent,
            file_name=import_job.file_name,
            stats=import_job.stats or {},
            error_details=import_job.error_details,
            started_at=import_job.started_at,
            completed_at=import_job.completed_at,
            created_at=import_job.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération du statut",
        )
