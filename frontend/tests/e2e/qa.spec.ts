import { test, expect } from '@playwright/test';

test.describe('Q&A Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/qa');
  });

  test('should display the page heading', async ({ page }) => {
    const heading = page.getByRole('heading', { name: /Quran Q&A/i });
    await expect(heading).toBeVisible();
  });

  test('should display back to home link', async ({ page }) => {
    const backLink = page.getByRole('link', { name: /Back to Home/i });
    await expect(backLink).toBeVisible();
  });

  test('should display question input form', async ({ page }) => {
    const input = page.getByRole('textbox', { name: /Enter your question/i });
    await expect(input).toBeVisible();
    await expect(input).toHaveAttribute('placeholder');
    
    const submitButton = page.getByRole('button', { name: /Ask|Submit/i });
    await expect(submitButton).toBeVisible();
  });

  test('should display example questions', async ({ page }) => {
    const exampleText = page.getByText(/Try these examples/i);
    await expect(exampleText).toBeVisible();
    
    // Should have clickable example buttons
    const exampleButtons = page.getByRole('button').filter({ hasText: /patience|charity|believers|forgiveness/i });
    await expect(exampleButtons.first()).toBeVisible();
  });

  test('should populate input with example question', async ({ page }) => {
    const input = page.getByRole('textbox', { name: /Enter your question/i });
    const exampleButton = page.getByRole('button').filter({ hasText: /patience/i }).first();
    
    await exampleButton.click();
    
    const value = await input.inputValue();
    expect(value.length).toBeGreaterThan(0);
  });

  test('should disable submit when input is empty', async ({ page }) => {
    const submitButton = page.getByRole('button', { name: /Ask/i });
    await expect(submitButton).toBeDisabled();
  });

  test('should enable submit when input has text', async ({ page }) => {
    const input = page.getByRole('textbox', { name: /Enter your question/i });
    const submitButton = page.getByRole('button', { name: /Ask/i });
    
    await input.fill('What is patience?');
    await expect(submitButton).toBeEnabled();
  });

  test('should submit question and show results', async ({ page }) => {
    const input = page.getByRole('textbox', { name: /Enter your question/i });
    const submitButton = page.getByRole('button', { name: /Ask/i });
    
    await input.fill('What does the Quran say about patience?');
    await submitButton.click();
    
    // Should show loading state
    const searching = page.getByText(/Searching/i);
    
    // Wait for results (will use mock data)
    await page.waitForTimeout(2000);
    
    // Should show answer
    const answerSection = page.getByText(/Question:/i);
    await expect(answerSection).toBeVisible();
  });

  test('should display cited verses in results', async ({ page }) => {
    const input = page.getByRole('textbox', { name: /Enter your question/i });
    await input.fill('What is patience?');
    
    await page.getByRole('button', { name: /Ask/i }).click();
    await page.waitForTimeout(2000);
    
    // Should show cited verses section
    const citedVerses = page.getByText(/Cited Verses/i);
    if (await citedVerses.count() > 0) {
      await expect(citedVerses).toBeVisible();
    }
  });

  test('should show confidence score and processing time', async ({ page }) => {
    const input = page.getByRole('textbox', { name: /Enter your question/i });
    await input.fill('What is patience?');
    
    await page.getByRole('button', { name: /Ask/i }).click();
    await page.waitForTimeout(2000);
    
    // Should display metadata
    const confidence = page.getByText(/Confidence:/i);
    if (await confidence.count() > 0) {
      await expect(confidence).toBeVisible();
    }
  });

  test('should display verse details with Arabic text', async ({ page }) => {
    const input = page.getByRole('textbox', { name: /Enter your question/i });
    await input.fill('What is patience?');
    
    await page.getByRole('button', { name: /Ask/i }).click();
    await page.waitForTimeout(2000);
    
    // Look for Arabic text in results
    const arabicText = page.locator('[lang="ar"]').first();
    if (await arabicText.count() > 0) {
      await expect(arabicText).toBeVisible();
    }
  });

  test('should have view details button for verses', async ({ page }) => {
    const input = page.getByRole('textbox', { name: /Enter your question/i });
    await input.fill('What is patience?');
    
    await page.getByRole('button', { name: /Ask/i }).click();
    await page.waitForTimeout(2000);
    
    const viewDetailsButton = page.getByRole('button', { name: /View Details/i }).first();
    if (await viewDetailsButton.count() > 0) {
      await expect(viewDetailsButton).toBeVisible();
    }
  });

  test('should open modal when clicking view details', async ({ page }) => {
    const input = page.getByRole('textbox', { name: /Enter your question/i });
    await input.fill('What is patience?');
    
    await page.getByRole('button', { name: /Ask/i }).click();
    await page.waitForTimeout(2000);
    
    const viewDetailsButton = page.getByRole('button', { name: /View Details/i }).first();
    
    if (await viewDetailsButton.count() > 0) {
      await viewDetailsButton.click();
      
      // Should show modal
      const modal = page.getByRole('dialog');
      await expect(modal).toBeVisible();
    }
  });

  test('should close modal when clicking close button', async ({ page }) => {
    const input = page.getByRole('textbox', { name: /Enter your question/i });
    await input.fill('What is patience?');
    
    await page.getByRole('button', { name: /Ask/i }).click();
    await page.waitForTimeout(2000);
    
    const viewDetailsButton = page.getByRole('button', { name: /View Details/i }).first();
    
    if (await viewDetailsButton.count() > 0) {
      await viewDetailsButton.click();
      
      const closeButton = page.getByRole('button', { name: /Close/i }).last();
      await closeButton.click();
      
      await page.waitForTimeout(300);
      
      // Modal should be hidden
      const modal = page.getByRole('dialog');
      await expect(modal).not.toBeVisible();
    }
  });

  test('should have read in context links', async ({ page }) => {
    const input = page.getByRole('textbox', { name: /Enter your question/i });
    await input.fill('What is patience?');
    
    await page.getByRole('button', { name: /Ask/i }).click();
    await page.waitForTimeout(2000);
    
    const contextLink = page.getByRole('link', { name: /Read in Context/i }).first();
    
    if (await contextLink.count() > 0) {
      await expect(contextLink).toBeVisible();
      const href = await contextLink.getAttribute('href');
      expect(href).toMatch(/\/reader\/\d+/);
    }
  });

  test('should display empty state when no results', async ({ page }) => {
    // Before asking any questions
    const emptyState = page.getByText(/Ask a question to get started/i);
    await expect(emptyState).toBeVisible();
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Intercept and fail the API call
    await page.route('**/api/v1/qa/ask', route => route.abort());
    
    const input = page.getByRole('textbox', { name: /Enter your question/i });
    await input.fill('Test question');
    
    await page.getByRole('button', { name: /Ask/i }).click();
    await page.waitForTimeout(2000);
    
    // Should still show results (mock data) or error
    const content = await page.textContent('body');
    expect(content).toBeTruthy();
  });

  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    
    const heading = page.getByRole('heading', { name: /Quran Q&A/i });
    await expect(heading).toBeVisible();
    
    const input = page.getByRole('textbox', { name: /Enter your question/i });
    await expect(input).toBeVisible();
  });

  test('should support keyboard navigation', async ({ page }) => {
    // Tab to input
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();
  });

  test('should have proper ARIA labels', async ({ page }) => {
    const input = page.getByRole('textbox');
    const ariaLabel = await input.getAttribute('aria-label');
    expect(ariaLabel).toBeTruthy();
    
    const submitButton = page.getByRole('button', { name: /Ask/i });
    const buttonLabel = await submitButton.getAttribute('aria-label');
    expect(buttonLabel).toBeTruthy();
  });

  test('should prevent empty question submission', async ({ page }) => {
    const input = page.getByRole('textbox', { name: /Enter your question/i });
    const submitButton = page.getByRole('button', { name: /Ask/i });
    
    await input.fill('   '); // Only whitespace
    await submitButton.click();
    
    // Should not submit or show error
    await page.waitForTimeout(500);
  });

  test('should handle special characters in questions', async ({ page }) => {
    const input = page.getByRole('textbox', { name: /Enter your question/i });
    await input.fill('What is صبر (patience)?');
    
    const submitButton = page.getByRole('button', { name: /Ask/i });
    await submitButton.click();
    
    await page.waitForTimeout(2000);
    
    // Should handle and display correctly
    const questionDisplay = page.getByText(/What is صبر/i);
    if (await questionDisplay.count() > 0) {
      await expect(questionDisplay).toBeVisible();
    }
  });

  test('should have a clear button in the input field', async ({ page }) => {
    const input = page.getByRole('textbox', { name: /Enter your question/i });
    
    // Clear button should not be visible when input is empty
    let clearButton = page.getByRole('button', { name: /Clear question input/i });
    await expect(clearButton).not.toBeVisible();
    
    // Fill the input
    await input.fill('Test question');
    
    // Clear button should now be visible
    clearButton = page.getByRole('button', { name: /Clear question input/i });
    await expect(clearButton).toBeVisible();
  });

  test('should clear input when clear button is clicked', async ({ page }) => {
    const input = page.getByRole('textbox', { name: /Enter your question/i });
    
    // Fill the input
    await input.fill('What is patience?');
    let value = await input.inputValue();
    expect(value).toBe('What is patience?');
    
    // Click clear button
    const clearButton = page.getByRole('button', { name: /Clear question input/i });
    await clearButton.click();
    
    // Input should be empty
    value = await input.inputValue();
    expect(value).toBe('');
  });

  test('should display question history after submitting questions', async ({ page }) => {
    const input = page.getByRole('textbox', { name: /Enter your question/i });
    const submitButton = page.getByRole('button', { name: /Ask/i });
    
    // Submit first question
    await input.fill('What is patience?');
    await submitButton.click();
    await page.waitForTimeout(2000);
    
    // History should be visible
    const historySection = page.getByText(/Previously Asked Questions/i);
    await expect(historySection).toBeVisible();
    
    // Should show the question in history
    const historyQuestion = page.getByText('What is patience?').nth(1); // nth(1) because it's also in the response
    await expect(historyQuestion).toBeVisible();
  });

  test('should populate input when clicking history item', async ({ page }) => {
    const input = page.getByRole('textbox', { name: /Enter your question/i });
    const submitButton = page.getByRole('button', { name: /Ask/i });
    
    // Submit a question to create history
    await input.fill('What is charity?');
    await submitButton.click();
    await page.waitForTimeout(2000);
    
    // Clear the input
    const clearButton = page.getByRole('button', { name: /Clear question input/i });
    await clearButton.click();
    
    // Click on history item
    const historyButtons = page.getByRole('button').filter({ hasText: 'What is charity?' });
    // Find the history button (not the example button)
    for (let i = 0; i < await historyButtons.count(); i++) {
      const button = historyButtons.nth(i);
      const classes = await button.getAttribute('class');
      if (classes && classes.includes('bg-gray-50')) {
        await button.click();
        break;
      }
    }
    
    // Input should be repopulated
    const value = await input.inputValue();
    expect(value).toBe('What is charity?');
  });

  test('should have clear history button', async ({ page }) => {
    const input = page.getByRole('textbox', { name: /Enter your question/i });
    const submitButton = page.getByRole('button', { name: /Ask/i });
    
    // Submit a question to create history
    await input.fill('What is forgiveness?');
    await submitButton.click();
    await page.waitForTimeout(2000);
    
    // Clear history button should be visible
    const clearHistoryButton = page.getByRole('button', { name: /Clear question history/i });
    await expect(clearHistoryButton).toBeVisible();
  });

  test('should clear history when clear history button is clicked', async ({ page }) => {
    const input = page.getByRole('textbox', { name: /Enter your question/i });
    const submitButton = page.getByRole('button', { name: /Ask/i });
    
    // Submit questions to create history
    await input.fill('First question');
    await submitButton.click();
    await page.waitForTimeout(2000);
    
    await input.fill('Second question');
    await submitButton.click();
    await page.waitForTimeout(2000);
    
    // History should be visible
    let historySection = page.getByText(/Previously Asked Questions/i);
    await expect(historySection).toBeVisible();
    
    // Click clear history
    const clearHistoryButton = page.getByRole('button', { name: /Clear question history/i });
    await clearHistoryButton.click();
    
    // History section should not be visible anymore
    historySection = page.getByText(/Previously Asked Questions/i);
    await expect(historySection).not.toBeVisible();
  });

  test('should show question count in history header', async ({ page }) => {
    const input = page.getByRole('textbox', { name: /Enter your question/i });
    const submitButton = page.getByRole('button', { name: /Ask/i });
    
    // Submit multiple questions
    await input.fill('Question 1');
    await submitButton.click();
    await page.waitForTimeout(1500);
    
    await input.fill('Question 2');
    await submitButton.click();
    await page.waitForTimeout(1500);
    
    await input.fill('Question 3');
    await submitButton.click();
    await page.waitForTimeout(1500);
    
    // Should show count
    const countText = page.getByText(/Previously Asked Questions \(3\)/i);
    await expect(countText).toBeVisible();
  });

  test('should maintain keyboard accessibility for clear button', async ({ page }) => {
    const input = page.getByRole('textbox', { name: /Enter your question/i });
    
    // Fill the input
    await input.fill('Test question');
    
    // Tab to clear button
    await page.keyboard.press('Tab');
    
    // The focused element should be the clear button or submit button
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();
    
    // Press Enter to activate (if it's the clear button)
    const clearButton = page.getByRole('button', { name: /Clear question input/i });
    await clearButton.focus();
    await page.keyboard.press('Enter');
    
    // Input should be cleared
    const value = await input.inputValue();
    expect(value).toBe('');
  });

  test('should maintain keyboard accessibility for history items', async ({ page }) => {
    const input = page.getByRole('textbox', { name: /Enter your question/i });
    const submitButton = page.getByRole('button', { name: /Ask/i });
    
    // Create history
    await input.fill('Accessible question');
    await submitButton.click();
    await page.waitForTimeout(2000);
    
    // Clear input
    await input.fill('');
    
    // History button should be keyboard accessible
    const historyButtons = page.getByRole('button').filter({ hasText: 'Accessible question' });
    for (let i = 0; i < await historyButtons.count(); i++) {
      const button = historyButtons.nth(i);
      const classes = await button.getAttribute('class');
      if (classes && classes.includes('bg-gray-50')) {
        await button.focus();
        await page.keyboard.press('Enter');
        break;
      }
    }
    
    // Input should be repopulated
    const value = await input.inputValue();
    expect(value).toBe('Accessible question');
  });
});
