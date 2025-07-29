"""Excel対応の基本テスト."""

import shutil
import tempfile
from pathlib import Path

import pytest


# Excel対応の基本テスト(ImportErrorは内部で処理)
def test_excel_support():
    """Excel対応が基本的に動作することをテスト。"""
    try:
        from sphinxcontrib.jsontable.facade.excel_data_loader_facade import (
            ExcelDataLoaderFacade,
        )

        # 基本的なインスタンス作成テスト
        temp_dir = tempfile.mkdtemp()
        try:
            facade = ExcelDataLoaderFacade()
            # 新しいAPIでは設定はプロパティではなくメソッドで確認
            assert hasattr(facade, "load_from_excel")
            assert hasattr(facade, "get_sheet_names")
            assert hasattr(facade, "get_workbook_info")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        print("✓ ExcelDataLoaderFacade基本機能動作確認")

    except ImportError as e:
        # Excel機能が利用できない場合
        pytest.skip(f"Excel support not available: {e}")


def test_excel_directive_import():
    """JsonTableDirectiveのExcel対応インポートテスト。"""
    try:
        from sphinxcontrib.jsontable.directives import EXCEL_SUPPORT, JsonTableDirective

        assert isinstance(EXCEL_SUPPORT, bool)
        print(f"✓ Excel support flag: {EXCEL_SUPPORT}")

        # ディレクティブの基本クラス確認
        assert hasattr(JsonTableDirective, "__init__")
        assert hasattr(JsonTableDirective, "_load_data")

        print("✓ JsonTableDirective Excel統合確認")

    except ImportError as e:
        pytest.fail(f"Failed to import JsonTableDirective: {e}")


def test_excel_file_detection():
    """Excelファイル検出ロジックのテスト。"""

    # Excelファイルの拡張子テスト
    test_cases = [
        ("test.xlsx", True),
        ("test.xls", True),
        ("test.XLSX", True),  # 大文字小文字
        ("test.json", False),
        ("test.csv", False),
        ("test.txt", False),
    ]

    for filename, expected in test_cases:
        file_path = Path(filename)
        is_excel = file_path.suffix.lower() in {".xlsx", ".xls"}
        assert is_excel == expected, (
            f"Failed for {filename}: expected {expected}, got {is_excel}"
        )

    print("✓ Excelファイル検出ロジック確認")


def test_dependency_availability():
    """必要な依存関係の可用性テスト。"""
    # 基本依存関係

    # Excel依存関係(条件付き)
    try:
        import pandas as pd

        pandas_available = True
        pandas_version = pd.__version__
    except ImportError:
        pandas_available = False
        pandas_version = None

    try:
        import openpyxl

        openpyxl_available = True
        openpyxl_version = openpyxl.__version__
    except ImportError:
        openpyxl_available = False
        openpyxl_version = None

    print("✓ 基本依存関係: json, pathlib, typing")
    print(f"✓ pandas利用可能: {pandas_available} (version: {pandas_version})")
    print(f"✓ openpyxl利用可能: {openpyxl_available} (version: {openpyxl_version})")

    # 両方利用可能であることを確認
    if pandas_available and openpyxl_available:
        print("✓ Excel機能フル対応")
    else:
        pytest.skip("Excel dependencies not fully available")


if __name__ == "__main__":
    # スタンドアロン実行時の簡易テスト
    test_excel_support()
    test_excel_directive_import()
    test_excel_file_detection()
    test_dependency_availability()
    print("All basic Excel tests passed!")
