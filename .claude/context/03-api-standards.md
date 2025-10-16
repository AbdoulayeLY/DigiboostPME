# STANDARDS API - DIGIBOOST PME

## 🌐 CONVENTIONS REST API

### Base URL

```
Développement : http://localhost:8000/api/v1
Production    : https://api.digiboost.sn/api/v1
```

### Structure URLs

```
/api/v1/
├── /auth
│   ├── POST /login
│   ├── POST /register
│   ├── POST /refresh
│   └── POST /logout
├── /dashboards
│   ├── GET /overview
│   ├── GET /stock-health
│   └── GET /sales-metrics
├── /products
│   ├── GET    /
│   ├── POST   /
│   ├── GET    /{id}
│   ├── PUT    /{id}
│   ├── DELETE /{id}
│   └── GET    /export
├── /categories
│   ├── GET    /
│   ├── POST   /
│   ├── GET    /{id}
│   ├── PUT    /{id}
│   └── DELETE /{id}
├── /suppliers
│   ├── GET    /
│   ├── POST   /
│   ├── GET    /{id}
│   ├── PUT    /{id}
│   └── DELETE /{id}
├── /sales
│   ├── GET    /
│   ├── POST   /
│   ├── GET    /{id}
│   ├── PUT    /{id}
│   └── DELETE /{id}
├── /alerts
│   ├── GET    /
│   ├── POST   /
│   ├── GET    /{id}
│   ├── PUT    /{id}
│   ├── DELETE /{id}
│   └── GET    /history
├── /predictions
│   ├── GET /stock-outs
│   └── GET /replenishment-suggestions
├── /reports
│   ├── POST /generate/inventory
│   ├── POST /generate/sales-analysis
│   ├── POST /generate/monthly-summary
│   └── GET  /history
└── /analytics
    ├── GET /sales-trends
    ├── GET /product-performance
    └── GET /category-analysis
```

## 📋 FORMATS STANDARD

### Request Headers

```http
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
Accept: application/json
X-Request-ID: <UUID>  (optionnel, pour traçabilité)
```

### Response Structure

#### Succès (200, 201)

```json
{
  "data": {
    // Payload principal
  },
  "message": "Opération réussie",
  "timestamp": "2025-10-15T10:30:00Z"
}
```

#### Succès avec pagination (200)

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 156,
    "total_pages": 8,
    "has_next": true,
    "has_previous": false
  },
  "message": "Liste récupérée avec succès",
  "timestamp": "2025-10-15T10:30:00Z"
}
```

#### Erreur (4xx, 5xx)

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Les données fournies sont invalides",
    "details": [
      {
        "field": "sale_price",
        "message": "Le prix de vente doit être supérieur au prix d'achat"
      }
    ]
  },
  "timestamp": "2025-10-15T10:30:00Z"
}
```

## 🔐 AUTHENTIFICATION

### JWT Structure

```json
{
  "sub": "user-uuid",           // User ID
  "tenant_id": "tenant-uuid",   // Tenant ID (CRITICAL)
  "email": "user@pme.sn",
  "role": "admin",              // admin, manager, user
  "exp": 1729000000,            // Expiration timestamp
  "iat": 1728996400             // Issued at timestamp
}
```

### Endpoints Auth

#### POST /auth/login

```json
Request:
{
  "email": "gerant@pme.sn",
  "password": "SecurePass123!"
}

Response (200):
{
  "data": {
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": "user-uuid",
      "email": "gerant@pme.sn",
      "full_name": "Abdou Diop",
      "role": "admin",
      "tenant": {
        "id": "tenant-uuid",
        "name": "PME Diop & Frères"
      }
    }
  },
  "message": "Connexion réussie"
}
```

#### POST /auth/refresh

```json
Request:
{
  "refresh_token": "eyJhbGc..."
}

Response (200):
{
  "data": {
    "access_token": "eyJhbGc...",
    "token_type": "Bearer",
    "expires_in": 3600
  },
  "message": "Token rafraîchi"
}
```

## 📊 ENDPOINTS DASHBOARDS

### GET /dashboards/overview

**Description** : Vue d'ensemble complète avec KPIs principaux

**Query Parameters** : Aucun

**Response (200)** :
```json
{
  "data": {
    "stock_health": {
      "total_products": 156,
      "ruptures": 8,
      "faibles": 23,
      "ok": 125,
      "valorisation_achat": 12500000,  // FCFA
      "valorisation_vente": 18750000,
      "taux_service": 91.5             // %
    },
    "sales_metrics": {
      "ca_7j": 1250000,
      "ca_30j": 5600000,
      "ca_90j": 18200000,
      "variation_7j": 8.5,             // % vs semaine précédente
      "variation_30j": -3.2,           // % vs mois précédent
      "panier_moyen": 45000,
      "chart_daily": [
        {"date": "2025-10-01", "amount": 185000},
        {"date": "2025-10-02", "amount": 192000},
        // ... 30 derniers jours
      ]
    },
    "top_products": [
      {
        "product_id": "prod-uuid-1",
        "product_name": "Riz parfumé 50kg",
        "quantity_sold": 145,
        "revenue": 725000,
        "num_transactions": 87
      },
      // ... top 5
    ],
    "dormant_products": [
      {
        "product_id": "prod-uuid-99",
        "product_name": "Produit dormant",
        "days_without_sale": 45,
        "current_stock": 120,
        "valorisation": 360000
      }
      // ... produits sans vente depuis 30+ jours
    ]
  },
  "message": "Dashboard récupéré avec succès",
  "timestamp": "2025-10-15T10:30:00Z"
}
```

## 📦 ENDPOINTS PRODUCTS

### GET /products

**Description** : Liste paginée des produits

**Query Parameters** :
- `page` (int, default=1) : Numéro page
- `page_size` (int, default=20, max=100) : Taille page
- `search` (string) : Recherche nom/code/barcode
- `category_id` (UUID) : Filtrer par catégorie
- `supplier_id` (UUID) : Filtrer par fournisseur
- `stock_status` (enum) : `all`, `ok`, `low`, `out`
- `is_active` (bool) : Filtrer actifs/inactifs
- `sort` (string) : Champ tri (ex: `name`, `-current_stock`)

**Response (200)** :
```json
{
  "data": [
    {
      "id": "prod-uuid-1",
      "code": "RIZ-PARF-50",
      "name": "Riz parfumé 50kg",
      "category": {
        "id": "cat-uuid-1",
        "name": "Alimentaire"
      },
      "supplier": {
        "id": "sup-uuid-1",
        "name": "Fournisseur X"
      },
      "purchase_price": 45000,
      "sale_price": 50000,
      "unit": "sac",
      "current_stock": 245,
      "stock_min": 50,
      "stock_max": 500,
      "stock_status": "ok",
      "valorisation_achat": 11025000,
      "valorisation_vente": 12250000,
      "is_active": true,
      "created_at": "2025-01-15T08:00:00Z",
      "updated_at": "2025-10-14T16:30:00Z"
    }
    // ... autres produits
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 156,
    "total_pages": 8,
    "has_next": true,
    "has_previous": false
  }
}
```

### POST /products

**Description** : Créer nouveau produit

**Request Body** :
```json
{
  "code": "HUILE-5L",
  "name": "Huile végétale 5L",
  "category_id": "cat-uuid-1",
  "supplier_id": "sup-uuid-1",
  "purchase_price": 8500,
  "sale_price": 10000,
  "unit": "bidon",
  "current_stock": 120,
  "stock_min": 30,
  "stock_max": 200,
  "description": "Huile de qualité supérieure",
  "barcode": "3245678901234"
}
```

**Response (201)** :
```json
{
  "data": {
    "id": "prod-uuid-new",
    "code": "HUILE-5L",
    "name": "Huile végétale 5L",
    // ... autres champs
  },
  "message": "Produit créé avec succès"
}
```

**Erreurs possibles** :
- `400 VALIDATION_ERROR` : Données invalides
- `409 CONFLICT` : Code produit déjà existant

### PUT /products/{id}

**Description** : Modifier produit existant

**Request Body** : Identique à POST (tous champs optionnels)

**Response (200)** : Produit mis à jour

### DELETE /products/{id}

**Description** : Supprimer produit (soft delete : `is_active = false`)

**Response (204)** : Pas de contenu

## 💰 ENDPOINTS SALES

### POST /sales

**Description** : Enregistrer nouvelle vente

**Request Body** :
```json
{
  "product_id": "prod-uuid-1",
  "quantity": 5,
  "unit_price": 50000,
  "sale_date": "2025-10-15T14:30:00Z",
  "payment_method": "mobile_money",
  "customer_name": "Client A",
  "order_number": "CMD-2025-1234",
  "notes": "Livraison demain"
}
```

**Response (201)** :
```json
{
  "data": {
    "id": "sale-uuid-new",
    "product_id": "prod-uuid-1",
    "product_name": "Riz parfumé 50kg",
    "quantity": 5,
    "unit_price": 50000,
    "total_amount": 250000,
    "sale_date": "2025-10-15T14:30:00Z",
    "payment_method": "mobile_money",
    "customer_name": "Client A",
    "status": "completed",
    "created_at": "2025-10-15T14:30:15Z"
  },
  "message": "Vente enregistrée avec succès"
}
```

**Validations automatiques** :
- Vérifier `current_stock >= quantity`
- Décrémenter stock automatiquement
- Calculer `total_amount = quantity * unit_price`

## 🚨 ENDPOINTS ALERTS

### POST /alerts

**Description** : Créer nouvelle alerte

**Request Body** :
```json
{
  "name": "Alerte stock faible - Riz",
  "alert_type": "stock_low",
  "conditions": {
    "threshold_type": "percentage",
    "threshold_value": 20,
    "products": ["prod-uuid-1", "prod-uuid-2"],
    "check_frequency": "hourly"
  },
  "channels": ["whatsapp", "email"],
  "recipients": {
    "whatsapp": ["+221771234567"],
    "email": ["gerant@pme.sn"]
  },
  "is_active": true
}
```

**Response (201)** :
```json
{
  "data": {
    "id": "alert-uuid-new",
    "name": "Alerte stock faible - Riz",
    "alert_type": "stock_low",
    "conditions": {...},
    "channels": ["whatsapp", "email"],
    "is_active": true,
    "created_at": "2025-10-15T15:00:00Z"
  },
  "message": "Alerte créée avec succès"
}
```

### GET /alerts/history

**Description** : Historique déclenchements alertes

**Query Parameters** :
- `alert_id` (UUID) : Filtrer par alerte
- `status` (enum) : `pending`, `sent`, `failed`
- `from_date` (ISO date)
- `to_date` (ISO date)

**Response (200)** :
```json
{
  "data": [
    {
      "id": "history-uuid-1",
      "alert": {
        "id": "alert-uuid-1",
        "name": "Alerte stock faible - Riz"
      },
      "triggered_at": "2025-10-15T08:00:00Z",
      "conditions_met": {
        "products": [
          {
            "product_id": "prod-uuid-1",
            "product_name": "Riz parfumé 50kg",
            "current_stock": 48,
            "stock_min": 50,
            "threshold_reached": true
          }
        ]
      },
      "sent_channels": ["whatsapp", "email"],
      "status": "sent",
      "acknowledged_at": "2025-10-15T08:15:00Z"
    }
  ]
}
```

## 🔮 ENDPOINTS PREDICTIONS

### GET /predictions/stock-outs

**Description** : Prédictions ruptures de stock prochains 30 jours

**Response (200)** :
```json
{
  "data": [
    {
      "product_id": "prod-uuid-1",
      "product_name": "Riz parfumé 50kg",
      "current_stock": 120,
      "stock_min": 50,
      "daily_avg_sales": 8.5,
      "predicted_stock_out_date": "2025-10-29",
      "days_until_stock_out": 14,
      "confidence": 0.92,
      "recommended_order_quantity": 200,
      "recommended_order_date": "2025-10-22"
    }
  ],
  "message": "Prédictions générées avec succès"
}
```

## 📄 ENDPOINTS REPORTS

### POST /reports/generate/inventory

**Description** : Générer rapport inventaire (Excel)

**Request Body** :
```json
{
  "include_inactive": false,
  "format": "excel"
}
```

**Response (202 Accepted)** :
```json
{
  "data": {
    "job_id": "report-job-uuid",
    "status": "processing",
    "estimated_completion": "2025-10-15T15:05:00Z"
  },
  "message": "Génération du rapport en cours"
}
```

**Polling Status** : GET `/reports/status/{job_id}`

**Download** : GET `/reports/download/{job_id}`

## ⚠️ CODES D'ERREUR

### 4xx Client Errors

```json
400 BAD_REQUEST
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Les données fournies sont invalides"
  }
}

401 UNAUTHORIZED
{
  "error": {
    "code": "AUTHENTICATION_FAILED",
    "message": "Token invalide ou expiré"
  }
}

403 FORBIDDEN
{
  "error": {
    "code": "INSUFFICIENT_PERMISSIONS",
    "message": "Vous n'avez pas les permissions nécessaires"
  }
}

404 NOT_FOUND
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "La ressource demandée n'existe pas"
  }
}

409 CONFLICT
{
  "error": {
    "code": "DUPLICATE_RESOURCE",
    "message": "Un produit avec ce code existe déjà"
  }
}

422 UNPROCESSABLE_ENTITY
{
  "error": {
    "code": "BUSINESS_RULE_VIOLATION",
    "message": "Stock insuffisant pour effectuer la vente",
    "details": {
      "current_stock": 3,
      "requested_quantity": 5
    }
  }
}

429 TOO_MANY_REQUESTS
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Trop de requêtes. Réessayez dans 60 secondes"
  }
}
```

### 5xx Server Errors

```json
500 INTERNAL_SERVER_ERROR
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "Une erreur interne est survenue",
    "request_id": "req-uuid-123"
  }
}

503 SERVICE_UNAVAILABLE
{
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "Service temporairement indisponible"
  }
}
```

## 📊 PAGINATION & FILTRES

### Query Parameters Standard

```
?page=1
&page_size=20
&search=riz
&sort=-created_at
&is_active=true
```

### Sorting

- Préfixe `-` pour ordre décroissant
- Exemples : `name`, `-created_at`, `sale_price`

### Recherche

- Recherche insensible à la casse
- Sur plusieurs champs (nom, code, description)
- Minimum 2 caractères

## 🔒 RATE LIMITING

```
Authentification : 5 requêtes / minute / IP
API Standard     : 100 requêtes / minute / user
Exports/Rapports : 10 requêtes / heure / user
```

Headers de réponse :
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1729000000
```

---

**Standards garantissent** :
- ✅ Cohérence des endpoints
- ✅ Sécurité multi-tenant stricte
- ✅ Gestion d'erreurs robuste
- ✅ Performance optimale
- ✅ Documentation auto-générée (OpenAPI/Swagger)