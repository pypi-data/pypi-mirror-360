"""
Excel-specific error classes for structured error handling.

This module extracts and improves upon the error classes that were previously
scattered throughout the monolithic ExcelDataLoader class.
"""

from typing import Any, Dict, List, Optional


class ExcelProcessingError(Exception):
    """Base class for all Excel processing errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "EXCEL_ERROR",
        context: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.original_error = original_error

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for structured logging."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
            "original_error": str(self.original_error) if self.original_error else None,
        }


class SecurityValidationError(ExcelProcessingError):
    """Error raised during security validation of Excel files."""

    def __init__(
        self,
        security_issues: List[Dict[str, str]],
        message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            issue_count = len(security_issues)
            message = (
                f"Security validation failed: {issue_count} security issues detected"
            )

        super().__init__(
            message=message, error_code="SECURITY_VALIDATION_ERROR", context=context
        )
        self.security_issues = security_issues

    def get_high_severity_issues(self) -> List[Dict[str, str]]:
        """Get only high-severity security issues."""
        return [
            issue for issue in self.security_issues if issue.get("severity") == "high"
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary with security issue details."""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "security_issues": self.security_issues,
                "high_severity_count": len(self.get_high_severity_issues()),
            }
        )
        return base_dict


class RangeValidationError(ExcelProcessingError):
    """Error raised during Excel range specification validation."""

    def __init__(
        self,
        range_spec: str,
        message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        if message is None:
            message = f"Invalid range specification: {range_spec}"

        super().__init__(
            message=message,
            error_code="RANGE_VALIDATION_ERROR",
            context=context,
            original_error=original_error,
        )
        self.range_spec = range_spec

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary with range details."""
        base_dict = super().to_dict()
        base_dict.update({"range_specification": self.range_spec})
        return base_dict


class DataConversionError(ExcelProcessingError):
    """Error raised during data conversion from Excel to JSON."""

    def __init__(
        self,
        conversion_stage: str,
        message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        if message is None:
            message = f"Data conversion failed at stage: {conversion_stage}"

        super().__init__(
            message=message,
            error_code="DATA_CONVERSION_ERROR",
            context=context,
            original_error=original_error,
        )
        self.conversion_stage = conversion_stage

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary with conversion details."""
        base_dict = super().to_dict()
        base_dict.update({"conversion_stage": self.conversion_stage})
        return base_dict


class FileAccessError(ExcelProcessingError):
    """Error raised when Excel file cannot be accessed or read."""

    def __init__(
        self,
        file_path: str,
        message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        if message is None:
            message = f"Cannot access Excel file: {file_path}"

        super().__init__(
            message=message,
            error_code="FILE_ACCESS_ERROR",
            context=context,
            original_error=original_error,
        )
        self.file_path = file_path

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary with file details."""
        base_dict = super().to_dict()
        base_dict.update({"file_path": self.file_path})
        return base_dict


class WorksheetNotFoundError(ExcelProcessingError):
    """Error raised when specified worksheet is not found."""

    def __init__(
        self,
        sheet_name: str,
        available_sheets: List[str],
        message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"Worksheet '{sheet_name}' not found. Available sheets: {', '.join(available_sheets)}"

        super().__init__(
            message=message, error_code="WORKSHEET_NOT_FOUND_ERROR", context=context
        )
        self.sheet_name = sheet_name
        self.available_sheets = available_sheets

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary with worksheet details."""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "requested_sheet": self.sheet_name,
                "available_sheets": self.available_sheets,
            }
        )
        return base_dict


# Legacy error classes for backward compatibility
class EnhancedExcelError(ExcelProcessingError):
    """Legacy base exception class - maintained for backward compatibility."""

    pass


class ExcelFileNotFoundError(FileAccessError):
    """Legacy exception class - maintained for backward compatibility."""

    pass


class ExcelFileFormatError(ExcelProcessingError):
    """Legacy exception class - maintained for backward compatibility."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message, error_code="EXCEL_FILE_FORMAT_ERROR", context=context
        )


class ExcelDataNotFoundError(ExcelProcessingError):
    """Legacy exception class - maintained for backward compatibility."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message, error_code="EXCEL_DATA_NOT_FOUND_ERROR", context=context
        )


class RangeSpecificationError(RangeValidationError):
    """Legacy exception class - maintained for backward compatibility."""

    pass


class SkipRowsError(ExcelProcessingError):
    """Legacy exception class - maintained for backward compatibility."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, error_code="SKIP_ROWS_ERROR", context=context)


class MergedCellsError(ExcelProcessingError):
    """Legacy exception class - maintained for backward compatibility."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message, error_code="MERGED_CELLS_ERROR", context=context
        )
