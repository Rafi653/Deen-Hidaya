"""
Integration tests for embedding generation and semantic search
These tests verify the embedding functionality when OpenAI API key is available
"""
import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set testing mode before imports
os.environ["TESTING"] = "true"

from database import Base, get_db
from main import app
from models import Surah, Verse, Translation, Embedding
from embedding_service import EmbeddingService

# Create test database
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Add test data
    surah = Surah(
        id=1,
        number=1,
        name_arabic="الفاتحة",
        name_english="Al-Fatihah",
        name_transliteration="Al-Faatiha",
        revelation_place="Meccan",
        total_verses=7
    )
    db.add(surah)
    
    verse = Verse(
        id=1,
        surah_id=1,
        verse_number=1,
        text_arabic="بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ",
        text_simple="بسم الله الرحمن الرحيم",
        text_transliteration="Bismi Allahi alrrahmani alrraheemi"
    )
    db.add(verse)
    
    translation = Translation(
        id=1,
        verse_id=1,
        language="en",
        translator="Sahih International",
        text="In the name of Allah, the Entirely Merciful, the Especially Merciful.",
        license="Public Domain",
        source="quran.com"
    )
    db.add(translation)
    
    db.commit()
    
    yield db
    
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_embedding_service_initialization():
    """Test EmbeddingService initialization"""
    service = EmbeddingService()
    assert service is not None
    assert service.model == "text-embedding-ada-002"
    assert service.dimension == 1536
    assert service.batch_size == 100


def test_embedding_service_without_api_key():
    """Test EmbeddingService behavior without API key"""
    # Clear API key
    original_key = os.environ.get("OPENAI_API_KEY")
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
    
    service = EmbeddingService()
    assert service.client is None
    
    # Test that generate_embedding returns None without API key
    result = service.generate_embedding("test text")
    assert result is None
    
    # Restore original key
    if original_key:
        os.environ["OPENAI_API_KEY"] = original_key


@patch("embedding_service.OpenAI")
def test_generate_embedding_success(mock_openai, db_session):
    """Test successful embedding generation"""
    # Mock OpenAI client
    mock_client = Mock()
    mock_response = Mock()
    mock_response.data = [Mock(embedding=[0.1] * 1536)]
    mock_client.embeddings.create.return_value = mock_response
    mock_openai.return_value = mock_client
    
    # Set mock API key
    os.environ["OPENAI_API_KEY"] = "test-key"
    
    service = EmbeddingService()
    embedding = service.generate_embedding("test text")
    
    assert embedding is not None
    assert len(embedding) == 1536
    assert all(isinstance(x, float) for x in embedding)


@patch("embedding_service.OpenAI")
def test_generate_embeddings_batch(mock_openai):
    """Test batch embedding generation"""
    # Mock OpenAI client
    mock_client = Mock()
    mock_response = Mock()
    mock_response.data = [
        Mock(index=0, embedding=[0.1] * 1536),
        Mock(index=1, embedding=[0.2] * 1536),
        Mock(index=2, embedding=[0.3] * 1536)
    ]
    mock_client.embeddings.create.return_value = mock_response
    mock_openai.return_value = mock_client
    
    os.environ["OPENAI_API_KEY"] = "test-key"
    
    service = EmbeddingService()
    texts = ["text1", "text2", "text3"]
    embeddings = service.generate_embeddings_batch(texts)
    
    assert len(embeddings) == 3
    assert all(len(emb) == 1536 for emb in embeddings)


@patch("embedding_service.OpenAI")
def test_create_verse_embedding(mock_openai, db_session):
    """Test creating embedding for a single verse"""
    # Mock OpenAI client
    mock_client = Mock()
    mock_response = Mock()
    mock_response.data = [Mock(embedding=[0.1] * 1536)]
    mock_client.embeddings.create.return_value = mock_response
    mock_openai.return_value = mock_client
    
    os.environ["OPENAI_API_KEY"] = "test-key"
    
    service = EmbeddingService()
    verse = db_session.query(Verse).first()
    
    result = service.create_verse_embedding(verse, language="en", db=db_session)
    
    assert result is not None
    assert isinstance(result, Embedding)
    assert result.verse_id == verse.id
    assert result.language == "en"
    assert result.dimension == 1536
    
    # Verify it was saved to database
    saved_embedding = db_session.query(Embedding).filter_by(verse_id=verse.id).first()
    assert saved_embedding is not None


@patch("embedding_service.OpenAI")
def test_create_embeddings_batch_api(mock_openai, db_session):
    """Test batch embedding creation via API"""
    # Mock OpenAI client
    mock_client = Mock()
    mock_response = Mock()
    mock_response.data = [Mock(index=0, embedding=[0.1] * 1536)]
    mock_client.embeddings.create.return_value = mock_response
    mock_openai.return_value = mock_client
    
    os.environ["OPENAI_API_KEY"] = "test-key"
    
    headers = {"Authorization": "Bearer dev_admin_token_change_in_production"}
    response = client.post(
        "/api/v1/admin/embed/verse",
        json={"verse_ids": [1], "language": "en"},
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["success", "partial_success"]
    assert data["verses_embedded"] >= 0


def test_get_verse_text_for_embedding(db_session):
    """Test getting verse text for different languages"""
    service = EmbeddingService()
    verse = db_session.query(Verse).first()
    
    # Test Arabic text
    arabic_text = service.get_verse_text_for_embedding(verse, language="ar", db=db_session)
    assert arabic_text == verse.text_arabic
    
    # Test English translation
    english_text = service.get_verse_text_for_embedding(verse, language="en", db=db_session)
    assert english_text is not None
    assert "Allah" in english_text or "God" in english_text


@patch("search_utils.get_embedding_service")
def test_semantic_search_fallback_without_api_key(mock_get_service, db_session):
    """Test semantic search falls back to fuzzy search without API key"""
    # Mock embedding service without client
    mock_service = Mock()
    mock_service.client = None
    mock_get_service.return_value = mock_service
    
    response = client.get("/api/v1/search?q=mercy&search_type=semantic&lang=en")
    
    assert response.status_code == 200
    # Should fall back to fuzzy/exact search


@patch("search_utils.get_embedding_service")
@patch("embedding_service.OpenAI")
def test_semantic_search_with_embeddings(mock_openai, mock_get_service, db_session):
    """Test semantic search with embeddings"""
    # Mock OpenAI client
    mock_client = Mock()
    mock_response = Mock()
    mock_response.data = [Mock(embedding=[0.1] * 1536)]
    mock_client.embeddings.create.return_value = mock_response
    
    # Mock embedding service
    mock_service = Mock()
    mock_service.client = mock_client
    mock_service.model = "text-embedding-ada-002"
    mock_service.generate_embedding.return_value = [0.1] * 1536
    mock_get_service.return_value = mock_service
    
    os.environ["OPENAI_API_KEY"] = "test-key"
    
    # Note: Actual semantic search requires pgvector which isn't available in SQLite
    # This test verifies the endpoint doesn't crash
    response = client.get("/api/v1/search?q=mercy&search_type=semantic&lang=en")
    
    assert response.status_code == 200


def test_hybrid_search_includes_semantic():
    """Test hybrid search attempts to include semantic results"""
    response = client.get("/api/v1/search?q=mercy&search_type=hybrid&lang=en")
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data


@patch("embedding_service.OpenAI")
def test_update_existing_embedding(mock_openai, db_session):
    """Test updating an existing embedding"""
    # Mock OpenAI client
    mock_client = Mock()
    mock_response = Mock()
    mock_response.data = [Mock(embedding=[0.1] * 1536)]
    mock_client.embeddings.create.return_value = mock_response
    mock_openai.return_value = mock_client
    
    os.environ["OPENAI_API_KEY"] = "test-key"
    
    service = EmbeddingService()
    verse = db_session.query(Verse).first()
    
    # Create initial embedding
    result1 = service.create_verse_embedding(verse, language="en", db=db_session)
    embedding_id = result1.id
    
    # Update with new embedding
    mock_response.data = [Mock(embedding=[0.2] * 1536)]
    result2 = service.create_verse_embedding(verse, language="en", db=db_session)
    
    # Should update the same record
    assert result2.id == embedding_id
    
    # Verify only one embedding exists
    count = db_session.query(Embedding).filter_by(verse_id=verse.id, language="en").count()
    assert count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
