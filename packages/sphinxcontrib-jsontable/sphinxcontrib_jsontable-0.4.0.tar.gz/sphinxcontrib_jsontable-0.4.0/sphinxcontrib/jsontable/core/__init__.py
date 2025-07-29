"""
Core processing components for Excel file handling.

This module provides core functionality that was previously
embedded within the monolithic ExcelDataLoader class.
"""

from .data_converter import (
    ConversionResult,
    DataConverter,
    HeaderDetectionResult,
    IDataConverter,
)
from .excel_reader import ExcelReader, IExcelReader, ReadResult, WorkbookInfo
from .range_parser import IRangeParser, RangeInfo, RangeParser

__all__ = [
    "IRangeParser",
    "RangeParser",
    "RangeInfo",
    "IDataConverter",
    "DataConverter",
    "ConversionResult",
    "HeaderDetectionResult",
    "IExcelReader",
    "ExcelReader",
    "ReadResult",
    "WorkbookInfo",
]
