"""
Unit tests for RerankerService
"""
import pytest
from services.reranker_service import RerankerService


class TestRerankerService:
    """Test cases for the RerankerService class"""
    
    @pytest.fixture
    def reranker_service(self):
        """Fixture to create a RerankerService instance"""
        # Use a smaller model for faster testing
        return RerankerService("cross-encoder/ms-marco-MiniLM-L-2-v2")
    
    @pytest.fixture
    def sample_documents(self):
        """Fixture providing sample documents for testing"""
        return [
            {
                "id": 1,
                "content": "To reset your password, click the Forgot Password link on the login page.",
                "similarity": 0.85
            },
            {
                "id": 2,
                "content": "VPN connection requires a valid password and certificate.",
                "similarity": 0.82
            },
            {
                "id": 3,
                "content": "Password requirements: minimum 8 characters, one uppercase, one number.",
                "similarity": 0.80
            },
            {
                "id": 4,
                "content": "Contact IT helpdesk for password reset assistance.",
                "similarity": 0.78
            },
            {
                "id": 5,
                "content": "Your password expires every 90 days.",
                "similarity": 0.75
            }
        ]
    
    def test_initialization(self, reranker_service):
        """Test that the service initializes correctly"""
        assert reranker_service is not None
        assert reranker_service.model is not None
        assert reranker_service.tokenizer is not None
        assert reranker_service.device in ["cpu", "cuda"]
    
    def test_rerank_returns_list(self, reranker_service, sample_documents):
        """Test that rerank returns a list"""
        query = "How do I reset my password?"
        result = reranker_service.rerank(query, sample_documents, top_k=3)
        
        assert isinstance(result, list)
    
    def test_rerank_returns_correct_count(self, reranker_service, sample_documents):
        """Test that rerank returns the requested number of documents"""
        query = "How do I reset my password?"
        
        result_3 = reranker_service.rerank(query, sample_documents, top_k=3)
        assert len(result_3) == 3
        
        result_5 = reranker_service.rerank(query, sample_documents, top_k=5)
        assert len(result_5) == 5
    
    def test_rerank_adds_rerank_score(self, reranker_service, sample_documents):
        """Test that rerank adds rerank_score to documents"""
        query = "How do I reset my password?"
        result = reranker_service.rerank(query, sample_documents, top_k=3)
        
        for doc in result:
            assert 'rerank_score' in doc
            assert isinstance(doc['rerank_score'], float)
    
    def test_rerank_preserves_original_fields(self, reranker_service, sample_documents):
        """Test that rerank preserves original document fields"""
        query = "How do I reset my password?"
        result = reranker_service.rerank(query, sample_documents, top_k=3)
        
        for doc in result:
            assert 'id' in doc
            assert 'content' in doc
            assert 'similarity' in doc
    
    def test_rerank_orders_by_relevance(self, reranker_service, sample_documents):
        """Test that rerank orders documents by relevance score"""
        query = "How do I reset my password?"
        result = reranker_service.rerank(query, sample_documents, top_k=5)
        
        # Check that results are in descending order of rerank_score
        scores = [doc['rerank_score'] for doc in result]
        assert scores == sorted(scores, reverse=True)
    
    def test_rerank_most_relevant_first(self, reranker_service, sample_documents):
        """Test that most relevant document is ranked first"""
        query = "How do I reset my password?"
        result = reranker_service.rerank(query, sample_documents, top_k=3)
        
        # Document about resetting password should be first
        top_doc = result[0]
        assert "reset your password" in top_doc['content'].lower()
    
    def test_rerank_empty_documents(self, reranker_service):
        """Test handling of empty document list"""
        query = "Test query"
        result = reranker_service.rerank(query, [], top_k=3)
        
        assert result == []
    
    def test_rerank_single_document(self, reranker_service):
        """Test reranking with single document"""
        query = "Test query"
        docs = [{"id": 1, "content": "Test content", "similarity": 0.8}]
        result = reranker_service.rerank(query, docs, top_k=3)
        
        assert len(result) == 1
        assert 'rerank_score' in result[0]
    
    def test_rerank_top_k_larger_than_documents(self, reranker_service, sample_documents):
        """Test when top_k is larger than number of documents"""
        query = "Test query"
        result = reranker_service.rerank(query, sample_documents, top_k=100)
        
        # Should return all documents
        assert len(result) == len(sample_documents)
    
    def test_rerank_different_queries_different_rankings(self, reranker_service, sample_documents):
        """Test that different queries produce different rankings"""
        query1 = "How do I reset my password?"
        query2 = "What are the VPN requirements?"
        
        result1 = reranker_service.rerank(query1, sample_documents, top_k=3)
        result2 = reranker_service.rerank(query2, sample_documents, top_k=3)
        
        # Top documents should be different
        top_id_1 = result1[0]['id']
        top_id_2 = result2[0]['id']
        
        assert top_id_1 != top_id_2
    
    def test_rerank_scores_are_reasonable(self, reranker_service, sample_documents):
        """Test that rerank scores are in a reasonable range"""
        query = "How do I reset my password?"
        result = reranker_service.rerank(query, sample_documents, top_k=5)
        
        for doc in result:
            score = doc['rerank_score']
            # Scores typically range from -10 to +10 for cross-encoders
            assert -20 < score < 20
    
    def test_rerank_with_special_characters_in_query(self, reranker_service, sample_documents):
        """Test handling of special characters in query"""
        query = "How do I reset my password? @#$%"
        result = reranker_service.rerank(query, sample_documents, top_k=3)
        
        assert len(result) == 3
        assert all('rerank_score' in doc for doc in result)
    
    def test_rerank_with_long_query(self, reranker_service, sample_documents):
        """Test handling of very long query"""
        query = "How do I reset my password? " * 50  # Very long query
        result = reranker_service.rerank(query, sample_documents, top_k=3)
        
        assert len(result) == 3
    
    def test_rerank_with_empty_content(self, reranker_service):
        """Test handling of documents with empty content"""
        query = "Test query"
        docs = [
            {"id": 1, "content": "", "similarity": 0.8},
            {"id": 2, "content": "Valid content", "similarity": 0.7}
        ]
        result = reranker_service.rerank(query, docs, top_k=2)
        
        # Should handle empty content gracefully
        assert len(result) == 2
        assert all('rerank_score' in doc for doc in result)
