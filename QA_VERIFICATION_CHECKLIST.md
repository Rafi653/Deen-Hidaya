# QA Testing Verification Checklist

Use this checklist to verify the QA testing work completed for the Deen Hidaya frontend.

## Pre-requisites

- [ ] Node.js v18+ installed
- [ ] npm installed
- [ ] Git repository cloned

## Installation Verification

```bash
cd frontend
npm install
```

- [ ] Installation completes without errors
- [ ] All dependencies installed (check package.json)
- [ ] Test dependencies present:
  - [ ] vitest
  - [ ] @playwright/test
  - [ ] @testing-library/react
  - [ ] @axe-core/playwright

## Unit Tests Verification

### Run Unit Tests
```bash
npm test -- --run
```

**Expected Results:**
- [ ] All 46 tests pass
- [ ] 3 test files execute
- [ ] No errors or failures
- [ ] Output shows:
  - [ ] `tests/unit/bookmarks.test.ts (14 tests)` - PASS
  - [ ] `tests/unit/audioPlayer.test.ts (17 tests)` - PASS
  - [ ] `tests/unit/api.test.ts (15 tests)` - PASS

### Generate Coverage Report
```bash
npm run test:coverage
```

**Expected Results:**
- [ ] Coverage report generated
- [ ] ~90% coverage for lib/ directory
- [ ] HTML report created in coverage/ directory
- [ ] Can open coverage/index.html in browser

## Linter Verification

```bash
npm run lint
```

**Expected Results:**
- [ ] Linter completes successfully
- [ ] Exit code 0 (success)
- [ ] Only 3 minor warnings about custom fonts
- [ ] No errors

## E2E Test Setup Verification

### Install Playwright Browsers
```bash
npm run playwright:install
```

**Expected Results:**
- [ ] Browsers download successfully
- [ ] Chromium, Firefox, WebKit installed
- [ ] No errors during installation

### Verify E2E Test Files Exist
- [ ] `tests/e2e/home.spec.ts` exists
- [ ] `tests/e2e/reader.spec.ts` exists
- [ ] `tests/e2e/surah-detail.spec.ts` exists
- [ ] `tests/e2e/qa.spec.ts` exists
- [ ] `tests/e2e/accessibility.spec.ts` exists

## E2E Tests Execution (Optional - Requires Running Server)

### Start Dev Server
In Terminal 1:
```bash
npm run dev
```

**Expected Results:**
- [ ] Server starts on http://localhost:3000
- [ ] No errors in console
- [ ] "Ready on http://localhost:3000" displayed

### Run E2E Tests
In Terminal 2:
```bash
npm run test:e2e
```

**Expected Results:**
- [ ] Tests execute across multiple browsers
- [ ] All home page tests pass (10 tests)
- [ ] All reader tests pass (16 tests)
- [ ] All surah detail tests pass (21 tests)
- [ ] All Q&A tests pass (24 tests)
- [ ] All accessibility tests pass (20+ tests)
- [ ] Report generated

### View Test Report
```bash
npx playwright show-report
```

**Expected Results:**
- [ ] HTML report opens in browser
- [ ] All tests marked as passed
- [ ] Screenshots available (if any failures)
- [ ] Trace files available for debugging

## Configuration Files Verification

### Check Config Files Exist
- [ ] `vitest.config.ts` exists
- [ ] `playwright.config.ts` exists
- [ ] `tests/setup.ts` exists

### Verify Test Scripts in package.json
- [ ] `test` script exists
- [ ] `test:coverage` script exists
- [ ] `test:e2e` script exists
- [ ] `test:e2e:ui` script exists
- [ ] `playwright:install` script exists

## Documentation Verification

### Check Documentation Files Exist
- [ ] `tests/README.md` exists (comprehensive guide)
- [ ] `TEST_REPORT.md` exists (detailed results)
- [ ] `TESTING_QUICKSTART.md` exists (quick start)
- [ ] Root: `QA_SUMMARY.md` exists (executive summary)
- [ ] Root: `SECURITY_SUMMARY.md` exists (security analysis)

### Verify Documentation Quality
- [ ] tests/README.md has table of contents
- [ ] tests/README.md explains how to run tests
- [ ] TEST_REPORT.md shows test results
- [ ] TESTING_QUICKSTART.md is easy to follow
- [ ] All code examples are properly formatted

## Test Coverage Verification

### Issue #8: Quran Reader UI
- [ ] Surah list tests exist
- [ ] Surah detail tests exist
- [ ] Search functionality tested
- [ ] Arabic text rendering tested
- [ ] Transliteration toggle tested
- [ ] Translation switching tested
- [ ] Bookmark functionality tested
- [ ] Navigation tested
- [ ] Responsive design tested
- [ ] Accessibility tested

### Issue #9: Q&A Feature
- [ ] Question input tests exist
- [ ] Submission tests exist
- [ ] Answer display tests exist
- [ ] Citation tests exist
- [ ] Modal dialog tests exist
- [ ] Navigation tests exist
- [ ] Error handling tested
- [ ] Loading states tested

### Issue #10: Audio Player UI
- [ ] Audio player initialization tested
- [ ] State management tested
- [ ] Play/pause controls tested
- [ ] Error handling tested
- [ ] UI feedback tested

## Accessibility Verification

### Check Accessibility Tests
- [ ] Accessibility test file exists
- [ ] axe-core integration verified
- [ ] Keyboard navigation tests exist
- [ ] ARIA label tests exist
- [ ] Color contrast tests exist
- [ ] Screen reader tests exist
- [ ] Focus management tests exist

### Manual Accessibility Check
- [ ] Tab through pages works
- [ ] Focus indicators visible
- [ ] ARIA labels present
- [ ] Heading hierarchy correct
- [ ] Alt text on images

## Security Verification

### Check Security Files
- [ ] SECURITY_SUMMARY.md exists
- [ ] CodeQL scan results documented
- [ ] Zero vulnerabilities reported
- [ ] Security best practices documented

### Manual Security Check
- [ ] No hardcoded secrets in code
- [ ] Input validation present
- [ ] Error messages don't expose sensitive info
- [ ] localStorage used safely

## Code Quality Verification

### Check Test Quality
- [ ] Tests are well-organized
- [ ] Test names are descriptive
- [ ] Tests are independent
- [ ] Proper use of before/after hooks
- [ ] Good assertions
- [ ] Edge cases covered

### Check Code Quality
- [ ] TypeScript types used correctly
- [ ] No console errors in tests
- [ ] Proper error handling
- [ ] Mock data is representative
- [ ] Tests are maintainable

## Browser Compatibility Verification

### Check Playwright Config
- [ ] Chromium project configured
- [ ] Firefox project configured
- [ ] WebKit project configured
- [ ] Mobile Chrome configured
- [ ] Mobile Safari configured

### Run on Multiple Browsers (Optional)
```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

- [ ] Tests pass on Chromium
- [ ] Tests pass on Firefox
- [ ] Tests pass on WebKit

## Final Verification

### Overall Quality
- [ ] All unit tests passing (46/46)
- [ ] All E2E tests implemented (100+)
- [ ] Linter passing
- [ ] Security scan clean
- [ ] Documentation complete
- [ ] Code quality high

### Deliverables Checklist
- [ ] Test infrastructure set up
- [ ] Unit tests implemented and passing
- [ ] E2E tests implemented
- [ ] Accessibility tests implemented
- [ ] Documentation written
- [ ] Security summary created
- [ ] Quick start guide created
- [ ] QA summary created

### Ready for Production?
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Security verified
- [ ] Accessibility compliant
- [ ] Code reviewed
- [ ] No critical issues

## Sign-Off

**Verified By**: _________________  
**Date**: _________________  
**Status**: [ ] APPROVED [ ] NEEDS WORK  

**Comments**:
```
[Add any comments or issues found during verification]
```

## Troubleshooting

### If Unit Tests Fail
1. Check Node.js version (should be 18+)
2. Run `npm install` again
3. Clear node_modules and reinstall
4. Check for errors in test output

### If E2E Tests Fail
1. Ensure dev server is running
2. Check http://localhost:3000 is accessible
3. Verify Playwright browsers are installed
4. Check for port conflicts

### If Linter Fails
1. The warnings about custom fonts are acceptable
2. Any errors should be investigated
3. Run `npm run lint -- --fix` to auto-fix

### Getting Help
- See `TESTING_QUICKSTART.md` for quick start
- See `tests/README.md` for detailed guide
- See `TEST_REPORT.md` for test results
- Open GitHub issue with `role:qa` label

---

**Document Version**: 1.0  
**Last Updated**: 2025-10-29  
**Checklist Items**: 150+
