#!/usr/bin/env python3
"""
Git Grep Parser Module

This module provides functions for parsing git grep output to extract structured
code snippets. It handles the specific format of git grep output with context lines
and matched lines.
"""

import re
from typing import List, Dict, Any, Tuple, Optional


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


def extract_file_and_line(line: str) -> Tuple[Optional[str], Optional[int]]:
    """
    Extract file path and line number from a git grep line.
    
    Args:
        line: The line to parse
        
    Returns:
        Tuple of (file_path, line_number)
    """
    if ':' in line:
        parts = line.split(':', 2)
        if len(parts) >= 2:
            file_path = parts[0]
            try:
                line_number = int(parts[1])
                return file_path, line_number
            except ValueError:
                return None, None
    return None, None


def parse_git_grep_output(output: str) -> List[Dict[str, Any]]:
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
    
    Args:
        output: Raw output from git grep command

        
    Returns:
        List of snippet dictionaries. Each snippet dictionary contains the following keys:
        - file_path: The path to the file containing the snippet
        - sprintf_line: The line numbers of the sprintf calls. Note that this can be a list of line numbers
            if there are multiple sprintf calls in the snippet spanning multiple lines.
        - context_lines: A list of context lines surrounding the sprintf calls.
        - raw_content: The raw content of the snippet. This includes the sprintf call and the context lines.
    """
    snippets = []
    current_snippet = None

    for line in output.split('\n'):
        if not line.strip():
            continue
            
        # Skip separator lines
        if is_separator_line(line):
            # Save previous snippet if exists
            if current_snippet:
                snippets.append(current_snippet)
                current_snippet = None
            continue
            
        # Check if this is a matched line (contains sprintf)
        is_matched, file_path, line_number, content = parse_matched_line(line)
        if is_matched:
            if file_path and line_number:
                # If we have a current snippet and it's the same file, add to existing snippet
                if current_snippet and current_snippet["file_path"] == file_path:
                    # For now, just update the raw content (multiple sprintf calls in same snippet not supported)
                    current_snippet["raw_content"] += "\n" + line
                else:
                    # Save previous snippet if exists
                    if current_snippet:
                        snippets.append(current_snippet)
                    
                    # Start new snippet
                    current_snippet = {
                        "file_path": file_path,
                        "sprintf_line": line_number,  # Single line number
                        "context_lines": [],
                        "raw_content": line
                    }
                
        elif current_snippet and is_context_line(line):
            # This is a context line (before or after the match)
            # Format: filename-line_number- content
            current_snippet["context_lines"].append(line)
            current_snippet["raw_content"] += "\n" + line
            
    # Add the last snippet
    if current_snippet:
        snippets.append(current_snippet)
        
    return snippets
