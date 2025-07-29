"""
Test suite for table_builder.py module - TDD implementation

Test-driven development for TableBuilder class
- テーブル生成・構築ロジック
- docutilsノード生成機能
- reStructuredText出力対応
"""

import pytest
from docutils import nodes

from sphinxcontrib.jsontable.directives.table_builder import TableBuilder


class TestTableBuilderInitialization:
    """TableBuilder初期化テスト"""

    def test_init_default_values(self):
        """デフォルト値での初期化テスト"""
        builder = TableBuilder()
        assert builder.max_rows == 10000
        assert builder.encoding == "utf-8"

    def test_init_custom_values(self):
        """カスタム値での初期化テスト"""
        builder = TableBuilder(max_rows=5000, encoding="shift_jis")
        assert builder.max_rows == 5000
        assert builder.encoding == "shift_jis"

    def test_init_invalid_max_rows(self):
        """不正なmax_rows値でのエラーテスト"""
        with pytest.raises(ValueError):
            TableBuilder(max_rows=0)


class TestTableBuilderTableGeneration:
    """テーブル生成機能テスト"""

    @pytest.fixture
    def builder(self):
        return TableBuilder()

    def test_build_table_simple_data(self, builder):
        """シンプルなデータでのテーブル生成テスト"""
        table_data = [["Name", "Age"], ["Alice", "25"], ["Bob", "30"]]

        result = builder.build_table(table_data)
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], nodes.table)

    def test_build_table_empty_data(self, builder):
        """空データでのエラーテスト"""
        with pytest.raises(ValueError):
            builder.build_table([])

    def test_build_table_none_data(self, builder):
        """Noneデータでのエラーテスト"""
        with pytest.raises(ValueError):
            builder.build_table(None)

    def test_build_table_max_rows_exceeded(self, builder):
        """最大行数超過時のエラーテスト"""
        large_data = [["col1"]] * 10001
        with pytest.raises(ValueError):
            builder.build_table(large_data)


class TestTableBuilderDocutilsNodes:
    """docutilsノード生成テスト"""

    @pytest.fixture
    def builder(self):
        return TableBuilder()

    def test_create_table_node_structure(self, builder):
        """テーブルノード構造の検証"""
        table_data = [["Header1", "Header2"], ["Data1", "Data2"]]
        nodes_list = builder.build_table(table_data)

        table_node = nodes_list[0]
        assert isinstance(table_node, nodes.table)

        # テーブル構造の検証
        tgroup = table_node[0]
        assert isinstance(tgroup, nodes.tgroup)
        assert tgroup.get("cols") == 2

    def test_create_thead_node(self, builder):
        """ヘッダーノード生成テスト"""
        table_data = [["Name", "Age"], ["Alice", "25"]]
        nodes_list = builder.build_table(table_data)

        table_node = nodes_list[0]
        tgroup = table_node[0]
        thead = tgroup[2]  # colspec x2, then thead

        assert isinstance(thead, nodes.thead)
        assert len(thead) == 1  # header row

    def test_create_tbody_node(self, builder):
        """ボディノード生成テスト"""
        table_data = [["Name", "Age"], ["Alice", "25"], ["Bob", "30"]]
        nodes_list = builder.build_table(table_data)

        table_node = nodes_list[0]
        tgroup = table_node[0]
        tbody = tgroup[3]  # colspec x2, thead, tbody

        assert isinstance(tbody, nodes.tbody)
        assert len(tbody) == 2  # data rows


class TestTableBuilderRowProcessing:
    """行処理機能テスト"""

    @pytest.fixture
    def builder(self):
        return TableBuilder()

    def test_create_row_node(self, builder):
        """行ノード生成テスト"""
        row_data = ["Alice", "25", "Engineer"]
        row_node = builder._create_table_row(row_data)

        assert isinstance(row_node, nodes.row)
        assert len(row_node) == 3  # 3 entries

        for i, entry in enumerate(row_node):
            assert isinstance(entry, nodes.entry)
            assert entry.astext() == row_data[i]

    def test_create_row_empty_cell(self, builder):
        """空セルを含む行の処理テスト"""
        row_data = ["Alice", "", "Engineer"]
        row_node = builder._create_table_row(row_data)

        assert len(row_node) == 3
        assert row_node[1].astext() == ""

    def test_create_row_none_cell(self, builder):
        """Noneセルの処理テスト"""
        row_data = ["Alice", None, "Engineer"]
        row_node = builder._create_table_row(row_data)

        assert len(row_node) == 3
        assert row_node[1].astext() == ""


class TestTableBuilderColumnSpecification:
    """列仕様生成テスト"""

    @pytest.fixture
    def builder(self):
        return TableBuilder()

    def test_create_colspec_nodes(self, builder):
        """列仕様ノード生成テスト"""
        col_count = 3
        colspecs = builder._create_colspec_nodes(col_count)

        assert len(colspecs) == 3
        for colspec in colspecs:
            assert isinstance(colspec, nodes.colspec)
            assert colspec.get("colwidth") == 1

    def test_create_colspec_zero_columns(self, builder):
        """0列での列仕様エラーテスト"""
        with pytest.raises(ValueError):
            builder._create_colspec_nodes(0)


class TestTableBuilderIntegration:
    """統合テスト"""

    @pytest.fixture
    def builder(self):
        return TableBuilder()

    def test_complex_table_build(self, builder):
        """複雑なテーブルの完全な構築テスト"""
        table_data = [
            ["Product", "Price", "Category", "Stock"],
            ["Laptop", "$999", "Electronics", "5"],
            ["Book", "$19.99", "Education", "50"],
            ["Chair", "$149", "Furniture", "10"],
        ]

        nodes_list = builder.build_table(table_data)
        table_node = nodes_list[0]

        # 完全な構造検証
        assert isinstance(table_node, nodes.table)
        tgroup = table_node[0]
        assert tgroup.get("cols") == 4

        # ヘッダー検証
        thead = tgroup[4]  # colspec x4, then thead
        header_row = thead[0]
        assert header_row[0].astext() == "Product"

        # データ行検証
        tbody = tgroup[5]  # colspec x4, thead, tbody
        assert len(tbody) == 3  # 3 data rows
        assert tbody[0][0].astext() == "Laptop"

    def test_single_column_table(self, builder):
        """単一列テーブルテスト"""
        table_data = [["Items"], ["Apple"], ["Banana"], ["Cherry"]]

        nodes_list = builder.build_table(table_data)
        table_node = nodes_list[0]
        tgroup = table_node[0]

        assert tgroup.get("cols") == 1
