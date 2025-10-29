"""
Pydantic schemas for Deen Hidaya API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TranslationMetadata(BaseModel):
    """Translation metadata schema"""
    language: str
    translator: str
    source: Optional[str] = None
    license: Optional[str] = None


class TranslationResponse(BaseModel):
    """Translation response schema"""
    id: int
    language: str
    translator: str
    text: str
    license: Optional[str] = None
    source: Optional[str] = None
    
    class Config:
        from_attributes = True


class VerseResponse(BaseModel):
    """Verse response schema"""
    id: int
    verse_number: int
    text_arabic: str
    text_simple: Optional[str] = None
    text_transliteration: Optional[str] = None
    juz_number: Optional[int] = None
    hizb_number: Optional[int] = None
    rub_number: Optional[int] = None
    sajda: bool = False
    translations: List[TranslationResponse] = []
    
    class Config:
        from_attributes = True


class SurahSummary(BaseModel):
    """Surah summary schema (without verses)"""
    id: int
    number: int
    name_arabic: str
    name_english: str
    name_transliteration: Optional[str] = None
    revelation_place: Optional[str] = None
    total_verses: int
    
    class Config:
        from_attributes = True


class SurahDetailResponse(BaseModel):
    """Surah detail response schema (with verses)"""
    id: int
    number: int
    name_arabic: str
    name_english: str
    name_transliteration: Optional[str] = None
    revelation_place: Optional[str] = None
    total_verses: int
    verses: List[VerseResponse] = []
    
    class Config:
        from_attributes = True


class AudioMetadataResponse(BaseModel):
    """Audio metadata response schema"""
    id: int
    reciter: str
    reciter_arabic: Optional[str] = None
    audio_url: str
    duration: Optional[float] = None
    format: Optional[str] = None
    quality: Optional[str] = None
    
    class Config:
        from_attributes = True


class BookmarkCreate(BaseModel):
    """Schema for creating a bookmark"""
    verse_id: int = Field(..., description="ID of the verse to bookmark")
    user_id: str = Field(..., description="User ID or session ID")
    note: Optional[str] = Field(None, description="Optional note for the bookmark")


class BookmarkResponse(BaseModel):
    """Bookmark response schema"""
    id: int
    verse_id: int
    user_id: str
    note: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BookmarkWithVerseResponse(BaseModel):
    """Bookmark response with verse details"""
    id: int
    verse_id: int
    user_id: str
    note: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    verse: Optional[VerseResponse] = None
    
    class Config:
        from_attributes = True


class SearchResult(BaseModel):
    """Search result schema"""
    verse_id: int
    verse_number: int
    surah_number: int
    surah_name: str
    text_arabic: str
    text_transliteration: Optional[str] = None
    translations: List[TranslationResponse] = []
    score: float = Field(..., description="Relevance score")
    match_type: str = Field(..., description="Type of match: exact, fuzzy, or semantic")


class SearchResponse(BaseModel):
    """Search response schema"""
    query: str
    results: List[SearchResult]
    total: int
    search_type: str = Field(..., description="Search type used: exact, fuzzy, semantic, or hybrid")


class IngestRequest(BaseModel):
    """Request schema for ingesting data"""
    surah_numbers: Optional[List[int]] = Field(None, description="Specific surah numbers to scrape")


class IngestResponse(BaseModel):
    """Response schema for ingest operation"""
    status: str
    message: str
    surahs_processed: List[int] = []
    verses_processed: int = 0


class EmbedRequest(BaseModel):
    """Request schema for creating embeddings"""
    verse_ids: Optional[List[int]] = Field(None, description="Specific verse IDs to embed")
    model: str = Field("text-embedding-ada-002", description="Embedding model to use")
    language: str = Field("en", description="Language of text to embed")


class EmbedResponse(BaseModel):
    """Response schema for embed operation"""
    status: str
    message: str
    verses_embedded: int = 0
