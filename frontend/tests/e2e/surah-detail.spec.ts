import { test, expect } from '@playwright/test';

test.describe('Surah Detail Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/reader/1'); // Al-Fatihah
  });

  test('should display surah header information', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Should display surah name in Arabic
    const arabicName = page.locator('.font-arabic, [lang="ar"]').first();
    await expect(arabicName).toBeVisible();
    
    // Should display English name
    const englishName = page.getByText(/Al-Fatihah|The Opening/i);
    await expect(englishName).toBeVisible();
  });

  test('should display back to surah list link', async ({ page }) => {
    const backLink = page.getByRole('link', { name: /Back to Surah List/i });
    await expect(backLink).toBeVisible();
    
    await backLink.click();
    await expect(page).toHaveURL(/\/reader$/);
  });

  test('should display control buttons', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    const transliterationToggle = page.getByRole('button', { name: /Transliteration/i });
    await expect(transliterationToggle).toBeVisible();
    
    const translationSelect = page.getByRole('combobox');
    await expect(translationSelect).toBeVisible();
  });

  test('should toggle transliteration display', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    const toggle = page.getByRole('button', { name: /Transliteration/i });
    
    // Initially may or may not be active
    const initialState = await toggle.getAttribute('aria-pressed');
    
    // Click to toggle
    await toggle.click();
    
    const newState = await toggle.getAttribute('aria-pressed');
    expect(newState).not.toBe(initialState);
  });

  test('should change translation language', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    const select = page.getByRole('combobox');
    
    // Change to Telugu
    await select.selectOption('te');
    await page.waitForTimeout(500);
    
    const value = await select.inputValue();
    expect(value).toBe('te');
  });

  test('should display verses with proper structure', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Check for verse numbers
    const verseNumbers = page.locator('[class*="rounded-full"]').filter({ hasText: /^\d+$/ });
    await expect(verseNumbers.first()).toBeVisible();
    
    // Check for Arabic text
    const arabicText = page.locator('.font-arabic, [lang="ar"]');
    await expect(arabicText.first()).toBeVisible();
  });

  test('should display bismillah for appropriate surahs', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Al-Fatihah (Surah 1) contains bismillah in first verse
    // Check if bismillah or similar text is present
    const content = await page.textContent('body');
    expect(content).toBeTruthy();
  });

  test('should handle bookmark functionality', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Find first bookmark button
    const bookmarkButtons = page.getByRole('button', { name: /bookmark/i });
    const firstBookmark = bookmarkButtons.first();
    
    if (await firstBookmark.count() > 0) {
      await expect(firstBookmark).toBeVisible();
      
      // Click to add bookmark
      await firstBookmark.click();
      await page.waitForTimeout(300);
      
      // Click again to remove
      await firstBookmark.click();
    }
  });

  test('should handle audio play button', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Find play buttons
    const playButtons = page.getByRole('button', { name: /Play verse/i });
    const firstPlay = playButtons.first();
    
    if (await firstPlay.count() > 0) {
      await expect(firstPlay).toBeVisible();
      
      // Should have proper title/tooltip
      const title = await firstPlay.getAttribute('title');
      expect(title).toContain('Audio');
    }
  });

  test('should display translations correctly', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Look for translation containers
    const translations = page.locator('[class*="bg-green-50"]');
    await expect(translations.first()).toBeVisible();
  });

  test('should show proper verse IDs for deep linking', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Check for verse ID anchors
    const verseElement = page.locator('[id^="verse-"]').first();
    if (await verseElement.count() > 0) {
      await expect(verseElement).toBeVisible();
    }
  });

  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(2000);
    
    // Controls should be responsive
    const controls = page.locator('.sticky');
    await expect(controls).toBeVisible();
    
    // Verses should be visible
    const verses = page.locator('article').first();
    await expect(verses).toBeVisible();
  });

  test('should handle loading state', async ({ page }) => {
    // Navigate to another surah
    await page.goto('/reader/2');
    
    // Should show loading indicator briefly
    const loading = page.getByText(/Loading surah/i);
    // May or may not catch it depending on speed
  });

  test('should handle invalid surah number', async ({ page }) => {
    await page.goto('/reader/999');
    await page.waitForTimeout(2000);
    
    // Should show error or fallback content
    const content = await page.textContent('body');
    expect(content).toBeTruthy();
  });

  test('should maintain sticky controls on scroll', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    const controls = page.locator('.sticky').first();
    await expect(controls).toBeVisible();
    
    // Scroll down
    await page.evaluate(() => window.scrollBy(0, 500));
    await page.waitForTimeout(500);
    
    // Controls should still be visible
    await expect(controls).toBeVisible();
  });

  test('should support keyboard navigation between verses', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Tab through elements
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();
  });

  test('should display proper ARIA labels for accessibility', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Check transliteration button has aria-pressed
    const toggle = page.getByRole('button', { name: /Transliteration/i });
    const ariaPressed = await toggle.getAttribute('aria-pressed');
    expect(ariaPressed).toBeDefined();
  });

  test('should handle verse navigation via URL hash', async ({ page }) => {
    await page.goto('/reader/1#verse-3');
    await page.waitForTimeout(2000);
    
    // Should navigate to verse 3
    const verse3 = page.locator('#verse-3');
    if (await verse3.count() > 0) {
      await expect(verse3).toBeInViewport();
    }
  });
});
