"""
Router API pour la génération de rapports.
"""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.api.deps import get_db, get_current_user
from app.services.report_service import ReportService
from app.models.user import User

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/inventory/excel")
async def generate_inventory_report_excel(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Générer rapport Inventaire Stock (Excel).

    Contient:
    - Liste complète des produits
    - Statut stock (RUPTURE, FAIBLE, NORMAL, SURSTOCK)
    - Valorisation par produit
    - Total valorisation

    **Requiert**: Token JWT valide

    **Returns**: Fichier Excel téléchargeable
    """
    service = ReportService(db)
    excel_file = service.generate_inventory_report(current_user.tenant_id)

    # Nom de fichier avec date
    filename = f"inventaire_stock_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/sales-analysis/excel")
async def generate_sales_analysis_report_excel(
    start_date: str = Query(..., description="Date de début (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Date de fin (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Générer rapport Analyse Ventes (Excel multi-onglets).

    Onglets:
    1. Synthèse (KPIs)
    2. Ventes par Produit (avec graphique)
    3. Ventes par Catégorie
    4. Évolution Quotidienne (avec graphique)

    **Requiert**: Token JWT valide

    **Paramètres**:
    - start_date: Date de début (format YYYY-MM-DD)
    - end_date: Date de fin (format YYYY-MM-DD)

    **Returns**: Fichier Excel téléchargeable
    """
    # Parser les dates
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    service = ReportService(db)
    excel_file = service.generate_sales_analysis_report(
        current_user.tenant_id,
        start_dt,
        end_dt
    )

    # Nom de fichier avec période
    filename = f"analyse_ventes_{start_date}_au_{end_date}.xlsx"

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/sales-analysis/monthly/excel")
async def generate_monthly_sales_report(
    year: int = Query(..., description="Année"),
    month: int = Query(..., ge=1, le=12, description="Mois (1-12)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Générer rapport Analyse Ventes Mensuel (Excel).

    Raccourci pour générer un rapport pour un mois complet.

    **Requiert**: Token JWT valide

    **Paramètres**:
    - year: Année (ex: 2025)
    - month: Mois (1-12)

    **Returns**: Fichier Excel téléchargeable
    """
    # Calculer début et fin du mois
    start_dt = datetime(year, month, 1)
    if month == 12:
        end_dt = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_dt = datetime(year, month + 1, 1) - timedelta(days=1)

    service = ReportService(db)
    excel_file = service.generate_sales_analysis_report(
        current_user.tenant_id,
        start_dt,
        end_dt
    )

    # Nom de fichier
    month_names = [
        "janvier", "fevrier", "mars", "avril", "mai", "juin",
        "juillet", "aout", "septembre", "octobre", "novembre", "decembre"
    ]
    filename = f"analyse_ventes_{month_names[month-1]}_{year}.xlsx"

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/monthly-summary/pdf")
async def generate_monthly_summary_pdf(
    year: int = Query(..., description="Année"),
    month: int = Query(..., ge=1, le=12, description="Mois (1-12)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Générer Synthèse Mensuelle (PDF).

    Contenu:
    - KPIs mensuels (CA, transactions, panier moyen)
    - Graphique évolution CA quotidienne
    - Top 5 produits du mois
    - Alertes stock (ruptures et stock faible)
    - Footer avec pagination

    **Requiert**: Token JWT valide

    **Paramètres**:
    - year: Année (ex: 2025)
    - month: Mois (1-12)

    **Returns**: Fichier PDF téléchargeable
    """
    service = ReportService(db)
    pdf_file = service.generate_monthly_summary_pdf(
        current_user.tenant_id,
        month,
        year
    )

    # Nom de fichier
    month_names = [
        "janvier", "fevrier", "mars", "avril", "mai", "juin",
        "juillet", "aout", "septembre", "octobre", "novembre", "decembre"
    ]
    filename = f"synthese_mensuelle_{month_names[month-1]}_{year}.pdf"

    return StreamingResponse(
        pdf_file,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
