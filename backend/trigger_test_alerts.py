#!/usr/bin/env python3
"""
Script pour déclencher manuellement les alertes de test
Usage: python trigger_test_alerts.py
"""
import asyncio
import sys
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.alert import Alert
from app.models.tenant import Tenant
from app.services.alert_service import AlertService
from app.integrations.whatsapp_templates import format_alert_message


async def main():
    """Déclencher toutes les alertes actives pour test"""
    db: Session = SessionLocal()

    try:
        # Récupérer tous les tenants actifs
        tenants = db.query(Tenant).filter(Tenant.is_active == True).all()
        print(f"🔍 Tenants actifs trouvés: {len(tenants)}")

        if not tenants:
            print("❌ Aucun tenant actif trouvé")
            return

        for tenant in tenants:
            print(f"\n{'='*60}")
            print(f"📊 Tenant: {tenant.name} (ID: {tenant.id})")
            print(f"{'='*60}")

            # Récupérer alertes actives
            alerts = db.query(Alert).filter(
                Alert.tenant_id == tenant.id,
                Alert.is_active == True
            ).all()

            print(f"✅ Alertes actives: {len(alerts)}")

            if not alerts:
                print("⚠️  Aucune alerte active configurée pour ce tenant")
                continue

            # Service alerting
            service = AlertService(db)

            for alert in alerts:
                print(f"\n🔔 Test alerte: {alert.name}")
                print(f"   Type: {alert.alert_type}")
                print(f"   Canaux: {alert.channels}")

                # Évaluer l'alerte
                if alert.alert_type == "RUPTURE_STOCK":
                    result = service._evaluate_rupture_stock(alert)
                elif alert.alert_type == "LOW_STOCK":
                    result = service._evaluate_low_stock(alert)
                elif alert.alert_type == "BAISSE_TAUX_SERVICE":
                    result = service._evaluate_taux_service(alert)
                else:
                    print(f"   ❌ Type d'alerte inconnu: {alert.alert_type}")
                    continue

                # Afficher résultat
                if result["triggered"]:
                    print(f"   ✅ DÉCLENCHÉE!")
                    print(f"   Message: {result['message']}")
                    print(f"   Sévérité: {result['severity']}")
                    print(f"   Détails: {result['details']}")

                    # Créer historique
                    history = service.create_history_entry(alert, result)
                    print(f"   📝 Historique créé (ID: {history.id})")

                    # Envoyer notifications
                    try:
                        service.send_alert_notifications(alert, result, history)
                        print(f"   📨 Notifications envoyées")
                    except Exception as e:
                        print(f"   ❌ Erreur envoi notifications: {str(e)}")
                else:
                    print(f"   ℹ️  Non déclenchée (conditions non remplies)")
                    if result.get("message"):
                        print(f"   Raison: {result['message']}")

        print(f"\n{'='*60}")
        print("✅ Test terminé!")
        print(f"{'='*60}")

    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Déclenchement manuel des alertes de test")
    print("=" * 60)
    asyncio.run(main())
