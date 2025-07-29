"""
Unit tests for SecurityScanner - extracted from monolithic ExcelDataLoader.

Tests the security validation logic that was previously in lines 365-381 and 413-434
of excel_data_loader.py. This provides improved testability and coverage.
"""

import warnings
from pathlib import Path
from unittest.mock import Mock

from sphinxcontrib.jsontable.security.security_scanner import (
    ISecurityValidator,
    MockSecurityValidator,
    SecurityScanner,
    ValidationResult,
)


class TestSecurityScanner:
    """Test suite for SecurityScanner class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.scanner = SecurityScanner()
        self.strict_scanner = SecurityScanner(
            macro_security=SecurityScanner.MACRO_SECURITY_STRICT
        )
        self.disabled_scanner = SecurityScanner(
            macro_security=SecurityScanner.MACRO_SECURITY_DISABLED
        )

    def test_initialization(self):
        """Test SecurityScanner initialization."""
        # Default initialization
        scanner = SecurityScanner()
        assert scanner.macro_security == SecurityScanner.MACRO_SECURITY_WARN
        assert len(scanner.dangerous_protocols) > 0
        assert "http://" in scanner.dangerous_protocols

        # Custom initialization
        strict_scanner = SecurityScanner(
            macro_security=SecurityScanner.MACRO_SECURITY_STRICT
        )
        assert strict_scanner.macro_security == SecurityScanner.MACRO_SECURITY_STRICT

    def test_validate_file_not_found(self):
        """Test file validation when file doesn't exist."""
        non_existent_file = Path("/non/existent/file.xlsx")

        result = self.scanner.validate_file(non_existent_file)

        assert not result.is_valid
        assert len(result.errors) == 1
        assert "File not found" in result.errors[0]

    def test_validate_file_macro_enabled(self, tmp_path):
        """Test validation of macro-enabled Excel file."""
        # Create a mock .xlsm file
        mock_file = tmp_path / "test.xlsm"
        mock_file.write_text("mock excel content")

        result = self.scanner.validate_file(mock_file)

        assert result.is_valid  # File exists, so valid
        assert len(result.security_issues) == 1
        assert result.security_issues[0]["type"] == "macro_file"
        assert result.security_issues[0]["severity"] == "medium"

    def test_validate_file_unexpected_extension(self, tmp_path):
        """Test validation with unexpected file extension."""
        mock_file = tmp_path / "test.txt"
        mock_file.write_text("mock content")

        result = self.scanner.validate_file(mock_file)

        assert result.is_valid
        assert len(result.warnings) == 1
        assert "Unexpected file extension" in result.warnings[0]

    def test_scan_external_links_dangerous(self):
        """Test scanning for dangerous external links (lines 365-381 coverage)."""
        # Create mock workbook with dangerous hyperlink
        workbook = Mock()
        workbook.sheetnames = ["Sheet1"]

        worksheet = Mock()
        workbook.__getitem__ = Mock(return_value=worksheet)

        # Mock cell with dangerous hyperlink
        cell = Mock()
        cell.hyperlink = Mock()
        cell.hyperlink.target = "http://malicious-site.com/evil.exe"
        cell.coordinate = "A1"

        worksheet.iter_rows.return_value = [[cell]]

        result = self.scanner.scan_security_threats(workbook)

        # Should detect dangerous link
        assert len(result.security_issues) >= 1
        dangerous_link = next(
            (issue for issue in result.security_issues if issue["type"] == "hyperlink"),
            None,
        )
        assert dangerous_link is not None
        assert dangerous_link["severity"] == "high"
        assert "Sheet1!A1" in dangerous_link["location"]

    def test_scan_suspicious_links(self):
        """Test detection of suspicious link patterns."""
        workbook = Mock()
        workbook.sheetnames = ["Sheet1"]

        worksheet = Mock()
        workbook.__getitem__ = Mock(return_value=worksheet)

        # Mock cell with suspicious link
        cell = Mock()
        cell.hyperlink = Mock()
        cell.hyperlink.target = "file:///C:/Windows/System32/evil.exe"
        cell.coordinate = "B2"

        worksheet.iter_rows.return_value = [[cell]]

        result = self.scanner.scan_security_threats(workbook)

        # Should detect both dangerous protocol and suspicious pattern
        suspicious_issues = [
            issue
            for issue in result.security_issues
            if issue.get("type") in ["hyperlink", "suspicious_link"]
        ]
        assert len(suspicious_issues) >= 1

    def test_scan_dangerous_formulas(self):
        """Test detection of dangerous formulas."""
        workbook = Mock()
        workbook.sheetnames = ["Sheet1"]

        worksheet = Mock()
        workbook.__getitem__ = Mock(return_value=worksheet)

        # Mock cell with dangerous formula
        cell = Mock()
        cell.data_type = "f"  # Formula cell
        cell.value = (
            '=CALL("kernel32","CreateProcessA","JJJJJJJJJJJ",0,0,0,0,0,0,0,0,0,0)'
        )
        cell.coordinate = "C3"

        worksheet.iter_rows.return_value = [[cell]]

        result = self.scanner.scan_security_threats(workbook)

        # Should detect dangerous formula
        dangerous_formula = next(
            (
                issue
                for issue in result.security_issues
                if issue["type"] == "dangerous_formula"
            ),
            None,
        )
        assert dangerous_formula is not None
        assert dangerous_formula["severity"] == "high"

    def test_security_policy_strict_mode(self):
        """Test strict security policy (lines 413-434 coverage)."""
        workbook = Mock()
        workbook.sheetnames = ["Sheet1"]

        worksheet = Mock()
        workbook.__getitem__ = Mock(return_value=worksheet)

        # Mock cell with dangerous content
        cell = Mock()
        cell.hyperlink = Mock()
        cell.hyperlink.target = "http://evil.com"
        cell.coordinate = "A1"

        worksheet.iter_rows.return_value = [[cell]]

        result = self.strict_scanner.scan_security_threats(workbook)

        # Strict mode should generate errors
        assert not result.is_valid
        assert len(result.errors) >= 1
        assert "Security policy violation" in result.errors[0]

    def test_security_policy_warn_mode(self):
        """Test warn security policy with Python warnings."""
        workbook = Mock()
        workbook.sheetnames = ["Sheet1"]

        worksheet = Mock()
        workbook.__getitem__ = Mock(return_value=worksheet)

        # Mock cell with dangerous content
        cell = Mock()
        cell.hyperlink = Mock()
        cell.hyperlink.target = "https://suspicious.com"
        cell.coordinate = "A1"

        worksheet.iter_rows.return_value = [[cell]]

        # Capture warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            result = self.scanner.scan_security_threats(workbook)

            # Should be valid but with warnings
            assert result.is_valid
            assert len(result.warnings) >= 1
            assert "Security Warning" in result.warnings[0]

            # Should also issue Python warning
            assert len(w) >= 1
            assert issubclass(w[0].category, UserWarning)
            assert "Excel Security Warning" in str(w[0].message)

    def test_security_policy_disabled_mode(self):
        """Test disabled security policy."""
        workbook = Mock()
        workbook.sheetnames = ["Sheet1"]

        worksheet = Mock()
        workbook.__getitem__ = Mock(return_value=worksheet)

        # Mock cell with dangerous content
        cell = Mock()
        cell.hyperlink = Mock()
        cell.hyperlink.target = "http://very-evil.com/malware.exe"
        cell.coordinate = "A1"

        worksheet.iter_rows.return_value = [[cell]]

        result = self.disabled_scanner.scan_security_threats(workbook)

        # Disabled mode should not generate errors or warnings from policy
        # (threats are still detected but not acted upon)
        assert result.is_valid
        # Security issues are still detected
        assert len(result.security_issues) >= 1
        # But no policy errors
        policy_errors = [error for error in result.errors if "Security policy" in error]
        assert len(policy_errors) == 0

    def test_is_suspicious_link(self):
        """Test suspicious link detection logic."""
        scanner = SecurityScanner()

        # Test suspicious patterns
        assert scanner._is_suspicious_link("file:///path/to/evil.exe")
        assert scanner._is_suspicious_link("something.bat")
        assert scanner._is_suspicious_link("javascript:alert('xss')")
        assert scanner._is_suspicious_link(
            "data:text/html,<script>alert('xss')</script>"
        )

        # Test safe patterns
        assert not scanner._is_suspicious_link("https://google.com")
        assert not scanner._is_suspicious_link("mailto:user@example.com")
        assert not scanner._is_suspicious_link("file.xlsx")

    def test_scan_error_handling(self):
        """Test error handling during security scan."""
        workbook = Mock()
        workbook.sheetnames = ["Sheet1"]

        worksheet = Mock()
        workbook.__getitem__ = Mock(return_value=worksheet)

        # Mock worksheet.iter_rows to raise exception
        worksheet.iter_rows.side_effect = Exception("Mock scan error")

        result = self.scanner.scan_security_threats(workbook)

        # Should handle error gracefully (errors recorded as security issues)
        assert result.is_valid  # Individual scan errors don't fail the whole scan
        assert len(result.security_issues) >= 1
        # Check that scan errors are recorded
        scan_errors = [
            issue
            for issue in result.security_issues
            if "scan_error" in issue.get("type", "")
        ]
        assert len(scan_errors) >= 1

    def test_coverage_difficult_lines(self):
        """
        Test the specific lines that were difficult to cover in the original code.

        This test specifically targets:
        - Lines 365-381: External link validation logic
        - Lines 413-434: Security policy error handling
        """
        # Test case covering lines 365-381 logic
        workbook = Mock()
        workbook.sheetnames = ["TestSheet"]

        worksheet = Mock()
        workbook.__getitem__ = Mock(return_value=worksheet)

        # Create cells with various dangerous scenarios
        cells = []

        # Dangerous protocol scenario
        cell1 = Mock()
        cell1.hyperlink = Mock()
        cell1.hyperlink.target = "ftp://dangerous.com/file"
        cell1.coordinate = "A1"
        cells.append(cell1)

        # Multiple dangerous protocols
        cell2 = Mock()
        cell2.hyperlink = Mock()
        cell2.hyperlink.target = "telnet://remote.server.com"
        cell2.coordinate = "B2"
        cells.append(cell2)

        # Non-hyperlink cell (should be ignored)
        cell3 = Mock()
        cell3.hyperlink = None
        cell3.coordinate = "C3"
        cells.append(cell3)

        worksheet.iter_rows.return_value = [cells]

        # Test with strict security (lines 413-434 coverage)
        result = self.strict_scanner.scan_security_threats(workbook)

        # Verify the complex conditional logic is covered
        assert not result.is_valid  # Should fail in strict mode
        assert len(result.errors) >= 1
        assert "Security policy violation" in result.errors[0]
        assert "2" in result.errors[0]  # Should mention 2 high-severity threats

        # Verify security issues are detected
        hyperlink_issues = [
            issue for issue in result.security_issues if issue["type"] == "hyperlink"
        ]
        assert len(hyperlink_issues) == 2


class TestMockSecurityValidator:
    """Test suite for MockSecurityValidator."""

    def test_mock_validator_default(self):
        """Test MockSecurityValidator with default result."""
        mock_validator = MockSecurityValidator()

        result = mock_validator.validate_file(Path("dummy.xlsx"))
        assert result.is_valid
        assert len(result.errors) == 0

        result = mock_validator.scan_security_threats(Mock())
        assert result.is_valid
        assert len(result.errors) == 0

    def test_mock_validator_custom_result(self):
        """Test MockSecurityValidator with custom result."""
        custom_result = ValidationResult(
            is_valid=False,
            errors=["Mock error"],
            warnings=["Mock warning"],
            security_issues=[{"type": "mock_issue"}],
        )

        mock_validator = MockSecurityValidator(custom_result)

        result = mock_validator.validate_file(Path("dummy.xlsx"))
        assert not result.is_valid
        assert result.errors == ["Mock error"]
        assert result.warnings == ["Mock warning"]
        assert len(result.security_issues) == 1


class TestValidationResult:
    """Test suite for ValidationResult dataclass."""

    def test_validation_result_creation(self):
        """Test ValidationResult creation and access."""
        result = ValidationResult(
            is_valid=True,
            errors=["error1", "error2"],
            warnings=["warning1"],
            security_issues=[{"type": "test", "severity": "low"}],
        )

        assert result.is_valid
        assert len(result.errors) == 2
        assert len(result.warnings) == 1
        assert len(result.security_issues) == 1
        assert result.security_issues[0]["type"] == "test"


class TestInterface:
    """Test interface implementation."""

    def test_interface_implementation(self):
        """Test that SecurityScanner implements ISecurityValidator."""
        scanner = SecurityScanner()
        assert isinstance(scanner, ISecurityValidator)

        # Verify all abstract methods are implemented
        assert hasattr(scanner, "validate_file")
        assert hasattr(scanner, "scan_security_threats")
        assert callable(scanner.validate_file)
        assert callable(scanner.scan_security_threats)


# Integration test with real-world scenario
class TestIntegration:
    """Integration tests simulating real Excel processing scenarios."""

    def test_integration_with_dependency_injection(self):
        """Test integration with dependency injection pattern."""
        # This would be used in the main ExcelDataLoader
        custom_validator = MockSecurityValidator(
            ValidationResult(
                is_valid=True,
                errors=[],
                warnings=["Custom warning"],
                security_issues=[],
            )
        )

        # Simulate how it would be used in ExcelDataLoader
        def mock_excel_loader_method(security_validator: ISecurityValidator):
            file_result = security_validator.validate_file(Path("test.xlsx"))
            scan_result = security_validator.scan_security_threats(Mock())
            return file_result, scan_result

        file_result, scan_result = mock_excel_loader_method(custom_validator)

        assert file_result.is_valid
        assert scan_result.is_valid
        assert len(file_result.warnings) == 1
        assert "Custom warning" in file_result.warnings[0]
