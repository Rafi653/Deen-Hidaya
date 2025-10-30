# Local Embedding Backend Setup Guide

This guide explains how to set up and use the **free, local embedding backend** for Deen Hidaya's semantic search functionality, powered by Sentence-Transformers and FAISS. No API keys required!

## Overview

Deen Hidaya now supports **three embedding backends**:

1. **SBERT (Sentence-Transformers)** - *Recommended* - Free, local, no API keys
2. **OpenAI** - Requires API key and costs money per embedding
3. **Disabled** - No semantic search, falls back to text search only

## Quick Start (Local/Free Backend)

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- `sentence-transformers>=2.2` - For local embedding generation
- `faiss-cpu==1.7.4` - For fast similarity search
- `torch>=2.0.0` - PyTorch (required by sentence-transformers)

### 2. Configure Environment

The local backend works **out of the box** with zero configuration! But you can customize:

```bash
# Optional: Explicitly set backend (default is "auto")
EMBEDDING_BACKEND=sbert

# Optional: Choose a different model (default is paraphrase-multilingual-MiniLM-L12-v2)
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2

# Optional: Use GPU if available (default is "cpu")
EMBEDDING_DEVICE=cpu
```

Add these to your `.env` file or export them in your shell.

### 3. Generate Embeddings

```bash
cd backend
python fix_embeddings.py --language en
```

The script will automatically:
- Detect that sentence-transformers is installed
- Use the local SBERT backend
- Download the model on first run (~118MB)
- Generate embeddings for all verses

### 4. Test the Demo

Run the demo script to see the local backend in action:

```bash
python scripts/demo_embeddings.py
```

This demonstrates:
- Embedding generation
- FAISS index creation
- Similarity search
- Multilingual support (Arabic + English)
- Performance benchmarks

## Backend Selection

The embedding service automatically selects the best available backend:

### Auto Mode (Default)
```bash
EMBEDDING_BACKEND=auto  # or omit this line
```

Selection priority:
1. If `sentence-transformers` is installed → Use SBERT (local)
2. Else if `OPENAI_API_KEY` is set → Use OpenAI
3. Else → Disabled (no semantic search)

### Force SBERT
```bash
EMBEDDING_BACKEND=sbert
```

Requires: `sentence-transformers` installed

### Force OpenAI
```bash
EMBEDDING_BACKEND=openai
OPENAI_API_KEY=sk-...
```

Requires: `OPENAI_API_KEY` environment variable

### Disable Semantic Search
```bash
EMBEDDING_BACKEND=disabled
```

API will still work but semantic search endpoints will return errors.

## Model Selection

The default model is `paraphrase-multilingual-MiniLM-L12-v2`:
- **Size**: 118MB
- **Dimension**: 384
- **Languages**: 50+ including Arabic and English
- **Speed**: ~500 embeddings/second on CPU

### Alternative Models

You can use any model from [Sentence-Transformers](https://www.sbert.net/docs/pretrained_models.html):

```bash
# Smaller, faster (50MB, 384-dim)
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Larger, more accurate (420MB, 768-dim)
EMBEDDING_MODEL=all-mpnet-base-v2

# Multilingual (supports 100+ languages)
EMBEDDING_MODEL=paraphrase-multilingual-mpnet-base-v2
```

⚠️ **Note**: Changing models requires regenerating all embeddings.

## Usage in Code

### Using the Factory Function

```python
from embeddings import get_embedding_service

# Auto-select best backend
service = get_embedding_service(backend="auto")

# Generate single embedding
embedding = service.generate_embedding("In the name of Allah")

# Generate batch embeddings
embeddings = service.generate_embeddings([
    "Verse 1 text",
    "Verse 2 text",
    "Verse 3 text"
])
```

### Using Unified Service Directly

```python
from embeddings.unified_service import UnifiedEmbeddingService

# Initialize with specific backend
service = UnifiedEmbeddingService(backend="sbert")

# Check if backend is available
if not service.client:
    print("No embedding backend available")
else:
    print(f"Using model: {service.model}")
    print(f"Dimension: {service.dimension}")
```

### Using SBERT Directly

```python
from embeddings.sbert_faiss import EmbeddingServiceSBERT
import numpy as np

# Initialize
service = EmbeddingServiceSBERT(
    model_name="paraphrase-multilingual-MiniLM-L12-v2",
    device="cpu"
)

# Generate embeddings
texts = ["Text 1", "Text 2", "Text 3"]
embeddings = service.generate_embeddings(texts)

# Build FAISS index
index = service.build_faiss_index(embeddings)

# Search
query_embedding = service.generate_embeddings(["search query"])[0]
distances, indices = service.search(index, query_embedding, k=5)

# Save/load index
service.save_index(index, "my_index.faiss")
loaded_index = service.load_index("my_index.faiss")
```

## API Usage

The API endpoints work the same regardless of backend:

### Generate Embeddings (Admin)

```bash
curl -X POST http://localhost:8000/admin/embed/verse \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "language": "en",
    "verse_ids": null
  }'
```

### Semantic Search

```bash
curl "http://localhost:8000/api/v1/search?q=mercy&type=semantic&language=en"
```

## Migration from OpenAI

If you were using OpenAI embeddings:

### Option 1: Switch to SBERT (Recommended)

```bash
# 1. Install new dependencies
pip install sentence-transformers faiss-cpu

# 2. Set backend to SBERT
export EMBEDDING_BACKEND=sbert

# 3. Regenerate embeddings with local model
python fix_embeddings.py --language en
```

⚠️ **Important**: SBERT embeddings have different dimensions (384 vs 1536), so you must regenerate all embeddings. The old OpenAI embeddings will be replaced.

### Option 2: Keep Using OpenAI

```bash
# Explicitly set backend to OpenAI
export EMBEDDING_BACKEND=openai
export OPENAI_API_KEY=sk-...
```

Your existing embeddings will continue to work.

## CI/CD Configuration

### GitHub Actions

No special configuration needed! The local backend works in CI without API keys:

```yaml
- name: Install dependencies
  run: |
    cd backend
    pip install -r requirements.txt

- name: Run tests
  run: |
    cd backend
    export EMBEDDING_BACKEND=sbert  # Optional: force SBERT
    pytest
```

### Docker

```dockerfile
# Install dependencies
RUN pip install -r requirements.txt

# The model will be downloaded on first run
# Optional: Pre-download model in build
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"

# Set backend (optional, auto is default)
ENV EMBEDDING_BACKEND=sbert
```

## Performance

### SBERT vs OpenAI

| Metric | SBERT (Local) | OpenAI (API) |
|--------|--------------|--------------|
| Cost | Free | ~$0.0001/embedding |
| Speed | ~500/sec (CPU) | ~2000/sec (API) |
| Network | Offline | Online required |
| Privacy | Local only | Sent to OpenAI |
| Dimension | 384 | 1536 |
| Languages | 50+ | 100+ |

### Optimization Tips

1. **Use GPU if available**: `EMBEDDING_DEVICE=cuda`
2. **Batch processing**: Always use `generate_embeddings()` for multiple texts
3. **Cache model**: The model is loaded once and reused
4. **Use smaller models**: For speed, try `all-MiniLM-L6-v2`

## Troubleshooting

### "sentence-transformers not installed"

```bash
pip install sentence-transformers
```

### "faiss not installed"

```bash
pip install faiss-cpu
```

For GPU support:
```bash
pip install faiss-gpu
```

### Model download fails

The model downloads from HuggingFace on first use. If it fails:

```bash
# Set cache directory
export TRANSFORMERS_CACHE=/path/to/cache

# Or pre-download manually
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"
```

### Out of memory

Use a smaller model or increase batch size:

```bash
# Use smaller model
export EMBEDDING_MODEL=all-MiniLM-L6-v2

# Or reduce batch size in code
service.batch_size = 50  # default is 100
```

### Embeddings not working

Check backend status:

```bash
cd backend
python fix_embeddings.py --check-only
```

This shows which backends are available and will be used.

## License and Privacy

### SBERT (Local Backend)
- **License**: Apache 2.0
- **Privacy**: All data stays local, never sent to external services
- **Models**: Various licenses, check model card on HuggingFace

### OpenAI Backend
- **License**: Proprietary (OpenAI terms)
- **Privacy**: Text is sent to OpenAI servers
- **Data retention**: Per OpenAI's data policy

## Support

For issues or questions:
1. Check the demo script: `python scripts/demo_embeddings.py`
2. Check backend status: `python fix_embeddings.py --check-only`
3. Review logs for error messages
4. Open an issue on GitHub

## References

- [Sentence-Transformers Documentation](https://www.sbert.net/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [Available Models](https://www.sbert.net/docs/pretrained_models.html)
- [HuggingFace Model Hub](https://huggingface.co/models?library=sentence-transformers)
