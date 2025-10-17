"""
Service Analytics Avancé - Analyses et KPIs détaillés.

Ce service fournit des analyses avancées sur les produits, ventes et catégories :
- Analyse détaillée par produit (stock, ventes, métriques)
- Évolution des ventes quotidiennes
- Top/Flop produits
- Performance par catégorie
- Classification ABC des produits
"""
from sqlalchemy.orm import Session
from sqlalchemy import text, func, and_
from uuid import UUID
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from app.models.product import Product
from app.models.sale import Sale
from app.models.category import Category


class AnalyticsService:
    """Service pour les analyses avancées et KPIs."""

    def __init__(self, db: Session):
        self.db = db

    def get_product_analysis(
        self,
        tenant_id: UUID,
        product_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Analyse détaillée d'un produit.

        Retourne :
        - Stock actuel et historique
        - Ventes 30/90 jours
        - Rotation stock
        - Couverture jours
        - Marge moyenne
        """
        product = self.db.query(Product).filter(
            Product.id == product_id,
            Product.tenant_id == tenant_id
        ).first()

        if not product:
            return None

        # Ventes 30 derniers jours
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        sales_30d = self.db.query(
            func.count(Sale.id).label('count'),
            func.sum(Sale.quantity).label('total_quantity'),
            func.sum(Sale.total_amount).label('total_revenue')
        ).filter(
            and_(
                Sale.product_id == product_id,
                Sale.sale_date >= thirty_days_ago
            )
        ).first()

        # Ventes 90 derniers jours
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)
        sales_90d = self.db.query(
            func.count(Sale.id).label('count'),
            func.sum(Sale.quantity).label('total_quantity')
        ).filter(
            and_(
                Sale.product_id == product_id,
                Sale.sale_date >= ninety_days_ago
            )
        ).first()

        # Calcul métriques
        avg_daily_sales_30d = float(sales_30d.total_quantity or 0) / 30
        avg_daily_sales_90d = float(sales_90d.total_quantity or 0) / 90

        # Couverture stock (jours)
        coverage_days = None
        if avg_daily_sales_30d > 0:
            coverage_days = float(product.current_stock) / avg_daily_sales_30d

        # Rotation stock (fois/an)
        rotation_annual = None
        if product.current_stock > 0 and avg_daily_sales_90d > 0:
            rotation_annual = (avg_daily_sales_90d * 365) / float(product.current_stock)

        # Marge
        margin = float(product.sale_price) - float(product.purchase_price)
        margin_percent = (margin / float(product.purchase_price) * 100) if product.purchase_price > 0 else 0

        return {
            "product": {
                "id": str(product.id),
                "code": product.code,
                "name": product.name,
                "current_stock": float(product.current_stock),
                "min_stock": float(product.min_stock or 0),
                "max_stock": float(product.max_stock or 0),
                "purchase_price": float(product.purchase_price),
                "sale_price": float(product.sale_price),
                "unit": product.unit
            },
            "sales": {
                "last_30_days": {
                    "transactions": sales_30d.count or 0,
                    "quantity": float(sales_30d.total_quantity or 0),
                    "revenue": float(sales_30d.total_revenue or 0),
                    "avg_daily": round(avg_daily_sales_30d, 2)
                },
                "last_90_days": {
                    "transactions": sales_90d.count or 0,
                    "quantity": float(sales_90d.total_quantity or 0),
                    "avg_daily": round(avg_daily_sales_90d, 2)
                }
            },
            "metrics": {
                "coverage_days": round(coverage_days, 1) if coverage_days else None,
                "rotation_annual": round(rotation_annual, 2) if rotation_annual else None,
                "margin": float(margin),
                "margin_percent": round(margin_percent, 2)
            },
            "status": self._calculate_stock_status(product, coverage_days)
        }

    def _calculate_stock_status(
        self,
        product: Product,
        coverage_days: Optional[float]
    ) -> str:
        """Calculer statut stock."""
        if product.current_stock == 0:
            return "RUPTURE"
        elif product.min_stock and product.current_stock <= product.min_stock:
            return "FAIBLE"
        elif coverage_days and coverage_days < 7:
            return "ALERTE"
        elif product.max_stock and product.current_stock >= product.max_stock:
            return "SURSTOCK"
        else:
            return "NORMAL"

    def get_sales_evolution(
        self,
        tenant_id: UUID,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Évolution CA quotidienne sur X jours.

        Retourne une liste de données quotidiennes avec :
        - date
        - transactions
        - revenue (CA)
        - units_sold
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        query = text("""
            SELECT
                DATE(sale_date) as date,
                COUNT(*) as transactions,
                SUM(total_amount) as revenue,
                SUM(quantity) as units_sold
            FROM sales
            WHERE tenant_id = :tenant_id
                AND sale_date >= :start_date
            GROUP BY DATE(sale_date)
            ORDER BY date ASC
        """)

        results = self.db.execute(query, {
            "tenant_id": str(tenant_id),
            "start_date": start_date
        }).fetchall()

        return [
            {
                "date": row.date.isoformat(),
                "transactions": row.transactions,
                "revenue": float(row.revenue),
                "units_sold": float(row.units_sold)
            }
            for row in results
        ]

    def get_top_products(
        self,
        tenant_id: UUID,
        limit: int = 10,
        days: int = 30,
        order_by: str = "revenue"  # revenue, quantity, transactions
    ) -> List[Dict[str, Any]]:
        """
        Top produits par CA, quantité ou nombre de transactions.

        Args:
            tenant_id: UUID du tenant
            limit: Nombre de produits à retourner
            days: Période d'analyse en jours
            order_by: Critère de tri (revenue, quantity, transactions)
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        order_clause = {
            "revenue": "SUM(s.total_amount) DESC",
            "quantity": "SUM(s.quantity) DESC",
            "transactions": "COUNT(s.id) DESC"
        }.get(order_by, "SUM(s.total_amount) DESC")

        query = text(f"""
            SELECT
                p.id,
                p.code,
                p.name,
                p.unit,
                p.current_stock,
                p.min_stock,
                p.max_stock,
                c.name as category_name,
                COUNT(s.id) as transactions,
                SUM(s.quantity) as quantity_sold,
                SUM(s.total_amount) as revenue,
                AVG(s.unit_price) as avg_price
            FROM products p
            LEFT JOIN sales s ON p.id = s.product_id AND s.sale_date >= :start_date
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.tenant_id = :tenant_id
                AND s.id IS NOT NULL
            GROUP BY p.id, p.code, p.name, p.unit, p.current_stock, p.min_stock, p.max_stock, c.name
            ORDER BY {order_clause}
            LIMIT :limit
        """)

        results = self.db.execute(query, {
            "tenant_id": str(tenant_id),
            "start_date": start_date,
            "limit": limit
        }).fetchall()

        products_with_status = []
        for row in results:
            # Calcul couverture en jours
            avg_daily_sales = float(row.quantity_sold) / days
            coverage_days = None
            if avg_daily_sales > 0:
                coverage_days = float(row.current_stock) / avg_daily_sales

            # Calcul statut basé sur la logique officielle
            status = self._calculate_stock_status_simple(
                current_stock=float(row.current_stock),
                min_stock=float(row.min_stock or 0),
                max_stock=float(row.max_stock or 0),
                coverage_days=coverage_days
            )

            products_with_status.append({
                "product_id": str(row.id),
                "code": row.code,
                "name": row.name,
                "unit": row.unit,
                "current_stock": float(row.current_stock),
                "category": row.category_name,
                "transactions": row.transactions,
                "quantity": float(row.quantity_sold),
                "revenue": float(row.revenue),
                "avg_price": float(row.avg_price or 0),
                "coverage_days": round(coverage_days, 1) if coverage_days else None,
                "status": status
            })

        return products_with_status

    def _calculate_stock_status_simple(
        self,
        current_stock: float,
        min_stock: float,
        max_stock: float,
        coverage_days: Optional[float]
    ) -> str:
        """Calculer statut stock (version simplifiée sans objet Product)."""
        if current_stock == 0:
            return "RUPTURE"
        elif min_stock > 0 and current_stock <= min_stock:
            return "FAIBLE"
        elif coverage_days and coverage_days < 7:
            return "ALERTE"
        elif max_stock > 0 and current_stock >= max_stock:
            return "SURSTOCK"
        else:
            return "NORMAL"

    def get_category_performance(
        self,
        tenant_id: UUID,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Performance par catégorie.

        Retourne statistiques pour chaque catégorie :
        - Nombre de produits
        - Transactions
        - Quantité vendue
        - Chiffre d'affaires
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        query = text("""
            SELECT
                c.id,
                c.name,
                COUNT(DISTINCT p.id) as product_count,
                COUNT(s.id) as transactions,
                SUM(s.quantity) as quantity_sold,
                SUM(s.total_amount) as revenue,
                AVG(s.unit_price) as avg_price
            FROM categories c
            LEFT JOIN products p ON c.id = p.category_id
            LEFT JOIN sales s ON p.id = s.product_id AND s.sale_date >= :start_date
            WHERE c.tenant_id = :tenant_id
            GROUP BY c.id, c.name
            ORDER BY revenue DESC NULLS LAST
        """)

        results = self.db.execute(query, {
            "tenant_id": str(tenant_id),
            "start_date": start_date
        }).fetchall()

        return [
            {
                "category_id": str(row.id),
                "category_name": row.name,
                "product_count": row.product_count,
                "transactions": row.transactions or 0,
                "quantity_sold": float(row.quantity_sold or 0),
                "revenue": float(row.revenue or 0),
                "avg_price": float(row.avg_price or 0)
            }
            for row in results
        ]

    def classify_products_abc(
        self,
        tenant_id: UUID,
        days: int = 90
    ) -> Dict[str, List[str]]:
        """
        Classification ABC des produits selon la méthode Pareto.

        Méthode ABC :
        - Classe A : 80% du CA (environ 20% des produits)
        - Classe B : 15% du CA (environ 30% des produits)
        - Classe C : 5% du CA (environ 50% des produits)

        Retourne un dictionnaire avec les listes de product_id par classe.
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        # Récupérer tous produits avec CA
        query = text("""
            SELECT
                p.id,
                p.name,
                COALESCE(SUM(s.total_amount), 0) as revenue
            FROM products p
            LEFT JOIN sales s ON p.id = s.product_id AND s.sale_date >= :start_date
            WHERE p.tenant_id = :tenant_id
                AND p.is_active = TRUE
            GROUP BY p.id, p.name
            ORDER BY revenue DESC
        """)

        results = self.db.execute(query, {
            "tenant_id": str(tenant_id),
            "start_date": start_date
        }).fetchall()

        if not results:
            return {"A": [], "B": [], "C": []}

        # Calculer CA total
        total_revenue = sum(float(row.revenue) for row in results)

        # Classification
        classification = {"A": [], "B": [], "C": []}
        cumulative_revenue = 0
        cumulative_percent = 0

        for row in results:
            cumulative_revenue += float(row.revenue)
            cumulative_percent = (cumulative_revenue / total_revenue * 100) if total_revenue > 0 else 0

            if cumulative_percent <= 80:
                classification["A"].append(str(row.id))
            elif cumulative_percent <= 95:
                classification["B"].append(str(row.id))
            else:
                classification["C"].append(str(row.id))

        return classification
