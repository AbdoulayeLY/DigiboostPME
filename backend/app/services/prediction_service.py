"""
Service Prédictions & Recommandations - Anticiper les ruptures de stock.

Ce service fournit des prédictions et recommandations pour optimiser la gestion du stock :
- Prédiction de date de rupture de stock
- Calcul de quantité de réapprovisionnement
- Liste des ruptures prévues dans les X prochains jours
- Recommandations d'achat groupées par fournisseur
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from uuid import UUID
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import math

from app.models.product import Product
from app.models.sale import Sale
from app.models.supplier import Supplier


class PredictionService:
    """Service pour les prédictions et recommandations d'achat."""

    def __init__(self, db: Session):
        self.db = db

    def predict_rupture_date(
        self,
        tenant_id: UUID,
        product_id: UUID
    ) -> Optional[datetime]:
        """
        Prédire la date de rupture de stock basée sur :
        - Stock actuel
        - Ventes moyennes quotidiennes (30 derniers jours)

        Retourne None si :
        - Produit déjà en rupture
        - Pas d'historique de ventes
        - Stock suffisant (>30 jours de couverture)
        """
        product = self.db.query(Product).filter(
            Product.id == product_id,
            Product.tenant_id == tenant_id
        ).first()

        if not product or product.current_stock <= 0:
            return None

        # Ventes moyennes quotidiennes sur 30 derniers jours
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        # Calculer la moyenne quotidienne des ventes
        daily_sales = self.db.query(
            func.date(Sale.sale_date).label('sale_day'),
            func.sum(Sale.quantity).label('daily_quantity')
        ).filter(
            and_(
                Sale.product_id == product_id,
                Sale.sale_date >= thirty_days_ago
            )
        ).group_by(
            func.date(Sale.sale_date)
        ).all()

        if not daily_sales:
            return None

        # Calculer la moyenne
        total_quantity = sum(float(day.daily_quantity) for day in daily_sales)
        avg_daily_sales = total_quantity / len(daily_sales)

        if avg_daily_sales <= 0:
            return None

        # Jours jusqu'à rupture
        days_until_rupture = float(product.current_stock) / avg_daily_sales

        # Si >30 jours, pas d'alerte
        if days_until_rupture > 30:
            return None

        rupture_date = datetime.utcnow() + timedelta(days=days_until_rupture)
        return rupture_date

    def calculate_reorder_quantity(
        self,
        tenant_id: UUID,
        product_id: UUID,
        target_days: int = 15
    ) -> Optional[Dict[str, Any]]:
        """
        Calculer la quantité à commander pour couvrir X jours.

        Formule :
        Qté = (Vente moyenne quotidienne × Jours cible) - Stock actuel + Stock sécurité

        Args:
            tenant_id: UUID du tenant
            product_id: UUID du produit
            target_days: Nombre de jours de couverture souhaité (défaut: 15)
        """
        product = self.db.query(Product).filter(
            Product.id == product_id,
            Product.tenant_id == tenant_id
        ).first()

        if not product:
            return None

        # Ventes sur 30 derniers jours
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        sales_data = self.db.query(
            func.sum(Sale.quantity).label('total'),
            func.count(func.distinct(func.date(Sale.sale_date))).label('days')
        ).filter(
            and_(
                Sale.product_id == product_id,
                Sale.sale_date >= thirty_days_ago
            )
        ).first()

        if not sales_data or not sales_data.total:
            # Pas d'historique : commander stock minimum
            return {
                "product_id": str(product_id),
                "product_name": product.name,
                "current_stock": float(product.current_stock),
                "recommended_quantity": float(product.min_stock or 0),
                "rationale": "NO_HISTORY",
                "target_days": None,
                "avg_daily_sales": 0
            }

        # Calculer moyenne quotidienne
        avg_daily_sales = float(sales_data.total) / max(sales_data.days, 1)

        # Stock sécurité = stock minimum
        safety_stock = float(product.min_stock or 0)

        # Quantité nécessaire
        needed_quantity = (avg_daily_sales * target_days) - float(product.current_stock) + safety_stock

        # Arrondir au-dessus
        needed_quantity = math.ceil(needed_quantity)

        # Minimum = 0
        needed_quantity = max(0, needed_quantity)

        return {
            "product_id": str(product_id),
            "product_name": product.name,
            "current_stock": float(product.current_stock),
            "avg_daily_sales": round(avg_daily_sales, 2),
            "target_days": target_days,
            "recommended_quantity": needed_quantity,
            "safety_stock": safety_stock,
            "rationale": "NORMAL"
        }

    def get_ruptures_prevues(
        self,
        tenant_id: UUID,
        horizon_days: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Liste des ruptures prévues dans les X prochains jours.

        Args:
            tenant_id: UUID du tenant
            horizon_days: Horizon de prédiction en jours (défaut: 15)

        Retourne une liste triée par urgence (date de rupture proche).
        """
        # Récupérer tous produits actifs avec stock > 0
        products = self.db.query(Product).filter(
            and_(
                Product.tenant_id == tenant_id,
                Product.is_active == True,
                Product.current_stock > 0
            )
        ).all()

        ruptures = []
        cutoff_date = datetime.utcnow() + timedelta(days=horizon_days)

        for product in products:
            rupture_date = self.predict_rupture_date(tenant_id, product.id)

            if rupture_date and rupture_date <= cutoff_date:
                # Calculer quantité recommandée
                reorder = self.calculate_reorder_quantity(tenant_id, product.id)

                days_until_rupture = (rupture_date - datetime.utcnow()).days

                rupture_data = {
                    "product_id": str(product.id),
                    "product_code": product.code,
                    "product_name": product.name,
                    "current_stock": float(product.current_stock),
                    "min_stock": float(product.min_stock or 0),
                    "predicted_rupture_date": rupture_date.isoformat(),
                    "days_until_rupture": days_until_rupture,
                    "recommended_quantity": reorder["recommended_quantity"] if reorder else 0,
                    "supplier": None
                }

                # Ajouter info fournisseur si disponible
                if product.supplier_id:
                    supplier = self.db.query(Supplier).filter(
                        Supplier.id == product.supplier_id
                    ).first()

                    if supplier:
                        rupture_data["supplier"] = {
                            "id": str(supplier.id),
                            "name": supplier.name,
                            "lead_time_days": supplier.lead_time_days or 7
                        }

                ruptures.append(rupture_data)

        # Trier par urgence (date rupture proche = plus urgent)
        ruptures.sort(key=lambda x: x["days_until_rupture"])

        return ruptures

    def get_recommandations_achat(
        self,
        tenant_id: UUID,
        horizon_days: int = 15
    ) -> Dict[str, Any]:
        """
        Recommandations d'achat groupées par fournisseur.

        Facilite la création de bons de commande en regroupant
        les produits par fournisseur.

        Args:
            tenant_id: UUID du tenant
            horizon_days: Horizon de prédiction en jours

        Retourne :
        - by_supplier : Liste des commandes groupées par fournisseur
        - without_supplier : Liste des produits sans fournisseur
        - total_products : Nombre total de produits à commander
        - total_suppliers : Nombre de fournisseurs concernés
        """
        ruptures = self.get_ruptures_prevues(tenant_id, horizon_days)

        # Grouper par fournisseur
        by_supplier = {}
        no_supplier = []

        for rupture in ruptures:
            if rupture["supplier"]:
                supplier_id = rupture["supplier"]["id"]

                if supplier_id not in by_supplier:
                    by_supplier[supplier_id] = {
                        "supplier_id": supplier_id,
                        "supplier_name": rupture["supplier"]["name"],
                        "lead_time_days": rupture["supplier"]["lead_time_days"],
                        "products": []
                    }

                # Déterminer urgence
                urgency = "HIGH" if rupture["days_until_rupture"] < 7 else "MEDIUM"

                by_supplier[supplier_id]["products"].append({
                    "product_id": rupture["product_id"],
                    "product_code": rupture["product_code"],
                    "product_name": rupture["product_name"],
                    "quantity": rupture["recommended_quantity"],
                    "urgency": urgency,
                    "days_until_rupture": rupture["days_until_rupture"]
                })
            else:
                no_supplier.append(rupture)

        return {
            "by_supplier": list(by_supplier.values()),
            "without_supplier": no_supplier,
            "total_products": len(ruptures),
            "total_suppliers": len(by_supplier)
        }
