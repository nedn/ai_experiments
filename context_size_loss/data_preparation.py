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

import json
import logging
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

from code_snippet import CodeSnippet, CodeSnippetList
from git_grep_parser import parse_git_grep_output

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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
            
    def extract_sprintf_snippets(self) -> CodeSnippetList:
        """
        Extract sprintf code snippets using git grep with context.
        
        Returns:
            CodeSnippetList containing snippet information
        """
        logger.info("Extracting sprintf code snippets...")
        
        try:
            # Run git grep to find sprintf calls with context and make sure
            # we only match .c, .cc, .h files
            result = subprocess.run([
                "git", "grep", "-n", "--context=5", "sprintf", "--", "*.c", "*.cc", "*.cpp", "*.h"
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

        
    def save_snippets(self, snippets: CodeSnippetList) -> str:
        """
        Save extracted snippets to a structured JSON file.
        
        Args:
            snippets: CodeSnippetList containing snippet objects
            
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
                "total_snippets": snippets.get_total_snippets(),
                "total_files": snippets.get_file_count(),
                "total_lines": snippets.get_total_lines(),
                "total_matched_lines": snippets.get_total_matched_lines(),
                "total_context_lines": snippets.get_total_context_lines(),
                "description": "Code snippets containing sprintf calls from RISE repository"
            },
            "snippets": snippets.to_dict()["snippets"]
        }
        
        # Save to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Saved {snippets.get_total_snippets()} snippets to {output_file}")
        return str(output_file)
        
    def generate_summary_report(self, snippets: CodeSnippetList) -> str:
        """
        Generate a summary report of the extracted data.
        
        Args:
            snippets: CodeSnippetList containing snippet objects
            
        Returns:
            Path to the summary report file
        """
        report_file = self.output_dir / "extraction_summary.txt"
        
        # Get snippets grouped by file
        file_groups = snippets.get_snippets_by_file()
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("RISE sprintf Code Snippets Extraction Summary\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Repository: {self.repo_url}\n")
            f.write(f"Commit: {self.target_commit}\n")
            f.write(f"Total snippets extracted: {snippets.get_total_snippets()}\n")
            f.write(f"Files containing sprintf calls: {snippets.get_file_count()}\n")
            f.write(f"Total lines across all snippets: {snippets.get_total_lines()}\n")
            f.write(f"Total matched lines: {snippets.get_total_matched_lines()}\n")
            f.write(f"Total context lines: {snippets.get_total_context_lines()}\n\n")
            
            f.write("Snippets per file:\n")
            f.write("-" * 20 + "\n")
            for file_path, file_snippets in sorted(file_groups.items()):
                f.write(f"{file_path}: {len(file_snippets)} snippets\n")
                
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
