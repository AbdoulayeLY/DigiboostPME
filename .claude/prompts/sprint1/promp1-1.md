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
