#!/usr/bin/env python3
"""
Git Grep Parser Module

This module provides functions for parsing git grep output to extract structured
code snippets. It handles the specific format of git grep output with context lines
and matched lines.
"""

import argparse
import json
import logging
import re
import sys
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from code_snippet import CodeSnippet, CodeSnippetList


def is_separator_line(line: str) -> bool:
    """
    Check if a line is a separator line in git grep output.
    
    Args:
        line: The line to check
        
    Returns:
        True if the line is a separator (--), False otherwise
    """
    return line.strip() == '--'


def parse_context_line(line: str) -> Tuple[bool, Optional[str], Optional[int], Optional[str]]:
    """
    Parse a context line from git grep output.
    
    Context lines have format: filename-line_number- content
    
    Args:
        line: The line to parse
        
    Returns:
        Tuple of (is_context_line, filename, line_number, content)
    """
    # Context lines have format: filename-line_number- content
    # Use regex to match the exact pattern: filename-line_number- (with at least one dash before line number)
    pattern = r'^[^:]+-\d+-'
    is_context_line = bool(re.match(pattern, line))
    if is_context_line:
        parts = line.split('-', 2)
        return True, parts[0], int(parts[1]), parts[2]
    return False, None, None, None


def parse_matched_line(line: str) -> Tuple[bool, Optional[str], Optional[int], Optional[str]]:
    """
    Parse a matched line from git grep output.
    
    Matched lines have format: filename:line_number:content
    
    Args:
        line: The line to parse
        
    Returns:
        Tuple of (is_matched_line, filename, line_number, content)
    """
    # Matched lines have format: filename:line_number:content
    # Use regex to match the exact pattern: filename:line_number: (with exactly one colon before line number)
    pattern = r'^[^:]+:\d+:'
    is_matched_line = bool(re.match(pattern, line))
    if is_matched_line:
        parts = line.split(':', 2)
        return True, parts[0], int(parts[1]), parts[2]
    return False, None, None, None


def is_context_line(line: str) -> bool:
    """
    Check if a line is a context line in git grep output.
    
    Args:
        line: The line to check
        
    Returns:
        True if the line is a context line, False otherwise
    """
    pattern = r'^[^:]+-\d+-'
    return bool(re.match(pattern, line))

class LineType(Enum):
    SEPARATOR = "separator"
    CONTEXT = "context"
    MATCHED = "matched" 

def parse_git_grep_line(line: str) -> Tuple[LineType, Optional[str], Optional[int], Optional[str]]:
    """
    Parse a line from git grep output.
    
    Args:
        line: The line to parse
    """
    if is_separator_line(line):
        return LineType.SEPARATOR, None, None, None
    parsed_context_line = parse_context_line(line)
    if parsed_context_line[0]:
        return LineType.CONTEXT, parsed_context_line[1], parsed_context_line[2], parsed_context_line[3]
    parsed_matched_line = parse_matched_line(line)
    if parsed_matched_line[0]:
        return LineType.MATCHED, parsed_matched_line[1], parsed_matched_line[2], parsed_matched_line[3]
    raise ValueError(f"Invalid line: {line}")


def parse_git_grep_output(output: str) -> CodeSnippetList:
    """
    Parse git grep output to extract structured snippet data.
    
    Git grep output format (from actual RISE repository):
    - Matching lines: filename:line_number:content
    - Context lines (before/after): filename-line_number-content (with dashes)
    - Separator lines: --
    
    Example actual output when --context=2 is used:
    $ git grep -n --context 2 sprintf -- *.c *.cc *.h
    extlib/libpng/png.c-639-   {
    extlib/libpng/png.c-640-      wchar_t time_buf[29];
    extlib/libpng/png.c:641:      wsprintf(time_buf, TEXT("%d %S %d %02d:%02d:%02d +0000"),
    extlib/libpng/png.c-642-          ptime->day % 32, short_months[(ptime->month - 1) % 12],
    extlib/libpng/png.c-643-        ptime->year, ptime->hour % 24, ptime->minute % 60,
    --
    extlib/libpng/png.c-650-   {
    extlib/libpng/png.c-651-      char near_time_buf[29];
    extlib/libpng/png.c:652:      sprintf(near_time_buf, "%d %s %d %02d:%02d:%02d +0000",
    extlib/libpng/png.c-653-          ptime->day % 32, short_months[(ptime->month - 1) % 12],
    extlib/libpng/png.c-654-          ptime->year, ptime->hour % 24, ptime->minute % 60,
    --
    extlib/libpng/pnggccrd.c-5104-#if !defined(PNG_1_0_X)
    --
    extlib/libpng/pnggccrd.c-5108-"x86");
    extlib/libpng/pnggccrd.c-5109-         break;
    extlib/libpng/pnggccrd.c:5110:      case 2: sprintf(filnm, "up-%s",
    extlib/libpng/pnggccrd.c-5111-#ifdef PNG_ASSEMBLER_CODE_SUPPORTED
    extlib/libpng/pnggccrd.c-5112-#if !defined(PNG_1_0_X)
    --
    extlib/libpng/pnggccrd.c-5116- "x86");
    extlib/libpng/pnggccrd.c-5117-         break;
    extlib/libpng/pnggccrd.c:5118:      case 3: sprintf(filnm, "avg-%s",
    extlib/libpng/pnggccrd.c-5119-#if defined(PNG_ASSEMBLER_CODE_SUPPORTED) && defined(PNG_THREAD_UNSAFE_OK)
    extlib/libpng/pnggccrd.c-5120-#if !defined(PNG_1_0_X)
    --

    Our parsing strategy is to define snippet as a contiguous block of lines that contain the sprintf calls 
    based on the output of git grep. Separate snippets are separated by separator lines "--".
    
    Note: All returned CodeSnippet objects are automatically frozen (immutable) for thread safety
    and data integrity. The CodeSnippetList ensures all snippets are frozen and the list itself is immutable.
    
    Args:
        output: Raw output from git grep command

        
    Returns:
        CodeSnippetList containing frozen CodeSnippet objects with the parsed snippet data.
    """
    snippets = []
    current_snippet = None
    
    lines = output.strip().split('\n')
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue
        line_type, filename, line_number, content = parse_git_grep_line(line)
        
        if line_type == LineType.SEPARATOR:
            # Save current snippet if it exists
            if current_snippet is not None:
                current_snippet.freeze()  # Make snippet immutable before adding to list
                snippets.append(current_snippet)
                current_snippet = None
            continue
        
        if current_snippet is None:
            current_snippet = CodeSnippet(
                file_path=filename,
                matched_lines=[],
                context_lines=[],
                raw_surrounding_git_grep_lines=[],
                raw_content=[]
            )
        current_snippet.raw_surrounding_git_grep_lines.append(line)
        current_snippet.raw_content.append(content)
        if line_type == LineType.MATCHED:
            current_snippet.matched_lines.append(line_number)
        elif line_type == LineType.CONTEXT:
            current_snippet.context_lines.append(line_number)
    
    # Don't forget to add the last snippet if it exists
    if current_snippet is not None:
        current_snippet.freeze()  # Make snippet immutable before adding to list
        snippets.append(current_snippet)

    return CodeSnippetList(snippets)

def setup_logging(debug: bool = False) -> None:
    """Set up logging configuration for debugging."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main():
    """Main function to handle command-line execution."""
    parser = argparse.ArgumentParser(
        description="Parse git grep output and generate JSON snippets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse git grep output from stdin and save to output.json
  git grep -n --context 2 sprintf -- *.c *.cc *.h | python git_grep_parser.py
  
  # Parse with debug output
  git grep -n --context 2 sprintf -- *.c *.cc *.h | python git_grep_parser.py --debug
  
  # Specify custom output file
  git grep -n --context 2 sprintf -- *.c *.cc *.h | python git_grep_parser.py --output my_snippets.json
        """
    )
    
    parser.add_argument(
        '--output', '-o',
        default='output.json',
        help='Output JSON file path (default: output.json)'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--input', '-i',
        help='Input file path (if not provided, reads from stdin)'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)
    
    try:
        # Read input
        if args.input:
            logger.info(f"Reading input from file: {args.input}")
            with open(args.input, 'r', encoding='utf-8') as f:
                input_data = f.read()
        else:
            logger.info("Reading input from stdin")
            input_data = sys.stdin.read()
        
        if not input_data.strip():
            logger.warning("No input data provided")
            return
        
        # Parse the git grep output
        logger.info("Parsing git grep output...")
        snippets = parse_git_grep_output(input_data)
        
        logger.info(f"Parsed {snippets.get_total_snippets()} snippets")
        
        # Write output to JSON file
        logger.info(f"Writing output to: {args.output}")
        with open(args.output, 'w', encoding='utf-8') as f:
            # Use CodeSnippetList's to_dict method for JSON serialization
            json.dump(snippets.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully wrote {snippets.get_total_snippets()} snippets to {args.output}")
        
        # Print summary to stderr so it doesn't interfere with piping
        print(f"Parsed {snippets.get_total_snippets()} snippets and saved to {args.output}", file=sys.stderr)
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"JSON encoding error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.debug:
            logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == "__main__":
    main()