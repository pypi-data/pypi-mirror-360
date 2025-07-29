"""
Error handling components for Excel file processing.

This module provides structured error handling functionality that was previously
embedded within the monolithic ExcelDataLoader class.
"""

from .error_handlers import ErrorHandler, HandlingResult, IErrorHandler
from .excel_errors import (
    DataConversionError,
    ExcelProcessingError,
    RangeValidationError,
    SecurityValidationError,
)

__all__ = [
    "IErrorHandler",
    "ErrorHandler",
    "HandlingResult",
    "ExcelProcessingError",
    "SecurityValidationError",
    "RangeValidationError",
    "DataConversionError",
]
