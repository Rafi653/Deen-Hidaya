# Quran Data Scraping & Ingestion Pipeline

This directory contains the tools for scraping Quran text, translations, and audio metadata from verified sources and ingesting them into the database.

## Overview

The pipeline consists of three main components:

1. **scrape_quran.py** - Fetches Quran data from api.quran.com
2. **ingest_data.py** - Loads scraped JSON data into PostgreSQL
3. **generate_sample_data.py** - Generates sample data for testing

## Data Sources

### Primary Source: api.quran.com

- **Quran Text**: Public Domain
- **Translations**: Various licenses (see individual translators)
- **Audio**: everyayah.com (Free for non-commercial use)

All scraped data includes complete license metadata and attribution information.

## Quick Start

### 1. Scraping Data

**Note:** Due to network restrictions in sandboxed environments, the scraper includes fallback mechanisms. For testing, use the sample data generator.

```bash
# Scrape surahs 1-5 from api.quran.com (requires internet access)
python3 scrape_quran.py --start 1 --end 5

# Generate sample data for testing (works offline)
python3 generate_sample_data.py
```

**Scraper Options:**
- `--start N` - Starting surah number (1-114, default: 1)
- `--end N` - Ending surah number (1-114, default: 5)
- `--no-audio` - Skip audio metadata
- `--output-dir PATH` - Custom output directory

### 2. Setting Up the Database

```bash
# Create .env file (if not exists)
cp ../.env.example ../.env

# Start PostgreSQL
docker compose up -d postgres

# Wait for database to be ready (check with docker ps)

# Run migrations
alembic upgrade head

# Seed surah metadata
python3 seed_surahs.py
```

### 3. Ingesting Data

```bash
# Ingest surahs 1-5 from JSON files
python3 ingest_data.py --start 1 --end 5

# Ingest all available JSON files
python3 ingest_data.py --start 1 --end 114
```

**Ingester Options:**
- `--start N` - Starting surah number (default: 1)
- `--end N` - Ending surah number (default: 5)
- `--data-dir PATH` - Custom data directory

## Data Structure

### JSON File Format

Each scraped surah is saved as `data/quran_text/surah_XXX.json` with the following structure:

```json
{
  "metadata": {
    "surah_number": 1,
    "scraped_at": "2025-10-29T02:00:00.000000",
    "source": "api.quran.com",
    "version": "1.0"
  },
  "license": {
    "text": {
      "source": "api.quran.com",
      "license": "Public Domain",
      "attribution": "The Quran text is in the public domain",
      "terms_url": "https://quran.com/terms",
      "fetched_at": "2025-10-29T02:00:00.000000"
    },
    "translations": { /* ... */ },
    "audio": { /* ... */ }
  },
  "surah_info": {
    "id": 1,
    "name_arabic": "الفاتحة",
    "name_simple": "Al-Fatihah",
    "name_complex": "Al-Fātihah",
    "revelation_place": "Meccan",
    "verses_count": 7
  },
  "verses": [
    {
      "verse_number": 1,
      "text_uthmani": "بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ",
      "text_imlaei": "بسم الله الرحمن الرحيم",
      "juz_number": 1,
      "translations": [
        {
          "text": "In the name of Allah...",
          "resource_name": "Sahih International",
          "language_name": "english"
        }
      ]
    }
  ],
  "audio_metadata": {
    "audio_file": {
      "audio_url": "https://verses.quran.com/..."
    },
    "recitation": {
      "reciter_name": "Mishari Rashid al-`Afasy"
    }
  }
}
```

### Database Schema

The ingester populates the following tables:

- **surah** - Chapter metadata
- **verse** - Verse text and metadata
- **translation** - Verse translations
- **audio_track** - Audio recitation URLs

## Features

### Scraper (`scrape_quran.py`)

- ✅ Fetches from verified API (api.quran.com)
- ✅ Retry logic with exponential backoff
- ✅ Rate limiting (1 second between requests)
- ✅ Complete license metadata
- ✅ Audio URL storage (not downloaded locally)
- ✅ Structured JSON output
- ✅ Progress tracking and statistics

### Ingester (`ingest_data.py`)

- ✅ Upsert logic (handles updates gracefully)
- ✅ Transactional processing
- ✅ Relationship management (surahs → verses → translations)
- ✅ Audio metadata storage
- ✅ Error handling and rollback
- ✅ Progress reporting
- ✅ Statistics output

## Testing

### Running the Complete Pipeline

```bash
# 1. Generate sample data
python3 generate_sample_data.py

# 2. Setup database
alembic upgrade head
python3 seed_surahs.py

# 3. Ingest data
python3 ingest_data.py --start 1 --end 5

# 4. Verify data
python3 -c "
from database import SessionLocal
from models import Surah, Verse, Translation

db = SessionLocal()
print(f'Surahs: {db.query(Surah).count()}')
print(f'Verses: {db.query(Verse).count()}')
print(f'Translations: {db.query(Translation).count()}')
db.close()
"
```

### Verification Queries

```python
from database import SessionLocal
from models import Surah, Verse, Translation, AudioTrack

db = SessionLocal()

# Count ingested data
print(f"Surahs: {db.query(Surah).filter(Surah.number <= 5).count()}")
print(f"Verses: {db.query(Verse).join(Surah).filter(Surah.number <= 5).count()}")
print(f"Translations: {db.query(Translation).join(Verse).join(Surah).filter(Surah.number <= 5).count()}")
print(f"Audio Tracks: {db.query(AudioTrack).join(Verse).join(Surah).filter(Surah.number <= 5).count()}")

# Sample verse
verse = db.query(Verse).join(Surah).filter(Surah.number == 1, Verse.verse_number == 1).first()
print(f"\nSample (1:1): {verse.text_arabic}")
if verse.translations:
    print(f"Translation: {verse.translations[0].text}")

db.close()
```

## License Compliance

All data includes proper attribution:

1. **Quran Text**: Public Domain
2. **Translations**: Varies by translator (documented in JSON)
3. **Audio**: Free for non-commercial use (everyayah.com)

Each JSON file includes complete license information with:
- Source attribution
- License type
- Terms URL
- Fetch timestamp

## Troubleshooting

### Network Issues

If scraping fails due to network restrictions:
```bash
# Use sample data generator instead
python3 generate_sample_data.py
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Verify connection settings
cat ../.env | grep POSTGRES

# Test connection
python3 -c "from database import engine; print(engine.connect())"
```

### Ingestion Failures

```bash
# Check if JSON files exist
ls -lh ../data/quran_text/

# Validate JSON format
python3 -c "import json; json.load(open('../data/quran_text/surah_001.json'))"

# Run with single surah for debugging
python3 ingest_data.py --start 1 --end 1
```

## API Reference

### QuranScraper Class

```python
from scrape_quran import QuranScraper

scraper = QuranScraper(output_dir="custom/path")
scraper.scrape_surah(1)  # Scrape single surah
stats = scraper.scrape_multiple_surahs(1, 5)  # Scrape range
```

### QuranDataIngester Class

```python
from ingest_data import QuranDataIngester

ingester = QuranDataIngester(data_dir="custom/path")
ingester.ingest_surah(1)  # Ingest single surah
stats = ingester.ingest_multiple_surahs(1, 5)  # Ingest range
```

## Future Enhancements

- [ ] Support for multiple translations
- [ ] Word-by-word data
- [ ] Tafsir (commentary) integration
- [ ] Multiple reciters
- [ ] Verse-level audio segments
- [ ] Juz and Hizb boundaries
- [ ] Progress resumption for large batches
- [ ] Parallel processing for faster ingestion

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review error logs
3. Verify database schema is up to date
4. Ensure all dependencies are installed

## References

- [api.quran.com Documentation](https://api.quran.com/api/docs/)
- [Quran.com Terms](https://quran.com/terms)
- [EveryAyah.com](https://everyayah.com/)
