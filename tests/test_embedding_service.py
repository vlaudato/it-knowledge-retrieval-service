"""
Unit tests for EmbeddingService
"""
import pytest
import numpy as np
from services.embedding_service import EmbeddingService


class TestEmbeddingService:
    """Test cases for the EmbeddingService class"""
    
    @pytest.fixture
    def embedding_service(self):
        """Fixture to create an EmbeddingService instance"""
        # Use a smaller, faster model for testing
        return EmbeddingService("sentence-transformers/all-MiniLM-L6-v2")
    
    def test_initialization(self, embedding_service):
        """Test that the service initializes correctly"""
        assert embedding_service is not None
        assert embedding_service.model is not None
    
    def test_generate_embedding_returns_list(self, embedding_service):
        """Test that generate_embedding returns a list"""
        text = "This is a test sentence"
        embedding = embedding_service.generate_embedding(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) > 0
    
    def test_generate_embedding_correct_dimension(self, embedding_service):
        """Test that embeddings have the correct dimension"""
        text = "Test sentence"
        embedding = embedding_service.generate_embedding(text)
        
        # MiniLM-L6-v2 produces 384-dimensional embeddings
        assert len(embedding) == 384
    
    def test_generate_embedding_all_floats(self, embedding_service):
        """Test that all embedding values are floats"""
        text = "Another test"
        embedding = embedding_service.generate_embedding(text)
        
        assert all(isinstance(x, float) for x in embedding)
    
    def test_generate_embedding_normalized(self, embedding_service):
        """Test that embeddings are normalized (magnitude ≈ 1)"""
        text = "Normalized embedding test"
        embedding = embedding_service.generate_embedding(text)
        
        # Calculate magnitude (L2 norm)
        magnitude = sum(x**2 for x in embedding) ** 0.5
        
        # Should be close to 1.0 (normalized)
        assert abs(magnitude - 1.0) < 0.01
    
    def test_generate_embedding_different_texts_different_embeddings(self, embedding_service):
        """Test that different texts produce different embeddings"""
        text1 = "The cat sat on the mat"
        text2 = "The dog ran in the park"
        
        embedding1 = embedding_service.generate_embedding(text1)
        embedding2 = embedding_service.generate_embedding(text2)
        
        # Embeddings should be different
        assert embedding1 != embedding2
    
    def test_generate_embedding_similar_texts_similar_embeddings(self, embedding_service):
        """Test that similar texts produce similar embeddings"""
        text1 = "I love machine learning"
        text2 = "I enjoy artificial intelligence"
        text3 = "The weather is nice today"
        
        emb1 = embedding_service.generate_embedding(text1)
        emb2 = embedding_service.generate_embedding(text2)
        emb3 = embedding_service.generate_embedding(text3)
        
        # Calculate cosine similarity
        def cosine_similarity(a, b):
            return sum(x*y for x, y in zip(a, b))
        
        sim_12 = cosine_similarity(emb1, emb2)  # Similar topics
        sim_13 = cosine_similarity(emb1, emb3)  # Different topics
        
        # Similar texts should have higher similarity
        assert sim_12 > sim_13
    
    def test_generate_embedding_empty_string(self, embedding_service):
        """Test handling of empty string"""
        text = ""
        embedding = embedding_service.generate_embedding(text)
        
        # Should still return an embedding
        assert isinstance(embedding, list)
        assert len(embedding) == 384
    
    def test_generate_embedding_long_text(self, embedding_service):
        """Test handling of long text"""
        text = "This is a very long text. " * 100  # 500+ words
        embedding = embedding_service.generate_embedding(text)
        
        # Should handle long text and return correct dimension
        assert isinstance(embedding, list)
        assert len(embedding) == 384
    
    def test_generate_embedding_special_characters(self, embedding_service):
        """Test handling of special characters"""
        text = "Test with special chars: @#$%^&*()!?"
        embedding = embedding_service.generate_embedding(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) == 384
    
    def test_generate_embedding_consistency(self, embedding_service):
        """Test that same text produces same embedding"""
        text = "Consistency test"
        
        embedding1 = embedding_service.generate_embedding(text)
        embedding2 = embedding_service.generate_embedding(text)
        
        # Should be identical (or very close due to floating point)
        for v1, v2 in zip(embedding1, embedding2):
            assert abs(v1 - v2) < 1e-6
