"""Excel Utilities - Backward compatibility and utility functions.

This module provides utility functions and backward compatibility methods
for the Excel data processing system.

CLAUDE.md Code Excellence Compliance:
- Single Responsibility: Utility functions and compatibility
- DRY Principle: Centralized utility logic
- YAGNI Principle: Only essential utility functions
"""

from pathlib import Path
from typing import Any, Dict, List, Union

import pandas as pd

from ..core.data_converter import IDataConverter
from ..core.excel_reader import IExcelReader
from ..errors.error_handlers import IErrorHandler


class ExcelUtilities:
    """Utility functions for Excel processing operations.

    This class provides commonly used utility functions and maintains
    backward compatibility with the original ExcelDataLoader API.
    """

    def __init__(
        self,
        excel_reader: IExcelReader,
        data_converter: IDataConverter,
        error_handler: IErrorHandler = None,
        enable_error_handling: bool = True,
    ):
        """Initialize utilities with required components."""
        self.excel_reader = excel_reader
        self.data_converter = data_converter
        self.error_handler = error_handler
        self.enable_error_handling = enable_error_handling

    def validate_excel_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Validate Excel file structure and accessibility.

        Args:
            file_path: Path to Excel file

        Returns:
            Validation result with file information
        """
        context = "validate_excel_file"

        try:
            workbook_info = self.excel_reader.validate_file(file_path)

            return {
                "valid": True,
                "workbook_info": workbook_info.to_dict(),
                "validation_timestamp": pd.Timestamp.now().isoformat(),
            }

        except Exception as e:
            return self._handle_utility_error(e, context)

    def get_sheet_names(self, file_path: Union[str, Path]) -> List[str]:
        """Get list of sheet names from Excel file.

        Args:
            file_path: Path to Excel file

        Returns:
            List of sheet names
        """
        context = "get_sheet_names"

        try:
            return self.excel_reader.get_sheet_names(file_path)
        except Exception as e:
            if self.enable_error_handling and self.error_handler:
                error_response = self.error_handler.create_error_response(e, context)
                return error_response.get("data", [])
            else:
                raise

    def detect_headers(self, dataframe: pd.DataFrame) -> Dict[str, Any]:
        """Detect header information in DataFrame.

        Args:
            dataframe: Pandas DataFrame to analyze

        Returns:
            Header detection result
        """
        context = "detect_headers"

        try:
            return self.data_converter.detect_header(dataframe).to_dict()
        except Exception as e:
            return self._handle_utility_error(e, context)

    def get_workbook_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Get comprehensive workbook information.

        Args:
            file_path: Path to Excel file

        Returns:
            Workbook information dictionary
        """
        context = "get_workbook_info"

        try:
            workbook_info = self.excel_reader.validate_file(file_path)
            sheet_names = self.excel_reader.get_sheet_names(file_path)

            return {
                "file_path": str(file_path),
                "workbook_info": workbook_info.to_dict(),
                "sheet_names": sheet_names,
                "sheet_count": len(sheet_names),
                "analysis_timestamp": pd.Timestamp.now().isoformat(),
            }

        except Exception as e:
            return self._handle_utility_error(e, context)

    # Backward compatibility methods

    def is_safe_path(self, file_path: Union[str, Path]) -> bool:
        """Check if file path is safe and accessible.

        Backward compatibility method for original API.

        Args:
            file_path: Path to check

        Returns:
            True if path is safe, False otherwise
        """
        try:
            self.excel_reader.validate_file(file_path)
            return True
        except Exception:
            return False

    def get_data_summary(self, dataframe: pd.DataFrame) -> Dict[str, Any]:
        """Get summary statistics for DataFrame.

        Args:
            dataframe: DataFrame to analyze

        Returns:
            Data summary dictionary
        """
        try:
            return {
                "shape": dataframe.shape,
                "columns": list(dataframe.columns),
                "dtypes": dataframe.dtypes.to_dict(),
                "memory_usage": dataframe.memory_usage(deep=True).sum(),
                "null_counts": dataframe.isnull().sum().to_dict(),
                "analysis_timestamp": pd.Timestamp.now().isoformat(),
            }
        except Exception as e:
            return self._handle_utility_error(e, "get_data_summary")

    def normalize_file_path(self, file_path: Union[str, Path]) -> Path:
        """Normalize and validate file path.

        Args:
            file_path: Path to normalize

        Returns:
            Normalized Path object
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            return path.resolve()
        except Exception as e:
            if self.enable_error_handling and self.error_handler:
                error_response = self.error_handler.create_error_response(
                    e, "normalize_file_path"
                )
                raise UtilityError(
                    f"Path normalization failed: {error_response}"
                ) from e
            else:
                raise

    def _handle_utility_error(self, error: Exception, context: str) -> Dict[str, Any]:
        """Handle utility operation errors."""
        if self.enable_error_handling and self.error_handler:
            return self.error_handler.create_error_response(error, context)
        else:
            return {
                "success": False,
                "error": {
                    "type": type(error).__name__,
                    "message": str(error),
                    "context": context,
                },
                "data": None,
            }


class UtilityError(Exception):
    """Exception raised during utility operations."""

    pass
