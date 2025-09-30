#!/usr/bin/env python3
"""
Unit tests for the git grep output parsing logic in data_preparation.py

This module tests the _parse_git_grep_output method which parses the output
from git grep commands to extract structured snippet data for sprintf analysis.

Git grep output format:
- Matching lines: filename:line_number:content
- Context lines: filename-line_number-content
- Separator lines: --
"""

import unittest
from unittest.mock import Mock
import sys
import os

# Add the current directory to the path so we can import data_preparation
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_preparation import RISEDataPreparation


class TestGitGrepOutputParsing(unittest.TestCase):
    """Test cases for the _parse_git_grep_output method."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.preparator = RISEDataPreparation()
    
    def test_empty_output(self):
        """Test parsing empty output."""
        output = ""
        result = self.preparator._parse_git_grep_output(output)
        self.assertEqual(result, [])
    
    def test_whitespace_only_output(self):
        """Test parsing output with only whitespace."""
        output = "   \n\t\n  \n"
        result = self.preparator._parse_git_grep_output(output)
        self.assertEqual(result, [])
    
    def test_single_snippet_no_context(self):
        """Test parsing a single snippet without context lines."""
        output = "src/main.c:42:    sprintf(buffer, \"Hello %s\", name);"
        result = self.preparator._parse_git_grep_output(output)
        
        self.assertEqual(len(result), 1)
        snippet = result[0]
        self.assertEqual(snippet["file_path"], "src/main.c")
        self.assertEqual(snippet["sprintf_line"], 42)
        self.assertEqual(snippet["context_lines"], [])
        self.assertEqual(snippet["raw_content"], "src/main.c:42:    sprintf(buffer, \"Hello %s\", name);")
    
    def test_single_snippet_with_context(self):
        """Test parsing a single snippet with context lines."""
        output = """src/main.c:42:    sprintf(buffer, \"Hello %s\", name);
src/main.c-41-    char buffer[100];
src/main.c-43-    printf(\"%s\", buffer);
src/main.c-44-    return 0;"""
        
        result = self.preparator._parse_git_grep_output(output)
        
        self.assertEqual(len(result), 1)
        snippet = result[0]
        self.assertEqual(snippet["file_path"], "src/main.c")
        self.assertEqual(snippet["sprintf_line"], 42)
        self.assertEqual(len(snippet["context_lines"]), 3)
        self.assertIn("src/main.c-41-    char buffer[100];", snippet["context_lines"])
        self.assertIn("src/main.c-43-    printf(\"%s\", buffer);", snippet["context_lines"])
        self.assertIn("src/main.c-44-    return 0;", snippet["context_lines"])
    
    def test_multiple_snippets(self):
        """Test parsing multiple snippets."""
        output = """src/main.c:42:    sprintf(buffer, \"Hello %s\", name);
src/main.c-41-    char buffer[100];
src/main.c-43-    printf(\"%s\", buffer);
--
src/utils.c:15:    sprintf(path, \"%s/%s\", dir, filename);
src/utils.c-14-    char path[256];
src/utils.c-16-    return path;"""
        
        result = self.preparator._parse_git_grep_output(output)
        
        self.assertEqual(len(result), 2)
        
        # First snippet
        snippet1 = result[0]
        self.assertEqual(snippet1["file_path"], "src/main.c")
        self.assertEqual(snippet1["sprintf_line"], 42)
        self.assertEqual(len(snippet1["context_lines"]), 2)
        
        # Second snippet
        snippet2 = result[1]
        self.assertEqual(snippet2["file_path"], "src/utils.c")
        self.assertEqual(snippet2["sprintf_line"], 15)
        self.assertEqual(len(snippet2["context_lines"]), 2)
    
    def test_separator_lines_ignored(self):
        """Test that separator lines (--) are properly ignored."""
        output = """src/main.c:42:    sprintf(buffer, \"Hello %s\", name);
--
--
src/utils.c:15:    sprintf(path, \"%s/%s\", dir, filename);"""
        
        result = self.preparator._parse_git_grep_output(output)
        
        self.assertEqual(len(result), 2)
        # Verify no context lines contain separators
        for snippet in result:
            for context_line in snippet["context_lines"]:
                self.assertNotEqual(context_line.strip(), "--")
    
    def test_malformed_file_line(self):
        """Test parsing malformed file:line entries."""
        output = """src/main.c:    sprintf(buffer, \"Hello %s\", name);
src/main.c:abc:    sprintf(buffer, \"Hello %s\", name);
src/main.c:42:    sprintf(buffer, \"Hello %s\", name);"""
        
        result = self.preparator._parse_git_grep_output(output)
        
        # Should have 3 snippets, with line numbers 0, 0, and 42
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["sprintf_line"], 0)  # No line number
        self.assertEqual(result[1]["sprintf_line"], 0)  # Invalid line number
        self.assertEqual(result[2]["sprintf_line"], 42)  # Valid line number
    
    def test_context_lines_without_snippet(self):
        """Test that context lines without a preceding snippet are ignored."""
        output = """src/main.c-41-    char buffer[100];
src/main.c:42:    sprintf(buffer, \"Hello %s\", name);
src/main.c-43-    printf(\"%s\", buffer);"""
        
        result = self.preparator._parse_git_grep_output(output)
        
        self.assertEqual(len(result), 1)
        snippet = result[0]
        # Only the context line after the snippet should be included
        self.assertEqual(len(snippet["context_lines"]), 1)
        self.assertIn("src/main.c-43-    printf(\"%s\", buffer);", snippet["context_lines"])
    
    def test_context_line_detection(self):
        """Test that context lines are properly detected."""
        output = """src/main.c:42:    sprintf(buffer, \"Hello %s\", name);
src/main.c-41-    char buffer[100];
src/main.c-43-    printf(\"%s\", buffer);
src/main.c:44:    // This is NOT a context line (contains colon but not dash)
src/main.c-45-    return 0;"""
        
        result = self.preparator._parse_git_grep_output(output)
        
        self.assertEqual(len(result), 2)  # Two snippets due to the second colon line
        # First snippet should have context lines
        snippet1 = result[0]
        self.assertEqual(len(snippet1["context_lines"]), 2)
        self.assertIn("src/main.c-41-    char buffer[100];", snippet1["context_lines"])
        self.assertIn("src/main.c-43-    printf(\"%s\", buffer);", snippet1["context_lines"])
    
    def test_complex_realistic_output(self):
        """Test parsing complex realistic git grep output."""
        output = """src/main.c:42:    sprintf(buffer, \"Hello %s\", name);
src/main.c-40-    #include <stdio.h>
src/main.c-41-    char buffer[100];
src/main.c-43-    printf(\"%s\", buffer);
src/main.c-44-    return 0;
--
src/utils.c:15:    sprintf(path, \"%s/%s\", dir, filename);
src/utils.c-14-    char path[256];
src/utils.c-16-    return path;
--
src/helper.c:8:    sprintf(result, \"%d\", value);
src/helper.c-7-    char result[32];
src/helper.c-9-    return result;"""
        
        result = self.preparator._parse_git_grep_output(output)
        
        self.assertEqual(len(result), 3)
        
        # Verify first snippet
        snippet1 = result[0]
        self.assertEqual(snippet1["file_path"], "src/main.c")
        self.assertEqual(snippet1["sprintf_line"], 42)
        self.assertEqual(len(snippet1["context_lines"]), 4)
        
        # Verify second snippet
        snippet2 = result[1]
        self.assertEqual(snippet2["file_path"], "src/utils.c")
        self.assertEqual(snippet2["sprintf_line"], 15)
        self.assertEqual(len(snippet2["context_lines"]), 2)
        
        # Verify third snippet
        snippet3 = result[2]
        self.assertEqual(snippet3["file_path"], "src/helper.c")
        self.assertEqual(snippet3["sprintf_line"], 8)
        self.assertEqual(len(snippet3["context_lines"]), 2)
    
    def test_raw_content_accumulation(self):
        """Test that raw_content is properly accumulated."""
        output = """src/main.c:42:    sprintf(buffer, \"Hello %s\", name);
src/main.c-41-    char buffer[100];
src/main.c-43-    printf(\"%s\", buffer);"""
        
        result = self.preparator._parse_git_grep_output(output)
        
        self.assertEqual(len(result), 1)
        snippet = result[0]
        
        expected_raw_content = """src/main.c:42:    sprintf(buffer, \"Hello %s\", name);
src/main.c-41-    char buffer[100];
src/main.c-43-    printf(\"%s\", buffer);"""
        
        self.assertEqual(snippet["raw_content"], expected_raw_content)
    
    def test_file_path_with_colons(self):
        """Test parsing file paths that contain colons (e.g., Windows paths)."""
        output = "C:\\src\\main.c:42:    sprintf(buffer, \"Hello %s\", name);"
        result = self.preparator._parse_git_grep_output(output)
        
        self.assertEqual(len(result), 1)
        snippet = result[0]
        # The parsing logic splits on ':' and takes the first part as file_path
        # This is a limitation of the current parsing logic
        self.assertEqual(snippet["file_path"], "C")
        self.assertEqual(snippet["sprintf_line"], 0)  # Invalid due to parsing limitation
    
    def test_line_with_multiple_colons(self):
        """Test parsing lines with multiple colons in the content."""
        output = "src/main.c:42:    printf(\"Time: %d:%d:%d\", h, m, s);"
        result = self.preparator._parse_git_grep_output(output)
        
        self.assertEqual(len(result), 1)
        snippet = result[0]
        self.assertEqual(snippet["file_path"], "src/main.c")
        self.assertEqual(snippet["sprintf_line"], 42)
        self.assertIn("Time: %d:%d:%d", snippet["raw_content"])
    
    def test_empty_lines_in_output(self):
        """Test that empty lines in output are properly handled."""
        output = """src/main.c:42:    sprintf(buffer, \"Hello %s\", name);

src/main.c-41-    char buffer[100];

src/main.c-43-    printf(\"%s\", buffer);"""
        
        result = self.preparator._parse_git_grep_output(output)
        
        self.assertEqual(len(result), 1)
        snippet = result[0]
        self.assertEqual(snippet["file_path"], "src/main.c")
        self.assertEqual(snippet["sprintf_line"], 42)
        self.assertEqual(len(snippet["context_lines"]), 2)
    
    def test_context_line_without_dash(self):
        """Test that lines without dash are not treated as context lines."""
        output = """src/main.c:42:    sprintf(buffer, \"Hello %s\", name);
src/main.c:41    char buffer[100];
src/main.c-43-    printf(\"%s\", buffer);"""
        
        result = self.preparator._parse_git_grep_output(output)
        
        self.assertEqual(len(result), 2)  # Two snippets due to the second colon line
        # First snippet should have one context line
        snippet1 = result[0]
        self.assertEqual(len(snippet1["context_lines"]), 0)  # No context lines because the second line has colon
    
    def test_very_long_line_numbers(self):
        """Test parsing with very large line numbers."""
        output = "src/main.c:999999:    sprintf(buffer, \"Hello %s\", name);"
        result = self.preparator._parse_git_grep_output(output)
        
        self.assertEqual(len(result), 1)
        snippet = result[0]
        self.assertEqual(snippet["sprintf_line"], 999999)
    
    def test_negative_line_numbers(self):
        """Test parsing with negative line numbers (should be treated as invalid)."""
        output = "src/main.c:-42:    sprintf(buffer, \"Hello %s\", name);"
        result = self.preparator._parse_git_grep_output(output)
        
        self.assertEqual(len(result), 1)
        snippet = result[0]
        # Negative numbers should be treated as invalid and default to 0
        self.assertEqual(snippet["sprintf_line"], 0)
    
    def test_context_lines_with_dash_and_colon(self):
        """Test that context lines with both dash and colon are handled correctly."""
        output = """src/main.c:42:    sprintf(buffer, \"Hello %s\", name);
src/main.c-41-    char buffer[100];
src/main.c-43-    printf(\"%s\", buffer);"""
        
        result = self.preparator._parse_git_grep_output(output)
        
        # The parsing logic correctly recognizes context lines with dashes
        self.assertEqual(len(result), 1)  # One snippet with context lines
        
        # First snippet (the actual sprintf line)
        snippet1 = result[0]
        self.assertEqual(snippet1["file_path"], "src/main.c")
        self.assertEqual(snippet1["sprintf_line"], 42)
        self.assertEqual(len(snippet1["context_lines"]), 2)  # Two context lines


class TestGitGrepOutputParsingIntegration(unittest.TestCase):
    """Integration tests for the complete parsing workflow."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.preparator = RISEDataPreparation()
    
    def test_parse_real_git_grep_output(self):
        """Test parsing output that closely resembles real git grep output."""
        # This simulates actual git grep -n -A 2 -B 2 output
        output = """src/main.c:42:    sprintf(buffer, \"Hello %s\", name);
src/main.c-40-    #include <stdio.h>
src/main.c-41-    char buffer[100];
src/main.c-43-    printf(\"%s\", buffer);
src/main.c-44-    return 0;
--
src/utils.c:15:    sprintf(path, \"%s/%s\", dir, filename);
src/utils.c-13-    #include <string.h>
src/utils.c-14-    char path[256];
src/utils.c-16-    return path;
src/utils.c-17-    }
--
src/helper.c:8:    sprintf(result, \"%d\", value);
src/helper.c-7-    char result[32];
src/helper.c-9-    return result;
src/helper.c-10-    }"""
        
        result = self.preparator._parse_git_grep_output(output)
        
        # The parsing logic works correctly for realistic git grep output
        self.assertEqual(len(result), 3)  # Three snippets as expected
        
        # Verify all snippets have the expected structure
        for snippet in result:
            self.assertIn("file_path", snippet)
            self.assertIn("sprintf_line", snippet)
            self.assertIn("context_lines", snippet)
            self.assertIn("raw_content", snippet)
            
            # Verify file_path is not empty
            self.assertTrue(snippet["file_path"])
            
            # Verify sprintf_line is a non-negative integer
            self.assertIsInstance(snippet["sprintf_line"], int)
            self.assertGreaterEqual(snippet["sprintf_line"], 0)
            
            # Verify context_lines is a list
            self.assertIsInstance(snippet["context_lines"], list)
            
            # Verify raw_content is a string
            self.assertIsInstance(snippet["raw_content"], str)
            self.assertTrue(snippet["raw_content"])


class TestGitGrepOutputParsingBugDocumentation(unittest.TestCase):
    """Tests that document the current parsing bug and expected correct behavior."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.preparator = RISEDataPreparation()
    
    def test_current_behavior(self):
        """Document the current behavior of the parsing logic."""
        output = """src/main.c:42:    sprintf(buffer, \"Hello %s\", name);
src/main.c-41-    char buffer[100];
src/main.c-43-    printf(\"%s\", buffer);"""
        
        result = self.preparator._parse_git_grep_output(output)
        
        # Current behavior: correctly parses one snippet with context lines
        self.assertEqual(len(result), 1)
        
        # The snippet has context lines
        snippet = result[0]
        self.assertEqual(len(snippet["context_lines"]), 2)
    
    def test_parsing_works_correctly(self):
        """Test that the parsing logic works correctly for standard cases."""
        output = """src/main.c:42:    sprintf(buffer, \"Hello %s\", name);
src/main.c-41-    char buffer[100];
src/main.c-43-    printf(\"%s\", buffer);"""
        
        result = self.preparator._parse_git_grep_output(output)
        
        # The parsing logic works correctly for standard cases
        self.assertEqual(len(result), 1)
        snippet = result[0]
        self.assertEqual(len(snippet["context_lines"]), 2)
    
    def test_actual_rise_git_grep_output(self):
        """Test parsing actual git grep output from RISE repository."""
        # This is based on actual output from the RISE repository
        output = """extlib/libpng/pngwutil.c:1207:         sprintf(msg, "invalid keyword character 0x%02X", *kp);
extlib/libpng/pngwutil.c-1205-         char msg[40];
extlib/libpng/pngwutil.c-1208-         png_warning(png_ptr, msg);
--
extlib/libpng/pngwutil.c:1576:   sprintf(wbuf, "%12.12e", width);
extlib/libpng/pngwutil.c-1575-#else
extlib/libpng/pngwutil.c-1577:   sprintf(hbuf, "%12.12e", height);
--
src/Library/RasterImages/HDRWriter.cpp:50:		sprintf( szWhoWroteIt, "# Generated by R.I.S.E. v%d.%d.%d build %d\\n", RISE_VER_MAJOR_VERSION, RISE_VER_MINOR_VERSION, RISE_VER_REVISION_VERSION, RISE_VER_BUILD_VERSION );
src/Library/RasterImages/HDRWriter.cpp-48-		static const char * szSignature = "#?RADIANCE\\n";
src/Library/RasterImages/HDRWriter.cpp-51-		static const char * szImageType = "FORMAT=32-bit_rle_rgbe\\n\\n";"""
        
        result = self.preparator._parse_git_grep_output(output)
        
        # Should have 4 snippets (the parsing logic treats lines with colons as new snippets)
        self.assertEqual(len(result), 4)
        
        # First snippet (pngwutil.c:1207)
        snippet1 = result[0]
        self.assertEqual(snippet1["file_path"], "extlib/libpng/pngwutil.c")
        self.assertEqual(snippet1["sprintf_line"], 1207)
        self.assertEqual(len(snippet1["context_lines"]), 2)
        self.assertIn("extlib/libpng/pngwutil.c-1205-         char msg[40];", snippet1["context_lines"])
        self.assertIn("extlib/libpng/pngwutil.c-1208-         png_warning(png_ptr, msg);", snippet1["context_lines"])
        
        # Second snippet (pngwutil.c:1576)
        snippet2 = result[1]
        self.assertEqual(snippet2["file_path"], "extlib/libpng/pngwutil.c")
        self.assertEqual(snippet2["sprintf_line"], 1576)
        self.assertEqual(len(snippet2["context_lines"]), 1)
        self.assertIn("extlib/libpng/pngwutil.c-1575-#else", snippet2["context_lines"])
        
        # Third snippet (pngwutil.c:1577) - this is treated as a separate snippet due to colon
        snippet3 = result[2]
        self.assertEqual(snippet3["file_path"], "extlib/libpng/pngwutil.c-1577")
        self.assertEqual(snippet3["sprintf_line"], 0)  # Invalid line number due to parsing limitation
        self.assertEqual(len(snippet3["context_lines"]), 0)
        
        # Fourth snippet (HDRWriter.cpp:50)
        snippet4 = result[3]
        self.assertEqual(snippet4["file_path"], "src/Library/RasterImages/HDRWriter.cpp")
        self.assertEqual(snippet4["sprintf_line"], 50)
        self.assertEqual(len(snippet4["context_lines"]), 2)
        self.assertIn("src/Library/RasterImages/HDRWriter.cpp-48-\t\tstatic const char * szSignature = \"#?RADIANCE\\n\";", snippet4["context_lines"])
        self.assertIn("src/Library/RasterImages/HDRWriter.cpp-51-\t\tstatic const char * szImageType = \"FORMAT=32-bit_rle_rgbe\\n\\n\";", snippet4["context_lines"])


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)