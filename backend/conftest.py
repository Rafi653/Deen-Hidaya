"""
Pytest configuration and fixtures for backend tests
"""
import os

# Set testing mode BEFORE importing any application modules
os.environ["TESTING"] = "true"

import pytest
from fastapi.testclient import TestClient

from main import app
from database import Base, get_db, engine
from models import Surah, Verse, Translation


@pytest.fixture(scope="function", autouse=True)
def setup_test_database():
    """Create and tear down test database for each test"""
    import os
    # Remove test database if it exists
    if os.path.exists("/tmp/test_deen_hidaya.db"):
        os.remove("/tmp/test_deen_hidaya.db")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables after test
    Base.metadata.drop_all(bind=engine)
    
    # Clean up test database file
    if os.path.exists("/tmp/test_deen_hidaya.db"):
        os.remove("/tmp/test_deen_hidaya.db")


@pytest.fixture(scope="function")
def client():
    """Create a test client"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_surah():
    """Create a sample surah for testing"""
    from database import SessionLocal
    db = SessionLocal()
    try:
        surah = Surah(
            number=1,
            name_arabic="الفاتحة",
            name_english="Al-Fatihah",
            name_transliteration="Al-Fatihah",
            revelation_place="Meccan",
            total_verses=7
        )
        db.add(surah)
        db.commit()
        db.refresh(surah)
        return surah
    finally:
        db.close()


@pytest.fixture
def sample_verses(sample_surah):
    """Create sample verses for testing"""
    from database import SessionLocal
    db = SessionLocal()
    try:
        verses = []
        for i in range(1, 4):
            verse = Verse(
                surah_id=sample_surah.id,
                verse_number=i,
                text_arabic=f"Arabic text {i}",
                text_simple=f"Simple text {i}",
                text_transliteration=f"Transliteration {i}",
                juz_number=1,
                hizb_number=1,
                rub_number=1,
                sajda=False
            )
            verses.append(verse)
            db.add(verse)
        
        db.commit()
        for verse in verses:
            db.refresh(verse)
        return verses
    finally:
        db.close()


@pytest.fixture
def sample_translation(sample_verses):
    """Create a sample translation for testing"""
    from database import SessionLocal
    db = SessionLocal()
    try:
        translation = Translation(
            verse_id=sample_verses[0].id,
            language="en",
            text="Translation text",
            translator="Test Translator",
            source="Test Source",
            license="CC BY-SA 4.0"
        )
        db.add(translation)
        db.commit()
        db.refresh(translation)
        return translation
    finally:
        db.close()
