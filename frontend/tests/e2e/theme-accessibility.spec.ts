import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Theme and Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should have accessibility controls visible on all pages', async ({ page }) => {
    // Check home page
    await expect(page.getByRole('region', { name: 'Accessibility controls' })).toBeVisible();
    await expect(page.getByLabel('Select theme preference')).toBeVisible();
    await expect(page.getByRole('button', { name: /set text size/i }).first()).toBeVisible();

    // Check reader page
    await page.goto('/reader');
    await expect(page.getByRole('region', { name: 'Accessibility controls' })).toBeVisible();

    // Check QA page
    await page.goto('/qa');
    await expect(page.getByRole('region', { name: 'Accessibility controls' })).toBeVisible();
  });

  test('should switch to dark mode', async ({ page }) => {
    const themeSelect = page.getByLabel('Select theme preference');
    
    // Verify initial state (should show light or system)
    await expect(page.locator('html')).not.toHaveClass(/dark/);
    
    // Switch to dark mode
    await themeSelect.selectOption('dark');
    
    // Verify dark mode is applied
    await expect(page.locator('html')).toHaveClass(/dark/);
    
    // Verify status updates
    await expect(page.getByText('(Dark)')).toBeVisible();
  });

  test('should persist theme preference across pages', async ({ page }) => {
    // Set dark mode
    await page.getByLabel('Select theme preference').selectOption('dark');
    await expect(page.locator('html')).toHaveClass(/dark/);
    
    // Navigate to another page
    await page.click('text=📖 Read Quran');
    await expect(page).toHaveURL('/reader');
    
    // Verify dark mode persists
    await expect(page.locator('html')).toHaveClass(/dark/);
    await expect(page.getByLabel('Select theme preference')).toHaveValue('dark');
  });

  test('should change font size', async ({ page }) => {
    // Click on large font size
    await page.click('button[aria-label="Set text size to Large"]');
    
    // Verify button is pressed
    await expect(page.getByRole('button', { name: 'Set text size to Large' })).toHaveAttribute('aria-pressed', 'true');
    
    // Navigate to reader page to see font changes
    await page.goto('/reader');
    
    // Verify font size persists
    await expect(page.getByRole('button', { name: 'Set text size to Large' })).toHaveAttribute('aria-pressed', 'true');
  });

  test('should have skip to content link', async ({ page }) => {
    const skipLink = page.getByRole('link', { name: 'Skip to main content' });
    
    // Focus the skip link with keyboard
    await page.keyboard.press('Tab');
    
    // Verify it becomes visible when focused
    await expect(skipLink).toBeFocused();
    
    // Click it
    await skipLink.click();
    
    // Verify main content is now in focus area
    await expect(page.locator('#main-content')).toBeVisible();
  });

  test('should be keyboard navigable', async ({ page }) => {
    // Tab through accessibility controls
    await page.keyboard.press('Tab'); // Skip link
    await page.keyboard.press('Tab'); // Theme select
    await expect(page.getByLabel('Select theme preference')).toBeFocused();
    
    // Change theme with keyboard
    await page.keyboard.press('ArrowDown');
    
    // Continue tabbing to font size controls
    await page.keyboard.press('Tab'); // Move to font size buttons
    await expect(page.getByRole('button', { name: /set text size/i }).first()).toBeFocused();
  });

  test('should pass accessibility scan on home page', async ({ page }) => {
    const accessibilityScanResults = await new AxeBuilder({ page })
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('should pass accessibility scan on reader page', async ({ page }) => {
    await page.goto('/reader');
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('should pass accessibility scan in dark mode', async ({ page }) => {
    // Switch to dark mode
    await page.getByLabel('Select theme preference').selectOption('dark');
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('should have proper ARIA labels on controls', async ({ page }) => {
    // Theme control
    await expect(page.getByLabel('Select theme preference')).toHaveAttribute('aria-label', 'Select theme preference');
    
    // Font size controls
    await expect(page.getByRole('button', { name: 'Set text size to Small' })).toHaveAttribute('aria-label', 'Set text size to Small');
    await expect(page.getByRole('button', { name: 'Set text size to Medium' })).toHaveAttribute('aria-label', 'Set text size to Medium');
    await expect(page.getByRole('button', { name: 'Set text size to Large' })).toHaveAttribute('aria-label', 'Set text size to Large');
    await expect(page.getByRole('button', { name: 'Set text size to Extra Large' })).toHaveAttribute('aria-label', 'Set text size to Extra Large');
  });

  test('should announce theme changes to screen readers', async ({ page }) => {
    // Check for live region
    const liveRegion = page.locator('[aria-live="polite"]');
    await expect(liveRegion).toBeVisible();
    
    // Change theme
    await page.getByLabel('Select theme preference').selectOption('dark');
    
    // Verify live region updates
    await expect(liveRegion).toContainText('Dark');
  });

  test('theme and font controls should work together', async ({ page }) => {
    // Set dark mode
    await page.getByLabel('Select theme preference').selectOption('dark');
    await expect(page.locator('html')).toHaveClass(/dark/);
    
    // Set large font
    await page.click('button[aria-label="Set text size to Large"]');
    await expect(page.getByRole('button', { name: 'Set text size to Large' })).toHaveAttribute('aria-pressed', 'true');
    
    // Navigate to reader
    await page.goto('/reader');
    
    // Verify both settings persist
    await expect(page.locator('html')).toHaveClass(/dark/);
    await expect(page.getByRole('button', { name: 'Set text size to Large' })).toHaveAttribute('aria-pressed', 'true');
  });
});
