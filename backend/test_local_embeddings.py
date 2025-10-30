"""
Tests for local embedding backend (SBERT + FAISS)
Tests the new embedding service without requiring OpenAI API key
"""
import pytest
import os
import numpy as np
from unittest.mock import Mock, patch

# Set testing mode before imports
os.environ["TESTING"] = "true"

# Test if sentence-transformers is available
try:
    import sentence_transformers
    SBERT_AVAILABLE = True
except ImportError:
    SBERT_AVAILABLE = False

# Skip all tests if sentence-transformers not installed
pytestmark = pytest.mark.skipif(
    not SBERT_AVAILABLE,
    reason="sentence-transformers not installed"
)


def test_sbert_service_initialization():
    """Test EmbeddingServiceSBERT initialization"""
    from embeddings.sbert_faiss import EmbeddingServiceSBERT
    
    service = EmbeddingServiceSBERT()
    assert service is not None
    assert service.model is not None
    assert service.model_name == "paraphrase-multilingual-MiniLM-L12-v2"
    assert service.dimension == 384
    assert service.device == "cpu"


def test_sbert_custom_model():
    """Test EmbeddingServiceSBERT with custom model"""
    from embeddings.sbert_faiss import EmbeddingServiceSBERT
    
    # Use a smaller model for faster testing
    service = EmbeddingServiceSBERT(model_name="all-MiniLM-L6-v2")
    assert service.model_name == "all-MiniLM-L6-v2"
    assert service.dimension == 384


def test_generate_single_embedding():
    """Test single embedding generation"""
    from embeddings.sbert_faiss import EmbeddingServiceSBERT
    
    service = EmbeddingServiceSBERT()
    embedding = service.generate_embedding("In the name of Allah")
    
    assert embedding is not None
    assert isinstance(embedding, list)
    assert len(embedding) == 384
    assert all(isinstance(x, float) for x in embedding)


def test_generate_batch_embeddings():
    """Test batch embedding generation"""
    from embeddings.sbert_faiss import EmbeddingServiceSBERT
    
    service = EmbeddingServiceSBERT()
    texts = [
        "In the name of Allah",
        "All praise is due to Allah",
        "Lord of the Worlds"
    ]
    embeddings = service.generate_embeddings(texts)
    
    assert embeddings is not None
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape == (3, 384)
    assert embeddings.dtype == np.float32


def test_embeddings_are_normalized():
    """Test that embeddings are normalized to unit length"""
    from embeddings.sbert_faiss import EmbeddingServiceSBERT
    
    service = EmbeddingServiceSBERT()
    embeddings = service.generate_embeddings(["test text"])
    
    # Check that vectors are normalized (L2 norm should be ~1.0)
    norm = np.linalg.norm(embeddings[0])
    assert abs(norm - 1.0) < 0.001


def test_multilingual_support():
    """Test embedding generation for Arabic text"""
    from embeddings.sbert_faiss import EmbeddingServiceSBERT
    
    service = EmbeddingServiceSBERT()
    
    # Arabic text
    arabic_embedding = service.generate_embedding("بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ")
    
    # English translation
    english_embedding = service.generate_embedding("In the name of Allah, the Most Gracious, the Most Merciful")
    
    assert arabic_embedding is not None
    assert english_embedding is not None
    assert len(arabic_embedding) == 384
    assert len(english_embedding) == 384


def test_empty_text_handling():
    """Test handling of empty text"""
    from embeddings.sbert_faiss import EmbeddingServiceSBERT
    
    service = EmbeddingServiceSBERT()
    embeddings = service.generate_embeddings([])
    
    assert embeddings is not None
    assert embeddings.shape == (0, 384)


@pytest.mark.skipif(not SBERT_AVAILABLE, reason="faiss-cpu not installed")
def test_faiss_index_creation():
    """Test FAISS index creation"""
    try:
        import faiss
    except ImportError:
        pytest.skip("faiss-cpu not installed")
    
    from embeddings.sbert_faiss import EmbeddingServiceSBERT
    
    service = EmbeddingServiceSBERT()
    texts = ["text 1", "text 2", "text 3"]
    embeddings = service.generate_embeddings(texts)
    
    index = service.build_faiss_index(embeddings)
    
    assert index is not None
    assert index.ntotal == 3
    assert index.d == 384


@pytest.mark.skipif(not SBERT_AVAILABLE, reason="faiss-cpu not installed")
def test_faiss_search():
    """Test FAISS similarity search"""
    try:
        import faiss
    except ImportError:
        pytest.skip("faiss-cpu not installed")
    
    from embeddings.sbert_faiss import EmbeddingServiceSBERT
    
    service = EmbeddingServiceSBERT()
    
    # Create index with some verses
    texts = [
        "In the name of Allah, the Most Gracious, the Most Merciful",
        "All praise is due to Allah, Lord of the Worlds",
        "The Most Gracious, the Most Merciful"
    ]
    embeddings = service.generate_embeddings(texts)
    index = service.build_faiss_index(embeddings)
    
    # Search for similar verse
    query = "Praise be to Allah"
    query_embedding = service.generate_embeddings([query])[0]
    distances, indices = service.search(index, query_embedding, k=2)
    
    assert len(distances) == 2
    assert len(indices) == 2
    # First result should be the most similar
    assert distances[0] >= distances[1]  # Using inner product, higher is better


@pytest.mark.skipif(not SBERT_AVAILABLE, reason="faiss-cpu not installed")
def test_faiss_save_load():
    """Test FAISS index save and load"""
    try:
        import faiss
    except ImportError:
        pytest.skip("faiss-cpu not installed")
    
    import tempfile
    from embeddings.sbert_faiss import EmbeddingServiceSBERT
    
    service = EmbeddingServiceSBERT()
    
    # Create index
    embeddings = service.generate_embeddings(["test1", "test2"])
    index = service.build_faiss_index(embeddings)
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".faiss") as f:
        temp_path = f.name
    
    try:
        service.save_index(index, temp_path)
        
        # Load index
        loaded_index = service.load_index(temp_path)
        
        assert loaded_index is not None
        assert loaded_index.ntotal == index.ntotal
        assert loaded_index.d == index.d
    finally:
        os.unlink(temp_path)


def test_factory_get_sbert_backend():
    """Test factory function returns SBERT backend"""
    from embeddings import get_embedding_service
    
    # Force SBERT backend
    service = get_embedding_service(backend="sbert")
    
    assert service is not None
    assert hasattr(service, 'model_name')
    assert service.model_name == "paraphrase-multilingual-MiniLM-L12-v2"


def test_factory_auto_backend():
    """Test factory function auto-selects SBERT when available"""
    from embeddings import get_embedding_service
    
    # Auto should select SBERT since it's available
    service = get_embedding_service(backend="auto")
    
    assert service is not None
    # Should be SBERT since it's installed
    assert hasattr(service, 'model_name')


def test_factory_disabled_backend():
    """Test factory function with disabled backend"""
    from embeddings import get_embedding_service
    
    service = get_embedding_service(backend="disabled")
    
    assert service is None


def test_unified_service_with_sbert():
    """Test UnifiedEmbeddingService with SBERT backend"""
    from embeddings.unified_service import UnifiedEmbeddingService
    
    service = UnifiedEmbeddingService(backend="sbert")
    
    assert service is not None
    assert service.client is not None
    assert service.model == "paraphrase-multilingual-MiniLM-L12-v2"
    assert service.dimension == 384


def test_unified_service_generate_embedding():
    """Test UnifiedEmbeddingService embedding generation"""
    from embeddings.unified_service import UnifiedEmbeddingService
    
    service = UnifiedEmbeddingService(backend="sbert")
    embedding = service.generate_embedding("test text")
    
    assert embedding is not None
    assert len(embedding) == 384


def test_unified_service_batch_embeddings():
    """Test UnifiedEmbeddingService batch embedding generation"""
    from embeddings.unified_service import UnifiedEmbeddingService
    
    service = UnifiedEmbeddingService(backend="sbert")
    texts = ["text1", "text2", "text3"]
    embeddings = service.generate_embeddings_batch(texts)
    
    assert embeddings is not None
    assert len(embeddings) == 3
    assert all(len(emb) == 384 for emb in embeddings)


def test_embedding_dimension_lookup():
    """Test get_embedding_dimension function"""
    from embeddings import get_embedding_dimension
    
    # Should return 384 for default SBERT model
    dimension = get_embedding_dimension(backend="sbert")
    assert dimension == 384
