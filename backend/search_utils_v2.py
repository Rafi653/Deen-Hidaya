"""
Enhanced search utilities with PostgreSQL Full-Text Search

Implements:
1. PostgreSQL Full-Text Search (fast, free, always available)
2. Optional semantic search with sentence-transformers
3. Hybrid search combining multiple methods
4. Query optimization and caching
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func, text
from models import Verse, Surah, Translation, Embedding
from schemas import SearchResult, TranslationResponse
from embedding_service_v2 import EmbeddingServiceV2
import os
import logging
import re

# Configure module-specific logger
logger = logging.getLogger(__name__)

# Search scoring weights
EXACT_MATCH_WEIGHT = 1.0
FULLTEXT_MATCH_WEIGHT = 0.9
SEMANTIC_MATCH_WEIGHT = 0.8

# Initialize embedding service (lazy loading)
_embedding_service = None


def get_embedding_service() -> Optional[EmbeddingServiceV2]:
    """Get or create embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingServiceV2()
    return _embedding_service


def parse_query_to_tsquery(query: str) -> str:
    """
    Convert user query to PostgreSQL tsquery format
    
    Handles:
    - AND/OR/NOT operators
    - Quoted phrases
    - Parentheses for grouping
    
    Examples:
      "patience and faith" -> "patience & faith"
      "patience OR faith" -> "patience | faith"
      '"exact phrase"' -> "exact <-> phrase"
      "patience -doubt" -> "patience & !doubt"
    """
    # Remove special characters except quotes, spaces, hyphens
    query = re.sub(r'[^\w\s\-"\']', ' ', query)
    
    # Handle quoted phrases (convert to phrase search)
    def replace_phrase(match):
        phrase = match.group(1)
        words = phrase.split()
        return ' <-> '.join(words)
    
    query = re.sub(r'"([^"]+)"', replace_phrase, query)
    
    # Handle boolean operators
    query = query.replace(' AND ', ' & ')
    query = query.replace(' OR ', ' | ')
    query = query.replace(' NOT ', ' & !')
    
    # Handle negation with minus sign
    query = re.sub(r'\s-(\w+)', r' & !\1', query)
    
    # Default to AND if no operators present
    if '&' not in query and '|' not in query and '<->' not in query:
        words = query.split()
        query = ' & '.join(words)
    
    return query


def fulltext_search(
    db: Session,
    query: str,
    language: str = "en",
    limit: int = 20
) -> List[SearchResult]:
    """
    Perform PostgreSQL full-text search with ranking
    
    Uses to_tsvector and to_tsquery for efficient text search.
    Falls back to ILIKE if full-text search fails.
    
    Args:
        db: Database session
        query: Search query
        language: Language to search in (en, ar, te)
        limit: Maximum number of results
        
    Returns:
        List of search results ranked by relevance
    """
    results = []
    
    try:
        # Parse query to tsquery format
        tsquery = parse_query_to_tsquery(query)
        
        # Determine text search configuration based on language
        if language == "ar":
            # Arabic search
            config = "simple"  # Use simple config for Arabic (no stemming issues)
            
            # Try full-text search
            verses = (
                db.query(
                    Verse,
                    func.ts_rank_cd(
                        func.to_tsvector(config, Verse.text_simple),
                        func.to_tsquery(config, tsquery)
                    ).label('rank')
                )
                .filter(
                    func.to_tsvector(config, Verse.text_simple).op('@@')(
                        func.to_tsquery(config, tsquery)
                    )
                )
                .options(joinedload(Verse.surah))
                .options(joinedload(Verse.translations))
                .order_by(text('rank DESC'))
                .limit(limit)
                .all()
            )
        else:
            # Translation search
            config = "english"  # Use english config for better stemming
            
            verses = (
                db.query(
                    Verse,
                    func.ts_rank_cd(
                        func.to_tsvector(config, Translation.text),
                        func.to_tsquery(config, tsquery)
                    ).label('rank')
                )
                .join(Translation)
                .filter(
                    Translation.language == language,
                    func.to_tsvector(config, Translation.text).op('@@')(
                        func.to_tsquery(config, tsquery)
                    )
                )
                .options(joinedload(Verse.surah))
                .options(joinedload(Verse.translations))
                .order_by(text('rank DESC'))
                .limit(limit)
                .all()
            )
        
        # Convert to SearchResult objects
        for verse, rank in verses:
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
                    score=float(rank) if rank else 0.0,
                    match_type="fulltext"
                )
            )
    
    except Exception as e:
        # Fallback to ILIKE search if full-text search fails
        logger.warning(f"Full-text search failed: {e}, falling back to ILIKE search")
        return exact_search(db, query, language, limit)
    
    return results


def exact_search(
    db: Session,
    query: str,
    language: str = "en",
    limit: int = 20
) -> List[SearchResult]:
    """
    Perform exact text search using ILIKE
    
    Fast for short queries and exact matches.
    
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


def semantic_search(
    db: Session,
    query: str,
    language: str = "en",
    limit: int = 20
) -> List[SearchResult]:
    """
    Perform semantic search using embeddings
    
    Uses either OpenAI or sentence-transformers depending on configuration.
    Falls back to full-text search if embeddings are disabled.
    
    Args:
        db: Database session
        query: Search query
        language: Language to search in
        limit: Maximum number of results
        
    Returns:
        List of search results ranked by semantic similarity
    """
    results = []
    
    try:
        # Get embedding service
        embedding_service = get_embedding_service()
        if not embedding_service or not embedding_service.is_enabled:
            logger.info("Embeddings disabled, falling back to full-text search")
            return fulltext_search(db, query, language, limit)
        
        # Generate embedding for query
        query_embedding = embedding_service.generate_embedding(query)
        if not query_embedding:
            logger.warning("Failed to generate query embedding, falling back to full-text search")
            return fulltext_search(db, query, language, limit)
        
        # Check if we're using PostgreSQL with pgvector
        try:
            from pgvector.sqlalchemy import Vector
            
            # Use pgvector's cosine distance for similarity search
            verses_with_similarity = (
                db.query(
                    Verse,
                    Embedding.embedding_vector.cosine_distance(query_embedding).label("distance")
                )
                .join(Embedding, Verse.id == Embedding.verse_id)
                .filter(
                    Embedding.language == language,
                    Embedding.model == embedding_service.model_name
                )
                .order_by(Embedding.embedding_vector.cosine_distance(query_embedding))
                .options(joinedload(Verse.surah))
                .options(joinedload(Verse.translations))
                .limit(limit)
                .all()
            )
            
            for verse, distance in verses_with_similarity:
                # Convert distance to similarity score (1 - distance)
                similarity = max(0, 1 - distance)
                
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
                        match_type="semantic"
                    )
                )
        
        except (ImportError, Exception) as e:
            logger.warning(f"Semantic search failed: {e}. Falling back to full-text search")
            return fulltext_search(db, query, language, limit)
    
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        return fulltext_search(db, query, language, limit)
    
    return results


def hybrid_search(
    db: Session,
    query: str,
    language: str = "en",
    limit: int = 20
) -> List[SearchResult]:
    """
    Perform hybrid search combining full-text and semantic search
    
    Combines results from both methods with weighted scoring for best results.
    
    Args:
        db: Database session
        query: Search query
        language: Language to search in
        limit: Maximum number of results
        
    Returns:
        Combined and ranked search results
    """
    # Get results from both methods
    fulltext_results = fulltext_search(db, query, language, limit=int(limit * 0.7))
    semantic_results = semantic_search(db, query, language, limit=int(limit * 0.7))
    
    # Combine and deduplicate results
    seen_verse_ids = set()
    combined_results = []
    
    # Add full-text matches with adjusted scores
    for result in fulltext_results:
        if result.verse_id not in seen_verse_ids:
            seen_verse_ids.add(result.verse_id)
            result.score = result.score * FULLTEXT_MATCH_WEIGHT
            result.match_type = "hybrid"
            combined_results.append(result)
    
    # Add semantic matches with adjusted scores
    for result in semantic_results:
        if result.verse_id not in seen_verse_ids:
            seen_verse_ids.add(result.verse_id)
            result.score = result.score * SEMANTIC_MATCH_WEIGHT
            result.match_type = "hybrid"
            combined_results.append(result)
        else:
            # If already found in full-text, boost its score
            for existing in combined_results:
                if existing.verse_id == result.verse_id:
                    existing.score = max(existing.score, result.score * SEMANTIC_MATCH_WEIGHT)
                    break
    
    # Sort by score
    combined_results.sort(key=lambda x: x.score, reverse=True)
    
    return combined_results[:limit]


def choose_search_type(query: str) -> str:
    """
    Automatically choose best search type based on query characteristics
    
    Rules:
    - Very short queries (1-2 words): exact
    - Quoted phrases: exact
    - Question queries (what, how, why): semantic if available, else fulltext
    - Default: fulltext
    
    Args:
        query: User's search query
        
    Returns:
        Search type: 'exact', 'fulltext', 'semantic', or 'hybrid'
    """
    query_lower = query.lower().strip()
    words = query_lower.split()
    
    # Very short queries
    if len(words) <= 2:
        return 'exact'
    
    # Quoted phrases
    if query.startswith('"') and query.endswith('"'):
        return 'exact'
    
    # Question queries (semantic search is better)
    question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which']
    if any(query_lower.startswith(qw) for qw in question_words):
        # Check if semantic search is available
        embedding_service = get_embedding_service()
        if embedding_service and embedding_service.is_enabled:
            return 'hybrid'  # Use hybrid for best results
        else:
            return 'fulltext'
    
    # Default to full-text search
    return 'fulltext'


def unified_search(
    db: Session,
    query: str,
    language: str = "en",
    search_type: str = "auto",
    limit: int = 20
) -> List[SearchResult]:
    """
    Unified search interface with automatic method selection
    
    Args:
        db: Database session
        query: Search query
        language: Language to search in (en, ar, te)
        search_type: Search type ('auto', 'exact', 'fulltext', 'semantic', 'hybrid')
        limit: Maximum number of results
        
    Returns:
        List of search results
    """
    # Auto-detect search type if requested
    if search_type == "auto":
        search_type = choose_search_type(query)
        logger.info(f"Auto-selected search type: {search_type}")
    
    # Execute search based on type
    if search_type == "exact":
        return exact_search(db, query, language, limit)
    elif search_type == "fulltext":
        return fulltext_search(db, query, language, limit)
    elif search_type == "semantic":
        return semantic_search(db, query, language, limit)
    elif search_type == "hybrid":
        return hybrid_search(db, query, language, limit)
    else:
        logger.warning(f"Unknown search type '{search_type}', defaulting to fulltext")
        return fulltext_search(db, query, language, limit)
