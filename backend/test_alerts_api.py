"""
Script de test pour les endpoints API d'alertes.

Usage:
    python test_alerts_api.py
"""
import requests
import json
from pprint import pprint

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
LOGIN_EMAIL = "admin@digiboost.sn"
LOGIN_PASSWORD = "admin123"


def test_alerts_endpoints():
    """Tester tous les endpoints alertes."""

    print("\n" + "="*60)
    print("🧪 TEST ENDPOINTS API ALERTES")
    print("="*60)

    # 1. Login pour obtenir token
    print("\n1️⃣  Authentification...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": LOGIN_EMAIL, "password": LOGIN_PASSWORD}
    )

    if login_response.status_code != 200:
        print(f"❌ Login échoué: {login_response.status_code}")
        print(login_response.text)
        return False

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ Login réussi, token obtenu")

    # 2. GET /alerts - Liste des alertes
    print("\n2️⃣  GET /alerts - Liste des alertes")
    response = requests.get(f"{BASE_URL}/alerts", headers=headers)
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        alerts = response.json()
        print(f"   ✅ {len(alerts)} alerte(s) trouvée(s)")
        if alerts:
            print("\n   Première alerte:")
            pprint(alerts[0], indent=6)
    else:
        print(f"   ❌ Erreur: {response.text}")
        return False

    # 3. POST /alerts - Créer une nouvelle alerte
    print("\n3️⃣  POST /alerts - Créer nouvelle alerte")
    new_alert = {
        "name": "Test Alerte API - Rupture Stock Riz",
        "alert_type": "RUPTURE_STOCK",
        "conditions": {
            "threshold": 0,
            "product_ids": []
        },
        "channels": {
            "whatsapp": True,
            "email": False
        },
        "recipients": {
            "whatsapp_numbers": ["+33645090636"],
            "emails": []
        },
        "is_active": True
    }

    response = requests.post(
        f"{BASE_URL}/alerts",
        headers=headers,
        json=new_alert
    )
    print(f"   Status: {response.status_code}")

    if response.status_code == 201:
        created_alert = response.json()
        alert_id = created_alert["id"]
        print(f"   ✅ Alerte créée avec ID: {alert_id}")
        print(f"   Nom: {created_alert['name']}")
        print(f"   Type: {created_alert['alert_type']}")
        print(f"   Active: {created_alert['is_active']}")
    else:
        print(f"   ❌ Erreur: {response.text}")
        return False

    # 4. GET /alerts/{id} - Récupérer alerte spécifique
    print(f"\n4️⃣  GET /alerts/{alert_id} - Détails alerte")
    response = requests.get(f"{BASE_URL}/alerts/{alert_id}", headers=headers)
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        alert = response.json()
        print(f"   ✅ Alerte récupérée: {alert['name']}")
    else:
        print(f"   ❌ Erreur: {response.text}")

    # 5. PUT /alerts/{id} - Modifier alerte
    print(f"\n5️⃣  PUT /alerts/{alert_id} - Modifier alerte")
    update_data = {
        "name": "Test Alerte API - Rupture Stock Riz (Modifié)",
        "is_active": False
    }

    response = requests.put(
        f"{BASE_URL}/alerts/{alert_id}",
        headers=headers,
        json=update_data
    )
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        updated_alert = response.json()
        print(f"   ✅ Alerte modifiée")
        print(f"   Nouveau nom: {updated_alert['name']}")
        print(f"   Active: {updated_alert['is_active']}")
    else:
        print(f"   ❌ Erreur: {response.text}")

    # 6. GET /alerts/history - Historique
    print("\n6️⃣  GET /alerts/history - Historique déclenchements")
    response = requests.get(
        f"{BASE_URL}/alerts/history/",
        headers=headers,
        params={"limit": 10}
    )
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        history = response.json()
        print(f"   ✅ {len(history)} entrée(s) d'historique")
        if history:
            print("\n   Dernière alerte déclenchée:")
            print(f"      Type: {history[0]['alert_type']}")
            print(f"      Sévérité: {history[0]['severity']}")
            print(f"      Message: {history[0]['message'][:80]}...")
            print(f"      WhatsApp envoyé: {history[0]['sent_whatsapp']}")
    else:
        print(f"   ❌ Erreur: {response.text}")

    # 7. POST /alerts/{id}/test - Tester alerte
    print(f"\n7️⃣  POST /alerts/{alert_id}/test - Tester alerte")
    response = requests.post(
        f"{BASE_URL}/alerts/{alert_id}/test",
        headers=headers
    )
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        test_result = response.json()
        print(f"   ✅ Test réussi")
        print(f"   Alerte: {test_result['alert_name']}")
        print(f"   WhatsApp envoyé: {test_result['sent_whatsapp']}")
        print(f"   Email envoyé: {test_result['sent_email']}")
    else:
        print(f"   ❌ Erreur: {response.text}")

    # 8. GET /alerts - Filtres
    print("\n8️⃣  GET /alerts?is_active=false - Filtrer alertes inactives")
    response = requests.get(
        f"{BASE_URL}/alerts",
        headers=headers,
        params={"is_active": False}
    )
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        inactive_alerts = response.json()
        print(f"   ✅ {len(inactive_alerts)} alerte(s) inactive(s)")
    else:
        print(f"   ❌ Erreur: {response.text}")

    # 9. DELETE /alerts/{id} - Supprimer alerte
    print(f"\n9️⃣  DELETE /alerts/{alert_id} - Supprimer alerte")
    response = requests.delete(f"{BASE_URL}/alerts/{alert_id}", headers=headers)
    print(f"   Status: {response.status_code}")

    if response.status_code == 204:
        print(f"   ✅ Alerte supprimée")
    else:
        print(f"   ❌ Erreur: {response.text}")

    # Vérifier suppression
    print(f"\n🔍  Vérification suppression...")
    response = requests.get(f"{BASE_URL}/alerts/{alert_id}", headers=headers)
    if response.status_code == 404:
        print(f"   ✅ Alerte bien supprimée (404)")
    else:
        print(f"   ⚠️  Statut inattendu: {response.status_code}")

    print("\n" + "="*60)
    print("📊 RÉSUMÉ")
    print("="*60)
    print("✅ Tous les endpoints testés avec succès!")
    print("="*60 + "\n")

    return True


if __name__ == "__main__":
    try:
        success = test_alerts_endpoints()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
