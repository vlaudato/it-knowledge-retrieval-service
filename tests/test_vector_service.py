"""
Unit tests for VectorService
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from services.vector_service import VectorService


class TestVectorService:
    """Test cases for the VectorService class"""
    
    @pytest.fixture
    def mock_supabase_client(self):
        """Fixture to create a mock Supabase client"""
        mock_client = Mock()
        mock_client.rpc = Mock()
        return mock_client
    
    @pytest.fixture
    def vector_service(self, mock_supabase_client):
        """Fixture to create a VectorService instance with mocked Supabase"""
        with patch('services.vector_service.create_client', return_value=mock_supabase_client):
            service = VectorService(
                supabase_url="https://test.supabase.co",
                supabase_key="test-key",
                table_name="test_table"
            )
            service.client = mock_supabase_client
            return service
    
    @pytest.fixture
    def sample_embedding(self):
        """Fixture providing a sample embedding vector"""
        return [0.1, 0.2, 0.3] * 256  # 768-dimensional vector
    
    @pytest.fixture
    def sample_search_results(self):
        """Fixture providing sample search results"""
        return [
            {
                "id": 1,
                "content": "Document 1 content",
                "topic": "Topic A",
                "similarity": 0.95
            },
            {
                "id": 2,
                "content": "Document 2 content",
                "topic": "Topic A",
                "similarity": 0.88
            },
            {
                "id": 3,
                "content": "Document 3 content",
                "topic": "Topic B",
                "similarity": 0.82
            }
        ]
    
    def test_initialization(self, vector_service):
        """Test that the service initializes correctly"""
        assert vector_service is not None
        assert vector_service.client is not None
    
    def test_search_similar_documents_returns_list(self, vector_service, sample_embedding, sample_search_results):
        """Test that search_similar_documents returns a list"""
        # Mock the RPC call
        mock_response = Mock()
        mock_response.data = sample_search_results
        vector_service.client.rpc.return_value.execute.return_value = mock_response
        
        result = vector_service.search_similar_documents(sample_embedding)
        
        assert isinstance(result, list)
    
    def test_search_similar_documents_calls_rpc_with_correct_params(self, vector_service, sample_embedding):
        """Test that search calls RPC with correct parameters"""
        mock_response = Mock()
        mock_response.data = []
        vector_service.client.rpc.return_value.execute.return_value = mock_response
        
        vector_service.search_similar_documents(
            sample_embedding,
            match_count=5,
            match_threshold=0.7
        )
        
        # Verify RPC was called with correct function name and parameters
        vector_service.client.rpc.assert_called_once_with(
            'match_doc',
            {
                'query_embedding': sample_embedding,
                'match_count': 5,
                'match_threshold': 0.7
            }
        )
    
    def test_search_similar_documents_default_parameters(self, vector_service, sample_embedding):
        """Test that default parameters are used correctly"""
        mock_response = Mock()
        mock_response.data = []
        vector_service.client.rpc.return_value.execute.return_value = mock_response
        
        vector_service.search_similar_documents(sample_embedding)
        
        # Check default values
        call_args = vector_service.client.rpc.call_args[0][1]
        assert call_args['match_count'] == 5
        assert call_args['match_threshold'] == 0.7
    
    def test_search_similar_documents_returns_results(self, vector_service, sample_embedding, sample_search_results):
        """Test that search returns the correct results"""
        mock_response = Mock()
        mock_response.data = sample_search_results
        vector_service.client.rpc.return_value.execute.return_value = mock_response
        
        result = vector_service.search_similar_documents(sample_embedding)
        
        assert result == sample_search_results
        assert len(result) == 3
    
    def test_search_similar_documents_empty_results(self, vector_service, sample_embedding):
        """Test handling of empty search results"""
        mock_response = Mock()
        mock_response.data = []
        vector_service.client.rpc.return_value.execute.return_value = mock_response
        
        result = vector_service.search_similar_documents(sample_embedding)
        
        assert result == []
    
    def test_search_similar_documents_none_data(self, vector_service, sample_embedding):
        """Test handling when response data is None"""
        mock_response = Mock()
        mock_response.data = None
        vector_service.client.rpc.return_value.execute.return_value = mock_response
        
        result = vector_service.search_similar_documents(sample_embedding)
        
        assert result == []
    
    def test_search_similar_documents_handles_exception(self, vector_service, sample_embedding):
        """Test that exceptions are raised properly"""
        vector_service.client.rpc.return_value.execute.side_effect = Exception("Database error")
        
        with pytest.raises(Exception) as exc_info:
            vector_service.search_similar_documents(sample_embedding)
        
        assert "Database error" in str(exc_info.value)
    
    def test_search_similar_documents_with_different_match_counts(self, vector_service, sample_embedding, sample_search_results):
        """Test search with different match_count values"""
        mock_response = Mock()
        mock_response.data = sample_search_results[:2]
        vector_service.client.rpc.return_value.execute.return_value = mock_response
        
        result = vector_service.search_similar_documents(sample_embedding, match_count=2)
        
        call_args = vector_service.client.rpc.call_args[0][1]
        assert call_args['match_count'] == 2
    
    def test_search_similar_documents_with_different_thresholds(self, vector_service, sample_embedding):
        """Test search with different match_threshold values"""
        mock_response = Mock()
        mock_response.data = []
        vector_service.client.rpc.return_value.execute.return_value = mock_response
        
        vector_service.search_similar_documents(sample_embedding, match_threshold=0.9)
        
        call_args = vector_service.client.rpc.call_args[0][1]
        assert call_args['match_threshold'] == 0.9
    
    def test_search_similar_documents_result_structure(self, vector_service, sample_embedding, sample_search_results):
        """Test that returned documents have expected structure"""
        mock_response = Mock()
        mock_response.data = sample_search_results
        vector_service.client.rpc.return_value.execute.return_value = mock_response
        
        result = vector_service.search_similar_documents(sample_embedding)
        
        for doc in result:
            assert 'id' in doc
            assert 'content' in doc
            assert 'similarity' in doc
    
    def test_search_similar_documents_similarity_scores(self, vector_service, sample_embedding, sample_search_results):
        """Test that similarity scores are in valid range"""
        mock_response = Mock()
        mock_response.data = sample_search_results
        vector_service.client.rpc.return_value.execute.return_value = mock_response
        
        result = vector_service.search_similar_documents(sample_embedding)
        
        for doc in result:
            similarity = doc['similarity']
            assert 0 <= similarity <= 1
