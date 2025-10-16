"""
Templates de messages WhatsApp pour les alertes.
"""
from typing import Any, Dict


def format_rupture_stock_message(data: Dict[str, Any]) -> str:
    """
    Formatter message pour alerte rupture de stock.

    Args:
        data: Détails de l'alerte contenant product_count, product_names, etc.

    Returns:
        str: Message formaté pour WhatsApp
    """
    product_names = data.get("product_names", [])
    product_count = data.get("product_count", 0)

    message = f"""🚨 *ALERTE RUPTURE STOCK*

Nombre de produits en rupture: *{product_count}*

Produits concernés:
"""

    for name in product_names[:5]:
        message += f"  • {name}\n"

    if product_count > 5:
        message += f"  ... et {product_count - 5} autre(s)\n"

    message += """
⚠️  Action requise: Commander ces produits rapidement

_Digiboost PME - Intelligence Supply Chain_"""

    return message


def format_low_stock_message(data: Dict[str, Any]) -> str:
    """
    Formatter message pour alerte stock faible.

    Args:
        data: Détails de l'alerte contenant product_count, product_names, etc.

    Returns:
        str: Message formaté pour WhatsApp
    """
    product_names = data.get("product_names", [])
    product_count = data.get("product_count", 0)

    message = f"""⚠️  *ALERTE STOCK FAIBLE*

Nombre de produits sous le seuil: *{product_count}*

Produits à réapprovisionner:
"""

    for name in product_names[:5]:
        message += f"  • {name}\n"

    if product_count > 5:
        message += f"  ... et {product_count - 5} autre(s)\n"

    message += """
📦 Suggestion: Passer commande avant rupture

_Digiboost PME_"""

    return message


def format_taux_service_message(data: Dict[str, Any]) -> str:
    """
    Formatter message pour alerte baisse taux de service.

    Args:
        data: Détails de l'alerte contenant taux_service, threshold, etc.

    Returns:
        str: Message formaté pour WhatsApp
    """
    taux = data.get("taux_service", 0)
    threshold = data.get("threshold", 90)
    total_orders = data.get("total_orders", 0)
    delivered_orders = data.get("delivered_orders", 0)

    message = f"""📉 *ALERTE PERFORMANCE*

Taux de service actuel: *{taux:.1f}%*
Objectif: {threshold}%

Sur 7 derniers jours:
  • Total commandes: {total_orders}
  • Livrées: {delivered_orders}

⚠️  Performance en baisse, vérifier les causes

_Digiboost PME_"""

    return message


def format_alert_message(alert_type: str, data: Dict[str, Any]) -> str:
    """
    Formatter message d'alerte selon le type.

    Args:
        alert_type: Type d'alerte (RUPTURE_STOCK, LOW_STOCK, BAISSE_TAUX_SERVICE)
        data: Détails de l'alerte

    Returns:
        str: Message formaté pour WhatsApp
    """
    if alert_type == "RUPTURE_STOCK":
        return format_rupture_stock_message(data)
    elif alert_type == "LOW_STOCK":
        return format_low_stock_message(data)
    elif alert_type == "BAISSE_TAUX_SERVICE":
        return format_taux_service_message(data)
    else:
        # Message générique pour types inconnus
        return f"⚠️  Alerte: {data.get('message', 'Notification')}"


def format_test_message() -> str:
    """
    Créer un message de test pour vérifier l'intégration WhatsApp.

    Returns:
        str: Message de test formaté
    """
    return """🧪 *TEST DIGIBOOST PME*

Ceci est un message de test pour vérifier l'intégration WhatsApp.

Si vous recevez ce message, l'intégration fonctionne correctement ! ✅

_Digiboost PME - Intelligence Supply Chain_"""
