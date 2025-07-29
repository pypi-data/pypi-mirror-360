"""Excel Processing Pipeline - Multi-stage Excel processing workflow.

This module contains the core processing pipeline for Excel data loading,
implementing a 5-stage processing workflow with error handling and validation.

CLAUDE.md Code Excellence Compliance:
- Single Responsibility: Excel processing workflow
- DRY Principle: Centralized processing logic
- SOLID Principles: Interface segregation and dependency injection
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union

import pandas as pd

from ..core.data_converter import IDataConverter
from ..core.excel_reader import IExcelReader
from ..core.range_parser import IRangeParser, RangeInfo
from ..errors.error_handlers import IErrorHandler
from ..security.security_scanner import ISecurityValidator


class ExcelProcessingPipeline:
    """5-stage Excel processing pipeline with integrated error handling.

    This class implements the core processing workflow for Excel data loading,
    coordinating security validation, range parsing, file reading, data conversion,
    and result integration.

    Processing Stages:
        1. Security validation
        2. Range parsing (if specified)
        3. File reading
        4. Data conversion
        5. Result integration
    """

    def __init__(
        self,
        excel_reader: IExcelReader,
        data_converter: IDataConverter,
        range_parser: IRangeParser,
        security_validator: Optional[ISecurityValidator] = None,
        error_handler: Optional[IErrorHandler] = None,
        enable_security: bool = True,
        enable_error_handling: bool = True,
    ):
        """Initialize processing pipeline with components."""
        self.excel_reader = excel_reader
        self.data_converter = data_converter
        self.range_parser = range_parser
        self.security_validator = security_validator
        self.error_handler = error_handler
        self.enable_security = enable_security
        self.enable_error_handling = enable_error_handling

    def process_excel_file(
        self,
        file_path: Union[str, Path],
        sheet_name: Optional[str] = None,
        sheet_index: Optional[int] = None,
        range_spec: Optional[str] = None,
        header_row: Optional[int] = None,
        skip_rows: Optional[str] = None,
        merge_mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute 5-stage Excel processing pipeline.

        Args:
            file_path: Path to Excel file
            sheet_name: Target sheet name
            sheet_index: Target sheet index (0-based)
            range_spec: Excel range specification (e.g., "A1:C10")
            header_row: Header row number (0-based)
            skip_rows: Row skip specification (e.g., "0,1,2" or "0-2,5,7-9")
            merge_mode: How to handle merged cells ('expand', 'first', 'skip')

        Returns:
            Processing result with data and metadata
        """
        context = "excel_processing_pipeline"

        try:
            # Stage 1: Security validation
            if self.enable_security and self.security_validator:
                self._perform_security_validation(file_path, context)

            # Stage 2: Range parsing (if specified)
            range_info = None
            if range_spec:
                range_info = self._parse_range_specification(range_spec, context)

            # Stage 3: File reading
            read_result = self._read_excel_file(
                file_path, sheet_name, sheet_index, context
            )

            # Stage 3.5: Apply range to raw DataFrame (if specified)
            # This ensures range operates on Excel's 1-based row numbering
            if range_info:
                read_result.dataframe = self._apply_range_to_dataframe(
                    read_result.dataframe, range_info, context
                )

                # Adjust header_row index to be relative to the range
                if header_row is not None:
                    header_row = self._adjust_header_row_for_range(
                        header_row, range_info, context
                    )

            # Stage 3.75: Apply skip rows to dataframe (if specified)
            skip_rows_list = None
            if skip_rows:
                skip_rows_list = self._parse_skip_rows_specification(skip_rows, context)
                read_result.dataframe = self._apply_skip_rows_to_dataframe(
                    read_result.dataframe, skip_rows_list, context
                )

                # Adjust header_row index to account for skipped rows
                if header_row is not None:
                    header_row = self._adjust_header_row_for_skip_rows(
                        header_row, skip_rows_list, context
                    )

            # Stage 4: Data conversion
            conversion_result = self._convert_data_to_json(
                read_result.dataframe, header_row, context
            )

            # Stage 5: Result integration (header processing only)
            return self._build_integrated_result(
                conversion_result,
                read_result,
                range_info,
                context,
                header_row,
                skip_rows_list,
                skip_rows,
                merge_mode,
            )

        except ValueError:
            # Re-raise ValueError directly for proper test behavior
            raise
        except Exception as e:
            return self._handle_processing_error(e, context)

    def _perform_security_validation(
        self, file_path: Union[str, Path], context: str
    ) -> None:
        """Stage 1: Perform security validation."""
        if not self.security_validator:
            return

        try:
            security_result = self.security_validator.validate_file(Path(file_path))
            # ValidationResultはdataclassなので属性アクセスを使用
            if not security_result.is_valid:
                threats = security_result.security_issues
                threat_summary = ", ".join([t.get("type", "Unknown") for t in threats])
                raise SecurityError(f"Security threats detected: {threat_summary}")

        except Exception as e:
            if self.enable_error_handling and self.error_handler:
                error_response = self.error_handler.create_error_response(e, context)
                raise ProcessingError(
                    f"Security validation failed: {error_response}"
                ) from e
            else:
                raise

    def _parse_range_specification(
        self, range_spec: str, context: str
    ) -> Optional[RangeInfo]:
        """Stage 2: Parse range specification."""
        try:
            return self.range_parser.parse(range_spec)
        except Exception as e:
            if self.enable_error_handling and self.error_handler:
                error_response = self.error_handler.create_error_response(e, context)
                raise ProcessingError(f"Range parsing failed: {error_response}") from e
            else:
                raise

    def _read_excel_file(
        self,
        file_path: Union[str, Path],
        sheet_name: Optional[str],
        sheet_index: Optional[int],
        context: str,
    ) -> Any:
        """Stage 3: Read Excel file."""
        try:
            return self.excel_reader.read_workbook(
                file_path, sheet_name=sheet_name, sheet_index=sheet_index
            )
        except Exception as e:
            if self.enable_error_handling and self.error_handler:
                error_response = self.error_handler.create_error_response(e, context)
                raise ProcessingError(f"File reading failed: {error_response}") from e
            else:
                raise

    def _convert_data_to_json(
        self, dataframe: pd.DataFrame, header_row: Optional[int], context: str
    ) -> Any:
        """Stage 4: Convert data to JSON format.

        Note: header_row processing is handled separately in _apply_header_row_processing
        to avoid double-processing. DataConverter should use auto-detection only.
        """
        try:
            # Pass header_row=None to avoid double-processing
            # Header row processing is handled separately in Stage 5
            return self.data_converter.convert_dataframe_to_json(
                dataframe, header_row=None
            )
        except Exception as e:
            if self.enable_error_handling and self.error_handler:
                error_response = self.error_handler.create_error_response(e, context)
                raise ProcessingError(
                    f"Data conversion failed: {error_response}"
                ) from e
            else:
                raise

    def _build_integrated_result(
        self,
        conversion_result: Any,
        read_result: Any,
        range_info: Optional[RangeInfo],
        context: str,
        header_row: Optional[int] = None,
        skip_rows_list: Optional[list] = None,
        skip_rows_original: Optional[str] = None,
        merge_mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Stage 5: Build integrated result with header processing only.

        Note: Range application is now handled in Stage 3.5 on raw DataFrame.
        """
        try:
            # Get converted data (range already applied if specified)
            data = conversion_result.data
            actual_rows = len(data) if data else 0
            actual_cols = len(data[0]) if data else 0

            # Process header row if specified
            headers = conversion_result.headers
            has_header = conversion_result.has_header
            if header_row is not None:
                data, headers, has_header = self._apply_header_row_processing(
                    data, header_row
                )
                actual_rows = len(data)

            result = {
                "success": True,
                "data": data,
                "rows": actual_rows,
                "columns": actual_cols,
                "headers": headers,  # Add headers to top level
                "has_header": has_header,  # Add has_header to top level
                "metadata": {
                    "has_header": has_header,
                    "headers": headers,
                    "workbook_info": read_result.workbook_info.to_dict(),
                    "processing_timestamp": pd.Timestamp.now().isoformat(),
                },
                "components_used": self._get_components_info(),
            }

            # Add header row information if specified
            if header_row is not None:
                result["header_row"] = header_row

            # Add range information if available
            if range_info:
                result["range"] = range_info.original_spec
                result["metadata"]["range_info"] = {
                    "original_spec": range_info.original_spec,
                    "normalized_spec": range_info.normalized_spec,
                    "row_count": range_info.row_count,
                    "col_count": range_info.col_count,
                }

            # Add skip rows information if available
            if skip_rows_list:
                result["skip_rows"] = skip_rows_original or ",".join(
                    map(str, skip_rows_list)
                )
                result["skipped_row_count"] = len(skip_rows_list)
                result["metadata"]["skip_rows_info"] = {
                    "skipped_rows": skip_rows_list,
                    "skipped_count": len(skip_rows_list),
                    "original_spec": skip_rows_original,
                }

            # Add merge mode information if available
            if merge_mode:
                result["merge_mode"] = merge_mode
                result["metadata"]["merge_info"] = {
                    "merge_mode": merge_mode,
                    "has_merged_cells": False,  # Placeholder - TODO: implement actual detection
                    "merged_ranges": [],  # Placeholder
                }

            return result

        except ValueError:
            # Re-raise ValueError directly for proper test behavior
            raise
        except Exception as e:
            if self.enable_error_handling and self.error_handler:
                error_response = self.error_handler.create_error_response(e, context)
                raise ProcessingError(
                    f"Result integration failed: {error_response}"
                ) from e
            else:
                raise

    def _handle_processing_error(
        self, error: Exception, context: str
    ) -> Dict[str, Any]:
        """Handle processing errors."""
        if self.enable_error_handling and self.error_handler:
            return self.error_handler.create_error_response(error, context)
        else:
            return {
                "success": False,
                "error": {
                    "type": type(error).__name__,
                    "message": str(error),
                    "context": context,
                },
                "data": None,
            }

    def _apply_range_to_dataframe(
        self, dataframe: pd.DataFrame, range_info: RangeInfo, context: str
    ) -> pd.DataFrame:
        """Apply range specification to raw DataFrame.

        Operates on Excel's 1-based row/column numbering for accurate range selection.

        Args:
            dataframe: Original pandas DataFrame
            range_info: Range specification with 1-based indices
            context: Processing context for error reporting

        Returns:
            DataFrame subset matching the specified range
        """
        try:
            # Convert 1-based Excel indices to 0-based DataFrame indices
            start_row = range_info.start_row - 1
            end_row = range_info.end_row - 1
            start_col = range_info.start_col - 1
            end_col = range_info.end_col - 1

            # Validate range bounds against DataFrame
            max_df_rows = len(dataframe)
            max_df_cols = len(dataframe.columns)

            if start_row >= max_df_rows or end_row >= max_df_rows:
                raise ProcessingError(
                    f"Range row indices ({range_info.start_row}-{range_info.end_row}) "
                    f"exceed DataFrame rows (1-{max_df_rows})"
                )

            if start_col >= max_df_cols or end_col >= max_df_cols:
                raise ProcessingError(
                    f"Range column indices ({range_info.start_col}-{range_info.end_col}) "
                    f"exceed DataFrame columns (1-{max_df_cols})"
                )

            # Apply range selection to DataFrame
            range_df = dataframe.iloc[start_row : end_row + 1, start_col : end_col + 1]

            # Reset index to maintain 0-based indexing
            return range_df.reset_index(drop=True)

        except Exception as e:
            if self.enable_error_handling and self.error_handler:
                error_response = self.error_handler.create_error_response(e, context)
                raise ProcessingError(
                    f"DataFrame range application failed: {error_response}"
                ) from e
            else:
                raise

    def _adjust_header_row_for_range(
        self, header_row: int, range_info: RangeInfo, context: str
    ) -> int:
        """Adjust header_row index to be relative to the applied range.

        Args:
            header_row: Original header row index (0-based)
            range_info: Range specification with 1-based indices
            context: Processing context for error reporting

        Returns:
            Adjusted header row index relative to the range (0-based)

        Raises:
            ProcessingError: If header_row is outside the specified range
        """
        try:
            # Convert 1-based Excel range to 0-based DataFrame indices
            range_start_row = range_info.start_row - 1
            range_end_row = range_info.end_row - 1

            # Check if header_row is within the range
            if header_row < range_start_row or header_row > range_end_row:
                raise ProcessingError(
                    f"Header row {header_row} is outside the specified range "
                    f"({range_info.start_row}-{range_info.end_row})"
                )

            # Calculate relative index within the range
            relative_header_row = header_row - range_start_row

            return relative_header_row

        except Exception as e:
            if self.enable_error_handling and self.error_handler:
                error_response = self.error_handler.create_error_response(e, context)
                raise ProcessingError(
                    f"Header row adjustment failed: {error_response}"
                ) from e
            else:
                raise

    def _apply_range_to_data(self, data: Any, range_info: RangeInfo) -> Any:
        """Apply range specification to extract data subset.

        Converts 1-based Excel indices to 0-based Python indices and extracts
        the specified range from the data.

        Args:
            data: Original data as list of lists
            range_info: Range specification with 1-based indices

        Returns:
            Extracted data subset as list of lists
        """
        if not data or not isinstance(data, list):
            return data

        # Convert 1-based Excel indices to 0-based Python indices
        start_row = range_info.start_row - 1
        end_row = range_info.end_row - 1
        start_col = range_info.start_col - 1
        end_col = range_info.end_col - 1

        # Validate range bounds against actual data
        max_data_rows = len(data)
        max_data_cols = len(data[0]) if data else 0

        if start_row >= max_data_rows or end_row >= max_data_rows:
            raise ProcessingError(
                f"Range row indices ({range_info.start_row}-{range_info.end_row}) "
                f"exceed data rows (1-{max_data_rows})"
            )

        if start_col >= max_data_cols or end_col >= max_data_cols:
            raise ProcessingError(
                f"Range column indices ({range_info.start_col}-{range_info.end_col}) "
                f"exceed data columns (1-{max_data_cols})"
            )

        # Extract range data: rows [start_row:end_row+1], columns [start_col:end_col+1]
        range_data = []
        for row_idx in range(start_row, end_row + 1):
            if row_idx < len(data):
                row_data = data[row_idx]
                if isinstance(row_data, list):
                    # Extract specified columns from this row
                    range_row = row_data[start_col : end_col + 1]
                    range_data.append(range_row)
                else:
                    # Handle non-list row data
                    range_data.append([row_data])

        return range_data

    def _apply_header_row_processing(
        self, data: Any, header_row: int
    ) -> tuple[Any, list[str], bool]:
        """Apply header row processing to extract headers and remove header row from data.

        Args:
            data: Original data as list of lists
            header_row: Header row index (0-based)

        Returns:
            Tuple of (processed_data, headers, has_header)
        """
        # Validate header_row parameter
        if header_row < 0:
            raise ValueError("Header row must be non-negative")

        if not data or not isinstance(data, list):
            return data, [], False

        # Validate header_row bounds
        if header_row >= len(data):
            raise ValueError(f"Header row {header_row} is out of range")

        # Extract headers from specified row
        header_data = data[header_row]
        if isinstance(header_data, list):
            headers = [str(cell) if cell is not None else "" for cell in header_data]
        else:
            headers = [str(header_data)]

        # Normalize headers (handle empty headers)
        headers = self._normalize_header_names(headers)

        # Remove header row and all rows before it from data
        processed_data = data[header_row + 1 :]

        return processed_data, headers, True

    def _normalize_header_names(self, headers: list[str]) -> list[str]:
        """Normalize header names to handle empty headers and duplicates.

        Args:
            headers: List of raw header names

        Returns:
            List of normalized header names
        """
        normalized = []
        header_counts = {}

        for i, header in enumerate(headers):
            # Strip whitespace
            header = header.strip()

            # Handle empty headers
            if not header:
                header = f"column_{i + 1}"

            # Handle duplicates
            if header in header_counts:
                header_counts[header] += 1
                header = f"{header}_{header_counts[header]}"
            else:
                header_counts[header] = 0

            normalized.append(header)

        return normalized

    def _parse_skip_rows_specification(self, skip_rows: str, context: str) -> list[int]:
        """Parse skip rows specification into list of row indices.

        Args:
            skip_rows: Skip rows specification (e.g., "0,1,2" or "0-2,5,7-9")
            context: Processing context for error reporting

        Returns:
            List of row indices to skip (0-based, sorted, deduplicated)

        Raises:
            ProcessingError: If skip_rows format is invalid
        """
        try:
            if not skip_rows or not skip_rows.strip():
                return []

            # Split by commas and process each part
            parts = skip_rows.strip().split(",")
            skip_indices = set()

            for part in parts:
                part = part.strip()
                if not part:
                    raise ProcessingError(
                        "Empty values not allowed in skip rows specification"
                    )

                if "-" in part:
                    # Handle range format (e.g., "0-2")
                    range_parts = part.split("-")
                    if len(range_parts) != 2:
                        raise ProcessingError(f"Invalid range format: {part}")

                    try:
                        start = int(range_parts[0])
                        end = int(range_parts[1])

                        if start < 0 or end < 0:
                            raise ProcessingError(
                                f"Negative row indices not allowed: {part}"
                            )
                        if start > end:
                            raise ProcessingError(f"Invalid range order: {part}")

                        skip_indices.update(range(start, end + 1))
                    except ValueError as e:
                        raise ProcessingError(
                            f"Invalid range specification: {part}"
                        ) from e
                else:
                    # Handle single index
                    try:
                        index = int(part)
                        if index < 0:
                            raise ProcessingError(
                                f"Negative row index not allowed: {index}"
                            )
                        skip_indices.add(index)
                    except ValueError as e:
                        raise ProcessingError(f"Invalid row index: {part}") from e

            return sorted(list(skip_indices))

        except Exception as e:
            if self.enable_error_handling and self.error_handler:
                error_response = self.error_handler.create_error_response(e, context)
                raise ProcessingError(
                    f"Skip rows parsing failed: {error_response}"
                ) from e
            else:
                raise

    def _apply_skip_rows_to_dataframe(
        self, dataframe: pd.DataFrame, skip_rows_list: list[int], context: str
    ) -> pd.DataFrame:
        """Apply skip rows specification to remove specified rows from DataFrame.

        Args:
            dataframe: Original pandas DataFrame
            skip_rows_list: List of row indices to skip (0-based)
            context: Processing context for error reporting

        Returns:
            DataFrame with specified rows removed and reset index

        Raises:
            ProcessingError: If skip_rows are out of range
        """
        try:
            if not skip_rows_list:
                return dataframe

            # Validate skip rows are within DataFrame bounds
            max_df_rows = len(dataframe)
            invalid_rows = [idx for idx in skip_rows_list if idx >= max_df_rows]

            if invalid_rows:
                raise ProcessingError(
                    f"Skip row {invalid_rows[0]} is out of range (0-{max_df_rows - 1})"
                )

            # Create boolean mask for rows to keep (inverse of skip_rows)
            keep_mask = ~dataframe.index.isin(skip_rows_list)

            # Apply mask and reset index
            filtered_df = dataframe[keep_mask].reset_index(drop=True)

            return filtered_df

        except Exception as e:
            if self.enable_error_handling and self.error_handler:
                error_response = self.error_handler.create_error_response(e, context)
                raise ProcessingError(
                    f"DataFrame skip rows application failed: {error_response}"
                ) from e
            else:
                raise

    def _adjust_header_row_for_skip_rows(
        self, header_row: int, skip_rows_list: list[int], context: str
    ) -> int:
        """Adjust header_row index to account for skipped rows.

        Args:
            header_row: Original header row index (0-based)
            skip_rows_list: List of skipped row indices (0-based, sorted)
            context: Processing context for error reporting

        Returns:
            Adjusted header row index after skipping rows

        Raises:
            ProcessingError: If header_row is in skip_rows_list
        """
        try:
            if not skip_rows_list:
                return header_row

            # Check if header_row is being skipped
            if header_row in skip_rows_list:
                raise ProcessingError(f"Header row {header_row} cannot be skipped")

            # Count how many rows before header_row are being skipped
            skipped_before_header = sum(
                1 for skip_idx in skip_rows_list if skip_idx < header_row
            )

            # Adjust header_row index
            adjusted_header_row = header_row - skipped_before_header

            return adjusted_header_row

        except Exception as e:
            if self.enable_error_handling and self.error_handler:
                error_response = self.error_handler.create_error_response(e, context)
                raise ProcessingError(
                    f"Header row adjustment failed: {error_response}"
                ) from e
            else:
                raise

    def _get_components_info(self) -> Dict[str, str]:
        """Get information about pipeline components."""
        return {
            "excel_reader": type(self.excel_reader).__name__,
            "data_converter": type(self.data_converter).__name__,
            "range_parser": type(self.range_parser).__name__,
            "security_validator": type(self.security_validator).__name__
            if self.security_validator
            else None,
            "error_handler": type(self.error_handler).__name__
            if self.error_handler
            else None,
        }


class ProcessingError(Exception):
    """Exception raised during pipeline processing."""

    pass


class SecurityError(Exception):
    """Exception raised during security validation."""

    pass
