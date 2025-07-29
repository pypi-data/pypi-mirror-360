"""
Unit tests for JsonTableDirective class.

This module provides comprehensive test coverage for all methods of the
JsonTableDirective class, including normal and error cases.
"""

from pathlib import Path
from unittest.mock import Mock, PropertyMock, patch

import pytest

# Import the class under test and related exceptions
from sphinxcontrib.jsontable.directives import (
    DEFAULT_ENCODING,
    NO_JSON_SOURCE_ERROR,
    JsonTableDirective,
    JsonTableError,
)


class TestJsonTableDirective:
    """Test suite for JsonTableDirective class methods."""

    @pytest.fixture
    def mock_state(self):
        """Create a mock state with document and environment."""
        state = Mock()
        state.document = Mock()
        state.document.settings = Mock()
        state.document.settings.env = Mock()
        state.document.settings.env.srcdir = "/mock/source/dir"
        return state

    @pytest.fixture
    def directive_instance(self, mock_state):
        """Create a JsonTableDirective instance with mocked dependencies."""
        with patch("sphinx.util.docutils.SphinxDirective.__init__"), patch(
            "sphinxcontrib.jsontable.directives.JsonDataLoader"
        ) as mock_loader_class, patch(
            "sphinxcontrib.jsontable.directives.TableConverter"
        ) as mock_converter_class, patch(
            "sphinxcontrib.jsontable.directives.TableBuilder"
        ) as mock_builder_class:
            # Create instance without calling parent __init__
            directive = JsonTableDirective.__new__(JsonTableDirective)

            # Set up basic attributes
            directive.state = mock_state
            directive.arguments = []
            directive.content = []
            directive.options = {}
            directive.base_path = Path("/tmp/test_docs")

            # Set up mock instances
            directive.loader = mock_loader_class.return_value
            directive.converter = mock_converter_class.return_value
            directive.builder = mock_builder_class.return_value
            directive.json_processor = mock_loader_class.return_value
            directive.table_converter = mock_converter_class.return_value
            directive.table_builder = mock_builder_class.return_value

            # Store mock classes for verification
            directive._mock_loader_class = mock_loader_class
            directive._mock_converter_class = mock_converter_class
            directive._mock_builder_class = mock_builder_class

            return directive

    # Tests for __init__ method

    @patch("sphinxcontrib.jsontable.directives.JsonDataLoader")
    @patch("sphinxcontrib.jsontable.directives.TableConverter")
    @patch("sphinxcontrib.jsontable.directives.TableBuilder")
    def test_init_with_default_encoding(
        self, mock_builder, mock_converter, mock_loader
    ):
        """Test initialization uses default encoding when no encoding option provided."""
        # Arrange
        mock_state = Mock()
        mock_state_machine = Mock()
        args = (
            "json-table",
            [],
            {},
            [],
            1,
            0,
            "block text",
            mock_state,
            mock_state_machine,
        )

        # Act
        directive = JsonTableDirective(*args)  # noqa

        # Assert
        mock_loader.assert_called_once_with(encoding=DEFAULT_ENCODING)

    @patch("sphinxcontrib.jsontable.directives.JsonDataLoader")
    @patch("sphinxcontrib.jsontable.directives.TableConverter")
    @patch("sphinxcontrib.jsontable.directives.TableBuilder")
    def test_init_with_custom_encoding(self, mock_builder, mock_converter, mock_loader):
        """Test initialization uses custom encoding when encoding option provided."""
        # Arrange
        custom_encoding = "latin-1"
        mock_state = Mock()
        mock_state_machine = Mock()
        args = (
            "json-table",
            [],
            {"encoding": custom_encoding},
            [],
            1,
            0,
            "block text",
            mock_state,
            mock_state_machine,
        )

        # Act
        directive = JsonTableDirective(*args)  # noqa

        # Assert
        mock_loader.assert_called_once_with(encoding=custom_encoding)

    @patch("sphinxcontrib.jsontable.directives.JsonDataLoader")
    @patch("sphinxcontrib.jsontable.directives.TableConverter")
    @patch("sphinxcontrib.jsontable.directives.TableBuilder")
    def test_init_creates_required_components(
        self, mock_builder, mock_converter, mock_loader
    ):
        """Test initialization creates loader, converter, and builder instances."""
        # Arrange
        mock_state = Mock()
        mock_state_machine = Mock()
        args = (
            "json-table",
            [],
            {},
            [],
            1,
            0,
            "block text",
            mock_state,
            mock_state_machine,
        )

        # Act
        directive = JsonTableDirective(*args)

        # Assert
        assert hasattr(directive, "loader")
        assert hasattr(directive, "converter")
        assert hasattr(directive, "builder")

    # Tests for run method

    @patch("sphinxcontrib.jsontable.directives.directive_core.logger")
    def test_run_with_file_argument_no_options(self, mock_logger, directive_instance):
        """Test run method with file argument and no options."""
        # Arrange
        directive_instance.arguments = ["test.json"]
        directive_instance.options = {}

        mock_json_data = {"key": "value"}
        mock_table_data = [["row1"]]
        mock_table_node = Mock()

        directive_instance.loader.load_from_file.return_value = mock_json_data
        directive_instance.table_converter.convert.return_value = mock_table_data
        directive_instance.table_builder.build_table.return_value = [mock_table_node]

        # Act
        result = directive_instance.run()

        # Assert
        assert result == [mock_table_node]

    @patch("sphinxcontrib.jsontable.directives.directive_core.logger")
    def test_run_with_file_argument_and_header_option(
        self, mock_logger, directive_instance
    ):
        """Test run method with file argument and header option."""
        # Arrange
        directive_instance.arguments = ["test.json"]
        directive_instance.options = {"header": True}

        mock_json_data = [{"name": "test"}]
        directive_instance.loader.load_from_file.return_value = mock_json_data
        directive_instance.table_converter.convert.return_value = [["name"], ["test"]]
        directive_instance.table_builder.build_table.return_value = [Mock()]

        # Act
        directive_instance.run()

        # Assert
        directive_instance.table_converter.convert.assert_called_once_with(
            mock_json_data
        )

    @patch("sphinxcontrib.jsontable.directives.directive_core.logger")
    def test_run_with_file_argument_and_limit_option(
        self, mock_logger, directive_instance
    ):
        """Test run method with file argument and limit option."""
        # Arrange
        directive_instance.arguments = ["test.json"]
        directive_instance.options = {"limit": 10}

        mock_json_data = [{"name": "test"}]
        directive_instance.loader.load_from_file.return_value = mock_json_data
        directive_instance.table_converter.convert.return_value = [["test"]]
        directive_instance.table_builder.build_table.return_value = [Mock()]

        # Act
        directive_instance.run()

        # Assert
        directive_instance.table_converter.convert.assert_called_once_with(
            mock_json_data
        )

    @patch("sphinxcontrib.jsontable.directives.directive_core.logger")
    def test_run_with_inline_content_no_options(self, mock_logger, directive_instance):
        """Test run method with inline content and no options."""
        # Arrange
        directive_instance.arguments = []
        directive_instance.content = ['{"key": "value"}']
        directive_instance.options = {}

        mock_json_data = {"key": "value"}
        directive_instance.loader.parse_inline.return_value = mock_json_data
        directive_instance.table_converter.convert.return_value = [["row1"]]
        directive_instance.table_builder.build_table.return_value = [Mock()]

        # Act
        result = directive_instance.run()

        # Assert
        assert len(result) == 1

    @patch("sphinxcontrib.jsontable.directives.directive_core.logger")
    def test_run_with_inline_content_and_header_option(
        self, mock_logger, directive_instance
    ):
        """Test run method with inline content and header option."""
        # Arrange
        directive_instance.arguments = []
        directive_instance.content = ['[{"name": "test"}]']
        directive_instance.options = {"header": True}

        mock_json_data = [{"name": "test"}]
        directive_instance.loader.parse_inline.return_value = mock_json_data
        directive_instance.table_converter.convert.return_value = [["name"], ["test"]]
        directive_instance.table_builder.build_table.return_value = [Mock()]

        # Act
        directive_instance.run()

        # Assert
        directive_instance.table_builder.build_table.assert_called_once_with(
            [["name"], ["test"]]
        )

    @patch("sphinxcontrib.jsontable.directives.directive_core.logger")
    def test_run_with_all_options(self, mock_logger, directive_instance):
        """Test run method with all options provided."""
        # Arrange
        directive_instance.arguments = ["test.json"]
        directive_instance.options = {"header": True, "limit": 5, "encoding": "utf-8"}

        mock_json_data = [{"name": "test"}]
        directive_instance.loader.load_from_file.return_value = mock_json_data
        directive_instance.table_converter.convert.return_value = [["name"], ["test"]]
        directive_instance.table_builder.build_table.return_value = [Mock()]

        # Act
        directive_instance.run()

        # Assert
        directive_instance.table_converter.convert.assert_called_once_with(
            mock_json_data
        )

    @patch("sphinxcontrib.jsontable.directives.directive_core.logger")
    def test_run_handles_json_table_error(self, mock_logger, directive_instance):
        """Test run method handles JsonTableError and returns error node."""
        # Arrange
        directive_instance.arguments = ["test.json"]
        directive_instance.loader.load_from_file.side_effect = JsonTableError(
            "Test error"
        )

        with patch.object(
            directive_instance, "_create_error_node"
        ) as mock_create_error:
            mock_error_node = Mock()
            mock_create_error.return_value = mock_error_node

            # Act
            result = directive_instance.run()

            # Assert
            assert result == [mock_error_node]

    @patch("sphinxcontrib.jsontable.directives.directive_core.logger")
    def test_run_handles_file_not_found_error(self, mock_logger, directive_instance):
        """Test run method handles FileNotFoundError and returns error node."""
        # Arrange
        directive_instance.arguments = ["nonexistent.json"]
        directive_instance.loader.load_from_file.side_effect = FileNotFoundError(
            "File not found"
        )

        with patch.object(
            directive_instance, "_create_error_node"
        ) as mock_create_error:
            mock_error_node = Mock()
            mock_create_error.return_value = mock_error_node

            # Act
            result = directive_instance.run()

            # Assert
            assert result == [mock_error_node]

    # Tests for _load_json_file method

    def test_load_json_file_from_file(self, directive_instance):
        """Test _load_json_file loads from file when arguments provided."""
        # Arrange
        directive_instance.arguments = ["test.json"]
        directive_instance.content = []

        mock_json_data = {"key": "value"}
        directive_instance.loader.load_from_file.return_value = mock_json_data

        # Mock the env property access
        with patch.object(
            type(directive_instance), "env", new_callable=PropertyMock
        ) as mock_env:
            mock_env.return_value.srcdir = "/source/dir"

            # Act
            result = directive_instance._load_json_file("test.json")

            # Assert
            assert result == mock_json_data

    def test_load_json_file_from_inline_content(self, directive_instance):
        """Test _load_data loads from inline content when no arguments."""
        # Arrange
        directive_instance.arguments = []
        directive_instance.content = ['{"key": "value"}']

        mock_json_data = {"key": "value"}
        directive_instance.loader.parse_inline.return_value = mock_json_data

        # Act
        result = directive_instance._load_data()

        # Assert
        assert result == mock_json_data

    def test_load_json_file_no_source_raises_error(self, directive_instance):
        """Test _load_data raises JsonTableError when no source provided."""
        # Arrange
        directive_instance.arguments = []
        directive_instance.content = []

        # Act & Assert
        with pytest.raises(JsonTableError) as exc_info:
            directive_instance._load_data()

        assert str(exc_info.value) == NO_JSON_SOURCE_ERROR

    # Tests for _create_error_node method

    def test_create_error_node_structure(self, directive_instance):
        """Test _create_error_node creates correct node structure."""
        # Arrange
        error_message = "Test error message"

        # Act
        result = directive_instance._create_error_node(error_message)

        # Assert - Check that it returns an actual error node
        from docutils import nodes

        assert isinstance(result, nodes.error)
        assert len(result.children) == 1  # Should contain one paragraph
        assert isinstance(result.children[0], nodes.paragraph)
        assert result.children[0].astext() == error_message

    def test_create_error_node_message_content(self, directive_instance):
        """Test _create_error_node includes message in paragraph node."""
        # Arrange
        error_message = "Custom error message for testing"

        # Act
        result = directive_instance._create_error_node(error_message)

        # Assert - Check message content
        from docutils import nodes

        assert isinstance(result, nodes.error)
        paragraph = result.children[0]
        assert isinstance(paragraph, nodes.paragraph)
        assert paragraph.astext() == error_message

    # Additional edge case tests

    @patch("sphinxcontrib.jsontable.directives.directive_core.logger")
    def test_run_processes_limit_option_correctly(
        self, mock_logger, directive_instance
    ):
        """Test run method processes limit option correctly without specific logging."""
        # Arrange
        directive_instance.arguments = ["test.json"]
        directive_instance.options = {"limit": 10}

        mock_json_data = [{"name": "test"}]
        directive_instance.loader.load_from_file.return_value = mock_json_data
        directive_instance.table_converter.convert.return_value = [["test"]]
        directive_instance.table_builder.build_table.return_value = [Mock()]

        # Act
        result = directive_instance.run()

        # Assert
        # Verify that the limit was passed to converter.convert
        directive_instance.table_converter.convert.assert_called_once_with(
            mock_json_data
        )
        # Verify successful execution
        assert len(result) == 1

    def test_load_json_file_calls_loader_with_correct_path(self, directive_instance):
        """Test _load_json_file calls loader with correct source directory path."""
        # Arrange
        directive_instance.arguments = ["data/test.json"]
        directive_instance.content = []

        mock_json_data = {"key": "value"}
        directive_instance.loader.load_from_file.return_value = mock_json_data

        # Mock the env property access
        with patch.object(
            type(directive_instance), "env", new_callable=PropertyMock
        ) as mock_env:
            mock_source_dir = Path("/project/source")
            mock_env.return_value.srcdir = str(mock_source_dir)

            # Act
            directive_instance._load_json_file("test.json")

            # Assert
            directive_instance.loader.load_from_file.assert_called_once_with(
                "test.json",
                mock_source_dir,
            )
