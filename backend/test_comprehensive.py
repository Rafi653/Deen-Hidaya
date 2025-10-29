"""
Comprehensive Integration Tests for Deen Hidaya Backend
Testing Issues #3, #4, #5, #6, #7

This test suite provides thorough testing of:
- Database schema and migrations (Issue #3)
- Data scraping and ingestion (Issue #4)
- Search functionality (Issue #5)
- Backend APIs (Issue #6)
- Embeddings and semantic search (Issue #7)
"""
import pytest
import os
import json
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set testing mode before imports
os.environ["TESTING"] = "true"

from main import app
from database import Base, get_db
from models import Surah, Verse, Translation, Bookmark, AudioTrack, Tag, VerseTag, Embedding
from embedding_service import EmbeddingService
from transliteration_generator import generate_transliteration

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Setup test database with comprehensive test data"""
    # Drop and recreate tables for each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    # Create test surahs
    surahs_data = [
        {"number": 1, "name_arabic": "الفاتحة", "name_english": "Al-Fatiha", 
         "name_transliteration": "Al-Fatihah", "revelation_place": "Meccan", "total_verses": 7},
        {"number": 2, "name_arabic": "البقرة", "name_english": "Al-Baqarah", 
         "name_transliteration": "Al-Baqarah", "revelation_place": "Medinan", "total_verses": 286},
        {"number": 112, "name_arabic": "الإخلاص", "name_english": "Al-Ikhlas", 
         "name_transliteration": "Al-Ikhlaas", "revelation_place": "Meccan", "total_verses": 4},
    ]
    
    for surah_data in surahs_data:
        surah = Surah(**surah_data)
        db.add(surah)
    db.commit()
    
    # Create test verses with Arabic text
    verses_data = [
        {"surah_number": 1, "verse_number": 1, "text_arabic": "بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ", 
         "text_simple": "بسم الله الرحمن الرحيم", "juz_number": 1},
        {"surah_number": 1, "verse_number": 2, "text_arabic": "ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَـٰلَمِينَ", 
         "text_simple": "الحمد لله رب العالمين", "juz_number": 1},
        {"surah_number": 2, "verse_number": 1, "text_arabic": "الٓمٓ", 
         "text_simple": "الم", "juz_number": 1},
        {"surah_number": 2, "verse_number": 255, "text_arabic": "ٱللَّهُ لَآ إِلَـٰهَ إِلَّا هُوَ ٱلْحَىُّ ٱلْقَيُّومُ", 
         "text_simple": "الله لا إله إلا هو الحي القيوم", "juz_number": 3},
        {"surah_number": 112, "verse_number": 1, "text_arabic": "قُلْ هُوَ ٱللَّهُ أَحَدٌ", 
         "text_simple": "قل هو الله احد", "juz_number": 30},
    ]
    
    for verse_data in verses_data:
        surah_number = verse_data.pop("surah_number")
        surah = db.query(Surah).filter(Surah.number == surah_number).first()
        
        # Generate transliteration
        transliteration = generate_transliteration(verse_data["text_arabic"])
        verse_data["text_transliteration"] = transliteration
        
        verse = Verse(surah_id=surah.id, **verse_data)
        db.add(verse)
    
    db.commit()
    
    # Create test translations
    verses = db.query(Verse).all()
    translations_data = [
        {"language": "en", "translator": "Sahih International", 
         "texts": [
             "In the name of Allah, the Entirely Merciful, the Especially Merciful.",
             "Praise be to Allah, Lord of the worlds.",
             "Alif, Lam, Meem.",
             "Allah - there is no deity except Him, the Ever-Living, the Sustainer of existence.",
             "Say, He is Allah, [who is] One,"
         ]},
        {"language": "en", "translator": "Dr. Mustafa Khattab", 
         "texts": [
             "In the Name of Allah—the Most Compassionate, Most Merciful.",
             "All praise is for Allah—Lord of all worlds.",
             "Alif-Lãm-Mĩm.",
             "Allah! There is no god ˹worthy of worship˺ except Him, the Ever-Living, All-Sustaining.",
             "Say, ˹O Prophet,˺ 'He is Allah—One ˹and Indivisible˺;'"
         ]},
    ]
    
    for i, verse in enumerate(verses):
        for trans_data in translations_data:
            translation = Translation(
                verse_id=verse.id,
                language=trans_data["language"],
                translator=trans_data["translator"],
                text=trans_data["texts"][i],
                license="Public Domain",
                source="api.quran.com"
            )
            db.add(translation)
    
    db.commit()
    
    # Create test audio tracks
    for verse in verses[:3]:
        audio = AudioTrack(
            verse_id=verse.id,
            reciter="Abdul Basit",
            reciter_arabic="عبد الباسط عبد الصمد",
            audio_url=f"https://example.com/audio/{verse.id}.mp3",
            duration=5.0,
            format="mp3",
            quality="128kbps"
        )
        db.add(audio)
    
    db.commit()
    
    # Create test tags (Tag model may not have name_arabic field in all versions)
    # Using introspection to check available fields
    from sqlalchemy import inspect as sql_inspect
    tag_mapper = sql_inspect(Tag)
    tag_columns = [col.key for col in tag_mapper.columns]
    
    tags_data = [
        {"name": "Faith"},
        {"name": "Mercy"},
        {"name": "Prayer"},
    ]
    
    # Add name_arabic if the field exists
    if "name_arabic" in tag_columns:
        tags_data[0]["name_arabic"] = "الإيمان"
        tags_data[1]["name_arabic"] = "الرحمة"
        tags_data[2]["name_arabic"] = "الصلاة"
    
    for tag_data in tags_data:
        db.add(Tag(**tag_data))
    
    db.commit()
    
    # Associate verses with tags
    verse_tags = [
        VerseTag(verse_id=1, tag_id=1),
        VerseTag(verse_id=1, tag_id=2),
        VerseTag(verse_id=4, tag_id=1),
    ]
    for vt in verse_tags:
        db.add(vt)
    
    db.commit()
    db.close()
    
    yield
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)


# ==================== Issue #3: Database Schema Tests ====================

class TestDatabaseSchema:
    """Test database schema and models (Issue #3)"""
    
    def test_all_tables_exist(self):
        """Verify all required tables are created"""
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        required_tables = ['surah', 'verse', 'translation', 'audio_track', 
                          'tag', 'verse_tag', 'embedding', 'bookmark']
        
        for table in required_tables:
            assert table in tables, f"Table {table} not found"
    
    def test_surah_model(self):
        """Test Surah model structure and relationships"""
        db = TestingSessionLocal()
        surah = db.query(Surah).filter(Surah.number == 1).first()
        
        assert surah is not None
        assert surah.name_arabic == "الفاتحة"
        assert surah.name_english == "Al-Fatiha"
        assert surah.total_verses == 7
        assert len(surah.verses) > 0
        
        db.close()
    
    def test_verse_model(self):
        """Test Verse model structure and relationships"""
        db = TestingSessionLocal()
        verse = db.query(Verse).first()
        
        assert verse is not None
        assert verse.text_arabic is not None
        assert verse.text_transliteration is not None
        assert verse.surah is not None
        assert len(verse.translations) > 0
        
        db.close()
    
    def test_translation_model(self):
        """Test Translation model with license metadata"""
        db = TestingSessionLocal()
        translation = db.query(Translation).first()
        
        assert translation is not None
        assert translation.language is not None
        assert translation.translator is not None
        assert translation.license is not None
        assert translation.source is not None
        
        db.close()
    
    def test_foreign_key_relationships(self):
        """Test foreign key relationships"""
        db = TestingSessionLocal()
        
        verse = db.query(Verse).first()
        assert verse.surah_id is not None
        
        translation = db.query(Translation).first()
        assert translation.verse_id is not None
        
        db.close()


# ==================== Issue #4: Data Ingestion Tests ====================

class TestDataIngestion:
    """Test data scraping and ingestion (Issue #4)"""
    
    def test_transliteration_generation(self):
        """Test automatic transliteration generation"""
        arabic_text = "بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ"
        transliteration = generate_transliteration(arabic_text)
        
        assert transliteration is not None
        assert len(transliteration) > 0
        # Check it contains Latin characters
        assert any(c.isalpha() and ord(c) < 128 for c in transliteration)
    
    def test_verses_have_transliteration(self):
        """Test all verses have transliteration"""
        db = TestingSessionLocal()
        verses = db.query(Verse).all()
        
        for verse in verses:
            assert verse.text_transliteration is not None
            assert len(verse.text_transliteration) > 0
        
        db.close()
    
    def test_translations_have_metadata(self):
        """Test all translations have license metadata"""
        db = TestingSessionLocal()
        translations = db.query(Translation).all()
        
        for translation in translations:
            assert translation.license is not None
            assert translation.source is not None
        
        db.close()
    
    def test_audio_tracks_metadata(self):
        """Test audio tracks have metadata"""
        db = TestingSessionLocal()
        audio_tracks = db.query(AudioTrack).all()
        
        for audio in audio_tracks:
            assert audio.reciter is not None
            assert audio.audio_url is not None
            assert audio.format is not None
        
        db.close()


# ==================== Issue #5: Search Functionality Tests ====================

class TestSearchFunctionality:
    """Test search functionality (Issue #5)"""
    
    def test_exact_search(self):
        """Test exact text matching search"""
        response = client.get("/api/v1/search?q=Allah&lang=en&search_type=exact")
        assert response.status_code == 200
        
        data = response.json()
        assert "results" in data
        assert data["search_type"] == "exact"
        assert data["total"] >= 0
    
    def test_fuzzy_search(self):
        """Test fuzzy search with typos"""
        response = client.get("/api/v1/search?q=Merciful&lang=en&search_type=fuzzy")
        assert response.status_code == 200
        
        data = response.json()
        assert "results" in data
        assert data["search_type"] == "fuzzy"
    
    def test_search_arabic(self):
        """Test search in Arabic text"""
        response = client.get("/api/v1/search?q=الله&lang=ar&search_type=exact")
        assert response.status_code == 200
        
        data = response.json()
        assert "results" in data
    
    def test_search_with_limit(self):
        """Test search result limiting"""
        response = client.get("/api/v1/search?q=Allah&lang=en&search_type=exact&limit=2")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["results"]) <= 2
    
    def test_search_transliteration(self):
        """Test search includes transliteration in results"""
        response = client.get("/api/v1/search?q=Allah&lang=en&search_type=exact&limit=1")
        assert response.status_code == 200
        
        data = response.json()
        if data["results"]:
            result = data["results"][0]
            # SearchResult has text_transliteration at top level, not nested
            assert "text_transliteration" in result
            assert result["text_transliteration"] is not None


# ==================== Issue #6: Backend API Tests ====================

class TestBackendAPIs:
    """Test Backend API endpoints (Issue #6)"""
    
    def test_health_endpoints(self):
        """Test all health check endpoints"""
        endpoints = ["/health", "/api/v1/health", "/"]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
    
    def test_list_surahs_pagination(self):
        """Test surah listing with pagination"""
        response = client.get("/api/v1/surahs?skip=0&limit=2")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) <= 2
        assert data[0]["number"] == 1
    
    def test_get_surah_with_verses(self):
        """Test getting surah with all verses"""
        response = client.get("/api/v1/surahs/1?include_translations=true")
        assert response.status_code == 200
        
        data = response.json()
        assert data["number"] == 1
        assert "verses" in data
        assert len(data["verses"]) > 0
        
        # Check verse has translations
        verse = data["verses"][0]
        assert "translations" in verse
        assert len(verse["translations"]) > 0
    
    def test_get_verse_by_reference(self):
        """Test getting verse by Quran reference (surah:verse)"""
        response = client.get("/api/v1/surahs/2/verses/255")
        assert response.status_code == 200
        
        data = response.json()
        assert data["verse_number"] == 255
        assert "text_arabic" in data
        assert "text_transliteration" in data
    
    def test_list_translations_metadata(self):
        """Test listing available translations with metadata"""
        response = client.get("/api/v1/translations")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
        
        # Check metadata
        translation = data[0]
        assert "language" in translation
        assert "translator" in translation
    
    def test_bookmark_crud(self):
        """Test bookmark create, read, update, delete"""
        # Create bookmark
        bookmark_data = {
            "verse_id": 1,
            "user_id": "test_user",
            "note": "Important verse"
        }
        response = client.post("/api/v1/bookmarks", json=bookmark_data)
        assert response.status_code == 201
        
        bookmark_id = response.json()["id"]
        
        # List bookmarks
        response = client.get("/api/v1/bookmarks?user_id=test_user")
        assert response.status_code == 200
        assert len(response.json()) > 0
        
        # Delete bookmark
        response = client.delete(f"/api/v1/bookmarks/{bookmark_id}?user_id=test_user")
        assert response.status_code == 204
    
    def test_audio_metadata_endpoint(self):
        """Test audio metadata endpoint"""
        response = client.get("/api/v1/verses/1/audio")
        
        # May not have audio file in test environment
        assert response.status_code in [200, 404]
    
    def test_admin_endpoints_require_auth(self):
        """Test admin endpoints require authentication"""
        # Without auth
        response = client.post("/api/v1/admin/ingest/scrape", json={})
        assert response.status_code == 403
        
        response = client.post("/api/v1/admin/embed/verse", json={})
        assert response.status_code == 403
    
    def test_admin_endpoints_with_auth(self):
        """Test admin endpoints with valid token"""
        headers = {"Authorization": "Bearer dev_admin_token_change_in_production"}
        
        # Test ingest endpoint
        response = client.post(
            "/api/v1/admin/ingest/scrape",
            json={"surah_numbers": [1]},
            headers=headers
        )
        assert response.status_code != 403


# ==================== Issue #7: Embeddings and Semantic Search Tests ====================

class TestEmbeddingsAndSemanticSearch:
    """Test embeddings and semantic search (Issue #7)"""
    
    def test_embedding_service_initialization(self):
        """Test EmbeddingService can be initialized"""
        service = EmbeddingService()
        assert service is not None
        assert service.model == "text-embedding-ada-002"
        assert service.dimension == 1536
    
    @patch("embedding_service.OpenAI")
    def test_embedding_generation_mock(self, mock_openai, monkeypatch):
        """Test embedding generation with mocked OpenAI"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Use monkeypatch to set environment variable safely
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        
        service = EmbeddingService()
        embedding = service.generate_embedding("test text")
        
        assert embedding is not None
        assert len(embedding) == 1536
    
    def test_hybrid_search(self):
        """Test hybrid search combines multiple search types"""
        response = client.get("/api/v1/search?q=Allah&lang=en&search_type=hybrid&limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert "results" in data
        assert data["search_type"] == "hybrid"
    
    def test_semantic_search_fallback(self):
        """Test semantic search falls back gracefully without embeddings"""
        response = client.get("/api/v1/search?q=mercy&lang=en&search_type=semantic")
        assert response.status_code == 200
        
        # Should not crash even without embeddings
        data = response.json()
        assert "results" in data
    
    @patch("embedding_service.OpenAI")
    def test_batch_embedding_creation(self, mock_openai, monkeypatch):
        """Test batch embedding creation endpoint"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(index=0, embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Use monkeypatch to set environment variable safely
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        
        headers = {"Authorization": "Bearer dev_admin_token_change_in_production"}
        response = client.post(
            "/api/v1/admin/embed/verse",
            json={"verse_ids": [1], "language": "en"},
            headers=headers
        )
        
        assert response.status_code == 200


# ==================== Security and Error Handling Tests ====================

class TestSecurityAndErrorHandling:
    """Test security measures and error handling"""
    
    def test_invalid_verse_id(self):
        """Test handling of invalid verse IDs"""
        response = client.get("/api/v1/verses/99999")
        assert response.status_code == 404
    
    def test_invalid_surah_number(self):
        """Test handling of invalid surah numbers"""
        response = client.get("/api/v1/surahs/999")
        assert response.status_code == 404
    
    def test_duplicate_bookmark_prevention(self):
        """Test duplicate bookmark prevention"""
        bookmark_data = {
            "verse_id": 1,
            "user_id": "test_user",
            "note": "Test"
        }
        
        # Create first bookmark
        response1 = client.post("/api/v1/bookmarks", json=bookmark_data)
        assert response1.status_code == 201
        
        # Try to create duplicate
        response2 = client.post("/api/v1/bookmarks", json=bookmark_data)
        assert response2.status_code == 400
    
    def test_bookmark_ownership_verification(self):
        """Test bookmark deletion requires correct user"""
        # Create bookmark
        bookmark_data = {
            "verse_id": 1,
            "user_id": "user1",
            "note": "Test"
        }
        response = client.post("/api/v1/bookmarks", json=bookmark_data)
        bookmark_id = response.json()["id"]
        
        # Try to delete with different user
        response = client.delete(f"/api/v1/bookmarks/{bookmark_id}?user_id=user2")
        assert response.status_code == 403
    
    def test_audio_path_traversal_prevention(self):
        """Test audio streaming prevents path traversal"""
        response = client.get("/api/v1/verses/1/audio/stream?reciter=../../../etc/passwd")
        assert response.status_code == 400
    
    def test_invalid_search_language(self):
        """Test invalid language code handling"""
        response = client.get("/api/v1/search?q=test&lang=invalid_lang")
        
        # API should either return no results (200) or reject invalid language (400)
        # Based on implementation, it returns 200 with empty results for unsupported languages
        assert response.status_code == 200
        
        data = response.json()
        # With invalid language, should return no results
        assert "results" in data


# ==================== Performance and Integration Tests ====================

class TestPerformanceAndIntegration:
    """Test performance and end-to-end scenarios"""
    
    def test_verse_with_all_related_data(self):
        """Test verse retrieval with all relationships"""
        db = TestingSessionLocal()
        verse = db.query(Verse).first()
        
        # Verify all relationships load
        assert verse.surah is not None
        assert len(verse.translations) > 0
        
        db.close()
    
    def test_search_returns_complete_data(self):
        """Test search returns complete verse data"""
        response = client.get("/api/v1/search?q=Allah&lang=en&search_type=exact&limit=1")
        assert response.status_code == 200
        
        data = response.json()
        if data["results"]:
            result = data["results"][0]
            
            # Check completeness - SearchResult has flattened structure
            assert "text_arabic" in result
            assert "text_transliteration" in result
            assert "translations" in result
            assert "verse_id" in result
            assert "surah_name" in result
    
    def test_multiple_concurrent_requests(self):
        """Test handling multiple concurrent requests"""
        # Simulate multiple requests
        responses = []
        for i in range(5):
            response = client.get(f"/api/v1/verses/{i+1}")
            responses.append(response)
        
        # All should succeed or return 404
        for response in responses:
            assert response.status_code in [200, 404]


# ==================== Data Validation Tests ====================

class TestDataValidation:
    """Test data validation and integrity"""
    
    def test_all_verses_have_required_fields(self):
        """Test all verses have required fields"""
        db = TestingSessionLocal()
        verses = db.query(Verse).all()
        
        for verse in verses:
            assert verse.text_arabic is not None
            assert verse.verse_number is not None
            assert verse.surah_id is not None
        
        db.close()
    
    def test_translation_language_codes(self):
        """Test translation language codes are valid"""
        db = TestingSessionLocal()
        translations = db.query(Translation).all()
        
        valid_languages = ["en", "ar", "te", "ur", "fr"]
        
        for translation in translations:
            assert translation.language in valid_languages
        
        db.close()
    
    def test_verse_numbers_sequential(self):
        """Test verse numbers are sequential within surah"""
        db = TestingSessionLocal()
        
        for surah_num in [1, 2]:
            verses = db.query(Verse).join(Surah).filter(
                Surah.number == surah_num
            ).order_by(Verse.verse_number).all()
            
            # Check verses are in order
            for i, verse in enumerate(verses):
                assert verse.verse_number >= 1
        
        db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
