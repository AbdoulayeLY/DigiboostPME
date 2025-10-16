"""
Script de test pour l'intégration WhatsApp avec Twilio.

IMPORTANT: Avant d'exécuter ce script, configurez les variables dans .env:
- TWILIO_ACCOUNT_SID
- TWILIO_AUTH_TOKEN
- TWILIO_WHATSAPP_FROM (optionnel, utilise sandbox par défaut)
- WHATSAPP_ENABLED=True

Pour obtenir les credentials Twilio:
1. Créer compte sur https://www.twilio.com/try-twilio
2. Aller dans Console → WhatsApp → Try it Out
3. Envoyer 'join <code>' au numéro Twilio depuis votre WhatsApp
4. Copier Account SID et Auth Token
"""
from app.integrations.whatsapp import whatsapp_service
from app.integrations.whatsapp_templates import (
    format_test_message,
    format_rupture_stock_message,
    format_low_stock_message
)


def test_whatsapp_status():
    """Tester le statut du service WhatsApp."""
    print("\n" + "="*60)
    print("TEST WHATSAPP - Statut du service")
    print("="*60)

    status = whatsapp_service.get_status()

    print(f"\n✅ Statut:")
    print(f"   - Activé: {status['enabled']}")
    print(f"   - Provider: {status['provider']}")
    print(f"   - Numéro FROM: {status['from_number']}")
    print(f"   - Client initialisé: {status['client_initialized']}")

    if not status['enabled']:
        print("\n❌ WhatsApp est désactivé!")
        print("   Configurez TWILIO_ACCOUNT_SID et TWILIO_AUTH_TOKEN dans .env")
        return False

    if not status['client_initialized']:
        print("\n❌ Client Twilio non initialisé!")
        print("   Vérifiez vos credentials dans .env")
        return False

    print("\n✅ Service WhatsApp prêt!")
    return True


def test_send_simple_message():
    """Tester l'envoi d'un message simple."""
    print("\n" + "="*60)
    print("TEST WHATSAPP - Envoi message simple")
    print("="*60)

    # IMPORTANT: Remplacez par votre numéro WhatsApp
    test_number = input("\n📱 Entrez votre numéro WhatsApp (format: +221771234567): ").strip()

    if not test_number.startswith("+"):
        print("❌ Format invalide. Le numéro doit commencer par +")
        return False

    print(f"\nEnvoi du message de test à {test_number}...")

    message = format_test_message()
    success = whatsapp_service.send_alert(test_number, message)

    if success:
        print(f"\n✅ Message envoyé avec succès à {test_number}!")
        print("   Vérifiez votre WhatsApp dans quelques secondes.")
        return True
    else:
        print(f"\n❌ Échec de l'envoi à {test_number}")
        print("   Vérifiez les logs ci-dessus pour plus de détails.")
        return False


def test_send_alert_templates():
    """Tester les templates d'alertes."""
    print("\n" + "="*60)
    print("TEST WHATSAPP - Templates d'alertes")
    print("="*60)

    test_number = input("\n📱 Entrez votre numéro WhatsApp (format: +221771234567): ").strip()

    if not test_number.startswith("+"):
        print("❌ Format invalide.")
        return False

    # Test message rupture stock
    print("\n1. Test message RUPTURE STOCK...")
    rupture_data = {
        "product_count": 3,
        "product_names": ["Riz 50kg", "Sucre 25kg", "Huile 5L"]
    }
    rupture_msg = format_rupture_stock_message(rupture_data)

    success1 = whatsapp_service.send_alert(test_number, rupture_msg)
    print(f"   {'✅' if success1 else '❌'} Rupture stock")

    # Pause
    import time
    time.sleep(2)

    # Test message stock faible
    print("\n2. Test message STOCK FAIBLE...")
    low_stock_data = {
        "product_count": 5,
        "product_names": ["Café Touba", "Thé Lipton", "Lait Nido", "Detergent Omo", "Savon"]
    }
    low_stock_msg = format_low_stock_message(low_stock_data)

    success2 = whatsapp_service.send_alert(test_number, low_stock_msg)
    print(f"   {'✅' if success2 else '❌'} Stock faible")

    if success1 and success2:
        print("\n✅ Tous les templates fonctionnent!")
        return True
    else:
        print("\n⚠️  Certains envois ont échoué.")
        return False


def test_bulk_send():
    """Tester l'envoi groupé."""
    print("\n" + "="*60)
    print("TEST WHATSAPP - Envoi groupé")
    print("="*60)

    print("\nEntrez plusieurs numéros WhatsApp (un par ligne, vide pour terminer):")
    recipients = []

    while True:
        num = input(f"Numéro {len(recipients) + 1} (ou Entrée pour terminer): ").strip()
        if not num:
            break
        if num.startswith("+"):
            recipients.append(num)
        else:
            print("   ⚠️  Format invalide, ignoré.")

    if not recipients:
        print("❌ Aucun destinataire.")
        return False

    print(f"\nEnvoi groupé à {len(recipients)} destinataire(s)...")

    message = format_test_message()
    results = whatsapp_service.send_bulk_alerts(recipients, message)

    print(f"\n✅ Envois réussis: {len(results['success'])}")
    for num in results['success']:
        print(f"   ✓ {num}")

    if results['failed']:
        print(f"\n❌ Envois échoués: {len(results['failed'])}")
        for num in results['failed']:
            print(f"   ✗ {num}")

    return len(results['success']) > 0


def main():
    """Menu principal de test."""
    print("\n" + "="*60)
    print("🧪 TEST WHATSAPP AVEC TWILIO - Digiboost PME")
    print("="*60)

    # 1. Vérifier le statut
    if not test_whatsapp_status():
        print("\n⚠️  Service WhatsApp non disponible. Arrêt des tests.")
        return

    # Menu de choix
    while True:
        print("\n" + "-"*60)
        print("Choisissez un test:")
        print("  1. Envoyer un message simple")
        print("  2. Tester les templates d'alertes")
        print("  3. Tester l'envoi groupé")
        print("  4. Quitter")
        print("-"*60)

        choice = input("\nVotre choix (1-4): ").strip()

        if choice == "1":
            test_send_simple_message()
        elif choice == "2":
            test_send_alert_templates()
        elif choice == "3":
            test_bulk_send()
        elif choice == "4":
            print("\n👋 Au revoir!")
            break
        else:
            print("❌ Choix invalide.")

    print("\n" + "="*60)
    print("✅ Tests terminés")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
