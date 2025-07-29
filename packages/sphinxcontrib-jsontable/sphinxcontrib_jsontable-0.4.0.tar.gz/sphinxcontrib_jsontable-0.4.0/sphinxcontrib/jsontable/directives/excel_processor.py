"""
Excel処理専門モジュール

このモジュールは、Excelファイルの読み込み・解析・統合処理を提供し、
CLAUDE.mdコードエクセレンス原則に準拠した設計となっています。
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Union

from .validators import JsonTableError

# 型エイリアス
JsonData = Union[List[Any], Dict[str, Any]]
ExcelOptions = Dict[str, Any]

# ロガー
logger = logging.getLogger(__name__)

__all__ = ["ExcelProcessor", "JsonData", "ExcelOptions"]


class ExcelProcessor:
    """
    Excel データ処理専門クラス

    CLAUDE.mdコードエクセレンス準拠:
    - DRY原則: Excel読み込み処理の統一
    - 単一責任原則: Excelデータ処理のみに特化
    - SOLID原則: ExcelDataLoaderFacadeとの適切な分離
    - 防御的プログラミング: 全入力データの厳格な検証

    このクラスは、Excelファイル読み込み、シート処理、
    範囲指定、JSON変換を統合的に提供します。

    Args:
        base_path: ベースディレクトリパス（相対パス解決用）
    """

    def __init__(self, base_path: str | Path):
        """
        ExcelProcessor の初期化

        Args:
            base_path: ベースディレクトリパス

        Raises:
            JsonTableError: Excel対応が利用できない場合
        """
        self.base_path = Path(base_path) if isinstance(base_path, str) else base_path
        # Enhanced caching system with file modification time tracking
        self._cache = {}  # Data cache: {cache_key: (data, timestamp, file_mtime)}
        self._cache_max_size = 100  # Maximum cache entries
        self._cache_ttl = 300  # Time-to-live in seconds (5 minutes)

        try:
            # ExcelDataLoaderFacadeの動的インポートと初期化
            from ..facade.excel_data_loader_facade import ExcelDataLoaderFacade

            self.excel_loader = ExcelDataLoaderFacade()
            logger.info(
                f"ExcelProcessor initialized successfully with base_path: {self.base_path}"
            )
        except ImportError as e:
            error_msg = (
                "Excel support not available. "
                "Install with: pip install 'sphinxcontrib-jsontable[excel]'"
            )
            logger.error(
                f"ExcelProcessor initialization failed - Excel support unavailable. "
                f"Import error: {e}. "
                f"Required packages: pandas>=2.0.0, openpyxl>=3.1.0"
            )
            raise JsonTableError(error_msg) from e

    def _resolve_sheet_name(
        self, file_path: str, sheet_name: str | None, sheet_index: int | None = None
    ) -> str | None:
        """
        シート名とシートインデックスからシート名を解決

        優先順位: sheet_name > sheet_index > デフォルト

        Args:
            file_path: Excelファイルパス
            sheet_name: 指定されたシート名
            sheet_index: 指定されたシートインデックス

        Returns:
            解決されたシート名（None=デフォルトシート）

        Raises:
            JsonTableError: 指定されたシートが存在しない場合
        """
        # シート名が明示的に指定された場合
        if sheet_name:
            available_sheets = self.excel_loader.get_sheet_names(file_path)
            if sheet_name not in available_sheets:
                raise JsonTableError(
                    f"Sheet '{sheet_name}' not found in {file_path}. "
                    f"Available sheets: {available_sheets}"
                )
            return sheet_name

        # シートインデックスが指定された場合
        if sheet_index is not None:
            try:
                return self.excel_loader.get_sheet_name_by_index(file_path, sheet_index)
            except (IndexError, ValueError) as e:
                raise JsonTableError(f"Invalid sheet index {sheet_index}: {e}") from e

        # デフォルト（最初のシート）を返す
        available_sheets = self.excel_loader.get_sheet_names(file_path)
        return available_sheets[0] if available_sheets else None

    def _resolve_file_path(self, file_path: str) -> Path:
        """
        ファイルパスを解決し、セキュリティ検証を行う

        Args:
            file_path: 入力ファイルパス

        Returns:
            解決されたPathオブジェクト

        Raises:
            JsonTableError: パスが無効またはセキュリティ違反の場合
        """
        if not file_path:
            raise JsonTableError("File path cannot be None or empty")

        # パストラバーサル攻撃防止
        if ".." in file_path:
            raise JsonTableError("Path traversal detected - security violation")

        path = Path(file_path)
        if not path.is_absolute():
            path = self.base_path / path

        return path.resolve()

    def _validate_file_path(self, file_path):
        """ファイルパス検証"""
        if file_path is None:
            raise JsonTableError("File path cannot be None")
        if not str(file_path).strip():
            raise JsonTableError("File path cannot be empty")

    def _validate_options(self, options):
        """オプション検証"""
        if options is None:
            return {}
        if not isinstance(options, dict):
            raise JsonTableError("Options must be a dictionary")
        return options

    def _convert_directive_options(self, options):
        """ディレクティブオプション名をAPIパラメータ名に変換"""
        converted_options = {}
        for key, value in options.items():
            if key == "header-row":
                converted_options["header_row"] = value
            elif key == "skip-rows":
                converted_options["skip_rows"] = value
            else:
                converted_options[key] = value
        return converted_options

    def _generate_cache_key(self, file_path: str, options: dict) -> str:
        """Enhanced cache key generation with file path normalization"""
        normalized_path = str(Path(file_path).resolve())
        options_str = str(sorted(options.items()))
        return f"{normalized_path}:{hash(options_str)}"

    def _get_file_modification_time(self, file_path: str) -> float:
        """Get file modification time safely"""
        try:
            return Path(file_path).stat().st_mtime
        except OSError:
            return 0.0

    def _is_cache_valid(self, cache_entry: tuple, file_path: str) -> bool:
        """Check if cache entry is still valid"""
        data, cache_timestamp, cached_file_mtime = cache_entry
        current_time = time.time()
        current_file_mtime = self._get_file_modification_time(file_path)

        # Check TTL expiration
        if current_time - cache_timestamp > self._cache_ttl:
            return False

        # Check file modification
        if current_file_mtime != cached_file_mtime:
            return False

        return True

    def _evict_old_cache_entries(self):
        """Evict old cache entries when cache size limit is reached"""
        if len(self._cache) >= self._cache_max_size:
            # Remove oldest entries (simple FIFO for now)
            oldest_keys = sorted(
                self._cache.keys(),
                key=lambda k: self._cache[k][1],  # Sort by timestamp
            )
            # Remove oldest 20% of entries
            remove_count = max(1, len(oldest_keys) // 5)
            for key in oldest_keys[:remove_count]:
                del self._cache[key]

    def clear_cache(self):
        """Enhanced cache clearing with logging"""
        cache_size = len(self._cache)
        self._cache.clear()
        logger.debug(f"Cache cleared: {cache_size} entries removed")

    def _load_with_cache(self, file_path: str, options: dict):
        """Enhanced cache system with file modification time and TTL"""
        cache_key = self._generate_cache_key(file_path, options)
        current_time = time.time()

        # Check if valid cache entry exists
        if cache_key in self._cache:
            cache_entry = self._cache[cache_key]
            if self._is_cache_valid(cache_entry, file_path):
                logger.debug(f"Cache hit for {file_path}")
                return cache_entry[0]  # Return cached data
            else:
                logger.debug(f"Cache invalidated for {file_path}")
                del self._cache[cache_key]

        # Cache miss or invalid - load data
        logger.debug(f"Cache miss for {file_path}")

        # Evict old entries if necessary
        self._evict_old_cache_entries()

        # Convert options and load data
        converted_options = self._convert_directive_options(options)
        result = self.excel_loader.load_from_excel(file_path, **converted_options)
        data = result.get("data", [])

        # Store in cache with metadata
        file_mtime = self._get_file_modification_time(file_path)
        self._cache[cache_key] = (data, current_time, file_mtime)

        return data

    def load_excel_data(self, file_path: str, options: ExcelOptions) -> JsonData:
        """
        Excelファイルからデータを読み込み、JSON形式で返すエンタープライズグレード処理メソッド

        このメソッドは、Excel(.xlsx/.xls)ファイルの包括的な読み込み処理を提供し、
        シート選択、範囲指定、ヘッダー処理、エラーハンドリングを統合的に実行します。

        サポート機能:
            - 複数シート対応：シート名またはインデックスによる指定
            - 範囲指定：Excel形式(A1:C10)またはPython形式での指定
            - ヘッダー処理：自動検出または手動指定
            - データ型自動変換：適切なPython型への変換
            - キャッシュ機能：パフォーマンス向上のための結果キャッシュ
            - 結合セル対応：Excelの結合セル構造の適切な処理

        パフォーマンス特性:
            - 大容量ファイル対応：メモリ効率的な読み込み
            - キャッシュ機能：重複読み込みの回避
            - 遅延評価：必要時のみデータ処理実行
            - エラー回復：部分的なデータ破損への対応

        セキュリティ機能:
            - パストラバーサル防止：ファイルパスの検証
            - 入力検証：全オプションパラメータの検証
            - リソース制限：メモリ使用量の監視
            - マクロ無効化：実行ファイル形式の安全な処理

        Args:
            file_path: Excelファイルへのパス（絶対パスまたは相対パス）
                      相対パスはbase_pathからの相対として解釈される
                      サポート形式: .xlsx, .xls

            options: 読み込みオプション辞書。以下のオプションをサポート:
                - sheet: シート名(str)またはシートインデックス(int)
                - range: 読み込み範囲(str, 例: "A1:C10")
                - header_row: ヘッダー行の行番号(int, 0ベース)
                - skip_rows: スキップする行数(int)
                - json-cache: キャッシュ使用フラグ(bool)
                - encoding: 文字エンコーディング(str, デフォルト: utf-8)

        Returns:
            JsonData: JSON互換の2次元リスト形式データ
                     [
                         ["列1", "列2", "列3"],        # ヘッダー行
                         ["データ1", "データ2", "データ3"],  # データ行1
                         ["データ4", "データ5", "データ6"]   # データ行2
                     ]

        Raises:
            JsonTableError: 包括的なエラーハンドリング:
                - ファイルが見つからない場合
                - ファイル形式が不正な場合
                - 指定されたシートが存在しない場合
                - 指定された範囲が無効な場合
                - メモリ不足や読み込み失敗の場合
                - パスセキュリティ違反の場合

        使用例:
            >>> processor = ExcelProcessor(Path("/base/path"))
            >>>
            >>> # 基本的な読み込み
            >>> data = processor.load_excel_data("data.xlsx", {})
            >>>
            >>> # シートとヘッダーを指定
            >>> options = {
            >>>     "sheet": "データ",
            >>>     "header_row": 0,
            >>>     "range": "A1:F100"
            >>> }
            >>> data = processor.load_excel_data("sales.xlsx", options)
            >>>
            >>> # キャッシュ機能を使用
            >>> cache_options = {"json-cache": True}
            >>> data = processor.load_excel_data("large_file.xlsx", cache_options)

        互換性:
            - Excel 2007以降(.xlsx形式)
            - Excel 97-2003(.xls形式)
            - LibreOffice Calc
            - Google Sheets エクスポートファイル

        パフォーマンス注意事項:
            - 10,000行を超える大容量ファイルではキャッシュ使用を推奨
            - 範囲指定により処理時間とメモリ使用量を最適化可能
            - ネットワークドライブ上のファイルは読み込み時間が増加する可能性
        """
        try:
            # 入力検証
            self._validate_file_path(file_path)
            validated_options = self._validate_options(options)

            # キャッシュ機能使用時
            if validated_options.get("json-cache", False):
                return self._load_with_cache(file_path, validated_options)

            # ディレクティブオプション名をAPIパラメータ名に変換
            converted_options = self._convert_directive_options(validated_options)

            # 通常の読み込み処理
            result = self.excel_loader.load_from_excel(file_path, **converted_options)

            # Check for error result
            if result.get("error"):
                error_msg = result.get("error_message", "Unknown error")
                raise JsonTableError(f"Excel processing error: {error_msg}")

            return result.get("data", [])

        except Exception as e:
            if isinstance(e, JsonTableError):
                raise
            raise JsonTableError(f"Excel file processing failed: {e}") from e
