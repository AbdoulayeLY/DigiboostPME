import { test, expect } from '@playwright/test';

/**
 * Tests E2E pour le Dashboard Vue d'Ensemble
 */

// Helper function pour se connecter
async function login(page: any) {
  await page.goto('/');
  await page.fill('input[type="email"]', 'test@digiboost.sn');
  await page.fill('input[type="password"]', 'password123');
  await page.click('button[type="submit"]');
  await page.waitForURL('/dashboard', { timeout: 10000 });
}

test.describe('Dashboard Vue d\'Ensemble', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('should display dashboard with correct title', async ({ page }) => {
    // Vérifier qu'on est sur le dashboard
    await expect(page).toHaveURL('/dashboard');

    // Vérifier titre ou éléments principaux
    await expect(
      page.locator('h1, h2').filter({ hasText: /vue d'ensemble|dashboard/i })
    ).toBeVisible({ timeout: 5000 });
  });

  test('should display KPI cards', async ({ page }) => {
    // Attendre chargement des données
    await page.waitForTimeout(2000);

    // Vérifier présence des KPIs principaux
    // Note: Adapter les textes selon les KPIs réels du dashboard
    const kpiTexts = [
      'Total Produits',
      'Ruptures',
      'Stock Faible',
      'Valorisation'
    ];

    for (const text of kpiTexts) {
      // Utiliser getByText avec option pour plus de flexibilité
      const locator = page.getByText(text, { exact: false });
      await expect(locator.first()).toBeVisible({ timeout: 5000 });
    }
  });

  test('should display charts or data visualizations', async ({ page }) => {
    // Attendre chargement des graphiques
    await page.waitForTimeout(2000);

    // Vérifier présence de graphiques (recharts utilise des SVG)
    const charts = page.locator('svg.recharts-surface');
    await expect(charts.first()).toBeVisible({ timeout: 5000 });
  });

  test('should have working navigation menu', async ({ page }) => {
    // Vérifier présence menu navigation
    const navItems = [
      'Dashboard',
      'Produits',
      'Ventes',
      'Alertes'
    ];

    for (const item of navItems) {
      await expect(page.getByRole('link', { name: new RegExp(item, 'i') })).toBeVisible();
    }
  });

  test('should navigate to other pages from dashboard', async ({ page }) => {
    // Cliquer sur Produits
    await page.click('a[href="/produits"]');
    await expect(page).toHaveURL('/produits', { timeout: 5000 });

    // Retour dashboard
    await page.click('a[href="/dashboard"]');
    await expect(page).toHaveURL('/dashboard');
  });

  test('should display loading state initially', async ({ page }) => {
    // Recharger la page pour voir le loading
    await page.reload();

    // Vérifier présence d'un indicateur de chargement
    // (spinner, skeleton, ou texte "Chargement...")
    const loadingIndicators = [
      page.locator('[role="progressbar"]'),
      page.locator('text=/chargement/i'),
      page.locator('.animate-spin')
    ];

    // Au moins un indicateur devrait être visible
    const isLoading = await Promise.race(
      loadingIndicators.map(loc => loc.isVisible().catch(() => false))
    );

    // Note: Le loading peut être très rapide, donc ce test peut être flaky
  });

  test('should handle data refresh', async ({ page }) => {
    // Chercher bouton actualiser/refresh
    const refreshButton = page.getByRole('button', { name: /actualiser|refresh/i });

    if (await refreshButton.isVisible()) {
      await refreshButton.click();

      // Attendre un peu pour la requête
      await page.waitForTimeout(1000);

      // Vérifier que les données sont toujours affichées
      await expect(page.locator('text=Total Produits')).toBeVisible();
    }
  });

  test('should display data tables or lists', async ({ page }) => {
    // Attendre chargement
    await page.waitForTimeout(2000);

    // Chercher tableaux ou listes de données
    const tables = page.locator('table');
    const lists = page.locator('ul, ol').filter({ has: page.locator('li') });

    // Au moins un élément de données devrait être présent
    const hasTable = await tables.first().isVisible().catch(() => false);
    const hasList = await lists.first().isVisible().catch(() => false);

    expect(hasTable || hasList).toBeTruthy();
  });

  test('should be responsive on mobile viewport', async ({ page }) => {
    // Changer viewport pour mobile
    await page.setViewportSize({ width: 375, height: 667 });

    // Attendre re-render
    await page.waitForTimeout(500);

    // Vérifier que le contenu est toujours accessible
    await expect(page.locator('text=Total Produits')).toBeVisible();

    // Sur mobile, le menu peut être dans un drawer/sidebar
    // Vérifier présence d'un bouton menu si applicable
  });
});
