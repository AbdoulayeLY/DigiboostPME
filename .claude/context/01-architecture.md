# ARCHITECTURE TECHNIQUE - PLATEFORME DIGIBOOST PME
## Intelligence Supply Chain pour PME Sénégalaises

**Version** : 1.0 MVP  
**Date** : Octobre 2025  
**Rôle** : Architecte Technique  
**Public** : Équipe Développement, CTO, CEO

---

## 📋 TABLE DES MATIÈRES

1. [Vue d'Ensemble Architecture](#1-vue-densemble-architecture)
2. [Stack Technique](#2-stack-technique)
3. [Architecture Backend (FastAPI)](#3-architecture-backend-fastapi)
4. [Architecture Frontend (React)](#4-architecture-frontend-react)
5. [Architecture Base de Données](#5-architecture-base-de-données)
6. [Sécurité & Authentification (JWT)](#6-sécurité--authentification-jwt)
7. [Gestion Offline/Online (Contexte Sénégal)](#7-gestion-offlineonline-contexte-sénégal)
8. [Intégrations Externes](#8-intégrations-externes)
9. [Infrastructure & Déploiement](#9-infrastructure--déploiement)
10. [Roadmap Implémentation Value-Driven](#10-roadmap-implémentation-value-driven)

---

## 1. VUE D'ENSEMBLE ARCHITECTURE

### 1.1 Principes Architecturaux

```
PRINCIPES DIRECTEURS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ MVP-First          : Prioriser fonctionnalités à forte valeur
✅ Offline-Capable    : Fonctionnement partiel sans connexion
✅ Mobile-First       : Design responsive, optimisé smartphones
✅ Multi-Tenant       : Isolation données entre PME clientes
✅ Scalable           : Prêt pour croissance (1→1000 PME)
✅ API-First          : Backend exposé via API REST
✅ Monitoring-Ready   : Observabilité dès le départ
```

### 1.2 Architecture Haut Niveau

```
┌─────────────────────────────────────────────────────────────────┐
│                      UTILISATEURS FINAUX                         │
│            (Gérants PME - Smartphones & Desktop)                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTPS
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                   FRONTEND (React PWA)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Dashboards  │  │   Alertes    │  │   Rapports   │          │
│  │  Analytics   │  │ Notifications│  │   Exports    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────────────────────────────────────────┐          │
│  │     Service Worker (Cache, Offline Queue)        │          │
│  └──────────────────────────────────────────────────┘          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ REST API (JSON)
                         │ JWT Authentication
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                  API GATEWAY (FastAPI)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Auth Router  │  │  Dashboard   │  │   Alerting   │          │
│  │              │  │   Router     │  │    Router    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Reports    │  │  Analytics   │  │   Tenant     │          │
│  │   Router     │  │   Router     │  │   Router     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
┌────────▼─────┐  ┌─────▼──────┐  ┌────▼──────┐
│  PostgreSQL  │  │   Redis    │  │  Celery   │
│   Database   │  │   Cache    │  │  Workers  │
│ (Multi-Tenant)│  │  Sessions  │  │  Tasks    │
└──────────────┘  └────────────┘  └───────────┘
         │                              │
         │                              │
┌────────▼──────────────────────────────▼──────┐
│         INTÉGRATIONS EXTERNES                 │
│  ┌──────────────┐  ┌──────────────┐          │
│  │  WhatsApp    │  │    Email     │          │
│  │   Business   │  │   (SMTP)     │          │
│  └──────────────┘  └──────────────┘          │
└───────────────────────────────────────────────┘
```

---

## 2. STACK TECHNIQUE

### 2.1 Technologies Backend

```yaml
Framework Principal:
  - FastAPI 0.104+            # Framework API moderne, performant
  - Python 3.11+              # Dernière version stable
  - Pydantic 2.0+             # Validation données & sérialisation

Base de Données:
  - PostgreSQL 15+            # Base relationnelle principale
  - SQLAlchemy 2.0            # ORM pour gestion modèles
  - Alembic                   # Migrations schéma DB

Cache & Queue:
  - Redis 7.0+                # Cache, sessions, queue messages
  - Celery 5.3+               # Tâches asynchrones (rapports, alertes)

Sécurité:
  - python-jose[cryptography] # Gestion JWT
  - passlib[bcrypt]           # Hashing mots de passe
  - python-multipart          # Upload fichiers

Observabilité:
  - prometheus-fastapi-instrumentator  # Métriques API
  - python-json-logger                 # Logs structurés
  - sentry-sdk                         # Error tracking
```

### 2.2 Technologies Frontend

```yaml
Framework Principal:
  - React 18.2+               # Framework UI moderne
  - TypeScript 5.0+           # Typage statique
  - Vite 5.0+                 # Build tool rapide

UI Components & Styling:
  - TailwindCSS 3.4+          # Utility-first CSS
  - Shadcn/ui                 # Composants UI accessibles
  - Recharts 2.x              # Graphiques & visualisations
  - Lucide React              # Icônes modernes

State Management:
  - TanStack Query (React Query)  # Gestion état serveur
  - Zustand                       # État local léger

Routing & Forms:
  - React Router 6.x          # Navigation SPA
  - React Hook Form           # Gestion formulaires
  - Zod                       # Validation schémas

PWA & Offline:
  - Workbox 7.x               # Service Worker stratégies
  - IndexedDB (Dexie.js)      # Base locale offline
  - localForage               # Abstraction storage
```

### 2.3 DevOps & Infrastructure

```yaml
Conteneurisation:
  - Docker 24+                # Containerisation
  - Docker Compose            # Orchestration locale

CI/CD:
  - GitHub Actions            # Pipeline CI/CD
  - Pre-commit hooks          # Qualité code

Monitoring:
  - Grafana                   # Visualisation métriques
  - Prometheus                # Collecte métriques
  - Loki                      # Agrégation logs

Hébergement (MVP):
  - Hetzner Cloud / OVH       # VPS Europe, bas coût
  - Option: Railway.app       # PaaS pour démarrage rapide
  - Cloudflare                # CDN + protection DDoS
```

---

## 3. ARCHITECTURE BACKEND (FASTAPI)

### 3.1 Structure Projet Backend

```
digiboost-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Point entrée FastAPI
│   ├── config.py               # Configuration (env vars)
│   │
│   ├── api/                    # Routes API
│   │   ├── __init__.py
│   │   ├── deps.py             # Dépendances communes (auth, db)
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py         # Authentification
│   │   │   ├── tenants.py      # Gestion tenants
│   │   │   ├── dashboards.py   # Endpoints dashboards
│   │   │   ├── analytics.py    # Analyses & KPIs
│   │   │   ├── alerts.py       # Gestion alertes
│   │   │   ├── reports.py      # Génération rapports
│   │   │   └── products.py     # Produits (lecture seule MVP)
│   │
│   ├── core/                   # Logique métier centrale
│   │   ├── __init__.py
│   │   ├── security.py         # JWT, hashing passwords
│   │   ├── tenant_context.py   # Isolation multi-tenant
│   │   └── exceptions.py       # Exceptions custom
│   │
│   ├── models/                 # Modèles SQLAlchemy
│   │   ├── __init__.py
│   │   ├── base.py             # Modèle base (timestamps, etc.)
│   │   ├── tenant.py           # Tenant (PME cliente)
│   │   ├── user.py             # Utilisateurs
│   │   ├── product.py          # Produits
│   │   ├── sale.py             # Ventes
│   │   ├── stock_movement.py   # Mouvements stock
│   │   ├── alert.py            # Alertes configurées
│   │   └── alert_history.py    # Historique alertes
│   │
│   ├── schemas/                # Schémas Pydantic (DTO)
│   │   ├── __init__.py
│   │   ├── auth.py             # Token, Login
│   │   ├── tenant.py           # Tenant DTO
│   │   ├── dashboard.py        # Réponses dashboards
│   │   ├── alert.py            # Configuration alertes
│   │   └── report.py           # Paramètres rapports
│   │
│   ├── services/               # Logique métier
│   │   ├── __init__.py
│   │   ├── dashboard_service.py    # Calculs dashboards
│   │   ├── kpi_service.py          # Calculs KPIs
│   │   ├── alert_service.py        # Évaluation alertes
│   │   ├── prediction_service.py   # Prédictions ruptures
│   │   └── report_service.py       # Génération rapports
│   │
│   ├── db/                     # Base de données
│   │   ├── __init__.py
│   │   ├── session.py          # Gestion sessions DB
│   │   ├── base_class.py       # Classes base
│   │   └── init_db.py          # Initialisation DB
│   │
│   ├── tasks/                  # Tâches asynchrones Celery
│   │   ├── __init__.py
│   │   ├── celery_app.py       # Configuration Celery
│   │   ├── alert_tasks.py      # Évaluation alertes périodique
│   │   └── report_tasks.py     # Génération rapports auto
│   │
│   ├── integrations/           # Intégrations externes
│   │   ├── __init__.py
│   │   ├── whatsapp.py         # WhatsApp Business API
│   │   └── email.py            # Envoi emails (SMTP)
│   │
│   └── utils/                  # Utilitaires
│       ├── __init__.py
│       ├── logger.py           # Configuration logs
│       └── validators.py       # Validations custom
│
├── alembic/                    # Migrations DB
│   ├── versions/
│   └── env.py
│
├── tests/                      # Tests
│   ├── api/
│   ├── services/
│   └── conftest.py
│
├── docker/                     # Configuration Docker
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── .env.example                # Variables environnement
├── requirements.txt            # Dépendances Python
├── pyproject.toml              # Configuration projet
└── README.md
```

### 3.2 Modèle de Données Simplifié (MVP)

```sql
-- TENANT (PME Cliente)
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    ninea VARCHAR(50),                  -- Numéro entreprise Sénégal
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    settings JSONB,                     -- Config alertes, objectifs
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- UTILISATEURS (Gérants, employés)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',    -- admin, user, viewer
    whatsapp_number VARCHAR(20),        -- Pour alertes
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- CATÉGORIES PRODUITS
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- FOURNISSEURS
CREATE TABLE suppliers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    code VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(255),
    lead_time_days INT DEFAULT 7,       -- Délai livraison moyen
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, code)
);

-- PRODUITS
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    code VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    category_id UUID REFERENCES categories(id),
    supplier_id UUID REFERENCES suppliers(id),
    
    -- Tarification
    purchase_price DECIMAL(15,2) NOT NULL,
    sale_price DECIMAL(15,2) NOT NULL,
    unit VARCHAR(50) DEFAULT 'unité',   -- sac, kg, litre, etc.
    
    -- Stock
    current_stock DECIMAL(15,3) DEFAULT 0,
    min_stock DECIMAL(15,3),
    max_stock DECIMAL(15,3),
    
    -- Métadonnées
    description TEXT,
    barcode VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(tenant_id, code)
);

-- VENTES
CREATE TABLE sales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id),
    
    sale_date TIMESTAMP NOT NULL,
    quantity DECIMAL(15,3) NOT NULL,
    unit_price DECIMAL(15,2) NOT NULL,
    total_amount DECIMAL(15,2) NOT NULL,
    
    -- Optionnel
    order_number VARCHAR(100),
    customer_name VARCHAR(255),
    status VARCHAR(50) DEFAULT 'DELIVERED',
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- MOUVEMENTS STOCK
CREATE TABLE stock_movements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id),
    
    movement_date TIMESTAMP NOT NULL,
    movement_type VARCHAR(50) NOT NULL,    -- ENTRY, EXIT, ADJUSTMENT
    quantity DECIMAL(15,3) NOT NULL,
    
    -- Contexte
    reference VARCHAR(100),                -- Réf bon livraison, etc.
    reason TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- ALERTES CONFIGURÉES
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,       -- LOW_STOCK, RUPTURE, etc.
    
    -- Configuration
    conditions JSONB NOT NULL,             -- Seuils, paramètres
    channels JSONB NOT NULL,               -- WhatsApp, Email
    recipients JSONB NOT NULL,             -- Numéros/emails
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- HISTORIQUE ALERTES
CREATE TABLE alert_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    alert_id UUID REFERENCES alerts(id),
    
    triggered_at TIMESTAMP NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,         -- LOW, MEDIUM, HIGH, CRITICAL
    
    message TEXT NOT NULL,
    details JSONB,                         -- Contexte additionnel
    
    -- Envoi
    sent_whatsapp BOOLEAN DEFAULT FALSE,
    sent_email BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- VUES MATÉRIALISÉES (Dashboards)
-- Ces vues seront créées pour optimiser les dashboards
-- Exemple: Vue pour le dashboard "Vue d'Ensemble"
```

### 3.3 Endpoints API Principaux (MVP)

```python
# api/v1/auth.py
@router.post("/login", response_model=Token)
def login(credentials: LoginRequest)
    """Authentification JWT"""

@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str)
    """Renouvellement token"""

# api/v1/dashboards.py
@router.get("/overview", response_model=DashboardOverview)
def get_dashboard_overview(tenant_id: UUID)
    """Dashboard Vue d'Ensemble"""
    # - Santé stock (ruptures, alertes)
    # - Performance ventes (CA, taux service)
    # - Valorisation stock

@router.get("/stock-detail", response_model=StockDetailDashboard)
def get_stock_detail(tenant_id: UUID, filters: StockFilters)
    """Dashboard Gestion Stock Détaillée"""
    # - Liste produits avec statuts
    # - Détails par produit

@router.get("/sales-analysis", response_model=SalesAnalysisDashboard)
def get_sales_analysis(tenant_id: UUID, period: str)
    """Dashboard Analyse Ventes"""
    # - Évolution CA temporelle
    # - Top produits, catégories

@router.get("/predictions", response_model=PredictionsDashboard)
def get_predictions(tenant_id: UUID, horizon_days: int = 15)
    """Dashboard Prédictions & Recommandations"""
    # - Ruptures prévues
    # - Recommandations achat

# api/v1/analytics.py
@router.get("/kpis", response_model=KPIResponse)
def get_kpis(tenant_id: UUID, period: str)
    """Calcul KPIs consolidés"""

@router.get("/products/{product_id}/analysis")
def analyze_product(product_id: UUID)
    """Analyse détaillée produit"""

# api/v1/alerts.py
@router.get("/", response_model=List[AlertConfig])
def list_alerts(tenant_id: UUID)
    """Liste alertes configurées"""

@router.post("/", response_model=AlertConfig)
def create_alert(alert: AlertCreate)
    """Créer nouvelle alerte"""

@router.put("/{alert_id}", response_model=AlertConfig)
def update_alert(alert_id: UUID, alert: AlertUpdate)
    """Modifier configuration alerte"""

@router.get("/history", response_model=List[AlertHistoryItem])
def get_alert_history(tenant_id: UUID, filters: HistoryFilters)
    """Historique déclenchements"""

# api/v1/reports.py
@router.post("/generate", response_model=ReportResponse)
def generate_report(report_request: ReportRequest)
    """Générer rapport (Excel/PDF)"""

@router.get("/scheduled", response_model=List[ScheduledReport])
def list_scheduled_reports(tenant_id: UUID)
    """Liste rapports automatisés"""
```

---

## 4. ARCHITECTURE FRONTEND (REACT)

### 4.1 Structure Projet Frontend

```
digiboost-frontend/
├── public/
│   ├── manifest.json           # PWA manifest
│   ├── service-worker.js       # Service Worker (généré)
│   └── icons/                  # Icônes PWA
│
├── src/
│   ├── main.tsx                # Point entrée
│   ├── App.tsx                 # Composant racine
│   ├── vite-env.d.ts
│   │
│   ├── api/                    # Clients API
│   │   ├── client.ts           # Client HTTP (axios/fetch)
│   │   ├── auth.ts             # API authentification
│   │   ├── dashboards.ts       # API dashboards
│   │   ├── alerts.ts           # API alertes
│   │   └── reports.ts          # API rapports
│   │
│   ├── components/             # Composants réutilisables
│   │   ├── ui/                 # Composants base (shadcn/ui)
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   └── ...
│   │   │
│   │   ├── layout/             # Layout général
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── MainLayout.tsx
│   │   │
│   │   ├── charts/             # Graphiques personnalisés
│   │   │   ├── LineChart.tsx
│   │   │   ├── BarChart.tsx
│   │   │   └── KPICard.tsx
│   │   │
│   │   └── common/             # Composants communs
│   │       ├── LoadingSpinner.tsx
│   │       ├── ErrorBoundary.tsx
│   │       └── EmptyState.tsx
│   │
│   ├── features/               # Fonctionnalités par domaine
│   │   ├── auth/
│   │   │   ├── components/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   └── ProtectedRoute.tsx
│   │   │   ├── hooks/
│   │   │   │   └── useAuth.ts
│   │   │   └── store/
│   │   │       └── authStore.ts
│   │   │
│   │   ├── dashboard/
│   │   │   ├── components/
│   │   │   │   ├── OverviewDashboard.tsx
│   │   │   │   ├── StockHealthCard.tsx
│   │   │   │   └── SalesPerformanceCard.tsx
│   │   │   └── hooks/
│   │   │       └── useDashboardData.ts
│   │   │
│   │   ├── stock/
│   │   │   ├── components/
│   │   │   │   ├── StockDetailDashboard.tsx
│   │   │   │   ├── ProductList.tsx
│   │   │   │   └── ProductDetail.tsx
│   │   │   └── hooks/
│   │   │       └── useStockData.ts
│   │   │
│   │   ├── sales/
│   │   │   ├── components/
│   │   │   │   ├── SalesAnalysisDashboard.tsx
│   │   │   │   └── SalesTrendChart.tsx
│   │   │   └── hooks/
│   │   │       └── useSalesData.ts
│   │   │
│   │   ├── predictions/
│   │   │   ├── components/
│   │   │   │   ├── PredictionsDashboard.tsx
│   │   │   │   └── RecommendationsList.tsx
│   │   │   └── hooks/
│   │   │       └── usePredictions.ts
│   │   │
│   │   ├── alerts/
│   │   │   ├── components/
│   │   │   │   ├── AlertsManagement.tsx
│   │   │   │   ├── AlertConfigForm.tsx
│   │   │   │   └── AlertHistory.tsx
│   │   │   └── hooks/
│   │   │       └── useAlerts.ts
│   │   │
│   │   └── reports/
│   │       ├── components/
│   │       │   ├── ReportsPage.tsx
│   │       │   └── ReportGenerator.tsx
│   │       └── hooks/
│   │           └── useReports.ts
│   │
│   ├── hooks/                  # Hooks globaux
│   │   ├── useOfflineSync.ts   # Gestion offline
│   │   ├── useNetworkStatus.ts # Détection connexion
│   │   └── useLocalStorage.ts  # Storage local
│   │
│   ├── lib/                    # Utilitaires
│   │   ├── utils.ts            # Fonctions helpers
│   │   ├── constants.ts        # Constantes
│   │   ├── formatters.ts       # Formatage données
│   │   └── validators.ts       # Validations
│   │
│   ├── services/               # Services métier frontend
│   │   ├── offlineService.ts   # Gestion mode offline
│   │   ├── syncService.ts      # Synchronisation données
│   │   └── cacheService.ts     # Gestion cache
│   │
│   ├── stores/                 # State management global (Zustand)
│   │   ├── useAppStore.ts      # Store application
│   │   └── useTenantStore.ts   # Store tenant courant
│   │
│   ├── types/                  # Types TypeScript
│   │   ├── api.types.ts        # Types API
│   │   ├── dashboard.types.ts  # Types dashboards
│   │   └── models.types.ts     # Types modèles
│   │
│   ├── styles/                 # Styles globaux
│   │   ├── globals.css
│   │   └── tailwind.css
│   │
│   └── routes/                 # Configuration routes
│       └── index.tsx
│
├── .env.example
├── .eslintrc.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── package.json
└── README.md
```

### 4.2 Configuration PWA (Progressive Web App)

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'robots.txt', 'icons/**/*'],
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
        // Stratégie cache
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\.digiboost\.sn\/api\/v1\/dashboards/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'dashboard-cache',
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 300 // 5 minutes
              },
              networkTimeoutSeconds: 10
            }
          },
          {
            urlPattern: /^https:\/\/api\.digiboost\.sn\/api\/v1\/products/,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'products-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 3600 // 1 heure
              }
            }
          }
        ]
      }
    })
  ]
});
```

### 4.3 Gestion État avec TanStack Query

```typescript
// hooks/useDashboardData.ts
import { useQuery } from '@tanstack/react-query';
import { dashboardsApi } from '@/api/dashboards';

export const useDashboardOverview = () => {
  return useQuery({
    queryKey: ['dashboard', 'overview'],
    queryFn: () => dashboardsApi.getOverview(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 30 * 1000, // Rafraîchir toutes les 30s
    refetchOnWindowFocus: true,
    // Mode offline
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000)
  });
};
```

---

## 5. ARCHITECTURE BASE DE DONNÉES

### 5.1 Stratégie Multi-Tenant

```
APPROCHE: Schéma Partagé avec Isolation par tenant_id (Shared Database)

Avantages:
✅ Simple à implémenter pour MVP
✅ Coût infrastructure réduit
✅ Maintenance centralisée
✅ Backups unifiés

Implémentation:
- Chaque table contient colonne tenant_id
- Row Level Security (RLS) PostgreSQL
- Middleware FastAPI filtre automatiquement par tenant
```

```python
# core/tenant_context.py
from contextvars import ContextVar

# Context variable pour tenant courant
current_tenant_id: ContextVar[UUID | None] = ContextVar(
    'current_tenant_id', 
    default=None
)

# Middleware FastAPI
class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extraire tenant_id du JWT token
        token = request.headers.get('Authorization')
        if token:
            payload = decode_jwt(token)
            tenant_id = payload.get('tenant_id')
            current_tenant_id.set(UUID(tenant_id))
        
        response = await call_next(request)
        current_tenant_id.set(None)
        return response

# Base model avec filtrage automatique
class TenantBaseModel(Base):
    __abstract__ = True
    
    tenant_id = Column(UUID, nullable=False, index=True)
    
    @declared_attr
    def __table_args__(cls):
        return (
            # Index composite pour performance
            Index(f'idx_{cls.__tablename__}_tenant', 'tenant_id'),
        )
```

### 5.2 Vues Matérialisées pour Performance

```sql
-- Vue Dashboard "Vue d'Ensemble" - Santé Stock
CREATE MATERIALIZED VIEW mv_dashboard_stock_health AS
SELECT 
    p.tenant_id,
    COUNT(DISTINCT p.id) as total_products,
    COUNT(DISTINCT CASE WHEN p.current_stock = 0 THEN p.id END) as rupture_count,
    COUNT(DISTINCT CASE WHEN p.current_stock <= p.min_stock AND p.current_stock > 0 THEN p.id END) as low_stock_count,
    SUM(p.current_stock * p.purchase_price) as total_stock_value
FROM products p
WHERE p.is_active = TRUE
GROUP BY p.tenant_id;

-- Rafraîchissement toutes les 5 minutes
CREATE UNIQUE INDEX ON mv_dashboard_stock_health (tenant_id);

-- Vue Dashboard "Vue d'Ensemble" - Performance Ventes
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

-- Fonction de rafraîchissement automatique (appelée par Celery)
CREATE OR REPLACE FUNCTION refresh_dashboard_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_dashboard_stock_health;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_dashboard_sales_performance;
END;
$$ LANGUAGE plpgsql;
```

### 5.3 Indexes Optimisés

```sql
-- Index composites pour requêtes fréquentes

-- Produits: recherche par tenant + filtre statut
CREATE INDEX idx_products_tenant_active ON products(tenant_id, is_active) 
WHERE is_active = TRUE;

-- Ventes: agrégations temporelles
CREATE INDEX idx_sales_tenant_date ON sales(tenant_id, sale_date DESC);
CREATE INDEX idx_sales_product ON sales(product_id, sale_date DESC);

-- Mouvements stock: historique produit
CREATE INDEX idx_stock_movements_product ON stock_movements(product_id, movement_date DESC);

-- Alertes: recherche actives
CREATE INDEX idx_alerts_tenant_active ON alerts(tenant_id, is_active) 
WHERE is_active = TRUE;

-- Historique alertes: consultation récente
CREATE INDEX idx_alert_history_tenant_date ON alert_history(tenant_id, triggered_at DESC);
```

---

## 6. SÉCURITÉ & AUTHENTIFICATION (JWT)

### 6.1 Flux Authentification JWT

```
┌─────────────┐                          ┌─────────────┐
│   Client    │                          │   Backend   │
│   React     │                          │   FastAPI   │
└──────┬──────┘                          └──────┬──────┘
       │                                        │
       │  POST /api/v1/auth/login               │
       │  { email, password }                   │
       ├───────────────────────────────────────>│
       │                                        │
       │                                        │ Vérification
       │                                        │ credentials
       │                                        │
       │  { access_token, refresh_token }       │
       │<───────────────────────────────────────┤
       │                                        │
       │  Stockage tokens                       │
       │  - access: memory                      │
       │  - refresh: httpOnly cookie            │
       │                                        │
       │  GET /api/v1/dashboards/overview       │
       │  Authorization: Bearer {access_token}  │
       ├───────────────────────────────────────>│
       │                                        │
       │                                        │ Validation JWT
       │                                        │ Extraction tenant_id
       │                                        │
       │  { dashboard_data }                    │
       │<───────────────────────────────────────┤
       │                                        │
       
       ... access_token expire après 15 min ...
       
       │  GET /api/v1/dashboards/...            │
       │  Authorization: Bearer {expired}       │
       ├───────────────────────────────────────>│
       │                                        │
       │  401 Unauthorized                      │
       │<───────────────────────────────────────┤
       │                                        │
       │  POST /api/v1/auth/refresh             │
       │  Cookie: refresh_token                 │
       ├───────────────────────────────────────>│
       │                                        │
       │  { access_token, refresh_token }       │
       │<───────────────────────────────────────┤
       │                                        │
```

### 6.2 Configuration JWT Backend

```python
# core/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": expire,
        "type": "access"
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str, expected_type: str = "access"):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != expected_type:
            raise JWTError("Invalid token type")
        return payload
    except JWTError:
        return None

# api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Dépendance: extraction utilisateur courant depuis JWT"""
    
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
    current_tenant_id.set(UUID(tenant_id))
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user
```

### 6.3 Protection CSRF & XSS

```python
# main.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()

# CORS Configuration (Production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.digiboost.sn",
        "https://digiboost.sn"
    ],  # Domaines autorisés
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    max_age=3600,
)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["api.digiboost.sn", "*.digiboost.sn"]
)

# Security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

---

## 7. GESTION OFFLINE/ONLINE (CONTEXTE SÉNÉGAL)

### 7.1 Stratégie Offline-First

```
PROBLÉMATIQUES SÉNÉGAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ Connexion internet instable (coupures fréquentes)
❌ Débit limité (3G majoritaire, 4G limitée aux zones urbaines)
❌ Coût data élevé (1 GB ~ 1000 FCFA)
❌ Smartphones entrée de gamme (RAM limitée)

SOLUTIONS TECHNIQUES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ PWA avec Service Worker (cache intelligent)
✅ IndexedDB pour stockage local (~50 MB)
✅ Queue actions offline → sync quand online
✅ Chargement différé (lazy loading)
✅ Compression données (gzip)
✅ Indicateur connexion visible
✅ Mode lecture seule offline gracieux
```

### 7.2 Service Worker Configuration

```typescript
// services/offlineService.ts
import Dexie, { Table } from 'dexie';

// Base de données locale
export interface CachedDashboard {
  id: string;
  tenantId: string;
  type: 'overview' | 'stock' | 'sales' | 'predictions';
  data: any;
  cachedAt: Date;
  expiresAt: Date;
}

export interface PendingAction {
  id: string;
  type: 'alert_update' | 'report_generate';
  payload: any;
  createdAt: Date;
  retryCount: number;
}

class OfflineDatabase extends Dexie {
  dashboards!: Table<CachedDashboard>;
  pendingActions!: Table<PendingAction>;

  constructor() {
    super('DigiboostOfflineDB');
    this.version(1).stores({
      dashboards: 'id, tenantId, type, cachedAt',
      pendingActions: 'id, type, createdAt'
    });
  }
}

const db = new OfflineDatabase();

export class OfflineService {
  // Sauvegarder dashboard en cache
  static async cacheDashboard(
    type: string,
    data: any,
    tenantId: string
  ): Promise<void> {
    const id = `${tenantId}-${type}`;
    const now = new Date();
    const expiresAt = new Date(now.getTime() + 10 * 60 * 1000); // 10 min

    await db.dashboards.put({
      id,
      tenantId,
      type: type as any,
      data,
      cachedAt: now,
      expiresAt
    });
  }

  // Récupérer dashboard depuis cache
  static async getCachedDashboard(
    type: string,
    tenantId: string
  ): Promise<any | null> {
    const id = `${tenantId}-${type}`;
    const cached = await db.dashboards.get(id);

    if (!cached) return null;

    // Vérifier expiration
    if (new Date() > cached.expiresAt) {
      await db.dashboards.delete(id);
      return null;
    }

    return cached.data;
  }

  // Ajouter action en attente
  static async queueAction(
    type: string,
    payload: any
  ): Promise<void> {
    await db.pendingActions.add({
      id: crypto.randomUUID(),
      type: type as any,
      payload,
      createdAt: new Date(),
      retryCount: 0
    });
  }

  // Synchroniser actions en attente
  static async syncPendingActions(): Promise<void> {
    const actions = await db.pendingActions.toArray();

    for (const action of actions) {
      try {
        // Exécuter action selon type
        await this.executeAction(action);
        
        // Supprimer si succès
        await db.pendingActions.delete(action.id);
      } catch (error) {
        // Incrémenter retry
        if (action.retryCount < 3) {
          await db.pendingActions.update(action.id, {
            retryCount: action.retryCount + 1
          });
        } else {
          // Abandonner après 3 tentatives
          await db.pendingActions.delete(action.id);
        }
      }
    }
  }

  private static async executeAction(action: PendingAction): Promise<void> {
    // Implémenter logique selon type action
    switch (action.type) {
      case 'alert_update':
        // Appel API mise à jour alerte
        break;
      case 'report_generate':
        // Appel API génération rapport
        break;
    }
  }
}
```

### 7.3 Hook Détection Connexion

```typescript
// hooks/useNetworkStatus.ts
import { useState, useEffect } from 'react';

export const useNetworkStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [connectionType, setConnectionType] = useState<string>('unknown');

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Détection type connexion (si disponible)
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      setConnectionType(connection?.effectiveType || 'unknown');

      connection?.addEventListener('change', () => {
        setConnectionType(connection.effectiveType);
      });
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return { isOnline, connectionType };
};
```

### 7.4 Composant Indicateur Connexion

```tsx
// components/NetworkIndicator.tsx
import { useNetworkStatus } from '@/hooks/useNetworkStatus';
import { Wifi, WifiOff, Signal } from 'lucide-react';

export const NetworkIndicator = () => {
  const { isOnline, connectionType } = useNetworkStatus();

  if (isOnline) {
    return (
      <div className="flex items-center gap-2 text-green-600 text-sm">
        <Wifi className="w-4 h-4" />
        <span>Connecté</span>
        {connectionType !== 'unknown' && (
          <span className="text-xs text-gray-500">
            ({connectionType})
          </span>
        )}
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 text-amber-600 text-sm bg-amber-50 px-3 py-2 rounded-md">
      <WifiOff className="w-4 h-4" />
      <span>Mode hors ligne - Les données affichées peuvent être anciennes</span>
    </div>
  );
};
```

---

## 8. INTÉGRATIONS EXTERNES

### 8.1 WhatsApp Business API

```python
# integrations/whatsapp.py
import httpx
from typing import List

class WhatsAppService:
    """Service envoi messages WhatsApp Business API"""
    
    def __init__(self):
        self.api_url = os.getenv("WHATSAPP_API_URL")
        self.api_token = os.getenv("WHATSAPP_API_TOKEN")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    
    async def send_alert(
        self,
        recipient: str,  # Format: +221771234567
        message: str,
        template_name: str = None
    ) -> bool:
        """
        Envoyer alerte WhatsApp
        
        Args:
            recipient: Numéro téléphone (format international)
            message: Contenu message
            template_name: Template pré-approuvé (optionnel)
        """
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_url}/{self.phone_number_id}/messages",
                    headers=headers,
                    json=payload,
                    timeout=10.0
                )
                response.raise_for_status()
                return True
            except Exception as e:
                # Log erreur
                logger.error(f"WhatsApp send failed: {e}")
                return False
    
    async def send_bulk_alerts(
        self,
        recipients: List[str],
        message: str
    ) -> dict:
        """Envoi groupé avec rapport succès/échec"""
        
        results = {
            "success": [],
            "failed": []
        }
        
        for recipient in recipients:
            success = await self.send_alert(recipient, message)
            if success:
                results["success"].append(recipient)
            else:
                results["failed"].append(recipient)
        
        return results

# Exemple message formaté
ALERT_TEMPLATES = {
    "rupture_stock": """
🚨 *ALERTE RUPTURE STOCK*

Produit: {product_name}
Stock actuel: {current_stock} {unit}
Statut: ❌ RUPTURE

Action recommandée:
Commander {recommended_qty} {unit} auprès de {supplier}

Digiboost PME - Intelligence Supply Chain
    """.strip(),
    
    "stock_faible": """
⚠️ *ALERTE STOCK FAIBLE*

Produit: {product_name}
Stock actuel: {current_stock} {unit}
Stock minimum: {min_stock} {unit}
Couverture: {coverage_days} jours

Rupture prévue: {predicted_date}

Commander avant cette date pour éviter rupture.

Digiboost PME
    """.strip()
}
```

### 8.2 Service Email (SMTP)

```python
# integrations/email.py
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib

class EmailService:
    """Service envoi emails (rapports, alertes)"""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@digiboost.sn")
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        attachments: List[tuple] = None
    ) -> bool:
        """
        Envoyer email avec pièces jointes optionnelles
        
        Args:
            to_email: Destinataire
            subject: Objet
            body_html: Corps HTML
            attachments: [(filename, bytes), ...]
        """
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.from_email
        msg['To'] = to_email
        
        # Corps HTML
        html_part = MIMEText(body_html, 'html')
        msg.attach(html_part)
        
        # Pièces jointes
        if attachments:
            for filename, file_data in attachments:
                attachment = MIMEApplication(file_data)
                attachment.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=filename
                )
                msg.attach(attachment)
        
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            return True
        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return False
```

---

## 9. INFRASTRUCTURE & DÉPLOIEMENT

### 9.1 Architecture Infrastructure (MVP)

```
┌────────────────────────────────────────────────────────────┐
│                    CLOUDFLARE CDN                           │
│         (Cache statique, Protection DDoS, SSL)              │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       │ HTTPS
                       │
┌──────────────────────▼─────────────────────────────────────┐
│              VPS HETZNER / OVH (Europe)                     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              Docker Compose                         │    │
│  │                                                      │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │    │
│  │  │   Nginx     │  │   FastAPI   │  │   React    │ │    │
│  │  │   Reverse   │  │   Backend   │  │  Frontend  │ │    │
│  │  │   Proxy     │  │  (Gunicorn) │  │  (Build)   │ │    │
│  │  └─────────────┘  └─────────────┘  └────────────┘ │    │
│  │                                                      │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │    │
│  │  │ PostgreSQL  │  │    Redis    │  │   Celery   │ │    │
│  │  │   Database  │  │    Cache    │  │   Worker   │ │    │
│  │  └─────────────┘  └─────────────┘  └────────────┘ │    │
│  │                                                      │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │         Monitoring Stack                      │  │    │
│  │  │  - Prometheus (métriques)                     │  │    │
│  │  │  - Grafana (dashboards)                       │  │    │
│  │  │  - Loki (logs)                                │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Specs recommandées MVP:                                    │
│  - CPU: 4 vCores                                            │
│  - RAM: 8 GB                                                │
│  - SSD: 160 GB                                              │
│  - Coût: ~20€/mois (Hetzner CX31)                          │
└─────────────────────────────────────────────────────────────┘
```

### 9.2 Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./frontend/dist:/usr/share/nginx/html:ro
    depends_on:
      - backend
    restart: unless-stopped

  # Backend FastAPI
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/digiboost
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - WHATSAPP_API_TOKEN=${WHATSAPP_API_TOKEN}
    volumes:
      - ./backend/app:/app
      - uploads:/app/uploads
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Celery Worker
  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A app.tasks.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/digiboost
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  # Celery Beat (Scheduler)
  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A app.tasks.celery_app beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/digiboost
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=digiboost
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Prometheus (Métriques)
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    ports:
      - "9090:9090"
    restart: unless-stopped

  # Grafana (Visualisation)
  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
  uploads:
```

### 9.3 Pipeline CI/CD (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches:
      - main

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          cd backend
          pytest tests/ -v --cov=app

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Frontend tests
        run: |
          cd frontend
          npm ci
          npm run test

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Frontend
        run: |
          cd frontend
          npm ci
          npm run build
      
      - name: Deploy to VPS
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd /opt/digiboost
            git pull origin main
            docker-compose down
            docker-compose build
            docker-compose up -d
            docker-compose exec -T backend alembic upgrade head
      
      - name: Health Check
        run: |
          sleep 30
          curl -f https://api.digiboost.sn/health || exit 1
      
      - name: Notify deployment
        if: success()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Deployment successful! 🚀'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 10. ROADMAP IMPLÉMENTATION VALUE-DRIVEN

### 10.1 Vue d'Ensemble Roadmap (6-8 Semaines)

```
SPRINT 1 (S1-S2)  →  SPRINT 2 (S3-S4)  →  SPRINT 3 (S5-S6)  →  SPRINT 4 (S7-S8)
   Fondations          Alerting          Analyses            Rapports & Finitions
      ↓                    ↓                  ↓                      ↓
 ✅ Infrastructure   ✅ Alertes temps   ✅ 3 Dashboards    ✅ 3 Rapports auto
 ✅ 1er Dashboard       réel WhatsApp      complets           (Excel/PDF)
 ✅ Auth JWT         ✅ Config alertes   ✅ Prédictions     ✅ Agent IA prep
 ✅ DB + Vues SQL    ✅ Historique       ✅ Recommandations ✅ Tests E2E
                                                            ✅ Documentation

    VALEUR             VALEUR              VALEUR             VALEUR
Voir situation      Être alerté         Analyser données   Automatiser
   stock                proactivement         & anticiper       reporting
```

### 10.2 SPRINT 1 - Fondations (Semaines 1-2)

**Objectif**: Infrastructure complète + Premier dashboard fonctionnel

#### BACKEND (Jours 1-7)

```
Jour 1-2: Setup Projet
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Initialiser projet FastAPI (structure)
✅ Configuration Docker Compose
✅ Variables environnement (.env)
✅ Base PostgreSQL + Redis
✅ Migration Alembic initiale

Livrables:
- docker-compose.yml fonctionnel
- Backend démarrable sur http://localhost:8000
- DB PostgreSQL accessible

Jour 3-5: Modèles & Auth
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Modèles SQLAlchemy (Tenant, User, Product, Sale)
✅ Migration schéma DB
✅ Système auth JWT complet
✅ Middleware multi-tenant
✅ Endpoints auth (/login, /refresh)

Livrables:
- Tables créées en DB
- Login fonctionnel retournant JWT
- Protection routes par JWT

Jour 6-7: Dashboard Vue d'Ensemble (Backend)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Services KPI (dashboard_service.py)
✅ Vues SQL optimisées (mv_dashboard_stock_health, etc.)
✅ Endpoint GET /api/v1/dashboards/overview
✅ Données test (1 tenant, 50 produits, 90j historique)

Livrables:
- API retourne données dashboard
- KPIs calculés correctement:
  * Nombre ruptures
  * Taux service
  * Valorisation stock
  * CA 7/30 jours
```

#### FRONTEND (Jours 8-14)

```
Jour 8-9: Setup Projet React
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Initialiser Vite + React + TypeScript
✅ Configuration Tailwind CSS
✅ Installation Shadcn/ui
✅ Structure dossiers
✅ Configuration ESLint/Prettier

Livrables:
- App React démarrable sur http://localhost:5173
- Tailwind fonctionnel

Jour 10-11: Auth Frontend
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Page login (LoginForm.tsx)
✅ Service auth (api/auth.ts)
✅ Store auth (Zustand)
✅ Hook useAuth
✅ ProtectedRoute component
✅ Gestion tokens (memory + cookie)

Livrables:
- Login fonctionnel avec backend
- Redirection si non authentifié
- Token refresh automatique

Jour 12-14: Dashboard Vue d'Ensemble (Frontend)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Layout principal (Header + Sidebar)
✅ Page dashboard /dashboard/overview
✅ 3 Sections dashboard:
  * Santé Stock (KPI cards + graphique)
  * Performance Ventes (graphiques)
  * Valorisation Stock (total + répartition)
✅ Hook useDashboardData (TanStack Query)
✅ États loading / error
✅ Design responsive mobile

Livrables:
- Dashboard affiche données réelles backend
- Chargement < 3s
- Responsive (mobile + desktop)
- Graphiques interactifs (Recharts)
```

#### CRITÈRES ACCEPTATION SPRINT 1

```
TECHNIQUES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Backend déployé en local (Docker)
✅ Frontend déployé en local (Vite dev)
✅ Auth JWT fonctionnel end-to-end
✅ Dashboard charge données < 3s
✅ Tests unitaires backend (>70% couverture)
✅ DB avec données test cohérentes

FONCTIONNELS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Gérant test peut se connecter
✅ Gérant voit dashboard avec:
  * Nombre produits en rupture
  * Nombre produits stock faible
  * CA 7 jours vs 30 jours
  * Taux de service
  * Valorisation stock totale
✅ KPIs calculés correctement (vérification manuelle)
✅ Interface responsive (testé mobile Android)

DÉMO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Démonstration 15 min devant CTO:
1. Login
2. Navigation dashboard
3. Explication KPIs affichés
4. Test responsive (resize navigateur)
```

### 10.3 SPRINT 2 - Alerting (Semaines 3-4)

**Objectif**: Système alertes configurable + WhatsApp opérationnel

#### Livrables Clés

```
BACKEND (Jours 15-21)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Modèles Alert + AlertHistory
✅ Service alerting (alert_service.py)
✅ Vues SQL alertes (v_alert_rupture_stock, etc.)
✅ Tâches Celery:
  * Évaluation alertes (toutes les 5 min)
  * Envoi WhatsApp
✅ Intégration WhatsApp Business API
✅ Endpoints API:
  * GET /api/v1/alerts (liste alertes)
  * POST /api/v1/alerts (créer alerte)
  * PUT /api/v1/alerts/{id} (modifier)
  * GET /api/v1/alerts/history
✅ 3 types alertes implémentés:
  * Rupture stock
  * Stock faible
  * Baisse taux service

FRONTEND (Jours 22-28)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Page /alerts/management
✅ Liste alertes configurées (table)
✅ Formulaire création alerte (AlertConfigForm)
✅ Toggle activation/désactivation
✅ Page /alerts/history (historique)
✅ Notifications toast si alerte déclenchée
✅ Badge "Alertes" dans header (nombre actives)

CRITÈRES ACCEPTATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Gérant crée alerte "Rupture stock" produit X
✅ Simulation rupture → Alerte WhatsApp reçue < 2 min
✅ Gérant peut désactiver alerte
✅ Historique affiche déclenchements passés
✅ 3 types alertes testés et fonctionnels
```

### 10.4 SPRINT 3 - Analyses (Semaines 5-6)

**Objectif**: Dashboards analyse + Prédictions

#### Livrables Clés

```
BACKEND (Jours 29-35)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Service analytics (analytics_service.py)
✅ Service prédictions (prediction_service.py)
✅ Fonctions SQL:
  * fn_predict_date_rupture
  * fn_calc_quantite_reappro
✅ Endpoints:
  * GET /api/v1/dashboards/stock-detail
  * GET /api/v1/dashboards/sales-analysis
  * GET /api/v1/dashboards/predictions
  * GET /api/v1/analytics/products/{id}

FRONTEND (Jours 36-42)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Dashboard Gestion Stock Détaillée:
  * Liste produits avec statuts
  * Filtres (catégorie, statut, recherche)
  * Détail produit (modal/page)
✅ Dashboard Analyse Ventes:
  * Graphique évolution CA
  * Top 10 produits
  * Analyse par catégorie
✅ Dashboard Prédictions:
  * Liste ruptures prévues 15j
  * Recommandations achat groupées
  * Indicateur fiabilité prédiction

CRITÈRES ACCEPTATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Gérant voit liste produits triable/filtrable
✅ Prédictions ruptures affichées avec dates
✅ Recommandations achat calculées (quantités)
✅ Graphiques ventes fluides (<3s chargement)
✅ Marge erreur prédictions <10% (validation manuelle)
```

### 10.5 SPRINT 4 - Rapports & Finitions (Semaines 7-8)

**Objectif**: Rapports automatisés + Préparation agent IA + Polish

#### Livrables Clés

```
BACKEND (Jours 43-49)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Service rapports (report_service.py)
✅ 3 rapports standards:
  * Inventaire stock (Excel)
  * Synthèse mensuelle (PDF)
  * Analyse ventes détaillée (Excel)
✅ Tâches Celery:
  * Génération rapport auto (1er du mois)
  * Envoi email + WhatsApp
✅ Vues SQL agent IA:
  * v_ai_diagnostic_stock
  * v_ai_analyse_ventes
  * v_ai_recommandations
✅ Documentation vues/fonctions pour IA
✅ Endpoints:
  * POST /api/v1/reports/generate
  * GET /api/v1/reports/scheduled

FRONTEND (Jours 50-56)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Page /reports
✅ Générateur rapport (sélection type, période)
✅ Liste rapports générés (téléchargement)
✅ Configuration rapports automatiques
✅ Polish UI (animations, micro-interactions)
✅ Optimisation performance (lazy loading)
✅ Tests E2E (Playwright/Cypress)
✅ Documentation utilisateur (guide PME)

FINALISATION (Jours 50-56)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Tests E2E complets (happy paths)
✅ Optimisation requêtes SQL (EXPLAIN ANALYZE)
✅ Configuration monitoring (Grafana dashboards)
✅ Documentation technique complète
✅ Guide utilisateur PDF (10 pages)
✅ Vidéo démo 5 min (screen recording)

CRITÈRES ACCEPTATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Rapport mensuel généré automatiquement 1er du mois
✅ Rapports Excel exploitables (formules, graphiques)
✅ Rapports PDF présentables (banquier)
✅ POC démontrable 30 min devant prospect
✅ Uptime >99% sur semaine test
✅ Temps réponse API P95 <500ms
```

### 10.6 Métriques Succès POC

```
ADOPTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 80% gérants consultent dashboard 1×/jour
🎯 90% gérants reçoivent et lisent alertes WhatsApp
🎯 70% gérants génèrent ≥1 rapport/mois

BUSINESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 -50% ruptures de stock (vs avant)
🎯 +15% taux de service moyen
🎯 -30% capital immobilisé (produits dormants)
🎯 +20% marge brute (meilleure gestion)

SATISFACTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 NPS > 50
🎯 70% gérants recommandent plateforme
🎯 80% gérants prêts payer abonnement post-test

TECHNIQUES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Uptime > 99.5%
🎯 Temps chargement dashboards < 3s (P95)
🎯 Taux erreur API < 1%
🎯 Alertes envoyées < 2 min après déclenchement
```

---

## ANNEXES

### A. Estimations Effort (Développeur Full-Stack)

```
SPRINT 1: 80 heures (2 semaines × 40h)
  - Backend: 40h
  - Frontend: 35h
  - Tests/Debug: 5h

SPRINT 2: 80 heures
  - Backend: 35h (intégration WhatsApp complexe)
  - Frontend: 30h
  - Tests/Debug: 15h

SPRINT 3: 80 heures
  - Backend: 40h (prédictions)
  - Frontend: 35h
  - Tests/Debug: 5h

SPRINT 4: 80 heures
  - Backend: 30h
  - Frontend: 25h
  - Documentation: 15h
  - Tests E2E: 10h

TOTAL: 320 heures (8 semaines × 40h)
```

### B. Checklist Avant Déploiement Production

```
SÉCURITÉ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Variables sensibles dans .env (pas hardcodées)
✅ SECRET_KEY robuste (>32 caractères aléatoires)
✅ CORS configuré (domaines autorisés uniquement)
✅ Rate limiting API (ex: 100 req/min par IP)
✅ HTTPS obligatoire (certificat SSL Let's Encrypt)
✅ Firewall VPS configuré (ports 80, 443 uniquement)
✅ DB backups automatiques quotidiens
✅ Logs centralisés (pas de données sensibles)

PERFORMANCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Index DB optimisés (EXPLAIN ANALYZE requêtes)
✅ Cache Redis configuré (sessions, dashboards)
✅ Vues matérialisées rafraîchies (Celery beat)
✅ Frontend minifié (build production)
✅ Images optimisées (WebP, lazy loading)
✅ CDN Cloudflare activé
✅ Compression gzip nginx

MONITORING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Prometheus + Grafana configurés
✅ Dashboards monitoring créés:
  * Santé serveur (CPU, RAM, disque)
  * Métriques API (latence, erreurs)
  * Métriques métier (dashboards consultés, alertes)
✅ Alertes monitoring (email si downtime)
✅ Logs structurés (JSON)
✅ Sentry configuré (error tracking)

QUALITÉ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Tests unitaires backend >70% couverture
✅ Tests intégration API (endpoints critiques)
✅ Tests E2E (happy paths principaux)
✅ Validation Lighthouse PWA (score >80)
✅ Tests charge (JMeter/Locust: 50 users concurrents)
✅ Documentation à jour (README, API docs)
```

---

**FIN DU DOCUMENT**

*Pour questions techniques : CTO Digiboost*  
*Version : 1.0 MVP - Octobre 2025*
