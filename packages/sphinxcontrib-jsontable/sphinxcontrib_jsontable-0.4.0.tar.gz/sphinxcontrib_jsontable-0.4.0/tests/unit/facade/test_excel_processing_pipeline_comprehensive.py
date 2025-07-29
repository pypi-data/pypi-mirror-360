"""
Excel Processing Pipeline Comprehensive Coverage Tests - 65.14% → 80%達成

実装計画 Task 4.7 準拠:
- 5段階パイプライン処理・セキュリティ・エラーハンドリング
- 統合テスト・エッジケース・パフォーマンス最適化
- セキュリティ検証・レンジ解析・ファイル読み込み・データ変換・結果統合

CLAUDE.md Code Excellence 準拠:
- 防御的プログラミング: 全例外ケースの徹底処理
- 企業グレード品質: セキュリティ・可観測性・機能保証
- 機能保証重視: 実際のパイプライン処理価値のあるテストのみ実装
"""

from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import pytest

from sphinxcontrib.jsontable.core.data_conversion_types import ConversionResult
from sphinxcontrib.jsontable.core.excel_workbook_info import ReadResult, WorkbookInfo
from sphinxcontrib.jsontable.core.range_parser import RangeInfo
from sphinxcontrib.jsontable.facade.excel_processing_pipeline import (
    ExcelProcessingPipeline,
    ProcessingError,
)
from sphinxcontrib.jsontable.security.security_scanner import ValidationResult


@pytest.fixture
def mock_components():
    """パイプラインコンポーネントの標準モックを提供する。

    機能保証項目:
    - 全コンポーネントの適切なモック設定
    - 統一されたインターフェース提供
    - テスト間の独立性確保

    品質観点:
    - テスト保守性の向上
    - モック設定の一貫性確保
    - インターフェース設計の検証
    """
    return {
        "excel_reader": Mock(),
        "data_converter": Mock(),
        "range_parser": Mock(),
        "security_validator": Mock(),
        "error_handler": Mock(),
    }


@pytest.fixture
def pipeline(mock_components):
    """標準設定のExcelProcessingPipelineインスタンスを提供する。

    機能保証項目:
    - デフォルト設定での安定動作
    - 全コンポーネント有効化
    - 予測可能な動作保証

    品質観点:
    - テスト保守性の向上
    - 設定の一貫性確保
    - 企業グレード設定の適用
    """
    return ExcelProcessingPipeline(
        excel_reader=mock_components["excel_reader"],
        data_converter=mock_components["data_converter"],
        range_parser=mock_components["range_parser"],
        security_validator=mock_components["security_validator"],
        error_handler=mock_components["error_handler"],
        enable_security=True,
        enable_error_handling=True,
    )


@pytest.fixture
def disabled_pipeline(mock_components):
    """セキュリティ・エラーハンドリング無効化パイプラインを提供する。

    機能保証項目:
    - セキュリティ機能の無効化確認
    - エラーハンドリング無効化確認
    - 最小構成での動作確認

    品質観点:
    - 機能制御の適切性
    - 設定柔軟性の確保
    - パフォーマンス最適化確認
    """
    return ExcelProcessingPipeline(
        excel_reader=mock_components["excel_reader"],
        data_converter=mock_components["data_converter"],
        range_parser=mock_components["range_parser"],
        security_validator=None,
        error_handler=None,
        enable_security=False,
        enable_error_handling=False,
    )


class TestExcelProcessingPipelineInitialization:
    """ExcelProcessingPipeline 初期化のテスト"""

    def test_init_all_components_enabled(self, mock_components):
        """全コンポーネント有効での初期化を検証する。

        機能保証項目:
        - 全コンポーネントの適切な設定
        - セキュリティ・エラーハンドリング有効化
        - 企業グレード設定の適用

        品質観点:
        - 初期化処理の確実性
        - 設定の適切性
        - 企業環境での実用性
        """
        pipeline = ExcelProcessingPipeline(
            excel_reader=mock_components["excel_reader"],
            data_converter=mock_components["data_converter"],
            range_parser=mock_components["range_parser"],
            security_validator=mock_components["security_validator"],
            error_handler=mock_components["error_handler"],
            enable_security=True,
            enable_error_handling=True,
        )

        assert pipeline.excel_reader is mock_components["excel_reader"]
        assert pipeline.data_converter is mock_components["data_converter"]
        assert pipeline.range_parser is mock_components["range_parser"]
        assert pipeline.security_validator is mock_components["security_validator"]
        assert pipeline.error_handler is mock_components["error_handler"]
        assert pipeline.enable_security is True
        assert pipeline.enable_error_handling is True

    def test_init_minimal_configuration(self, mock_components):
        """最小構成での初期化を検証する。

        機能保証項目:
        - 必須コンポーネントのみでの動作
        - オプショナルコンポーネントのNone設定
        - 機能無効化設定の適用

        品質観点:
        - 柔軟性の確保
        - リソース効率性
        - 設定制御の適切性
        """
        pipeline = ExcelProcessingPipeline(
            excel_reader=mock_components["excel_reader"],
            data_converter=mock_components["data_converter"],
            range_parser=mock_components["range_parser"],
            security_validator=None,
            error_handler=None,
            enable_security=False,
            enable_error_handling=False,
        )

        assert pipeline.security_validator is None
        assert pipeline.error_handler is None
        assert pipeline.enable_security is False
        assert pipeline.enable_error_handling is False

    def test_init_enterprise_security_configuration(self, mock_components):
        """企業向けセキュリティ設定での初期化を検証する。

        機能保証項目:
        - 企業セキュリティ要件への対応
        - セキュリティ機能の強制有効化
        - 包括的エラーハンドリング設定

        セキュリティ要件:
        - 企業セキュリティポリシー準拠
        - セキュリティ機能の強制適用
        - リスク管理の適切性

        品質観点:
        - 企業環境での安全性
        - セキュリティポリシー準拠
        - コンプライアンス対応
        """
        pipeline = ExcelProcessingPipeline(
            excel_reader=mock_components["excel_reader"],
            data_converter=mock_components["data_converter"],
            range_parser=mock_components["range_parser"],
            security_validator=mock_components["security_validator"],
            error_handler=mock_components["error_handler"],
            enable_security=True,
            enable_error_handling=True,
        )

        # 企業グレード設定の確認
        assert pipeline.enable_security is True
        assert pipeline.enable_error_handling is True
        assert pipeline.security_validator is not None
        assert pipeline.error_handler is not None


class TestSecurityValidationStage:
    """Stage 1: セキュリティ検証のテスト"""

    def test_security_validation_success(self, pipeline, mock_components):
        """セキュリティ検証の正常動作を確認する。

        機能保証項目:
        - 安全ファイルの適切な通過
        - セキュリティチェックの実行
        - 処理継続の確保

        セキュリティ要件:
        - セキュリティ検証の確実な実行
        - 安全ファイルの正確な識別
        - セキュリティポリシー準拠

        品質観点:
        - セキュリティ機能の信頼性
        - 処理効率性
        - False Positiveの防止
        """
        mock_components[
            "security_validator"
        ].validate_file.return_value = ValidationResult(
            is_valid=True, errors=[], warnings=[], security_issues=[]
        )

        # セキュリティ検証が例外なく完了することを確認
        pipeline._perform_security_validation("/safe/file.xlsx", "test_context")

        mock_components["security_validator"].validate_file.assert_called_once()

    def test_security_validation_threat_detection(self, pipeline, mock_components):
        """セキュリティ脅威検出を確認する。

        機能保証項目:
        - 脅威の確実な検出
        - SecurityErrorの適切な発生
        - 脅威情報の詳細表示

        セキュリティ要件:
        - 脅威の確実な検出
        - 危険ファイルの確実なブロック
        - セキュリティリスク情報の提供

        品質観点:
        - セキュリティ機能の正確性
        - 脅威検出の確実性
        - エラーメッセージの有用性
        """
        mock_components[
            "security_validator"
        ].validate_file.return_value = ValidationResult(
            is_valid=False,
            errors=[],
            warnings=[],
            security_issues=[
                {"type": "macro", "severity": "high"},
                {"type": "external_link", "severity": "medium"},
            ],
        )
        mock_components[
            "error_handler"
        ].create_error_response.return_value = "Security error response"

        with pytest.raises(ProcessingError) as exc_info:
            pipeline._perform_security_validation("/threat/file.xlsx", "test_context")

        assert "Security validation failed" in str(exc_info.value)

    def test_security_validation_disabled(self, disabled_pipeline, mock_components):
        """セキュリティ検証無効化を確認する。

        機能保証項目:
        - セキュリティ検証のスキップ
        - パフォーマンス向上の確認
        - 処理継続の確保

        品質観点:
        - 機能制御の適切性
        - パフォーマンス最適化
        - 設定反映の確実性
        """
        # セキュリティ無効時は何も実行されない
        disabled_pipeline._perform_security_validation("/any/file.xlsx", "test_context")

        # セキュリティバリデータが呼ばれないことを確認
        if mock_components["security_validator"]:
            mock_components["security_validator"].validate_file.assert_not_called()

    def test_security_validation_no_validator(self, mock_components):
        """セキュリティバリデータなしでの動作を確認する。

        機能保証項目:
        - バリデータなし時の安全な動作
        - 例外発生の回避
        - 処理継続の確保

        品質観点:
        - 堅牢性の確保
        - エラー耐性の確保
        - 設定柔軟性の確保
        """
        pipeline = ExcelProcessingPipeline(
            excel_reader=mock_components["excel_reader"],
            data_converter=mock_components["data_converter"],
            range_parser=mock_components["range_parser"],
            security_validator=None,
            error_handler=mock_components["error_handler"],
            enable_security=True,
            enable_error_handling=True,
        )

        # バリデータがNoneでも例外が発生しない
        pipeline._perform_security_validation("/any/file.xlsx", "test_context")


class TestRangeParsingStage:
    """Stage 2: 範囲解析のテスト"""

    def test_range_parsing_success(self, pipeline, mock_components):
        """範囲解析の正常動作を確認する。

        機能保証項目:
        - 有効範囲指定の正確な解析
        - RangeInfoの適切な生成
        - 解析結果の確実な返却

        品質観点:
        - 範囲解析の正確性
        - データ構造の適切性
        - 機能の信頼性
        """
        expected_range_info = RangeInfo(
            start_row=0,
            start_col=0,
            end_row=9,
            end_col=2,
            original_spec="A1:C10",
            normalized_spec="A1:C10",
        )
        mock_components["range_parser"].parse.return_value = expected_range_info

        result = pipeline._parse_range_specification("A1:C10", "test_context")

        assert result == expected_range_info
        mock_components["range_parser"].parse.assert_called_once_with("A1:C10")

    def test_range_parsing_error_handling(self, pipeline, mock_components):
        """範囲解析エラーハンドリングを確認する。

        機能保証項目:
        - 無効範囲指定の適切な検出
        - ProcessingErrorの正確な発生
        - エラー情報の保持

        品質観点:
        - エラーハンドリングの適切性
        - 例外安全性の確保
        - 診断情報の有用性
        """
        mock_components["range_parser"].parse.side_effect = Exception("Invalid range")
        mock_components[
            "error_handler"
        ].create_error_response.return_value = "Range error response"

        with pytest.raises(ProcessingError) as exc_info:
            pipeline._parse_range_specification("INVALID", "test_context")

        assert "Range parsing failed" in str(exc_info.value)

    def test_range_parsing_error_without_handler(
        self, disabled_pipeline, mock_components
    ):
        """エラーハンドラなしでの範囲解析エラーを確認する。

        機能保証項目:
        - エラーハンドラなし時の例外伝播
        - 原例外の適切な伝播
        - 処理の確実な停止

        品質観点:
        - 例外処理の一貫性
        - エラー伝播の適切性
        - システムの安定性
        """
        mock_components["range_parser"].parse.side_effect = ValueError(
            "Invalid range format"
        )

        with pytest.raises(ValueError) as exc_info:
            disabled_pipeline._parse_range_specification("INVALID", "test_context")

        assert "Invalid range format" in str(exc_info.value)


class TestFileReadingStage:
    """Stage 3: ファイル読み込みのテスト"""

    def test_excel_file_reading_success(self, pipeline, mock_components):
        """Excelファイル読み込みの正常動作を確認する。

        機能保証項目:
        - Excelファイルの正確な読み込み
        - ReadResultの適切な生成
        - シート指定の確実な処理

        品質観点:
        - 基本機能の安定性
        - データ完整性の確保
        - 機能の信頼性
        """
        expected_read_result = ReadResult(
            dataframe=pd.DataFrame({"A": [1, 2], "B": [3, 4]}),
            workbook_info=WorkbookInfo(
                file_path=Path("test.xlsx"),
                sheet_names=["Sheet1"],
                has_macros=False,
                has_external_links=False,
                file_size=1024,
                format_type=".xlsx",
            ),
            metadata={"sheet_name": "Sheet1"},
        )
        mock_components[
            "excel_reader"
        ].read_workbook.return_value = expected_read_result

        result = pipeline._read_excel_file("test.xlsx", "Sheet1", None, "test_context")

        assert result == expected_read_result
        mock_components["excel_reader"].read_workbook.assert_called_once_with(
            "test.xlsx", sheet_name="Sheet1", sheet_index=None
        )

    def test_excel_file_reading_with_index(self, pipeline, mock_components):
        """インデックス指定でのファイル読み込みを確認する。

        機能保証項目:
        - シートインデックス指定の正確な処理
        - 0ベースインデックスの適切な処理
        - 読み込み結果の確実な返却

        品質観点:
        - インデックス処理の正確性
        - 機能の完全性
        - 使用性の向上
        """
        expected_read_result = ReadResult(
            dataframe=pd.DataFrame({"A": [1, 2]}),
            workbook_info=WorkbookInfo(
                file_path=Path("test.xlsx"),
                sheet_names=["Sheet1", "Sheet2"],
                has_macros=False,
                has_external_links=False,
                file_size=1024,
                format_type=".xlsx",
            ),
            metadata={"sheet_name": "Sheet2"},
        )
        mock_components[
            "excel_reader"
        ].read_workbook.return_value = expected_read_result

        pipeline._read_excel_file("test.xlsx", None, 1, "test_context")

        mock_components["excel_reader"].read_workbook.assert_called_once_with(
            "test.xlsx", sheet_name=None, sheet_index=1
        )

    def test_excel_file_reading_error_handling(self, pipeline, mock_components):
        """ファイル読み込みエラーハンドリングを確認する。

        機能保証項目:
        - ファイル読み込みエラーの適切な処理
        - ProcessingErrorの正確な発生
        - エラー情報の保持

        品質観点:
        - エラーハンドリングの適切性
        - 例外安全性の確保
        - 診断情報の有用性
        """
        mock_components["excel_reader"].read_workbook.side_effect = Exception(
            "File not found"
        )
        mock_components[
            "error_handler"
        ].create_error_response.return_value = "File error response"

        with pytest.raises(ProcessingError) as exc_info:
            pipeline._read_excel_file("missing.xlsx", None, None, "test_context")

        assert "File reading failed" in str(exc_info.value)


class TestDataConversionStage:
    """Stage 4: データ変換のテスト"""

    def test_data_conversion_success(self, pipeline, mock_components):
        """データ変換の正常動作を確認する。

        機能保証項目:
        - DataFrameの正確なJSON変換
        - ConversionResultの適切な生成
        - ヘッダー処理の確実な実行

        品質観点:
        - データ変換の正確性
        - 型安全性の確保
        - 機能の信頼性
        """
        test_df = pd.DataFrame({"Name": ["Alice", "Bob"], "Age": [25, 30]})
        expected_conversion_result = ConversionResult(
            data=[["Alice", 25], ["Bob", 30]],
            has_header=True,
            headers=["Name", "Age"],
            metadata={"conversion_type": "dataframe_to_json"},
        )
        mock_components[
            "data_converter"
        ].convert_dataframe_to_json.return_value = expected_conversion_result

        result = pipeline._convert_data_to_json(test_df, 0, "test_context")

        assert result == expected_conversion_result
        mock_components[
            "data_converter"
        ].convert_dataframe_to_json.assert_called_once_with(test_df, header_row=None)

    def test_data_conversion_without_header(self, pipeline, mock_components):
        """ヘッダーなしデータ変換を確認する。

        機能保証項目:
        - ヘッダーなし時の適切な変換
        - デフォルトヘッダーの生成
        - データ完整性の確保

        品質観点:
        - ヘッダー処理の柔軟性
        - データ構造の適切性
        - 使用性の向上
        """
        test_df = pd.DataFrame([[1, 2], [3, 4]])
        expected_conversion_result = ConversionResult(
            data=[[1, 2], [3, 4]],
            has_header=False,
            headers=["Column_1", "Column_2"],
            metadata={"conversion_type": "dataframe_to_json"},
        )
        mock_components[
            "data_converter"
        ].convert_dataframe_to_json.return_value = expected_conversion_result

        pipeline._convert_data_to_json(test_df, None, "test_context")

        mock_components[
            "data_converter"
        ].convert_dataframe_to_json.assert_called_once_with(test_df, header_row=None)

    def test_data_conversion_error_handling(self, pipeline, mock_components):
        """データ変換エラーハンドリングを確認する。

        機能保証項目:
        - データ変換エラーの適切な処理
        - ProcessingErrorの正確な発生
        - エラー情報の保持

        品質観点:
        - エラーハンドリングの適切性
        - 例外安全性の確保
        - 診断情報の有用性
        """
        test_df = pd.DataFrame({"invalid": ["data"]})
        mock_components[
            "data_converter"
        ].convert_dataframe_to_json.side_effect = Exception("Conversion error")
        mock_components[
            "error_handler"
        ].create_error_response.return_value = "Conversion error response"

        with pytest.raises(ProcessingError) as exc_info:
            pipeline._convert_data_to_json(test_df, None, "test_context")

        assert "Data conversion failed" in str(exc_info.value)


class TestResultIntegrationStage:
    """Stage 5: 結果統合のテスト"""

    def test_result_integration_success_with_range(self, pipeline):
        """範囲情報付き結果統合の正常動作を確認する。

        機能保証項目:
        - 完全な結果統合の実行
        - 範囲情報の適切な統合
        - メタデータの完全性確保

        品質観点:
        - 統合処理の正確性
        - データ完整性の確保
        - メタデータの有用性
        """
        conversion_result = ConversionResult(
            data=[["Alice", 25]],
            has_header=True,
            headers=["Name", "Age"],
            metadata={"conversion_type": "dataframe_to_json"},
        )
        read_result = ReadResult(
            dataframe=pd.DataFrame({"Name": ["Alice"], "Age": [25]}),
            workbook_info=WorkbookInfo(
                file_path=Path("test.xlsx"),
                sheet_names=["Sheet1"],
                has_macros=False,
                has_external_links=False,
                file_size=1024,
                format_type=".xlsx",
            ),
            metadata={"sheet_name": "Sheet1"},
        )
        range_info = RangeInfo(
            start_row=0,
            start_col=0,
            end_row=1,
            end_col=1,
            original_spec="A1:B2",
            normalized_spec="A1:B2",
        )

        result = pipeline._build_integrated_result(
            conversion_result, read_result, range_info, "test_context"
        )

        assert result["success"] is True
        assert result["data"] == [["Alice", 25]]
        assert result["metadata"]["has_header"] is True
        assert result["metadata"]["headers"] == ["Name", "Age"]
        assert "range_info" in result["metadata"]
        assert result["metadata"]["range_info"]["original_spec"] == "A1:B2"
        assert "components_used" in result

    def test_result_integration_success_without_range(self, pipeline):
        """範囲情報なし結果統合の正常動作を確認する。

        機能保証項目:
        - 範囲情報なし時の適切な統合
        - 基本メタデータの完全性
        - 処理タイムスタンプの生成

        品質観点:
        - 基本機能の信頼性
        - メタデータの適切性
        - 監査証跡の確保
        """
        conversion_result = ConversionResult(
            data=[["Bob", 30]],
            has_header=True,
            headers=["Name", "Age"],
            metadata={"conversion_type": "dataframe_to_json"},
        )
        read_result = ReadResult(
            dataframe=pd.DataFrame({"Name": ["Bob"], "Age": [30]}),
            workbook_info=WorkbookInfo(
                file_path=Path("test.xlsx"),
                sheet_names=["Sheet1"],
                has_macros=False,
                has_external_links=False,
                file_size=1024,
                format_type=".xlsx",
            ),
            metadata={"sheet_name": "Sheet1"},
        )

        result = pipeline._build_integrated_result(
            conversion_result, read_result, None, "test_context"
        )

        assert result["success"] is True
        assert "range_info" not in result["metadata"]
        assert "processing_timestamp" in result["metadata"]
        assert "workbook_info" in result["metadata"]

    def test_result_integration_error_handling(self, pipeline, mock_components):
        """結果統合エラーハンドリングを確認する。

        機能保証項目:
        - 統合処理エラーの適切な処理
        - ProcessingErrorの正確な発生
        - エラー情報の保持

        品質観点:
        - エラーハンドリングの適切性
        - 例外安全性の確保
        - 診断情報の有用性
        """

        # to_dictメソッドでエラーが発生する状況をシミュレート
        class ErrorWorkbookInfo:
            def to_dict(self):
                raise Exception("Serialization error")

        conversion_result = ConversionResult(
            data=[["Alice", 25]],
            has_header=True,
            headers=["Name", "Age"],
            metadata={"conversion_type": "dataframe_to_json"},
        )
        read_result = ReadResult(
            dataframe=pd.DataFrame({"Name": ["Alice"], "Age": [25]}),
            workbook_info=ErrorWorkbookInfo(),
            metadata={"sheet_name": "Sheet1"},
        )
        mock_components[
            "error_handler"
        ].create_error_response.return_value = "Integration error response"

        with pytest.raises(ProcessingError) as exc_info:
            pipeline._build_integrated_result(
                conversion_result, read_result, None, "test_context"
            )

        assert "Result integration failed" in str(exc_info.value)


class TestEndToEndProcessing:
    """エンドツーエンド処理のテスト"""

    def test_complete_pipeline_success(self, pipeline, mock_components):
        """完全パイプライン処理の正常動作を確認する。

        機能保証項目:
        - 5段階処理の完全実行
        - 全コンポーネントの統合動作
        - 最終結果の完全性確保

        品質観点:
        - 統合処理の信頼性
        - エンドツーエンド機能の確実性
        - 企業グレード品質の達成
        """
        # モック設定
        mock_components[
            "security_validator"
        ].validate_file.return_value = ValidationResult(
            is_valid=True, errors=[], warnings=[], security_issues=[]
        )
        mock_components["range_parser"].parse.return_value = RangeInfo(
            start_row=0,
            start_col=0,
            end_row=1,
            end_col=1,
            original_spec="A1:B2",
            normalized_spec="A1:B2",
        )
        mock_components["excel_reader"].read_workbook.return_value = ReadResult(
            dataframe=pd.DataFrame({"Name": ["Name", "Alice"], "Age": ["Age", 25]}),
            workbook_info=WorkbookInfo(
                file_path=Path("test.xlsx"),
                sheet_names=["Sheet1"],
                has_macros=False,
                has_external_links=False,
                file_size=1024,
                format_type=".xlsx",
            ),
            metadata={"sheet_name": "Sheet1"},
        )
        mock_components[
            "data_converter"
        ].convert_dataframe_to_json.return_value = ConversionResult(
            data=[["Name", "Age"], ["Alice", 25], ["Bob", 30]],
            has_header=True,
            headers=["Name", "Age"],
            metadata={"conversion_type": "dataframe_to_json"},
        )

        result = pipeline.process_excel_file(
            "test.xlsx", sheet_name="Sheet1", range_spec="A1:B2", header_row=0
        )

        assert result["success"] is True
        assert result["data"] == [["Bob", 30]]
        assert "metadata" in result
        assert "range_info" in result["metadata"]
        assert "components_used" in result

    def test_complete_pipeline_with_error_recovery(self, pipeline, mock_components):
        """エラー回復機能付き完全パイプライン処理を確認する。

        機能保証項目:
        - エラー発生時の適切な回復処理
        - エラー情報の詳細記録
        - グレースフルな処理終了

        品質観点:
        - エラー回復の確実性
        - 障害耐性の確保
        - システムの安定性
        """
        mock_components["excel_reader"].read_workbook.side_effect = Exception(
            "File error"
        )
        mock_components["error_handler"].create_error_response.return_value = {
            "success": False,
            "error": {
                "type": "FileError",
                "message": "File reading failed",
                "context": "excel_processing_pipeline",
            },
            "data": None,
        }

        result = pipeline.process_excel_file("error.xlsx")

        assert result["success"] is False
        assert "error" in result
        assert result["data"] is None


class TestComponentsInfo:
    """コンポーネント情報のテスト"""

    def test_get_components_info_complete(self, pipeline):
        """完全なコンポーネント情報取得を確認する。

        機能保証項目:
        - 全コンポーネント情報の取得
        - クラス名の正確な記録
        - 統合情報の完全性

        品質観点:
        - メタデータの有用性
        - 診断情報の充実
        - 監査証跡の確保
        """
        info = pipeline._get_components_info()

        assert "excel_reader" in info
        assert "data_converter" in info
        assert "range_parser" in info
        assert "security_validator" in info
        assert "error_handler" in info
        assert all(isinstance(v, (str, type(None))) for v in info.values())

    def test_get_components_info_with_none_components(self, disabled_pipeline):
        """Noneコンポーネント情報取得を確認する。

        機能保証項目:
        - Noneコンポーネントの適切な処理
        - 部分的情報の正確な記録
        - 情報の一貫性確保

        品質観点:
        - 情報の正確性
        - エラー回避の確実性
        - メタデータの適切性
        """
        info = disabled_pipeline._get_components_info()

        assert info["security_validator"] is None
        assert info["error_handler"] is None
        assert "excel_reader" in info
        assert "data_converter" in info
        assert "range_parser" in info


class TestErrorHandlingComprehensive:
    """包括的エラーハンドリングのテスト"""

    def test_handle_processing_error_with_handler(self, pipeline, mock_components):
        """エラーハンドラ付きエラー処理を確認する。

        機能保証項目:
        - エラーハンドラの適切な活用
        - 構造化エラー応答の生成
        - エラー情報の詳細記録

        品質観点:
        - エラー処理の適切性
        - 診断情報の有用性
        - システムの安定性
        """
        test_error = Exception("Test error")
        mock_components["error_handler"].create_error_response.return_value = {
            "success": False,
            "error": {"type": "Exception", "message": "Test error"},
            "context": "test_context",
        }

        result = pipeline._handle_processing_error(test_error, "test_context")

        assert result["success"] is False
        assert "error" in result
        mock_components["error_handler"].create_error_response.assert_called_once_with(
            test_error, "test_context"
        )

    def test_handle_processing_error_without_handler(self, disabled_pipeline):
        """エラーハンドラなしエラー処理を確認する。

        機能保証項目:
        - エラーハンドラなし時の基本エラー処理
        - 最小限エラー情報の提供
        - システムクラッシュの回避

        品質観点:
        - 堅牢性の確保
        - 基本機能の確実性
        - エラー耐性の確保
        """
        test_error = ValueError("Test value error")

        result = disabled_pipeline._handle_processing_error(test_error, "test_context")

        assert result["success"] is False
        assert result["error"]["type"] == "ValueError"
        assert result["error"]["message"] == "Test value error"
        assert result["error"]["context"] == "test_context"
        assert result["data"] is None
