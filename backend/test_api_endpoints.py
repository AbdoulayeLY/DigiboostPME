"""
Script de test des endpoints API Analytics & Prédictions.

Ce script teste tous les nouveaux endpoints créés dans le Prompt 3.3.
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_EMAIL = "manager@digiboost.sn"
TEST_PASSWORD = "password123"

# Couleurs pour l'affichage
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def print_success(message):
    print(f"{GREEN}✅ {message}{RESET}")


def print_error(message):
    print(f"{RED}❌ {message}{RESET}")


def print_info(message):
    print(f"{YELLOW}ℹ️  {message}{RESET}")


def login():
    """Authentifier et récupérer le token."""
    print("\n" + "="*80)
    print("AUTHENTIFICATION")
    print("="*80)

    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )

    if response.status_code == 200:
        data = response.json()
        token = data["access_token"]
        print_success(f"Authentification réussie")
        return token
    else:
        print_error(f"Authentification échouée: {response.text}")
        return None


def test_product_analysis(token, product_id):
    """Tester GET /analytics/products/{id}"""
    print("\n" + "="*80)
    print("TEST 1: Analyse produit (GET /analytics/products/{product_id})")
    print("="*80)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/analytics/products/{product_id}",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        print_success("Endpoint fonctionnel")
        print(f"   Produit: {data['product']['name']}")
        print(f"   Stock actuel: {data['product']['current_stock']} {data['product']['unit']}")
        print(f"   Ventes 30j: {data['sales']['last_30_days']['quantity']} unités")
        print(f"   Couverture: {data['metrics']['coverage_days']} jours" if data['metrics']['coverage_days'] else "   Couverture: N/A")
        print(f"   Marge: {data['metrics']['margin_percent']:.2f}%")
        print(f"   Statut: {data['status']}")
        return True
    else:
        print_error(f"Erreur {response.status_code}: {response.text}")
        return False


def test_sales_evolution(token):
    """Tester GET /analytics/sales/evolution"""
    print("\n" + "="*80)
    print("TEST 2: Évolution ventes (GET /analytics/sales/evolution)")
    print("="*80)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/analytics/sales/evolution?days=30",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        print_success("Endpoint fonctionnel")
        print(f"   Période: {data['period_days']} jours")
        print(f"   Jours de données: {len(data['data'])}")
        if data['data']:
            total_revenue = sum(day['revenue'] for day in data['data'])
            print(f"   CA total: {total_revenue:.2f} FCFA")
        return True
    else:
        print_error(f"Erreur {response.status_code}: {response.text}")
        return False


def test_top_products(token):
    """Tester GET /analytics/products/top"""
    print("\n" + "="*80)
    print("TEST 3: Top produits (GET /analytics/products/top)")
    print("="*80)

    headers = {"Authorization": f"Bearer {token}"}

    # Test par CA
    response = requests.get(
        f"{BASE_URL}/analytics/products/top?limit=5&days=30&order_by=revenue",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        print_success("Endpoint fonctionnel (tri par CA)")
        print(f"   Top {data['count']} produits:")
        for i, prod in enumerate(data['products'][:3], 1):
            print(f"   {i}. {prod['name']}: {prod['revenue']:.2f} FCFA")
        return True
    else:
        print_error(f"Erreur {response.status_code}: {response.text}")
        return False


def test_category_performance(token):
    """Tester GET /analytics/categories/performance"""
    print("\n" + "="*80)
    print("TEST 4: Performance catégories (GET /analytics/categories/performance)")
    print("="*80)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/analytics/categories/performance?days=30",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        print_success("Endpoint fonctionnel")
        print(f"   Catégories: {len(data['categories'])}")
        for cat in data['categories'][:3]:
            print(f"   - {cat['name']}: {cat['revenue']:.2f} FCFA ({cat['product_count']} produits)")
        return True
    else:
        print_error(f"Erreur {response.status_code}: {response.text}")
        return False


def test_abc_classification(token):
    """Tester GET /analytics/products/abc"""
    print("\n" + "="*80)
    print("TEST 5: Classification ABC (GET /analytics/products/abc)")
    print("="*80)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/analytics/products/abc?days=90",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        print_success("Endpoint fonctionnel")
        print(f"   Classe A: {len(data['class_a'])} produits")
        print(f"   Classe B: {len(data['class_b'])} produits")
        print(f"   Classe C: {len(data['class_c'])} produits")
        print(f"   Total: {data['total_products']} produits")
        return True
    else:
        print_error(f"Erreur {response.status_code}: {response.text}")
        return False


def test_ruptures_prevues(token):
    """Tester GET /predictions/ruptures"""
    print("\n" + "="*80)
    print("TEST 6: Ruptures prévues (GET /predictions/ruptures)")
    print("="*80)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/predictions/ruptures?horizon_days=15",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        print_success("Endpoint fonctionnel")
        print(f"   Ruptures prévues (15j): {data['count']} produits")
        for rupture in data['ruptures'][:3]:
            print(f"   - {rupture['product_name']}: rupture dans {rupture['days_until_rupture']} jours")
        return True
    else:
        print_error(f"Erreur {response.status_code}: {response.text}")
        return False


def test_recommandations_achat(token):
    """Tester GET /predictions/recommandations"""
    print("\n" + "="*80)
    print("TEST 7: Recommandations achat (GET /predictions/recommandations)")
    print("="*80)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/predictions/recommandations?horizon_days=15",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        print_success("Endpoint fonctionnel")
        print(f"   Total produits: {data['total_products']}")
        print(f"   Fournisseurs: {data['total_suppliers']}")
        if data['by_supplier']:
            print(f"   Commandes groupées:")
            for supplier in data['by_supplier']:
                print(f"   - {supplier['supplier_name']}: {len(supplier['products'])} produits")
        return True
    else:
        print_error(f"Erreur {response.status_code}: {response.text}")
        return False


def main():
    """Exécuter tous les tests."""
    print("🚀 TEST DES ENDPOINTS API - Analytics & Prédictions")
    print("="*80)

    # Authentification
    token = login()
    if not token:
        print_error("Impossible de continuer sans authentification")
        return

    # Récupérer un product_id de test
    print_info("Récupération d'un product_id de test...")
    # ID connu depuis les tests précédents
    product_id = "04855c21-bd55-456e-acbb-0c8c645cbf8e"  # Eau Kirene
    print_success(f"Product ID: {product_id}")

    # Exécuter tous les tests
    results = []
    results.append(test_product_analysis(token, product_id))
    results.append(test_sales_evolution(token))
    results.append(test_top_products(token))
    results.append(test_category_performance(token))
    results.append(test_abc_classification(token))
    results.append(test_ruptures_prevues(token))
    results.append(test_recommandations_achat(token))

    # Résumé
    print("\n" + "="*80)
    print("RÉSUMÉ DES TESTS")
    print("="*80)
    success_count = sum(results)
    total_count = len(results)

    if success_count == total_count:
        print_success(f"TOUS LES TESTS RÉUSSIS ({success_count}/{total_count})")
    else:
        print_error(f"{success_count}/{total_count} tests réussis")

    print("\n📊 Documentation Swagger disponible: http://localhost:8000/api/v1/docs")


if __name__ == "__main__":
    main()
