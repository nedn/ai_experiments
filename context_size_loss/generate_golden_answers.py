#!/usr/bin/env python3
"""
Golden Answer Generation Script

This script generates golden answers for sprintf→snprintf conversions using
gemini-2.5-pro with batch size 1 for optimal quality.

Usage:
    python generate_golden_answers.py --api-key YOUR_API_KEY
    python generate_golden_answers.py --config config.yaml

Author: AI Assistant
Date: 2025
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import time

# Add the current directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

from code_snippet import CodeSnippet, CodeSnippetList, snippets_from_json_list
from validator import GoldenAnswerManager, generate_golden_answers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_snippets(snippets_file: str) -> CodeSnippetList:
    """Load code snippets from JSON file."""
    logger.info(f"Loading snippets from {snippets_file}")
    
    try:
        with open(snippets_file, 'r') as f:
            data = json.load(f)
        
        if 'snippets' in data:
            snippets_data = data['snippets']
        else:
            snippets_data = data
        
        snippets = snippets_from_json_list(snippets_data)
        logger.info(f"Loaded {len(snippets)} snippets")
        return snippets
        
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading snippets: {e}")
        raise


def call_gemini_api(snippet_content: str, api_key: str, model: str = "gemini-2.5-pro") -> str:
    """
    Call Gemini API to convert sprintf to snprintf.
    
    This is a placeholder function - in practice, you would integrate with
    the actual Gemini API client library.
    
    Args:
        snippet_content: The code snippet to convert
        api_key: Gemini API key
        model: Model to use (default: gemini-2.5-pro)
        
    Returns:
        Converted code snippet
    """
    # TODO: Replace this with actual Gemini API call
    # For now, return a placeholder response
    
    prompt = f"""
Convert the following C code snippet to use snprintf instead of sprintf for better buffer safety.
Make sure to add the buffer size parameter and handle the return value appropriately.

Original code:
```c
{snippet_content}
```

Converted code:
```c
"""
    
    # Placeholder response - replace with actual API call
    logger.debug(f"Would call {model} API with prompt length: {len(prompt)}")
    
    # Simulate API call delay
    time.sleep(0.1)
    
    # Return placeholder converted code
    return f"// TODO: Convert sprintf to snprintf in:\n{snippet_content}"


def generate_golden_answers_for_snippets(snippets: CodeSnippetList, api_key: str, 
                                       output_file: str = "golden_answers.json") -> Dict[str, str]:
    """
    Generate golden answers for all snippets using gemini-2.5-pro.
    
    Args:
        snippets: Code snippets to convert
        api_key: Gemini API key
        output_file: File to save golden answers
        
    Returns:
        Dictionary mapping snippet ID to golden converted code
    """
    logger.info(f"Generating golden answers for {len(snippets)} snippets using gemini-2.5-pro")
    
    golden_answers = {}
    manager = GoldenAnswerManager(output_file)
    
    # Check which snippets already have golden answers
    existing_answers = set(manager.golden_answers.keys())
    snippets_to_process = []
    
    for i, snippet in enumerate(snippets):
        snippet_id = f"snippet_{i:03d}"
        if snippet_id not in existing_answers:
            snippets_to_process.append((snippet_id, snippet))
        else:
            logger.debug(f"Skipping {snippet_id} - already has golden answer")
    
    logger.info(f"Processing {len(snippets_to_process)} new snippets")
    
    # Process snippets one by one (batch size 1 for optimal quality)
    for i, (snippet_id, snippet) in enumerate(snippets_to_process):
        try:
            logger.info(f"Processing snippet {i+1}/{len(snippets_to_process)}: {snippet_id}")
            
            # Get snippet content
            snippet_content = snippet.get_full_content()
            
            # Call Gemini API
            converted_code = call_gemini_api(snippet_content, api_key)
            
            # Store golden answer
            golden_answers[snippet_id] = converted_code
            manager.add_golden_answer(snippet_id, converted_code)
            
            # Save progress every 10 snippets
            if (i + 1) % 10 == 0:
                manager.save_golden_answers()
                logger.info(f"Saved progress: {i+1}/{len(snippets_to_process)} snippets processed")
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Error processing snippet {snippet_id}: {e}")
            # Continue with next snippet
            continue
    
    # Save final results
    manager.save_golden_answers()
    
    logger.info(f"Generated {len(golden_answers)} golden answers")
    return golden_answers


def main():
    """Main function for golden answer generation."""
    parser = argparse.ArgumentParser(description="Generate golden answers for sprintf→snprintf conversion")
    parser.add_argument("--snippets-file", default="rise_data/sprintf_snippets.json",
                       help="Path to snippets JSON file")
    parser.add_argument("--output-file", default="golden_answers.json",
                       help="Output file for golden answers")
    parser.add_argument("--api-key", help="Gemini API key (or set GEMINI_API_KEY env var)")
    parser.add_argument("--model", default="gemini-2.5-pro",
                       help="Gemini model to use")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Get API key
    api_key = args.api_key or os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.error("API key required. Set GEMINI_API_KEY env var or use --api-key")
        sys.exit(1)
    
    # Check if snippets file exists
    if not Path(args.snippets_file).exists():
        logger.error(f"Snippets file not found: {args.snippets_file}")
        sys.exit(1)
    
    try:
        # Load snippets
        snippets = load_snippets(args.snippets_file)
        
        if len(snippets) == 0:
            logger.error("No snippets found in file")
            sys.exit(1)
        
        # Generate golden answers
        golden_answers = generate_golden_answers_for_snippets(
            snippets, api_key, args.output_file
        )
        
        # Print summary
        print(f"\n{'='*60}")
        print("GOLDEN ANSWER GENERATION COMPLETED")
        print(f"{'='*60}")
        print(f"Snippets processed: {len(golden_answers)}")
        print(f"Output file: {args.output_file}")
        print(f"Model used: {args.model}")
        print(f"{'='*60}")
        
    except Exception as e:
        logger.error(f"Error during golden answer generation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
