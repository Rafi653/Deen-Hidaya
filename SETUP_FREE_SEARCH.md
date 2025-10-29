# Setup Guide: Free Search & Embeddings

This guide shows how to set up Deen Hidaya with free embeddings and scalable search.

## Quick Start (Recommended)

### Option 1: Full-Text Search Only (Ultra-lightweight)

**Best for**: Getting started, limited resources, or don't need semantic search

```bash
# 1. Clone and navigate to project
cd Deen-Hidaya

# 2. Configure for FTS-only
cat >> .env << EOF
EMBEDDING_BACKEND=disabled
ENABLE_SEMANTIC_SEARCH=false
EOF

# 3. Start services
docker compose up -d

# 4. Run migrations (includes FTS indexes)
docker compose exec backend alembic upgrade head

# 5. Ingest Quran data
docker compose exec backend python ingest_data.py

# 6. Test search
docker compose exec backend python test_new_search.py
```

**Result**: Fast, free search with zero dependencies on external APIs.

### Option 2: With Free Embeddings (Recommended)

**Best for**: Want semantic search without API costs

```bash
# 1. Clone and navigate to project
cd Deen-Hidaya

# 2. Configure for sentence-transformers
cat >> .env << EOF
EMBEDDING_BACKEND=sentence-transformers
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
EMBEDDING_DIMENSION=384
ENABLE_SEMANTIC_SEARCH=true
EOF

# 3. Install sentence-transformers
docker compose exec backend pip install sentence-transformers

# Or add to requirements.txt and rebuild
echo "sentence-transformers==2.2.2" >> backend/requirements.txt
docker compose build backend
docker compose up -d

# 4. Run migrations
docker compose exec backend alembic upgrade head

# 5. Ingest Quran data
docker compose exec backend python ingest_data.py

# 6. Generate embeddings (one-time, ~5 minutes)
docker compose exec backend python fix_embeddings.py

# 7. Test search
docker compose exec backend python test_new_search.py
```

**Result**: Free semantic search with no ongoing costs.

### Option 3: Keep Using OpenAI (Legacy)

**Best for**: Already have OpenAI API key and want to keep using it

```bash
# 1. Configure for OpenAI
cat >> .env << EOF
EMBEDDING_BACKEND=openai
OPENAI_API_KEY=sk-your-key-here
EMBEDDING_MODEL=text-embedding-ada-002
EMBEDDING_DIMENSION=1536
ENABLE_SEMANTIC_SEARCH=true
EOF

# 2. Follow steps 3-7 from Option 2
```

## Detailed Setup

### Prerequisites

- Docker and Docker Compose
- Git
- 1-2GB free disk space
- (Optional) GPU for faster embedding generation

### Step 1: Database Setup

The database migration automatically creates full-text search indexes:

```bash
# Run migration
docker compose exec backend alembic upgrade head

# Verify indexes were created
docker compose exec postgres psql -U deen_user -d deen_hidaya -c "\d+ verses"
docker compose exec postgres psql -U deen_user -d deen_hidaya -c "\d+ translations"
```

You should see indexes like:
- `verses_text_simple_fts_idx`
- `translations_text_fts_idx`
- `verses_text_simple_trgm_idx`

### Step 2: Choose Embedding Backend

#### Auto-detection (Default)

```bash
# Let the system choose the best available option
export EMBEDDING_BACKEND=auto
```

The system will try in this order:
1. sentence-transformers (if installed)
2. OpenAI (if API key available)
3. Disabled (fall back to FTS)

#### Manual Selection

```bash
# Option A: sentence-transformers (free, local)
export EMBEDDING_BACKEND=sentence-transformers

# Option B: OpenAI (requires API key)
export EMBEDDING_BACKEND=openai
export OPENAI_API_KEY=sk-...

# Option C: Disabled (FTS only)
export EMBEDDING_BACKEND=disabled
```

### Step 3: Install Dependencies

#### For sentence-transformers:

```bash
# Method 1: Install directly
pip install sentence-transformers

# Method 2: Add to requirements.txt
echo "sentence-transformers==2.2.2" >> backend/requirements.txt
pip install -r backend/requirements.txt
```

#### For OpenAI:

```bash
# Already in requirements.txt
pip install openai
```

### Step 4: Generate Embeddings (Optional)

Only needed if you want semantic search:

```bash
# Generate embeddings for all verses
python fix_embeddings.py

# Or for specific language
python fix_embeddings.py --language en

# Or for specific surahs
python fix_embeddings.py --start 1 --end 5
```

**Time**: ~5 minutes for all verses with sentence-transformers
**Storage**: ~9MB for 384-dim embeddings

### Step 5: Test Your Setup

```bash
# Run comprehensive tests
python test_new_search.py

# Test specific search types
python test_new_search.py --query "patience" --type fulltext
python test_new_search.py --query "what is charity" --type semantic
```

## Configuration Reference

### Environment Variables

```env
# Embedding Backend Selection
EMBEDDING_BACKEND=auto|sentence-transformers|openai|disabled

# Sentence-Transformers Configuration
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
EMBEDDING_DIMENSION=384

# OpenAI Configuration (if using openai backend)
OPENAI_API_KEY=sk-...
EMBEDDING_MODEL=text-embedding-ada-002
EMBEDDING_DIMENSION=1536

# Search Configuration
ENABLE_SEMANTIC_SEARCH=true|false

# Optional: Caching
ENABLE_CACHE=false
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Model Options

#### For Multilingual (Recommended)
```env
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
EMBEDDING_DIMENSION=384
```
- Size: 118MB
- Speed: Fast
- Languages: Arabic, English, Telugu, 50+ more

#### For English Only (Faster)
```env
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
```
- Size: 80MB
- Speed: Very fast
- Languages: English primarily

#### For Maximum Quality
```env
EMBEDDING_MODEL=all-mpnet-base-v2
EMBEDDING_DIMENSION=768
```
- Size: 420MB
- Speed: Moderate
- Languages: English
- Quality: Best

## Usage Examples

### API Endpoints

#### Search with Auto-detection
```bash
curl "http://localhost:8000/api/v1/search?q=patience&search_type=auto"
```

#### Full-Text Search
```bash
curl "http://localhost:8000/api/v1/search?q=patience+faith&search_type=fulltext"
```

#### Semantic Search (if enabled)
```bash
curl "http://localhost:8000/api/v1/search?q=what+is+charity&search_type=semantic"
```

#### Hybrid Search
```bash
curl "http://localhost:8000/api/v1/search?q=mercy&search_type=hybrid"
```

### Python SDK

```python
from database import SessionLocal
from search_utils_v2 import unified_search

db = SessionLocal()

# Auto-select best method
results = unified_search(
    db, 
    query="patience and gratitude",
    search_type="auto"
)

# Specific method
results = unified_search(
    db,
    query="what does quran say about prayer",
    search_type="semantic"
)

for result in results:
    print(f"{result.surah_number}:{result.verse_number}")
    print(f"Score: {result.score:.3f}")
    print(f"Type: {result.match_type}")
```

## Troubleshooting

### Issue: sentence-transformers not found

```bash
# Install it
pip install sentence-transformers

# Or use FTS only
export EMBEDDING_BACKEND=disabled
```

### Issue: Model download fails

```bash
# Manually download model
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
```

### Issue: Search returns no results

```bash
# Check if data is ingested
docker compose exec backend python -c "from database import SessionLocal; from models import Verse; print(SessionLocal().query(Verse).count())"

# If 0, ingest data
docker compose exec backend python ingest_data.py
```

### Issue: Semantic search not working

```bash
# Check if embeddings are generated
docker compose exec backend python -c "from database import SessionLocal; from models import Embedding; print(SessionLocal().query(Embedding).count())"

# If 0, generate embeddings
docker compose exec backend python fix_embeddings.py
```

### Issue: Search is slow

```bash
# Check if indexes exist
docker compose exec postgres psql -U deen_user -d deen_hidaya -c "\di"

# If missing, run migration
docker compose exec backend alembic upgrade head
```

## Performance Tuning

### For Better Speed

1. **Use smaller model**:
   ```env
   EMBEDDING_MODEL=all-MiniLM-L6-v2
   ```

2. **Add indexes** (if not already present):
   ```bash
   docker compose exec backend alembic upgrade head
   ```

3. **Enable caching**:
   ```env
   ENABLE_CACHE=true
   REDIS_HOST=redis
   ```

### For Better Quality

1. **Use larger model**:
   ```env
   EMBEDDING_MODEL=all-mpnet-base-v2
   EMBEDDING_DIMENSION=768
   ```

2. **Use hybrid search**:
   ```bash
   curl "http://localhost:8000/api/v1/search?q=charity&search_type=hybrid"
   ```

## Migration from OpenAI

If you're currently using OpenAI and want to switch:

### Step 1: Backup Current Setup
```bash
docker compose exec backend python -c "from database import SessionLocal; from models import Embedding; print(f'{SessionLocal().query(Embedding).count()} embeddings')"
```

### Step 2: Install sentence-transformers
```bash
docker compose exec backend pip install sentence-transformers
```

### Step 3: Update Configuration
```bash
# Update .env
export EMBEDDING_BACKEND=sentence-transformers
export EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
export EMBEDDING_DIMENSION=384
```

### Step 4: Regenerate Embeddings
```bash
# This will replace OpenAI embeddings with sentence-transformers embeddings
docker compose exec backend python fix_embeddings.py --regenerate
```

### Step 5: Test
```bash
docker compose exec backend python test_new_search.py
```

## Cost Comparison

### Current OpenAI Setup
- Initial: $0.03 (6,236 verses)
- Monthly queries: ~$0.10
- Annual: ~$1.23

### New sentence-transformers Setup
- Initial: $0
- Monthly queries: $0
- Annual: $0
- Savings: 100%

### FTS Only Setup
- Initial: $0
- Monthly queries: $0
- Annual: $0
- Performance: Excellent

## Next Steps

1. ✅ Set up your preferred backend
2. ✅ Run migrations for FTS indexes
3. ✅ Ingest Quran data
4. ✅ Generate embeddings (if using semantic search)
5. ✅ Test search functionality
6. 📖 Read [API Documentation](./backend/API_DOCUMENTATION.md)
7. 🔍 Explore [Search Architecture](./backend/LIGHTWEIGHT_SEARCH_ARCHITECTURE.md)
8. 🤖 Learn about [Embedding Alternatives](./backend/FREE_EMBEDDING_ALTERNATIVES.md)

## Support

- 📚 [Full Documentation](./README.md)
- 🐛 [Report Issues](https://github.com/Rafi653/Deen-Hidaya/issues)
- 💬 [Discussions](https://github.com/Rafi653/Deen-Hidaya/discussions)

---

**Status**: Ready for production use  
**Cost**: $0 (recommended setup)  
**Performance**: Fast and scalable  
**Quality**: Excellent
