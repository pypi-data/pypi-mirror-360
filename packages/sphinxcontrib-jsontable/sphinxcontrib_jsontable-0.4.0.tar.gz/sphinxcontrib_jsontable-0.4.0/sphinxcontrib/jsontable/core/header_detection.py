"""Header Detection - Specialized header analysis functionality.

Clean separation of header detection logic with advanced analysis capabilities.

CLAUDE.md Code Excellence Compliance:
- Single Responsibility: Header detection and analysis only
- DRY Principle: Centralized header analysis logic
- YAGNI Principle: Essential detection features only
"""

import re
from typing import List

import pandas as pd

from ..errors.excel_errors import DataConversionError
from .data_conversion_types import HeaderDetectionResult


class HeaderDetector:
    """Specialized header detection functionality.

    Provides advanced header detection analysis with confidence scoring
    and Japanese language support.
    """

    def __init__(self, header_keywords: List[str] = None):
        """Initialize header detector with configuration.

        Args:
            header_keywords: Keywords that indicate header presence
        """
        self.header_keywords = header_keywords or [
            "名前",
            "name",
            "氏名",
            "項目",
            "item",
            "title",
            "タイトル",
            "id",
            "識別子",
            "番号",
            "no",
            "number",
            "date",
            "日付",
            "時間",
            "time",
        ]

    def detect_header(self, df: pd.DataFrame) -> HeaderDetectionResult:
        """Detect whether DataFrame has a header row.

        Implements comprehensive header detection with multiple analysis factors.

        Args:
            df: DataFrame to analyze

        Returns:
            HeaderDetectionResult with detection analysis
        """
        if df.empty or len(df) < 2:
            return HeaderDetectionResult(
                has_header=False,
                confidence=0.0,
                headers=[],
                analysis={"reason": "insufficient_data", "rows": len(df)},
            )

        try:
            # Analyze first row (potential header)
            first_row = df.iloc[0]
            string_ratio = self._calculate_string_ratio(first_row)

            # Analyze second row (potential data)
            second_row = df.iloc[1]
            numeric_ratio = self._calculate_numeric_ratio(second_row)

            # Check for header keywords in column names
            keyword_match = self._check_header_keywords_in_columns(df.columns)

            # Calculate confidence based on multiple factors
            confidence = self._calculate_header_confidence(
                string_ratio, numeric_ratio, keyword_match
            )

            has_header = confidence >= 0.6  # Threshold for header detection

            headers = [str(val) for val in first_row] if has_header else []

            analysis = {
                "string_ratio": string_ratio,
                "numeric_ratio": numeric_ratio,
                "keyword_match": keyword_match,
                "confidence_threshold": 0.6,
                "factors_analyzed": [
                    "string_ratio",
                    "numeric_ratio",
                    "keyword_presence",
                ],
            }

            return HeaderDetectionResult(
                has_header=has_header,
                confidence=confidence,
                headers=headers,
                analysis=analysis,
            )

        except Exception as e:
            raise DataConversionError(
                "header_detection",
                message=f"Failed to detect headers: {e}",
                original_error=e,
            ) from e

    def _calculate_string_ratio(self, row: pd.Series) -> float:
        """Calculate ratio of string values in row."""
        if len(row) == 0:
            return 0.0

        string_count = sum(1 for val in row if isinstance(val, str))
        return string_count / len(row)

    def _calculate_numeric_ratio(self, row: pd.Series) -> float:
        """Calculate ratio of numeric values in row."""
        if len(row) == 0:
            return 0.0

        numeric_count = sum(
            1 for val in row if pd.notna(val) and isinstance(val, (int, float))
        )
        return numeric_count / len(row)

    def _check_header_keywords_in_columns(self, columns: List[str]) -> bool:
        """Check if any column names contain header keywords."""
        column_text = " ".join(str(col).lower() for col in columns)

        for keyword in self.header_keywords:
            if keyword.lower() in column_text:
                return True
        return False

    def _calculate_header_confidence(
        self, string_ratio: float, numeric_ratio: float, keyword_match: bool
    ) -> float:
        """Calculate overall confidence score for header detection."""
        # Base confidence from string ratio in first row
        confidence = string_ratio * 0.4

        # Boost if second row is mostly numeric (data pattern)
        if numeric_ratio > 0.5:
            confidence += 0.3

        # Boost if header keywords found
        if keyword_match:
            confidence += 0.3

        # Ensure confidence is in valid range
        return min(max(confidence, 0.0), 1.0)


class HeaderNormalizer:
    """Specialized header normalization functionality.

    Provides consistent header name processing with Japanese language support.
    """

    def __init__(self):
        """Initialize header normalizer with character mappings."""
        # Japanese character mappings for header normalization
        self._japanese_char_map = {
            "（": "_",
            "）": "_",
            "［": "_",
            "］": "_",
            "【": "_",
            "】": "_",
            "〈": "_",
            "〉": "_",
            "《": "_",
            "》": "_",
            "「": "_",
            "」": "_",
            "『": "_",
            "』": "_",
        }

    def normalize_headers(
        self, headers: List[str], japanese_support: bool = True
    ) -> List[str]:
        """Normalize header names for consistency.

        Args:
            headers: List of header names to normalize
            japanese_support: Enable Japanese character handling

        Returns:
            Normalized header names
        """
        try:
            normalized = []
            seen_headers = set()

            for i, header in enumerate(headers):
                # Basic normalization
                normalized_header = str(header).strip()

                # Handle empty headers
                if not normalized_header or normalized_header.lower() in [
                    "nan",
                    "none",
                    "null",
                ]:
                    normalized_header = f"Column_{i + 1}"

                # Apply Japanese-specific normalization if enabled
                if japanese_support:
                    normalized_header = self._normalize_japanese_header(
                        normalized_header
                    )

                # Handle duplicates
                original_header = normalized_header
                counter = 1
                while normalized_header in seen_headers:
                    normalized_header = f"{original_header}_{counter}"
                    counter += 1

                seen_headers.add(normalized_header)
                normalized.append(normalized_header)

            return normalized

        except Exception as e:
            raise DataConversionError(
                "header_normalization",
                message=f"Failed to normalize headers: {e}",
                original_error=e,
            ) from e

    def _normalize_japanese_header(self, header: str) -> str:
        """Apply Japanese-specific header normalization."""
        # Replace Japanese punctuation with underscores
        for japanese_char, replacement in self._japanese_char_map.items():
            header = header.replace(japanese_char, replacement)

        # Remove excessive underscores and clean up
        header = re.sub(r"_+", "_", header)
        header = header.strip("_")

        return header
