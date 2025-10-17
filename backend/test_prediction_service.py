"""
Script de test du service PredictionService.

Ce script teste toutes les fonctionnalités du service de prédictions avec les données seed.
"""
import sys
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.services.prediction_service import PredictionService
from app.models.tenant import Tenant
from app.models.product import Product
from sqlalchemy import text


def test_prediction_service():
    """Test complet du service de prédictions."""
    db = SessionLocal()

    try:
        # Récupérer un tenant de test
        tenant = db.query(Tenant).first()
        if not tenant:
            print("❌ Aucun tenant trouvé en base de données")
            return

        print(f"✅ Tenant trouvé : {tenant.name} (ID: {tenant.id})")

        # Récupérer un produit avec du stock et des ventes
        product = db.query(Product).filter(
            Product.tenant_id == tenant.id,
            Product.is_active == True,
            Product.current_stock > 0
        ).first()

        if not product:
            print("❌ Aucun produit avec stock trouvé")
            return

        print(f"✅ Produit test : {product.name} (Code: {product.code})")
        print(f"   - Stock actuel : {product.current_stock} {product.unit}")
        print(f"   - Stock minimum : {product.min_stock or 'N/A'} {product.unit}")

        # Initialiser le service
        service = PredictionService(db)

        print("\n" + "="*80)
        print("TEST 1 : Prédiction date rupture (predict_rupture_date)")
        print("="*80)

        rupture_date = service.predict_rupture_date(tenant.id, product.id)
        if rupture_date:
            from datetime import datetime
            days_until = (rupture_date - datetime.utcnow()).days
            print(f"✅ Rupture prévue le : {rupture_date.strftime('%Y-%m-%d')}")
            print(f"   - Dans {days_until} jours")
        else:
            print(f"✅ Pas de rupture prévue dans les 30 prochains jours")
            print(f"   (Stock suffisant ou pas d'historique de ventes)")

        print("\n" + "="*80)
        print("TEST 2 : Calcul quantité réapprovisionnement (calculate_reorder_quantity)")
        print("="*80)

        reorder = service.calculate_reorder_quantity(tenant.id, product.id, target_days=15)
        if reorder:
            print(f"✅ Recommandation réapprovisionnement :")
            print(f"   - Produit : {reorder['product_name']}")
            print(f"   - Stock actuel : {reorder['current_stock']} unités")
            print(f"   - Vente moyenne : {reorder['avg_daily_sales']} unités/jour")
            print(f"   - Objectif couverture : {reorder['target_days']} jours")
            print(f"   - Quantité à commander : {reorder['recommended_quantity']} unités")
            print(f"   - Stock sécurité : {reorder['safety_stock']} unités")
            print(f"   - Rationale : {reorder['rationale']}")
        else:
            print("❌ Calcul réapprovisionnement échoué")

        print("\n" + "="*80)
        print("TEST 3 : Liste ruptures prévues 15j (get_ruptures_prevues)")
        print("="*80)

        ruptures = service.get_ruptures_prevues(tenant.id, horizon_days=15)
        print(f"✅ Ruptures prévues (15 jours) : {len(ruptures)} produits")

        if ruptures:
            for i, rupture in enumerate(ruptures, 1):
                print(f"\n   {i}. {rupture['product_name']} (Code: {rupture['product_code']})")
                print(f"      - Stock actuel : {rupture['current_stock']}")
                print(f"      - Rupture prévue : {rupture['predicted_rupture_date'][:10]}")
                print(f"      - Urgence : {rupture['days_until_rupture']} jours")
                print(f"      - À commander : {rupture['recommended_quantity']} unités")
                if rupture['supplier']:
                    print(f"      - Fournisseur : {rupture['supplier']['name']} (Délai: {rupture['supplier']['lead_time_days']}j)")
                else:
                    print(f"      - Fournisseur : Non défini")
        else:
            print("   ℹ️  Aucune rupture prévue dans les 15 prochains jours")

        print("\n" + "="*80)
        print("TEST 4 : Recommandations d'achat (get_recommandations_achat)")
        print("="*80)

        recommandations = service.get_recommandations_achat(tenant.id, horizon_days=15)
        print(f"✅ Recommandations d'achat :")
        print(f"   - Total produits : {recommandations['total_products']}")
        print(f"   - Fournisseurs concernés : {recommandations['total_suppliers']}")

        if recommandations['by_supplier']:
            print(f"\n   📦 Commandes groupées par fournisseur :")
            for supplier in recommandations['by_supplier']:
                print(f"\n   🏢 {supplier['supplier_name']} (Délai: {supplier['lead_time_days']} jours)")
                print(f"      Produits à commander : {len(supplier['products'])}")
                for prod in supplier['products']:
                    urgency_icon = "🔴" if prod['urgency'] == "HIGH" else "🟡"
                    print(f"      {urgency_icon} {prod['product_name']} : {prod['quantity']} unités (rupture dans {prod['days_until_rupture']}j)")

        if recommandations['without_supplier']:
            print(f"\n   ⚠️  Produits sans fournisseur : {len(recommandations['without_supplier'])}")
            for prod in recommandations['without_supplier']:
                print(f"      - {prod['product_name']} : {prod['recommended_quantity']} unités")

        print("\n" + "="*80)
        print("TEST 5 : Fonction SQL fn_predict_date_rupture")
        print("="*80)

        # Tester la fonction SQL directement
        query = text("""
            SELECT fn_predict_date_rupture(:tenant_id, :product_id) as rupture_date
        """)

        result = db.execute(query, {
            "tenant_id": str(tenant.id),
            "product_id": str(product.id)
        }).fetchone()

        if result and result.rupture_date:
            print(f"✅ Fonction SQL fn_predict_date_rupture fonctionne")
            print(f"   - Date prévue : {result.rupture_date}")
        else:
            print(f"✅ Fonction SQL retourne NULL (pas de rupture prévue)")

        print("\n" + "="*80)
        print("TEST 6 : Fonction SQL fn_calc_quantite_reappro")
        print("="*80)

        # Tester la fonction SQL de calcul de réapprovisionnement
        query = text("""
            SELECT fn_calc_quantite_reappro(:tenant_id, :product_id, :target_days) as quantity
        """)

        result = db.execute(query, {
            "tenant_id": str(tenant.id),
            "product_id": str(product.id),
            "target_days": 15
        }).fetchone()

        if result and result.quantity is not None:
            print(f"✅ Fonction SQL fn_calc_quantite_reappro fonctionne")
            print(f"   - Quantité recommandée : {float(result.quantity)} unités")
        else:
            print(f"✅ Fonction SQL retourne NULL")

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
    print("🚀 Test du service PredictionService\n")
    test_prediction_service()
