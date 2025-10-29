"""SQLAlchemy database models for Deen Hidaya"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Float, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
from database import Base


class Surah(Base):
    """Surah (Chapter) model"""
    __tablename__ = "surah"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, unique=True, nullable=False, index=True)
    name_arabic = Column(String(255), nullable=False)
    name_english = Column(String(255), nullable=False)
    name_transliteration = Column(String(255))
    revelation_place = Column(String(50))  # Meccan or Medinan
    total_verses = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    verses = relationship("Verse", back_populates="surah", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Surah {self.number}: {self.name_english}>"


class Verse(Base):
    """Verse (Ayah) model"""
    __tablename__ = "verse"

    id = Column(Integer, primary_key=True, index=True)
    surah_id = Column(Integer, ForeignKey("surah.id", ondelete="CASCADE"), nullable=False, index=True)
    verse_number = Column(Integer, nullable=False, index=True)
    text_arabic = Column(Text, nullable=False)
    text_simple = Column(Text)  # Simplified Arabic text without diacritics
    text_transliteration = Column(Text)  # Romanized/transliterated text
    juz_number = Column(Integer, index=True)
    hizb_number = Column(Integer)
    rub_number = Column(Integer)
    sajda = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    surah = relationship("Surah", back_populates="verses")
    translations = relationship("Translation", back_populates="verse", cascade="all, delete-orphan")
    audio_tracks = relationship("AudioTrack", back_populates="verse", cascade="all, delete-orphan")
    verse_tags = relationship("VerseTag", back_populates="verse", cascade="all, delete-orphan")
    embeddings = relationship("Embedding", back_populates="verse", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="verse", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Verse {self.surah_id}:{self.verse_number}>"

    __table_args__ = (
        Index('ix_verse_surah_number', 'surah_id', 'verse_number', unique=True),
    )


class Translation(Base):
    """Translation model for verse translations"""
    __tablename__ = "translation"

    id = Column(Integer, primary_key=True, index=True)
    verse_id = Column(Integer, ForeignKey("verse.id", ondelete="CASCADE"), nullable=False, index=True)
    language = Column(String(10), nullable=False, index=True)  # ISO 639-1 code (e.g., 'en', 'ur')
    translator = Column(String(255), nullable=False)
    text = Column(Text, nullable=False)
    license = Column(String(255))  # License information for this translation
    source = Column(String(255))  # Source of the translation (e.g., 'api.quran.com')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    verse = relationship("Verse", back_populates="translations")

    def __repr__(self):
        return f"<Translation {self.language} - {self.translator}>"

    __table_args__ = (
        Index('ix_translation_verse_language', 'verse_id', 'language', 'translator'),
    )


class AudioTrack(Base):
    """Audio track model for verse recitations"""
    __tablename__ = "audio_track"

    id = Column(Integer, primary_key=True, index=True)
    verse_id = Column(Integer, ForeignKey("verse.id", ondelete="CASCADE"), nullable=False, index=True)
    reciter = Column(String(255), nullable=False, index=True)
    reciter_arabic = Column(String(255))
    audio_url = Column(String(512), nullable=False)
    duration = Column(Float)  # Duration in seconds
    format = Column(String(10))  # mp3, ogg, etc.
    quality = Column(String(50))  # 32kbps, 64kbps, 128kbps, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    verse = relationship("Verse", back_populates="audio_tracks")

    def __repr__(self):
        return f"<AudioTrack {self.reciter} - Verse {self.verse_id}>"

    __table_args__ = (
        Index('ix_audio_verse_reciter', 'verse_id', 'reciter'),
    )


class Tag(Base):
    """Tag model for categorizing verses"""
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    category = Column(String(50), index=True)  # theme, topic, context, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    verse_tags = relationship("VerseTag", back_populates="tag", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Tag {self.name}>"


class VerseTag(Base):
    """Association table for verses and tags (many-to-many)"""
    __tablename__ = "verse_tag"

    id = Column(Integer, primary_key=True, index=True)
    verse_id = Column(Integer, ForeignKey("verse.id", ondelete="CASCADE"), nullable=False, index=True)
    tag_id = Column(Integer, ForeignKey("tag.id", ondelete="CASCADE"), nullable=False, index=True)
    relevance_score = Column(Float)  # Optional: how relevant is this tag to the verse (0-1)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    verse = relationship("Verse", back_populates="verse_tags")
    tag = relationship("Tag", back_populates="verse_tags")

    def __repr__(self):
        return f"<VerseTag verse_id={self.verse_id} tag_id={self.tag_id}>"

    __table_args__ = (
        Index('ix_verse_tag_unique', 'verse_id', 'tag_id', unique=True),
    )


class Entity(Base):
    """Entity model for named entities mentioned in the Quran"""
    __tablename__ = "entity"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    name_arabic = Column(String(255))
    entity_type = Column(String(50), nullable=False, index=True)  # person, place, event, concept
    description = Column(Text)
    verse_references = Column(ARRAY(String))  # Array of verse references like ["2:30", "2:31"]
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Entity {self.name} ({self.entity_type})>"


class Embedding(Base):
    """Embedding model for semantic search"""
    __tablename__ = "embedding"

    id = Column(Integer, primary_key=True, index=True)
    verse_id = Column(Integer, ForeignKey("verse.id", ondelete="CASCADE"), nullable=False, index=True)
    model = Column(String(100), nullable=False, index=True)  # embedding model used
    embedding_vector = Column(Text, nullable=False)  # Stored as text, will use pgvector in production
    dimension = Column(Integer, nullable=False)  # embedding dimension (e.g., 1536 for OpenAI)
    language = Column(String(10), index=True)  # Language of the embedded text
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    verse = relationship("Verse", back_populates="embeddings")

    def __repr__(self):
        return f"<Embedding verse_id={self.verse_id} model={self.model}>"

    __table_args__ = (
        Index('ix_embedding_verse_model', 'verse_id', 'model', 'language'),
    )


class Bookmark(Base):
    """Bookmark model for user bookmarks (simplified without user table)"""
    __tablename__ = "bookmark"

    id = Column(Integer, primary_key=True, index=True)
    verse_id = Column(Integer, ForeignKey("verse.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(255), index=True)  # Can be session ID or user ID from auth system
    note = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    verse = relationship("Verse", back_populates="bookmarks")

    def __repr__(self):
        return f"<Bookmark user_id={self.user_id} verse_id={self.verse_id}>"

    __table_args__ = (
        Index('ix_bookmark_user_verse', 'user_id', 'verse_id'),
    )
