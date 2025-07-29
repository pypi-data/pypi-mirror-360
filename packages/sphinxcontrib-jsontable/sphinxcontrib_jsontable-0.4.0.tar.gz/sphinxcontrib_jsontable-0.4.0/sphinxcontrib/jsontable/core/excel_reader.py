"""Excel Reader - Simplified integration module.

Unified entry point for Excel reading functionality with clean imports
and backward compatibility. Dramatically reduced from 740 lines to ~50 lines.

CLAUDE.md Code Excellence Compliance:
- DRY Principle: Delegated implementation to specialized modules
- Single Responsibility: Import coordination and compatibility only
- YAGNI Principle: Essential exports only
"""

# Import all necessary components from specialized modules
# Import openpyxl components for external access
from openpyxl import load_workbook

from .excel_reader_core import ExcelReader
from .excel_reader_interface import IExcelReader
from .excel_reader_mock import MockExcelReader
from .excel_workbook_info import ReadResult, WorkbookInfo

# Re-export for backward compatibility
__all__ = [
    "IExcelReader",
    "ExcelReader",
    "MockExcelReader",
    "WorkbookInfo",
    "ReadResult",
    "load_workbook",  # Critical: 追加でインポートエラー解消
]

# Backward compatibility aliases
DefaultExcelReader = ExcelReader
TestExcelReader = MockExcelReader
