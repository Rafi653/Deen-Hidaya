"""
Tests for the name generator API
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base, get_db
from models import NameEntity, NameFavorite

# Setup test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
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


@pytest.fixture(scope="function")
def client():
    """Create test database and client"""
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create test database session"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_names(db):
    """Create sample name data for testing"""
    names = [
        NameEntity(
            name="Muhammad",
            entity_type="baby",
            subtype="human",
            gender="male",
            meaning="Praised one",
            origin="Arabic",
            phonetic="moo-HAM-mad",
            themes=["classic", "religious"],
            associated_traits=["leadership", "strength"],
            popularity_score=0.95
        ),
        NameEntity(
            name="Aisha",
            entity_type="baby",
            subtype="human",
            gender="female",
            meaning="Living, prosperous",
            origin="Arabic",
            phonetic="ah-EE-shah",
            themes=["classic", "traditional"],
            associated_traits=["wisdom", "prosperity"],
            popularity_score=0.89
        ),
        NameEntity(
            name="Max",
            entity_type="pet",
            subtype="dog",
            gender="male",
            meaning="Greatest",
            origin="Latin",
            phonetic="MAKS",
            themes=["classic", "strong"],
            associated_traits=["strength", "loyalty"],
            popularity_score=0.95
        ),
        NameEntity(
            name="Luna",
            entity_type="pet",
            subtype="dog",
            gender="female",
            meaning="Moon",
            origin="Latin",
            phonetic="LOO-nah",
            themes=["mystical", "elegant"],
            associated_traits=["beauty", "grace"],
            popularity_score=0.92
        ),
        NameEntity(
            name="Thunder",
            entity_type="vehicle",
            subtype="car",
            gender="unisex",
            meaning="Loud rumbling",
            origin="English",
            phonetic="THUN-der",
            themes=["powerful", "bold"],
            associated_traits=["power", "speed"],
            popularity_score=0.70
        ),
    ]
    
    for name in names:
        db.add(name)
    db.commit()
    
    return names


def test_get_entity_types(client, sample_names):
    """Test getting all entity types"""
    response = client.get("/api/v1/names/entity-types")
    assert response.status_code == 200
    
    entity_types = response.json()
    assert "baby" in entity_types
    assert "pet" in entity_types
    assert "vehicle" in entity_types


def test_get_subtypes(client, sample_names):
    """Test getting subtypes for an entity type"""
    response = client.get("/api/v1/names/subtypes/pet")
    assert response.status_code == 200
    
    subtypes = response.json()
    assert "dog" in subtypes


def test_suggest_names_by_entity_type(client, sample_names):
    """Test basic name suggestion by entity type"""
    request_data = {
        "entity_type": "baby",
        "max_results": 10
    }
    
    response = client.post("/api/v1/names/suggest", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "suggestions" in data
    assert len(data["suggestions"]) <= 10
    assert data["total"] <= 10
    
    # All suggestions should be baby names
    for suggestion in data["suggestions"]:
        assert suggestion["entity_type"] == "baby"
        assert "relevance_score" in suggestion


def test_suggest_names_with_gender(client, sample_names):
    """Test name suggestion with gender filter"""
    request_data = {
        "entity_type": "baby",
        "gender": "female",
        "max_results": 10
    }
    
    response = client.post("/api/v1/names/suggest", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    suggestions = data["suggestions"]
    
    # Should return female names
    for suggestion in suggestions:
        assert suggestion["gender"] in ["female", "unisex", None]


def test_suggest_names_with_meaning(client, sample_names):
    """Test name suggestion with meaning preference"""
    request_data = {
        "entity_type": "baby",
        "meaning": "strength",
        "max_results": 10
    }
    
    response = client.post("/api/v1/names/suggest", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    # Should return names with relevance scores
    assert len(data["suggestions"]) > 0
    
    # Names with matching traits should have higher scores
    for suggestion in data["suggestions"]:
        assert "relevance_score" in suggestion


def test_suggest_names_with_themes(client, sample_names):
    """Test name suggestion with theme preferences"""
    request_data = {
        "entity_type": "pet",
        "subtype": "dog",
        "themes": ["classic", "strong"],
        "max_results": 10
    }
    
    response = client.post("/api/v1/names/suggest", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    suggestions = data["suggestions"]
    
    # Should have at least one result
    assert len(suggestions) > 0


def test_suggest_names_with_origin(client, sample_names):
    """Test name suggestion with origin filter"""
    request_data = {
        "entity_type": "baby",
        "origin": "Arabic",
        "max_results": 10
    }
    
    response = client.post("/api/v1/names/suggest", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    suggestions = data["suggestions"]
    
    # All results should have Arabic origin
    for suggestion in suggestions:
        if suggestion["origin"]:
            assert "Arabic" in suggestion["origin"]


def test_get_name_by_id(client, sample_names):
    """Test getting a specific name by ID"""
    response = client.get("/api/v1/names/names/1")
    assert response.status_code == 200
    
    data = response.json()
    assert "name" in data
    assert "entity_type" in data
    assert "meaning" in data


def test_get_name_by_id_not_found(client):
    """Test getting a non-existent name"""
    response = client.get("/api/v1/names/names/9999")
    assert response.status_code == 404


def test_search_names(client, sample_names):
    """Test searching names by query"""
    response = client.get("/api/v1/names/search?query=Max")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) > 0
    assert any("Max" in item["name"] for item in data)


def test_search_names_with_entity_type_filter(client, sample_names):
    """Test searching names with entity type filter"""
    response = client.get("/api/v1/names/search?query=a&entity_type=baby")
    assert response.status_code == 200
    
    data = response.json()
    # All results should be baby names
    for item in data:
        assert item["entity_type"] == "baby"


def test_create_favorite(client, sample_names):
    """Test creating a favorite"""
    favorite_data = {
        "name_entity_id": 1,
        "user_id": "test_user_123",
        "note": "Love this name!"
    }
    
    response = client.post("/api/v1/names/favorites", json=favorite_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name_entity_id"] == 1
    assert data["user_id"] == "test_user_123"
    assert data["note"] == "Love this name!"


def test_create_duplicate_favorite(client, sample_names):
    """Test creating a duplicate favorite (should fail)"""
    favorite_data = {
        "name_entity_id": 1,
        "user_id": "test_user_123",
        "note": "First favorite"
    }
    
    # Create first favorite
    response1 = client.post("/api/v1/names/favorites", json=favorite_data)
    assert response1.status_code == 200
    
    # Try to create duplicate
    response2 = client.post("/api/v1/names/favorites", json=favorite_data)
    assert response2.status_code == 400


def test_get_user_favorites(client, sample_names):
    """Test getting user favorites"""
    # Create some favorites
    client.post("/api/v1/names/favorites", json={
        "name_entity_id": 1,
        "user_id": "test_user_123",
        "note": "Favorite 1"
    })
    client.post("/api/v1/names/favorites", json={
        "name_entity_id": 2,
        "user_id": "test_user_123",
        "note": "Favorite 2"
    })
    
    # Get favorites
    response = client.get("/api/v1/names/favorites/test_user_123")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2


def test_delete_favorite(client, sample_names):
    """Test deleting a favorite"""
    # Create a favorite
    create_response = client.post("/api/v1/names/favorites", json={
        "name_entity_id": 1,
        "user_id": "test_user_123",
        "note": "Test favorite"
    })
    favorite_id = create_response.json()["id"]
    
    # Delete the favorite
    delete_response = client.delete(
        f"/api/v1/names/favorites/{favorite_id}?user_id=test_user_123"
    )
    assert delete_response.status_code == 200
    
    # Verify it's deleted
    favorites_response = client.get("/api/v1/names/favorites/test_user_123")
    assert len(favorites_response.json()) == 0


def test_delete_favorite_not_found(client):
    """Test deleting a non-existent favorite"""
    response = client.delete("/api/v1/names/favorites/9999?user_id=test_user_123")
    assert response.status_code == 404


def test_relevance_scoring(client, sample_names):
    """Test that relevance scoring works correctly"""
    # Request with multiple preference criteria
    request_data = {
        "entity_type": "baby",
        "gender": "male",
        "origin": "Arabic",
        "themes": ["classic", "religious"],
        "max_results": 10
    }
    
    response = client.post("/api/v1/names/suggest", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    suggestions = data["suggestions"]
    
    # Verify results are sorted by relevance score (descending)
    scores = [s["relevance_score"] for s in suggestions]
    assert scores == sorted(scores, reverse=True)


def test_max_results_limit(client, sample_names):
    """Test that max_results parameter is respected"""
    request_data = {
        "entity_type": "baby",
        "max_results": 1
    }
    
    response = client.post("/api/v1/names/suggest", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["suggestions"]) <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
