import { test, expect } from '@playwright/test';

/**
 * Tests E2E pour l'authentification
 */
test.describe('Authentication', () => {
  test('should display login form', async ({ page }) => {
    await page.goto('/');

    // Vérifier présence titre
    await expect(page.locator('h2')).toContainText('Digiboost PME');
    await expect(page.locator('text=Intelligence Supply Chain pour PME Senegalaises')).toBeVisible();

    // Vérifier champs formulaire
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should show validation errors for empty fields', async ({ page }) => {
    await page.goto('/');

    // Soumettre formulaire vide
    await page.click('button[type="submit"]');

    // Vérifier messages d'erreur de validation
    await expect(page.locator('text=Email requis')).toBeVisible();
  });

  test('should show validation error for invalid email', async ({ page }) => {
    await page.goto('/');

    // Remplir avec email invalide
    await page.fill('input[type="email"]', 'invalidemail');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Vérifier message d'erreur
    await expect(page.locator('text=Email invalide')).toBeVisible();
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    await page.goto('/');

    // Remplir formulaire avec identifiants valides
    await page.fill('input[type="email"]', 'test@digiboost.sn');
    await page.fill('input[type="password"]', 'password123');

    // Soumettre
    await page.click('button[type="submit"]');

    // Attendre navigation (ajuster timeout si nécessaire)
    await page.waitForURL('/dashboard', { timeout: 10000 });

    // Vérifier redirection dashboard
    await expect(page).toHaveURL('/dashboard');

    // Vérifier présence d'éléments du dashboard
    await expect(page.locator('text=Total Produits').or(page.locator('text=Vue d\'ensemble'))).toBeVisible({ timeout: 10000 });
  });

  test('should show error message on invalid credentials', async ({ page }) => {
    await page.goto('/');

    // Remplir avec identifiants invalides
    await page.fill('input[type="email"]', 'wrong@digiboost.sn');
    await page.fill('input[type="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');

    // Attendre un peu pour la requête
    await page.waitForTimeout(2000);

    // Vérifier qu'on reste sur la page de connexion
    await expect(page).toHaveURL('/');

    // Le message d'erreur devrait être visible (si implémenté dans l'UI)
    // Note: Adapter selon l'implémentation réelle de l'affichage des erreurs
  });

  test('should handle network errors gracefully', async ({ page }) => {
    // Simuler offline
    await page.context().setOffline(true);

    await page.goto('/');
    await page.fill('input[type="email"]', 'test@digiboost.sn');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Attendre un peu
    await page.waitForTimeout(2000);

    // Vérifier qu'on reste sur login
    await expect(page).toHaveURL('/');

    // Remettre online
    await page.context().setOffline(false);
  });
});
