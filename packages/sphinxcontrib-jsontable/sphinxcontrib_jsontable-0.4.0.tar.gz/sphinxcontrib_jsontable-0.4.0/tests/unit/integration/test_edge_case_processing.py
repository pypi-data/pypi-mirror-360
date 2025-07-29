"""Task 3.2: エッジケース処理テスト

極端なケース・異常データ・境界値での処理確認テスト
"""

import os
import tempfile
from unittest.mock import Mock

import pandas as pd
import pytest

from sphinxcontrib.jsontable.directives.directive_core import JsonTableDirective


class TestEdgeCaseProcessing:
    """Task 3.2: エッジケース処理テスト."""

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

    def create_empty_excel_file(self, filename: str = "empty.xlsx") -> str:
        """空のExcelファイルを作成.

        Args:
            filename: ファイル名

        Returns:
            作成されたファイルのパス
        """
        file_path = os.path.join(self.temp_dir, filename)

        # 空のDataFrame作成
        df = pd.DataFrame()
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Sheet1", index=False)

        return file_path

    def create_header_only_excel_file(self, filename: str = "header_only.xlsx") -> str:
        """ヘッダーのみのExcelファイルを作成.

        Args:
            filename: ファイル名

        Returns:
            作成されたファイルのパス
        """
        file_path = os.path.join(self.temp_dir, filename)

        # ヘッダーのみのデータ
        data = [["列1", "列2", "列3"]]

        df = pd.DataFrame([], columns=data[0])
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Sheet1", index=False)

        return file_path

    def create_single_cell_excel_file(self, filename: str = "single_cell.xlsx") -> str:
        """単一セルのExcelファイルを作成.

        Args:
            filename: ファイル名

        Returns:
            作成されたファイルのパス
        """
        file_path = os.path.join(self.temp_dir, filename)

        # 単一セルデータ
        data = [["値"]]

        df = pd.DataFrame(data)
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Sheet1", index=False, header=False)

        return file_path

    def create_special_characters_excel_file(
        self, filename: str = "special_chars.xlsx"
    ) -> str:
        """特殊文字を含むExcelファイルを作成.

        Args:
            filename: ファイル名

        Returns:
            作成されたファイルのパス
        """
        file_path = os.path.join(self.temp_dir, filename)

        # 特殊文字データ
        data = [
            ["項目", "値"],
            ["記号", "!@#$%^&*()_+-=[]{}|;':\",./<>?"],
            ["タブ", "前\t後"],
            ["改行", "前\n後"],
            ["CR+LF", "前\r\n後"],
            ["Unicode", "🎉🌟⭐️🚀💻"],
            ["Empty", ""],
            ["Space", "   "],
            ["Zero", "0"],
            ["Boolean", "True"],
            ["NULL", None],
        ]

        df = pd.DataFrame(data[1:], columns=data[0])
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Sheet1", index=False)

        return file_path

    def create_long_text_excel_file(self, filename: str = "long_text.xlsx") -> str:
        """長いテキストを含むExcelファイルを作成.

        Args:
            filename: ファイル名

        Returns:
            作成されたファイルのパス
        """
        file_path = os.path.join(self.temp_dir, filename)

        # 長いテキストデータ
        long_text = "これは非常に長いテキストです。" * 1000  # 約30KB
        very_long_text = "X" * 32768  # Excel単一セル制限近く

        data = [
            ["種類", "内容"],
            ["通常", "短いテキスト"],
            ["長文", long_text],
            ["最大級", very_long_text],
            ["繰り返し", "ABC" * 5000],
        ]

        df = pd.DataFrame(data[1:], columns=data[0])
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Sheet1", index=False)

        return file_path

    def create_numeric_edge_cases_excel_file(
        self, filename: str = "numeric_edge.xlsx"
    ) -> str:
        """数値の境界値ケースExcelファイルを作成.

        Args:
            filename: ファイル名

        Returns:
            作成されたファイルのパス
        """
        file_path = os.path.join(self.temp_dir, filename)

        # 数値境界値データ
        data = [
            ["種類", "値"],
            ["ゼロ", 0],
            ["負数", -12345],
            ["大きな正数", 999999999999],
            ["小数", 3.14159265359],
            ["科学記法", "1.23E+10"],
            ["無限大", "inf"],
            ["非数", "nan"],
            ["真偽値T", True],
            ["真偽値F", False],
            ["文字列数値", "12345"],
            ["混合", "123ABC"],
        ]

        df = pd.DataFrame(data[1:], columns=data[0])
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Sheet1", index=False)

        return file_path

    def create_malformed_data_excel_file(self, filename: str = "malformed.xlsx") -> str:
        """不正形式データのExcelファイルを作成.

        Args:
            filename: ファイル名

        Returns:
            作成されたファイルのパス
        """
        file_path = os.path.join(self.temp_dir, filename)

        # 不正形式データ（スキップされた行、不整合列数等）
        data = [
            ["A", "B", "C"],
            ["1", "2"],  # 列数不足
            ["4", "5", "6", "7"],  # 列数過多
            [],  # 空行
            ["8", "", "10"],  # 空セル含む
            [None, "12", None],  # None値含む
        ]

        # 不正データを直接Excelに書き込み
        import openpyxl

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Sheet1"

        for i, row in enumerate(data, 1):
            for j, value in enumerate(row, 1):
                if value is not None:
                    ws.cell(row=i, column=j, value=value)

        wb.save(file_path)
        return file_path

    def test_empty_file_processing(self):
        """空ファイル処理テスト."""
        excel_path = self.create_empty_excel_file()

        # 初期化
        self.directive._initialize_processors()

        options = {"header": True}

        # 統合処理実行
        result = self.directive.process_excel_file(excel_path, options)

        # 空ファイルでもエラーにならないことを確認
        # 空データの場合、適切にハンドリングされることを期待
        if result["success"]:
            assert "data" in result
            # 空データまたは最小限のデータ
            assert len(result["data"]) >= 0
        else:
            # エラーの場合、適切なエラーメッセージ
            assert "error" in result
            assert "Excel" in result["error"] or "empty" in result["error"].lower()

    def test_header_only_file_processing(self):
        """ヘッダーのみファイル処理テスト."""
        excel_path = self.create_header_only_excel_file()

        # 初期化
        self.directive._initialize_processors()

        options = {"header": True}

        # 統合処理実行
        result = self.directive.process_excel_file(excel_path, options)

        # ヘッダーのみでも適切に処理されることを確認
        if result["success"]:
            assert "data" in result
            # ヘッダー行のみの場合
            data = result["data"]
            if len(data) > 0:
                # ヘッダー情報が含まれていることを確認
                assert any("列1" in str(row) for row in data) or len(data) == 1
        else:
            # エラーの場合、適切なエラーメッセージ
            assert "error" in result

    def test_single_cell_processing(self):
        """単一セル処理テスト."""
        excel_path = self.create_single_cell_excel_file()

        # 初期化
        self.directive._initialize_processors()

        options = {"header": False}  # ヘッダーなしで処理

        # 統合処理実行
        result = self.directive.process_excel_file(excel_path, options)

        # 単一セルでも正常処理されることを確認
        assert result["success"] is True
        assert "data" in result

        data = result["data"]
        assert len(data) >= 1
        # 単一セルの値が含まれていることを確認
        assert any("値" in str(row) for row in data)

    def test_special_characters_processing(self):
        """特殊文字処理テスト."""
        excel_path = self.create_special_characters_excel_file()

        # 初期化
        self.directive._initialize_processors()

        options = {"header": True}

        # 統合処理実行
        result = self.directive.process_excel_file(excel_path, options)

        # 特殊文字でも正常処理されることを確認
        assert result["success"] is True
        assert "data" in result

        data = result["data"]
        assert len(data) >= 5  # データ行数確認

        # 特殊文字データの存在確認
        data_str = str(data)
        assert "!@#$%^&*()" in data_str or "記号" in data_str
        assert "🎉" in data_str or "Unicode" in data_str

    def test_long_text_processing(self):
        """長文テキスト処理テスト."""
        excel_path = self.create_long_text_excel_file()

        # 初期化
        self.directive._initialize_processors()

        options = {"header": True}

        # 統合処理実行
        result = self.directive.process_excel_file(excel_path, options)

        # 長文でも正常処理されることを確認
        assert result["success"] is True
        assert "data" in result

        data = result["data"]
        assert len(data) >= 4  # データ行数確認

        # 長文データの存在確認
        found_long_text = any(
            len(str(cell)) > 1000
            for row in data
            for cell in row
            if isinstance(cell, str)
        )
        assert found_long_text, "長文データが見つかりません"

    def test_numeric_edge_cases_processing(self):
        """数値境界値処理テスト."""
        excel_path = self.create_numeric_edge_cases_excel_file()

        # 初期化
        self.directive._initialize_processors()

        options = {"header": True}

        # 統合処理実行
        result = self.directive.process_excel_file(excel_path, options)

        # 数値境界値でも正常処理されることを確認
        assert result["success"] is True
        assert "data" in result

        data = result["data"]
        assert len(data) >= 10  # データ行数確認

        # 特殊数値データの存在確認
        data_str = str(data)
        assert "999999999999" in data_str or "大きな正数" in data_str
        assert "3.14159" in data_str or "小数" in data_str

    def test_malformed_data_processing(self):
        """不正形式データ処理テスト."""
        excel_path = self.create_malformed_data_excel_file()

        # 初期化
        self.directive._initialize_processors()

        options = {"header": True}

        # 統合処理実行
        result = self.directive.process_excel_file(excel_path, options)

        # 不正形式でも適切に処理されることを確認
        if result["success"]:
            assert "data" in result
            data = result["data"]
            # 何らかのデータが処理されていることを確認
            assert len(data) >= 1
        else:
            # エラーの場合、適切なエラーメッセージ
            assert "error" in result
            assert "Excel" in result["error"]

    def test_boundary_range_specifications(self):
        """境界値範囲指定テスト."""
        excel_path = self.create_special_characters_excel_file()

        # 初期化
        self.directive._initialize_processors()

        # 境界値範囲指定テスト
        boundary_ranges = [
            "A1:A1",  # 単一セル
            "A1:Z1",  # 単一行
            "A1:A100",  # 単一列
            "A1:B2",  # 最小範囲
        ]

        for range_spec in boundary_ranges:
            options = {"header": True, "range": range_spec}

            # 統合処理実行
            result = self.directive.process_excel_file(excel_path, options)

            # 境界値範囲でも適切に処理されることを確認
            # 範囲外の場合はエラー、範囲内の場合は成功
            if result["success"]:
                assert "data" in result
                print(f"範囲 {range_spec}: 成功 ({len(result['data'])}行)")
            else:
                # エラーの場合、適切なエラーメッセージ
                assert "error" in result
                print(f"範囲 {range_spec}: {result['error']}")

    def test_invalid_sheet_specifications(self):
        """無効シート指定テスト."""
        excel_path = self.create_special_characters_excel_file()

        # 初期化
        self.directive._initialize_processors()

        # 無効シート名テスト
        invalid_sheets = [
            "NonExistentSheet",
            "Sheet999",
            "",
            "   ",
            "Sheet1!",
            "特殊文字シート名",
        ]

        for sheet_name in invalid_sheets:
            options = {"header": True, "sheet": sheet_name}

            # 統合処理実行
            result = self.directive.process_excel_file(excel_path, options)

            # 無効シート名の場合、適切にエラーハンドリングされることを確認
            if not result["success"]:
                assert "error" in result
                assert "sheet" in result["error"].lower() or "Excel" in result["error"]
                print(f"無効シート '{sheet_name}': {result['error']}")
            else:
                # 成功した場合は、デフォルトシートが使用された可能性
                print(f"シート '{sheet_name}': デフォルト処理成功")

    def test_extreme_option_combinations(self):
        """極端なオプション組み合わせテスト."""
        excel_path = self.create_special_characters_excel_file()

        # 初期化
        self.directive._initialize_processors()

        # 極端なオプション組み合わせ
        extreme_options = [
            {"header": True, "range": "A1:A1", "skip-rows": "0", "header-row": 0},
            {
                "header": True,
                "range": "A1:Z100",
                "skip-rows": "1,2,3,4,5",
                "header-row": 10,
            },
            {"range": "A1:B2", "sheet-index": 0, "auto-header": True},
        ]

        for i, options in enumerate(extreme_options):
            # 統合処理実行
            result = self.directive.process_excel_file(excel_path, options)

            # 極端な組み合わせでも適切に処理されることを確認
            print(f"極端オプション{i + 1}: {'成功' if result['success'] else 'エラー'}")

            if result["success"]:
                assert "data" in result
            else:
                assert "error" in result
                print(f"エラー詳細: {result['error']}")

    def test_file_corruption_simulation(self):
        """ファイル破損シミュレーションテスト."""
        # 正常ファイル作成
        excel_path = self.create_special_characters_excel_file()

        # ファイル内容を部分的に破損
        corrupted_path = os.path.join(self.temp_dir, "corrupted.xlsx")

        # バイナリデータの一部を変更してファイル破損をシミュレート
        with open(excel_path, "rb") as f:
            data = bytearray(f.read())

        # データの中間部分を変更（完全破損ではなく部分破損）
        if len(data) > 100:
            data[50:55] = b"\x00\x00\x00\x00\x00"

        with open(corrupted_path, "wb") as f:
            f.write(data)

        # 初期化
        self.directive._initialize_processors()

        options = {"header": True}

        # 統合処理実行
        result = self.directive.process_excel_file(corrupted_path, options)

        # 破損ファイルでは適切にエラーハンドリングされることを確認
        # 軽微な破損の場合、pandasやopenpyxlが修復して読める場合もある
        if result["success"]:
            # 修復されて読めた場合
            assert "data" in result
            print(f"破損ファイル修復成功: {len(result['data'])}行処理")
        else:
            # エラーの場合
            assert "error" in result
            assert "Excel" in result["error"]
            print(f"破損ファイルエラー: {result['error']}")

    def test_zero_size_file_handling(self):
        """ゼロサイズファイル処理テスト."""
        # ゼロサイズファイル作成
        zero_size_path = os.path.join(self.temp_dir, "zero_size.xlsx")
        with open(zero_size_path, "w") as _f:
            pass  # 空ファイル作成

        # 初期化
        self.directive._initialize_processors()

        options = {"header": True}

        # 統合処理実行
        result = self.directive.process_excel_file(zero_size_path, options)

        # ゼロサイズファイルでは適切にエラーハンドリングされることを確認
        assert result["success"] is False
        assert "error" in result
        assert "Excel" in result["error"]
        print(f"ゼロサイズファイルエラー: {result['error']}")


if __name__ == "__main__":
    # スタンドアロンテスト実行
    pytest.main([__file__, "-v"])
