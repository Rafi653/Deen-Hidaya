# Solution: psycopg2 Import Error

## Problem
When trying to run `pytest test_api.py`, you encountered an error:
```
ImportError: dlopen(...) symbol not found in flat namespace '_PQbackendPID'
```

This error occurs because:
1. Your conda Python environment has a broken `psycopg2` installation (common issue on macOS)
2. The `database.py` module tries to create a PostgreSQL connection at import time
3. Tests don't actually need PostgreSQL - they should use a test database

## Solution

### Quick Fix: Use the Test Runner

I've created a test runner script that handles everything for you:

```bash
cd backend
pip install -r requirements-dev.txt
./run_tests.sh
```

This script:
- Sets `TESTING=true` to use SQLite instead of PostgreSQL
- Cleans up Python cache and old test databases
- Runs pytest with proper configuration

### Manual Testing

If you prefer to run tests manually:

```bash
TESTING=true pytest test_api.py -v
```

The `TESTING=true` environment variable tells the application to use SQLite for testing, which doesn't require psycopg2.

### Fixing psycopg2 (For Production Use)

If you need to fix psycopg2 for running the actual application (not just tests), try these solutions:

**Option 1: Use psycopg2-binary (Recommended for development)**
```bash
pip uninstall psycopg2 psycopg2-binary
pip install psycopg2-binary==2.9.9
```

**Option 2: Reinstall PostgreSQL client libraries**
```bash
brew reinstall postgresql
pip uninstall psycopg2 psycopg2-binary
pip install psycopg2-binary==2.9.9
```

**Option 3: Use a virtual environment instead of conda**
```bash
# Create a fresh virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## What Changed

1. **database.py**: Modified to use SQLite when `TESTING=true` is set
2. **test_api.py**: Created comprehensive API tests (19 tests)
3. **conftest.py**: Added pytest fixtures for test database setup
4. **pytest.ini**: Added pytest configuration
5. **requirements-dev.txt**: Added testing dependencies
6. **run_tests.sh**: Created convenient test runner script
7. **README.md**: Added testing documentation and troubleshooting guide

## Running Tests

All of these commands work now:

```bash
# Using the test runner (easiest)
./run_tests.sh

# Run specific tests
./run_tests.sh test_api.py::test_health_check -v

# Run with coverage
./run_tests.sh --cov=. --cov-report=html

# Manual execution
TESTING=true pytest test_api.py -v
```

## Key Points

- **Always use `TESTING=true`** when running tests to avoid psycopg2 issues
- Tests use SQLite in `/tmp`, not PostgreSQL
- The test database is automatically created and cleaned up
- No need to have PostgreSQL running for tests
- The broken psycopg2 in your conda environment won't affect testing

## Verification

Try running:
```bash
cd backend
./run_tests.sh test_api.py::test_root_endpoint -v
```

You should see:
```
test_api.py::test_root_endpoint PASSED
```

If this works, your test infrastructure is set up correctly!
