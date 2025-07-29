"""Data Conversion Types - Type definitions and data structures.

Clean data structures for data conversion operations with focused responsibility.

CLAUDE.md Code Excellence Compliance:
- Single Responsibility: Type definitions and data structures only
- DRY Principle: Centralized data type definitions
- YAGNI Principle: Essential data fields only
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import pandas as pd


@dataclass
class ConversionResult:
    """Structured result of data conversion operations.

    Contains the converted data along with metadata about the conversion
    process and detected headers.
    """

    data: List[List[Any]]
    has_header: bool
    headers: List[str]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation of conversion result
        """
        return {
            "data": self.data,
            "has_header": self.has_header,
            "headers": self.headers,
            "metadata": self.metadata,
            "rows": len(self.data),
            "columns": len(self.data[0]) if self.data else 0,
        }

    @property
    def row_count(self) -> int:
        """Number of data rows."""
        return len(self.data)

    @property
    def column_count(self) -> int:
        """Number of columns."""
        return len(self.data[0]) if self.data else 0

    @property
    def is_empty(self) -> bool:
        """Check if conversion result is empty."""
        return len(self.data) == 0


@dataclass
class HeaderDetectionResult:
    """Result of header detection analysis.

    Contains analysis results for determining whether the first row
    of data should be treated as headers.
    """

    has_header: bool
    confidence: float
    headers: List[str]
    analysis: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary containing header detection results
        """
        return {
            "has_header": self.has_header,
            "confidence": self.confidence,
            "headers": self.headers,
            "analysis": self.analysis,
        }

    @property
    def is_confident(self) -> bool:
        """Check if detection confidence is high (>= 0.8)."""
        return self.confidence >= 0.8

    @property
    def header_count(self) -> int:
        """Number of detected headers."""
        return len(self.headers)


class IDataConverter(ABC):
    """Abstract interface for data conversion functionality.

    Defines the contract for data conversion implementations with
    clean separation of concerns.
    """

    @abstractmethod
    def convert_dataframe_to_json(
        self, df: pd.DataFrame, header_row: Optional[int] = None
    ) -> ConversionResult:
        """Convert DataFrame to JSON-compatible format.

        Args:
            df: Pandas DataFrame to convert
            header_row: Row number to use as headers (0-based)

        Returns:
            ConversionResult with converted data and metadata
        """
        pass

    @abstractmethod
    def detect_header(self, df: pd.DataFrame) -> HeaderDetectionResult:
        """Detect if DataFrame has a header row.

        Args:
            df: DataFrame to analyze

        Returns:
            HeaderDetectionResult with detection analysis
        """
        pass

    @abstractmethod
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
        pass
