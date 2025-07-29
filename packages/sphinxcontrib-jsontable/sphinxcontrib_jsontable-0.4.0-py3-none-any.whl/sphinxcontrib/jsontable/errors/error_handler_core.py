"""Error Handler Core - Core error handling functionality.

Essential error handling operations with recovery strategies and logging.

CLAUDE.md Code Excellence Compliance:
- Single Responsibility: Core error handling operations only
- DRY Principle: Centralized error handling logic
- SOLID Principles: Interface implementation with strategy pattern
"""

import logging
import traceback
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from .error_types import ErrorSeverity, HandlingResult, RecoveryStrategy
from .excel_errors import (
    DataConversionError,
    ExcelProcessingError,
    FileAccessError,
    RangeValidationError,
    SecurityValidationError,
)


class IErrorHandler(ABC):
    """Abstract interface for error handling."""

    @abstractmethod
    def handle_error(
        self, error: Exception, context: str, severity: Optional[ErrorSeverity] = None
    ) -> HandlingResult:
        """Handle an error with appropriate strategy."""
        pass

    @abstractmethod
    def create_error_response(
        self, error: Exception, context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create standardized error response."""
        pass


class ErrorHandlerCore(IErrorHandler):
    """Core error handler for Excel processing.

    Provides essential error handling functionality with recovery strategies
    and comprehensive logging integration.
    """

    def __init__(
        self,
        default_strategy: RecoveryStrategy = RecoveryStrategy.GRACEFUL_DEGRADATION,
        enable_logging: bool = True,
        logger_name: str = "sphinxcontrib.jsontable.errors",
    ):
        """Initialize error handler with configuration."""
        self.default_strategy = default_strategy
        self.enable_logging = enable_logging
        self.logger = logging.getLogger(logger_name) if enable_logging else None

        # Error severity mapping
        self.severity_mapping = {
            SecurityValidationError: ErrorSeverity.CRITICAL,
            RangeValidationError: ErrorSeverity.HIGH,
            DataConversionError: ErrorSeverity.MEDIUM,
            FileAccessError: ErrorSeverity.HIGH,
            ExcelProcessingError: ErrorSeverity.MEDIUM,
            ValueError: ErrorSeverity.LOW,
            TypeError: ErrorSeverity.MEDIUM,
            Exception: ErrorSeverity.LOW,
        }

        # Recovery strategy mapping
        self.strategy_mapping = {
            ErrorSeverity.CRITICAL: RecoveryStrategy.FAIL_FAST,
            ErrorSeverity.HIGH: RecoveryStrategy.GRACEFUL_DEGRADATION,
            ErrorSeverity.MEDIUM: RecoveryStrategy.GRACEFUL_DEGRADATION,
            ErrorSeverity.LOW: RecoveryStrategy.IGNORE,
        }

    def handle_error(
        self, error: Exception, context: str, severity: Optional[ErrorSeverity] = None
    ) -> HandlingResult:
        """Handle an error with appropriate strategy."""
        try:
            # Determine severity
            if severity is None:
                severity = self._determine_severity(error)

            # Get recovery strategy
            strategy = self.strategy_mapping.get(severity, self.default_strategy)

            # Log error
            if self.enable_logging and self.logger:
                self._log_error(error, context, severity, strategy)

            # Apply recovery strategy
            return self._apply_recovery_strategy(error, context, severity, strategy)

        except Exception as handling_error:
            # Fallback error handling
            return self._create_fallback_result(error, context, handling_error)

    def create_error_response(
        self, error: Exception, context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create standardized error response."""
        error_type = type(error).__name__
        error_message = str(error)

        response = {
            "error": True,
            "error_type": error_type,
            "error_message": error_message,
            "context": context or "Unknown context",
            "timestamp": self._get_timestamp(),
        }

        # Add traceback for debugging if logging enabled
        if self.enable_logging:
            response["traceback"] = traceback.format_exc()

        return response

    def _determine_severity(self, error: Exception) -> ErrorSeverity:
        """Determine error severity based on error type."""
        error_type = type(error)

        # Check exact match first
        if error_type in self.severity_mapping:
            return self.severity_mapping[error_type]

        # Check inheritance hierarchy
        for mapped_type, severity in self.severity_mapping.items():
            if isinstance(error, mapped_type):
                return severity

        # Default to LOW severity
        return ErrorSeverity.LOW

    def _apply_recovery_strategy(
        self,
        error: Exception,
        context: str,
        severity: ErrorSeverity,
        strategy: RecoveryStrategy,
    ) -> HandlingResult:
        """Apply recovery strategy based on error severity."""
        if strategy == RecoveryStrategy.FAIL_FAST:
            return HandlingResult(
                success=False,
                error_handled=True,
                recovery_applied=False,
                response_data=self.create_error_response(error, context),
                warning_messages=[],
                error_messages=[f"Critical error in {context}: {str(error)}"],
                metadata={"severity": severity.value, "strategy": strategy.value},
            )

        elif strategy == RecoveryStrategy.GRACEFUL_DEGRADATION:
            return HandlingResult(
                success=False,
                error_handled=True,
                recovery_applied=True,
                response_data={"error": "Processing failed with graceful degradation"},
                warning_messages=[f"Degraded performance due to error in {context}"],
                error_messages=[str(error)],
                metadata={"severity": severity.value, "strategy": strategy.value},
            )

        elif strategy == RecoveryStrategy.IGNORE:
            return HandlingResult(
                success=True,
                error_handled=True,
                recovery_applied=True,
                response_data=None,
                warning_messages=[f"Ignored error in {context}: {str(error)}"],
                error_messages=[],
                metadata={"severity": severity.value, "strategy": strategy.value},
            )

        else:
            # Default to graceful degradation
            return self._apply_recovery_strategy(
                error, context, severity, RecoveryStrategy.GRACEFUL_DEGRADATION
            )

    def _log_error(
        self,
        error: Exception,
        context: str,
        severity: ErrorSeverity,
        strategy: RecoveryStrategy,
    ) -> None:
        """Log error with appropriate level based on severity."""
        if not self.logger:
            return

        log_message = f"Error in {context}: {str(error)} (severity: {severity.value}, strategy: {strategy.value})"

        if severity == ErrorSeverity.CRITICAL:
            self.logger.error(log_message, exc_info=True)
        elif severity == ErrorSeverity.HIGH:
            self.logger.error(log_message)
        elif severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

    def _create_fallback_result(
        self, original_error: Exception, context: str, handling_error: Exception
    ) -> HandlingResult:
        """Create fallback result when error handling itself fails."""
        return HandlingResult(
            success=False,
            error_handled=False,
            recovery_applied=False,
            response_data=None,
            warning_messages=[],
            error_messages=[
                f"Original error: {str(original_error)}",
                f"Error handling failed: {str(handling_error)}",
            ],
            metadata={"context": context, "fallback": True},
        )

    def _get_timestamp(self) -> str:
        """Get current timestamp for error response."""
        import datetime

        return datetime.datetime.now().isoformat()
