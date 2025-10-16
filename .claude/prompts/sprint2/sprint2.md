# PROMPTS CLAUDE CODE - SPRINT 2
## Système Alerting WhatsApp (Semaines 3-4)

**Objectif Sprint** : Alertes temps réel configurables avec notifications WhatsApp  
**Valeur Métier** : Être alerté proactivement des ruptures et stocks faibles  
**Durée** : 2 semaines (80 heures)

---

## 📋 TABLE DES MATIÈRES

1. [Vue d'Ensemble Sprint 2](#vue-densemble-sprint-2)
2. [Semaine 3 : Backend Alerting](#semaine-3--backend-alerting)
3. [Semaine 4 : Frontend Alerting](#semaine-4--frontend-alerting)

---

## VUE D'ENSEMBLE SPRINT 2

### Fonctionnalités à Implémenter

**Backend** :
- Modèles Alert + AlertHistory
- Service évaluation alertes
- Tâches Celery périodiques (toutes les 5 min)
- Intégration WhatsApp Business API
- Historique déclenchements

**Frontend** :
- Page gestion alertes (liste, création, modification)
- Formulaire configuration alerte
- Page historique alertes
- Notifications toast en temps réel
- Badge alertes actives dans header

### Types d'Alertes MVP

1. **Rupture Stock** : Stock = 0
2. **Stock Faible** : Stock ≤ min_stock
3. **Baisse Taux Service** : Taux service < seuil (ex: 90%)

---

## SEMAINE 3 : BACKEND ALERTING

### 🔧 PROMPT 2.1 : Modèles Alert & AlertHistory

```
CONTEXTE:
Le dashboard Vue d'Ensemble est fonctionnel. Je dois maintenant créer le système d'alerting avec stockage des configurations d'alertes et historique des déclenchements.

OBJECTIF:
Créer modèles SQLAlchemy pour:
- Alert (configuration alertes)
- AlertHistory (historique déclenchements)
- Relations avec Tenant
- Migration Alembic

SPÉCIFICATIONS TECHNIQUES:

MODÈLE ALERT (app/models/alert.py):
```python
from sqlalchemy import Column, String, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.models.base import TimestampMixin, TenantMixin
from app.db.base_class import Base

class Alert(Base, TenantMixin, TimestampMixin):
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Configuration
    name = Column(String(255), nullable=False)
    alert_type = Column(String(50), nullable=False)  # RUPTURE_STOCK, LOW_STOCK, BAISSE_TAUX_SERVICE
    
    # Conditions (JSON)
    # Exemple: {"threshold": 10, "product_ids": ["uuid1", "uuid2"]}
    conditions = Column(JSON, nullable=False, default={})
    
    # Canaux (JSON)
    # Exemple: {"whatsapp": true, "email": true}
    channels = Column(JSON, nullable=False, default={"whatsapp": True})
    
    # Destinataires (JSON)
    # Exemple: {"whatsapp_numbers": ["+221771234567"], "emails": ["user@example.com"]}
    recipients = Column(JSON, nullable=False, default={})
    
    # État
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relations
    history = relationship("AlertHistory", back_populates="alert", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Alert {self.name} ({self.alert_type})>"
```

MODÈLE ALERT HISTORY (app/models/alert_history.py):
```python
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
import uuid
from app.models.base import TenantMixin
from app.db.base_class import Base

class AlertHistory(Base, TenantMixin):
    __tablename__ = "alert_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id = Column(UUID(as_uuid=True), ForeignKey('alerts.id', ondelete='CASCADE'))
    
    # Moment déclenchement
    triggered_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Type et sévérité
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    
    # Message
    message = Column(Text, nullable=False)
    details = Column(JSON, default={})  # Contexte additionnel
    
    # Statut envoi
    sent_whatsapp = Column(Boolean, default=False)
    sent_email = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relations
    alert = relationship("Alert", back_populates="history")
    
    def __repr__(self):
        return f"<AlertHistory {self.alert_type} at {self.triggered_at}>"
```

SCHEMAS PYDANTIC (app/schemas/alert.py):
```python
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime

class AlertConditions(BaseModel):
    threshold: Optional[float] = None
    product_ids: Optional[List[UUID]] = None
    category_ids: Optional[List[UUID]] = None

class AlertChannels(BaseModel):
    whatsapp: bool = True
    email: bool = False

class AlertRecipients(BaseModel):
    whatsapp_numbers: List[str] = []
    emails: List[str] = []

class AlertBase(BaseModel):
    name: str
    alert_type: str
    conditions: Dict
    channels: Dict
    recipients: Dict

class AlertCreate(AlertBase):
    pass

class AlertUpdate(BaseModel):
    name: Optional[str] = None
    conditions: Optional[Dict] = None
    channels: Optional[Dict] = None
    recipients: Optional[Dict] = None
    is_active: Optional[bool] = None

class AlertResponse(AlertBase):
    id: UUID
    tenant_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AlertHistoryResponse(BaseModel):
    id: UUID
    alert_id: UUID
    triggered_at: datetime
    alert_type: str
    severity: str
    message: str
    details: Dict
    sent_whatsapp: bool
    sent_email: bool
    
    class Config:
        from_attributes = True
```

MIGRATION ALEMBIC:
```bash
alembic revision --autogenerate -m "Create alerts and alert_history tables"
alembic upgrade head
```

INDEX RECOMMANDÉS:
```sql
CREATE INDEX idx_alerts_tenant_active ON alerts(tenant_id, is_active) WHERE is_active = TRUE;
CREATE INDEX idx_alert_history_tenant_triggered ON alert_history(tenant_id, triggered_at DESC);
CREATE INDEX idx_alert_history_alert ON alert_history(alert_id, triggered_at DESC);
```

CRITÈRES D'ACCEPTATION:
✅ Modèles Alert et AlertHistory créés
✅ Champs JSON pour conditions, channels, recipients
✅ Relations entre Alert et AlertHistory
✅ Schemas Pydantic pour API
✅ Migration Alembic générée et appliquée
✅ Tables créées en base de données
✅ Index créés pour performance
✅ Vérification: \d alerts dans psql

COMMANDES DE TEST:
```bash
# Générer migration
alembic revision --autogenerate -m "Create alerts tables"

# Appliquer
alembic upgrade head

# Vérifier structure
docker-compose exec postgres psql -U postgres -d digiboost_dev
\d alerts
\d alert_history
```
```

---

### 🔧 PROMPT 2.2 : Service Alerting & Évaluation

```
CONTEXTE:
Les modèles Alert sont créés. Je dois maintenant implémenter la logique métier d'évaluation des alertes et détection des conditions.

OBJECTIF:
Créer service AlertService avec:
- Évaluation alertes configurées
- Détection conditions rupture stock
- Détection conditions stock faible
- Détection baisse taux service
- Création historique déclenchements
- Déduplication alertes (ne pas répéter si déjà envoyée récemment)

SPÉCIFICATIONS TECHNIQUES:

SERVICE ALERTING (app/services/alert_service.py):
```python
from sqlalchemy.orm import Session
from sqlalchemy import text, and_
from uuid import UUID
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

from app.models.alert import Alert
from app.models.alert_history import AlertHistory
from app.models.product import Product

logger = logging.getLogger(__name__)

class AlertService:
    def __init__(self, db: Session):
        self.db = db
    
    def evaluate_all_alerts(self, tenant_id: UUID) -> List[Dict[str, Any]]:
        """
        Évaluer toutes les alertes actives d'un tenant
        Retourne liste des alertes déclenchées
        """
        alerts = self.db.query(Alert).filter(
            and_(
                Alert.tenant_id == tenant_id,
                Alert.is_active == True
            )
        ).all()
        
        triggered_alerts = []
        
        for alert in alerts:
            if alert.alert_type == "RUPTURE_STOCK":
                result = self._evaluate_rupture_stock(alert)
            elif alert.alert_type == "LOW_STOCK":
                result = self._evaluate_low_stock(alert)
            elif alert.alert_type == "BAISSE_TAUX_SERVICE":
                result = self._evaluate_taux_service(alert)
            else:
                logger.warning(f"Unknown alert type: {alert.alert_type}")
                continue
            
            if result["triggered"]:
                # Vérifier déduplication (pas d'alerte similaire dernières 2h)
                if not self._is_duplicate(alert.id, result["products"]):
                    triggered_alerts.append({
                        "alert": alert,
                        "result": result
                    })
        
        return triggered_alerts
    
    def _evaluate_rupture_stock(self, alert: Alert) -> Dict[str, Any]:
        """Évaluer condition rupture stock"""
        conditions = alert.conditions
        
        # Query produits en rupture
        query = self.db.query(Product).filter(
            and_(
                Product.tenant_id == alert.tenant_id,
                Product.current_stock == 0,
                Product.is_active == True
            )
        )
        
        # Filtres optionnels
        if conditions.get("product_ids"):
            query = query.filter(Product.id.in_(conditions["product_ids"]))
        
        if conditions.get("category_ids"):
            query = query.filter(Product.category_id.in_(conditions["category_ids"]))
        
        products = query.all()
        
        if not products:
            return {"triggered": False, "products": []}
        
        # Construire message
        product_names = [p.name for p in products[:5]]
        message = f"🚨 RUPTURE STOCK - {len(products)} produit(s) en rupture"
        if len(products) <= 5:
            message += f": {', '.join(product_names)}"
        else:
            message += f": {', '.join(product_names)} et {len(products) - 5} autre(s)"
        
        return {
            "triggered": True,
            "products": [str(p.id) for p in products],
            "message": message,
            "severity": "CRITICAL" if len(products) > 10 else "HIGH",
            "details": {
                "product_count": len(products),
                "product_names": product_names
            }
        }
    
    def _evaluate_low_stock(self, alert: Alert) -> Dict[str, Any]:
        """Évaluer condition stock faible"""
        conditions = alert.conditions
        
        # Query produits stock faible
        query = self.db.query(Product).filter(
            and_(
                Product.tenant_id == alert.tenant_id,
                Product.current_stock > 0,
                Product.current_stock <= Product.min_stock,
                Product.is_active == True
            )
        )
        
        # Filtres optionnels
        if conditions.get("product_ids"):
            query = query.filter(Product.id.in_(conditions["product_ids"]))
        
        if conditions.get("category_ids"):
            query = query.filter(Product.category_id.in_(conditions["category_ids"]))
        
        products = query.all()
        
        if not products:
            return {"triggered": False, "products": []}
        
        # Construire message
        product_names = [p.name for p in products[:5]]
        message = f"⚠️  STOCK FAIBLE - {len(products)} produit(s) sous le seuil minimum"
        if len(products) <= 5:
            message += f": {', '.join(product_names)}"
        else:
            message += f": {', '.join(product_names)} et {len(products) - 5} autre(s)"
        
        return {
            "triggered": True,
            "products": [str(p.id) for p in products],
            "message": message,
            "severity": "MEDIUM" if len(products) < 5 else "HIGH",
            "details": {
                "product_count": len(products),
                "product_names": product_names
            }
        }
    
    def _evaluate_taux_service(self, alert: Alert) -> Dict[str, Any]:
        """Évaluer taux de service"""
        conditions = alert.conditions
        threshold = conditions.get("threshold", 90)  # Seuil par défaut 90%
        
        # Calculer taux service 7 derniers jours
        query = text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'DELIVERED' THEN 1 END) as delivered
            FROM sales
            WHERE tenant_id = :tenant_id
                AND sale_date >= CURRENT_DATE - INTERVAL '7 days'
        """)
        
        result = self.db.execute(query, {"tenant_id": alert.tenant_id}).first()
        
        if not result or result.total == 0:
            return {"triggered": False, "products": []}
        
        taux_service = (result.delivered / result.total) * 100
        
        if taux_service >= threshold:
            return {"triggered": False, "products": []}
        
        message = f"📉 TAUX SERVICE FAIBLE - {taux_service:.1f}% (seuil: {threshold}%)"
        
        return {
            "triggered": True,
            "products": [],
            "message": message,
            "severity": "MEDIUM" if taux_service > threshold - 10 else "HIGH",
            "details": {
                "taux_service": round(taux_service, 2),
                "threshold": threshold,
                "total_orders": result.total,
                "delivered_orders": result.delivered
            }
        }
    
    def _is_duplicate(self, alert_id: UUID, product_ids: List[str]) -> bool:
        """
        Vérifier si alerte similaire envoyée récemment
        Déduplication: même alerte + mêmes produits dernières 2h
        """
        two_hours_ago = datetime.utcnow() - timedelta(hours=2)
        
        recent = self.db.query(AlertHistory).filter(
            and_(
                AlertHistory.alert_id == alert_id,
                AlertHistory.triggered_at >= two_hours_ago
            )
        ).first()
        
        if not recent:
            return False
        
        # Comparer produits
        recent_products = set(recent.details.get("product_ids", []))
        current_products = set(product_ids)
        
        # Si 80%+ des produits identiques, considérer comme duplicate
        if len(recent_products) > 0:
            overlap = len(recent_products & current_products)
            similarity = overlap / len(recent_products)
            return similarity > 0.8
        
        return False
    
    def create_history_entry(
        self,
        alert: Alert,
        result: Dict[str, Any]
    ) -> AlertHistory:
        """Créer entrée historique"""
        history = AlertHistory(
            tenant_id=alert.tenant_id,
            alert_id=alert.id,
            triggered_at=datetime.utcnow(),
            alert_type=alert.alert_type,
            severity=result["severity"],
            message=result["message"],
            details=result["details"]
        )
        
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        
        return history
```

VUES SQL ALERTES (Migration Alembic):
```sql
-- Vue: Produits en rupture par tenant
CREATE VIEW v_alert_rupture_stock AS
SELECT 
    p.tenant_id,
    p.id as product_id,
    p.code,
    p.name,
    p.current_stock,
    p.min_stock,
    c.name as category_name
FROM products p
LEFT JOIN categories c ON p.category_id = c.id
WHERE p.current_stock = 0
    AND p.is_active = TRUE;

-- Vue: Produits stock faible par tenant
CREATE VIEW v_alert_stock_faible AS
SELECT 
    p.tenant_id,
    p.id as product_id,
    p.code,
    p.name,
    p.current_stock,
    p.min_stock,
    (p.min_stock - p.current_stock) as deficit,
    c.name as category_name
FROM products p
LEFT JOIN categories c ON p.category_id = c.id
WHERE p.current_stock > 0
    AND p.current_stock <= p.min_stock
    AND p.is_active = TRUE;
```

CRITÈRES D'ACCEPTATION:
✅ Service AlertService implémenté
✅ Méthode evaluate_all_alerts fonctionne
✅ Détection rupture stock opérationnelle
✅ Détection stock faible opérationnelle
✅ Détection baisse taux service opérationnelle
✅ Déduplication alertes (pas de spam)
✅ Création historique automatique
✅ Vues SQL créées
✅ Tests unitaires évaluation alertes
✅ Logs appropriés pour debug

COMMANDES DE TEST:
```python
# Script test (scripts/test_alerts.py)
from app.db.session import SessionLocal
from app.services.alert_service import AlertService
from app.models.alert import Alert
from uuid import UUID

db = SessionLocal()

# Créer alerte test
alert = Alert(
    tenant_id=UUID("..."),
    name="Test Rupture",
    alert_type="RUPTURE_STOCK",
    conditions={},
    channels={"whatsapp": True},
    recipients={"whatsapp_numbers": ["+221771234567"]}
)
db.add(alert)
db.commit()

# Évaluer
service = AlertService(db)
triggered = service.evaluate_all_alerts(alert.tenant_id)
print(f"Alertes déclenchées: {len(triggered)}")
```
```

---

### 🔧 PROMPT 2.3 : Intégration WhatsApp Business API

```
CONTEXTE:
Le service d'évaluation alertes est fonctionnel. Je dois maintenant intégrer WhatsApp Business API pour envoyer les notifications.

OBJECTIF:
Créer intégration WhatsApp avec:
- Service WhatsAppService
- Envoi messages texte
- Templates de messages formatés
- Gestion erreurs et retry
- Configuration credentials
- Tests avec numéros sandbox

SPÉCIFICATIONS TECHNIQUES:

CONFIGURATION (app/config.py):
Ajouter variables:
```python
# WhatsApp Business API
WHATSAPP_API_URL: str = "https://graph.facebook.com/v18.0"
WHATSAPP_API_TOKEN: str  # Token d'accès
WHATSAPP_PHONE_NUMBER_ID: str  # ID numéro WhatsApp Business
WHATSAPP_ENABLED: bool = True
```

SERVICE WHATSAPP (app/integrations/whatsapp.py):
```python
import httpx
import logging
from typing import List, Dict, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Service envoi messages WhatsApp Business API"""
    
    def __init__(self):
        self.api_url = settings.WHATSAPP_API_URL
        self.api_token = settings.WHATSAPP_API_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.enabled = settings.WHATSAPP_ENABLED
    
    async def send_alert(
        self,
        recipient: str,
        message: str
    ) -> bool:
        """
        Envoyer alerte WhatsApp
        
        Args:
            recipient: Numéro téléphone format international (+221771234567)
            message: Contenu message (max 4096 caractères)
        
        Returns:
            bool: Succès/échec envoi
        """
        if not self.enabled:
            logger.info(f"WhatsApp disabled, skipping send to {recipient}")
            return False
        
        # Nettoyer numéro (enlever espaces, tirets)
        recipient_clean = recipient.replace(" ", "").replace("-", "")
        
        # Valider format
        if not recipient_clean.startswith("+"):
            logger.error(f"Invalid WhatsApp number format: {recipient}")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_clean,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }
        
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                
                logger.info(f"WhatsApp sent successfully to {recipient_clean}")
                return True
                
        except httpx.HTTPStatusError as e:
            logger.error(f"WhatsApp API error {e.response.status_code}: {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"WhatsApp send failed: {str(e)}")
            return False
    
    async def send_bulk_alerts(
        self,
        recipients: List[str],
        message: str
    ) -> Dict[str, List[str]]:
        """
        Envoi groupé avec rapport succès/échec
        
        Returns:
            {"success": [...], "failed": [...]}
        """
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

# Instance singleton
whatsapp_service = WhatsAppService()
```

TEMPLATES MESSAGES (app/integrations/whatsapp_templates.py):
```python
from typing import Dict, Any

def format_rupture_stock_message(data: Dict[str, Any]) -> str:
    """Formatter message rupture stock"""
    product_names = data.get("product_names", [])
    product_count = data.get("product_count", 0)
    
    message = f"""🚨 *ALERTE RUPTURE STOCK*

Nombre de produits en rupture: *{product_count}*

Produits concernés:
"""
    for name in product_names[:5]:
        message += f"  • {name}\n"
    
    if product_count > 5:
        message += f"  ... et {product_count - 5} autre(s)\n"
    
    message += """
⚠️  Action requise: Commander ces produits rapidement

_Digiboost PME - Intelligence Supply Chain_"""
    
    return message

def format_low_stock_message(data: Dict[str, Any]) -> str:
    """Formatter message stock faible"""
    product_names = data.get("product_names", [])
    product_count = data.get("product_count", 0)
    
    message = f"""⚠️  *ALERTE STOCK FAIBLE*

Nombre de produits sous le seuil: *{product_count}*

Produits à réapprovisionner:
"""
    for name in product_names[:5]:
        message += f"  • {name}\n"
    
    if product_count > 5:
        message += f"  ... et {product_count - 5} autre(s)\n"
    
    message += """
📦 Suggestion: Passer commande avant rupture

_Digiboost PME_"""
    
    return message

def format_taux_service_message(data: Dict[str, Any]) -> str:
    """Formatter message baisse taux service"""
    taux = data.get("taux_service", 0)
    threshold = data.get("threshold", 90)
    
    message = f"""📉 *ALERTE PERFORMANCE*

Taux de service actuel: *{taux:.1f}%*
Objectif: {threshold}%

Sur 7 derniers jours:
  • Total commandes: {data.get('total_orders', 0)}
  • Livrées: {data.get('delivered_orders', 0)}

⚠️  Performance en baisse, vérifier les causes

_Digiboost PME_"""
    
    return message

def format_alert_message(alert_type: str, data: Dict[str, Any]) -> str:
    """Formatter message selon type alerte"""
    if alert_type == "RUPTURE_STOCK":
        return format_rupture_stock_message(data)
    elif alert_type == "LOW_STOCK":
        return format_low_stock_message(data)
    elif alert_type == "BAISSE_TAUX_SERVICE":
        return format_taux_service_message(data)
    else:
        return f"⚠️  Alerte: {data.get('message', 'Notification')}"
```

MISE À JOUR SERVICE ALERT:
Ajouter méthode pour envoyer notifications:
```python
async def send_alert_notifications(
    self,
    alert: Alert,
    result: Dict[str, Any],
    history: AlertHistory
) -> None:
    """Envoyer notifications selon canaux configurés"""
    channels = alert.channels
    recipients = alert.recipients
    
    # Formatter message
    from app.integrations.whatsapp_templates import format_alert_message
    message = format_alert_message(alert.alert_type, result["details"])
    
    # WhatsApp
    if channels.get("whatsapp") and recipients.get("whatsapp_numbers"):
        from app.integrations.whatsapp import whatsapp_service
        
        numbers = recipients["whatsapp_numbers"]
        results = await whatsapp_service.send_bulk_alerts(numbers, message)
        
        # Mettre à jour historique
        if results["success"]:
            history.sent_whatsapp = True
            self.db.commit()
        
        logger.info(f"WhatsApp sent: {len(results['success'])}/{len(numbers)}")
    
    # Email (à implémenter Sprint 4)
    if channels.get("email") and recipients.get("emails"):
        logger.info("Email notifications not implemented yet")
```

CRITÈRES D'ACCEPTATION:
✅ Service WhatsAppService créé
✅ Méthode send_alert fonctionne
✅ Templates messages formatés
✅ Envoi bulk avec rapport succès/échec
✅ Gestion erreurs HTTP et timeout
✅ Logs détaillés pour debug
✅ Variables env configurées (.env.example)
✅ Tests avec numéro sandbox WhatsApp
✅ Message reçu sur WhatsApp dans <2 min
✅ Historique updated (sent_whatsapp=True)

CONFIGURATION WHATSAPP BUSINESS:
1. Créer compte Meta Business
2. Configurer WhatsApp Business API
3. Obtenir Phone Number ID
4. Générer Access Token (permanent)
5. Configurer webhook (optionnel)
6. Tester avec numéro sandbox

COMMANDES DE TEST:
```python
# Test direct
import asyncio
from app.integrations.whatsapp import whatsapp_service

async def test():
    result = await whatsapp_service.send_alert(
        "+221771234567",  # Remplacer par votre numéro
        "🚨 Test alerte Digiboost PME"
    )
    print(f"Envoi: {'Succès' if result else 'Échec'}")

asyncio.run(test())
```
```

---

### 🔧 PROMPT 2.4 : Tâches Celery Périodiques

```
CONTEXTE:
L'intégration WhatsApp est fonctionnelle. Je dois maintenant configurer Celery pour l'évaluation périodique automatique des alertes (toutes les 5 minutes).

OBJECTIF:
Configurer Celery avec:
- Worker pour tâches asynchrones
- Beat scheduler pour tâches périodiques
- Tâche évaluation alertes (5 min)
- Tâche rafraîchissement vues matérialisées (10 min)
- Monitoring tâches

SPÉCIFICATIONS TECHNIQUES:

CONFIGURATION CELERY (app/tasks/celery_app.py):
```python
from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    "digiboost",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Africa/Dakar',  # Timezone Sénégal
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max par tâche
    task_soft_time_limit=240,  # Warning à 4 minutes
)

# Configuration Beat (tâches périodiques)
celery_app.conf.beat_schedule = {
    'evaluate-alerts-every-5-minutes': {
        'task': 'app.tasks.alert_tasks.evaluate_all_tenants_alerts',
        'schedule': 300.0,  # 5 minutes (en secondes)
        'options': {'queue': 'alerts'}
    },
    'refresh-materialized-views-every-10-minutes': {
        'task': 'app.tasks.dashboard_tasks.refresh_dashboard_views',
        'schedule': 600.0,  # 10 minutes
        'options': {'queue': 'maintenance'}
    },
}

# Auto-découvrir tâches dans modules
celery_app.autodiscover_tasks(['app.tasks'])
```

TÂCHE ÉVALUATION ALERTES (app/tasks/alert_tasks.py):
```python
import asyncio
import logging
from celery import shared_task
from sqlalchemy import distinct
from app.db.session import SessionLocal
from app.models.tenant import Tenant
from app.services.alert_service import AlertService

logger = logging.getLogger(__name__)

@shared_task(name='app.tasks.alert_tasks.evaluate_all_tenants_alerts')
def evaluate_all_tenants_alerts():
    """
    Tâche périodique: évaluer alertes de tous les tenants actifs
    Exécutée toutes les 5 minutes par Celery Beat
    """
    logger.info("Starting alert evaluation for all tenants")
    
    db = SessionLocal()
    try:
        # Récupérer tous les tenants actifs
        tenants = db.query(Tenant).filter(Tenant.is_active == True).all()
        
        total_triggered = 0
        total_sent = 0
        
        for tenant in tenants:
            try:
                result = asyncio.run(_evaluate_tenant_alerts(tenant.id, db))
                total_triggered += result["triggered"]
                total_sent += result["sent"]
                
            except Exception as e:
                logger.error(f"Error evaluating alerts for tenant {tenant.id}: {str(e)}")
                continue
        
        logger.info(f"Alert evaluation completed: {total_triggered} triggered, {total_sent} sent")
        
        return {
            "tenants_processed": len(tenants),
            "alerts_triggered": total_triggered,
            "notifications_sent": total_sent
        }
        
    finally:
        db.close()

async def _evaluate_tenant_alerts(tenant_id, db):
    """Évaluer alertes d'un tenant et envoyer notifications"""
    service = AlertService(db)
    
    # Évaluer alertes
    triggered_alerts = service.evaluate_all_alerts(tenant_id)
    
    notifications_sent = 0
    
    for item in triggered_alerts:
        alert = item["alert"]
        result = item["result"]
        
        # Créer historique
        history = service.create_history_entry(alert, result)
        
        # Envoyer notifications
        try:
            await service.send_alert_notifications(alert, result, history)
            notifications_sent += 1
        except Exception as e:
            logger.error(f"Failed to send notification for alert {alert.id}: {str(e)}")
    
    return {
        "triggered": len(triggered_alerts),
        "sent": notifications_sent
    }

@shared_task(name='app.tasks.alert_tasks.test_whatsapp_connection')
def test_whatsapp_connection():
    """Tâche test: vérifier connexion WhatsApp"""
    from app.integrations.whatsapp import whatsapp_service
    
    # Test avec numéro configuré dans settings
    test_number = "+221771234567"  # À configurer
    message = "🧪 Test connexion WhatsApp - Digiboost PME"
    
    result = asyncio.run(whatsapp_service.send_alert(test_number, message))
    
    return {"success": result}
```

TÂCHE MAINTENANCE VUES (app/tasks/dashboard_tasks.py):
```python
from celery import shared_task
from sqlalchemy import text
from app.db.session import SessionLocal
import logging

logger = logging.getLogger(__name__)

@shared_task(name='app.tasks.dashboard_tasks.refresh_dashboard_views')
def refresh_dashboard_views():
    """
    Rafraîchir vues matérialisées des dashboards
    Exécutée toutes les 10 minutes
    """
    logger.info("Refreshing materialized views")
    
    db = SessionLocal()
    try:
        # Rafraîchir vues matérialisées
        views = [
            'mv_dashboard_stock_health',
            'mv_dashboard_sales_performance'
        ]
        
        for view in views:
            try:
                db.execute(text(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view}"))
                logger.info(f"Refreshed view: {view}")
            except Exception as e:
                logger.error(f"Failed to refresh {view}: {str(e)}")
        
        db.commit()
        
        return {"views_refreshed": len(views)}
        
    finally:
        db.close()
```

DOCKER COMPOSE - AJOUT CELERY (docker-compose.yml):
```yaml
services:
  # ... postgres, redis existants ...
  
  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A app.tasks.celery_app worker --loglevel=info --concurrency=2
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/digiboost_dev
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - WHATSAPP_API_TOKEN=${WHATSAPP_API_TOKEN}
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
  
  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A app.tasks.celery_app beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/digiboost_dev
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
```

MONITORING CELERY:
Ajouter Flower (interface web Celery):
```yaml
  flower:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A app.tasks.celery_app flower --port=5555
    ports:
      - "5555:5555"
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
      - celery-worker
```

CRITÈRES D'ACCEPTATION:
✅ Celery configuré avec Redis
✅ Worker démarre sans erreur
✅ Beat scheduler démarre
✅ Tâche evaluate_all_tenants_alerts s'exécute toutes les 5 min
✅ Tâche refresh_dashboard_views s'exécute toutes les 10 min
✅ Alertes déclenchées automatiquement
✅ WhatsApp envoyé automatiquement
✅ Logs Celery dans console
✅ Flower accessible sur http://localhost:5555
✅ Monitoring tâches dans Flower

COMMANDES DE TEST:
```bash
# Démarrer services
docker-compose up -d

# Logs Celery Worker
docker-compose logs -f celery-worker

# Logs Celery Beat
docker-compose logs -f celery-beat

# Exécuter tâche manuellement (debug)
docker-compose exec celery-worker celery -A app.tasks.celery_app call app.tasks.alert_tasks.evaluate_all_tenants_alerts

# Vérifier tâches programmées
docker-compose exec celery-worker celery -A app.tasks.celery_app inspect scheduled

# Flower UI
open http://localhost:5555
```
```

---

## SEMAINE 4 : FRONTEND ALERTING

### 🔧 PROMPT 2.5 : API Endpoints Alertes

```
CONTEXTE:
Les tâches Celery d'évaluation sont fonctionnelles. Je dois maintenant créer les endpoints API REST pour gérer les alertes depuis le frontend.

OBJECTIF:
Créer endpoints API CRUD pour:
- Lister alertes configurées
- Créer nouvelle alerte
- Modifier alerte existante
- Supprimer alerte
- Activer/désactiver alerte
- Consulter historique alertes

SPÉCIFICATIONS TECHNIQUES:

ROUTER ALERTS (app/api/v1/alerts.py):
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.alert import Alert
from app.models.alert_history import AlertHistory
from app.schemas.alert import (
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    AlertHistoryResponse
)

router = APIRouter()

@router.get("/", response_model=List[AlertResponse])
def list_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Liste toutes les alertes du tenant"""
    alerts = db.query(Alert).filter(
        Alert.tenant_id == current_user.tenant_id
    ).order_by(Alert.created_at.desc()).all()
    
    return alerts

@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_alert(
    alert: AlertCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Créer nouvelle alerte"""
    
    # Valider type alerte
    valid_types = ["RUPTURE_STOCK", "LOW_STOCK", "BAISSE_TAUX_SERVICE"]
    if alert.alert_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid alert_type. Must be one of: {valid_types}"
        )
    
    # Valider recipients
    if not alert.recipients.get("whatsapp_numbers") and not alert.recipients.get("emails"):
        raise HTTPException(
            status_code=400,
            detail="At least one recipient (whatsapp or email) is required"
        )
    
    db_alert = Alert(
        tenant_id=current_user.tenant_id,
        **alert.model_dump()
    )
    
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    return db_alert

@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupérer alerte par ID"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.tenant_id == current_user.tenant_id
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return alert

@router.put("/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: UUID,
    alert_update: AlertUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Modifier alerte existante"""
    db_alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.tenant_id == current_user.tenant_id
    ).first()
    
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Appliquer modifications
    update_data = alert_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_alert, key, value)
    
    db.commit()
    db.refresh(db_alert)
    
    return db_alert

@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(
    alert_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Supprimer alerte"""
    db_alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.tenant_id == current_user.tenant_id
    ).first()
    
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    db.delete(db_alert)
    db.commit()
    
    return None

@router.patch("/{alert_id}/toggle", response_model=AlertResponse)
def toggle_alert(
    alert_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Activer/désactiver alerte"""
    db_alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.tenant_id == current_user.tenant_id
    ).first()
    
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    db_alert.is_active = not db_alert.is_active
    db.commit()
    db.refresh(db_alert)
    
    return db_alert

@router.get("/history/", response_model=List[AlertHistoryResponse])
def get_alert_history(
    alert_id: UUID = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Consulter historique alertes
    Optionnel: filtrer par alert_id spécifique
    """
    query = db.query(AlertHistory).filter(
        AlertHistory.tenant_id == current_user.tenant_id
    )
    
    if alert_id:
        query = query.filter(AlertHistory.alert_id == alert_id)
    
    history = query.order_by(
        AlertHistory.triggered_at.desc()
    ).limit(limit).all()
    
    return history
```

ENREGISTRER ROUTER (app/main.py):
```python
from app.api.v1 import alerts

app.include_router(
    alerts.router,
    prefix=f"{settings.API_V1_PREFIX}/alerts",
    tags=["alerts"]
)
```

CRITÈRES D'ACCEPTATION:
✅ Tous les endpoints créés
✅ Liste alertes retourne JSON
✅ Création alerte fonctionne
✅ Modification alerte fonctionne
✅ Suppression alerte fonctionne
✅ Toggle activation/désactivation
✅ Historique alertes accessible
✅ Filtrage tenant_id automatique
✅ Validation données (Pydantic)
✅ Codes HTTP appropriés (201, 204, 404)
✅ Documentation Swagger /docs

COMMANDES DE TEST:
```bash
# Liste alertes
curl http://localhost:8000/api/v1/alerts \
  -H "Authorization: Bearer <token>"

# Créer alerte
curl -X POST http://localhost:8000/api/v1/alerts \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rupture riz",
    "alert_type": "RUPTURE_STOCK",
    "conditions": {},
    "channels": {"whatsapp": true},
    "recipients": {"whatsapp_numbers": ["+221771234567"]}
  }'

# Historique
curl http://localhost:8000/api/v1/alerts/history/ \
  -H "Authorization: Bearer <token>"
```
```

---

### 🔧 PROMPT 2.6 : Frontend - Gestion Alertes UI

```
CONTEXTE:
Les endpoints API alertes sont fonctionnels. Je dois créer l'interface frontend pour gérer les alertes : liste, création, modification, activation/désactivation.

OBJECTIF:
Créer pages frontend:
- Liste alertes configurées (table)
- Formulaire création/modification alerte
- Toggle activation rapide
- Suppression alerte (avec confirmation)
- Filtres et recherche

SPÉCIFICATIONS TECHNIQUES:

API CLIENT (src/api/alerts.ts):
```typescript
import { apiClient } from './client';

export interface Alert {
  id: string;
  name: string;
  alert_type: string;
  conditions: Record<string, any>;
  channels: {
    whatsapp: boolean;
    email: boolean;
  };
  recipients: {
    whatsapp_numbers: string[];
    emails: string[];
  };
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export const alertsApi = {
  list: async (): Promise<Alert[]> => {
    const { data } = await apiClient.get('/alerts/');
    return data;
  },

  create: async (alert: Omit<Alert, 'id' | 'created_at' | 'updated_at'>): Promise<Alert> => {
    const { data } = await apiClient.post('/alerts/', alert);
    return data;
  },

  update: async (id: string, alert: Partial<Alert>): Promise<Alert> => {
    const { data } = await apiClient.put(`/alerts/${id}`, alert);
    return data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/alerts/${id}`);
  },

  toggle: async (id: string): Promise<Alert> => {
    const { data } = await apiClient.patch(`/alerts/${id}/toggle`);
    return data;
  },
};
```

HOOK ALERTS (src/features/alerts/hooks/useAlerts.ts):
```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { alertsApi, Alert } from '@/api/alerts';
import { toast } from 'sonner';

export const useAlerts = () => {
  const queryClient = useQueryClient();

  const { data: alerts, isLoading, error } = useQuery({
    queryKey: ['alerts'],
    queryFn: alertsApi.list,
  });

  const createMutation = useMutation({
    mutationFn: alertsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      toast.success('Alerte créée avec succès');
    },
    onError: () => {
      toast.error('Erreur lors de la création');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Alert> }) =>
      alertsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      toast.success('Alerte modifiée');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: alertsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      toast.success('Alerte supprimée');
    },
  });

  const toggleMutation = useMutation({
    mutationFn: alertsApi.toggle,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
  });

  return {
    alerts,
    isLoading,
    error,
    createAlert: createMutation.mutate,
    updateAlert: updateMutation.mutate,
    deleteAlert: deleteMutation.mutate,
    toggleAlert: toggleMutation.mutate,
  };
};
```

PAGE LISTE ALERTES (src/features/alerts/components/AlertsList.tsx):
```typescript
import { useState } from 'react';
import { useAlerts } from '../hooks/useAlerts';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Plus, Trash2, Edit, Bell, BellOff } from 'lucide-react';
import { AlertConfigDialog } from './AlertConfigDialog';

export const AlertsList = () => {
  const { alerts, isLoading, deleteAlert, toggleAlert } = useAlerts();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingAlert, setEditingAlert] = useState<Alert | null>(null);

  const getAlertTypeLabel = (type: string) => {
    const labels = {
      RUPTURE_STOCK: 'Rupture Stock',
      LOW_STOCK: 'Stock Faible',
      BAISSE_TAUX_SERVICE: 'Baisse Taux Service',
    };
    return labels[type] || type;
  };

  const getAlertTypeBadge = (type: string) => {
    const colors = {
      RUPTURE_STOCK: 'bg-red-100 text-red-800',
      LOW_STOCK: 'bg-amber-100 text-amber-800',
      BAISSE_TAUX_SERVICE: 'bg-blue-100 text-blue-800',
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  if (isLoading) return <div>Chargement...</div>;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Gestion des Alertes</h1>
          <p className="text-gray-600 mt-1">
            Configurez vos alertes pour être notifié en temps réel
          </p>
        </div>
        <Button onClick={() => setIsDialogOpen(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Nouvelle Alerte
        </Button>
      </div>

      {/* Stats rapides */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Alertes</p>
              <p className="text-2xl font-bold">{alerts?.length || 0}</p>
            </div>
            <Bell className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Alertes Actives</p>
              <p className="text-2xl font-bold text-green-600">
                {alerts?.filter((a) => a.is_active).length || 0}
              </p>
            </div>
            <Bell className="w-8 h-8 text-green-500" />
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Alertes Inactives</p>
              <p className="text-2xl font-bold text-gray-400">
                {alerts?.filter((a) => !a.is_active).length || 0}
              </p>
            </div>
            <BellOff className="w-8 h-8 text-gray-400" />
          </div>
        </div>
      </div>

      {/* Table alertes */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Nom
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Canaux
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Destinataires
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Statut
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {alerts?.map((alert) => (
              <tr key={alert.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div className="font-medium text-gray-900">{alert.name}</div>
                </td>
                <td className="px-6 py-4">
                  <Badge className={getAlertTypeBadge(alert.alert_type)}>
                    {getAlertTypeLabel(alert.alert_type)}
                  </Badge>
                </td>
                <td className="px-6 py-4">
                  <div className="flex gap-2">
                    {alert.channels.whatsapp && (
                      <Badge variant="outline">WhatsApp</Badge>
                    )}
                    {alert.channels.email && (
                      <Badge variant="outline">Email</Badge>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {alert.recipients.whatsapp_numbers?.length || 0} WhatsApp,{' '}
                  {alert.recipients.emails?.length || 0} Email
                </td>
                <td className="px-6 py-4">
                  <Switch
                    checked={alert.is_active}
                    onCheckedChange={() => toggleAlert(alert.id)}
                  />
                </td>
                <td className="px-6 py-4 text-right space-x-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setEditingAlert(alert);
                      setIsDialogOpen(true);
                    }}
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      if (confirm('Supprimer cette alerte ?')) {
                        deleteAlert(alert.id);
                      }
                    }}
                  >
                    <Trash2 className="w-4 h-4 text-red-600" />
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Dialog création/modification */}
      <AlertConfigDialog
        open={isDialogOpen}
        onOpenChange={setIsDialogOpen}
        alert={editingAlert}
      />
    </div>
  );
};
```

DIALOG CONFIGURATION (src/features/alerts/components/AlertConfigDialog.tsx):
```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { useAlerts } from '../hooks/useAlerts';

const alertSchema = z.object({
  name: z.string().min(3, 'Minimum 3 caractères'),
  alert_type: z.enum(['RUPTURE_STOCK', 'LOW_STOCK', 'BAISSE_TAUX_SERVICE']),
  channels: z.object({
    whatsapp: z.boolean(),
    email: z.boolean(),
  }),
  recipients: z.object({
    whatsapp_numbers: z.array(z.string()).optional(),
    emails: z.array(z.string().email()).optional(),
  }),
  conditions: z.record(z.any()).optional(),
});

export const AlertConfigDialog = ({ open, onOpenChange, alert }) => {
  const { createAlert, updateAlert } = useAlerts();
  const isEditing = !!alert;

  const form = useForm({
    resolver: zodResolver(alertSchema),
    defaultValues: alert || {
      name: '',
      alert_type: 'RUPTURE_STOCK',
      channels: { whatsapp: true, email: false },
      recipients: { whatsapp_numbers: [], emails: [] },
      conditions: {},
    },
  });

  const onSubmit = (data) => {
    if (isEditing) {
      updateAlert({ id: alert.id, data });
    } else {
      createAlert(data);
    }
    onOpenChange(false);
    form.reset();
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>
            {isEditing ? 'Modifier' : 'Créer'} une Alerte
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          {/* Nom */}
          <div>
            <Label>Nom de l'alerte</Label>
            <Input {...form.register('name')} placeholder="Ex: Rupture produits prioritaires" />
            {form.formState.errors.name && (
              <p className="text-sm text-red-600 mt-1">
                {form.formState.errors.name.message}
              </p>
            )}
          </div>

          {/* Type */}
          <div>
            <Label>Type d'alerte</Label>
            <Select {...form.register('alert_type')}>
              <option value="RUPTURE_STOCK">Rupture Stock</option>
              <option value="LOW_STOCK">Stock Faible</option>
              <option value="BAISSE_TAUX_SERVICE">Baisse Taux Service</option>
            </Select>
          </div>

          {/* Canaux */}
          <div>
            <Label>Canaux de notification</Label>
            <div className="space-y-2 mt-2">
              <div className="flex items-center space-x-2">
                <Checkbox {...form.register('channels.whatsapp')} />
                <label>WhatsApp</label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox {...form.register('channels.email')} />
                <label>Email</label>
              </div>
            </div>
          </div>

          {/* Destinataires WhatsApp */}
          <div>
            <Label>Numéros WhatsApp</Label>
            <Input
              placeholder="+221771234567, +221765432109"
              onChange={(e) => {
                const numbers = e.target.value.split(',').map((n) => n.trim());
                form.setValue('recipients.whatsapp_numbers', numbers);
              }}
            />
            <p className="text-sm text-gray-500 mt-1">
              Séparer plusieurs numéros par des virgules
            </p>
          </div>

          {/* Boutons */}
          <div className="flex justify-end space-x-2">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Annuler
            </Button>
            <Button type="submit">
              {isEditing ? 'Modifier' : 'Créer'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};
```

CRITÈRES D'ACCEPTATION:
✅ Liste alertes affiche toutes les alertes
✅ Toggle activation fonctionne (Switch)
✅ Dialog création s'ouvre
✅ Formulaire validation fonctionne
✅ Création alerte appelle API
✅ Modification alerte fonctionne
✅ Suppression avec confirmation
✅ Toast notifications (succès/erreur)
✅ Design responsive mobile
✅ Stats alertes affichées (total, actives, inactives)

COMMANDES DE TEST:
```bash
npm run dev
# Login → /alerts
# Créer alerte
# Toggle activation
# Modifier alerte
# Supprimer alerte
```
```

---

### 🔧 PROMPT 2.7 : Frontend - Historique Alertes

```
CONTEXTE:
La gestion des alertes est fonctionnelle. Je dois créer la page d'historique pour consulter toutes les alertes déclenchées.

OBJECTIF:
Créer page historique avec:
- Liste déclenchements alertes
- Filtres (date, type, sévérité)
- Détails déclenchement
- Timeline visuelle
- Statistiques historique

SPÉCIFICATIONS TECHNIQUES:

API CLIENT (src/api/alerts.ts - ajouter):
```typescript
export interface AlertHistory {
  id: string;
  alert_id: string;
  triggered_at: string;
  alert_type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  message: string;
  details: Record<string, any>;
  sent_whatsapp: boolean;
  sent_email: boolean;
}

export const alertsApi = {
  // ... méthodes existantes ...

  getHistory: async (alertId?: string): Promise<AlertHistory[]> => {
    const params = alertId ? { alert_id: alertId } : {};
    const { data } = await apiClient.get('/alerts/history/', { params });
    return data;
  },
};
```

HOOK HISTORY (src/features/alerts/hooks/useAlertHistory.ts):
```typescript
import { useQuery } from '@tanstack/react-query';
import { alertsApi } from '@/api/alerts';

export const useAlertHistory = (alertId?: string) => {
  return useQuery({
    queryKey: ['alert-history', alertId],
    queryFn: () => alertsApi.getHistory(alertId),
    refetchInterval: 60 * 1000, // Rafraîchir chaque minute
  });
};
```

PAGE HISTORIQUE (src/features/alerts/components/AlertHistory.tsx):
```typescript
import { useState } from 'react';
import { useAlertHistory } from '../hooks/useAlertHistory';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Select } from '@/components/ui/select';
import { Bell, CheckCircle, XCircle, Clock } from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

export const AlertHistory = () => {
  const { data: history, isLoading } = useAlertHistory();
  const [filterType, setFilterType] = useState<string | null>(null);
  const [filterSeverity, setFilterSeverity] = useState<string | null>(null);

  const filteredHistory = history?.filter((item) => {
    if (filterType && item.alert_type !== filterType) return false;
    if (filterSeverity && item.severity !== filterSeverity) return false;
    return true;
  });

  const getSeverityColor = (severity: string) => {
    const colors = {
      LOW: 'bg-blue-100 text-blue-800',
      MEDIUM: 'bg-amber-100 text-amber-800',
      HIGH: 'bg-orange-100 text-orange-800',
      CRITICAL: 'bg-red-100 text-red-800',
    };
    return colors[severity] || 'bg-gray-100 text-gray-800';
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return '🚨';
      case 'HIGH':
        return '⚠️';
      case 'MEDIUM':
        return '⚡';
      default:
        return 'ℹ️';
    }
  };

  if (isLoading) return <div>Chargement...</div>;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Historique des Alertes</h1>
        <p className="text-gray-600 mt-1">
          Consultez l'historique de tous les déclenchements
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Déclenchements</p>
              <p className="text-2xl font-bold">{history?.length || 0}</p>
            </div>
            <Bell className="w-8 h-8 text-blue-500" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Envoyés WhatsApp</p>
              <p className="text-2xl font-bold text-green-600">
                {history?.filter((h) => h.sent_whatsapp).length || 0}
              </p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-500" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Alertes Critiques</p>
              <p className="text-2xl font-bold text-red-600">
                {history?.filter((h) => h.severity === 'CRITICAL').length || 0}
              </p>
            </div>
            <XCircle className="w-8 h-8 text-red-500" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Dernière Alerte</p>
              <p className="text-sm font-medium">
                {history?.[0]
                  ? format(new Date(history[0].triggered_at), 'HH:mm', { locale: fr })
                  : '-'}
              </p>
            </div>
            <Clock className="w-8 h-8 text-gray-400" />
          </div>
        </Card>
      </div>

      {/* Filtres */}
      <div className="flex gap-4">
        <Select
          value={filterType || ''}
          onChange={(e) => setFilterType(e.target.value || null)}
        >
          <option value="">Tous les types</option>
          <option value="RUPTURE_STOCK">Rupture Stock</option>
          <option value="LOW_STOCK">Stock Faible</option>
          <option value="BAISSE_TAUX_SERVICE">Baisse Taux Service</option>
        </Select>

        <Select
          value={filterSeverity || ''}
          onChange={(e) => setFilterSeverity(e.target.value || null)}
        >
          <option value="">Toutes sévérités</option>
          <option value="LOW">Faible</option>
          <option value="MEDIUM">Moyenne</option>
          <option value="HIGH">Élevée</option>
          <option value="CRITICAL">Critique</option>
        </Select>
      </div>

      {/* Timeline */}
      <div className="space-y-4">
        {filteredHistory?.map((item) => (
          <Card key={item.id} className="p-6">
            <div className="flex items-start gap-4">
              {/* Icône */}
              <div className="text-3xl">{getSeverityIcon(item.severity)}</div>

              {/* Contenu */}
              <div className="flex-1">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-lg">{item.message}</h3>
                    <p className="text-sm text-gray-600 mt-1">
                      {format(new Date(item.triggered_at), "dd MMM yyyy 'à' HH:mm", {
                        locale: fr,
                      })}
                    </p>
                  </div>
                  <Badge className={getSeverityColor(item.severity)}>
                    {item.severity}
                  </Badge>
                </div>

                {/* Détails */}
                {item.details && Object.keys(item.details).length > 0 && (
                  <div className="mt-4 bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm font-medium mb-2">Détails:</p>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      {item.details.product_count && (
                        <div>
                          <span className="text-gray-600">Produits affectés:</span>
                          <span className="font-medium ml-2">
                            {item.details.product_count}
                          </span>
                        </div>
                      )}
                      {item.details.taux_service && (
                        <div>
                          <span className="text-gray-600">Taux service:</span>
                          <span className="font-medium ml-2">
                            {item.details.taux_service}%
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Statut envoi */}
                <div className="flex gap-4 mt-4 text-sm">
                  <div className="flex items-center gap-2">
                    {item.sent_whatsapp ? (
                      <CheckCircle className="w-4 h-4 text-green-600" />
                    ) : (
                      <XCircle className="w-4 h-4 text-gray-400" />
                    )}
                    <span>WhatsApp</span>
                  </div>
                  <div className="flex items-center gap-2">
                    {item.sent_email ? (
                      <CheckCircle className="w-4 h-4 text-green-600" />
                    ) : (
                      <XCircle className="w-4 h-4 text-gray-400" />
                    )}
                    <span>Email</span>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Empty state */}
      {filteredHistory?.length === 0 && (
        <Card className="p-12 text-center">
          <Bell className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">Aucun historique</h3>
          <p className="text-gray-600">
            Aucune alerte n'a été déclenchée avec ces filtres
          </p>
        </Card>
      )}
    </div>
  );
};
```

ROUTE (src/routes/index.tsx - ajouter):
```typescript
<Route path="/alerts/history" element={<AlertHistory />} />
```

CRITÈRES D'ACCEPTATION:
✅ Historique affiche tous les déclenchements
✅ Stats historique calculées
✅ Filtres par type et sévérité fonctionnent
✅ Timeline visuelle claire
✅ Badges couleur selon sévérité
✅ Détails déclenchement affichés
✅ Statut envoi (WhatsApp/Email) visible
✅ Format date français
✅ Rafraîchissement automatique (1 min)
✅ Empty state si pas d'historique
✅ Design responsive mobile

COMMANDES DE TEST:
```bash
npm run dev
# Déclencher alertes (via backend)
# Vérifier historique s'affiche
# Tester filtres
# Vérifier rafraîchissement auto
```
```

---

## 🎯 RÉCAPITULATIF SPRINT 2

### Fonctionnalités Livrées

✅ **Backend Complet**
- Modèles Alert + AlertHistory
- Service évaluation alertes (3 types)
- Intégration WhatsApp Business API
- Tâches Celery périodiques (5 min)
- Endpoints API CRUD alertes

✅ **Frontend Complet**
- Page liste alertes (table interactive)
- Dialog création/modification
- Toggle activation rapide
- Page historique avec timeline
- Filtres et statistiques

✅ **Notifications**
- WhatsApp temps réel (<2 min)
- Messages formatés avec templates
- Déduplication intelligente
- Historique complet

### Tests de Validation Sprint 2

```bash
# 1. Backend
docker-compose logs -f celery-worker
# Vérifier tâche s'exécute toutes les 5 min

# 2. Créer alerte via API
curl -X POST http://localhost:8000/api/v1/alerts \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","alert_type":"RUPTURE_STOCK","conditions":{},"channels":{"whatsapp":true},"recipients":{"whatsapp_numbers":["+221771234567"]}}'

# 3. Simuler rupture stock
# Mettre current_stock = 0 sur un produit via psql

# 4. Attendre 5 min
# Vérifier WhatsApp reçu

# 5. Frontend
# Login → /alerts
# Créer alerte via UI
# Toggle activation
# Consulter historique
```

### Métriques Succès Sprint 2

- ✅ Alertes envoyées dans <2 min après déclenchement
- ✅ 0 doublon (déduplication fonctionne)
- ✅ 100% alertes critiques envoyées
- ✅ Interface responsive mobile
- ✅ Uptime Celery >99%

---

**FIN SPRINT 2**

Vous êtes prêt à passer au Sprint 3 (Analyses & Prédictions) !
