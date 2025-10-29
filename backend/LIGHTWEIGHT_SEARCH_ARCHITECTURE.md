# Lightweight & Scalable Search Architecture

## Problem Statement
Need a lightweight but scalable implementation for search and Q&A functionality that:
- Works without expensive API calls
- Scales to handle increasing load
- Provides good search quality
- Requires minimal infrastructure

## Current Implementation Analysis

### Existing Search Methods
1. **Exact Search**: Simple ILIKE matching
2. **Fuzzy Search**: PostgreSQL trigram similarity
3. **Semantic Search**: OpenAI embeddings (costly)
4. **Hybrid Search**: Combines all three

### Current Issues
1. ❌ Semantic search requires paid OpenAI API
2. ❌ No full-text search indexes (slow on large datasets)
3. ❌ Limited relevance scoring
4. ❌ No query optimization
5. ❌ No caching layer

## Recommended Architecture: Multi-Tier Search

### Tier 1: PostgreSQL Full-Text Search (Primary)
**Purpose**: Fast, reliable keyword and phrase matching  
**Cost**: Zero  
**Performance**: Excellent with proper indexes  
**Quality**: Good for exact and near-exact matches  

#### Implementation

##### 1. Add Full-Text Search Columns
```sql
-- Add tsvector columns for fast text search
ALTER TABLE verses ADD COLUMN text_arabic_tsv tsvector;
ALTER TABLE verses ADD COLUMN text_simple_tsv tsvector;
ALTER TABLE translations ADD COLUMN text_tsv tsvector;

-- Update vectors (run once, or use triggers)
UPDATE verses SET 
  text_arabic_tsv = to_tsvector('arabic', COALESCE(text_arabic, '')),
  text_simple_tsv = to_tsvector('simple', COALESCE(text_simple, ''));

UPDATE translations SET
  text_tsv = to_tsvector('english', COALESCE(text, ''));

-- Create GIN indexes for fast lookup
CREATE INDEX verses_text_arabic_tsv_idx ON verses USING GIN(text_arabic_tsv);
CREATE INDEX verses_text_simple_tsv_idx ON verses USING GIN(text_simple_tsv);
CREATE INDEX translations_text_tsv_idx ON translations USING GIN(text_tsv);

-- Auto-update triggers
CREATE TRIGGER verses_text_arabic_tsv_update 
  BEFORE INSERT OR UPDATE ON verses
  FOR EACH ROW EXECUTE FUNCTION
  tsvector_update_trigger(text_arabic_tsv, 'pg_catalog.arabic', text_arabic);
```

##### 2. Implement BM25-Style Ranking
```python
def fulltext_search(db, query, language='en', limit=20):
    """
    PostgreSQL full-text search with BM25-style ranking
    """
    # Parse query into tsquery format
    tsquery = parse_query_to_tsquery(query)
    
    if language == 'ar':
        # Arabic search
        results = db.query(
            Verse,
            func.ts_rank_cd(Verse.text_simple_tsv, func.to_tsquery('simple', tsquery)).label('rank')
        ).filter(
            Verse.text_simple_tsv.op('@@')(func.to_tsquery('simple', tsquery))
        ).order_by(
            text('rank DESC')
        ).limit(limit).all()
    else:
        # Translation search
        results = db.query(
            Verse,
            func.ts_rank_cd(Translation.text_tsv, func.to_tsquery('english', tsquery)).label('rank')
        ).join(Translation).filter(
            Translation.language == language,
            Translation.text_tsv.op('@@')(func.to_tsquery('english', tsquery))
        ).order_by(
            text('rank DESC')
        ).limit(limit).all()
    
    return results
```

##### 3. Query Optimization
```python
def parse_query_to_tsquery(query):
    """
    Convert user query to PostgreSQL tsquery format
    
    Examples:
      "patience and faith" -> "patience & faith"
      "patience OR faith" -> "patience | faith"
      "patience -doubt" -> "patience & !doubt"
    """
    # Handle AND, OR, NOT operators
    query = query.replace(' AND ', ' & ')
    query = query.replace(' OR ', ' | ')
    query = query.replace(' NOT ', ' !')
    query = query.replace('-', '!')
    
    # Default to AND if no operators
    if '&' not in query and '|' not in query:
        words = query.split()
        query = ' & '.join(words)
    
    return query
```

### Tier 2: Optional Sentence-Transformers (Enhanced)
**Purpose**: Semantic understanding for conceptual queries  
**Cost**: Zero (local model)  
**Performance**: Good (with caching)  
**Quality**: Excellent for "what does Quran say about..." queries  

#### Implementation (Optional Feature)

```python
from sentence_transformers import SentenceTransformer
from functools import lru_cache

class OptionalSemanticSearch:
    """Optional semantic search using free sentence-transformers"""
    
    def __init__(self):
        self.enabled = os.getenv('ENABLE_SEMANTIC_SEARCH', 'false').lower() == 'true'
        self.model = None
        
    @lru_cache(maxsize=1)
    def get_model(self):
        """Lazy load model only when needed"""
        if not self.enabled:
            return None
        
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            except ImportError:
                logger.warning("sentence-transformers not installed, semantic search disabled")
                self.enabled = False
                return None
        
        return self.model
    
    def search(self, query, db, language='en', limit=20):
        """Semantic search with fallback to full-text"""
        model = self.get_model()
        
        if not model:
            # Fallback to full-text search
            return fulltext_search(db, query, language, limit)
        
        # Generate query embedding
        query_embedding = model.encode(query)
        
        # Use pgvector for similarity search
        results = db.query(
            Verse,
            Embedding.embedding_vector.cosine_distance(query_embedding).label('distance')
        ).join(Embedding).filter(
            Embedding.language == language
        ).order_by(
            text('distance ASC')
        ).limit(limit).all()
        
        return results
```

### Tier 3: Redis Caching (Performance)
**Purpose**: Cache frequently accessed queries  
**Cost**: Minimal (optional)  
**Performance**: Excellent  
**Quality**: Same as underlying search  

```python
import redis
import json

class SearchCache:
    """Cache search results for performance"""
    
    def __init__(self):
        self.enabled = os.getenv('ENABLE_CACHE', 'false').lower() == 'true'
        if self.enabled:
            self.redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=0,
                decode_responses=True
            )
        else:
            self.redis_client = None
    
    def get(self, key):
        """Get cached result"""
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            result = self.redis_client.get(key)
            return json.loads(result) if result else None
        except:
            return None
    
    def set(self, key, value, ttl=3600):
        """Cache result with TTL"""
        if not self.enabled or not self.redis_client:
            return
        
        try:
            self.redis_client.setex(key, ttl, json.dumps(value))
        except:
            pass
    
    def cache_key(self, query, language, search_type, limit):
        """Generate cache key"""
        import hashlib
        key_parts = f"{query}:{language}:{search_type}:{limit}"
        return f"search:{hashlib.md5(key_parts.encode()).hexdigest()}"
```

## Complete Search Flow

```python
def unified_search(db, query, language='en', search_type='auto', limit=20):
    """
    Unified search with automatic method selection
    
    Search Type Selection:
    - 'exact': Fast keyword matching
    - 'fulltext': PostgreSQL FTS with ranking
    - 'semantic': ML-based semantic search (optional)
    - 'auto': Automatically choose best method
    """
    
    # 1. Check cache
    cache = SearchCache()
    cache_key = cache.cache_key(query, language, search_type, limit)
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    # 2. Choose search method
    if search_type == 'auto':
        search_type = choose_search_type(query)
    
    # 3. Execute search
    if search_type == 'exact':
        results = exact_search(db, query, language, limit)
    elif search_type == 'fulltext':
        results = fulltext_search(db, query, language, limit)
    elif search_type == 'semantic':
        semantic_searcher = OptionalSemanticSearch()
        results = semantic_searcher.search(query, db, language, limit)
    else:
        # Default to full-text
        results = fulltext_search(db, query, language, limit)
    
    # 4. Cache results
    cache.set(cache_key, results)
    
    return results

def choose_search_type(query):
    """
    Automatically choose best search type based on query
    
    Rules:
    - Short queries (1-2 words): exact
    - Phrase queries ("..."): exact
    - Question queries (what, how, why): semantic (if enabled) or fulltext
    - Default: fulltext
    """
    words = query.split()
    
    # Short queries
    if len(words) <= 2:
        return 'exact'
    
    # Question queries
    question_words = ['what', 'how', 'why', 'when', 'where', 'who']
    if any(query.lower().startswith(qw) for qw in question_words):
        return 'semantic'
    
    # Default
    return 'fulltext'
```

## Performance Benchmarks

### Expected Performance (6,236 verses)

| Search Method | Query Time | Memory Usage | Setup Cost |
|--------------|-----------|--------------|------------|
| Exact (ILIKE) | ~50-100ms | 0MB | None |
| Full-Text Search | ~5-20ms | ~10MB indexes | One-time index |
| Semantic (local) | ~100-200ms | ~120MB model | First load |
| Semantic (cached) | ~5-10ms | ~120MB model | First load |
| With Redis | ~1-5ms | +50MB | Redis setup |

### Scalability

| Dataset Size | FTS Performance | Semantic Performance | Recommended Setup |
|-------------|-----------------|---------------------|-------------------|
| 6K verses | Excellent | Good | FTS only |
| 100K verses | Excellent | Good | FTS + optional semantic |
| 1M+ verses | Good | Moderate | FTS + Redis + semantic |

## Infrastructure Requirements

### Minimal Setup (Recommended)
- PostgreSQL 13+ with pg_trgm and full-text search
- 512MB RAM for backend
- No additional services
- **Cost**: $0

### Enhanced Setup (Optional)
- PostgreSQL 13+ with pg_trgm, FTS, and pgvector
- 1GB RAM for backend + model
- sentence-transformers library
- **Cost**: $0

### Production Setup (Optional)
- PostgreSQL 13+ with extensions
- 2GB RAM for backend + model
- Redis for caching
- Load balancer for multiple instances
- **Cost**: ~$10-20/month (hosting)

## Migration Path

### Phase 1: Immediate (Zero Cost)
1. Add full-text search indexes
2. Implement FTS-based search
3. Remove OpenAI dependency from default config
4. Update documentation

**Result**: Fast, free search available immediately

### Phase 2: Optional Enhancement (Zero Cost)
1. Add sentence-transformers as optional dependency
2. Implement semantic search as opt-in feature
3. Add configuration flag: `ENABLE_SEMANTIC_SEARCH`

**Result**: Users can enable semantic search if desired

### Phase 3: Performance Optimization (Optional Cost)
1. Add Redis caching layer
2. Implement query optimization
3. Add monitoring and metrics

**Result**: Production-ready for high traffic

## Code Changes Required

### 1. Database Migration
```python
# alembic/versions/add_fulltext_search.py
def upgrade():
    # Add tsvector columns
    op.add_column('verses', sa.Column('text_simple_tsv', sa.TEXT))
    op.add_column('translations', sa.Column('text_tsv', sa.TEXT))
    
    # Create indexes
    op.execute("""
        CREATE INDEX verses_text_simple_tsv_idx 
        ON verses USING GIN(to_tsvector('simple', text_simple))
    """)
    
    op.execute("""
        CREATE INDEX translations_text_tsv_idx 
        ON translations USING GIN(to_tsvector('english', text))
    """)
```

### 2. Update search_utils.py
- Replace current fuzzy search with FTS
- Add optional semantic search
- Implement caching layer
- Add query optimization

### 3. Update requirements.txt
```txt
# Core requirements (no change)
fastapi==0.104.1
sqlalchemy==2.0.23
psycopg2-binary==2.9.9

# Optional for semantic search
sentence-transformers==2.2.2  # optional

# Optional for caching
redis==5.0.1  # optional
```

### 4. Update .env.example
```env
# Search Configuration
ENABLE_SEMANTIC_SEARCH=false
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2

# Cache Configuration (Optional)
ENABLE_CACHE=false
REDIS_HOST=localhost
REDIS_PORT=6379
```

## Testing Strategy

### Performance Tests
```python
def test_search_performance():
    """Benchmark search performance"""
    queries = [
        "patience",
        "what does quran say about charity",
        "mercy and forgiveness"
    ]
    
    for query in queries:
        # Test FTS
        start = time.time()
        fulltext_search(db, query)
        fts_time = time.time() - start
        
        # Test semantic (if enabled)
        start = time.time()
        semantic_search(db, query)
        semantic_time = time.time() - start
        
        print(f"{query}: FTS={fts_time:.3f}s, Semantic={semantic_time:.3f}s")
```

### Quality Tests
```python
def test_search_quality():
    """Compare search quality between methods"""
    test_cases = [
        ("patience", ["2:153", "2:155", "3:200"]),
        ("charity", ["2:110", "2:215", "2:271"]),
    ]
    
    for query, expected_verses in test_cases:
        results = fulltext_search(db, query, limit=10)
        found_verses = [f"{r.surah_number}:{r.verse_number}" for r in results]
        
        # Check if expected verses are in top results
        assert any(v in found_verses for v in expected_verses)
```

## Documentation Updates

1. **README.md**: Update search documentation
2. **API_DOCUMENTATION.md**: Document search parameters
3. **SETUP.md**: Add full-text search setup steps
4. **ARCHITECTURE.md**: Document search architecture

## Conclusion

**Recommended Approach**: Implement PostgreSQL Full-Text Search as the primary search method with optional sentence-transformers for semantic search.

**Benefits**:
- ✅ Zero cost for baseline functionality
- ✅ Excellent performance with proper indexes
- ✅ Scales to millions of verses
- ✅ No external API dependencies
- ✅ Optional enhancements available
- ✅ Production-ready

**Timeline**:
- Phase 1 (FTS): 1-2 days
- Phase 2 (Optional semantic): 1 day
- Phase 3 (Caching): 1 day

**Next Steps**:
1. Create database migration for FTS indexes
2. Update search_utils.py with FTS implementation
3. Test performance and quality
4. Update documentation
5. Deploy and monitor
