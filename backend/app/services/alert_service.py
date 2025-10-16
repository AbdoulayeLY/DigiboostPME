"""
Service AlertService - Évaluation et gestion des alertes.
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy import and_, text
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.alert_history import AlertHistory
from app.models.product import Product

logger = logging.getLogger(__name__)


class AlertService:
    """Service d'évaluation et de gestion des alertes."""

    def __init__(self, db: Session):
        self.db = db

    def evaluate_all_alerts(self, tenant_id: UUID) -> List[Dict[str, Any]]:
        """
        Évaluer toutes les alertes actives d'un tenant.

        Args:
            tenant_id: UUID du tenant

        Returns:
            Liste des alertes déclenchées avec leurs résultats
        """
        logger.info(f"Evaluating alerts for tenant {tenant_id}")

        # Récupérer toutes les alertes actives du tenant
        alerts = self.db.query(Alert).filter(
            and_(
                Alert.tenant_id == tenant_id,
                Alert.is_active == True
            )
        ).all()

        logger.info(f"Found {len(alerts)} active alerts for tenant {tenant_id}")

        triggered_alerts = []

        for alert in alerts:
            try:
                # Évaluer selon le type d'alerte
                if alert.alert_type == "RUPTURE_STOCK":
                    result = self._evaluate_rupture_stock(alert)
                elif alert.alert_type == "LOW_STOCK":
                    result = self._evaluate_low_stock(alert)
                elif alert.alert_type == "BAISSE_TAUX_SERVICE":
                    result = self._evaluate_taux_service(alert)
                else:
                    logger.warning(f"Unknown alert type: {alert.alert_type}")
                    continue

                # Si déclenchée, vérifier déduplication
                if result["triggered"]:
                    product_ids = result.get("products", [])
                    if not self._is_duplicate(alert.id, product_ids):
                        triggered_alerts.append({
                            "alert": alert,
                            "result": result
                        })
                        logger.info(f"Alert {alert.name} triggered: {result['message']}")
                    else:
                        logger.debug(f"Alert {alert.name} is duplicate, skipping")

            except Exception as e:
                logger.error(f"Error evaluating alert {alert.id}: {str(e)}", exc_info=True)
                continue

        logger.info(f"Total triggered alerts: {len(triggered_alerts)}")
        return triggered_alerts

    def _evaluate_rupture_stock(self, alert: Alert) -> Dict[str, Any]:
        """
        Évaluer condition rupture de stock.

        Args:
            alert: Configuration de l'alerte

        Returns:
            Dictionnaire avec triggered, products, message, severity, details
        """
        conditions = alert.conditions

        # Query produits en rupture (stock = 0)
        query = self.db.query(Product).filter(
            and_(
                Product.tenant_id == alert.tenant_id,
                Product.current_stock == 0,
                Product.is_active == True
            )
        )

        # Filtres optionnels sur produits spécifiques
        if conditions.get("product_ids"):
            query = query.filter(Product.id.in_(conditions["product_ids"]))

        # Filtres optionnels sur catégories
        if conditions.get("category_ids"):
            query = query.filter(Product.category_id.in_(conditions["category_ids"]))

        products = query.all()

        if not products:
            return {"triggered": False, "products": []}

        # Construire message
        product_names = [p.name for p in products[:5]]
        message = f"🚨 RUPTURE STOCK - {len(products)} produit(s) en rupture"

        if len(products) <= 5:
            message += f": {', '.join(product_names)}"
        else:
            message += f": {', '.join(product_names)} et {len(products) - 5} autre(s)"

        # Déterminer sévérité
        severity = "CRITICAL" if len(products) > 10 else "HIGH"

        return {
            "triggered": True,
            "products": [str(p.id) for p in products],
            "message": message,
            "severity": severity,
            "details": {
                "product_count": len(products),
                "product_names": product_names,
                "product_ids": [str(p.id) for p in products]
            }
        }

    def _evaluate_low_stock(self, alert: Alert) -> Dict[str, Any]:
        """
        Évaluer condition stock faible.

        Args:
            alert: Configuration de l'alerte

        Returns:
            Dictionnaire avec triggered, products, message, severity, details
        """
        conditions = alert.conditions

        # Query produits avec stock faible (0 < stock <= min_stock)
        query = self.db.query(Product).filter(
            and_(
                Product.tenant_id == alert.tenant_id,
                Product.current_stock > 0,
                Product.current_stock <= Product.min_stock,
                Product.is_active == True
            )
        )

        # Filtres optionnels
        if conditions.get("product_ids"):
            query = query.filter(Product.id.in_(conditions["product_ids"]))

        if conditions.get("category_ids"):
            query = query.filter(Product.category_id.in_(conditions["category_ids"]))

        products = query.all()

        if not products:
            return {"triggered": False, "products": []}

        # Construire message
        product_names = [p.name for p in products[:5]]
        message = f"⚠️ STOCK FAIBLE - {len(products)} produit(s) sous le seuil minimum"

        if len(products) <= 5:
            message += f": {', '.join(product_names)}"
        else:
            message += f": {', '.join(product_names)} et {len(products) - 5} autre(s)"

        # Déterminer sévérité
        severity = "MEDIUM" if len(products) < 5 else "HIGH"

        return {
            "triggered": True,
            "products": [str(p.id) for p in products],
            "message": message,
            "severity": severity,
            "details": {
                "product_count": len(products),
                "product_names": product_names,
                "product_ids": [str(p.id) for p in products]
            }
        }

    def _evaluate_taux_service(self, alert: Alert) -> Dict[str, Any]:
        """
        Évaluer taux de service.

        Args:
            alert: Configuration de l'alerte

        Returns:
            Dictionnaire avec triggered, message, severity, details
        """
        conditions = alert.conditions
        threshold = conditions.get("threshold", 90)  # Seuil par défaut 90%

        # Calculer taux de service sur les 7 derniers jours
        query = text("""
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'DELIVERED' THEN 1 END) as delivered
            FROM sales
            WHERE tenant_id = :tenant_id
                AND sale_date >= CURRENT_DATE - INTERVAL '7 days'
        """)

        result = self.db.execute(query, {"tenant_id": alert.tenant_id}).first()

        if not result or result.total == 0:
            return {"triggered": False, "products": []}

        taux_service = (result.delivered / result.total) * 100

        if taux_service >= threshold:
            return {"triggered": False, "products": []}

        message = f"📉 TAUX SERVICE FAIBLE - {taux_service:.1f}% (seuil: {threshold}%)"

        # Déterminer sévérité
        severity = "MEDIUM" if taux_service > threshold - 10 else "HIGH"

        return {
            "triggered": True,
            "products": [],
            "message": message,
            "severity": severity,
            "details": {
                "taux_service": round(taux_service, 2),
                "threshold": threshold,
                "total_orders": result.total,
                "delivered_orders": result.delivered
            }
        }

    def _is_duplicate(self, alert_id: UUID, product_ids: List[str]) -> bool:
        """
        Vérifier si une alerte similaire a été envoyée récemment.
        Déduplication: même alerte + mêmes produits dans les 30 dernières minutes.

        Args:
            alert_id: UUID de l'alerte
            product_ids: Liste des IDs produits concernés

        Returns:
            True si duplicate, False sinon
        """
        thirty_minutes_ago = datetime.utcnow() - timedelta(minutes=30)

        # Chercher alertes récentes (30 min)
        recent = self.db.query(AlertHistory).filter(
            and_(
                AlertHistory.alert_id == alert_id,
                AlertHistory.triggered_at >= thirty_minutes_ago
            )
        ).first()

        if not recent:
            return False

        # Comparer les produits concernés
        recent_products = set(recent.details.get("product_ids", []))
        current_products = set(product_ids)

        # Pour les alertes sans produits (ex: BAISSE_TAUX_SERVICE),
        # considérer comme duplicate si même alerte dans les 30 dernières minutes
        if len(recent_products) == 0 and len(current_products) == 0:
            logger.debug(
                f"Duplicate detected for alert {alert_id}: "
                f"same alert type without products within 30 minutes"
            )
            return True

        # Si 80%+ des produits sont identiques, considérer comme duplicate
        if len(recent_products) > 0:
            overlap = len(recent_products & current_products)
            similarity = overlap / len(recent_products)

            if similarity > 0.8:
                logger.debug(
                    f"Duplicate detected for alert {alert_id}: "
                    f"similarity {similarity:.2%}"
                )
                return True

        return False

    def create_history_entry(
        self,
        alert: Alert,
        result: Dict[str, Any]
    ) -> AlertHistory:
        """
        Créer une entrée dans l'historique des alertes.

        Args:
            alert: Configuration de l'alerte
            result: Résultat de l'évaluation

        Returns:
            AlertHistory créé
        """
        history = AlertHistory(
            tenant_id=alert.tenant_id,
            alert_id=alert.id,
            triggered_at=datetime.utcnow(),
            alert_type=alert.alert_type,
            severity=result["severity"],
            message=result["message"],
            details=result["details"]
        )

        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)

        logger.info(
            f"Created alert history {history.id} for alert {alert.name} "
            f"(severity: {result['severity']})"
        )

        return history

    def send_alert_notifications(
        self,
        alert: Alert,
        result: Dict[str, Any],
        history: AlertHistory
    ) -> None:
        """
        Envoyer notifications selon les canaux configurés.

        Args:
            alert: Configuration de l'alerte
            result: Résultat de l'évaluation
            history: Entrée historique créée
        """
        channels = alert.channels
        recipients = alert.recipients

        # Formatter message WhatsApp
        from app.integrations.whatsapp_templates import format_alert_message
        whatsapp_message = format_alert_message(alert.alert_type, result["details"])

        # Backward compatibility: gérer ancien format (list) et nouveau format (dict)
        if isinstance(channels, list):
            logger.warning(f"Alert {alert.id} uses old format (list) for channels, migrating...")
            should_send_whatsapp = "whatsapp" in channels
            should_send_email = "email" in channels
        else:
            should_send_whatsapp = channels.get("whatsapp", False)
            should_send_email = channels.get("email", False)

        if isinstance(recipients, list):
            logger.warning(f"Alert {alert.id} uses old format (list) for recipients, migrating...")
            # Séparer numéros de téléphone et emails
            whatsapp_numbers = [r for r in recipients if r.startswith("+")]
            emails = [r for r in recipients if "@" in r]
        else:
            whatsapp_numbers = recipients.get("whatsapp_numbers", [])
            emails = recipients.get("emails", [])

        # Envoi WhatsApp
        if should_send_whatsapp and whatsapp_numbers:
            from app.integrations.whatsapp import whatsapp_service

            logger.info(f"Sending WhatsApp alerts to {len(whatsapp_numbers)} recipient(s)")

            results = whatsapp_service.send_bulk_alerts(whatsapp_numbers, whatsapp_message)

            # Mettre à jour historique si au moins un envoi réussi
            if results["success"]:
                history.sent_whatsapp = True
                self.db.commit()
                logger.info(
                    f"WhatsApp sent: {len(results['success'])}/{len(whatsapp_numbers)} "
                    f"(failed: {len(results['failed'])})"
                )
            else:
                logger.error(f"All WhatsApp sends failed for alert {alert.id}")

        # Email (à implémenter Sprint 4)
        if should_send_email and emails:
            logger.info("Email notifications not implemented yet")
            # TODO: Implémenter envoi email
