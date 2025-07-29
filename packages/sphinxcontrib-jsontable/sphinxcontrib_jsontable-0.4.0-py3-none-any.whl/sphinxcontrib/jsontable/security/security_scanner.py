"""
Security scanner for Excel files - handles external links and threat detection.

This module extracts security validation logic from the monolithic ExcelDataLoader
to improve testability and follow single responsibility principle.
"""

import re
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ValidationResult:
    """Security validation result container."""

    is_valid: bool
    errors: List[str]
    warnings: List[str]
    security_issues: List[Dict[str, str]]


class ISecurityValidator(ABC):
    """Abstract interface for security validation."""

    @abstractmethod
    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate file-level security."""
        pass

    @abstractmethod
    def scan_security_threats(self, workbook: Any) -> ValidationResult:
        """Scan workbook for security threats."""
        pass


class SecurityScanner(ISecurityValidator):
    """
    Excel security scanner implementation.

    Extracts security validation logic from ExcelDataLoader (lines 365-381, 413-434).
    Provides testable, mockable security validation functionality.
    """

    # Security levels (migrated from ExcelDataLoader)
    MACRO_SECURITY_DISABLED = "disabled"
    MACRO_SECURITY_WARN = "warn"
    MACRO_SECURITY_STRICT = "strict"

    def __init__(self, macro_security: str = MACRO_SECURITY_WARN):
        """Initialize security scanner with specified security level."""
        self.macro_security = macro_security
        self.dangerous_protocols = [
            "http://",
            "https://",
            "ftp://",
            "file://",
            "mailto:",
            "telnet://",
            "ssh://",
        ]

    def validate_file(self, file_path: Path) -> ValidationResult:
        """
        Validate file-level security aspects.

        Args:
            file_path: Path to Excel file

        Returns:
            ValidationResult with security assessment
        """
        errors = []
        warning_messages = []
        security_issues = []

        # Basic file validation
        if not file_path.exists():
            errors.append(f"File not found: {file_path}")
            return ValidationResult(False, errors, warning_messages, security_issues)

        # File extension validation
        if file_path.suffix.lower() not in [".xlsx", ".xls", ".xlsm"]:
            warning_messages.append(f"Unexpected file extension: {file_path.suffix}")

        # Macro-enabled file detection
        if file_path.suffix.lower() == ".xlsm":
            security_issues.append(
                {
                    "type": "macro_file",
                    "severity": "medium",
                    "location": str(file_path),
                    "description": "File may contain macros",
                }
            )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warning_messages,
            security_issues=security_issues,
        )

    def scan_security_threats(self, workbook: Any) -> ValidationResult:
        """
        Scan workbook for security threats.

        This method extracts and refactors the complex security logic from
        ExcelDataLoader._validate_external_links() (lines 365-381) and
        error handling logic (lines 413-434).

        Args:
            workbook: openpyxl Workbook object

        Returns:
            ValidationResult with detected threats
        """
        errors = []
        warning_messages = []
        security_issues = []

        try:
            # Scan all worksheets for security threats
            for sheet_name in workbook.sheetnames:
                worksheet = workbook[sheet_name]

                # Scan for external links (extracted from lines 365-381)
                external_links = self._scan_external_links(worksheet, sheet_name)
                security_issues.extend(external_links)

                # Scan for dangerous formulas
                dangerous_formulas = self._scan_dangerous_formulas(
                    worksheet, sheet_name
                )
                security_issues.extend(dangerous_formulas)

            # Apply security policy (extracted from lines 413-434)
            policy_result = self._apply_security_policy(security_issues)
            errors.extend(policy_result["errors"])
            warning_messages.extend(policy_result["warnings"])

        except Exception as e:
            errors.append(f"Security scan failed: {str(e)}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warning_messages,
            security_issues=security_issues,
        )

    def _scan_external_links(
        self, worksheet: Any, sheet_name: str
    ) -> List[Dict[str, str]]:
        """
        Scan worksheet for external links.

        Extracted and refactored from ExcelDataLoader._validate_external_links()
        lines 365-381. Now testable in isolation.
        """
        dangerous_links = []

        try:
            for row in worksheet.iter_rows():
                for cell in row:
                    if cell.hyperlink and cell.hyperlink.target:
                        target = str(cell.hyperlink.target).lower()

                        # Check for dangerous protocols (improved logic)
                        if any(proto in target for proto in self.dangerous_protocols):
                            dangerous_links.append(
                                {
                                    "type": "hyperlink",
                                    "severity": "high",
                                    "location": f"{sheet_name}!{cell.coordinate}",
                                    "target": cell.hyperlink.target,
                                    "description": f"External link to {target}",
                                }
                            )

                        # Check for suspicious patterns
                        if self._is_suspicious_link(target):
                            dangerous_links.append(
                                {
                                    "type": "suspicious_link",
                                    "severity": "medium",
                                    "location": f"{sheet_name}!{cell.coordinate}",
                                    "target": cell.hyperlink.target,
                                    "description": "Potentially suspicious external link",
                                }
                            )

        except Exception as e:
            dangerous_links.append(
                {
                    "type": "scan_error",
                    "severity": "low",
                    "location": f"{sheet_name}",
                    "target": "",
                    "description": f"Failed to scan hyperlinks: {str(e)}",
                }
            )

        return dangerous_links

    def _scan_dangerous_formulas(
        self, worksheet: Any, sheet_name: str
    ) -> List[Dict[str, str]]:
        """Scan for potentially dangerous formulas."""
        dangerous_formulas = []

        # Patterns for dangerous formula functions
        dangerous_patterns = [
            r"CALL\s*\(",
            r"REGISTER\s*\(",
            r"EXECUTE\s*\(",
            r"SYSTEM\s*\(",
        ]

        try:
            for row in worksheet.iter_rows():
                for cell in row:
                    if cell.data_type == "f" and cell.value:  # Formula cell
                        formula = str(cell.value).upper()

                        for pattern in dangerous_patterns:
                            if re.search(pattern, formula):
                                dangerous_formulas.append(
                                    {
                                        "type": "dangerous_formula",
                                        "severity": "high",
                                        "location": f"{sheet_name}!{cell.coordinate}",
                                        "target": cell.value,
                                        "description": f"Potentially dangerous formula: {pattern}",
                                    }
                                )

        except Exception as e:
            dangerous_formulas.append(
                {
                    "type": "formula_scan_error",
                    "severity": "low",
                    "location": f"{sheet_name}",
                    "target": "",
                    "description": f"Failed to scan formulas: {str(e)}",
                }
            )

        return dangerous_formulas

    def _is_suspicious_link(self, target: str) -> bool:
        """Check if link target is suspicious."""
        suspicious_patterns = [
            r"\.exe$",
            r"\.bat$",
            r"\.cmd$",
            r"\.scr$",
            r"javascript:",
            r"data:",
            r"vbscript:",
        ]

        return any(
            re.search(pattern, target, re.IGNORECASE) for pattern in suspicious_patterns
        )

    def _apply_security_policy(
        self, security_issues: List[Dict[str, str]]
    ) -> Dict[str, List[str]]:
        """
        Apply security policy based on macro_security setting.

        Extracted and refactored from ExcelDataLoader error handling (lines 413-434).
        Now testable and mockable.
        """
        errors = []
        warning_messages = []

        # Filter high-severity issues
        high_severity_issues = [
            issue for issue in security_issues if issue.get("severity") == "high"
        ]

        if high_severity_issues:
            issue_descriptions = [
                issue["description"] for issue in high_severity_issues
            ]

            if self.macro_security == self.MACRO_SECURITY_STRICT:
                # Strict mode: treat as errors
                errors.append(
                    f"Security policy violation: {len(high_severity_issues)} "
                    f"high-severity threats detected: {', '.join(issue_descriptions[:3])}"
                    f"{'...' if len(issue_descriptions) > 3 else ''}"
                )

            elif self.macro_security == self.MACRO_SECURITY_WARN:
                # Warn mode: issue warnings
                warning_msg = (
                    f"Security Warning: {len(high_severity_issues)} "
                    f"potential threats detected: {', '.join(issue_descriptions[:3])}"
                    f"{'...' if len(issue_descriptions) > 3 else ''}"
                )
                warning_messages.append(warning_msg)

                # Also issue Python warning (testable)
                warnings.warn(
                    f"Excel Security Warning: {len(high_severity_issues)} threats detected",
                    UserWarning,
                    stacklevel=3,
                )

            # MACRO_SECURITY_DISABLED: no action taken

        return {"errors": errors, "warnings": warning_messages}


# Default implementation for dependency injection
class DefaultSecurityValidator(SecurityScanner):
    """Default security validator implementation."""

    def __init__(self):
        super().__init__(macro_security=self.MACRO_SECURITY_WARN)


# Mock implementation for testing
class MockSecurityValidator(ISecurityValidator):
    """Mock security validator for testing purposes."""

    def __init__(self, mock_result: Optional[ValidationResult] = None):
        self.mock_result = mock_result or ValidationResult(
            is_valid=True, errors=[], warnings=[], security_issues=[]
        )

    def validate_file(self, file_path: Path) -> ValidationResult:
        """Return mock validation result."""
        return self.mock_result

    def scan_security_threats(self, workbook: Any) -> ValidationResult:
        """Return mock scan result."""
        return self.mock_result
