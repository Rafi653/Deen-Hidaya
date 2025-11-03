"""
Name suggestion service with recommendation algorithm
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from models import NameEntity
from schemas import NameSuggestionRequest, NameEntityResponse


class NameSuggestionService:
    """Service for generating name suggestions based on user preferences"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def suggest_names(self, request: NameSuggestionRequest) -> List[Dict[str, Any]]:
        """
        Generate name suggestions based on user preferences with weighted relevance scoring
        
        Args:
            request: NameSuggestionRequest with user preferences
            
        Returns:
            List of name entities with relevance scores
        """
        # Start with base query filtered by entity type
        query = self.db.query(NameEntity).filter(NameEntity.entity_type == request.entity_type)
        
        # Apply filters based on provided preferences
        if request.subtype:
            query = query.filter(NameEntity.subtype == request.subtype)
        
        if request.gender:
            # Include unisex names along with the specified gender
            query = query.filter(
                or_(
                    NameEntity.gender == request.gender,
                    NameEntity.gender == 'unisex',
                    NameEntity.gender.is_(None)
                )
            )
        
        if request.origin:
            query = query.filter(NameEntity.origin.ilike(f"%{request.origin}%"))
        
        # Get all candidate names
        candidates = query.all()
        
        # Calculate relevance score for each candidate
        scored_names = []
        for name in candidates:
            score = self._calculate_relevance_score(name, request)
            scored_names.append({
                "name_entity": name,
                "relevance_score": score
            })
        
        # Sort by relevance score (descending) and limit results
        scored_names.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_names[:request.max_results]
    
    def _calculate_relevance_score(self, name: NameEntity, request: NameSuggestionRequest) -> float:
        """
        Calculate relevance score based on how well the name matches user preferences
        
        Scoring weights:
        - Base popularity: 20%
        - Meaning match: 25%
        - Theme match: 25%
        - Phonetic match: 15%
        - Origin match: 15%
        """
        score = 0.0
        max_score = 0.0
        
        # Base popularity score (weight: 0.2)
        score += (name.popularity_score or 0.5) * 0.2
        max_score += 0.2
        
        # Meaning match (weight: 0.25)
        if request.meaning and name.meaning:
            if self._text_similarity(request.meaning.lower(), name.meaning.lower()) > 0.5:
                score += 0.25
            elif any(word in name.meaning.lower() for word in request.meaning.lower().split()):
                score += 0.15
        max_score += 0.25
        
        # Theme match (weight: 0.25)
        if request.themes and name.themes:
            theme_overlap = len(set(request.themes) & set(name.themes))
            if theme_overlap > 0:
                score += (theme_overlap / len(request.themes)) * 0.25
        max_score += 0.25
        
        # Phonetic match (weight: 0.15)
        if request.phonetic_preference and name.phonetic:
            if self._phonetic_similarity(request.phonetic_preference.lower(), name.phonetic.lower()) > 0.5:
                score += 0.15
            elif request.phonetic_preference.lower() in name.phonetic.lower():
                score += 0.08
        max_score += 0.15
        
        # Origin match (weight: 0.15) - already filtered, so give full credit if it matches
        if request.origin and name.origin:
            if request.origin.lower() in name.origin.lower():
                score += 0.15
        max_score += 0.15
        
        # Normalize score to 0-1 range
        return score / max_score if max_score > 0 else 0.5
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity based on word overlap"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def _phonetic_similarity(self, pattern: str, phonetic: str) -> float:
        """Calculate phonetic similarity based on character overlap"""
        if not pattern or not phonetic:
            return 0.0
        
        # Simple character-based similarity
        pattern_chars = set(pattern)
        phonetic_chars = set(phonetic)
        
        intersection = pattern_chars & phonetic_chars
        union = pattern_chars | phonetic_chars
        
        return len(intersection) / len(union) if union else 0.0
    
    def get_entity_types(self) -> List[str]:
        """Get all available entity types"""
        result = self.db.query(NameEntity.entity_type).distinct().all()
        return [r[0] for r in result]
    
    def get_subtypes(self, entity_type: str) -> List[str]:
        """Get all available subtypes for a given entity type"""
        result = self.db.query(NameEntity.subtype)\
            .filter(NameEntity.entity_type == entity_type)\
            .filter(NameEntity.subtype.isnot(None))\
            .distinct()\
            .all()
        return [r[0] for r in result]
    
    def get_origins(self) -> List[str]:
        """Get all available origins"""
        result = self.db.query(NameEntity.origin)\
            .filter(NameEntity.origin.isnot(None))\
            .distinct()\
            .all()
        return [r[0] for r in result]
    
    def get_themes(self) -> List[str]:
        """Get all available themes"""
        # Get all names with themes
        names_with_themes = self.db.query(NameEntity.themes)\
            .filter(NameEntity.themes.isnot(None))\
            .all()
        
        # Extract unique themes from all names
        themes = set()
        for (theme_list,) in names_with_themes:
            if theme_list:
                themes.update(theme_list)
        
        return sorted(list(themes))
