# INTÉGRATION WHATSAPP - GUIDE TECHNIQUE

## 📋 État actuel

**Version actuelle** : Twilio WhatsApp API (implémentation Sprint 2)
**Fichier** : `backend/app/integrations/whatsapp.py`
**Date** : Octobre 2025

### Configuration actuelle (Twilio)

```bash
# .env
TWILIO_ACCOUNT_SID=ACxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxx
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
WHATSAPP_ENABLED=True
```

### Architecture actuelle

```
AlertService
    ↓
send_alert_notifications()
    ↓
WhatsAppService (Twilio SDK)
    ↓ twilio.rest.Client
Twilio API → WhatsApp Business Platform → Destinataire
```

---

## 🔄 MIGRATION FUTURE : Meta WhatsApp Business API

### Pourquoi migrer ?

1. **Coût** : Meta gratuit jusqu'à 1000 conversations/mois, puis moins cher que Twilio
2. **Fonctionnalités** : Templates interactifs, boutons, quick replies
3. **Contrôle** : Numéro WhatsApp propre à l'entreprise
4. **Scalabilité** : Meilleure pour production avec gros volumes

### Quand migrer ?

- ✅ **Maintenant (Twilio)** : POC, développement, tests
- ⏳ **Dans 3-6 mois** : Passage en production, > 1000 conversations/mois
- 🚀 **Dans 1 an** : Fonctionnalités avancées (chatbot, templates interactifs)

---

## 📝 ÉTAPES DE MIGRATION VERS META WHATSAPP

### Prérequis (à faire en avance)

#### 1. Compte Meta Business (3-7 jours)
```
1. Créer compte Meta Business : https://business.facebook.com
2. Vérifier l'entreprise (documents requis) : ~3-5 jours
3. Ajouter méthode de paiement
```

#### 2. Application WhatsApp Business (1 jour)
```
1. Aller sur https://developers.facebook.com
2. Créer une nouvelle App
3. Ajouter produit "WhatsApp Business API"
4. Configurer profil entreprise (nom, description, logo)
```

#### 3. Numéro de téléphone (1 jour)
```
Options :
  A. Utiliser numéro existant (recommandé pour production)
  B. Acheter nouveau numéro (Twilio, Vonage, etc.)

⚠️  Le numéro ne peut être utilisé que pour WhatsApp Business API
⚠️  Ne plus utiliser le numéro sur WhatsApp mobile après migration
```

#### 4. Obtenir les credentials (30 min)
```
Dans Facebook Developers → Votre App → WhatsApp :

1. WHATSAPP_API_URL (fixe)
   https://graph.facebook.com/v18.0

2. WHATSAPP_API_TOKEN (Access Token)
   - Temporary token (24h) : Dans API Setup
   - Permanent token :
     a. Créer System User dans Business Settings
     b. Assigner permissions WhatsApp
     c. Générer token permanent

3. WHATSAPP_PHONE_NUMBER_ID
   - Dans "API Setup" → "Phone number ID"
   - Format : 123456789012345 (15 chiffres)
```

---

## 🔧 CHANGEMENTS DE CODE NÉCESSAIRES

### 1. Mise à jour `.env`

**Retirer (Twilio)** :
```bash
#TWILIO_ACCOUNT_SID=
#TWILIO_AUTH_TOKEN=
#TWILIO_WHATSAPP_FROM=
```

**Ajouter (Meta)** :
```bash
# WhatsApp Business API (Meta)
WHATSAPP_API_URL=https://graph.facebook.com/v18.0
WHATSAPP_API_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxxx
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_ENABLED=True
```

### 2. Mise à jour `app/config.py`

**Retirer** :
```python
# WhatsApp (Twilio)
TWILIO_ACCOUNT_SID: str = ""
TWILIO_AUTH_TOKEN: str = ""
TWILIO_WHATSAPP_FROM: str = "whatsapp:+14155238886"
```

**Ajouter** :
```python
# WhatsApp Business API (Meta)
WHATSAPP_API_URL: str = "https://graph.facebook.com/v18.0"
WHATSAPP_API_TOKEN: str = ""
WHATSAPP_PHONE_NUMBER_ID: str = ""
WHATSAPP_ENABLED: bool = True
```

### 3. Réécrire `app/integrations/whatsapp.py`

**Changements principaux** :

```python
"""
Service WhatsApp avec Meta WhatsApp Business API.
"""
import logging
from typing import Dict, List
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Service d'envoi de messages WhatsApp via Meta API."""

    def __init__(self):
        """Initialiser le client HTTP."""
        self.enabled = settings.WHATSAPP_ENABLED
        self.api_url = settings.WHATSAPP_API_URL
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.api_token = settings.WHATSAPP_API_TOKEN

        if self.enabled and self.api_token and self.phone_number_id:
            logger.info("WhatsApp service initialized with Meta API")
        else:
            logger.warning("WhatsApp service disabled (missing credentials)")
            self.enabled = False

    def send_alert(self, recipient: str, message: str) -> bool:
        """
        Envoyer une alerte WhatsApp à un destinataire.

        Args:
            recipient: Numéro au format international (+221771234567)
            message: Contenu du message (max 4096 caractères)

        Returns:
            bool: True si envoi réussi, False sinon
        """
        if not self.enabled:
            logger.info(f"WhatsApp disabled, skipping send to {recipient}")
            return False

        # Nettoyer le numéro (retirer + et espaces)
        recipient_clean = recipient.replace("+", "").replace(" ", "").replace("-", "")

        # Construire l'URL de l'API
        url = f"{self.api_url}/{self.phone_number_id}/messages"

        # Headers
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        # Payload
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

        try:
            # Limiter la taille (Meta max 4096)
            if len(message) > 4096:
                logger.warning(f"Message too long ({len(message)}), truncating")
                payload["text"]["body"] = message[:4093] + "..."

            # Envoyer via HTTP
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()

            data = response.json()
            message_id = data.get("messages", [{}])[0].get("id")

            logger.info(f"WhatsApp sent to {recipient} (ID: {message_id})")
            return True

        except httpx.HTTPStatusError as e:
            logger.error(f"Meta API error {e.response.status_code}: {e.response.text}")
            return False

        except Exception as e:
            logger.error(f"WhatsApp send failed: {str(e)}", exc_info=True)
            return False

    # send_bulk_alerts() reste identique
    # get_status() : changer provider = "Meta WhatsApp Business API"
```

**⚠️  IMPORTANT** : La méthode devient `async` avec Meta car on utilise `httpx` au lieu du SDK Twilio synchrone.

### 4. Mise à jour `AlertService.send_alert_notifications()`

**Changement mineur** :

```python
# Devient async
async def send_alert_notifications(...):
    ...
    if channels.get("whatsapp"):
        # Appel async
        results = await whatsapp_service.send_bulk_alerts(numbers, message)
```

### 5. Supprimer dépendance Twilio

**requirements.txt** :
```bash
# Retirer
twilio==9.0.4
```

**Garder** :
```bash
httpx==0.25.2  # Déjà présent, utilisé pour Meta API
```

---

## 📊 COMPARAISON DÉTAILLÉE

| Aspect | Twilio | Meta WhatsApp Business API |
|--------|--------|---------------------------|
| **Setup initial** | 5 min | 3-7 jours (vérification) |
| **Numéro de test** | Sandbox gratuit | Numéro propre requis |
| **Coût (1000 msg/mois)** | ~$50 | Gratuit |
| **Coût (10k msg/mois)** | ~$500 | ~$50 |
| **SDK officiel** | ✅ Oui (Python) | ❌ Non (HTTP direct) |
| **Destinataires test** | Max 5 | Illimité |
| **Templates interactifs** | ❌ Limité | ✅ Oui (boutons, listes) |
| **Analytics** | Dashboard Twilio | Facebook Business Manager |
| **Support** | Excellent | Moyen |
| **Changement code** | Minimal | Moyen |

---

## ✅ CHECKLIST DE MIGRATION

### Phase 1 : Préparation (1-2 semaines)
- [ ] Créer compte Meta Business
- [ ] Soumettre documents de vérification entreprise
- [ ] Attendre validation Meta (3-5 jours)
- [ ] Créer application WhatsApp sur developers.facebook.com
- [ ] Obtenir/configurer numéro de téléphone dédié
- [ ] Générer token permanent (System User)

### Phase 2 : Développement (1 jour)
- [ ] Mettre à jour `config.py` avec variables Meta
- [ ] Réécrire `whatsapp.py` avec HTTP client (httpx)
- [ ] Convertir méthodes en `async/await`
- [ ] Mettre à jour `AlertService` pour appels async
- [ ] Adapter `test_whatsapp.py`

### Phase 3 : Tests (1 jour)
- [ ] Tester avec numéro de test
- [ ] Vérifier formatage messages
- [ ] Tester envoi bulk
- [ ] Vérifier logs et erreurs
- [ ] Valider mise à jour `sent_whatsapp` en BDD

### Phase 4 : Déploiement (½ jour)
- [ ] Mettre à jour `.env` production
- [ ] Déployer nouvelle version
- [ ] Monitorer premiers envois
- [ ] Vérifier analytics Meta Business

---

## 🚀 FONCTIONNALITÉS AVANCÉES META (FUTURES)

### 1. Templates WhatsApp approuvés

Créer des templates pré-approuvés par Meta pour messages transactionnels :

```json
{
  "name": "alerte_rupture_stock",
  "language": "fr",
  "components": [
    {
      "type": "body",
      "text": "🚨 *Alerte Stock*\n\n{{1}} produit(s) en rupture:\n{{2}}\n\n_Digiboost PME_"
    }
  ]
}
```

**Avantages** :
- Meilleur taux de délivrabilité
- Tarif réduit (conversations marketing)
- Formatage garanti

### 2. Messages interactifs

Ajouter boutons d'action :

```python
{
    "type": "interactive",
    "interactive": {
        "type": "button",
        "body": {"text": "Stock faible détecté. Commander maintenant ?"},
        "action": {
            "buttons": [
                {"type": "reply", "reply": {"id": "yes", "title": "Oui"}},
                {"type": "reply", "reply": {"id": "no", "title": "Non"}}
            ]
        }
    }
}
```

### 3. Webhooks (réception messages)

Permettre aux gérants de répondre aux alertes via WhatsApp :

```python
# backend/app/api/v1/webhooks/whatsapp.py

@router.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    """Recevoir réponses WhatsApp des utilisateurs."""
    data = await request.json()

    # Extraire message
    message = data["entry"][0]["changes"][0]["value"]["messages"][0]
    from_number = message["from"]
    text = message["text"]["body"]

    # Traiter commande (ex: "STOCK RIZ" → renvoyer état stock riz)
    # À implémenter en Phase 2 (Agent IA conversationnel)

    return {"status": "ok"}
```

---

## 📚 RESSOURCES

### Documentation officielle
- Meta WhatsApp Business API : https://developers.facebook.com/docs/whatsapp
- API Reference : https://developers.facebook.com/docs/whatsapp/cloud-api/reference
- Templates : https://developers.facebook.com/docs/whatsapp/message-templates

### Guides utiles
- Quickstart : https://developers.facebook.com/docs/whatsapp/cloud-api/get-started
- Webhooks : https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks
- Error codes : https://developers.facebook.com/docs/whatsapp/cloud-api/support/error-codes

---

## ⚠️  NOTES IMPORTANTES

1. **Ne PAS migrer en production avant validation POC** : Twilio suffit pour les tests et le MVP
2. **Prévoir 1-2 semaines de setup Meta** : Vérification entreprise peut prendre du temps
3. **Tester en sandbox d'abord** : Meta propose aussi un mode test
4. **Budget WhatsApp** : Gratuit jusqu'à 1000 conversations/mois, puis tarification par paliers
5. **Qualité vs Coût** : Meta moins cher mais setup plus complexe

---

**Date de création** : 15 octobre 2025
**Prochaine révision** : Avant passage en production (estimé : janvier 2026)
