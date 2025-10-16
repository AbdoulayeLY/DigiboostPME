"""
Service pour les dashboards et KPIs.
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from uuid import UUID
from typing import Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal


class DashboardService:
    """Service pour generer les donnees des dashboards."""

    def __init__(self, db: Session):
        self.db = db

    def get_overview(self, tenant_id: UUID) -> Dict[str, Any]:
        """
        Dashboard Vue d'Ensemble complet.

        Args:
            tenant_id: UUID du tenant

        Returns:
            Dict contenant toutes les donnees du dashboard
        """
        return {
            "stock_health": self._get_stock_health(tenant_id),
            "sales_performance": self._get_sales_performance(tenant_id),
            "top_products": self._get_top_products(tenant_id, limit=5),
            "dormant_products": self._get_dormant_products(tenant_id, limit=5),
            "kpis": {
                "taux_service": self._get_taux_service(tenant_id)
            },
            "generated_at": datetime.utcnow().isoformat()
        }

    def _get_stock_health(self, tenant_id: UUID) -> Dict[str, Any]:
        """
        Sante stock depuis vue materialisee.

        Args:
            tenant_id: UUID du tenant

        Returns:
            Dict avec total_products, rupture_count, low_stock_count, etc.
        """
        query = text("""
            SELECT
                total_products,
                rupture_count,
                low_stock_count,
                total_stock_value
            FROM mv_dashboard_stock_health
            WHERE tenant_id = :tenant_id
        """)

        result = self.db.execute(query, {"tenant_id": str(tenant_id)}).first()

        if not result:
            return {
                "total_products": 0,
                "rupture_count": 0,
                "low_stock_count": 0,
                "alert_count": 0,
                "total_stock_value": 0.0
            }

        return {
            "total_products": result.total_products or 0,
            "rupture_count": result.rupture_count or 0,
            "low_stock_count": result.low_stock_count or 0,
            "alert_count": (result.rupture_count or 0) + (result.low_stock_count or 0),
            "total_stock_value": float(result.total_stock_value or 0)
        }

    def _get_sales_performance(self, tenant_id: UUID) -> Dict[str, Any]:
        """
        Performance ventes 7j et 30j.

        Args:
            tenant_id: UUID du tenant

        Returns:
            Dict avec CA 7j, CA 30j, evolution, nombre ventes
        """
        query = text("""
            SELECT
                SUM(CASE WHEN sale_day >= CURRENT_DATE - INTERVAL '7 days' THEN daily_revenue ELSE 0 END) as ca_7j,
                SUM(CASE WHEN sale_day >= CURRENT_DATE - INTERVAL '30 days' THEN daily_revenue ELSE 0 END) as ca_30j,
                SUM(CASE WHEN sale_day >= CURRENT_DATE - INTERVAL '7 days' THEN transactions_count ELSE 0 END) as ventes_7j,
                SUM(CASE WHEN sale_day >= CURRENT_DATE - INTERVAL '30 days' THEN transactions_count ELSE 0 END) as ventes_30j,
                SUM(CASE WHEN sale_day >= CURRENT_DATE - INTERVAL '14 days' AND sale_day < CURRENT_DATE - INTERVAL '7 days' THEN daily_revenue ELSE 0 END) as ca_7j_previous
            FROM mv_dashboard_sales_performance
            WHERE tenant_id = :tenant_id
        """)

        result = self.db.execute(query, {"tenant_id": str(tenant_id)}).first()

        if not result:
            return {
                "ca_7j": 0.0,
                "ca_30j": 0.0,
                "evolution_ca": 0.0,
                "ventes_7j": 0,
                "ventes_30j": 0
            }

        ca_7j = float(result.ca_7j or 0)
        ca_7j_previous = float(result.ca_7j_previous or 0)

        # Calcul evolution (% variation)
        if ca_7j_previous > 0:
            evolution_ca = ((ca_7j - ca_7j_previous) / ca_7j_previous) * 100
        else:
            evolution_ca = 100.0 if ca_7j > 0 else 0.0

        return {
            "ca_7j": ca_7j,
            "ca_30j": float(result.ca_30j or 0),
            "evolution_ca": round(evolution_ca, 2),
            "ventes_7j": result.ventes_7j or 0,
            "ventes_30j": result.ventes_30j or 0
        }

    def _get_top_products(self, tenant_id: UUID, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Top produits par CA sur 30 derniers jours.

        Args:
            tenant_id: UUID du tenant
            limit: Nombre de produits a retourner

        Returns:
            Liste des top produits
        """
        query = text("""
            SELECT
                p.id,
                p.name,
                p.code,
                SUM(s.total_amount) as total_revenue,
                SUM(s.quantity) as total_quantity
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE s.tenant_id = :tenant_id
                AND s.sale_date >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY p.id, p.name, p.code
            ORDER BY total_revenue DESC
            LIMIT :limit
        """)

        results = self.db.execute(
            query,
            {"tenant_id": str(tenant_id), "limit": limit}
        ).fetchall()

        return [
            {
                "product_id": str(row.id),
                "product_name": row.name,
                "product_code": row.code,
                "total_revenue": float(row.total_revenue),
                "total_quantity": float(row.total_quantity)
            }
            for row in results
        ]

    def _get_dormant_products(self, tenant_id: UUID, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Produits dormants (pas de vente 30j + stock > 0).

        Args:
            tenant_id: UUID du tenant
            limit: Nombre de produits a retourner

        Returns:
            Liste des produits dormants
        """
        query = text("""
            SELECT
                p.id,
                p.name,
                p.code,
                p.current_stock,
                p.purchase_price
            FROM products p
            WHERE p.tenant_id = :tenant_id
                AND p.is_active = TRUE
                AND p.current_stock > 0
                AND NOT EXISTS (
                    SELECT 1 FROM sales s
                    WHERE s.product_id = p.id
                        AND s.sale_date >= CURRENT_DATE - INTERVAL '30 days'
                )
            ORDER BY (p.current_stock * p.purchase_price) DESC
            LIMIT :limit
        """)

        results = self.db.execute(
            query,
            {"tenant_id": str(tenant_id), "limit": limit}
        ).fetchall()

        return [
            {
                "product_id": str(row.id),
                "product_name": row.name,
                "product_code": row.code,
                "current_stock": float(row.current_stock),
                "immobilized_value": float(row.current_stock * row.purchase_price)
            }
            for row in results
        ]

    def _get_taux_service(self, tenant_id: UUID) -> float:
        """
        Taux de service via fonction SQL.

        Args:
            tenant_id: UUID du tenant

        Returns:
            Taux de service en pourcentage
        """
        query = text("SELECT fn_calc_taux_service(:tenant_id, 30)")
        result = self.db.execute(query, {"tenant_id": str(tenant_id)}).scalar()
        return float(result or 100.0)

    def refresh_views(self) -> Dict[str, str]:
        """
        Rafraichir les vues materialisees.

        Returns:
            Dict avec statut du rafraichissement
        """
        try:
            self.db.execute(text("REFRESH MATERIALIZED VIEW mv_dashboard_stock_health"))
            self.db.execute(text("REFRESH MATERIALIZED VIEW mv_dashboard_sales_performance"))
            self.db.commit()
            return {"status": "success", "message": "Vues rafraichies"}
        except Exception as e:
            self.db.rollback()
            return {"status": "error", "message": str(e)}
