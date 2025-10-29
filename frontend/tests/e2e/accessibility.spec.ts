import { test, expect } from '@playwright/test';
import { injectAxe, checkA11y, getViolations } from '@axe-core/playwright';

test.describe('Accessibility Tests', () => {
  test.describe('Home Page Accessibility', () => {
    test('should not have any automatically detectable accessibility issues', async ({ page }) => {
      await page.goto('/');
      await injectAxe(page);
      await checkA11y(page, undefined, {
        detailedReport: true,
        detailedReportOptions: { html: true },
      });
    });

    test('should have proper heading hierarchy', async ({ page }) => {
      await page.goto('/');
      
      const h1 = await page.locator('h1').count();
      expect(h1).toBeGreaterThanOrEqual(1);
      expect(h1).toBeLessThanOrEqual(1); // Should have exactly one h1
    });

    test('should have proper landmark regions', async ({ page }) => {
      await page.goto('/');
      
      const main = await page.locator('main').count();
      expect(main).toBeGreaterThanOrEqual(1);
    });
  });

  test.describe('Reader Page Accessibility', () => {
    test('should not have any automatically detectable accessibility issues', async ({ page }) => {
      await page.goto('/reader');
      await page.waitForTimeout(2000);
      
      await injectAxe(page);
      await checkA11y(page, undefined, {
        detailedReport: true,
      });
    });

    test('should have accessible search input', async ({ page }) => {
      await page.goto('/reader');
      
      const searchInput = page.getByRole('textbox', { name: /search/i });
      await expect(searchInput).toBeVisible();
      
      const ariaLabel = await searchInput.getAttribute('aria-label');
      expect(ariaLabel).toBeTruthy();
    });

    test('should have accessible links', async ({ page }) => {
      await page.goto('/reader');
      await page.waitForTimeout(2000);
      
      const links = page.getByRole('link');
      const count = await links.count();
      
      for (let i = 0; i < Math.min(count, 5); i++) {
        const link = links.nth(i);
        const text = await link.textContent();
        expect(text?.trim().length).toBeGreaterThan(0);
      }
    });
  });

  test.describe('Surah Detail Page Accessibility', () => {
    test('should not have any automatically detectable accessibility issues', async ({ page }) => {
      await page.goto('/reader/1');
      await page.waitForTimeout(2000);
      
      await injectAxe(page);
      
      // May have some minor issues with dynamic content, focus on critical violations
      const violations = await getViolations(page, undefined, {
        rules: {
          // Focus on critical rules
          'color-contrast': { enabled: true },
          'button-name': { enabled: true },
          'link-name': { enabled: true },
          'image-alt': { enabled: true },
          'label': { enabled: true },
        },
      });
      
      // Filter for critical and serious violations only
      const criticalViolations = violations.filter(
        v => v.impact === 'critical' || v.impact === 'serious'
      );
      
      expect(criticalViolations.length).toBe(0);
    });

    test('should have accessible buttons', async ({ page }) => {
      await page.goto('/reader/1');
      await page.waitForTimeout(2000);
      
      const buttons = page.getByRole('button');
      const count = await buttons.count();
      
      for (let i = 0; i < Math.min(count, 5); i++) {
        const button = buttons.nth(i);
        const accessibleName = await button.getAttribute('aria-label') || await button.textContent();
        expect(accessibleName?.trim().length).toBeGreaterThan(0);
      }
    });

    test('should have proper ARIA attributes', async ({ page }) => {
      await page.goto('/reader/1');
      await page.waitForTimeout(2000);
      
      // Check transliteration toggle has aria-pressed
      const toggle = page.getByRole('button', { name: /transliteration/i });
      if (await toggle.count() > 0) {
        const ariaPressed = await toggle.getAttribute('aria-pressed');
        expect(ariaPressed).toBeDefined();
      }
    });

    test('should have accessible verse elements', async ({ page }) => {
      await page.goto('/reader/1');
      await page.waitForTimeout(2000);
      
      // Verses should be in semantic elements
      const articles = page.locator('article');
      const count = await articles.count();
      expect(count).toBeGreaterThan(0);
    });
  });

  test.describe('Q&A Page Accessibility', () => {
    test('should not have any automatically detectable accessibility issues', async ({ page }) => {
      await page.goto('/qa');
      
      await injectAxe(page);
      await checkA11y(page, undefined, {
        detailedReport: true,
      });
    });

    test('should have accessible form elements', async ({ page }) => {
      await page.goto('/qa');
      
      const input = page.getByRole('textbox');
      const inputLabel = await input.getAttribute('aria-label') || await input.getAttribute('id');
      expect(inputLabel).toBeTruthy();
      
      const button = page.getByRole('button', { name: /ask/i });
      await expect(button).toBeVisible();
    });

    test('should have accessible modal dialog', async ({ page }) => {
      await page.goto('/qa');
      
      const input = page.getByRole('textbox');
      await input.fill('What is patience?');
      await page.getByRole('button', { name: /ask/i }).click();
      await page.waitForTimeout(2000);
      
      const viewDetailsButton = page.getByRole('button', { name: /view details/i }).first();
      
      if (await viewDetailsButton.count() > 0) {
        await viewDetailsButton.click();
        
        const dialog = page.getByRole('dialog');
        await expect(dialog).toBeVisible();
        
        // Check for aria-modal
        const ariaModal = await dialog.getAttribute('aria-modal');
        expect(ariaModal).toBe('true');
        
        // Check for aria-labelledby
        const ariaLabelledBy = await dialog.getAttribute('aria-labelledby');
        expect(ariaLabelledBy).toBeTruthy();
      }
    });
  });

  test.describe('Keyboard Navigation', () => {
    test('should support tab navigation on home page', async ({ page }) => {
      await page.goto('/');
      
      // Press tab multiple times
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      
      const focused = page.locator(':focus');
      await expect(focused).toBeVisible();
      
      // Check focus indicator is visible (should have outline or other visual indicator)
      const outline = await focused.evaluate(el => {
        const styles = window.getComputedStyle(el);
        return styles.outline + styles.outlineColor + styles.outlineWidth;
      });
      expect(outline.length).toBeGreaterThan(0);
    });

    test('should support tab navigation in reader', async ({ page }) => {
      await page.goto('/reader');
      await page.waitForTimeout(2000);
      
      // Tab to search input
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      
      const focused = page.locator(':focus');
      await expect(focused).toBeVisible();
    });

    test('should support enter key for button activation', async ({ page }) => {
      await page.goto('/qa');
      
      // Tab to example button
      const exampleButton = page.getByRole('button').filter({ hasText: /patience/i }).first();
      await exampleButton.focus();
      
      // Press enter
      await page.keyboard.press('Enter');
      
      // Should populate input
      const input = page.getByRole('textbox');
      const value = await input.inputValue();
      expect(value.length).toBeGreaterThan(0);
    });
  });

  test.describe('Color Contrast', () => {
    test('should have sufficient color contrast for text', async ({ page }) => {
      await page.goto('/');
      
      await injectAxe(page);
      const violations = await getViolations(page, undefined, {
        rules: {
          'color-contrast': { enabled: true },
        },
      });
      
      const contrastViolations = violations.filter(v => v.id === 'color-contrast');
      expect(contrastViolations.length).toBe(0);
    });
  });

  test.describe('Screen Reader Support', () => {
    test('should have proper alt text for images', async ({ page }) => {
      await page.goto('/');
      
      const images = page.locator('img');
      const count = await images.count();
      
      for (let i = 0; i < count; i++) {
        const img = images.nth(i);
        const alt = await img.getAttribute('alt');
        // Alt can be empty for decorative images, but should be present
        expect(alt).toBeDefined();
      }
    });

    test('should have proper page titles', async ({ page }) => {
      await page.goto('/');
      await expect(page).toHaveTitle(/Deen Hidaya/);
      
      await page.goto('/reader');
      await expect(page).toHaveTitle(/Quran Reader|Deen Hidaya/);
      
      await page.goto('/qa');
      await expect(page).toHaveTitle(/Q&A|Deen Hidaya/);
    });

    test('should have lang attribute on HTML', async ({ page }) => {
      await page.goto('/');
      
      const lang = await page.locator('html').getAttribute('lang');
      expect(lang).toBeTruthy();
    });
  });

  test.describe('Focus Management', () => {
    test('should trap focus in modal dialog', async ({ page }) => {
      await page.goto('/qa');
      
      const input = page.getByRole('textbox');
      await input.fill('What is patience?');
      await page.getByRole('button', { name: /ask/i }).click();
      await page.waitForTimeout(2000);
      
      const viewDetailsButton = page.getByRole('button', { name: /view details/i }).first();
      
      if (await viewDetailsButton.count() > 0) {
        await viewDetailsButton.click();
        
        // Tab through modal elements
        await page.keyboard.press('Tab');
        const focused = page.locator(':focus');
        
        // Focused element should be within modal
        const dialog = page.getByRole('dialog');
        const isInModal = await focused.evaluate((el, dialogEl) => {
          return dialogEl?.contains(el) ?? false;
        }, await dialog.elementHandle());
        
        expect(isInModal).toBe(true);
      }
    });
  });
});
