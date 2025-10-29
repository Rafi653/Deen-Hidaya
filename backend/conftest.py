"""
Pytest configuration and fixtures for backend tests
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set testing mode before importing application modules
os.environ["TESTING"] = "true"

from main import app
from database import Base, get_db
from models import Surah, Verse, Translation


# Create test database engine
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_surah(db_session):
    """Create a sample surah for testing"""
    surah = Surah(
        number=1,
        name="Al-Fatihah",
        english_name="The Opener",
        english_name_translation="The Opening",
        revelation_type="Meccan",
        number_of_ayahs=7
    )
    db_session.add(surah)
    db_session.commit()
    db_session.refresh(surah)
    return surah


@pytest.fixture
def sample_verses(db_session, sample_surah):
    """Create sample verses for testing"""
    verses = []
    for i in range(1, 4):
        verse = Verse(
            surah_id=sample_surah.id,
            verse_number=i,
            text=f"Arabic text {i}",
            text_simple=f"Simple text {i}",
            text_transliteration=f"Transliteration {i}",
            juz_number=1,
            hizb_number=1,
            rub_number=1,
            sajdah_type=None
        )
        verses.append(verse)
        db_session.add(verse)
    
    db_session.commit()
    for verse in verses:
        db_session.refresh(verse)
    return verses


@pytest.fixture
def sample_translation(db_session, sample_verses):
    """Create a sample translation for testing"""
    translation = Translation(
        verse_id=sample_verses[0].id,
        language="en",
        text="Translation text",
        translator="Test Translator",
        source="Test Source",
        license="CC BY-SA 4.0"
    )
    db_session.add(translation)
    db_session.commit()
    db_session.refresh(translation)
    return translation
