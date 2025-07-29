"""Data Converter - Simplified integration module.

Unified entry point for data conversion functionality with clean delegation
to specialized modules. Dramatically reduced from 510 lines to ~100 lines.

CLAUDE.md Code Excellence Compliance:
- DRY Principle: Delegated implementation to specialized modules
- Single Responsibility: Integration and backward compatibility only
- YAGNI Principle: Essential functionality only
"""

from typing import List

# Import all necessary components from specialized modules
from .data_conversion_types import (
    ConversionResult,
    HeaderDetectionResult,
    IDataConverter,
)
from .data_converter_core import DataConverterCore
from .header_detection import HeaderDetector, HeaderNormalizer

# Re-export for backward compatibility
__all__ = [
    "IDataConverter",
    "DataConverter",
    "ConversionResult",
    "HeaderDetectionResult",
    "HeaderDetector",
    "HeaderNormalizer",
]


# Main converter class using delegation pattern
class DataConverter(DataConverterCore):
    """Production data converter with full functionality.

    Provides complete data conversion capabilities through delegation
    to specialized components while maintaining backward compatibility.
    """

    def __init__(
        self,
        empty_string_replacement: str = "",
        preserve_numeric_types: bool = True,
        header_keywords: List[str] = None,
    ):
        """Initialize data converter with configuration.

        Args:
            empty_string_replacement: String to replace empty/NaN values
            preserve_numeric_types: Whether to preserve numeric type info
            header_keywords: Keywords that indicate header presence
        """
        # Delegate to core implementation
        super().__init__(
            empty_string_replacement=empty_string_replacement,
            preserve_numeric_types=preserve_numeric_types,
            header_keywords=header_keywords,
        )


# Backward compatibility aliases
DefaultDataConverter = DataConverter
ProductionDataConverter = DataConverter


# Legacy class names for complete backward compatibility
class LegacyDataConverter(DataConverter):
    """Legacy compatibility wrapper for existing code."""

    pass
