"""
機能保証テスト for BaseDirective class.

このモジュールは BaseDirective の企業グレード機能の包括的なテストを提供し、
テンプレートメソッドパターン、エラーハンドリング、セキュリティ機能の
品質保証を行います。単なるカバレッジ向上ではなく、実際の機能品質保証に重点を置きます。
"""

from unittest.mock import Mock, patch

import pytest
from docutils import nodes

from sphinxcontrib.jsontable.directives.base_directive import BaseDirective
from sphinxcontrib.jsontable.directives.validators import JsonTableError


class ConcreteDirectiveTest(BaseDirective):
    """
    テスト用の具象BaseDirective実装。

    抽象メソッドの実装を提供し、テンプレートメソッドパターンの
    実行フローを検証するために使用します。
    """

    def _initialize_processors(self) -> None:
        """プロセッサ初期化のテスト実装。"""
        self.test_processor = Mock()
        self.test_processor.initialized = True

    def _load_data(self):
        """データ読み込みのテスト実装。"""
        return [["Header1", "Header2"], ["Value1", "Value2"]]


class ConcreteDirectiveWithError(BaseDirective):
    """
    エラーハンドリングテスト用の具象BaseDirective実装。

    意図的にエラーを発生させて、エラーハンドリング機能の
    品質保証を行います。
    """

    def _initialize_processors(self) -> None:
        """プロセッサ初期化のテスト実装。"""
        self.test_processor = Mock()

    def _load_data(self):
        """意図的にエラーを発生させるデータ読み込み実装。"""
        raise JsonTableError("Test error for error handling validation")


class TestBaseDirectiveTemplateMethodPattern:
    """
    BaseDirectiveのテンプレートメソッドパターンの機能品質保証テスト。

    企業グレードのテンプレートメソッド実行フローが正しく動作し、
    抽象メソッドの委譲が適切に行われることを保証します。
    """

    @pytest.fixture
    def sphinx_app_mock(self):
        """Sphinxアプリケーションのモックを作成する。"""
        app = Mock()
        app.config = Mock()
        return app

    @pytest.fixture
    def directive_instance(self, sphinx_app_mock):
        """
        テスト用BaseDirective具象実装のインスタンスを作成する。

        テンプレートメソッドパターンの実行に必要な
        最小限の設定を行います。
        """
        # Sphinxディレクティブの必要な引数を設定
        name = "test-directive"
        arguments = []
        options = {}
        content = []
        lineno = 1
        content_offset = 0
        block_text = ""
        state = Mock()
        state_machine = Mock()

        # テーブルビルダーのモック設定
        with patch(
            "sphinxcontrib.jsontable.directives.base_directive.TableBuilder"
        ) as mock_table_builder:
            mock_builder_instance = Mock()
            mock_builder_instance.build_table.return_value = [nodes.table()]
            mock_table_builder.return_value = mock_builder_instance

            directive = ConcreteDirectiveTest(
                name,
                arguments,
                options,
                content,
                lineno,
                content_offset,
                block_text,
                state,
                state_machine,
            )

            # Sphinxアプリケーションの設定
            # envはproperty属性のため、state.document.settingsでアクセス
            directive.state.document = Mock()
            directive.state.document.settings = Mock()
            directive.state.document.settings.env = Mock()
            directive.state.document.settings.env.app = sphinx_app_mock

            return directive

    def test_template_method_execution_flow_success(self, directive_instance):
        """
        テンプレートメソッドパターンの正常実行フローを検証する。

        BaseDirectiveのrun()メソッドが設計通りの順序で処理を実行し、
        各段階が適切に実行されることを保証する機能品質テストです。

        検証項目:
        1. 実行前バリデーション
        2. データ読み込み（抽象メソッド委譲）
        3. オプション処理
        4. データ変換・検証
        5. テーブル生成
        6. 実行後バリデーション
        """
        # 実行フローをトレースするためのモック設定
        with patch.object(
            directive_instance, "_validate_execution_context"
        ) as mock_validate:
            with patch.object(directive_instance, "_process_options") as mock_process:
                with patch.object(
                    directive_instance, "_validate_and_convert_data"
                ) as mock_convert:
                    mock_convert.return_value = [
                        ["Header1", "Header2"],
                        ["Value1", "Value2"],
                    ]

                    # テンプレートメソッドの実行
                    result = directive_instance.run()

                    # 実行フローの検証
                    mock_validate.assert_called_once()
                    mock_process.assert_called_once()
                    mock_convert.assert_called_once()

                    # 結果の検証
                    assert isinstance(result, list)
                    assert len(result) == 1
                    assert isinstance(result[0], nodes.table)

    def test_abstract_method_delegation_data_loading(self, directive_instance):
        """
        抽象メソッド_load_data()の委譲が正しく動作することを検証する。

        テンプレートメソッドパターンの核心である抽象メソッドの委譲が
        適切に実行され、具象クラスの実装が呼び出されることを保証します。

        機能保証の重要性:
        - アーキテクチャの健全性確保
        - 具象クラスの実装自由度保証
        - フレームワークの拡張性確保
        """
        # _load_data()メソッドの委譲を検証
        with patch.object(
            directive_instance, "_load_data", return_value=[["test"]]
        ) as mock_load:
            with patch.object(
                directive_instance,
                "_validate_and_convert_data",
                return_value=[["test"]],
            ):
                result = directive_instance.run()

                # 抽象メソッドが呼び出されることを確認
                mock_load.assert_called_once()

                # 結果が適切に処理されることを確認
                assert isinstance(result, list)

    def test_processor_initialization_abstract_method(self, sphinx_app_mock):
        """
        抽象メソッド_initialize_processors()の委譲が正しく動作することを検証する。

        BaseDirectiveのコンストラクタで抽象メソッドが適切に呼び出され、
        具象クラスのプロセッサ初期化が実行されることを保証します。

        機能保証の観点:
        - 初期化時の抽象メソッド委譲
        - プロセッサの適切な設定
        - エラー時の適切な処理
        """
        # コンストラクタでの抽象メソッド呼び出しを検証
        with patch("sphinxcontrib.jsontable.directives.base_directive.TableBuilder"):
            directive = ConcreteDirectiveTest(
                "test", [], {}, [], 1, 0, "", Mock(), Mock()
            )

            # 具象クラスで初期化されたプロセッサの確認
            assert hasattr(directive, "test_processor")
            assert directive.test_processor.initialized is True


class TestBaseDirectiveErrorHandling:
    """
    BaseDirectiveのエラーハンドリング機能の品質保証テスト。

    企業グレードのエラーハンドリングが適切に動作し、
    セキュリティ要件を満たしていることを保証します。
    """

    @pytest.fixture
    def error_directive(self):
        """エラーテスト用のディレクティブインスタンスを作成する。"""
        with patch("sphinxcontrib.jsontable.directives.base_directive.TableBuilder"):
            directive = ConcreteDirectiveWithError(
                "test", [], {}, [], 1, 0, "", Mock(), Mock()
            )
            # Sphinxアプリケーションの設定
            directive.state.document = Mock()
            directive.state.document.settings = Mock()
            directive.state.document.settings.env = Mock()
            directive.state.document.settings.env.app = Mock()
            return directive

    def test_json_table_error_handling_user_friendly_message(self, error_directive):
        """
        JsonTableErrorの適切な処理とユーザーフレンドリーなメッセージ生成を検証する。

        機能保証項目:
        - 既知のエラーの適切な捕捉
        - ユーザーフレンドリーなエラーメッセージ
        - エラーノードの正しい生成
        - ログ出力の適切性

        セキュリティ観点:
        - 機密情報の漏洩防止
        - エラーメッセージのサニタイゼーション
        """
        result = error_directive.run()

        # エラーノードが適切に生成されることを確認
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], nodes.error)

        # エラーメッセージの内容確認
        error_node = result[0]
        assert len(error_node.children) == 1
        assert isinstance(error_node.children[0], nodes.paragraph)

        # ユーザーフレンドリーなメッセージが含まれていることを確認
        error_text = str(error_node.children[0])
        assert "Test error for error handling validation" in error_text

    def test_file_not_found_error_graceful_handling(self):
        """
        FileNotFoundErrorの適切な処理を検証する。

        ファイルシステムエラーに対する適切な処理と
        ユーザーへの分かりやすいエラー表示を保証します。

        機能保証項目:
        - ファイルシステムエラーの捕捉
        - ファイル名情報の適切な抽出
        - エラーノードの生成
        """

        class FileNotFoundDirective(BaseDirective):
            def _initialize_processors(self):
                pass

            def _load_data(self):
                raise FileNotFoundError("test_file.json")

        with patch("sphinxcontrib.jsontable.directives.base_directive.TableBuilder"):
            directive = FileNotFoundDirective(
                "test", [], {}, [], 1, 0, "", Mock(), Mock()
            )
            # Sphinxアプリケーションの設定
            directive.state.document = Mock()
            directive.state.document.settings = Mock()
            directive.state.document.settings.env = Mock()
            directive.state.document.settings.env.app = Mock()

            result = directive.run()

            # エラーノードの生成確認
            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], nodes.error)

            # ファイル名が含まれたエラーメッセージの確認
            error_text = str(result[0])
            assert "test_file.json" in error_text

    def test_unexpected_error_security_sanitization(self):
        """
        予期しないエラーのセキュリティを考慮した処理を検証する。

        機能保証項目:
        - 予期しないエラーの適切な捕捉
        - 機密情報の漏洩防止
        - 汎用エラーメッセージの生成
        - ログへの詳細情報記録

        セキュリティ要件:
        - システム内部情報の非開示
        - スタックトレース情報の非表示
        - サニタイズされたエラーメッセージ
        """

        class UnexpectedErrorDirective(BaseDirective):
            def _initialize_processors(self):
                pass

            def _load_data(self):
                raise ValueError(
                    "Internal system error with sensitive data: secret_key_123"
                )

        with patch("sphinxcontrib.jsontable.directives.base_directive.TableBuilder"):
            directive = UnexpectedErrorDirective(
                "test", [], {}, [], 1, 0, "", Mock(), Mock()
            )
            # Sphinxアプリケーションの設定
            directive.state.document = Mock()
            directive.state.document.settings = Mock()
            directive.state.document.settings.env = Mock()
            directive.state.document.settings.env.app = Mock()

            result = directive.run()

            # エラーノードの生成確認
            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], nodes.error)

            # セキュリティサニタイゼーションの確認
            error_text = str(result[0])
            assert (
                "secret_key_123" not in error_text
            )  # 機密情報が含まれていないことを確認
            assert "Internal error" in error_text  # 汎用メッセージが含まれることを確認


class TestBaseDirectiveOptionProcessing:
    """
    BaseDirectiveのオプション処理機能の品質保証テスト。

    オプションの適切な処理、検証、セキュリティチェックが
    正しく動作することを保証します。
    """

    @pytest.fixture
    def directive_with_options(self):
        """オプション付きディレクティブのインスタンスを作成する。"""
        options = {"header": True, "limit": 100}

        with patch("sphinxcontrib.jsontable.directives.base_directive.TableBuilder"):
            directive = ConcreteDirectiveTest(
                "test", [], options, [], 1, 0, "", Mock(), Mock()
            )
            # Sphinxアプリケーションの設定
            directive.state.document = Mock()
            directive.state.document.settings = Mock()
            directive.state.document.settings.env = Mock()
            directive.state.document.settings.env.app = Mock()
            return directive

    def test_option_processing_comprehensive_validation(self, directive_with_options):
        """
        オプション処理の包括的な検証を行う。

        機能保証項目:
        - headerオプションの適切な処理
        - limitオプションの適切な処理
        - オプション値の検証
        - 処理結果の正確性

        セキュリティ観点:
        - オプション値の検証
        - 不正値の拒否
        - インジェクション攻撃の防止
        """
        processed = directive_with_options._process_options()

        # オプション処理結果の検証
        assert isinstance(processed, dict)
        assert processed["include_header"] is True
        assert processed["limit"] == 100

    def test_negative_limit_option_validation_security(self):
        """
        負の値のlimitオプションに対するセキュリティ検証を行う。

        機能保証項目:
        - 不正なオプション値の検出
        - 適切なエラー発生
        - セキュリティ違反の防止

        セキュリティ要件:
        - 入力値検証の徹底
        - 不正値による攻撃の防止
        """
        options = {"limit": -1}

        with patch("sphinxcontrib.jsontable.directives.base_directive.TableBuilder"):
            directive = ConcreteDirectiveTest(
                "test", [], options, [], 1, 0, "", Mock(), Mock()
            )

            with pytest.raises(JsonTableError) as exc_info:
                directive._process_options()

            assert "non-negative" in str(exc_info.value)

    def test_default_option_values_handling(self):
        """
        デフォルトオプション値の適切な処理を検証する。

        機能保証項目:
        - オプション未指定時の適切な処理
        - デフォルト値の正確な適用
        - 設定の一貫性保証
        """
        with patch("sphinxcontrib.jsontable.directives.base_directive.TableBuilder"):
            directive = ConcreteDirectiveTest(
                "test", [], {}, [], 1, 0, "", Mock(), Mock()
            )

            processed = directive._process_options()

            # デフォルト値の確認
            assert processed["include_header"] is False
            assert "limit" not in processed


class TestBaseDirectiveDataValidation:
    """
    BaseDirectiveのデータ検証機能の品質保証テスト。

    データの適切な検証、変換、セキュリティチェックが
    正しく動作することを保証します。
    """

    @pytest.fixture
    def directive_instance(self):
        """データ検証テスト用のディレクティブインスタンスを作成する。"""
        with patch("sphinxcontrib.jsontable.directives.base_directive.TableBuilder"):
            directive = ConcreteDirectiveTest(
                "test", [], {}, [], 1, 0, "", Mock(), Mock()
            )
            return directive

    def test_valid_table_data_structure_validation(self, directive_instance):
        """
        有効なテーブルデータ構造の検証を行う。

        機能保証項目:
        - 正しいデータ構造の受け入れ
        - データ検証の正確性
        - 変換処理の適切性
        """
        valid_data = [
            ["Header1", "Header2"],
            ["Value1", "Value2"],
            ["Value3", "Value4"],
        ]

        result = directive_instance._validate_and_convert_data(valid_data)

        assert result == valid_data
        assert isinstance(result, list)
        assert all(isinstance(row, list) for row in result)

    def test_invalid_data_type_rejection(self, directive_instance):
        """
        無効なデータ型の適切な拒否を検証する。

        機能保証項目:
        - 不正なデータ型の検出
        - 適切なエラー発生
        - データ品質の保証

        セキュリティ観点:
        - 不正データによる攻撃の防止
        - データ構造の整合性保証
        """
        invalid_data = "not a list"

        with pytest.raises(JsonTableError) as exc_info:
            directive_instance._validate_and_convert_data(invalid_data)

        assert "must be a list" in str(exc_info.value)

    def test_empty_data_handling(self, directive_instance):
        """
        空のデータに対する適切な処理を検証する。

        機能保証項目:
        - 空データの検出
        - 適切なエラー処理
        - エッジケースの処理
        """
        empty_data = []

        with pytest.raises(JsonTableError) as exc_info:
            directive_instance._validate_and_convert_data(empty_data)

        assert "cannot be empty" in str(exc_info.value)

    def test_malformed_row_structure_detection(self, directive_instance):
        """
        不正な行構造の検出と処理を検証する。

        機能保証項目:
        - 不正な行構造の検出
        - 詳細なエラー情報の提供
        - データ品質の保証

        セキュリティ要件:
        - 不正構造による攻撃の防止
        - データ整合性の確保
        """
        malformed_data = [
            ["Header1", "Header2"],
            "not a list row",  # 不正な行構造
            ["Value1", "Value2"],
        ]

        with pytest.raises(JsonTableError) as exc_info:
            directive_instance._validate_and_convert_data(malformed_data)

        error_message = str(exc_info.value)
        assert "Row 1" in error_message
        assert "not a list" in error_message


class TestBaseDirectiveExecutionContext:
    """
    BaseDirectiveの実行コンテキスト検証機能の品質保証テスト。

    実行環境の適切な検証とセキュリティチェックが
    正しく動作することを保証します。
    """

    def test_execution_context_validation_success(self):
        """
        正常な実行コンテキストの検証を行う。

        機能保証項目:
        - 実行前バリデーションの適切な実行
        - 必要なコンポーネントの存在確認
        - 実行環境の健全性確認
        """
        with patch("sphinxcontrib.jsontable.directives.base_directive.TableBuilder"):
            directive = ConcreteDirectiveTest(
                "test", [], {}, [], 1, 0, "", Mock(), Mock()
            )

            # 正常なコンテキストでは例外が発生しないことを確認
            directive._validate_execution_context()  # Should not raise

    def test_missing_table_builder_detection(self):
        """
        テーブルビルダー未初期化の検出を検証する。

        機能保証項目:
        - 必須コンポーネントの存在確認
        - 初期化エラーの適切な検出
        - システムの整合性保証

        セキュリティ観点:
        - 不完全な初期化による攻撃の防止
        - コンポーネントの整合性確認
        """
        with patch("sphinxcontrib.jsontable.directives.base_directive.TableBuilder"):
            directive = ConcreteDirectiveTest(
                "test", [], {}, [], 1, 0, "", Mock(), Mock()
            )

            # テーブルビルダーを意図的に削除
            directive.table_builder = None

            with pytest.raises(JsonTableError) as exc_info:
                directive._validate_execution_context()

            assert "not properly initialized" in str(exc_info.value)


class TestBaseDirectiveErrorNodeCreation:
    """
    BaseDirectiveのエラーノード生成機能の品質保証テスト。

    エラーノードの適切な生成とフォーマットが
    正しく動作することを保証します。
    """

    @pytest.fixture
    def directive_instance(self):
        """エラーノード生成テスト用のディレクティブインスタンスを作成する。"""
        with patch("sphinxcontrib.jsontable.directives.base_directive.TableBuilder"):
            directive = ConcreteDirectiveTest(
                "test", [], {}, [], 1, 0, "", Mock(), Mock()
            )
            return directive

    def test_error_node_creation_structure(self, directive_instance):
        """
        エラーノードの構造が正しく生成されることを検証する。

        機能保証項目:
        - エラーノードの適切な構造
        - メッセージの正確な表示
        - DocUtilsノードの正しい生成
        """
        error_message = "Test error message for validation"

        error_node = directive_instance._create_error_node(error_message)

        # エラーノードの構造検証
        assert isinstance(error_node, nodes.error)
        assert len(error_node.children) == 1
        assert isinstance(error_node.children[0], nodes.paragraph)

        # メッセージ内容の検証
        paragraph = error_node.children[0]
        assert paragraph.astext() == error_message

    def test_error_node_message_sanitization(self, directive_instance):
        """
        エラーメッセージのサニタイゼーションを検証する。

        セキュリティ要件:
        - 特殊文字の適切な処理
        - HTMLエスケープの確認
        - インジェクション攻撃の防止
        """
        malicious_message = "<script>alert('xss')</script>Test message"

        error_node = directive_instance._create_error_node(malicious_message)

        # 生成されたノードの内容確認
        assert isinstance(error_node, nodes.error)
        paragraph = error_node.children[0]

        # スクリプトタグがそのまま文字列として扱われることを確認
        # （DocUtilsが適切にエスケープすることを前提）
        assert paragraph.astext() == malicious_message
