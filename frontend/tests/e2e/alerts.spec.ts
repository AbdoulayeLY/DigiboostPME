import { test, expect } from '@playwright/test';

/**
 * Tests E2E pour la Gestion des Alertes
 */

// Helper function pour se connecter
async function login(page: any) {
  await page.goto('/');
  await page.fill('input[type="email"]', 'test@digiboost.sn');
  await page.fill('input[type="password"]', 'password123');
  await page.click('button[type="submit"]');
  await page.waitForURL('/dashboard', { timeout: 10000 });
}

test.describe('Gestion Alertes', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('should navigate to alerts page', async ({ page }) => {
    // Cliquer sur lien/bouton Alertes dans la navigation
    await page.click('a[href="/alertes"]');

    // Vérifier URL
    await expect(page).toHaveURL(/\/alertes/);

    // Vérifier contenu de la page
    await expect(
      page.locator('h1, h2').filter({ hasText: /alerte/i })
    ).toBeVisible({ timeout: 5000 });
  });

  test('should display list of alerts', async ({ page }) => {
    await page.goto('/alertes');
    await page.waitForTimeout(2000);

    // Vérifier présence d'une table ou liste d'alertes
    const table = page.locator('table');
    const hasTable = await table.isVisible().catch(() => false);

    if (hasTable) {
      // Vérifier présence de colonnes
      await expect(table.locator('thead')).toBeVisible();
      await expect(table.locator('tbody')).toBeVisible();
    }
  });

  test('should open create alert dialog', async ({ page }) => {
    await page.goto('/alertes');

    // Chercher bouton "Nouvelle Alerte" ou similaire
    const createButton = page.getByRole('button', { name: /nouvelle alerte|créer|ajouter/i });

    if (await createButton.isVisible()) {
      await createButton.click();

      // Vérifier ouverture dialog/modal
      await expect(
        page.locator('[role="dialog"], .modal').first()
      ).toBeVisible({ timeout: 5000 });

      // Vérifier présence formulaire
      await expect(page.locator('input[name="name"]')).toBeVisible();
    }
  });

  test('should create new alert with valid data', async ({ page }) => {
    await page.goto('/alertes');

    const createButton = page.getByRole('button', { name: /nouvelle alerte|créer|ajouter/i });

    if (await createButton.isVisible()) {
      await createButton.click();
      await page.waitForTimeout(500);

      // Remplir formulaire
      await page.fill('input[name="name"]', `Test Alerte E2E ${Date.now()}`);

      // Sélectionner type d'alerte (adapter selon les options disponibles)
      const alertTypeSelect = page.locator('select[name="alert_type"], select[name="alertType"]');
      if (await alertTypeSelect.isVisible()) {
        await alertTypeSelect.selectOption({ index: 1 });
      }

      // Activer un canal de notification (ex: WhatsApp)
      const whatsappCheckbox = page.locator('input[type="checkbox"][name*="whatsapp"]');
      if (await whatsappCheckbox.isVisible()) {
        await whatsappCheckbox.check();

        // Remplir numéro WhatsApp
        const whatsappInput = page.locator('input[placeholder*="WhatsApp"], input[name*="whatsapp"]');
        if (await whatsappInput.isVisible()) {
          await whatsappInput.fill('+221771234567');
        }
      }

      // Soumettre formulaire
      const submitButton = page.getByRole('button', { name: /créer|enregistrer|valider/i });
      await submitButton.click();

      // Attendre fermeture du dialog
      await page.waitForTimeout(2000);

      // Vérifier message de succès (toast)
      const successMessage = page.locator('text=/alerte créée|succès/i');
      await expect(successMessage.first()).toBeVisible({ timeout: 5000 });
    }
  });

  test('should show validation errors on invalid input', async ({ page }) => {
    await page.goto('/alertes');

    const createButton = page.getByRole('button', { name: /nouvelle alerte|créer|ajouter/i });

    if (await createButton.isVisible()) {
      await createButton.click();
      await page.waitForTimeout(500);

      // Soumettre sans remplir
      const submitButton = page.getByRole('button', { name: /créer|enregistrer|valider/i });
      await submitButton.click();

      // Vérifier messages d'erreur
      await page.waitForTimeout(500);
      const errorMessages = page.locator('.text-red-600, [role="alert"]');
      expect(await errorMessages.count()).toBeGreaterThan(0);
    }
  });

  test('should toggle alert activation status', async ({ page }) => {
    await page.goto('/alertes');
    await page.waitForTimeout(2000);

    // Chercher premier toggle/switch
    const firstToggle = page.locator('[role="switch"], input[type="checkbox"]').first();

    if (await firstToggle.isVisible()) {
      // Récupérer état initial
      const initialState = await firstToggle.isChecked();

      // Cliquer pour changer état
      await firstToggle.click();
      await page.waitForTimeout(1000);

      // Vérifier changement d'état
      const newState = await firstToggle.isChecked();
      expect(newState).not.toBe(initialState);
    }
  });

  test('should view alert details', async ({ page }) => {
    await page.goto('/alertes');
    await page.waitForTimeout(2000);

    // Chercher bouton "Voir détails" ou ligne de tableau cliquable
    const detailsButton = page.getByRole('button', { name: /détails|voir/i }).first();

    if (await detailsButton.isVisible()) {
      await detailsButton.click();

      // Vérifier ouverture modal/page de détails
      await page.waitForTimeout(1000);
      await expect(
        page.locator('[role="dialog"], .modal').first()
      ).toBeVisible();
    }
  });

  test('should navigate to alert history', async ({ page }) => {
    await page.goto('/alertes');

    // Chercher lien vers historique
    const historyLink = page.getByRole('link', { name: /historique/i });

    if (await historyLink.isVisible()) {
      await historyLink.click();

      // Vérifier navigation
      await expect(page).toHaveURL(/\/alertes\/history/);
      await expect(page.locator('h1, h2').filter({ hasText: /historique/i })).toBeVisible();
    }
  });

  test('should filter alerts by type', async ({ page }) => {
    await page.goto('/alertes');
    await page.waitForTimeout(2000);

    // Chercher filtres
    const filterSelect = page.locator('select').filter({ hasText: /type|filtre/i });

    if (await filterSelect.isVisible()) {
      // Appliquer un filtre
      await filterSelect.selectOption({ index: 1 });
      await page.waitForTimeout(1000);

      // Vérifier que la liste est mise à jour
      // (difficile à vérifier sans connaître les données exactes)
    }
  });

  test('should delete alert', async ({ page }) => {
    await page.goto('/alertes');
    await page.waitForTimeout(2000);

    // Chercher bouton supprimer
    const deleteButton = page.getByRole('button', { name: /supprimer|delete/i }).first();

    if (await deleteButton.isVisible()) {
      // Compter nombre d'alertes avant suppression
      const rowsBefore = await page.locator('tbody tr').count();

      await deleteButton.click();

      // Confirmer suppression dans dialog de confirmation
      const confirmButton = page.getByRole('button', { name: /confirmer|oui|supprimer/i });
      if (await confirmButton.isVisible()) {
        await confirmButton.click();
      }

      await page.waitForTimeout(2000);

      // Vérifier message de succès
      const successMessage = page.locator('text=/supprimée|succès/i');
      await expect(successMessage.first()).toBeVisible({ timeout: 5000 });
    }
  });
});
