"""
Script de generation de donnees de simulation pour toutes les tables.
Execute avec: python seed_data.py
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import random

# Ajouter le repertoire backend au path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.tenant import Tenant
from app.models.user import User
from app.models.category import Category
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.sale import Sale
from app.models.stock_movement import StockMovement
from app.models.alert import Alert
from app.models.alert_history import AlertHistory
from app.core.security import get_password_hash


def create_tenant(db: Session) -> Tenant:
    """Creer un tenant de test"""
    print("Creation du tenant...")
    tenant = Tenant(
        name="Boutique Digiboost Test",
        ninea="123456789",
        email="test@digiboost.sn",
        phone="+221771234567",
        settings={
            "currency": "XOF",
            "timezone": "Africa/Dakar",
            "low_stock_threshold": 10,
            "sales_target_monthly": 5000000
        },
        is_active=True
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    print(f"  ✓ Tenant cree: {tenant.name} (ID: {tenant.id})")
    return tenant


def create_users(db: Session, tenant_id: uuid.UUID) -> list:
    """Creer des utilisateurs de test"""
    print("Creation des utilisateurs...")
    users_data = [
        {
            "email": "admin@digiboost.sn",
            "full_name": "Amadou Diallo",
            "role": "admin",
            "whatsapp_number": "+221771234567"
        },
        {
            "email": "manager@digiboost.sn",
            "full_name": "Fatou Sall",
            "role": "manager",
            "whatsapp_number": "+221772345678"
        },
        {
            "email": "user@digiboost.sn",
            "full_name": "Moussa Ndiaye",
            "role": "user",
            "whatsapp_number": "+221773456789"
        }
    ]

    users = []
    for user_data in users_data:
        user = User(
            tenant_id=tenant_id,
            email=user_data["email"],
            hashed_password=get_password_hash("password123"),
            full_name=user_data["full_name"],
            role=user_data["role"],
            whatsapp_number=user_data["whatsapp_number"],
            is_active=True
        )
        db.add(user)
        users.append(user)

    db.commit()
    for user in users:
        db.refresh(user)
        print(f"  ✓ User cree: {user.email} ({user.role})")

    return users


def create_categories(db: Session, tenant_id: uuid.UUID) -> list:
    """Creer des categories de produits"""
    print("Creation des categories...")
    categories_data = [
        {"name": "Alimentation", "description": "Produits alimentaires"},
        {"name": "Boissons", "description": "Boissons diverses"},
        {"name": "Hygiene", "description": "Produits d'hygiene"},
        {"name": "Electronique", "description": "Appareils electroniques"},
        {"name": "Textile", "description": "Vetements et tissus"}
    ]

    categories = []
    for cat_data in categories_data:
        category = Category(
            tenant_id=tenant_id,
            name=cat_data["name"],
            description=cat_data["description"]
        )
        db.add(category)
        categories.append(category)

    db.commit()
    for cat in categories:
        db.refresh(cat)
        print(f"  ✓ Categorie creee: {cat.name}")

    return categories


def create_suppliers(db: Session, tenant_id: uuid.UUID) -> list:
    """Creer des fournisseurs"""
    print("Creation des fournisseurs...")
    suppliers_data = [
        {
            "code": "FRN001",
            "name": "SICAP Distribution",
            "contact_name": "Ibrahima Ba",
            "phone": "+221338234567",
            "email": "contact@sicap-distrib.sn",
            "lead_time_days": 2
        },
        {
            "code": "FRN002",
            "name": "Grands Moulins de Dakar",
            "contact_name": "Awa Gueye",
            "phone": "+221338345678",
            "email": "gmd@gmd.sn",
            "lead_time_days": 3
        },
        {
            "code": "FRN003",
            "name": "Senegal Electronique",
            "contact_name": "Omar Sy",
            "phone": "+221338456789",
            "email": "info@senelec.sn",
            "lead_time_days": 5
        }
    ]

    suppliers = []
    for sup_data in suppliers_data:
        supplier = Supplier(
            tenant_id=tenant_id,
            code=sup_data["code"],
            name=sup_data["name"],
            contact_name=sup_data["contact_name"],
            phone=sup_data["phone"],
            email=sup_data["email"],
            lead_time_days=sup_data["lead_time_days"]
        )
        db.add(supplier)
        suppliers.append(supplier)

    db.commit()
    for sup in suppliers:
        db.refresh(sup)
        print(f"  ✓ Fournisseur cree: {sup.name}")

    return suppliers


def create_products(db: Session, tenant_id: uuid.UUID, categories: list, suppliers: list) -> list:
    """Creer des produits avec stock"""
    print("Creation des produits...")
    products_data = [
        # Alimentation
        {"code": "RIZ001", "name": "Riz Brisure 50kg", "category_idx": 0, "supplier_idx": 1,
         "purchase_price": 18000, "sale_price": 22000, "unit": "sac", "current_stock": 45, "min_stock": 20, "max_stock": 100},
        {"code": "HUILE001", "name": "Huile Vegetale 5L", "category_idx": 0, "supplier_idx": 0,
         "purchase_price": 4500, "sale_price": 5500, "unit": "bidon", "current_stock": 30, "min_stock": 15, "max_stock": 50},
        {"code": "SUCRE001", "name": "Sucre 50kg", "category_idx": 0, "supplier_idx": 1,
         "purchase_price": 25000, "sale_price": 30000, "unit": "sac", "current_stock": 8, "min_stock": 10, "max_stock": 40},

        # Boissons
        {"code": "EAU001", "name": "Eau Kirene 1.5L Pack 6", "category_idx": 1, "supplier_idx": 0,
         "purchase_price": 1800, "sale_price": 2200, "unit": "pack", "current_stock": 120, "min_stock": 50, "max_stock": 200},
        {"code": "JUS001", "name": "Jus Pomme Happy 1L", "category_idx": 1, "supplier_idx": 0,
         "purchase_price": 1200, "sale_price": 1500, "unit": "unite", "current_stock": 65, "min_stock": 30, "max_stock": 100},

        # Hygiene
        {"code": "SAV001", "name": "Savon Imperial x50", "category_idx": 2, "supplier_idx": 0,
         "purchase_price": 8500, "sale_price": 10500, "unit": "carton", "current_stock": 25, "min_stock": 10, "max_stock": 50},
        {"code": "DET001", "name": "Detergent Omo 1kg", "category_idx": 2, "supplier_idx": 0,
         "purchase_price": 2800, "sale_price": 3500, "unit": "paquet", "current_stock": 5, "min_stock": 15, "max_stock": 60},

        # Electronique
        {"code": "TEL001", "name": "Telephone Samsung A14", "category_idx": 3, "supplier_idx": 2,
         "purchase_price": 85000, "sale_price": 105000, "unit": "unite", "current_stock": 12, "min_stock": 5, "max_stock": 20},
        {"code": "CHAR001", "name": "Chargeur USB-C Rapide", "category_idx": 3, "supplier_idx": 2,
         "purchase_price": 5000, "sale_price": 7500, "unit": "unite", "current_stock": 35, "min_stock": 10, "max_stock": 50},

        # Textile
        {"code": "WAX001", "name": "Pagne Wax 6 yards", "category_idx": 4, "supplier_idx": 0,
         "purchase_price": 12000, "sale_price": 18000, "unit": "piece", "current_stock": 20, "min_stock": 10, "max_stock": 40}
    ]

    products = []
    for prod_data in products_data:
        product = Product(
            tenant_id=tenant_id,
            code=prod_data["code"],
            name=prod_data["name"],
            category_id=categories[prod_data["category_idx"]].id,
            supplier_id=suppliers[prod_data["supplier_idx"]].id,
            purchase_price=Decimal(str(prod_data["purchase_price"])),
            sale_price=Decimal(str(prod_data["sale_price"])),
            unit=prod_data["unit"],
            current_stock=Decimal(str(prod_data["current_stock"])),
            min_stock=Decimal(str(prod_data["min_stock"])),
            max_stock=Decimal(str(prod_data["max_stock"])),
            barcode=f"SN{prod_data['code']}",
            is_active=True
        )
        db.add(product)
        products.append(product)

    db.commit()
    for prod in products:
        db.refresh(prod)
        print(f"  ✓ Produit cree: {prod.name} (Stock: {prod.current_stock})")

    return products


def create_stock_movements(db: Session, tenant_id: uuid.UUID, products: list) -> list:
    """Creer des mouvements de stock historiques"""
    print("Creation des mouvements de stock...")
    movements = []

    # Generer des mouvements pour les 30 derniers jours
    for product in products:
        # Entree initiale de stock
        movement = StockMovement(
            tenant_id=tenant_id,
            product_id=product.id,
            movement_date=datetime.now() - timedelta(days=30),
            movement_type="IN",
            quantity=product.current_stock + Decimal(str(random.randint(10, 50))),
            reference=f"INIT-{product.code}",
            reason="Stock initial"
        )
        db.add(movement)
        movements.append(movement)

        # Quelques sorties aleatoires
        num_out = random.randint(2, 5)
        for i in range(num_out):
            days_ago = random.randint(1, 29)
            quantity_out = Decimal(str(random.randint(1, 10)))
            movement = StockMovement(
                tenant_id=tenant_id,
                product_id=product.id,
                movement_date=datetime.now() - timedelta(days=days_ago),
                movement_type="OUT",
                quantity=quantity_out,
                reference=f"SALE-{random.randint(1000, 9999)}",
                reason="Vente"
            )
            db.add(movement)
            movements.append(movement)

    db.commit()
    print(f"  ✓ {len(movements)} mouvements de stock crees")
    return movements


def create_sales(db: Session, tenant_id: uuid.UUID, products: list) -> list:
    """Creer des ventes historiques"""
    print("Creation des ventes...")
    sales = []

    # Generer des ventes pour les 30 derniers jours
    for _ in range(50):
        product = random.choice(products)
        days_ago = random.randint(0, 30)
        quantity = Decimal(str(random.randint(1, 5)))
        unit_price = product.sale_price

        sale = Sale(
            tenant_id=tenant_id,
            product_id=product.id,
            sale_date=datetime.now() - timedelta(days=days_ago),
            quantity=quantity,
            unit_price=unit_price,
            total_amount=quantity * unit_price,
            order_number=f"ORD-{random.randint(10000, 99999)}",
            customer_name=random.choice([
                "Mamadou Diop", "Aissatou Fall", "Cheikh Mbaye",
                "Marieme Sow", "Boubacar Kane", None
            ]),
            status=random.choice(["completed", "completed", "completed", "pending"])
        )
        db.add(sale)
        sales.append(sale)

    db.commit()
    print(f"  ✓ {len(sales)} ventes creees")
    return sales


def create_alerts(db: Session, tenant_id: uuid.UUID) -> list:
    """Creer des configurations d'alertes"""
    print("Creation des alertes...")
    alerts_data = [
        {
            "name": "Stock Faible",
            "alert_type": "LOW_STOCK",
            "conditions": {"threshold_type": "min_stock", "operator": "<="},
            "channels": ["whatsapp", "email"],
            "recipients": ["+221771234567", "admin@digiboost.sn"]
        },
        {
            "name": "Rupture de Stock",
            "alert_type": "OUT_OF_STOCK",
            "conditions": {"threshold": 0, "operator": "=="},
            "channels": ["whatsapp"],
            "recipients": ["+221771234567", "+221772345678"]
        },
        {
            "name": "Objectif Ventes Mensuel",
            "alert_type": "SALES_TARGET",
            "conditions": {"target": 5000000, "period": "monthly"},
            "channels": ["email"],
            "recipients": ["admin@digiboost.sn", "manager@digiboost.sn"]
        }
    ]

    alerts = []
    for alert_data in alerts_data:
        alert = Alert(
            tenant_id=tenant_id,
            name=alert_data["name"],
            alert_type=alert_data["alert_type"],
            conditions=alert_data["conditions"],
            channels=alert_data["channels"],
            recipients=alert_data["recipients"],
            is_active=True
        )
        db.add(alert)
        alerts.append(alert)

    db.commit()
    for alert in alerts:
        db.refresh(alert)
        print(f"  ✓ Alerte creee: {alert.name}")

    return alerts


def create_alert_history(db: Session, tenant_id: uuid.UUID, alerts: list, products: list) -> list:
    """Creer l'historique des alertes declenchees"""
    print("Creation de l'historique des alertes...")
    history = []

    # Generer quelques alertes declenchees
    low_stock_alert = next((a for a in alerts if a.alert_type == "LOW_STOCK"), None)
    if low_stock_alert:
        # Alertes pour produits en stock faible
        low_stock_products = [p for p in products if p.min_stock and p.current_stock <= p.min_stock]
        for product in low_stock_products:
            days_ago = random.randint(1, 7)
            alert_hist = AlertHistory(
                tenant_id=tenant_id,
                alert_id=low_stock_alert.id,
                triggered_at=datetime.now() - timedelta(days=days_ago),
                alert_type="LOW_STOCK",
                severity="warning",
                message=f"Stock faible pour {product.name}",
                details={
                    "product_id": str(product.id),
                    "product_name": product.name,
                    "current_stock": float(product.current_stock),
                    "min_stock": float(product.min_stock)
                },
                sent_whatsapp=True,
                sent_email=True
            )
            db.add(alert_hist)
            history.append(alert_hist)

    db.commit()
    print(f"  ✓ {len(history)} entrees d'historique d'alertes creees")
    return history


def seed_all():
    """Fonction principale pour generer toutes les donnees"""
    print("\n" + "="*60)
    print("GENERATION DES DONNEES DE SIMULATION")
    print("="*60 + "\n")

    db = SessionLocal()
    try:
        # Verifier si des donnees existent deja
        existing_tenant = db.query(Tenant).first()
        if existing_tenant:
            print("⚠️  Des donnees existent deja dans la base.")
            response = input("Voulez-vous supprimer toutes les donnees et recommencer? (oui/non): ")
            if response.lower() not in ['oui', 'yes', 'o', 'y']:
                print("Operation annulee.")
                return

            # Supprimer toutes les donnees (CASCADE supprimera tout)
            print("\nSuppression des donnees existantes...")
            db.query(Tenant).delete()
            db.commit()
            print("  ✓ Donnees supprimees\n")

        # Creation des donnees
        tenant = create_tenant(db)
        users = create_users(db, tenant.id)
        categories = create_categories(db, tenant.id)
        suppliers = create_suppliers(db, tenant.id)
        products = create_products(db, tenant.id, categories, suppliers)
        stock_movements = create_stock_movements(db, tenant.id, products)
        sales = create_sales(db, tenant.id, products)
        alerts = create_alerts(db, tenant.id)
        alert_history = create_alert_history(db, tenant.id, alerts, products)

        print("\n" + "="*60)
        print("RESUME DES DONNEES GENEREES")
        print("="*60)
        print(f"Tenants:           {1}")
        print(f"Utilisateurs:      {len(users)}")
        print(f"Categories:        {len(categories)}")
        print(f"Fournisseurs:      {len(suppliers)}")
        print(f"Produits:          {len(products)}")
        print(f"Mouvements stock:  {len(stock_movements)}")
        print(f"Ventes:            {len(sales)}")
        print(f"Alertes:           {len(alerts)}")
        print(f"Historique alertes: {len(alert_history)}")
        print("="*60)
        print("\n✅ Generation terminee avec succes!\n")

        print("INFORMATIONS DE CONNEXION:")
        print("-" * 60)
        print(f"Email:     admin@digiboost.sn")
        print(f"Password:  password123")
        print(f"Tenant ID: {tenant.id}")
        print("-" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ Erreur lors de la generation: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()
