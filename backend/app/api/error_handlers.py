"""
Custom error handlers pour l'API FastAPI
Sprint 4 - Error handling robuste
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, OperationalError
from celery.exceptions import TimeoutError as CeleryTaskTimeout
import logging

logger = logging.getLogger(__name__)


class FileUploadError(Exception):
    """Exception levée lors d'erreurs d'upload de fichier"""

    def __init__(self, message: str, code: str = "FILE_UPLOAD_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class BusinessValidationError(Exception):
    """Exception levée lors de violations de règles métier"""

    def __init__(self, message: str, code: str = "BUSINESS_VALIDATION_ERROR", details: dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handler pour les erreurs de validation Pydantic (422)
    Retourne des messages user-friendly
    """
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        msg = error["msg"]

        # Messages français user-friendly
        if "field required" in msg.lower():
            msg = f"Le champ '{field}' est obligatoire"
        elif "string type expected" in msg.lower():
            msg = f"Le champ '{field}' doit être du texte"
        elif "value is not a valid email" in msg.lower():
            msg = f"L'email '{field}' est invalide"
        elif "ensure this value has at least" in msg.lower():
            msg = f"Le champ '{field}' est trop court"

        errors.append({
            "field": field,
            "message": msg,
            "type": error["type"]
        })

    logger.warning(f"Validation error on {request.url.path}: {errors}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Les données fournies sont invalides",
            "details": errors
        }
    )


async def integrity_error_handler(request: Request, exc: IntegrityError):
    """
    Handler pour les erreurs d'intégrité DB (contraintes uniques, FK, etc.)
    """
    error_msg = str(exc.orig) if hasattr(exc, 'orig') else str(exc)

    # Détection de contraintes spécifiques
    if "unique constraint" in error_msg.lower():
        message = "Cette entrée existe déjà dans la base de données"
        if "email" in error_msg.lower():
            message = "Cet email est déjà utilisé"
        elif "phone" in error_msg.lower():
            message = "Ce numéro de téléphone est déjà utilisé"
        elif "code" in error_msg.lower():
            message = "Ce code produit existe déjà"
    elif "foreign key constraint" in error_msg.lower():
        message = "Référence invalide: l'élément lié n'existe pas"
    elif "not null constraint" in error_msg.lower():
        message = "Un champ obligatoire est manquant"
    else:
        message = "Erreur d'intégrité des données"

    logger.error(f"Integrity error on {request.url.path}: {error_msg}")

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": "INTEGRITY_ERROR",
            "message": message,
            "technical_details": error_msg if logger.isEnabledFor(logging.DEBUG) else None
        }
    )


async def operational_error_handler(request: Request, exc: OperationalError):
    """
    Handler pour les erreurs opérationnelles DB (timeout, connexion perdue, etc.)
    """
    error_msg = str(exc.orig) if hasattr(exc, 'orig') else str(exc)

    logger.error(f"Database operational error on {request.url.path}: {error_msg}")

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": "DATABASE_ERROR",
            "message": "Service temporairement indisponible. Veuillez réessayer dans quelques instants.",
            "retry_after": 30  # secondes
        }
    )


async def celery_timeout_handler(request: Request, exc: CeleryTaskTimeout):
    """
    Handler pour les timeouts Celery (tâche > timeout configuré)
    """
    logger.error(f"Celery task timeout on {request.url.path}: {exc}")

    return JSONResponse(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        content={
            "error": "TASK_TIMEOUT",
            "message": "L'opération prend plus de temps que prévu. Elle continue en arrière-plan.",
            "details": "Vous pouvez vérifier le statut via l'API de suivi des tâches."
        }
    )


async def file_upload_error_handler(request: Request, exc: FileUploadError):
    """
    Handler pour les erreurs d'upload de fichier
    """
    logger.warning(f"File upload error on {request.url.path}: {exc.message}")

    # Déterminer le status code selon le type d'erreur
    if exc.code == "FILE_TOO_LARGE":
        status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    elif exc.code == "INVALID_FILE_TYPE":
        status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    else:
        status_code = status.HTTP_400_BAD_REQUEST

    return JSONResponse(
        status_code=status_code,
        content={
            "error": exc.code,
            "message": exc.message
        }
    )


async def business_validation_error_handler(request: Request, exc: BusinessValidationError):
    """
    Handler pour les erreurs de validation métier
    """
    logger.warning(f"Business validation error on {request.url.path}: {exc.message}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": exc.code,
            "message": exc.message,
            "details": exc.details
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handler générique pour toutes les exceptions non gérées
    """
    logger.exception(f"Unhandled exception on {request.url.path}: {exc}")

    # En production, ne pas exposer les détails techniques
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "Une erreur inattendue s'est produite. Nos équipes ont été notifiées.",
            "request_id": id(request)  # Permet de tracer dans les logs
        }
    )


def register_error_handlers(app):
    """
    Enregistre tous les error handlers dans l'application FastAPI
    """
    from fastapi import FastAPI

    # Validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)

    # Database errors
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(OperationalError, operational_error_handler)

    # Custom errors
    app.add_exception_handler(FileUploadError, file_upload_error_handler)
    app.add_exception_handler(BusinessValidationError, business_validation_error_handler)
    app.add_exception_handler(CeleryTaskTimeout, celery_timeout_handler)

    # Catch-all
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("Error handlers registered successfully")
