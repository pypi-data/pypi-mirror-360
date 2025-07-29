"""Data Converter Core - Core data conversion functionality.

Essential data conversion operations with type preservation and optimization.

CLAUDE.md Code Excellence Compliance:
- Single Responsibility: Data conversion operations only
- DRY Principle: Centralized conversion logic
- SOLID Principles: Interface implementation with dependency injection
"""

from typing import Any, List

import pandas as pd

from ..errors.excel_errors import DataConversionError
from .data_conversion_types import ConversionResult, IDataConverter
from .header_detection import HeaderDetector, HeaderNormalizer


class DataConverterCore(IDataConverter):
    """Core data conversion functionality.

    Provides essential DataFrame to JSON conversion with type preservation
    and integrated header detection/normalization.
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
        self.empty_string_replacement = empty_string_replacement
        self.preserve_numeric_types = preserve_numeric_types

        # Initialize specialized components
        self.header_detector = HeaderDetector(header_keywords)
        self.header_normalizer = HeaderNormalizer()

    def convert_dataframe_to_json(
        self, df: pd.DataFrame, header_row: int = None
    ) -> ConversionResult:
        """Convert pandas DataFrame to JSON-compatible structure.

        Args:
            df: Pandas DataFrame to convert
            header_row: Row number to use as headers (0-based)

        Returns:
            ConversionResult with converted data and metadata
        """
        try:
            # Determine header presence
            if header_row is not None:
                has_header = True
                if header_row > 0:
                    # Extract specific header row
                    headers = [str(val) for val in df.iloc[header_row]]
                    data_df = df.drop(df.index[header_row]).reset_index(drop=True)
                else:
                    headers = [str(col) for col in df.columns]
                    data_df = df
            else:
                # Auto-detect headers
                detection_result = self.header_detector.detect_header(df)
                has_header = detection_result.has_header

                if has_header:
                    headers = detection_result.headers
                    data_df = df.iloc[1:].reset_index(drop=True)  # Skip first row
                else:
                    headers = [f"Column_{i + 1}" for i in range(len(df.columns))]
                    data_df = df

            # Convert DataFrame to 2D array with proper type handling
            data_array = self._convert_dataframe_values(data_df)

            # Normalize headers if needed
            if has_header:
                headers = self.header_normalizer.normalize_headers(headers)

            # Build metadata
            metadata = {
                "conversion_type": "dataframe_to_json",
                "preserve_numeric_types": self.preserve_numeric_types,
                "empty_replacement": self.empty_string_replacement,
                "original_columns": len(df.columns),
                "original_rows": len(df),
                "processed_rows": len(data_array),
                "header_detection": has_header,
            }

            return ConversionResult(
                data=data_array,
                has_header=has_header,
                headers=headers,
                metadata=metadata,
            )

        except Exception as e:
            raise DataConversionError(
                "dataframe_to_json",
                message=f"Failed to convert DataFrame to JSON: {e}",
                original_error=e,
            ) from e

    def detect_header(self, df: pd.DataFrame):
        """Detect if DataFrame has a header row.

        Args:
            df: DataFrame to analyze

        Returns:
            HeaderDetectionResult with detection analysis
        """
        return self.header_detector.detect_header(df)

    def normalize_headers(
        self, headers: List[str], japanese_support: bool = True
    ) -> List[str]:
        """Normalize header names for consistency.

        Args:
            headers: List of header names to normalize
            japanese_support: Enable Japanese character handling

        Returns:
            Normalized header names
        """
        return self.header_normalizer.normalize_headers(headers, japanese_support)

    def _convert_dataframe_values(self, df: pd.DataFrame) -> List[List[Any]]:
        """Convert DataFrame values with proper type handling.

        Args:
            df: DataFrame to convert

        Returns:
            2D array of converted values
        """
        data_array = []

        for _, row in df.iterrows():
            row_data = []
            for value in row:
                # Handle NaN/None values
                if pd.isna(value):
                    row_data.append(self.empty_string_replacement)
                    continue

                # Handle numeric values with type preservation
                if self.preserve_numeric_types and self._is_numeric_value(value):
                    # Convert to int if it's a whole number, otherwise keep as float
                    if isinstance(value, float) and value.is_integer():
                        row_data.append(int(value))
                    else:
                        row_data.append(value)
                else:
                    # Convert to string for consistency
                    row_data.append(str(value))

            data_array.append(row_data)

        return data_array

    def _is_numeric_value(self, value: Any) -> bool:
        """Check if value is numeric.

        Args:
            value: Value to check

        Returns:
            True if value is numeric
        """
        if isinstance(value, (int, float)):
            return True

        if isinstance(value, str):
            try:
                float(value)
                return True
            except (ValueError, TypeError):
                return False

        return False

    def normalize_data_structure(self, data: Any) -> List[List[Any]]:
        """Normalize data structure to 2D list format.

        Args:
            data: Input data to normalize

        Returns:
            Normalized 2D list structure
        """
        if isinstance(data, list):
            # If it's already a list of dicts, convert to 2D list
            if data and isinstance(data[0], dict):
                if not data:
                    return []
                headers = list(data[0].keys())
                result = [headers]
                for item in data:
                    row = [item.get(key, "") for key in headers]
                    result.append(row)
                return result
            # If it's already a 2D list, return as-is
            elif data and isinstance(data[0], list):
                return data
            else:
                # Single level list, convert to single row
                return [data] if data else []
        elif isinstance(data, dict):
            # Convert single dict to 2D list
            headers = list(data.keys())
            values = list(data.values())
            return [headers, values]
        else:
            # Single value, wrap in 2D structure
            return [[str(data)]]

    def handle_missing_values(self, data: Any) -> Any:
        """Handle missing values in data structure.

        Args:
            data: Data with potential missing values

        Returns:
            Data with missing values handled
        """
        if isinstance(data, list):
            return [
                self.handle_missing_values(item)
                if isinstance(item, (list, dict))
                else (self.empty_string_replacement if item is None else item)
                for item in data
            ]
        elif isinstance(data, dict):
            return {
                key: (
                    self.empty_string_replacement
                    if value is None
                    else self.handle_missing_values(value)
                    if isinstance(value, (list, dict))
                    else value
                )
                for key, value in data.items()
            }
        else:
            return self.empty_string_replacement if data is None else data

    def convert_data_types(self, data: Any) -> Any:
        """Convert data types for consistency.

        Args:
            data: Data to convert types

        Returns:
            Data with converted types
        """
        if isinstance(data, list):
            return [self.convert_data_types(item) for item in data]
        elif isinstance(data, dict):
            return {key: self.convert_data_types(value) for key, value in data.items()}
        elif isinstance(data, str):
            # Try to convert string numbers to numeric types
            if self.preserve_numeric_types and self._is_numeric_value(data):
                try:
                    if "." in data:
                        return float(data)
                    else:
                        return int(data)
                except (ValueError, TypeError):
                    pass
            # Convert boolean strings
            if data.lower() in ("true", "yes", "1"):
                return True
            elif data.lower() in ("false", "no", "0"):
                return False
        return data
