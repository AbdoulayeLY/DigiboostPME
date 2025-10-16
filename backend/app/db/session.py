"""
Configuration de la session de base de données.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config import settings

# Créer le moteur de base de données
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Vérifier la connexion avant de l'utiliser
    pool_size=10,  # Taille du pool de connexions
    max_overflow=20,  # Connexions supplémentaires autorisées
    echo=settings.DEBUG,  # Logger les requêtes SQL en mode debug
)

# Créer le SessionLocal
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Session:
    """
    Dependency pour obtenir une session de base de données.
    À utiliser avec FastAPI Depends().

    Yields:
        Session de base de données

    Example:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
