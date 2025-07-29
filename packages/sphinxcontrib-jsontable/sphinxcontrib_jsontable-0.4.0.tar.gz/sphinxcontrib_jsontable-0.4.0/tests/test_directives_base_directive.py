"""
Test suite for base_directive.py module - TDD implementation

Test-driven development for BaseDirective abstract class
- ディレクティブ基底機能
- オプション解析統合
- エラーハンドリング共通化
- プロセッサー統合管理
"""

from unittest.mock import Mock, patch

import pytest
from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective

from sphinxcontrib.jsontable.directives.base_directive import BaseDirective


class TestBaseDirectiveAbstractClass:
    """BaseDirective抽象クラステスト"""

    def test_base_directive_is_abstract(self):
        """BaseDirectiveが抽象クラスであることを確認"""
        with pytest.raises(TypeError):
            BaseDirective()

    def test_base_directive_inherits_sphinx_directive(self):
        """SphinxDirectiveを継承していることを確認"""
        assert issubclass(BaseDirective, SphinxDirective)

    def test_base_option_spec_exists(self):
        """基本オプション仕様が定義されていることを確認"""
        assert hasattr(BaseDirective, "base_option_spec")
        assert isinstance(BaseDirective.base_option_spec, dict)
        assert "header" in BaseDirective.base_option_spec
        assert "limit" in BaseDirective.base_option_spec


class TestBaseDirectiveOptionSpecification:
    """オプション仕様テスト"""

    def test_base_option_spec_header_flag(self):
        """headerオプションがflag型であることを確認"""
        assert BaseDirective.base_option_spec["header"] == directives.flag

    def test_base_option_spec_limit_int(self):
        """limitオプションがnonnegative_int型であることを確認"""
        assert BaseDirective.base_option_spec["limit"] == directives.nonnegative_int

    def test_option_spec_merging(self):
        """オプション仕様のマージ機能テスト"""

        # 具象クラスでのオプション拡張をテスト
        class ConcreteDirective(BaseDirective):
            option_spec = {
                **BaseDirective.base_option_spec,
                "encoding": directives.unchanged,
                "sheet": directives.unchanged,
            }

            def _initialize_processors(self):
                pass

            def _load_data(self):
                return []

        expected_options = {"header", "limit", "encoding", "sheet"}
        assert set(ConcreteDirective.option_spec.keys()) == expected_options


class TestBaseDirectiveAbstractMethods:
    """抽象メソッドテスト"""

    def test_initialize_processors_abstract(self):
        """_initialize_processorsが抽象メソッドであることを確認"""

        class IncompleteDirective(BaseDirective):
            def _load_data(self):
                return []

        with pytest.raises(TypeError):
            IncompleteDirective()

    def test_load_data_abstract(self):
        """_load_dataが抽象メソッドであることを確認"""

        class IncompleteDirective(BaseDirective):
            def _initialize_processors(self):
                pass

        with pytest.raises(TypeError):
            IncompleteDirective()

    def test_concrete_implementation_works(self):
        """完全な実装クラスが正常に動作することを確認"""

        class ConcreteDirective(BaseDirective):
            option_spec = BaseDirective.base_option_spec

            def _initialize_processors(self):
                self.table_builder = Mock()

            def _load_data(self):
                return [["Name", "Age"], ["Alice", "25"]]

        # モックされたSphinx環境で初期化テスト
        with patch("sphinx.util.docutils.SphinxDirective.__init__"):
            directive = ConcreteDirective.__new__(ConcreteDirective)
            # envプロパティを直接設定ではなく、__dict__で設定
            directive.__dict__["env"] = Mock()
            directive.arguments = []
            directive.content = []
            directive.options = {}
            directive._initialize_processors()

            assert hasattr(directive, "table_builder")


class TestBaseDirectiveInitialization:
    """初期化プロセステスト"""

    @pytest.fixture
    def concrete_directive(self):
        """テスト用具象ディレクティブ"""

        class ConcreteDirective(BaseDirective):
            option_spec = BaseDirective.base_option_spec

            def _initialize_processors(self):
                self.json_processor = Mock()
                self.table_builder = Mock()

            def _load_data(self):
                return [["test", "data"]]

        return ConcreteDirective

    def test_initialization_calls_abstract_methods(self, concrete_directive):
        """初期化時に抽象メソッドが呼ばれることを確認"""
        with patch("sphinx.util.docutils.SphinxDirective.__init__"):
            directive = concrete_directive.__new__(concrete_directive)
            directive.__dict__["env"] = Mock()
            directive.arguments = []
            directive.content = []
            directive.options = {}

            # _initialize_processorsの呼び出しをモック
            with patch.object(directive, "_initialize_processors") as mock_init:
                directive.__init__()
                mock_init.assert_called_once()


class TestBaseDirectiveRunMethod:
    """runメソッドテスト - テンプレートメソッドパターン"""

    @pytest.fixture
    def mock_directive(self):
        """モック済みディレクティブ"""

        class MockDirective(BaseDirective):
            option_spec = BaseDirective.base_option_spec

            def _initialize_processors(self):
                self.table_builder = Mock()
                self.table_builder.build_table.return_value = [nodes.table()]

            def _load_data(self):
                return [["Name", "Age"], ["Alice", "25"]]

        with patch("sphinx.util.docutils.SphinxDirective.__init__"):
            directive = MockDirective.__new__(MockDirective)
            directive.__dict__["env"] = Mock()
            directive.arguments = []
            directive.content = []
            directive.options = {}
            directive._initialize_processors()

            return directive

    def test_run_method_basic_flow(self, mock_directive):
        """runメソッドの基本フローテスト"""
        result = mock_directive.run()

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], nodes.table)

    def test_run_method_calls_load_data(self, mock_directive):
        """runメソッドが_load_dataを呼ぶことを確認"""
        with patch.object(
            mock_directive, "_load_data", return_value=[["test"]]
        ) as mock_load:
            mock_directive.run()
            mock_load.assert_called_once()

    def test_run_method_calls_table_builder(self, mock_directive):
        """runメソッドがtable_builderを呼ぶことを確認"""
        mock_directive.run()
        mock_directive.table_builder.build_table.assert_called_once()


class TestBaseDirectiveErrorHandling:
    """エラーハンドリングテスト"""

    @pytest.fixture
    def error_directive(self):
        """エラー発生用ディレクティブ"""

        class ErrorDirective(BaseDirective):
            option_spec = BaseDirective.base_option_spec

            def _initialize_processors(self):
                self.table_builder = Mock()

            def _load_data(self):
                raise FileNotFoundError("Test file not found")

        with patch("sphinx.util.docutils.SphinxDirective.__init__"):
            directive = ErrorDirective.__new__(ErrorDirective)
            directive.__dict__["env"] = Mock()
            directive.arguments = []
            directive.content = []
            directive.options = {}
            directive._initialize_processors()

            return directive

    def test_error_node_creation(self, error_directive):
        """エラーノード作成機能テスト"""
        error_message = "Test error message"
        error_node = error_directive._create_error_node(error_message)

        assert isinstance(error_node, nodes.error)
        assert error_message in error_node.astext()

    def test_run_method_handles_file_not_found_error(self, error_directive):
        """FileNotFoundError処理テスト"""
        with patch.object(error_directive, "_create_error_node") as mock_error:
            mock_error.return_value = nodes.error("test error")

            result = error_directive.run()

            assert len(result) == 1
            mock_error.assert_called_once()

    def test_run_method_handles_json_table_error(self):
        """JsonTableError処理テスト"""
        from sphinxcontrib.jsontable.directives.validators import JsonTableError

        class JsonErrorDirective(BaseDirective):
            option_spec = BaseDirective.base_option_spec

            def _initialize_processors(self):
                self.table_builder = Mock()

            def _load_data(self):
                raise JsonTableError("Test JSON error")

        with patch("sphinx.util.docutils.SphinxDirective.__init__"):
            directive = JsonErrorDirective.__new__(JsonErrorDirective)
            directive.__dict__["env"] = Mock()
            directive.arguments = []
            directive.content = []
            directive.options = {}
            directive._initialize_processors()

            with patch.object(directive, "_create_error_node") as mock_error:
                mock_error.return_value = nodes.error("json error")

                result = directive.run()

                assert len(result) == 1
                mock_error.assert_called_once()


class TestBaseDirectiveOptionProcessing:
    """オプション処理テスト"""

    @pytest.fixture
    def option_directive(self):
        """オプション処理テスト用ディレクティブ"""

        class OptionDirective(BaseDirective):
            option_spec = BaseDirective.base_option_spec

            def _initialize_processors(self):
                self.table_builder = Mock()
                self.table_builder.build_table.return_value = [nodes.table()]

            def _load_data(self):
                return [["Name", "Age"], ["Alice", "25"]]

        return OptionDirective

    def test_header_option_processing(self, option_directive):
        """headerオプション処理テスト"""
        with patch("sphinx.util.docutils.SphinxDirective.__init__"):
            directive = option_directive.__new__(option_directive)
            directive.__dict__["env"] = Mock()
            directive.arguments = []
            directive.content = []
            directive.options = {"header": True}
            directive._initialize_processors()

            directive.run()

            # headerオプションが正しく処理されることを確認
            directive.table_builder.build_table.assert_called_once()
            call_args = directive.table_builder.build_table.call_args[0]
            assert len(call_args) == 1  # table_data引数

    def test_limit_option_processing(self, option_directive):
        """limitオプション処理テスト"""
        with patch("sphinx.util.docutils.SphinxDirective.__init__"):
            directive = option_directive.__new__(option_directive)
            directive.__dict__["env"] = Mock()
            directive.arguments = []
            directive.content = []
            directive.options = {"limit": 100}
            directive._initialize_processors()

            # limitオプションが設定されることを確認
            assert directive.options.get("limit") == 100


class TestBaseDirectiveIntegration:
    """統合テスト"""

    def test_complete_directive_flow(self):
        """完全なディレクティブフローの統合テスト"""

        class CompleteDirective(BaseDirective):
            option_spec = {
                **BaseDirective.base_option_spec,
                "encoding": directives.unchanged,
            }

            def _initialize_processors(self):
                self.json_processor = Mock()
                self.table_builder = Mock()
                self.table_builder.build_table.return_value = [nodes.table()]

            def _load_data(self):
                return [
                    ["Product", "Price", "Stock"],
                    ["Laptop", "$999", "5"],
                    ["Mouse", "$25", "50"],
                ]

        with patch("sphinx.util.docutils.SphinxDirective.__init__"):
            directive = CompleteDirective.__new__(CompleteDirective)
            directive.__dict__["env"] = Mock()
            directive.arguments = ["test.json"]
            directive.content = []
            directive.options = {"header": True, "encoding": "utf-8"}
            directive._initialize_processors()

            result = directive.run()

            # 完全な処理フローの検証
            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], nodes.table)

            # プロセッサーが適切に呼ばれたことを確認
            directive.table_builder.build_table.assert_called_once()

    def test_processor_integration_consistency(self):
        """プロセッサー統合の一貫性テスト"""

        class ProcessorDirective(BaseDirective):
            option_spec = BaseDirective.base_option_spec

            def _initialize_processors(self):
                # 既存プロセッサーとの統合確認
                from sphinxcontrib.jsontable.directives.table_builder import (
                    TableBuilder,
                )

                self.table_builder = TableBuilder()

            def _load_data(self):
                return [["test", "data"], ["value1", "value2"]]

        with patch("sphinx.util.docutils.SphinxDirective.__init__"):
            directive = ProcessorDirective.__new__(ProcessorDirective)
            directive.__dict__["env"] = Mock()
            directive.arguments = []
            directive.content = []
            directive.options = {}
            directive._initialize_processors()

            # 実際のTableBuilderとの統合確認
            assert hasattr(directive, "table_builder")
            assert hasattr(directive.table_builder, "build_table")

            result = directive.run()
            assert isinstance(result, list)
            assert len(result) == 1
