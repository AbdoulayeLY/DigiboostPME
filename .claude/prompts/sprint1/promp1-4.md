
### 🔧 PROMPT 1.4 : Vues SQL Dashboard & Service KPI

```
CONTEXTE:
L'authentification est fonctionnelle. Je dois maintenant créer les vues SQL matérialisées et le service backend pour le dashboard "Vue d'Ensemble". Ce dashboard affiche les KPIs principaux de santé stock et performance ventes.

OBJECTIF:
Créer:
- Vues SQL matérialisées pour performance
- Fonctions SQL pour calculs KPIs
- Service Python pour dashboard
- Endpoint API GET /api/v1/dashboards/overview
- Données de test (1 tenant, 50 produits, 90 jours ventes)

SPÉCIFICATIONS SELON supply_chain_spec_v3.md:

DASHBOARD "VUE D'ENSEMBLE" CONTIENT:

1. SANTÉ STOCK:
- Nombre total produits actifs
- Nombre produits en rupture (stock = 0)
- Nombre produits en stock faible (stock <= min_stock)
- Nombre produits en alerte
- Valorisation stock totale (∑ stock × prix_achat)

2. PERFORMANCE VENTES:
- CA 7 derniers jours
- CA 30 derniers jours
- Évolution CA (% variation)
- Nombre ventes 7j / 30j
- Taux de service (% commandes livrées)

3. TOP/FLOP:
- Top 5 produits (par CA)
- 5 produits dormants (pas de vente 30j + stock > 0)

VUES SQL À CRÉER (via Alembic migration):

```sql
-- Vue: Santé Stock
CREATE MATERIALIZED VIEW mv_dashboard_stock_health AS
SELECT 
    p.tenant_id,
    COUNT(DISTINCT p.id) as total_products,
    COUNT(DISTINCT CASE WHEN p.current_stock = 0 THEN p.id END) as rupture_count,
    COUNT(DISTINCT CASE WHEN p.current_stock > 0 AND p.current_stock <= p.min_stock THEN p.id END) as low_stock_count,
    SUM(p.current_stock * p.purchase_price) as total_stock_value
FROM products p
WHERE p.is_active = TRUE
GROUP BY p.tenant_id;

CREATE UNIQUE INDEX ON mv_dashboard_stock_health (tenant_id);

-- Vue: Performance Ventes
CREATE MATERIALIZED VIEW mv_dashboard_sales_performance AS
SELECT 
    s.tenant_id,
    DATE_TRUNC('day', s.sale_date) as sale_day,
    COUNT(*) as transactions_count,
    SUM(s.total_amount) as daily_revenue,
    SUM(s.quantity) as total_units_sold
FROM sales s
WHERE s.sale_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY s.tenant_id, DATE_TRUNC('day', s.sale_date);

CREATE INDEX ON mv_dashboard_sales_performance (tenant_id, sale_day);

-- Fonction: Calcul Taux Service
CREATE OR REPLACE FUNCTION fn_calc_taux_service(
    p_tenant_id UUID,
    p_days INT DEFAULT 30
) RETURNS DECIMAL AS $$
DECLARE
    total_orders INT;
    delivered_orders INT;
BEGIN
    SELECT 
        COUNT(*),
        COUNT(CASE WHEN status = 'DELIVERED' THEN 1 END)
    INTO total_orders, delivered_orders
    FROM sales
    WHERE tenant_id = p_tenant_id
        AND sale_date >= CURRENT_DATE - p_days;
    
    IF total_orders = 0 THEN
        RETURN 100;
    END IF;
    
    RETURN ROUND((delivered_orders::DECIMAL / total_orders) * 100, 2);
END;
$$ LANGUAGE plpgsql;
```

SERVICE DASHBOARD (app/services/dashboard_service.py):
```python
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from uuid import UUID
from typing import Dict, Any, List
from datetime import datetime, timedelta

class DashboardService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_overview(self, tenant_id: UUID) -> Dict[str, Any]:
        """
        Dashboard Vue d'Ensemble complet
        """
        return {
            "stock_health": self._get_stock_health(tenant_id),
            "sales_performance": self._get_sales_performance(tenant_id),
            "top_products": self._get_top_products(tenant_id, limit=5),
            "dormant_products": self._get_dormant_products(tenant_id, limit=5),
            "kpis": {
                "taux_service": self._get_taux_service(tenant_id)
            }
        }
    
    def _get_stock_health(self, tenant_id: UUID) -> Dict[str, Any]:
        """Santé stock depuis vue matérialisée"""
        query = text("""
            SELECT 
                total_products,
                rupture_count,
                low_stock_count,
                total_stock_value
            FROM mv_dashboard_stock_health
            WHERE tenant_id = :tenant_id
        """)
        result = self.db.execute(query, {"tenant_id": tenant_id}).first()
        
        if not result:
            return {
                "total_products": 0,
                "rupture_count": 0,
                "low_stock_count": 0,
                "total_stock_value": 0
            }
        
        return {
            "total_products": result.total_products,
            "rupture_count": result.rupture_count,
            "low_stock_count": result.low_stock_count,
            "alert_count": result.rupture_count + result.low_stock_count,
            "total_stock_value": float(result.total_stock_value or 0)
        }
    
    def _get_sales_performance(self, tenant_id: UUID) -> Dict[str, Any]:
        """Performance ventes 7j et 30j"""
        # Implémenter calculs CA 7j, CA 30j, évolution
        pass
    
    def _get_top_products(self, tenant_id: UUID, limit: int = 5) -> List[Dict]:
        """Top produits par CA"""
        # Implémenter requête
        pass
    
    def _get_taux_service(self, tenant_id: UUID) -> float:
        """Taux de service via fonction SQL"""
        query = text("SELECT fn_calc_taux_service(:tenant_id, 30)")
        result = self.db.execute(query, {"tenant_id": tenant_id}).scalar()
        return float(result or 100)
```

ENDPOINT API (app/api/v1/dashboards.py):
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.services.dashboard_service import DashboardService
from app.models.user import User

router = APIRouter()

@router.get("/overview")
def get_dashboard_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dashboard Vue d'Ensemble"""
    service = DashboardService(db)
    return service.get_overview(current_user.tenant_id)
```

ENREGISTRER ROUTER (app/main.py):
```python
from app.api.v1 import dashboards

app.include_router(
    dashboards.router,
    prefix=f"{settings.API_V1_PREFIX}/dashboards",
    tags=["dashboards"]
)
```

SCRIPT DONNÉES TEST (scripts/seed_data.py):
Créer script Python qui:
- Crée 1 tenant
- Crée 1 user admin
- Crée 5 catégories
- Crée 3 fournisseurs
- Crée 50 produits variés (stock différents)
- Crée 500 ventes sur 90 derniers jours

CRITÈRES D'ACCEPTATION:
✅ Vues matérialisées créées (migration Alembic)
✅ Fonction SQL taux_service créée
✅ Service DashboardService implémenté
✅ Endpoint /api/v1/dashboards/overview retourne JSON
✅ Script seed_data.py génère données cohérentes
✅ Dashboard retourne KPIs corrects
✅ Performance < 3 secondes
✅ Test: Login → GET /dashboards/overview → JSON valide

COMMANDES DE TEST:
```bash
# Appliquer migration vues SQL
alembic revision -m "Create dashboard views"
alembic upgrade head

# Seed data
python scripts/seed_data.py

# Rafraîchir vues
psql -U ais_db_owner -d DigiboostPME -c "REFRESH MATERIALIZED VIEW mv_dashboard_stock_health;"

# Tester API
curl http://localhost:8000/api/v1/dashboards/overview \
  -H "Authorization: Bearer <token>"
```
```

---