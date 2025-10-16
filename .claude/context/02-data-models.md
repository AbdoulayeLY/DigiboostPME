# MODÈLES DE DONNÉES - DIGIBOOST PME

## 📊 SCHÉMA DE BASE DE DONNÉES

### Vue d'Ensemble ERD (Entity Relationship Diagram)

```
┌──────────────┐
│   TENANTS    │
│──────────────│
│ id (PK)      │
│ name         │
│ ninea        │
│ email        │
│ phone        │
│ settings     │◄───────┐
│ is_active    │        │
│ created_at   │        │
│ updated_at   │        │
└──────────────┘        │
       ▲                │
       │                │
       │ tenant_id      │
       │                │
┌──────┴───────┐        │
│    USERS     │        │
│──────────────│        │
│ id (PK)      │        │
│ tenant_id(FK)│────────┤
│ email        │        │
│ hashed_pwd   │        │
│ full_name    │        │
│ role         │        │
│ whatsapp_num │        │
│ is_active    │        │
│ created_at   │        │
│ updated_at   │        │
└──────────────┘        │
                        │
┌─────────────┐         │
│ CATEGORIES  │         │
│─────────────│         │
│ id (PK)     │         │
│ tenant_id   │─────────┤
│ name        │         │
│ description │         │
│ created_at  │         │
└─────────────┘         │
       ▲                │
       │                │
┌──────┴───────┐        │
│  SUPPLIERS   │        │
│──────────────│        │
│ id (PK)      │        │
│ tenant_id(FK)│────────┤
│ name         │        │
│ contact      │        │
│ phone        │        │
│ email        │        │
│ address      │        │
│ is_active    │        │
│ created_at   │        │
└──────────────┘        │
       ▲                │
       │                │
┌──────┴───────────────┐│
│     PRODUCTS         ││
│──────────────────────││
│ id (PK)              ││
│ tenant_id (FK)       │├────────┐
│ code (unique)        ││        │
│ name                 ││        │
│ category_id (FK)     │┘        │
│ supplier_id (FK)     │         │
│ purchase_price       │         │
│ sale_price           │         │
│ unit                 │         │
│ current_stock        │         │
│ stock_min            │         │
│ stock_max            │         │
│ description          │         │
│ barcode              │         │
│ is_active            │         │
│ created_at           │         │
│ updated_at           │         │
└──────────────────────┘         │
       ▲                         │
       │                         │
       │ product_id              │
       │                         │
┌──────┴───────────┐             │
│      SALES       │             │
│──────────────────│             │
│ id (PK)          │             │
│ tenant_id (FK)   │─────────────┤
│ product_id (FK)  │             │
│ sale_date        │             │
│ quantity         │             │
│ unit_price       │             │
│ total_amount     │             │
│ order_number     │             │
│ customer_name    │             │
│ status           │             │
│ created_at       │             │
└──────────────────┘             │
                                 │
┌───────────────────┐            │
│ STOCK_MOVEMENTS   │            │
│───────────────────│            │
│ id (PK)           │            │
│ tenant_id (FK)    │────────────┤
│ product_id (FK)   │            │
│ movement_type     │            │
│ quantity          │            │
│ reference         │            │
│ notes             │            │
│ created_at        │            │
│ created_by        │            │
└───────────────────┘            │
                                 │
┌───────────────┐                │
│    ALERTS     │                │
│───────────────│                │
│ id (PK)       │                │
│ tenant_id(FK) │────────────────┤
│ name          │                │
│ alert_type    │                │
│ conditions    │ (JSON)         │
│ channels      │ (JSON)         │
│ recipients    │ (JSON)         │
│ is_active     │                │
│ created_at    │                │
│ updated_at    │                │
└───────────────┘                │
       ▲                         │
       │                         │
       │ alert_id                │
┌──────┴──────────┐              │
│ ALERT_HISTORY   │              │
│─────────────────│              │
│ id (PK)         │              │
│ tenant_id (FK)  │──────────────┤
│ alert_id (FK)   │              │
│ triggered_at    │              │
│ conditions_met  │ (JSON)       │
│ sent_channels   │ (JSON)       │
│ status          │              │
│ error_message   │              │
└─────────────────┘              │
                                 │
┌──────────────────┐             │
│ REPORT_GENERATION│             │
│──────────────────│             │
│ id (PK)          │             │
│ tenant_id (FK)   │─────────────┘
│ report_type      │
│ parameters       │ (JSON)
│ status           │
│ file_path        │
│ generated_at     │
│ generated_by     │
└──────────────────┘
```

## 📋 DÉFINITION DES TABLES

### 1. TENANTS (PME)

```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    ninea VARCHAR(50),  -- Numéro identification entreprise Sénégal
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    settings JSONB DEFAULT '{}',  -- Configuration alertes, objectifs
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tenants_email ON tenants(email);
CREATE INDEX idx_tenants_is_active ON tenants(is_active);
```

**Exemple settings JSON** :
```json
{
  "alert_channels": ["whatsapp", "email"],
  "default_currency": "FCFA",
  "business_hours": {
    "start": "08:00",
    "end": "18:00"
  },
  "monthly_report_day": 1,
  "stock_optimization": {
    "enabled": true,
    "prediction_days": 30
  }
}
```

### 2. USERS (Utilisateurs par PME)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',  -- 'admin', 'manager', 'user'
    whatsapp_number VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(tenant_id, role);
```

**Rôles** :
- **admin** : Accès complet, gestion utilisateurs, configuration
- **manager** : Gestion stock, ventes, alertes, rapports
- **user** : Consultation dashboards, saisie ventes (lecture seule alertes)

### 3. CATEGORIES (Catégories de produits)

```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, name)
);

CREATE INDEX idx_categories_tenant ON categories(tenant_id);
```

**Exemples** : Alimentaire, Électronique, Vêtements, Quincaillerie, etc.

### 4. SUPPLIERS (Fournisseurs)

```sql
CREATE TABLE suppliers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, name)
);

CREATE INDEX idx_suppliers_tenant ON suppliers(tenant_id);
CREATE INDEX idx_suppliers_active ON suppliers(tenant_id, is_active);
```

### 5. PRODUCTS (Produits)

```sql
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    code VARCHAR(50) NOT NULL,  -- Code interne produit (SKU)
    name VARCHAR(255) NOT NULL,
    category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    supplier_id UUID REFERENCES suppliers(id) ON DELETE SET NULL,
    purchase_price DECIMAL(15, 2) NOT NULL DEFAULT 0,
    sale_price DECIMAL(15, 2) NOT NULL,
    unit VARCHAR(20) NOT NULL DEFAULT 'pièce',  -- pièce, kg, litre, carton
    current_stock DECIMAL(15, 3) NOT NULL DEFAULT 0,
    stock_min DECIMAL(15, 3) NOT NULL DEFAULT 0,
    stock_max DECIMAL(15, 3),
    description TEXT,
    barcode VARCHAR(100),
    image_url VARCHAR(500),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, code)
);

CREATE INDEX idx_products_tenant ON products(tenant_id);
CREATE INDEX idx_products_code ON products(tenant_id, code);
CREATE INDEX idx_products_category ON products(tenant_id, category_id);
CREATE INDEX idx_products_supplier ON products(tenant_id, supplier_id);
CREATE INDEX idx_products_stock_status ON products(tenant_id, current_stock, stock_min);
CREATE INDEX idx_products_active ON products(tenant_id, is_active);
```

**Contraintes métier** :
- `sale_price` doit être > `purchase_price` (marge positive)
- `current_stock` >= 0
- `stock_min` >= 0
- Si `stock_max` défini, alors `stock_max` > `stock_min`

### 6. SALES (Ventes)

```sql
CREATE TABLE sales (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    sale_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    quantity DECIMAL(15, 3) NOT NULL,
    unit_price DECIMAL(15, 2) NOT NULL,
    total_amount DECIMAL(15, 2) NOT NULL,  -- quantity * unit_price
    order_number VARCHAR(100),
    customer_name VARCHAR(255),
    payment_method VARCHAR(50),  -- cash, mobile_money, credit
    status VARCHAR(50) NOT NULL DEFAULT 'completed',  -- completed, cancelled, returned
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_sales_tenant ON sales(tenant_id);
CREATE INDEX idx_sales_product ON sales(tenant_id, product_id);
CREATE INDEX idx_sales_date ON sales(tenant_id, sale_date DESC);
CREATE INDEX idx_sales_status ON sales(tenant_id, status);
CREATE INDEX idx_sales_order ON sales(tenant_id, order_number);
```

**Trigger automatique** : Décrémenter `current_stock` du produit après insert vente

```sql
CREATE OR REPLACE FUNCTION update_stock_on_sale()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'completed' THEN
        UPDATE products
        SET current_stock = current_stock - NEW.quantity,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = NEW.product_id AND tenant_id = NEW.tenant_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_stock_on_sale
AFTER INSERT ON sales
FOR EACH ROW EXECUTE FUNCTION update_stock_on_sale();
```

### 7. STOCK_MOVEMENTS (Mouvements de stock)

```sql
CREATE TABLE stock_movements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    movement_type VARCHAR(50) NOT NULL,  -- 'IN' (entrée), 'OUT' (sortie), 'ADJUSTMENT' (ajustement)
    quantity DECIMAL(15, 3) NOT NULL,
    reference VARCHAR(255),  -- Numéro bon livraison, facture, etc.
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_stock_movements_tenant ON stock_movements(tenant_id);
CREATE INDEX idx_stock_movements_product ON stock_movements(tenant_id, product_id);
CREATE INDEX idx_stock_movements_date ON stock_movements(tenant_id, created_at DESC);
CREATE INDEX idx_stock_movements_type ON stock_movements(tenant_id, movement_type);
```

**Trigger automatique** : Mettre à jour `current_stock` selon type mouvement

### 8. ALERTS (Alertes configurées)

```sql
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,  -- 'stock_low', 'stock_out', 'expiry', 'sales_drop'
    conditions JSONB NOT NULL,
    channels JSONB NOT NULL DEFAULT '["whatsapp"]',  -- whatsapp, email, sms
    recipients JSONB NOT NULL,  -- Liste destinataires (phones, emails)
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_alerts_tenant ON alerts(tenant_id);
CREATE INDEX idx_alerts_type ON alerts(tenant_id, alert_type);
CREATE INDEX idx_alerts_active ON alerts(tenant_id, is_active);
```

**Exemple conditions JSON** :
```json
{
  "threshold_type": "percentage",  // ou "absolute"
  "threshold_value": 20,           // 20% du stock_min
  "products": ["all"],             // ou ["prod-uuid-1", "prod-uuid-2"]
  "categories": ["category-uuid"], // Filtrer par catégorie
  "check_frequency": "daily"       // daily, hourly
}
```

**Exemple recipients JSON** :
```json
{
  "whatsapp": ["+221771234567", "+221765432109"],
  "email": ["gerant@pme.sn", "assistant@pme.sn"]
}
```

### 9. ALERT_HISTORY (Historique déclenchements)

```sql
CREATE TABLE alert_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    alert_id UUID NOT NULL REFERENCES alerts(id) ON DELETE CASCADE,
    triggered_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    conditions_met JSONB NOT NULL,  -- Détails produits/conditions qui ont déclenché
    sent_channels JSONB,            -- Canaux où alerte envoyée
    status VARCHAR(50) NOT NULL DEFAULT 'pending',  -- pending, sent, failed
    error_message TEXT,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    acknowledged_by UUID REFERENCES users(id)
);

CREATE INDEX idx_alert_history_tenant ON alert_history(tenant_id);
CREATE INDEX idx_alert_history_alert ON alert_history(tenant_id, alert_id);
CREATE INDEX idx_alert_history_date ON alert_history(tenant_id, triggered_at DESC);
CREATE INDEX idx_alert_history_status ON alert_history(tenant_id, status);
```

**Partitionnement par mois recommandé** (table volumineuse)

### 10. REPORT_GENERATION (Rapports générés)

```sql
CREATE TABLE report_generation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    report_type VARCHAR(100) NOT NULL,  -- 'inventory', 'sales_analysis', 'monthly_summary'
    parameters JSONB,                   -- Filtres, période, etc.
    status VARCHAR(50) NOT NULL DEFAULT 'pending',  -- pending, processing, completed, failed
    file_path VARCHAR(500),
    file_size INTEGER,
    format VARCHAR(20) NOT NULL,        -- pdf, excel, csv
    generated_at TIMESTAMP WITH TIME ZONE,
    generated_by UUID REFERENCES users(id),
    expires_at TIMESTAMP WITH TIME ZONE,  -- Suppression auto après 30 jours
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reports_tenant ON report_generation(tenant_id);
CREATE INDEX idx_reports_type ON report_generation(tenant_id, report_type);
CREATE INDEX idx_reports_status ON report_generation(tenant_id, status);
CREATE INDEX idx_reports_date ON report_generation(tenant_id, generated_at DESC);
```

## 🔍 VUES MATÉRIALISÉES (Performance)

### 1. Vue Santé du Stock

```sql
CREATE MATERIALIZED VIEW mv_dashboard_stock_health AS
SELECT 
    tenant_id,
    COUNT(*) as total_products,
    COUNT(*) FILTER (WHERE current_stock = 0) as ruptures,
    COUNT(*) FILTER (WHERE current_stock > 0 AND current_stock < stock_min) as faibles,
    COUNT(*) FILTER (WHERE current_stock >= stock_min) as ok,
    SUM(current_stock * purchase_price) as valorisation_achat,
    SUM(current_stock * sale_price) as valorisation_vente,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE current_stock >= stock_min) / NULLIF(COUNT(*), 0),
        2
    ) as taux_service
FROM products
WHERE is_active = true
GROUP BY tenant_id;

CREATE UNIQUE INDEX ON mv_dashboard_stock_health (tenant_id);
```

### 2. Vue Métriques Ventes

```sql
CREATE MATERIALIZED VIEW mv_dashboard_sales_metrics AS
SELECT 
    tenant_id,
    SUM(total_amount) FILTER (WHERE sale_date >= CURRENT_DATE - INTERVAL '7 days') as ca_7j,
    SUM(total_amount) FILTER (WHERE sale_date >= CURRENT_DATE - INTERVAL '30 days') as ca_30j,
    SUM(total_amount) FILTER (WHERE sale_date >= CURRENT_DATE - INTERVAL '90 days') as ca_90j,
    COUNT(*) FILTER (WHERE sale_date >= CURRENT_DATE - INTERVAL '7 days') as ventes_7j,
    COUNT(*) FILTER (WHERE sale_date >= CURRENT_DATE - INTERVAL '30 days') as ventes_30j,
    ROUND(
        AVG(total_amount) FILTER (WHERE sale_date >= CURRENT_DATE - INTERVAL '30 days'),
        2
    ) as panier_moyen_30j
FROM sales
WHERE status = 'completed'
GROUP BY tenant_id;

CREATE UNIQUE INDEX ON mv_dashboard_sales_metrics (tenant_id);
```

### 3. Vue Top Produits

```sql
CREATE MATERIALIZED VIEW mv_top_products AS
SELECT 
    s.tenant_id,
    p.id as product_id,
    p.name as product_name,
    SUM(s.quantity) as quantity_sold,
    SUM(s.total_amount) as revenue,
    COUNT(*) as num_transactions
FROM sales s
JOIN products p ON p.id = s.product_id AND p.tenant_id = s.tenant_id
WHERE s.sale_date >= CURRENT_DATE - INTERVAL '30 days'
  AND s.status = 'completed'
GROUP BY s.tenant_id, p.id, p.name;

CREATE INDEX ON mv_top_products (tenant_id, revenue DESC);
```

**Refresh automatique toutes les 5 minutes via Celery task**

## 📐 MODÈLES SQLALCHEMY (Python)

### Base & Mixins

```python
# app/models/base.py
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declarative_mixin

@declarative_mixin
class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

### Exemple Modèle Product

```python
# app/models/product.py
from sqlalchemy import Column, String, Numeric, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.models.base import TimestampMixin
from app.db.base_class import Base

class Product(Base, TimestampMixin):
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"))
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id", ondelete="SET NULL"))
    purchase_price = Column(Numeric(15, 2), nullable=False, default=0)
    sale_price = Column(Numeric(15, 2), nullable=False)
    unit = Column(String(20), nullable=False, default="pièce")
    current_stock = Column(Numeric(15, 3), nullable=False, default=0)
    stock_min = Column(Numeric(15, 3), nullable=False, default=0)
    stock_max = Column(Numeric(15, 3))
    description = Column(Text)
    barcode = Column(String(100))
    image_url = Column(String(500))
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Relations
    tenant = relationship("Tenant", back_populates="products")
    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    sales = relationship("Sale", back_populates="product", cascade="all, delete-orphan")
    stock_movements = relationship("StockMovement", back_populates="product", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_products_code', 'tenant_id', 'code', unique=True),
    )
```

## 🔐 CONTRAINTES MULTI-TENANT

### Règles Strictes

1. **Toute table (sauf `tenants`) DOIT avoir `tenant_id`**
2. **Index composite systématique** : `(tenant_id, other_columns)`
3. **Constraints UNIQUE incluent `tenant_id`** : `UNIQUE(tenant_id, code)`
4. **Foreign Keys vérifient `tenant_id`** (même tenant)
5. **Queries TOUJOURS filtrées par `tenant_id`**

### Validation au niveau Service

```python
def get_product(db: Session, product_id: UUID, tenant_id: UUID) -> Product:
    """TOUJOURS filtrer par tenant_id"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.tenant_id == tenant_id  # CRITIQUE - Isolation tenant
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product
```

---

**Ce schéma garantit** :
- ✅ Isolation stricte des données par tenant
- ✅ Performance optimale (index adaptés)
- ✅ Intégrité référentielle
- ✅ Historique complet des opérations
- ✅ Scalabilité (partitionnement possible)