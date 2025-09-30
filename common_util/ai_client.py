#!/usr/bin/env python3
"""
Simple AI Client for Gemini API

A minimal client for interacting with Google's Gemini API.
Supports automatic API key detection and basic content generation.

Usage:
    from ai_client import AIClient
    
    # Initialize with automatic API key detection
    client = AIClient()
    
    # Generate content
    response = client.generate_content("Your prompt here")
    
    # Or specify API key explicitly
    client = AIClient(api_key="your-api-key", model="gemini-2.5-pro")
"""

import os
import sys
from pathlib import Path
from typing import Optional

try:
    import google.generativeai as genai
except ImportError:
    print("Error: google-generativeai package not found.")
    print("Please install it with: pip install google-generativeai")
    sys.exit(1)


def _load_from_env_file() -> Optional[str]:
    """Load API key from .env file."""
    env_files = ['.env', '.env.local', '.env.production']
    
    for env_file in env_files:
        env_path = Path(env_file)
        if env_path.exists():
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('GEMINI_API_KEY='):
                            key = line.split('=', 1)[1].strip().strip('"\'')
                            if key:
                                return key
            except (IOError, IndexError):
                continue
    
    return None


def get_api_key() -> str:
    """
    Get API key from environment variable or .env file.
    
    Returns:
        API key string
        
    Raises:
        ValueError: If no API key is found
    """
    # Check environment variable
    env_key = os.getenv('GEMINI_API_KEY')
    if env_key:
        return env_key
    
    # Check .env file
    env_file_key = _load_from_env_file()
    if env_file_key:
        return env_file_key
    
    raise ValueError(
        "No API key found. Please provide one of:\n"
        "1. Set GEMINI_API_KEY environment variable\n"
        "2. Create .env file with GEMINI_API_KEY=your_key\n"
        "3. Initialize AIClient(api_key='your_key')"
    )


class AIClient:
    """
    Simple AI Client for Gemini API integration.
    """
    
    ALLOWED_MODELS = ["gemini-2.5-pro", "gemini-flash-latest", "gemini-flash-lite-latest"]
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-pro"):
        """
        Initialize the AI Client.
        
        Args:
            api_key: API key for Gemini. If None, will attempt to find from various sources.
            model: Gemini model to use (must be one of the allowed models)
        """
        if model not in self.ALLOWED_MODELS:
            raise ValueError(f"Model must be one of: {', '.join(self.ALLOWED_MODELS)}")
        
        self.model_name = model
        self.api_key = api_key or get_api_key()
        self._configure_genai()
        self.model = genai.GenerativeModel(self.model_name)
    
    def _configure_genai(self):
        """Configure the generative AI library."""
        if not self.api_key:
            raise ValueError("API key is required")
        
        genai.configure(api_key=self.api_key)
    
    def generate_content(self, prompt: str) -> str:
        """
        Generate content using the Gemini model.
        
        Args:
            prompt: Input prompt for content generation
            
        Returns:
            Generated content string
            
        Raises:
            Exception: If generation fails
        """
        try:
            response = self.model.generate_content(prompt)
            
            if response.text:
                return response.text
            else:
                return ""
                
        except Exception as e:
            raise Exception(f"Error generating content: {e}")
    
