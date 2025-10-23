"""
Celery Tasks - Onboarding et import de données.

Sprint 2: Import asynchrone de données Excel avec tracking de progression.
"""
import logging
from datetime import datetime
from typing import Dict
from uuid import UUID

import pandas as pd
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.category import Category
from app.models.import_job import ImportJob
from app.models.onboarding import OnboardingSession
from app.models.product import Product
from app.models.sale import Sale
from app.models.supplier import Supplier
from app.models.tenant import Tenant
from app.services.import_service import ImportService
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.tasks.onboarding.import_tenant_data")
def import_tenant_data(self, import_job_id: str, file_path: str):
    """
    Tâche Celery d'import asynchrone de données tenant depuis Excel.

    Phases:
    1. Validation fichier (0-25%)
    2. Parsing données (25-50%)
    3. Import produits (50-75%)
    4. Import ventes (75-90%)
    5. Post-processing (90-100%)

    Args:
        import_job_id: ID de l'ImportJob
        file_path: Chemin vers le fichier Excel

    Returns:
        Dict avec stats d'import
    """
    db: Session = SessionLocal()

    try:
        # Récupérer ImportJob
        import_job = db.query(ImportJob).filter(ImportJob.id == import_job_id).first()
        if not import_job:
            raise ValueError(f"ImportJob {import_job_id} introuvable")

        tenant_id = import_job.tenant_id

        # Phase 1: Validation (0-25%)
        logger.info(f"[Import {import_job_id}] Phase 1: Validation")
        _update_progress(db, import_job, 10, "Validation de la structure du fichier...")

        import_service = ImportService(db)
        is_valid, report = import_service.validate_excel_file(file_path, tenant_id)

        if not is_valid:
            _fail_import(db, import_job, report)
            return {"status": "failed", "errors": report["errors"]}

        _update_progress(db, import_job, 25, "Validation réussie, parsing des données...")

        # Phase 2: Parsing (25-50%)
        logger.info(f"[Import {import_job_id}] Phase 2: Parsing")
        df_products = pd.read_excel(file_path, sheet_name="Produits")
        df_products.columns = [col.replace("*", "").strip() for col in df_products.columns]

        df_sales = None
        try:
            df_sales = pd.read_excel(file_path, sheet_name="Ventes")
            if not df_sales.empty:
                df_sales.columns = [col.replace("*", "").strip() for col in df_sales.columns]
        except Exception:
            pass  # Ventes optionnelles

        _update_progress(db, import_job, 50, f"Import de {len(df_products)} produits...")

        # Phase 3: Import Produits (50-75%)
        logger.info(f"[Import {import_job_id}] Phase 3: Import produits")
        products_imported = _import_products(db, df_products, tenant_id)

        _update_progress(db, import_job, 75, f"{products_imported} produits importés, import des ventes...")

        # Phase 4: Import Ventes (75-90%)
        sales_imported = 0
        if df_sales is not None and not df_sales.empty:
            logger.info(f"[Import {import_job_id}] Phase 4: Import ventes")
            sales_imported = _import_sales(db, df_sales, tenant_id)

        _update_progress(db, import_job, 90, "Post-processing...")

        # Phase 5: Post-processing (90-100%)
        logger.info(f"[Import {import_job_id}] Phase 5: Post-processing")
        _post_process(db, tenant_id)

        # Succès
        stats = {
            "products_imported": products_imported,
            "sales_imported": sales_imported,
            "completed_at": datetime.utcnow().isoformat(),
        }

        import_job.status = "success"
        import_job.progress_percent = 100
        import_job.stats = stats
        import_job.completed_at = datetime.utcnow()
        db.commit()

        logger.info(f"[Import {import_job_id}] Terminé avec succès")
        return {"status": "success", "stats": stats}

    except Exception as e:
        logger.error(f"[Import {import_job_id}] Erreur: {str(e)}", exc_info=True)
        if import_job:
            _fail_import(db, import_job, {"error": str(e)})
        raise

    finally:
        db.close()


def _import_products(db: Session, df: pd.DataFrame, tenant_id: UUID) -> int:
    """Importer produits en batch."""
    count = 0
    batch_size = 100

    # Créer catégories/fournisseurs manquants
    categories_map = _ensure_categories(db, df["Catégorie"].dropna().unique(), tenant_id)
    suppliers_map = _ensure_suppliers(db, df["Fournisseur"].dropna().unique(), tenant_id)

    products = []
    for _, row in df.iterrows():
        if pd.isna(row.get("Code")):
            continue

        product = Product(
            tenant_id=tenant_id,
            code=str(row["Code"]).strip(),
            name=str(row["Nom"]).strip(),
            category_id=categories_map.get(row.get("Catégorie")),
            supplier_id=suppliers_map.get(row.get("Fournisseur")),
            purchase_price=float(row["Prix Achat"]),
            sale_price=float(row["Prix Vente"]),
            unit=str(row["Unité"]).strip() if not pd.isna(row.get("Unité")) else "unité",
            current_stock=int(row["Stock Initial"]),
            min_stock=int(row.get("Stock Min", 0)),
            max_stock=int(row.get("Stock Max", 100)),
            description=str(row.get("Description", "")).strip() or None,
            barcode=str(row.get("Code-barres", "")).strip() or None,
            is_active=True,
        )
        products.append(product)
        count += 1

        if len(products) >= batch_size:
            db.bulk_save_objects(products)
            db.commit()
            products = []

    if products:
        db.bulk_save_objects(products)
        db.commit()

    return count


def _import_sales(db: Session, df: pd.DataFrame, tenant_id: UUID) -> int:
    """Importer ventes en batch."""
    count = 0
    batch_size = 1000

    # Mapper codes produits → product_id
    products = db.query(Product).filter(Product.tenant_id == tenant_id).all()
    product_map = {p.code: p.id for p in products}

    sales = []
    for _, row in df.iterrows():
        code = str(row.get("Code Produit", "")).strip()
        product_id = product_map.get(code)

        if not product_id:
            continue  # Skip si produit inexistant

        try:
            sale_date = pd.to_datetime(row["Date Vente"])
        except Exception:
            continue  # Skip si date invalide

        sale = Sale(
            tenant_id=tenant_id,
            product_id=product_id,
            sale_date=sale_date,
            quantity=int(row["Quantité"]),
            unit_price=float(row["Prix Unitaire"]),
            total_amount=float(row["Quantité"]) * float(row["Prix Unitaire"]),
        )
        sales.append(sale)
        count += 1

        if len(sales) >= batch_size:
            db.bulk_save_objects(sales)
            db.commit()
            sales = []

    if sales:
        db.bulk_save_objects(sales)
        db.commit()

    return count


def _ensure_categories(db: Session, names: list, tenant_id: UUID) -> Dict[str, UUID]:
    """Créer catégories manquantes et retourner mapping."""
    existing = db.query(Category).filter(Category.tenant_id == tenant_id).all()
    categories_map = {c.name: c.id for c in existing}

    for name in names:
        if pd.isna(name):
            continue
        name = str(name).strip()
        if name not in categories_map:
            cat = Category(tenant_id=tenant_id, name=name)
            db.add(cat)
            db.flush()
            categories_map[name] = cat.id

    db.commit()
    return categories_map


def _ensure_suppliers(db: Session, names: list, tenant_id: UUID) -> Dict[str, UUID]:
    """Créer fournisseurs manquants et retourner mapping."""
    existing = db.query(Supplier).filter(Supplier.tenant_id == tenant_id).all()
    suppliers_map = {s.name: s.id for s in existing}

    for name in names:
        if pd.isna(name):
            continue
        name = str(name).strip()
        if name not in suppliers_map:
            sup = Supplier(tenant_id=tenant_id, name=name, code=name[:10].upper())
            db.add(sup)
            db.flush()
            suppliers_map[name] = sup.id

    db.commit()
    return suppliers_map


def _post_process(db: Session, tenant_id: UUID):
    """Post-processing après import."""
    # Activer le tenant
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if tenant:
        tenant.is_active = True

    # Compléter session onboarding
    session = (
        db.query(OnboardingSession)
        .filter(OnboardingSession.tenant_id == tenant_id)
        .order_by(OnboardingSession.created_at.desc())
        .first()
    )
    if session:
        session.status = "completed"
        session.current_step = 4
        session.completed_at = datetime.utcnow()

    db.commit()

    # TODO Sprint 3: Refresh materialized views
    # db.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_dashboard_stock_health")


def _update_progress(db: Session, import_job: ImportJob, percent: int, message: str):
    """Mettre à jour progression."""
    import_job.progress_percent = percent
    import_job.stats = import_job.stats or {}
    import_job.stats["current_message"] = message
    db.commit()
    logger.info(f"[Import {import_job.id}] {percent}% - {message}")


def _fail_import(db: Session, import_job: ImportJob, error_details: Dict):
    """Marquer import comme échoué."""
    import_job.status = "failed"
    import_job.error_details = error_details
    import_job.completed_at = datetime.utcnow()
    db.commit()
    logger.error(f"[Import {import_job.id}] Échoué: {error_details}")
