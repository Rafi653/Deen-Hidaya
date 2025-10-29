"""
Embedding generation service for semantic search
Supports OpenAI embeddings with batch processing
"""
import os
import logging
from typing import List, Optional, Dict, Any
from openai import OpenAI
from sqlalchemy.orm import Session
from models import Verse, Embedding, Translation
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating and managing verse embeddings"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the embedding service
        
        Args:
            api_key: OpenAI API key (defaults to environment variable)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OpenAI API key not found. Embedding generation will not work.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
        
        self.model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        self.dimension = int(os.getenv("EMBEDDING_DIMENSION", "1536"))
        
        # Batch size for processing multiple verses
        self.batch_size = 100
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector, or None if failed
        """
        if not self.client:
            logger.error("OpenAI client not initialized. Check API key.")
            return None
        
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts in batch
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors (same order as input)
        """
        if not self.client:
            logger.error("OpenAI client not initialized. Check API key.")
            return [None] * len(texts)
        
        try:
            # OpenAI API supports batching up to 2048 texts
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            # Sort by index to maintain order
            embeddings = sorted(response.data, key=lambda x: x.index)
            return [emb.embedding for emb in embeddings]
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return [None] * len(texts)
    
    def get_verse_text_for_embedding(
        self, 
        verse: Verse, 
        language: str = "en",
        db: Optional[Session] = None
    ) -> Optional[str]:
        """
        Get the text to embed for a verse based on language
        
        Args:
            verse: Verse object
            language: Language code ('ar' for Arabic, 'en' for English, etc.)
            db: Database session (required for translations)
            
        Returns:
            Text to embed, or None if not available
        """
        if language == "ar":
            # Use Arabic text
            return verse.text_arabic
        else:
            # Use translation
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
        verse: Verse, 
        language: str = "en",
        db: Session = None
    ) -> Optional[Embedding]:
        """
        Create or update embedding for a single verse
        
        Args:
            verse: Verse object to embed
            language: Language of text to embed
            db: Database session
            
        Returns:
            Embedding object if successful, None otherwise
        """
        if not db:
            logger.error("Database session is required")
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
            # Update existing embedding
            existing.embedding_vector = embedding_vector
            existing.dimension = self.dimension
            db.commit()
            db.refresh(existing)
            logger.info(f"Updated embedding for verse {verse.id} ({language})")
            return existing
        else:
            # Create new embedding
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
        Create embeddings for multiple verses in batch
        
        Args:
            verse_ids: List of verse IDs to embed
            language: Language of text to embed
            db: Database session
            
        Returns:
            Dictionary with success count and error count
        """
        if not db:
            logger.error("Database session is required")
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
        Create embeddings for all verses in the database
        
        Args:
            language: Language of text to embed
            db: Database session
            
        Returns:
            Dictionary with success count and error count
        """
        if not db:
            logger.error("Database session is required")
            return {"success": 0, "errors": 0}
        
        # Get all verse IDs
        verse_ids = [v.id for v in db.query(Verse.id).all()]
        
        logger.info(f"Starting to embed {len(verse_ids)} verses in {language}")
        
        return self.create_embeddings_batch(verse_ids, language, db)
