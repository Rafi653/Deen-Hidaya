# Quick Reference - Free Search & Embeddings

## TL;DR - What Changed?

### Before
- ❌ Required OpenAI API key ($)
- ❌ Had usage costs
- ❌ Telugu translation (ID 213) not working
- ❌ Only semantic search available

### After
- ✅ Free local embeddings (sentence-transformers)
- ✅ Zero cost
- ✅ Translation issues documented with solutions
- ✅ Multiple search methods (FTS, semantic, hybrid)
- ✅ Works offline

## Setup Commands

### Minimal Setup (FTS Only)
```bash
export EMBEDDING_BACKEND=disabled
docker compose up -d
docker compose exec backend alembic upgrade head
docker compose exec backend python ingest_data.py
```

### Recommended Setup (Free Embeddings)
```bash
export EMBEDDING_BACKEND=sentence-transformers
docker compose exec backend pip install sentence-transformers
docker compose up -d
docker compose exec backend alembic upgrade head
docker compose exec backend python ingest_data.py
docker compose exec backend python fix_embeddings.py
```

## Search Examples

### Full-Text Search (Fast, always available)
```bash
curl "localhost:8000/api/v1/search?q=patience&search_type=fulltext"
```

### Semantic Search (Requires embeddings)
```bash
curl "localhost:8000/api/v1/search?q=what+is+charity&search_type=semantic"
```

### Auto-Select (Recommended)
```bash
curl "localhost:8000/api/v1/search?q=mercy&search_type=auto"
```

## Configuration Cheat Sheet

### FTS Only (No embeddings)
```env
EMBEDDING_BACKEND=disabled
ENABLE_SEMANTIC_SEARCH=false
```

### Free Embeddings (Recommended)
```env
EMBEDDING_BACKEND=sentence-transformers
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
EMBEDDING_DIMENSION=384
ENABLE_SEMANTIC_SEARCH=true
```

### OpenAI (Legacy)
```env
EMBEDDING_BACKEND=openai
OPENAI_API_KEY=sk-...
EMBEDDING_MODEL=text-embedding-ada-002
EMBEDDING_DIMENSION=1536
ENABLE_SEMANTIC_SEARCH=true
```

## Files Reference

### New Files
- `backend/embedding_service_v2.py` - Multi-backend embedding service
- `backend/search_utils_v2.py` - Enhanced search with FTS
- `backend/test_new_search.py` - Test script
- `backend/alembic/versions/add_fulltext_search_indexes.py` - DB migration
- `SETUP_FREE_SEARCH.md` - Detailed setup guide

### Documentation
- `FREE_EMBEDDING_ALTERNATIVES.md` - Embedding alternatives analysis
- `TRANSLATION_API_INVESTIGATION.md` - Translation API issues
- `LIGHTWEIGHT_SEARCH_ARCHITECTURE.md` - Search architecture
- `ISSUE_1_SOLUTION_SUMMARY.md` - Complete solution summary

### Updated Files
- `requirements.txt` - Added sentence-transformers
- `.env.example` - New configuration options

## Common Tasks

### Test Embedding Service
```bash
python backend/test_new_search.py
```

### Generate Embeddings
```bash
# All verses
python backend/fix_embeddings.py

# Specific language
python backend/fix_embeddings.py --language en

# Specific surahs
python backend/fix_embeddings.py --start 1 --end 5
```

### Run Migrations
```bash
docker compose exec backend alembic upgrade head
```

### Check Search Performance
```bash
python backend/test_new_search.py
```

## Troubleshooting Quick Fixes

### No search results?
```bash
# Check data
docker compose exec backend python -c "from database import SessionLocal; from models import Verse; print(SessionLocal().query(Verse).count())"

# Ingest if needed
docker compose exec backend python ingest_data.py
```

### Semantic search not working?
```bash
# Check embeddings
docker compose exec backend python -c "from database import SessionLocal; from models import Embedding; print(SessionLocal().query(Embedding).count())"

# Generate if needed
docker compose exec backend python fix_embeddings.py
```

### Search is slow?
```bash
# Check indexes
docker compose exec postgres psql -U deen_user -d deen_hidaya -c "\di"

# Add if missing
docker compose exec backend alembic upgrade head
```

## Cost Savings

| Setup | Initial Cost | Monthly Cost | Annual Cost |
|-------|-------------|--------------|-------------|
| OpenAI (old) | $0.03 | $0.10 | $1.23 |
| sentence-transformers | $0 | $0 | $0 |
| FTS only | $0 | $0 | $0 |

**Savings**: 100% ($1.23/year → $0)

## Performance Comparison

| Method | Speed | Quality | Cost | When to Use |
|--------|-------|---------|------|-------------|
| Exact | 50-100ms | Basic | $0 | Short queries |
| Full-Text | 5-20ms | Good | $0 | Keyword search |
| Semantic | 100-200ms | Excellent | $0 | Conceptual queries |
| Hybrid | 150-300ms | Best | $0 | Complex queries |

## Model Comparison

| Model | Size | Speed | Languages | Quality |
|-------|------|-------|-----------|---------|
| MiniLM-L6 | 80MB | Very Fast | English | Good |
| MiniLM-L12-Multi | 118MB | Fast | 50+ | Excellent |
| MPNet-base | 420MB | Moderate | English | Outstanding |

## Integration Example

```python
from embedding_service_v2 import EmbeddingServiceV2
from search_utils_v2 import unified_search
from database import SessionLocal

# Initialize
db = SessionLocal()
embedding_service = EmbeddingServiceV2()

# Check what's available
print(f"Backend: {embedding_service.backend_name}")
print(f"Enabled: {embedding_service.is_enabled}")

# Search
results = unified_search(
    db,
    query="patience in hardship",
    search_type="auto",  # Auto-selects best method
    limit=10
)

# Display results
for r in results:
    print(f"{r.surah_number}:{r.verse_number} - Score: {r.score:.3f}")
```

## Migration Paths

### From OpenAI → sentence-transformers
```bash
export EMBEDDING_BACKEND=sentence-transformers
pip install sentence-transformers
python fix_embeddings.py --regenerate
```

### From OpenAI → FTS only
```bash
export EMBEDDING_BACKEND=disabled
export ENABLE_SEMANTIC_SEARCH=false
# No regeneration needed, just use FTS
```

### From FTS → sentence-transformers
```bash
export EMBEDDING_BACKEND=sentence-transformers
pip install sentence-transformers
python fix_embeddings.py
export ENABLE_SEMANTIC_SEARCH=true
```

## Key Takeaways

1. ✅ **Free is possible**: sentence-transformers provides zero-cost embeddings
2. ✅ **FTS is fast**: PostgreSQL full-text search is excellent for most queries
3. ✅ **Flexible setup**: Choose what works for your needs
4. ✅ **Offline capable**: No external API dependencies required
5. ✅ **Multilingual**: Supports Arabic, English, Telugu and more

## Next Steps

1. Choose your setup (FTS, sentence-transformers, or OpenAI)
2. Run setup commands
3. Test with `test_new_search.py`
4. Start using the search API
5. Monitor performance and adjust as needed

## Support Resources

- 📖 [Detailed Setup](./SETUP_FREE_SEARCH.md)
- 🏗️ [Architecture Guide](./backend/LIGHTWEIGHT_SEARCH_ARCHITECTURE.md)
- 🔍 [Embedding Alternatives](./backend/FREE_EMBEDDING_ALTERNATIVES.md)
- 🌐 [Translation Investigation](./backend/TRANSLATION_API_INVESTIGATION.md)
- 📝 [Complete Solution](./ISSUE_1_SOLUTION_SUMMARY.md)
