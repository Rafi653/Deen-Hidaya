# Translation and Embedding Fixes

This document explains how to fix two critical issues in the Deen Hidaya backend:

1. **Missing Translations** - English and Telugu translations not available
2. **Missing Embeddings** - Q&A page not working due to missing embeddings

## Issue #1: Missing Translations

### Problem
The Quran data was scraped with both English (translation ID 131) and Telugu (translation ID 140) requested, but only one translation appears in the actual verse data. This causes the frontend to display "Translation not available" for one or both languages.

### Root Cause
The API response from api.quran.com may only include one translation per request, or the scraping parameters need adjustment.

### Solution

Use the provided `fix_translations.py` script to re-scrape and re-ingest the data:

```bash
cd backend

# Fix all surahs (1-114)
python fix_translations.py

# Fix specific range
python fix_translations.py --start 1 --end 10

# Force re-scrape even if files exist
python fix_translations.py --force
```

### What the Script Does

1. **Checks current state**: Analyzes existing translations in the database
2. **Re-scrapes data**: Fetches verses with both translation IDs [131, 140]
3. **Re-ingests data**: Updates the database with new translations
4. **Verifies results**: Confirms both languages are now available

### Expected Results

After running the fix:
- English translations (Dr. Mustafa Khattab) available
- Telugu translations available
- Frontend translation selector works correctly
- "Translation not available" messages should disappear

### Verification

Check translations in database:
```bash
python -c "from database import SessionLocal; from models import Translation; db = SessionLocal(); langs = db.query(Translation.language).distinct().all(); print('Languages:', [l[0] for l in langs]); print('Total:', db.query(Translation).count())"
```

Test API endpoint:
```bash
curl http://localhost:8000/api/v1/surahs/1 | jq '.verses[0].translations'
```

## Issue #2: Missing Embeddings (Q&A Not Working)

### Problem
The Q&A page doesn't work because embeddings are not generated. Even with `OPENAI_API_KEY` configured, the embeddings table is empty, causing semantic search to fail.

### Root Cause
Embeddings need to be explicitly generated after data ingestion. The ingestion process doesn't automatically create embeddings.

### Prerequisites

1. **OpenAI API Key Required**: Get one from https://platform.openai.com/api-keys
2. **Configure Environment**: Add to `.env` file:
   ```
   OPENAI_API_KEY=sk-...
   EMBEDDING_MODEL=text-embedding-ada-002
   EMBEDDING_DIMENSION=1536
   ```
3. **Translations Must Exist**: Run `fix_translations.py` first (embeddings are generated from translation text)

### Solution

Use the provided `fix_embeddings.py` script:

```bash
cd backend

# Check current state (no changes made)
python fix_embeddings.py --check-only

# Generate embeddings for all verses (English)
python fix_embeddings.py

# Generate for specific language
python fix_embeddings.py --language en

# Process in smaller batches (default: 100)
python fix_embeddings.py --batch-size 50

# Resume from specific verse (if interrupted)
python fix_embeddings.py --start-verse 1000

# Test with limited verses
python fix_embeddings.py --max-verses 100
```

### What the Script Does

1. **Validates API Key**: Checks if `OPENAI_API_KEY` is configured correctly
2. **Checks Prerequisites**: Ensures translations exist in the database
3. **Tests API Connection**: Verifies OpenAI API is accessible
4. **Batch Processing**: Generates embeddings in configurable batches
5. **Tracks Progress**: Shows real-time progress and handles errors
6. **Skips Existing**: Only processes verses without embeddings

### Expected Results

After running the fix:
- Embeddings table populated with ~6,236 embeddings (for all Quran verses)
- Q&A page functional with semantic search
- Questions return relevant verses with citations
- Processing time: ~10-20 minutes for all verses (depends on API rate limits)

### Verification

Check embeddings in database:
```bash
python -c "from database import SessionLocal; from models import Embedding; db = SessionLocal(); print('Total embeddings:', db.query(Embedding).count())"
```

Test Q&A endpoint:
```bash
curl -X POST http://localhost:8000/api/v1/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What does the Quran say about patience?", "language": "en", "max_verses": 5}'
```

Expected response includes `cited_verses` with relevant Quran verses.

## Cost Considerations

### OpenAI Embeddings Cost
- Model: `text-embedding-ada-002`
- Cost: ~$0.0001 per 1K tokens
- Quran: ~6,236 verses × ~50 tokens average = ~310K tokens
- **Estimated Cost**: ~$0.03 (three cents) for all verses

### Rate Limits
- Free tier: 3 requests/minute
- Paid tier: 3,000 requests/minute
- Script uses batch API (up to 100 texts per request)
- Processing time depends on your rate limit

## Troubleshooting

### Problem: "OPENAI_API_KEY environment variable is not set"

**Solution**: 
```bash
# Check if .env exists
ls -la .env

# Add to .env file
echo "OPENAI_API_KEY=sk-your-key-here" >> .env

# Restart backend
docker compose restart backend

# Or set temporarily
export OPENAI_API_KEY=sk-your-key-here
python fix_embeddings.py
```

### Problem: "No translations found! You need to fix translations first"

**Solution**: Run translation fix first:
```bash
python fix_translations.py
python fix_embeddings.py
```

### Problem: "Failed to generate test embedding"

**Possible causes**:
1. Invalid API key
2. Network connectivity issues
3. OpenAI API outage
4. Rate limit exceeded

**Solutions**:
- Verify API key at https://platform.openai.com/api-keys
- Check network connection
- Wait a few minutes and retry
- Check OpenAI status: https://status.openai.com/

### Problem: Embeddings generation interrupted

**Solution**: Resume from where it stopped:
```bash
# Check last embedded verse
python -c "from database import SessionLocal; from models import Embedding; db = SessionLocal(); last = db.query(Embedding).order_by(Embedding.verse_id.desc()).first(); print('Last verse ID:', last.verse_id if last else 'None')"

# Resume from next verse
python fix_embeddings.py --start-verse <last_id + 1>
```

### Problem: "Translation not available" still showing after fix

**Solution**:
1. Check if translations were actually added:
   ```bash
   python -c "from database import SessionLocal; from models import Translation; db = SessionLocal(); print('Total:', db.query(Translation).count()); langs = db.query(Translation.language).distinct().all(); print('Languages:', [l[0] for l in langs])"
   ```

2. Verify JSON files have both translations:
   ```bash
   python -c "import json; data = json.load(open('../data/quran_text/surah_001.json')); print('Translations in verse 1:', len(data['verses'][0]['translations']))"
   ```

3. Clear frontend cache and reload

4. If still not working, check frontend language mapping in translation selector

## Docker Usage

If running in Docker:

```bash
# Fix translations
docker compose exec backend python fix_translations.py

# Fix embeddings
docker compose exec backend python fix_embeddings.py

# Check status
docker compose exec backend python fix_embeddings.py --check-only
```

## Running Without Docker

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export POSTGRES_HOST=localhost
export POSTGRES_DB=deen_hidaya
export POSTGRES_USER=deen_user
export POSTGRES_PASSWORD=your_password
export OPENAI_API_KEY=sk-your-key-here

# Run fixes
python fix_translations.py
python fix_embeddings.py
```

## Summary

| Issue | Script | Prerequisite | Estimated Time |
|-------|--------|--------------|----------------|
| Missing Translations | `fix_translations.py` | Internet connection | 5-10 minutes |
| Missing Embeddings | `fix_embeddings.py` | OpenAI API key, translations | 10-20 minutes |

**Total Setup Time**: ~15-30 minutes for complete fix

After running both scripts:
✓ English and Telugu translations available  
✓ Q&A functionality working  
✓ Semantic search operational  
✓ Full Quran browsing experience ready  

## Support

For issues or questions:
1. Check this README first
2. Verify environment variables in `.env`
3. Check Docker logs: `docker compose logs backend`
4. Review API documentation: http://localhost:8000/docs
5. Create an issue on GitHub with error logs
