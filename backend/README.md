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

- `GET /` - Root endpoint
- `GET /health` - Health check endpoint
- `GET /api/v1/health` - API health check endpoint

## Database Schema

The backend uses PostgreSQL with the following main tables:
- `surah` - Quran chapters (114 surahs)
- `verse` - Quran verses (ayahs)
- `translation` - Verse translations
- `audio_track` - Audio recordings by reciters
- `tag` - Tags for categorizing verses
- `verse_tag` - Verse-tag relationships
- `entity` - Named entities in the Quran
- `embedding` - Vector embeddings for semantic search
- `bookmark` - User bookmarks

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

