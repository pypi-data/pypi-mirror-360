# sphinxcontrib-jsontable

[![Tests](https://github.com/sasakama-code/sphinxcontrib-jsontable/actions/workflows/ci.yml/badge.svg)](https://github.com/sasakama-code/sphinxcontrib-jsontable/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/sasakama-code/sphinxcontrib-jsontable/graph/badge.svg)](https://codecov.io/gh/sasakama-code/sphinxcontrib-jsontable)
[![Python](https://img.shields.io/pypi/pyversions/sphinxcontrib-jsontable.svg)](https://pypi.org/project/sphinxcontrib-jsontable/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/sasakama-code/sphinxcontrib-jsontable)

**Languages:** [English](README.md) | [日本語](README_ja.md)

A powerful Sphinx extension that renders **JSON and Excel data** (from files or inline content) as beautifully formatted reStructuredText tables. Perfect for documentation that needs to display structured data, API examples, configuration references, and data-driven content.

✨ **Complete Excel Support**: Render Excel files (.xlsx/.xls) with 36+ advanced processing methods including sheet selection, range specification, merged cell processing, automatic range detection, hierarchical headers, and performance caching.

## Background / Motivation

In recent years, there has been an increasing trend of using documents as data sources for Retrieval Augmented Generation (RAG). However, tabular data within documents often loses its structural relevance during the process of being ingested by RAG systems. This presented a challenge where the original value of the structured data could not be fully leveraged.

Against this backdrop, sphinxcontrib-jsontable was developed to directly embed structured data, such as JSON, as meaningful tables in Sphinx-generated documents, with the objective to ensure that readability and the data's value as a source effectively coexist.

## Features

✨ **Flexible Data Sources**
* Load JSON from files within your Sphinx project
* **Load Excel files (.xlsx/.xls) directly with advanced processing**
* Embed JSON directly inline in your documentation
* Support for relative file paths with safe path resolution

📊 **Multiple Data Formats**
* JSON objects (single or arrays)
* 2D arrays with optional headers
* **Excel spreadsheets with complex structures**
* Mixed data types with automatic string conversion
* Nested data structures (flattened appropriately)

📋 **Excel-Specific Features**
* **Sheet Selection**: Target specific sheets by name or index
* **Range Specification**: Extract data from specific cell ranges (A1:D10)
* **Smart Header Detection**: Automatic header row identification
* **Merged Cell Processing**: Handle merged cells with various strategies
* **Row Skipping**: Skip unwanted rows with flexible patterns
* **Auto Range Detection**: Intelligent data boundary detection
* **JSON Caching**: Cache converted data for improved performance

🎛️ **Customizable Output**
* Optional header rows with automatic key extraction
* Row limiting for large datasets
* Custom file encoding support
* Responsive table formatting

🔒 **Robust & Safe**
* Path traversal protection
* Comprehensive error handling
* Encoding validation
* Detailed logging for debugging

⚡ **Performance Optimized**
* Automatic row limiting for large datasets (10,000 rows by default)
* Configurable performance limits
* Memory-safe processing
* User-friendly warnings for large data

## Installation

### Using UV (Recommended)

**UV Installation:**
```bash
# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# For new projects
uv init my-sphinx-project
cd my-sphinx-project
uv add sphinxcontrib-jsontable

# With Excel support
uv add "sphinxcontrib-jsontable[excel]"
```

**Development Environment:**
```bash
# Clone and setup development environment
git clone https://github.com/sasakama-code/sphinxcontrib-jsontable.git
cd sphinxcontrib-jsontable
uv sync
uv run pytest
```

### From PyPI

**Basic Installation (JSON support only):**
```bash
pip install sphinxcontrib-jsontable
```

**With Excel Support:**
```bash
pip install sphinxcontrib-jsontable[excel]
```

**Complete Installation (all features):**
```bash
pip install sphinxcontrib-jsontable[all]
```

### From Source
```bash
git clone https://github.com/sasakama-code/sphinxcontrib-jsontable.git
cd sphinxcontrib-jsontable
pip install -e .[excel]  # With Excel support
```

### Dependencies

**Core:** Python 3.10+, Sphinx 3.0+, docutils 0.18+

**Excel Support:** pandas 2.0+, openpyxl 3.1+

## Quick Start

### 1. Enable the Extension

Add to your `conf.py`:

```python
extensions = [
    # ... your other extensions
    'sphinxcontrib.jsontable',
]

# Optional: Configure performance limits
jsontable_max_rows = 5000  # Default: 10000
```

### 2. Create Sample Data

Create `data/users.json`:
```json
[
  {
    "id": 1,
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "department": "Engineering",
    "active": true
  },
  {
    "id": 2,
    "name": "Bob Smith",
    "email": "bob@example.com", 
    "department": "Marketing",
    "active": false
  }
]
```

### 3. Add to Your Documentation

**JSON Example in reStructuredText (.rst):**
```rst
User Database
=============

.. jsontable:: data/users.json
   :header:
   :limit: 10
```

**Excel Example in reStructuredText (.rst):**
```rst
Sales Data Analysis
==================

.. jsontable:: data/sales_report.xlsx
   :header:
   :sheet: "Q1 Data"
   :range: A1:E50
   :skip-rows: 2,4
   :merge-cells: expand
   :json-cache:
```

**Advanced Excel Processing:**
```rst
Financial Report
===============

.. jsontable:: reports/financial.xlsx
   :sheet-index: 1
   :header-row: 2
   :detect-range: auto
   :merge-headers: 
   :limit: 100
```

**In Markdown (with myst-parser):**
````markdown
# User Database

```{jsontable} data/users.json
:header:
:limit: 10
```

# Excel Sales Data

```{jsontable} data/quarterly_sales.xlsx
:header:
:sheet: Summary
:header-row: 2
```
````

### 4. Build Your Documentation

```bash
sphinx-build -b html docs/ build/html/
```

## Excel Support Guide

### Excel File Processing

sphinxcontrib-jsontable provides comprehensive Excel file support with advanced features for handling complex spreadsheet structures.

#### Basic Excel Usage

```rst
.. jsontable:: data/employees.xlsx
   :header:
```

#### Sheet Selection

**By Sheet Name:**
```rst
.. jsontable:: data/financial_report.xlsx
   :header:
   :sheet: Quarterly Results
```

**By Sheet Index (0-based):**
```rst
.. jsontable:: data/financial_report.xlsx
   :header:
   :sheet-index: 2
```

#### Range Specification

**Specific Cell Range:**
```rst
.. jsontable:: data/large_dataset.xlsx
   :header:
   :range: A1:F25
```

**Starting from Specific Cell:**
```rst
.. jsontable:: data/data_with_headers.xlsx
   :header:
   :range: B3:H50
```

#### Advanced Header Configuration

**Custom Header Row:**
```rst
.. jsontable:: data/complex_report.xlsx
   :header:
   :header-row: 3
```

**Skip Unwanted Rows:**
```rst
.. jsontable:: data/messy_data.xlsx
   :header:
   :skip-rows: 0-2,5,7-9
```

#### Merged Cell Processing

**Expand Merged Cells:**
```rst
.. jsontable:: data/formatted_report.xlsx
   :header:
   :merge-cells: expand
```

**Ignore Merged Cells:**
```rst
.. jsontable:: data/formatted_report.xlsx
   :header:
   :merge-cells: ignore
```

#### Automatic Range Detection

**Smart Data Detection:**
```rst
.. jsontable:: data/unstructured.xlsx
   :header:
   :detect-range: auto
```

**Manual Override:**
```rst
.. jsontable:: data/complex_layout.xlsx
   :header:
   :detect-range: manual
   :range: C5:J30
```

#### Performance Optimization

**Enable JSON Caching:**
```rst
.. jsontable:: data/large_workbook.xlsx
   :header:
   :json-cache:
```

### Excel Options Reference

| Option | Type | Description | Example |
|--------|------|-------------|---------|
| `sheet` | string | Sheet name to read | `:sheet: Sales Data` |
| `sheet-index` | int | Sheet index (0-based) | `:sheet-index: 1` |
| `range` | string | Cell range (A1:D10) | `:range: B2:F20` |
| `header-row` | int | Header row number (0-based) | `:header-row: 2` |
| `skip-rows` | string | Rows to skip | `:skip-rows: 0-2,5,7-9` |
| `detect-range` | string | Auto detection mode | `:detect-range: auto` |
| `merge-cells` | string | Merged cell handling | `:merge-cells: expand` |
| `merge-headers` | string | Multi-row header merging | `:merge-headers: true` |
| `json-cache` | flag | Enable caching | `:json-cache:` |
| `auto-header` | flag | Auto header detection | `:auto-header:` |

### Complete Directive Options

The `jsontable` directive supports all these options for maximum flexibility:

```rst
.. jsontable:: data.xlsx
   :header:              # Include header row
   :encoding: utf-8      # File encoding specification  
   :limit: 1000          # Row limit for display
   :sheet: "Data Sheet"  # Sheet name selection
   :sheet-index: 0       # Sheet index selection (0-based)
   :range: A1:E50        # Cell range (Excel format)
   :header-row: 1        # Header row number (0-based)
   :skip-rows: 2,4,6-10  # Skip specific rows
   :detect-range: auto   # Auto-detect data range (auto/smart/manual)
   :auto-header:         # Automatic header detection
   :merge-cells: expand  # Merged cell processing (expand/ignore/first-value)
   :merge-headers:       # Hierarchical header merging
   :json-cache:          # Enable JSON caching for performance
```

## Comprehensive Usage Guide

### Data Format Support

#### Array of Objects (Most Common)

Perfect for database records, API responses, configuration lists:

```json
[
  {"name": "Redis", "port": 6379, "ssl": false},
  {"name": "PostgreSQL", "port": 5432, "ssl": true},
  {"name": "MongoDB", "port": 27017, "ssl": true}
]
```

```rst
.. jsontable:: data/services.json
   :header:
```

**Output:** Automatically generates headers from object keys (name, port, ssl).

#### 2D Arrays with Headers

Great for CSV-like data, reports, matrices:

```json
[
  ["Service", "Port", "Protocol", "Status"],
  ["HTTP", 80, "TCP", "Active"],
  ["HTTPS", 443, "TCP", "Active"],
  ["SSH", 22, "TCP", "Inactive"]
]
```

```rst
.. jsontable:: data/ports.json
   :header:
```

**Output:** First row becomes the table header.

#### 2D Arrays without Headers

Simple tabular data:

```json
[
  ["Monday", "Sunny", "75°F"],
  ["Tuesday", "Cloudy", "68°F"],
  ["Wednesday", "Rainy", "62°F"]
]
```

```rst
.. jsontable:: data/weather.json
```

**Output:** All rows treated as data (no headers).

#### Single Object

Configuration objects, settings, metadata:

```json
{
  "database_host": "localhost",
  "database_port": 5432,
  "debug_mode": true,
  "max_connections": 100
}
```

```rst
.. jsontable:: data/config.json
   :header:
```

**Output:** Keys become one column, values become another.

### Directive Options Reference

| Option | Type | Default | Description | Example |
|--------|------|---------|-------------|---------|
| `header` | flag | off | Include first row as table header | `:header:` |
| `encoding` | string | `utf-8` | File encoding for JSON files | `:encoding: utf-16` |
| `limit` | positive int/0 | automatic | Maximum rows to display (0 = unlimited) | `:limit: 50` |

## Configuration Options

Configure sphinxcontrib-jsontable in your `conf.py`:

### Performance Settings

```python
# Maximum rows before automatic limiting kicks in (default: 10000)
jsontable_max_rows = 5000

# Example configurations for different use cases:

# For documentation with mostly small datasets
jsontable_max_rows = 100

# For large data-heavy documentation
jsontable_max_rows = 50000

# Disable automatic limiting entirely (not recommended for web deployment)
# jsontable_max_rows = None  # Will use unlimited by default
```

### Advanced Examples

#### Automatic Performance Protection

When no `:limit:` is specified, the extension automatically protects against large datasets:

```rst
.. jsontable:: data/huge_dataset.json
   :header:

# If dataset > 10,000 rows, automatically shows first 10,000 with warning
# User sees: "Large dataset detected (25,000 rows). Showing first 10,000 
# rows for performance. Use :limit: option to customize."
```

#### Explicit Unlimited Processing

For cases where you need to display all data regardless of size:

```rst
.. jsontable:: data/large_but_manageable.json
   :header:
   :limit: 0

# ⚠️ Shows ALL rows - use with caution for web deployment
```

#### Large Dataset with Pagination

For performance and readability with large datasets:

```rst
.. jsontable:: data/large_dataset.json
   :header:
   :limit: 100

.. note::
   This table shows the first 100 entries out of 50,000+ total records. 
   Download the complete dataset: :download:`large_dataset.json <data/large_dataset.json>`
```

#### Non-UTF8 Encoding

Working with legacy systems or specific character encodings:

```rst
.. jsontable:: data/legacy_data.json
   :encoding: iso-8859-1
   :header:
```

#### Inline JSON for Examples

Perfect for API documentation, examples, tutorials:

```rst
API Response Format
==================

The user endpoint returns data in this format:

.. jsontable::

   {
     "user_id": 12345,
     "username": "john_doe",
     "email": "john@example.com",
     "created_at": "2024-01-15T10:30:00Z",
     "is_verified": true,
     "profile": {
       "first_name": "John",
       "last_name": "Doe",
       "avatar_url": "https://example.com/avatar.jpg"
     }
   }
```

#### Complex Nested Data

For nested JSON, the extension flattens appropriately:

```rst
.. jsontable::

   [
     {
       "id": 1,
       "name": "Product A",
       "category": {"name": "Electronics", "id": 10},
       "tags": ["popular", "sale"],
       "price": 99.99
     }
   ]
```

**Note:** Objects and arrays in values are converted to string representations.

### Integration Examples

#### With Sphinx Tabs

Combine with sphinx-tabs for multi-format documentation:

```rst
.. tabs::

   .. tab:: JSON Data

      .. jsontable:: data/api_response.json
         :header:

   .. tab:: Raw JSON

      .. literalinclude:: data/api_response.json
         :language: json
```

#### With Code Blocks

Document API endpoints with request/response examples:

```rst
Get Users Endpoint
==================

**Request:**

.. code-block:: http

   GET /api/v1/users HTTP/1.1
   Host: api.example.com
   Authorization: Bearer <token>

**Response:**

.. jsontable::

   [
     {
       "id": 1,
       "username": "alice",
       "email": "alice@example.com",
       "status": "active"
     },
     {
       "id": 2, 
       "username": "bob",
       "email": "bob@example.com",
       "status": "inactive"
     }
   ]
```

#### In MyST Markdown

Full MyST Markdown support for modern documentation workflows:

````markdown
# Configuration Reference

## Database Settings

```{jsontable} config/database.json
:header:
:encoding: utf-8
```

## Feature Flags

```{jsontable}
[
  {"feature": "dark_mode", "enabled": true, "rollout": "100%"},
  {"feature": "new_dashboard", "enabled": false, "rollout": "0%"},
  {"feature": "advanced_search", "enabled": true, "rollout": "50%"}
]
```
````

### File Organization Best Practices

#### Recommended Directory Structure

```
docs/
├── conf.py
├── index.rst
├── data/
│   ├── users.json
│   ├── products.json
│   ├── config/
│   │   ├── database.json
│   │   └── features.json
│   └── examples/
│       ├── api_responses.json
│       └── error_codes.json
└── api/
    └── endpoints.rst
```

#### Naming Conventions

- Use descriptive filenames: `user_permissions.json` not `data1.json`
- Group related data in subdirectories: `config/`, `examples/`, `test_data/`
- Include version or date when appropriate: `api_v2_responses.json`

### Performance Considerations

#### Automatic Protection for Large Datasets

The extension automatically protects against performance issues:

- **Default Limit**: 10,000 rows maximum by default
- **Smart Detection**: Automatically estimates dataset size
- **User Warnings**: Clear messages when limits are applied
- **Configurable**: Adjust limits via `jsontable_max_rows` setting

#### Performance Behavior

| Dataset Size | Default Behavior | User Action Required |
|--------------|------------------|---------------------|
| ≤ 10,000 rows | ✅ Display all rows | None |
| > 10,000 rows | ⚠️ Auto-limit + warning | Use `:limit:` to customize |
| Any size with `:limit: 0` | 🚨 Display all (unlimited) | Use with caution |

#### Build Time Optimization

**Small Datasets (< 1,000 rows):**
```rst
.. jsontable:: data/small_dataset.json
   :header:
   # No limit needed - processes quickly
```

**Medium Datasets (1,000-10,000 rows):**
```rst
.. jsontable:: data/medium_dataset.json
   :header:
   # Automatic protection applies - good performance
```

**Large Datasets (> 10,000 rows):**
```rst
.. jsontable:: data/large_dataset.json
   :header:
   :limit: 100
   # Explicit limit recommended for predictable performance
```

#### Memory Considerations

**Safe Configurations:**
```python
# Conservative (good for low-memory environments)
jsontable_max_rows = 1000

# Balanced (default - good for most use cases)
jsontable_max_rows = 10000

# Aggressive (high-memory environments only)
jsontable_max_rows = 100000
```

**Memory Usage Guidelines:**
- **~1MB JSON**: ~1,000-5,000 rows (safe for all environments)
- **~10MB JSON**: ~10,000-50,000 rows (requires adequate memory)
- **>50MB JSON**: Consider data preprocessing or database solutions

#### Best Practices for Large Data

1. **Use Appropriate Limits**:
   ```rst
   .. jsontable:: data/sales_data.json
      :header:
      :limit: 50
      
   *Showing top 50 sales records. Full data available in source file.*
   ```

2. **Consider Data Preprocessing**:
   - Split large files into logical chunks
   - Create summary datasets for documentation
   - Use database views instead of static files

3. **Optimize for Build Performance**:
   ```python
   # In conf.py - faster builds for large projects
   jsontable_max_rows = 100
   ```

4. **Provide Context for Limited Data**:
   ```rst
   .. jsontable:: data/user_activity.json
      :header:
      :limit: 20
      
   .. note::
      This table shows recent activity only. For complete logs, 
      see the :doc:`admin-dashboard` or download the 
      :download:`full dataset <data/user_activity.json>`.
   ```

### Migration Guide

#### Upgrading from Previous Versions

**No Breaking Changes**: Existing documentation continues to work unchanged.

**New Features Available**:
```rst
# Before: Manual limit required for large datasets
.. jsontable:: large_data.json
   :header:
   :limit: 100

# After: Automatic protection (manual limit still supported)
.. jsontable:: large_data.json
   :header:
   # Automatically limited to 10,000 rows with user warning
```

**Recommended Configuration Update**:
```python
# Add to conf.py for customized behavior
jsontable_max_rows = 5000  # Adjust based on your needs
```

## ⚠️ Breaking Changes Notice

### ExcelDataLoader Removal (v0.4.0) - **COMPLETED**

**Important:** `ExcelDataLoader` class has been **completely removed** in **v0.4.0** as announced in the deprecation timeline. All Excel processing functionality now uses the modern, component-based architecture for significantly better performance and maintainability.

#### Migration Required - **IMMEDIATE ACTION NEEDED**

If you are directly importing `ExcelDataLoader` in your code, you **must** update to the new API:

```python
# ❌ REMOVED in v0.4.0 - Will cause ImportError
from sphinxcontrib.jsontable.excel_data_loader import ExcelDataLoader

# ✅ Required in v0.4.0+ - Use this instead
from sphinxcontrib.jsontable.facade.excel_data_loader_facade import ExcelDataLoaderFacade
```

#### Benefits of Migration

- **40% Performance Improvement**: Modern modular architecture with 9 specialized components
- **25% Memory Reduction**: Optimized processing pipeline with streaming support
- **Enhanced Type Safety**: Comprehensive type annotations and interfaces
- **Improved Security**: Advanced validation and error handling
- **Future-Ready**: Async-ready foundation and modern Python patterns

#### Migration Timeline - **COMPLETED**

- **v0.3.1**: Deprecation warnings added, both APIs worked
- **v0.4.0** (**Current**): `ExcelDataLoader` completely removed, `ExcelDataLoaderFacade` only
- **v0.4.1+**: Full modern API stabilization ongoing

#### Migration Support

See our comprehensive [MIGRATION.md](MIGRATION.md) guide featuring:
- **Step-by-step migration instructions** with code examples
- **Performance comparison charts** showing quantified improvements
- **Complete API mapping** from old to new methods
- **Troubleshooting guide** for common migration issues
- **Automated migration tools** for faster conversion

#### Quick Migration Example

```python
# OLD (v0.3.x) - Causes ImportError in v0.4.0
from sphinxcontrib.jsontable.excel_data_loader import ExcelDataLoader
loader = ExcelDataLoader(base_path="./data", macro_security="strict")
result = loader.load_from_excel_with_range("file.xlsx", "A1:C10")

# NEW (v0.4.0+) - Required implementation
from sphinxcontrib.jsontable.facade.excel_data_loader_facade import ExcelDataLoaderFacade
from sphinxcontrib.jsontable.security.security_scanner import SecurityScanner

security_scanner = SecurityScanner(macro_security="strict")
facade = ExcelDataLoaderFacade(security_validator=security_scanner)
result = facade.load_from_excel("./data/file.xlsx", range_spec="A1:C10")
```

#### Directive Usage Unchanged

**Important**: The `jsontable` directive usage remains **completely unchanged**. This breaking change only affects direct Python API usage:

```rst
# This continues to work exactly the same in v0.4.0
.. jsontable:: data.xlsx
   :header:
   :sheet: "Data"
   :range: A1:E50
```

**📝 Migration Help**: For assistance with migration, please use our [GitHub Discussions](https://github.com/sasakama-code/sphinxcontrib-jsontable/discussions) with the "migration" tag.

### Troubleshooting

#### Common Issues

**Error: "No JSON data source provided"**
```rst
# ❌ Missing file path or content
.. jsontable::

# ✅ Provide file path or inline content  
.. jsontable:: data/example.json
```

**Error: "JSON file not found"**
- Check file path relative to source directory
- Verify file exists and has correct permissions
- Ensure no typos in filename

**Error: "Invalid inline JSON"**
- Validate JSON syntax using online validator
- Check for trailing commas, unquoted keys
- Ensure proper escaping of special characters

**Excel-Specific Errors:**

**Error: "Excel file not found"**
```rst
# ❌ Incorrect path
.. jsontable:: data/missing_file.xlsx

# ✅ Correct path and file exists
.. jsontable:: data/actual_file.xlsx
```

**Error: "Invalid Excel file format"**
- Ensure file has .xlsx or .xls extension
- Verify file is not corrupted
- Check if file is actually an Excel file (not renamed CSV)

**Error: "Sheet not found"**
```rst
# ❌ Non-existent sheet name
.. jsontable:: data/report.xlsx
   :sheet: NonExistentSheet

# ✅ Valid sheet name or index
.. jsontable:: data/report.xlsx
   :sheet: Sheet1
```

**Error: "Invalid range specification"**
```rst
# ❌ Invalid range format
.. jsontable:: data/report.xlsx
   :range: Z99:AA1000

# ✅ Valid range format
.. jsontable:: data/report.xlsx
   :range: A1:F25
```

**Error: "No data found in specified range"**
- Check if the specified range contains data
- Verify range coordinates are within sheet bounds
- Ensure range specification format is correct (A1:D10)

**Performance Warnings**
```
WARNING: Large dataset detected (25,000 rows). Showing first 10,000 rows for performance.
```
**Solutions:**
- Add explicit `:limit:` option: `:limit: 50`
- Use `:limit: 0` for unlimited (if needed)
- Increase global limit: `jsontable_max_rows = 25000`
- Consider data preprocessing for smaller files

**Encoding Issues**
```rst
# For non-UTF8 files
.. jsontable:: data/legacy.json
   :encoding: iso-8859-1
```

**Empty Tables**
- Check if JSON file is empty or null
- Verify JSON structure (must be array or object)
- Check if automatic limiting is hiding your data

#### Debug Mode

Enable detailed logging in `conf.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# For sphinx-specific logs
extensions = ['sphinxcontrib.jsontable']

# Performance monitoring
jsontable_max_rows = 1000  # Lower limit for debugging
```

#### Testing Configuration

Create a simple test file to verify setup:

```json
[{"test": "success", "status": "ok"}]
```

```rst
.. jsontable:: test.json
   :header:
```

### Security Considerations

#### Path Traversal Protection

The extension automatically prevents directory traversal attacks:

```rst
# ❌ This will be blocked
.. jsontable:: ../../etc/passwd

# ✅ Safe relative paths only
.. jsontable:: data/safe_file.json
```

#### File Access

- Only files within the Sphinx source directory are accessible
- No network URLs or absolute system paths allowed
- File permissions respected by the system

#### Performance Security

- Default limits prevent accidental resource exhaustion
- Memory usage is bounded by configurable limits
- Large dataset warnings help prevent unintentional performance impact

### Migration Guide

#### From Other Extensions

**From sphinx-jsonschema:**
- Replace `.. jsonschema::` with `.. jsontable::`
- Remove schema validation options
- Add `:header:` option if needed

**From Custom Solutions:**
- Export your data to JSON format
- Replace custom table generation with `.. jsontable::`
- Update file paths to be relative to source directory

#### Version Compatibility

- **Sphinx:** 3.0+ (recommended: 4.0+)
- **Python:** 3.10+ (recommended: 3.11+)
- **Docutils:** 0.14+

## Developer Documentation

### Architecture Overview

sphinxcontrib-jsontable follows a modular, layered architecture designed for extensibility and maintainability:

```
┌─────────────────────────────────────────────────────────────┐
│                    Sphinx Integration                       │
├─────────────────────────────────────────────────────────────┤
│              JsonTableDirective (Main Entry)                │
├─────────────────────┬───────────────────────────────────────┤
│   JsonDataLoader    │        ExcelDataLoader               │
│   (JSON Support)    │        (Excel Support)               │
├─────────────────────┴───────────────────────────────────────┤
│                   TableConverter                            │
│              (Format-agnostic Processing)                   │
├─────────────────────────────────────────────────────────────┤
│                    TableBuilder                             │
│                (Docutils Integration)                       │
└─────────────────────────────────────────────────────────────┘
```

### API Reference

#### Core Classes

**`JsonTableDirective`** (`sphinxcontrib/jsontable/directives.py:596`)
- Main Sphinx directive class
- Handles option parsing and execution  
- Coordinates data loading, conversion, and rendering
- **Options**: 13 total options including Excel-specific features

**`JsonDataLoader`** (`sphinxcontrib/jsontable/directives.py:112`)
- Loads JSON from files or inline content
- Validates encoding and file paths
- Provides secure file access with path traversal protection

**`ExcelDataLoader`** (`sphinxcontrib/jsontable/excel_data_loader.py`)
- Comprehensive Excel file processing
- **Methods**: `load_from_excel()`, `validate_excel_file()`, `header_detection()`
- **Features**: Sheet selection, range specification, merged cell handling
- **Error Handling**: Enhanced error classes with multilingual support

**`TableConverter`** (`sphinxcontrib/jsontable/directives.py:204`)
- Transforms JSON/Excel data into 2D table format
- Handles different data formats (objects, arrays, mixed)
- Manages header extraction and row limiting
- Applies automatic performance limits (10,000 rows default)

**`TableBuilder`** (`sphinxcontrib/jsontable/directives.py:403`)
- Generates Docutils table nodes for Sphinx rendering
- Creates proper table structure with headers/body
- Handles cell formatting and padding

#### Excel-Specific Classes

**Enhanced Error Classes** (`excel_data_loader.py:29-143`)
```python
class EnhancedExcelError(Exception):
    """Base class for enhanced Excel errors with multilingual support"""
    
class ExcelFileNotFoundError(EnhancedExcelError):
    """Excel file not found with recovery suggestions"""
    
class ExcelFileFormatError(EnhancedExcelError):
    """Invalid Excel format with user-friendly guidance"""
```

#### Option Specification

```python
option_spec = {
    # Core options
    "header": directives.flag,
    "encoding": directives.unchanged,
    "limit": directives.nonnegative_int,
    
    # Excel-specific options  
    "sheet": directives.unchanged,
    "sheet-index": directives.nonnegative_int,
    "range": directives.unchanged,
    "header-row": directives.nonnegative_int,
    "skip-rows": directives.unchanged,
    "detect-range": directives.unchanged,
    "auto-header": directives.flag,
    "merge-cells": directives.unchanged,
    "merge-headers": directives.unchanged,
    "json-cache": directives.flag,
}
```

### Extension Development

#### Adding New Data Sources

To add support for new data formats, follow this pattern:

1. **Create a Data Loader Class**:
```python
class NewFormatDataLoader:
    def __init__(self, source_dir: str):
        self.source_dir = source_dir
        
    def load_from_format(self, file_path: str, **options) -> dict:
        """Load and convert to JSON-compatible format"""
        # Implementation here
        return {"data": converted_data, "headers": headers}
```

2. **Update JsonTableDirective**:
```python
def run(self) -> list[nodes.Node]:
    # Add format detection
    if file_path.endswith('.newformat'):
        loader = NewFormatDataLoader(self.env.srcdir)
        result = loader.load_from_format(file_path, **options)
```

3. **Add Option Specifications**:
```python
option_spec["new-option"] = directives.unchanged
```

#### Performance Considerations

**Memory Management**:
- Large datasets are automatically limited (configurable)
- Streaming processing for Excel files
- JSON caching for improved rebuild performance

**Security Features**:
- Path traversal protection via `is_safe_path()`
- File access restricted to source directory
- Input validation for all options

#### Error Handling

All errors inherit from domain-specific base classes:
- `JsonTableError`: Base error class
- `EnhancedExcelError`: Excel-specific enhanced errors
- File access errors with recovery suggestions
- Input validation errors with user guidance

### Testing Framework

**Test Organization**:
```
tests/
├── excel/              # Excel-specific tests (18 files)
├── unit/               # Core component unit tests  
├── integration/        # Cross-component integration tests
├── performance/        # Performance and benchmark tests
└── coverage/           # Coverage-specific tests
```

**Test Execution**:
```bash
# Standard test execution
uv run python -m pytest

# Excel-specific tests
uv run python -m pytest tests/excel/

# Performance tests
uv run python -m pytest --benchmark-only
```

### Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Code style guidelines
- Testing procedures
- Pull request process

#### Development Setup

```bash
git clone https://github.com/sasakama-code/sphinxcontrib-jsontable.git
cd sphinxcontrib-jsontable
pip install -e ".[dev]"
pytest
```

#### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=sphinxcontrib.jsontable

# Run specific test
pytest tests/test_directives.py::test_json_table_basic
```

### Examples Repository

See the [`examples/`](examples/) directory for:
- Complete Sphinx project setup
- Various data format examples  
- Integration with other extensions
- Advanced configuration examples

```bash
cd examples/
sphinx-build -b html . _build/html/
```

### Development Tools

The [`scripts/`](scripts/) directory contains development and analysis tools used during the creation of performance features:

- **`performance_benchmark.py`** - Performance measurement and analysis tool
- **`memory_analysis.py`** - Memory usage analysis for different dataset sizes
- **`competitive_analysis.py`** - Industry standard research and best practices
- **`validate_ci_tests.py`** - CI environment testing and validation
- **`test_integration.py`** - Comprehensive integration testing

These tools were instrumental in establishing the scientific foundation for performance limits and ensuring enterprise-grade reliability. They can be used for ongoing performance monitoring and analysis.

```bash
# Run performance analysis
python scripts/performance_benchmark.py

# Validate CI environment
python scripts/validate_ci_tests.py
```

### Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and release notes.

### License

This project is licensed under the [MIT License](LICENSE).

### Support

- **Documentation:** [GitHub Pages](https://sasakama-code.github.io/sphinxcontrib-jsontable/)
- **Issues:** [GitHub Issues](https://github.com/sasakama-code/sphinxcontrib-jsontable/issues)
- **Discussions:** [GitHub Discussions](https://github.com/sasakama-code/sphinxcontrib-jsontable/discussions)
