"""add_prediction_functions

Revision ID: bd2625f321eb
Revises: 68bd3fcd154e
Create Date: 2025-10-16 15:03:40.194960

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd2625f321eb'
down_revision: Union[str, None] = '68bd3fcd154e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ajouter fonction SQL de prédiction de date de rupture."""

    # Créer la fonction fn_predict_date_rupture
    op.execute("""
        CREATE OR REPLACE FUNCTION fn_predict_date_rupture(
            p_tenant_id UUID,
            p_product_id UUID
        ) RETURNS DATE AS $$
        DECLARE
            v_current_stock DECIMAL;
            v_avg_daily_sales DECIMAL;
            v_days_until_rupture INT;
        BEGIN
            -- Récupérer stock actuel
            SELECT current_stock INTO v_current_stock
            FROM products
            WHERE id = p_product_id AND tenant_id = p_tenant_id;

            IF v_current_stock IS NULL OR v_current_stock <= 0 THEN
                RETURN NULL;
            END IF;

            -- Calculer ventes moyennes quotidiennes (30j)
            SELECT AVG(daily_quantity) INTO v_avg_daily_sales
            FROM (
                SELECT DATE(sale_date), SUM(quantity) as daily_quantity
                FROM sales
                WHERE product_id = p_product_id
                    AND sale_date >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY DATE(sale_date)
            ) daily_sales;

            IF v_avg_daily_sales IS NULL OR v_avg_daily_sales <= 0 THEN
                RETURN NULL;
            END IF;

            -- Calculer jours jusqu'à rupture
            v_days_until_rupture := FLOOR(v_current_stock / v_avg_daily_sales);

            -- Si >30 jours, pas d'alerte
            IF v_days_until_rupture > 30 THEN
                RETURN NULL;
            END IF;

            RETURN CURRENT_DATE + v_days_until_rupture;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Créer une fonction helper pour calculer la quantité de réapprovisionnement
    op.execute("""
        CREATE OR REPLACE FUNCTION fn_calc_quantite_reappro(
            p_tenant_id UUID,
            p_product_id UUID,
            p_target_days INT DEFAULT 15
        ) RETURNS DECIMAL AS $$
        DECLARE
            v_current_stock DECIMAL;
            v_min_stock DECIMAL;
            v_avg_daily_sales DECIMAL;
            v_needed_quantity DECIMAL;
        BEGIN
            -- Récupérer infos produit
            SELECT current_stock, min_stock INTO v_current_stock, v_min_stock
            FROM products
            WHERE id = p_product_id AND tenant_id = p_tenant_id;

            IF v_current_stock IS NULL THEN
                RETURN NULL;
            END IF;

            -- Calculer ventes moyennes quotidiennes (30j)
            SELECT AVG(daily_quantity) INTO v_avg_daily_sales
            FROM (
                SELECT DATE(sale_date), SUM(quantity) as daily_quantity
                FROM sales
                WHERE product_id = p_product_id
                    AND sale_date >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY DATE(sale_date)
            ) daily_sales;

            -- Si pas d'historique, retourner stock minimum
            IF v_avg_daily_sales IS NULL OR v_avg_daily_sales <= 0 THEN
                RETURN COALESCE(v_min_stock, 0);
            END IF;

            -- Calculer quantité nécessaire
            v_needed_quantity := (v_avg_daily_sales * p_target_days) - v_current_stock + COALESCE(v_min_stock, 0);

            -- Minimum = 0
            IF v_needed_quantity < 0 THEN
                v_needed_quantity := 0;
            END IF;

            RETURN CEIL(v_needed_quantity);
        END;
        $$ LANGUAGE plpgsql;
    """)


def downgrade() -> None:
    """Supprimer les fonctions SQL de prédiction."""

    op.execute("DROP FUNCTION IF EXISTS fn_predict_date_rupture(UUID, UUID);")
    op.execute("DROP FUNCTION IF EXISTS fn_calc_quantite_reappro(UUID, UUID, INT);")
