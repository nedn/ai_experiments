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

### 5. Working with Common Utilities
When working with files in the `common_util/` directory:
- Import from `common_util` module: `from common_util.ai_client import AIClient`
- Test common utilities: `python run_tests.py --pattern "common_util/*"`
- The AI client and examples are self-contained in this directory

## Project Structure

The project is organized into the following main directories:

### Top Level
- `run_tests.py` - Main test runner script (AI-friendly with JSON output)
- `AGENTS.md` - This guide for AI agents
- `LICENSE` - Project license

### Directory Organization
- `common_util/` - Shared utilities and common code
  - `ai_client.py` - AI client for Gemini API integration
  - `example_usage.py` - Usage examples for the AI client
  - `test_ai_client.py` - Tests for the AI client
- `context_size_loss/` - Context size loss experiments
  - `test_validation.py` - Validation tests
  - `tests/` - Additional test files
    - `test_code_snippet.py` - Tests for code snippet classes
    - `test_git_grep_parser.py` - Tests for git grep parsing functionality
- `ai_constraining/` - AI constraining experiments

### Test Structure

The project currently has the following test files:
- `common_util/test_ai_client.py` - Tests for AI client functionality
- `context_size_loss/test_validation.py` - Validation tests for context size loss experiments
- `context_size_loss/tests/test_code_snippet.py` - Tests for code snippet classes
- `context_size_loss/tests/test_git_grep_parser.py` - Tests for git grep parsing functionality

### Test Organization
- Tests are co-located with the code they test
- Each test file follows the naming convention `test_*.py`
- Tests use Python's `unittest` framework
- Tests are comprehensive and cover edge cases
- Common utilities are tested in the `common_util/` directory

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
4. For `common_util/` imports, use: `from common_util.ai_client import AIClient`
5. Check that relative imports in `common_util/` files are working correctly

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

### Testing Common Utilities
```bash
python run_tests.py --test-files common_util/test_ai_client.py
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


# Python Code Style

This section outlines the Python coding standards that should be followed in this project, based on the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).

## Import Rules

### 2.2 Imports

Use `import` statements for packages and modules only, not for individual types, classes, or functions.

#### 2.2.1 Definition

Reusability mechanism for sharing code from one module to another.

#### 2.2.2 Pros

The namespace management convention is simple. The source of each identifier is indicated in a consistent way; `x.Obj` says that object `Obj` is defined in module `x`.

#### 2.2.3 Cons

Module names can still collide. Some module names are inconveniently long.

#### 2.2.4 Decision

* Use `import x` for importing packages and modules.
* Use `from x import y` where `x` is the package prefix and `y` is the module name with no prefix.
* Use `from x import y as z` in any of the following circumstances:  
   * Two modules named `y` are to be imported.  
   * `y` conflicts with a top-level name defined in the current module.  
   * `y` conflicts with a common parameter name that is part of the public API (e.g., `features`).  
   * `y` is an inconveniently long name.  
   * `y` is too generic in the context of your code (e.g., `from storage.file_system import options as fs_options`).
* Use `import y as z` only when `z` is a standard abbreviation (e.g., `import numpy as np`).

For example the module `sound.effects.echo` may be imported as follows:

```python
from sound.effects import echo
...
echo.EchoFilter(input, output, delay=0.7, atten=4)
```

Do not use relative names in imports. Even if the module is in the same package, use the full package name. This helps prevent unintentionally importing a package twice.

##### 2.2.4.1 Exemptions

Exemptions from this rule:

* Symbols from the following modules are used to support static analysis and type checking:  
   * typing module  
   * collections.abc module  
   * typing_extensions module
* Redirects from the six.moves module.

### 2.3 Packages

Import each module using the full pathname location of the module.

#### 2.3.1 Pros

Avoids conflicts in module names or incorrect imports due to the module search path not being what the author expected. Makes it easier to find modules.

#### 2.3.2 Cons

Makes it harder to deploy code because you have to replicate the package hierarchy. Not really a problem with modern deployment mechanisms.

#### 2.3.3 Decision

All new code should import each module by its full package name.

Imports should be as follows:

```python
Yes:
  # Reference absl.flags in code with the complete name (verbose).
  import absl.flags
  from doctor.who import jodie

  _FOO = absl.flags.DEFINE_string(...)
```

```python
No:
  # Bad namespacing.  Don't do this.
  from absl import flags
  from doctor.who import jodie

  _FOO = flags.DEFINE_string(...)
```

### Import Formatting (3.13)

Imports should be on separate lines.

```python
Yes:
  import os
  import sys
```

```python
No:
  import os, sys
```

Imports are always put at the top of the file, just after any module comments and docstrings, and before module globals and constants.

Imports should be grouped in the following order:

1. Standard library imports
2. Related third party imports  
3. Local application/library specific imports

You should put a blank line between each group of imports.

```python
import collections
import queue
import sys

from absl import app
from absl import flags
import bs4
import cryptography
import tensorflow as tf

from myproject.backends import huxley
from myproject.backends.huxley import powerplant
from myproject import io
from myproject.matchers import *
from myproject.regression import linear
from myproject.regression import other
from myproject import app
from myproject import auth
from myproject import message
from myproject import utils
```

### Type Annotation Imports (3.19.12)

For symbols (including types, functions, and constants) from the `typing` or `collections.abc` modules used to support static analysis and type checking, always import the symbol itself. This keeps common annotations more concise and matches typing practices used around the world. You are explicitly allowed to import multiple specific symbols on one line from the `typing` and `collections.abc` modules.

```python
from collections.abc import Mapping, Sequence
from typing import Any, Generic, cast, TYPE_CHECKING
```

Given that this way of importing adds items to the local namespace, names in `typing` or `collections.abc` should be treated similarly to keywords, and not be defined in your Python code, typed or not. If there is a collision between a type and an existing name in a module, import it using `import x as y`.

```python
from typing import Any as AnyType
```

When annotating function signatures, prefer abstract container types like `collections.abc.Sequence` over concrete types like `list`. If you need to use a concrete type (for example, a `tuple` of typed elements), prefer built-in types like `tuple` over the parametric type aliases from the `typing` module (e.g., `typing.Tuple`).

```python
from typing import List, Tuple

def transform_coordinates(original: List[Tuple[float, float]]) ->
    List[Tuple[float, float]]:
  ...
```

```python
from collections.abc import Sequence

def transform_coordinates(original: Sequence[tuple[float, float]]) ->
    Sequence[tuple[float, float]]:
  ...
```

### Conditional Imports (3.19.13)

Use conditional imports only in exceptional cases where the additional imports needed for type checking must be avoided at runtime. This pattern is discouraged; alternatives such as refactoring the code to allow top-level imports should be preferred.

Imports that are needed only for type annotations can be placed within an `if TYPE_CHECKING:` block.

* Conditionally imported types need to be referenced as strings, to be forward compatible with Python 3.6 where the annotation expressions are actually evaluated.
* Only entities that are used solely for typing should be defined here; this includes aliases. Otherwise it will be a runtime error, as the module will not be imported at runtime.
* The block should be right after all the normal imports.
* There should be no empty lines in the typing imports list.
* Sort this list as if it were a regular imports list.

```python
import typing
if typing.TYPE_CHECKING:
  import sketch
def f(x: "sketch.Sketch"): ...
```

### Circular Dependencies (3.19.14)

Circular dependencies that are caused by typing are code smells. Such code is a good candidate for refactoring. Although technically it is possible to keep circular dependencies, various build systems will not let you do so because each module has to depend on the other.

Replace modules that create circular dependency imports with `Any`. Set an alias with a meaningful name, and use the real type name from this module (any attribute of `Any` is `Any`). Alias definitions should be separated from the last import by one line.

```python
from typing import Any

some_mod = Any  # some_mod.py imports this module.
...

def my_method(self, var: "some_mod.SomeType") -> None:
  ...
```

