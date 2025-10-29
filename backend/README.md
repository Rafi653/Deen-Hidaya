# Deen Hidaya Backend

FastAPI backend service for the Deen Hidaya Islamic knowledge platform.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp ../.env.example ../.env
# Edit .env with your database credentials
```

3. Run database migrations:
```bash
alembic upgrade head
```

4. Seed the database with surah metadata:
```bash
python seed_surahs.py
```

5. Run the development server:
```bash
uvicorn main:app --reload
```

## Database Migrations

This project uses Alembic for database migrations. See [alembic/MIGRATIONS.md](./alembic/MIGRATIONS.md) for detailed documentation.

### Quick Reference

```bash
# Apply migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description"

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check endpoint
- `GET /api/v1/health` - API health check endpoint

### Quran Data
- `GET /api/v1/surahs` - List all surahs with pagination
- `GET /api/v1/surahs/{surah_number}` - Get surah details with all verses
- `GET /api/v1/verses/{verse_id}` - Get specific verse by ID
- `GET /api/v1/surahs/{surah_number}/verses/{verse_number}` - Get verse by Quran reference (e.g., 2:255)
- `GET /api/v1/translations` - List all available translations with license info

### API Features
- **Transliteration**: All verses include romanized Arabic text
- **Multiple Translations**: Support for multiple language translations
- **License Metadata**: All translations include license and source information
- **Pagination**: List endpoints support skip/limit parameters
- **OpenAPI Documentation**: Available at `/docs` when server is running

### Example API Usage
```bash
# Get verse with transliteration and translation
curl http://localhost:8000/api/v1/surahs/2/verses/255

# List available translations
curl http://localhost:8000/api/v1/translations
```

## Database Schema

The backend uses PostgreSQL with the following main tables:
- `surah` - Quran chapters (114 surahs) with transliteration
- `verse` - Quran verses (ayahs) with Arabic text, simple text, and **transliteration**
- `translation` - Verse translations with **license and source metadata**
- `audio_track` - Audio recordings by reciters
- `tag` - Tags for categorizing verses
- `verse_tag` - Verse-tag relationships
- `entity` - Named entities in the Quran
- `embedding` - Vector embeddings for semantic search
- `bookmark` - User bookmarks

### Key Fields Added in Issue #5
- `verse.text_transliteration` - Romanized Arabic text
- `translation.license` - License information for translations
- `translation.source` - Source attribution for translations

## Data Pipeline

### Scraping Quran Data
```bash
# Scrape with multiple translations
python scrape_quran.py --start 1 --end 5 --translations "131,20,140"

# Available translation IDs:
# 131 - Dr. Mustafa Khattab, The Clear Quran (English)
# 20  - Saheeh International (English)
# 140 - Telugu Translation
```

### Ingesting Data
```bash
# Generate sample data for testing
python generate_sample_data.py

# Ingest scraped data (automatically generates transliteration)
python ingest_data.py --start 1 --end 5
```

### Transliteration
Transliteration is automatically generated during data ingestion using the `transliteration_generator.py` module. It converts Arabic text to romanized Latin characters:
- Example: "بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ" → "Bismi llahi lrahmaani lrahiymi"

See [DATA_PIPELINE.md](./DATA_PIPELINE.md) for complete documentation on the data pipeline.

## Docker

Build and run with Docker:
```bash
docker build -t deen-hidaya-backend .
docker run -p 8000:8000 deen-hidaya-backend
```

Or use Docker Compose from the project root:
```bash
docker-compose up backend
```

