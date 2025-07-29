"""
Comprehensive unit tests for directives.json_processor module.

This test suite provides complete coverage for JsonProcessor class methods,
following TDD approach and AAA (Arrange-Act-Assert) pattern.
Tests cover normal operation, edge cases, and error scenarios.
"""

import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

# Import the classes and functions to be tested
from sphinxcontrib.jsontable.directives.json_processor import JsonProcessor
from sphinxcontrib.jsontable.directives.validators import JsonTableError


class TestJsonProcessor:
    """Test suite for JsonProcessor class methods."""

    @pytest.fixture
    def processor(self):
        """Create a JsonProcessor instance for testing."""
        return JsonProcessor(base_path=Path("/test/base"), encoding="utf-8")

    @pytest.fixture
    def processor_default_encoding(self):
        """Create a JsonProcessor instance with default encoding."""
        return JsonProcessor(base_path=Path("/test/base"))

    class TestInit:
        """Test suite for JsonProcessor.__init__ method."""

        def test_init_with_custom_encoding(self):
            """Test initialization with custom encoding."""
            # Arrange
            base_path = Path("/test/path")
            encoding = "iso-8859-1"

            # Act
            processor = JsonProcessor(base_path=base_path, encoding=encoding)

            # Assert
            assert processor.base_path == base_path
            assert processor.encoding == encoding

        def test_init_with_default_encoding(self):
            """Test initialization with default encoding."""
            # Arrange
            base_path = Path("/test/path")

            # Act
            processor = JsonProcessor(base_path=base_path)

            # Assert
            assert processor.base_path == base_path
            assert processor.encoding == "utf-8"

        def test_init_validates_encoding(self):
            """Test that initialization validates encoding."""
            # Arrange
            base_path = Path("/test/path")
            invalid_encoding = "invalid-encoding-123"

            # Act
            processor = JsonProcessor(base_path=base_path, encoding=invalid_encoding)

            # Assert - should fall back to default encoding
            assert processor.encoding == "utf-8"

    class TestValidateEncoding:
        """Test suite for _validate_encoding method."""

        def test_validate_encoding_with_valid_encoding(self, processor):
            """Test _validate_encoding with valid encoding."""
            # Arrange
            valid_encoding = "utf-8"

            # Act
            result = processor._validate_encoding(valid_encoding)

            # Assert
            assert result == valid_encoding

        def test_validate_encoding_with_invalid_encoding(self, processor):
            """Test _validate_encoding with invalid encoding."""
            # Arrange
            invalid_encoding = "invalid-encoding-123"

            # Act
            result = processor._validate_encoding(invalid_encoding)

            # Assert
            assert result == "utf-8"  # Should fall back to default

        def test_validate_encoding_with_common_encodings(self, processor):
            """Test _validate_encoding with common valid encodings."""
            # Arrange
            valid_encodings = ["utf-8", "utf-16", "ascii", "iso-8859-1"]

            for encoding in valid_encodings:
                # Act
                result = processor._validate_encoding(encoding)

                # Assert
                assert result == encoding

    class TestValidateFilePath:
        """Test suite for _validate_file_path method."""

        @patch(
            "sphinxcontrib.jsontable.directives.json_processor.ValidationUtils.is_safe_path"
        )
        def test_validate_file_path_with_safe_path(self, mock_is_safe_path, processor):
            """Test _validate_file_path with safe path."""
            # Arrange
            source = "data/test.json"
            mock_is_safe_path.return_value = True

            # Act
            result = processor._validate_file_path(source)

            # Assert
            expected_path = processor.base_path / source
            assert result == expected_path
            mock_is_safe_path.assert_called_once()

        @patch(
            "sphinxcontrib.jsontable.directives.json_processor.ValidationUtils.is_safe_path"
        )
        def test_validate_file_path_with_unsafe_path(
            self, mock_is_safe_path, processor
        ):
            """Test _validate_file_path with unsafe path raises JsonTableError."""
            # Arrange
            source = "../../../etc/passwd"
            mock_is_safe_path.return_value = False

            # Act & Assert
            with pytest.raises(JsonTableError) as exc_info:
                processor._validate_file_path(source)
            assert "Invalid file path" in str(exc_info.value)

    class TestLoadFromFile:
        """Test suite for load_from_file method."""

        @patch(
            "sphinxcontrib.jsontable.directives.json_processor.ValidationUtils.ensure_file_exists"
        )
        @patch(
            "sphinxcontrib.jsontable.directives.json_processor.ValidationUtils.is_safe_path"
        )
        def test_load_from_file_success(
            self, mock_is_safe_path, mock_ensure_file_exists, processor
        ):
            """Test successful file loading."""
            # Arrange
            source = "data/test.json"
            test_data = {"name": "test", "value": 123}
            mock_is_safe_path.return_value = True

            with patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
                # Act
                result = processor.load_from_file(source)

                # Assert
                assert result == test_data
                mock_ensure_file_exists.assert_called_once()

        @patch(
            "sphinxcontrib.jsontable.directives.json_processor.ValidationUtils.ensure_file_exists"
        )
        @patch(
            "sphinxcontrib.jsontable.directives.json_processor.ValidationUtils.is_safe_path"
        )
        def test_load_from_file_json_decode_error(
            self, mock_is_safe_path, mock_ensure_file_exists, processor
        ):
            """Test load_from_file with invalid JSON raises JsonTableError."""
            # Arrange
            source = "data/invalid.json"
            invalid_json = "{ invalid json }"
            mock_is_safe_path.return_value = True

            with patch("builtins.open", mock_open(read_data=invalid_json)):
                # Act & Assert
                with pytest.raises(JsonTableError) as exc_info:
                    processor.load_from_file(source)
                assert "Failed to load" in str(exc_info.value)

        @patch(
            "sphinxcontrib.jsontable.directives.json_processor.ValidationUtils.ensure_file_exists"
        )
        @patch(
            "sphinxcontrib.jsontable.directives.json_processor.ValidationUtils.is_safe_path"
        )
        def test_load_from_file_unicode_decode_error(
            self, mock_is_safe_path, mock_ensure_file_exists, processor
        ):
            """Test load_from_file with encoding error raises JsonTableError."""
            # Arrange
            source = "data/bad_encoding.json"
            mock_is_safe_path.return_value = True

            with patch(
                "builtins.open",
                side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "test error"),
            ):
                # Act & Assert
                with pytest.raises(JsonTableError) as exc_info:
                    processor.load_from_file(source)
                assert "Failed to load" in str(exc_info.value)

    class TestParseInline:
        """Test suite for parse_inline method."""

        def test_parse_inline_success_object(self, processor):
            """Test successful inline JSON object parsing."""
            # Arrange
            content = ['{"name": "test", "value": 123}']

            # Act
            result = processor.parse_inline(content)

            # Assert
            assert result == {"name": "test", "value": 123}

        def test_parse_inline_success_array(self, processor):
            """Test successful inline JSON array parsing."""
            # Arrange
            content = ['[{"id": 1}, {"id": 2}]']

            # Act
            result = processor.parse_inline(content)

            # Assert
            assert result == [{"id": 1}, {"id": 2}]

        def test_parse_inline_multiline(self, processor):
            """Test successful parsing of multiline JSON."""
            # Arrange
            content = ["{", '  "name": "test",', '  "value": 123', "}"]

            # Act
            result = processor.parse_inline(content)

            # Assert
            assert result == {"name": "test", "value": 123}

        @patch(
            "sphinxcontrib.jsontable.directives.json_processor.ValidationUtils.validate_not_empty"
        )
        def test_parse_inline_empty_content_raises_error(
            self, mock_validate, processor
        ):
            """Test parse_inline with empty content raises JsonTableError."""
            # Arrange
            content = []
            mock_validate.side_effect = JsonTableError(
                "No inline JSON content provided"
            )

            # Act & Assert
            with pytest.raises(JsonTableError) as exc_info:
                processor.parse_inline(content)
            assert "No inline JSON content provided" in str(exc_info.value)

        def test_parse_inline_invalid_json_raises_error(self, processor):
            """Test parse_inline with invalid JSON raises JsonTableError."""
            # Arrange
            content = ["{ invalid json }"]

            # Act & Assert
            with pytest.raises(JsonTableError) as exc_info:
                processor.parse_inline(content)
            assert "Invalid inline JSON" in str(exc_info.value)

        def test_parse_inline_none_content_raises_error(self, processor):
            """Test parse_inline with None content raises JsonTableError."""
            # Arrange
            content = None

            # Act & Assert
            with pytest.raises(JsonTableError):
                processor.parse_inline(content)

    class TestIntegration:
        """Integration tests for JsonProcessor."""

        def test_processor_handles_different_data_types(self):
            """Test that processor correctly handles various JSON data types."""
            # Arrange
            processor = JsonProcessor(base_path=Path("/test"))
            test_cases = [
                '{"string": "value", "number": 123, "boolean": true, "null": null}',
                "[1, 2, 3, 4, 5]",
                '{"nested": {"deep": {"value": "test"}}}',
                "[]",
                "{}",
            ]

            for json_string in test_cases:
                # Act
                result = processor.parse_inline([json_string])

                # Assert
                expected = json.loads(json_string)
                assert result == expected

        def test_processor_encoding_handling(self):
            """Test processor handles different encodings correctly."""
            # Arrange & Act
            utf8_processor = JsonProcessor(Path("/test"), "utf-8")
            ascii_processor = JsonProcessor(Path("/test"), "ascii")

            # Assert
            assert utf8_processor.encoding == "utf-8"
            assert ascii_processor.encoding == "ascii"
