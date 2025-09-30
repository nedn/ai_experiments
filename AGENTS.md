# AI Agent Testing Guide

This document provides comprehensive instructions for AI agents on how to run tests, validate functionality, and focus on failure cases in the AI Experiments project.

## Quick Start

### Running All Tests
```bash
python run_tests.py
```

### Running Only Failed Tests (AI Focus Mode)
```bash
python run_tests.py --focus-failures
```

### Getting JSON Output for AI Processing
```bash
python run_tests.py --json
```

## Test Runner Features

The `run_tests.py` script is specifically designed to be AI-friendly with the following features:

### 1. Automatic Test Discovery
- Automatically finds all test files matching `test_*.py` and `*_test.py` patterns
- Recursively searches the entire project directory
- No manual configuration required

### 2. Failure-Focused Testing
- `--focus-failures` flag runs only previously failed tests
- Saves failed test information for quick re-runs
- Perfect for iterative debugging and fixing

### 3. AI-Friendly Output Formats
- `--json` flag provides structured JSON output for easy parsing
- Detailed error messages with line numbers
- Traceback information for debugging

### 4. Comprehensive Test Information
- Test execution time
- File paths and line numbers for failures
- Error messages and stack traces
- Test class and method names

## AI Agent Workflow

### Step 1: Initial Test Run
```bash
python run_tests.py --json
```
This gives you a complete overview of all tests and their status.

### Step 2: Focus on Failures
```bash
python run_tests.py --focus-failures --verbose
```
This runs only the tests that failed in the previous run, with detailed output.

### Step 3: Fix and Re-test
After making changes:
```bash
python run_tests.py --focus-failures
```
This quickly validates your fixes.

### Step 4: Full Validation
```bash
python run_tests.py
```
This ensures all tests pass after your changes.

## Understanding Test Output

### JSON Output Structure
```json
{
  "total_tests": 25,
  "passed": 23,
  "failed": 2,
  "errors": 0,
  "skipped": 0,
  "duration": 1.234,
  "test_results": [
    {
      "test_name": "TestGitGrepParser.test_parse_context_line",
      "test_file": "/path/to/test_git_grep_parser.py",
      "test_class": "TestGitGrepParser",
      "test_method": "test_parse_context_line",
      "status": "failed",
      "duration": 0.001,
      "error_message": "AssertionError: Expected 'file.c' but got 'file.py'",
      "error_traceback": "Traceback (most recent call last)...",
      "line_number": 98
    }
  ],
  "timestamp": "2024-01-15T10:30:00.000000",
  "python_version": "3.9.0",
  "platform": "linux"
}
```

### Key Fields for AI Processing
- `test_name`: Full test identifier
- `test_file`: Path to the test file
- `test_class`: Test class name
- `test_method`: Specific test method
- `status`: Test result (passed, failed, error, skipped)
- `error_message`: Human-readable error description
- `error_traceback`: Full stack trace for debugging
- `line_number`: Line number where error occurred

## Common AI Agent Tasks

### 1. Validating Code Changes
After making changes to any Python file:
```bash
python run_tests.py
```
This ensures your changes don't break existing functionality.

### 2. Debugging Specific Failures
```bash
python run_tests.py --focus-failures --verbose
```
This shows detailed information about what went wrong.

### 3. Testing Specific Files
```bash
python run_tests.py --test-files context_size_loss/test_git_grep_parser.py
```
This runs tests for a specific file only.

### 4. Pattern-Based Testing
```bash
python run_tests.py --pattern "*git*"
```
This runs only tests matching a specific pattern.

## Project Test Structure

The project currently has the following test files:
- `context_size_loss/test_git_grep_parser.py` - Tests for git grep parsing functionality
- `context_size_loss/test_code_snippet.py` - Tests for code snippet classes

### Test Organization
- Tests are co-located with the code they test
- Each test file follows the naming convention `test_*.py`
- Tests use Python's `unittest` framework
- Tests are comprehensive and cover edge cases

## Best Practices for AI Agents

### 1. Always Run Tests After Changes
```bash
python run_tests.py
```
This is the most important step to ensure code quality.

### 2. Use Focus Mode for Iterative Development
```bash
python run_tests.py --focus-failures
```
This saves time by running only relevant tests.

### 3. Use JSON Output for Programmatic Processing
```bash
python run_tests.py --json > test_results.json
```
This allows for automated analysis of test results.

### 4. Use Verbose Mode for Debugging
```bash
python run_tests.py --focus-failures --verbose
```
This provides detailed error information.

### 5. Check Test Coverage
The test runner provides comprehensive coverage information:
- Total number of tests
- Pass/fail/error counts
- Execution time
- Detailed failure information

## Troubleshooting

### No Tests Found
If you see "No test files found matching the pattern":
1. Check that test files follow the naming convention (`test_*.py` or `*_test.py`)
2. Verify you're running from the project root directory
3. Use `--pattern` to specify a different pattern

### Import Errors
If tests fail with import errors:
1. Ensure all dependencies are installed
2. Check that Python path includes the project directory
3. Verify that test files are in the correct location

### Permission Errors
If you get permission errors:
1. Ensure the script is executable: `chmod +x run_tests.py`
2. Check file permissions in the project directory

## Integration with Development Workflow

### Pre-commit Validation
```bash
python run_tests.py && echo "All tests passed" || echo "Tests failed"
```

### CI/CD Integration
```bash
python run_tests.py --json > test_results.json
```

### Automated Fixing
Use the JSON output to programmatically identify and fix test failures:
1. Parse the JSON output
2. Identify failed tests
3. Analyze error messages and line numbers
4. Apply fixes
5. Re-run tests

## Advanced Usage

### Custom Test Discovery
```bash
python run_tests.py --pattern "test_*integration*"
```

### Specific Test Execution
```bash
python run_tests.py --test-files context_size_loss/test_git_grep_parser.py context_size_loss/test_code_snippet.py
```

### Performance Testing
```bash
python run_tests.py --json | jq '.duration'
```

## Support and Maintenance

The test runner is designed to be self-maintaining and AI-friendly. It automatically:
- Discovers new test files
- Tracks test results
- Provides detailed error information
- Supports various output formats

For issues or questions about the test runner, refer to the script's built-in help:
```bash
python run_tests.py --help
```

## Conclusion

This test runner provides AI agents with powerful tools to:
1. Quickly validate code changes
2. Focus on specific failure cases
3. Get detailed debugging information
4. Maintain code quality through automated testing

Use these tools to ensure the project remains functional and reliable as you make changes and improvements.
