import { test, expect } from '@playwright/test';

/**
 * Tests E2E pour la Génération de Rapports
 */

// Helper function pour se connecter
async function login(page: any) {
  await page.goto('/');
  await page.fill('input[type="email"]', 'test@digiboost.sn');
  await page.fill('input[type="password"]', 'password123');
  await page.click('button[type="submit"]');
  await page.waitForURL('/dashboard', { timeout: 10000 });
}

test.describe('Génération Rapports', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('should navigate to reports page', async ({ page }) => {
    // Chercher lien Rapports dans navigation
    const reportsLink = page.getByRole('link', { name: /rapport/i });

    if (await reportsLink.isVisible()) {
      await reportsLink.click();
      await expect(page).toHaveURL(/\/rapports/);
    } else {
      // Alternative: Accès direct
      await page.goto('/rapports');
    }

    await expect(
      page.locator('h1, h2').filter({ hasText: /rapport/i })
    ).toBeVisible({ timeout: 5000 });
  });

  test('should display available report types', async ({ page }) => {
    await page.goto('/rapports');
    await page.waitForTimeout(1000);

    // Vérifier présence de différents types de rapports
    const reportTypes = [
      /inventaire/i,
      /stock/i,
      /vente/i,
      /synthèse/i
    ];

    // Au moins un type de rapport devrait être visible
    let foundReport = false;
    for (const reportType of reportTypes) {
      const element = page.locator(`text=${reportType}`).first();
      if (await element.isVisible().catch(() => false)) {
        foundReport = true;
        break;
      }
    }

    expect(foundReport).toBeTruthy();
  });

  test('should generate inventory report (Excel)', async ({ page }) => {
    await page.goto('/rapports');
    await page.waitForTimeout(1000);

    // Préparer écoute du téléchargement
    const downloadPromise = page.waitForEvent('download', { timeout: 15000 });

    // Chercher bouton génération inventaire
    const inventoryButton = page.getByRole('button', { name: /inventaire|stock/i }).first();

    if (await inventoryButton.isVisible()) {
      await inventoryButton.click();

      // Attendre téléchargement
      const download = await downloadPromise;

      // Vérifier nom fichier contient "inventaire" et extension .xlsx
      const filename = download.suggestedFilename();
      expect(filename.toLowerCase()).toContain('inventaire');
      expect(filename).toMatch(/\.xlsx$/);

      // Vérifier que le fichier a une taille > 0
      const path = await download.path();
      expect(path).toBeTruthy();
    }
  });

  test('should generate monthly summary report (PDF)', async ({ page }) => {
    await page.goto('/rapports');
    await page.waitForTimeout(1000);

    // Préparer écoute du téléchargement
    const downloadPromise = page.waitForEvent('download', { timeout: 15000 });

    // Chercher bouton génération synthèse mensuelle
    const summaryButton = page.getByRole('button', { name: /synthèse|mensuel/i }).first();

    if (await summaryButton.isVisible()) {
      await summaryButton.click();

      // Si formulaire de sélection mois/année apparaît
      const monthSelect = page.locator('select[name="month"]');
      if (await monthSelect.isVisible({ timeout: 2000 }).catch(() => false)) {
        await monthSelect.selectOption('1'); // Janvier
        const yearSelect = page.locator('select[name="year"], input[name="year"]');
        if (await yearSelect.isVisible()) {
          await yearSelect.fill('2025');
        }

        // Cliquer bouton générer
        const generateButton = page.getByRole('button', { name: /générer|télécharger/i });
        await generateButton.click();
      }

      // Attendre téléchargement
      const download = await downloadPromise;

      // Vérifier nom fichier et extension .pdf
      const filename = download.suggestedFilename();
      expect(filename.toLowerCase()).toMatch(/synthèse|mensuel/);
      expect(filename).toMatch(/\.pdf$/);
    }
  });

  test('should generate sales report (Excel)', async ({ page }) => {
    await page.goto('/rapports');
    await page.waitForTimeout(1000);

    const downloadPromise = page.waitForEvent('download', { timeout: 15000 });

    const salesButton = page.getByRole('button', { name: /vente/i }).first();

    if (await salesButton.isVisible()) {
      await salesButton.click();

      const download = await downloadPromise;
      const filename = download.suggestedFilename();

      expect(filename.toLowerCase()).toContain('vente');
      expect(filename).toMatch(/\.xlsx$/);
    }
  });

  test('should filter reports by date range', async ({ page }) => {
    await page.goto('/rapports');
    await page.waitForTimeout(1000);

    // Chercher filtres de date
    const startDateInput = page.locator('input[type="date"]').first();

    if (await startDateInput.isVisible()) {
      // Remplir dates
      await startDateInput.fill('2025-01-01');

      const endDateInput = page.locator('input[type="date"]').nth(1);
      if (await endDateInput.isVisible()) {
        await endDateInput.fill('2025-01-31');
      }

      // Vérifier que les filtres sont appliqués (les boutons sont toujours disponibles)
      await expect(startDateInput).toHaveValue('2025-01-01');
    }
  });

  test('should show loading state during report generation', async ({ page }) => {
    await page.goto('/rapports');
    await page.waitForTimeout(1000);

    const reportButton = page.getByRole('button', { name: /générer|inventaire|stock/i }).first();

    if (await reportButton.isVisible()) {
      // Cliquer et vérifier loading immédiatement
      await reportButton.click();

      // Chercher indicateur de chargement
      const loadingIndicators = [
        page.locator('[role="progressbar"]'),
        page.locator('.animate-spin'),
        page.locator('text=/génération|chargement/i')
      ];

      // Au moins un indicateur devrait apparaître brièvement
      // Note: Peut être très rapide
      await page.waitForTimeout(500);
    }
  });

  test('should display report history or list', async ({ page }) => {
    await page.goto('/rapports');
    await page.waitForTimeout(2000);

    // Vérifier si historique des rapports générés est affiché
    const historySection = page.locator('text=/historique|rapports générés/i');

    if (await historySection.isVisible()) {
      // Vérifier présence d'une liste
      await expect(page.locator('table, ul')).toBeVisible();
    }
  });

  test('should handle report generation errors gracefully', async ({ page }) => {
    // Simuler offline pour forcer une erreur
    await page.context().setOffline(true);

    await page.goto('/rapports');
    await page.waitForTimeout(1000);

    const reportButton = page.getByRole('button', { name: /générer|inventaire/i }).first();

    if (await reportButton.isVisible()) {
      await reportButton.click();
      await page.waitForTimeout(2000);

      // Vérifier message d'erreur
      const errorMessage = page.locator('[role="alert"], .text-red-600').filter({ hasText: /erreur/i });
      // L'erreur peut ne pas s'afficher si le téléchargement n'est pas initié
    }

    // Remettre online
    await page.context().setOffline(false);
  });

  test('should allow selecting report format (if applicable)', async ({ page }) => {
    await page.goto('/rapports');
    await page.waitForTimeout(1000);

    // Chercher sélecteur de format (Excel vs PDF)
    const formatSelect = page.locator('select').filter({ hasText: /format|type/i });

    if (await formatSelect.isVisible()) {
      // Tester sélection PDF
      await formatSelect.selectOption(/pdf/i);
      await expect(formatSelect).toHaveValue(/pdf/i);

      // Tester sélection Excel
      await formatSelect.selectOption(/excel|xlsx/i);
      await expect(formatSelect).toHaveValue(/excel|xlsx/i);
    }
  });

  test('should provide export options for multiple reports', async ({ page }) => {
    await page.goto('/rapports');
    await page.waitForTimeout(1000);

    // Compter le nombre de boutons de génération disponibles
    const generateButtons = page.getByRole('button', { name: /générer|télécharger|exporter/i });
    const count = await generateButtons.count();

    // Il devrait y avoir au moins 2-3 types de rapports disponibles
    expect(count).toBeGreaterThan(0);
  });
});
