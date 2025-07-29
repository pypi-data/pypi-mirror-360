"""Range Parser for Excel data processing.

Extracted from monolithic ExcelDataLoader (lines 814-853) to provide
focused, testable range parsing functionality using functional composition.
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Tuple

from ..errors.excel_errors import RangeSpecificationError, RangeValidationError


@dataclass
class RangeInfo:
    """Structured information about a parsed Excel range."""

    start_row: int
    start_col: int
    end_row: int
    end_col: int
    original_spec: str
    normalized_spec: str

    @property
    def row_count(self) -> int:
        """Number of rows in the range."""
        return self.end_row - self.start_row + 1

    @property
    def col_count(self) -> int:
        """Number of columns in the range."""
        return self.end_col - self.start_col + 1

    @property
    def cell_count(self) -> int:
        """Total number of cells in the range."""
        return self.row_count * self.col_count

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "start_row": self.start_row,
            "start_col": self.start_col,
            "end_row": self.end_row,
            "end_col": self.end_col,
            "original_spec": self.original_spec,
            "normalized_spec": self.normalized_spec,
            "row_count": self.row_count,
            "col_count": self.col_count,
            "cell_count": self.cell_count,
        }


class IRangeParser(ABC):
    """Abstract interface for range parsing functionality."""

    @abstractmethod
    def parse(self, range_spec: str) -> RangeInfo:
        """Parse a range specification into structured information.

        Args:
            range_spec: Excel range specification (e.g., 'A1:B10')

        Returns:
            RangeInfo: Structured range information

        Raises:
            RangeSpecificationError: If range specification is invalid
            RangeValidationError: If range bounds are invalid
        """
        pass


class RangeParser(IRangeParser):
    """Functional composition-based range parser.

    Implements range parsing through small, composable functions
    to address the 814-853 line complexity problem in excel_data_loader.py.
    """

    def __init__(self, max_rows: int = 1048576, max_cols: int = 16384):
        """Initialize range parser with Excel limits.

        Args:
            max_rows: Maximum number of rows (Excel default: 1,048,576)
            max_cols: Maximum number of columns (Excel default: 16,384)
        """
        self.max_rows = max_rows
        self.max_cols = max_cols

        # Cell reference pattern
        self._cell_pattern = re.compile(r"^([A-Z]+)(\d+)$")
        self._range_pattern = re.compile(r"^([A-Z]+\d+):([A-Z]+\d+)$")

    def parse(self, range_spec: str) -> RangeInfo:
        """Parse range specification using functional composition.

        Implements the pattern from plan.md:
        return self._compose_parsers(
            self._validate_type,      # 814-817行対応
            self._validate_empty,     # 819-823行対応
            self._parse_format,       # 828-835行対応
            self._validate_bounds     # 849-853行対応
        )(spec)
        """
        # Store original input for preservation
        self.original_input = range_spec

        return self._compose_parsers(
            self._validate_type,
            self._validate_empty,
            self._normalize_spec,
            self._parse_format,
            self._validate_bounds,
        )(range_spec)

    def _compose_parsers(self, *functions: Callable) -> Callable:
        """Compose parsing functions into a single callable.

        This enables functional composition for range parsing,
        making each step independently testable.
        """

        def composed(spec: str) -> RangeInfo:
            result = spec
            for func in functions:
                result = func(result)
            return result

        return composed

    def _validate_type(self, range_spec: Any) -> str:
        """Stage 1: Validate input type (addresses lines 814-817)."""
        if not isinstance(range_spec, str):
            raise TypeError(
                f"Range specification must be a string, got {type(range_spec).__name__}"
            )
        return range_spec

    def _validate_empty(self, range_spec: str) -> str:
        """Stage 2: Validate non-empty specification (addresses lines 819-823)."""
        range_spec_clean = range_spec.strip()
        if not range_spec_clean:
            raise RangeSpecificationError(
                range_spec, message="Range specification cannot be empty"
            )
        return range_spec_clean

    def _normalize_spec(self, range_spec: str) -> str:
        """Stage 3: Normalize specification format."""
        return range_spec.upper()

    def _parse_format(self, range_spec: str) -> Tuple[str, str, str, str]:
        """Stage 4: Parse range format (addresses lines 828-835)."""
        try:
            # Try to match range pattern (A1:B10)
            match = self._range_pattern.match(range_spec)
            if match:
                start_cell, end_cell = match.groups()
                return start_cell, end_cell, range_spec, self.original_input

            # Try single cell (A1 -> A1:A1)
            if self._cell_pattern.match(range_spec):
                return range_spec, range_spec, range_spec, self.original_input

            # Invalid format
            raise RangeSpecificationError(
                self.original_input,
                message=f"Invalid range format: {range_spec}. Expected format: A1:B10 or A1",
            )

        except Exception as e:
            if isinstance(e, RangeSpecificationError):
                raise
            raise RangeSpecificationError(
                self.original_input,
                message=f"Failed to parse range specification: {e}",
                original_error=e,
            ) from e

    def _validate_bounds(self, parse_result: Tuple[str, str, str, str]) -> RangeInfo:
        """Stage 5: Validate range bounds (addresses lines 847-851)."""
        start_cell, end_cell, normalized_spec, original_spec = parse_result

        try:
            # Parse cell addresses
            start_row, start_col = self._parse_cell_address(start_cell)
            end_row, end_col = self._parse_cell_address(end_cell)

            # Validate bounds
            self._check_bounds(start_row, start_col, end_row, end_col, original_spec)

            return RangeInfo(
                start_row=start_row,
                start_col=start_col,
                end_row=end_row,
                end_col=end_col,
                original_spec=original_spec,
                normalized_spec=f"{start_cell}:{end_cell}"
                if start_cell != end_cell
                else start_cell,
            )

        except (RangeSpecificationError, RangeValidationError):
            raise
        except Exception as e:
            raise RangeSpecificationError(
                original_spec,
                message=f"Failed to parse cell addresses in range: {e}",
                original_error=e,
            ) from e

    def _parse_cell_address(self, cell_address: str) -> Tuple[int, int]:
        """Parse Excel cell address into (row, column) indices.

        Args:
            cell_address: Excel cell address like 'A1', 'BC123'

        Returns:
            Tuple of (row_index, col_index) both 1-based
        """
        match = self._cell_pattern.match(cell_address)
        if not match:
            raise RangeSpecificationError(
                cell_address, message=f"Invalid cell address format: {cell_address}"
            )

        col_letters, row_str = match.groups()

        try:
            row = int(row_str)
            if row <= 0:
                raise ValueError("Row number must be positive")
        except ValueError as e:
            raise RangeSpecificationError(
                cell_address,
                message=f"Invalid row number in cell address: {row_str}",
                original_error=e,
            ) from e

        # Convert column letters to number (A=1, B=2, ..., Z=26, AA=27, ...)
        col = self._column_letters_to_number(col_letters)

        return row, col

    def _column_letters_to_number(self, letters: str) -> int:
        """Convert Excel column letters to number.

        Examples:
            A -> 1, B -> 2, ..., Z -> 26
            AA -> 27, AB -> 28, ..., AZ -> 52
            BA -> 53, etc.
        """
        result = 0
        for char in letters:
            result = result * 26 + (ord(char) - ord("A") + 1)
        return result

    def _check_bounds(
        self,
        start_row: int,
        start_col: int,
        end_row: int,
        end_col: int,
        range_spec: str,
    ) -> None:
        """Validate range bounds against Excel limits and logical constraints."""
        # Check if coordinates are positive
        if start_row < 1 or start_col < 1 or end_row < 1 or end_col < 1:
            raise RangeValidationError(
                range_spec, message="Row and column indices must be positive (1-based)"
            )

        # Check Excel limits
        if start_row > self.max_rows or end_row > self.max_rows:
            raise RangeValidationError(
                range_spec, message=f"Row index exceeds Excel limit of {self.max_rows}"
            )

        if start_col > self.max_cols or end_col > self.max_cols:
            raise RangeValidationError(
                range_spec,
                message=f"Column index exceeds Excel limit of {self.max_cols}",
            )

        # Check logical order
        if start_row > end_row:
            raise RangeValidationError(
                range_spec,
                message=f"Start row ({start_row}) cannot be greater than end row ({end_row})",
            )

        if start_col > end_col:
            raise RangeValidationError(
                range_spec,
                message=f"Start column ({start_col}) cannot be greater than end column ({end_col})",
            )


class MockRangeParser(IRangeParser):
    """Mock implementation for testing purposes."""

    def __init__(
        self,
        mock_result: Optional[RangeInfo] = None,
        should_fail: bool = False,
        error_to_raise: Optional[Exception] = None,
    ):
        """Initialize mock parser.

        Args:
            mock_result: Fixed result to return, or None for default
            should_fail: Whether to raise an error
            error_to_raise: Specific error to raise, or default RangeSpecificationError
        """
        self.mock_result = mock_result
        self.should_fail = should_fail
        self.error_to_raise = error_to_raise or RangeSpecificationError(
            "A1:B2", message="Mock error"
        )
        self.parse_calls = []

    def parse(self, range_spec: str) -> RangeInfo:
        """Mock parse implementation with call tracking."""
        self.parse_calls.append({"range_spec": range_spec})

        if self.should_fail:
            raise self.error_to_raise

        if self.mock_result:
            return self.mock_result

        # Default mock result
        return RangeInfo(
            start_row=1,
            start_col=1,
            end_row=10,
            end_col=2,
            original_spec=range_spec,
            normalized_spec="A1:B10",
        )
