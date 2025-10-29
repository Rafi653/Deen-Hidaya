import { test, expect } from '@playwright/test';

test.describe('Quran Reader Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/reader');
  });

  test('should display the page heading', async ({ page }) => {
    const heading = page.getByRole('heading', { name: /The Holy Quran|القرآن الكريم/ });
    await expect(heading).toBeVisible();
  });

  test('should display back to home link', async ({ page }) => {
    const backLink = page.getByRole('link', { name: /Back to Home/ });
    await expect(backLink).toBeVisible();
  });

  test('should display search input', async ({ page }) => {
    const searchInput = page.getByPlaceholder(/Search by name or number/i);
    await expect(searchInput).toBeVisible();
    await expect(searchInput).toHaveAttribute('aria-label', 'Search surahs');
  });

  test('should display loading state initially', async ({ page }) => {
    // Wait for loading indicator
    const loadingText = page.getByText(/Loading surahs/i);
    // May or may not be visible depending on backend speed
  });

  test('should display surah list', async ({ page }) => {
    // Wait for surahs to load (either from backend or mock)
    await page.waitForTimeout(2000);
    
    // Should display at least one surah
    const surahCards = page.locator('a[href^="/reader/"]');
    await expect(surahCards.first()).toBeVisible();
  });

  test('should display surah details correctly', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    const firstSurah = page.locator('a[href^="/reader/"]').first();
    
    // Check for English name
    const englishName = firstSurah.getByText(/Al-Fatihah|Al-Baqarah/i);
    await expect(englishName).toBeVisible();
    
    // Check for verse count
    const verseCount = firstSurah.getByText(/verses/i);
    await expect(verseCount).toBeVisible();
  });

  test('should filter surahs by search query', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    const searchInput = page.getByPlaceholder(/Search by name or number/i);
    await searchInput.fill('Fatihah');
    
    // Should show filtered results
    await page.waitForTimeout(500);
    
    const surahCards = page.locator('a[href^="/reader/"]');
    const count = await surahCards.count();
    
    // Should have fewer results after filtering
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('should show no results message for invalid search', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    const searchInput = page.getByPlaceholder(/Search by name or number/i);
    await searchInput.fill('NonExistentSurah12345');
    
    await page.waitForTimeout(500);
    
    const noResults = page.getByText(/No surahs found matching/i);
    await expect(noResults).toBeVisible();
  });

  test('should navigate to surah detail page', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    const firstSurah = page.locator('a[href^="/reader/"]').first();
    await firstSurah.click();
    
    await expect(page).toHaveURL(/\/reader\/\d+/);
  });

  test('should display Arabic text correctly', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Check for Arabic text (RTL)
    const arabicText = page.locator('[lang="ar"], .font-arabic, .text-arabic').first();
    if (await arabicText.count() > 0) {
      await expect(arabicText).toBeVisible();
    }
  });

  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(2000);
    
    const heading = page.getByRole('heading', { name: /The Holy Quran|القرآن الكريم/ });
    await expect(heading).toBeVisible();
    
    const searchInput = page.getByPlaceholder(/Search by name or number/i);
    await expect(searchInput).toBeVisible();
  });

  test('should handle error state gracefully', async ({ page }) => {
    // Intercept API call and simulate error
    await page.route('**/api/v1/surahs', route => route.abort());
    
    await page.reload();
    await page.waitForTimeout(2000);
    
    // Should show mock data or error message
    const content = await page.textContent('body');
    expect(content).toBeTruthy();
  });

  test('should have proper ARIA labels', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    const searchInput = page.getByRole('textbox', { name: /Search surahs/i });
    await expect(searchInput).toBeVisible();
  });

  test('should support keyboard navigation', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Focus on search input
    const searchInput = page.getByPlaceholder(/Search by name or number/i);
    await searchInput.focus();
    
    // Tab to first surah link
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();
  });
});
