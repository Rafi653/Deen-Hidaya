# Free Embedding Alternatives for Semantic Search

## Problem Statement
OpenAI embeddings API is not free and incurs costs (~$0.03 for all Quran verses). We need a free, self-hosted alternative for generating embeddings for semantic search functionality.

## Recommended Solution: Sentence-Transformers

### Overview
**Sentence-Transformers** is an open-source Python library that provides state-of-the-art text embeddings using pre-trained transformer models. It's completely free and can run locally without any API costs.

### Key Benefits
1. **Zero Cost**: Completely free, no API charges
2. **Privacy**: Data never leaves your server
3. **No Rate Limits**: Process as much data as you need
4. **Fast**: Optimized for efficient inference
5. **Quality**: Comparable or better than OpenAI Ada-002 for many tasks
6. **Multilingual**: Supports Arabic, English, and 100+ languages

### Recommended Models

#### 1. all-MiniLM-L6-v2 (Recommended for Most Use Cases)
- **Size**: 80MB
- **Dimensions**: 384
- **Speed**: Very fast (~2000 sentences/sec on CPU)
- **Quality**: Excellent for general semantic search
- **Languages**: English primarily, decent for other languages
- **Use Case**: Best balance of speed, size, and quality

#### 2. paraphrase-multilingual-MiniLM-L12-v2 (For Multilingual Support)
- **Size**: 118MB
- **Dimensions**: 384
- **Speed**: Fast (~1000 sentences/sec on CPU)
- **Quality**: Excellent for 50+ languages including Arabic
- **Languages**: Multilingual (Arabic, English, Telugu, etc.)
- **Use Case**: Best for Quran translations in multiple languages

#### 3. all-mpnet-base-v2 (For Maximum Quality)
- **Size**: 420MB
- **Dimensions**: 768
- **Speed**: Moderate (~400 sentences/sec on CPU)
- **Quality**: State-of-the-art performance
- **Languages**: English primarily
- **Use Case**: When quality is more important than speed

### Implementation

#### Installation
```bash
pip install sentence-transformers
```

#### Basic Usage
```python
from sentence_transformers import SentenceTransformer

# Load model (downloads automatically on first use)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings
text = "And He is with you wherever you are"
embedding = model.encode(text)

# Batch processing
texts = ["verse 1", "verse 2", "verse 3"]
embeddings = model.encode(texts, batch_size=32)
```

### Architecture Decision

For Deen Hidaya, we recommend a **hybrid approach**:

1. **Primary Search**: PostgreSQL Full-Text Search with GIN indexes
   - Fast exact and fuzzy matching
   - No ML model needed
   - Low resource usage
   - Always available

2. **Enhanced Search**: Optional Sentence-Transformers embeddings
   - Enable with `ENABLE_SEMANTIC_SEARCH=true`
   - Use `paraphrase-multilingual-MiniLM-L12-v2` for multilingual support
   - Fallback to full-text search if disabled
   - Better conceptual understanding

### Performance Comparison

| Method | Speed | Quality | Cost | Resource Usage |
|--------|-------|---------|------|----------------|
| OpenAI Ada-002 | Fast (API) | Excellent | $0.0001/1K tokens | Low (API call) |
| Sentence-Transformers (MiniLM) | Very Fast | Excellent | Free | Low (80MB RAM) |
| Sentence-Transformers (MPNet) | Moderate | Outstanding | Free | Medium (420MB RAM) |
| PostgreSQL FTS | Very Fast | Good | Free | Very Low |

### Cost Comparison (6,236 Quran verses)

| Solution | Initial Cost | Monthly Cost | Total Year 1 |
|----------|--------------|--------------|---------------|
| OpenAI Ada-002 | ~$0.03 | ~$0.10 (queries) | ~$1.23 |
| Sentence-Transformers | $0 | $0 | $0 |
| PostgreSQL FTS | $0 | $0 | $0 |

### Storage Comparison

| Solution | Embedding Dimensions | Storage per Verse | Total Storage (6,236 verses) |
|----------|---------------------|-------------------|------------------------------|
| OpenAI Ada-002 | 1536 | ~6KB | ~37MB |
| MiniLM-L6-v2 | 384 | ~1.5KB | ~9MB |
| MPNet-base-v2 | 768 | ~3KB | ~18MB |
| PostgreSQL FTS | N/A | ~500 bytes | ~3MB |

## Alternative Solutions Considered

### 1. Cohere Free Tier
- **Pros**: Free tier available, good quality
- **Cons**: Rate limited, requires API key, privacy concerns
- **Verdict**: Not recommended (still depends on external API)

### 2. Ollama with Local LLMs
- **Pros**: Completely local, very powerful
- **Cons**: Large models (>1GB), slow on CPU, overkill for embeddings
- **Verdict**: Too heavy for this use case

### 3. FAISS + Pre-computed Embeddings
- **Pros**: Very fast similarity search
- **Cons**: Still needs embedding generation, complex setup
- **Verdict**: Could be future optimization, but sentence-transformers already fast

### 4. PostgreSQL Full-Text Search Only
- **Pros**: Fast, built-in, no ML needed
- **Cons**: Keyword-based, no semantic understanding
- **Verdict**: Good baseline, recommended as primary search

## Recommended Implementation Plan

### Phase 1: Improve PostgreSQL Full-Text Search (High Priority)
1. Add GIN indexes for fast text search
2. Implement tsquery for better relevance ranking
3. Support Arabic text search with proper language configuration
4. Add BM25-style scoring

**Result**: Fast, reliable search without ML dependencies

### Phase 2: Add Optional Semantic Search (Medium Priority)
1. Add `sentence-transformers` as optional dependency
2. Use `paraphrase-multilingual-MiniLM-L12-v2` model
3. Generate embeddings on-demand or during ingestion
4. Store embeddings in pgvector (already configured)
5. Make it opt-in via environment variable

**Result**: Enhanced search for users who want semantic capabilities

### Phase 3: Hybrid Search (Low Priority)
1. Combine FTS and semantic search results
2. Weighted scoring system
3. Re-ranking based on user feedback

**Result**: Best of both worlds

## Code Changes Required

### 1. Update requirements.txt
```txt
# Optional: for semantic search
sentence-transformers==2.2.2  # ~300MB download
```

### 2. Update .env.example
```env
# Semantic Search (Optional)
ENABLE_SEMANTIC_SEARCH=false
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
EMBEDDING_DIMENSION=384
```

### 3. Update embedding_service.py
Add support for multiple backends:
- OpenAI (legacy, requires API key)
- Sentence-Transformers (free, local)
- Disabled (falls back to FTS)

### 4. Update search_utils.py
Improve PostgreSQL full-text search as primary method

## Testing Strategy

1. **Unit Tests**: Test each embedding backend independently
2. **Performance Tests**: Benchmark search speed with 6,236 verses
3. **Quality Tests**: Compare search relevance between methods
4. **Integration Tests**: Ensure fallback works correctly

## Migration Guide

### For Existing Installations with OpenAI Embeddings
```bash
# Option 1: Keep using OpenAI (if you have API key)
# No changes needed

# Option 2: Switch to free sentence-transformers
pip install sentence-transformers
export EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
export EMBEDDING_DIMENSION=384
python fix_embeddings.py --regenerate

# Option 3: Disable semantic search (use FTS only)
export ENABLE_SEMANTIC_SEARCH=false
```

### For New Installations
```bash
# Recommended: Use PostgreSQL FTS only (no setup needed)
# Works out of the box, no API keys, no ML models

# Optional: Enable semantic search later
pip install sentence-transformers
export ENABLE_SEMANTIC_SEARCH=true
python fix_embeddings.py
```

## Conclusion

**Recommendation**: Implement PostgreSQL Full-Text Search as the primary search mechanism, with optional sentence-transformers support for users who want semantic search capabilities.

**Benefits**:
- ✅ Zero cost
- ✅ No API dependencies
- ✅ Privacy-friendly
- ✅ Fast performance
- ✅ Scalable
- ✅ Works offline
- ✅ Multilingual support

**Next Steps**:
1. Enhance PostgreSQL FTS implementation
2. Add sentence-transformers as optional feature
3. Update documentation
4. Add configuration examples
