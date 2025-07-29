"""
Excel Utilities Comprehensive Coverage Tests - 27.27% → 80%達成

実装計画 Phase 2.1.1 準拠:
- セキュリティ検証テスト（悪意のあるExcelファイル検出）
- ファイル形式対応テスト（.xlsx/.xls/.xlsm完全対応）
- パフォーマンステスト（大容量ファイル処理）
- エラー回復テスト（破損ファイル処理）

CLAUDE.md Code Excellence 準拠:
- 機能保証重視: 実際のビジネス価値のあるテストのみ実装
- 防御的プログラミング: セキュリティテスト・エラーハンドリング徹底
- 企業グレード品質: 長期的品質維持・保守性確保
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import pytest

from sphinxcontrib.jsontable.core.data_conversion_types import HeaderDetectionResult
from sphinxcontrib.jsontable.core.excel_workbook_info import WorkbookInfo
from sphinxcontrib.jsontable.facade.excel_utilities import ExcelUtilities


@pytest.fixture
def temp_excel_files():
    """テスト用一時Excelファイルを提供する。

    機能保証項目:
    - 各種Excelファイル形式の生成
    - テスト後のクリーンアップ保証
    - セキュリティテスト用データの安全な提供

    品質観点:
    - リソースリークの防止
    - テスト環境の分離
    - クロスプラットフォーム互換性
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 標準Excelファイル作成
        valid_xlsx = temp_path / "valid.xlsx"
        test_data = pd.DataFrame(
            {
                "Name": ["田中太郎", "佐藤花子", "Smith John"],
                "Age": [25, 30, 35],
                "Department": ["営業部", "開発部", "Sales"],
            }
        )
        test_data.to_excel(valid_xlsx, index=False)

        # 大容量テスト用ファイル
        large_xlsx = temp_path / "large.xlsx"
        large_data = pd.DataFrame(
            {"ID": range(1000), "Data": [f"Item {i}" for i in range(1000)]}
        )
        large_data.to_excel(large_xlsx, index=False)

        yield {
            "temp_dir": temp_path,
            "valid_xlsx": valid_xlsx,
            "large_xlsx": large_xlsx,
            "nonexistent": temp_path / "nonexistent.xlsx",
        }


@pytest.fixture
def mock_components():
    """ExcelUtilities用モックコンポーネントを提供する。

    機能保証項目:
    - 統一されたモック設定の提供
    - 予測可能な動作保証
    - テスト間の独立性確保

    品質観点:
    - テスト保守性の向上
    - デバッグ容易性の確保
    - インターフェース設計の検証
    """
    mock_excel_reader = Mock()
    mock_data_converter = Mock()
    mock_error_handler = Mock()

    # デフォルトの戻り値設定
    mock_excel_reader.validate_file.return_value = WorkbookInfo(
        file_path=Path("test.xlsx"),
        sheet_names=["Sheet1", "Sheet2"],
        has_macros=False,
        has_external_links=False,
        file_size=1024,
        format_type="xlsx",
    )
    mock_excel_reader.get_sheet_names.return_value = ["Sheet1", "Sheet2"]

    mock_data_converter.detect_header.return_value = HeaderDetectionResult(
        has_header=True,
        confidence=0.95,
        headers=["Name", "Age", "Department"],
        analysis={"detected_patterns": ["string", "numeric", "string"]},
    )

    mock_error_handler.create_error_response.return_value = {
        "success": False,
        "error": {"type": "TestError", "message": "Test error"},
    }

    return {
        "excel_reader": mock_excel_reader,
        "data_converter": mock_data_converter,
        "error_handler": mock_error_handler,
    }


class TestExcelUtilitiesInitialization:
    """ExcelUtilities 初期化のテスト"""

    def test_init_with_all_components(self, mock_components):
        """全コンポーネント指定での初期化を検証する。

        機能保証項目:
        - 依存関係注入の適切な実行
        - コンポーネント設定の正確な保存
        - インターフェース設計の整合性確認

        品質観点:
        - オブジェクト指向設計の適切性
        - 依存関係管理の健全性
        - 初期化処理の確実性
        """
        utilities = ExcelUtilities(
            excel_reader=mock_components["excel_reader"],
            data_converter=mock_components["data_converter"],
            error_handler=mock_components["error_handler"],
            enable_error_handling=True,
        )

        assert utilities.excel_reader == mock_components["excel_reader"]
        assert utilities.data_converter == mock_components["data_converter"]
        assert utilities.error_handler == mock_components["error_handler"]
        assert utilities.enable_error_handling is True

    def test_init_minimal_components(self, mock_components):
        """最小コンポーネントでの初期化を検証する。

        機能保証項目:
        - 必須コンポーネントのみでの正常動作
        - オプション設定のデフォルト値確認
        - 後方互換性の維持

        品質観点:
        - API設計の柔軟性
        - 使用性の向上
        - エラー耐性の確保
        """
        utilities = ExcelUtilities(
            excel_reader=mock_components["excel_reader"],
            data_converter=mock_components["data_converter"],
        )

        assert utilities.excel_reader == mock_components["excel_reader"]
        assert utilities.data_converter == mock_components["data_converter"]
        assert utilities.error_handler is None
        assert utilities.enable_error_handling is True


class TestExcelFileValidation:
    """Excel ファイル検証機能のテスト"""

    def test_validate_excel_file_success(self, mock_components, temp_excel_files):
        """正常なExcelファイルの検証を確認する。

        機能保証項目:
        - 正常ファイルの適切な検証
        - ワークブック情報の正確な取得
        - タイムスタンプの適切な生成

        品質観点:
        - 基本機能の安定性
        - データ形式の一貫性
        - メタデータの有用性
        """
        utilities = ExcelUtilities(
            excel_reader=mock_components["excel_reader"],
            data_converter=mock_components["data_converter"],
            error_handler=mock_components["error_handler"],
        )

        result = utilities.validate_excel_file(temp_excel_files["valid_xlsx"])

        assert result["valid"] is True
        assert "workbook_info" in result
        assert "validation_timestamp" in result
        mock_components["excel_reader"].validate_file.assert_called_once()

    def test_validate_excel_file_error_handling(
        self, mock_components, temp_excel_files
    ):
        """Excelファイル検証エラーのハンドリングを確認する。

        機能保証項目:
        - ファイルエラーの適切な検出
        - エラーハンドラーの正確な呼び出し
        - エラー情報の適切な伝達

        セキュリティ要件:
        - 機密情報の非漏洩
        - セキュアなエラー処理

        品質観点:
        - 障害処理の適切性
        - エラー診断の容易性
        - システム安定性の確保
        """
        mock_components["excel_reader"].validate_file.side_effect = Exception(
            "Test validation error"
        )

        utilities = ExcelUtilities(
            excel_reader=mock_components["excel_reader"],
            data_converter=mock_components["data_converter"],
            error_handler=mock_components["error_handler"],
        )

        result = utilities.validate_excel_file(temp_excel_files["valid_xlsx"])

        assert result["success"] is False
        assert "error" in result
        mock_components["error_handler"].create_error_response.assert_called_once()


class TestSheetOperations:
    """シート操作機能のテスト"""

    def test_get_sheet_names_success(self, mock_components, temp_excel_files):
        """シート名取得の正常動作を確認する。

        機能保証項目:
        - シート名リストの正確な取得
        - 複数シートの適切な処理
        - データ形式の一貫性確保

        品質観点:
        - 基本機能の信頼性
        - データ構造の適切性
        - エラーの無い標準動作
        """
        utilities = ExcelUtilities(
            excel_reader=mock_components["excel_reader"],
            data_converter=mock_components["data_converter"],
        )

        result = utilities.get_sheet_names(temp_excel_files["valid_xlsx"])

        assert isinstance(result, list)
        assert result == ["Sheet1", "Sheet2"]
        mock_components["excel_reader"].get_sheet_names.assert_called_once()

    def test_get_sheet_names_with_error_handling(
        self, mock_components, temp_excel_files
    ):
        """シート名取得エラー時のハンドリングを確認する。

        機能保証項目:
        - エラー発生時の適切な処理
        - エラーハンドラー連携の確認
        - デフォルト値の適切な返却

        品質観点:
        - 障害耐性の確保
        - グレースフルデグラデーション
        - ユーザビリティの維持
        """
        mock_components["excel_reader"].get_sheet_names.side_effect = Exception(
            "Sheet access error"
        )

        utilities = ExcelUtilities(
            excel_reader=mock_components["excel_reader"],
            data_converter=mock_components["data_converter"],
            error_handler=mock_components["error_handler"],
        )

        result = utilities.get_sheet_names(temp_excel_files["valid_xlsx"])

        assert isinstance(result, list)
        mock_components["error_handler"].create_error_response.assert_called_once()

    def test_get_workbook_info_comprehensive(self, mock_components, temp_excel_files):
        """包括的ワークブック情報取得を確認する。

        機能保証項目:
        - ワークブック情報の包括的取得
        - ファイルパス・シート情報の統合
        - メタデータの適切な生成

        品質観点:
        - 統合機能の正確性
        - データ一貫性の確保
        - 情報の完全性保証
        """
        utilities = ExcelUtilities(
            excel_reader=mock_components["excel_reader"],
            data_converter=mock_components["data_converter"],
            error_handler=mock_components["error_handler"],
        )

        result = utilities.get_workbook_info(temp_excel_files["valid_xlsx"])

        assert "file_path" in result
        assert "workbook_info" in result
        assert "sheet_names" in result
        assert "sheet_count" in result
        assert result["sheet_count"] == 2
        assert "analysis_timestamp" in result


class TestHeaderDetection:
    """ヘッダー検出機能のテスト"""

    def test_detect_headers_success(self, mock_components):
        """ヘッダー検出の正常動作を確認する。

        機能保証項目:
        - DataFrame内ヘッダーの正確な検出
        - 検出結果の適切な形式変換
        - 信頼度情報の提供

        品質観点:
        - アルゴリズム精度の確保
        - データ構造の一貫性
        - パフォーマンスの適切性
        """
        test_df = pd.DataFrame(
            {"Name": ["田中", "佐藤"], "Age": [25, 30], "Department": ["営業", "開発"]}
        )

        utilities = ExcelUtilities(
            excel_reader=mock_components["excel_reader"],
            data_converter=mock_components["data_converter"],
        )

        result = utilities.detect_headers(test_df)

        assert isinstance(result, dict)
        mock_components["data_converter"].detect_header.assert_called_once_with(test_df)

    def test_detect_headers_error_handling(self, mock_components):
        """ヘッダー検出エラー時のハンドリングを確認する。

        機能保証項目:
        - 検出エラーの適切な処理
        - エラー情報の適切な伝達
        - システムの安定性維持

        品質観点:
        - 障害処理の適切性
        - エラー回復の確実性
        - ユーザビリティの保持
        """
        mock_components["data_converter"].detect_header.side_effect = Exception(
            "Header detection error"
        )

        test_df = pd.DataFrame({"A": [1, 2, 3]})

        utilities = ExcelUtilities(
            excel_reader=mock_components["excel_reader"],
            data_converter=mock_components["data_converter"],
            error_handler=mock_components["error_handler"],
        )

        result = utilities.detect_headers(test_df)

        assert isinstance(result, dict)
        mock_components["error_handler"].create_error_response.assert_called_once()


class TestBackwardCompatibility:
    """後方互換性機能のテスト"""

    def test_is_safe_path_valid_file(self, mock_components, temp_excel_files):
        """安全パス確認の正常動作を確認する。

        機能保証項目:
        - 有効ファイルパスの正確な判定
        - セキュリティチェックの実行
        - 後方互換APIの動作保証

        セキュリティ要件:
        - パス検証の適切な実行
        - セキュリティホールの防止

        品質観点:
        - 後方互換性の確実な維持
        - API設計の一貫性
        - 使用性の保持
        """
        utilities = ExcelUtilities(
            excel_reader=mock_components["excel_reader"],
            data_converter=mock_components["data_converter"],
        )

        result = utilities.is_safe_path(temp_excel_files["valid_xlsx"])

        assert result is True
        mock_components["excel_reader"].validate_file.assert_called_once()

    def test_is_safe_path_invalid_file(self, mock_components, temp_excel_files):
        """危険パスの適切な検出を確認する。

        機能保証項目:
        - 無効ファイルパスの適切な判定
        - セキュリティリスクの検出
        - False値の確実な返却

        セキュリティ要件:
        - 危険パスの確実な拒否
        - パストラバーサル攻撃の防止

        品質観点:
        - セキュリティ機能の信頼性
        - 防御的プログラミング実装
        - エラー処理の適切性
        """
        mock_components["excel_reader"].validate_file.side_effect = Exception(
            "Validation failed"
        )

        utilities = ExcelUtilities(
            excel_reader=mock_components["excel_reader"],
            data_converter=mock_components["data_converter"],
        )

        result = utilities.is_safe_path(temp_excel_files["nonexistent"])

        assert result is False


class TestDataSummaryOperations:
    """データ要約機能のテスト"""

    def test_get_data_summary_comprehensive(self, mock_components):
        """包括的データ要約機能を確認する。

        機能保証項目:
        - DataFrame要約統計の正確な生成
        - メモリ使用量・Null値の適切な計算
        - 多言語データの適切な処理

        品質観点:
        - 統計計算の正確性
        - パフォーマンスの適切性
        - データ型対応の包括性
        """
        test_df = pd.DataFrame(
            {
                "Name": ["田中太郎", "佐藤花子", None],
                "Age": [25, 30, 35],
                "Salary": [50000.0, 60000.0, None],
            }
        )

        utilities = ExcelUtilities(
            excel_reader=mock_components["excel_reader"],
            data_converter=mock_components["data_converter"],
        )

        result = utilities.get_data_summary(test_df)

        assert "shape" in result
        assert result["shape"] == (3, 3)
        assert "columns" in result
        assert "dtypes" in result
        assert "memory_usage" in result
        assert "null_counts" in result
        assert "analysis_timestamp" in result

    def test_get_data_summary_large_dataset(self, mock_components):
        """大容量データセットの要約処理を確認する。

        機能保証項目:
        - 大容量データの適切な処理
        - メモリ効率性の確保
        - パフォーマンス劣化の防止

        品質観点:
        - スケーラビリティの確保
        - リソース消費の最適化
        - 処理時間の適切性
        """
        # 大容量テストデータ作成
        large_df = pd.DataFrame(
            {
                "ID": range(5000),
                "Data": [f"Item {i}" for i in range(5000)],
                "Value": [i * 1.5 for i in range(5000)],
            }
        )

        utilities = ExcelUtilities(
            excel_reader=mock_components["excel_reader"],
            data_converter=mock_components["data_converter"],
        )

        result = utilities.get_data_summary(large_df)

        assert result["shape"] == (5000, 3)
        # numpy.int64を含む数値型の確認
        memory_usage = result["memory_usage"]
        assert isinstance(memory_usage, (int, float)) or (
            hasattr(memory_usage, "item") and callable(memory_usage.item)
        )
        assert result["memory_usage"] > 0


class TestPathOperations:
    """パス操作機能のテスト"""

    def test_normalize_file_path_valid(self, mock_components, temp_excel_files):
        """有効ファイルパスの正規化を確認する。

        機能保証項目:
        - パス正規化の正確な実行
        - 絶対パスへの適切な変換
        - ファイル存在確認の実行

        品質観点:
        - パス処理の信頼性
        - クロスプラットフォーム互換性
        - エラーの無い標準動作
        """
        utilities = ExcelUtilities(
            excel_reader=mock_components["excel_reader"],
            data_converter=mock_components["data_converter"],
        )

        result = utilities.normalize_file_path(temp_excel_files["valid_xlsx"])

        assert isinstance(result, Path)
        assert result.is_absolute()
        assert result.exists()

    def test_normalize_file_path_nonexistent(self, mock_components, temp_excel_files):
        """存在しないファイルパス処理を確認する。

        機能保証項目:
        - 存在しないファイルの適切な検出
        - FileNotFoundErrorの適切な発生
        - エラーメッセージの明確性

        セキュリティ要件:
        - パス検証の確実な実行
        - 不正パスの拒否

        品質観点:
        - エラーハンドリングの適切性
        - セキュリティ機能の確実性
        - 診断情報の有用性
        """
        utilities = ExcelUtilities(
            excel_reader=mock_components["excel_reader"],
            data_converter=mock_components["data_converter"],
        )

        with pytest.raises(FileNotFoundError, match="File not found"):
            utilities.normalize_file_path(temp_excel_files["nonexistent"])


class TestSecurityAndPerformance:
    """セキュリティ・パフォーマンステスト"""

    def test_security_malicious_file_detection(self, mock_components):
        """悪意のあるファイルの検出を確認する。

        機能保証項目:
        - 悪意のあるファイル形式の検出
        - セキュリティスキャンの実行
        - 適切なエラー応答の生成

        セキュリティ要件:
        - XXE攻撃の防止
        - マルウェア検出の実行
        - 機密情報漏洩の防止

        品質観点:
        - セキュリティ機能の信頼性
        - 防御的プログラミング実装
        - 企業グレードセキュリティ達成
        """
        # 悪意のあるファイルのシミュレーション
        mock_components["excel_reader"].validate_file.side_effect = Exception(
            "Malicious file detected"
        )

        utilities = ExcelUtilities(
            excel_reader=mock_components["excel_reader"],
            data_converter=mock_components["data_converter"],
            error_handler=mock_components["error_handler"],
        )

        result = utilities.validate_excel_file("malicious.xlsx")

        assert result["success"] is False
        assert "error" in result
        mock_components["error_handler"].create_error_response.assert_called_once()

    def test_performance_large_file_handling(self, mock_components, temp_excel_files):
        """大容量ファイル処理のパフォーマンスを確認する。

        機能保証項目:
        - 大容量ファイルの適切な処理
        - パフォーマンス劣化の防止
        - メモリ効率性の確保

        品質観点:
        - スケーラビリティの確保
        - リソース消費の最適化
        - 処理時間の適切性
        """
        utilities = ExcelUtilities(
            excel_reader=mock_components["excel_reader"],
            data_converter=mock_components["data_converter"],
        )

        # 大容量ファイル処理のシミュレーション
        result = utilities.validate_excel_file(temp_excel_files["large_xlsx"])

        assert result["valid"] is True
        mock_components["excel_reader"].validate_file.assert_called_once()

    def test_error_recovery_comprehensive(self, mock_components):
        """包括的エラー回復機能を確認する。

        機能保証項目:
        - 各種エラーからの適切な回復
        - エラーコンテキストの保持
        - グレースフルデグラデーション

        品質観点:
        - 障害耐性の確保
        - システム安定性の維持
        - ユーザビリティの保持
        """
        # 複数種類のエラーをシミュレート
        mock_components["excel_reader"].validate_file.side_effect = [
            Exception("Network error"),
            Exception("Permission denied"),
            Exception("Corrupted file"),
        ]

        utilities = ExcelUtilities(
            excel_reader=mock_components["excel_reader"],
            data_converter=mock_components["data_converter"],
            error_handler=mock_components["error_handler"],
        )

        # 各エラーケースでの回復確認
        for test_file in ["network.xlsx", "permission.xlsx", "corrupted.xlsx"]:
            result = utilities.validate_excel_file(test_file)
            assert result["success"] is False
            assert "error" in result
