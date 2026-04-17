import os
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_distances


class EmbedderEngine:

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
        self.model_name = os.getenv("EMBEDDINGS_MODEL", model_name)
        self.batch_size = self._env_int("EMBEDDING_BATCH_SIZE", 64, min_value=1)
        self.normalize_embeddings = self._env_bool("EMBEDDING_NORMALIZE", True)

        model_kwargs = {}
        configured_device = os.getenv("EMBEDDING_DEVICE", "").strip()
        if configured_device:
            model_kwargs["device"] = configured_device

        self.model = SentenceTransformer(self.model_name, **model_kwargs)

    @staticmethod
    def _env_int(name: str, default: int, min_value: int = 1) -> int:
        raw = os.getenv(name)
        if raw is None:
            return default
        try:
            value = int(raw)
            return max(min_value, value)
        except ValueError:
            return default

    @staticmethod
    def _env_bool(name: str, default: bool) -> bool:
        raw = os.getenv(name)
        if raw is None:
            return default
        return raw.strip().lower() in {"1", "true", "yes", "on"}

    def embed(self, texts: List[str]) -> np.ndarray:
        
        if not texts:
            return np.array([])
        
        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=self.normalize_embeddings,
        )
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
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)

        if self.normalize_embeddings:
            similarity = np.matmul(embeddings, embeddings.T)
            distances = 1.0 - similarity
            np.fill_diagonal(distances, 0.0)
            return np.clip(distances, 0.0, 2.0)

        return cosine_distances(embeddings)


_embedder = None


def get_embedder() -> EmbedderEngine:

    global _embedder
    if _embedder is None:
        _embedder = EmbedderEngine()
    return _embedder


def embed_texts(texts: List[str]) -> np.ndarray:

    return get_embedder().embed(texts)


def cosine_distance(vec1: np.ndarray, vec2: np.ndarray) -> float:

    return get_embedder().cosine_distance(vec1, vec2)


def pairwise_distances(embeddings: np.ndarray) -> np.ndarray:

    return get_embedder().pairwise_distances(embeddings)
