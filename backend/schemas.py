"""
Pydantic schemas for Deen Hidaya API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


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
