"""
Search utilities for Quran text search
Implements exact, fuzzy, and semantic search capabilities
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from models import Verse, Surah, Translation
from schemas import SearchResult, TranslationResponse


def exact_search(
    db: Session,
    query: str,
    language: str = "en",
    limit: int = 20
) -> List[SearchResult]:
    """
    Perform exact text search
    
    Args:
        db: Database session
        query: Search query
        language: Language to search in (en, ar, te)
        limit: Maximum number of results
        
    Returns:
        List of search results
    """
    results = []
    
    # Search in Arabic text
    if language == "ar":
        verses = (
            db.query(Verse)
            .filter(
                or_(
                    Verse.text_arabic.ilike(f"%{query}%"),
                    Verse.text_simple.ilike(f"%{query}%")
                )
            )
            .options(joinedload(Verse.surah))
            .options(joinedload(Verse.translations))
            .limit(limit)
            .all()
        )
    else:
        # Search in translations
        verses = (
            db.query(Verse)
            .join(Translation)
            .filter(
                Translation.language == language,
                Translation.text.ilike(f"%{query}%")
            )
            .options(joinedload(Verse.surah))
            .options(joinedload(Verse.translations))
            .limit(limit)
            .all()
        )
    
    for verse in verses:
        translations = [
            TranslationResponse(
                id=t.id,
                language=t.language,
                translator=t.translator,
                text=t.text,
                license=t.license,
                source=t.source
            )
            for t in verse.translations
        ]
        
        results.append(
            SearchResult(
                verse_id=verse.id,
                verse_number=verse.verse_number,
                surah_number=verse.surah.number,
                surah_name=verse.surah.name_english,
                text_arabic=verse.text_arabic,
                text_transliteration=verse.text_transliteration,
                translations=translations,
                score=1.0,  # Exact matches have highest score
                match_type="exact"
            )
        )
    
    return results


def fuzzy_search(
    db: Session,
    query: str,
    language: str = "en",
    limit: int = 20
) -> List[SearchResult]:
    """
    Perform fuzzy text search using PostgreSQL similarity
    Falls back to LIKE search if similarity function not available
    
    Args:
        db: Database session
        query: Search query
        language: Language to search in
        limit: Maximum number of results
        
    Returns:
        List of search results
    """
    results = []
    
    try:
        # Use PostgreSQL trigram similarity for fuzzy matching
        if language == "ar":
            verses = (
                db.query(
                    Verse,
                    func.similarity(Verse.text_simple, query).label("similarity")
                )
                .filter(func.similarity(Verse.text_simple, query) > 0.3)
                .order_by(func.similarity(Verse.text_simple, query).desc())
                .options(joinedload(Verse.surah))
                .options(joinedload(Verse.translations))
                .limit(limit)
                .all()
            )
        else:
            verses = (
                db.query(
                    Verse,
                    func.similarity(Translation.text, query).label("similarity")
                )
                .join(Translation)
                .filter(
                    Translation.language == language,
                    func.similarity(Translation.text, query) > 0.3
                )
                .order_by(func.similarity(Translation.text, query).desc())
                .options(joinedload(Verse.surah))
                .options(joinedload(Verse.translations))
                .limit(limit)
                .all()
            )
        
        for verse, similarity in verses:
            translations = [
                TranslationResponse(
                    id=t.id,
                    language=t.language,
                    translator=t.translator,
                    text=t.text,
                    license=t.license,
                    source=t.source
                )
                for t in verse.translations
            ]
            
            results.append(
                SearchResult(
                    verse_id=verse.id,
                    verse_number=verse.verse_number,
                    surah_number=verse.surah.number,
                    surah_name=verse.surah.name_english,
                    text_arabic=verse.text_arabic,
                    text_transliteration=verse.text_transliteration,
                    translations=translations,
                    score=float(similarity),
                    match_type="fuzzy"
                )
            )
    except Exception:
        # Fallback to LIKE search if similarity function not available (e.g., in SQLite)
        return exact_search(db, query, language, limit)
    
    return results


def semantic_search(
    db: Session,
    query: str,
    language: str = "en",
    limit: int = 20
) -> List[SearchResult]:
    """
    Perform semantic search using embeddings
    Note: This is a placeholder. Full implementation requires embedding generation
    
    Args:
        db: Database session
        query: Search query
        language: Language to search in
        limit: Maximum number of results
        
    Returns:
        List of search results (currently returns empty list)
    """
    # TODO: Implement semantic search with embeddings
    # This will be fully implemented in issue #7
    # For now, return empty list or fall back to fuzzy search
    return []


def hybrid_search(
    db: Session,
    query: str,
    language: str = "en",
    limit: int = 20
) -> List[SearchResult]:
    """
    Perform hybrid search combining exact, fuzzy, and semantic results
    
    Args:
        db: Database session
        query: Search query
        language: Language to search in
        limit: Maximum number of results
        
    Returns:
        Combined and ranked search results
    """
    # Get results from all search types
    exact_results = exact_search(db, query, language, limit=10)
    fuzzy_results = fuzzy_search(db, query, language, limit=10)
    semantic_results = semantic_search(db, query, language, limit=10)
    
    # Combine and deduplicate results
    seen_verse_ids = set()
    combined_results = []
    
    # Add results with weighted scores
    # Exact matches get highest priority
    for result in exact_results:
        if result.verse_id not in seen_verse_ids:
            seen_verse_ids.add(result.verse_id)
            combined_results.append(result)
    
    # Add fuzzy matches with adjusted scores
    for result in fuzzy_results:
        if result.verse_id not in seen_verse_ids:
            seen_verse_ids.add(result.verse_id)
            result.score = result.score * 0.8  # Weight fuzzy matches lower
            result.match_type = "fuzzy"
            combined_results.append(result)
    
    # Add semantic matches with adjusted scores
    for result in semantic_results:
        if result.verse_id not in seen_verse_ids:
            seen_verse_ids.add(result.verse_id)
            result.score = result.score * 0.7  # Weight semantic matches lower
            result.match_type = "semantic"
            combined_results.append(result)
    
    # Sort by score
    combined_results.sort(key=lambda x: x.score, reverse=True)
    
    return combined_results[:limit]
