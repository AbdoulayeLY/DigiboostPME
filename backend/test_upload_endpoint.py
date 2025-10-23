"""
Test script pour débuguer l'erreur 500 sur upload-template endpoint.
"""
import requests
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8000"
TENANT_ID = "8840a84e-0e1d-4808-bace-7264e15d900c"  # Dernier tenant testé
TOKEN = None  # Will get from login

def login_as_admin():
    """Login et récupérer le token."""
    response = requests.post(
        f"{BACKEND_URL}/api/v1/auth/login",
        json={
            "username": "admin",
            "password": "admin123"  # Mot de passe par défaut admin
        }
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    else:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        return None

def test_upload():
    """Tester l'endpoint upload-template."""
    global TOKEN

    # Login
    TOKEN = login_as_admin()
    if not TOKEN:
        print("❌ Impossible de se connecter")
        return

    print(f"✅ Connecté avec token: {TOKEN[:20]}...")

    # Créer un fichier Excel de test minimal
    test_file_path = Path("test_template.xlsx")

    # Si le fichier n'existe pas, on le crée
    if not test_file_path.exists():
        import pandas as pd

        # Sheet Produits
        df_products = pd.DataFrame({
            "Code": ["P001", "P002"],
            "Nom": ["Produit Test 1", "Produit Test 2"],
            "Catégorie": ["Test", "Test"],
            "Prix Achat": [100, 200],
            "Prix Vente": [150, 300],
            "Unité": ["unité", "unité"],
            "Stock Initial": [10, 20],
            "Stock Min": [5, 5],
            "Stock Max": [100, 100],
        })

        # Sheet Ventes
        df_sales = pd.DataFrame({
            "Code Produit": ["P001", "P002"],
            "Date Vente": ["2025-10-01", "2025-10-02"],
            "Quantité": [2, 3],
            "Prix Unitaire": [150, 300],
        })

        with pd.ExcelWriter(test_file_path) as writer:
            df_products.to_excel(writer, sheet_name="Produits", index=False)
            df_sales.to_excel(writer, sheet_name="Ventes", index=False)

        print(f"✅ Fichier de test créé: {test_file_path}")

    # Upload
    print(f"\n📤 Upload du fichier vers tenant {TENANT_ID}...")

    with open(test_file_path, "rb") as f:
        files = {"file": ("test_template.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        headers = {"Authorization": f"Bearer {TOKEN}"}

        response = requests.post(
            f"{BACKEND_URL}/api/v1/admin/onboarding/upload-template/{TENANT_ID}",
            files=files,
            headers=headers
        )

    print(f"\n📊 Réponse: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")

    if response.status_code == 200:
        print(f"✅ Succès!")
        print(response.json())
    else:
        print(f"❌ Erreur {response.status_code}")
        print(f"Body: {response.text}")

        # Essayer de parser le JSON
        try:
            error_data = response.json()
            print(f"\nErreur JSON: {error_data}")
        except:
            pass

if __name__ == "__main__":
    test_upload()
