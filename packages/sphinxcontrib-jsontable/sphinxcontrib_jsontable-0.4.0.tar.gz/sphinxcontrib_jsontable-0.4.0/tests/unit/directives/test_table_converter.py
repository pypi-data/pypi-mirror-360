"""Table Converter Tests - Phase 3.2 Coverage Boost."""

import pytest

from sphinxcontrib.jsontable.directives.table_converter import TableConverter
from sphinxcontrib.jsontable.directives.validators import JsonTableError


class TestTableConverter:
    """Test suite for TableConverter."""

    def test_init_default(self):
        """Test default initialization."""
        converter = TableConverter()
        assert converter.max_rows == 10000
        assert converter.performance_mode is False

    def test_init_with_custom_max_rows(self):
        """Test initialization with custom max_rows."""
        converter = TableConverter(max_rows=5000)
        assert converter.max_rows == 5000
        assert converter.performance_mode is False

    def test_init_with_performance_mode(self):
        """Test initialization with performance mode."""
        converter = TableConverter(performance_mode=True)
        assert converter.max_rows == 10000
        assert converter.performance_mode is True

    def test_init_with_zero_max_rows(self):
        """Test initialization with zero max_rows raises error."""
        with pytest.raises(ValueError, match="max_rows must be positive"):
            TableConverter(max_rows=0)

    def test_init_with_negative_max_rows(self):
        """Test initialization with negative max_rows raises error."""
        with pytest.raises(ValueError, match="max_rows must be positive"):
            TableConverter(max_rows=-100)

    def test_convert_none_data(self):
        """Test convert with None data."""
        converter = TableConverter()
        with pytest.raises(JsonTableError, match="Data cannot be None"):
            converter.convert(None)

    def test_convert_empty_list(self):
        """Test convert with empty list."""
        converter = TableConverter()
        with pytest.raises(JsonTableError, match="No JSON data to process"):
            converter.convert([])

    def test_convert_empty_dict(self):
        """Test convert with empty dict."""
        converter = TableConverter()
        with pytest.raises(JsonTableError, match="No JSON data to process"):
            converter.convert({})

    def test_convert_invalid_type(self):
        """Test convert with invalid data type."""
        converter = TableConverter()
        with pytest.raises(
            JsonTableError, match="JSON data must be an array or object"
        ):
            converter.convert("invalid string data")

    def test_convert_exceeds_max_rows(self):
        """Test convert with data exceeding max_rows."""
        converter = TableConverter(max_rows=2)
        large_data = [{"id": i} for i in range(5)]

        with pytest.raises(JsonTableError, match="Data size 5 exceeds maximum 2 rows"):
            converter.convert(large_data)

    def test_convert_single_object_simple(self):
        """Test convert with simple single object."""
        converter = TableConverter()
        data = {"name": "Alice", "age": 25}

        result = converter.convert(data)

        expected = [["age", "name"], ["25", "Alice"]]
        assert result == expected

    def test_convert_single_object_with_none_values(self):
        """Test convert with single object containing None values."""
        converter = TableConverter()
        data = {"name": "Alice", "age": None, "city": "Tokyo"}

        result = converter.convert(data)

        expected = [["age", "city", "name"], ["", "Tokyo", "Alice"]]
        assert result == expected

    def test_convert_object_array_simple(self):
        """Test convert with simple object array."""
        converter = TableConverter()
        data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]

        result = converter.convert(data)

        expected = [["age", "name"], ["25", "Alice"], ["30", "Bob"]]
        assert result == expected

    def test_convert_object_array_missing_keys(self):
        """Test convert with object array having missing keys."""
        converter = TableConverter()
        data = [
            {"name": "Alice", "age": 25, "city": "Tokyo"},
            {"name": "Bob", "age": 30},
            {"name": "Charlie", "city": "Osaka"},
        ]

        result = converter.convert(data)

        expected = [
            ["age", "city", "name"],
            ["25", "Tokyo", "Alice"],
            ["30", "", "Bob"],
            ["", "Osaka", "Charlie"],
        ]
        assert result == expected

    def test_convert_object_array_with_non_dict_items(self):
        """Test convert with object array containing non-dict items."""
        converter = TableConverter()
        data = [
            {"name": "Alice", "age": 25},
            "invalid item",
            {"name": "Bob", "age": 30},
        ]

        result = converter.convert(data)

        expected = [["age", "name"], ["25", "Alice"], ["", ""], ["30", "Bob"]]
        assert result == expected

    def test_convert_2d_array_simple(self):
        """Test convert with simple 2D array."""
        converter = TableConverter()
        data = [["Name", "Age", "City"], ["Alice", 25, "Tokyo"], ["Bob", 30, "Osaka"]]

        result = converter.convert(data)

        expected = [
            ["Name", "Age", "City"],
            ["Alice", "25", "Tokyo"],
            ["Bob", "30", "Osaka"],
        ]
        assert result == expected

    def test_convert_2d_array_irregular_lengths(self):
        """Test convert with 2D array having irregular row lengths."""
        converter = TableConverter()
        data = [
            ["Name", "Age", "City", "Country"],
            ["Alice", 25],
            ["Bob", 30, "Osaka"],
            ["Charlie"],
        ]

        result = converter.convert(data)

        expected = [
            ["Name", "Age", "City", "Country"],
            ["Alice", "25", "", ""],
            ["Bob", "30", "Osaka", ""],
            ["Charlie", "", "", ""],
        ]
        assert result == expected

    def test_convert_2d_array_with_non_list_items(self):
        """Test convert with 2D array containing non-list items."""
        converter = TableConverter()
        data = [["Name", "Age"], ["Alice", 25], "single item", ["Bob", 30]]

        result = converter.convert(data)

        expected = [
            ["Name", "Age"],
            ["Alice", "25"],
            ["single item", ""],
            ["Bob", "30"],
        ]
        assert result == expected

    def test_safe_str_none(self):
        """Test _safe_str with None value."""
        converter = TableConverter()
        result = converter._safe_str(None)
        assert result == ""

    def test_safe_str_various_types(self):
        """Test _safe_str with various value types."""
        converter = TableConverter()
        assert converter._safe_str("test") == "test"
        assert converter._safe_str(42) == "42"
        assert converter._safe_str(3.14) == "3.14"
        assert converter._safe_str(True) == "True"
        assert converter._safe_str(False) == "False"

    def test_safe_str_complex_types(self):
        """Test _safe_str with complex types."""
        converter = TableConverter()
        test_dict = {"key": "value"}
        test_list = [1, 2, 3]
        assert converter._safe_str(test_dict) == str(test_dict)
        assert converter._safe_str(test_list) == str(test_list)

    def test_convert_single_object_empty(self):
        """Test _convert_single_object with empty dict."""
        converter = TableConverter()
        result = converter._convert_single_object({})
        assert result == []

    def test_convert_array_empty(self):
        """Test _convert_array with empty list."""
        converter = TableConverter()
        result = converter._convert_array([])
        assert result == []

    def test_convert_object_array_empty(self):
        """Test _convert_object_array with empty list."""
        converter = TableConverter()
        result = converter._convert_object_array([])
        assert result == []

    def test_convert_2d_array_empty(self):
        """Test _convert_2d_array with empty list."""
        converter = TableConverter()
        result = converter._convert_2d_array([])
        assert result == []

    def test_large_data_within_limit(self):
        """Test conversion of large data within limits."""
        converter = TableConverter(max_rows=1000)
        data = [{"id": i, "value": f"item_{i}"} for i in range(500)]

        result = converter.convert(data)

        assert len(result) == 501
        assert result[0] == ["id", "value"]
        assert result[1] == ["0", "item_0"]
        assert result[-1] == ["499", "item_499"]

    def test_performance_mode_flag(self):
        """Test performance mode flag is set correctly."""
        converter_normal = TableConverter(performance_mode=False)
        converter_performance = TableConverter(performance_mode=True)

        assert converter_normal.performance_mode is False
        assert converter_performance.performance_mode is True
