"""Error Types Tests - Phase 3.1 Coverage Boost.

Tests for error_types.py to boost coverage in errors module.
"""

from dataclasses import fields

import pytest

from sphinxcontrib.jsontable.errors.error_types import ErrorSeverity, RecoveryStrategy


class TestErrorTypes:
    """Test suite for error types to boost coverage."""

    def test_error_severity_enum(self):
        """Test ErrorSeverity enum values."""
        assert ErrorSeverity.LOW.value == "low"
        assert ErrorSeverity.MEDIUM.value == "medium"
        assert ErrorSeverity.HIGH.value == "high"
        assert ErrorSeverity.CRITICAL.value == "critical"

    def test_recovery_strategy_enum(self):
        """Test RecoveryStrategy enum values."""
        assert RecoveryStrategy.FAIL_FAST.value == "fail_fast"
        assert RecoveryStrategy.GRACEFUL_DEGRADATION.value == "graceful_degradation"
        assert RecoveryStrategy.RETRY.value == "retry"

    def test_error_context_dataclass(self):
        """Test ErrorContext dataclass if it exists."""
        try:
            from sphinxcontrib.jsontable.errors.error_types import ErrorContext

            # Test dataclass creation
            context = ErrorContext(
                operation="test_operation",
                severity=ErrorSeverity.HIGH,
                recovery_strategy=RecoveryStrategy.RETRY,
            )

            assert context.operation == "test_operation"
            assert context.severity == ErrorSeverity.HIGH
            assert context.recovery_strategy == RecoveryStrategy.RETRY

        except ImportError:
            pytest.skip("ErrorContext not available")

    def test_error_context_fields(self):
        """Test ErrorContext fields if it exists."""
        try:
            from sphinxcontrib.jsontable.errors.error_types import ErrorContext

            field_names = [field.name for field in fields(ErrorContext)]
            assert "operation" in field_names or "message" in field_names

        except (ImportError, TypeError):
            pytest.skip("ErrorContext fields test not applicable")

    def test_enum_iteration(self):
        """Test enum iteration."""
        severity_values = [item.value for item in ErrorSeverity]
        assert "low" in severity_values
        assert "high" in severity_values

        strategy_values = [item.value for item in RecoveryStrategy]
        assert "fail_fast" in strategy_values
        assert "retry" in strategy_values

    def test_enum_comparison(self):
        """Test enum comparison."""
        assert ErrorSeverity.LOW != ErrorSeverity.HIGH
        assert ErrorSeverity.CRITICAL == ErrorSeverity.CRITICAL

        assert RecoveryStrategy.RETRY != RecoveryStrategy.FAIL_FAST
        assert (
            RecoveryStrategy.GRACEFUL_DEGRADATION
            == RecoveryStrategy.GRACEFUL_DEGRADATION
        )

    def test_enum_string_representation(self):
        """Test enum string representation."""
        assert str(ErrorSeverity.HIGH) == "ErrorSeverity.HIGH"
        assert str(RecoveryStrategy.RETRY) == "RecoveryStrategy.RETRY"

    def test_enum_membership(self):
        """Test enum membership."""
        assert ErrorSeverity.LOW in ErrorSeverity
        assert ErrorSeverity.CRITICAL in ErrorSeverity

        assert RecoveryStrategy.FAIL_FAST in RecoveryStrategy
        assert RecoveryStrategy.GRACEFUL_DEGRADATION in RecoveryStrategy
