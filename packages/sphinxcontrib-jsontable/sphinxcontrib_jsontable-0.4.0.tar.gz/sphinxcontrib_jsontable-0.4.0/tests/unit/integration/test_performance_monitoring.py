"""Task 3.2: パフォーマンス監視テスト

Excel処理のパフォーマンス、メモリ使用量、リソース管理の包括的テスト
"""

import os
import tempfile
import time
from unittest.mock import Mock

import pandas as pd
import psutil
import pytest

from sphinxcontrib.jsontable.directives.directive_core import JsonTableDirective


class TestPerformanceMonitoring:
    """Task 3.2: パフォーマンス監視・リソース管理テスト."""

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

    def create_performance_test_file(self, rows: int, filename: str = None) -> str:
        """パフォーマンステスト用Excelファイルを作成.

        Args:
            rows: データ行数
            filename: ファイル名（指定しない場合は自動生成）

        Returns:
            作成されたファイルのパス
        """
        if filename is None:
            filename = f"performance_test_{rows}_rows.xlsx"

        file_path = os.path.join(self.temp_dir, filename)

        # 性能テスト用データ生成
        data = []
        headers = [
            "ID",
            "氏名",
            "年齢",
            "部署",
            "役職",
            "給与",
            "入社日",
            "住所",
            "電話番号",
            "メール",
            "プロジェクト",
            "評価",
        ]
        data.append(headers)

        for i in range(rows):
            row = [
                f"EMP{i:08d}",
                f"従業員{i}",
                20 + (i % 45),
                f"部署{i % 20}",
                f"役職{i % 10}",
                300000 + (i % 500000),
                f"202{i % 4}-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
                f"東京都{i % 23}区{i % 100}-{i % 999}",
                f"090-{i % 9000 + 1000:04d}-{i % 9000 + 1000:04d}",
                f"emp{i}@company.com",
                f"プロジェクト{i % 50}",
                i % 5 + 1,
            ]
            data.append(row)

        df = pd.DataFrame(data[1:], columns=data[0])
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="EmployeeData", index=False)

        return file_path

    def measure_processing_time(self, file_path: str, options: dict) -> tuple:
        """処理時間測定.

        Args:
            file_path: Excelファイルパス
            options: 処理オプション

        Returns:
            (処理時間, 結果, データ行数)
        """
        # 初期化
        self.directive._initialize_processors()

        # 処理時間測定
        start_time = time.time()
        result = self.directive.process_excel_file(file_path, options)
        end_time = time.time()

        processing_time = end_time - start_time
        data_count = len(result.get("data", [])) if result["success"] else 0

        return processing_time, result, data_count

    def measure_memory_usage(self, file_path: str, options: dict) -> tuple:
        """メモリ使用量測定.

        Args:
            file_path: Excelファイルパス
            options: 処理オプション

        Returns:
            (処理前メモリ, 処理後メモリ, メモリ増加量, 結果)
        """
        # プロセス情報取得
        process = psutil.Process(os.getpid())

        # 処理前メモリ測定
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # 初期化
        self.directive._initialize_processors()

        # 処理実行
        result = self.directive.process_excel_file(file_path, options)

        # 処理後メモリ測定
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        return initial_memory, final_memory, memory_increase, result

    @pytest.mark.performance
    def test_small_file_performance(self):
        """小規模ファイルパフォーマンステスト（100行）."""
        rows = 100
        file_path = self.create_performance_test_file(rows)

        options = {"header": True}
        processing_time, result, data_count = self.measure_processing_time(
            file_path, options
        )

        # 結果検証
        assert result["success"] is True
        # ヘッダー行を含むため+1行
        assert data_count == rows + 1, f"期待: {rows + 1}行, 実際: {data_count}行"

        # パフォーマンス検証（0.5秒以内）
        assert processing_time < 0.5, (
            f"小規模ファイル処理が遅い: {processing_time:.3f}秒"
        )

        print(f"小規模ファイル（{rows}行）処理時間: {processing_time:.3f}秒")

    @pytest.mark.performance
    def test_medium_file_performance(self):
        """中規模ファイルパフォーマンステスト（1000行）."""
        rows = 1000
        file_path = self.create_performance_test_file(rows)

        options = {"header": True}
        processing_time, result, data_count = self.measure_processing_time(
            file_path, options
        )

        # 結果検証
        assert result["success"] is True
        # ヘッダー行を含むため+1行
        assert data_count == rows + 1, f"期待: {rows + 1}行, 実際: {data_count}行"

        # パフォーマンス検証（2秒以内）
        assert processing_time < 2.0, (
            f"中規模ファイル処理が遅い: {processing_time:.3f}秒"
        )

        print(f"中規模ファイル（{rows}行）処理時間: {processing_time:.3f}秒")

    @pytest.mark.performance
    def test_large_file_performance(self):
        """大規模ファイルパフォーマンステスト（5000行）."""
        rows = 5000
        file_path = self.create_performance_test_file(rows)

        options = {"header": True}
        processing_time, result, data_count = self.measure_processing_time(
            file_path, options
        )

        # 結果検証
        assert result["success"] is True
        # ヘッダー行を含むため+1行
        assert data_count == rows + 1, f"期待: {rows + 1}行, 実際: {data_count}行"

        # パフォーマンス検証（10秒以内）
        assert processing_time < 10.0, (
            f"大規模ファイル処理が遅い: {processing_time:.3f}秒"
        )

        print(f"大規模ファイル（{rows}行）処理時間: {processing_time:.3f}秒")

    @pytest.mark.performance
    def test_memory_usage_small_file(self):
        """小規模ファイルメモリ使用量テスト."""
        rows = 100
        file_path = self.create_performance_test_file(rows)

        options = {"header": True}
        initial, final, increase, result = self.measure_memory_usage(file_path, options)

        # 結果検証
        assert result["success"] is True

        # メモリ使用量検証（10MB以内の増加）
        assert increase < 10, f"小規模ファイルでメモリ使用量が多い: {increase:.1f}MB"

        print(f"小規模ファイル（{rows}行）メモリ増加: {increase:.1f}MB")

    @pytest.mark.performance
    def test_memory_usage_large_file(self):
        """大規模ファイルメモリ使用量テスト."""
        rows = 2000
        file_path = self.create_performance_test_file(rows)

        options = {"header": True}
        initial, final, increase, result = self.measure_memory_usage(file_path, options)

        # 結果検証
        assert result["success"] is True

        # メモリ使用量検証（100MB以内の増加）
        assert increase < 100, (
            f"大規模ファイルでメモリ使用量が多すぎる: {increase:.1f}MB"
        )

        print(f"大規模ファイル（{rows}行）メモリ増加: {increase:.1f}MB")

    @pytest.mark.performance
    def test_processing_scalability(self):
        """処理スケーラビリティテスト."""
        # 異なるサイズでの処理時間測定
        test_sizes = [100, 500, 1000, 2000]
        results = []

        for rows in test_sizes:
            file_path = self.create_performance_test_file(
                rows, f"scale_test_{rows}.xlsx"
            )
            options = {"header": True}

            processing_time, result, data_count = self.measure_processing_time(
                file_path, options
            )

            assert result["success"] is True
            # ヘッダー行を含むため+1行
            assert data_count == rows + 1, f"期待: {rows + 1}行, 実際: {data_count}行"

            # 1行あたりの処理時間計算（ヘッダー除くデータ行数で計算）
            time_per_row = processing_time / rows * 1000  # ミリ秒
            results.append((rows, processing_time, time_per_row))

            print(f"サイズ{rows}行: {processing_time:.3f}秒 ({time_per_row:.3f}ms/行)")

        # スケーラビリティ検証（線形性チェック）
        # 大きなファイルでも1行あたりの処理時間が極端に増加しないことを確認
        time_per_row_values = [result[2] for result in results]
        max_time_per_row = max(time_per_row_values)
        min_time_per_row = min(time_per_row_values)

        # 1行あたりの処理時間の変動が5倍以内
        ratio = (
            max_time_per_row / min_time_per_row
            if min_time_per_row > 0
            else float("inf")
        )
        assert ratio < 5.0, f"処理スケーラビリティが悪い: 最大/最小比 = {ratio:.2f}"

    @pytest.mark.performance
    def test_concurrent_processing_performance(self):
        """並行処理パフォーマンステスト."""
        import concurrent.futures

        # 複数ファイル準備
        file_count = 3
        files = []
        for i in range(file_count):
            file_path = self.create_performance_test_file(
                500, f"concurrent_perf_{i}.xlsx"
            )
            files.append(file_path)

        def process_single_file(file_path):
            """単一ファイル処理."""
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

            start_time = time.time()
            result = directive.process_excel_file(file_path, {"header": True})
            end_time = time.time()

            return end_time - start_time, result["success"]

        # 順次処理時間測定
        sequential_start = time.time()
        sequential_results = []
        for file_path in files:
            time_taken, success = process_single_file(file_path)
            sequential_results.append((time_taken, success))
        sequential_end = time.time()
        sequential_total = sequential_end - sequential_start

        # 並行処理時間測定
        concurrent_start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=file_count) as executor:
            futures = [
                executor.submit(process_single_file, file_path) for file_path in files
            ]
            concurrent_results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]
        concurrent_end = time.time()
        concurrent_total = concurrent_end - concurrent_start

        # 結果検証
        for _time_taken, success in sequential_results + concurrent_results:
            assert success is True

        # 並行処理の効率確認（並行処理が順次処理より高速）
        print(f"順次処理時間: {sequential_total:.3f}秒")
        print(f"並行処理時間: {concurrent_total:.3f}秒")
        print(f"並行処理効率: {(sequential_total / concurrent_total):.2f}倍")

        # 並行処理テストは参考値として実行（環境により効果が異なるため）
        # 少なくとも並行処理でも正常に処理されることを確認
        efficiency_ratio = (
            sequential_total / concurrent_total if concurrent_total > 0 else 0
        )
        print(f"並行処理効率比: {efficiency_ratio:.2f}")

        # 並行処理が極端に遅くないことを確認（2倍以上遅くない）
        assert concurrent_total < sequential_total * 2.0, (
            "並行処理が極端に遅くなっています"
        )

    @pytest.mark.performance
    def test_memory_cleanup_verification(self):
        """メモリクリーンアップ検証テスト."""
        import gc

        # プロセス情報取得
        process = psutil.Process(os.getpid())

        # 初期メモリ測定
        gc.collect()  # ガベージコレクション実行
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # 大量処理実行
        for i in range(5):
            file_path = self.create_performance_test_file(
                1000, f"cleanup_test_{i}.xlsx"
            )

            # 初期化
            self.directive._initialize_processors()

            options = {"header": True}
            result = self.directive.process_excel_file(file_path, options)

            assert result["success"] is True

            # ファイル削除
            os.remove(file_path)

        # メモリクリーンアップ
        gc.collect()

        # 最終メモリ測定
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        print(f"5回処理後のメモリ増加: {memory_increase:.1f}MB")

        # メモリリークがないことを確認（50MB以内の増加）
        assert memory_increase < 50, (
            f"メモリリークの可能性: {memory_increase:.1f}MB増加"
        )

    @pytest.mark.performance
    def test_cpu_usage_monitoring(self):
        """CPU使用率監視テスト."""
        import psutil

        file_path = self.create_performance_test_file(2000)

        # 初期化
        self.directive._initialize_processors()

        # CPU使用率監視開始
        process = psutil.Process(os.getpid())
        _cpu_percent_before = process.cpu_percent()

        # 重い処理実行
        options = {"header": True}
        start_time = time.time()
        result = self.directive.process_excel_file(file_path, options)
        end_time = time.time()

        # CPU使用率測定
        time.sleep(0.1)  # CPU測定のための短い待機
        cpu_percent_after = process.cpu_percent()

        # 結果検証
        assert result["success"] is True

        processing_time = end_time - start_time
        print(f"処理時間: {processing_time:.3f}秒")
        print(f"CPU使用率（処理後）: {cpu_percent_after:.1f}%")

        # CPU使用率が適切な範囲内であることを確認
        # 処理中はCPUを使用するが、極端に高くないことを確認
        assert cpu_percent_after < 100, f"CPU使用率が高すぎる: {cpu_percent_after:.1f}%"

    @pytest.mark.performance
    def test_disk_io_efficiency(self):
        """ディスクI/O効率テスト."""
        import psutil

        # ディスクI/O統計取得
        disk_io_before = psutil.disk_io_counters()

        file_path = self.create_performance_test_file(1500)

        # 初期化
        self.directive._initialize_processors()

        # 処理実行
        options = {"header": True}
        result = self.directive.process_excel_file(file_path, options)

        # ディスクI/O統計取得
        disk_io_after = psutil.disk_io_counters()

        # 結果検証
        assert result["success"] is True

        # I/O統計計算
        if disk_io_before and disk_io_after:
            read_bytes = disk_io_after.read_bytes - disk_io_before.read_bytes
            write_bytes = disk_io_after.write_bytes - disk_io_before.write_bytes

            print(f"読み取りバイト数: {read_bytes / 1024 / 1024:.2f}MB")
            print(f"書き込みバイト数: {write_bytes / 1024 / 1024:.2f}MB")

            # 過度なディスクI/Oが発生していないことを確認
            total_io = (read_bytes + write_bytes) / 1024 / 1024  # MB
            assert total_io < 500, f"ディスクI/Oが多すぎる: {total_io:.2f}MB"

    @pytest.mark.performance
    def test_resource_limits_compliance(self):
        """リソース制限遵守テスト."""
        # 制限値設定
        MAX_PROCESSING_TIME = 15.0  # 秒
        MAX_MEMORY_INCREASE = 150  # MB

        rows = 3000
        file_path = self.create_performance_test_file(rows)

        # 統合測定
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024

        self.directive._initialize_processors()

        start_time = time.time()
        options = {"header": True}
        result = self.directive.process_excel_file(file_path, options)
        end_time = time.time()

        final_memory = process.memory_info().rss / 1024 / 1024

        # リソース使用量計算
        processing_time = end_time - start_time
        memory_increase = final_memory - initial_memory

        # 結果検証
        assert result["success"] is True

        # リソース制限遵守確認
        assert processing_time < MAX_PROCESSING_TIME, (
            f"処理時間制限超過: {processing_time:.2f}秒 > {MAX_PROCESSING_TIME}秒"
        )

        assert memory_increase < MAX_MEMORY_INCREASE, (
            f"メモリ使用量制限超過: {memory_increase:.1f}MB > {MAX_MEMORY_INCREASE}MB"
        )

        print(
            f"リソース使用量 - 時間: {processing_time:.2f}秒, メモリ: {memory_increase:.1f}MB"
        )
        print("✓ 全リソース制限遵守")


if __name__ == "__main__":
    # スタンドアロンテスト実行
    pytest.main([__file__, "-v"])
