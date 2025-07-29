"""ベンチマークテスト

sphinxcontrib-jsontableの基本的なベンチマークテスト
pytest-benchmarkプラグインを使用してパフォーマンス測定を行う
"""

import os
import tempfile
from unittest.mock import Mock

import pandas as pd
import pytest

from sphinxcontrib.jsontable.directives.directive_core import JsonTableDirective


class TestBenchmarkCore:
    """基本的なベンチマークテスト."""

    def setup_method(self):
        """各テストメソッドの前に実行される。"""
        self.temp_dir = tempfile.mkdtemp()

        # Mock環境の設定
        self.mock_env = Mock()
        self.mock_env.srcdir = self.temp_dir
        self.mock_env.config = Mock()
        self.mock_env.config.jsontable_max_rows = 10000

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

    def create_benchmark_test_file(self, rows: int, filename: str = None) -> str:
        """ベンチマークテスト用Excelファイルを作成.

        Args:
            rows: データ行数
            filename: ファイル名（指定しない場合は自動生成）

        Returns:
            作成されたファイルのパス
        """
        if filename is None:
            filename = f"benchmark_test_{rows}_rows.xlsx"

        file_path = os.path.join(self.temp_dir, filename)

        # ベンチマークテスト用データ生成
        data = []
        headers = ["ID", "Name", "Value", "Category", "Score"]
        data.append(headers)

        for i in range(rows):
            row = [
                f"ID{i:06d}",
                f"Name{i}",
                i * 100,
                f"Category{i % 10}",
                i % 100,
            ]
            data.append(row)

        df = pd.DataFrame(data[1:], columns=data[0])
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="TestData", index=False)

        return file_path

    @pytest.mark.benchmark
    def test_small_excel_processing_benchmark(self, benchmark):
        """小規模Excelファイル処理のベンチマーク（100行）."""
        file_path = self.create_benchmark_test_file(100)

        def excel_processing():
            """ベンチマーク対象の処理."""
            self.directive._initialize_processors()
            return self.directive.process_excel_file(file_path, {"header": True})

        result = benchmark(excel_processing)
        assert result["success"] is True

    @pytest.mark.benchmark
    def test_medium_excel_processing_benchmark(self, benchmark):
        """中規模Excelファイル処理のベンチマーク（500行）."""
        file_path = self.create_benchmark_test_file(500)

        def excel_processing():
            """ベンチマーク対象の処理."""
            self.directive._initialize_processors()
            return self.directive.process_excel_file(file_path, {"header": True})

        result = benchmark(excel_processing)
        assert result["success"] is True

    @pytest.mark.benchmark
    def test_json_data_creation_benchmark(self, benchmark):
        """JSONデータ作成のベンチマーク."""

        def json_data_creation():
            """ベンチマーク対象の処理."""
            return [{"id": i, "name": f"Item{i}", "value": i * 10} for i in range(100)]

        result = benchmark(json_data_creation)
        assert len(result) == 100

    @pytest.mark.benchmark
    def test_table_data_conversion_benchmark(self, benchmark):
        """テーブルデータ変換のベンチマーク."""

        def table_data_conversion():
            """ベンチマーク対象の処理."""
            headers = ["ID", "Name", "Value"]
            data = [headers] + [[f"ID{i}", f"Name{i}", i] for i in range(200)]
            return data

        result = benchmark(table_data_conversion)
        assert len(result) == 201

    @pytest.mark.benchmark
    def test_directive_initialization_benchmark(self, benchmark):
        """ディレクティブ初期化のベンチマーク."""

        def directive_init():
            """ベンチマーク対象の処理."""
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
            return directive

        result = benchmark(directive_init)
        assert result is not None


if __name__ == "__main__":
    # スタンドアロンテスト実行
    pytest.main([__file__, "--benchmark-only", "-v"])
