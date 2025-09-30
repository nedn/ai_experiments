#!/usr/bin/env python3
"""
Unit tests for git_grep_parser.py

This module provides comprehensive unit tests for all functions in git_grep_parser.py,
including individual parsing functions and the main parse_git_grep_output function.
"""

import unittest
import json
import tempfile
import os
import sys
from unittest.mock import patch, mock_open

# Add the current directory to the path so we can import git_grep_parser
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from git_grep_parser import (
    is_separator_line,
    parse_context_line,
    parse_matched_line,
    is_context_line,
    LineType,
    parse_git_grep_line,
    parse_git_grep_output,
    setup_logging
)
from code_snippet import CodeSnippet


class TestGitGrepParser(unittest.TestCase):
    """Test cases for git_grep_parser module."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Sample git grep output data based on real RISE repository data
        self.sample_git_grep_output = """extlib/libpng/png.c-638-#if defined(_WIN32_WCE)
extlib/libpng/png.c-639-   {
extlib/libpng/png.c-640-      wchar_t time_buf[29];
extlib/libpng/png.c:641:      wsprintf(time_buf, TEXT("%d %S %d %02d:%02d:%02d +0000"),
extlib/libpng/png.c-642-          ptime->day % 32, short_months[(ptime->month - 1) % 12],
extlib/libpng/png.c-643-        ptime->year, ptime->hour % 24, ptime->minute % 60,
extlib/libpng/png.c-644-          ptime->second % 61);
--
extlib/libpng/png.c-649-#ifdef USE_FAR_KEYWORD
extlib/libpng/png.c-650-   {
extlib/libpng/png.c-651-      char near_time_buf[29];
extlib/libpng/png.c:652:      sprintf(near_time_buf, "%d %s %d %02d:%02d:%02d +0000",
extlib/libpng/png.c-653-          ptime->day % 32, short_months[(ptime->month - 1) % 12],
extlib/libpng/png.c-654-          ptime->year, ptime->hour % 24, ptime->minute % 60,
extlib/libpng/png.c-655-          ptime->second % 61);
--
extlib/libpng/pnggccrd.c-5097-   png_debug(1, "in png_read_filter_row (pnggccrd.c)\\n");
extlib/libpng/pnggccrd.c-5098-   switch (filter)
extlib/libpng/pnggccrd.c-5099-   {
extlib/libpng/pnggccrd.c:5100:      case 0: sprintf(filnm, "none");
extlib/libpng/pnggccrd.c:5102:      case 1: sprintf(filnm, "sub-%s",
extlib/libpng/pnggccrd.c-5103-#if defined(PNG_ASSEMBLER_CODE_SUPPORTED) && defined(PNG_THREAD_UNSAFE_OK)
extlib/libpng/pnggccrd.c-5104-#if !defined(PNG_1_0_X)
extlib/libpng/pnggccrd.c-5105-        (png_ptr->asm_flags & PNG_ASM_FLAG_MMX_READ_FILTER_SUB)? "MMX" : 
--
extlib/libpng/pnggccrd.c-5107-#endif
extlib/libpng/pnggccrd.c-5108-"x86");
extlib/libpng/pnggccrd.c-5109-         break;
extlib/libpng/pnggccrd.c:5110:      case 2: sprintf(filnm, "up-%s",
extlib/libpng/pnggccrd.c-5111-#ifdef PNG_ASSEMBLER_CODE_SUPPORTED
extlib/libpng/pnggccrd.c-5112-#if !defined(PNG_1_0_X)
extlib/libpng/pnggccrd.c-5113-        (png_ptr->asm_flags & PNG_ASM_FLAG_MMX_READ_FILTER_UP)? "MMX" :
--
extlib/libpng/pnggccrd.c-5115-#endif
extlib/libpng/pnggccrd.c-5116- "x86");
extlib/libpng/pnggccrd.c-5117-         break;
extlib/libpng/pnggccrd.c:5118:      case 3: sprintf(filnm, "avg-%s",
extlib/libpng/pnggccrd.c-5119-#if defined(PNG_ASSEMBLER_CODE_SUPPORTED) && defined(PNG_THREAD_UNSAFE_OK)
extlib/libpng/pnggccrd.c-5120-#if !defined(PNG_1_0_X)
extlib/libpng/pnggccrd.c-5121-        (png_ptr->asm_flags & PNG_ASM_FLAG_MMX_READ_FILTER_AVG)? "MMX" :
--
"""

    def test_is_separator_line(self):
        """Test is_separator_line function."""
        # Test valid separator lines
        self.assertTrue(is_separator_line("--"))
        self.assertTrue(is_separator_line("  --  "))
        self.assertTrue(is_separator_line("\t--\t"))
        
        # Test invalid separator lines
        self.assertFalse(is_separator_line("---"))
        self.assertFalse(is_separator_line(""))
        self.assertFalse(is_separator_line("some text"))
        self.assertFalse(is_separator_line("filename:123:content"))

    def test_parse_context_line(self):
        """Test parse_context_line function."""
        # Test valid context lines
        is_context, filename, line_num, content = parse_context_line("file.c-123-  some code")
        self.assertTrue(is_context)
        self.assertEqual(filename, "file.c")
        self.assertEqual(line_num, 123)
        self.assertEqual(content, "  some code")
        
        # Test with complex filename
        is_context, filename, line_num, content = parse_context_line("extlib/libpng/png.c-641-      wsprintf(time_buf, TEXT(\"%d %S %d %02d:%02d:%02d +0000\"),")
        self.assertTrue(is_context)
        self.assertEqual(filename, "extlib/libpng/png.c")
        self.assertEqual(line_num, 641)
        self.assertEqual(content, "      wsprintf(time_buf, TEXT(\"%d %S %d %02d:%02d:%02d +0000\"),")
        
        # Test with empty content
        is_context, filename, line_num, content = parse_context_line("file.c-456-")
        self.assertTrue(is_context)
        self.assertEqual(filename, "file.c")
        self.assertEqual(line_num, 456)
        self.assertEqual(content, "")
        
        # Test invalid context lines
        is_context, filename, line_num, content = parse_context_line("file.c:123:content")
        self.assertFalse(is_context)
        self.assertIsNone(filename)
        self.assertIsNone(line_num)
        self.assertIsNone(content)
        
        is_context, filename, line_num, content = parse_context_line("not-a-context-line")
        self.assertFalse(is_context)
        self.assertIsNone(filename)
        self.assertIsNone(line_num)
        self.assertIsNone(content)

    def test_parse_matched_line(self):
        """Test parse_matched_line function."""
        # Test valid matched lines
        is_matched, filename, line_num, content = parse_matched_line("file.c:123:some code")
        self.assertTrue(is_matched)
        self.assertEqual(filename, "file.c")
        self.assertEqual(line_num, 123)
        self.assertEqual(content, "some code")
        
        # Test with complex filename
        is_matched, filename, line_num, content = parse_matched_line("extlib/libpng/png.c:641:      wsprintf(time_buf, TEXT(\"%d %S %d %02d:%02d:%02d +0000\"),")
        self.assertTrue(is_matched)
        self.assertEqual(filename, "extlib/libpng/png.c")
        self.assertEqual(line_num, 641)
        self.assertEqual(content, "      wsprintf(time_buf, TEXT(\"%d %S %d %02d:%02d:%02d +0000\"),")
        
        # Test with empty content
        is_matched, filename, line_num, content = parse_matched_line("file.c:456:")
        self.assertTrue(is_matched)
        self.assertEqual(filename, "file.c")
        self.assertEqual(line_num, 456)
        self.assertEqual(content, "")
        
        # Test invalid matched lines
        is_matched, filename, line_num, content = parse_matched_line("file.c-123-content")
        self.assertFalse(is_matched)
        self.assertIsNone(filename)
        self.assertIsNone(line_num)
        self.assertIsNone(content)
        
        is_matched, filename, line_num, content = parse_matched_line("not-a-matched-line")
        self.assertFalse(is_matched)
        self.assertIsNone(filename)
        self.assertIsNone(line_num)
        self.assertIsNone(content)

    def test_is_context_line(self):
        """Test is_context_line function."""
        # Test valid context lines
        self.assertTrue(is_context_line("file.c-123-content"))
        self.assertTrue(is_context_line("extlib/libpng/png.c-641-      wsprintf"))
        self.assertTrue(is_context_line("file.c-456-"))
        
        # Test invalid context lines
        self.assertFalse(is_context_line("file.c:123:content"))
        self.assertFalse(is_context_line("--"))
        self.assertFalse(is_context_line("not-a-context-line"))
        self.assertFalse(is_context_line(""))

    def test_parse_git_grep_line(self):
        """Test parse_git_grep_line function."""
        # Test separator line
        line_type, filename, line_num, content = parse_git_grep_line("--")
        self.assertEqual(line_type, LineType.SEPARATOR)
        self.assertIsNone(filename)
        self.assertIsNone(line_num)
        self.assertIsNone(content)
        
        # Test context line
        line_type, filename, line_num, content = parse_git_grep_line("file.c-123-  some code")
        self.assertEqual(line_type, LineType.CONTEXT)
        self.assertEqual(filename, "file.c")
        self.assertEqual(line_num, 123)
        self.assertEqual(content, "  some code")
        
        # Test matched line
        line_type, filename, line_num, content = parse_git_grep_line("file.c:123:some code")
        self.assertEqual(line_type, LineType.MATCHED)
        self.assertEqual(filename, "file.c")
        self.assertEqual(line_num, 123)
        self.assertEqual(content, "some code")
        
        # Test invalid line
        with self.assertRaises(ValueError):
            parse_git_grep_line("invalid line format")

    def test_parse_git_grep_output_empty(self):
        """Test parse_git_grep_output with empty input."""
        result = parse_git_grep_output("")
        self.assertEqual(result, [])
        
        # Test with whitespace-only lines (these should be skipped)
        result = parse_git_grep_output("   \n  \t  \n  ")
        self.assertEqual(result, [])

    def test_parse_git_grep_output_single_snippet(self):
        """Test parse_git_grep_output with a single snippet."""
        input_data = """file.c-1-  // comment
file.c:2:  printf("hello");
file.c-3-  return 0;
"""
        result = parse_git_grep_output(input_data)
        
        self.assertEqual(len(result), 1)
        snippet = result[0]
        self.assertEqual(snippet.file_path, 'file.c')
        self.assertEqual(list(snippet.matched_lines), [2])
        self.assertEqual(list(snippet.context_lines), [1, 3])
        self.assertEqual(len(snippet.raw_surrounding_git_grep_lines), 3)
        self.assertEqual(len(snippet.raw_content), 3)
        self.assertEqual(snippet.raw_content[1], '  printf("hello");')

    def test_parse_git_grep_output_multiple_snippets(self):
        """Test parse_git_grep_output with multiple snippets."""
        input_data = """file1.c-1-  // comment
file1.c:2:  printf("hello");
file1.c-3-  return 0;
--
file2.c-10-  // another comment
file2.c:11:  sprintf(buffer, "world");
file2.c-12-  return 1;
"""
        result = parse_git_grep_output(input_data)
        
        self.assertEqual(len(result), 2)
        
        # First snippet
        snippet1 = result[0]
        self.assertEqual(snippet1.file_path, 'file1.c')
        self.assertEqual(list(snippet1.matched_lines), [2])
        self.assertEqual(list(snippet1.context_lines), [1, 3])
        
        # Second snippet
        snippet2 = result[1]
        self.assertEqual(snippet2.file_path, 'file2.c')
        self.assertEqual(list(snippet2.matched_lines), [11])
        self.assertEqual(list(snippet2.context_lines), [10, 12])

    def test_parse_git_grep_output_multiple_matches_in_snippet(self):
        """Test parse_git_grep_output with multiple matches in one snippet."""
        input_data = """file.c-1-  // comment
file.c:2:  printf("hello");
file.c:3:  sprintf(buffer, "world");
file.c-4-  return 0;
"""
        result = parse_git_grep_output(input_data)
        
        self.assertEqual(len(result), 1)
        snippet = result[0]
        self.assertEqual(snippet.file_path, 'file.c')
        self.assertEqual(list(snippet.matched_lines), [2, 3])
        self.assertEqual(list(snippet.context_lines), [1, 4])

    def test_parse_git_grep_output_real_data(self):
        """Test parse_git_grep_output with real RISE repository data."""
        result = parse_git_grep_output(self.sample_git_grep_output)
        
        # Should have 5 snippets based on the sample data (counted manually)
        self.assertEqual(len(result), 5)
        
        # First snippet - png.c with wsprintf
        snippet1 = result[0]
        self.assertEqual(snippet1.file_path, 'extlib/libpng/png.c')
        self.assertEqual(list(snippet1.matched_lines), [641])
        self.assertEqual(list(snippet1.context_lines), [638, 639, 640, 642, 643, 644])
        self.assertIn('wsprintf', snippet1.raw_content[3])
        
        # Second snippet - png.c with sprintf
        snippet2 = result[1]
        self.assertEqual(snippet2.file_path, 'extlib/libpng/png.c')
        self.assertEqual(list(snippet2.matched_lines), [652])
        self.assertEqual(list(snippet2.context_lines), [649, 650, 651, 653, 654, 655])
        self.assertIn('sprintf', snippet2.raw_content[3])
        
        # Third snippet - pnggccrd.c with multiple sprintf calls
        snippet3 = result[2]
        self.assertEqual(snippet3.file_path, 'extlib/libpng/pnggccrd.c')
        self.assertEqual(list(snippet3.matched_lines), [5100, 5102])
        self.assertEqual(list(snippet3.context_lines), [5097, 5098, 5099, 5103, 5104, 5105])
        
        # Fourth snippet - pnggccrd.c with single sprintf call
        snippet4 = result[3]
        self.assertEqual(snippet4.file_path, 'extlib/libpng/pnggccrd.c')
        self.assertEqual(list(snippet4.matched_lines), [5110])
        self.assertEqual(list(snippet4.context_lines), [5107, 5108, 5109, 5111, 5112, 5113])

    def test_parse_git_grep_output_context_only_snippet(self):
        """Test parse_git_grep_output with snippet containing only context lines."""
        input_data = """file.c-1-  // comment
file.c-2-  // another comment
--
"""
        result = parse_git_grep_output(input_data)
        
        self.assertEqual(len(result), 1)
        snippet = result[0]
        self.assertEqual(snippet.file_path, 'file.c')
        self.assertEqual(list(snippet.matched_lines), [])
        self.assertEqual(list(snippet.context_lines), [1, 2])

    def test_parse_git_grep_output_trailing_separator(self):
        """Test parse_git_grep_output with trailing separator."""
        input_data = """file.c-1-  // comment
file.c:2:  printf("hello");
file.c-3-  return 0;
--
"""
        result = parse_git_grep_output(input_data)
        
        self.assertEqual(len(result), 1)  # Trailing separator should not create empty snippet

    def test_parse_git_grep_output_leading_separator(self):
        """Test parse_git_grep_output with leading separator."""
        input_data = """--
file.c-1-  // comment
file.c:2:  printf("hello");
file.c-3-  return 0;
"""
        result = parse_git_grep_output(input_data)
        
        self.assertEqual(len(result), 1)  # Leading separator should not create empty snippet

    def test_parse_git_grep_output_consecutive_separators(self):
        """Test parse_git_grep_output with consecutive separators."""
        input_data = """file.c-1-  // comment
file.c:2:  printf("hello");
file.c-3-  return 0;
--
--
file.c-10-  // another comment
file.c:11:  sprintf(buffer, "world");
file.c-12-  return 1;
"""
        result = parse_git_grep_output(input_data)
        
        self.assertEqual(len(result), 2)  # Consecutive separators should not create empty snippets

    def test_setup_logging(self):
        """Test setup_logging function."""
        # Test with debug=False (default)
        setup_logging(debug=False)
        # This test mainly ensures the function doesn't raise an exception
        
        # Test with debug=True
        setup_logging(debug=True)
        # This test mainly ensures the function doesn't raise an exception

    def test_edge_cases(self):
        """Test various edge cases."""
        # Test with very long line numbers
        is_context, filename, line_num, content = parse_context_line("file.c-999999-  content")
        self.assertTrue(is_context)
        self.assertEqual(line_num, 999999)
        
        # Test with content containing special characters
        is_context, filename, line_num, content = parse_context_line("file.c-123-  printf(\"hello\\n\");")
        self.assertTrue(is_context)
        self.assertEqual(content, "  printf(\"hello\\n\");")

    def test_error_handling(self):
        """Test error handling in parse_git_grep_line."""
        # Test with malformed context line (missing dash after line number)
        with self.assertRaises(ValueError):
            parse_git_grep_line("file.c-123 content")
        
        # Test with malformed matched line (missing colon after line number)
        with self.assertRaises(ValueError):
            parse_git_grep_line("file.c:123 content")
        
        # Test with completely invalid line
        with self.assertRaises(ValueError):
            parse_git_grep_line("completely invalid line")

    def test_unicode_handling(self):
        """Test handling of unicode characters in content."""
        unicode_content = "printf(\"Hello 世界\");"
        is_matched, filename, line_num, content = parse_matched_line(f"file.c:123:{unicode_content}")
        self.assertTrue(is_matched)
        self.assertEqual(content, unicode_content)
        
        # Test with unicode in context line
        is_context, filename, line_num, content = parse_context_line(f"file.c-123-  {unicode_content}")
        self.assertTrue(is_context)
        self.assertEqual(content, f"  {unicode_content}")

    def test_whitespace_handling(self):
        """Test handling of various whitespace scenarios."""
        # Test with leading/trailing whitespace in separator
        self.assertTrue(is_separator_line("  --  "))
        self.assertTrue(is_separator_line("\t--\t"))
        
        # Test with whitespace in content
        is_context, filename, line_num, content = parse_context_line("file.c-123-  \t  content  \t  ")
        self.assertTrue(is_context)
        self.assertEqual(content, "  \t  content  \t  ")
        
        # Test with empty content
        is_context, filename, line_num, content = parse_context_line("file.c-123-")
        self.assertTrue(is_context)
        self.assertEqual(content, "")


class TestGitGrepParserIntegration(unittest.TestCase):
    """Integration tests for git_grep_parser module."""

    def test_main_function_with_stdin(self):
        """Test main function when reading from stdin."""
        test_input = """file.c-1-  // comment
file.c:2:  printf("hello");
file.c-3-  return 0;
"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # Create a mock stdin object
            mock_stdin = type('MockStdin', (), {'read': lambda self: test_input})()
            
            with patch('sys.stdin', mock_stdin):
                with patch('sys.argv', ['git_grep_parser.py', '--output', tmp_path]):
                    from git_grep_parser import main
                    main()
            
            # Verify output file was created and contains expected data
            self.assertTrue(os.path.exists(tmp_path))
            with open(tmp_path, 'r') as f:
                result = json.load(f)
            
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['file_path'], 'file.c')
            self.assertEqual(result[0]['matched_lines'], [2])
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_main_function_with_input_file(self):
        """Test main function when reading from input file."""
        test_input = """file.c-1-  // comment
file.c:2:  printf("hello");
file.c-3-  return 0;
"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as input_file:
            input_file.write(test_input)
            input_path = input_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as output_file:
            output_path = output_file.name
        
        try:
            with patch('sys.argv', ['git_grep_parser.py', '--input', input_path, '--output', output_path]):
                from git_grep_parser import main
                main()
            
            # Verify output file was created and contains expected data
            self.assertTrue(os.path.exists(output_path))
            with open(output_path, 'r') as f:
                result = json.load(f)
            
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['file_path'], 'file.c')
            self.assertEqual(result[0]['matched_lines'], [2])
            
        finally:
            for path in [input_path, output_path]:
                if os.path.exists(path):
                    os.unlink(path)


class TestCodeSnippetImmutability(unittest.TestCase):
    """Test cases for CodeSnippet immutability functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sample_snippet = CodeSnippet(
            file_path="test.py",
            matched_lines=[10, 15],
            context_lines=[8, 9, 11, 12, 13, 14, 16, 17],
            raw_surrounding_git_grep_lines=[
                "test.py-8-  def helper():",
                "test.py-9-      pass",
                "test.py:10:  print('hello')",
                "test.py-11-  return True",
                "test.py-12-",
                "test.py-13-def main():",
                "test.py-14-  x = 1",
                "test.py:15:  print('world')",
                "test.py-16-  return x",
                "test.py-17-"
            ],
            raw_content=[
                "  def helper():",
                "      pass",
                "  print('hello')",
                "  return True",
                "",
                "def main():",
                "  x = 1",
                "  print('world')",
                "  return x",
                ""
            ]
        )
    
    def test_initial_state_is_mutable(self):
        """Test that CodeSnippet starts in mutable state."""
        self.assertFalse(self.sample_snippet.is_frozen())
        self.assertIsInstance(self.sample_snippet.matched_lines, list)
        self.assertIsInstance(self.sample_snippet.context_lines, list)
        self.assertIsInstance(self.sample_snippet.raw_surrounding_git_grep_lines, list)
        self.assertIsInstance(self.sample_snippet.raw_content, list)
    
    def test_freeze_makes_immutable(self):
        """Test that freeze() makes the object immutable."""
        # Initially mutable
        self.assertFalse(self.sample_snippet.is_frozen())
        
        # Freeze the object
        self.sample_snippet.freeze()
        
        # Should now be frozen
        self.assertTrue(self.sample_snippet.is_frozen())
        
        # Fields should be converted to tuples
        self.assertIsInstance(self.sample_snippet.matched_lines, tuple)
        self.assertIsInstance(self.sample_snippet.context_lines, tuple)
        self.assertIsInstance(self.sample_snippet.raw_surrounding_git_grep_lines, tuple)
        self.assertIsInstance(self.sample_snippet.raw_content, tuple)
    
    def test_freeze_idempotent(self):
        """Test that calling freeze() multiple times is safe."""
        # First freeze
        self.sample_snippet.freeze()
        self.assertTrue(self.sample_snippet.is_frozen())
        
        # Second freeze should not cause issues
        self.sample_snippet.freeze()
        self.assertTrue(self.sample_snippet.is_frozen())
    
    def test_cannot_modify_frozen_object_direct_assignment(self):
        """Test that direct field assignment fails on frozen object."""
        self.sample_snippet.freeze()
        
        with self.assertRaises(ValueError) as context:
            self.sample_snippet.file_path = "new_file.py"
        
        self.assertIn("Cannot modify frozen CodeSnippet object", str(context.exception))
        self.assertIn("file_path", str(context.exception))
    
    def test_cannot_modify_frozen_object_list_operations(self):
        """Test that list operations fail on frozen object."""
        self.sample_snippet.freeze()
        
        # Test that we can't modify the lists (now tuples)
        with self.assertRaises(AttributeError):
            self.sample_snippet.matched_lines.append(20)
        
        with self.assertRaises(AttributeError):
            self.sample_snippet.context_lines.append(21)
        
        with self.assertRaises(AttributeError):
            self.sample_snippet.raw_content.append("new line")
    
    def test_freeze_preserves_data_integrity(self):
        """Test that freeze() preserves all data correctly."""
        original_data = {
            'file_path': self.sample_snippet.file_path,
            'matched_lines': list(self.sample_snippet.matched_lines),
            'context_lines': list(self.sample_snippet.context_lines),
            'raw_surrounding_git_grep_lines': list(self.sample_snippet.raw_surrounding_git_grep_lines),
            'raw_content': list(self.sample_snippet.raw_content)
        }
        
        self.sample_snippet.freeze()
        
        # Data should be preserved
        self.assertEqual(self.sample_snippet.file_path, original_data['file_path'])
        self.assertEqual(list(self.sample_snippet.matched_lines), original_data['matched_lines'])
        self.assertEqual(list(self.sample_snippet.context_lines), original_data['context_lines'])
        self.assertEqual(list(self.sample_snippet.raw_surrounding_git_grep_lines), original_data['raw_surrounding_git_grep_lines'])
        self.assertEqual(list(self.sample_snippet.raw_content), original_data['raw_content'])
    
    def test_methods_work_after_freeze(self):
        """Test that all methods work correctly after freezing."""
        self.sample_snippet.freeze()
        
        # Test that methods still work
        self.assertEqual(self.sample_snippet.get_total_lines(), 10)
        self.assertEqual(self.sample_snippet.get_matched_line_count(), 2)
        self.assertEqual(self.sample_snippet.get_context_line_count(), 8)
        
        # Test content methods
        content = self.sample_snippet.get_full_content()
        self.assertIn("print('hello')", content)
        self.assertIn("print('world')", content)
        
        git_output = self.sample_snippet.get_git_grep_output()
        self.assertIn("test.py:10:", git_output)
        self.assertIn("test.py:15:", git_output)
    
    def test_json_serialization_after_freeze(self):
        """Test that JSON serialization works after freezing."""
        self.sample_snippet.freeze()
        
        # Should be able to convert to dict and JSON
        snippet_dict = self.sample_snippet.to_dict()
        self.assertIsInstance(snippet_dict, dict)
        
        json_str = self.sample_snippet.to_json()
        self.assertIsInstance(json_str, str)
        
        # Should be able to recreate from dict
        recreated = CodeSnippet.from_dict(snippet_dict)
        self.assertEqual(recreated.file_path, self.sample_snippet.file_path)
        self.assertEqual(list(recreated.matched_lines), list(self.sample_snippet.matched_lines))
    
    def test_parser_creates_frozen_snippets(self):
        """Test that the parser creates frozen snippets."""
        sample_output = """file.c-1-  int x = 1;
file.c:2:  printf("hello");
file.c-3-  return x;
--
file.c-5-  int y = 2;
file.c:6:  printf("world");
file.c-7-  return y;
"""
        
        snippets = parse_git_grep_output(sample_output)
        
        # All snippets should be frozen
        for snippet in snippets:
            self.assertTrue(snippet.is_frozen(), f"Snippet {snippet.file_path} is not frozen")
            self.assertIsInstance(snippet.matched_lines, tuple)
            self.assertIsInstance(snippet.context_lines, tuple)
            self.assertIsInstance(snippet.raw_surrounding_git_grep_lines, tuple)
            self.assertIsInstance(snippet.raw_content, tuple)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
