"""
Enhanced Embedding Service with Multiple Backend Support

Supports:
1. OpenAI (legacy, requires API key, has costs)
2. Sentence-Transformers (free, local, recommended)
3. Disabled (falls back to full-text search)
"""
import os
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from models import Verse, Embedding, Translation
import numpy as np
from functools import lru_cache

# Configure module-specific logger
logger = logging.getLogger(__name__)


class EmbeddingBackend:
    """Base class for embedding backends"""
    
    def __init__(self):
        self.dimension = 384
        self.model_name = "unknown"
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for a single text"""
        raise NotImplementedError
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts"""
        return [self.generate_embedding(text) for text in texts]


class OpenAIBackend(EmbeddingBackend):
    """OpenAI embedding backend (requires API key, has costs)"""
    
    def __init__(self, api_key: str):
        super().__init__()
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self.model_name = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
            self.dimension = 1536
            logger.info(f"Initialized OpenAI backend with model {self.model_name}")
        except ImportError:
            logger.error("OpenAI library not installed. Install with: pip install openai")
            raise
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding using OpenAI API"""
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model_name
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating OpenAI embedding: {e}")
            return None
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embeddings in batch using OpenAI API"""
        try:
            response = self.client.embeddings.create(
                input=texts,
                model=self.model_name
            )
            embeddings = sorted(response.data, key=lambda x: x.index)
            return [emb.embedding for emb in embeddings]
        except Exception as e:
            logger.error(f"Error generating OpenAI batch embeddings: {e}")
            return [None] * len(texts)


class SentenceTransformerBackend(EmbeddingBackend):
    """Sentence-Transformers backend (free, local, no API needed)"""
    
    def __init__(self, model_name: str = None):
        super().__init__()
        try:
            from sentence_transformers import SentenceTransformer
            
            if model_name is None:
                # Default to multilingual model for Quran (Arabic, English, Telugu, etc.)
                model_name = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
            
            logger.info(f"Loading sentence-transformers model: {model_name}")
            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
            
            # Get dimension from model
            self.dimension = self.model.get_sentence_embedding_dimension()
            
            logger.info(f"Initialized SentenceTransformer backend: {model_name} (dim={self.dimension})")
            
        except ImportError:
            logger.error("sentence-transformers library not installed. Install with: pip install sentence-transformers")
            raise
        except Exception as e:
            logger.error(f"Error loading sentence-transformers model: {e}")
            raise
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding using sentence-transformers"""
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating sentence-transformer embedding: {e}")
            return None
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embeddings in batch using sentence-transformers"""
        try:
            embeddings = self.model.encode(
                texts, 
                batch_size=32,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Error generating sentence-transformer batch embeddings: {e}")
            return [None] * len(texts)


class EmbeddingServiceV2:
    """
    Enhanced embedding service with multiple backend support
    
    Backend selection priority:
    1. If EMBEDDING_BACKEND env var is set, use that
    2. If OPENAI_API_KEY is set, use OpenAI
    3. Try sentence-transformers (free, local)
    4. Disable embeddings (fall back to full-text search)
    """
    
    def __init__(self, backend: str = None):
        """
        Initialize the embedding service
        
        Args:
            backend: Backend to use ('openai', 'sentence-transformers', 'disabled')
                    If None, auto-detect based on environment
        """
        self.backend = None
        self.backend_name = "disabled"
        
        # Determine backend
        if backend is None:
            backend = os.getenv("EMBEDDING_BACKEND", "auto")
        
        if backend == "auto":
            backend = self._auto_detect_backend()
        
        # Initialize backend
        if backend == "openai":
            self._init_openai_backend()
        elif backend == "sentence-transformers":
            self._init_sentence_transformer_backend()
        elif backend == "disabled":
            logger.info("Embeddings disabled, will use full-text search only")
        else:
            logger.warning(f"Unknown backend '{backend}', embeddings disabled")
        
        # Batch size for processing
        self.batch_size = 100
    
    def _auto_detect_backend(self) -> str:
        """Auto-detect which backend to use"""
        # Check if OpenAI API key is available
        if os.getenv("OPENAI_API_KEY"):
            logger.info("OPENAI_API_KEY found, using OpenAI backend")
            return "openai"
        
        # Check if sentence-transformers is available
        try:
            import sentence_transformers
            logger.info("sentence-transformers available, using local embedding backend")
            return "sentence-transformers"
        except ImportError:
            pass
        
        # No backend available
        logger.info("No embedding backend available, embeddings disabled")
        return "disabled"
    
    def _init_openai_backend(self):
        """Initialize OpenAI backend"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY not found")
            return
        
        try:
            self.backend = OpenAIBackend(api_key)
            self.backend_name = "openai"
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI backend: {e}")
    
    def _init_sentence_transformer_backend(self):
        """Initialize sentence-transformers backend"""
        try:
            model_name = os.getenv("EMBEDDING_MODEL")
            self.backend = SentenceTransformerBackend(model_name)
            self.backend_name = "sentence-transformers"
        except Exception as e:
            logger.error(f"Failed to initialize sentence-transformers backend: {e}")
    
    @property
    def is_enabled(self) -> bool:
        """Check if embeddings are enabled"""
        return self.backend is not None
    
    @property
    def model_name(self) -> str:
        """Get current model name"""
        if self.backend:
            return self.backend.model_name
        return "disabled"
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension"""
        if self.backend:
            return self.backend.dimension
        return 0
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector, or None if disabled/failed
        """
        if not self.backend:
            logger.warning("Embeddings disabled, returning None")
            return None
        
        return self.backend.generate_embedding(text)
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts in batch
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors (same order as input)
        """
        if not self.backend:
            logger.warning("Embeddings disabled, returning None list")
            return [None] * len(texts)
        
        return self.backend.generate_embeddings_batch(texts)
    
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
            return verse.text_arabic or verse.text_simple
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
        if not self.is_enabled:
            logger.warning("Embeddings disabled, skipping")
            return None
        
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
            Embedding.model == self.model_name,
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
                model=self.model_name,
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
        if not self.is_enabled:
            logger.warning("Embeddings disabled, skipping")
            return {"success": 0, "errors": len(verse_ids), "skipped": len(verse_ids)}
        
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
                            Embedding.model == self.model_name,
                            Embedding.language == language
                        ).first()
                        
                        if existing:
                            existing.embedding_vector = embedding_vector
                            existing.dimension = self.dimension
                        else:
                            new_embedding = Embedding(
                                verse_id=verse.id,
                                model=self.model_name,
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
        if not self.is_enabled:
            logger.warning("Embeddings disabled, skipping")
            return {"success": 0, "errors": 0, "skipped": "all"}
        
        if not db:
            logger.error("Database session is required")
            return {"success": 0, "errors": 0}
        
        # Get all verse IDs
        verse_ids = [v.id for v in db.query(Verse.id).all()]
        
        logger.info(f"Starting to embed {len(verse_ids)} verses in {language} using {self.backend_name}")
        
        return self.create_embeddings_batch(verse_ids, language, db)
