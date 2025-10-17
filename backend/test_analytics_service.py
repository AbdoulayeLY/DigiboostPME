"""
Script de test du service AnalyticsService.

Ce script teste toutes les fonctionnalités du service analytics avec les données seed.
"""
import sys
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.services.analytics_service import AnalyticsService
from app.models.tenant import Tenant
from app.models.product import Product
from sqlalchemy import func


def test_analytics_service():
    """Test complet du service analytics."""
    db = SessionLocal()

    try:
        # Récupérer un tenant de test
        tenant = db.query(Tenant).first()
        if not tenant:
            print("❌ Aucun tenant trouvé en base de données")
            return

        print(f"✅ Tenant trouvé : {tenant.name} (ID: {tenant.id})")

        # Récupérer un produit avec des ventes
        product = db.query(Product).filter(
            Product.tenant_id == tenant.id,
            Product.is_active == True
        ).first()

        if not product:
            print("❌ Aucun produit trouvé")
            return

        print(f"✅ Produit test : {product.name} (Code: {product.code})")

        # Initialiser le service
        service = AnalyticsService(db)

        print("\n" + "="*80)
        print("TEST 1 : Analyse détaillée produit (get_product_analysis)")
        print("="*80)

        analysis = service.get_product_analysis(tenant.id, product.id)
        if analysis:
            print(f"✅ Analyse produit récupérée")
            print(f"   - Stock actuel : {analysis['product']['current_stock']} {analysis['product']['unit']}")
            print(f"   - Ventes 30j : {analysis['sales']['last_30_days']['quantity']} unités")
            print(f"   - CA 30j : {analysis['sales']['last_30_days']['revenue']:.2f} FCFA")
            print(f"   - Moyenne quotidienne : {analysis['sales']['last_30_days']['avg_daily']:.2f} unités/jour")
            print(f"   - Couverture : {analysis['metrics']['coverage_days']} jours" if analysis['metrics']['coverage_days'] else "   - Couverture : N/A")
            print(f"   - Rotation annuelle : {analysis['metrics']['rotation_annual']} fois/an" if analysis['metrics']['rotation_annual'] else "   - Rotation annuelle : N/A")
            print(f"   - Marge : {analysis['metrics']['margin']:.2f} FCFA ({analysis['metrics']['margin_percent']:.2f}%)")
            print(f"   - Statut : {analysis['status']}")
        else:
            print("❌ Analyse produit échouée")

        print("\n" + "="*80)
        print("TEST 2 : Évolution des ventes (get_sales_evolution)")
        print("="*80)

        evolution = service.get_sales_evolution(tenant.id, days=30)
        print(f"✅ Évolution ventes récupérée : {len(evolution)} jours de données")
        if evolution:
            total_revenue = sum(day['revenue'] for day in evolution)
            total_transactions = sum(day['transactions'] for day in evolution)
            print(f"   - Période : {evolution[0]['date']} → {evolution[-1]['date']}")
            print(f"   - CA total : {total_revenue:.2f} FCFA")
            print(f"   - Transactions totales : {total_transactions}")
            print(f"   - Exemple jour : {evolution[0]['date']} → {evolution[0]['revenue']:.2f} FCFA ({evolution[0]['transactions']} transactions)")

        print("\n" + "="*80)
        print("TEST 3 : Top produits (get_top_products)")
        print("="*80)

        # Test par CA
        top_revenue = service.get_top_products(tenant.id, limit=5, days=30, order_by="revenue")
        print(f"✅ Top 5 produits par CA :")
        for i, prod in enumerate(top_revenue, 1):
            print(f"   {i}. {prod['name']} - {prod['revenue']:.2f} FCFA ({prod['quantity_sold']:.0f} {prod['unit']})")

        # Test par quantité
        top_quantity = service.get_top_products(tenant.id, limit=5, days=30, order_by="quantity")
        print(f"\n✅ Top 5 produits par quantité :")
        for i, prod in enumerate(top_quantity, 1):
            print(f"   {i}. {prod['name']} - {prod['quantity_sold']:.0f} {prod['unit']} ({prod['revenue']:.2f} FCFA)")

        print("\n" + "="*80)
        print("TEST 4 : Performance par catégorie (get_category_performance)")
        print("="*80)

        categories = service.get_category_performance(tenant.id, days=30)
        print(f"✅ Performance {len(categories)} catégories :")
        for cat in categories:
            print(f"   - {cat['name']} : {cat['revenue']:.2f} FCFA ({cat['product_count']} produits, {cat['transactions']} transactions)")

        print("\n" + "="*80)
        print("TEST 5 : Classification ABC (classify_products_abc)")
        print("="*80)

        abc = service.classify_products_abc(tenant.id, days=90)
        print(f"✅ Classification ABC sur 90 jours :")
        print(f"   - Classe A (80% CA) : {len(abc['A'])} produits")
        print(f"   - Classe B (15% CA) : {len(abc['B'])} produits")
        print(f"   - Classe C (5% CA) : {len(abc['C'])} produits")

        total_products = len(abc['A']) + len(abc['B']) + len(abc['C'])
        if total_products > 0:
            print(f"   - Total : {total_products} produits")
            print(f"   - % Classe A : {len(abc['A'])/total_products*100:.1f}%")
            print(f"   - % Classe B : {len(abc['B'])/total_products*100:.1f}%")
            print(f"   - % Classe C : {len(abc['C'])/total_products*100:.1f}%")

        print("\n" + "="*80)
        print("✅ TOUS LES TESTS SONT RÉUSSIS !")
        print("="*80)

    except Exception as e:
        print(f"\n❌ ERREUR : {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Test du service AnalyticsService\n")
    test_analytics_service()
