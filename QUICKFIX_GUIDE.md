# Quick Fix Guide - Translation & Embedding Issues

This guide helps you quickly fix two critical issues in Deen Hidaya:
1. **Missing/Incorrect Translations** (English + Telugu)
2. **Q&A Not Working** (Missing Embeddings)

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key (for embeddings only)
- ~30 minutes of time

## Quick Start (Recommended)

### Step 1: Start Services

```bash
# Clone and start the project
git clone https://github.com/Rafi653/Deen-Hidaya.git
cd Deen-Hidaya

# Create .env file
cp .env.example .env

# Add your OpenAI API key to .env
echo "OPENAI_API_KEY=sk-your-key-here" >> .env

# Start services
docker compose up -d

# Wait for services to be ready (~30 seconds)
docker compose logs -f backend | grep "Application startup complete"
```

### Step 2: Fix Translations

```bash
# Re-scrape with correct translation IDs (English 131 + Telugu 213)
docker compose exec backend python fix_translations.py --force

# This will:
# - Re-scrape all 114 surahs with correct translations
# - Take ~5-10 minutes
# - Show progress for each surah
```

**Expected Output:**
```
✓ Successfully saved Surah 1 to /data/quran_text/surah_001.json
✓ Successfully saved Surah 2 to /data/quran_text/surah_002.json
...
Successful: 114/114
```

### Step 3: Fix Embeddings (Enable Q&A)

```bash
# Generate embeddings for semantic search
docker compose exec backend python fix_embeddings.py

# This will:
# - Generate embeddings for ~6,236 verses
# - Take ~10-20 minutes
# - Cost ~$0.03 in OpenAI API calls
# - Show batch progress
```

**Expected Output:**
```
✓ API connection successful (embedding dimension: 1536)
Processing 6236 verses...
Batch 1/63 (verses 1-100)
  Success: 100, Errors: 0
  Overall progress: 1.6%
...
✓ All embeddings generated successfully!
```

### Step 4: Verify

```bash
# Check translations
docker compose exec backend python -c "from database import SessionLocal; from models import Translation; db = SessionLocal(); print(f'Translations: {db.query(Translation).count()}'); print(f'Languages: {[l[0] for l in db.query(Translation.language).distinct().all()]}')"

# Expected: Translations: 12472, Languages: ['en', 'te']

# Check embeddings
docker compose exec backend python -c "from database import SessionLocal; from models import Embedding; db = SessionLocal(); print(f'Embeddings: {db.query(Embedding).count()}')"

# Expected: Embeddings: 6236

# Test Q&A endpoint
curl -X POST http://localhost:8000/api/v1/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What does the Quran say about patience?", "language": "en", "max_verses": 3}' | jq '.cited_verses | length'

# Expected: 3 (or more verses returned)
```

### Step 5: Browse

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **Test Q&A**: http://localhost:3000/qa

## Troubleshooting

### Issue: "OPENAI_API_KEY environment variable is not set"

```bash
# Edit .env file
nano .env

# Add this line:
OPENAI_API_KEY=sk-your-actual-key-here

# Restart backend
docker compose restart backend

# Try again
docker compose exec backend python fix_embeddings.py
```

### Issue: "No translations found"

```bash
# Run translation fix first
docker compose exec backend python fix_translations.py --force

# Then run embeddings
docker compose exec backend python fix_embeddings.py
```

### Issue: "Failed to generate test embedding"

**Possible causes:**
- Invalid API key
- Network issues
- Rate limit

**Solutions:**
```bash
# Verify API key
echo $OPENAI_API_KEY

# Check network
curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"

# Wait and retry
sleep 60
docker compose exec backend python fix_embeddings.py
```

### Issue: Process interrupted

```bash
# Resume from where it stopped
docker compose exec backend python -c "from database import SessionLocal; from models import Embedding; db = SessionLocal(); last = db.query(Embedding).order_by(Embedding.verse_id.desc()).first(); print(f'Last verse: {last.verse_id if last else 0}')"

# Resume (replace 1234 with last verse ID + 1)
docker compose exec backend python fix_embeddings.py --start-verse 1234
```

## Alternative: Non-Docker Setup

If you're not using Docker:

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment
export POSTGRES_HOST=localhost
export POSTGRES_DB=deen_hidaya
export POSTGRES_USER=deen_user
export POSTGRES_PASSWORD=your_password
export OPENAI_API_KEY=sk-your-key-here

# Run fixes
python fix_translations.py --force
python fix_embeddings.py
```

## Summary

| Step | Script | Time | Cost |
|------|--------|------|------|
| 1. Fix Translations | `fix_translations.py --force` | 5-10 min | Free |
| 2. Generate Embeddings | `fix_embeddings.py` | 10-20 min | ~$0.03 |
| **Total** | | **15-30 min** | **~$0.03** |

After completion:
- ✅ English and Telugu translations available
- ✅ Q&A functionality working with semantic search
- ✅ Full Quran browsing experience ready
- ✅ Translation selector working in frontend

## Getting Help

1. Check detailed documentation: `backend/FIXES_README.md`
2. View logs: `docker compose logs backend`
3. Test API: http://localhost:8000/docs
4. Create GitHub issue with error details

## What Gets Fixed?

### Before Fix
❌ "Translation not available" in frontend  
❌ Only Spanish translation (wrong language)  
❌ Q&A page returns no results  
❌ Semantic search not working  

### After Fix
✅ English translations (Dr. Mustafa Khattab)  
✅ Telugu translations (Abdul Hafeez & Mohammed Abdul Haq)  
✅ Q&A page working with verse citations  
✅ Semantic search operational  
✅ All 6,236+ verses searchable  

## Advanced Options

### Fix Only Specific Surahs
```bash
# Fix first 10 surahs only
docker compose exec backend python fix_translations.py --start 1 --end 10 --force
```

### Test Embeddings First
```bash
# Generate embeddings for 100 verses only (test)
docker compose exec backend python fix_embeddings.py --max-verses 100

# Check results
# If successful, run for all verses
docker compose exec backend python fix_embeddings.py
```

### Check Status Only
```bash
# Check without making changes
docker compose exec backend python fix_embeddings.py --check-only
```

### Batch Size Adjustment
```bash
# Smaller batches (if rate limited)
docker compose exec backend python fix_embeddings.py --batch-size 50

# Larger batches (if you have higher rate limits)
docker compose exec backend python fix_embeddings.py --batch-size 200
```

## Support

For detailed troubleshooting and explanations:
- **Detailed Guide**: `backend/FIXES_README.md`
- **Backend Docs**: `backend/README.md`
- **API Docs**: http://localhost:8000/docs
- **GitHub Issues**: https://github.com/Rafi653/Deen-Hidaya/issues

---

**Note**: These scripts are safe to run multiple times. They skip existing data and only update what's needed.
