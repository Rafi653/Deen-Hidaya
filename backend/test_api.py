"""
API endpoint tests for Deen Hidaya backend
"""
import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client):
    """Test the root endpoint returns correct response"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Deen Hidaya API"
    assert data["status"] == "running"


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "backend"


def test_api_health_check(client):
    """Test API health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "backend-api"


def test_list_surahs_empty(client):
    """Test listing surahs when database is empty"""
    response = client.get("/api/v1/surahs")
    assert response.status_code == 200
    assert response.json() == []


def test_list_surahs_with_data(client, sample_surah):
    """Test listing surahs with data"""
    response = client.get("/api/v1/surahs")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["number"] == 1
    assert data[0]["name_english"] == "Al-Fatihah"


def test_get_surah_not_found(client):
    """Test getting a surah that doesn't exist"""
    response = client.get("/api/v1/surahs/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_surah_with_verses(client, sample_surah, sample_verses):
    """Test getting a surah with verses"""
    response = client.get(f"/api/v1/surahs/{sample_surah.number}")
    assert response.status_code == 200
    data = response.json()
    assert data["number"] == sample_surah.number
    assert data["name_english"] == sample_surah.name_english
    assert len(data["verses"]) == 3
    assert data["verses"][0]["verse_number"] == 1


def test_get_surah_without_translations(client, sample_surah, sample_verses, sample_translation):
    """Test getting a surah without translations"""
    response = client.get(f"/api/v1/surahs/{sample_surah.number}?include_translations=false")
    assert response.status_code == 200
    data = response.json()
    # Verify verses are included but translations are not loaded
    assert len(data["verses"]) == 3


def test_get_verse_by_id(client, sample_verses):
    """Test getting a verse by ID"""
    verse_id = sample_verses[0].id
    response = client.get(f"/api/v1/verses/{verse_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == verse_id
    assert data["verse_number"] == 1


def test_get_verse_by_id_not_found(client):
    """Test getting a verse that doesn't exist"""
    response = client.get("/api/v1/verses/999")
    assert response.status_code == 404


def test_get_verse_by_surah_and_number(client, sample_surah, sample_verses):
    """Test getting a verse by surah number and verse number"""
    response = client.get(f"/api/v1/surahs/{sample_surah.number}/verses/1")
    assert response.status_code == 200
    data = response.json()
    assert data["verse_number"] == 1
    assert data["text_arabic"] == "Arabic text 1"


def test_get_verse_by_surah_and_number_not_found(client, sample_surah):
    """Test getting a verse that doesn't exist in a surah"""
    response = client.get(f"/api/v1/surahs/{sample_surah.number}/verses/999")
    assert response.status_code == 404


def test_get_verse_with_translation(client, sample_verses, sample_translation):
    """Test getting a verse with translation"""
    verse_id = sample_verses[0].id
    response = client.get(f"/api/v1/verses/{verse_id}?include_translations=true")
    assert response.status_code == 200
    data = response.json()
    assert "translations" in data
    assert len(data["translations"]) == 1
    assert data["translations"][0]["language"] == "en"
    assert data["translations"][0]["translator"] == "Test Translator"


def test_list_translations_empty(client):
    """Test listing translations when none exist"""
    response = client.get("/api/v1/translations")
    assert response.status_code == 200
    assert response.json() == []


def test_list_translations(client, sample_translation):
    """Test listing available translations"""
    response = client.get("/api/v1/translations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    translation = data[0]
    assert translation["language"] == "en"
    assert translation["translator"] == "Test Translator"
    assert translation["license"] == "CC BY-SA 4.0"


def test_pagination_skip(client, sample_surah):
    """Test pagination with skip parameter"""
    response = client.get("/api/v1/surahs?skip=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0  # Only one surah, skip=1 means no results


def test_pagination_limit(client, sample_surah):
    """Test pagination with limit parameter"""
    response = client.get("/api/v1/surahs?limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


@pytest.mark.parametrize("endpoint", [
    "/api/v1/surahs",
    "/api/v1/translations",
])
def test_endpoints_return_json(client, endpoint):
    """Test that endpoints return JSON content type"""
    response = client.get(endpoint)
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
