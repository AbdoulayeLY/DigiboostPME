# Digiboost PME - Backend API

Plateforme d'intelligence supply chain pour PME sénégalaises.

## 🎯 Vue d'ensemble

API REST construite avec FastAPI pour gérer la chaîne d'approvisionnement des PME :
- Gestion multi-tenant (isolation par tenant_id)
- Dashboards temps réel
- Alertes automatiques (WhatsApp)
- Prédictions ruptures de stock
- Rapports automatisés

## 🛠️ Stack technique

- **Framework**: FastAPI 0.104+
- **Base de données**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0
- **Cache**: Redis 7+
- **Async tasks**: Celery
- **Auth**: JWT (python-jose)
- **Python**: 3.11+

## 📦 Installation

### Prérequis

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+ (ou via Docker)
- Redis 7+ (ou via Docker)

### Setup rapide

1. **Cloner le repository et aller dans le dossier backend**
   ```bash
   cd backend
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate  # Windows
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer les variables d'environnement**
   ```bash
   cp .env.example .env
   # Éditer .env avec vos valeurs
   ```

5. **Démarrer PostgreSQL et Redis avec Docker**
   ```bash
   docker-compose up -d
   ```

6. **Lancer l'application**
   ```bash
   uvicorn app.main:app --reload
   ```

L'API sera accessible sur `http://localhost:8000`

## 🚀 Utilisation

### Endpoints principaux

- **Documentation interactive**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **Health check**: http://localhost:8000/health

### Tester l'API

```bash
# Health check
curl http://localhost:8000/health

# Réponse attendue
{"status":"ok","environment":"development"}
```

## 📁 Structure du projet

```
backend/
├── app/
│   ├── api/              # Endpoints API
│   │   └── v1/           # Version 1 de l'API
│   ├── core/             # Logique centrale (auth, security)
│   ├── db/               # Configuration base de données
│   ├── models/           # Modèles SQLAlchemy
│   ├── schemas/          # Schémas Pydantic (validation)
│   ├── services/         # Logique métier
│   ├── tasks/            # Tâches Celery
│   ├── utils/            # Utilitaires
│   ├── config.py         # Configuration
│   └── main.py           # Point d'entrée
├── alembic/              # Migrations DB
├── tests/                # Tests
├── docker-compose.yml    # Services Docker
├── requirements.txt      # Dépendances Python
└── .env                  # Variables d'environnement
```

## 🗄️ Base de données

### Migrations avec Alembic

```bash
# Créer une nouvelle migration
alembic revision --autogenerate -m "Description"

# Appliquer les migrations
alembic upgrade head

# Revenir en arrière
alembic downgrade -1
```

### Accès direct à PostgreSQL

```bash
# Via Docker
docker exec -it digiboost_postgres psql -U postgres -d digiboost_dev
```

## 🧪 Tests

```bash
# Lancer tous les tests
pytest

# Avec couverture de code
pytest --cov=app --cov-report=html

# Tests spécifiques
pytest tests/api/
```

## 🔧 Développement

### Formater le code

```bash
# Black (formatage)
black app/

# isort (imports)
isort app/

# flake8 (linting)
flake8 app/
```

### Variables d'environnement

Voir `.env.example` pour la liste complète des variables configurables.

Variables essentielles :
- `SECRET_KEY`: Clé secrète pour JWT (min 32 caractères)
- `DATABASE_URL`: URL de connexion PostgreSQL
- `REDIS_URL`: URL de connexion Redis

## 🐳 Docker

### Démarrer les services

```bash
# Démarrer PostgreSQL + Redis
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter les services
docker-compose down
```

### Rebuild les images

```bash
docker-compose up -d --build
```

## 📊 Monitoring

- **Logs**: Les logs sont affichés dans la console en mode développement
- **Métriques**: À venir (Prometheus + Grafana)

## 🔐 Sécurité

- JWT pour l'authentification
- Mots de passe hashés avec bcrypt
- Validation des inputs avec Pydantic
- Isolation multi-tenant stricte
- CORS configuré

## 🌍 Multi-tenant

Le système est conçu en multi-tenant avec isolation par `tenant_id` :
- Chaque PME = 1 tenant
- Toutes les requêtes sont filtrées par tenant_id
- Données complètement isolées entre tenants

## 📝 Documentation

- **API Docs**: http://localhost:8000/api/v1/docs (Swagger)
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **Architecture**: Voir `.claude/context/01-architecture.md`

## 🤝 Contribution

1. Créer une branche feature
2. Faire vos modifications
3. Lancer les tests
4. Créer une Pull Request

## 📄 Licence

Propriétaire - Digiboost © 2025

## 👥 Équipe

- **CEO**: Stratégie & Produit
- **CTO**: Architecture & Développement

---

Pour plus d'informations, consultez la documentation dans `.claude/context/`
