#!/usr/bin/env python3
"""
Comprehensive Test Runner for AI Experiments Project

This script provides a unified way to run all Python unit tests in the project,
with special features designed for AI agents to easily identify and focus on test failures.

Key Features:
- Automatic test discovery across the entire project
- Detailed failure reporting with context
- AI-friendly output formats (JSON, structured text)
- Focus mode for running only failed tests
- Integration with common CI/CD workflows
- Support for different verbosity levels
- Test result caching and comparison

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --focus-failures  # Run only previously failed tests
    python run_tests.py --json            # Output results in JSON format
    python run_tests.py --verbose         # Detailed output
    python run_tests.py --help            # Show all options
"""

import argparse
import json
import os
import sys
import time
import unittest
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import subprocess
import tempfile


@dataclass
class TestResult:
    """Structured representation of a test result."""
    test_name: str
    test_file: str
    test_class: str
    test_method: str
    status: str  # 'passed', 'failed', 'error', 'skipped'
    duration: float
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class TestSuiteResult:
    """Structured representation of a test suite result."""
    total_tests: int
    passed: int
    failed: int
    errors: int
    skipped: int
    duration: float
    test_results: List[TestResult]
    timestamp: str
    python_version: str
    platform: str


class AITestRunner:
    """Test runner optimized for AI agent usage."""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.test_results_file = self.project_root / ".test_results.json"
        self.failed_tests_file = self.project_root / ".failed_tests.json"
        
    def discover_tests(self, pattern: str = "test_*.py") -> List[str]:
        """Discover all test files in the project."""
        test_files = []
        
        # Search for test files recursively
        for test_file in self.project_root.rglob(pattern):
            if test_file.is_file() and test_file.suffix == '.py':
                test_files.append(str(test_file))
        
        # Also search for files ending with _test.py
        for test_file in self.project_root.rglob("*_test.py"):
            if test_file.is_file() and test_file.suffix == '.py':
                test_files.append(str(test_file))
        
        return sorted(test_files)
    
    def run_tests(self, 
                  test_files: Optional[List[str]] = None,
                  focus_failures: bool = False,
                  verbose: bool = False,
                  json_output: bool = False) -> TestSuiteResult:
        """Run tests and return structured results."""
        
        if test_files is None:
            test_files = self.discover_tests()
        
        if focus_failures:
            test_files = self._get_failed_tests()
            if not test_files:
                print("No previously failed tests found.")
                return TestSuiteResult(
                    total_tests=0, passed=0, failed=0, errors=0, skipped=0,
                    duration=0.0, test_results=[], timestamp=datetime.now().isoformat(),
                    python_version=sys.version, platform=sys.platform
                )
        
        # Set up test discovery
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Add tests from each file
        for test_file in test_files:
            if os.path.exists(test_file):
                # Add the directory to Python path
                test_dir = os.path.dirname(os.path.abspath(test_file))
                if test_dir not in sys.path:
                    sys.path.insert(0, test_dir)
                
                try:
                    # Discover tests in the file
                    module_suite = loader.loadTestsFromName(os.path.basename(test_file)[:-3])
                    suite.addTest(module_suite)
                except Exception as e:
                    print(f"Warning: Could not load tests from {test_file}: {e}")
        
        # Run tests with custom result collector
        start_time = time.time()
        
        # Create a custom result collector
        result_collector = AITestResult()
        
        # Run the tests
        test_result = result_collector
        suite.run(test_result)
        duration = time.time() - start_time
        
        # Convert test results to proper format
        test_results = []
        for result in result_collector.test_results:
            test_results.append(TestResult(
                test_name=result['test_name'],
                test_file=result['test_file'],
                test_class=result['test_class'],
                test_method=result['test_method'],
                status=result['status'],
                duration=0.0,  # We'll calculate this later if needed
                error_message=result['error_message'],
                error_traceback=result['error_traceback'],
                line_number=result['line_number']
            ))
        
        suite_result = TestSuiteResult(
            total_tests=test_result.testsRun,
            passed=test_result.testsRun - len(test_result.failures) - len(test_result.errors),
            failed=len(test_result.failures),
            errors=len(test_result.errors),
            skipped=len(getattr(test_result, 'skipped', [])),
            duration=duration,
            test_results=test_results,
            timestamp=datetime.now().isoformat(),
            python_version=sys.version,
            platform=sys.platform
        )
        
        # Save results for future reference
        self._save_test_results(suite_result)
        
        return suite_result
    
    def _get_failed_tests(self) -> List[str]:
        """Get list of previously failed test files."""
        if not self.failed_tests_file.exists():
            return []
        
        try:
            with open(self.failed_tests_file, 'r') as f:
                failed_data = json.load(f)
            return failed_data.get('failed_test_files', [])
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_test_results(self, suite_result: TestSuiteResult):
        """Save test results for future reference."""
        # Save full results
        with open(self.test_results_file, 'w') as f:
            json.dump(asdict(suite_result), f, indent=2)
        
        # Save failed test files for focus mode
        failed_files = set()
        for test_result in suite_result.test_results:
            if test_result.status in ['failed', 'error']:
                failed_files.add(test_result.test_file)
        
        failed_data = {
            'failed_test_files': list(failed_files),
            'last_run': suite_result.timestamp
        }
        
        with open(self.failed_tests_file, 'w') as f:
            json.dump(failed_data, f, indent=2)
    
    def print_summary(self, suite_result: TestSuiteResult, verbose: bool = False):
        """Print a human-readable test summary."""
        print("\n" + "="*80)
        print("TEST EXECUTION SUMMARY")
        print("="*80)
        print(f"Total Tests: {suite_result.total_tests}")
        print(f"Passed: {suite_result.passed}")
        print(f"Failed: {suite_result.failed}")
        print(f"Errors: {suite_result.errors}")
        print(f"Skipped: {suite_result.skipped}")
        print(f"Duration: {suite_result.duration:.2f} seconds")
        print(f"Python Version: {suite_result.python_version}")
        print(f"Platform: {suite_result.platform}")
        print(f"Timestamp: {suite_result.timestamp}")
        
        if suite_result.failed > 0 or suite_result.errors > 0:
            print("\n" + "="*80)
            print("FAILED TESTS DETAILS")
            print("="*80)
            
            for test_result in suite_result.test_results:
                if test_result.status in ['failed', 'error']:
                    print(f"\n❌ {test_result.test_name}")
                    print(f"   File: {test_result.test_file}")
                    print(f"   Class: {test_result.test_class}")
                    print(f"   Method: {test_result.test_method}")
                    print(f"   Duration: {test_result.duration:.3f}s")
                    
                    if test_result.error_message:
                        print(f"   Error: {test_result.error_message}")
                    
                    if verbose and test_result.error_traceback:
                        print(f"   Traceback:\n{test_result.error_traceback}")
        
        print("\n" + "="*80)
        if suite_result.failed == 0 and suite_result.errors == 0:
            print("✅ ALL TESTS PASSED!")
        else:
            print(f"❌ {suite_result.failed + suite_result.errors} TESTS FAILED")
            print(f"\nTo run only failed tests: python run_tests.py --focus-failures")
        print("="*80)
    
    def print_json_summary(self, suite_result: TestSuiteResult):
        """Print test results in JSON format for AI processing."""
        print(json.dumps(asdict(suite_result), indent=2))


class AITestResult(unittest.TestResult):
    """Custom test result class for AI-friendly output."""
    
    def __init__(self, stream=None, descriptions=None, verbosity=None):
        super().__init__(stream, descriptions, verbosity)
        self.test_results = []
    
    def addSuccess(self, test):
        super().addSuccess(test)
        self._record_test_result(test, 'passed')
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._record_test_result(test, 'failed', err)
    
    def addError(self, test, err):
        super().addError(test, err)
        self._record_test_result(test, 'error', err)
    
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._record_test_result(test, 'skipped')
    
    def _record_test_result(self, test, status, err=None):
        """Record a test result with detailed information."""
        test_name = str(test)
        test_class = test.__class__.__name__
        test_method = test._testMethodName
        
        # Extract file path from test
        test_file = "unknown"
        if hasattr(test, '_testMethodDoc'):
            # Try to get file from test module
            test_module = test.__class__.__module__
            if test_module != '__main__':
                try:
                    module = sys.modules[test_module]
                    test_file = getattr(module, '__file__', 'unknown')
                except (KeyError, AttributeError):
                    pass
        
        error_message = None
        error_traceback = None
        line_number = None
        
        if err:
            error_message = str(err[1])
            error_traceback = ''.join(err[2])
            # Try to extract line number from traceback
            if err[2]:
                for line in err[2]:
                    if 'line ' in str(line):
                        try:
                            line_number = int(str(line).split('line ')[1].split(',')[0])
                            break
                        except (ValueError, IndexError):
                            pass
        
        self.test_results.append({
            'test_name': test_name,
            'test_file': test_file,
            'test_class': test_class,
            'test_method': test_method,
            'status': status,
            'error_message': error_message,
            'error_traceback': error_traceback,
            'line_number': line_number
        })


class AITestResultCollector:
    """Collects test results for AI processing."""
    
    def __init__(self):
        self.test_results = []
        self.start_times = {}
    
    def write(self, text):
        """Capture test output."""
        pass
    
    def flush(self):
        """Flush output."""
        pass
    
    def get_test_results(self) -> List[TestResult]:
        """Get collected test results."""
        return self.test_results


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="AI-Optimized Test Runner for AI Experiments Project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py --focus-failures  # Run only previously failed tests
  python run_tests.py --json            # Output results in JSON format
  python run_tests.py --verbose         # Detailed output with tracebacks
  python run_tests.py --pattern "*test*" # Run tests matching pattern
  python run_tests.py --help            # Show this help message

AI Agent Usage:
  This script is designed to be AI-friendly. Use --json for structured output
  and --focus-failures to quickly identify and fix test issues.
        """
    )
    
    parser.add_argument(
        '--focus-failures',
        action='store_true',
        help='Run only previously failed tests (useful for AI agents)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format (AI-friendly)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output with detailed tracebacks'
    )
    
    parser.add_argument(
        '--pattern', '-p',
        default='test_*.py',
        help='Pattern to match test files (default: test_*.py)'
    )
    
    parser.add_argument(
        '--project-root',
        default=None,
        help='Project root directory (default: current directory)'
    )
    
    parser.add_argument(
        '--test-files',
        nargs='*',
        help='Specific test files to run'
    )
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = AITestRunner(args.project_root)
    
    # Discover and run tests
    if args.test_files:
        test_files = args.test_files
    else:
        test_files = runner.discover_tests(args.pattern)
    
    if not test_files:
        print("No test files found matching the pattern.")
        return 1
    
    print(f"Found {len(test_files)} test file(s):")
    for test_file in test_files:
        print(f"  - {test_file}")
    print()
    
    # Run tests
    suite_result = runner.run_tests(
        test_files=test_files,
        focus_failures=args.focus_failures,
        verbose=args.verbose,
        json_output=args.json
    )
    
    # Output results
    if args.json:
        runner.print_json_summary(suite_result)
    else:
        runner.print_summary(suite_result, args.verbose)
    
    # Return appropriate exit code
    return 0 if suite_result.failed == 0 and suite_result.errors == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
