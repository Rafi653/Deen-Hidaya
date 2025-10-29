#!/bin/bash
# Test runner script for Deen Hidaya backend
# This script sets up the test environment and runs pytest with the correct configuration

# Set testing mode to use SQLite instead of PostgreSQL
export TESTING=true

# Clean up any previous test database
rm -f /tmp/test_deen_hidaya.db

# Clear Python cache to avoid import issues
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

# Run pytest with all arguments passed to this script
python -m pytest "$@"
