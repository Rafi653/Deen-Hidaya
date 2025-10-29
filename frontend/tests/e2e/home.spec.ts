import { test, expect } from '@playwright/test';

test.describe('Home Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display the page title', async ({ page }) => {
    await expect(page).toHaveTitle(/Deen Hidaya/);
  });

  test('should display the main heading', async ({ page }) => {
    const heading = page.getByRole('heading', { name: 'Deen Hidaya' });
    await expect(heading).toBeVisible();
  });

  test('should display navigation buttons', async ({ page }) => {
    const readQuranButton = page.getByRole('link', { name: /Read Quran/i });
    const qaButton = page.getByRole('link', { name: /Ask Questions/i });

    await expect(readQuranButton).toBeVisible();
    await expect(qaButton).toBeVisible();
  });

  test('should navigate to reader page', async ({ page }) => {
    await page.getByRole('link', { name: /Read Quran/i }).click();
    await expect(page).toHaveURL(/\/reader/);
  });

  test('should navigate to Q&A page', async ({ page }) => {
    await page.getByRole('link', { name: /Ask Questions/i }).click();
    await expect(page).toHaveURL(/\/qa/);
  });

  test('should display system status', async ({ page }) => {
    const frontendStatus = page.getByText(/Frontend:/);
    const backendStatus = page.getByText(/Backend:/);

    await expect(frontendStatus).toBeVisible();
    await expect(backendStatus).toBeVisible();
  });

  test('should check frontend health status', async ({ page }) => {
    // Wait for health check to complete
    await page.waitForTimeout(1000);

    const statusText = await page.getByText(/Frontend:/).locator('..').textContent();
    expect(statusText).toMatch(/healthy|checking|error/i);
  });

  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    
    const heading = page.getByRole('heading', { name: 'Deen Hidaya' });
    await expect(heading).toBeVisible();
    
    const buttons = page.getByRole('link');
    await expect(buttons.first()).toBeVisible();
  });

  test('should have proper semantic HTML structure', async ({ page }) => {
    const main = page.locator('main');
    await expect(main).toBeVisible();
    
    const heading = page.getByRole('heading', { level: 1 });
    await expect(heading).toBeVisible();
  });

  test('should support keyboard navigation', async ({ page }) => {
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();
  });
});
