# PROMPTS CLAUDE CODE - SPRINT 3
## Analyses & Prédictions (Semaines 5-6)

**Objectif Sprint** : Dashboards avancés + Prédictions ruptures stock  
**Valeur Métier** : Analyser données & anticiper problèmes  
**Durée** : 2 semaines (80 heures)

---

## 📋 TABLE DES MATIÈRES

1. [Vue d'Ensemble Sprint 3](#vue-densemble-sprint-3)
2. [Semaine 5 : Backend Analytics & Prédictions](#semaine-5--backend-analytics--prédictions)
3. [Semaine 6 : Frontend Dashboards Avancés](#semaine-6--frontend-dashboards-avancés)

---

## VUE D'ENSEMBLE SPRINT 3

### Fonctionnalités à Implémenter

**3 Nouveaux Dashboards** :
1. **Gestion Stock Détaillée** : Liste produits avec filtres avancés
2. **Analyse Ventes** : Évolution CA, top produits, catégories
3. **Prédictions & Recommandations** : Ruptures prévues + quantités à commander

**Backend** :
- Service analytics avancé
- Fonctions prédiction ruptures
- Calcul quantités réapprovisionnement
- Analyse ABC produits
- Statistiques ventes par catégorie

**Frontend** :
- 3 pages dashboard interactives
- Graphiques avancés (Recharts)
- Filtres dynamiques
- Tableaux triables
- Export données

---

## SEMAINE 5 : BACKEND ANALYTICS & PRÉDICTIONS

### 🔧 PROMPT 3.1 : Service Analytics Avancé

```
CONTEXTE:
Les dashboards de base et alerting fonctionnent. Je dois créer un service analytics avancé pour les dashboards détaillés et analyses ventes.

OBJECTIF:
Créer service AnalyticsService avec:
- Analyse détaillée produits (stock, ventes, marges)
- Statistiques ventes (évolution, tendances)
- Top/Flop produits
- Analyse par catégorie
- Classification ABC produits

SPÉCIFICATIONS TECHNIQUES:

SERVICE ANALYTICS (app/services/analytics_service.py):
```python
from sqlalchemy.orm import Session
from sqlalchemy import text, func, and_, or_
from uuid import UUID
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.models.product import Product
from app.models.sale import Sale
from app.models.category import Category

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_product_analysis(
        self,
        tenant_id: UUID,
        product_id: UUID
    ) -> Dict[str, Any]:
        """
        Analyse détaillée d'un produit
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
            coverage_days = product.current_stock / avg_daily_sales_30d
        
        # Rotation stock (fois/an)
        rotation_annual = None
        if product.current_stock > 0 and avg_daily_sales_90d > 0:
            rotation_annual = (avg_daily_sales_90d * 365) / product.current_stock
        
        # Marge
        margin = product.sale_price - product.purchase_price
        margin_percent = (margin / product.purchase_price * 100) if product.purchase_price > 0 else 0
        
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
        """Calculer statut stock"""
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
        Évolution CA quotidienne
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
            "tenant_id": tenant_id,
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
        Top produits par CA, quantité ou nombre transactions
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
                c.name as category_name,
                COUNT(s.id) as transactions,
                SUM(s.quantity) as quantity_sold,
                SUM(s.total_amount) as revenue
            FROM products p
            LEFT JOIN sales s ON p.id = s.product_id AND s.sale_date >= :start_date
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.tenant_id = :tenant_id
                AND s.id IS NOT NULL
            GROUP BY p.id, p.code, p.name, p.unit, c.name
            ORDER BY {order_clause}
            LIMIT :limit
        """)
        
        results = self.db.execute(query, {
            "tenant_id": tenant_id,
            "start_date": start_date,
            "limit": limit
        }).fetchall()
        
        return [
            {
                "product_id": str(row.id),
                "code": row.code,
                "name": row.name,
                "unit": row.unit,
                "category": row.category_name,
                "transactions": row.transactions,
                "quantity_sold": float(row.quantity_sold),
                "revenue": float(row.revenue)
            }
            for row in results
        ]
    
    def get_category_performance(
        self,
        tenant_id: UUID,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Performance par catégorie
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = text("""
            SELECT 
                c.id,
                c.name,
                COUNT(DISTINCT p.id) as product_count,
                COUNT(s.id) as transactions,
                SUM(s.quantity) as quantity_sold,
                SUM(s.total_amount) as revenue
            FROM categories c
            LEFT JOIN products p ON c.id = p.category_id
            LEFT JOIN sales s ON p.id = s.product_id AND s.sale_date >= :start_date
            WHERE c.tenant_id = :tenant_id
            GROUP BY c.id, c.name
            ORDER BY revenue DESC NULLS LAST
        """)
        
        results = self.db.execute(query, {
            "tenant_id": tenant_id,
            "start_date": start_date
        }).fetchall()
        
        return [
            {
                "category_id": str(row.id),
                "name": row.name,
                "product_count": row.product_count,
                "transactions": row.transactions or 0,
                "quantity_sold": float(row.quantity_sold or 0),
                "revenue": float(row.revenue or 0)
            }
            for row in results
        ]
    
    def classify_products_abc(
        self,
        tenant_id: UUID,
        days: int = 90
    ) -> Dict[str, List[str]]:
        """
        Classification ABC des produits
        A: 80% du CA (20% produits)
        B: 15% du CA (30% produits)
        C: 5% du CA (50% produits)
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
            "tenant_id": tenant_id,
            "start_date": start_date
        }).fetchall()
        
        if not results:
            return {"A": [], "B": [], "C": []}
        
        # Calculer CA total
        total_revenue = sum(row.revenue for row in results)
        
        # Classification
        classification = {"A": [], "B": [], "C": []}
        cumulative_revenue = 0
        cumulative_percent = 0
        
        for row in results:
            cumulative_revenue += row.revenue
            cumulative_percent = (cumulative_revenue / total_revenue * 100) if total_revenue > 0 else 0
            
            if cumulative_percent <= 80:
                classification["A"].append(str(row.id))
            elif cumulative_percent <= 95:
                classification["B"].append(str(row.id))
            else:
                classification["C"].append(str(row.id))
        
        return classification
```

CRITÈRES D'ACCEPTATION:
✅ Service AnalyticsService créé
✅ Méthode get_product_analysis retourne données complètes
✅ Calcul couverture stock fonctionne
✅ Calcul rotation stock fonctionne
✅ get_sales_evolution retourne évolution quotidienne
✅ get_top_products avec tri configurable
✅ get_category_performance par catégorie
✅ classify_products_abc classification ABC
✅ Tests unitaires service
✅ Performance <500ms par requête

COMMANDES DE TEST:
```python
# Script test
from app.services.analytics_service import AnalyticsService
from app.db.session import SessionLocal

db = SessionLocal()
service = AnalyticsService(db)

# Test analyse produit
analysis = service.get_product_analysis(tenant_id, product_id)
print(f"Couverture: {analysis['metrics']['coverage_days']} jours")

# Test évolution ventes
evolution = service.get_sales_evolution(tenant_id, days=30)
print(f"Jours avec ventes: {len(evolution)}")

# Test top produits
top = service.get_top_products(tenant_id, limit=5)
print(f"Top produit: {top[0]['name']} - {top[0]['revenue']} FCFA")

# Test classification ABC
abc = service.classify_products_abc(tenant_id)
print(f"Classe A: {len(abc['A'])} produits")
```
```

---

### 🔧 PROMPT 3.2 : Service Prédictions & Recommandations

```
CONTEXTE:
Le service analytics est fonctionnel. Je dois créer le service de prédictions pour anticiper les ruptures stock et calculer les quantités à commander.

OBJECTIF:
Créer service PredictionService avec:
- Prédiction date rupture stock
- Calcul quantité réapprovisionnement
- Recommandations achat groupées
- Gestion délais livraison fournisseurs

SPÉCIFICATIONS TECHNIQUES:

SERVICE PRÉDICTIONS (app/services/prediction_service.py):
```python
from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import UUID
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.models.product import Product
from app.models.sale import Sale
from app.models.supplier import Supplier

class PredictionService:
    def __init__(self, db: Session):
        self.db = db
    
    def predict_rupture_date(
        self,
        tenant_id: UUID,
        product_id: UUID
    ) -> Optional[datetime]:
        """
        Prédire date rupture stock basée sur:
        - Stock actuel
        - Ventes moyennes quotidiennes (30j)
        
        Retourne None si:
        - Produit déjà en rupture
        - Pas d'historique ventes
        - Stock suffisant (>30 jours)
        """
        product = self.db.query(Product).filter(
            Product.id == product_id,
            Product.tenant_id == tenant_id
        ).first()
        
        if not product or product.current_stock <= 0:
            return None
        
        # Ventes moyennes 30 derniers jours
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        from sqlalchemy import func
        avg_daily_sales = self.db.query(
            func.avg(func.sum(Sale.quantity))
        ).filter(
            and_(
                Sale.product_id == product_id,
                Sale.sale_date >= thirty_days_ago
            )
        ).group_by(
            func.date(Sale.sale_date)
        ).scalar()
        
        if not avg_daily_sales or avg_daily_sales <= 0:
            return None
        
        # Jours jusqu'à rupture
        days_until_rupture = product.current_stock / float(avg_daily_sales)
        
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
        Calculer quantité à commander pour couvrir X jours
        
        Formule:
        Qté = (Vente moyenne quotidienne × Jours cible) - Stock actuel + Stock sécurité
        """
        product = self.db.query(Product).filter(
            Product.id == product_id,
            Product.tenant_id == tenant_id
        ).first()
        
        if not product:
            return None
        
        # Ventes moyennes
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        from sqlalchemy import func
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
            # Pas d'historique: commander stock minimum
            return {
                "product_id": str(product_id),
                "recommended_quantity": float(product.min_stock or 0),
                "rationale": "NO_HISTORY",
                "target_days": None,
                "avg_daily_sales": 0
            }
        
        avg_daily_sales = float(sales_data.total) / max(sales_data.days, 1)
        
        # Stock sécurité = stock minimum
        safety_stock = float(product.min_stock or 0)
        
        # Quantité nécessaire
        needed_quantity = (avg_daily_sales * target_days) - product.current_stock + safety_stock
        
        # Arrondir au-dessus
        import math
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
        Liste des ruptures prévues dans les X prochains jours
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
                
                ruptures.append({
                    "product_id": str(product.id),
                    "product_code": product.code,
                    "product_name": product.name,
                    "current_stock": float(product.current_stock),
                    "min_stock": float(product.min_stock or 0),
                    "predicted_rupture_date": rupture_date.isoformat(),
                    "days_until_rupture": (rupture_date - datetime.utcnow()).days,
                    "recommended_quantity": reorder["recommended_quantity"] if reorder else 0,
                    "supplier": {
                        "id": str(product.supplier.id) if product.supplier else None,
                        "name": product.supplier.name if product.supplier else None,
                        "lead_time_days": product.supplier.lead_time_days if product.supplier else 7
                    } if product.supplier_id else None
                })
        
        # Trier par urgence (date rupture proche)
        ruptures.sort(key=lambda x: x["days_until_rupture"])
        
        return ruptures
    
    def get_recommandations_achat(
        self,
        tenant_id: UUID,
        horizon_days: int = 15
    ) -> Dict[str, Any]:
        """
        Recommandations achat groupées par fournisseur
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
                by_supplier[supplier_id]["products"].append({
                    "product_id": rupture["product_id"],
                    "product_name": rupture["product_name"],
                    "quantity": rupture["recommended_quantity"],
                    "urgency": "HIGH" if rupture["days_until_rupture"] < 7 else "MEDIUM"
                })
            else:
                no_supplier.append(rupture)
        
        return {
            "by_supplier": list(by_supplier.values()),
            "without_supplier": no_supplier,
            "total_products": len(ruptures),
            "total_suppliers": len(by_supplier)
        }
```

FONCTION SQL PRÉDICTION (Migration Alembic):
```sql
-- Fonction: Prédire date rupture
CREATE OR REPLACE FUNCTION fn_predict_date_rupture(
    p_tenant_id UUID,
    p_product_id UUID
) RETURNS DATE AS $$
DECLARE
    v_current_stock DECIMAL;
    v_avg_daily_sales DECIMAL;
    v_days_until_rupture INT;
BEGIN
    -- Récupérer stock actuel
    SELECT current_stock INTO v_current_stock
    FROM products
    WHERE id = p_product_id AND tenant_id = p_tenant_id;
    
    IF v_current_stock IS NULL OR v_current_stock <= 0 THEN
        RETURN NULL;
    END IF;
    
    -- Calculer ventes moyennes quotidiennes (30j)
    SELECT AVG(daily_quantity) INTO v_avg_daily_sales
    FROM (
        SELECT DATE(sale_date), SUM(quantity) as daily_quantity
        FROM sales
        WHERE product_id = p_product_id
            AND sale_date >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY DATE(sale_date)
    ) daily_sales;
    
    IF v_avg_daily_sales IS NULL OR v_avg_daily_sales <= 0 THEN
        RETURN NULL;
    END IF;
    
    -- Calculer jours jusqu'à rupture
    v_days_until_rupture := FLOOR(v_current_stock / v_avg_daily_sales);
    
    IF v_days_until_rupture > 30 THEN
        RETURN NULL;
    END IF;
    
    RETURN CURRENT_DATE + v_days_until_rupture;
END;
$$ LANGUAGE plpgsql;
```

CRITÈRES D'ACCEPTATION:
✅ Service PredictionService créé
✅ predict_rupture_date retourne date précise
✅ calculate_reorder_quantity formule correcte
✅ get_ruptures_prevues liste complète
✅ get_recommandations_achat groupées par fournisseur
✅ Fonction SQL fn_predict_date_rupture
✅ Gestion cas aucun historique ventes
✅ Tri par urgence (date proche)
✅ Tests unitaires prédictions
✅ Marge erreur <10% (validation manuelle)

COMMANDES DE TEST:
```python
# Test prédictions
from app.services.prediction_service import PredictionService

service = PredictionService(db)

# Rupture prévue
rupture = service.predict_rupture_date(tenant_id, product_id)
print(f"Rupture prévue: {rupture}")

# Quantité à commander
reorder = service.calculate_reorder_quantity(tenant_id, product_id, target_days=15)
print(f"Commander: {reorder['recommended_quantity']} unités")

# Liste ruptures 15j
ruptures = service.get_ruptures_prevues(tenant_id, horizon_days=15)
print(f"{len(ruptures)} ruptures prévues")

# Recommandations achat
reco = service.get_recommandations_achat(tenant_id)
print(f"Commandes à passer auprès de {reco['total_suppliers']} fournisseurs")
```
```

---

### 🔧 PROMPT 3.3 : Endpoints API Analytics & Prédictions

```
CONTEXTE:
Les services Analytics et Prediction sont fonctionnels. Je dois créer les endpoints API pour exposer ces fonctionnalités au frontend.

OBJECTIF:
Créer endpoints API pour:
- Analyse détaillée produit
- Évolution ventes
- Top produits
- Performance catégories
- Ruptures prévues
- Recommandations achat

SPÉCIFICATIONS TECHNIQUES:

ROUTER ANALYTICS (app/api/v1/analytics.py):
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("/products/{product_id}")
def get_product_analysis(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyse détaillée d'un produit"""
    service = AnalyticsService(db)
    analysis = service.get_product_analysis(current_user.tenant_id, product_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return analysis

@router.get("/sales/evolution")
def get_sales_evolution(
    days: int = Query(default=30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Évolution des ventes quotidiennes"""
    service = AnalyticsService(db)
    return service.get_sales_evolution(current_user.tenant_id, days)

@router.get("/products/top")
def get_top_products(
    limit: int = Query(default=10, ge=1, le=50),
    days: int = Query(default=30, ge=7, le=365),
    order_by: str = Query(default="revenue", regex="^(revenue|quantity|transactions)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Top produits par CA, quantité ou transactions"""
    service = AnalyticsService(db)
    return service.get_top_products(
        current_user.tenant_id,
        limit=limit,
        days=days,
        order_by=order_by
    )

@router.get("/categories/performance")
def get_category_performance(
    days: int = Query(default=30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Performance par catégorie"""
    service = AnalyticsService(db)
    return service.get_category_performance(current_user.tenant_id, days)

@router.get("/products/abc-classification")
def get_abc_classification(
    days: int = Query(default=90, ge=30, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Classification ABC des produits"""
    service = AnalyticsService(db)
    return service.classify_products_abc(current_user.tenant_id, days)
```

ROUTER PREDICTIONS (app/api/v1/predictions.py):
```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.prediction_service import PredictionService

router = APIRouter()

@router.get("/ruptures")
def get_ruptures_prevues(
    horizon_days: int = Query(default=15, ge=7, le=60),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Liste des ruptures prévues"""
    service = PredictionService(db)
    return service.get_ruptures_prevues(current_user.tenant_id, horizon_days)

@router.get("/recommandations")
def get_recommandations_achat(
    horizon_days: int = Query(default=15, ge=7, le=60),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Recommandations achat groupées par fournisseur"""
    service = PredictionService(db)
    return service.get_recommandations_achat(current_user.tenant_id, horizon_days)

@router.get("/products/{product_id}/rupture-date")
def predict_product_rupture(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Prédire date rupture d'un produit spécifique"""
    service = PredictionService(db)
    rupture_date = service.predict_rupture_date(current_user.tenant_id, product_id)
    
    return {
        "product_id": str(product_id),
        "predicted_rupture_date": rupture_date.isoformat() if rupture_date else None
    }

@router.get("/products/{product_id}/reorder")
def calculate_product_reorder(
    product_id: UUID,
    target_days: int = Query(default=15, ge=7, le=60),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculer quantité à commander pour un produit"""
    service = PredictionService(db)
    return service.calculate_reorder_quantity(
        current_user.tenant_id,
        product_id,
        target_days
    )
```

ENREGISTRER ROUTERS (app/main.py):
```python
from app.api.v1 import analytics, predictions

app.include_router(
    analytics.router,
    prefix=f"{settings.API_V1_PREFIX}/analytics",
    tags=["analytics"]
)

app.include_router(
    predictions.router,
    prefix=f"{settings.API_V1_PREFIX}/predictions",
    tags=["predictions"]
)
```

CRITÈRES D'ACCEPTATION:
✅ Tous les endpoints créés
✅ Validation paramètres Query (min/max)
✅ Documentation Swagger complète
✅ Filtrage tenant_id automatique
✅ Codes HTTP appropriés
✅ Tests Postman/curl fonctionnels
✅ Performance <1s par endpoint

COMMANDES DE TEST:
```bash
# Analyse produit
curl http://localhost:8000/api/v1/analytics/products/{product_id} \
  -H "Authorization: Bearer <token>"

# Évolution ventes
curl "http://localhost:8000/api/v1/analytics/sales/evolution?days=30" \
  -H "Authorization: Bearer <token>"

# Top produits
curl "http://localhost:8000/api/v1/analytics/products/top?limit=10&order_by=revenue" \
  -H "Authorization: Bearer <token>"

# Ruptures prévues
curl "http://localhost:8000/api/v1/predictions/ruptures?horizon_days=15" \
  -H "Authorization: Bearer <token>"

# Recommandations achat
curl http://localhost:8000/api/v1/predictions/recommandations \
  -H "Authorization: Bearer <token>"
```
```

---

## SEMAINE 6 : FRONTEND DASHBOARDS AVANCÉS

### 🔧 PROMPT 3.4 : Dashboard Gestion Stock Détaillée

```
CONTEXTE:
Les endpoints analytics sont fonctionnels. Je dois créer le dashboard "Gestion Stock Détaillée" avec liste produits, filtres avancés et vue détail.

OBJECTIF:
Créer dashboard stock avec:
- Liste produits (table)
- Filtres: catégorie, statut, recherche
- Tri colonnes
- Vue détail produit (modal)
- Badges statut couleur
- Export CSV

SPÉCIFICATIONS TECHNIQUES:

API CLIENT (src/api/analytics.ts):
```typescript
import { apiClient } from './client';

export const analyticsApi = {
  getProductAnalysis: async (productId: string) => {
    const { data } = await apiClient.get(`/analytics/products/${productId}`);
    return data;
  },

  getSalesEvolution: async (days: number = 30) => {
    const { data } = await apiClient.get('/analytics/sales/evolution', {
      params: { days },
    });
    return data;
  },

  getTopProducts: async (params: { limit?: number; days?: number; order_by?: string }) => {
    const { data } = await apiClient.get('/analytics/products/top', { params });
    return data;
  },

  getCategoryPerformance: async (days: number = 30) => {
    const { data } = await apiClient.get('/analytics/categories/performance', {
      params: { days },
    });
    return data;
  },
};
```

TYPES (src/types/analytics.types.ts):
```typescript
export interface ProductAnalysis {
  product: {
    id: string;
    code: string;
    name: string;
    current_stock: number;
    min_stock: number;
    max_stock: number;
    purchase_price: number;
    sale_price: number;
    unit: string;
  };
  sales: {
    last_30_days: {
      transactions: number;
      quantity: number;
      revenue: number;
      avg_daily: number;
    };
    last_90_days: {
      transactions: number;
      quantity: number;
      avg_daily: number;
    };
  };
  metrics: {
    coverage_days: number | null;
    rotation_annual: number | null;
    margin: number;
    margin_percent: number;
  };
  status: 'RUPTURE' | 'FAIBLE' | 'ALERTE' | 'SURSTOCK' | 'NORMAL';
}
```

HOOK (src/features/stock/hooks/useStockData.ts):
```typescript
import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '@/api/analytics';

export const useProductAnalysis = (productId: string | null) => {
  return useQuery({
    queryKey: ['product-analysis', productId],
    queryFn: () => analyticsApi.getProductAnalysis(productId!),
    enabled: !!productId,
  });
};
```

PAGE STOCK DÉTAILLÉ (src/features/stock/components/StockDetailDashboard.tsx):
```typescript
import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Search, Download, Eye } from 'lucide-react';
import { ProductDetailModal } from './ProductDetailModal';
import { apiClient } from '@/api/client';

export const StockDetailDashboard = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [selectedProduct, setSelectedProduct] = useState<string | null>(null);

  // Récupérer liste produits
  const { data: products, isLoading } = useQuery({
    queryKey: ['products'],
    queryFn: async () => {
      const { data } = await apiClient.get('/products/');
      return data;
    },
  });

  // Filtrer produits
  const filteredProducts = useMemo(() => {
    if (!products) return [];

    return products.filter((product) => {
      // Recherche
      const matchesSearch =
        product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        product.code.toLowerCase().includes(searchTerm.toLowerCase());

      // Statut
      const matchesStatus = statusFilter === 'ALL' || product.status === statusFilter;

      return matchesSearch && matchesStatus;
    });
  }, [products, searchTerm, statusFilter]);

  const getStatusBadge = (status: string) => {
    const config = {
      RUPTURE: { label: 'Rupture', class: 'bg-red-100 text-red-800' },
      FAIBLE: { label: 'Stock Faible', class: 'bg-amber-100 text-amber-800' },
      ALERTE: { label: 'Alerte', class: 'bg-orange-100 text-orange-800' },
      SURSTOCK: { label: 'Surstock', class: 'bg-purple-100 text-purple-800' },
      NORMAL: { label: 'Normal', class: 'bg-green-100 text-green-800' },
    };
    return config[status] || config.NORMAL;
  };

  const exportToCSV = () => {
    // Implémenter export CSV
    const csv = [
      ['Code', 'Nom', 'Stock', 'Stock Min', 'Statut'].join(','),
      ...filteredProducts.map((p) =>
        [p.code, p.name, p.current_stock, p.min_stock, p.status].join(',')
      ),
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'stock-detail.csv';
    a.click();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Gestion Stock Détaillée</h1>
          <p className="text-gray-600 mt-1">
            Vue complète de tous les produits avec analyses
          </p>
        </div>
        <Button onClick={exportToCSV} variant="outline">
          <Download className="w-4 h-4 mr-2" />
          Exporter CSV
        </Button>
      </div>

      {/* Stats rapides */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-600">Total Produits</p>
          <p className="text-2xl font-bold">{products?.length || 0}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-600">Ruptures</p>
          <p className="text-2xl font-bold text-red-600">
            {products?.filter((p) => p.status === 'RUPTURE').length || 0}
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-600">Stock Faible</p>
          <p className="text-2xl font-bold text-amber-600">
            {products?.filter((p) => p.status === 'FAIBLE').length || 0}
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-600">Normal</p>
          <p className="text-2xl font-bold text-green-600">
            {products?.filter((p) => p.status === 'NORMAL').length || 0}
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-600">Surstock</p>
          <p className="text-2xl font-bold text-purple-600">
            {products?.filter((p) => p.status === 'SURSTOCK').length || 0}
          </p>
        </div>
      </div>

      {/* Filtres */}
      <div className="flex gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <Input
            placeholder="Rechercher par nom ou code..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="ALL">Tous les statuts</option>
          <option value="RUPTURE">Rupture</option>
          <option value="FAIBLE">Stock Faible</option>
          <option value="ALERTE">Alerte</option>
          <option value="NORMAL">Normal</option>
          <option value="SURSTOCK">Surstock</option>
        </Select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Code
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Nom
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Stock Actuel
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Stock Min
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Statut
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {filteredProducts.map((product) => {
              const statusConfig = getStatusBadge(product.status);
              return (
                <tr key={product.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">
                    {product.code}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">{product.name}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {product.current_stock} {product.unit}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {product.min_stock || '-'} {product.unit}
                  </td>
                  <td className="px-6 py-4">
                    <Badge className={statusConfig.class}>{statusConfig.label}</Badge>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setSelectedProduct(product.id)}
                    >
                      <Eye className="w-4 h-4" />
                    </Button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Modal détail */}
      <ProductDetailModal
        productId={selectedProduct}
        onClose={() => setSelectedProduct(null)}
      />
    </div>
  );
};
```

MODAL DÉTAIL PRODUIT (src/features/stock/components/ProductDetailModal.tsx):
```typescript
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { useProductAnalysis } from '../hooks/useStockData';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, Package, DollarSign } from 'lucide-react';

export const ProductDetailModal = ({ productId, onClose }) => {
  const { data: analysis, isLoading } = useProductAnalysis(productId);

  if (!productId) return null;

  return (
    <Dialog open={!!productId} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Analyse Détaillée Produit</DialogTitle>
        </DialogHeader>

        {isLoading ? (
          <div>Chargement...</div>
        ) : (
          <div className="space-y-6">
            {/* Info produit */}
            <div>
              <h3 className="font-semibold text-lg">{analysis.product.name}</h3>
              <p className="text-gray-600">Code: {analysis.product.code}</p>
            </div>

            {/* Métriques principales */}
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Package className="w-5 h-5 text-blue-600" />
                  <span className="text-sm font-medium">Stock</span>
                </div>
                <p className="text-2xl font-bold">
                  {analysis.product.current_stock} {analysis.product.unit}
                </p>
                <p className="text-sm text-gray-600 mt-1">
                  Min: {analysis.product.min_stock || '-'} {analysis.product.unit}
                </p>
              </div>

              <div className="bg-green-50 p-4 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <DollarSign className="w-5 h-5 text-green-600" />
                  <span className="text-sm font-medium">Marge</span>
                </div>
                <p className="text-2xl font-bold">{analysis.metrics.margin_percent}%</p>
                <p className="text-sm text-gray-600 mt-1">
                  {analysis.metrics.margin} FCFA/unité
                </p>
              </div>

              <div className="bg-purple-50 p-4 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="w-5 h-5 text-purple-600" />
                  <span className="text-sm font-medium">Couverture</span>
                </div>
                <p className="text-2xl font-bold">
                  {analysis.metrics.coverage_days?.toFixed(1) || '-'}
                </p>
                <p className="text-sm text-gray-600 mt-1">jours de stock</p>
              </div>
            </div>

            {/* Ventes */}
            <div>
              <h4 className="font-semibold mb-3">Performance Ventes</h4>
              <div className="grid grid-cols-2 gap-4">
                <div className="border rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-2">30 derniers jours</p>
                  <p className="text-lg font-semibold">
                    {analysis.sales.last_30_days.quantity} {analysis.product.unit}
                  </p>
                  <p className="text-sm text-gray-600">
                    {analysis.sales.last_30_days.revenue.toLocaleString()} FCFA
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    Moyenne: {analysis.sales.last_30_days.avg_daily.toFixed(1)}/jour
                  </p>
                </div>

                <div className="border rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-2">90 derniers jours</p>
                  <p className="text-lg font-semibold">
                    {analysis.sales.last_90_days.quantity} {analysis.product.unit}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    Moyenne: {analysis.sales.last_90_days.avg_daily.toFixed(1)}/jour
                  </p>
                </div>
              </div>
            </div>

            {/* Métriques avancées */}
            <div>
              <h4 className="font-semibold mb-3">Métriques Supply Chain</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Rotation annuelle:</span>
                  <span className="font-medium">
                    {analysis.metrics.rotation_annual?.toFixed(2) || '-'} fois/an
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Prix achat:</span>
                  <span className="font-medium">
                    {analysis.product.purchase_price} FCFA
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Prix vente:</span>
                  <span className="font-medium">
                    {analysis.product.sale_price} FCFA
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};
```

CRITÈRES D'ACCEPTATION:
✅ Liste produits affiche tous les produits
✅ Recherche fonctionne (nom + code)
✅ Filtres statut fonctionnels
✅ Tri colonnes (optionnel)
✅ Badges couleur selon statut
✅ Modal détail s'ouvre
✅ Analyse produit affichée complète
✅ Export CSV fonctionne
✅ Performance <3s chargement
✅ Responsive mobile

COMMANDES DE TEST:
```bash
npm run dev
# Login → /stock/detail
# Tester recherche
# Tester filtres
# Ouvrir détail produit
# Vérifier métriques cohérentes
# Tester export CSV
```
```

---

### 🔧 PROMPT 3.5 : Dashboard Analyse Ventes

```
CONTEXTE:
Le dashboard Stock Détaillée est fonctionnel. Je dois créer le dashboard "Analyse Ventes" avec évolution CA, top produits et performance catégories.

OBJECTIF:
Créer dashboard ventes avec:
- Graphique évolution CA (Line Chart)
- Top 10 produits (Bar Chart)
- Performance catégories (Pie Chart)
- Sélecteur période (7j, 30j, 90j)
- KPI cards (CA total, transactions, panier moyen)

SPÉCIFICATIONS TECHNIQUES:

PAGE ANALYSE VENTES (src/features/sales/components/SalesAnalysisDashboard.tsx):
```typescript
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '@/api/analytics';
import { Card } from '@/components/ui/card';
import { Select } from '@/components/ui/select';
import { TrendingUp, ShoppingCart, DollarSign } from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

export const SalesAnalysisDashboard = () => {
  const [period, setPeriod] = useState(30);

  // Évolution ventes
  const { data: evolution, isLoading: evolutionLoading } = useQuery({
    queryKey: ['sales-evolution', period],
    queryFn: () => analyticsApi.getSalesEvolution(period),
  });

  // Top produits
  const { data: topProducts } = useQuery({
    queryKey: ['top-products', period],
    queryFn: () =>
      analyticsApi.getTopProducts({
        limit: 10,
        days: period,
        order_by: 'revenue',
      }),
  });

  // Performance catégories
  const { data: categories } = useQuery({
    queryKey: ['category-performance', period],
    queryFn: () => analyticsApi.getCategoryPerformance(period),
  });

  // Calculer KPIs
  const kpis = evolution
    ? {
        totalRevenue: evolution.reduce((sum, day) => sum + day.revenue, 0),
        totalTransactions: evolution.reduce((sum, day) => sum + day.transactions, 0),
        avgBasket:
          evolution.reduce((sum, day) => sum + day.revenue, 0) /
          evolution.reduce((sum, day) => sum + day.transactions, 0),
      }
    : null;

  // Couleurs graphiques
  const COLORS = [
    '#4F46E5',
    '#10B981',
    '#F59E0B',
    '#EF4444',
    '#8B5CF6',
    '#06B6D4',
    '#EC4899',
    '#6366F1',
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Analyse des Ventes</h1>
          <p className="text-gray-600 mt-1">
            Évolution du chiffre d'affaires et performance produits
          </p>
        </div>
        <Select
          value={period}
          onChange={(e) => setPeriod(Number(e.target.value))}
          className="w-48"
        >
          <option value={7}>7 derniers jours</option>
          <option value={30}>30 derniers jours</option>
          <option value={90}>90 derniers jours</option>
        </Select>
      </div>

      {/* KPI Cards */}
      {kpis && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Chiffre d'Affaires</p>
                <p className="text-3xl font-bold mt-2">
                  {(kpis.totalRevenue / 1000000).toFixed(2)}M
                </p>
                <p className="text-sm text-gray-500 mt-1">FCFA</p>
              </div>
              <DollarSign className="w-12 h-12 text-green-500" />
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Transactions</p>
                <p className="text-3xl font-bold mt-2">{kpis.totalTransactions}</p>
                <p className="text-sm text-gray-500 mt-1">commandes</p>
              </div>
              <ShoppingCart className="w-12 h-12 text-blue-500" />
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Panier Moyen</p>
                <p className="text-3xl font-bold mt-2">
                  {kpis.avgBasket.toLocaleString('fr-FR', {
                    maximumFractionDigits: 0,
                  })}
                </p>
                <p className="text-sm text-gray-500 mt-1">FCFA</p>
              </div>
              <TrendingUp className="w-12 h-12 text-purple-500" />
            </div>
          </Card>
        </div>
      )}

      {/* Évolution CA */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">Évolution du Chiffre d'Affaires</h2>
        {evolutionLoading ? (
          <div className="h-80 flex items-center justify-center">
            <p>Chargement...</p>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={evolution}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tickFormatter={(date) => format(new Date(date), 'dd MMM', { locale: fr })}
              />
              <YAxis
                tickFormatter={(value) =>
                  `${(value / 1000).toFixed(0)}K`
                }
              />
              <Tooltip
                formatter={(value: number) =>
                  `${value.toLocaleString()} FCFA`
                }
                labelFormatter={(label) =>
                  format(new Date(label), 'dd MMMM yyyy', { locale: fr })
                }
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="revenue"
                stroke="#4F46E5"
                strokeWidth={2}
                name="CA Quotidien"
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </Card>

      {/* Top Produits */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">Top 10 Produits (par CA)</h2>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={topProducts} layout="horizontal">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              type="number"
              tickFormatter={(value) => `${(value / 1000).toFixed(0)}K`}
            />
            <YAxis type="category" dataKey="name" width={150} />
            <Tooltip
              formatter={(value: number) => `${value.toLocaleString()} FCFA`}
            />
            <Bar dataKey="revenue" fill="#10B981" radius={[0, 8, 8, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </Card>

      {/* Performance Catégories */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Répartition CA par Catégorie</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={categories}
                dataKey="revenue"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={(entry) => `${entry.name}: ${((entry.revenue / kpis.totalRevenue) * 100).toFixed(1)}%`}
              >
                {categories?.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value: number) => `${value.toLocaleString()} FCFA`} />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Détail par Catégorie</h2>
          <div className="space-y-3">
            {categories?.slice(0, 5).map((cat, index) => (
              <div key={cat.category_id} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className="w-4 h-4 rounded"
                    style={{ backgroundColor: COLORS[index] }}
                  />
                  <span className="font-medium">{cat.name}</span>
                </div>
                <div className="text-right">
                  <p className="font-semibold">
                    {cat.revenue.toLocaleString()} FCFA
                  </p>
                  <p className="text-sm text-gray-600">
                    {cat.transactions} transactions
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};
```

CRITÈRES D'ACCEPTATION:
✅ Graphique évolution CA fonctionnel
✅ Sélecteur période change les données
✅ KPI cards calculées correctement
✅ Top 10 produits affiché (bar chart)
✅ Pie chart catégories avec %
✅ Tooltips formatés français
✅ Axes graphiques formatés (K, M)
✅ Dates formatées français
✅ Responsive mobile
✅ Performance <3s chargement

COMMANDES DE TEST:
```bash
npm run dev
# Login → /sales/analysis
# Changer période (7j, 30j, 90j)
# Vérifier graphiques se mettent à jour
# Hover tooltips
# Tester responsive
```
```

---

### 🔧 PROMPT 3.6 : Dashboard Prédictions & Recommandations

```
CONTEXTE:
Le dashboard Analyse Ventes est fonctionnel. Je dois créer le dashboard "Prédictions & Recommandations" affichant les ruptures prévues et recommandations d'achat.

OBJECTIF:
Créer dashboard prédictions avec:
- Liste ruptures prévues (timeline)
- Compteur jours avant rupture
- Recommandations achat par fournisseur
- Quantités à commander
- Indicateurs urgence (couleurs)

SPÉCIFICATIONS TECHNIQUES:

API CLIENT (src/api/predictions.ts):
```typescript
import { apiClient } from './client';

export const predictionsApi = {
  getRupturesPrevues: async (horizonDays: number = 15) => {
    const { data } = await apiClient.get('/predictions/ruptures', {
      params: { horizon_days: horizonDays },
    });
    return data;
  },

  getRecommandations: async (horizonDays: number = 15) => {
    const { data } = await apiClient.get('/predictions/recommandations', {
      params: { horizon_days: horizonDays },
    });
    return data;
  },
};
```

PAGE PRÉDICTIONS (src/features/predictions/components/PredictionsDashboard.tsx):
```typescript
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { predictionsApi } from '@/api/predictions';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select } from '@/components/ui/select';
import {
  AlertTriangle,
  Clock,
  TrendingDown,
  Package,
  FileText,
} from 'lucide-react';
import { format, parseISO } from 'date-fns';
import { fr } from 'date-fns/locale';

export const PredictionsDashboard = () => {
  const [horizon, setHorizon] = useState(15);

  // Ruptures prévues
  const { data: ruptures, isLoading: rupturesLoading } = useQuery({
    queryKey: ['ruptures-prevues', horizon],
    queryFn: () => predictionsApi.getRupturesPrevues(horizon),
  });

  // Recommandations achat
  const { data: recommandations } = useQuery({
    queryKey: ['recommandations', horizon],
    queryFn: () => predictionsApi.getRecommandations(horizon),
  });

  const getUrgencyColor = (days: number) => {
    if (days <= 3) return 'bg-red-100 text-red-800 border-red-300';
    if (days <= 7) return 'bg-orange-100 text-orange-800 border-orange-300';
    return 'bg-amber-100 text-amber-800 border-amber-300';
  };

  const getUrgencyLabel = (days: number) => {
    if (days <= 3) return 'URGENT';
    if (days <= 7) return 'PRIORITAIRE';
    return 'À SURVEILLER';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Prédictions & Recommandations</h1>
          <p className="text-gray-600 mt-1">
            Anticipez les ruptures et optimisez vos commandes
          </p>
        </div>
        <Select
          value={horizon}
          onChange={(e) => setHorizon(Number(e.target.value))}
          className="w-48"
        >
          <option value={7}>7 prochains jours</option>
          <option value={15}>15 prochains jours</option>
          <option value={30}>30 prochains jours</option>
        </Select>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Ruptures Prévues</p>
              <p className="text-3xl font-bold mt-2 text-red-600">
                {ruptures?.length || 0}
              </p>
            </div>
            <AlertTriangle className="w-10 h-10 text-red-500" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Urgentes (≤3j)</p>
              <p className="text-3xl font-bold mt-2 text-red-600">
                {ruptures?.filter((r) => r.days_until_rupture <= 3).length || 0}
              </p>
            </div>
            <Clock className="w-10 h-10 text-red-500" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Fournisseurs</p>
              <p className="text-3xl font-bold mt-2 text-blue-600">
                {recommandations?.total_suppliers || 0}
              </p>
            </div>
            <Package className="w-10 h-10 text-blue-500" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Produits à Commander</p>
              <p className="text-3xl font-bold mt-2 text-purple-600">
                {recommandations?.total_products || 0}
              </p>
            </div>
            <TrendingDown className="w-10 h-10 text-purple-500" />
          </div>
        </Card>
      </div>

      {/* Ruptures prévues */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">
          Ruptures Prévues ({horizon} jours)
        </h2>
        {rupturesLoading ? (
          <div>Chargement...</div>
        ) : ruptures && ruptures.length > 0 ? (
          <div className="space-y-3">
            {ruptures.map((rupture) => (
              <div
                key={rupture.product_id}
                className={`border-l-4 p-4 rounded-lg ${getUrgencyColor(
                  rupture.days_until_rupture
                )}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <Badge variant="outline">
                        {getUrgencyLabel(rupture.days_until_rupture)}
                      </Badge>
                      <span className="font-semibold text-lg">
                        {rupture.product_name}
                      </span>
                      <span className="text-sm text-gray-600">
                        ({rupture.product_code})
                      </span>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600">Stock actuel</p>
                        <p className="font-medium">
                          {rupture.current_stock.toFixed(1)}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-600">Rupture prévue</p>
                        <p className="font-medium">
                          {format(parseISO(rupture.predicted_rupture_date), 'dd MMM', {
                            locale: fr,
                          })}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-600">Dans</p>
                        <p className="font-medium text-red-600">
                          {rupture.days_until_rupture} jour{rupture.days_until_rupture > 1 ? 's' : ''}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-600">À commander</p>
                        <p className="font-bold text-green-600">
                          {rupture.recommended_quantity} unités
                        </p>
                      </div>
                    </div>

                    {rupture.supplier && (
                      <div className="mt-3 text-sm">
                        <span className="text-gray-600">Fournisseur: </span>
                        <span className="font-medium">{rupture.supplier.name}</span>
                        <span className="text-gray-500 ml-2">
                          (Délai: {rupture.supplier.lead_time_days}j)
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <AlertTriangle className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <p className="text-lg">Aucune rupture prévue</p>
            <p className="text-sm mt-2">
              Votre stock est bien géré pour les {horizon} prochains jours
            </p>
          </div>
        )}
      </Card>

      {/* Recommandations par fournisseur */}
      <Card className="p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Recommandations d'Achat</h2>
          <Button variant="outline">
            <FileText className="w-4 h-4 mr-2" />
            Générer Bon de Commande
          </Button>
        </div>

        {recommandations?.by_supplier && recommandations.by_supplier.length > 0 ? (
          <div className="space-y-4">
            {recommandations.by_supplier.map((supplier) => (
              <div key={supplier.supplier_id} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="font-semibold text-lg">{supplier.supplier_name}</h3>
                    <p className="text-sm text-gray-600">
                      Délai livraison: {supplier.lead_time_days} jours
                    </p>
                  </div>
                  <Badge>{supplier.products.length} produits</Badge>
                </div>

                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="text-left p-2">Produit</th>
                      <th className="text-right p-2">Quantité</th>
                      <th className="text-center p-2">Urgence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {supplier.products.map((product) => (
                      <tr key={product.product_id} className="border-t">
                        <td className="p-2">{product.product_name}</td>
                        <td className="text-right p-2 font-medium">
                          {product.quantity}
                        </td>
                        <td className="text-center p-2">
                          <Badge
                            variant={product.urgency === 'HIGH' ? 'destructive' : 'default'}
                          >
                            {product.urgency === 'HIGH' ? 'Urgent' : 'Normal'}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            Aucune recommandation d'achat
          </div>
        )}
      </Card>
    </div>
  );
};
```

CRITÈRES D'ACCEPTATION:
✅ Liste ruptures prévues affichée
✅ Tri par urgence (date proche)
✅ Badges couleur urgence (rouge/orange/amber)
✅ Compteur jours avant rupture
✅ Quantités recommandées affichées
✅ Recommandations groupées par fournisseur
✅ Sélecteur horizon change données
✅ Stats calculées correctement
✅ Empty state si pas de ruptures
✅ Responsive mobile

COMMANDES DE TEST:
```bash
npm run dev
# Login → /predictions
# Vérifier ruptures prévues
# Changer horizon (7j, 15j, 30j)
# Vérifier recommandations par fournisseur
# Tester responsive
```
```

---

## 🎯 RÉCAPITULATIF SPRINT 3

### Fonctionnalités Livrées

✅ **Backend Analytics**
- Service AnalyticsService complet
- Service PredictionService avec prédictions
- Fonctions SQL prédictions
- Endpoints API analytics + predictions

✅ **Dashboards Frontend**
- Dashboard Gestion Stock Détaillée (liste + détail produit)
- Dashboard Analyse Ventes (évolution CA + top produits + catégories)
- Dashboard Prédictions & Recommandations (ruptures prévues + achat)

✅ **Analyses Avancées**
- Calcul couverture stock (jours)
- Calcul rotation stock (fois/an)
- Prédiction date rupture
- Recommandations quantités achat
- Classification ABC produits
- Performance par catégorie

### Tests de Validation Sprint 3

```bash
# 1. Backend - Analyse produit
curl http://localhost:8000/api/v1/analytics/products/{product_id} \
  -H "Authorization: Bearer <token>"

# 2. Backend - Ruptures prévues
curl http://localhost:8000/api/v1/predictions/ruptures?horizon_days=15 \
  -H "Authorization: Bearer <token>"

# 3. Frontend - Stock Détaillée
# Login → /stock/detail
# Rechercher produit
# Ouvrir détail
# Vérifier métriques

# 4. Frontend - Analyse Ventes
# Login → /sales/analysis
# Changer période
# Vérifier graphiques

# 5. Frontend - Prédictions
# Login → /predictions
# Vérifier ruptures prévues
# Vérifier recommandations
```

### Métriques Succès Sprint 3

- ✅ Prédictions fiables (marge erreur <10%)
- ✅ Dashboards chargement <3s
- ✅ 100% graphiques fonctionnels
- ✅ Responsive mobile tous dashboards
- ✅ Filtres/recherche performants (<500ms)

---

**FIN SPRINT 3**

Vous êtes prêt pour le Sprint 4 (Rapports & Finitions) !
