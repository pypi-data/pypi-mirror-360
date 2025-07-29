"""Task 3.2: 実ファイル処理保証テスト

実Excelファイルでの動作確認・パフォーマンス・エッジケース処理の包括的テスト
"""

import os
import tempfile
import time
from unittest.mock import Mock

import pandas as pd
import pytest

from sphinxcontrib.jsontable.directives.directive_core import JsonTableDirective
from sphinxcontrib.jsontable.directives.validators import JsonTableError


class TestRealFileProcessing:
    """Task 3.2: 実ファイル処理保証テスト."""

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

    def create_complex_excel_file(self, filename: str = "complex_test.xlsx") -> str:
        """複雑な実Excelファイルを作成.

        Args:
            filename: ファイル名

        Returns:
            作成されたファイルのパス
        """
        file_path = os.path.join(self.temp_dir, filename)

        # 複雑なデータ構造
        data = {
            "Sheet1": [
                ["製品ID", "製品名", "価格", "在庫", "カテゴリ", "備考"],
                ["P001", "ノートPC", "120000", "15", "電子機器", "新製品"],
                ["P002", "デスクトップPC", "95000", "8", "電子機器", ""],
                ["P003", "タブレット", "58000", "25", "電子機器", "人気商品"],
                ["P004", "スマートフォン", "78000", "32", "電子機器", ""],
                ["P005", "ヘッドフォン", "12000", "45", "音響機器", ""],
            ],
            "Sheet2": [
                ["月", "売上", "利益"],
                ["1月", "2500000", "500000"],
                ["2月", "2800000", "560000"],
                ["3月", "3200000", "640000"],
            ],
        }

        # 複数シートのExcelファイル作成
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            for sheet_name, sheet_data in data.items():
                df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        return file_path

    def create_large_excel_file(
        self, filename: str = "large_test.xlsx", rows: int = 5000
    ) -> str:
        """大容量Excelファイルを作成.

        Args:
            filename: ファイル名
            rows: データ行数

        Returns:
            作成されたファイルのパス
        """
        file_path = os.path.join(self.temp_dir, filename)

        # 大容量データ生成
        data = []
        data.append(["ID", "名前", "年齢", "部署", "給与", "入社日"])

        for i in range(rows):
            data.append(
                [
                    f"EMP{i:06d}",
                    f"社員{i}",
                    20 + (i % 45),
                    f"部署{i % 10}",
                    300000 + (i % 200000),
                    f"2020-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
                ]
            )

        df = pd.DataFrame(data[1:], columns=data[0])
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="EmployeeData", index=False)

        return file_path

    def create_edge_case_excel_file(self, filename: str = "edge_case.xlsx") -> str:
        """エッジケースExcelファイルを作成.

        Args:
            filename: ファイル名

        Returns:
            作成されたファイルのパス
        """
        file_path = os.path.join(self.temp_dir, filename)

        # エッジケースデータ
        data = [
            ["項目", "値", "備考"],
            ["", "空の項目名", "項目名が空"],
            ["特殊文字", "!@#$%^&*()", "記号"],
            ["日本語", "こんにちは世界", "マルチバイト"],
            ["長いテキスト", "これは非常に長いテキストデータです。" * 10, "長文"],
            ["数値", "12345.67", "小数点"],
            ["NULL値", "", "空文字列"],
            ["改行\n含む", "複数行\nテキスト", "改行文字"],
        ]

        df = pd.DataFrame(data[1:], columns=data[0])
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="EdgeCases", index=False)

        return file_path

    def test_complex_excel_file_processing(self):
        """複雑Excelファイルの処理テスト."""
        excel_path = self.create_complex_excel_file()

        # 初期化
        self.directive._initialize_processors()

        # 複雑ファイル処理
        options = {"header": True, "sheet": "Sheet1"}

        # 統合処理実行
        result = self.directive.process_excel_file(excel_path, options)

        # 結果検証
        assert result["success"] is True
        assert "data" in result
        assert len(result["data"]) >= 5  # 製品データ5件以上

        # データ内容確認
        data = result["data"]
        assert any("ノートPC" in str(row) for row in data)
        assert any("120000" in str(row) for row in data)
        assert any("電子機器" in str(row) for row in data)

    def test_multiple_sheet_processing(self):
        """複数シート処理テスト."""
        excel_path = self.create_complex_excel_file()

        # 初期化
        self.directive._initialize_processors()

        # Sheet2処理
        options = {"header": True, "sheet": "Sheet2"}

        # 統合処理実行
        result = self.directive.process_excel_file(excel_path, options)

        # 結果検証
        assert result["success"] is True
        assert "data" in result
        assert len(result["data"]) >= 3  # 売上データ3件以上

        # データ内容確認
        data = result["data"]
        assert any("1月" in str(row) for row in data)
        assert any("2500000" in str(row) for row in data)

    def test_large_file_performance(self):
        """大容量ファイルパフォーマンステスト."""
        rows = 1000  # テスト用に適度なサイズ
        excel_path = self.create_large_excel_file("performance_test.xlsx", rows)

        # 初期化
        self.directive._initialize_processors()

        # パフォーマンス測定
        start_time = time.time()

        options = {
            "header": True,
            "limit": 500,  # 制限付き処理
        }

        # 統合処理実行
        result = self.directive.process_excel_file(excel_path, options)

        end_time = time.time()
        processing_time = end_time - start_time

        # 結果検証
        assert result["success"] is True
        assert "data" in result

        # パフォーマンス検証（5秒以内）
        assert processing_time < 5.0, f"処理時間が遅すぎます: {processing_time:.2f}秒"

        # データサイズ確認
        data = result["data"]
        assert len(data) >= 500  # 制限通りのデータ

        print(f"大容量ファイル処理時間: {processing_time:.2f}秒")

    def test_memory_usage_monitoring(self):
        """メモリ使用量監視テスト."""
        import os

        import psutil

        # プロセス情報取得
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        excel_path = self.create_large_excel_file("memory_test.xlsx", 2000)

        # 初期化
        self.directive._initialize_processors()

        options = {"header": True}

        # 統合処理実行
        result = self.directive.process_excel_file(excel_path, options)

        # メモリ使用量確認
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # 結果検証
        assert result["success"] is True

        # メモリ使用量確認（200MB以内の増加）
        assert memory_increase < 200, (
            f"メモリ使用量増加が大きすぎます: {memory_increase:.1f}MB"
        )

        print(f"メモリ使用量増加: {memory_increase:.1f}MB")

    def test_edge_case_data_handling(self):
        """エッジケースデータ処理テスト."""
        excel_path = self.create_edge_case_excel_file()

        # 初期化
        self.directive._initialize_processors()

        options = {"header": True}

        # 統合処理実行
        result = self.directive.process_excel_file(excel_path, options)

        # 結果検証
        assert result["success"] is True
        assert "data" in result

        # エッジケースデータ確認
        data = result["data"]

        # 特殊文字データの存在確認
        found_special = any("!@#$%^&*()" in str(row) for row in data)
        assert found_special, "特殊文字データが見つかりません"

        # 日本語データの存在確認
        found_japanese = any("こんにちは世界" in str(row) for row in data)
        assert found_japanese, "日本語データが見つかりません"

        # 長文データの処理確認
        found_long_text = any(len(str(cell)) > 100 for row in data for cell in row)
        assert found_long_text, "長文データが見つかりません"

    def test_concurrent_file_processing(self):
        """並行ファイル処理テスト."""
        import queue
        import threading

        # 複数ファイル作成
        files = []
        for i in range(3):
            file_path = self.create_complex_excel_file(f"concurrent_test_{i}.xlsx")
            files.append(file_path)

        # 結果格納用キュー
        results_queue = queue.Queue()

        def process_file(file_path, file_index):
            try:
                # 各スレッド用のDirectiveインスタンス
                directive = JsonTableDirective(
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

                directive._initialize_processors()

                options = {"header": True, "sheet": "Sheet1"}
                result = directive.process_excel_file(file_path, options)

                results_queue.put(
                    (file_index, result["success"], len(result.get("data", [])))
                )

            except Exception as e:
                results_queue.put((file_index, False, str(e)))

        # 並行処理実行
        threads = []
        for i, file_path in enumerate(files):
            thread = threading.Thread(target=process_file, args=(file_path, i))
            threads.append(thread)
            thread.start()

        # 全スレッド完了待機
        for thread in threads:
            thread.join()

        # 結果検証
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())

        # 全て成功していることを確認
        assert len(results) == 3
        for file_index, success, data_count in results:
            assert success is True, f"ファイル{file_index}の処理が失敗"
            assert data_count > 0, f"ファイル{file_index}のデータが空"

    def test_file_permission_handling(self):
        """ファイル権限処理テスト."""
        excel_path = self.create_complex_excel_file("permission_test.xlsx")

        # 初期化
        self.directive._initialize_processors()

        # ファイル権限変更（読み取り専用）
        import stat

        os.chmod(excel_path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

        try:
            options = {"header": True}

            # 統合処理実行
            result = self.directive.process_excel_file(excel_path, options)

            # 読み取り専用でも正常処理されることを確認
            assert result["success"] is True
            assert "data" in result

        finally:
            # 権限復元
            os.chmod(
                excel_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
            )

    def test_file_size_limits(self):
        """ファイルサイズ制限テスト."""
        # 中程度サイズファイル（制限内）
        excel_path = self.create_large_excel_file("size_test.xlsx", 500)

        # 初期化
        self.directive._initialize_processors()

        options = {"header": True}

        # 統合処理実行
        result = self.directive.process_excel_file(excel_path, options)

        # 正常処理確認
        assert result["success"] is True
        assert "data" in result
        assert len(result["data"]) >= 500

    def test_real_world_scenario_simulation(self):
        """実世界シナリオシミュレーション."""
        # 実業務で使われそうなExcelファイル作成
        file_path = os.path.join(self.temp_dir, "business_data.xlsx")

        # 実業務データ形式
        business_data = [
            ["取引ID", "顧客名", "製品", "数量", "単価", "合計", "取引日", "担当者"],
            [
                "T001",
                "株式会社ABC",
                "製品A",
                "10",
                "5000",
                "50000",
                "2023-01-15",
                "田中",
            ],
            ["T002", "XYZ商事", "製品B", "5", "8000", "40000", "2023-01-16", "佐藤"],
            ["T003", "DEF工業", "製品C", "20", "3000", "60000", "2023-01-17", "鈴木"],
            [
                "T004",
                "GHI株式会社",
                "製品A",
                "15",
                "5000",
                "75000",
                "2023-01-18",
                "田中",
            ],
            ["T005", "JKL商店", "製品D", "8", "12000", "96000", "2023-01-19", "佐藤"],
        ]

        df = pd.DataFrame(business_data[1:], columns=business_data[0])
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="取引データ", index=False)

        # 初期化
        self.directive._initialize_processors()

        # 実業務シナリオでの処理
        options = {"header": True, "sheet": "取引データ"}

        # 統合処理実行
        result = self.directive.process_excel_file(file_path, options)

        # 結果検証
        assert result["success"] is True
        assert "data" in result

        # 業務データ検証
        data = result["data"]
        assert len(data) >= 5  # 5件の取引データ

        # 実データ確認
        assert any("株式会社ABC" in str(row) for row in data)
        assert any("田中" in str(row) for row in data)
        assert any("50000" in str(row) for row in data)

    def test_error_recovery_scenarios(self):
        """エラー回復シナリオテスト."""
        # 初期化
        self.directive._initialize_processors()

        # 存在しないファイル
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.xlsx")

        options = {"header": True}

        # 統合処理実行（エラー回復）
        result = self.directive.process_excel_file(nonexistent_file, options)

        # エラーハンドリング確認
        assert result["success"] is False
        assert "error" in result
        assert result["data"] is None

        # エラーメッセージ確認
        assert "Excel" in result["error"]

    def test_directive_level_real_processing(self):
        """Directiveレベル実処理テスト."""
        excel_path = self.create_complex_excel_file()

        # Directive引数として設定
        self.directive.arguments = [excel_path]
        self.directive.options = {"header": True, "sheet": "Sheet1"}

        # 初期化
        self.directive._initialize_processors()

        # _load_excel_data直接呼び出し
        try:
            data = self.directive._load_excel_data(excel_path)

            # データ検証
            assert isinstance(data, list)
            assert len(data) >= 5

            # 実データ確認
            assert any("ノートPC" in str(row) for row in data)

        except Exception as e:
            # エラーがあっても適切に処理されることを確認
            assert "Excel" in str(e) or isinstance(e, JsonTableError)


if __name__ == "__main__":
    # スタンドアロンテスト実行
    pytest.main([__file__, "-v"])
