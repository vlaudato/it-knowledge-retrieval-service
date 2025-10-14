from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np


class EmbeddingService:
    """Service for generating embeddings using SentenceTransformer"""
    
    def __init__(self, model_name: str):
        """
        Initialize the embedding service
        
        Args:
            model_name: Name of the model to use
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print("Embedding model loaded successfully")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        embedding = self.model.encode(
            text,
            batch_size=64,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        
        # Handle numpy array conversion
        vec = embedding
        if isinstance(vec, np.ndarray):
            if vec.ndim == 2 and vec.shape[0] == 1:
                vec = vec[0]
            vec = vec.astype(float).tolist()
        
        return vec