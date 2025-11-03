import { test, expect } from '@playwright/test';

test.describe('Name Generator Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/name-generator');
  });

  test('should display the page title', async ({ page }) => {
    await expect(page).toHaveTitle(/Name Generator/);
  });

  test('should display the main heading', async ({ page }) => {
    const heading = page.getByRole('heading', { name: /Suggestive Name Generator/i });
    await expect(heading).toBeVisible();
  });

  test('should display back to home link', async ({ page }) => {
    const backLink = page.getByRole('link', { name: /Back to Home/i });
    await expect(backLink).toBeVisible();
  });

  test('should navigate back to home page', async ({ page }) => {
    await page.getByRole('link', { name: /Back to Home/i }).click();
    await expect(page).toHaveURL('/');
  });

  test('should display preference form', async ({ page }) => {
    const form = page.locator('form');
    await expect(form).toBeVisible();

    const entityTypeSelect = page.locator('select#entityType');
    await expect(entityTypeSelect).toBeVisible();

    const submitButton = page.getByRole('button', { name: /Generate Names/i });
    await expect(submitButton).toBeVisible();
  });

  test('should have entity type as required field', async ({ page }) => {
    const entityTypeSelect = page.locator('select#entityType');
    await expect(entityTypeSelect).toHaveAttribute('required', '');
  });

  test('should display all form fields', async ({ page }) => {
    // Entity Type
    await expect(page.locator('select#entityType')).toBeVisible();

    // Gender
    await expect(page.locator('select#gender')).toBeVisible();

    // Meaning
    await expect(page.locator('input#meaning')).toBeVisible();

    // Phonetic Preference
    await expect(page.locator('input#phonetic')).toBeVisible();
  });

  test('should display empty state message initially', async ({ page }) => {
    const emptyMessage = page.getByText(/Set your preferences and click "Generate Names"/i);
    await expect(emptyMessage).toBeVisible();
  });

  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    
    const heading = page.getByRole('heading', { name: /Suggestive Name Generator/i });
    await expect(heading).toBeVisible();
    
    const form = page.locator('form');
    await expect(form).toBeVisible();
  });

  test('should have proper semantic HTML structure', async ({ page }) => {
    const main = page.locator('main#main-content');
    await expect(main).toBeVisible();
    
    const heading = page.getByRole('heading', { level: 1 });
    await expect(heading).toBeVisible();

    const form = page.locator('form');
    await expect(form).toBeVisible();
  });

  test('should support keyboard navigation', async ({ page }) => {
    // Tab through form elements
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();
  });

  test('should display accessibility bar', async ({ page }) => {
    // The AccessibilityBar component should be present
    const skipLink = page.getByText(/Skip to content/i);
    await expect(skipLink).toBeVisible();
  });

  test('gender select should have correct options', async ({ page }) => {
    const genderSelect = page.locator('select#gender');
    
    // Check that options exist
    const anyOption = genderSelect.locator('option[value=""]');
    await expect(anyOption).toBeVisible();
    
    const maleOption = genderSelect.locator('option[value="male"]');
    await expect(maleOption).toBeVisible();
    
    const femaleOption = genderSelect.locator('option[value="female"]');
    await expect(femaleOption).toBeVisible();
    
    const unisexOption = genderSelect.locator('option[value="unisex"]');
    await expect(unisexOption).toBeVisible();
  });

  test('form inputs should accept text', async ({ page }) => {
    const meaningInput = page.locator('input#meaning');
    await meaningInput.fill('strength');
    await expect(meaningInput).toHaveValue('strength');

    const phoneticInput = page.locator('input#phonetic');
    await phoneticInput.fill('starts with A');
    await expect(phoneticInput).toHaveValue('starts with A');
  });

  test('should have dark mode support', async ({ page }) => {
    const main = page.locator('main');
    const classes = await main.getAttribute('class');
    
    // Should have dark mode classes
    expect(classes).toContain('dark:');
  });

  test('form labels should be associated with inputs', async ({ page }) => {
    const entityTypeLabel = page.locator('label[for="entityType"]');
    await expect(entityTypeLabel).toBeVisible();
    
    const genderLabel = page.locator('label[for="gender"]');
    await expect(genderLabel).toBeVisible();
    
    const meaningLabel = page.locator('label[for="meaning"]');
    await expect(meaningLabel).toBeVisible();
  });

  test('submit button should have proper styling', async ({ page }) => {
    const submitButton = page.getByRole('button', { name: /Generate Names/i });
    
    const classes = await submitButton.getAttribute('class');
    expect(classes).toContain('bg-blue-600');
  });

  test('page should have proper meta tags', async ({ page }) => {
    const description = await page.locator('meta[name="description"]').getAttribute('content');
    expect(description).toContain('name');
  });
});

test.describe('Name Generator Page - With Mock Backend', () => {
  test('should handle form submission', async ({ page }) => {
    // Mock the API endpoint
    await page.route('**/api/v1/names/entity-types', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(['baby', 'pet', 'vehicle']),
      });
    });

    await page.route('**/api/v1/names/origins', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(['Arabic', 'English', 'Latin']),
      });
    });

    await page.route('**/api/v1/names/themes', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(['classic', 'modern', 'playful']),
      });
    });

    await page.route('**/api/v1/names/suggest', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          request: { entity_type: 'baby' },
          suggestions: [
            {
              id: 1,
              name: 'Muhammad',
              entity_type: 'baby',
              gender: 'male',
              meaning: 'Praised one',
              origin: 'Arabic',
              relevance_score: 0.95,
            },
          ],
          total: 1,
        }),
      });
    });

    await page.goto('/name-generator');

    // Wait for initial data to load
    await page.waitForTimeout(500);

    // Select entity type
    await page.locator('select#entityType').selectOption('baby');

    // Submit form
    await page.getByRole('button', { name: /Generate Names/i }).click();

    // Wait for results
    await page.waitForTimeout(500);

    // Check for results
    const resultName = page.getByText('Muhammad');
    await expect(resultName).toBeVisible();
  });

  test('should display error message on API failure', async ({ page }) => {
    await page.route('**/api/v1/names/entity-types', async route => {
      await route.fulfill({ status: 200, body: JSON.stringify([]) });
    });

    await page.route('**/api/v1/names/origins', async route => {
      await route.fulfill({ status: 200, body: JSON.stringify([]) });
    });

    await page.route('**/api/v1/names/themes', async route => {
      await route.fulfill({ status: 200, body: JSON.stringify([]) });
    });

    await page.route('**/api/v1/names/suggest', async route => {
      await route.fulfill({ status: 500 });
    });

    await page.goto('/name-generator');
    await page.waitForTimeout(500);

    // Try to submit with any entity type
    const entityTypeSelect = page.locator('select#entityType');
    await entityTypeSelect.selectOption({ index: 1 }); // Select first non-empty option if available

    await page.getByRole('button', { name: /Generate Names/i }).click();

    // Wait for error
    await page.waitForTimeout(500);

    // Check for error message (should appear somewhere)
    const errorMessage = page.getByText(/Failed to get name suggestions/i);
    await expect(errorMessage).toBeVisible();
  });
});
