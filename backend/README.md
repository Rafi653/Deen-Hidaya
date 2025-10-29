# Deen Hidaya Backend

FastAPI backend service for the Deen Hidaya Islamic knowledge platform.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

For development and testing, install additional dependencies:
```bash
pip install -r requirements-dev.txt
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

## Testing

### Quick Start

The easiest way to run tests is using the provided test runner script:

```bash
./run_tests.sh
```

This script automatically:
- Sets `TESTING=true` to use SQLite instead of PostgreSQL
- Cleans up any previous test databases and Python cache
- Runs pytest with all tests

You can also pass pytest arguments to the script:
```bash
./run_tests.sh -v                    # Verbose output
./run_tests.sh test_api.py          # Run specific file
./run_tests.sh -k test_health        # Run tests matching pattern
./run_tests.sh --cov=.              # With coverage
```

### Running Tests Manually

If you prefer to run pytest directly, always set `TESTING=true`:

```bash
TESTING=true pytest
```

Run tests with coverage:
```bash
TESTING=true pytest --cov=. --cov-report=html
```

Run specific test file:
```bash
TESTING=true pytest test_api.py -v
```

Run tests with specific markers:
```bash
TESTING=true pytest -m unit          # Run only unit tests
TESTING=true pytest -m integration   # Run only integration tests
```

### Test Database

Tests automatically use a file-based SQLite database in `/tmp` when `TESTING=true` is set, so you don't need PostgreSQL running to execute tests. This also avoids any psycopg2 installation issues during testing.

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

## Troubleshooting

### psycopg2 Import Error on macOS

If you encounter an error like `ImportError: symbol not found in flat namespace '_PQbackendPID'` when running tests or importing the application, this is typically caused by a broken `psycopg2` installation in conda environments on macOS.

**Solution 1: Use psycopg2-binary (Recommended for development)**
```bash
pip uninstall psycopg2 psycopg2-binary
pip install psycopg2-binary==2.9.9
```

**Solution 2: Reinstall PostgreSQL client libraries**
```bash
brew reinstall postgresql
pip uninstall psycopg2 psycopg2-binary
pip install psycopg2-binary==2.9.9
```

**Solution 3: Use a virtual environment instead of conda**
```bash
# Create a fresh virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

**For Testing Only:**
If you only need to run tests and don't need PostgreSQL connectivity, set the `TESTING` environment variable:
```bash
export TESTING=true
pytest test_api.py -v
```

This will use SQLite in-memory database instead of PostgreSQL, avoiding the psycopg2 dependency entirely during tests.

### Database Connection Issues

If you get connection errors when starting the application:

1. Ensure PostgreSQL is running:
```bash
# macOS
brew services start postgresql

# Linux
sudo systemctl start postgresql
```

2. Check your `.env` file has correct database credentials
3. Verify the database exists:
```bash
psql -U postgres -c "SELECT 1 FROM pg_database WHERE datname='deen_hidaya'"
```

4. Create the database if it doesn't exist:
```bash
psql -U postgres -c "CREATE DATABASE deen_hidaya"
```


