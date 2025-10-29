"""
Database models for Deen Hidaya

Defines SQLAlchemy models for storing Quran data.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Surah(Base):
    """Surah (Chapter) model."""
    
    __tablename__ = "surahs"
    
    id = Column(Integer, primary_key=True)
    number = Column(Integer, unique=True, nullable=False, index=True)
    name_arabic = Column(String(100), nullable=False)
    name_simple = Column(String(100), nullable=False)
    name_complex = Column(String(100))
    revelation_place = Column(String(20))  # makkah or madinah
    revelation_order = Column(Integer)
    verses_count = Column(Integer, nullable=False)
    pages = Column(JSON)  # [start_page, end_page]
    created_at = Column(TIMESTAMP, default=datetime.now)
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    
    # Relationship
    verses = relationship("Verse", back_populates="surah", cascade="all, delete-orphan")
    audio_tracks = relationship("AudioTrack", back_populates="surah", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Surah {self.number}: {self.name_simple}>"


class Verse(Base):
    """Verse (Ayah) model."""
    
    __tablename__ = "verses"
    
    id = Column(Integer, primary_key=True)
    surah_id = Column(Integer, ForeignKey("surahs.id", ondelete="CASCADE"), nullable=False)
    verse_number = Column(Integer, nullable=False)
    verse_key = Column(String(20), unique=True, nullable=False, index=True)  # e.g., "1:1"
    juz_number = Column(Integer)
    hizb_number = Column(Integer)
    rub_number = Column(Integer)
    text_uthmani = Column(Text, nullable=False)  # Uthmani script (with tajweed marks)
    text_imlaei = Column(Text)  # Imlaei script (simplified)
    text_simple = Column(Text)  # Simple text
    created_at = Column(TIMESTAMP, default=datetime.now)
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    surah = relationship("Surah", back_populates="verses")
    translations = relationship("Translation", back_populates="verse", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Verse {self.verse_key}>"


class Translation(Base):
    """Translation model for verses."""
    
    __tablename__ = "translations"
    
    id = Column(Integer, primary_key=True)
    verse_id = Column(Integer, ForeignKey("verses.id", ondelete="CASCADE"), nullable=False)
    resource_id = Column(Integer)  # External translation resource ID
    text = Column(Text, nullable=False)
    language = Column(String(50), default="english")
    created_at = Column(TIMESTAMP, default=datetime.now)
    
    # Relationship
    verse = relationship("Verse", back_populates="translations")
    
    def __repr__(self):
        return f"<Translation {self.verse_id} ({self.language})>"


class AudioTrack(Base):
    """Audio track model for recitations."""
    
    __tablename__ = "audio_tracks"
    
    id = Column(Integer, primary_key=True)
    surah_id = Column(Integer, ForeignKey("surahs.id", ondelete="CASCADE"), nullable=False)
    reciter = Column(String(200), nullable=False)
    reciter_id = Column(Integer)
    audio_url = Column(Text, nullable=False)
    format = Column(String(10), default="mp3")
    license_info = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.now)
    
    # Relationship
    surah = relationship("Surah", back_populates="audio_tracks")
    
    def __repr__(self):
        return f"<AudioTrack {self.surah_id} by {self.reciter}>"


class DataSource(Base):
    """Track data sources and their licenses."""
    
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True)
    source_name = Column(String(200), nullable=False)
    source_url = Column(Text)
    license_text = Column(Text)
    license_url = Column(Text)
    data_type = Column(String(50))  # text, translation, audio
    scraped_at = Column(TIMESTAMP)
    source_metadata = Column(JSON)
    created_at = Column(TIMESTAMP, default=datetime.now)
    
    def __repr__(self):
        return f"<DataSource {self.source_name}>"
