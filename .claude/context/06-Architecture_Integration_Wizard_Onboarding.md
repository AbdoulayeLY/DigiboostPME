# ARCHITECTURE TECHNIQUE - INTÉGRATION WIZARD ONBOARDING
## Module d'Onboarding Light - DigiboostPME Phase 0

**Version** : 1.0  
**Date** : 23 Octobre 2025  
**Auteur** : Architecte Technique Digiboost  
**Contexte** : Intégration wizard onboarding au POC DigiboostPME existant

---

## 📋 TABLE DES MATIÈRES

1. [Vue d'Ensemble Intégration](#1-vue-densemble-intégration)
2. [Architecture Technique Détaillée](#2-architecture-technique-détaillée)
3. [Modèle de Données Étendu](#3-modèle-de-données-étendu)
4. [Stack Technique & Dépendances](#4-stack-technique--dépendances)
5. [Structure Projet Étendue](#5-structure-projet-étendue)
6. [Roadmap Implémentation](#6-roadmap-implémentation)
7. [Découpage en Sprints](#7-découpage-en-sprints)
8. [Prompts Claude Code par Sprint](#8-prompts-claude-code-par-sprint)

---

## 1. VUE D'ENSEMBLE INTÉGRATION

### 1.1 Contexte Actuel

**POC EXISTANT** :
- ✅ Backend FastAPI avec authentification JWT
- ✅ Frontend React avec dashboards opérationnels
- ✅ Base PostgreSQL avec modèle multi-tenant
- ✅ Système d'alerting WhatsApp
- ✅ Génération rapports (Excel, PDF)
- ✅ Architecture modulaire extensible

**GAP À COMBLER** :
- ❌ Pas d'interface admin pour onboarding
- ❌ Création manuelle des tenants via SQL
- ❌ Pas de template Excel standardisé
- ❌ Import données complexe et manuel
- ❌ Activation tenant non automatisée

### 1.2 Objectifs Module Onboarding

```
OBJECTIFS FONCTIONNELS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Wizard admin 4 étapes (Tenant → Users → Template → Import)
✅ Génération template Excel personnalisé
✅ Import asynchrone avec validation
✅ Activation automatique tenant + dashboards
✅ Gestion identifiants flexibles (email/téléphone)
✅ Changement mot de passe obligatoire 1ère connexion

OBJECTIFS TECHNIQUES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Intégration transparente architecture existante
✅ Réutilisation maximum code POC
✅ Extension modèle données (non breaking)
✅ Isolation module admin (sécurité)
✅ Performance import (Celery async)
✅ Traçabilité complète (audit logs)
```

### 1.3 Principes Architecture

```
PRINCIPES DIRECTEURS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Extension > Modification : Étendre le POC, ne pas le casser
2. Isolation Admin : Routes /admin séparées, protection renforcée
3. Backward Compatible : Anciens tenants continuent fonctionner
4. Async-First : Import données via Celery (pas de timeout)
5. Validation Stricte : Schéma Excel + règles métier
6. Idempotence : Retry-safe, transaction atomique
7. Observabilité : Logs structurés + métriques
```

---

## 2. ARCHITECTURE TECHNIQUE DÉTAILLÉE

### 2.1 Architecture Globale Extended

```
┌─────────────────────────────────────────────────────────────────┐
│                    UTILISATEURS & INTERFACES                     │
├──────────────────────┬──────────────────────────────────────────┤
│   CEO/Admin          │         Gérants PME                      │
│  (Interface Admin)   │    (Interface Standard)                  │
└──────────┬───────────┴────────────┬─────────────────────────────┘
           │                        │
           │ HTTPS                  │ HTTPS
           │                        │
┌──────────▼────────────────────────▼─────────────────────────────┐
│                   FRONTEND REACT (Extended)                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  EXISTING MODULES                                        │   │
│  │  • Dashboard Overview, Stock, Sales, Predictions         │   │
│  │  • Alerting, Reports, Settings                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  NEW MODULE: ADMIN WIZARD                                │   │
│  │  • Wizard Onboarding (4 steps)                           │   │
│  │  • Template Generator                                    │   │
│  │  • Import Progress Tracker                               │   │
│  │  • Tenant Management                                     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────┬────────────────────────────────────────┘
                          │
                          │ HTTP REST API (JWT)
                          │
┌─────────────────────────▼────────────────────────────────────────┐
│               BACKEND FASTAPI (Extended)                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  EXISTING SERVICES                                       │   │
│  │  • auth_service, dashboard_service, product_service      │   │
│  │  • sales_service, prediction_service, alert_service      │   │
│  │  • report_service, analytics_service                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  NEW SERVICES                                            │   │
│  │  • onboarding_service : Logique wizard                   │   │
│  │  • template_service : Génération Excel                   │   │
│  │  • import_service : Validation + Import                  │   │
│  │  • admin_service : Gestion tenants/users admin           │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  NEW ROUTES                                              │   │
│  │  • /api/v1/admin/onboarding/* (Protected)               │   │
│  │  • /api/v1/auth/change-password-first-login              │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────┬────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼──────┐  ┌───────▼──────┐  ┌──────▼───────┐
│ PostgreSQL   │  │    Redis     │  │    Celery    │
│  (Extended)  │  │    Cache     │  │   Workers    │
│              │  │              │  │  (Extended)  │
│ • tenants    │  │              │  │              │
│ • sites      │  │              │  │ NEW QUEUE:   │
│ • users      │  │              │  │ • onboarding │
│ • products   │  │              │  │   (import)   │
│ • sales      │  │              │  │              │
│              │  │              │  │              │
│ NEW TABLES:  │  │              │  │              │
│ • onboarding_│  │              │  │              │
│   sessions   │  │              │  │              │
│ • audit_logs │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

### 2.2 Flux Onboarding Complet

```
┌─────────────────────────────────────────────────────────────────┐
│                  CEO ADMIN (Interface Web)                       │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│ ÉTAPE 1 : CRÉATION TENANT & SITE                                │
│                                                                  │
│ Frontend → POST /api/v1/admin/onboarding/create-tenant          │
│                                                                  │
│ Backend :                                                        │
│   1. Validation données entreprise                              │
│   2. Création tenant (table tenants)                            │
│   3. Création site principal (table sites)                      │
│   4. Création session onboarding (tracking)                     │
│   5. Return tenant_id + site_id                                 │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│ ÉTAPE 2 : CRÉATION UTILISATEURS                                 │
│                                                                  │
│ Frontend → POST /api/v1/admin/onboarding/create-users           │
│                                                                  │
│ Backend :                                                        │
│   1. Validation identifiants (email/phone unique)               │
│   2. Hash mot de passe par défaut                               │
│   3. Création users (must_change_password=true)                 │
│   4. Return liste users créés                                   │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│ ÉTAPE 3 : GÉNÉRATION TEMPLATE EXCEL                             │
│                                                                  │
│ Frontend → GET /api/v1/admin/onboarding/generate-template/      │
│            {tenant_id}                                           │
│                                                                  │
│ Backend :                                                        │
│   1. Génération fichier Excel (OpenPyXL)                        │
│   2. Onglets : Produits, Ventes (avec instructions)            │
│   3. Validation intégrée (formules Excel)                       │
│   4. Return file stream (download)                              │
│                                                                  │
│ ⏱️ CEO remplit template avec client (15-30 min)                 │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│ ÉTAPE 4 : IMPORT DONNÉES                                        │
│                                                                  │
│ Frontend → POST /api/v1/admin/onboarding/upload-template/       │
│            {tenant_id} (multipart/form-data)                     │
│                                                                  │
│ Backend :                                                        │
│   1. Validation structure fichier                               │
│   2. Lancement Celery task import_tenant_data                   │
│   3. Return task_id                                             │
│                                                                  │
│ Frontend → Polling GET /api/v1/admin/onboarding/import-status/  │
│            {task_id}                                             │
│                                                                  │
│ Celery Worker (Queue onboarding) :                              │
│   1. Parsing Excel                                              │
│   2. Validation métier données                                  │
│   3. Transaction atomique :                                     │
│      • Insert products                                          │
│      • Insert sales                                             │
│   4. Post-processing :                                          │
│      • Calcul score qualité                                     │
│      • Activation tenant (is_active=true)                       │
│      • Activation dashboards                                    │
│      • Refresh vues matérialisées                               │
│      • Update session onboarding (status=completed)             │
│   5. Notification fin import                                    │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│ RÉSULTAT : TENANT OPÉRATIONNEL                                  │
│                                                                  │
│ • Tenant activé                                                  │
│ • Users peuvent se connecter                                     │
│ • Dashboards visibles avec données                              │
│ • Première connexion → Changement mot de passe obligatoire      │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 Flux Première Connexion User

```
┌─────────────────────────────────────────────────────────────────┐
│ UTILISATEUR FINAL (Gérant PME)                                  │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│ TENTATIVE CONNEXION                                              │
│                                                                  │
│ Frontend → POST /api/v1/auth/login                               │
│   Body: { identifier, password: "Digiboost2025" }               │
│                                                                  │
│ Backend :                                                        │
│   1. Vérification credentials                                    │
│   2. Check must_change_password flag                            │
│   3. Si true :                                                   │
│      • Return { must_change_password: true, temp_token }        │
│   4. Si false :                                                  │
│      • Return access_token + refresh_token standard             │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│ CHANGEMENT MOT DE PASSE (si must_change_password=true)          │
│                                                                  │
│ Frontend → Affiche modal changement MDP                          │
│                                                                  │
│ User → Saisit ancien + nouveau mot de passe                      │
│                                                                  │
│ Frontend → POST /api/v1/auth/change-password-first-login         │
│   Headers: Authorization Bearer {temp_token}                     │
│   Body: { old_password, new_password }                           │
│                                                                  │
│ Backend :                                                        │
│   1. Validation temp_token                                       │
│   2. Vérification old_password                                   │
│   3. Validation nouveau MDP (force)                              │
│   4. Hash + update password                                      │
│   5. Set must_change_password = false                            │
│   6. Return access_token + refresh_token                         │
│                                                                  │
│ Frontend → Redirection automatique vers /dashboard              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. MODÈLE DE DONNÉES ÉTENDU

### 3.1 Schéma Complet (Extensions en Gras)

```sql
-- ============================================================
-- EXISTING TABLES (POC)
-- ============================================================

-- Table tenants (EXTENDED)
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    ninea VARCHAR(50),                    -- NOUVEAU
    sector VARCHAR(50),                   -- NOUVEAU
    country VARCHAR(2) DEFAULT 'SN',      -- NOUVEAU
    settings JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100)               -- NOUVEAU: "ceo_manual", "wizard", etc.
);

-- Table sites (EXTENDED)
CREATE TABLE sites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    address TEXT,                         -- NOUVEAU
    type VARCHAR(50) DEFAULT 'main',      -- NOUVEAU: "main", "branch"
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table users (EXTENDED)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255),                   -- Nullable maintenant
    phone VARCHAR(20),                    -- NOUVEAU: Identifier alternatif
    first_name VARCHAR(100) NOT NULL,     -- Split name
    last_name VARCHAR(100) NOT NULL,      -- Split name
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    must_change_password BOOLEAN DEFAULT FALSE,  -- NOUVEAU
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT unique_email UNIQUE (email),
    CONSTRAINT unique_phone UNIQUE (phone),
    CONSTRAINT check_identifier CHECK (email IS NOT NULL OR phone IS NOT NULL)
);

-- Table products (EXISTING - no change)
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    site_id UUID REFERENCES sites(id),
    code VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    unit_price DECIMAL(10,2),
    cost_price DECIMAL(10,2),
    current_stock INTEGER DEFAULT 0,
    reorder_point INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, code)
);

-- Table sales (EXISTING - no change)
CREATE TABLE sales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    site_id UUID REFERENCES sites(id),
    product_id UUID REFERENCES products(id),
    sale_date DATE NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- NEW TABLES (WIZARD ONBOARDING)
-- ============================================================

-- Table onboarding_sessions
-- Tracking des sessions d'onboarding pour audit et reprise
CREATE TABLE onboarding_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,  -- "in_progress", "completed", "failed"
    current_step INTEGER DEFAULT 1,  -- 1-4
    data JSONB DEFAULT '{}',      -- Données temporaires session
    created_by VARCHAR(255),      -- Email/nom admin qui fait l'onboarding
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    error_message TEXT,
    
    INDEX idx_tenant_status (tenant_id, status)
);

-- Table admin_audit_logs
-- Logs d'audit pour actions admin critiques
CREATE TABLE admin_audit_logs (
    id BIGSERIAL PRIMARY KEY,
    admin_user_id UUID,           -- NULL si action système
    action_type VARCHAR(100) NOT NULL,  -- "create_tenant", "create_user", "import_data"
    entity_type VARCHAR(50),      -- "tenant", "user", "product", "sale"
    entity_id UUID,
    details JSONB DEFAULT '{}',   -- Détails spécifiques action
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_action_date (action_type, created_at),
    INDEX idx_entity (entity_type, entity_id)
);

-- Table import_jobs
-- Tracking des jobs d'import asynchrones
CREATE TABLE import_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    session_id UUID REFERENCES onboarding_sessions(id),
    celery_task_id VARCHAR(255) UNIQUE,
    status VARCHAR(50) NOT NULL,  -- "pending", "running", "success", "failed"
    file_name VARCHAR(255),
    file_size_bytes BIGINT,
    progress_percent INTEGER DEFAULT 0,
    stats JSONB DEFAULT '{}',     -- Stats import (products_imported, sales_imported, etc.)
    error_details JSONB,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_tenant_status (tenant_id, status),
    INDEX idx_celery_task (celery_task_id)
);

-- ============================================================
-- INDEXES PERFORMANCE (EXTENSIONS)
-- ============================================================

CREATE INDEX idx_users_phone ON users(phone) WHERE phone IS NOT NULL;
CREATE INDEX idx_users_must_change_pwd ON users(must_change_password) WHERE must_change_password = TRUE;
CREATE INDEX idx_tenants_active ON tenants(is_active);
CREATE INDEX idx_onboarding_status ON onboarding_sessions(status, created_at);
```

### 3.2 Schéma Relationnel Visual

```
┌─────────────────────┐
│     tenants         │
│ ─────────────────── │
│ id (PK)             │◄───────┐
│ name                │        │
│ ninea               │        │
│ sector              │        │
│ is_active           │        │
│ created_by [NEW]    │        │
└─────────┬───────────┘        │
          │                    │
          │                    │
  ┌───────┴───────┐            │
  │               │            │
  ▼               ▼            │
┌─────────┐ ┌─────────────────┴───┐
│  sites  │ │     users            │
│ ─────── │ │ ──────────────────── │
│ id (PK) │ │ id (PK)              │
│ tenant  │ │ tenant_id (FK)       │
│ name    │ │ email [nullable]     │
│ address │ │ phone [NEW]          │
└─────────┘ │ first_name           │
            │ last_name            │
            │ must_change_pwd [NEW]│
            └──────────────────────┘

┌───────────────────────────┐
│  onboarding_sessions      │
│ ────────────────────────  │
│ id (PK)                   │
│ tenant_id (FK)            │
│ status                    │
│ current_step              │
│ data (JSONB)              │
└─────────┬─────────────────┘
          │
          │
          ▼
┌───────────────────────────┐
│      import_jobs          │
│ ────────────────────────  │
│ id (PK)                   │
│ tenant_id (FK)            │
│ session_id (FK)           │
│ celery_task_id            │
│ status                    │
│ stats (JSONB)             │
└───────────────────────────┘
```

---

## 4. STACK TECHNIQUE & DÉPENDANCES

### 4.1 Backend - Dépendances Additionnelles

```toml
# pyproject.toml (ADDITIONS au POC existant)

[project.dependencies]
# EXISTING (from POC)
fastapi = "^0.104.0"
uvicorn = "^0.24.0"
sqlalchemy = "^2.0.0"
alembic = "^1.12.0"
pydantic = "^2.0.0"
python-jose = "^3.3.0"
passlib = "^1.7.4"
psycopg2-binary = "^2.9.0"
redis = "^5.0.0"
celery = "^5.3.0"

# NEW DEPENDENCIES for Onboarding
openpyxl = "^3.1.2"           # Génération/lecture Excel
pandas = "^2.1.0"             # Manipulation données import
phonenumbers = "^8.13.0"      # Validation numéros téléphone
python-magic = "^0.4.27"      # Détection type fichier
celery-progress = "^0.3.0"    # Progress tracking Celery
flower = "^2.0.1"             # Monitoring Celery (existing)
```

### 4.2 Frontend - Dépendances Additionnelles

```json
// package.json (ADDITIONS au POC existant)

{
  "dependencies": {
    // EXISTING (from POC)
    "react": "^18.2.0",
    "typescript": "^5.0.0",
    "vite": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "@tanstack/react-query": "^5.0.0",
    "react-router-dom": "^6.20.0",
    "zustand": "^4.4.0",
    
    // NEW DEPENDENCIES for Onboarding Wizard
    "react-dropzone": "^14.2.3",     // Upload fichier Excel
    "xlsx": "^0.18.5",               // Preview Excel (optionnel)
    "react-step-progress-bar": "^1.0.3",  // Progress bar wizard
    "file-saver": "^2.0.5"           // Download template
  }
}
```

---

## 5. STRUCTURE PROJET ÉTENDUE

### 5.1 Structure Backend

```
backend/
├── app/
│   ├── main.py (EXTENDED: +admin routes)
│   ├── core/
│   │   ├── config.py (EXTENDED: +onboarding settings)
│   │   ├── security.py (EXTENDED: +admin role check)
│   │   └── celery_app.py (EXTENDED: +onboarding queue)
│   │
│   ├── models/
│   │   ├── tenant.py (EXTENDED: +ninea, sector, created_by)
│   │   ├── user.py (EXTENDED: +phone, must_change_password)
│   │   ├── site.py (EXTENDED: +address, type)
│   │   ├── onboarding.py (NEW: OnboardingSession model)
│   │   ├── import_job.py (NEW: ImportJob model)
│   │   └── audit_log.py (NEW: AdminAuditLog model)
│   │
│   ├── schemas/
│   │   ├── auth.py (EXTENDED: +ChangePasswordFirstLogin)
│   │   ├── tenant.py (EXTENDED: +CreateTenantAdmin)
│   │   ├── user.py (EXTENDED: +CreateUserAdmin, +phone)
│   │   └── onboarding.py (NEW: All onboarding schemas)
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py (EXTENDED: +change-password-first-login)
│   │   │   ├── dashboard.py (EXISTING)
│   │   │   ├── products.py (EXISTING)
│   │   │   ├── sales.py (EXISTING)
│   │   │   └── admin/  (NEW FOLDER)
│   │   │       ├── __init__.py
│   │   │       ├── onboarding.py (NEW: Wizard endpoints)
│   │   │       └── tenants.py (NEW: Admin tenant management)
│   │   │
│   │   └── dependencies.py (EXTENDED: +get_admin_user)
│   │
│   ├── services/
│   │   ├── auth_service.py (EXTENDED: +change_password_first_login)
│   │   ├── dashboard_service.py (EXISTING)
│   │   ├── product_service.py (EXISTING)
│   │   ├── sales_service.py (EXISTING)
│   │   ├── onboarding_service.py (NEW: Logique wizard)
│   │   ├── template_service.py (NEW: Génération Excel)
│   │   ├── import_service.py (NEW: Validation + import)
│   │   └── admin_service.py (NEW: Admin utilities)
│   │
│   ├── tasks/
│   │   ├── alerts.py (EXISTING)
│   │   ├── reports.py (EXISTING)
│   │   └── onboarding.py (NEW: Import async task)
│   │
│   └── utils/
│       ├── validators.py (EXTENDED: +validate_phone, +validate_excel)
│       ├── excel_generator.py (NEW: Template Excel generator)
│       └── audit_logger.py (NEW: Admin action logger)
│
├── alembic/
│   └── versions/
│       └── 00X_add_onboarding_tables.py (NEW migration)
│
├── tests/
│   ├── test_api/
│   │   └── test_admin_onboarding.py (NEW)
│   ├── test_services/
│   │   ├── test_onboarding_service.py (NEW)
│   │   └── test_import_service.py (NEW)
│   └── test_tasks/
│       └── test_onboarding_tasks.py (NEW)
│
└── templates/
    └── excel/
        └── template_base.xlsx (NEW: Template Excel base)
```

### 5.2 Structure Frontend

```
frontend/
├── src/
│   ├── features/
│   │   ├── auth/
│   │   │   ├── components/
│   │   │   │   ├── LoginForm.tsx (EXTENDED: +change password modal)
│   │   │   │   └── ChangePasswordModal.tsx (NEW)
│   │   │   ├── hooks/
│   │   │   │   └── useAuth.ts (EXTENDED: +changePasswordFirstLogin)
│   │   │   └── store/
│   │   │       └── authStore.ts (EXISTING)
│   │   │
│   │   ├── dashboard/ (EXISTING)
│   │   ├── stock/ (EXISTING)
│   │   ├── sales/ (EXISTING)
│   │   │
│   │   └── admin/ (NEW FOLDER)
│   │       ├── components/
│   │       │   ├── WizardLayout.tsx
│   │       │   ├── Step1TenantCreation.tsx
│   │       │   ├── Step2UserCreation.tsx
│   │       │   ├── Step3TemplateGeneration.tsx
│   │       │   ├── Step4DataImport.tsx
│   │       │   ├── ImportProgressTracker.tsx
│   │       │   └── OnboardingSummary.tsx
│   │       ├── hooks/
│   │       │   ├── useOnboardingWizard.ts
│   │       │   ├── useTemplateDownload.ts
│   │       │   └── useImportProgress.ts
│   │       └── pages/
│   │           ├── OnboardingWizardPage.tsx
│   │           └── TenantManagementPage.tsx
│   │
│   ├── api/
│   │   ├── auth.ts (EXTENDED: +changePasswordFirstLogin)
│   │   └── admin.ts (NEW: Admin API calls)
│   │
│   ├── routes/
│   │   └── index.tsx (EXTENDED: +admin routes)
│   │
│   └── types/
│       └── admin.ts (NEW: Admin types)
│
└── public/
    └── docs/
        └── template_instructions.pdf (NEW: Instructions remplissage)
```

---

## 6. ROADMAP IMPLÉMENTATION

### 6.1 Timeline Globale

```
DURÉE TOTALE ESTIMÉE : 4-5 semaines (160-200 heures dev)

┌──────────────────────────────────────────────────────────────┐
│ SEMAINE 1 : Fondations Backend                               │
│   • Migrations DB                                            │
│   • Models + Schemas                                         │
│   • Services core (onboarding, template, import)             │
│   • API endpoints admin                                      │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ SEMAINE 2 : Celery Tasks & Validation                       │
│   • Celery task import asynchrone                            │
│   • Validation Excel avancée                                 │
│   • Génération template Excel                                │
│   • Tests unitaires backend                                  │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ SEMAINE 3 : Frontend Wizard                                  │
│   • Components wizard 4 étapes                               │
│   • Hooks onboarding                                         │
│   • Upload + progress tracking                               │
│   • Change password modal                                    │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ SEMAINE 4 : Intégration & Tests                             │
│   • Intégration frontend-backend                             │
│   • Tests E2E wizard complet                                 │
│   • Audit logging                                            │
│   • Documentation                                            │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ SEMAINE 5 (BUFFER) : Polish & Déploiement                   │
│   • Corrections bugs                                         │
│   • Optimisations performance                                │
│   • Déploiement staging                                      │
│   • Tests utilisateur (CEO)                                  │
└──────────────────────────────────────────────────────────────┘
```

### 6.2 Dépendances Critiques

```
DÉPENDANCES PATH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Migrations DB → Models → Services → API
   (Séquentiel, pas de parallèle possible)

2. Génération template → Import → Validation
   (Template doit être finalisé avant import)

3. Backend API → Frontend Components
   (Frontend dépend des endpoints)

4. Change password → Wizard complet
   (Must be done en premier pour sécurité)

TRAVAIL PARALLÉLISABLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Services backend + Tests unitaires (simultané)
• Celery tasks + Génération Excel (2 devs différents)
• Frontend components wizard (indépendants entre eux)
```

---

## 7. DÉCOUPAGE EN SPRINTS

### Sprint 1 : Fondations Backend (40h - 1 semaine)

**Objectif** : Infrastructure backend onboarding fonctionnelle

**Livrables** :
- ✅ Migration DB avec nouvelles tables
- ✅ Models + Schemas Pydantic
- ✅ Services core (onboarding_service, template_service, import_service)
- ✅ API endpoints admin (create-tenant, create-users, generate-template)
- ✅ Extension auth (change-password-first-login)
- ✅ Tests unitaires services (>80% coverage)

**Acceptance Criteria** :
- ✅ Migration appliquée sans erreur sur DB test
- ✅ POST /api/v1/admin/onboarding/create-tenant retourne tenant_id
- ✅ POST /api/v1/admin/onboarding/create-users crée N users avec phone/email
- ✅ GET /api/v1/admin/onboarding/generate-template/{tenant_id} retourne fichier Excel
- ✅ POST /api/v1/auth/change-password-first-login fonctionne + flag updated
- ✅ Tests unitaires passent (pytest)

---

### Sprint 2 : Import Asynchrone & Validation (40h - 1 semaine)

**Objectif** : Import Excel robuste avec validation + tracking

**Livrables** :
- ✅ Celery task import_tenant_data (async)
- ✅ Validation schéma Excel (structure, types, business rules)
- ✅ Parsing Excel avec Pandas + OpenPyXL
- ✅ Transaction atomique import (products + sales)
- ✅ Progress tracking temps réel
- ✅ Post-processing (activation tenant, refresh vues)
- ✅ Tests intégration import

**Acceptance Criteria** :
- ✅ POST /api/v1/admin/onboarding/upload-template déclenche Celery task
- ✅ GET /api/v1/admin/onboarding/import-status/{task_id} retourne progress
- ✅ Import 150 produits + 2000 ventes < 2 min
- ✅ Validation rejette fichiers malformés avec messages clairs
- ✅ Transaction rollback en cas d'erreur (pas de données partielles)
- ✅ Tenant activé automatiquement après import réussi
- ✅ Tests Celery passent (100% success rate sur 10 runs)

---

### Sprint 3 : Frontend Wizard (40h - 1 semaine)

**Objectif** : Interface wizard admin complète

**Livrables** :
- ✅ Layout wizard avec stepper 4 étapes
- ✅ Step1TenantCreation component
- ✅ Step2UserCreation component (multi-users, email/phone)
- ✅ Step3TemplateGeneration component (download button)
- ✅ Step4DataImport component (upload + progress)
- ✅ ImportProgressTracker component (polling status)
- ✅ OnboardingSummary component (récap final)
- ✅ ChangePasswordModal component
- ✅ Hooks : useOnboardingWizard, useImportProgress
- ✅ Route /admin/onboarding protégée (admin only)

**Acceptance Criteria** :
- ✅ Wizard accessible à /admin/onboarding (après login admin)
- ✅ Navigation 4 étapes fluide (next/previous)
- ✅ Validation frontend (champs requis, formats)
- ✅ Upload fichier Excel fonctionne (drag & drop ou click)
- ✅ Progress bar update en temps réel (polling toutes les 2s)
- ✅ Récap final affiche : tenant créé, users, stats import
- ✅ Change password modal s'affiche si must_change_password=true
- ✅ Responsive mobile (testable sur iPhone)

---

### Sprint 4 : Intégration & Tests E2E (40h - 1 semaine)

**Objectif** : Wizard E2E fonctionnel + tests automatisés

**Livrables** :
- ✅ Intégration frontend-backend complète
- ✅ Tests E2E Playwright (wizard complet)
- ✅ Audit logging (admin_audit_logs)
- ✅ Error handling robuste (UI + backend)
- ✅ Documentation technique (README onboarding)
- ✅ Vidéo démo wizard (5 min)

**Acceptance Criteria** :
- ✅ Wizard E2E : Créer tenant → Users → Download template → Upload → Tenant actif
- ✅ Durée wizard E2E < 3 min (hors remplissage template)
- ✅ Tests E2E passent 10/10 fois (CI/CD)
- ✅ Toutes actions admin loggées dans admin_audit_logs
- ✅ Erreurs affichées user-friendly (toast notifications)
- ✅ Documentation à jour (architecture, API, deployment)
- ✅ Vidéo démo validée par CEO

---

### Sprint 5 : Polish & Production (40h - 1 semaine - BUFFER)

**Objectif** : Production-ready + optimisations

**Livrables** :
- ✅ Corrections bugs sprint 1-4
- ✅ Optimisations performance (import, UI)
- ✅ Sécurité renforcée (rate limiting admin routes)
- ✅ Monitoring Celery (Flower dashboard)
- ✅ Déploiement staging
- ✅ Tests utilisateur final (CEO onboarde 1 client réel)

**Acceptance Criteria** :
- ✅ Zéro bug critique
- ✅ Import 5000 ventes < 3 min (test charge)
- ✅ Rate limiting admin : 20 req/min (évite abus)
- ✅ Flower dashboard configuré (monitor Celery tasks)
- ✅ Staging déployé + accessible
- ✅ CEO teste wizard : feedback positif (NPS >8)

---

## 8. PROMPTS CLAUDE CODE PAR SPRINT

### 8.1 PROMPT SPRINT 1 : Fondations Backend

```
CONTEXTE:
Je travaille sur DigiboostPME, une plateforme SaaS multi-tenant de supply chain intelligence pour PME africaines. Le POC backend FastAPI est fonctionnel avec :
- Authentification JWT
- Architecture multi-tenant (PostgreSQL)
- Services : dashboard, products, sales, predictions, alerts
- Celery pour tâches async (alerting, rapports)

OBJECTIF:
Intégrer un module d'onboarding admin qui permet au CEO de créer rapidement des tenants avec un wizard en 4 étapes :
1. Création tenant + site
2. Création users (identifiant email ou téléphone)
3. Génération template Excel
4. Import données (async Celery)

TÂCHES SPRINT 1:
1. Créer migration Alembic pour nouvelles tables :
   - Extension table tenants (ninea, sector, country, created_by)
   - Extension table users (phone nullable, must_change_password, split first_name/last_name)
   - Extension table sites (address, type)
   - Nouvelle table onboarding_sessions
   - Nouvelle table admin_audit_logs
   - Nouvelle table import_jobs

2. Créer Models SQLAlchemy (app/models/) :
   - Étendre Tenant, User, Site
   - Créer OnboardingSession, AdminAuditLog, ImportJob

3. Créer Schemas Pydantic (app/schemas/onboarding.py) :
   - CreateTenantAdmin
   - CreateUserAdmin (avec phone, must_change_password)
   - TenantCreationResponse
   - OnboardingSessionSchema

4. Créer Services (app/services/) :
   - onboarding_service.py : Logique création tenant, site, users
   - admin_service.py : Utilities admin (vérifications, audit)
   - template_service.py : Génération template Excel (stub pour l'instant)

5. Créer Routes Admin (app/api/routes/admin/onboarding.py) :
   - POST /api/v1/admin/onboarding/create-tenant
   - POST /api/v1/admin/onboarding/create-users
   - GET /api/v1/admin/onboarding/generate-template/{tenant_id} (stub)

6. Étendre Route Auth (app/api/routes/auth.py) :
   - POST /api/v1/auth/change-password-first-login

7. Créer Dependency admin (app/api/dependencies.py) :
   - get_admin_user : Vérifier role="admin"

8. Tests unitaires (tests/test_services/) :
   - test_onboarding_service.py
   - test_admin_service.py

CONTRAINTES:
- ZERO BREAKING CHANGE : Ancien code POC doit continuer fonctionner
- Validation stricte : phone avec phonenumbers library
- Idempotence : Pouvoir relancer création sans erreur si tenant existe
- Audit : Toute action admin loggée dans admin_audit_logs
- Sécurité : Endpoints /admin/* protégés par JWT + role check

SPÉCIFICATIONS TECHNIQUES:
- FastAPI 0.104+, SQLAlchemy 2.0, Alembic
- PostgreSQL 15+
- Pydantic v2 pour validation
- python-jose pour JWT
- phonenumbers pour validation téléphone
- passlib[bcrypt] pour hashing passwords

STRUCTURE FICHIERS ATTENDUE:
backend/
├── alembic/versions/00X_add_onboarding_tables.py
├── app/
│   ├── models/
│   │   ├── onboarding.py (NEW)
│   │   ├── audit_log.py (NEW)
│   │   ├── import_job.py (NEW)
│   │   ├── tenant.py (EXTENDED)
│   │   ├── user.py (EXTENDED)
│   │   └── site.py (EXTENDED)
│   ├── schemas/
│   │   ├── onboarding.py (NEW)
│   │   ├── user.py (EXTENDED)
│   │   └── auth.py (EXTENDED)
│   ├── services/
│   │   ├── onboarding_service.py (NEW)
│   │   ├── template_service.py (NEW stub)
│   │   ├── admin_service.py (NEW)
│   │   └── auth_service.py (EXTENDED)
│   ├── api/
│   │   ├── routes/
│   │   │   ├── admin/
│   │   │   │   ├── __init__.py (NEW)
│   │   │   │   └── onboarding.py (NEW)
│   │   │   └── auth.py (EXTENDED)
│   │   └── dependencies.py (EXTENDED)
│   └── utils/
│       ├── validators.py (NEW)
│       └── audit_logger.py (NEW)
└── tests/
    └── test_services/
        ├── test_onboarding_service.py (NEW)
        └── test_admin_service.py (NEW)

CRITÈRES D'ACCEPTATION:
✅ Migration appliquée sans erreur
✅ POST /api/v1/admin/onboarding/create-tenant crée tenant + site, retourne IDs
✅ POST /api/v1/admin/onboarding/create-users crée N users avec phone ou email
✅ POST /api/v1/auth/change-password-first-login change MDP + flag must_change_password
✅ Endpoints /admin/* rejettent non-admin (401/403)
✅ Validation phone avec phonenumbers (rejet si invalide)
✅ Actions admin loggées dans admin_audit_logs
✅ Tests unitaires passent (pytest, >80% coverage)

COMMANDES DE TEST:
```bash
# Appliquer migration
alembic upgrade head

# Lancer tests
pytest tests/test_services/test_onboarding_service.py -v
pytest tests/test_services/test_admin_service.py -v

# Tester API manuellement (avec Postman ou curl)
curl -X POST http://localhost:8000/api/v1/admin/onboarding/create-tenant \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{"company_name":"Test PME","ninea":"123","sector":"retail","country":"SN","site_name":"Site Principal","site_address":"Dakar"}'
```
```

---

### 8.2 PROMPT SPRINT 2 : Import Asynchrone & Validation

```
CONTEXTE:
Sprint 1 terminé. Backend admin onboarding fonctionnel :
- ✅ Tables DB créées (onboarding_sessions, import_jobs, etc.)
- ✅ Routes admin create-tenant, create-users opérationnelles
- ✅ Change password first login implémenté

OBJECTIF SPRINT 2:
Implémenter l'import asynchrone Excel avec validation robuste :
1. Génération template Excel personnalisé (étape 3 wizard)
2. Upload + validation structure Excel
3. Celery task import asynchrone (products + sales)
4. Progress tracking temps réel
5. Post-processing : activation tenant, refresh vues

TÂCHES:

1. **Génération Template Excel** (app/utils/excel_generator.py)
   - Créer classe ExcelTemplateGenerator
   - Méthode generate_template(tenant_id) → BytesIO
   - Onglets : "Produits", "Ventes"
   - Headers avec instructions
   - Validation Excel intégrée (formules, listes déroulantes)
   - Logo Digiboost + styling

2. **Service Template** (app/services/template_service.py)
   - generate_template_for_tenant(tenant_id: UUID) → BytesIO
   - Personnalisation template (nom entreprise, dates, etc.)

3. **Route Génération** (app/api/routes/admin/onboarding.py)
   - GET /api/v1/admin/onboarding/generate-template/{tenant_id}
   - Return FileResponse (download Excel)

4. **Validation Excel** (app/utils/validators.py)
   - validate_excel_structure(file: UploadFile) → ValidationResult
   - Vérifier :
     • Onglets requis présents
     • Headers correctes
     • Types colonnes (texte, nombre, date)
     • Business rules (stock >= 0, prix > 0, dates cohérentes)
   - Return liste erreurs détaillées

5. **Service Import** (app/services/import_service.py)
   - parse_excel_file(file: UploadFile, tenant_id: UUID) → ParsedData
   - validate_products(products: List[dict]) → ValidationResult
   - validate_sales(sales: List[dict], products: List[UUID]) → ValidationResult
   - import_products(tenant_id, products, session: Session)
   - import_sales(tenant_id, sales, session: Session)

6. **Celery Task** (app/tasks/onboarding.py)
   - @celery_app.task(bind=True) import_tenant_data(self, import_job_id, file_path, tenant_id)
   - Steps :
     1. Update import_job status = "running"
     2. Parse Excel
     3. Validate data
     4. Transaction atomique : import products + sales
     5. Post-processing :
        - Refresh vues matérialisées
        - Activation tenant (is_active=true)
        - Activation dashboards (settings)
        - Calcul score qualité
     6. Update import_job status = "success" + stats
   - Progress tracking : self.update_state(state='PROGRESS', meta={...})
   - Error handling : rollback + update status = "failed"

7. **Routes Import** (app/api/routes/admin/onboarding.py)
   - POST /api/v1/admin/onboarding/upload-template/{tenant_id}
     • Upload fichier (multipart/form-data)
     • Validation synchrone structure
     • Créer ImportJob
     • Déclencher Celery task
     • Return task_id
   
   - GET /api/v1/admin/onboarding/import-status/{task_id}
     • Query Celery task state
     • Query ImportJob stats
     • Return status + progress + stats

8. **Configuration Celery** (app/core/celery_app.py)
   - Ajouter queue "onboarding" dédiée
   - Configurer retry policy
   - Configurer timeout (10 min max)

9. **Tests** :
   - tests/test_utils/test_excel_generator.py
   - tests/test_utils/test_validators.py
   - tests/test_services/test_import_service.py
   - tests/test_tasks/test_onboarding_tasks.py
   - tests/fixtures/sample_data.xlsx (fichier test)

DÉPENDANCES:
```toml
openpyxl = "^3.1.2"
pandas = "^2.1.0"
phonenumbers = "^8.13.0"
python-magic = "^0.4.27"
celery-progress = "^0.3.0"
```

SPÉCIFICATIONS TEMPLATE EXCEL:
Onglet "Produits":
| Code | Nom | Catégorie | Prix Vente | Prix Achat | Stock Initial | Seuil Alerte |
|------|-----|-----------|------------|------------|---------------|--------------|
| P001 |     |           |            |            |               |              |

Onglet "Ventes":
| Date (YYYY-MM-DD) | Code Produit | Quantité | Prix Unitaire |
|-------------------|--------------|----------|---------------|
| 2025-01-15        | P001         | 10       | 5000          |

Instructions :
- En-tête avec instructions remplissage
- Validation Excel (listes déroulantes catégories, formules somme)
- Plage dates : 6 derniers mois minimum

SPÉCIFICATIONS VALIDATION:
Règles métier :
- Code produit unique par tenant
- Prix vente > 0, prix achat >= 0
- Stock initial >= 0
- Date vente dans les 24 derniers mois
- Quantité vente > 0
- Code produit vente existe dans onglet Produits
- Total ventes cohérent (quantité * prix)

Contraintes performance :
- Import 150 produits + 2000 ventes < 2 min
- Transaction atomique (tout ou rien)
- Progress update toutes les 100 lignes

CRITÈRES D'ACCEPTATION:
✅ GET /generate-template retourne fichier Excel téléchargeable
✅ Template contient onglets + headers + instructions
✅ Upload fichier valide déclenche Celery task
✅ Upload fichier invalide retourne erreurs claires (pas de task)
✅ Celery task import réussit : products + sales en DB
✅ Celery task import échoue : rollback (pas de données partielles)
✅ GET /import-status retourne progress temps réel
✅ Tenant activé automatiquement après import réussi
✅ Import 2000+ lignes < 2 min (test charge)
✅ Tests Celery passent 10/10 runs

COMMANDES TEST:
```bash
# Tester génération template
curl -X GET http://localhost:8000/api/v1/admin/onboarding/generate-template/{tenant_id} \
  -H "Authorization: Bearer {admin_token}" \
  --output template.xlsx

# Tester upload
curl -X POST http://localhost:8000/api/v1/admin/onboarding/upload-template/{tenant_id} \
  -H "Authorization: Bearer {admin_token}" \
  -F "file=@template_rempli.xlsx"

# Tester status import
curl -X GET http://localhost:8000/api/v1/admin/onboarding/import-status/{task_id} \
  -H "Authorization: Bearer {admin_token}"

# Lancer Celery worker (queue onboarding)
celery -A app.core.celery_app worker --loglevel=info -Q onboarding

# Tests
pytest tests/test_tasks/test_onboarding_tasks.py -v --cov
```
```

---

### 8.3 PROMPT SPRINT 3 : Frontend Wizard

```
CONTEXTE:
Backend onboarding complet :
- ✅ API admin : create-tenant, create-users, generate-template, upload-template
- ✅ Celery task import async fonctionnel
- ✅ Progress tracking opérationnel

Frontend POC existant :
- React 18.2 + TypeScript + Vite
- TailwindCSS + Shadcn/UI components
- React Router 6, TanStack Query, Zustand
- Authentification JWT fonctionnelle
- Dashboards opérationnels (Overview, Stock, Sales, Predictions)

OBJECTIF SPRINT 3:
Créer interface wizard admin 4 étapes pour onboarding tenants.

TÂCHES:

1. **Routes Admin** (src/routes/index.tsx)
   - Ajouter routes /admin/onboarding (protected admin only)
   - Créer AdminRoute component (check role admin)

2. **API Client Admin** (src/api/admin.ts)
   - createTenant(data: CreateTenantRequest)
   - createUsers(tenantId: UUID, users: CreateUserRequest[])
   - downloadTemplate(tenantId: UUID)
   - uploadTemplate(tenantId: UUID, file: File)
   - getImportStatus(taskId: string)

3. **Types** (src/types/admin.ts)
   - CreateTenantRequest, TenantResponse
   - CreateUserRequest, UserResponse
   - ImportStatus, OnboardingSession
   - OnboardingStep enum

4. **Hooks** (src/features/admin/hooks/)
   - useOnboardingWizard.ts :
     • State management wizard (current step, data, loading)
     • goToStep(step), nextStep(), previousStep()
     • submitTenant(), submitUsers(), submitImport()
   
   - useTemplateDownload.ts :
     • downloadTemplate(tenantId) → trigger download
   
   - useImportProgress.ts :
     • Polling GET /import-status toutes les 2s
     • Return { progress, status, stats, isComplete, error }

5. **Layout Wizard** (src/features/admin/components/WizardLayout.tsx)
   - Stepper 4 étapes (visual progress)
   - Header "Onboarding Nouveau Client"
   - Navigation : Previous / Next / Submit buttons
   - Responsive mobile

6. **Step 1** (src/features/admin/components/Step1TenantCreation.tsx)
   - Formulaire :
     • Nom entreprise (required)
     • NINEA (optional)
     • Secteur (select : retail, wholesale, manufacturing, services)
     • Pays (select, default SN)
     • Nom site principal (required)
     • Adresse site (required)
   - Validation react-hook-form + zod
   - Submit → API createTenant → Store tenant_id → Next step

7. **Step 2** (src/features/admin/components/Step2UserCreation.tsx)
   - Liste dynamique users (min 1, max 10)
   - Par user :
     • Prénom (required)
     • Nom (required)
     • Type identifiant : Email ou Téléphone (radio)
     • Email ou Téléphone (selon choix)
     • Rôle (select : admin, manager, collaborateur)
   - Boutons : Ajouter user, Supprimer user
   - Validation :
     • Email format valide
     • Téléphone format international (+221...)
     • Au moins 1 admin
   - Submit → API createUsers → Store user_ids → Next step

8. **Step 3** (src/features/admin/components/Step3TemplateGeneration.tsx)
   - Titre : "Télécharger le Template Excel"
   - Instructions :
     • "Remplissez ce template avec les données du client"
     • "Produits : Code, Nom, Catégorie, Prix, Stock"
     • "Ventes : 6 mois d'historique minimum"
   - Bouton "Télécharger Template" → API downloadTemplate
   - Lien PDF instructions (optionnel)
   - Bouton "Suivant" (manuel, après remplissage)

9. **Step 4** (src/features/admin/components/Step4DataImport.tsx)
   - Upload zone (react-dropzone) :
     • Drag & drop ou click
     • Accept .xlsx only
     • Max size 10 MB
   - Après upload :
     • Validation synchrone (frontend check file type)
     • API uploadTemplate → task_id
     • Afficher <ImportProgressTracker />

10. **Progress Tracker** (src/features/admin/components/ImportProgressTracker.tsx)
    - useImportProgress(taskId) hook
    - Display :
      • Progress bar (0-100%)
      • Status message ("Importation produits...", "Importation ventes...")
      • Stats : X produits importés, Y ventes importées
      • Durée estimée restante
    - Success → <OnboardingSummary />
    - Error → Afficher erreur + bouton "Réessayer"

11. **Summary** (src/features/admin/components/OnboardingSummary.tsx)
    - Récapitulatif :
      • ✅ Tenant créé : {nom}
      • ✅ Site : {nom site}
      • ✅ Users créés : {nb users}
      • ✅ Données importées : {nb produits} produits, {nb ventes} ventes
      • 📊 Score qualité : {score}%
      • 🔗 Lien accès client : https://app.digiboost.sn/login
    - Boutons :
      • "Terminer" → Redirect /admin/tenants
      • "Nouvel onboarding" → Reset wizard

12. **Change Password Modal** (src/features/auth/components/ChangePasswordModal.tsx)
    - Modal forced (cannot close) si must_change_password=true
    - Form :
      • Ancien mot de passe
      • Nouveau mot de passe (min 8 char, 1 maj, 1 min, 1 chiffre)
      • Confirmation nouveau mot de passe
    - Submit → API changePasswordFirstLogin → Redirect /dashboard

13. **Page Wizard** (src/features/admin/pages/OnboardingWizardPage.tsx)
    - Container wizard
    - useOnboardingWizard hook
    - Render step selon currentStep
    - Protected AdminRoute

14. **Styling**
    - TailwindCSS + Shadcn components
    - Responsive mobile-first
    - Animations smooth (transitions steps)
    - Toast notifications (success, error)

DÉPENDANCES FRONTEND:
```json
{
  "react-dropzone": "^14.2.3",
  "react-step-progress-bar": "^1.0.3",
  "file-saver": "^2.0.5"
}
```

STRUCTURE FICHIERS:
frontend/src/
├── features/
│   ├── auth/
│   │   ├── components/
│   │   │   ├── LoginForm.tsx (EXTENDED)
│   │   │   └── ChangePasswordModal.tsx (NEW)
│   │   └── hooks/
│   │       └── useAuth.ts (EXTENDED: +changePasswordFirstLogin)
│   │
│   └── admin/ (NEW FOLDER)
│       ├── components/
│       │   ├── WizardLayout.tsx
│       │   ├── Step1TenantCreation.tsx
│       │   ├── Step2UserCreation.tsx
│       │   ├── Step3TemplateGeneration.tsx
│       │   ├── Step4DataImport.tsx
│       │   ├── ImportProgressTracker.tsx
│       │   └── OnboardingSummary.tsx
│       ├── hooks/
│       │   ├── useOnboardingWizard.ts
│       │   ├── useTemplateDownload.ts
│       │   └── useImportProgress.ts
│       └── pages/
│           └── OnboardingWizardPage.tsx
│
├── api/
│   ├── auth.ts (EXTENDED)
│   └── admin.ts (NEW)
│
├── routes/
│   └── index.tsx (EXTENDED: +admin routes)
│
└── types/
    └── admin.ts (NEW)

CRITÈRES D'ACCEPTATION:
✅ Route /admin/onboarding accessible (admin only)
✅ Step 1 : Créer tenant → Next fonctionne
✅ Step 2 : Créer 3 users (1 admin, 2 managers) → Next
✅ Step 3 : Download template → Fichier Excel téléchargé
✅ Step 4 : Upload Excel → Progress tracker s'affiche
✅ Progress polling update toutes les 2s
✅ Summary affiche stats correctes après import
✅ Change password modal s'affiche si must_change_password=true
✅ Modal change password submit → Redirect dashboard
✅ Responsive mobile (testable iPhone)
✅ Toast notifications pour succès/erreurs

COMMANDES TEST:
```bash
# Dev server
npm run dev

# Build
npm run build

# Tests (optionnel sprint 3)
npm run test
```
```

---

### 8.4 PROMPT SPRINT 4 : Intégration & Tests E2E

```
CONTEXTE:
Backend + Frontend onboarding implémentés :
- ✅ Backend : API admin, Celery import, validation
- ✅ Frontend : Wizard 4 étapes, progress tracking, change password

OBJECTIF SPRINT 4:
Finaliser l'intégration complète + tests E2E + audit + docs.

TÂCHES:

1. **Intégration Frontend-Backend**
   - Vérifier tous endpoints API appelés correctement
   - Gestion erreurs HTTP (400, 401, 403, 500)
   - Toast notifications user-friendly
   - Loading states cohérents
   - Timeout handling (import > 10 min)

2. **Error Handling Robuste**
   Backend (app/api/error_handlers.py) :
   - HTTPException handlers personnalisés
   - ValidationError → 400 avec détails
   - CeleryTaskTimeout → 504
   - FileUploadError → 413/415
   
   Frontend (src/utils/errorHandling.ts) :
   - parseApiError(error) → user message
   - Toast notifications (success, error, warning)
   - Retry logic import (si timeout)

3. **Audit Logging**
   - Compléter admin_audit_logs pour toutes actions :
     • create_tenant
     • create_users
     • download_template
     • upload_template
     • import_data
   - Logger IP address, user agent, détails action
   - Créer endpoint GET /api/v1/admin/audit-logs (pagination)

4. **Tests E2E Playwright** (tests/e2e/)
   - test_wizard_complete_flow.spec.ts :
     • Login admin
     • Navigate /admin/onboarding
     • Step 1 : Fill tenant form → Next
     • Step 2 : Add 3 users → Next
     • Step 3 : Download template (check file)
     • Step 4 : Upload template (mock file) → Wait import
     • Verify summary stats
     • Click "Terminer"
   
   - test_change_password_first_login.spec.ts :
     • Login with default password
     • Modal appears
     • Change password
     • Redirect to dashboard
   
   - test_admin_protection.spec.ts :
     • Login as non-admin user
     • Try access /admin/onboarding
     • Verify 403 or redirect

5. **Tests Intégration Backend** (tests/integration/)
   - test_onboarding_full_flow.py :
     • Create tenant via API
     • Create users via API
     • Generate template via API (check bytes)
     • Upload template via API (mock file)
     • Poll import status until complete
     • Verify tenant activated
     • Verify products + sales in DB
     • Verify dashboards enabled

6. **Performance Testing**
   - Script JMeter/Locust (tests/load/) :
     • Simulate 10 imports simultanés
     • Mesurer temps import (P50, P95, P99)
     • Vérifier zéro timeout < 5000 lignes
   
   - Optimisations si nécessaire :
     • Bulk insert SQL (au lieu de N inserts)
     • Index DB supplémentaires
     • Celery worker scaling

7. **Documentation Technique** (docs/onboarding/)
   - README_ONBOARDING.md :
     • Architecture overview
     • API endpoints description
     • Workflow diagram
     • Schéma DB
     • Deployment instructions
   
   - API_ADMIN_ENDPOINTS.md :
     • Spécifications OpenAPI complètes
     • Exemples curl
     • Schémas request/response
   
   - TROUBLESHOOTING.md :
     • Common errors + solutions
     • Celery task stuck → how to fix
     • Import failed → how to debug

8. **Vidéo Démo**
   - Screen recording (5 min) :
     • Login admin
     • Wizard complet (accéléré 2x)
     • Summary
     • Login client avec nouveau MDP
     • Dashboard client visible
   - Sous-titres français
   - Export MP4 (upload Google Drive)

9. **Security Review**
   - Rate limiting admin routes : 20 req/min par IP
   - CSRF protection (si applicable)
   - Validation upload fichier :
     • Max size 10 MB
     • Extension .xlsx only (MIME type check)
     • Virus scan (ClamAV optionnel)
   - Secrets management (env vars)

10. **Monitoring**
    - Flower dashboard pour Celery
    - Prometheus metrics :
      • onboarding_sessions_total
      • import_jobs_duration_seconds
      • import_jobs_failed_total
    - Grafana dashboard "Admin Onboarding"

CRITÈRES D'ACCEPTATION:
✅ Tests E2E passent 10/10 runs (CI/CD)
✅ Import 2000 lignes < 2 min (95th percentile)
✅ Zéro memory leak (profiler Python)
✅ Zéro erreur non-catchée (Sentry zéro alert)
✅ Audit logs complets (check DB)
✅ Documentation à jour + reviewed
✅ Vidéo démo validée par CEO
✅ Rate limiting fonctionne (test curl)
✅ Monitoring Flower + Grafana opérationnel

COMMANDES TEST:
```bash
# Tests E2E
npx playwright test tests/e2e/test_wizard_complete_flow.spec.ts

# Tests intégration backend
pytest tests/integration/test_onboarding_full_flow.py -v

# Load testing
locust -f tests/load/test_onboarding_load.py --host=http://localhost:8000

# Profiling
python -m cProfile -o profile.out app/tasks/onboarding.py
snakeviz profile.out

# Monitoring
# Flower : http://localhost:5555
# Grafana : http://localhost:3000
```
```

---

### 8.5 PROMPT SPRINT 5 : Polish & Production

```
CONTEXTE:
Sprints 1-4 terminés :
- ✅ Backend complet + tests unitaires/intégration
- ✅ Frontend wizard + tests E2E
- ✅ Audit logging + monitoring
- ✅ Documentation + vidéo démo

OBJECTIF SPRINT 5:
Préparer production + optimisations finales + tests utilisateur.

TÂCHES:

1. **Corrections Bugs Sprint 1-4**
   - Review issues backlog
   - Fixer bugs critiques/bloquants
   - Fixer bugs mineurs si temps

2. **Optimisations Performance**
   Backend :
   - Profiling SQL queries (EXPLAIN ANALYZE)
   - Ajouter indexes manquants
   - Optimiser Celery task (bulk inserts)
   - Cache Redis pour generate-template (si appelé N fois)
   
   Frontend :
   - Code splitting wizard (lazy loading)
   - Optimiser bundle size (analyze webpack)
   - Lazy load Shadcn components
   - Image optimization (si logo/icons)

3. **Sécurité Renforcée**
   - Rate limiting strict :
     • POST /create-tenant : 5 req/hour par IP
     • POST /upload-template : 10 req/hour par IP
   - CORS configuré production (domaine fixe)
   - Secrets rotation policy
   - Security headers (helmet.js)
   - Content Security Policy

4. **Monitoring Production**
   - Configure Flower production (auth protégée)
   - Grafana dashboard finalisé :
     • Onboarding sessions by status
     • Import duration histogram
     • Error rate
     • Active Celery workers
   - Alerts :
     • Email si import failed
     • Slack si Celery worker down

5. **Deployment Staging**
   - Docker Compose production-ready :
     • Gunicorn workers (4)
     • Celery workers (2) queue onboarding
     • Redis
     • PostgreSQL
     • Nginx reverse proxy
   - CI/CD pipeline (GitHub Actions) :
     • Run tests
     • Build Docker images
     • Deploy staging auto
   - Environment variables :
     • DATABASE_URL
     • REDIS_URL
     • SECRET_KEY
     • CELERY_BROKER_URL
     • ADMIN_EMAIL (pour premier admin)

6. **Documentation Production** (docs/deployment/)
   - DEPLOYMENT.md :
     • Requirements serveur
     • Docker Compose setup
     • Environment variables
     • Backups strategy
     • Rollback procedure
   
   - RUNBOOK.md :
     • How to create first admin user
     • How to monitor Celery
     • How to debug failed import
     • How to scale workers

7. **Tests Utilisateur Final**
   - CEO onboarde 1 client réel en staging
   - Mesurer durée réelle wizard (feedback)
   - Collecter feedback UX :
     • Wizard clair ?
     • Instructions suffisantes ?
     • Erreurs compréhensibles ?
   - Itérer sur feedback (si critique)

8. **Checklist Production**
   - [ ] Secrets dans .env (pas hardcodés)
   - [ ] HTTPS obligatoire (certificat SSL)
   - [ ] Firewall VPS configuré
   - [ ] Backups DB automatiques (quotidiens)
   - [ ] Monitoring alertes configurées
   - [ ] Documentation à jour
   - [ ] Vidéo démo publiée
   - [ ] Rollback plan documenté
   - [ ] Logs centralisés (Loki/ELK)
   - [ ] Rate limiting activé
   - [ ] Celery workers supervisord/systemd

9. **Plan Rollout**
   - Phase 1 (Semaine 1) : Staging accessible CEO uniquement
   - Phase 2 (Semaine 2) : CEO onboarde 3 clients beta
   - Phase 3 (Semaine 3) : Review feedback + ajustements
   - Phase 4 (Semaine 4) : Production rollout complet

10. **Handoff Documentation**
    - Guide admin CEO :
      • Comment accéder wizard
      • Étapes wizard détaillées
      • Remplissage template Excel
      • Troubleshooting commun
    - Guide technique :
      • Architecture overview
      • Code structure
      • Maintenance tasks
      • How to add new dashboard

CRITÈRES D'ACCEPTATION:
✅ Zéro bug critique en staging
✅ Import 5000 lignes < 3 min (P95)
✅ Rate limiting testé (bloque après X req)
✅ Monitoring Grafana opérationnel
✅ Staging déployé + accessible CEO
✅ CEO teste wizard : NPS >8/10
✅ Documentation production complète
✅ Backups DB configurés (test restore)
✅ Rollback plan testé (staging → rollback → staging)
✅ Handoff documentation reviewed

COMMANDES DÉPLOIEMENT:
```bash
# Build Docker images
docker-compose -f docker-compose.prod.yml build

# Deploy staging
docker-compose -f docker-compose.prod.yml up -d

# Check services
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f celery_worker

# Backup DB
docker exec digiboost_db pg_dump -U postgres digiboost > backup_$(date +%Y%m%d).sql

# Restore DB
docker exec -i digiboost_db psql -U postgres digiboost < backup_20251023.sql

# Scale Celery workers
docker-compose up -d --scale celery_worker=4

# Monitoring URLs
# Flower: https://staging.digiboost.sn/flower
# Grafana: https://staging.digiboost.sn/grafana
```

TESTS FINAUX:
```bash
# Load test production
locust -f tests/load/test_onboarding_load.py --host=https://staging.digiboost.sn --users=20 --spawn-rate=2

# Security scan
docker run --rm -v $(pwd):/zap/wrk/:rw owasp/zap2docker-stable zap-baseline.py -t https://staging.digiboost.sn

# Performance audit
lighthouse https://staging.digiboost.sn --view
```
```

---

## 9. CONCLUSION

### 9.1 Récapitulatif

Cette architecture technique définit l'intégration complète du module d'onboarding wizard au projet DigiboostPME POC existant :

**FORCES** :
✅ Extension non-breaking du POC (zéro impact fonctionnalités existantes)
✅ Architecture modulaire et scalable
✅ Import asynchrone robuste (Celery + progress tracking)
✅ Validation multi-couches (frontend + backend + business rules)
✅ Sécurité renforcée (admin routes protégées, audit logs)
✅ Observabilité complète (monitoring, logs, métriques)
✅ Tests automatisés (unitaires, intégration, E2E)

**INNOVATION** :
- Identifiants flexibles (email OU téléphone) adapté contexte Afrique
- Template Excel généré dynamiquement avec validation intégrée
- Activation automatique tenant + dashboards post-import
- Wizard fluide 4 étapes (25-40 min total)

**IMPACT BUSINESS** :
- CEO peut onboarder 1 client en < 1h (vs 1 journée manuel)
- Zéro erreur données (validation stricte)
- Traçabilité complète (audit logs)
- Scalable : 10 clients/mois → 100 clients/mois sans friction

### 9.2 Prochaines Étapes

**COURT TERME** (Post-Sprint 5) :
1. Déploiement production après validation staging
2. Onboarding 5-10 clients pilotes
3. Collecte feedback + itérations UX

**MOYEN TERME** (3-6 mois) :
1. Self-service onboarding (Phase 1 spec complète)
2. Intégration ExposeAPI (import depuis ERPs)
3. Module qualité données avancé

**LONG TERME** (6-12 mois) :
1. Wizard multi-sites (Phase 2)
2. Dashboards personnalisables (activation à la carte)
3. Mobile app native (vs PWA)

---

**FIN DU DOCUMENT**

*Pour questions techniques : CTO Digiboost*  
*Version : 1.0 - 23 Octobre 2025*
