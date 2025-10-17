"""
Point d'entree principal de l'application Digiboost PME.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.api.v1 import auth, dashboards, alerts, analytics, predictions, reports


class TenantContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware pour gerer le contexte tenant.
    Nettoie le contexte apres chaque requete.
    """

    async def dispatch(self, request: Request, call_next):
        from app.core.tenant_context import clear_current_tenant

        try:
            response = await call_next(request)
            return response
        finally:
            # Nettoyer le contexte apres la requete
            clear_current_tenant()


def create_application() -> FastAPI:
    """
    Factory pour creer l'application FastAPI.

    Returns:
        Instance configuree de FastAPI
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description="Plateforme d'intelligence supply chain pour PME senegalaises",
        version="1.0.0",
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    )

    # Configuration CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Middleware tenant context
    app.add_middleware(TenantContextMiddleware)

    # Include API routers
    app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
    app.include_router(dashboards.router, prefix=settings.API_V1_PREFIX)
    app.include_router(alerts.router, prefix=settings.API_V1_PREFIX)
    app.include_router(
        analytics.router,
        prefix=f"{settings.API_V1_PREFIX}/analytics",
        tags=["Analytics"]
    )
    app.include_router(
        predictions.router,
        prefix=f"{settings.API_V1_PREFIX}/predictions",
        tags=["Predictions"]
    )
    app.include_router(reports.router, prefix=settings.API_V1_PREFIX)

    # Routes de base
    @app.get("/")
    async def root():
        """Route racine - Information de base sur l'API."""
        return {
            "name": settings.APP_NAME,
            "version": "1.0.0",
            "status": "running",
            "environment": settings.ENVIRONMENT,
            "docs": f"{settings.API_V1_PREFIX}/docs"
        }

    @app.get("/health")
    async def health_check():
        """Health check endpoint - Verifier si l'API est operationnelle."""
        return JSONResponse(
            status_code=200,
            content={
                "status": "ok",
                "environment": settings.ENVIRONMENT
            }
        )

    return app


# Instance de l'application
app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
