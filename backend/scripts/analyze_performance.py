"""
Script d'analyse des performances SQL
Mesure le temps d'exécution des requêtes critiques et affiche EXPLAIN ANALYZE
"""
import sys
import os
import time
from uuid import UUID

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import SessionLocal
from sqlalchemy import text
from app.models.tenant import Tenant

def analyze_performance():
    """Analyser les performances des requêtes critiques"""
    db = SessionLocal()

    try:
        # Récupérer premier tenant pour les tests
        tenant = db.query(Tenant).filter(Tenant.is_active == True).first()

        if not tenant:
            print("❌ Aucun tenant actif trouvé")
            return

        tenant_id = tenant.id
        print(f"📊 Analyse des performances pour tenant: {tenant.name} ({tenant_id})\n")
        print("="*80)

        # Liste des requêtes critiques à analyser
        queries = [
            ("Dashboard Stock Health (Materialized View)", """
                SELECT * FROM mv_dashboard_stock_health
                WHERE tenant_id = :tenant_id
            """),

            ("Top 10 Products by Revenue", """
                SELECT
                    p.id,
                    p.name,
                    SUM(s.total_amount) as revenue,
                    COUNT(s.id) as total_sales
                FROM products p
                JOIN sales s ON p.id = s.product_id
                WHERE p.tenant_id = :tenant_id
                GROUP BY p.id, p.name
                ORDER BY revenue DESC
                LIMIT 10
            """),

            ("Products with Low Stock", """
                SELECT
                    p.id,
                    p.name,
                    p.current_stock,
                    p.minimum_stock,
                    p.unit_price
                FROM products p
                WHERE p.tenant_id = :tenant_id
                AND p.is_active = TRUE
                AND p.current_stock <= p.minimum_stock
                AND p.current_stock > 0
                ORDER BY (p.minimum_stock - p.current_stock) DESC
                LIMIT 20
            """),

            ("Sales Last 30 Days", """
                SELECT
                    DATE(s.sale_date) as date,
                    SUM(s.total_amount) as daily_revenue,
                    COUNT(s.id) as transactions
                FROM sales s
                WHERE s.tenant_id = :tenant_id
                AND s.sale_date >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY DATE(s.sale_date)
                ORDER BY date DESC
            """),

            ("Product Categories with Stock Value", """
                SELECT
                    c.id,
                    c.name,
                    COUNT(p.id) as product_count,
                    SUM(p.current_stock * p.unit_price) as total_value
                FROM categories c
                LEFT JOIN products p ON c.id = p.category_id AND p.tenant_id = :tenant_id
                WHERE c.tenant_id = :tenant_id
                GROUP BY c.id, c.name
                ORDER BY total_value DESC
            """),
        ]

        results = []

        for name, query in queries:
            print(f"\n{'='*80}")
            print(f"📌 {name}")
            print(f"{'='*80}\n")

            # EXPLAIN ANALYZE
            try:
                print("🔍 EXPLAIN ANALYZE:")
                print("-" * 80)
                explain_query = f"EXPLAIN ANALYZE {query}"
                explain_result = db.execute(text(explain_query), {"tenant_id": tenant_id})

                for row in explain_result:
                    print(row[0])

                print()
            except Exception as e:
                print(f"⚠️  Erreur EXPLAIN: {str(e)}\n")

            # Mesure du temps d'exécution (moyenne sur 3 runs)
            durations = []
            for i in range(3):
                start = time.time()
                try:
                    result = db.execute(text(query), {"tenant_id": tenant_id})
                    rows = result.fetchall()
                    duration = (time.time() - start) * 1000  # En millisecondes
                    durations.append(duration)
                except Exception as e:
                    print(f"❌ Erreur exécution: {str(e)}")
                    break

            if durations:
                avg_duration = sum(durations) / len(durations)
                min_duration = min(durations)
                max_duration = max(durations)

                # Déterminer le statut de performance
                if avg_duration < 100:
                    status = "✅ EXCELLENT"
                    color = "green"
                elif avg_duration < 500:
                    status = "🟡 BON"
                    color = "yellow"
                elif avg_duration < 1000:
                    status = "🟠 ACCEPTABLE"
                    color = "orange"
                else:
                    status = "🔴 LENT"
                    color = "red"

                print(f"⏱️  TEMPS D'EXÉCUTION:")
                print(f"   - Moyenne: {avg_duration:.2f}ms")
                print(f"   - Min: {min_duration:.2f}ms")
                print(f"   - Max: {max_duration:.2f}ms")
                print(f"   - Nombre de lignes: {len(rows)}")
                print(f"   - Statut: {status}")

                results.append({
                    'name': name,
                    'avg_duration': avg_duration,
                    'status': status,
                    'row_count': len(rows)
                })

        # Résumé final
        print(f"\n\n{'='*80}")
        print("📈 RÉSUMÉ DES PERFORMANCES")
        print(f"{'='*80}\n")

        print(f"{'Requête':<50} {'Temps moyen':<15} {'Statut':<15} {'Lignes':<10}")
        print("-" * 90)

        for result in results:
            print(f"{result['name']:<50} {result['avg_duration']:>10.2f}ms {result['status']:<15} {result['row_count']:>8}")

        # Recommendations
        print(f"\n{'='*80}")
        print("💡 RECOMMANDATIONS")
        print(f"{'='*80}\n")

        slow_queries = [r for r in results if r['avg_duration'] > 500]

        if slow_queries:
            print("⚠️  Requêtes lentes détectées (>500ms):")
            for q in slow_queries:
                print(f"   - {q['name']}: {q['avg_duration']:.2f}ms")
            print("\n🔧 Actions recommandées:")
            print("   1. Ajouter des index sur les colonnes filtrées/jointes")
            print("   2. Vérifier EXPLAIN ANALYZE pour les scans séquentiels")
            print("   3. Considérer mise en cache Redis")
            print("   4. Analyser les statistiques: ANALYZE tables;")
        else:
            print("✅ Toutes les requêtes sont performantes (<500ms)")
            print("   - Performances optimales")
            print("   - Monitoring continu recommandé")

        print("\n🗄️  Optimisations SQL suggérées:")
        print("   - CREATE INDEX CONCURRENTLY si nécessaire")
        print("   - VACUUM ANALYZE régulièrement")
        print("   - Rafraîchir vues matérialisées")

    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Démarrage de l'analyse de performance SQL...\n")
    analyze_performance()
    print("\n✅ Analyse terminée!")
