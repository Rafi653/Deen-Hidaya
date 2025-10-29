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

### Audio Endpoints (NEW in Issue #6)
- `GET /api/v1/verses/{verse_id}/audio` - Get audio metadata for a verse
- `GET /api/v1/verses/{verse_id}/audio/stream` - Stream audio with range request support

### Bookmark Endpoints (NEW in Issue #6)
- `POST /api/v1/bookmarks` - Create a new bookmark
- `GET /api/v1/bookmarks` - List bookmarks for a user
- `DELETE /api/v1/bookmarks/{bookmark_id}` - Delete a bookmark

### Search Endpoint (ENHANCED in Issue #7)
- `GET /api/v1/search` - Unified search (exact, fuzzy, semantic, hybrid)
  - Query parameters: `q`, `lang`, `search_type`, `limit`
  - Supports exact matching, fuzzy search, and **semantic search with pgvector**
  - **NEW**: Semantic search using OpenAI embeddings and vector similarity
  - **NEW**: Hybrid search combines lexical and semantic results with weighted scoring

### Admin Endpoints (ENHANCED in Issue #7)
**Authentication Required:** Bearer token in Authorization header
- `POST /api/v1/admin/ingest/scrape` - Run data scraping pipeline
- `POST /api/v1/admin/embed/verse` - **Create embeddings for semantic search (IMPLEMENTED)**
  - Generate vector embeddings for verses using OpenAI
  - Supports batch processing and multiple languages
  - See [EMBEDDING_EXAMPLES.md](./EMBEDDING_EXAMPLES.md) for usage examples

### API Features
- **Transliteration**: All verses include romanized Arabic text
- **Multiple Translations**: Support for multiple language translations
- **License Metadata**: All translations include license and source information
- **Pagination**: List endpoints support skip/limit parameters
- **Audio Streaming**: HTTP range request support for efficient audio streaming
- **Search**: Exact, fuzzy, and **semantic search with vector embeddings**
- **Embeddings**: Generate and store vector embeddings for verses (Issue #7)
- **Bookmarks**: User bookmark management
- **Admin Protection**: Admin endpoints secured with token authentication
- **OpenAPI Documentation**: Available at `/docs` when server is running

### API Documentation
Complete API documentation is available at:
- **Interactive Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Markdown Documentation**: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)

### Example API Usage
```bash
# Get verse with transliteration and translation
curl http://localhost:8000/api/v1/surahs/2/verses/255

# List available translations
curl http://localhost:8000/api/v1/translations

# Search for verses about patience
curl "http://localhost:8000/api/v1/search?q=patience&lang=en&search_type=hybrid"

# Create a bookmark
curl -X POST http://localhost:8000/api/v1/bookmarks \
  -H "Content-Type: application/json" \
  -d '{"verse_id": 1, "user_id": "user123", "note": "Important verse"}'

# Stream audio with range support
curl -H "Range: bytes=0-1023" \
  http://localhost:8000/api/v1/verses/1/audio/stream

# Admin: Run scraper (requires admin token)
curl -X POST http://localhost:8000/api/v1/admin/ingest/scrape \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"surah_numbers": [1, 2, 3]}'
```

**Note:** Replace `YOUR_ADMIN_TOKEN` with the actual token configured in your `.env` file under `ADMIN_TOKEN`.

### Semantic Search Examples (NEW in Issue #7)

```bash
# Generate embeddings for all verses
curl -X POST http://localhost:8000/api/v1/admin/embed/verse \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"language": "en"}'

# Semantic search for verses about patience
curl "http://localhost:8000/api/v1/search?q=patience+in+hardship&search_type=semantic&lang=en&limit=10"

# Hybrid search combining lexical and semantic
curl "http://localhost:8000/api/v1/search?q=charity&search_type=hybrid&lang=en&limit=20"
```

**For more examples**, see [EMBEDDING_EXAMPLES.md](./EMBEDDING_EXAMPLES.md)

## Database Schema

The backend uses PostgreSQL with the following main tables:
- `surah` - Quran chapters (114 surahs) with transliteration
- `verse` - Quran verses (ayahs) with Arabic text, simple text, and **transliteration**
- `translation` - Verse translations with **license and source metadata**
- `audio_track` - Audio recordings by reciters
- `tag` - Tags for categorizing verses
- `verse_tag` - Verse-tag relationships
- `entity` - Named entities in the Quran
- `embedding` - **Vector embeddings for semantic search (pgvector type - Issue #7)**
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

## Testing

### Running Tests
```bash
# Run all tests
pytest test_api.py -v

# Run specific test
pytest test_api.py::test_search_exact -v

# Run with coverage
pytest test_api.py --cov=. --cov-report=html
```

### Test Coverage
The test suite covers:
- Health check endpoints
- Surah and verse retrieval
- Translation listing
- Bookmark CRUD operations
- Search functionality (exact, fuzzy, hybrid)
- Admin endpoint authentication
- Error handling and edge cases

All 19 tests pass successfully with SQLite in-memory database.

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

## Embeddings & Semantic Search (Issue #7)

### Setup

1. **Install Dependencies**:
```bash
pip install openai pgvector numpy
```

2. **Configure OpenAI API Key**:
```bash
# Add to .env file
OPENAI_API_KEY=your_openai_api_key_here
EMBEDDING_MODEL=text-embedding-ada-002
EMBEDDING_DIMENSION=1536
```

3. **Run Migrations** (for pgvector support):
```bash
alembic upgrade head
```

### Features

- **Vector Embeddings**: Generate embeddings using OpenAI API
- **pgvector Integration**: Store and search embeddings efficiently with PostgreSQL
- **Semantic Search**: Find verses by meaning, not just keywords
- **Hybrid Search**: Combine lexical and semantic search for best results
- **Batch Processing**: Generate embeddings for thousands of verses efficiently
- **Multi-language Support**: Create embeddings for Arabic and English

### Usage

See [EMBEDDING_EXAMPLES.md](./EMBEDDING_EXAMPLES.md) for complete examples including:
- Generating embeddings
- Semantic search queries
- Topic-based discovery
- Question-based search
- Python and JavaScript client examples

### Performance

- **Embedding Generation**: ~100 verses per batch
- **Search Latency**: <100ms with pgvector indexes
- **Storage**: ~6KB per verse embedding (1536 dimensions)
- **API Cost**: ~$0.03 to embed entire Quran

