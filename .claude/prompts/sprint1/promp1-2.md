### 🔧 PROMPT 1.2 : Modèles SQLAlchemy & Multi-Tenant

```
CONTEXTE:
Le projet backend est initialisé. Je dois maintenant créer les modèles de données SQLAlchemy avec architecture multi-tenant. Les modèles doivent suivre la spécification fonctionnelle supply_chain_spec_v3.md.

OBJECTIF:
Créer les modèles SQLAlchemy de base avec:
- Système multi-tenant (tenant_id sur chaque table)
- Modèles: Tenant, User, Category, Supplier, Product, Sale, StockMovement, Alert, AlertHistory
- Relations entre modèles
- Contraintes d'intégrité
- Timestamps automatiques
- Configuration Alembic pour migrations

SPÉCIFICATIONS TECHNIQUES:

1. MODÈLE BASE (app/models/base.py):
```python
from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import declared_attr
from app.db.base_class import Base

class TimestampMixin:
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

class TenantMixin:
    @declared_attr
    def tenant_id(cls):
        from sqlalchemy import Column, ForeignKey
        from sqlalchemy.dialects.postgresql import UUID
        return Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)
```

2. MODÈLE TENANT (app/models/tenant.py):
```python
from sqlalchemy import Column, String, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.models.base import TimestampMixin
from app.db.base_class import Base

class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    ninea = Column(String(50))  # Numéro entreprise Sénégal
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    settings = Column(JSON, default={})  # Config alertes, objectifs
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relations
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="tenant", cascade="all, delete-orphan")
    sales = relationship("Sale", back_populates="tenant", cascade="all, delete-orphan")
```

3. MODÈLE USER (app/models/user.py):
- Champs: id, tenant_id, email, hashed_password, full_name, role, whatsapp_number, is_active
- Relation avec Tenant
- Index sur email (unique global)

4. MODÈLE PRODUCT (app/models/product.py):
Selon spéc:
- Code produit (unique par tenant)
- Nom, catégorie, fournisseur
- Prix achat, prix vente, unité
- Stock actuel, stock min, stock max
- Description, barcode, is_active
- Relations: Category, Supplier, Sales, StockMovements

5. MODÈLE SALE (app/models/sale.py):
- Date vente, produit, quantité, prix unitaire, montant total
- Optionnel: order_number, customer_name, status
- Relation: Product

6. MODÈLE ALERT (app/models/alert.py):
- Nom, type alerte, conditions (JSON), channels (JSON), recipients (JSON)
- is_active, timestamps
- Relation: AlertHistory

CONTRAINTES MULTI-TENANT:
- Chaque modèle (sauf Tenant) doit avoir tenant_id
- Index composite (tenant_id, <autres_champs>) pour performance
- Contrainte UNIQUE doit inclure tenant_id où applicable

CONFIGURATION ALEMBIC:
- Initialiser Alembic: alembic init alembic
- Configurer alembic/env.py pour importer Base et modèles
- Créer première migration: alembic revision --autogenerate -m "Initial schema"

FICHIERS À CRÉER:
- app/db/base_class.py (DeclarativeBase)
- app/db/session.py (engine, SessionLocal)
- app/models/base.py (Mixins)
- app/models/tenant.py
- app/models/user.py
- app/models/category.py
- app/models/supplier.py
- app/models/product.py
- app/models/sale.py
- app/models/stock_movement.py
- app/models/alert.py
- app/models/alert_history.py
- alembic/env.py (configuration)

CRITÈRES D'ACCEPTATION:
✅ Tous les modèles créés avec champs corrects
✅ Relations SQLAlchemy définies
✅ Contraintes UNIQUE avec tenant_id
✅ Index créés sur colonnes fréquentes (tenant_id, email, code, etc.)
✅ Alembic configuré correctement
✅ Migration initiale générée sans erreur
✅ Migration appliquée: alembic upgrade head
✅ Tables créées en base: \dt dans psql
✅ Contraintes vérifiables: \d tenants dans psql

COMMANDES DE TEST:
```bash
# Initialiser Alembic
alembic init alembic

# Générer migration
alembic revision --autogenerate -m "Initial schema"

# Appliquer migration
alembic upgrade head

# Vérifier tables
docker-compose exec postgres psql -U ais_db_owner -d DigiboostPME -c "\dt"
```
```

---
