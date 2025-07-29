"""
Comprehensive unit tests for JsonDataLoader class.

This module contains unit tests for all methods of the JsonDataLoader class,
following pytest best practices with AAA pattern and single assertion per test.
Tests cover both normal and error scenarios with proper mocking for isolation.
"""

import json
from pathlib import Path
from unittest.mock import call, mock_open, patch

import pytest

from sphinxcontrib.jsontable.directives import (
    DEFAULT_ENCODING,
    EMPTY_CONTENT_ERROR,
    JsonDataLoader,
    JsonTableError,
)


class TestJsonDataLoaderInit:
    """Test cases for JsonDataLoader.__init__ method."""

    def test_init_with_default_encoding(self):
        """Test initialization with default encoding."""
        # Arrange & Act
        loader = JsonDataLoader()

        # Assert
        assert loader.encoding == DEFAULT_ENCODING

    def test_init_with_valid_custom_encoding(self):
        """Test initialization with valid custom encoding."""
        # Arrange
        custom_encoding = "utf-16"

        # Act
        loader = JsonDataLoader(encoding=custom_encoding)

        # Assert
        assert loader.encoding == custom_encoding

    @patch("sphinxcontrib.jsontable.directives.logger")
    def test_init_with_invalid_encoding_falls_back_to_default(self, mock_logger):
        """Test initialization with invalid encoding falls back to default."""
        # Arrange
        invalid_encoding = "invalid-encoding"

        # Act
        loader = JsonDataLoader(encoding=invalid_encoding)

        # Assert
        assert loader.encoding == DEFAULT_ENCODING


class TestJsonDataLoaderValidateEncoding:
    """Test cases for JsonDataLoader._validate_encoding method."""

    def test_validate_encoding_with_valid_encoding(self):
        """Test _validate_encoding returns valid encoding unchanged."""
        # Arrange
        loader = JsonDataLoader()
        valid_encoding = "utf-8"

        # Act
        result = loader._validate_encoding(valid_encoding)

        # Assert
        assert result == valid_encoding

    @patch("sphinxcontrib.jsontable.directives.backward_compatibility.logger")
    def test_validate_encoding_with_invalid_encoding_returns_default(self, mock_logger):
        """Test _validate_encoding returns default for invalid encoding."""
        # Arrange
        loader = JsonDataLoader()
        invalid_encoding = "nonexistent-encoding"

        # Act
        result = loader._validate_encoding(invalid_encoding)

        # Assert
        assert result == DEFAULT_ENCODING

    @patch("sphinxcontrib.jsontable.directives.backward_compatibility.logger")
    def test_validate_encoding_logs_warning_for_invalid_encoding(self, mock_logger):
        """Test _validate_encoding logs warning for invalid encoding."""
        # Arrange
        loader = JsonDataLoader()
        invalid_encoding = "invalid-encoding"

        # Act
        loader._validate_encoding(invalid_encoding)

        # Assert
        mock_logger.warning.assert_called_once()


class TestJsonDataLoaderValidateFilePath:
    """Test cases for JsonDataLoader._validate_file_path method."""

    @patch("sphinxcontrib.jsontable.directives.is_safe_path")
    def test_validate_file_path_with_safe_path_returns_path(self, mock_is_safe_path):
        """Test _validate_file_path returns path for safe paths."""
        # Arrange
        loader = JsonDataLoader()
        source = "data.json"
        srcdir = Path("/safe/dir")
        mock_is_safe_path.return_value = True

        # Act
        result = loader._validate_file_path(source, srcdir)

        # Assert
        assert result == srcdir / source

    @patch("sphinxcontrib.jsontable.directives.is_safe_path")
    def test_validate_file_path_with_unsafe_path_raises_error(self, mock_is_safe_path):
        """Test _validate_file_path raises error for unsafe paths."""
        # Arrange
        loader = JsonDataLoader()
        source = "../../../etc/passwd"
        srcdir = Path("/safe/dir")
        mock_is_safe_path.return_value = False

        # Act & Assert
        with pytest.raises(JsonTableError, match="Unsafe file path"):
            loader._validate_file_path(source, srcdir)

    @patch("sphinxcontrib.jsontable.directives.is_safe_path")
    def test_validate_file_path_calls_is_safe_path_with_correct_arguments(
        self, mock_is_safe_path
    ):
        """Test _validate_file_path calls is_safe_path with correct arguments."""
        # Arrange
        loader = JsonDataLoader()
        source = "data.json"
        srcdir = Path("/safe/dir")
        mock_is_safe_path.return_value = True
        expected_file_path = Path(source)  # 相対パスのまま呼び出される

        # Act
        loader._validate_file_path(source, srcdir)

        # Assert
        mock_is_safe_path.assert_called_once_with(expected_file_path, srcdir)


class TestJsonDataLoaderLoadFromFile:
    """Test cases for JsonDataLoader.load_from_file method."""

    @patch(
        "sphinxcontrib.jsontable.directives.validators.ValidationUtils.ensure_file_exists"
    )
    @patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
    @patch("json.load")
    def test_load_from_file_with_valid_json_returns_data(
        self, mock_json_load, mock_file, mock_ensure_exists
    ):
        """Test load_from_file returns JSON data for valid file."""
        # Arrange
        loader = JsonDataLoader()
        source = "data.json"
        srcdir = Path("/test")
        expected_data = {"key": "value"}
        mock_json_load.return_value = expected_data

        with patch.object(loader, "_validate_file_path") as mock_validate:
            mock_validate.return_value = srcdir / source

            # Act
            result = loader.load_from_file(source, srcdir)

            # Assert
            assert result == expected_data

    def test_load_from_file_with_nonexistent_file_raises_error(self):
        """Test load_from_file raises error for nonexistent file."""
        # Arrange
        loader = JsonDataLoader()
        source = "nonexistent.json"
        srcdir = Path("/test")

        with patch.object(loader, "_validate_file_path") as mock_validate:
            mock_validate.return_value = srcdir / source

            with patch(
                "sphinxcontrib.jsontable.directives.validators.ValidationUtils.ensure_file_exists"
            ) as mock_ensure:
                mock_ensure.side_effect = FileNotFoundError("File not found")

                # Act & Assert
                with pytest.raises(FileNotFoundError):
                    loader.load_from_file(source, srcdir)

    @patch(
        "sphinxcontrib.jsontable.directives.validators.ValidationUtils.ensure_file_exists"
    )
    @patch("builtins.open", new_callable=mock_open, read_data="invalid json")
    @patch("json.load")
    def test_load_from_file_with_invalid_json_raises_json_table_error(
        self, mock_json_load, mock_file, mock_ensure_exists
    ):
        """Test load_from_file raises JsonTableError for invalid JSON."""
        # Arrange
        loader = JsonDataLoader()
        source = "invalid.json"
        srcdir = Path("/test")
        mock_json_load.side_effect = json.JSONDecodeError("Invalid JSON", "doc", 0)

        with patch.object(loader, "_validate_file_path") as mock_validate:
            mock_validate.return_value = srcdir / source

            # Act & Assert
            with pytest.raises(JsonTableError, match="Failed to load"):
                loader.load_from_file(source, srcdir)

    @patch(
        "sphinxcontrib.jsontable.directives.validators.ValidationUtils.ensure_file_exists"
    )
    @patch("builtins.open")
    def test_load_from_file_with_unicode_error_raises_json_table_error(
        self, mock_open_func, mock_ensure_exists
    ):
        """Test load_from_file raises JsonTableError for Unicode decode error."""
        # Arrange
        loader = JsonDataLoader()
        source = "binary.json"
        srcdir = Path("/test")
        mock_open_func.side_effect = UnicodeDecodeError("utf-8", b"", 0, 1, "invalid")

        with patch.object(loader, "_validate_file_path") as mock_validate:
            mock_validate.return_value = srcdir / source

            # Act & Assert
            with pytest.raises(JsonTableError, match="Failed to load"):
                loader.load_from_file(source, srcdir)

    @patch(
        "sphinxcontrib.jsontable.directives.validators.ValidationUtils.ensure_file_exists"
    )
    @patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
    @patch("json.load")
    def test_load_from_file_opens_file_with_correct_encoding(
        self, mock_json_load, mock_file, mock_ensure_exists
    ):
        """Test load_from_file opens file with correct encoding."""
        # Arrange
        custom_encoding = "utf-16"
        loader = JsonDataLoader(encoding=custom_encoding)
        source = "data.json"
        srcdir = Path("/test")
        mock_json_load.return_value = {"key": "value"}

        with patch.object(loader, "_validate_file_path") as mock_validate:
            mock_validate.return_value = srcdir / source

            # Act
            loader.load_from_file(source, srcdir)

            # Assert
            mock_file.assert_called_once_with(srcdir / source, encoding=custom_encoding)


class TestJsonDataLoaderParseInline:
    """Test cases for JsonDataLoader.parse_inline method."""

    def test_parse_inline_with_valid_json_list_returns_data(self):
        """Test parse_inline returns data for valid JSON list."""
        # Arrange
        loader = JsonDataLoader()
        content = ['{"key": "value",', '"number": 42}']
        expected_data = {"key": "value", "number": 42}

        # Act
        result = loader.parse_inline(content)

        # Assert
        assert result == expected_data

    def test_parse_inline_with_valid_json_array_returns_list(self):
        """Test parse_inline returns list for valid JSON array."""
        # Arrange
        loader = JsonDataLoader()
        content = ["[1, 2, 3]"]
        expected_data = [1, 2, 3]

        # Act
        result = loader.parse_inline(content)

        # Assert
        assert result == expected_data

    def test_parse_inline_with_multiline_json_returns_data(self):
        """Test parse_inline handles multiline JSON correctly."""
        # Arrange
        loader = JsonDataLoader()
        content = [
            "{",
            '  "name": "test",',
            '  "items": [1, 2, 3]',
            "}",
        ]
        expected_data = {"name": "test", "items": [1, 2, 3]}

        # Act
        result = loader.parse_inline(content)

        # Assert
        assert result == expected_data

    @patch(
        "sphinxcontrib.jsontable.directives.validators.ValidationUtils.validate_not_empty"
    )
    def test_parse_inline_with_empty_content_raises_error(self, mock_validate):
        """Test parse_inline raises error for empty content."""
        # Arrange
        loader = JsonDataLoader()
        content = []
        mock_validate.side_effect = JsonTableError(EMPTY_CONTENT_ERROR)

        # Act & Assert
        with pytest.raises(JsonTableError, match=EMPTY_CONTENT_ERROR):
            loader.parse_inline(content)

    def test_parse_inline_with_invalid_json_raises_json_table_error(self):
        """Test parse_inline raises JsonTableError for invalid JSON."""
        # Arrange
        loader = JsonDataLoader()
        content = ['{"invalid": json}']

        # Act & Assert
        with pytest.raises(JsonTableError, match="Invalid inline JSON"):
            loader.parse_inline(content)

    def test_parse_inline_with_incomplete_json_raises_json_table_error(self):
        """Test parse_inline raises JsonTableError for incomplete JSON."""
        # Arrange
        loader = JsonDataLoader()
        content = ['{"incomplete":']

        # Act & Assert
        with pytest.raises(JsonTableError, match="Invalid inline JSON"):
            loader.parse_inline(content)

    @patch(
        "sphinxcontrib.jsontable.directives.validators.ValidationUtils.validate_not_empty"
    )
    def test_parse_inline_calls_validate_not_empty_with_content(self, mock_validate):
        """Test parse_inline calls validate_not_empty with correct arguments."""
        # Arrange
        loader = JsonDataLoader()
        content = ['{"key": "value"}']

        # Act
        loader.parse_inline(content)

        # Assert - validate_not_empty is called twice: once in JsonDataLoader and once in JsonProcessor
        assert mock_validate.call_count == 2
        mock_validate.assert_has_calls(
            [call(content, EMPTY_CONTENT_ERROR), call(content, EMPTY_CONTENT_ERROR)]
        )


# Integration test fixtures and helpers
@pytest.fixture
def temp_json_file(tmp_path):
    """Create a temporary JSON file for testing."""
    json_file = tmp_path / "test.json"
    test_data = {"test": "data", "numbers": [1, 2, 3]}
    json_file.write_text(json.dumps(test_data), encoding="utf-8")
    return json_file, test_data


@pytest.fixture
def sample_json_data():
    """Sample JSON data for testing."""
    return {"name": "test", "values": [1, 2, 3], "nested": {"key": "value"}}


class TestJsonDataLoaderIntegration:
    """Integration tests for JsonDataLoader methods working together."""

    @patch("sphinxcontrib.jsontable.directives.validators.ValidationUtils.is_safe_path")
    def test_loader_encoding_affects_file_operations(self, mock_is_safe_path, tmp_path):
        """Test that loader encoding setting affects file operations."""
        # Arrange
        mock_is_safe_path.return_value = True  # Allow the test file path
        utf8_loader = JsonDataLoader(encoding="utf-8")
        test_data = {"test": "data"}
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(test_data), encoding="utf-8")

        # Act
        result = utf8_loader.load_from_file("test.json", tmp_path)

        # Assert
        assert result == test_data

    def test_different_loader_instances_are_independent(self):
        """Test that different loader instances maintain independent state."""
        # Arrange
        loader1 = JsonDataLoader(encoding="utf-8")
        loader2 = JsonDataLoader(encoding="utf-16")

        # Act & Assert
        assert loader1.encoding != loader2.encoding
        assert loader1.encoding == "utf-8"
        assert loader2.encoding == "utf-16"
