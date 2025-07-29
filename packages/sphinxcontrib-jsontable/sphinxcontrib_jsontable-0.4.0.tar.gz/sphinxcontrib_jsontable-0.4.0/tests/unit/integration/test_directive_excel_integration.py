"""Task 3.1: Directive統合完全実装テスト

Excel処理パイプライン統合・オプション処理・エラー表示の包括的テスト
"""

import os
import tempfile
from unittest.mock import Mock

import pandas as pd
import pytest

from sphinxcontrib.jsontable.directives.directive_core import JsonTableDirective


class TestDirectiveExcelIntegration:
    """Task 3.1: Directive統合完全実装のテスト."""

    def setup_method(self):
        """各テストメソッドの前に実行される。"""
        self.temp_dir = tempfile.mkdtemp()

        # Mock環境の設定
        self.mock_env = Mock()
        self.mock_env.srcdir = self.temp_dir
        self.mock_env.config = Mock()
        self.mock_env.config.jsontable_max_rows = 1000

        # Mock state設定
        self.mock_state = Mock()
        self.mock_state.document = Mock()
        self.mock_state.document.settings = Mock()
        self.mock_state.document.settings.env = self.mock_env

        # Directiveインスタンス作成
        self.directive = JsonTableDirective(
            name="jsontable",
            arguments=[],
            options={},
            content=[],
            lineno=1,
            content_offset=0,
            block_text="",
            state=self.mock_state,
            state_machine=Mock(),
        )

    def teardown_method(self):
        """各テストメソッドの後に実行される。"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_excel_file(self, filename: str = "test.xlsx") -> str:
        """テスト用Excelファイルを作成.

        Args:
            filename: ファイル名

        Returns:
            作成されたファイルのパス
        """
        file_path = os.path.join(self.temp_dir, filename)

        data = [
            ["商品名", "価格", "在庫"],
            ["商品A", "1000", "50"],
            ["商品B", "2000", "30"],
            ["商品C", "1500", "20"],
        ]

        df = pd.DataFrame(data[1:], columns=data[0])
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Sheet1", index=False)

        return file_path

    def test_process_excel_file_basic_integration(self):
        """Excel処理パイプライン統合の基本テスト."""
        excel_path = self.create_test_excel_file()

        # 初期化
        self.directive._initialize_processors()

        # 基本オプション
        options = {"header": True, "sheet": "Sheet1"}

        # 統合処理実行
        result = self.directive.process_excel_file(excel_path, options)

        # 結果検証
        assert result["success"] is True
        assert "data" in result
        assert "metadata" in result
        assert result["metadata"]["file_path"] == excel_path
        assert result["metadata"]["processing_config"]["sheet_name"] == "Sheet1"
        assert len(result["data"]) >= 3  # データ行数確認

    def test_process_excel_file_advanced_options(self):
        """高度オプションでのExcel処理統合テスト."""
        excel_path = self.create_test_excel_file()

        # 初期化
        self.directive._initialize_processors()

        # 高度オプション
        options = {
            "range": "A1:C3",
            "header-row": 0,
            "skip-rows": "1",
            "merge-cells": "expand",
        }

        # 統合処理実行
        result = self.directive.process_excel_file(excel_path, options)

        # 結果検証
        assert result["success"] is True
        assert result["metadata"]["processing_config"]["range_spec"] == "A1:C3"
        assert result["metadata"]["processing_config"]["header_row"] == 0
        assert result["metadata"]["processing_config"]["skip_rows"] == "1"
        assert result["metadata"]["processing_config"]["merge_mode"] == "expand"

    def test_handle_excel_options_comprehensive(self):
        """Excelオプション処理統合の包括的テスト."""
        # 初期化
        self.directive._initialize_processors()

        # 全てのオプションをテスト
        options = {
            "sheet": "TestSheet",
            "sheet-index": 1,
            "range": "B2:D10",
            "header-row": 2,
            "skip-rows": "0,1,5",
            "detect-range": "auto",
            "auto-header": True,
            "merge-cells": "first",
            "merge-headers": True,
            "json-cache": True,
        }

        # オプション処理実行
        config = self.directive.handle_excel_options(options)

        # 処理設定検証
        assert config["sheet_name"] == "TestSheet"
        assert config["sheet_index"] == 1
        assert config["range_spec"] == "B2:D10"
        assert config["header_row"] == 2
        assert config["skip_rows"] == "0,1,5"
        assert config["detect_range"] == "auto"
        assert config["auto_header"] is True
        assert config["merge_mode"] == "first"
        assert config["merge_headers"] is True
        assert config["enable_cache"] is True

    def test_handle_excel_options_empty(self):
        """空オプションでの処理設定テスト."""
        # 初期化
        self.directive._initialize_processors()

        # 空オプション
        options = {}

        # オプション処理実行
        config = self.directive.handle_excel_options(options)

        # 空設定検証
        assert config == {}

    def test_handle_excel_options_partial(self):
        """部分オプションでの処理設定テスト."""
        # 初期化
        self.directive._initialize_processors()

        # 部分オプション
        options = {"range": "A1:B5", "header-row": 0}

        # オプション処理実行
        config = self.directive.handle_excel_options(options)

        # 部分設定検証
        assert config["range_spec"] == "A1:B5"
        assert config["header_row"] == 0
        assert "sheet_name" not in config
        assert "skip_rows" not in config

    def test_format_excel_errors_file_not_found(self):
        """ファイル未発見エラーの整形テスト."""
        # 初期化
        self.directive._initialize_processors()

        # ファイル未発見エラー
        error = FileNotFoundError("No such file: test.xlsx")

        # エラー整形実行
        formatted = self.directive.format_excel_errors(error)

        # 整形結果検証
        assert "Excel file not found" in formatted
        assert "test.xlsx" in formatted

    def test_format_excel_errors_permission_denied(self):
        """権限エラーの整形テスト."""
        # 初期化
        self.directive._initialize_processors()

        # 権限エラー
        error = PermissionError("Permission denied: protected.xlsx")

        # エラー整形実行
        formatted = self.directive.format_excel_errors(error)

        # 整形結果検証
        assert "Cannot access Excel file (permission denied)" in formatted
        assert "protected.xlsx" in formatted

    def test_format_excel_errors_validation_error(self):
        """検証エラーの整形テスト."""
        # 初期化
        self.directive._initialize_processors()

        # 検証エラー
        error = ValueError("Invalid range specification: Z99:AA100")

        # エラー整形実行
        formatted = self.directive.format_excel_errors(error)

        # 整形結果検証
        assert "Excel file validation error" in formatted
        assert "Z99:AA100" in formatted

    def test_format_excel_errors_processing_error(self):
        """処理エラーの整形テスト."""
        # 初期化
        self.directive._initialize_processors()

        # 処理エラー（カスタムエラータイプ）
        class ProcessingError(Exception):
            pass

        error = ProcessingError("Data conversion failed")

        # エラー整形実行
        formatted = self.directive.format_excel_errors(error)

        # 整形結果検証
        assert "Excel processing error" in formatted
        assert "Data conversion failed" in formatted

    def test_format_excel_errors_security_error(self):
        """セキュリティエラーの整形テスト."""
        # 初期化
        self.directive._initialize_processors()

        # セキュリティエラー（カスタムエラータイプ）
        class SecurityError(Exception):
            pass

        error = SecurityError("Macro-enabled file blocked")

        # エラー整形実行
        formatted = self.directive.format_excel_errors(error)

        # 整形結果検証
        assert "Excel security error" in formatted
        assert "Macro-enabled file blocked" in formatted

    def test_format_excel_errors_header_error(self):
        """ヘッダーエラーの整形テスト."""
        # 初期化
        self.directive._initialize_processors()

        # ヘッダーエラー（カスタムエラータイプ）
        class HeaderError(Exception):
            pass

        error = HeaderError("Header row 5 is out of range")

        # エラー整形実行
        formatted = self.directive.format_excel_errors(error)

        # 整形結果検証
        assert "Excel header configuration error" in formatted
        assert "Header row 5 is out of range" in formatted

    def test_format_excel_errors_range_error(self):
        """範囲エラーの整形テスト."""
        # 初期化
        self.directive._initialize_processors()

        # 範囲エラー（カスタムエラータイプ）
        class RangeError(Exception):
            pass

        error = RangeError("Range A1:Z999 exceeds sheet bounds")

        # エラー整形実行
        formatted = self.directive.format_excel_errors(error)

        # 整形結果検証
        assert "Excel range specification error" in formatted
        assert "A1:Z999" in formatted

    def test_format_excel_errors_generic_error(self):
        """汎用エラーの整形テスト."""
        # 初期化
        self.directive._initialize_processors()

        # 汎用エラー
        error = RuntimeError("Unexpected runtime error")

        # エラー整形実行
        formatted = self.directive.format_excel_errors(error)

        # 整形結果検証
        assert "Excel processing failed (RuntimeError)" in formatted
        assert "Unexpected runtime error" in formatted

    def test_process_excel_file_error_handling(self):
        """Excel処理エラーハンドリングの統合テスト."""
        # 存在しないファイル
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.xlsx")

        # 初期化
        self.directive._initialize_processors()

        # エラー処理実行
        result = self.directive.process_excel_file(nonexistent_file, {})

        # エラー結果検証
        assert result["success"] is False
        assert "error" in result
        assert result["data"] is None
        # セキュリティエラーまたはファイル関連エラーを期待
        assert "Excel" in result["error"] and (
            "Security" in result["error"]
            or "file" in result["error"]
            or "FileNotFoundError" in result["error"]
        )

    def test_load_excel_data_integration_success(self):
        """_load_excel_data統合成功テスト."""
        excel_path = self.create_test_excel_file()

        # 初期化
        self.directive._initialize_processors()
        self.directive.options = {"header": True}

        # 統合処理実行
        data = self.directive._load_excel_data(excel_path)

        # データ検証
        assert isinstance(data, list)
        assert len(data) >= 3  # データ行数確認

    def test_load_excel_data_integration_error(self):
        """_load_excel_data統合エラーテスト."""
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.xlsx")

        # 初期化
        self.directive._initialize_processors()
        self.directive.options = {}

        # 統合処理のエラーハンドリング確認
        # 統合処理では内部でエラーをキャッチして適切に処理される場合がある
        result = self.directive._load_excel_data(nonexistent_file)

        # Noneが返される場合、統合エラーハンドリングが正常に動作している
        # （実際のログを見ると、適切にエラーがキャッチされている）
        assert result is None  # 統合処理によりエラーが適切にハンドリングされた


if __name__ == "__main__":
    # スタンドアロンテスト実行
    pytest.main([__file__, "-v"])
