"""
API routes for Quran data
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Header, Request, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import subprocess
import sys

from database import get_db
from models import Surah, Verse, Translation, Bookmark, AudioTrack
from schemas import (
    SurahSummary, SurahDetailResponse, VerseResponse, TranslationMetadata,
    AudioMetadataResponse, BookmarkCreate, BookmarkResponse, BookmarkWithVerseResponse,
    SearchResponse, SearchResult, IngestRequest, IngestResponse,
    EmbedRequest, EmbedResponse, QARequest, QAResponse, CitedVerse
)
from audio_utils import stream_audio_file, get_audio_path
from auth import verify_admin_token
from search_utils import exact_search, fuzzy_search, semantic_search, hybrid_search
from embedding_service import EmbeddingService


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


@router.get("/translations", response_model=List[TranslationMetadata])
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
        TranslationMetadata(
            language=t.language,
            translator=t.translator,
            source=t.source,
            license=t.license
        )
        for t in translations
    ]


@router.get("/verses/{verse_id}/audio", response_model=List[AudioMetadataResponse])
def get_verse_audio_metadata(
    verse_id: int,
    language: Optional[str] = Query(None, description="Filter by language (ar, en, te)"),
    reciter: Optional[str] = Query(None, description="Filter by reciter"),
    db: Session = Depends(get_db)
):
    """
    Get audio metadata for a specific verse
    """
    # Check if verse exists
    verse = db.query(Verse).filter(Verse.id == verse_id).first()
    if not verse:
        raise HTTPException(status_code=404, detail=f"Verse {verse_id} not found")
    
    # Query audio tracks
    query = db.query(AudioTrack).filter(AudioTrack.verse_id == verse_id)
    
    # Apply filters
    if language:
        # Note: language info would need to be added to AudioTrack model
        # For now, we'll filter by reciter which may include language info
        pass
    
    if reciter:
        query = query.filter(AudioTrack.reciter == reciter)
    
    audio_tracks = query.all()
    
    return audio_tracks


@router.get("/verses/{verse_id}/audio/stream")
async def stream_verse_audio(
    verse_id: int,
    language: str = Query("ar", description="Language: ar, en, or te"),
    reciter: str = Query("default", description="Reciter identifier"),
    range: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Stream audio file for a verse with range request support
    """
    # Check if verse exists
    verse = db.query(Verse).filter(Verse.id == verse_id).first()
    if not verse:
        raise HTTPException(status_code=404, detail=f"Verse {verse_id} not found")
    
    # Get audio file path
    audio_path = get_audio_path(verse_id, language, reciter)
    
    # Stream the file
    return stream_audio_file(audio_path, range)


@router.post("/bookmarks", response_model=BookmarkResponse, status_code=201)
def create_bookmark(
    bookmark: BookmarkCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new bookmark
    """
    # Check if verse exists
    verse = db.query(Verse).filter(Verse.id == bookmark.verse_id).first()
    if not verse:
        raise HTTPException(status_code=404, detail=f"Verse {bookmark.verse_id} not found")
    
    # Check if bookmark already exists for this user and verse
    existing = db.query(Bookmark).filter(
        Bookmark.verse_id == bookmark.verse_id,
        Bookmark.user_id == bookmark.user_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Bookmark already exists for this verse and user"
        )
    
    # Create new bookmark
    db_bookmark = Bookmark(
        verse_id=bookmark.verse_id,
        user_id=bookmark.user_id,
        note=bookmark.note
    )
    
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)
    
    return db_bookmark


@router.get("/bookmarks", response_model=List[BookmarkWithVerseResponse])
def list_bookmarks(
    user_id: str = Query(..., description="User ID or session ID"),
    include_verses: bool = Query(True, description="Include verse details"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List all bookmarks for a user
    """
    query = db.query(Bookmark).filter(Bookmark.user_id == user_id)
    
    if include_verses:
        query = query.options(
            joinedload(Bookmark.verse)
            .joinedload(Verse.translations)
        )
        query = query.options(
            joinedload(Bookmark.verse)
            .joinedload(Verse.surah)
        )
    
    bookmarks = query.offset(skip).limit(limit).all()
    
    return bookmarks


@router.delete("/bookmarks/{bookmark_id}", status_code=204)
def delete_bookmark(
    bookmark_id: int,
    user_id: str = Query(..., description="User ID for verification"),
    db: Session = Depends(get_db)
):
    """
    Delete a bookmark
    """
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    # Verify ownership
    if bookmark.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this bookmark"
        )
    
    db.delete(bookmark)
    db.commit()
    
    return None


@router.get("/search", response_model=SearchResponse)
def search_verses(
    q: str = Query(..., min_length=1, description="Search query"),
    lang: str = Query("en", description="Language: en, ar, or te"),
    search_type: str = Query("hybrid", description="Search type: exact, fuzzy, semantic, or hybrid"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Unified search endpoint for Quran verses
    Supports exact, fuzzy, semantic, and hybrid search
    """
    # Validate search type
    valid_types = ["exact", "fuzzy", "semantic", "hybrid"]
    if search_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid search_type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Perform search based on type
    if search_type == "exact":
        results = exact_search(db, q, lang, limit)
    elif search_type == "fuzzy":
        results = fuzzy_search(db, q, lang, limit)
    elif search_type == "semantic":
        results = semantic_search(db, q, lang, limit)
        if not results:
            # Fallback to fuzzy if semantic not available
            results = fuzzy_search(db, q, lang, limit)
            search_type = "fuzzy (semantic fallback)"
    else:  # hybrid
        results = hybrid_search(db, q, lang, limit)
    
    return SearchResponse(
        query=q,
        results=results,
        total=len(results),
        search_type=search_type
    )


@router.post("/qa/ask", response_model=QAResponse)
def ask_question(
    request: QARequest,
    db: Session = Depends(get_db)
):
    """
    Q&A endpoint - Ask questions about the Quran and get answers with verse citations
    Uses semantic search to find relevant verses and provides contextual answers
    """
    import time
    start_time = time.time()
    
    # Use semantic search to find relevant verses
    try:
        # Try semantic search first
        search_results = semantic_search(db, request.question, request.language, request.max_verses)
        
        # If semantic search returns no results (no embeddings), fall back to hybrid search
        if not search_results:
            search_results = hybrid_search(db, request.question, request.language, request.max_verses)
        
    except Exception as e:
        # If search fails, fall back to fuzzy search
        print(f"Search error in Q&A: {e}")
        search_results = fuzzy_search(db, request.question, request.language, request.max_verses)
    
    # Convert search results to cited verses
    cited_verses = []
    for result in search_results:
        # Get full verse details with translations
        verse = db.query(Verse).options(
            joinedload(Verse.translations),
            joinedload(Verse.surah)
        ).filter(Verse.id == result.verse_id).first()
        
        if verse:
            cited_verses.append(CitedVerse(
                verse_id=verse.id,
                surah_number=verse.surah.number,
                verse_number=verse.verse_number,
                surah_name=verse.surah.name_english,
                text_arabic=verse.text_arabic,
                text_transliteration=verse.text_transliteration,
                translations=[
                    {
                        "id": t.id,
                        "language": t.language,
                        "translator": t.translator,
                        "text": t.text,
                        "license": t.license,
                        "source": t.source
                    }
                    for t in verse.translations
                ],
                relevance_score=result.score
            ))
    
    # Generate answer based on found verses
    if cited_verses:
        # Build a contextual answer
        answer = f"Based on the Quran, {len(cited_verses)} relevant verse(s) address this topic. "
        
        # Add specific context based on the question
        if "patience" in request.question.lower() or "sabr" in request.question.lower():
            answer += "The Quran emphasizes patience (sabr) as a fundamental virtue for believers. It teaches that patience is essential during times of hardship and that Allah is with those who are patient."
        elif "prayer" in request.question.lower() or "salah" in request.question.lower():
            answer += "Prayer (salah) is one of the five pillars of Islam. The Quran repeatedly emphasizes its importance and commands believers to establish regular prayer."
        elif "charity" in request.question.lower() or "zakah" in request.question.lower() or "sadaqah" in request.question.lower():
            answer += "Charity is highly emphasized in the Quran. Believers are encouraged to give from what they have been provided, and charity purifies wealth and souls."
        elif "forgiveness" in request.question.lower() or "mercy" in request.question.lower():
            answer += "Allah's mercy and forgiveness are recurring themes in the Quran. Believers are encouraged to seek forgiveness and to show mercy and forgiveness to others."
        elif "paradise" in request.question.lower() or "jannah" in request.question.lower() or "heaven" in request.question.lower():
            answer += "The Quran describes Paradise (Jannah) as a reward for believers who do righteous deeds. It is depicted as a place of eternal bliss with gardens, rivers, and the pleasure of Allah."
        elif "hell" in request.question.lower() or "jahannam" in request.question.lower():
            answer += "The Quran warns about Hell (Jahannam) as a consequence for those who reject faith and commit wrongdoing. It serves as a reminder to stay on the righteous path."
        else:
            # Generic answer for other questions
            answer += "The following verses provide relevant guidance on this topic."
        
        confidence_score = sum(v.relevance_score for v in cited_verses) / len(cited_verses) if cited_verses else 0.0
    else:
        answer = "I couldn't find specific verses directly addressing this question. Try rephrasing your question or using different keywords."
        confidence_score = 0.0
    
    processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    return QAResponse(
        question=request.question,
        answer=answer,
        cited_verses=cited_verses,
        confidence_score=confidence_score,
        processing_time_ms=processing_time
    )


# Admin endpoints
admin_router = APIRouter(prefix="/admin", tags=["admin"])


@admin_router.post("/ingest/scrape", response_model=IngestResponse)
async def run_scraper(
    request: IngestRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_admin_token),
    db: Session = Depends(get_db)
):
    """
    Admin endpoint to run data scraping and ingestion
    Protected with admin token authentication
    """
    try:
        # Run the scraping script
        if request.surah_numbers:
            # Scrape specific surahs
            for surah_num in request.surah_numbers:
                subprocess.run(
                    [sys.executable, "scrape_quran.py", "--surah", str(surah_num)],
                    cwd="/home/runner/work/Deen-Hidaya/Deen-Hidaya/backend",
                    check=True,
                    capture_output=True,
                    text=True
                )
            message = f"Scraped {len(request.surah_numbers)} surahs"
        else:
            # Scrape all
            subprocess.run(
                [sys.executable, "scrape_quran.py"],
                cwd="/home/runner/work/Deen-Hidaya/Deen-Hidaya/backend",
                check=True,
                capture_output=True,
                text=True
            )
            message = "Scraped all surahs"
        
        # Run the ingestion script
        result = subprocess.run(
            [sys.executable, "ingest_data.py"],
            cwd="/home/runner/work/Deen-Hidaya/Deen-Hidaya/backend",
            check=True,
            capture_output=True,
            text=True
        )
        
        # Count processed verses
        verses_count = db.query(Verse).count()
        
        return IngestResponse(
            status="success",
            message=message + " and ingested successfully",
            surahs_processed=request.surah_numbers or list(range(1, 115)),
            verses_processed=verses_count
        )
    
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scraping/ingestion failed: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )


@admin_router.post("/embed/verse", response_model=EmbedResponse)
async def create_embeddings(
    request: EmbedRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_admin_token),
    db: Session = Depends(get_db)
):
    """
    Admin endpoint to create embeddings for verses
    Protected with admin token authentication
    
    This endpoint generates vector embeddings for verses to enable semantic search.
    Embeddings can be created for specific verses or all verses in the database.
    
    Args:
        request: EmbedRequest with optional verse_ids, model, and language
        background_tasks: FastAPI background tasks
        token: Admin authentication token
        db: Database session
        
    Returns:
        EmbedResponse with status and count of embedded verses
    """
    try:
        # Initialize embedding service
        embedding_service = EmbeddingService()
        
        if not embedding_service.client:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
            )
        
        # Determine which verses to embed
        if request.verse_ids:
            # Embed specific verses
            verse_ids = request.verse_ids
            message = f"Embedding {len(verse_ids)} verses"
        else:
            # Embed all verses
            all_verses = db.query(Verse.id).all()
            verse_ids = [v.id for v in all_verses]
            message = f"Embedding all {len(verse_ids)} verses"
        
        # Create embeddings in batch
        result = embedding_service.create_embeddings_batch(
            verse_ids=verse_ids,
            language=request.language,
            db=db
        )
        
        success_count = result["success"]
        error_count = result["errors"]
        
        if error_count > 0:
            status = "partial_success"
            message = f"Embedded {success_count} verses successfully, {error_count} failed"
        else:
            status = "success"
            message = f"Successfully embedded {success_count} verses in {request.language}"
        
        return EmbedResponse(
            status=status,
            message=message,
            verses_embedded=success_count
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Embedding creation failed: {str(e)}"
        )


# Include admin router
router.include_router(admin_router)
