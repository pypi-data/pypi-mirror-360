====================================
sphinxcontrib-jsontable Examples
====================================

This page demonstrates how to use the .. jsontable:: directive.
It works in both ".rst" files and (if you have myst_parser enabled) ".md" files.

Performance Features Demo
==========================

This documentation demonstrates the new performance protection features 
introduced to handle large datasets safely.

**Configuration in this example:**

.. code-block:: python

   # In conf.py
   jsontable_max_rows = 5000  # Custom limit for demonstration

Sample Data Files
----------------------

We will use the following sample JSON files.

**``data/sample_users.json`` (array of objects)**:

.. literalinclude:: data/sample_users.json
   :language: json
   :caption: data/sample_users.json

**``data/sample_products.json`` (2D array)**:

.. literalinclude:: data/sample_products.json
   :language: json
   :caption: data/sample_products.json

Basic Usage Examples
====================

External File (Array of Objects)
-----------------------------------

| A table is generated from ``data/sample_users.json``.
| Because it's an array of objects, keys are used automatically as headers.
| Use the ``:header:`` option to display the header row.

.. jsontable:: data/sample_users.json
   :header:

| Use the ``:limit:`` option to limit the number of items displayed.

.. jsontable:: data/sample_users.json
   :header:
   :limit: 1

External File (2D Array + Header)
-------------------------------------

| Generate a table from ``data/sample_products.json``.
| When the first row is a header, use the ``:header:`` option.

.. jsontable:: data/sample_products.json
   :header:

Inline JSON (Array of Objects)
----------------------------------

You can also embed JSON directly in your document:

.. jsontable::

   [
       {"name": "Alice", "age": 30, "city": "New York"},
       {"name": "Bob", "age": 25, "city": "Los Angeles"},
       {"name": "Charlie", "age": 35, "city": "Chicago"}
   ]

Inline JSON (2D Array)
-----------------------

Simple 2D array without headers:

.. jsontable::

   [
       ["A1", "B1", "C1"],
       ["A2", "B2", "C2"],
       ["A3", "B3", "C3"]
   ]

Performance Protection Features
===============================

The following examples demonstrate the automatic performance protection 
features that prevent performance issues with large datasets.

Automatic Protection Example
-----------------------------

When no ``:limit:`` is specified, the extension automatically protects 
against large datasets using the configured ``jsontable_max_rows`` setting.

.. note::
   
   In this example configuration, we set ``jsontable_max_rows = 5000``.
   If a dataset has more than 5000 rows, it will be automatically limited
   with a warning message.

.. code-block:: rst

   .. jsontable:: data/large_dataset.json
      :header:
      
   # If the file has >5000 rows, you'll see a warning like:
   # "Large dataset detected (12,000 rows). Showing first 5,000 rows 
   # for performance. Use :limit: option to customize."

Explicit Limit Override
-----------------------

You can override the automatic protection with explicit limits:

**Small Custom Limit:**

.. jsontable:: data/sample_users.json
   :header:
   :limit: 2

**Unlimited Mode (use with caution):**

.. note::
   
   The ``:limit: 0`` option disables all row restrictions. Use carefully 
   for web deployment as it may impact performance with very large datasets.

.. code-block:: rst

   .. jsontable:: data/potentially_large_dataset.json
      :header:
      :limit: 0
      
   # This will show ALL rows regardless of size

Performance Best Practices
===========================

Configuration Recommendations
------------------------------

**For Different Environments:**

.. code-block:: python

   # Conservative (low-memory environments):
   jsontable_max_rows = 1000

   # Balanced (default - most use cases):
   jsontable_max_rows = 10000

   # Aggressive (high-memory environments):
   jsontable_max_rows = 50000

**For Different Use Cases:**

.. code-block:: python

   # Documentation with mostly small datasets:
   jsontable_max_rows = 100

   # Large data-heavy documentation:
   jsontable_max_rows = 25000

   # Complete control (disable automatic limits):
   jsontable_max_rows = None  # Not recommended for web deployment

Data Size Guidelines
--------------------

=============== ======================== =========================
Dataset Size    Recommended Approach     Example Configuration
=============== ======================== =========================
< 1,000 rows    No configuration needed  Default settings
1K-10K rows     Default protection       ``jsontable_max_rows = 10000``
> 10K rows      Explicit limits          Custom limits + ``:limit:``
> 100K rows     Consider preprocessing   Split files/database
=============== ======================== =========================

Troubleshooting Performance Warnings
=====================================

Common Warning Messages
------------------------

**"Large dataset detected":**

.. code-block:: text

   WARNING: Large dataset detected (25,000 rows). Showing first 5,000 rows 
   for performance. Use :limit: option to customize.

**Solutions:**

1. **Add explicit limit:** ``:limit: 50``
2. **Use unlimited mode:** ``:limit: 0`` (if really needed)
3. **Increase global limit:** ``jsontable_max_rows = 25000`` in conf.py
4. **Consider data preprocessing:** Split into smaller files

Example: Handling Large Dataset Warning
----------------------------------------

**Original directive causing warning:**

.. code-block:: rst

   .. jsontable:: data/huge_sales_data.json
      :header:
   
   # Produces warning if file has >5000 rows

**Solution 1 - Explicit small limit:**

.. code-block:: rst

   .. jsontable:: data/huge_sales_data.json
      :header:
      :limit: 100
   
   *Showing top 100 sales records. Download full data: 
   :download:`complete dataset <data/huge_sales_data.json>`*

**Solution 2 - Increase global limit:**

.. code-block:: python

   # In conf.py
   jsontable_max_rows = 25000  # Allow larger datasets

**Solution 3 - Unlimited (use carefully):**

.. code-block:: rst

   .. jsontable:: data/huge_sales_data.json
      :header:
      :limit: 0
   
   .. warning::
      This table displays all data regardless of size. 
      Performance may be impacted for very large datasets.

Migration from Previous Versions
=================================

**No Breaking Changes**

All existing documentation continues to work without modification:

.. code-block:: rst

   # This still works exactly as before
   .. jsontable:: data/my_data.json
      :header:
      :limit: 50

**New Features Available**

You can now benefit from automatic protection:

.. code-block:: rst

   # Before: Manual limit was required for large datasets
   .. jsontable:: large_data.json
      :header:
      :limit: 100

   # After: Automatic protection (manual limit still supported)
   .. jsontable:: large_data.json
      :header:
      # Automatically limited with warning if dataset is large

Advanced Configuration Examples
===============================

Multiple Environment Setup
---------------------------

.. code-block:: python

   # conf.py - Environment-specific configuration
   import os
   
   # Detect environment
   if os.getenv('SPHINX_ENV') == 'development':
       jsontable_max_rows = 100  # Fast builds during development
   elif os.getenv('SPHINX_ENV') == 'production':
       jsontable_max_rows = 10000  # Full functionality for users
   else:
       jsontable_max_rows = 5000  # Default for most cases

Conditional Configuration
-------------------------

.. code-block:: python

   # conf.py - Memory-based configuration
   import psutil
   
   # Adjust based on available memory
   memory_gb = psutil.virtual_memory().total / (1024**3)
   
   if memory_gb < 4:
       jsontable_max_rows = 1000    # Conservative for low-memory systems
   elif memory_gb < 8:
       jsontable_max_rows = 5000    # Moderate for typical systems
   else:
       jsontable_max_rows = 25000   # Aggressive for high-memory systems

More Examples
=============

For additional examples and advanced usage patterns, see the main 
`README documentation <../README.md>`_.

Documentation Features
======================

This examples documentation demonstrates:

- ✅ Basic directive usage
- ✅ Performance protection features  
- ✅ Configuration options
- ✅ Best practices and guidelines
- ✅ Troubleshooting common issues
- ✅ Migration guidance
- ✅ Advanced configuration patterns

For the complete feature set and detailed documentation, visit the 
`project repository <https://github.com/sasakama-code/sphinxcontrib-jsontable>`_.
