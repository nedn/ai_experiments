#!/usr/bin/env python3
"""
Test script for simplified AI Client functionality.

This script tests the simplified AIClient class without requiring actual API calls.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

try:
    from common_util.ai_client import AIClient
except ImportError:
    from ai_client import AIClient


class TestAIClient(unittest.TestCase):
    """Test cases for AIClient class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_api_key = "test-api-key-12345"
    
    def test_api_key_from_environment(self):
        """Test API key retrieval from environment variable."""
        with patch.dict('os.environ', {'GEMINI_API_KEY': self.test_api_key}):
            with patch('ai_client.genai.configure'):
                with patch('ai_client.genai.GenerativeModel'):
                    client = AIClient()
                    self.assertEqual(client.api_key, self.test_api_key)
    
    def test_api_key_from_env_file(self):
        """Test API key retrieval from .env file."""
        env_content = f"GEMINI_API_KEY={self.test_api_key}\nOTHER_VAR=value"
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', unittest.mock.mock_open(read_data=env_content)):
                with patch('os.getenv', return_value=None):
                    with patch('ai_client.genai.configure'):
                        with patch('ai_client.genai.GenerativeModel'):
                            client = AIClient()
                            self.assertEqual(client.api_key, self.test_api_key)
    
    def test_explicit_api_key(self):
        """Test explicit API key initialization."""
        with patch('ai_client.genai.configure'):
            with patch('ai_client.genai.GenerativeModel'):
                client = AIClient(api_key=self.test_api_key)
                self.assertEqual(client.api_key, self.test_api_key)
    
    def test_no_api_key_raises_error(self):
        """Test that missing API key raises ValueError."""
        with patch('os.getenv', return_value=None):
            with patch('pathlib.Path.exists', return_value=False):
                with self.assertRaises(ValueError):
                    AIClient()
    
    def test_model_initialization(self):
        """Test model initialization with allowed models."""
        test_models = ["gemini-2.5-pro", "gemini-flash-latest", "gemini-flash-lite-latest"]
        
        for model in test_models:
            with patch('ai_client.genai.configure'):
                with patch('ai_client.genai.GenerativeModel') as mock_model:
                    client = AIClient(api_key=self.test_api_key, model=model)
                    self.assertEqual(client.model_name, model)
                    mock_model.assert_called_once_with(model)
    
    def test_invalid_model_raises_error(self):
        """Test that invalid model raises ValueError."""
        with patch('ai_client.genai.configure'):
            with self.assertRaises(ValueError) as context:
                AIClient(api_key=self.test_api_key, model="invalid-model")
            self.assertIn("Model must be one of", str(context.exception))
    
    def test_allowed_models_constant(self):
        """Test that ALLOWED_MODELS constant is correct."""
        expected_models = ["gemini-2.5-pro", "gemini-flash-latest", "gemini-flash-lite-latest"]
        self.assertEqual(AIClient.ALLOWED_MODELS, expected_models)
    
    def test_default_model(self):
        """Test that default model is gemini-2.5-pro."""
        with patch('ai_client.genai.configure'):
            with patch('ai_client.genai.GenerativeModel') as mock_model:
                client = AIClient(api_key=self.test_api_key)
                self.assertEqual(client.model_name, "gemini-2.5-pro")
                mock_model.assert_called_once_with("gemini-2.5-pro")
    
    def test_generate_content_mock(self):
        """Test content generation with mocked API response."""
        mock_response = MagicMock()
        mock_response.text = "This is a test response"
        
        with patch('ai_client.genai.configure'):
            with patch('ai_client.genai.GenerativeModel') as mock_model_class:
                mock_model = MagicMock()
                mock_model.generate_content.return_value = mock_response
                mock_model_class.return_value = mock_model
                
                client = AIClient(api_key=self.test_api_key)
                response = client.generate_content("Test prompt")
                
                self.assertEqual(response, "This is a test response")
                mock_model.generate_content.assert_called_once()
    
    def test_generate_content_empty_response(self):
        """Test content generation with empty response."""
        mock_response = MagicMock()
        mock_response.text = None
        
        with patch('ai_client.genai.configure'):
            with patch('ai_client.genai.GenerativeModel') as mock_model_class:
                mock_model = MagicMock()
                mock_model.generate_content.return_value = mock_response
                mock_model_class.return_value = mock_model
                
                client = AIClient(api_key=self.test_api_key)
                response = client.generate_content("Test prompt")
                
                self.assertEqual(response, "")
    
    def test_generate_content_exception(self):
        """Test content generation with API exception."""
        with patch('ai_client.genai.configure'):
            with patch('ai_client.genai.GenerativeModel') as mock_model_class:
                mock_model = MagicMock()
                mock_model.generate_content.side_effect = Exception("API Error")
                mock_model_class.return_value = mock_model
                
                client = AIClient(api_key=self.test_api_key)
                
                with self.assertRaises(Exception) as context:
                    client.generate_content("Test prompt")
                self.assertIn("Error generating content", str(context.exception))


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
