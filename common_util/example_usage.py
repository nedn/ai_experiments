#!/usr/bin/env python3
"""
Example usage of the AI Client for Gemini API integration.

This script demonstrates how to use the AIClient class for various tasks.
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

try:
    from .ai_client import AIClient
except ImportError:
    from ai_client import AIClient


def example_basic_usage():
    """Example of basic AI client usage."""
    print("=== Basic Usage Example ===")
    
    try:
        # Initialize client (will prompt for API key if multiple sources found)
        client = AIClient()
        
        # Generate content
        prompt = "Explain the difference between sprintf and snprintf in C programming."
        response = client.generate_content(prompt)
        
        print(f"Prompt: {prompt}")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_code_conversion():
    """Example of code conversion using the AI client."""
    print("\n=== Code Conversion Example ===")
    
    try:
        client = AIClient()
        
        # Example C code with sprintf
        code = """
        char buffer[100];
        char name[] = "John Doe";
        sprintf(buffer, "Hello, %s!", name);
        printf("%s\\n", buffer);
        """
        
        # Convert to snprintf
        converted_code = client.generate_code_conversion(code, "sprintf_to_snprintf")
        
        print("Original code:")
        print(code)
        print("\nConverted code:")
        print(converted_code)
        
    except Exception as e:
        print(f"Error: {e}")


def example_batch_processing():
    """Example of batch processing multiple prompts."""
    print("\n=== Batch Processing Example ===")
    
    try:
        client = AIClient()
        
        prompts = [
            "What is buffer overflow in C?",
            "How do you prevent buffer overflows?",
            "What are the benefits of using snprintf over sprintf?"
        ]
        
        responses = client.batch_generate(prompts)
        
        for i, (prompt, response) in enumerate(zip(prompts, responses)):
            print(f"\nPrompt {i+1}: {prompt}")
            print(f"Response: {response[:100]}...")  # Truncate for display
        
    except Exception as e:
        print(f"Error: {e}")


def example_with_explicit_api_key():
    """Example using explicit API key."""
    print("\n=== Explicit API Key Example ===")
    
    # This would normally use a real API key
    # For demonstration, we'll show the pattern
    api_key = "your-api-key-here"  # Replace with actual key
    
    try:
        client = AIClient(api_key=api_key, model="gemini-2.0-flash-exp")
        
        # Get model info
        info = client.get_model_info()
        print(f"Model info: {info}")
        
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Run all examples."""
    print("AI Client Usage Examples")
    print("=" * 50)
    
    # Note: These examples will only work if you have a valid API key
    # and the google-generativeai package installed
    
    print("\nTo run these examples, you need:")
    print("1. Install dependencies: pip install google-generativeai")
    print("2. Set up API key in one of these ways:")
    print("   - Set GEMINI_API_KEY environment variable")
    print("   - Create .env file with GEMINI_API_KEY=your_key")
    print("   - Pass --api-key when running the script")
    print("   - Initialize AIClient(api_key='your_key')")
    
    # Uncomment these to run the examples:
    # example_basic_usage()
    # example_code_conversion()
    # example_batch_processing()
    # example_with_explicit_api_key()


if __name__ == "__main__":
    main()
