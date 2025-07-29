"""
Unit tests for Excel-specific error classes.

Tests the structured error classes that were extracted from the
monolithic ExcelDataLoader to improve error handling and testability.
"""

from sphinxcontrib.jsontable.errors.excel_errors import (
    DataConversionError,
    # Legacy error classes
    EnhancedExcelError,
    ExcelDataNotFoundError,
    ExcelFileFormatError,
    ExcelFileNotFoundError,
    ExcelProcessingError,
    FileAccessError,
    MergedCellsError,
    RangeSpecificationError,
    RangeValidationError,
    SecurityValidationError,
    SkipRowsError,
    WorksheetNotFoundError,
)


class TestExcelProcessingError:
    """Test suite for base ExcelProcessingError class."""

    def test_basic_initialization(self):
        """Test basic error initialization."""
        error = ExcelProcessingError("Test error message")

        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.error_code == "EXCEL_ERROR"
        assert error.context == {}
        assert error.original_error is None

    def test_full_initialization(self):
        """Test error initialization with all parameters."""
        original_error = ValueError("Original error")
        context = {"file": "test.xlsx", "sheet": "Sheet1"}

        error = ExcelProcessingError(
            message="Custom error",
            error_code="CUSTOM_ERROR",
            context=context,
            original_error=original_error,
        )

        assert error.message == "Custom error"
        assert error.error_code == "CUSTOM_ERROR"
        assert error.context == context
        assert error.original_error is original_error

    def test_to_dict_conversion(self):
        """Test conversion to dictionary format."""
        original_error = RuntimeError("Runtime issue")
        context = {"row": 10, "column": "B"}

        error = ExcelProcessingError(
            message="Conversion test",
            error_code="TEST_ERROR",
            context=context,
            original_error=original_error,
        )

        error_dict = error.to_dict()

        assert error_dict["error_type"] == "ExcelProcessingError"
        assert error_dict["error_code"] == "TEST_ERROR"
        assert error_dict["message"] == "Conversion test"
        assert error_dict["context"] == context
        assert error_dict["original_error"] == "Runtime issue"

    def test_to_dict_without_original_error(self):
        """Test dictionary conversion without original error."""
        error = ExcelProcessingError("Simple error")
        error_dict = error.to_dict()

        assert error_dict["original_error"] is None


class TestSecurityValidationError:
    """Test suite for SecurityValidationError."""

    def test_initialization_with_issues(self):
        """Test initialization with security issues."""
        security_issues = [
            {"type": "dangerous_link", "severity": "high", "location": "A1"},
            {"type": "macro_detected", "severity": "medium", "location": "Sheet1"},
        ]

        error = SecurityValidationError(security_issues)

        assert "2 security issues detected" in error.message
        assert error.error_code == "SECURITY_VALIDATION_ERROR"
        assert error.security_issues == security_issues

    def test_initialization_with_custom_message(self):
        """Test initialization with custom message."""
        security_issues = [{"type": "test_threat"}]
        custom_message = "Custom security error"

        error = SecurityValidationError(
            security_issues,
            message=custom_message,
            context={"file_path": "/path/to/file.xlsx"},
        )

        assert error.message == custom_message
        assert error.context["file_path"] == "/path/to/file.xlsx"

    def test_get_high_severity_issues(self):
        """Test filtering high-severity security issues."""
        security_issues = [
            {"type": "malware", "severity": "high"},
            {"type": "suspicious_link", "severity": "medium"},
            {"type": "dangerous_formula", "severity": "high"},
            {"type": "minor_issue", "severity": "low"},
        ]

        error = SecurityValidationError(security_issues)
        high_severity = error.get_high_severity_issues()

        assert len(high_severity) == 2
        assert high_severity[0]["type"] == "malware"
        assert high_severity[1]["type"] == "dangerous_formula"

    def test_to_dict_with_security_details(self):
        """Test dictionary conversion with security issue details."""
        security_issues = [
            {"type": "critical_threat", "severity": "high"},
            {"type": "warning", "severity": "medium"},
        ]

        error = SecurityValidationError(security_issues)
        error_dict = error.to_dict()

        assert error_dict["error_type"] == "SecurityValidationError"
        assert error_dict["security_issues"] == security_issues
        assert error_dict["high_severity_count"] == 1


class TestRangeValidationError:
    """Test suite for RangeValidationError."""

    def test_initialization_with_range_spec(self):
        """Test initialization with range specification."""
        range_spec = "A1:Z999999"
        error = RangeValidationError(range_spec)

        assert f"Invalid range specification: {range_spec}" in error.message
        assert error.error_code == "RANGE_VALIDATION_ERROR"
        assert error.range_spec == range_spec

    def test_initialization_with_custom_message(self):
        """Test initialization with custom message and original error."""
        range_spec = "Sheet1!A1:B2"
        original_error = ValueError("Invalid cell reference")
        custom_message = "Custom range error"

        error = RangeValidationError(
            range_spec,
            message=custom_message,
            context={"sheet": "Sheet1"},
            original_error=original_error,
        )

        assert error.message == custom_message
        assert error.range_spec == range_spec
        assert error.original_error is original_error

    def test_to_dict_with_range_details(self):
        """Test dictionary conversion with range details."""
        range_spec = "A1:B10"
        error = RangeValidationError(range_spec)
        error_dict = error.to_dict()

        assert error_dict["error_type"] == "RangeValidationError"
        assert error_dict["range_specification"] == range_spec


class TestDataConversionError:
    """Test suite for DataConversionError."""

    def test_initialization_with_stage(self):
        """Test initialization with conversion stage."""
        stage = "json_serialization"
        error = DataConversionError(stage)

        assert f"Data conversion failed at stage: {stage}" in error.message
        assert error.error_code == "DATA_CONVERSION_ERROR"
        assert error.conversion_stage == stage

    def test_initialization_with_custom_message(self):
        """Test initialization with custom message and context."""
        stage = "header_parsing"
        custom_message = "Header parsing failed"
        context = {"row": 1, "columns": ["A", "B", "C"]}

        error = DataConversionError(stage, message=custom_message, context=context)

        assert error.message == custom_message
        assert error.conversion_stage == stage
        assert error.context == context

    def test_to_dict_with_conversion_details(self):
        """Test dictionary conversion with conversion details."""
        stage = "data_transformation"
        error = DataConversionError(stage)
        error_dict = error.to_dict()

        assert error_dict["error_type"] == "DataConversionError"
        assert error_dict["conversion_stage"] == stage


class TestFileAccessError:
    """Test suite for FileAccessError."""

    def test_initialization_with_file_path(self):
        """Test initialization with file path."""
        file_path = "/path/to/missing.xlsx"
        error = FileAccessError(file_path)

        assert f"Cannot access Excel file: {file_path}" in error.message
        assert error.error_code == "FILE_ACCESS_ERROR"
        assert error.file_path == file_path

    def test_initialization_with_original_error(self):
        """Test initialization with original error."""
        file_path = "/restricted/file.xlsx"
        original_error = PermissionError("Access denied")

        error = FileAccessError(file_path, original_error=original_error)

        assert error.file_path == file_path
        assert error.original_error is original_error

    def test_to_dict_with_file_details(self):
        """Test dictionary conversion with file details."""
        file_path = "/test/path.xlsx"
        error = FileAccessError(file_path)
        error_dict = error.to_dict()

        assert error_dict["error_type"] == "FileAccessError"
        assert error_dict["file_path"] == file_path


class TestWorksheetNotFoundError:
    """Test suite for WorksheetNotFoundError."""

    def test_initialization_with_sheet_info(self):
        """Test initialization with sheet information."""
        sheet_name = "NonExistentSheet"
        available_sheets = ["Sheet1", "Sheet2", "Data"]

        error = WorksheetNotFoundError(sheet_name, available_sheets)

        assert f"Worksheet '{sheet_name}' not found" in error.message
        assert "Available sheets: Sheet1, Sheet2, Data" in error.message
        assert error.error_code == "WORKSHEET_NOT_FOUND_ERROR"
        assert error.sheet_name == sheet_name
        assert error.available_sheets == available_sheets

    def test_initialization_with_custom_message(self):
        """Test initialization with custom message."""
        sheet_name = "TestSheet"
        available_sheets = ["Main"]
        custom_message = "Custom worksheet error"

        error = WorksheetNotFoundError(
            sheet_name,
            available_sheets,
            message=custom_message,
            context={"workbook": "test.xlsx"},
        )

        assert error.message == custom_message
        assert error.context["workbook"] == "test.xlsx"

    def test_to_dict_with_worksheet_details(self):
        """Test dictionary conversion with worksheet details."""
        sheet_name = "MissingSheet"
        available_sheets = ["Sheet1", "Sheet2"]

        error = WorksheetNotFoundError(sheet_name, available_sheets)
        error_dict = error.to_dict()

        assert error_dict["error_type"] == "WorksheetNotFoundError"
        assert error_dict["requested_sheet"] == sheet_name
        assert error_dict["available_sheets"] == available_sheets


class TestLegacyErrorClasses:
    """Test suite for legacy error classes maintained for backward compatibility."""

    def test_enhanced_excel_error(self):
        """Test EnhancedExcelError legacy class."""
        error = EnhancedExcelError("Legacy error")

        assert isinstance(error, ExcelProcessingError)
        assert str(error) == "Legacy error"
        assert error.error_code == "EXCEL_ERROR"

    def test_excel_file_not_found_error(self):
        """Test ExcelFileNotFoundError legacy class."""
        file_path = "/missing/file.xlsx"
        error = ExcelFileNotFoundError(file_path)

        assert isinstance(error, FileAccessError)
        assert error.file_path == file_path

    def test_excel_file_format_error(self):
        """Test ExcelFileFormatError legacy class."""
        error = ExcelFileFormatError("Invalid format", context={"format": "csv"})

        assert isinstance(error, ExcelProcessingError)
        assert error.error_code == "EXCEL_FILE_FORMAT_ERROR"
        assert error.context["format"] == "csv"

    def test_excel_data_not_found_error(self):
        """Test ExcelDataNotFoundError legacy class."""
        error = ExcelDataNotFoundError("No data found", context={"range": "A1:Z10"})

        assert isinstance(error, ExcelProcessingError)
        assert error.error_code == "EXCEL_DATA_NOT_FOUND_ERROR"
        assert error.context["range"] == "A1:Z10"

    def test_range_specification_error(self):
        """Test RangeSpecificationError legacy class."""
        range_spec = "InvalidRange"
        error = RangeSpecificationError(range_spec)

        assert isinstance(error, RangeValidationError)
        assert error.range_spec == range_spec

    def test_skip_rows_error(self):
        """Test SkipRowsError legacy class."""
        error = SkipRowsError("Skip rows error", context={"skip_rows": 5})

        assert isinstance(error, ExcelProcessingError)
        assert error.error_code == "SKIP_ROWS_ERROR"
        assert error.context["skip_rows"] == 5

    def test_merged_cells_error(self):
        """Test MergedCellsError legacy class."""
        error = MergedCellsError("Merged cells detected", context={"range": "A1:B2"})

        assert isinstance(error, ExcelProcessingError)
        assert error.error_code == "MERGED_CELLS_ERROR"
        assert error.context["range"] == "A1:B2"


class TestErrorInheritance:
    """Test error class inheritance and polymorphism."""

    def test_all_errors_inherit_from_base(self):
        """Test that all error classes inherit from ExcelProcessingError."""
        error_classes = [
            SecurityValidationError,
            RangeValidationError,
            DataConversionError,
            FileAccessError,
            WorksheetNotFoundError,
            EnhancedExcelError,
            ExcelFileNotFoundError,
            ExcelFileFormatError,
            ExcelDataNotFoundError,
            RangeSpecificationError,
            SkipRowsError,
            MergedCellsError,
        ]

        for error_class in error_classes:
            if error_class == ExcelFileNotFoundError:
                # This one inherits from FileAccessError
                assert issubclass(error_class, FileAccessError)
                assert issubclass(error_class, ExcelProcessingError)
            elif error_class == RangeSpecificationError:
                # This one inherits from RangeValidationError
                assert issubclass(error_class, RangeValidationError)
                assert issubclass(error_class, ExcelProcessingError)
            else:
                assert issubclass(error_class, ExcelProcessingError)

    def test_polymorphic_error_handling(self):
        """Test polymorphic handling of different error types."""
        errors = [
            SecurityValidationError([{"type": "test"}]),
            RangeValidationError("A1:B2"),
            DataConversionError("test_stage"),
            FileAccessError("/test/file.xlsx"),
            WorksheetNotFoundError("Sheet", ["Other"]),
            EnhancedExcelError("Legacy error"),
            ExcelFileFormatError("Format error"),
            SkipRowsError("Skip error"),
            MergedCellsError("Merge error"),
        ]

        for error in errors:
            # All should be catchable as ExcelProcessingError
            assert isinstance(error, ExcelProcessingError)
            # All should have to_dict method
            error_dict = error.to_dict()
            assert "error_type" in error_dict
            assert "error_code" in error_dict
            assert "message" in error_dict

    def test_exception_catching(self):
        """Test that errors can be caught by their base classes."""
        # Test SecurityValidationError can be caught as ExcelProcessingError
        try:
            raise SecurityValidationError([{"type": "test"}])
        except ExcelProcessingError as e:
            assert isinstance(e, SecurityValidationError)
            assert e.error_code == "SECURITY_VALIDATION_ERROR"

        # Test RangeValidationError can be caught as ExcelProcessingError
        try:
            raise RangeValidationError("A1:B2")
        except ExcelProcessingError as e:
            assert isinstance(e, RangeValidationError)
            assert e.error_code == "RANGE_VALIDATION_ERROR"


class TestComplexErrorScenarios:
    """Test complex error scenarios with context and chaining."""

    def test_error_chaining_with_original_error(self):
        """Test error chaining with original exception."""
        original = ValueError("Invalid input data")

        try:
            raise original
        except ValueError as e:
            conversion_error = DataConversionError(
                "json_parsing",
                message="Failed to parse Excel data as JSON",
                context={"input_type": "xlsx", "target_format": "json"},
                original_error=e,
            )

        error_dict = conversion_error.to_dict()
        assert error_dict["original_error"] == "Invalid input data"
        assert conversion_error.original_error is original
        assert conversion_error.context["input_type"] == "xlsx"

    def test_complex_security_error_context(self):
        """Test complex security error with detailed context."""
        security_issues = [
            {
                "type": "external_link",
                "severity": "high",
                "location": "Sheet1!A1",
                "target": "http://malicious-site.com",
                "description": "Dangerous external link detected",
            },
            {
                "type": "macro_code",
                "severity": "critical",
                "location": "VBA Module1",
                "description": "Potentially malicious macro code",
            },
        ]

        context = {
            "file_path": "/uploads/suspicious_file.xlsm",
            "user_id": "user123",
            "scan_timestamp": "2025-06-17T10:30:00Z",
            "security_level": "strict",
        }

        error = SecurityValidationError(
            security_issues,
            message="Multiple critical security threats detected",
            context=context,
        )

        assert len(error.security_issues) == 2
        assert len(error.get_high_severity_issues()) == 1  # Only "high" severity
        assert error.context["security_level"] == "strict"

        error_dict = error.to_dict()
        assert error_dict["high_severity_count"] == 1
        assert len(error_dict["security_issues"]) == 2

    def test_error_context_serialization(self):
        """Test that error contexts are properly serializable."""
        from pathlib import Path

        # Test with complex context data
        context = {
            "file_path": str(Path("/test/file.xlsx")),
            "sheet_names": ["Sheet1", "Sheet2", "Data"],
            "processing_options": {
                "skip_rows": 2,
                "header_row": True,
                "range_spec": "A1:Z100",
            },
            "metadata": {
                "file_size": 1024000,
                "last_modified": "2025-06-17",
                "contains_formulas": True,
            },
        }

        error = DataConversionError("complex_processing", context=context)

        error_dict = error.to_dict()

        # Verify all context data is preserved
        assert error_dict["context"]["file_path"] == str(Path("/test/file.xlsx"))
        assert error_dict["context"]["sheet_names"] == ["Sheet1", "Sheet2", "Data"]
        assert error_dict["context"]["processing_options"]["skip_rows"] == 2
        assert error_dict["context"]["metadata"]["file_size"] == 1024000
