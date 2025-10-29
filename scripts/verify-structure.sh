#!/bin/bash
# Verification script for repository structure

echo "================================================"
echo "Deen Hidaya - Repository Structure Verification"
echo "================================================"
echo ""

# Check directories
echo "Checking directory structure..."
directories=("frontend" "backend" "infra" "data")
for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        echo "✓ $dir/ directory exists"
    else
        echo "✗ $dir/ directory missing"
        exit 1
    fi
done
echo ""

# Check key files
echo "Checking key files..."
files=(
    ".gitignore"
    ".env.example"
    "docker-compose.yml"
    "README.md"
    "backend/Dockerfile"
    "backend/main.py"
    "backend/requirements.txt"
    "frontend/Dockerfile"
    "frontend/package.json"
    "frontend/pages/api/health.ts"
    "infra/init-db.sql"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file missing"
        exit 1
    fi
done
echo ""

# Check docker-compose services
echo "Checking Docker Compose services..."
services=$(docker compose config --services 2>/dev/null)
expected_services=("postgres" "backend" "frontend")
for service in "${expected_services[@]}"; do
    if echo "$services" | grep -q "^$service$"; then
        echo "✓ $service service configured"
    else
        echo "✗ $service service missing"
        exit 1
    fi
done
echo ""

# Check health endpoints
echo "Checking health endpoints..."
if grep -q '@app.get("/health")' backend/main.py; then
    echo "✓ Backend health endpoint defined"
else
    echo "✗ Backend health endpoint missing"
    exit 1
fi

if [ -f "frontend/pages/api/health.ts" ]; then
    echo "✓ Frontend health endpoint defined"
else
    echo "✗ Frontend health endpoint missing"
    exit 1
fi
echo ""

# Check PostgreSQL extensions
echo "Checking PostgreSQL extensions configuration..."
if grep -q "pgvector" infra/init-db.sql && grep -q "pg_trgm" infra/init-db.sql; then
    echo "✓ pgvector extension configured"
    echo "✓ pg_trgm extension configured"
else
    echo "✗ PostgreSQL extensions not properly configured"
    exit 1
fi
echo ""

echo "================================================"
echo "All checks passed! ✓"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env: cp .env.example .env"
echo "2. Start services: docker compose up"
echo "3. Check health endpoints:"
echo "   - Frontend: http://localhost:3000/api/health"
echo "   - Backend: http://localhost:8000/health"
echo ""
