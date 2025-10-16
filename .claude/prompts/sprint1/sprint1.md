# PROMPTS CLAUDE CODE - DIGIBOOST PME
## Guide d'Implémentation Séquentielle avec Claude Code

**Version** : 1.0 MVP  
**Date** : Octobre 2025  
**Usage** : Copier-coller ces prompts dans Claude Code en suivant l'ordre

---

## 📋 TABLE DES MATIÈRES

1. [Instructions Générales](#instructions-générales)
2. [Sprint 1 - Semaine 1 : Setup & Backend Foundation](#sprint-1---semaine-1--setup--backend-foundation)
3. [Sprint 1 - Semaine 2 : Dashboard Backend & Frontend](#sprint-1---semaine-2--dashboard-backend--frontend)
4. [Sprint 2 : Système Alerting](#sprint-2--système-alerting)
5. [Sprint 3 : Analyses & Prédictions](#sprint-3--analyses--prédictions)
6. [Sprint 4 : Rapports & Finitions](#sprint-4--rapports--finitions)

---

## INSTRUCTIONS GÉNÉRALES

### Comment Utiliser Ces Prompts

1. **Pré-requis** : Avoir suivi le Guide Démarrage Rapide (installation Docker, Python, Node.js)
2. **Ordre strict** : Suivre les prompts dans l'ordre numéroté
3. **Validation** : Tester chaque étape avant de passer à la suivante
4. **Contexte** : Toujours fournir le contexte complet à Claude Code
5. **Fichiers** : Avoir les documents d'architecture et specs accessibles

### Format Standard de Prompt

```
CONTEXTE:
[Description de ce qui a été fait jusqu'ici]

OBJECTIF:
[Ce qui doit être implémenté]

SPÉCIFICATIONS:
[Détails techniques précis]

CONTRAINTES:
[Limitations et règles à respecter]

CRITÈRES D'ACCEPTATION:
[Comment vérifier que c'est terminé]

FICHIERS À CRÉER/MODIFIER:
[Liste des fichiers concernés]
```

---

## SPRINT 1 - SEMAINE 1 : SETUP & BACKEND FOUNDATION

### 🔧 PROMPT 1.1 : Setup Projet Backend

```
CONTEXTE:
Je démarre le projet Digiboost PME, une plateforme d'intelligence supply chain pour PME sénégalaises. Je dois créer la structure backend FastAPI avec architecture multi-tenant.

OBJECTIF:
Créer la structure complète du projet backend FastAPI avec:
- Structure de dossiers recommandée
- Configuration de base (config.py)
- Point d'entrée FastAPI (main.py)
- Fichier requirements.txt
- Docker Compose (PostgreSQL + Redis)
- Configuration environnement (.env)

SPÉCIFICATIONS TECHNIQUES:
- FastAPI 0.104+
- Python 3.11+
- PostgreSQL 15+ comme base de données principale
- Redis 7+ pour cache et queue
- Architecture multi-tenant (shared database avec tenant_id)
- Structure modulaire (api, models, schemas, services, core)

STRUCTURE REQUISE:
```
digiboost-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Point entrée FastAPI
│   ├── config.py               # Configuration
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py             # Dépendances communes
│   │   └── v1/
│   │       └── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py         # JWT, hashing
│   │   ├── tenant_context.py   # Multi-tenant
│   │   └── exceptions.py       # Exceptions custom
│   ├── models/
│   │   ├── __init__.py
│   │   └── base.py             # Modèle base
│   ├── schemas/
│   │   └── __init__.py
│   ├── services/
│   │   └── __init__.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py          # Gestion sessions
│   │   └── base_class.py       # Classes base
│   └── utils/
│       └── __init__.py
├── alembic/
│   └── versions/
├── tests/
│   └── __init__.py
├── docker-compose.yml
├── .env
├── .env.example
├── requirements.txt
├── .gitignore
└── README.md
```

CONTENU requirements.txt:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
celery==5.3.4
redis==5.0.1
pydantic==2.5.0
pydantic-settings==2.1.0
httpx==0.25.2
python-json-logger==2.0.7
pytest==7.4.3
pytest-asyncio==0.21.1
```

CONTENU .env.example:
```
APP_NAME=Digiboost PME
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your-super-secret-key-min-32-chars
API_V1_PREFIX=/api/v1

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/digiboost_dev
REDIS_URL=redis://localhost:6379/0

ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

CONTENU docker-compose.yml:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: digiboost_postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: digiboost_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: digiboost_redis
    command: redis-server --appendonly yes
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  redis_data:
```

CONFIGURATION app/config.py:
Créer Settings avec Pydantic BaseSettings pour lire variables .env

CONFIGURATION app/main.py:
- Créer instance FastAPI
- Ajouter middleware CORS
- Endpoint GET / (root)
- Endpoint GET /health (health check)

CRITÈRES D'ACCEPTATION:
✅ Structure dossiers créée complètement
✅ Tous les __init__.py présents
✅ requirements.txt contient toutes les dépendances
✅ .env.example documenté
✅ docker-compose.yml fonctionnel
✅ app/config.py lit variables environnement
✅ app/main.py démarre sans erreur
✅ curl http://localhost:8000/health retourne {"status":"ok"}
✅ PostgreSQL et Redis démarrent avec docker-compose up

COMMANDES DE TEST:
```bash
docker-compose up -d
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
curl http://localhost:8000/health
```
```

---

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
docker-compose exec postgres psql -U postgres -d digiboost_dev -c "\dt"
```
```

---

### 🔧 PROMPT 1.3 : Authentification JWT & Sécurité

```
CONTEXTE:
Les modèles de base de données sont créés. Je dois maintenant implémenter le système d'authentification JWT complet avec:
- Génération et validation tokens JWT
- Hash mots de passe bcrypt
- Middleware multi-tenant
- Endpoints login/refresh
- Système de dépendances pour routes protégées

OBJECTIF:
Créer système auth JWT production-ready avec:
- Access tokens (15 min)
- Refresh tokens (7 jours)
- Hash passwords sécurisé
- Extraction automatique tenant_id
- Context variables pour tenant courant
- Routes publiques vs protégées

SPÉCIFICATIONS TECHNIQUES:

1. CORE SECURITY (app/core/security.py):
```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Créer access token JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": expire,
        "type": "access"
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """Créer refresh token JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str, expected_type: str = "access") -> Optional[dict]:
    """Vérifier et décoder token JWT"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != expected_type:
            return None
        return payload
    except JWTError:
        return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifier mot de passe"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hasher mot de passe"""
    return pwd_context.hash(password)
```

2. TENANT CONTEXT (app/core/tenant_context.py):
```python
from contextvars import ContextVar
from uuid import UUID
from typing import Optional

# Context variable pour tenant courant
current_tenant_id: ContextVar[Optional[UUID]] = ContextVar('current_tenant_id', default=None)

def get_current_tenant_id() -> Optional[UUID]:
    """Récupérer tenant_id du contexte"""
    return current_tenant_id.get()

def set_current_tenant_id(tenant_id: UUID) -> None:
    """Définir tenant_id dans contexte"""
    current_tenant_id.set(tenant_id)

def clear_current_tenant_id() -> None:
    """Nettoyer tenant_id du contexte"""
    current_tenant_id.set(None)
```

3. DEPENDENCIES (app/api/deps.py):
```python
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import SessionLocal
from app.core.security import verify_token
from app.core.tenant_context import set_current_tenant_id
from app.models.user import User

security = HTTPBearer()

def get_db() -> Generator:
    """Dependency pour session DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Dependency: extraction utilisateur depuis JWT"""
    token = credentials.credentials
    payload = verify_token(token, "access")
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    tenant_id = payload.get("tenant_id")
    
    # Set tenant context
    set_current_tenant_id(UUID(tenant_id))
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user
```

4. SCHEMAS AUTH (app/schemas/auth.py):
```python
from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str  # user_id
    tenant_id: str
    exp: int
    type: str
```

5. ROUTER AUTH (app/api/v1/auth.py):
Implémenter:
- POST /login (email + password → tokens)
- POST /refresh (refresh_token → nouveaux tokens)
- GET /me (user courant, protégé)

MIDDLEWARE TENANT (app/main.py):
Ajouter middleware qui extrait tenant_id et le met en contexte

CRITÈRES D'ACCEPTATION:
✅ Hash passwords fonctionnel (passlib bcrypt)
✅ Tokens JWT générés avec bonnes expirations
✅ Token refresh fonctionne
✅ Middleware tenant extrait et set tenant_id
✅ Dependency get_current_user protège routes
✅ Login retourne access + refresh tokens
✅ Route /me retourne user courant
✅ Tokens expirés rejetés avec 401
✅ Tests: login user → récupérer token → accéder /me

COMMANDES DE TEST:
```bash
# Créer utilisateur test (via psql ou script Python)
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Utiliser token
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```
```

---

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

## SPRINT 1 - SEMAINE 2 : DASHBOARD BACKEND & FRONTEND

### 🔧 PROMPT 1.5 : Setup Projet Frontend React

```
CONTEXTE:
Le backend avec premier dashboard est fonctionnel. Je dois maintenant créer le projet frontend React avec TypeScript, TailwindCSS, et configuration PWA pour mode offline.

OBJECTIF:
Initialiser projet React complet avec:
- Vite + React 18 + TypeScript
- TailwindCSS + Shadcn/ui
- TanStack Query (React Query)
- React Router 6
- Configuration PWA (Service Worker)
- Structure dossiers recommandée
- Client API avec axios
- Store auth (Zustand)

SPÉCIFICATIONS TECHNIQUES:

COMMANDES INITIALISATION:
```bash
# Créer projet Vite
npm create vite@latest digiboost-frontend -- --template react-ts
cd digiboost-frontend

# Installer dépendances
npm install

# UI & Styling
npm install -D tailwindcss postcss autoprefixer
npm install clsx tailwind-merge
npx tailwindcss init -p

# State & Data
npm install @tanstack/react-query
npm install zustand
npm install axios

# Routing & Forms
npm install react-router-dom
npm install react-hook-form @hookform/resolvers
npm install zod

# Charts & Icons
npm install recharts
npm install lucide-react

# PWA
npm install -D vite-plugin-pwa
npm install dexie  # IndexedDB wrapper
npm install workbox-window

# Dev tools
npm install -D @types/node
```

STRUCTURE REQUISE:
```
digiboost-frontend/
├── public/
│   ├── manifest.json
│   └── icons/
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── api/
│   │   ├── client.ts           # Client HTTP
│   │   ├── auth.ts             # API auth
│   │   └── dashboards.ts       # API dashboards
│   ├── components/
│   │   ├── ui/                 # Composants base
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── MainLayout.tsx
│   │   └── common/
│   │       ├── LoadingSpinner.tsx
│   │       └── ErrorBoundary.tsx
│   ├── features/
│   │   ├── auth/
│   │   │   ├── components/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   └── ProtectedRoute.tsx
│   │   │   ├── hooks/
│   │   │   │   └── useAuth.ts
│   │   │   └── store/
│   │   │       └── authStore.ts
│   │   └── dashboard/
│   │       ├── components/
│   │       └── hooks/
│   ├── hooks/
│   │   ├── useNetworkStatus.ts
│   │   └── useOfflineSync.ts
│   ├── lib/
│   │   ├── utils.ts
│   │   └── constants.ts
│   ├── services/
│   │   ├── offlineService.ts
│   │   └── cacheService.ts
│   ├── stores/
│   │   └── useAppStore.ts
│   ├── types/
│   │   ├── api.types.ts
│   │   └── models.types.ts
│   ├── styles/
│   │   └── globals.css
│   └── routes/
│       └── index.tsx
├── .env
├── .env.example
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
└── package.json
```

FICHIER .env:
```
VITE_API_URL=http://localhost:8000
VITE_API_V1_PREFIX=/api/v1
VITE_APP_NAME=Digiboost PME
```

CONFIGURATION VITE (vite.config.ts):
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';
import path from 'path';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'icons/**/*'],
      manifest: {
        name: 'Digiboost PME',
        short_name: 'Digiboost',
        description: 'Intelligence Supply Chain pour PME',
        theme_color: '#4F46E5',
        background_color: '#ffffff',
        display: 'standalone',
        orientation: 'portrait',
        start_url: '/',
        icons: [
          {
            src: '/icons/icon-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: '/icons/icon-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      },
      workbox: {
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/.*\/api\/v1\/dashboards/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'dashboard-cache',
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 300
              }
            }
          }
        ]
      }
    })
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
});
```

CONFIGURATION TAILWIND (tailwind.config.js):
```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eef2ff',
          100: '#e0e7ff',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
        },
      },
    },
  },
  plugins: [],
}
```

CLIENT API (src/api/client.ts):
```typescript
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;
const API_V1 = import.meta.env.VITE_API_V1_PREFIX;

export const apiClient = axios.create({
  baseURL: `${API_URL}${API_V1}`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Intercepteur pour refresh token
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Gérer refresh token
    }
    return Promise.reject(error);
  }
);
```

STORE AUTH (src/features/auth/store/authStore.ts):
```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  full_name: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  setAuth: (user: User, accessToken: string, refreshToken: string) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      setAuth: (user, accessToken, refreshToken) =>
        set({ user, accessToken, refreshToken }),
      clearAuth: () =>
        set({ user: null, accessToken: null, refreshToken: null }),
    }),
    {
      name: 'auth-storage',
    }
  )
);
```

CRITÈRES D'ACCEPTATION:
✅ Projet Vite créé et démarre
✅ TailwindCSS fonctionnel
✅ Structure dossiers complète
✅ Configuration PWA (manifest.json)
✅ Client API axios configuré
✅ Store auth Zustand créé
✅ Types TypeScript pour API
✅ npm run dev démarre sur http://localhost:5173
✅ npm run build génère dist/ sans erreur

COMMANDES DE TEST:
```bash
npm run dev
npm run build
npm run preview
```
```

---

### 🔧 PROMPT 1.6 : Auth Frontend & Layout Principal

```
CONTEXTE:
Le projet frontend est initialisé. Je dois créer l'interface d'authentification complète et le layout principal de l'application.

OBJECTIF:
Implémenter:
- Page login avec formulaire
- Gestion tokens (access + refresh)
- Hook useAuth
- ProtectedRoute component
- Layout principal (Header + Sidebar + Content)
- Navigation
- Indicateur connexion réseau

SPÉCIFICATIONS:

PAGE LOGIN (src/features/auth/components/LoginForm.tsx):
- Formulaire email + password
- Validation avec react-hook-form + zod
- Appel API /auth/login
- Stockage tokens
- Redirection après login
- Messages d'erreur
- Loading state

HOOK AUTH (src/features/auth/hooks/useAuth.ts):
```typescript
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { authApi } from '@/api/auth';

export const useAuth = () => {
  const navigate = useNavigate();
  const { setAuth, clearAuth, user, accessToken } = useAuthStore();

  const loginMutation = useMutation({
    mutationFn: authApi.login,
    onSuccess: (data) => {
      setAuth(data.user, data.access_token, data.refresh_token);
      navigate('/dashboard');
    },
  });

  const logout = () => {
    clearAuth();
    navigate('/login');
  };

  return {
    login: loginMutation.mutate,
    logout,
    user,
    isAuthenticated: !!accessToken,
    isLoading: loginMutation.isPending,
    error: loginMutation.error,
  };
};
```

PROTECTED ROUTE (src/features/auth/components/ProtectedRoute.tsx):
```typescript
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { accessToken } = useAuthStore();

  if (!accessToken) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};
```

LAYOUT HEADER (src/components/layout/Header.tsx):
- Logo Digiboost
- Nom utilisateur
- Indicateur connexion (online/offline)
- Bouton logout

LAYOUT SIDEBAR (src/components/layout/Sidebar.tsx):
Navigation:
- 📊 Vue d'Ensemble
- 📦 Gestion Stock
- 📈 Analyse Ventes
- 🔮 Prédictions
- 🚨 Alertes
- 📄 Rapports
- ⚙️ Paramètres

MAIN LAYOUT (src/components/layout/MainLayout.tsx):
```typescript
export const MainLayout = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  );
};
```

NETWORK INDICATOR (src/components/common/NetworkIndicator.tsx):
```typescript
import { useNetworkStatus } from '@/hooks/useNetworkStatus';
import { Wifi, WifiOff } from 'lucide-react';

export const NetworkIndicator = () => {
  const { isOnline } = useNetworkStatus();

  return (
    <div className={`flex items-center gap-2 text-sm ${isOnline ? 'text-green-600' : 'text-amber-600'}`}>
      {isOnline ? <Wifi className="w-4 h-4" /> : <WifiOff className="w-4 h-4" />}
      <span>{isOnline ? 'Connecté' : 'Hors ligne'}</span>
    </div>
  );
};
```

ROUTES (src/routes/index.tsx):
```typescript
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LoginForm } from '@/features/auth/components/LoginForm';
import { ProtectedRoute } from '@/features/auth/components/ProtectedRoute';
import { MainLayout } from '@/components/layout/MainLayout';
import { DashboardOverview } from '@/features/dashboard/components/DashboardOverview';

export const AppRoutes = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginForm />} />
        
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <MainLayout>
              <Routes>
                <Route index element={<DashboardOverview />} />
                {/* Autres routes dashboard */}
              </Routes>
            </MainLayout>
          </ProtectedRoute>
        } />
        
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
};
```

CRITÈRES D'ACCEPTATION:
✅ Page login accessible /login
✅ Formulaire validation fonctionne
✅ Login appelle API backend
✅ Tokens stockés après login réussi
✅ Redirection vers /dashboard après login
✅ ProtectedRoute bloque accès si non auth
✅ Layout Header + Sidebar s'affiche
✅ Navigation sidebar fonctionne
✅ Indicateur réseau change état
✅ Logout vide tokens et redirige /login

COMMANDES DE TEST:
```bash
npm run dev
# Tester login avec user créé en backend
# Vérifier tokens dans localStorage dev tools
# Tester navigation
# Tester logout
```
```

---

### 🔧 PROMPT 1.7 : Dashboard Vue d'Ensemble Frontend

```
CONTEXTE:
L'authentification et le layout sont fonctionnels. Je dois créer le dashboard "Vue d'Ensemble" frontend qui affiche les KPIs du backend.

OBJECTIF:
Créer dashboard responsive avec:
- 3 sections: Santé Stock, Performance Ventes, Top/Flop
- KPI Cards avec icônes
- Graphiques (Recharts)
- Loading states
- Error handling
- Responsive mobile
- Rafraîchissement automatique

SPÉCIFICATIONS:

HOOK DASHBOARD (src/features/dashboard/hooks/useDashboardData.ts):
```typescript
import { useQuery } from '@tanstack/react-query';
import { dashboardsApi } from '@/api/dashboards';

export const useDashboardOverview = () => {
  return useQuery({
    queryKey: ['dashboard', 'overview'],
    queryFn: () => dashboardsApi.getOverview(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 30 * 1000, // Rafraîchir toutes les 30s
    refetchOnWindowFocus: true,
  });
};
```

API CLIENT (src/api/dashboards.ts):
```typescript
import { apiClient } from './client';

export const dashboardsApi = {
  getOverview: async () => {
    const { data } = await apiClient.get('/dashboards/overview');
    return data;
  },
};
```

COMPOSANT KPI CARD (src/features/dashboard/components/KPICard.tsx):
```typescript
interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  color?: 'green' | 'red' | 'blue' | 'amber';
}

export const KPICard = ({ title, value, subtitle, icon, trend, trendValue, color = 'blue' }: KPICardProps) => {
  // Implémenter card avec styles Tailwind
  // Afficher icône, titre, valeur, trend
};
```

SECTION SANTÉ STOCK (src/features/dashboard/components/StockHealthSection.tsx):
```typescript
export const StockHealthSection = ({ data }: { data: any }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <KPICard
        title="Total Produits"
        value={data.total_products}
        icon={<Package className="w-6 h-6" />}
        color="blue"
      />
      <KPICard
        title="Ruptures"
        value={data.rupture_count}
        subtitle="Produits en rupture"
        icon={<AlertTriangle className="w-6 h-6" />}
        color="red"
      />
      <KPICard
        title="Stock Faible"
        value={data.low_stock_count}
        subtitle="À réapprovisionner"
        icon={<AlertCircle className="w-6 h-6" />}
        color="amber"
      />
      <KPICard
        title="Valorisation"
        value={`${(data.total_stock_value / 1000000).toFixed(1)}M FCFA`}
        subtitle="Stock total"
        icon={<DollarSign className="w-6 h-6" />}
        color="green"
      />
    </div>
  );
};
```

SECTION PERFORMANCE VENTES (src/features/dashboard/components/SalesPerformanceSection.tsx):
- CA 7 jours (KPI Card)
- CA 30 jours (KPI Card)
- Graphique évolution CA (Line Chart Recharts)
- Nombre transactions

GRAPHIQUE CA (src/features/dashboard/components/RevenueChart.tsx):
```typescript
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export const RevenueChart = ({ data }: { data: any[] }) => {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="revenue" stroke="#4F46E5" strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  );
};
```

DASHBOARD PRINCIPAL (src/features/dashboard/components/DashboardOverview.tsx):
```typescript
import { useDashboardOverview } from '../hooks/useDashboardData';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { StockHealthSection } from './StockHealthSection';
import { SalesPerformanceSection } from './SalesPerformanceSection';

export const DashboardOverview = () => {
  const { data, isLoading, error, refetch } = useDashboardOverview();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="text-center p-8">
        <p className="text-red-600">Erreur de chargement</p>
        <button onClick={() => refetch()} className="mt-4 btn-primary">
          Réessayer
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Vue d'Ensemble</h1>
        <button onClick={() => refetch()} className="btn-secondary">
          Actualiser
        </button>
      </div>

      {/* Santé Stock */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Santé Stock</h2>
        <StockHealthSection data={data.stock_health} />
      </section>

      {/* Performance Ventes */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Performance Ventes</h2>
        <SalesPerformanceSection data={data.sales_performance} />
      </section>

      {/* Top/Flop Produits */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TopProductsCard products={data.top_products} />
        <DormantProductsCard products={data.dormant_products} />
      </div>
    </div>
  );
};
```

RESPONSIVE DESIGN:
- Mobile (< 768px): Cards empilées verticalement
- Tablet (768-1024px): 2 colonnes
- Desktop (> 1024px): 4 colonnes

CRITÈRES D'ACCEPTATION:
✅ Dashboard affiche données backend
✅ KPI Cards affichent valeurs correctes
✅ Graphiques Recharts fonctionnels
✅ Loading spinner pendant chargement
✅ Message erreur si API échoue
✅ Bouton "Actualiser" rafraîchit données
✅ Rafraîchissement auto 30s
✅ Responsive mobile/tablet/desktop
✅ Performance < 3s chargement
✅ Tests: Login → Dashboard affiche KPIs

COMMANDES DE TEST:
```bash
npm run dev
# Login → Dashboard
# Vérifier KPIs affichés
# Tester responsive (Chrome DevTools)
# Vérifier rafraîchissement auto (Network tab)
```
```

---

## PROMPT SUIVANT : SPRINT 2

Voulez-vous que je continue avec les prompts pour le Sprint 2 (Système d'Alerting), Sprint 3 (Analyses & Prédictions), et Sprint 4 (Rapports & Finitions) ?

Les prompts suivants couvriront:
- Sprint 2: Modèles Alert, Celery tasks, WhatsApp API, UI gestion alertes
- Sprint 3: Prédictions ruptures, analyses ventes, dashboards avancés
- Sprint 4: Génération rapports Excel/PDF, préparation agent IA, tests E2E

Dois-je créer un second artefact avec les prompts Sprint 2-4 ?
