#!/usr/bin/env python3
"""
Golden Answer Generation Script

This script generates golden answers for sprintf→snprintf conversions using
gemini-2.5-pro with batch size 1 for optimal quality.

The golden_answers.json file format:
- Each snippet has both 'original_content' and 'golden_answer' fields
- Both fields are arrays of strings, where each string represents a line of code
- This format is more readable than single strings with newline characters

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
# Add the common_util directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent / "common_util"))

from code_snippet import CodeSnippet, CodeSnippetList, snippets_from_json_list
from validator import GoldenAnswerManager, generate_golden_answers
from ai_client import AIClient, get_api_key

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


def load_snippets_raw_data(snippets_file: str) -> List[Dict[str, Any]]:
    """Load raw snippets data from JSON file for sanity checking."""
    logger.debug(f"Loading raw snippets data from {snippets_file}")
    
    try:
        with open(snippets_file, 'r') as f:
            data = json.load(f)
        
        if 'snippets' in data:
            return data['snippets']
        else:
            return data
        
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading raw snippets data: {e}")
        raise


def sanity_check_original_content(golden_answers: Dict[str, Dict[str, List[str]]], 
                                 raw_snippets_data: List[Dict[str, Any]]) -> bool:
    """
    Sanity check to compare original_content in golden answers with raw_content from snippets.
    
    Args:
        golden_answers: Dictionary mapping snippet ID to golden answer data
        raw_snippets_data: Raw snippets data from the original JSON file
        
    Returns:
        True if all checks pass, False otherwise
    """
    logger.info("Running sanity check on original_content vs raw_content...")
    
    all_checks_passed = True
    total_checks = 0
    failed_checks = 0
    
    for snippet_id, golden_data in golden_answers.items():
        # Extract snippet index from snippet_id (e.g., "snippet_000" -> 0)
        try:
            snippet_index = int(snippet_id.split('_')[1])
        except (IndexError, ValueError):
            logger.warning(f"Could not parse snippet index from {snippet_id}, skipping sanity check")
            continue
        
        # Check if we have the corresponding raw snippet data
        if snippet_index >= len(raw_snippets_data):
            logger.warning(f"Snippet index {snippet_index} out of range for raw data, skipping")
            continue
        
        raw_snippet = raw_snippets_data[snippet_index]
        raw_content = raw_snippet.get('raw_content', [])
        original_content = golden_data.get('original_content', [])
        
        total_checks += 1
        
        # Compare the content
        if raw_content != original_content:
            failed_checks += 1
            logger.error(f"Sanity check FAILED for {snippet_id}:")
            logger.error(f"  Raw content length: {len(raw_content)}")
            logger.error(f"  Original content length: {len(original_content)}")
            
            # Show first few lines of difference for debugging
            max_lines_to_show = 5
            for i in range(min(max_lines_to_show, max(len(raw_content), len(original_content)))):
                raw_line = raw_content[i] if i < len(raw_content) else "<MISSING>"
                orig_line = original_content[i] if i < len(original_content) else "<MISSING>"
                
                if raw_line != orig_line:
                    logger.error(f"  Line {i+1}:")
                    logger.error(f"    Raw:      '{raw_line}'")
                    logger.error(f"    Original: '{orig_line}'")
            
            if len(raw_content) != len(original_content):
                logger.error(f"  Content length mismatch: {len(raw_content)} vs {len(original_content)}")
            
            all_checks_passed = False
        else:
            logger.debug(f"Sanity check PASSED for {snippet_id}")
    
    logger.info(f"Sanity check completed: {total_checks - failed_checks}/{total_checks} checks passed")
    
    if failed_checks > 0:
        logger.error(f"Sanity check FAILED: {failed_checks} mismatches found")
        return False
    else:
        logger.info("Sanity check PASSED: All original_content matches raw_content")
        return True


def call_gemini_api(snippet_content: str, ai_client: AIClient) -> str:
    """
    Call Gemini API to convert sprintf to snprintf using the AI client.
    
    Args:
        snippet_content: The code snippet to convert
        ai_client: Configured AIClient instance
        
    Returns:
        Converted code snippet
    """
    prompt = f"""Convert the following C code snippet to use snprintf instead of sprintf for better buffer safety.
Make sure to add the buffer size parameter and handle the return value appropriately.

Original code:
```c
{snippet_content}
```

Converted code:
```c
"""
    
    logger.debug(f"Calling {ai_client.model_name} API with prompt length: {len(prompt)}")
    
    try:
        response = ai_client.generate_content(prompt)
        
        # Extract code from response if it's wrapped in markdown code blocks
        if "```c" in response:
            # Find the code block and extract content
            start_marker = "```c"
            end_marker = "```"
            start_idx = response.find(start_marker)
            if start_idx != -1:
                start_idx += len(start_marker)
                end_idx = response.find(end_marker, start_idx)
                if end_idx != -1:
                    response = response[start_idx:end_idx].strip()
                else:
                    # No closing marker, take everything after start
                    response = response[start_idx:].strip()
            else:
                # No start marker, use response as-is
                response = response.strip()
        else:
            response = response.strip()
        
        return response
        
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")
        # Return a fallback response
        return f"// Error converting sprintf to snprintf: {e}\n{snippet_content}"


def generate_golden_answers_for_snippets(snippets: CodeSnippetList, api_key: str, 
                                       model: str = "gemini-2.5-pro",
                                       output_file: str = "golden_answers.json") -> Dict[str, Dict[str, List[str]]]:
    """
    Generate golden answers for all snippets using the specified Gemini model.
    
    Args:
        snippets: Code snippets to convert
        api_key: Gemini API key
        model: Gemini model to use
        output_file: File to save golden answers
        
    Returns:
        Dictionary mapping snippet ID to golden answer data with original and converted content
    """
    logger.info(f"Generating golden answers for {len(snippets)} snippets using {model}")
    
    # Initialize AI client
    try:
        ai_client = AIClient(api_key=api_key, model=model)
        logger.info(f"Initialized AI client with model: {model}")
    except Exception as e:
        logger.error(f"Failed to initialize AI client: {e}")
        raise
    
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
            
            # Call Gemini API using the AI client
            converted_code = call_gemini_api(snippet_content, ai_client)
            
            # Store golden answer with both original and converted content
            golden_answers[snippet_id] = {
                'original_content': snippet_content.split('\n'),
                'golden_answer': converted_code.split('\n')
            }
            manager.add_golden_answer(snippet_id, snippet_content, converted_code)
            
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
    parser.add_argument("--sanity-check", action="store_true", default=True,
                       help="Enable sanity check to compare original_content with raw_content (default: True)")
    parser.add_argument("--no-sanity-check", action="store_true",
                       help="Disable sanity check")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Determine if sanity check should be enabled
    enable_sanity_check = args.sanity_check and not args.no_sanity_check
    
    # Get API key
    api_key = args.api_key or get_api_key()
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
        
        # Load raw snippets data for sanity checking if enabled
        raw_snippets_data = None
        if enable_sanity_check:
            raw_snippets_data = load_snippets_raw_data(args.snippets_file)
            logger.info(f"Loaded raw snippets data for sanity checking: {len(raw_snippets_data)} snippets")
        
        # Generate golden answers
        golden_answers = generate_golden_answers_for_snippets(
            snippets, api_key, args.model, args.output_file
        )
        
        # Run sanity check if enabled
        if enable_sanity_check and raw_snippets_data is not None:
            logger.info("Running sanity check...")
            sanity_check_passed = sanity_check_original_content(golden_answers, raw_snippets_data)
            
            if not sanity_check_passed:
                logger.error("Sanity check failed! Generated golden answers may be corrupted.")
                logger.error("Please review the differences and regenerate if necessary.")
                # Don't exit with error code - let user decide what to do
            else:
                logger.info("Sanity check passed! All original_content matches raw_content.")
        
        # Print summary
        print(f"\n{'='*60}")
        print("GOLDEN ANSWER GENERATION COMPLETED")
        print(f"{'='*60}")
        print(f"Snippets processed: {len(golden_answers)}")
        print(f"Output file: {args.output_file}")
        print(f"Model used: {args.model}")
        print(f"Format: JSON with original_content and golden_answer as line arrays")
        if enable_sanity_check:
            print(f"Sanity check: {'PASSED' if sanity_check_passed else 'FAILED'}")
        else:
            print(f"Sanity check: DISABLED")
        print(f"{'='*60}")
        
    except Exception as e:
        logger.error(f"Error during golden answer generation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
