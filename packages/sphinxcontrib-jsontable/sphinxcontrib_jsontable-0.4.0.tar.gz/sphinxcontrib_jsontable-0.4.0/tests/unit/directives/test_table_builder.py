"""Table Builder Tests - Phase 3.2 Coverage Boost.

Tests for table_builder.py to boost coverage from 15.74% to 35%+.
"""

from unittest.mock import patch

import pytest
from docutils import nodes

from sphinxcontrib.jsontable.directives.table_builder import TableBuilder


class TestTableBuilder:
    """Test suite for TableBuilder."""

    def test_init_default(self):
        """Test default initialization."""
        builder = TableBuilder()
        assert builder.max_rows == 10000
        assert builder.encoding == "utf-8"

    def test_init_with_custom_params(self):
        """Test initialization with custom parameters."""
        builder = TableBuilder(max_rows=5000, encoding="shift_jis")
        assert builder.max_rows == 5000
        assert builder.encoding == "shift_jis"

    def test_init_with_zero_max_rows(self):
        """Test initialization with zero max_rows raises error."""
        with pytest.raises(ValueError, match="max_rows must be positive"):
            TableBuilder(max_rows=0)

    def test_init_with_negative_max_rows(self):
        """Test initialization with negative max_rows raises error."""
        with pytest.raises(ValueError, match="max_rows must be positive"):
            TableBuilder(max_rows=-100)

    def test_build_table_none_data(self):
        """Test build_table with None data."""
        builder = TableBuilder()
        with pytest.raises(ValueError, match="table_data cannot be None"):
            builder.build_table(None)

    def test_build_table_empty_data(self):
        """Test build_table with empty data."""
        builder = TableBuilder()
        with pytest.raises(ValueError, match="table_data cannot be empty"):
            builder.build_table([])

    def test_build_table_exceeds_max_rows(self):
        """Test build_table with data exceeding max_rows."""
        builder = TableBuilder(max_rows=2)
        large_data = [["col1"], ["row1"], ["row2"], ["row3"]]

        with pytest.raises(ValueError, match="Table exceeds maximum rows limit"):
            builder.build_table(large_data)

    def test_build_table_simple(self):
        """Test build_table with simple data."""
        builder = TableBuilder()
        data = [["Name", "Age"], ["Alice", "25"], ["Bob", "30"]]

        result = builder.build_table(data)

        assert len(result) == 1
        assert isinstance(result[0], nodes.table)

        # Check table structure
        table = result[0]
        assert isinstance(table[0], nodes.tgroup)
        assert table[0].attributes["cols"] == 2

    def test_build_table_single_row(self):
        """Test build_table with single row."""
        builder = TableBuilder()
        data = [["Header1", "Header2", "Header3"]]

        result = builder.build_table(data)

        assert len(result) == 1
        table = result[0]
        assert table[0].attributes["cols"] == 3

    def test_build_table_with_none_cells(self):
        """Test build_table with None cell values."""
        builder = TableBuilder()
        data = [["Name", "Age", "City"], ["Alice", None, "Tokyo"], [None, "30", None]]

        result = builder.build_table(data)

        assert len(result) == 1
        table = result[0]
        assert isinstance(table, nodes.table)

    def test_build_table_irregular_rows(self):
        """Test build_table with irregular row lengths."""
        builder = TableBuilder()
        data = [
            ["Name", "Age", "City", "Country"],
            ["Alice", "25"],
            ["Bob", "30", "Osaka"],
            ["Charlie"],
        ]

        result = builder.build_table(data)

        assert len(result) == 1
        table = result[0]
        # Should use maximum column count
        assert table[0].attributes["cols"] == 4

    def test_create_empty_table(self):
        """Test _create_empty_table method."""
        builder = TableBuilder()
        table = builder._create_empty_table()

        assert isinstance(table, nodes.table)
        assert table[0].attributes["cols"] == 1

    def test_create_table_structure(self):
        """Test _create_table_structure method."""
        builder = TableBuilder()
        table = builder._create_table_structure(3)

        assert isinstance(table, nodes.table)
        assert table[0].attributes["cols"] == 3

        # Check colspec nodes
        tgroup = table[0]
        colspecs = [node for node in tgroup if isinstance(node, nodes.colspec)]
        assert len(colspecs) == 3

    def test_create_colspec_nodes(self):
        """Test _create_colspec_nodes method."""
        builder = TableBuilder()
        colspecs = builder._create_colspec_nodes(4)

        assert len(colspecs) == 4
        for colspec in colspecs:
            assert isinstance(colspec, nodes.colspec)
            assert colspec.attributes["colwidth"] == 1

    def test_create_colspec_nodes_zero_count(self):
        """Test _create_colspec_nodes with zero count."""
        builder = TableBuilder()
        with pytest.raises(ValueError, match="col_count must be positive"):
            builder._create_colspec_nodes(0)

    def test_create_colspec_nodes_negative_count(self):
        """Test _create_colspec_nodes with negative count."""
        builder = TableBuilder()
        with pytest.raises(ValueError, match="col_count must be positive"):
            builder._create_colspec_nodes(-1)

    def test_add_header(self):
        """Test _add_header method."""
        builder = TableBuilder()
        table = builder._create_table_structure(2)
        header_data = ["Column1", "Column2"]

        builder._add_header(table, header_data)

        tgroup = table[0]
        thead = None
        for node in tgroup:
            if isinstance(node, nodes.thead):
                thead = node
                break

        assert thead is not None
        assert len(thead) == 1  # One header row
        assert isinstance(thead[0], nodes.row)

    def test_add_body(self):
        """Test _add_body method."""
        builder = TableBuilder()
        table = builder._create_table_structure(2)
        body_data = [["Alice", "25"], ["Bob", "30"]]

        builder._add_body(table, body_data, 2)

        tgroup = table[0]
        tbody = None
        for node in tgroup:
            if isinstance(node, nodes.tbody):
                tbody = node
                break

        assert tbody is not None
        assert len(tbody) == 2  # Two body rows

    def test_add_body_with_padding(self):
        """Test _add_body method with row padding."""
        builder = TableBuilder()
        table = builder._create_table_structure(3)
        body_data = [["Alice", "25"], ["Bob"]]  # Second row is shorter

        builder._add_body(table, body_data, 3)

        tgroup = table[0]
        tbody = None
        for node in tgroup:
            if isinstance(node, nodes.tbody):
                tbody = node
                break

        assert tbody is not None
        assert len(tbody) == 2

    def test_create_table_row_simple(self):
        """Test _create_table_row method with simple data."""
        builder = TableBuilder()
        row_data = ["Alice", "25", "Engineer"]

        row = builder._create_table_row(row_data)

        assert isinstance(row, nodes.row)
        assert len(row) == 3  # Three cells

        for entry in row:
            assert isinstance(entry, nodes.entry)
            assert len(entry) == 1  # One paragraph per entry
            assert isinstance(entry[0], nodes.paragraph)

    def test_create_table_row_with_none(self):
        """Test _create_table_row method with None values."""
        builder = TableBuilder()
        row_data = ["Alice", None, "Engineer"]

        row = builder._create_table_row(row_data)

        assert isinstance(row, nodes.row)
        assert len(row) == 3

        # Check that None is converted to empty string
        middle_entry = row[1]
        paragraph = middle_entry[0]
        assert paragraph.astext() == ""

    def test_create_table_row_with_numbers(self):
        """Test _create_table_row method with number values."""
        builder = TableBuilder()
        row_data = ["Alice", 25, 95.5]

        row = builder._create_table_row(row_data)

        assert isinstance(row, nodes.row)
        assert len(row) == 3

        # Check that numbers are converted to strings
        age_entry = row[1]
        score_entry = row[2]
        assert age_entry[0].astext() == "25"
        assert score_entry[0].astext() == "95.5"

    def test_create_table_row_encoding_error(self):
        """Test _create_table_row method with encoding issues."""
        builder = TableBuilder()

        # Mock a problematic object that raises UnicodeError
        class ProblematicObject:
            def __str__(self):
                raise UnicodeDecodeError("utf-8", b"", 0, 1, "invalid start byte")

        problematic_obj = ProblematicObject()
        row_data = ["Alice", problematic_obj, "Engineer"]

        with patch(
            "sphinxcontrib.jsontable.directives.table_builder.logger"
        ) as mock_logger:
            row = builder._create_table_row(row_data)

            assert isinstance(row, nodes.row)
            assert len(row) == 3
            # Should log a warning about encoding issue
            mock_logger.warning.assert_called()

    def test_build_table_internal_empty(self):
        """Test _build_table_internal with empty data."""
        builder = TableBuilder()
        table = builder._build_table_internal([])

        assert isinstance(table, nodes.table)
        assert table[0].attributes["cols"] == 1  # Empty table has 1 column

    def test_build_table_internal_with_header(self):
        """Test _build_table_internal with header."""
        builder = TableBuilder()
        data = [["Name", "Age"], ["Alice", "25"], ["Bob", "30"]]

        table = builder._build_table_internal(data, has_header=True)

        assert isinstance(table, nodes.table)
        tgroup = table[0]

        # Should have both thead and tbody
        has_thead = any(isinstance(node, nodes.thead) for node in tgroup)
        has_tbody = any(isinstance(node, nodes.tbody) for node in tgroup)

        assert has_thead
        assert has_tbody

    def test_build_table_internal_without_header(self):
        """Test _build_table_internal without header."""
        builder = TableBuilder()
        data = [["Alice", "25"], ["Bob", "30"]]

        table = builder._build_table_internal(data, has_header=False)

        assert isinstance(table, nodes.table)
        tgroup = table[0]

        # Should have tbody but no thead
        has_thead = any(isinstance(node, nodes.thead) for node in tgroup)
        has_tbody = any(isinstance(node, nodes.tbody) for node in tgroup)

        assert not has_thead
        assert has_tbody

    def test_logging_during_build(self):
        """Test that table building generates log messages."""
        builder = TableBuilder()
        data = [["Name", "Age"], ["Alice", "25"]]

        with patch(
            "sphinxcontrib.jsontable.directives.table_builder.logger"
        ) as mock_logger:
            builder.build_table(data)

            # Should log debug and info messages
            assert mock_logger.debug.called
            assert mock_logger.info.called

    def test_constants_values(self):
        """Test that constants have expected values."""
        from sphinxcontrib.jsontable.directives.table_builder import (
            DEFAULT_ENCODING,
            DEFAULT_MAX_ROWS,
        )

        assert DEFAULT_MAX_ROWS == 10000
        assert DEFAULT_ENCODING == "utf-8"

    def test_large_table_within_limit(self):
        """Test building large table within limits."""
        builder = TableBuilder(max_rows=1000)
        data = [["ID", "Value"]] + [[str(i), f"value_{i}"] for i in range(500)]

        result = builder.build_table(data)

        assert len(result) == 1
        table = result[0]
        assert isinstance(table, nodes.table)

    def test_empty_cells_handling(self):
        """Test handling of empty string cells."""
        builder = TableBuilder()
        data = [
            ["Name", "Age", "Notes"],
            ["Alice", "25", ""],
            ["", "30", "Some notes"],
            ["Charlie", "", ""],
        ]

        result = builder.build_table(data)

        assert len(result) == 1
        table = result[0]
        assert isinstance(table, nodes.table)

    def test_mixed_data_types_in_cells(self):
        """Test handling of mixed data types in cells."""
        builder = TableBuilder()
        data = [
            ["Name", "Age", "Active", "Score"],
            ["Alice", 25, True, 95.5],
            ["Bob", "30", False, "N/A"],
            [123, None, "Yes", 87],
        ]

        result = builder.build_table(data)

        assert len(result) == 1
        table = result[0]
        assert isinstance(table, nodes.table)
