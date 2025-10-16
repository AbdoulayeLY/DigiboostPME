"""
Script de test pour le dashboard Vue d'Ensemble.
"""
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BASE_URL = "http://localhost:8000/api/v1"


def login():
    """Login et recuperer le token."""
    print("\n=== LOGIN ===")
    url = f"{BASE_URL}/auth/login"
    data = json.dumps({
        "email": "admin@digiboost.sn",
        "password": "password123"
    }).encode('utf-8')

    req = Request(url, data=data, headers={'Content-Type': 'application/json'})

    try:
        with urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✓ Login reussi")
            return result['access_token']
    except HTTPError as e:
        print(f"✗ Error {e.code}: {e.read().decode('utf-8')}")
        return None


def test_dashboard(access_token):
    """Test du dashboard Vue d'Ensemble."""
    print("\n=== TEST DASHBOARD VUE D'ENSEMBLE ===")

    url = f"{BASE_URL}/dashboards/overview"
    req = Request(url, headers={
        'Authorization': f'Bearer {access_token}'
    })

    try:
        with urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✓ Status: {response.status}")
            print("\n--- SANTE STOCK ---")
            stock = result['stock_health']
            print(f"  Total produits:     {stock['total_products']}")
            print(f"  Ruptures:           {stock['rupture_count']}")
            print(f"  Stock faible:       {stock['low_stock_count']}")
            print(f"  Alertes totales:    {stock['alert_count']}")
            print(f"  Valorisation:       {stock['total_stock_value']:,.2f} XOF")

            print("\n--- PERFORMANCE VENTES ---")
            sales = result['sales_performance']
            print(f"  CA 7 jours:         {sales['ca_7j']:,.2f} XOF")
            print(f"  CA 30 jours:        {sales['ca_30j']:,.2f} XOF")
            print(f"  Evolution:          {sales['evolution_ca']:+.2f}%")
            print(f"  Ventes 7j:          {sales['ventes_7j']}")
            print(f"  Ventes 30j:         {sales['ventes_30j']}")

            print("\n--- TOP 5 PRODUITS ---")
            for i, prod in enumerate(result['top_products'], 1):
                print(f"  {i}. {prod['product_name']} ({prod['product_code']})")
                print(f"     CA: {prod['total_revenue']:,.2f} XOF - Qte: {prod['total_quantity']:.0f}")

            print("\n--- PRODUITS DORMANTS ---")
            if result['dormant_products']:
                for prod in result['dormant_products']:
                    print(f"  - {prod['product_name']} ({prod['product_code']})")
                    print(f"    Stock: {prod['current_stock']:.0f} - Valeur: {prod['immobilized_value']:,.2f} XOF")
            else:
                print("  Aucun produit dormant")

            print("\n--- KPIS ---")
            print(f"  Taux de service:    {result['kpis']['taux_service']:.2f}%")

            print(f"\n✓ Dashboard genere a: {result['generated_at']}")
            return result
    except HTTPError as e:
        print(f"✗ Error {e.code}: {e.read().decode('utf-8')}")
        return None


def test_refresh_views(access_token):
    """Test rafraichissement des vues."""
    print("\n=== TEST REFRESH VUES ===")

    url = f"{BASE_URL}/dashboards/refresh-views"
    req = Request(url, data=b'', headers={
        'Authorization': f'Bearer {access_token}'
    })
    req.get_method = lambda: 'POST'

    try:
        with urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✓ Status: {result['status']}")
            print(f"  Message: {result['message']}")
            return result
    except HTTPError as e:
        print(f"✗ Error {e.code}: {e.read().decode('utf-8')}")
        return None


if __name__ == "__main__":
    print("="*60)
    print("TEST DASHBOARD VUE D'ENSEMBLE - Digiboost PME")
    print("="*60)

    # Login
    token = login()
    if not token:
        print("\n✗ Login failed, stopping tests")
        exit(1)

    # Test dashboard
    dashboard = test_dashboard(token)
    if not dashboard:
        print("\n✗ Dashboard failed")

    # Test refresh views
    refresh = test_refresh_views(token)

    print("\n" + "="*60)
    print("TESTS TERMINES")
    print("="*60)
