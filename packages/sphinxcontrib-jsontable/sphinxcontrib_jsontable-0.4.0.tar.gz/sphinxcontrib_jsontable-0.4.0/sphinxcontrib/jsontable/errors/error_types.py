"""Error Types - Error handling data structures and enums.

Clean separation of error handling types and data structures.

CLAUDE.md Code Excellence Compliance:
- Single Responsibility: Type definitions and data structures only
- DRY Principle: Centralized error type definitions
- YAGNI Principle: Essential error handling types only
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class ErrorSeverity(Enum):
    """Error severity levels for handling strategy determination."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryStrategy(Enum):
    """Error recovery strategies."""

    FAIL_FAST = "fail_fast"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    RETRY = "retry"
    IGNORE = "ignore"


@dataclass
class HandlingResult:
    """Result of error handling operation."""

    success: bool
    error_handled: bool
    recovery_applied: bool
    response_data: Optional[Dict[str, Any]]
    warning_messages: List[str]
    error_messages: List[str]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "error_handled": self.error_handled,
            "recovery_applied": self.recovery_applied,
            "response_data": self.response_data,
            "warning_messages": self.warning_messages,
            "error_messages": self.error_messages,
            "metadata": self.metadata,
        }

    @property
    def has_warnings(self) -> bool:
        """Check if result has warning messages."""
        return len(self.warning_messages) > 0

    @property
    def has_errors(self) -> bool:
        """Check if result has error messages."""
        return len(self.error_messages) > 0
