#!/usr/bin/env python3
"""
Unit tests for CodeSnippet and CodeSnippetList classes

This module provides comprehensive unit tests for CodeSnippet immutability
functionality and CodeSnippetList functionality.
"""

import json
import os
import sys
import unittest

# Add the parent directory to the path so we can import code_snippet
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from code_snippet import CodeSnippet, CodeSnippetList


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
        from git_grep_parser import parse_git_grep_output
        
        sample_output = """file.c-1-  int x = 1;
file.c:2:  printf("hello");
file.c-3-  return x;
--
file.c-5-  int y = 2;
file.c:6:  printf("world");
file.c-7-  return y;
"""
        
        snippets = parse_git_grep_output(sample_output)
        
        # Should return a CodeSnippetList
        self.assertIsInstance(snippets, CodeSnippetList)
        
        # All snippets should be frozen
        for snippet in snippets:
            self.assertTrue(snippet.is_frozen(), f"Snippet {snippet.file_path} is not frozen")
            self.assertIsInstance(snippet.matched_lines, tuple)
            self.assertIsInstance(snippet.context_lines, tuple)
            self.assertIsInstance(snippet.raw_surrounding_git_grep_lines, tuple)
            self.assertIsInstance(snippet.raw_content, tuple)


class TestCodeSnippetList(unittest.TestCase):
    """Test cases for CodeSnippetList functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.snippet1 = CodeSnippet(
            file_path="test1.c",
            matched_lines=[10, 15],
            context_lines=[8, 9, 11, 12, 16, 17],
            raw_surrounding_git_grep_lines=["test1.c-8-  // context", "test1.c-9-  int x = 5;", "test1.c:10:  sprintf(buf, \"%d\", x);", "test1.c-11-  return buf;", "test1.c-12-}"],
            raw_content=["  // context", "  int x = 5;", "  sprintf(buf, \"%d\", x);", "  return buf;", "}"]
        )
        
        self.snippet2 = CodeSnippet(
            file_path="test2.c",
            matched_lines=[20],
            context_lines=[18, 19, 21, 22],
            raw_surrounding_git_grep_lines=["test2.c-18-  char buffer[100];", "test2.c-19-  int value = 42;", "test2.c:20:  sprintf(buffer, \"Value: %d\", value);", "test2.c-21-  printf(\"%s\", buffer);", "test2.c-22-}"],
            raw_content=["  char buffer[100];", "  int value = 42;", "  sprintf(buffer, \"Value: %d\", value);", "  printf(\"%s\", buffer);", "}"]
        )
    
    def test_code_snippet_list_creation(self):
        """Test CodeSnippetList creation and basic functionality."""
        snippet_list = CodeSnippetList([self.snippet1, self.snippet2])
        
        self.assertIsInstance(snippet_list, CodeSnippetList)
        self.assertEqual(len(snippet_list), 2)
        self.assertTrue(snippet_list.is_frozen())
    
    def test_code_snippet_list_automatic_freezing(self):
        """Test that CodeSnippetList automatically freezes all snippets."""
        # Create snippets that are not frozen
        unfrozen_snippet = CodeSnippet(
            file_path="test.c",
            matched_lines=[1],
            context_lines=[2, 3],
            raw_surrounding_git_grep_lines=["test.c-2-  // context", "test.c:1:  printf(\"test\");", "test.c-3-  return;"],
            raw_content=["  // context", "  printf(\"test\");", "  return;"]
        )
        
        self.assertFalse(unfrozen_snippet.is_frozen())
        
        # Create CodeSnippetList - should freeze the snippet
        snippet_list = CodeSnippetList([unfrozen_snippet])
        
        # The snippet should now be frozen
        self.assertTrue(unfrozen_snippet.is_frozen())
        self.assertTrue(snippet_list.is_frozen())
    
    def test_code_snippet_list_statistics(self):
        """Test CodeSnippetList statistics methods."""
        snippet_list = CodeSnippetList([self.snippet1, self.snippet2])
        
        self.assertEqual(snippet_list.get_total_snippets(), 2)
        self.assertEqual(snippet_list.get_file_count(), 2)
        self.assertEqual(snippet_list.get_total_lines(), 13)  # (2+6) + (1+4) = 8 + 5 = 13
        self.assertEqual(snippet_list.get_total_matched_lines(), 3)  # 2 + 1
        self.assertEqual(snippet_list.get_total_context_lines(), 10)  # 6 + 4
    
    def test_code_snippet_list_file_grouping(self):
        """Test CodeSnippetList file grouping functionality."""
        snippet_list = CodeSnippetList([self.snippet1, self.snippet2])
        
        file_groups = snippet_list.get_snippets_by_file()
        
        self.assertEqual(len(file_groups), 2)
        self.assertIn("test1.c", file_groups)
        self.assertIn("test2.c", file_groups)
        self.assertEqual(len(file_groups["test1.c"]), 1)
        self.assertEqual(len(file_groups["test2.c"]), 1)
    
    def test_code_snippet_list_iteration(self):
        """Test CodeSnippetList iteration functionality."""
        snippet_list = CodeSnippetList([self.snippet1, self.snippet2])
        
        snippets = list(snippet_list)
        self.assertEqual(len(snippets), 2)
        self.assertEqual(snippets[0].file_path, "test1.c")
        self.assertEqual(snippets[1].file_path, "test2.c")
    
    def test_code_snippet_list_indexing(self):
        """Test CodeSnippetList indexing functionality."""
        snippet_list = CodeSnippetList([self.snippet1, self.snippet2])
        
        self.assertEqual(snippet_list[0].file_path, "test1.c")
        self.assertEqual(snippet_list[1].file_path, "test2.c")
    
    def test_code_snippet_list_contains(self):
        """Test CodeSnippetList contains functionality."""
        snippet_list = CodeSnippetList([self.snippet1, self.snippet2])
        
        self.assertIn(self.snippet1, snippet_list)
        self.assertIn(self.snippet2, snippet_list)
        
        # Create a different snippet
        other_snippet = CodeSnippet(
            file_path="other.c",
            matched_lines=[1],
            context_lines=[2],
            raw_surrounding_git_grep_lines=["other.c-2-  // context", "other.c:1:  printf(\"other\");"],
            raw_content=["  // context", "  printf(\"other\");"]
        )
        
        self.assertNotIn(other_snippet, snippet_list)
    
    def test_code_snippet_list_json_serialization(self):
        """Test CodeSnippetList JSON serialization."""
        snippet_list = CodeSnippetList([self.snippet1, self.snippet2])
        
        # Test to_dict
        data = snippet_list.to_dict()
        self.assertIn("snippets", data)
        self.assertEqual(len(data["snippets"]), 2)
        
        # Test to_json
        json_str = snippet_list.to_json()
        self.assertIsInstance(json_str, str)
        
        # Test from_json
        recreated = CodeSnippetList.from_json(json_str)
        self.assertEqual(len(recreated), 2)
        self.assertEqual(recreated[0].file_path, "test1.c")
        self.assertEqual(recreated[1].file_path, "test2.c")
    
    def test_code_snippet_list_immutability(self):
        """Test that CodeSnippetList is immutable."""
        snippet_list = CodeSnippetList([self.snippet1, self.snippet2])
        
        # Should not be able to modify attributes after initialization
        with self.assertRaises(ValueError):
            snippet_list._snippets = []
        
        # Should not be able to set arbitrary attributes
        with self.assertRaises(ValueError):
            snippet_list.some_new_attribute = "test"
    
    def test_code_snippet_list_string_representations(self):
        """Test CodeSnippetList string representations."""
        snippet_list = CodeSnippetList([self.snippet1, self.snippet2])
        
        str_repr = str(snippet_list)
        self.assertIn("CodeSnippetList", str_repr)
        self.assertIn("2 snippets", str_repr)
        
        repr_str = repr(snippet_list)
        self.assertIn("CodeSnippetList", repr_str)
        self.assertIn("2 snippets", repr_str)
        self.assertIn("2 files", repr_str)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
