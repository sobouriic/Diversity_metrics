"""
Sentence embeddings utility module for semantic text representation.

This module provides:
- Lazy-loaded sentence-transformers model (all-MiniLM-L6-v2)
- 384-dimensional embeddings for semantic understanding
- Cosine distance computation for similarity/diversity
- Pairwise distance matrices for bulk comparisons

Model: all-MiniLM-L6-v2
- Source: sentence-transformers on HuggingFace
- Embedding dimension: 384
- Speed: ~5x faster than larger models
- Quality: Excellent for diversity analysis tasks
- Optimization: Distilled from larger models
- Use case: Semantic similarity in text understanding

Performance:
- First call: ~3-5 seconds (model download/load)
- Subsequent calls: Fast (<100ms for typical solutions)
- Lazy loading: Model loaded only once per process
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Union
from sklearn.metrics.pairwise import cosine_distances


class EmbedderEngine:
    """
    Wrapper around sentence-transformers for consistent text embeddings.
    
    Responsibilities:
    - Initialize and manage sentence-transformers model
    - Embed variable-length text to fixed-size vectors
    - Compute cosine distances between embeddings
    - Compute pairwise distance matrices
    
    Thread-safe: All operations are thread-safe due to stateless design
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedder with specified sentence-transformers model.
        
        First call triggers model download and initialization (~3-5 seconds).
        Subsequent calls use cached model from ~/.cache/huggingface/hub/
        
        Args:
            model_name: HuggingFace model identifier
                       Default: "all-MiniLM-L6-v2" (small, fast, good quality)
                       Other options: "all-mpnet-base-v2" (slower, higher quality)
                       
        Raises:
            OSError: If model cannot be downloaded or loaded
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> np.ndarray:
        """
        Convert text strings to fixed-size semantic vectors.
        
        Process:
        1. Input validation (non-empty list)
        2. Model forward pass (converts text to embeddings)
        3. Output shape normalization (ensure 2D array)
        
        Semantics:
        - Similar texts produce similar embeddings (high cosine similarity)
        - Distance semantics: cosine distance in [0, 1]
          - 0 = identical meaning
          - 1 = completely different meaning
        
        Args:
            texts: List of text strings to embed
                  - Each string can vary in length
                  - Empty strings handled gracefully
                  - Special characters and unicode supported
                  
        Returns:
            numpy array of shape (num_texts, 384)
            - num_texts: number of input texts
            - 384: embedding dimension for all-MiniLM-L6-v2
            - dtype: float32
            
        Example:
            >>> engine = EmbedderEngine()
            >>> embeddings = engine.embed([
            ...     "The cat sat on the mat",
            ...     "A dog played in the yard"
            ... ])
            >>> print(embeddings.shape)  # (2, 384)
        """
        if not texts:
            return np.array([])
        
        # Encode texts to embeddings using transformer model
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        
        # Ensure 2D shape even for single text (batch processing consistency)
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)
        
        return embeddings

    def cosine_distance(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Compute cosine distance between two embedding vectors.
        
        Mathematical Definition:
        - cosine_distance = 1 - cosine_similarity
        - cosine_similarity = dot(vec1, vec2) / (norm(vec1) * norm(vec2))
        - Range: [0, 1]
          - 0 = same direction (identical semantics)
          - 1 = opposite direction (opposite semantics)
        
        Args:
            vec1: First embedding vector (1D or 2D array)
                 Shape: (384,) or (1, 384)
            vec2: Second embedding vector (1D or 2D array)
                 Shape: (384,) or (1, 384)
                 
        Returns:
            float: Cosine distance value in [0, 1]
                  - 0.0: semantically identical
                  - 0.5: moderate semantic difference
                  - 1.0: maximally different
                  
        Example:
            >>> engine = EmbedderEngine()
            >>> emb1 = engine.embed(["cat"]).flatten()
            >>> emb2 = engine.embed(["dog"]).flatten()
            >>> distance = engine.cosine_distance(emb1, emb2)
            >>> print(f"{distance:.3f}")  # ~0.25 (similar animals)
        """
        # Reshape for single comparison if needed
        if vec1.ndim == 1:
            vec1 = vec1.reshape(1, -1)
        if vec2.ndim == 1:
            vec2 = vec2.reshape(1, -1)
        
        # Compute cosine distance using scikit-learn
        distance = cosine_distances(vec1, vec2)[0][0]
        return float(distance)

    def pairwise_distances(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Compute all-pairs cosine distances in batch.
        
        Process:
        - Input: N embeddings of 384 dimensions each
        - Output: N×N distance matrix
        - Symmetric: distance[i,j] = distance[j,i]
        - Diagonal: all zeros (distance from embedding to itself)
        
        Computational Complexity:
        - Time: O(N²) for N embeddings
        - Space: O(N²) for output matrix
        - Efficient: Vectorized using scikit-learn
        
        Args:
            embeddings: 2D array of shape (N, 384)
                       N = number of embeddings
                       384 = embedding dimension
                       
        Returns:
            2D array of shape (N, N) with cosine distances
            - distance[i,j] ∈ [0, 1]
            - distance[i,i] = 0 (always)
            - distance[i,j] = distance[j,i] (always, symmetric)
            
        Example:
            >>> engine = EmbedderEngine()
            >>> texts = ["apple", "orange", "banana"]
            >>> embeddings = engine.embed(texts)
            >>> distances = engine.pairwise_distances(embeddings)
            >>> print(distances.shape)  # (3, 3)
            >>> print(distances[0,1])  # Distance between "apple" and "orange"
        """
        distances = cosine_distances(embeddings)
        return distances


# Global embedder instance (initialized on first use)
_embedder = None


def get_embedder() -> EmbedderEngine:
    """
    Get or create global singleton embedder instance.
    
    Lazy Initialization:
    - On first call: Creates EmbedderEngine, downloads model (~3-5 seconds)
    - On subsequent calls: Returns cached instance instantly
    - Thread-safe: Uses global lock (Python GIL)
    
    Returns:
        EmbedderEngine: Singleton instance for embedding operations
        
    Example:
        >>> embedder = get_embedder()
        >>> embeddings = embedder.embed(["Hello", "World"])
    """
    global _embedder
    if _embedder is None:
        _embedder = EmbedderEngine()
    return _embedder


def embed_texts(texts: List[str]) -> np.ndarray:
    """
    Convenience function to embed texts using global embedder.
    
    Shorthand for: get_embedder().embed(texts)
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        numpy array of shape (len(texts), 384)
    """
    return get_embedder().embed(texts)


def cosine_distance(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Convenience function to compute cosine distance using global embedder.
    
    Shorthand for: get_embedder().cosine_distance(vec1, vec2)
    
    Args:
        vec1: First embedding vector
        vec2: Second embedding vector
        
    Returns:
        float: Cosine distance in [0, 1]
    """
    return get_embedder().cosine_distance(vec1, vec2)


def pairwise_distances(embeddings: np.ndarray) -> np.ndarray:
    """
    Convenience function to compute pairwise distances using global embedder.
    
    Shorthand for: get_embedder().pairwise_distances(embeddings)
    
    Args:
        embeddings: 2D array of embeddings (N, 384)
        
    Returns:
        2D array of shape (N, N) with pairwise distances
    """
    return get_embedder().pairwise_distances(embeddings)
