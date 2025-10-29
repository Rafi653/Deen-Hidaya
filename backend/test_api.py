"""
Tests for Backend API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base, get_db
from models import Surah, Verse, Translation, Bookmark, AudioTrack

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


@pytest.fixture(autouse=True)
def setup_database():
    """Setup test database before each test"""
    # Create only the tables we need for tests (excluding Entity which has ARRAY)
    tables_to_create = [
        Base.metadata.tables['surah'],
        Base.metadata.tables['verse'],
        Base.metadata.tables['translation'],
        Base.metadata.tables['bookmark'],
        Base.metadata.tables['audio_track'],
        Base.metadata.tables['tag'],
        Base.metadata.tables['verse_tag'],
        Base.metadata.tables['embedding']
    ]
    
    for table in tables_to_create:
        table.create(bind=engine, checkfirst=True)
    
    # Create test data
    db = TestingSessionLocal()
    
    # Create a test surah
    surah = Surah(
        number=1,
        name_arabic="الفاتحة",
        name_english="Al-Fatiha",
        name_transliteration="Al-Fatihah",
        revelation_place="Meccan",
        total_verses=7
    )
    db.add(surah)
    db.commit()
    db.refresh(surah)
    
    # Create test verses
    for i in range(1, 8):
        verse = Verse(
            surah_id=surah.id,
            verse_number=i,
            text_arabic=f"Arabic text {i}",
            text_simple=f"Simple text {i}",
            text_transliteration=f"Transliteration {i}",
            juz_number=1
        )
        db.add(verse)
    
    db.commit()
    
    # Create test translations
    verses = db.query(Verse).all()
    for verse in verses:
        translation = Translation(
            verse_id=verse.id,
            language="en",
            translator="Test Translator",
            text=f"English translation for verse {verse.verse_number}",
            license="Public Domain",
            source="Test"
        )
        db.add(translation)
    
    db.commit()
    db.close()
    
    yield
    
    # Cleanup
    for table in reversed(tables_to_create):
        table.drop(bind=engine, checkfirst=True)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_list_surahs():
    """Test listing surahs"""
    response = client.get("/api/v1/surahs")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name_english"] == "Al-Fatiha"


def test_get_surah():
    """Test getting a specific surah"""
    response = client.get("/api/v1/surahs/1")
    assert response.status_code == 200
    data = response.json()
    assert data["number"] == 1
    assert data["name_english"] == "Al-Fatiha"
    assert len(data["verses"]) == 7


def test_get_verse():
    """Test getting a specific verse"""
    response = client.get("/api/v1/verses/1")
    assert response.status_code == 200
    data = response.json()
    assert data["verse_number"] == 1
    assert "text_arabic" in data


def test_list_translations():
    """Test listing available translations"""
    response = client.get("/api/v1/translations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["language"] == "en"


def test_create_bookmark():
    """Test creating a bookmark"""
    bookmark_data = {
        "verse_id": 1,
        "user_id": "test_user_123",
        "note": "Test bookmark"
    }
    response = client.post("/api/v1/bookmarks", json=bookmark_data)
    assert response.status_code == 201
    data = response.json()
    assert data["verse_id"] == 1
    assert data["user_id"] == "test_user_123"
    assert data["note"] == "Test bookmark"


def test_list_bookmarks():
    """Test listing bookmarks"""
    # First create a bookmark
    bookmark_data = {
        "verse_id": 1,
        "user_id": "test_user_123",
        "note": "Test bookmark"
    }
    client.post("/api/v1/bookmarks", json=bookmark_data)
    
    # List bookmarks
    response = client.get("/api/v1/bookmarks?user_id=test_user_123")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["user_id"] == "test_user_123"


def test_delete_bookmark():
    """Test deleting a bookmark"""
    # First create a bookmark
    bookmark_data = {
        "verse_id": 1,
        "user_id": "test_user_123",
        "note": "Test bookmark"
    }
    create_response = client.post("/api/v1/bookmarks", json=bookmark_data)
    bookmark_id = create_response.json()["id"]
    
    # Delete the bookmark
    response = client.delete(f"/api/v1/bookmarks/{bookmark_id}?user_id=test_user_123")
    assert response.status_code == 204


def test_search_exact():
    """Test exact search"""
    response = client.get("/api/v1/search?q=verse&lang=en&search_type=exact")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert data["search_type"] == "exact"


def test_search_fuzzy():
    """Test fuzzy search"""
    response = client.get("/api/v1/search?q=translation&lang=en&search_type=fuzzy")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert data["search_type"] == "fuzzy"


def test_search_hybrid():
    """Test hybrid search"""
    response = client.get("/api/v1/search?q=verse&lang=en&search_type=hybrid")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert data["search_type"] == "hybrid"


def test_admin_ingest_without_auth():
    """Test admin endpoint without authentication"""
    response = client.post("/api/v1/admin/ingest/scrape", json={})
    assert response.status_code == 403


def test_admin_embed_without_auth():
    """Test admin embed endpoint without authentication"""
    response = client.post("/api/v1/admin/embed/verse", json={})
    assert response.status_code == 403


def test_admin_ingest_with_auth():
    """Test admin endpoint with authentication"""
    headers = {"Authorization": "Bearer dev_admin_token_change_in_production"}
    response = client.post(
        "/api/v1/admin/ingest/scrape",
        json={"surah_numbers": [1]},
        headers=headers
    )
    # This might fail due to missing scraper script, but should not be 403
    assert response.status_code != 403


def test_admin_embed_with_auth():
    """Test admin embed endpoint with authentication"""
    headers = {"Authorization": "Bearer dev_admin_token_change_in_production"}
    response = client.post(
        "/api/v1/admin/embed/verse",
        json={"verse_ids": [1]},
        headers=headers
    )
    # Since we don't have OpenAI API key in test environment,
    # we expect a 500 error with appropriate message
    assert response.status_code == 500
    assert "OpenAI API key not configured" in response.json()["detail"]


def test_verse_not_found():
    """Test getting non-existent verse"""
    response = client.get("/api/v1/verses/99999")
    assert response.status_code == 404


def test_surah_not_found():
    """Test getting non-existent surah"""
    response = client.get("/api/v1/surahs/999")
    assert response.status_code == 404


def test_duplicate_bookmark():
    """Test creating duplicate bookmark"""
    bookmark_data = {
        "verse_id": 1,
        "user_id": "test_user_123",
        "note": "Test bookmark"
    }
    # Create first bookmark
    response1 = client.post("/api/v1/bookmarks", json=bookmark_data)
    assert response1.status_code == 201
    
    # Try to create duplicate
    response2 = client.post("/api/v1/bookmarks", json=bookmark_data)
    assert response2.status_code == 400


def test_delete_bookmark_wrong_user():
    """Test deleting bookmark with wrong user"""
    # Create a bookmark
    bookmark_data = {
        "verse_id": 1,
        "user_id": "test_user_123",
        "note": "Test bookmark"
    }
    create_response = client.post("/api/v1/bookmarks", json=bookmark_data)
    bookmark_id = create_response.json()["id"]
    
    # Try to delete with different user
    response = client.delete(f"/api/v1/bookmarks/{bookmark_id}?user_id=different_user")
    assert response.status_code == 403


def test_audio_stream_invalid_language():
    """Test audio streaming with invalid language code"""
    response = client.get("/api/v1/verses/1/audio/stream?language=invalid")
    assert response.status_code == 400
    assert "Invalid language code" in response.json()["detail"]


def test_audio_stream_path_traversal():
    """Test audio streaming rejects path traversal attempts"""
    # Try path traversal in reciter parameter
    response = client.get("/api/v1/verses/1/audio/stream?reciter=../../../etc/passwd")
    assert response.status_code == 400
    
    # Try with encoded path traversal
    response = client.get("/api/v1/verses/1/audio/stream?reciter=..%2F..%2Fetc%2Fpasswd")
    assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
