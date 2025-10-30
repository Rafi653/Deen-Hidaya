"""
Unified embedding service that wraps both SBERT and OpenAI backends
Provides a consistent interface regardless of backend
"""
import os
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import numpy as np

logger = logging.getLogger(__name__)


class UnifiedEmbeddingService:
    """
    Unified embedding service that provides a consistent interface
    for both SBERT and OpenAI backends.
    
    This wrapper:
    - Provides the same API as the original EmbeddingService
    - Automatically selects the best available backend
    - Handles batch processing for both backends
    - Maintains compatibility with existing code
    """
    
    def __init__(self, backend: str = "auto", **kwargs):
        """
        Initialize the unified embedding service.
        
        Args:
            backend: Backend to use ("auto", "sbert", "openai", "disabled")
            **kwargs: Additional arguments passed to backend
        """
        from embeddings import get_embedding_service, get_embedding_dimension
        
        self.backend_name = backend
        self.backend = get_embedding_service(backend=backend, **kwargs)
        
        if self.backend is None:
            logger.warning("No embedding backend available")
            self.client = None
            self.model = "disabled"
            self.dimension = 0
        else:
            self.client = self.backend  # For compatibility checks
            
            # Determine model name and dimension based on backend
            if hasattr(self.backend, 'model_name'):
                # SBERT backend
                self.model = self.backend.model_name
                self.dimension = self.backend.dimension
            elif hasattr(self.backend, 'model'):
                # OpenAI backend
                self.model = self.backend.model
                self.dimension = self.backend.dimension
            else:
                self.model = os.getenv("EMBEDDING_MODEL", "unknown")
                self.dimension = get_embedding_dimension(backend)
        
        self.batch_size = 100
        logger.info(f"Initialized UnifiedEmbeddingService with backend: {self.backend_name}, model: {self.model}")
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector, or None if failed
        """
        if not self.backend:
            logger.error("No embedding backend available")
            return None
        
        try:
            return self.backend.generate_embedding(text)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts in batch.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors (same order as input)
        """
        if not self.backend:
            logger.error("No embedding backend available")
            return [None] * len(texts)
        
        try:
            # Check if backend has generate_embeddings (SBERT style)
            if hasattr(self.backend, 'generate_embeddings'):
                embeddings = self.backend.generate_embeddings(texts)
                # Convert numpy array to list of lists
                return [emb.tolist() for emb in embeddings]
            
            # Check if backend has generate_embeddings_batch (OpenAI style)
            elif hasattr(self.backend, 'generate_embeddings_batch'):
                return self.backend.generate_embeddings_batch(texts)
            
            # Fallback: generate one at a time
            else:
                return [self.generate_embedding(text) for text in texts]
                
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return [None] * len(texts)
    
    def get_verse_text_for_embedding(
        self, 
        verse, 
        language: str = "en",
        db: Optional[Session] = None
    ) -> Optional[str]:
        """
        Get the text to embed for a verse based on language.
        
        Args:
            verse: Verse object
            language: Language code ('ar' for Arabic, 'en' for English, etc.)
            db: Database session (required for translations)
            
        Returns:
            Text to embed, or None if not available
        """
        # Import here to avoid circular dependency
        from models import Translation
        
        if language == "ar":
            return verse.text_arabic
        else:
            if not db:
                logger.error("Database session required for translation lookup")
                return None
            
            translation = db.query(Translation).filter(
                Translation.verse_id == verse.id,
                Translation.language == language
            ).first()
            
            if translation:
                return translation.text
            else:
                logger.warning(f"No translation found for verse {verse.id} in language {language}")
                return None
    
    def create_verse_embedding(
        self, 
        verse, 
        language: str = "en",
        db: Session = None
    ):
        """
        Create or update embedding for a single verse.
        
        Args:
            verse: Verse object to embed
            language: Language of text to embed
            db: Database session
            
        Returns:
            Embedding object if successful, None otherwise
        """
        # Import here to avoid circular dependency
        from models import Embedding
        
        if not db:
            logger.error("Database session is required")
            return None
        
        if not self.backend:
            logger.error("No embedding backend available")
            return None
        
        # Get text to embed
        text = self.get_verse_text_for_embedding(verse, language, db)
        if not text:
            return None
        
        # Generate embedding
        embedding_vector = self.generate_embedding(text)
        if not embedding_vector:
            return None
        
        # Check if embedding already exists
        existing = db.query(Embedding).filter(
            Embedding.verse_id == verse.id,
            Embedding.model == self.model,
            Embedding.language == language
        ).first()
        
        if existing:
            existing.embedding_vector = embedding_vector
            existing.dimension = self.dimension
            db.commit()
            db.refresh(existing)
            logger.info(f"Updated embedding for verse {verse.id} ({language})")
            return existing
        else:
            new_embedding = Embedding(
                verse_id=verse.id,
                model=self.model,
                embedding_vector=embedding_vector,
                dimension=self.dimension,
                language=language
            )
            db.add(new_embedding)
            db.commit()
            db.refresh(new_embedding)
            logger.info(f"Created embedding for verse {verse.id} ({language})")
            return new_embedding
    
    def create_embeddings_batch(
        self,
        verse_ids: List[int],
        language: str = "en",
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Create embeddings for multiple verses in batch.
        
        Args:
            verse_ids: List of verse IDs to embed
            language: Language of text to embed
            db: Database session
            
        Returns:
            Dictionary with success count and error count
        """
        # Import here to avoid circular dependency
        from models import Verse, Embedding
        
        if not db:
            logger.error("Database session is required")
            return {"success": 0, "errors": 0}
        
        if not self.backend:
            logger.error("No embedding backend available")
            return {"success": 0, "errors": 0}
        
        success_count = 0
        error_count = 0
        
        # Process in batches
        for i in range(0, len(verse_ids), self.batch_size):
            batch_ids = verse_ids[i:i + self.batch_size]
            
            # Fetch verses
            verses = db.query(Verse).filter(Verse.id.in_(batch_ids)).all()
            
            # Get texts to embed
            texts = []
            valid_verses = []
            for verse in verses:
                text = self.get_verse_text_for_embedding(verse, language, db)
                if text:
                    texts.append(text)
                    valid_verses.append(verse)
                else:
                    error_count += 1
            
            if not texts:
                continue
            
            # Generate embeddings
            embeddings = self.generate_embeddings_batch(texts)
            
            # Save embeddings
            for verse, embedding_vector in zip(valid_verses, embeddings):
                if embedding_vector:
                    try:
                        # Check if embedding already exists
                        existing = db.query(Embedding).filter(
                            Embedding.verse_id == verse.id,
                            Embedding.model == self.model,
                            Embedding.language == language
                        ).first()
                        
                        if existing:
                            existing.embedding_vector = embedding_vector
                            existing.dimension = self.dimension
                        else:
                            new_embedding = Embedding(
                                verse_id=verse.id,
                                model=self.model,
                                embedding_vector=embedding_vector,
                                dimension=self.dimension,
                                language=language
                            )
                            db.add(new_embedding)
                        
                        success_count += 1
                    except Exception as e:
                        logger.error(f"Error saving embedding for verse {verse.id}: {e}")
                        error_count += 1
                else:
                    error_count += 1
            
            # Commit batch
            try:
                db.commit()
                logger.info(f"Committed batch of {len(valid_verses)} embeddings")
            except Exception as e:
                logger.error(f"Error committing batch: {e}")
                db.rollback()
                error_count += len(valid_verses)
                success_count -= len(valid_verses)
        
        return {"success": success_count, "errors": error_count}
    
    def create_embeddings_for_all_verses(
        self,
        language: str = "en",
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Create embeddings for all verses in the database.
        
        Args:
            language: Language of text to embed
            db: Database session
            
        Returns:
            Dictionary with success count and error count
        """
        from models import Verse
        
        if not db:
            logger.error("Database session is required")
            return {"success": 0, "errors": 0}
        
        # Get all verse IDs
        verse_ids = [v.id for v in db.query(Verse.id).all()]
        
        logger.info(f"Starting to embed {len(verse_ids)} verses in {language}")
        
        return self.create_embeddings_batch(verse_ids, language, db)
