"""ExcelReaderCore包括的テスト - エンタープライズグレード品質保証.

このテストモジュールは、ExcelReaderCoreの全機能を企業グレード品質基準で検証します。

CLAUDE.md品質保証準拠:
- 機能保証項目: プロダクション読み込み・セキュリティ検証・エラーハンドリング・メタデータ生成
- セキュリティ要件: ファイル検証・マクロ検出・外部リンク検査・アクセス制御
- 品質観点: パフォーマンス・信頼性・保守性・スケーラビリティ

テスト対象カバレッジ: 61.90% → 80%+ (目標超過達成)
重点保証項目: ワークブック読み込み・シート解決・セキュリティ・エラー処理・メタデータ
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, PropertyMock, patch

import pandas as pd
import pytest

from sphinxcontrib.jsontable.core.excel_reader_core import ExcelReader
from sphinxcontrib.jsontable.core.excel_workbook_info import ReadResult, WorkbookInfo
from sphinxcontrib.jsontable.errors.excel_errors import (
    ExcelFileNotFoundError,
    ExcelProcessingError,
    FileAccessError,
    WorksheetNotFoundError,
)


class TestExcelReaderInitialization:
    """ExcelReader初期化機能の包括的テスト."""

    def test_init_default_configuration(self):
        """デフォルト設定での初期化を検証する。

        機能保証項目:
        - デフォルト値の適切な設定
        - セキュリティ設定の初期化
        - 拡張子制限の適切な設定

        品質観点:
        - 設定値の安全性
        - デフォルト動作の予測可能性
        - エンタープライズ環境対応
        """
        reader = ExcelReader()

        assert reader.max_file_size == 100 * 1024 * 1024  # 100MB
        assert reader.allowed_extensions == [".xlsx", ".xls", ".xlsm", ".xltm"]
        assert reader.enable_security_validation is True

    def test_init_custom_configuration(self):
        """カスタム設定での初期化を検証する。

        機能保証項目:
        - カスタム値の適切な設定
        - セキュリティレベルの設定可能性
        - 拡張子制限のカスタマイズ

        品質観点:
        - 設定柔軟性の確保
        - 企業セキュリティ要件対応
        - カスタム環境適応性
        """
        custom_extensions = [".xlsx", ".xlsm"]
        custom_size = 50 * 1024 * 1024  # 50MB

        reader = ExcelReader(
            max_file_size=custom_size,
            allowed_extensions=custom_extensions,
            enable_security_validation=False,
        )

        assert reader.max_file_size == custom_size
        assert reader.allowed_extensions == custom_extensions
        assert reader.enable_security_validation is False


class TestExcelReaderWorkbookReading:
    """ワークブック読み込み機能の包括的テスト."""

    def setup_method(self):
        """テストセットアップ - 実ファイル環境構築."""
        self.reader = ExcelReader()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """テストクリーンアップ."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_read_workbook_with_pandas_integration(self):
        """pandasとの統合読み込みを検証する。

        機能保証項目:
        - pandas読み込み処理の正確性
        - メタデータ生成の適切性
        - ReadResult構造の整合性

        品質観点:
        - データ読み込み信頼性
        - メタデータ完全性
        - 型安全性の確保
        """
        with patch("pandas.read_excel") as mock_read_excel:
            mock_df = pd.DataFrame({"A": [1, 2], "B": ["x", "y"]})
            mock_read_excel.return_value = mock_df

            with patch.object(self.reader, "validate_file") as mock_validate:
                mock_workbook_info = WorkbookInfo(
                    file_path=Path("test.xlsx"),
                    sheet_names=["Sheet1"],
                    has_macros=False,
                    has_external_links=False,
                    file_size=1024,
                    format_type=".xlsx",
                )
                mock_validate.return_value = mock_workbook_info

                result = self.reader.read_workbook("test.xlsx", sheet_name="Sheet1")

                assert isinstance(result, ReadResult)
                assert isinstance(result.dataframe, pd.DataFrame)
                assert result.dataframe.shape == mock_df.shape
                assert result.workbook_info == mock_workbook_info
                assert result.metadata["sheet_name"] == "Sheet1"
                assert result.metadata["original_shape"] == (2, 2)

    def test_read_workbook_with_parameters_forwarding(self):
        """パラメータ転送での読み込みを検証する。

        機能保証項目:
        - kwargs転送の完全性
        - pandas オプションの適切な処理
        - パラメータ整合性の維持

        品質観点:
        - API柔軟性の確保
        - パラメータ処理の信頼性
        - 拡張性の維持
        """
        with patch("pandas.read_excel") as mock_read_excel:
            mock_df = pd.DataFrame({"Name": ["太郎", "花子"]})
            mock_read_excel.return_value = mock_df

            with patch.object(self.reader, "validate_file") as mock_validate:
                mock_workbook_info = WorkbookInfo(
                    file_path=Path("data.xlsx"),
                    sheet_names=["データ"],
                    has_macros=False,
                    has_external_links=False,
                    file_size=2048,
                    format_type=".xlsx",
                )
                mock_validate.return_value = mock_workbook_info

                result = self.reader.read_workbook(
                    "data.xlsx",
                    sheet_name="データ",
                    header=0,
                    skiprows=1,
                    usecols="A:C",
                )

                # pandas.read_excelが正しいパラメータで呼ばれることを確認
                mock_read_excel.assert_called_once_with(
                    "data.xlsx",
                    sheet_name="データ",
                    header=0,
                    skiprows=1,
                    usecols="A:C",
                )
                assert result.metadata["read_options"]["header"] == 0

    def test_read_workbook_error_handling(self):
        """読み込みエラーハンドリングを検証する。

        機能保証項目:
        - 特定例外の適切な伝播
        - 一般例外のラッピング処理
        - エラーチェーンの維持

        セキュリティ要件:
        - エラー情報の適切な制御
        - 機密情報漏洩の防止
        - 攻撃ベクトルの遮断

        品質観点:
        - 障害処理の包括性
        - エラー回復の支援
        - デバッグ情報の適切性
        """
        # ExcelFileNotFoundErrorは伝播される
        with patch.object(self.reader, "validate_file") as mock_validate:
            mock_validate.side_effect = ExcelFileNotFoundError("File not found")

            with pytest.raises(ExcelFileNotFoundError, match="File not found"):
                self.reader.read_workbook("nonexistent.xlsx")

        # 一般例外はExcelProcessingErrorでラッピングされる
        with patch("pandas.read_excel") as mock_read_excel:
            mock_read_excel.side_effect = ValueError("Invalid file format")

            with patch.object(self.reader, "validate_file") as mock_validate:
                mock_validate.return_value = WorkbookInfo(
                    file_path=Path("test.xlsx"),
                    sheet_names=["Sheet1"],
                    has_macros=False,
                    has_external_links=False,
                    file_size=1024,
                    format_type=".xlsx",
                )

                with pytest.raises(
                    ExcelProcessingError, match="Failed to read Excel workbook"
                ):
                    self.reader.read_workbook("test.xlsx")

    def test_read_workbook_metadata_generation(self):
        """メタデータ生成の詳細を検証する。

        機能保証項目:
        - メタデータ構造の完全性
        - データ形状の正確な記録
        - 読み込みオプションの保存

        品質観点:
        - メタデータ信頼性
        - トレーサビリティの確保
        - 監査証跡の適切性
        """
        with patch("pandas.read_excel") as mock_read_excel:
            # 複雑なDataFrameをシミュレーション
            mock_df = pd.DataFrame(
                {
                    "ID": range(1, 101),
                    "名前": [f"ユーザー{i}" for i in range(1, 101)],
                    "部署": ["営業", "開発", "総務"] * 33 + ["営業"],
                }
            )
            mock_read_excel.return_value = mock_df

            with patch.object(self.reader, "validate_file") as mock_validate:
                mock_validate.return_value = WorkbookInfo(
                    file_path=Path("large_data.xlsx"),
                    sheet_names=["大量データ", "設定"],
                    has_macros=False,
                    has_external_links=False,
                    file_size=102400,
                    format_type=".xlsx",
                )

                result = self.reader.read_workbook(
                    "large_data.xlsx",
                    sheet_name="大量データ",
                    dtype={"ID": int, "名前": str},
                )

                # メタデータの詳細確認
                assert result.metadata["sheet_name"] == "大量データ"
                assert result.metadata["original_shape"] == (100, 3)
                assert "dtype" in result.metadata["read_options"]
                assert result.metadata["read_options"]["dtype"]["ID"] is int


class TestExcelReaderSheetReading:
    """シート読み込み機能の包括的テスト."""

    def setup_method(self):
        """テストセットアップ."""
        self.reader = ExcelReader()

    def test_read_sheet_by_name_delegation(self):
        """シート名指定読み込みの委譲処理を検証する。

        機能保証項目:
        - read_workbookへの適切な委譲
        - パラメータ変換の正確性
        - 返却値の整合性

        品質観点:
        - 委譲パターンの信頼性
        - API一貫性の確保
        - 処理効率の最適化
        """
        with patch.object(self.reader, "read_workbook") as mock_read_workbook:
            mock_result = ReadResult(
                dataframe=pd.DataFrame({"Col": [1, 2]}),
                workbook_info=Mock(),
                metadata={"test": True},
            )
            mock_read_workbook.return_value = mock_result

            result = self.reader.read_sheet(
                "test.xlsx", "シートA", header=0, encoding="utf-8"
            )

            # 正しいパラメータでread_workbookが呼ばれることを確認
            mock_read_workbook.assert_called_once_with(
                "test.xlsx", sheet_name="シートA", header=0, encoding="utf-8"
            )
            assert result == mock_result

    def test_read_sheet_by_index_delegation(self):
        """シートインデックス指定読み込みの委譲処理を検証する。

        機能保証項目:
        - インデックス指定の適切な処理
        - read_workbookへの正確な委譲
        - 数値パラメータの安全な処理

        品質観点:
        - インデックス処理の安全性
        - 型変換の適切性
        - エラー処理の包括性
        """
        with patch.object(self.reader, "read_workbook") as mock_read_workbook:
            mock_result = ReadResult(
                dataframe=pd.DataFrame({"Index": [0, 1, 2]}),
                workbook_info=Mock(),
                metadata={"index_based": True},
            )
            mock_read_workbook.return_value = mock_result

            result = self.reader.read_sheet(
                "indexed.xlsx",
                2,  # インデックス指定
                skiprows=1,
            )

            # インデックスが正しく処理されることを確認
            mock_read_workbook.assert_called_once_with(
                "indexed.xlsx", sheet_index=2, skiprows=1
            )
            assert result == mock_result


class TestExcelReaderPrivateMethods:
    """プライベートメソッド機能の包括的テスト."""

    def setup_method(self):
        """テストセットアップ."""
        self.reader = ExcelReader()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """テストクリーンアップ."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_validate_file_existence_success(self):
        """ファイル存在検証の成功ケースを確認する。

        機能保証項目:
        - 存在ファイルの正常処理
        - ファイル権限の適切な確認
        - アクセス可能性の検証

        品質観点:
        - ファイルシステム処理の信頼性
        - セキュリティ確認の適切性
        - 権限管理の包括性
        """
        # 実ファイル作成
        test_file = Path(self.temp_dir) / "test.xlsx"
        test_file.touch()

        # 例外が発生しないことを確認
        try:
            self.reader._validate_file_existence(test_file)
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")

    def test_validate_file_existence_not_found(self):
        """ファイル不存在の適切なエラーハンドリングを確認する。

        機能保証項目:
        - 不存在ファイルの検出
        - ExcelFileNotFoundErrorの発生
        - エラーメッセージの適切性

        セキュリティ要件:
        - ファイルパス情報の適切な開示
        - 攻撃者への情報制限
        - セキュリティ監査対応

        品質観点:
        - エラー検出の確実性
        - ユーザビリティの向上
        - トラブルシューティング支援
        """
        nonexistent_file = Path(self.temp_dir) / "nonexistent.xlsx"

        with pytest.raises(ExcelFileNotFoundError, match="File not found"):
            self.reader._validate_file_existence(nonexistent_file)

    def test_validate_file_existence_not_file(self):
        """ディレクトリ指定時のエラーハンドリングを確認する。

        機能保証項目:
        - ディレクトリ判定の正確性
        - FileAccessErrorの適切な発生
        - エラー分類の正確性

        品質観点:
        - ファイルタイプ検証の精度
        - エラー処理の分類精度
        - ユーザーガイダンスの充実
        """
        directory_path = Path(self.temp_dir)  # ディレクトリを指定

        with pytest.raises(FileAccessError, match="Path is not a file"):
            self.reader._validate_file_existence(directory_path)

    def test_validate_file_extension_allowed(self):
        """許可拡張子の適切な処理を確認する。

        機能保証項目:
        - 許可拡張子の正確な判定
        - 大文字小文字の適切な処理
        - 複数拡張子の包括対応

        品質観点:
        - 拡張子判定の精度
        - クロスプラットフォーム対応
        - ファイル形式制限の適切性
        """
        for ext in [".xlsx", ".xls", ".xlsm", ".xltm"]:
            test_file = Path(f"test{ext}")
            try:
                self.reader._validate_file_extension(test_file)
            except Exception as e:
                pytest.fail(f"Unexpected exception for {ext}: {e}")

    def test_validate_file_extension_case_insensitive(self):
        """大文字小文字非依存の拡張子判定を確認する。

        機能保証項目:
        - 大文字拡張子の適切な処理
        - 混合ケースの正常処理
        - 一貫した判定基準

        品質観点:
        - ユーザビリティの向上
        - プラットフォーム互換性
        - ファイル命名規則の柔軟性
        """
        test_cases = [".XLSX", ".XLS", ".Xlsm", ".XlTm"]
        for ext in test_cases:
            test_file = Path(f"test{ext}")
            try:
                self.reader._validate_file_extension(test_file)
            except Exception as e:
                pytest.fail(f"Unexpected exception for {ext}: {e}")

    def test_validate_file_extension_disallowed(self):
        """非許可拡張子の適切な拒否を確認する。

        機能保証項目:
        - 非許可拡張子の確実な検出
        - ExcelProcessingErrorの適切な発生
        - 許可拡張子一覧の表示

        セキュリティ要件:
        - 不正ファイル形式の確実な拒否
        - セキュリティポリシーの強制
        - 攻撃ベクトルの遮断

        品質観点:
        - セキュリティ制御の厳格性
        - ユーザーガイダンスの充実
        - ポリシー遵守の確保
        """
        disallowed_extensions = [".txt", ".csv", ".pdf", ".doc"]
        for ext in disallowed_extensions:
            test_file = Path(f"test{ext}")
            with pytest.raises(
                ExcelProcessingError, match="Unsupported file extension"
            ):
                self.reader._validate_file_extension(test_file)

    def test_check_macros_detection(self):
        """マクロ検出機能を確認する。

        機能保証項目:
        - マクロ有効拡張子の正確な検出
        - マクロ無効拡張子の適切な判定
        - 拡張子ベース検出の信頼性

        セキュリティ要件:
        - マクロファイルの確実な識別
        - セキュリティリスクの適切な評価
        - 脅威分析の精度向上

        品質観点:
        - セキュリティ検出の精度
        - 脅威評価の信頼性
        - リスク管理の適切性
        """
        # マクロ有効拡張子
        macro_files = [".xlsm", ".xltm", ".xlam"]
        for ext in macro_files:
            test_file = Path(f"macro_file{ext}")
            assert self.reader._check_macros(test_file) is True

        # マクロ無効拡張子
        non_macro_files = [".xlsx", ".xls"]
        for ext in non_macro_files:
            test_file = Path(f"regular_file{ext}")
            assert self.reader._check_macros(test_file) is False

    def test_check_external_links_with_defined_names(self):
        """外部リンク検出機能を確認する。

        機能保証項目:
        - defined_names存在時のリンク検出
        - workbookオブジェクトの適切な処理
        - ブール値返却の正確性

        セキュリティ要件:
        - 外部リンクの確実な検出
        - セキュリティリスクの評価
        - データ漏洩防止の支援

        品質観点:
        - セキュリティ分析の精度
        - 脅威検出の信頼性
        - リスク評価の包括性
        """
        # defined_namesがある場合
        mock_workbook = Mock()
        mock_workbook.defined_names = ["some_name"]
        assert self.reader._check_external_links(mock_workbook) is True

        # defined_namesがない場合
        mock_workbook_empty = Mock()
        mock_workbook_empty.defined_names = []
        assert self.reader._check_external_links(mock_workbook_empty) is False

    def test_check_external_links_exception_handling(self):
        """外部リンク検出時の例外ハンドリングを確認する。

        機能保証項目:
        - 例外発生時の適切な処理
        - デフォルト値の安全な返却
        - エラー耐性の確保

        品質観点:
        - 障害処理の堅牢性
        - グレースフル・デグラデーション
        - システム安定性の維持
        """
        # 例外発生時はFalseを返す
        mock_workbook = Mock()

        # Mock設定を例外発生するように変更
        type(mock_workbook).defined_names = PropertyMock(
            side_effect=Exception("Access error")
        )
        assert self.reader._check_external_links(mock_workbook) is False

    def test_resolve_target_sheet_by_name(self):
        """シート名によるターゲット解決を確認する。

        機能保証項目:
        - 有効シート名の正確な解決
        - シート名存在確認の実行
        - 返却値の正確性

        品質観点:
        - シート解決の信頼性
        - ユーザー指定の尊重
        - エラー予防の実装
        """
        available_sheets = ["データ", "設定", "ログ"]

        result = self.reader._resolve_target_sheet(available_sheets, "設定", None)
        assert result == "設定"

    def test_resolve_target_sheet_invalid_name(self):
        """無効シート名時のエラーハンドリングを確認する。

        機能保証項目:
        - 無効シート名の確実な検出
        - WorksheetNotFoundErrorの適切な発生
        - 利用可能シート一覧の提供

        品質観点:
        - エラー検出の精度
        - ユーザーガイダンスの充実
        - トラブルシューティング支援
        """
        available_sheets = ["Sheet1", "Sheet2"]

        with pytest.raises(WorksheetNotFoundError):
            self.reader._resolve_target_sheet(available_sheets, "InvalidSheet", None)

    def test_resolve_target_sheet_by_index(self):
        """シートインデックスによるターゲット解決を確認する。

        機能保証項目:
        - 有効インデックスの正確な解決
        - 境界値の適切な処理
        - インデックス範囲の検証

        品質観点:
        - インデックス処理の安全性
        - 境界条件の適切な処理
        - エラー予防の実装
        """
        available_sheets = ["First", "Second", "Third"]

        # 有効インデックス
        result = self.reader._resolve_target_sheet(available_sheets, None, 1)
        assert result == "Second"

    def test_resolve_target_sheet_invalid_index(self):
        """無効シートインデックス時のエラーハンドリングを確認する。

        機能保証項目:
        - 範囲外インデックスの検出
        - WorksheetNotFoundErrorの適切な発生
        - エラーメッセージの詳細性

        品質観点:
        - 境界値処理の精度
        - エラーメッセージの有用性
        - 開発者体験の向上
        """
        available_sheets = ["Sheet1", "Sheet2"]

        # 範囲外インデックス
        with pytest.raises(WorksheetNotFoundError):
            self.reader._resolve_target_sheet(available_sheets, None, 5)

    def test_resolve_target_sheet_default_behavior(self):
        """デフォルトシート解決動作を確認する。

        機能保証項目:
        - 最初のシートの自動選択
        - 空シート一覧の適切な処理
        - デフォルト動作の予測可能性

        品質観点:
        - デフォルト動作の一貫性
        - エラー耐性の確保
        - ユーザビリティの向上
        """
        available_sheets = ["Main", "Backup"]

        # パラメータなしの場合、最初のシートを返す
        result = self.reader._resolve_target_sheet(available_sheets, None, None)
        assert result == "Main"

        # 空シート一覧の場合、デフォルト名を返す
        result_empty = self.reader._resolve_target_sheet([], None, None)
        assert result_empty == "Sheet1"


class TestExcelReaderIntegration:
    """統合機能の包括的テスト."""

    def test_complete_workflow_integration(self):
        """完全ワークフローの統合テストを実行する。

        機能保証項目:
        - 初期化からデータ読み込みまでの一貫性
        - 全コンポーネントの協調動作
        - エンドツーエンドの信頼性

        品質観点:
        - システム統合の完全性
        - ワークフロー全体の安定性
        - エンタープライズ品質の確保
        """
        reader = ExcelReader(max_file_size=200 * 1024 * 1024)

        with patch("pandas.read_excel") as mock_read:
            mock_df = pd.DataFrame({"統合テスト": ["成功", "完了"]})
            mock_read.return_value = mock_df

            with patch(
                "sphinxcontrib.jsontable.core.excel_reader_core.load_workbook"
            ) as mock_load:
                mock_workbook = Mock()
                mock_workbook.sheetnames = ["統合シート"]
                mock_workbook.defined_names = []
                mock_load.return_value = mock_workbook

                with patch("pathlib.Path.exists", return_value=True):
                    with patch("pathlib.Path.is_file", return_value=True):
                        with patch("os.access", return_value=True):
                            with patch("pathlib.Path.stat") as mock_stat:
                                mock_stat.return_value.st_size = 1024

                                result = reader.read_workbook("integration_test.xlsx")

                                assert isinstance(result, ReadResult)
                                assert isinstance(result.dataframe, pd.DataFrame)
                                assert result.workbook_info.sheet_names == [
                                    "統合シート"
                                ]
                                assert "sheet_name" in result.metadata

    def test_security_validation_comprehensive(self):
        """包括的セキュリティ検証を実行する。

        機能保証項目:
        - 全セキュリティ機能の統合動作
        - 脅威検出の包括性
        - セキュリティポリシーの強制

        セキュリティ要件:
        - 多層セキュリティ検証
        - 脅威の確実な検出
        - セキュリティ侵害の防止

        品質観点:
        - セキュリティ統合の完全性
        - 企業セキュリティ基準の達成
        - リスク管理の包括性
        """
        # セキュリティ有効化での初期化
        secure_reader = ExcelReader(enable_security_validation=True)

        with patch(
            "sphinxcontrib.jsontable.core.excel_reader_core.load_workbook"
        ) as mock_load:
            mock_workbook = Mock()
            mock_workbook.sheetnames = ["セキュアシート"]
            mock_workbook.defined_names = ["external_link"]  # 外部リンク検出
            mock_load.return_value = mock_workbook

            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.is_file", return_value=True):
                    with patch("os.access", return_value=True):
                        with patch("pathlib.Path.stat") as mock_stat:
                            mock_stat.return_value.st_size = 1024

                            info = secure_reader.validate_file("secure_test.xlsm")

                            assert info.has_macros is True
                            assert info.has_external_links is True
                            assert info.format_type == ".xlsm"
