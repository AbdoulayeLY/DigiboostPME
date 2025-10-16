"""
Script de test des endpoints API Alertes - Prompt 2.5
"""
import asyncio
from app.db.session import SessionLocal
from app.models.user import User
from app.models.tenant import Tenant
from app.models.alert import Alert
from app.core.security import create_access_token
from uuid import UUID
import requests

# Configuration
BASE_URL = "http://localhost:8000/api/v1"

def get_test_token():
    """Récupérer un token JWT de test"""
    db = SessionLocal()
    try:
        # Récupérer le premier user actif
        user = db.query(User).filter(User.is_active == True).first()

        if not user:
            print("❌ Aucun utilisateur actif trouvé en base")
            return None

        print(f"✅ User trouvé: {user.email} (tenant: {user.tenant_id})")

        # Créer token
        token = create_access_token(
            subject=str(user.id),
            tenant_id=user.tenant_id
        )

        return token, str(user.tenant_id)

    finally:
        db.close()

def test_list_alerts(token):
    """Test GET /alerts"""
    print("\n" + "="*70)
    print("TEST 1: GET /alerts - Liste des alertes")
    print("="*70)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/alerts/", headers=headers)

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {len(data)} alerte(s) trouvée(s)")
        for alert in data:
            print(f"   - {alert['name']} ({alert['alert_type']}) - Active: {alert['is_active']}")
        return data
    else:
        print(f"❌ Erreur: {response.text}")
        return []

def test_create_alert(token):
    """Test POST /alerts"""
    print("\n" + "="*70)
    print("TEST 2: POST /alerts - Création d'alerte")
    print("="*70)

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    payload = {
        "name": "Test API - Rupture Stock",
        "alert_type": "RUPTURE_STOCK",
        "conditions": {},
        "channels": {"whatsapp": True, "email": False},
        "recipients": {
            "whatsapp_numbers": ["+221771234567"],
            "emails": []
        },
        "is_active": True
    }

    response = requests.post(f"{BASE_URL}/alerts/", headers=headers, json=payload)

    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Alerte créée: {data['name']} (ID: {data['id']})")
        return data['id']
    else:
        print(f"❌ Erreur: {response.text}")
        return None

def test_get_alert(token, alert_id):
    """Test GET /alerts/{id}"""
    print("\n" + "="*70)
    print(f"TEST 3: GET /alerts/{alert_id} - Récupérer une alerte")
    print("="*70)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/alerts/{alert_id}", headers=headers)

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Alerte récupérée: {data['name']}")
        print(f"   Type: {data['alert_type']}")
        print(f"   Active: {data['is_active']}")
        print(f"   Recipients: {len(data['recipients'].get('whatsapp_numbers', []))} WhatsApp")
        return True
    else:
        print(f"❌ Erreur: {response.text}")
        return False

def test_update_alert(token, alert_id):
    """Test PUT /alerts/{id}"""
    print("\n" + "="*70)
    print(f"TEST 4: PUT /alerts/{alert_id} - Modification d'alerte")
    print("="*70)

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    payload = {
        "name": "Test API - Rupture Stock (Modifié)",
        "conditions": {"threshold": 5}
    }

    response = requests.put(f"{BASE_URL}/alerts/{alert_id}", headers=headers, json=payload)

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Alerte modifiée: {data['name']}")
        print(f"   Conditions: {data['conditions']}")
        return True
    else:
        print(f"❌ Erreur: {response.text}")
        return False

def test_toggle_alert(token, alert_id):
    """Test PATCH /alerts/{id}/toggle"""
    print("\n" + "="*70)
    print(f"TEST 5: PATCH /alerts/{alert_id}/toggle - Toggle activation")
    print("="*70)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.patch(f"{BASE_URL}/alerts/{alert_id}/toggle", headers=headers)

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Alerte toggled: is_active={data['is_active']}")

        # Toggle à nouveau pour remettre à True
        response2 = requests.patch(f"{BASE_URL}/alerts/{alert_id}/toggle", headers=headers)
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"✅ Alerte re-toggled: is_active={data2['is_active']}")

        return True
    else:
        print(f"❌ Erreur: {response.text}")
        return False

def test_alert_history(token):
    """Test GET /alerts/history"""
    print("\n" + "="*70)
    print("TEST 6: GET /alerts/history - Historique des alertes")
    print("="*70)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/alerts/history/", headers=headers)

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {len(data)} entrée(s) d'historique trouvée(s)")
        for entry in data[:3]:  # Afficher les 3 premières
            print(f"   - {entry['alert_type']} | {entry['severity']} | {entry['triggered_at']}")
        return True
    else:
        print(f"❌ Erreur: {response.text}")
        return False

def test_delete_alert(token, alert_id):
    """Test DELETE /alerts/{id}"""
    print("\n" + "="*70)
    print(f"TEST 7: DELETE /alerts/{alert_id} - Suppression d'alerte")
    print("="*70)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/alerts/{alert_id}", headers=headers)

    print(f"Status: {response.status_code}")
    if response.status_code == 204:
        print(f"✅ Alerte supprimée avec succès")
        return True
    else:
        print(f"❌ Erreur: {response.text}")
        return False

def test_multi_tenant_isolation(token, tenant_id):
    """Test isolation multi-tenant"""
    print("\n" + "="*70)
    print("TEST 8: Isolation Multi-Tenant")
    print("="*70)

    db = SessionLocal()
    try:
        # Vérifier que toutes les alertes du tenant sont bien filtrées
        alerts = db.query(Alert).filter(Alert.tenant_id == UUID(tenant_id)).all()
        print(f"✅ Alertes en base pour tenant {tenant_id}: {len(alerts)}")

        # Vérifier qu'on ne peut pas accéder aux alertes d'un autre tenant
        other_alerts = db.query(Alert).filter(Alert.tenant_id != UUID(tenant_id)).first()

        if other_alerts:
            print(f"\n🔒 Test d'isolation: Tentative d'accès à l'alerte d'un autre tenant...")
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/alerts/{other_alerts.id}", headers=headers)

            if response.status_code == 404:
                print("✅ Isolation multi-tenant OK: Accès refusé (404)")
            else:
                print(f"⚠️  Isolation multi-tenant ECHEC: Status {response.status_code}")
        else:
            print("ℹ️  Pas d'autres tenants en base pour tester l'isolation")

        return True

    finally:
        db.close()

def main():
    """Exécuter tous les tests"""
    print("="*70)
    print("TEST ENDPOINTS API ALERTES - PROMPT 2.5")
    print("="*70)

    # Obtenir token
    result = get_test_token()
    if not result:
        print("❌ Impossible de récupérer un token de test")
        return

    token, tenant_id = result

    # Test 1: Liste
    alerts = test_list_alerts(token)

    # Test 2: Création
    alert_id = test_create_alert(token)
    if not alert_id:
        print("\n❌ Tests interrompus: création échouée")
        return

    # Test 3: Récupération
    test_get_alert(token, alert_id)

    # Test 4: Modification
    test_update_alert(token, alert_id)

    # Test 5: Toggle
    test_toggle_alert(token, alert_id)

    # Test 6: Historique
    test_alert_history(token)

    # Test 7: Suppression
    test_delete_alert(token, alert_id)

    # Test 8: Isolation multi-tenant
    test_multi_tenant_isolation(token, tenant_id)

    print("\n" + "="*70)
    print("✅ TOUS LES TESTS TERMINÉS")
    print("="*70)

if __name__ == "__main__":
    main()
