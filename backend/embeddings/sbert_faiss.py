"""
Local embedding service using Sentence-Transformers and FAISS
Provides zero-cost, offline embedding generation for semantic search
"""
import logging
from typing import List, Optional
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingServiceSBERT:
    """
    Embedding service using Sentence-Transformers (SBERT) and FAISS for local embedding generation.
    
    This service provides:
    - Local embedding generation without API calls
    - Multi-lingual support via paraphrase-multilingual models
    - FAISS indexing for fast similarity search
    - Float32 embeddings for compatibility with pgvector
    """
    
    def __init__(
        self, 
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
        device: str = "cpu"
    ):
        """
        Initialize the SBERT embedding service.
        
        Args:
            model_name: Name of the sentence-transformers model to use.
                       Default is "paraphrase-multilingual-MiniLM-L12-v2" (118MB),
                       which supports 50+ languages including English and Arabic.
            device: Device to run the model on ('cpu' or 'cuda').
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        self._dimension = None
        
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name, device=device)
            # Get embedding dimension from model
            self._dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"Loaded SBERT model '{model_name}' on {device} (dimension: {self._dimension})")
        except ImportError as e:
            logger.error("sentence-transformers not installed. Install with: pip install sentence-transformers")
            raise ImportError(
                "sentence-transformers is required for local embeddings. "
                "Install with: pip install sentence-transformers>=2.2"
            ) from e
        except Exception as e:
            logger.error(f"Failed to load SBERT model '{model_name}': {e}")
            raise
    
    @property
    def dimension(self) -> int:
        """Get the embedding dimension."""
        return self._dimension
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed.
            
        Returns:
            numpy array of shape (len(texts), dimension) with float32 dtype.
            Embeddings are normalized to unit length for cosine similarity.
        """
        if not self.model:
            raise RuntimeError("SBERT model not initialized")
        
        if not texts:
            return np.array([], dtype=np.float32).reshape(0, self._dimension)
        
        try:
            # Generate embeddings with sentence-transformers
            # convert_to_numpy=True ensures we get numpy arrays
            # normalize_embeddings=True normalizes to unit length for cosine similarity
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False
            )
            
            # Ensure float32 dtype for compatibility with pgvector and FAISS
            embeddings = embeddings.astype(np.float32)
            
            logger.debug(f"Generated {len(embeddings)} embeddings of dimension {embeddings.shape[1]}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed.
            
        Returns:
            List of floats representing the embedding vector, or None if failed.
        """
        try:
            embeddings = self.generate_embeddings([text])
            if len(embeddings) > 0:
                return embeddings[0].tolist()
            return None
        except Exception as e:
            logger.error(f"Error generating single embedding: {e}")
            return None
    
    def build_faiss_index(self, embeddings: np.ndarray):
        """
        Build a FAISS index from embeddings for fast similarity search.
        
        Args:
            embeddings: numpy array of embeddings (shape: [n_samples, dimension])
            
        Returns:
            FAISS index (IndexFlatIP for normalized vectors = cosine similarity)
        """
        try:
            import faiss
        except ImportError as e:
            logger.error("faiss not installed. Install with: pip install faiss-cpu")
            raise ImportError(
                "faiss-cpu is required for FAISS indexing. "
                "Install with: pip install faiss-cpu"
            ) from e
        
        if embeddings.shape[0] == 0:
            logger.warning("No embeddings provided to build FAISS index")
            return None
        
        # Ensure embeddings are float32
        embeddings = embeddings.astype(np.float32)
        
        # Use IndexFlatIP (Inner Product) for normalized vectors
        # Since vectors are normalized, inner product = cosine similarity
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        
        # Add vectors to index
        index.add(embeddings)
        
        logger.info(f"Built FAISS index with {index.ntotal} vectors of dimension {dimension}")
        return index
    
    def save_index(self, index, path: str):
        """
        Save FAISS index to disk.
        
        Args:
            index: FAISS index to save
            path: Path to save the index file
        """
        try:
            import faiss
            faiss.write_index(index, path)
            logger.info(f"Saved FAISS index to {path}")
        except ImportError:
            logger.error("faiss not installed")
            raise
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
            raise
    
    def load_index(self, path: str):
        """
        Load FAISS index from disk.
        
        Args:
            path: Path to the index file
            
        Returns:
            Loaded FAISS index
        """
        try:
            import faiss
            index = faiss.read_index(path)
            logger.info(f"Loaded FAISS index from {path} ({index.ntotal} vectors)")
            return index
        except ImportError:
            logger.error("faiss not installed")
            raise
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
            raise
    
    def search(self, index, query_embedding: np.ndarray, k: int = 10):
        """
        Search for similar vectors in the FAISS index.
        
        Args:
            index: FAISS index to search
            query_embedding: Query embedding (shape: [dimension] or [1, dimension])
            k: Number of nearest neighbors to return
            
        Returns:
            Tuple of (distances, indices) arrays
        """
        # Ensure query is 2D array
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Ensure float32
        query_embedding = query_embedding.astype(np.float32)
        
        # Search index
        distances, indices = index.search(query_embedding, k)
        
        return distances[0], indices[0]
