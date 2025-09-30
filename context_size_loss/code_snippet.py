#!/usr/bin/env python3
"""
Code Snippet Module

This module provides the CodeSnippet class to represent parsed git grep output
in a structured way. It includes methods for JSON serialization and deserialization,
as well as immutability support through the freeze() method.

The CodeSnippet class encapsulates:
- file_path: The path to the file containing the snippet
- matched_lines: List of line numbers that matched the search pattern
- context_lines: List of context line numbers surrounding the matched lines
- raw_surrounding_git_grep_lines: Raw git grep output lines for this snippet
- raw_content: The actual content of the lines (without file/line number prefixes)

Immutability:
The CodeSnippet object can be made immutable by calling the freeze() method.
After freezing:
- All list fields are converted to tuples for additional immutability
- No fields can be modified (attempts raise ValueError)
- The object becomes truly immutable and thread-safe
- All existing methods continue to work normally
"""

import json
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict


@dataclass
class CodeSnippet:
    """
    Represents a code snippet extracted from git grep output.
    
    This class encapsulates all the information about a code snippet including
    the file path, matched lines, context lines, and raw content.
    
    The object can be made immutable by calling the freeze() method, after which
    no modifications are allowed.
    """
    
    file_path: str
    matched_lines: Union[List[int], Tuple[int, ...]]
    context_lines: Union[List[int], Tuple[int, ...]]
    raw_surrounding_git_grep_lines: Union[List[str], Tuple[str, ...]]
    raw_content: Union[List[str], Tuple[str, ...]]
    _frozen: bool = False
    
    def __post_init__(self):
        """Validate the snippet data after initialization."""
        if not self.file_path:
            raise ValueError("file_path cannot be empty")
        
        if not isinstance(self.matched_lines, (list, tuple)):
            raise ValueError("matched_lines must be a list or tuple")
        
        if not isinstance(self.context_lines, (list, tuple)):
            raise ValueError("context_lines must be a list or tuple")
        
        if not isinstance(self.raw_surrounding_git_grep_lines, (list, tuple)):
            raise ValueError("raw_surrounding_git_grep_lines must be a list or tuple")
        
        if not isinstance(self.raw_content, (list, tuple)):
            raise ValueError("raw_content must be a list or tuple")
    
    def __setattr__(self, name: str, value: Any) -> None:
        """Override setattr to prevent modification of frozen objects."""
        if hasattr(self, '_frozen') and self._frozen and name != '_frozen':
            raise ValueError(f"Cannot modify frozen CodeSnippet object. Attempted to set '{name}'")
        super().__setattr__(name, value)
    
    def freeze(self) -> None:
        """
        Make this CodeSnippet object immutable.
        
        After calling this method:
        - No fields can be modified
        - All list fields are converted to tuples for additional immutability
        - Any attempt to modify the object will raise a ValueError
        
        This method can only be called once. Subsequent calls are ignored.
        """
        if self._frozen:
            return  # Already frozen, do nothing
        
        # Convert mutable lists to immutable tuples
        object.__setattr__(self, 'matched_lines', tuple(self.matched_lines))
        object.__setattr__(self, 'context_lines', tuple(self.context_lines))
        object.__setattr__(self, 'raw_surrounding_git_grep_lines', tuple(self.raw_surrounding_git_grep_lines))
        object.__setattr__(self, 'raw_content', tuple(self.raw_content))
        
        # Mark as frozen
        object.__setattr__(self, '_frozen', True)
    
    def is_frozen(self) -> bool:
        """
        Check if this CodeSnippet object is frozen (immutable).
        
        Returns:
            True if the object is frozen, False otherwise
        """
        return self._frozen
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CodeSnippet':
        """
        Create a CodeSnippet instance from a dictionary.
        
        Args:
            data: Dictionary containing snippet data
            
        Returns:
            CodeSnippet instance
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        required_fields = ['file_path', 'matched_lines', 'context_lines', 
                          'raw_surrounding_git_grep_lines', 'raw_content']
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        return cls(
            file_path=data['file_path'],
            matched_lines=data['matched_lines'],
            context_lines=data['context_lines'],
            raw_surrounding_git_grep_lines=data['raw_surrounding_git_grep_lines'],
            raw_content=data['raw_content']
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'CodeSnippet':
        """
        Create a CodeSnippet instance from a JSON string.
        
        Args:
            json_str: JSON string containing snippet data
            
        Returns:
            CodeSnippet instance
            
        Raises:
            ValueError: If JSON is invalid or required fields are missing
            json.JSONDecodeError: If JSON parsing fails
        """
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON: {e.msg}", e.doc, e.pos)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the CodeSnippet to a dictionary.
        
        Returns:
            Dictionary representation of the snippet
        """
        return asdict(self)
    
    def to_json(self, indent: Optional[int] = None) -> str:
        """
        Convert the CodeSnippet to a JSON string.
        
        Args:
            indent: Number of spaces for JSON indentation (None for compact)
            
        Returns:
            JSON string representation of the snippet
        """
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def get_total_lines(self) -> int:
        """
        Get the total number of lines in this snippet.
        
        Returns:
            Total number of lines (matched + context)
        """
        return len(self.matched_lines) + len(self.context_lines)
    
    def get_matched_line_count(self) -> int:
        """
        Get the number of matched lines in this snippet.
        
        Returns:
            Number of matched lines
        """
        return len(self.matched_lines)
    
    def get_context_line_count(self) -> int:
        """
        Get the number of context lines in this snippet.
        
        Returns:
            Number of context lines
        """
        return len(self.context_lines)
    
    def get_full_content(self) -> str:
        """
        Get the full content of the snippet as a single string.
        
        Returns:
            Full content with newlines between lines
        """
        return '\n'.join(self.raw_content)
    
    def get_git_grep_output(self) -> str:
        """
        Get the raw git grep output for this snippet.
        
        Returns:
            Raw git grep output lines joined with newlines
        """
        return '\n'.join(self.raw_surrounding_git_grep_lines)
    
    def __str__(self) -> str:
        """String representation of the snippet."""
        return (f"CodeSnippet(file_path='{self.file_path}', "
                f"matched_lines={len(self.matched_lines)}, "
                f"context_lines={len(self.context_lines)})")
    
    def __repr__(self) -> str:
        """Detailed string representation of the snippet."""
        return (f"CodeSnippet(file_path='{self.file_path}', "
                f"matched_lines={self.matched_lines}, "
                f"context_lines={self.context_lines}, "
                f"total_lines={self.get_total_lines()})")


def snippets_from_json_list(json_data: List[Dict[str, Any]]) -> List[CodeSnippet]:
    """
    Create a list of CodeSnippet instances from a list of dictionaries.
    
    Args:
        json_data: List of dictionaries containing snippet data
        
    Returns:
        List of CodeSnippet instances
    """
    return [CodeSnippet.from_dict(snippet_data) for snippet_data in json_data]


def snippets_to_json_list(snippets: List[CodeSnippet], indent: Optional[int] = None) -> str:
    """
    Convert a list of CodeSnippet instances to a JSON string.
    
    Args:
        snippets: List of CodeSnippet instances
        indent: Number of spaces for JSON indentation (None for compact)
        
    Returns:
        JSON string representation of the snippets list
    """
    data = [snippet.to_dict() for snippet in snippets]
    return json.dumps(data, indent=indent, ensure_ascii=False)
