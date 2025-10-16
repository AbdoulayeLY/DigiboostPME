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
