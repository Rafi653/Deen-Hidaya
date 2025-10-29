"""
API routes for Quran data
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from database import get_db
from models import Surah, Verse, Translation
from schemas import SurahSummary, SurahDetailResponse, VerseResponse


router = APIRouter(prefix="/api/v1", tags=["quran"])


@router.get("/surahs", response_model=List[SurahSummary])
def list_surahs(
    skip: int = Query(0, ge=0, description="Number of surahs to skip"),
    limit: int = Query(114, ge=1, le=114, description="Number of surahs to return"),
    db: Session = Depends(get_db)
):
    """
    List all surahs with basic information
    """
    surahs = db.query(Surah).order_by(Surah.number).offset(skip).limit(limit).all()
    return surahs


@router.get("/surahs/{surah_number}", response_model=SurahDetailResponse)
def get_surah(
    surah_number: int,
    include_translations: bool = Query(True, description="Include translations in verses"),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific surah including all verses
    """
    query = db.query(Surah).filter(Surah.number == surah_number)
    
    # Eagerly load verses
    query = query.options(joinedload(Surah.verses))
    
    if include_translations:
        # Also eagerly load translations
        query = query.options(joinedload(Surah.verses).joinedload(Verse.translations))
    
    surah = query.first()
    
    if not surah:
        raise HTTPException(status_code=404, detail=f"Surah {surah_number} not found")
    
    return surah


@router.get("/verses/{verse_id}", response_model=VerseResponse)
def get_verse(
    verse_id: int,
    include_translations: bool = Query(True, description="Include translations"),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific verse
    """
    query = db.query(Verse).filter(Verse.id == verse_id)
    
    if include_translations:
        query = query.options(joinedload(Verse.translations))
    
    verse = query.first()
    
    if not verse:
        raise HTTPException(status_code=404, detail=f"Verse {verse_id} not found")
    
    return verse


@router.get("/surahs/{surah_number}/verses/{verse_number}", response_model=VerseResponse)
def get_verse_by_surah_and_number(
    surah_number: int,
    verse_number: int,
    include_translations: bool = Query(True, description="Include translations"),
    db: Session = Depends(get_db)
):
    """
    Get a verse by surah number and verse number (e.g., 2:255)
    """
    # First, find the surah
    surah = db.query(Surah).filter(Surah.number == surah_number).first()
    if not surah:
        raise HTTPException(status_code=404, detail=f"Surah {surah_number} not found")
    
    # Then find the verse
    query = db.query(Verse).filter(
        Verse.surah_id == surah.id,
        Verse.verse_number == verse_number
    )
    
    if include_translations:
        query = query.options(joinedload(Verse.translations))
    
    verse = query.first()
    
    if not verse:
        raise HTTPException(
            status_code=404,
            detail=f"Verse {verse_number} not found in Surah {surah_number}"
        )
    
    return verse


@router.get("/translations", response_model=List[dict])
def list_available_translations(db: Session = Depends(get_db)):
    """
    List all unique translator/language combinations available
    """
    translations = (
        db.query(
            Translation.language,
            Translation.translator,
            Translation.source,
            Translation.license
        )
        .distinct()
        .all()
    )
    
    return [
        {
            "language": t.language,
            "translator": t.translator,
            "source": t.source,
            "license": t.license
        }
        for t in translations
    ]
