"""
Script de test pour les tâches Celery.

Usage:
    python test_celery_tasks.py
"""
from app.tasks.alert_tasks import evaluate_all_tenants_alerts, test_whatsapp_connection
from app.tasks.dashboard_tasks import refresh_dashboard_views


def test_alert_evaluation():
    """Tester l'évaluation des alertes."""
    print("\n" + "="*60)
    print("TEST CELERY - Évaluation Alertes")
    print("="*60)

    try:
        print("\n🔔 Exécution de evaluate_all_tenants_alerts...")
        result = evaluate_all_tenants_alerts()

        print(f"\n✅ Tâche complétée avec succès:")
        print(f"   - Tenants traités: {result['tenants_processed']}")
        print(f"   - Alertes déclenchées: {result['alerts_triggered']}")
        print(f"   - Notifications envoyées: {result['notifications_sent']}")

        return True

    except Exception as e:
        print(f"\n❌ Erreur lors de l'exécution: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_dashboard_refresh():
    """Tester le rafraîchissement des vues."""
    print("\n" + "="*60)
    print("TEST CELERY - Rafraîchissement Vues")
    print("="*60)

    try:
        print("\n🔄 Exécution de refresh_dashboard_views...")
        result = refresh_dashboard_views()

        print(f"\n✅ Tâche complétée avec succès:")
        print(f"   - Vues totales: {result['views_total']}")
        print(f"   - Vues rafraîchies: {result['views_refreshed']}")
        print(f"   - Vues échouées: {result['views_failed']}")

        return True

    except Exception as e:
        print(f"\n❌ Erreur lors de l'exécution: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_whatsapp():
    """Tester la connexion WhatsApp."""
    print("\n" + "="*60)
    print("TEST CELERY - Connexion WhatsApp")
    print("="*60)

    try:
        print("\n📱 Exécution de test_whatsapp_connection...")
        result = test_whatsapp_connection()

        if result['success']:
            print(f"\n✅ Connexion WhatsApp réussie:")
            print(f"   - Destinataire: {result['recipient']}")
        else:
            print(f"\n⚠️  Connexion WhatsApp échouée:")
            print(f"   - Erreur: {result.get('error', 'Service désactivé')}")

        return result['success']

    except Exception as e:
        print(f"\n❌ Erreur lors de l'exécution: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Menu principal de test."""
    print("\n" + "="*60)
    print("🧪 TEST TÂCHES CELERY - Digiboost PME")
    print("="*60)

    tests = [
        ("Évaluation alertes", test_alert_evaluation),
        ("Rafraîchissement vues", test_dashboard_refresh),
        ("Connexion WhatsApp", test_whatsapp),
    ]

    results = {}

    for test_name, test_func in tests:
        results[test_name] = test_func()

    # Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*60)

    for test_name, success in results.items():
        status = "✅ Succès" if success else "❌ Échec"
        print(f"   {test_name}: {status}")

    total = len(results)
    passed = sum(1 for s in results.values() if s)

    print(f"\nRésultat: {passed}/{total} tests réussis")
    print("="*60 + "\n")

    return all(results.values())


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
