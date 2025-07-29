"""Excel Reader Interface - Abstract interface for Excel reading operations.

Defines the contract for Excel reading implementations with clean,
testable interface design.

CLAUDE.md Code Excellence Compliance:
- Interface Segregation: Clean, focused interface
- Dependency Inversion: Abstract interface for implementations
- Single Responsibility: Excel reading contract only
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Union

from .excel_workbook_info import ReadResult, WorkbookInfo


class IExcelReader(ABC):
    """Abstract interface for Excel reading operations.

    Defines the contract that all Excel reader implementations must follow.
    Enables dependency injection and testing through interface segregation.
    """

    @abstractmethod
    def validate_file(self, file_path: Union[str, Path]) -> WorkbookInfo:
        """Validate Excel file and return workbook information.

        Args:
            file_path: Path to Excel file

        Returns:
            WorkbookInfo containing file metadata

        Raises:
            ExcelFileNotFoundError: If file doesn't exist
            FileAccessError: If file cannot be accessed
            ExcelProcessingError: If file is corrupted or invalid
        """
        pass

    @abstractmethod
    def get_sheet_names(self, file_path: Union[str, Path]) -> List[str]:
        """Get list of sheet names from Excel file.

        Args:
            file_path: Path to Excel file

        Returns:
            List of sheet names

        Raises:
            ExcelFileNotFoundError: If file doesn't exist
            ExcelProcessingError: If file cannot be read
        """
        pass

    @abstractmethod
    def read_workbook(
        self,
        file_path: Union[str, Path],
        sheet_name: Optional[str] = None,
        sheet_index: Optional[int] = None,
        **kwargs,
    ) -> ReadResult:
        """Read Excel workbook and return data with metadata.

        Args:
            file_path: Path to Excel file
            sheet_name: Specific sheet name to read
            sheet_index: Specific sheet index to read (0-based)
            **kwargs: Additional reading options

        Returns:
            ReadResult containing DataFrame and metadata

        Raises:
            ExcelFileNotFoundError: If file doesn't exist
            WorksheetNotFoundError: If specified sheet doesn't exist
            ExcelProcessingError: If reading fails
        """
        pass

    @abstractmethod
    def read_sheet(
        self, file_path: Union[str, Path], sheet_identifier: Union[str, int], **kwargs
    ) -> ReadResult:
        """Read specific sheet from Excel file.

        Args:
            file_path: Path to Excel file
            sheet_identifier: Sheet name (str) or index (int)
            **kwargs: Additional reading options

        Returns:
            ReadResult containing sheet data and metadata

        Raises:
            WorksheetNotFoundError: If sheet doesn't exist
            ExcelProcessingError: If reading fails
        """
        pass
