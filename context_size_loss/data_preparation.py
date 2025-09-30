#!/usr/bin/env python3
"""
Data Preparation Script for Context Size Loss Analysis

This script prepares data for analyzing the impact of context size on AI performance
by extracting sprintf code snippets from the RISE (Realistic Image Synthesis Engine)
repository. The analysis focuses on understanding how the number of tasks in a single
AI prompt affects performance.

Data Preparation Process:
1. Clone the RISE repository from GitHub
2. Checkout to specific commit 297d0339a7f7acd1418e322a30a21f44c7dbbb1d
   (This commit contains numerous sprintf calls for analysis)
3. Extract sprintf code snippets using git grep with context (-10, +10 lines)
4. Store snippets in a structured JSON format for easy parsing

The extracted data will be used to study how context size (number of sprintf calls
and surrounding code) affects AI model performance in code understanding tasks.

Author: AI Assistant
Date: 2025
"""

import os
import json
import subprocess
import shutil
import sys
from pathlib import Path
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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
    SEPARATOR = '--'

    def is_separator_line(line):
        return line.strip() == SEPARATOR
        
    def is_context_line(line):
        # Context lines have format: filename-line_number- content
        return line.count('-') >= 2 and ':' not in line
        
    def is_matched_line(line):
        # Matched lines have format: filename:line_number:content
        return ':' in line and not line.startswith('-')
        
    def extract_file_and_line(line):
        """Extract file path and line number from a git grep line."""
        if ':' in line:
            parts = line.split(':', 2)
            if len(parts) >= 2:
                file_path = parts[0]
                line_info = parts[1]
                
                # Extract line number
                line_parts = line_info.split(':', 1)
                line_number = int(line_parts[0]) if line_parts[0].isdigit() else 0
                return file_path, line_number
        return None, None

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
        if is_matched_line(line):
            file_path, line_number = extract_file_and_line(line)
            
            if file_path and line_number:
                # If we have a current snippet and it's the same file, add to existing snippet
                if current_snippet and current_snippet["file_path"] == file_path:
                    # Add this sprintf line to the list
                    if line_number not in current_snippet["sprintf_line"]:
                        current_snippet["sprintf_line"].append(line_number)
                    current_snippet["raw_content"] += "\n" + line
                else:
                    # Save previous snippet if exists
                    if current_snippet:
                        snippets.append(current_snippet)
                    
                    # Start new snippet
                    current_snippet = {
                        "file_path": file_path,
                        "sprintf_line": [line_number],  # List of line numbers
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

class RISEDataPreparation:
    """Handles the complete data preparation pipeline for RISE sprintf analysis."""
    
    def __init__(self, output_dir: str = "rise_data"):
        """
        Initialize the data preparation pipeline.
        
        Args:
            output_dir: Directory to store extracted data and cloned repository
        """
        self.output_dir = Path(output_dir)
        self.rise_repo_dir = self.output_dir / "RISE"
        self.target_commit = "297d0339a7f7acd1418e322a30a21f44c7dbbb1d"
        self.repo_url = "https://github.com/aravindkrishnaswamy/RISE"
        
    def setup_directories(self) -> None:
        """Create necessary directories for data preparation."""
        self.output_dir.mkdir(exist_ok=True)
        logger.info(f"Created output directory: {self.output_dir}")
        
    def clone_repository(self) -> None:
        """Clone the RISE repository from GitHub or ensure existing repo is ready."""
        if self.rise_repo_dir.exists():
            logger.info("RISE repository already exists, checking if it's a valid git repository")
            # Check if it's a valid git repository
            try:
                subprocess.run([
                    "git", "rev-parse", "--git-dir"
                ], cwd=self.rise_repo_dir, check=True, capture_output=True, text=True)
                logger.info("Existing repository is valid, skipping clone")
                return
            except subprocess.CalledProcessError:
                logger.warning("Existing directory is not a valid git repository, removing and cloning fresh")
                shutil.rmtree(self.rise_repo_dir)
            
        logger.info(f"Cloning RISE repository from {self.repo_url}")
        try:
            subprocess.run([
                "git", "clone", self.repo_url, str(self.rise_repo_dir)
            ], check=True, capture_output=True, text=True)
            logger.info("Successfully cloned RISE repository")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to clone repository: {e}")
            raise
            
    def checkout_commit(self) -> None:
        """Checkout the specific commit containing sprintf calls."""
        logger.info(f"Checking out commit {self.target_commit}")
        
        # First, fetch all remote references to ensure we have the commit
        try:
            subprocess.run([
                "git", "fetch", "--all"
            ], cwd=self.rise_repo_dir, check=True, capture_output=True, text=True)
            logger.info("Fetched latest changes from remote")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to fetch from remote: {e}")
            # Continue anyway, the commit might already be available locally
        
        # Check if we're already on the target commit
        try:
            result = subprocess.run([
                "git", "rev-parse", "HEAD"
            ], cwd=self.rise_repo_dir, capture_output=True, text=True)
            current_commit = result.stdout.strip()
            
            if current_commit == self.target_commit:
                logger.info(f"Already on target commit {self.target_commit}")
                return
        except subprocess.CalledProcessError as e:
            logger.warning(f"Could not check current commit: {e}")
        
        # Checkout the target commit
        try:
            subprocess.run([
                "git", "checkout", self.target_commit
            ], cwd=self.rise_repo_dir, check=True, capture_output=True, text=True)
            logger.info(f"Successfully checked out commit {self.target_commit}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to checkout commit: {e}")
            raise
            
    def extract_sprintf_snippets(self) -> List[Dict[str, Any]]:
        """
        Extract sprintf code snippets using git grep with context.
        
        Returns:
            List of dictionaries containing snippet information
        """
        logger.info("Extracting sprintf code snippets...")
        
        try:
            # Run git grep to find sprintf calls with context and make sure
            # we only match .c, .cc, .h files
            result = subprocess.run([
                "git", "grep", "-n", "--context=10", "sprintf", "--", "*.c", "*.cc", "*.h"
            ], cwd=self.rise_repo_dir, capture_output=True, text=True)
            
            if result.returncode != 0 and result.returncode != 1:
                # Exit code 1 means no matches found, which is acceptable
                logger.error(f"Git grep failed with return code {result.returncode}")
                raise subprocess.CalledProcessError(result.returncode, "git grep")
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to run git grep: {e}")
            raise
            
        # Parse the output
        snippets = parse_git_grep_output(result.stdout)
        logger.info(f"Extracted {len(snippets)} sprintf code snippets")
        
        return snippets

        
    def save_snippets(self, snippets: List[Dict[str, Any]]) -> str:
        """
        Save extracted snippets to a structured JSON file.
        
        Args:
            snippets: List of snippet dictionaries
            
        Returns:
            Path to the saved file
        """
        output_file = self.output_dir / "sprintf_snippets.json"
        
        # Prepare data structure
        data = {
            "metadata": {
                "repository": self.repo_url,
                "commit": self.target_commit,
                "extraction_date": subprocess.run(["date"], capture_output=True, text=True).stdout.strip(),
                "total_snippets": len(snippets),
                "description": "Code snippets containing sprintf calls from RISE repository"
            },
            "snippets": snippets
        }
        
        # Save to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Saved {len(snippets)} snippets to {output_file}")
        return str(output_file)
        
    def generate_summary_report(self, snippets: List[Dict[str, Any]]) -> str:
        """
        Generate a summary report of the extracted data.
        
        Args:
            snippets: List of snippet dictionaries
            
        Returns:
            Path to the summary report file
        """
        report_file = self.output_dir / "extraction_summary.txt"
        
        # Count snippets by file
        file_counts = {}
        for snippet in snippets:
            file_path = snippet["file_path"]
            file_counts[file_path] = file_counts.get(file_path, 0) + 1
            
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("RISE sprintf Code Snippets Extraction Summary\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Repository: {self.repo_url}\n")
            f.write(f"Commit: {self.target_commit}\n")
            f.write(f"Total snippets extracted: {len(snippets)}\n")
            f.write(f"Files containing sprintf calls: {len(file_counts)}\n\n")
            
            f.write("Snippets per file:\n")
            f.write("-" * 20 + "\n")
            for file_path, count in sorted(file_counts.items()):
                f.write(f"{file_path}: {count} snippets\n")
                
        logger.info(f"Generated summary report: {report_file}")
        return str(report_file)
        
    def run_full_pipeline(self) -> Dict[str, str]:
        """
        Execute the complete data preparation pipeline.
        
        Returns:
            Dictionary with paths to generated files
        """
        logger.info("Starting RISE data preparation pipeline...")
        
        try:
            # Step 1: Setup directories
            self.setup_directories()
            
            # Step 2: Clone repository
            self.clone_repository()
            
            # Step 3: Checkout specific commit
            self.checkout_commit()
            
            # Step 4: Extract sprintf snippets
            snippets = self.extract_sprintf_snippets()
            
            # Step 5: Save snippets
            snippets_file = self.save_snippets(snippets)
            
            # Step 6: Generate summary report
            summary_file = self.generate_summary_report(snippets)
            
            logger.info("Data preparation pipeline completed successfully!")
            
            return {
                "snippets_file": snippets_file,
                "summary_file": summary_file,
                "repository_path": str(self.rise_repo_dir)
            }
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise

def main():
    """Main function to run the data preparation pipeline."""
    try:
        # Initialize data preparation
        preparator = RISEDataPreparation()
        
        # Run the full pipeline
        results = preparator.run_full_pipeline()
        
        print("\n" + "="*60)
        print("DATA PREPARATION COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"Snippets file: {results['snippets_file']}")
        print(f"Summary report: {results['summary_file']}")
        print(f"Repository path: {results['repository_path']}")
        print("\nThe extracted data is ready for context size loss analysis.")
        
    except Exception as e:
        logger.error(f"Data preparation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
