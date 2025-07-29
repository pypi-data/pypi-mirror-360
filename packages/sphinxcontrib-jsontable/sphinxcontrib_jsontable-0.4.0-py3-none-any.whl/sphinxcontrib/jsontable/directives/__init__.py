"""Directives Package - Simplified integration entry point.

Unified entry point for directive functionality with clean delegation
to specialized modules. Dramatically reduced from 441 lines to ~100 lines.

CLAUDE.md Code Excellence Compliance:
- DRY Principle: Delegated implementation to specialized modules
- Single Responsibility: Integration and export only
- YAGNI Principle: Essential directive functionality only
"""

# Import all necessary components from specialized modules
from .backward_compatibility import (
    DEFAULT_ENCODING,
    DEFAULT_MAX_ROWS,
    EMPTY_CONTENT_ERROR,
    INVALID_JSON_DATA_ERROR,
    NO_JSON_SOURCE_ERROR,
    JsonData,
    JsonDataLoader,
    ensure_file_exists,
    format_error,
    is_safe_path,
    logger,
    safe_str,
    validate_not_empty,
)
from .directive_core import JsonTableDirective
from .table_builder import TableBuilder
from .table_converter import TableConverter
from .validators import JsonTableError, ValidationUtils

# Type definitions for backward compatibility
TableData = list[list[str]]

# Re-export for backward compatibility
__all__ = [
    # Main directive class
    "JsonTableDirective",
    # Exception classes
    "JsonTableError",
    # Data processing classes
    "JsonDataLoader",  # Backward compatibility alias
    "TableConverter",
    "TableBuilder",
    # Utility classes
    "ValidationUtils",
    # Utility functions (backward compatibility)
    "validate_not_empty",
    "safe_str",
    "ensure_file_exists",
    "format_error",
    "is_safe_path",
    # Logging
    "logger",
    # Constants
    "DEFAULT_ENCODING",
    "DEFAULT_MAX_ROWS",
    "NO_JSON_SOURCE_ERROR",
    "INVALID_JSON_DATA_ERROR",
    "EMPTY_CONTENT_ERROR",
    # Type definitions
    "JsonData",
    "TableData",
]

# Excel support detection for backward compatibility
try:
    import importlib.util

    spec = importlib.util.find_spec(
        "sphinxcontrib.jsontable.facade.excel_data_loader_facade"
    )
    EXCEL_SUPPORT = spec is not None
except ImportError:
    EXCEL_SUPPORT = False

# Add EXCEL_SUPPORT to exports
__all__.append("EXCEL_SUPPORT")
