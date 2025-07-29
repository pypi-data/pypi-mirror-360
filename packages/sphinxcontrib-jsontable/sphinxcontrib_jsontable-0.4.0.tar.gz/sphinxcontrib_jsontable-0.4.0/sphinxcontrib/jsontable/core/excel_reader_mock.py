"""Mock Excel Reader - Testing implementation for Excel reading operations.

Mock implementation for testing and development purposes with call tracking
and configurable behavior simulation.

CLAUDE.md Code Excellence Compliance:
- Single Responsibility: Testing mock functionality only
- Testability: Call tracking and behavior simulation
- DRY Principle: Reusable mock implementation
"""

from pathlib import Path
from typing import List, Optional, Union

import pandas as pd

from ..errors.excel_errors import ExcelProcessingError
from .excel_reader_interface import IExcelReader
from .excel_workbook_info import ReadResult, WorkbookInfo


class MockExcelReader(IExcelReader):
    """Mock implementation for testing purposes.

    Provides configurable mock behavior for Excel reading operations
    with comprehensive call tracking for test verification.
    """

    def __init__(
        self,
        mock_workbook_info: Optional[WorkbookInfo] = None,
        mock_read_result: Optional[ReadResult] = None,
        mock_sheet_names: Optional[List[str]] = None,
        should_fail: bool = False,
        error_to_raise: Optional[Exception] = None,
    ):
        """Initialize mock reader with configurable behavior.

        Args:
            mock_workbook_info: Fixed result for validate_file
            mock_read_result: Fixed result for read_workbook
            mock_sheet_names: Fixed result for get_sheet_names
            should_fail: Whether to raise errors
            error_to_raise: Specific error to raise
        """
        self.mock_workbook_info = mock_workbook_info
        self.mock_read_result = mock_read_result
        self.mock_sheet_names = mock_sheet_names or ["Sheet1", "Sheet2"]
        self.should_fail = should_fail
        self.error_to_raise = error_to_raise or ExcelProcessingError("Mock error")

        # Call tracking for test verification
        self.validate_file_calls = []
        self.read_workbook_calls = []
        self.read_sheet_calls = []
        self.get_sheet_names_calls = []

    def validate_file(self, file_path: Union[str, Path]) -> WorkbookInfo:
        """Mock validate_file implementation with call tracking."""
        self.validate_file_calls.append({"file_path": str(file_path)})

        if self.should_fail:
            raise self.error_to_raise

        if self.mock_workbook_info:
            return self.mock_workbook_info

        # Default mock result
        return WorkbookInfo(
            file_path=Path(file_path),
            sheet_names=self.mock_sheet_names,
            has_macros=False,
            has_external_links=False,
            file_size=1024,
            format_type=".xlsx",
        )

    def get_sheet_names(self, file_path: Union[str, Path]) -> List[str]:
        """Mock get_sheet_names implementation with call tracking."""
        self.get_sheet_names_calls.append({"file_path": str(file_path)})

        if self.should_fail:
            raise self.error_to_raise

        return self.mock_sheet_names

    def read_workbook(
        self,
        file_path: Union[str, Path],
        sheet_name: Optional[str] = None,
        sheet_index: Optional[int] = None,
        **kwargs,
    ) -> ReadResult:
        """Mock read_workbook implementation with call tracking."""
        self.read_workbook_calls.append(
            {
                "file_path": str(file_path),
                "sheet_name": sheet_name,
                "sheet_index": sheet_index,
                "kwargs": kwargs,
            }
        )

        if self.should_fail:
            raise self.error_to_raise

        if self.mock_read_result:
            return self.mock_read_result

        # Default mock result
        mock_df = pd.DataFrame({"A": [1, 2, 3], "B": ["a", "b", "c"]})
        mock_workbook_info = self.validate_file(file_path)

        return ReadResult(
            dataframe=mock_df,
            workbook_info=mock_workbook_info,
            metadata={
                "mock": True,
                "sheet_name": sheet_name or self.mock_sheet_names[0],
            },
        )

    def read_sheet(
        self, file_path: Union[str, Path], sheet_identifier: Union[str, int], **kwargs
    ) -> ReadResult:
        """Mock read_sheet implementation with call tracking."""
        self.read_sheet_calls.append(
            {
                "file_path": str(file_path),
                "sheet_identifier": sheet_identifier,
                "kwargs": kwargs,
            }
        )

        if self.should_fail:
            raise self.error_to_raise

        # Convert sheet_identifier to appropriate parameters
        if isinstance(sheet_identifier, str):
            return self.read_workbook(file_path, sheet_name=sheet_identifier, **kwargs)
        else:
            return self.read_workbook(file_path, sheet_index=sheet_identifier, **kwargs)

    def reset_call_tracking(self):
        """Reset all call tracking lists for fresh testing."""
        self.validate_file_calls.clear()
        self.read_workbook_calls.clear()
        self.read_sheet_calls.clear()
        self.get_sheet_names_calls.clear()

    def get_call_summary(self) -> dict:
        """Get summary of all tracked calls for test verification."""
        return {
            "validate_file_calls": len(self.validate_file_calls),
            "read_workbook_calls": len(self.read_workbook_calls),
            "read_sheet_calls": len(self.read_sheet_calls),
            "get_sheet_names_calls": len(self.get_sheet_names_calls),
            "total_calls": (
                len(self.validate_file_calls)
                + len(self.read_workbook_calls)
                + len(self.read_sheet_calls)
                + len(self.get_sheet_names_calls)
            ),
        }
