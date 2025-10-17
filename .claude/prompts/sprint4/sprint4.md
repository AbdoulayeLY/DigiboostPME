# PROMPTS CLAUDE CODE - SPRINT 4
## Rapports & Finitions (Semaines 7-8)

**Objectif Sprint** : Rapports automatisés + Polish + Préparation Agent IA  
**Valeur Métier** : Automatiser reporting + Livrer POC production-ready  
**Durée** : 2 semaines (80 heures)

---

## 📋 TABLE DES MATIÈRES

1. [Vue d'Ensemble Sprint 4](#vue-densemble-sprint-4)
2. [Semaine 7 : Génération Rapports](#semaine-7--génération-rapports)
3. [Semaine 8 : Tests & Documentation](#semaine-8--tests--documentation)

---

## VUE D'ENSEMBLE SPRINT 4

### Fonctionnalités à Implémenter

**3 Rapports Standards** :
1. **Inventaire Stock** : Liste complète produits (Excel)
2. **Synthèse Mensuelle** : KPIs + graphiques (PDF)
3. **Analyse Ventes Détaillée** : Ventes par produit/catégorie (Excel multi-onglets)

**Backend** :
- Service génération Excel (openpyxl)
- Service génération PDF (ReportLab)
- Tâches Celery rapports auto
- Envoi email + WhatsApp rapports
- Vues SQL pour Agent IA

**Frontend** :
- Page génération rapports
- Liste rapports générés
- Configuration rapports automatiques
- Téléchargement rapports

**Finitions** :
- Tests E2E (Playwright)
- Optimisation performance
- Documentation utilisateur
- Guide déploiement

---

## SEMAINE 7 : GÉNÉRATION RAPPORTS

### 🔧 PROMPT 4.1 : Service Génération Rapports Excel

```
CONTEXTE:
Tous les dashboards sont fonctionnels. Je dois créer le service de génération de rapports Excel automatisés.

OBJECTIF:
Créer service ReportService avec:
- Rapport Inventaire Stock (Excel simple)
- Rapport Analyse Ventes (Excel multi-onglets)
- Formatage professionnel (couleurs, bordures)
- Graphiques Excel embarqués
- Stockage fichiers générés

SPÉCIFICATIONS TECHNIQUES:

DÉPENDANCES (requirements.txt - ajouter):
```
openpyxl==3.1.2
reportlab==4.0.7
xlsxwriter==3.1.9
```

SERVICE RAPPORTS (app/services/report_service.py):
```python
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from io import BytesIO
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference
from app.models.product import Product
from app.models.sale import Sale
from app.models.category import Category

class ReportService:
    def __init__(self, db: Session):
        self.db = db
    
    def generate_inventory_report(
        self,
        tenant_id: UUID
    ) -> BytesIO:
        """
        Rapport Inventaire Stock (Excel)
        
        Colonnes:
        - Code
        - Nom
        - Catégorie
        - Stock Actuel
        - Stock Min
        - Stock Max
        - Statut
        - Valorisation
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Inventaire Stock"
        
        # En-tête rapport
        ws['A1'] = "RAPPORT INVENTAIRE STOCK"
        ws['A1'].font = Font(size=16, bold=True)
        ws['A2'] = f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        # En-têtes colonnes
        headers = [
            "Code", "Nom Produit", "Catégorie", "Stock Actuel",
            "Stock Min", "Stock Max", "Unité", "Statut",
            "Prix Achat", "Valorisation"
        ]
        
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=4, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="4F46E5", end_color="4F46E5", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")
        
        # Données
        products = self.db.query(Product).filter(
            Product.tenant_id == tenant_id,
            Product.is_active == True
        ).order_by(Product.name).all()
        
        row = 5
        for product in products:
            # Calculer statut
            status = self._calculate_status(product)
            valorisation = product.current_stock * product.purchase_price
            
            ws.cell(row, 1, product.code)
            ws.cell(row, 2, product.name)
            ws.cell(row, 3, product.category.name if product.category else "-")
            ws.cell(row, 4, float(product.current_stock))
            ws.cell(row, 5, float(product.min_stock or 0))
            ws.cell(row, 6, float(product.max_stock or 0))
            ws.cell(row, 7, product.unit)
            ws.cell(row, 8, status)
            ws.cell(row, 9, float(product.purchase_price))
            ws.cell(row, 10, float(valorisation))
            
            # Coloration statut
            status_cell = ws.cell(row, 8)
            if status == "RUPTURE":
                status_cell.fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
                status_cell.font = Font(color="991B1B", bold=True)
            elif status == "FAIBLE":
                status_cell.fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
                status_cell.font = Font(color="92400E", bold=True)
            
            row += 1
        
        # Totaux
        row += 1
        ws.cell(row, 9, "TOTAL:")
        ws.cell(row, 9).font = Font(bold=True)
        ws.cell(row, 10, f"=SUM(J5:J{row-2})")
        ws.cell(row, 10).font = Font(bold=True)
        ws.cell(row, 10).number_format = '#,##0'
        
        # Ajuster largeurs colonnes
        column_widths = [12, 30, 20, 12, 12, 12, 10, 15, 15, 18]
        for i, width in enumerate(column_widths, start=1):
            ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width
        
        # Bordures
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        for row in ws[f'A4:J{row}']:
            for cell in row:
                cell.border = thin_border
        
        # Sauvegarder dans BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        return output
    
    def generate_sales_analysis_report(
        self,
        tenant_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> BytesIO:
        """
        Rapport Analyse Ventes (Excel multi-onglets)
        
        Onglets:
        1. Synthèse
        2. Ventes par Produit
        3. Ventes par Catégorie
        4. Évolution Quotidienne
        """
        wb = openpyxl.Workbook()
        
        # ONGLET 1: Synthèse
        ws_summary = wb.active
        ws_summary.title = "Synthèse"
        
        # Période
        ws_summary['A1'] = "ANALYSE VENTES"
        ws_summary['A1'].font = Font(size=16, bold=True)
        ws_summary['A2'] = f"Période: {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}"
        
        # KPIs
        from sqlalchemy import func
        kpis = self.db.query(
            func.count(Sale.id).label('transactions'),
            func.sum(Sale.quantity).label('units'),
            func.sum(Sale.total_amount).label('revenue')
        ).filter(
            Sale.tenant_id == tenant_id,
            Sale.sale_date >= start_date,
            Sale.sale_date <= end_date
        ).first()
        
        ws_summary['A4'] = "Indicateurs Clés"
        ws_summary['A4'].font = Font(bold=True, size=12)
        
        ws_summary['A6'] = "Nombre de transactions:"
        ws_summary['B6'] = kpis.transactions or 0
        ws_summary['B6'].font = Font(bold=True)
        
        ws_summary['A7'] = "Unités vendues:"
        ws_summary['B7'] = float(kpis.units or 0)
        ws_summary['B7'].font = Font(bold=True)
        
        ws_summary['A8'] = "Chiffre d'affaires:"
        ws_summary['B8'] = float(kpis.revenue or 0)
        ws_summary['B8'].font = Font(bold=True)
        ws_summary['B8'].number_format = '#,##0 "FCFA"'
        
        ws_summary['A9'] = "Panier moyen:"
        if kpis.transactions and kpis.transactions > 0:
            ws_summary['B9'] = float(kpis.revenue or 0) / kpis.transactions
        else:
            ws_summary['B9'] = 0
        ws_summary['B9'].font = Font(bold=True)
        ws_summary['B9'].number_format = '#,##0 "FCFA"'
        
        # ONGLET 2: Ventes par Produit
        ws_products = wb.create_sheet("Ventes par Produit")
        
        headers = ["Code", "Nom Produit", "Catégorie", "Quantité", "CA", "Transactions"]
        for col, header in enumerate(headers, start=1):
            cell = ws_products.cell(1, col, header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="4F46E5", end_color="4F46E5", fill_type="solid")
            cell.font = Font(bold=True, color="FFFFFF")
        
        # Données ventes par produit
        from sqlalchemy import text
        query = text("""
            SELECT 
                p.code,
                p.name,
                c.name as category,
                SUM(s.quantity) as quantity,
                SUM(s.total_amount) as revenue,
                COUNT(s.id) as transactions
            FROM products p
            LEFT JOIN sales s ON p.id = s.product_id 
                AND s.sale_date >= :start_date 
                AND s.sale_date <= :end_date
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.tenant_id = :tenant_id
                AND s.id IS NOT NULL
            GROUP BY p.id, p.code, p.name, c.name
            ORDER BY SUM(s.total_amount) DESC
        """)
        
        results = self.db.execute(query, {
            "tenant_id": tenant_id,
            "start_date": start_date,
            "end_date": end_date
        }).fetchall()
        
        for row_idx, result in enumerate(results, start=2):
            ws_products.cell(row_idx, 1, result.code)
            ws_products.cell(row_idx, 2, result.name)
            ws_products.cell(row_idx, 3, result.category)
            ws_products.cell(row_idx, 4, float(result.quantity))
            ws_products.cell(row_idx, 5, float(result.revenue))
            ws_products.cell(row_idx, 5).number_format = '#,##0'
            ws_products.cell(row_idx, 6, result.transactions)
        
        # Graphique Top 10
        if len(results) > 0:
            chart = BarChart()
            chart.title = "Top 10 Produits (CA)"
            chart.x_axis.title = "Produits"
            chart.y_axis.title = "CA (FCFA)"
            
            data = Reference(ws_products, min_col=5, min_row=1, max_row=min(11, len(results)+1))
            cats = Reference(ws_products, min_col=2, min_row=2, max_row=min(11, len(results)+1))
            
            chart.add_data(data, titles_from_data=True)
            chart.set_categories(cats)
            
            ws_products.add_chart(chart, "H2")
        
        # ONGLET 3: Ventes par Catégorie
        ws_categories = wb.create_sheet("Ventes par Catégorie")
        
        # (Similaire à ventes par produit, groupé par catégorie)
        
        # ONGLET 4: Évolution Quotidienne
        ws_daily = wb.create_sheet("Évolution Quotidienne")
        
        # (Table date + CA + transactions + graphique)
        
        # Sauvegarder
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        return output
    
    def _calculate_status(self, product: Product) -> str:
        """Calculer statut stock produit"""
        if product.current_stock == 0:
            return "RUPTURE"
        elif product.min_stock and product.current_stock <= product.min_stock:
            return "FAIBLE"
        elif product.max_stock and product.current_stock >= product.max_stock:
            return "SURSTOCK"
        return "NORMAL"
```

CRITÈRES D'ACCEPTATION:
✅ Service ReportService créé
✅ Rapport Inventaire Stock génère Excel
✅ Formatage professionnel (couleurs, bordures)
✅ Rapport Ventes multi-onglets
✅ Graphiques Excel embarqués
✅ Formules Excel (totaux)
✅ Format nombres français (#,##0)
✅ Largeurs colonnes ajustées
✅ Tests génération rapports
✅ Fichiers ouvrent sans erreur

COMMANDES DE TEST:
```python
# Script test
from app.services.report_service import ReportService
from app.db.session import SessionLocal

db = SessionLocal()
service = ReportService(db)

# Générer rapport inventaire
excel = service.generate_inventory_report(tenant_id)

# Sauvegarder pour test
with open("test_inventory.xlsx", "wb") as f:
    f.write(excel.getvalue())

print("Rapport généré: test_inventory.xlsx")

# Ouvrir avec Excel/LibreOffice pour vérifier
```
```

---

### 🔧 PROMPT 4.2 : Service Génération Rapports PDF

```
CONTEXTE:
La génération Excel fonctionne. Je dois créer la génération de rapports PDF formatés (Synthèse Mensuelle).

OBJECTIF:
Créer génération PDF avec:
- Rapport Synthèse Mensuelle
- Logo entreprise
- KPIs formatés
- Tableaux
- Graphiques (images embarquées)
- Footer avec date/page

SPÉCIFICATIONS TECHNIQUES:

SERVICE PDF (app/services/report_service.py - ajouter):
```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
from io import BytesIO

class ReportService:
    # ... méthodes Excel existantes ...
    
    def generate_monthly_summary_pdf(
        self,
        tenant_id: UUID,
        month: int,
        year: int
    ) -> BytesIO:
        """
        Rapport Synthèse Mensuelle (PDF)
        
        Contenu:
        - En-tête avec période
        - KPIs principaux (grid)
        - Graphique évolution CA
        - Top 5 produits
        - Alertes stock
        - Recommandations
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#4F46E5'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1F2937'),
            spaceAfter=12,
            spaceBefore=20
        )
        
        # Éléments du document
        story = []
        
        # Titre
        month_names = [
            "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
        ]
        title = Paragraph(
            f"SYNTHÈSE MENSUELLE<br/>{month_names[month-1]} {year}",
            title_style
        )
        story.append(title)
        story.append(Spacer(1, 1*cm))
        
        # Date génération
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=TA_RIGHT
        )
        story.append(Paragraph(
            f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
            date_style
        ))
        story.append(Spacer(1, 0.5*cm))
        
        # KPIs principaux
        story.append(Paragraph("Indicateurs Clés", heading_style))
        
        # Calculer KPIs
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        from sqlalchemy import func
        kpis = self.db.query(
            func.count(Sale.id).label('transactions'),
            func.sum(Sale.total_amount).label('revenue')
        ).filter(
            Sale.tenant_id == tenant_id,
            Sale.sale_date >= start_date,
            Sale.sale_date <= end_date
        ).first()
        
        # Santé stock
        stock_health = self.db.query(
            func.count(Product.id).label('total'),
            func.count(Product.id).filter(Product.current_stock == 0).label('rupture'),
            func.count(Product.id).filter(
                Product.current_stock <= Product.min_stock,
                Product.current_stock > 0
            ).label('faible')
        ).filter(
            Product.tenant_id == tenant_id,
            Product.is_active == True
        ).first()
        
        # Table KPIs
        kpi_data = [
            ['Indicateur', 'Valeur'],
            ['Chiffre d\'Affaires', f'{int(kpis.revenue or 0):,} FCFA'.replace(',', ' ')],
            ['Transactions', f'{kpis.transactions or 0}'],
            ['Panier Moyen', f'{int((kpis.revenue or 0) / max(kpis.transactions, 1)):,} FCFA'.replace(',', ' ')],
            ['', ''],
            ['Produits Actifs', f'{stock_health.total or 0}'],
            ['Ruptures Stock', f'{stock_health.rupture or 0}'],
            ['Stock Faible', f'{stock_health.faible or 0}'],
        ]
        
        kpi_table = Table(kpi_data, colWidths=[8*cm, 8*cm])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(kpi_table)
        story.append(Spacer(1, 1*cm))
        
        # Graphique évolution CA
        story.append(Paragraph("Évolution du Chiffre d'Affaires", heading_style))
        
        # Générer graphique matplotlib
        from sqlalchemy import text
        query = text("""
            SELECT 
                DATE(sale_date) as date,
                SUM(total_amount) as revenue
            FROM sales
            WHERE tenant_id = :tenant_id
                AND sale_date >= :start_date
                AND sale_date <= :end_date
            GROUP BY DATE(sale_date)
            ORDER BY date
        """)
        
        daily_sales = self.db.execute(query, {
            "tenant_id": tenant_id,
            "start_date": start_date,
            "end_date": end_date
        }).fetchall()
        
        if daily_sales:
            # Créer graphique
            fig, ax = plt.subplots(figsize=(12, 6))
            dates = [row.date for row in daily_sales]
            revenues = [float(row.revenue) for row in daily_sales]
            
            ax.plot(dates, revenues, marker='o', linewidth=2, color='#4F46E5')
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('CA (FCFA)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.ticklabel_format(style='plain', axis='y')
            
            # Formater axe Y
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}K'))
            
            # Sauvegarder dans buffer
            img_buffer = BytesIO()
            plt.tight_layout()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            # Ajouter au PDF
            img = Image(img_buffer, width=16*cm, height=8*cm)
            story.append(img)
        
        story.append(Spacer(1, 1*cm))
        
        # Top 5 produits
        story.append(Paragraph("Top 5 Produits du Mois", heading_style))
        
        top_query = text("""
            SELECT 
                p.name,
                SUM(s.quantity) as quantity,
                SUM(s.total_amount) as revenue
            FROM products p
            JOIN sales s ON p.id = s.product_id
            WHERE p.tenant_id = :tenant_id
                AND s.sale_date >= :start_date
                AND s.sale_date <= :end_date
            GROUP BY p.id, p.name
            ORDER BY SUM(s.total_amount) DESC
            LIMIT 5
        """)
        
        top_products = self.db.execute(top_query, {
            "tenant_id": tenant_id,
            "start_date": start_date,
            "end_date": end_date
        }).fetchall()
        
        top_data = [['Produit', 'Quantité', 'CA (FCFA)']]
        for product in top_products:
            top_data.append([
                product.name,
                f'{float(product.quantity):.1f}',
                f'{int(product.revenue):,}'.replace(',', ' ')
            ])
        
        top_table = Table(top_data, colWidths=[8*cm, 4*cm, 4*cm])
        top_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(top_table)
        
        # Footer personnalisé
        def footer(canvas, doc):
            canvas.saveState()
            canvas.setFont('Helvetica', 9)
            canvas.setFillColor(colors.grey)
            canvas.drawString(2*cm, 1*cm, "Digiboost PME - Intelligence Supply Chain")
            canvas.drawRightString(A4[0] - 2*cm, 1*cm, f"Page {doc.page}")
            canvas.restoreState()
        
        # Générer PDF
        doc.build(story, onFirstPage=footer, onLaterPages=footer)
        
        buffer.seek(0)
        return buffer
```

CRITÈRES D'ACCEPTATION:
✅ Génération PDF fonctionne
✅ Formatage professionnel
✅ Graphiques matplotlib embarqués
✅ Tableaux formatés (couleurs, bordures)
✅ Footer avec numéro page
✅ Logo entreprise (optionnel)
✅ Export qualité print (150 dpi)
✅ PDF ouvre sans erreur
✅ Tests génération mensuelle
✅ Présentable pour banquier/investisseur

COMMANDES DE TEST:
```python
# Test PDF
excel = service.generate_monthly_summary_pdf(
    tenant_id,
    month=10,
    year=2025
)

with open("test_monthly.pdf", "wb") as f:
    f.write(pdf.getvalue())

print("PDF généré: test_monthly.pdf")
# Ouvrir pour vérifier
```
```

---

### 🔧 PROMPT 4.3 : Endpoints API Rapports & Tâches Celery

```
CONTEXTE:
Les services de génération sont fonctionnels. Je dois créer les endpoints API et tâches Celery pour automatisation.

OBJECTIF:
Créer:
- Endpoints génération rapports (download)
- Stockage fichiers générés (filesystem/S3)
- Tâches Celery génération auto (1er du mois)
- Envoi email + WhatsApp avec rapports

SPÉCIFICATIONS TECHNIQUES:

CONFIGURATION STOCKAGE (app/config.py - ajouter):
```python
REPORTS_DIR: str = "reports"  # Dossier stockage rapports
REPORTS_RETENTION_DAYS: int = 90  # Durée conservation
```

ROUTER RAPPORTS (app/api/v1/reports.py):
```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID
import os

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.report_service import ReportService
from app.config import settings

router = APIRouter()

@router.post("/generate/inventory")
def generate_inventory_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Générer rapport inventaire stock (Excel)"""
    service = ReportService(db)
    excel = service.generate_inventory_report(current_user.tenant_id)
    
    filename = f"inventaire_stock_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return StreamingResponse(
        excel,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/generate/sales-analysis")
def generate_sales_analysis_report(
    start_date: str,  # Format: YYYY-MM-DD
    end_date: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Générer rapport analyse ventes (Excel)"""
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    service = ReportService(db)
    excel = service.generate_sales_analysis_report(current_user.tenant_id, start, end)
    
    filename = f"analyse_ventes_{start.strftime('%Y%m')}.xlsx"
    
    return StreamingResponse(
        excel,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/generate/monthly-summary")
def generate_monthly_summary(
    month: int,
    year: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Générer synthèse mensuelle (PDF)"""
    if not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    
    service = ReportService(db)
    pdf = service.generate_monthly_summary_pdf(current_user.tenant_id, month, year)
    
    filename = f"synthese_mensuelle_{year}_{month:02d}.pdf"
    
    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
```

TÂCHE CELERY RAPPORTS AUTO (app/tasks/report_tasks.py):
```python
from celery import shared_task
from datetime import datetime, timedelta
from app.db.session import SessionLocal
from app.models.tenant import Tenant
from app.services.report_service import ReportService
from app.integrations.email import EmailService
from app.integrations.whatsapp import whatsapp_service
import asyncio
import logging

logger = logging.getLogger(__name__)

@shared_task(name='app.tasks.report_tasks.generate_monthly_reports')
def generate_monthly_reports():
    """
    Tâche périodique: Générer rapports mensuels pour tous les tenants
    Exécutée le 1er de chaque mois à 08:00
    """
    logger.info("Starting monthly report generation")
    
    db = SessionLocal()
    try:
        # Mois précédent
        today = datetime.now()
        if today.month == 1:
            month = 12
            year = today.year - 1
        else:
            month = today.month - 1
            year = today.year
        
        tenants = db.query(Tenant).filter(Tenant.is_active == True).all()
        
        for tenant in tenants:
            try:
                # Générer PDF
                report_service = ReportService(db)
                pdf = report_service.generate_monthly_summary_pdf(tenant.id, month, year)
                
                # Sauvegarder fichier
                filename = f"synthese_{tenant.id}_{year}_{month:02d}.pdf"
                filepath = f"{settings.REPORTS_DIR}/{filename}"
                
                os.makedirs(settings.REPORTS_DIR, exist_ok=True)
                with open(filepath, "wb") as f:
                    f.write(pdf.getvalue())
                
                # Envoyer par email
                email_service = EmailService()
                asyncio.run(_send_report_email(tenant, filepath, month, year))
                
                # Envoyer par WhatsApp (lien download)
                # asyncio.run(_send_report_whatsapp(tenant, filename))
                
                logger.info(f"Monthly report generated for tenant {tenant.id}")
                
            except Exception as e:
                logger.error(f"Failed to generate report for tenant {tenant.id}: {str(e)}")
                continue
        
        return {"tenants_processed": len(tenants)}
        
    finally:
        db.close()

async def _send_report_email(tenant, filepath, month, year):
    """Envoyer rapport par email"""
    email_service = EmailService()
    
    # Lire fichier
    with open(filepath, "rb") as f:
        pdf_data = f.read()
    
    month_names = [
        "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
        "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
    ]
    
    subject = f"Synthèse Mensuelle - {month_names[month-1]} {year}"
    body = f"""
    <html>
    <body>
        <h2>Bonjour,</h2>
        <p>Veuillez trouver ci-joint votre synthèse mensuelle pour {month_names[month-1]} {year}.</p>
        <p>Ce rapport contient:</p>
        <ul>
            <li>Les indicateurs clés du mois</li>
            <li>L'évolution de votre chiffre d'affaires</li>
            <li>Le classement de vos meilleurs produits</li>
            <li>La santé de votre stock</li>
        </ul>
        <p>Cordialement,<br/>L'équipe Digiboost PME</p>
    </body>
    </html>
    """
    
    await email_service.send_email(
        to_email=tenant.email,
        subject=subject,
        body_html=body,
        attachments=[(f"synthese_{month_names[month-1]}_{year}.pdf", pdf_data)]
    )
```

CONFIGURATION CELERY BEAT (app/tasks/celery_app.py - ajouter):
```python
from celery.schedules import crontab

celery_app.conf.beat_schedule.update({
    'generate-monthly-reports': {
        'task': 'app.tasks.report_tasks.generate_monthly_reports',
        'schedule': crontab(day_of_month='1', hour='8', minute='0'),  # 1er du mois à 8h
        'options': {'queue': 'reports'}
    },
})
```

CRITÈRES D'ACCEPTATION:
✅ Endpoints génération rapports fonctionnels
✅ Téléchargement direct (StreamingResponse)
✅ Tâche Celery génération auto
✅ Envoi email avec PJ fonctionne
✅ Stockage fichiers organisé
✅ Logs appropriés
✅ Gestion erreurs robuste
✅ Tests génération manuelle
✅ Tests tâche Celery
✅ Rapports reçus par email

COMMANDES DE TEST:
```bash
# Test endpoint
curl -X POST "http://localhost:8000/api/v1/reports/generate/inventory" \
  -H "Authorization: Bearer <token>" \
  --output inventaire.xlsx

# Exécuter tâche manuellement
docker-compose exec celery-worker celery -A app.tasks.celery_app call app.tasks.report_tasks.generate_monthly_reports

# Vérifier emails envoyés
# Vérifier fichiers dans dossier reports/
ls -lh reports/
```
```

---

## SEMAINE 8 : TESTS & DOCUMENTATION

### 🔧 PROMPT 4.4 : Tests End-to-End (Playwright)

```
CONTEXTE:
Toutes les fonctionnalités sont implémentées. Je dois créer des tests E2E pour valider les parcours utilisateurs critiques.

OBJECTIF:
Créer suite tests E2E avec Playwright:
- Test login
- Test dashboard Vue d'Ensemble
- Test création alerte
- Test génération rapport
- Test navigation complète

SPÉCIFICATIONS TECHNIQUES:

INSTALLATION (package.json - ajouter):
```json
{
  "devDependencies": {
    "@playwright/test": "^1.40.0"
  },
  "scripts": {
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui"
  }
}
```

CONFIGURATION (playwright.config.ts):
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'mobile',
      use: { ...devices['iPhone 13'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
});
```

TEST LOGIN (tests/e2e/auth.spec.ts):
```typescript
import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('should login successfully', async ({ page }) => {
    await page.goto('/login');

    // Vérifier page login
    await expect(page.locator('h1')).toContainText('Connexion');

    // Remplir formulaire
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    
    // Soumettre
    await page.click('button[type="submit"]');

    // Vérifier redirection dashboard
    await expect(page).toHaveURL('/dashboard');
    
    // Vérifier header contient nom utilisateur
    await expect(page.locator('header')).toContainText('Test User');
  });

  test('should show error on invalid credentials', async ({ page }) => {
    await page.goto('/login');

    await page.fill('input[type="email"]', 'wrong@example.com');
    await page.fill('input[type="password"]', 'wrongpass');
    await page.click('button[type="submit"]');

    // Vérifier message erreur
    await expect(page.locator('[role="alert"]')).toBeVisible();
    
    // Reste sur page login
    await expect(page).toHaveURL('/login');
  });
});
```

TEST DASHBOARD (tests/e2e/dashboard.spec.ts):
```typescript
import { test, expect } from '@playwright/test';

test.describe('Dashboard Vue d\'Ensemble', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
  });

  test('should display KPI cards', async ({ page }) => {
    // Vérifier présence KPIs
    await expect(page.locator('text=Total Produits')).toBeVisible();
    await expect(page.locator('text=Ruptures')).toBeVisible();
    await expect(page.locator('text=Stock Faible')).toBeVisible();
    await expect(page.locator('text=Valorisation')).toBeVisible();
  });

  test('should refresh data on button click', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Actualiser")');
    await expect(refreshButton).toBeVisible();
    
    // Cliquer actualiser
    await refreshButton.click();
    
    // Vérifier loading (optionnel)
    // await expect(page.locator('[role="progressbar"]')).toBeVisible();
    
    // Attendre données rechargées
    await page.waitForTimeout(1000);
  });
});
```

TEST ALERTES (tests/e2e/alerts.spec.ts):
```typescript
import { test, expect } from '@playwright/test';

test.describe('Gestion Alertes', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
  });

  test('should create new alert', async ({ page }) => {
    // Navigation vers alertes
    await page.click('text=Alertes');
    await expect(page).toHaveURL('/alerts');

    // Ouvrir dialog création
    await page.click('button:has-text("Nouvelle Alerte")');
    
    // Remplir formulaire
    await page.fill('input[name="name"]', 'Test Alerte E2E');
    await page.selectOption('select[name="alert_type"]', 'RUPTURE_STOCK');
    await page.check('input[name="channels.whatsapp"]');
    await page.fill('input[placeholder*="WhatsApp"]', '+221771234567');

    // Soumettre
    await page.click('button[type="submit"]:has-text("Créer")');

    // Vérifier toast succès
    await expect(page.locator('text=Alerte créée')).toBeVisible();

    // Vérifier alerte dans liste
    await expect(page.locator('text=Test Alerte E2E')).toBeVisible();
  });

  test('should toggle alert activation', async ({ page }) => {
    await page.goto('/alerts');

    // Trouver première alerte
    const firstAlert = page.locator('tbody tr').first();
    const toggle = firstAlert.locator('[role="switch"]');

    // État initial
    const initialState = await toggle.isChecked();

    // Toggle
    await toggle.click();

    // Vérifier changement d'état
    await expect(toggle).toHaveAttribute('aria-checked', String(!initialState));
  });
});
```

TEST RAPPORTS (tests/e2e/reports.spec.ts):
```typescript
import { test, expect } from '@playwright/test';

test.describe('Génération Rapports', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
  });

  test('should generate inventory report', async ({ page }) => {
    await page.goto('/reports');

    // Attendre promise download
    const downloadPromise = page.waitForEvent('download');

    // Cliquer génération
    await page.click('button:has-text("Inventaire Stock")');

    // Attendre téléchargement
    const download = await downloadPromise;

    // Vérifier nom fichier
    expect(download.suggestedFilename()).toContain('inventaire');
    expect(download.suggestedFilename()).toContain('.xlsx');
  });
});
```

CRITÈRES D'ACCEPTATION:
✅ Playwright configuré
✅ Tests login passent
✅ Tests dashboard passent
✅ Tests alertes passent
✅ Tests rapports passent
✅ Tests mobile (viewport iPhone)
✅ Screenshots échecs automatiques
✅ Rapport HTML généré
✅ CI/CD ready (GitHub Actions)
✅ Tous tests passent en local

COMMANDES DE TEST:
```bash
# Installer Playwright
npm install -D @playwright/test
npx playwright install

# Lancer tests
npm run test:e2e

# Mode interactif (UI)
npm run test:e2e:ui

# Tests spécifiques
npx playwright test tests/e2e/auth.spec.ts

# Rapport HTML
npx playwright show-report
```
```

---

### 🔧 PROMPT 4.5 : Optimisation Performance

```
CONTEXTE:
Tous les tests passent. Je dois optimiser les performances backend et frontend pour garantir une expérience fluide.

OBJECTIF:
Optimiser:
- Requêtes SQL (index, EXPLAIN ANALYZE)
- Cache Redis
- Lazy loading frontend
- Bundle size
- Images optimisées

SPÉCIFICATIONS TECHNIQUES:

ANALYSE REQUÊTES SQL:
```bash
# Script analyse performance (scripts/analyze_performance.py)
from app.db.session import SessionLocal
from sqlalchemy import text
import time

db = SessionLocal()

# Liste requêtes critiques
queries = [
    ("Dashboard Overview", "SELECT * FROM mv_dashboard_stock_health WHERE tenant_id = :tenant_id"),
    ("Top Products", """
        SELECT p.id, p.name, SUM(s.total_amount) as revenue
        FROM products p
        JOIN sales s ON p.id = s.product_id
        WHERE p.tenant_id = :tenant_id
        GROUP BY p.id, p.name
        ORDER BY revenue DESC
        LIMIT 10
    """),
]

for name, query in queries:
    # EXPLAIN ANALYZE
    explain = db.execute(text(f"EXPLAIN ANALYZE {query}"), {"tenant_id": tenant_id})
    print(f"\n{name}:")
    for row in explain:
        print(row[0])
    
    # Temps exécution
    start = time.time()
    result = db.execute(text(query), {"tenant_id": tenant_id})
    result.fetchall()
    duration = time.time() - start
    print(f"Durée: {duration*1000:.2f}ms")
```

OPTIMISATIONS SQL:
```sql
-- Index composites additionnels
CREATE INDEX CONCURRENTLY idx_sales_tenant_date_product 
ON sales(tenant_id, sale_date, product_id);

CREATE INDEX CONCURRENTLY idx_products_tenant_active_stock 
ON products(tenant_id, is_active, current_stock) 
WHERE is_active = TRUE;

-- Statistiques à jour
ANALYZE products;
ANALYZE sales;
ANALYZE categories;

-- Vacuum (nettoyage)
VACUUM ANALYZE;
```

CACHE REDIS (app/services/dashboard_service.py - ajouter):
```python
import json
from app.config import settings
import redis

redis_client = redis.from_url(settings.REDIS_URL)

class DashboardService:
    # ... méthodes existantes ...
    
    def get_overview(self, tenant_id: UUID) -> Dict[str, Any]:
        """Dashboard avec cache Redis"""
        
        # Clé cache
        cache_key = f"dashboard:overview:{tenant_id}"
        
        # Vérifier cache
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Calculer si pas en cache
        data = {
            "stock_health": self._get_stock_health(tenant_id),
            "sales_performance": self._get_sales_performance(tenant_id),
            "top_products": self._get_top_products(tenant_id, limit=5),
            "dormant_products": self._get_dormant_products(tenant_id, limit=5),
        }
        
        # Mettre en cache (5 minutes)
        redis_client.setex(
            cache_key,
            300,  # 5 minutes
            json.dumps(data, default=str)
        )
        
        return data
```

LAZY LOADING FRONTEND (vite.config.ts):
```typescript
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['react', 'react-dom', 'react-router-dom'],
          'charts': ['recharts'],
          'query': ['@tanstack/react-query'],
        },
      },
    },
  },
});
```

LAZY ROUTES (src/routes/index.tsx):
```typescript
import { lazy, Suspense } from 'react';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';

// Lazy load routes
const DashboardOverview = lazy(() => import('@/features/dashboard/components/DashboardOverview'));
const StockDetailDashboard = lazy(() => import('@/features/stock/components/StockDetailDashboard'));
const SalesAnalysisDashboard = lazy(() => import('@/features/sales/components/SalesAnalysisDashboard'));
const PredictionsDashboard = lazy(() => import('@/features/predictions/components/PredictionsDashboard'));

export const AppRoutes = () => {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        {/* Routes avec lazy loading */}
        <Route path="/dashboard" element={<DashboardOverview />} />
        <Route path="/stock/detail" element={<StockDetailDashboard />} />
        <Route path="/sales/analysis" element={<SalesAnalysisDashboard />} />
        <Route path="/predictions" element={<PredictionsDashboard />} />
      </Routes>
    </Suspense>
  );
};
```

OPTIMISATION IMAGES:
```bash
# Convertir images en WebP
npm install -D @squoosh/lib

# Script conversion (scripts/optimize-images.js)
import { ImagePool } from '@squoosh/lib';
import { readdir, readFile, writeFile } from 'fs/promises';
import { join } from 'path';

const imagePool = new ImagePool();
const inputDir = 'public/images';
const outputDir = 'public/images/optimized';

const files = await readdir(inputDir);

for (const file of files) {
  if (file.match(/\.(jpg|jpeg|png)$/i)) {
    const image = imagePool.ingestImage(await readFile(join(inputDir, file)));
    
    await image.encode({
      webp: { quality: 80 },
    });
    
    const { binary } = await image.encodedWith.webp;
    const outputFile = file.replace(/\.(jpg|jpeg|png)$/i, '.webp');
    
    await writeFile(join(outputDir, outputFile), binary);
    console.log(`Optimized: ${file} → ${outputFile}`);
  }
}

await imagePool.close();
```

CRITÈRES D'ACCEPTATION:
✅ Dashboard charge <2s (P95)
✅ API responses <500ms (P95)
✅ Bundle JS <500KB (gzipped)
✅ Images format WebP
✅ Cache Redis actif
✅ Index SQL optimisés
✅ Lazy loading routes fonctionne
✅ Lighthouse score >80
✅ Tests performance passent
✅ Monitoring métriques Grafana

COMMANDES DE TEST:
```bash
# Analyse bundle
npm run build
npx vite-bundle-visualizer

# Lighthouse
npx lighthouse http://localhost:5173 --view

# Tests charge backend (Locust)
pip install locust
locust -f tests/load/locustfile.py --host=http://localhost:8000
```
```

---

### 🔧 PROMPT 4.6 : Documentation Utilisateur

```
CONTEXTE:
Le POC est fonctionnel et optimisé. Je dois créer la documentation utilisateur pour les gérants PME.

OBJECTIF:
Créer guide utilisateur avec:
- Guide démarrage rapide
- Tutoriels par fonctionnalité
- FAQ
- Captures d'écran


SPÉCIFICATIONS:

GUIDE UTILISATEUR (docs/guide-utilisateur.md):
```markdown
# GUIDE UTILISATEUR - DIGIBOOST PME
## Intelligence Supply Chain

Version 1.0 - Octobre 2025

---

## 📋 TABLE DES MATIÈRES

1. Introduction
2. Démarrage Rapide
3. Dashboard Vue d'Ensemble
4. Gestion des Alertes
5. Analyse des Ventes
6. Prédictions & Recommandations
7. Génération de Rapports
8. FAQ

---

## 1. INTRODUCTION

Bienvenue sur Digiboost PME, votre assistant intelligent pour la gestion de stock et l'optimisation de votre supply chain.

### Qu'est-ce que Digiboost PME ?

Digiboost PME transforme vos données de stock et de ventes en informations actionnables:
- 📊 **Dashboards temps réel** : Visualisez votre situation stock instantanément
- 🚨 **Alertes automatiques** : Soyez prévenu par WhatsApp des ruptures
- 📈 **Analyses avancées** : Comprenez vos meilleures ventes
- 🔮 **Prédictions** : Anticipez les ruptures avant qu'elles arrivent
- 📄 **Rapports automatiques** : Recevez des synthèses mensuelles

---

## 2. DÉMARRAGE RAPIDE

### Première Connexion

1. Ouvrez l'application : `https://app.digiboost.sn`
2. Entrez votre email et mot de passe
3. Cliquez sur "Se connecter"

Vous arrivez sur le **Dashboard Vue d'Ensemble**.

### Navigation

Le menu latéral vous permet d'accéder à:
- 📊 **Vue d'Ensemble** : Indicateurs principaux
- 📦 **Gestion Stock** : Liste détaillée produits
- 📈 **Analyse Ventes** : Évolution chiffre d'affaires
- 🔮 **Prédictions** : Ruptures prévues
- 🚨 **Alertes** : Configuration alertes
- 📄 **Rapports** : Génération documents

---

## 3. DASHBOARD VUE D'ENSEMBLE

Le dashboard principal affiche 3 sections:

### A. Santé Stock

**4 indicateurs clés:**
- **Total Produits** : Nombre de produits actifs
- **Ruptures** : Produits en stock zéro (🔴 Rouge)
- **Stock Faible** : Produits sous le minimum (🟡 Jaune)
- **Valorisation** : Valeur totale du stock (en FCFA)

**Action:** Cliquez sur un indicateur pour voir le détail.

### B. Performance Ventes

**Indicateurs:**
- **CA 7 jours** : Chiffre d'affaires semaine dernière
- **CA 30 jours** : Chiffre d'affaires du mois
- **Évolution** : Variation en pourcentage

**Graphique:** Évolution quotidienne du CA sur 30 jours.

### C. Top/Flop Produits

- **Top 5** : Vos 5 meilleurs produits (par CA)
- **Produits Dormants** : Produits sans vente depuis 30 jours

**Astuce:** Identifiez vos produits stars et réduisez le stock des produits dormants.

---

## 4. GESTION DES ALERTES

Les alertes vous préviennent automatiquement par WhatsApp.

### Créer une Alerte

1. Menu **Alertes** → **Nouvelle Alerte**
2. Remplir le formulaire:
   - **Nom:** Ex: "Alerte Riz en Rupture"
   - **Type:** Rupture Stock / Stock Faible / Baisse Taux Service
   - **Canaux:** WhatsApp (cocher)
   - **Destinataires:** Votre numéro WhatsApp (+221...)
3. Cliquer **Créer**

### Types d'Alertes

**Rupture Stock:**
- Déclenchée quand un produit atteint stock zéro
- 🚨 Urgence CRITIQUE

**Stock Faible:**
- Déclenchée quand stock ≤ stock minimum
- ⚠️ Urgence MOYENNE

**Baisse Taux Service:**
- Déclenchée si taux livraison < 90%
- 📉 Urgence FAIBLE

### Consulter l'Historique

Menu **Alertes** → **Historique**
- Voir toutes les alertes déclenchées
- Filtrer par date, type, sévérité

---

## 5. ANALYSE DES VENTES

Comprendre vos ventes pour mieux décider.

### Évolution du CA

**Graphique ligne:**
- Évolution quotidienne chiffre d'affaires
- Période réglable (7j / 30j / 90j)

**Astuce:** Identifiez les pics et creux pour anticiper.

### Top Produits

**Graphique barres:**
- Top 10 produits par chiffre d'affaires
- Quantités vendues
- Nombre de transactions

**Utilisation:** Concentrez vos efforts sur les produits rentables.

### Performance Catégories

**Graphique camembert:**
- Répartition CA par catégorie
- Pourcentages

**Action:** Investissez davantage dans les catégories performantes.

---

## 6. PRÉDICTIONS & RECOMMANDATIONS

Anticipez les ruptures et optimisez vos commandes.

### Ruptures Prévues

**Liste des produits:**
- Nom produit
- Stock actuel
- **Date rupture prévue** (algorithme IA)
- Nombre de jours restants
- **Quantité à commander**

**Code couleur urgence:**
- 🔴 Rouge : Rupture dans ≤3 jours (URGENT)
- 🟠 Orange : Rupture dans 4-7 jours (PRIORITAIRE)
- 🟡 Jaune : Rupture dans 8-15 jours (À SURVEILLER)

### Recommandations d'Achat

**Groupées par fournisseur:**
- Liste produits à commander
- Quantités recommandées
- Urgence

**Avantage:** Passez vos commandes groupées, économisez sur les frais de livraison.

**Astuce:** Imprimez ou exportez pour donner à votre fournisseur.

---

## 7. GÉNÉRATION DE RAPPORTS

Recevez des documents professionnels automatiquement.

### Rapports Disponibles

**1. Inventaire Stock (Excel)**
- Liste complète de tous vos produits
- Stock actuel, min, max
- Valorisation
- **Utilisation:** Inventaire comptable, bilan

**2. Synthèse Mensuelle (PDF)**
- KPIs du mois
- Graphiques évolution
- Top produits
- **Utilisation:** Présentation banque, investisseurs

**3. Analyse Ventes (Excel)**
- Ventes par produit
- Ventes par catégorie
- Évolution quotidienne
- **Utilisation:** Analyse approfondie

### Générer Manuellement

1. Menu **Rapports**
2. Choisir le type de rapport
3. Sélectionner la période (si applicable)
4. Cliquer **Générer**
5. Le fichier se télécharge automatiquement

### Rapports Automatiques

**Chaque 1er du mois à 8h:**
- Synthèse mensuelle générée automatiquement
- Envoyée par email
- (Optionnel) Notification WhatsApp

---

## 8. FAQ

### Comment modifier mes alertes ?

Menu **Alertes** → Cliquer sur l'alerte → Modifier

### Puis-je désactiver temporairement une alerte ?

Oui, utilisez le bouton toggle (interrupteur) sur la ligne de l'alerte.

### Les prédictions sont-elles fiables ?

Les prédictions sont basées sur vos ventes des 30 derniers jours. Précision ~90%.

### Puis-je exporter les données ?

Oui, utilisez les boutons "Exporter CSV" dans les dashboards ou générez des rapports Excel.

### Comment ajouter un nouvel utilisateur ?

Contactez l'administrateur ou l'équipe Digiboost.

### L'application fonctionne-t-elle hors ligne ?

Partiellement. Les dashboards récemment consultés restent accessibles hors ligne en lecture seule.

### Qui contacter en cas de problème ?

Email: support@digiboost.sn
WhatsApp: +221 77 123 4567

---

**Bonne utilisation de Digiboost PME !**

_Équipe Digiboost - Intelligence Supply Chain pour PME Africaines_
```

CAPTURES D'ÉCRAN:
```bash
# Générer screenshots automatiques (Playwright)
npx playwright test --headed --project=chromium

# Script captures (tests/screenshots.spec.ts)
test('generate screenshots', async ({ page }) => {
  await page.goto('/dashboard');
  await page.screenshot({ path: 'docs/images/dashboard-overview.png', fullPage: true });
  
  await page.goto('/alerts');
  await page.screenshot({ path: 'docs/images/alerts.png', fullPage: true });
  
  // etc...
});
```

CRITÈRES D'ACCEPTATION:
✅ Guide utilisateur complet
✅ Langage simple (non technique)
✅ Captures d'écran annotées
✅ Cas d'usage concrets
✅ FAQ couvre questions fréquentes
✅ Format PDF exportable
✅ Version imprimable
✅ Traduit français simple
✅ Accessible gérants PME
✅ <15 pages

COMMANDES DE TEST:
```bash
# Générer PDF
npx markdown-pdf docs/guide-utilisateur.md

# Ou utiliser pandoc
pandoc docs/guide-utilisateur.md -o docs/guide-utilisateur.pdf --pdf-engine=xelatex

# Vérifier accessibilité
# Faire relire par un gérant PME test
```
```

---

### 🔧 PROMPT 4.7 : Guide Déploiement Production

```
CONTEXTE:
Le POC est complet avec documentation. Je dois créer le guide de déploiement pour mise en production.

OBJECTIF:
Créer guide déploiement avec:
- Checklist pré-déploiement
- Configuration serveur
- Déploiement Docker
- Configuration SSL
- Monitoring
- Backup & Recovery

SPÉCIFICATIONS:

GUIDE DÉPLOIEMENT (docs/deployment-guide.md):
```markdown
# GUIDE DÉPLOIEMENT PRODUCTION
## Digiboost PME v1.0

---

## 1. PRÉ-REQUIS

### Serveur

**Minimum:**
- CPU: 4 vCores
- RAM: 8 GB
- SSD: 160 GB
- OS: Ubuntu 22.04 LTS

**Recommandé (Hetzner CX31):**
- CPU: 4 vCores AMD
- RAM: 16 GB
- SSD: 240 GB
- Coût: ~20€/mois
- Localisation: Nuremberg (proche Sénégal)

### Domaines

- `digiboost.sn` (site vitrine)
- `app.digiboost.sn` (application)
- `api.digiboost.sn` (API backend)

### Services Externes

- [x] Compte WhatsApp Business API
- [x] Compte Email SMTP (Gmail/SendGrid)
- [x] Cloudflare (CDN + DDoS protection)

---

## 2. INSTALLATION SERVEUR

### Connexion Initiale

```bash
ssh root@YOUR_SERVER_IP
```

### Sécurisation

```bash
# Créer utilisateur non-root
adduser digiboost
usermod -aG sudo digiboost

# Configuration SSH
nano /etc/ssh/sshd_config
# Modifier:
PermitRootLogin no
PasswordAuthentication no

systemctl restart sshd
```

### Installation Docker

```bash
# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Docker Compose
apt install docker-compose-plugin

# Vérifier
docker --version
docker compose version
```

### Firewall

```bash
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

---

## 3. DÉPLOIEMENT APPLICATION

### Cloner Repository

```bash
cd /opt
git clone https://github.com/digiboost/digiboost-pme.git
cd digiboost-pme
```

### Configuration Environnement

```bash
# Copier fichier env
cp .env.example .env

# Éditer variables
nano .env
```

**Variables critiques:**
```bash
# Application
APP_NAME=Digiboost PME
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<générer clé 64 caractères>

# Base de données
DATABASE_URL=postgresql://postgres:<strong-password>@postgres:5432/digiboost_prod

# Redis
REDIS_URL=redis://redis:6379/0

# WhatsApp
WHATSAPP_API_TOKEN=<token-production>
WHATSAPP_PHONE_NUMBER_ID=<id-production>

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@digiboost.sn
SMTP_PASSWORD=<app-password>

# Frontend
VITE_API_URL=https://api.digiboost.sn

# CORS
CORS_ORIGINS=https://app.digiboost.sn
```

### Build Images

```bash
# Backend
cd backend
docker build -t digiboost-backend:latest .

# Frontend
cd ../frontend
npm run build
docker build -t digiboost-frontend:latest .
```

### Lancer Services

```bash
cd /opt/digiboost-pme
docker compose -f docker-compose.prod.yml up -d
```

### Vérifier Services

```bash
docker compose ps

# Logs
docker compose logs -f backend
docker compose logs -f celery-worker
```

---

## 4. CONFIGURATION SSL (Let's Encrypt)

### Installation Certbot

```bash
apt install certbot python3-certbot-nginx
```

### Générer Certificats

```bash
# API
certbot --nginx -d api.digiboost.sn

# App
certbot --nginx -d app.digiboost.sn
```

### Auto-renouvellement

```bash
# Test renouvellement
certbot renew --dry-run

# Cron (automatique)
systemctl status certbot.timer
```

---

## 5. MONITORING

### Grafana Dashboard

Accès: `http://YOUR_SERVER_IP:3000`
- User: admin
- Pass: (défini dans .env)

**Dashboards à configurer:**
1. Santé Serveur (CPU, RAM, Disque)
2. Métriques API (latence, erreurs)
3. Métriques Métier (dashboards consultés, alertes envoyées)

### Alertes Monitoring

Configuration Grafana → Alerting:
- CPU >80% pendant 5 min
- RAM >90% pendant 5 min
- Disque >85%
- API errors >5% sur 10 min

**Canal:** Email + Slack (optionnel)

---

## 6. BACKUP & RECOVERY

### Backup Automatique Base de Données

```bash
# Script backup (scripts/backup-db.sh)
#!/bin/bash
BACKUP_DIR="/opt/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="digiboost_backup_$DATE.sql"

mkdir -p $BACKUP_DIR

docker compose exec -T postgres pg_dump -U postgres digiboost_prod > $BACKUP_DIR/$FILENAME

# Compression
gzip $BACKUP_DIR/$FILENAME

# Nettoyage (garder 30 jours)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $FILENAME.gz"
```

**Cron quotidien:**
```bash
crontab -e
# Ajouter:
0 2 * * * /opt/digiboost-pme/scripts/backup-db.sh
```

### Restauration

```bash
# Décompresser
gunzip backup_file.sql.gz

# Restaurer
cat backup_file.sql | docker compose exec -T postgres psql -U postgres digiboost_prod
```

---

## 7. CHECKLIST DÉPLOIEMENT

### Avant Déploiement

- [ ] Variables .env configurées
- [ ] Secrets rotés (SECRET_KEY, passwords)
- [ ] Domaines pointent vers serveur
- [ ] Certificats SSL générés
- [ ] Firewall configuré
- [ ] Backup automatique configuré
- [ ] Monitoring Grafana configuré

### Après Déploiement

- [ ] Application accessible HTTPS
- [ ] Login fonctionne
- [ ] Dashboards chargent <3s
- [ ] Alertes WhatsApp fonctionnent
- [ ] Rapports se génèrent
- [ ] Celery workers actifs
- [ ] Logs sans erreurs critiques
- [ ] Monitoring actif
- [ ] Tests E2E passent en prod

### Tests Validation Production

```bash
# Health check
curl https://api.digiboost.sn/health

# Login
curl -X POST https://api.digiboost.sn/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'

# Dashboard
curl https://api.digiboost.sn/api/v1/dashboards/overview \
  -H "Authorization: Bearer <token>"
```

---

## 8. MAINTENANCE

### Mises à Jour

```bash
cd /opt/digiboost-pme
git pull origin main

# Rebuild si nécessaire
docker compose down
docker compose build
docker compose up -d

# Migrations DB
docker compose exec backend alembic upgrade head
```

### Monitoring Quotidien

- Vérifier Grafana (alertes)
- Consulter logs erreurs
- Vérifier espace disque
- Vérifier backups réussis

### Support

Email: support@digiboost.sn
WhatsApp: +221 77 123 4567
Documentation: https://docs.digiboost.sn

---

**Digiboost PME est maintenant en production ! 🚀**
```

CRITÈRES D'ACCEPTATION:
✅ Guide déploiement complet
✅ Checklist pré/post-déploiement
✅ Commandes copier-coller prêtes
✅ Configuration SSL détaillée
✅ Backup automatique configuré
✅ Monitoring configuré
✅ Procédures recovery documentées
✅ Tests validation fournis
✅ Accessible DevOps junior
✅ <20 pages

---

## 🎯 RÉCAPITULATIF SPRINT 4

### Fonctionnalités Livrées

✅ **3 Rapports Standards**
- Inventaire Stock (Excel formaté)
- Synthèse Mensuelle (PDF avec graphiques)
- Analyse Ventes (Excel multi-onglets)

✅ **Automatisation**
- Génération automatique rapports (1er du mois)
- Envoi email avec pièces jointes
- Tâches Celery configurées

✅ **Qualité**
- Tests E2E (Playwright)
- Optimisation performance (<2s dashboards)
- Cache Redis actif
- Bundle optimisé (<500KB)

✅ **Documentation**
- Guide utilisateur (15 pages)
- Guide déploiement (20 pages)
- FAQ complète
- Captures d'écran annotées

### Tests Validation Sprint 4

```bash
# 1. Générer rapports
curl -X POST http://localhost:8000/api/v1/reports/generate/inventory \
  -H "Authorization: Bearer <token>" \
  --output inventaire.xlsx

# 2. Tests E2E
npm run test:e2e

# 3. Performance
npm run build
# Vérifier bundle size <500KB

# 4. Déploiement
# Suivre guide deployment-guide.md
```

### Métriques Succès POC

**Adoption:**
- 🎯 80% gérants consultent dashboard 1×/jour
- 🎯 90% gérants lisent alertes WhatsApp
- 🎯 70% gérants génèrent ≥1 rapport/mois

**Business:**
- 🎯 -50% ruptures de stock
- 🎯 +15% taux de service
- 🎯 -30% capital immobilisé

**Technique:**
- 🎯 Uptime >99.5%
- 🎯 Dashboards <3s (P95)
- 🎯 API <500ms (P95)
- 🎯 Alertes <2 min

---

## 🎉 POC TERMINÉ !

**Félicitations ! Vous avez un POC production-ready en 8 semaines.**

Le MVP Digiboost PME est maintenant prêt pour :
- ✅ Démo prospects
- ✅ Beta test utilisateurs
- ✅ Levée de fonds
- ✅ Mise en production

**Prochaines étapes suggérées :**
1. Beta test avec 5-10 PME pilotes
2. Collecte feedback utilisateurs
3. Itérations basées sur usage réel
4. Préparation Phase 2 (Agent IA conversationnel)

---

**FIN DES PROMPTS CLAUDE CODE**

*Bon développement ! 🚀*