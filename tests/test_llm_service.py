"""
Unit tests for LLMService
"""
import pytest
from unittest.mock import Mock, patch
from services.llm_service import LLMService


class TestLLMService:
    """Test cases for the LLMService class"""
    
    @pytest.fixture
    def llm_service(self):
        """Fixture to create an LLMService instance"""
        return LLMService(
            ollama_url="http://localhost:11434",
            model="llama3.2:latest"
        )
    
    @pytest.fixture
    def sample_documents(self):
        """Fixture providing sample context documents"""
        return [
            {
                "id": 1,
                "content": "To reset your password, click the Forgot Password link.",
                "similarity": 0.95
            },
            {
                "id": 2,
                "content": "You will receive a password reset email within 5 minutes.",
                "similarity": 0.88
            }
        ]
    
    def test_initialization(self, llm_service):
        """Test that the service initializes correctly"""
        assert llm_service is not None
        assert llm_service.ollama_url == "http://localhost:11434"
        assert llm_service.model == "llama3.2:latest"
    
    def test_build_context_with_documents(self, llm_service, sample_documents):
        """Test that _build_context creates proper context string"""
        context = llm_service._build_context(sample_documents)
        
        assert isinstance(context, str)
        assert "Document 1" in context
        assert "Document 2" in context
        assert sample_documents[0]['content'] in context
        assert sample_documents[1]['content'] in context
    
    def test_build_context_empty_documents(self, llm_service):
        """Test _build_context with empty document list"""
        context = llm_service._build_context([])
        
        assert context == "No relevant context found."
    
    def test_build_context_preserves_order(self, llm_service, sample_documents):
        """Test that _build_context preserves document order"""
        context = llm_service._build_context(sample_documents)
        
        # First document should appear before second
        pos1 = context.find(sample_documents[0]['content'])
        pos2 = context.find(sample_documents[1]['content'])
        assert pos1 < pos2
    
    def test_build_context_handles_missing_content(self, llm_service):
        """Test _build_context with documents missing content field"""
        docs = [
            {"id": 1, "similarity": 0.9},  # No content field
            {"id": 2, "content": "Valid content", "similarity": 0.8}
        ]
        
        context = llm_service._build_context(docs)
        
        # Should only include document with content
        assert "Valid content" in context
    
    @patch('services.llm_service.requests.post')
    def test_generate_answer_calls_ollama_api(self, mock_post, llm_service, sample_documents):
        """Test that generate_answer calls Ollama API correctly"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {"response": "Test answer"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        question = "How do I reset my password?"
        answer = llm_service.generate_answer(question, sample_documents)
        
        # Verify API was called
        assert mock_post.called
        assert answer == "Test answer"
    
    @patch('services.llm_service.requests.post')
    def test_generate_answer_request_structure(self, mock_post, llm_service, sample_documents):
        """Test that API request has correct structure"""
        mock_response = Mock()
        mock_response.json.return_value = {"response": "Test answer"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        question = "Test question?"
        llm_service.generate_answer(question, sample_documents)
        
        # Check request parameters
        call_args = mock_post.call_args
        assert call_args[0][0] == "http://localhost:11434/api/generate"
        
        json_data = call_args[1]['json']
        assert json_data['model'] == "llama3.2:latest"
        assert json_data['stream'] is False
        assert 'prompt' in json_data
        assert question in json_data['prompt']
    
    @patch('services.llm_service.requests.post')
    def test_generate_answer_includes_context(self, mock_post, llm_service, sample_documents):
        """Test that generated prompt includes context"""
        mock_response = Mock()
        mock_response.json.return_value = {"response": "Test answer"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        question = "Test question?"
        llm_service.generate_answer(question, sample_documents)
        
        # Check that context is in the prompt
        json_data = mock_post.call_args[1]['json']
        prompt = json_data['prompt']
        
        assert sample_documents[0]['content'] in prompt
        assert sample_documents[1]['content'] in prompt
    
    @patch('services.llm_service.requests.post')
    def test_generate_answer_with_custom_temperature(self, mock_post, llm_service, sample_documents):
        """Test generate_answer with custom temperature"""
        mock_response = Mock()
        mock_response.json.return_value = {"response": "Test answer"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        question = "Test question?"
        llm_service.generate_answer(question, sample_documents, temperature=0.5)
        
        # Check temperature in options
        json_data = mock_post.call_args[1]['json']
        assert json_data['options']['temperature'] == 0.5
    
    @patch('services.llm_service.requests.post')
    def test_generate_answer_strips_whitespace(self, mock_post, llm_service, sample_documents):
        """Test that answer is stripped of whitespace"""
        mock_response = Mock()
        mock_response.json.return_value = {"response": "  Test answer  \n"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        question = "Test question?"
        answer = llm_service.generate_answer(question, sample_documents)
        
        assert answer == "Test answer"
    
    @patch('services.llm_service.requests.post')
    def test_generate_answer_handles_empty_response(self, mock_post, llm_service, sample_documents):
        """Test handling of empty response from LLM"""
        mock_response = Mock()
        mock_response.json.return_value = {"response": ""}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        question = "Test question?"
        answer = llm_service.generate_answer(question, sample_documents)
        
        assert answer == ""
    
    @patch('services.llm_service.requests.post')
    def test_generate_answer_handles_missing_response_key(self, mock_post, llm_service, sample_documents):
        """Test handling when response doesn't have 'response' key"""
        mock_response = Mock()
        mock_response.json.return_value = {}  # No 'response' key
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        question = "Test question?"
        answer = llm_service.generate_answer(question, sample_documents)
        
        assert answer == ""
    
    @patch('services.llm_service.requests.post')
    def test_generate_answer_handles_api_error(self, mock_post, llm_service, sample_documents):
        """Test that API errors are raised"""
        mock_post.side_effect = Exception("API connection failed")
        
        question = "Test question?"
        
        with pytest.raises(Exception) as exc_info:
            llm_service.generate_answer(question, sample_documents)
        
        assert "API connection failed" in str(exc_info.value)
    
    @patch('services.llm_service.requests.post')
    def test_generate_answer_timeout_setting(self, mock_post, llm_service, sample_documents):
        """Test that timeout is set correctly"""
        mock_response = Mock()
        mock_response.json.return_value = {"response": "Test"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        question = "Test question?"
        llm_service.generate_answer(question, sample_documents)
        
        # Check timeout parameter
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs['timeout'] == 180
    
    def test_build_context_with_many_documents(self, llm_service):
        """Test _build_context with many documents"""
        docs = [
            {"id": i, "content": f"Document {i} content", "similarity": 0.9 - i*0.1}
            for i in range(10)
        ]
        
        context = llm_service._build_context(docs)
        
        # Should include all documents
        for i in range(10):
            assert f"Document {i}" in context
    
    def test_build_context_numbering(self, llm_service, sample_documents):
        """Test that documents are numbered correctly in context"""
        context = llm_service._build_context(sample_documents)
        
        assert "[Document 1]" in context
        assert "[Document 2]" in context
