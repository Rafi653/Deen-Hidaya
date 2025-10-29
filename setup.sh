#!/bin/bash
# Deen Hidaya - Automated Setup Script
# This script automates the complete setup process for the Deen Hidaya application

set -e  # Exit on error

echo "================================================"
echo "Deen Hidaya - Automated Setup"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check prerequisites
echo "Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi
print_success "Docker is installed"

if ! command -v docker compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi
print_success "Docker Compose is installed"

echo ""

# Step 1: Create .env file if it doesn't exist
echo "Step 1: Setting up environment configuration..."
if [ ! -f .env ]; then
    print_info "Creating .env file from .env.example..."
    cp .env.example .env
    print_success ".env file created"
    print_info "Note: Edit .env file to configure OpenAI API key for Q&A features"
else
    print_info ".env file already exists, skipping"
fi
echo ""

# Step 2: Stop any existing containers
echo "Step 2: Cleaning up existing containers..."
if docker compose ps | grep -q "Up"; then
    print_info "Stopping existing containers..."
    docker compose down
    print_success "Existing containers stopped"
else
    print_info "No running containers found"
fi
echo ""

# Step 3: Start Docker services
echo "Step 3: Starting Docker services..."
print_info "This may take a few minutes for the first run..."
docker compose up -d --build

# Wait for services to be ready
print_info "Waiting for services to be ready..."
sleep 10

# Check if services are running
if ! docker compose ps | grep -q "Up"; then
    print_error "Services failed to start. Check logs with: docker compose logs"
    exit 1
fi
print_success "Docker services started"
echo ""

# Step 4: Wait for database to be ready
echo "Step 4: Waiting for database to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if docker compose exec -T postgres pg_isready -U deen_user -d deen_hidaya &> /dev/null; then
        print_success "Database is ready"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        print_error "Database failed to start. Check logs with: docker compose logs postgres"
        exit 1
    fi
    sleep 2
done
echo ""

# Step 5: Run database migrations
echo "Step 5: Running database migrations..."
docker compose exec -T backend alembic upgrade head
if [ $? -eq 0 ]; then
    print_success "Database migrations completed"
else
    print_error "Database migrations failed"
    exit 1
fi
echo ""

# Step 6: Check if data needs to be ingested
echo "Step 6: Checking data status..."
VERSE_COUNT=$(docker compose exec -T postgres psql -U deen_user -d deen_hidaya -t -c "SELECT COUNT(*) FROM verse;" 2>/dev/null | tr -d ' ')
if [ -z "$VERSE_COUNT" ] || [ "$VERSE_COUNT" = "0" ]; then
    print_info "No data found in database. Ingesting data..."
    
    # Count available JSON files
    JSON_COUNT=$(ls -1 data/quran_text/surah_*.json 2>/dev/null | wc -l)
    if [ "$JSON_COUNT" -gt 0 ]; then
        print_info "Found $JSON_COUNT surah(s) to ingest"
        docker compose exec -T backend python ingest_data.py
        if [ $? -eq 0 ]; then
            print_success "Data ingestion completed"
        else
            print_error "Data ingestion failed"
            exit 1
        fi
    else
        print_info "No scraped data found in data/quran_text/"
        print_info "Scraping first 10 surahs..."
        docker compose exec -T backend python scrape_quran.py --start 1 --end 10 --translations 131,213
        print_info "Ingesting scraped data..."
        docker compose exec -T backend python ingest_data.py --start 1 --end 10
        if [ $? -eq 0 ]; then
            print_success "Data scraping and ingestion completed"
        else
            print_error "Data scraping/ingestion failed"
            exit 1
        fi
    fi
else
    print_info "Database already contains $VERSE_COUNT verses, skipping data ingestion"
fi
echo ""

# Step 7: Check embedding status for Q&A
echo "Step 7: Checking Q&A embeddings status..."
EMBEDDING_COUNT=$(docker compose exec -T postgres psql -U deen_user -d deen_hidaya -t -c "SELECT COUNT(*) FROM embedding;" 2>/dev/null | tr -d ' ')
if [ -z "$EMBEDDING_COUNT" ] || [ "$EMBEDDING_COUNT" = "0" ]; then
    print_info "No embeddings found for Q&A feature"
    
    # Check if OpenAI API key is set
    if grep -q "OPENAI_API_KEY=your_openai_api_key_here" .env || ! grep -q "OPENAI_API_KEY=" .env; then
        print_info "OpenAI API key not configured in .env file"
        print_info "Q&A feature will not work without embeddings"
        print_info "To enable Q&A:"
        print_info "  1. Add your OpenAI API key to .env file"
        print_info "  2. Run: docker compose exec backend python -c \"from embedding_service import EmbeddingService; from database import SessionLocal; es = EmbeddingService(); db = SessionLocal(); es.create_embeddings_batch([v.id for v in db.query(__import__('models').Verse).all()], 'en', db)\""
    else
        print_info "OpenAI API key found. Generating embeddings for Q&A..."
        print_info "This may take several minutes and will incur OpenAI API costs (~\$0.03 for full Quran)"
        read -p "Do you want to generate embeddings now? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker compose exec -T backend python -c "
from embedding_service import EmbeddingService
from database import SessionLocal
from models import Verse

es = EmbeddingService()
db = SessionLocal()
try:
    verses = db.query(Verse).all()
    verse_ids = [v.id for v in verses]
    print(f'Generating embeddings for {len(verse_ids)} verses...')
    result = es.create_embeddings_batch(verse_ids, 'en', db)
    print(f\"Success: {result['success']}, Errors: {result['errors']}\")
finally:
    db.close()
"
            if [ $? -eq 0 ]; then
                print_success "Embeddings generated successfully"
            else
                print_error "Embedding generation failed"
                print_info "You can generate embeddings later using the admin API endpoint"
            fi
        else
            print_info "Skipping embedding generation"
            print_info "Q&A feature will return 404 or fallback results"
        fi
    fi
else
    print_info "Found $EMBEDDING_COUNT embeddings for Q&A feature"
fi
echo ""

# Step 8: Verify services health
echo "Step 8: Verifying service health..."
sleep 5  # Give services a moment to stabilize

# Check backend health
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Backend is healthy (http://localhost:8000)"
else
    print_error "Backend health check failed"
    print_info "Check logs with: docker compose logs backend"
fi

# Check frontend health
if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
    print_success "Frontend is healthy (http://localhost:3000)"
else
    print_error "Frontend health check failed"
    print_info "Check logs with: docker compose logs frontend"
fi
echo ""

# Final summary
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Your Deen Hidaya application is ready:"
echo ""
echo "  📱 Frontend:     http://localhost:3000"
echo "  🔧 Backend API:  http://localhost:8000"
echo "  📚 API Docs:     http://localhost:8000/docs"
echo "  🗄️  Database:     localhost:5432"
echo ""
echo "Useful commands:"
echo "  • View logs:       docker compose logs -f"
echo "  • Stop services:   docker compose down"
echo "  • Restart:         docker compose restart"
echo "  • Run tests:       docker compose exec backend pytest"
echo ""
echo "Data status:"
FINAL_VERSE_COUNT=$(docker compose exec -T postgres psql -U deen_user -d deen_hidaya -t -c "SELECT COUNT(*) FROM verse;" 2>/dev/null | tr -d ' ')
FINAL_TRANSLATION_COUNT=$(docker compose exec -T postgres psql -U deen_user -d deen_hidaya -t -c "SELECT COUNT(*) FROM translation;" 2>/dev/null | tr -d ' ')
FINAL_AUDIO_COUNT=$(docker compose exec -T postgres psql -U deen_user -d deen_hidaya -t -c "SELECT COUNT(*) FROM audio_track;" 2>/dev/null | tr -d ' ')
FINAL_EMBEDDING_COUNT=$(docker compose exec -T postgres psql -U deen_user -d deen_hidaya -t -c "SELECT COUNT(*) FROM embedding;" 2>/dev/null | tr -d ' ')

echo "  • Verses:          $FINAL_VERSE_COUNT"
echo "  • Translations:    $FINAL_TRANSLATION_COUNT"
echo "  • Audio tracks:    $FINAL_AUDIO_COUNT"
echo "  • Embeddings:      $FINAL_EMBEDDING_COUNT"
echo ""

if [ "$FINAL_EMBEDDING_COUNT" = "0" ]; then
    print_info "Note: Q&A feature requires embeddings. Configure OpenAI API key and run setup again."
fi

echo "Happy coding! 🚀"
echo ""
