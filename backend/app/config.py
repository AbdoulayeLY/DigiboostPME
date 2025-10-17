"""
Configuration de l'application Digiboost PME.
Utilise Pydantic Settings pour charger les variables d'environnement.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuration principale de l'application.
    Les valeurs sont chargées depuis les variables d'environnement ou le fichier .env
    """

    # Application
    APP_NAME: str = "Digiboost PME"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Email
    SMTP_SERVER: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@digiboost.sn"

    # WhatsApp (Twilio)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_FROM: str = "whatsapp:+14155238886"  # Twilio sandbox par défaut
    WHATSAPP_ENABLED: bool = True

    # Monitoring
    SENTRY_DSN: str = ""

    # Reports
    REPORTS_DIR: str = "reports"  # Dossier stockage rapports
    REPORTS_RETENTION_DAYS: int = 90  # Durée conservation (jours)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Retourne la liste des origines CORS autorisées."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Instance globale des settings
settings = Settings()
