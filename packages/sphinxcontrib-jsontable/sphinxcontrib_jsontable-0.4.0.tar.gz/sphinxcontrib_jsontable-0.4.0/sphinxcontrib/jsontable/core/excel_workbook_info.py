"""Excel Workbook Information - Data structures for Excel metadata.

Extracted data classes for workbook information and read results.
Focuses on data representation with clean, testable structures.

CLAUDE.md Code Excellence Compliance:
- Single Responsibility: Excel metadata representation only
- DRY Principle: Centralized data structures
- YAGNI Principle: Essential data fields only
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd


@dataclass
class WorkbookInfo:
    """Information about an Excel workbook.

    Contains comprehensive metadata about Excel files including
    security-related information and structural details.
    """

    file_path: Path
    sheet_names: List[str]
    has_macros: bool
    has_external_links: bool
    file_size: int
    format_type: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation of workbook information
        """
        return {
            "file_path": str(self.file_path),
            "sheet_names": self.sheet_names,
            "has_macros": self.has_macros,
            "has_external_links": self.has_external_links,
            "file_size": self.file_size,
            "format_type": self.format_type,
            "total_sheets": len(self.sheet_names),
        }

    @property
    def is_legacy_format(self) -> bool:
        """Check if workbook uses legacy Excel format (.xls)."""
        return self.format_type.lower() in ["xls", "excel"]

    @property
    def has_security_concerns(self) -> bool:
        """Check if workbook has potential security concerns."""
        return self.has_macros or self.has_external_links


@dataclass
class ReadResult:
    """Result of reading Excel data.

    Contains the read DataFrame along with metadata about
    the reading operation and workbook information.
    """

    dataframe: pd.DataFrame
    workbook_info: WorkbookInfo
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary containing all read result information
        """
        return {
            "data_shape": self.dataframe.shape,
            "columns": list(self.dataframe.columns),
            "workbook_info": self.workbook_info.to_dict(),
            "metadata": self.metadata,
        }

    @property
    def row_count(self) -> int:
        """Number of rows in the DataFrame."""
        return len(self.dataframe)

    @property
    def column_count(self) -> int:
        """Number of columns in the DataFrame."""
        return len(self.dataframe.columns)

    @property
    def is_empty(self) -> bool:
        """Check if the read result contains no data."""
        return self.dataframe.empty
