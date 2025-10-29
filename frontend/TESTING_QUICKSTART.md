# Quick Start: Running Frontend Tests

This guide shows you how to quickly run all the tests for the Deen Hidaya frontend.

## Prerequisites

Make sure you have Node.js (v18+) and npm installed.

## Installation

```bash
cd frontend
npm install
```

## Running Tests

### 1. Unit Tests (Fastest) ⚡

Unit tests run in seconds and don't require a running server.

```bash
# Run all unit tests
npm test

# Run with coverage report
npm run test:coverage

# Run in watch mode (for development)
npm test -- --watch
```

**Expected Output:**
```
✓ tests/unit/bookmarks.test.ts (14 tests) 18ms
✓ tests/unit/audioPlayer.test.ts (17 tests) 17ms
✓ tests/unit/api.test.ts (15 tests) 28ms

Test Files  3 passed (3)
     Tests  46 passed (46)
```

### 2. End-to-End Tests 🌐

E2E tests require the dev server to be running.

**Step 1: Install Playwright browsers (first time only)**
```bash
npm run playwright:install
```

**Step 2: Start the dev server**
```bash
# In Terminal 1
npm run dev
```

Wait for the server to start (you'll see "Ready on http://localhost:3000")

**Step 3: Run E2E tests**
```bash
# In Terminal 2
npm run test:e2e

# Or run with UI (interactive mode)
npm run test:e2e:ui

# Or run in headed mode (see browser)
npm run test:e2e:headed

# Or debug specific tests
npm run test:e2e:debug
```

**Run specific test files:**
```bash
# Test home page only
npx playwright test tests/e2e/home.spec.ts

# Test reader pages only  
npx playwright test tests/e2e/reader.spec.ts tests/e2e/surah-detail.spec.ts

# Test Q&A only
npx playwright test tests/e2e/qa.spec.ts

# Test accessibility only
npx playwright test tests/e2e/accessibility.spec.ts
```

**Run on specific browsers:**
```bash
# Chromium only (fastest)
npx playwright test --project=chromium

# Firefox only
npx playwright test --project=firefox

# WebKit (Safari) only
npx playwright test --project=webkit

# Mobile devices
npx playwright test --project="Mobile Chrome"
npx playwright test --project="Mobile Safari"
```

### 3. View Test Reports 📊

After running E2E tests, view the HTML report:

```bash
npx playwright show-report
```

This opens an interactive report in your browser with:
- Test results and timings
- Screenshots of failures
- Trace files for debugging
- Browser console logs

## Test Results Summary

### ✅ Unit Tests
- **API Library**: 15 tests covering all API functions
- **Audio Player**: 17 tests covering playback logic
- **Bookmarks**: 14 tests covering localStorage operations
- **Total**: 46 tests, all passing

### ✅ E2E Tests
- **Home Page**: 10 tests
- **Reader List**: 16 tests
- **Surah Detail**: 21 tests
- **Q&A Page**: 24 tests
- **Accessibility**: 20+ tests
- **Total**: 100+ tests covering all user flows

## Troubleshooting

### Port 3000 is already in use

```bash
# Find and kill the process
lsof -ti:3000 | xargs kill -9

# Or use a different port
PORT=3001 npm run dev
```

Then update `playwright.config.ts` to use the new port.

### Playwright browsers not installed

```bash
npm run playwright:install
```

### Tests timeout or fail

1. Make sure dev server is running (`npm run dev`)
2. Check that http://localhost:3000 is accessible
3. Increase timeout in test files if needed

### Mock data vs Real backend

The frontend gracefully falls back to mock data when the backend is unavailable. To test with real backend:

1. Start the backend server (see backend/README.md)
2. Ensure backend is running on http://localhost:8000
3. Run tests as normal

## What's Being Tested?

### Issue #8: Quran Reader UI
- ✅ Surah list display and search
- ✅ Surah detail page with verses
- ✅ Arabic text rendering (RTL)
- ✅ Transliteration toggle
- ✅ Translation switching
- ✅ Bookmark functionality
- ✅ Navigation and routing
- ✅ Responsive design
- ✅ Keyboard accessibility

### Issue #9: Q&A Feature  
- ✅ Question input and submission
- ✅ Answer display with citations
- ✅ Verse modal with details
- ✅ Example questions
- ✅ Navigation to reader
- ✅ Error handling
- ✅ Loading states

### Issue #10: Audio Player UI
- ✅ Play/pause controls
- ✅ Audio player state management
- ✅ Verse-by-verse UI
- ✅ Error handling
- ⏳ Actual playback (pending backend audio URLs)

### Accessibility (WCAG 2.1 AA)
- ✅ Keyboard navigation
- ✅ Screen reader support
- ✅ Color contrast
- ✅ ARIA labels
- ✅ Focus management
- ✅ Semantic HTML

## Continuous Testing

### Watch Mode (Development)

```bash
# Unit tests with auto-reload
npm test -- --watch
```

### Pre-commit Checks

Before committing code, run:

```bash
# Lint check
npm run lint

# Unit tests
npm test -- --run

# Type check (if needed)
npx tsc --noEmit
```

## CI/CD Integration

The tests are ready for CI/CD. Example GitHub Actions workflow:

```yaml
name: Frontend Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run unit tests
        run: |
          cd frontend
          npm run test:coverage
      
      - name: Install Playwright
        run: |
          cd frontend
          npx playwright install --with-deps
      
      - name: Run E2E tests
        run: |
          cd frontend
          npm run dev &
          sleep 10
          npm run test:e2e
```

## Getting Help

- **Test Documentation**: See `tests/README.md` for detailed information
- **Test Report**: See `TEST_REPORT.md` for comprehensive test results
- **Issues**: Open a GitHub issue with the `role:qa` label

## Quick Commands Reference

| Command | Description |
|---------|-------------|
| `npm test` | Run unit tests |
| `npm run test:coverage` | Run unit tests with coverage |
| `npm run test:e2e` | Run E2E tests |
| `npm run test:e2e:ui` | Run E2E tests in UI mode |
| `npm run playwright:install` | Install Playwright browsers |
| `npm run lint` | Run linter |
| `npm run dev` | Start dev server |

---

**Happy Testing! 🎉**

For more details, see the [full testing documentation](tests/README.md).
