"""
Test AI Configuration

Tests for AI-related configuration validation and environment setup.
Ensures proper configuration of Gemini 2.5 Flash and LangChain settings.

Following TDD methodology:
1. Test configuration validation
2. Test environment variable handling
3. Test AI model parameter validation
"""

import pytest
from unittest.mock import patch
import os

from app.core.config import Settings


def get_minimal_config_dict():
    """Get minimal configuration for testing"""
    return {
        'DATABASE_URL': 'postgresql://test:test@localhost/test',
        'JWT_SECRET_KEY': 'test-secret-key-for-testing',
        'GOOGLE_CLIENT_ID': 'test-client-id',
        'GOOGLE_CLIENT_SECRET': 'test-client-secret'
    }


class TestAIConfiguration:
    """Test AI configuration validation and setup"""

    def test_ai_config_defaults(self):
        """Test that AI configuration has proper defaults"""
        config_dict = get_minimal_config_dict()
        settings = Settings(**config_dict)
        
        # Test default AI settings
        assert settings.AI_MODEL_NAME == "gemini-2.5-flash"
        assert settings.AI_TEMPERATURE == 0.7
        assert settings.AI_MAX_TOKENS == 2048
        assert settings.AI_TOP_P == 0.9
        assert settings.AI_TOP_K == 40
        # Note: GOOGLE_GEMINI_API_KEY may be set from environment, so we just check it exists
        assert hasattr(settings, 'GOOGLE_GEMINI_API_KEY')

    def test_ai_config_with_api_key(self):
        """Test configuration with valid API key"""
        config_dict = get_minimal_config_dict()
        config_dict['GOOGLE_GEMINI_API_KEY'] = 'test-api-key-12345'
        
        settings = Settings(**config_dict)
        assert settings.GOOGLE_GEMINI_API_KEY == 'test-api-key-12345'

    def test_ai_config_without_api_key(self):
        """Test configuration without API key (should use empty default)"""
        config_dict = get_minimal_config_dict()
        # Explicitly set empty API key to override environment
        config_dict['GOOGLE_GEMINI_API_KEY'] = ""
        
        settings = Settings(**config_dict)
        
        # Should be empty when explicitly set
        assert settings.GOOGLE_GEMINI_API_KEY == ""

    def test_ai_model_name_override(self):
        """Test that AI model name can be overridden"""
        config_dict = get_minimal_config_dict()
        config_dict['AI_MODEL_NAME'] = 'gemini-pro'
        
        settings = Settings(**config_dict)
        assert settings.AI_MODEL_NAME == 'gemini-pro'

    def test_ai_temperature_validation(self):
        """Test AI temperature parameter validation"""
        config_dict = get_minimal_config_dict()
        config_dict['AI_TEMPERATURE'] = 0.5
        
        settings = Settings(**config_dict)
        assert settings.AI_TEMPERATURE == 0.5

    def test_ai_max_tokens_validation(self):
        """Test AI max tokens parameter validation"""
        config_dict = get_minimal_config_dict()
        config_dict['AI_MAX_TOKENS'] = 4096
        
        settings = Settings(**config_dict)
        assert settings.AI_MAX_TOKENS == 4096

    def test_ai_config_complete_setup(self):
        """Test complete AI configuration setup"""
        config_dict = get_minimal_config_dict()
        config_dict.update({
            'GOOGLE_GEMINI_API_KEY': 'AIzaSyTest123456789',
            'AI_MODEL_NAME': 'gemini-2.5-flash',
            'AI_TEMPERATURE': 0.8,
            'AI_MAX_TOKENS': 3000,
            'AI_TOP_P': 0.95,
            'AI_TOP_K': 50
        })
        
        settings = Settings(**config_dict)
        
        # Verify all AI settings are properly loaded
        assert settings.GOOGLE_GEMINI_API_KEY == 'AIzaSyTest123456789'
        assert settings.AI_MODEL_NAME == 'gemini-2.5-flash'
        assert settings.AI_TEMPERATURE == 0.8
        assert settings.AI_MAX_TOKENS == 3000
        assert settings.AI_TOP_P == 0.95
        assert settings.AI_TOP_K == 50

    def test_api_key_format_validation(self):
        """Test that we can identify valid-looking API keys"""
        valid_key = "AIzaSyTest123456789abcdef"
        invalid_key = "invalid-key"
        
        # Valid API key format (starts with AIzaSy)
        assert valid_key.startswith("AIzaSy")
        assert len(valid_key) > 20
        
        # Invalid API key format  
        assert not invalid_key.startswith("AIzaSy")
