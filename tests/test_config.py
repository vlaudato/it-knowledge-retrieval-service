"""
Unit tests for Config
"""
import pytest
import os
from unittest.mock import patch
from config import Config


class TestConfig:
    """Test cases for the Config class"""
    
    def test_config_has_required_attributes(self):
        """Test that Config has all required attributes"""
        assert hasattr(Config, 'SUPABASE_URL')
        assert hasattr(Config, 'SUPABASE_KEY')
        assert hasattr(Config, 'OLLAMA_BASE_URL')
        assert hasattr(Config, 'EMBEDDING_MODEL')
        assert hasattr(Config, 'LLM_MODEL')
        assert hasattr(Config, 'RERANKER_MODEL')
        assert hasattr(Config, 'VECTOR_TABLE_NAME')
        assert hasattr(Config, 'MATCH_THRESHOLD')
        assert hasattr(Config, 'MATCH_COUNT')
        assert hasattr(Config, 'FLASK_ENV')
        assert hasattr(Config, 'PORT')
    
    def test_default_values(self):
        """Test that default values are set correctly"""
        # These should have defaults even without env vars
        assert Config.OLLAMA_BASE_URL == os.getenv('OLLAMA_BASE_URL', 'http://ollama:11434')
        assert Config.EMBEDDING_MODEL == os.getenv('EMBEDDING_MODEL', 'Qwen/Qwen3-Embedding-0.6B')
        assert Config.LLM_MODEL == os.getenv('LLM_MODEL', 'llama3.2:latest')
        assert Config.RERANKER_MODEL == os.getenv('RERANKER_MODEL', 'Qwen/Qwen3-Reranker-0.6B')
        assert Config.VECTOR_TABLE_NAME == os.getenv('VECTOR_TABLE_NAME', 'it_docs_embeddings')
        assert Config.FLASK_ENV == os.getenv('FLASK_ENV', 'development')
    
    def test_match_threshold_is_float(self):
        """Test that MATCH_THRESHOLD is a float"""
        assert isinstance(Config.MATCH_THRESHOLD, float)
        assert 0 <= Config.MATCH_THRESHOLD <= 1
    
    def test_match_count_is_int(self):
        """Test that MATCH_COUNT is an integer"""
        assert isinstance(Config.MATCH_COUNT, int)
        assert Config.MATCH_COUNT > 0
    
    def test_port_is_int(self):
        """Test that PORT is an integer"""
        assert isinstance(Config.PORT, int)
        assert Config.PORT > 0
    
    def test_reranker_enabled_is_bool(self):
        """Test that RERANKER_ENABLED is a boolean"""
        assert isinstance(Config.RERANKER_ENABLED, bool)
    
    def test_initial_retrieval_count_is_int(self):
        """Test that INITIAL_RETRIEVAL_COUNT is an integer"""
        assert isinstance(Config.INITIAL_RETRIEVAL_COUNT, int)
        assert Config.INITIAL_RETRIEVAL_COUNT > 0
    
    def test_final_result_count_is_int(self):
        """Test that FINAL_RESULT_COUNT is an integer"""
        assert isinstance(Config.FINAL_RESULT_COUNT, int)
        assert Config.FINAL_RESULT_COUNT > 0
    
    @patch.dict(os.environ, {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-key-123'
    })
    def test_validate_with_valid_config(self):
        """Test that validate passes with required env vars"""
        # Reload config with test env vars
        from importlib import reload
        import config
        reload(config)
        
        # Should not raise an exception
        try:
            config.Config.validate()
        except ValueError:
            pytest.fail("validate() raised ValueError unexpectedly")
    
    @patch.dict(os.environ, {}, clear=True)
    def test_validate_missing_supabase_url(self):
        """Test that validate fails when SUPABASE_URL is missing"""
        from importlib import reload
        import config
        reload(config)
        
        with pytest.raises(ValueError) as exc_info:
            config.Config.validate()
        
        assert "SUPABASE_URL" in str(exc_info.value)
    
    @patch.dict(os.environ, {
        'SUPABASE_URL': 'https://test.supabase.co'
    }, clear=True)
    def test_validate_missing_supabase_key(self):
        """Test that validate fails when SUPABASE_KEY is missing"""
        from importlib import reload
        import config
        reload(config)
        
        with pytest.raises(ValueError) as exc_info:
            config.Config.validate()
        
        assert "SUPABASE_KEY" in str(exc_info.value)
    
    @patch.dict(os.environ, {
        'MATCH_THRESHOLD': '0.85'
    })
    def test_custom_match_threshold(self):
        """Test that custom MATCH_THRESHOLD is loaded correctly"""
        from importlib import reload
        import config
        reload(config)
        
        assert config.Config.MATCH_THRESHOLD == 0.85
    
    @patch.dict(os.environ, {
        'MATCH_COUNT': '10'
    })
    def test_custom_match_count(self):
        """Test that custom MATCH_COUNT is loaded correctly"""
        from importlib import reload
        import config
        reload(config)
        
        assert config.Config.MATCH_COUNT == 10
    
    @patch.dict(os.environ, {
        'PORT': '8080'
    })
    def test_custom_port(self):
        """Test that custom PORT is loaded correctly"""
        from importlib import reload
        import config
        reload(config)
        
        assert config.Config.PORT == 8080
    
    @patch.dict(os.environ, {
        'RERANKER_ENABLED': 'false'
    })
    def test_reranker_disabled(self):
        """Test that RERANKER_ENABLED can be disabled"""
        from importlib import reload
        import config
        reload(config)
        
        assert config.Config.RERANKER_ENABLED is False
    
    @patch.dict(os.environ, {
        'RERANKER_ENABLED': 'true'
    })
    def test_reranker_enabled(self):
        """Test that RERANKER_ENABLED can be enabled"""
        from importlib import reload
        import config
        reload(config)
        
        assert config.Config.RERANKER_ENABLED is True
    
    @patch.dict(os.environ, {
        'INITIAL_RETRIEVAL_COUNT': '30'
    })
    def test_custom_initial_retrieval_count(self):
        """Test that custom INITIAL_RETRIEVAL_COUNT is loaded"""
        from importlib import reload
        import config
        reload(config)
        
        assert config.Config.INITIAL_RETRIEVAL_COUNT == 30
    
    @patch.dict(os.environ, {
        'FINAL_RESULT_COUNT': '7'
    })
    def test_custom_final_result_count(self):
        """Test that custom FINAL_RESULT_COUNT is loaded"""
        from importlib import reload
        import config
        reload(config)
        
        assert config.Config.FINAL_RESULT_COUNT == 7
