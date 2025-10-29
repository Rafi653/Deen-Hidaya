#!/bin/bash
# Test script for database migrations and seeding

set -e  # Exit on error

echo "==================================="
echo "Database Migration Test Script"
echo "==================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if postgres is running
if ! docker compose ps | grep -q "deen-hidaya-postgres.*Up"; then
    echo "Starting PostgreSQL container..."
    docker compose up -d postgres
    echo "Waiting for PostgreSQL to be ready..."
    sleep 10
fi

# Verify postgres is healthy
if ! docker compose ps | grep -q "deen-hidaya-postgres.*(healthy)"; then
    echo -e "${RED}Error: PostgreSQL is not healthy${NC}"
    exit 1
fi

echo -e "${GREEN}✓ PostgreSQL is running${NC}"

# Run migrations
echo ""
echo "Running Alembic migrations..."
cd backend
export POSTGRES_HOST=localhost
alembic upgrade head

echo -e "${GREEN}✓ Migrations applied successfully${NC}"

# Check tables
echo ""
echo "Verifying tables were created..."
TABLE_COUNT=$(docker compose exec postgres psql -U deen_user -d deen_hidaya -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name != 'alembic_version';")

if [ "$TABLE_COUNT" -eq 9 ]; then
    echo -e "${GREEN}✓ All 9 tables created successfully${NC}"
else
    echo -e "${RED}Error: Expected 9 tables, found $TABLE_COUNT${NC}"
    exit 1
fi

# Run seed script
echo ""
echo "Running seed script..."
python3 seed_surahs.py

echo -e "${GREEN}✓ Seed script executed successfully${NC}"

# Verify data
echo ""
echo "Verifying seeded data..."
SURAH_COUNT=$(docker compose exec postgres psql -U deen_user -d deen_hidaya -t -c "SELECT COUNT(*) FROM surah;")

if [ "$SURAH_COUNT" -eq 114 ]; then
    echo -e "${GREEN}✓ All 114 surahs seeded successfully${NC}"
else
    echo -e "${RED}Error: Expected 114 surahs, found $SURAH_COUNT${NC}"
    exit 1
fi

# Display sample data
echo ""
echo "Sample data from surah table:"
docker compose exec postgres psql -U deen_user -d deen_hidaya -c "SELECT number, name_english, name_arabic, total_verses FROM surah WHERE number IN (1, 2, 112, 113, 114) ORDER BY number;"

# Test downgrade
echo ""
echo "Testing migration downgrade..."
alembic downgrade -1

TABLE_COUNT_AFTER_DOWNGRADE=$(docker compose exec postgres psql -U deen_user -d deen_hidaya -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name != 'alembic_version';")

if [ "$TABLE_COUNT_AFTER_DOWNGRADE" -eq 0 ]; then
    echo -e "${GREEN}✓ Downgrade successful - all tables dropped${NC}"
else
    echo -e "${RED}Error: Expected 0 tables after downgrade, found $TABLE_COUNT_AFTER_DOWNGRADE${NC}"
    exit 1
fi

# Test upgrade again
echo ""
echo "Testing migration upgrade..."
alembic upgrade head

TABLE_COUNT_AFTER_UPGRADE=$(docker compose exec postgres psql -U deen_user -d deen_hidaya -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name != 'alembic_version';")

if [ "$TABLE_COUNT_AFTER_UPGRADE" -eq 9 ]; then
    echo -e "${GREEN}✓ Upgrade successful - all tables recreated${NC}"
else
    echo -e "${RED}Error: Expected 9 tables after upgrade, found $TABLE_COUNT_AFTER_UPGRADE${NC}"
    exit 1
fi

# Re-seed
echo ""
echo "Re-seeding database..."
python3 seed_surahs.py

echo ""
echo "==================================="
echo -e "${GREEN}All tests passed successfully!${NC}"
echo "==================================="

cd ..
