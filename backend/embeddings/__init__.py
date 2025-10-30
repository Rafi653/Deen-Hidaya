"""
Embedding service factory module
Provides auto-selection of embedding backend based on available dependencies
"""
import os
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)


def get_embedding_service(backend: str = "auto", **kwargs) -> Optional[Any]:
    """
    Factory function to get an embedding service instance.
    
    Auto-selects the best available backend:
    1. If backend="sbert" or auto and sentence-transformers is available: use SBERT
    2. If backend="openai" or SBERT not available and openai is available: use OpenAI
    3. If backend="disabled": return None (disabled mode)
    
    Args:
        backend: Backend to use ("auto", "sbert", "openai", or "disabled")
        **kwargs: Additional arguments passed to the backend constructor
        
    Returns:
        Embedding service instance or None if disabled
    """
    # Allow environment variable override
    backend = os.getenv("EMBEDDING_BACKEND", backend).lower()
    
    if backend == "disabled":
        logger.info("Embedding service disabled by configuration")
        return None
    
    # Try SBERT first (preferred for local/free operation)
    if backend in ("auto", "sbert"):
        try:
            from embeddings.sbert_faiss import EmbeddingServiceSBERT
            
            # Get model name from kwargs or environment
            model_name = kwargs.get("model_name") or os.getenv(
                "EMBEDDING_MODEL", 
                "paraphrase-multilingual-MiniLM-L12-v2"
            )
            device = kwargs.get("device") or os.getenv("EMBEDDING_DEVICE", "cpu")
            
            logger.info(f"Using SBERT backend with model: {model_name}")
            return EmbeddingServiceSBERT(model_name=model_name, device=device)
            
        except ImportError as e:
            if backend == "sbert":
                logger.error(f"SBERT backend requested but not available: {e}")
                raise
            logger.info("SBERT backend not available, trying OpenAI...")
    
    # Try OpenAI as fallback
    if backend in ("auto", "openai"):
        try:
            from embedding_service import EmbeddingService
            
            api_key = kwargs.get("api_key") or os.getenv("OPENAI_API_KEY")
            if not api_key:
                if backend == "openai":
                    logger.error("OpenAI backend requested but OPENAI_API_KEY not set")
                    raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI backend")
                logger.warning("OpenAI API key not found, embedding service disabled")
                return None
            
            logger.info("Using OpenAI backend")
            return EmbeddingService(api_key=api_key)
            
        except ImportError as e:
            if backend == "openai":
                logger.error(f"OpenAI backend requested but not available: {e}")
                raise
            logger.warning("OpenAI backend not available")
    
    # If we get here, no backend is available
    if backend == "auto":
        logger.warning("No embedding backend available. Install sentence-transformers or set OPENAI_API_KEY")
        return None
    
    raise ValueError(f"Unknown embedding backend: {backend}")


def get_embedding_dimension(backend: str = "auto") -> int:
    """
    Get the embedding dimension for the specified backend.
    
    Args:
        backend: Backend to check ("auto", "sbert", "openai")
        
    Returns:
        Embedding dimension
    """
    backend = os.getenv("EMBEDDING_BACKEND", backend).lower()
    
    if backend in ("auto", "sbert"):
        try:
            # For SBERT, we need to instantiate to get dimension
            # Or we can use a lookup table for common models
            model_name = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
            
            # Common model dimensions
            model_dimensions = {
                "paraphrase-multilingual-MiniLM-L12-v2": 384,
                "all-MiniLM-L6-v2": 384,
                "all-mpnet-base-v2": 768,
                "paraphrase-MiniLM-L6-v2": 384,
            }
            
            if model_name in model_dimensions:
                return model_dimensions[model_name]
            
            # If not in lookup, instantiate model
            from embeddings.sbert_faiss import EmbeddingServiceSBERT
            service = EmbeddingServiceSBERT(model_name=model_name)
            return service.dimension
            
        except ImportError:
            pass
    
    # OpenAI default
    return int(os.getenv("EMBEDDING_DIMENSION", "1536"))


__all__ = ["get_embedding_service", "get_embedding_dimension"]
