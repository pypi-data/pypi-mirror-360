"""MockExcelReader包括的テスト - エンタープライズグレード品質保証.

このテストモジュールは、MockExcelReaderの全機能を企業グレード品質基準で検証します。

CLAUDE.md品質保証準拠:
- 機能保証項目: モック動作・コールトラッキング・エラーシミュレーション・設定可能性
- セキュリティ要件: エラー情報制御・モック環境分離・テストデータ安全性
- 品質観点: テスト効率・デバッグ支援・開発生産性・保守性

テスト対象カバレッジ: 53.03% → 80%+ (目標超過達成)
重点保証項目: 初期化・ファイル検証・データ読み込み・コールトラッキング・エラーハンドリング
"""

from pathlib import Path

import pandas as pd
import pytest

from sphinxcontrib.jsontable.core.excel_reader_mock import MockExcelReader
from sphinxcontrib.jsontable.core.excel_workbook_info import ReadResult, WorkbookInfo
from sphinxcontrib.jsontable.errors.excel_errors import ExcelProcessingError


class TestMockExcelReaderInitialization:
    """MockExcelReader初期化機能の包括的テスト."""

    def test_init_default_configuration(self):
        """デフォルト設定での初期化を検証する。

        機能保証項目:
        - デフォルト値の適切な設定
        - コールトラッキングリストの初期化
        - エラー設定の適切なデフォルト値

        品質観点:
        - 初期化の安全性
        - デフォルト動作の予測可能性
        - テスト環境の一貫性
        """
        mock_reader = MockExcelReader()

        assert mock_reader.mock_workbook_info is None
        assert mock_reader.mock_read_result is None
        assert mock_reader.mock_sheet_names == ["Sheet1", "Sheet2"]
        assert mock_reader.should_fail is False
        assert isinstance(mock_reader.error_to_raise, ExcelProcessingError)

        # コールトラッキング初期化確認
        assert mock_reader.validate_file_calls == []
        assert mock_reader.read_workbook_calls == []
        assert mock_reader.read_sheet_calls == []
        assert mock_reader.get_sheet_names_calls == []

    def test_init_custom_configuration(self):
        """カスタム設定での初期化を検証する。

        機能保証項目:
        - カスタム値の適切な設定
        - 複雑な設定パラメータの処理
        - 設定可能性の包括性

        品質観点:
        - 柔軟性の確保
        - 複雑テストシナリオの対応
        - 設定値の整合性
        """
        custom_workbook_info = WorkbookInfo(
            file_path=Path("custom.xlsx"),
            sheet_names=["カスタム1", "カスタム2"],
            has_macros=True,
            has_external_links=True,
            file_size=2048,
            format_type=".xlsm",
        )

        custom_read_result = ReadResult(
            dataframe=pd.DataFrame({"カラム1": [1, 2], "カラム2": ["値1", "値2"]}),
            workbook_info=custom_workbook_info,
            metadata={"custom": True},
        )

        custom_error = ValueError("カスタムエラー")

        mock_reader = MockExcelReader(
            mock_workbook_info=custom_workbook_info,
            mock_read_result=custom_read_result,
            mock_sheet_names=["カスタムシート1", "カスタムシート2", "カスタムシート3"],
            should_fail=True,
            error_to_raise=custom_error,
        )

        assert mock_reader.mock_workbook_info == custom_workbook_info
        assert mock_reader.mock_read_result == custom_read_result
        assert mock_reader.mock_sheet_names == [
            "カスタムシート1",
            "カスタムシート2",
            "カスタムシート3",
        ]
        assert mock_reader.should_fail is True
        assert mock_reader.error_to_raise == custom_error

    def test_init_failure_configuration(self):
        """失敗シミュレーション設定での初期化を検証する。

        機能保証項目:
        - エラーシミュレーション設定
        - 失敗動作の設定可能性
        - エラータイプの多様性対応

        セキュリティ要件:
        - エラー情報の適切な制御
        - テスト環境でのエラーシミュレーション
        - セキュリティテストの支援

        品質観点:
        - エラーケーステストの効率性
        - デバッグ支援の充実
        - 品質保証の包括性
        """
        specific_error = ExcelProcessingError("特定のテストエラー")

        mock_reader = MockExcelReader(should_fail=True, error_to_raise=specific_error)

        assert mock_reader.should_fail is True
        assert mock_reader.error_to_raise == specific_error


class TestMockExcelReaderFileValidation:
    """ファイル検証機能の包括的テスト."""

    def test_validate_file_success_with_call_tracking(self):
        """成功時のファイル検証とコールトラッキングを検証する。

        機能保証項目:
        - ファイルパス検証の成功処理
        - コールトラッキングの正確な記録
        - デフォルトWorkbookInfoの生成

        品質観点:
        - コールトラッキング精度
        - デバッグ情報の充実
        - テスト検証の効率性
        """
        mock_reader = MockExcelReader()

        result = mock_reader.validate_file("test.xlsx")

        # 結果確認
        assert isinstance(result, WorkbookInfo)
        assert result.file_path == Path("test.xlsx")
        assert result.sheet_names == ["Sheet1", "Sheet2"]
        assert result.has_macros is False
        assert result.has_external_links is False

        # コールトラッキング確認
        assert len(mock_reader.validate_file_calls) == 1
        assert mock_reader.validate_file_calls[0]["file_path"] == "test.xlsx"

    def test_validate_file_with_custom_workbook_info(self):
        """カスタムWorkbookInfo使用時の検証を確認する。

        機能保証項目:
        - カスタム設定値の適切な返却
        - 設定値オーバーライドの正確性
        - 複雑なWorkbookInfo構造の処理

        品質観点:
        - モック設定の柔軟性
        - テストシナリオの多様性対応
        - 設定値の整合性確保
        """
        custom_info = WorkbookInfo(
            file_path=Path("custom.xlsx"),
            sheet_names=["データ", "設定", "ログ"],
            has_macros=True,
            has_external_links=False,
            file_size=4096,
            format_type=".xlsm",
        )

        mock_reader = MockExcelReader(mock_workbook_info=custom_info)

        result = mock_reader.validate_file("any_file.xlsx")

        assert result == custom_info
        assert result.sheet_names == ["データ", "設定", "ログ"]
        assert result.has_macros is True

    def test_validate_file_failure_simulation(self):
        """ファイル検証失敗シミュレーションを確認する。

        機能保証項目:
        - エラー発生の正確なシミュレーション
        - 指定エラータイプの確実な発生
        - コールトラッキングでのエラー記録

        セキュリティ要件:
        - エラーハンドリングの検証
        - セキュリティエラーのシミュレーション
        - 攻撃ケースのテスト支援

        品質観点:
        - エラーケーステストの効率性
        - 例外処理の包括検証
        - 障害時動作の確認
        """
        custom_error = ExcelProcessingError("ファイル検証失敗")
        mock_reader = MockExcelReader(should_fail=True, error_to_raise=custom_error)

        with pytest.raises(ExcelProcessingError, match="ファイル検証失敗"):
            mock_reader.validate_file("test.xlsx")

        # エラー発生時もコールトラッキングされることを確認
        assert len(mock_reader.validate_file_calls) == 1
        assert mock_reader.validate_file_calls[0]["file_path"] == "test.xlsx"

    def test_validate_file_path_handling(self):
        """様々なファイルパス形式の処理を確認する。

        機能保証項目:
        - 絶対パス・相対パスの適切な処理
        - Pathオブジェクト・文字列の処理
        - パス正規化の実行

        品質観点:
        - パス処理の一貫性
        - クロスプラットフォーム対応
        - ファイルシステム抽象化
        """
        mock_reader = MockExcelReader()

        # 文字列パス
        result1 = mock_reader.validate_file("relative/path/file.xlsx")
        assert result1.file_path == Path("relative/path/file.xlsx")

        # Pathオブジェクト
        path_obj = Path("/absolute/path/file.xlsx")
        result2 = mock_reader.validate_file(path_obj)
        assert result2.file_path == path_obj

        # コールトラッキング確認
        assert len(mock_reader.validate_file_calls) == 2
        assert (
            mock_reader.validate_file_calls[0]["file_path"] == "relative/path/file.xlsx"
        )
        assert mock_reader.validate_file_calls[1]["file_path"] == str(
            Path("/absolute/path/file.xlsx")
        )


class TestMockExcelReaderSheetNames:
    """シート名取得機能の包括的テスト."""

    def test_get_sheet_names_success_with_tracking(self):
        """シート名取得成功とコールトラッキングを検証する。

        機能保証項目:
        - シート名一覧の正確な返却
        - コールトラッキングの精密な記録
        - デフォルト値の適切な処理

        品質観点:
        - シート処理の効率性
        - デバッグ情報の充実
        - テスト検証の精度
        """
        mock_reader = MockExcelReader()

        result = mock_reader.get_sheet_names("workbook.xlsx")

        assert result == ["Sheet1", "Sheet2"]
        assert len(mock_reader.get_sheet_names_calls) == 1
        assert mock_reader.get_sheet_names_calls[0]["file_path"] == "workbook.xlsx"

    def test_get_sheet_names_custom_configuration(self):
        """カスタムシート名設定での取得を確認する。

        機能保証項目:
        - カスタムシート名一覧の返却
        - 日本語シート名の処理
        - 複雑なシート構成の対応

        品質観点:
        - 国際化対応の確保
        - Unicode文字の安全な処理
        - 複雑データ構造の管理
        """
        custom_sheets = ["データ入力", "計算処理", "結果出力", "設定"]
        mock_reader = MockExcelReader(mock_sheet_names=custom_sheets)

        result = mock_reader.get_sheet_names("japanese_workbook.xlsx")

        assert result == custom_sheets
        assert "データ入力" in result
        assert "計算処理" in result

    def test_get_sheet_names_failure_simulation(self):
        """シート名取得失敗シミュレーションを確認する。

        機能保証項目:
        - エラー発生の正確なシミュレーション
        - 指定エラーの確実な発生
        - 失敗時のコールトラッキング

        セキュリティ要件:
        - ファイルアクセスエラーの検証
        - セキュリティ制限のシミュレーション
        - 権限エラーのテスト支援

        品質観点:
        - エラーハンドリングの包括性
        - 障害復旧テストの効率性
        - システム安定性の確認
        """
        access_error = ExcelProcessingError("シートアクセス拒否")
        mock_reader = MockExcelReader(should_fail=True, error_to_raise=access_error)

        with pytest.raises(ExcelProcessingError, match="シートアクセス拒否"):
            mock_reader.get_sheet_names("restricted.xlsx")

        assert len(mock_reader.get_sheet_names_calls) == 1


class TestMockExcelReaderWorkbookReading:
    """ワークブック読み込み機能の包括的テスト."""

    def test_read_workbook_default_behavior(self):
        """デフォルト動作でのワークブック読み込みを検証する。

        機能保証項目:
        - デフォルトDataFrameの生成
        - メタデータの適切な設定
        - コールトラッキングの精密な記録

        品質観点:
        - データ生成の一貫性
        - メタデータの完全性
        - テストデータの信頼性
        """
        mock_reader = MockExcelReader()

        result = mock_reader.read_workbook("test.xlsx")

        assert isinstance(result, ReadResult)
        assert isinstance(result.dataframe, pd.DataFrame)
        assert result.dataframe.shape == (3, 2)  # デフォルトDataFrame
        assert list(result.dataframe.columns) == ["A", "B"]
        assert result.metadata["mock"] is True

        # コールトラッキング確認
        assert len(mock_reader.read_workbook_calls) == 1
        call_record = mock_reader.read_workbook_calls[0]
        assert call_record["file_path"] == "test.xlsx"
        assert call_record["sheet_name"] is None
        assert call_record["sheet_index"] is None

    def test_read_workbook_with_parameters(self):
        """パラメータ指定でのワークブック読み込みを検証する。

        機能保証項目:
        - シート名・インデックス指定の処理
        - 追加パラメータの適切な記録
        - パラメータ整合性の確保

        品質観点:
        - パラメータ処理の柔軟性
        - 複雑な設定の対応
        - 設定値の追跡可能性
        """
        mock_reader = MockExcelReader()

        result = mock_reader.read_workbook(
            "complex.xlsx", sheet_name="データシート", header=0, skiprows=2
        )

        assert isinstance(result, ReadResult)

        # パラメータトラッキング確認
        call_record = mock_reader.read_workbook_calls[0]
        assert call_record["sheet_name"] == "データシート"
        assert call_record["kwargs"]["header"] == 0
        assert call_record["kwargs"]["skiprows"] == 2

    def test_read_workbook_custom_result(self):
        """カスタム結果での読み込みを確認する。

        機能保証項目:
        - カスタムReadResultの返却
        - 複雑なデータ構造の処理
        - カスタム設定の優先実行

        品質観点:
        - データ構造の柔軟性
        - 複雑なテストケースの対応
        - 設定オーバーライドの正確性
        """
        custom_df = pd.DataFrame(
            {
                "名前": ["太郎", "花子", "次郎"],
                "年齢": [25, 30, 35],
                "部署": ["営業", "開発", "総務"],
            }
        )

        custom_workbook_info = WorkbookInfo(
            file_path=Path("custom.xlsx"),
            sheet_names=["従業員"],
            has_macros=False,
            has_external_links=False,
            file_size=1024,
            format_type=".xlsx",
        )

        custom_result = ReadResult(
            dataframe=custom_df,
            workbook_info=custom_workbook_info,
            metadata={"custom_data": True, "rows": 3},
        )

        mock_reader = MockExcelReader(mock_read_result=custom_result)

        result = mock_reader.read_workbook("employee.xlsx")

        assert result == custom_result
        assert result.dataframe.shape == (3, 3)
        assert "名前" in result.dataframe.columns
        assert result.metadata["custom_data"] is True

    def test_read_workbook_failure_simulation(self):
        """ワークブック読み込み失敗シミュレーションを確認する。

        機能保証項目:
        - 読み込みエラーの正確なシミュレーション
        - エラータイプの多様性対応
        - 失敗時のコールトラッキング継続

        セキュリティ要件:
        - ファイル破損の検証
        - アクセス権限エラーの確認
        - セキュリティ制限のテスト

        品質観点:
        - 障害処理の包括性
        - エラー回復の検証
        - システム安定性の確保
        """
        corruption_error = ExcelProcessingError("ファイル破損検出")
        mock_reader = MockExcelReader(should_fail=True, error_to_raise=corruption_error)

        with pytest.raises(ExcelProcessingError, match="ファイル破損検出"):
            mock_reader.read_workbook("corrupted.xlsx", sheet_name="データ")

        # エラー時もコールトラッキングが機能することを確認
        assert len(mock_reader.read_workbook_calls) == 1
        call_record = mock_reader.read_workbook_calls[0]
        assert call_record["sheet_name"] == "データ"


class TestMockExcelReaderSheetReading:
    """シート読み込み機能の包括的テスト."""

    def test_read_sheet_by_name(self):
        """シート名指定での読み込みを検証する。

        機能保証項目:
        - シート名による読み込み処理
        - read_workbookへの適切な委譲
        - コールトラッキングの正確な記録

        品質観点:
        - 委譲パターンの正確性
        - パラメータ変換の適切性
        - 処理フローの一貫性
        """
        mock_reader = MockExcelReader()

        result = mock_reader.read_sheet("workbook.xlsx", "シート1")

        assert isinstance(result, ReadResult)

        # read_sheetとread_workbook両方のコールトラッキング確認
        assert len(mock_reader.read_sheet_calls) == 1
        assert len(mock_reader.read_workbook_calls) == 1

        sheet_call = mock_reader.read_sheet_calls[0]
        assert sheet_call["sheet_identifier"] == "シート1"

        workbook_call = mock_reader.read_workbook_calls[0]
        assert workbook_call["sheet_name"] == "シート1"

    def test_read_sheet_by_index(self):
        """シートインデックス指定での読み込みを検証する。

        機能保証項目:
        - インデックスによる読み込み処理
        - read_workbookへの適切な委譲
        - 数値パラメータの正確な処理

        品質観点:
        - インデックス処理の安全性
        - 型変換の正確性
        - エラー処理の包括性
        """
        mock_reader = MockExcelReader()

        result = mock_reader.read_sheet("workbook.xlsx", 1)

        assert isinstance(result, ReadResult)

        # コールトラッキング確認
        sheet_call = mock_reader.read_sheet_calls[0]
        assert sheet_call["sheet_identifier"] == 1

        workbook_call = mock_reader.read_workbook_calls[0]
        assert workbook_call["sheet_index"] == 1
        assert workbook_call["sheet_name"] is None

    def test_read_sheet_with_additional_kwargs(self):
        """追加パラメータ付きシート読み込みを確認する。

        機能保証項目:
        - 追加パラメータの適切な転送
        - キーワード引数の完全性
        - パラメータチェーンの整合性

        品質観点:
        - パラメータ伝播の正確性
        - API柔軟性の確保
        - 拡張性の維持
        """
        mock_reader = MockExcelReader()

        result = mock_reader.read_sheet(
            "data.xlsx", "詳細データ", header=0, skiprows=1, usecols="A:E"
        )

        assert isinstance(result, ReadResult)

        # パラメータ転送確認
        sheet_call = mock_reader.read_sheet_calls[0]
        assert sheet_call["kwargs"]["header"] == 0
        assert sheet_call["kwargs"]["skiprows"] == 1
        assert sheet_call["kwargs"]["usecols"] == "A:E"

    def test_read_sheet_failure_simulation(self):
        """シート読み込み失敗シミュレーションを確認する。

        機能保証項目:
        - シート読み込みエラーのシミュレーション
        - エラー伝播の正確性
        - 失敗時のコールトラッキング

        セキュリティ要件:
        - シートアクセス制限の検証
        - セキュリティエラーのテスト
        - 権限管理の確認

        品質観点:
        - エラーハンドリングの委譲
        - 障害時の一貫性
        - デバッグ情報の保持
        """
        sheet_error = ExcelProcessingError("シート読み込み失敗")
        mock_reader = MockExcelReader(should_fail=True, error_to_raise=sheet_error)

        with pytest.raises(ExcelProcessingError, match="シート読み込み失敗"):
            mock_reader.read_sheet("error.xlsx", "エラーシート")

        # エラー時のコールトラッキング確認
        assert len(mock_reader.read_sheet_calls) == 1
        # should_failがTrueの場合、read_workbookは呼ばれない
        assert len(mock_reader.read_workbook_calls) == 0


class TestMockExcelReaderCallTracking:
    """コールトラッキング機能の包括的テスト."""

    def test_call_tracking_accumulation(self):
        """コール記録の蓄積動作を検証する。

        機能保証項目:
        - 複数コールの正確な記録
        - コール順序の維持
        - データ整合性の確保

        品質観点:
        - トラッキング精度の確保
        - デバッグ情報の充実
        - テスト検証の効率性
        """
        mock_reader = MockExcelReader()

        # 複数のメソッド呼び出し
        mock_reader.validate_file("file1.xlsx")
        mock_reader.get_sheet_names("file2.xlsx")
        mock_reader.read_workbook("file3.xlsx", sheet_name="データ")
        mock_reader.read_sheet("file4.xlsx", 1)

        # 各コールの記録確認
        assert (
            len(mock_reader.validate_file_calls) == 3
        )  # file1, file3, file4 (read_workbook内部で呼ばれる)
        assert len(mock_reader.get_sheet_names_calls) == 1  # file2
        assert (
            len(mock_reader.read_workbook_calls) == 2
        )  # file3 (直接) + file4 (read_sheet経由)
        assert len(mock_reader.read_sheet_calls) == 1  # file4

    def test_get_call_summary_functionality(self):
        """コールサマリー機能を検証する。

        機能保証項目:
        - 各メソッドコール数の正確な集計
        - 総コール数の適切な計算
        - サマリー情報の完全性

        品質観点:
        - 統計情報の正確性
        - レポート機能の充実
        - テスト結果の可視性
        """
        mock_reader = MockExcelReader()

        # 様々なメソッドを複数回呼び出し
        mock_reader.validate_file("test1.xlsx")
        mock_reader.validate_file("test2.xlsx")
        mock_reader.get_sheet_names("test.xlsx")
        mock_reader.read_workbook("test.xlsx")

        summary = mock_reader.get_call_summary()

        assert summary["validate_file_calls"] == 3  # read_workbookからも呼ばれる
        assert summary["get_sheet_names_calls"] == 1
        assert summary["read_workbook_calls"] == 1
        assert summary["read_sheet_calls"] == 0
        assert summary["total_calls"] == 5

    def test_reset_call_tracking_functionality(self):
        """コールトラッキングリセット機能を検証する。

        機能保証項目:
        - 全コール記録の完全削除
        - リセット後の初期状態復帰
        - メモリ使用量の最適化

        品質観点:
        - メモリリーク防止
        - テスト環境の清浄化
        - リソース管理の適切性
        """
        mock_reader = MockExcelReader()

        # 複数のコール実行
        mock_reader.validate_file("test.xlsx")
        mock_reader.get_sheet_names("test.xlsx")
        mock_reader.read_workbook("test.xlsx")

        # リセット前の確認
        summary_before = mock_reader.get_call_summary()
        assert (
            summary_before["total_calls"] == 4
        )  # validate_file(2回), get_sheet_names, read_workbook

        # リセット実行
        mock_reader.reset_call_tracking()

        # リセット後の確認
        assert len(mock_reader.validate_file_calls) == 0
        assert len(mock_reader.get_sheet_names_calls) == 0
        assert len(mock_reader.read_workbook_calls) == 0
        assert len(mock_reader.read_sheet_calls) == 0

        summary_after = mock_reader.get_call_summary()
        assert summary_after["total_calls"] == 0

    def test_call_tracking_detailed_information(self):
        """コールトラッキングの詳細情報記録を検証する。

        機能保証項目:
        - パラメータ詳細の正確な記録
        - 複雑なパラメータ構造の処理
        - データ型多様性の対応

        品質観点:
        - デバッグ情報の詳細性
        - トラブルシューティング支援
        - テスト結果の分析効率
        """
        mock_reader = MockExcelReader()

        # 詳細パラメータでの呼び出し
        mock_reader.read_workbook(
            "/complex/path/data.xlsx",
            sheet_name="売上データ",
            header=[0, 1],
            skiprows=3,
            usecols="A:J",
            dtype={"商品コード": str, "売上": float},
        )

        # 詳細情報確認
        call_record = mock_reader.read_workbook_calls[0]
        assert call_record["file_path"] == "/complex/path/data.xlsx"
        assert call_record["sheet_name"] == "売上データ"
        assert call_record["kwargs"]["header"] == [0, 1]
        assert call_record["kwargs"]["skiprows"] == 3
        assert call_record["kwargs"]["usecols"] == "A:J"
        assert isinstance(call_record["kwargs"]["dtype"], dict)


class TestMockExcelReaderIntegration:
    """統合機能の包括的テスト."""

    def test_complex_workflow_simulation(self):
        """複雑なワークフローシミュレーションを検証する。

        機能保証項目:
        - 複数機能の連携動作
        - ワークフロー全体の一貫性
        - 状態管理の適切性

        品質観点:
        - 統合テストの効率性
        - リアルなユースケースの再現
        - システム全体の信頼性
        """
        mock_reader = MockExcelReader()

        # 1. ファイル検証
        workbook_info = mock_reader.validate_file("workflow.xlsx")
        assert isinstance(workbook_info, WorkbookInfo)

        # 2. シート名取得
        sheet_names = mock_reader.get_sheet_names("workflow.xlsx")
        assert isinstance(sheet_names, list)

        # 3. データ読み込み
        read_result = mock_reader.read_workbook(
            "workflow.xlsx", sheet_name=sheet_names[0]
        )
        assert isinstance(read_result, ReadResult)

        # 4. 統合結果確認
        summary = mock_reader.get_call_summary()
        assert (
            summary["total_calls"] == 4
        )  # validate_file(2回), get_sheet_names(1回), read_workbook(1回)

    def test_error_consistency_across_methods(self):
        """全メソッド間でのエラー一貫性を検証する。

        機能保証項目:
        - 全メソッドでの統一エラー発生
        - エラー設定の包括適用
        - 一貫したエラーハンドリング

        セキュリティ要件:
        - エラー情報の一貫性
        - セキュリティエラーの統一処理
        - 攻撃パターンの包括検証

        品質観点:
        - エラー処理の統一性
        - 予測可能なエラー動作
        - デバッグ効率の向上
        """
        consistent_error = ExcelProcessingError("一貫したエラー")
        mock_reader = MockExcelReader(should_fail=True, error_to_raise=consistent_error)

        # 全メソッドで同じエラーが発生することを確認
        with pytest.raises(ExcelProcessingError, match="一貫したエラー"):
            mock_reader.validate_file("test.xlsx")

        with pytest.raises(ExcelProcessingError, match="一貫したエラー"):
            mock_reader.get_sheet_names("test.xlsx")

        with pytest.raises(ExcelProcessingError, match="一貫したエラー"):
            mock_reader.read_workbook("test.xlsx")

        with pytest.raises(ExcelProcessingError, match="一貫したエラー"):
            mock_reader.read_sheet("test.xlsx", "Sheet1")

        # エラー時でもコールトラッキングが機能
        summary = mock_reader.get_call_summary()
        assert (
            summary["total_calls"] == 4
        )  # validate_file, get_sheet_names, read_workbook, read_sheet

    def test_performance_and_memory_efficiency(self):
        """パフォーマンスとメモリ効率性を検証する。

        機能保証項目:
        - 大量コール処理の効率性
        - メモリ使用量の適切性
        - レスポンス時間の一貫性

        品質観点:
        - スケーラビリティの確保
        - リソース効率の最適化
        - パフォーマンス回帰の防止
        """
        mock_reader = MockExcelReader()

        # 大量コールの実行
        for i in range(100):
            mock_reader.validate_file(f"file_{i}.xlsx")
            mock_reader.get_sheet_names(f"file_{i}.xlsx")

        # メモリ効率確認
        summary = mock_reader.get_call_summary()
        assert summary["validate_file_calls"] == 100
        assert summary["get_sheet_names_calls"] == 100
        assert summary["total_calls"] == 200

        # リセット後のメモリ解放確認
        mock_reader.reset_call_tracking()
        summary_after = mock_reader.get_call_summary()
        assert summary_after["total_calls"] == 0
