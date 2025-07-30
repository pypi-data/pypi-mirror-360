"""Unit tests for mynds filesystem functionality."""

from pathlib import Path

import pytest
from unittest.mock import patch

from mynd.utils.filesystem import list_directory, search_files


# Tests for list_directory
def test_list_directory():
    with patch("glob.glob") as mock_glob:
        mock_glob.return_value = ["/path/file1.txt", "/path/file2.txt"]
        result = list_directory(Path("/path"), "*.txt")
        assert len(result) == 2
        assert all(isinstance(item, Path) for item in result)
        mock_glob.assert_called_once_with("/path/*.txt")


# Tests for search_files
def test_search_files():
    with patch("glob.glob") as mock_glob:
        mock_glob.return_value = ["/path/file1.txt", "/path/file2.txt"]
        result = search_files("*.txt")
        assert len(result) == 2
        assert all(isinstance(item, Path) for item in result)
        mock_glob.assert_called_once_with("*.txt")
