"""
API routes for name suggestion service
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from database import get_db
from models import NameEntity, NameFavorite
from schemas import (
    NameSuggestionRequest, NameSuggestionResponse, NameEntityResponse,
    NameFavoriteCreate, NameFavoriteResponse
)
from name_suggestion_service import NameSuggestionService


router = APIRouter(prefix="/api/v1/names", tags=["names"])


@router.post("/suggest", response_model=NameSuggestionResponse)
def suggest_names(
    request: NameSuggestionRequest,
    db: Session = Depends(get_db)
):
    """
    Get name suggestions based on user preferences
    
    Supports multiple entity types: baby, pet, vehicle, company, toy, etc.
    Returns names ranked by relevance to user preferences.
    """
    service = NameSuggestionService(db)
    scored_names = service.suggest_names(request)
    
    # Convert to response format
    suggestions = []
    for item in scored_names:
        name_entity = item["name_entity"]
        response = NameEntityResponse(
            id=name_entity.id,
            name=name_entity.name,
            entity_type=name_entity.entity_type,
            subtype=name_entity.subtype,
            gender=name_entity.gender,
            meaning=name_entity.meaning,
            origin=name_entity.origin,
            phonetic=name_entity.phonetic,
            themes=name_entity.themes,
            associated_traits=name_entity.associated_traits,
            popularity_score=name_entity.popularity_score,
            relevance_score=item["relevance_score"]
        )
        suggestions.append(response)
    
    return NameSuggestionResponse(
        request=request,
        suggestions=suggestions,
        total=len(suggestions)
    )


@router.get("/entity-types", response_model=List[str])
def get_entity_types(db: Session = Depends(get_db)):
    """
    Get all available entity types (baby, pet, vehicle, company, toy, etc.)
    """
    service = NameSuggestionService(db)
    return service.get_entity_types()


@router.get("/subtypes/{entity_type}", response_model=List[str])
def get_subtypes(entity_type: str, db: Session = Depends(get_db)):
    """
    Get all available subtypes for a given entity type
    """
    service = NameSuggestionService(db)
    return service.get_subtypes(entity_type)


@router.get("/origins", response_model=List[str])
def get_origins(db: Session = Depends(get_db)):
    """
    Get all available cultural/linguistic origins
    """
    service = NameSuggestionService(db)
    return service.get_origins()


@router.get("/themes", response_model=List[str])
def get_themes(db: Session = Depends(get_db)):
    """
    Get all available themes (classic, modern, playful, professional, etc.)
    """
    service = NameSuggestionService(db)
    return service.get_themes()


@router.get("/names/{name_id}", response_model=NameEntityResponse)
def get_name_by_id(name_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific name
    """
    name = db.query(NameEntity).filter(NameEntity.id == name_id).first()
    
    if not name:
        raise HTTPException(status_code=404, detail=f"Name with id {name_id} not found")
    
    return NameEntityResponse(
        id=name.id,
        name=name.name,
        entity_type=name.entity_type,
        subtype=name.subtype,
        gender=name.gender,
        meaning=name.meaning,
        origin=name.origin,
        phonetic=name.phonetic,
        themes=name.themes,
        associated_traits=name.associated_traits,
        popularity_score=name.popularity_score
    )


@router.post("/favorites", response_model=NameFavoriteResponse)
def create_favorite(
    favorite: NameFavoriteCreate,
    db: Session = Depends(get_db)
):
    """
    Add a name to user's favorites
    """
    # Check if name exists
    name_entity = db.query(NameEntity).filter(NameEntity.id == favorite.name_entity_id).first()
    if not name_entity:
        raise HTTPException(status_code=404, detail="Name not found")
    
    # Check if already favorited
    existing = db.query(NameFavorite).filter(
        NameFavorite.user_id == favorite.user_id,
        NameFavorite.name_entity_id == favorite.name_entity_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Name already in favorites")
    
    # Create favorite
    db_favorite = NameFavorite(
        name_entity_id=favorite.name_entity_id,
        user_id=favorite.user_id,
        note=favorite.note
    )
    
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    
    # Load the name_entity relationship
    db_favorite = db.query(NameFavorite)\
        .options(joinedload(NameFavorite.name_entity))\
        .filter(NameFavorite.id == db_favorite.id)\
        .first()
    
    return db_favorite


@router.get("/favorites/{user_id}", response_model=List[NameFavoriteResponse])
def get_user_favorites(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all favorites for a user
    """
    favorites = db.query(NameFavorite)\
        .options(joinedload(NameFavorite.name_entity))\
        .filter(NameFavorite.user_id == user_id)\
        .order_by(NameFavorite.created_at.desc())\
        .all()
    
    return favorites


@router.delete("/favorites/{favorite_id}")
def delete_favorite(
    favorite_id: int,
    user_id: str = Query(..., description="User ID for authorization"),
    db: Session = Depends(get_db)
):
    """
    Remove a name from user's favorites
    """
    favorite = db.query(NameFavorite).filter(
        NameFavorite.id == favorite_id,
        NameFavorite.user_id == user_id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    db.delete(favorite)
    db.commit()
    
    return {"message": "Favorite removed successfully"}


@router.get("/search", response_model=List[NameEntityResponse])
def search_names(
    query: str = Query(..., min_length=1, description="Search query"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """
    Search names by query string
    """
    search_query = db.query(NameEntity).filter(
        NameEntity.name.ilike(f"%{query}%")
    )
    
    if entity_type:
        search_query = search_query.filter(NameEntity.entity_type == entity_type)
    
    names = search_query.limit(limit).all()
    
    return [
        NameEntityResponse(
            id=name.id,
            name=name.name,
            entity_type=name.entity_type,
            subtype=name.subtype,
            gender=name.gender,
            meaning=name.meaning,
            origin=name.origin,
            phonetic=name.phonetic,
            themes=name.themes,
            associated_traits=name.associated_traits,
            popularity_score=name.popularity_score
        )
        for name in names
    ]
