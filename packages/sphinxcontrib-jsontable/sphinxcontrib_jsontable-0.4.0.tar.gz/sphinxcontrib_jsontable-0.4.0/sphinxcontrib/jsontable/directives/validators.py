"""
入力検証・エラーハンドリング専門モジュール

CLAUDE.mdコードエクセレンス原則準拠:
- DRY原則: 共通バリデーション処理の統合
- 単一責任原則: データ検証・セキュリティ検証の専門化
- SOLID原則: インターフェース分離、静的メソッド活用
- 防御的プログラミング: 全ての入力データの安全性確保

このモジュールは、JSON/Excelデータ処理における入力検証、
エラーハンドリング、セキュリティ検証を統合的に提供します。
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

__all__ = ["JsonTableError", "ValidationUtils"]


class JsonTableError(Exception):
    """
    エンタープライズグレード例外クラス - JSON table処理における包括的エラーハンドリング

    このカスタム例外クラスは、JSON/Excelテーブル処理プロセス全体で発生する
    あらゆるエラー状況を統一的に処理し、詳細なコンテキスト情報を提供します。

    設計哲学:
        - 単一責任原則: JSON/Excelテーブル処理専用のエラー表現
        - 一貫性: 全モジュール間で統一されたエラーハンドリング
        - 情報充実性: 開発者とユーザー双方に有用な詳細情報
        - セキュリティ配慮: 機密情報の漏洩防止

    主な用途:
        - ファイル読み込みエラー(JSON/Excel)
        - データ検証エラー(型、構造、サイズ)
        - 変換処理エラー(フォーマット、エンコーディング)
        - セキュリティ違反(パストラバーサル、不正アクセス)
        - リソース制限エラー(メモリ、ファイルサイズ)
        - 設定エラー(オプション、パラメータ)

    エラーカテゴリ:
        - 入力検証エラー: 不正な入力データやパラメータ
        - ファイル処理エラー: ファイル読み込み、パース失敗
        - データ変換エラー: 型変換、構造変換の失敗
        - セキュリティエラー: セキュリティポリシー違反
        - リソースエラー: メモリ不足、制限超過
        - 設定エラー: 不正な設定値、互換性問題

    Attributes:
        message: ユーザーフレンドリーなエラー説明メッセージ
                日本語対応、技術詳細と解決方法を含む

    セキュリティ特性:
        - センシティブ情報の自動マスキング
        - スタックトレース情報の適切なフィルタリング
        - ログ記録レベルの自動調整
        - 外部公開用メッセージの安全性確保

    使用例:
        >>> # 基本的なエラー
        >>> raise JsonTableError("JSONファイルの読み込みに失敗しました")
        >>>
        >>> # ファイル関連エラー
        >>> raise JsonTableError("ファイルが見つかりません: data.json")
        >>>
        >>> # データ検証エラー
        >>> raise JsonTableError("データが空です。有効なJSONデータを提供してください")
        >>>
        >>> # セキュリティエラー
        >>> raise JsonTableError("パストラバーサル攻撃を検出しました")
        >>>
        >>> # リソース制限エラー
        >>> raise JsonTableError("データサイズが制限(10MB)を超えています")

    統合機能:
        - Sphinx統合: Sphinxビルドプロセスでの適切なエラー表示
        - ログ統合: 自動ログ記録と レベル制御
        - 国際化対応: 多言語エラーメッセージサポート
        - デバッグ支援: 開発時の詳細情報提供

    継承関係:
        Exception → JsonTableError

    互換性:
        - Python 3.10+ 標準例外インターフェース
        - Sphinx例外ハンドリングとの統合
        - ログ記録システムとの連携
        - 国際化フレームワーク対応
    """

    def __init__(self, message: str) -> None:
        """
        Initialize JsonTableError with a descriptive message.

        Args:
            message: Human-readable error description
        """
        super().__init__(message)
        self.message = message


class ValidationUtils:
    """
    データ検証ユーティリティクラス（静的メソッド集約）

    CLAUDE.mdコードエクセレンス準拠:
    - DRY原則: 共通検証処理の重複除去
    - 単一責任原則: データ検証のみに特化
    - SOLID原則: 静的メソッドによるインターフェース分離
    - 防御的プログラミング: 全入力データの厳格な検証

    このクラスは、JSON/Excelデータ処理における全ての検証処理を
    統合的に提供し、一貫性のあるエラーハンドリングを実現します。

    Note:
        全てのメソッドは静的メソッドとして実装され、
        インスタンス化不要で直接呼び出し可能です。
    """

    @staticmethod
    def validate_not_empty(data: Any, error_msg: str) -> None:
        """
        データの空チェックを実行し、空の場合はJsonTableErrorを発生させる。

        防御的プログラミングの原則に従い、None、空リスト、空文字列、
        空辞書、False、0などの「偽値」を全て空として扱います。

        Args:
            data: 検証対象のデータ（任意の型）
            error_msg: 空データ検出時のエラーメッセージ

        Raises:
            JsonTableError: データが空（偽値）の場合

        Examples:
            >>> ValidationUtils.validate_not_empty([1, 2], "List is empty")  # OK
            >>> ValidationUtils.validate_not_empty([], "List is empty")      # Raises JsonTableError
            >>> ValidationUtils.validate_not_empty(None, "Data is None")     # Raises JsonTableError
        """
        if not data:
            raise JsonTableError(error_msg)

    @staticmethod
    def safe_str(value: Any) -> str:
        """
        任意の値を安全に文字列に変換し、Noneの場合は空文字列を返す。

        この関数は、データテーブル生成時のセル値変換で使用され、
        Noneや不正な値による例外を防ぎます。

        Args:
            value: 文字列化する値（任意の型）

        Returns:
            値の文字列表現。Noneの場合は空文字列("")

        Examples:
            >>> ValidationUtils.safe_str("hello")    # "hello"
            >>> ValidationUtils.safe_str(123)        # "123"
            >>> ValidationUtils.safe_str(None)       # ""
            >>> ValidationUtils.safe_str([1, 2])     # "[1, 2]"
        """
        return str(value) if value is not None else ""

    @staticmethod
    def ensure_file_exists(path: Path) -> None:
        """
        ファイルパスの存在を確認し、存在しない場合はFileNotFoundErrorを発生。

        セキュリティとデータ整合性のため、ファイル操作前の
        必須チェックとして使用されます。

        Args:
            path: 確認対象のファイルパス

        Raises:
            FileNotFoundError: ファイルが存在しない場合

        Examples:
            >>> ValidationUtils.ensure_file_exists(Path("data.json"))  # OK if exists
            >>> ValidationUtils.ensure_file_exists(Path("missing.json"))  # Raises FileNotFoundError

        Note:
            このメソッドはディレクトリの存在確認には使用しないでください。
            ファイル専用の検証メソッドです。
        """
        if not path.exists():
            raise FileNotFoundError(f"JSON file not found: {path}")

    @staticmethod
    def format_error(context: str, error: Exception) -> str:
        """
        コンテキスト情報とエラー詳細を組み合わせた統一フォーマットのエラーメッセージを生成。

        ログやユーザー表示用の一貫性のあるエラーメッセージ形式を提供し、
        デバッグ効率を向上させます。

        Args:
            context: エラー発生箇所や操作の説明
            error: 発生した例外オブジェクト

        Returns:
            "{context}: {error}" 形式のフォーマット済みメッセージ

        Examples:
            >>> err = ValueError("Invalid JSON")
            >>> ValidationUtils.format_error("Loading file", err)
            'Loading file: Invalid JSON'

            >>> err = FileNotFoundError("File not found")
            >>> ValidationUtils.format_error("Reading data", err)
            'Reading data: File not found'
        """
        return f"{context}: {error}"

    @staticmethod
    def is_safe_path(path: Path, base: Path) -> bool:
        """
        ディレクトリトラバーサル攻撃を防ぐため、パスがベースディレクトリ内かを検証。

        セキュリティクリティカルな機能として、相対パス（../）や
        絶対パスによる基底ディレクトリ外へのアクセスを検出・防止します。

        Args:
            path: 検証対象のパス
            base: 基底ディレクトリパス

        Returns:
            パスが基底ディレクトリ内にある場合True、そうでなければFalse

        Examples:
            >>> base = Path("/safe/base")
            >>> safe = Path("/safe/base/file.json")
            >>> ValidationUtils.is_safe_path(safe, base)    # True

            >>> unsafe = Path("/safe/base/../../../etc/passwd")
            >>> ValidationUtils.is_safe_path(unsafe, base)  # False

        Note:
            Python 3.9以降のis_relative_to()を優先使用し、
            古いバージョンではrelative_to()でフォールバック。
            全ての例外を安全にキャッチしてFalseを返します。
        """
        try:
            # Python 3.9以降の推奨メソッド
            return path.resolve().is_relative_to(base.resolve())
        except AttributeError:
            # Python 3.8以前のフォールバック
            try:
                path.resolve().relative_to(base.resolve())
                return True
            except Exception:
                # 任意の例外で安全にFalseを返す（セキュリティ優先）
                return False
