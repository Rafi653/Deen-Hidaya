# Database Migrations

This directory contains Alembic database migrations for the Deen Hidaya backend.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure database connection in `.env` file:
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=deen_hidaya
POSTGRES_USER=deen_user
POSTGRES_PASSWORD=your_password
```

## Running Migrations

### Apply all pending migrations
```bash
alembic upgrade head
```

### Rollback one migration
```bash
alembic downgrade -1
```

### Rollback to a specific revision
```bash
alembic downgrade <revision_id>
```

### View migration history
```bash
alembic history
```

### View current database version
```bash
alembic current
```

## Creating New Migrations

### Auto-generate a migration from model changes
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Create an empty migration
```bash
alembic revision -m "Description of changes"
```

## Seeding Data

After running migrations, populate the database with surah metadata:

```bash
python seed_surahs.py
```

This will insert all 114 surahs with their metadata (names, verse counts, revelation place, etc.).

## Docker Usage

When using Docker Compose, migrations can be run inside the backend container:

```bash
# Start services
docker-compose up -d postgres

# Wait for postgres to be ready, then run migrations
docker-compose exec backend alembic upgrade head

# Run seed script
docker-compose exec backend python seed_surahs.py
```

Or add migration commands to your Dockerfile or docker-compose startup script.

## Migration Files

Migration files are stored in `alembic/versions/`. Each file represents a database schema change.

## Database Schema

The current schema includes the following tables:

- **surah**: Quran chapters (114 surahs)
- **verse**: Quran verses (ayahs)
- **translation**: Verse translations in different languages
- **audio_track**: Audio recordings of verses by different reciters
- **tag**: Tags for categorizing verses
- **verse_tag**: Many-to-many relationship between verses and tags
- **entity**: Named entities mentioned in the Quran
- **embedding**: Vector embeddings for semantic search
- **bookmark**: User bookmarks with notes

## Troubleshooting

### Connection refused
Make sure PostgreSQL is running and accessible at the configured host/port.

### Migration conflicts
If you have migration conflicts, you may need to merge migration branches:
```bash
alembic merge <revision1> <revision2>
```

### Reset database (WARNING: destroys all data)
```bash
alembic downgrade base
alembic upgrade head
python seed_surahs.py
```
