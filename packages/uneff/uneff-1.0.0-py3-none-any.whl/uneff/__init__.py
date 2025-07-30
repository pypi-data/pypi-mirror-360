"""
Uneff - A tool to remove BOM and problematic Unicode characters from files

This module provides functionality to clean text files by removing BOM markers
and other invisible Unicode characters that can cause issues when processing data files.
"""

from .core import (
    clean_file,
    clean_text,
    clean_content,
    analyze_file,
    analyze_content,
    get_default_mappings_csv,
    parse_mapping_csv,
    read_char_mappings
)

__version__ = "1.0.0"
__author__ = "Mark"
__email__ = "mark@example.com"  # Update with your email
__description__ = "Remove BOM and problematic Unicode characters from text files"

__all__ = [
    'clean_file',
    'clean_text', 
    'clean_content',
    'analyze_file',
    'analyze_content',
    'get_default_mappings_csv',
    'parse_mapping_csv',
    'read_char_mappings'
]