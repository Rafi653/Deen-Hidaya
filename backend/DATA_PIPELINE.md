# Quran Data Scraping & Ingestion Pipeline

This directory contains the data scraping and ingestion system for Deen Hidaya.

## Overview

The pipeline consists of two main components:
1. **Scraper** (`scrape_quran.py`) - Fetches Quran text and audio metadata from verified sources
2. **Ingestor** (`ingest.py`) - Loads scraped data into the PostgreSQL database

## Data Sources

### Primary Sources
- **Text**: Quran.com API (https://api.quran.com/) - with local fallback for sample data
- **Translation**: Dr. Mustafa Khattab - The Clear Quran (Translation ID: 131)
- **Audio**: Mishary Rashid Alafasy recitations (links only, not downloaded)

### License Information
- **Quran Text**: Public domain (divine revelation)
- **Translations**: Licensed - Dr. Mustafa Khattab's The Clear Quran (used with permission)
- **Audio**: Permission required - URLs stored, no direct downloads
- **Terms**: https://quran.com/terms

## Quick Start

### 1. Start PostgreSQL

```bash
# From project root
docker compose up -d postgres
```

### 2. Scrape Quran Data

```bash
cd backend

# Scrape first 5 surahs (for testing)
python scrape_quran.py --surahs 1-5

# Scrape specific range
python scrape_quran.py --surahs 1-10

# Scrape all 114 surahs
python scrape_quran.py --all
```

The scraper will:
- Create `/data/quran_text/` directory
- Save one JSON file per surah (e.g., `surah_001.json`)
- Include license metadata in each file
- Store audio URLs (not actual audio files)

### 3. Ingest Data into Database

```bash
cd backend

# Initialize database tables and ingest first 5 surahs
python ingest.py --init --surahs 1-5 --verify

# Ingest specific range
python ingest.py --surahs 1-10

# Ingest all surahs
python ingest.py --all --verify
```

The ingestor will:
- Create database tables (if `--init` is used)
- Upsert surah metadata
- Insert verses with Arabic text
- Insert English translations
- Store audio track URLs
- Record data source and license information

## Data Structure

### Scraped JSON Format

Each surah is stored as a JSON file with this structure:

```json
{
  "surah": {
    "number": 1,
    "name_arabic": "الفاتحة",
    "name_simple": "Al-Fatihah",
    "name_complex": "Al-Fātiĥah",
    "revelation_place": "makkah",
    "revelation_order": 5,
    "verses_count": 7,
    "pages": [1, 1]
  },
  "verses": [
    {
      "verse_number": 1,
      "verse_key": "1:1",
      "text_uthmani": "بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ",
      "text_simple": "بسم الله الرحمن الرحيم",
      "translations": [
        {
          "id": 131,
          "text": "In the name of Allah...",
          "language": "english"
        }
      ]
    }
  ],
  "audio": {
    "reciter": "Mishary Rashid Alafasy",
    "reciter_id": 7,
    "format": "mp3",
    "audio_url": "https://...",
    "license": "Permission required - URL only"
  },
  "metadata": {
    "source": "Quran.com API",
    "scraped_at": "2025-10-29T...",
    "license": {
      "text": "Quran text is public domain",
      "translation": "Dr. Mustafa Khattab...",
      "audio": "Reciter permission required",
      "terms": "https://quran.com/terms"
    }
  }
}
```

### Database Schema

The ingestion creates these tables:

- **surahs** - Chapter metadata (114 surahs)
- **verses** - Individual verses with Arabic text (6236 verses)
- **translations** - Verse translations (one per verse)
- **audio_tracks** - Audio recitation URLs
- **data_sources** - Track data sources and licenses

## Usage Examples

### Verify Database Content

```bash
# Check surahs in database
docker compose exec postgres psql -U deen_user -d deen_hidaya \
  -c "SELECT number, name_simple, verses_count FROM surahs;"

# View verses from Al-Fatihah
docker compose exec postgres psql -U deen_user -d deen_hidaya \
  -c "SELECT verse_key, text_uthmani FROM verses WHERE surah_id = 1;"

# Check translations
docker compose exec postgres psql -U deen_user -d deen_hidaya \
  -c "SELECT v.verse_key, t.text FROM verses v 
      JOIN translations t ON v.id = t.verse_id WHERE v.surah_id = 1;"
```

### Re-run Ingestion

The ingestor performs upsert operations, so you can safely re-run it:

```bash
# Re-ingest with updates
python ingest.py --surahs 1-5
```

## Files

- **scrape_quran.py** - Data scraper module
- **ingest.py** - Database ingestion script
- **models.py** - SQLAlchemy database models
- **database.py** - Database connection management

## Configuration

Environment variables (in `.env`):

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=deen_hidaya
POSTGRES_USER=deen_user
POSTGRES_PASSWORD=change_this_password
```

## Error Handling

Both scripts include robust error handling:
- Graceful fallback when API is unavailable
- Transaction rollback on errors
- Detailed error messages
- Verification mode to check data integrity

## License Compliance

All scraped data includes proper license attribution:
- Source URL
- License type
- Terms of use
- Scraping timestamp

This ensures compliance with data providers' terms of service.

## Testing

The pipeline has been tested with:
- ✓ First 5 surahs scraped successfully
- ✓ Data ingested into PostgreSQL
- ✓ License metadata present
- ✓ Audio URLs stored (not downloaded)
- ✓ Database verification passed

## Next Steps

To extend the pipeline:
1. Add more translations
2. Support multiple reciters
3. Add verse-by-verse audio
4. Implement incremental updates
5. Add data validation rules
6. Create migration scripts

## Support

For issues or questions:
- Check PostgreSQL is running: `docker compose ps`
- Verify database connection: `python -c "from backend.database import test_connection; test_connection()"`
- Review logs: `docker compose logs postgres`
