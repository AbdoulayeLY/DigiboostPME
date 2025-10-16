"""
Script de test pour AlertService.
"""
from app.db.session import SessionLocal
from app.services.alert_service import AlertService
from app.models.alert import Alert
from app.models.tenant import Tenant
from sqlalchemy import text


def test_alert_service():
    """Tester le service AlertService."""
    db = SessionLocal()

    try:
        print("\n" + "="*60)
        print("TEST ALERTSERVICE - Sprint 2 Prompt 2.2")
        print("="*60)

        # 1. Récupérer un tenant existant
        print("\n1. Recherche d'un tenant...")
        tenant = db.query(Tenant).first()

        if not tenant:
            print("❌ Aucun tenant trouvé. Exécutez seed_data.py d'abord.")
            return

        print(f"✅ Tenant trouvé: {tenant.name} (ID: {tenant.id})")

        # 2. Vérifier les vues SQL
        print("\n2. Vérification des vues SQL...")

        # Vue rupture stock
        result = db.execute(text("""
            SELECT COUNT(*) as count FROM v_alert_rupture_stock
            WHERE tenant_id = :tenant_id
        """), {"tenant_id": tenant.id}).first()
        print(f"   - v_alert_rupture_stock: {result.count} produits en rupture")

        # Vue stock faible
        result = db.execute(text("""
            SELECT COUNT(*) as count FROM v_alert_stock_faible
            WHERE tenant_id = :tenant_id
        """), {"tenant_id": tenant.id}).first()
        print(f"   - v_alert_stock_faible: {result.count} produits en stock faible")

        # 3. Créer une alerte de test
        print("\n3. Création d'une alerte de test...")

        # Vérifier si alerte existe déjà
        existing_alert = db.query(Alert).filter(
            Alert.tenant_id == tenant.id,
            Alert.name == "Test Rupture Stock Auto"
        ).first()

        if existing_alert:
            print(f"   Alerte existante trouvée: {existing_alert.name}")
            test_alert = existing_alert
        else:
            test_alert = Alert(
                tenant_id=tenant.id,
                name="Test Rupture Stock Auto",
                alert_type="RUPTURE_STOCK",
                conditions={},
                channels={"whatsapp": True, "email": False},
                recipients={
                    "whatsapp_numbers": ["+221771234567"],
                    "emails": []
                },
                is_active=True
            )
            db.add(test_alert)
            db.commit()
            db.refresh(test_alert)
            print(f"✅ Alerte créée: {test_alert.name} (ID: {test_alert.id})")

        # 4. Tester AlertService
        print("\n4. Test évaluation AlertService...")
        service = AlertService(db)

        triggered_alerts = service.evaluate_all_alerts(tenant.id)

        print(f"\n   Nombre d'alertes déclenchées: {len(triggered_alerts)}")

        if triggered_alerts:
            for item in triggered_alerts:
                alert = item["alert"]
                result = item["result"]
                print(f"\n   📢 Alerte: {alert.name}")
                print(f"      Type: {alert.alert_type}")
                print(f"      Sévérité: {result['severity']}")
                print(f"      Message: {result['message']}")
                print(f"      Produits concernés: {len(result.get('products', []))}")
        else:
            print("   ℹ️  Aucune alerte déclenchée (normal si stock OK)")

        # 5. Tester création historique
        if triggered_alerts:
            print("\n5. Test création historique...")
            first_alert = triggered_alerts[0]
            history = service.create_history_entry(
                first_alert["alert"],
                first_alert["result"]
            )
            print(f"✅ Historique créé: ID {history.id}")
            print(f"   - Déclenché à: {history.triggered_at}")
            print(f"   - Sévérité: {history.severity}")
            print(f"   - WhatsApp envoyé: {history.sent_whatsapp}")

        # 6. Vérifier déduplication
        print("\n6. Test déduplication...")
        if triggered_alerts:
            first_alert = triggered_alerts[0]
            is_dup = service._is_duplicate(
                first_alert["alert"].id,
                first_alert["result"].get("products", [])
            )
            print(f"   Déduplication: {'🔄 Duplicate détecté' if is_dup else '✅ Pas de duplicate'}")

        # 7. Statistiques finales
        print("\n7. Statistiques alertes...")
        total_alerts = db.query(Alert).filter(Alert.tenant_id == tenant.id).count()
        active_alerts = db.query(Alert).filter(
            Alert.tenant_id == tenant.id,
            Alert.is_active == True
        ).count()
        print(f"   - Total alertes: {total_alerts}")
        print(f"   - Alertes actives: {active_alerts}")

        from app.models.alert_history import AlertHistory
        total_history = db.query(AlertHistory).filter(
            AlertHistory.tenant_id == tenant.id
        ).count()
        print(f"   - Entrées historique: {total_history}")

        print("\n" + "="*60)
        print("✅ TEST ALERTSERVICE COMPLÉTÉ")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_alert_service()
