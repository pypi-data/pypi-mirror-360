"""Error Handlers - Simplified integration module.

Unified entry point for error handling functionality with clean delegation
to specialized modules. Dramatically reduced from 458 lines to ~100 lines.

CLAUDE.md Code Excellence Compliance:
- DRY Principle: Delegated implementation to specialized modules
- Single Responsibility: Integration and backward compatibility only
- YAGNI Principle: Essential error handling only
"""

from typing import Any, Dict, Optional

# Import all necessary components from specialized modules
from .error_handler_core import ErrorHandlerCore, IErrorHandler
from .error_types import ErrorSeverity, HandlingResult, RecoveryStrategy

# Re-export for backward compatibility
__all__ = [
    "IErrorHandler",
    "ErrorHandler",
    "ErrorHandlerCore",
    "HandlingResult",
    "ErrorSeverity",
    "RecoveryStrategy",
]


# Main error handler class using delegation pattern
class ErrorHandler(ErrorHandlerCore):
    """Production error handler with full functionality.

    Provides complete error handling capabilities through delegation
    to specialized components while maintaining backward compatibility.
    """

    def __init__(
        self,
        default_strategy: RecoveryStrategy = RecoveryStrategy.GRACEFUL_DEGRADATION,
        enable_logging: bool = True,
        logger_name: str = "sphinxcontrib.jsontable.errors",
    ):
        """Initialize error handler with configuration.

        Args:
            default_strategy: Default recovery strategy to use
            enable_logging: Whether to enable logging
            logger_name: Name for the logger instance
        """
        # Delegate to core implementation
        super().__init__(
            default_strategy=default_strategy,
            enable_logging=enable_logging,
            logger_name=logger_name,
        )

    def handle_excel_error(
        self, error: Exception, operation: str, file_path: Optional[str] = None
    ) -> HandlingResult:
        """Handle Excel-specific errors with context.

        Args:
            error: Exception that occurred
            operation: Operation being performed when error occurred
            file_path: Path to Excel file if applicable

        Returns:
            HandlingResult with error handling details
        """
        context = f"Excel {operation}"
        if file_path:
            context += f" on file: {file_path}"

        return self.handle_error(error, context)

    def handle_data_conversion_error(
        self, error: Exception, data_type: str, target_format: str
    ) -> HandlingResult:
        """Handle data conversion errors with context.

        Args:
            error: Exception that occurred
            data_type: Type of data being converted
            target_format: Target format for conversion

        Returns:
            HandlingResult with error handling details
        """
        context = f"Data conversion from {data_type} to {target_format}"
        return self.handle_error(error, context)

    def create_excel_error_response(
        self, error: Exception, file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create Excel-specific error response.

        Args:
            error: Exception that occurred
            file_path: Path to Excel file if applicable

        Returns:
            Standardized error response dictionary
        """
        context = "Excel processing"
        if file_path:
            context += f" for file: {file_path}"

        response = self.create_error_response(error, context)
        response["file_path"] = file_path
        return response


# Backward compatibility aliases
DefaultErrorHandler = ErrorHandler
ProductionErrorHandler = ErrorHandler


# Legacy class names for complete backward compatibility
class LegacyErrorHandler(ErrorHandler):
    """Legacy compatibility wrapper for existing code."""

    pass


# Backward compatibility functions
def create_error_response(error: Exception, context: str = None) -> Dict[str, Any]:
    """Backward compatibility function for creating error responses."""
    handler = ErrorHandler()
    return handler.create_error_response(error, context)


def handle_error_with_strategy(
    error: Exception, strategy: RecoveryStrategy, context: str = "Unknown"
) -> HandlingResult:
    """Backward compatibility function for handling errors with strategy."""
    handler = ErrorHandler(default_strategy=strategy)
    return handler.handle_error(error, context)
