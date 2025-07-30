# [Query.Farm](https://query.farm) SQL Scan Planning

A Python library for intelligent file filtering using SQL expressions and metadata-based scan planning. This library enables efficient data lake query optimization by determining which files need to be scanned based on their statistical metadata.

## Overview

This module provides predicate pushdown capabilities for file-based data storage systems. By maintaining metadata about file contents (min/max values, value sets, null presence), the library can quickly determine which files contain data that could satisfy a given `SQL WHERE` clause, significantly reducing query execution time.

## Features

- **SQL Expression Parsing**: Parse and evaluate complex `SQL WHERE` clauses using [SQLGlot](https://github.com/tobymao/sqlglot)
- **Metadata-Based Filtering**: Support for both range-based (min/max) and set-based field metadata
- **Null Handling**: Comprehensive support for `NULL` value semantics in SQL expressions
- **Complex Predicates**: Handle `AND`, `OR`, `XOR`, `NOT`, `IN`, `BETWEEN`, `CASE` statements, and more
- **Multiple Data Types**: Support for integers, floats, strings, decimals, and `NULL` values
- **Dialect Support**: Configurable SQL dialect support (default: DuckDB)

## Installation

```bash
pip install query-farm-sql-scan-planning
```

Or using rye:

```bash
rye add query-farm-sql-scan-planning
```

## Quick Start

```python
from query_farm_sql_scan_planning import Planner, RangeFieldInfo, SetFieldInfo

# Define file metadata
files = [
    (
        "data_2023_q1.parquet",
        {
            "sales_amount": RangeFieldInfo[int](
                min_value=100, max_value=50000,
                has_nulls=False, has_non_nulls=True
            ),
            "region": SetFieldInfo[str](
                values={"US", "CA", "MX"},
                has_nulls=False, has_non_nulls=True
            ),
        }
    ),
    (
        "data_2023_q2.parquet",
        {
            "sales_amount": RangeFieldInfo[int](
                min_value=200, max_value=75000,
                has_nulls=False, has_non_nulls=True
            ),
            "region": SetFieldInfo[str](
                values={"US", "EU", "UK"},
                has_nulls=False, has_non_nulls=True
            ),
        }
    ),
]

# Create planner
planner = Planner(files)

# Filter files based on SQL expressions
matching_files = planner.get_matching_files("sales_amount > 40000 AND region = 'US'")
print(matching_files)  # {'data_2023_q1.parquet', 'data_2023_q2.parquet'}

# More complex queries
matching_files = planner.get_matching_files("region IN ('EU', 'UK')")
print(matching_files)  # {'data_2023_q2.parquet'}
```

## Field Information Types

### `RangeFieldInfo`

For fields with known minimum and maximum values:

```python
RangeFieldInfo[int](
    min_value=0,
    max_value=100,
    has_nulls=False,      # Whether the field contains NULL values
    has_non_nulls=True    # Whether the field contains non-NULL values
)
```

### `SetFieldInfo`

For fields with a known set of possible values (useful for categorical data):

```python
SetFieldInfo[str](
    values={"apple", "banana", "cherry"},
    has_nulls=False,
    has_non_nulls=True
)
```

**Note**: `SetFieldInfo` can produce false positives - if a value is in the set, the file *might* contain it, but the file could contain additional values not in the set.

## Supported SQL Operations

### Comparison Operators
- `=`, `!=`, `<>` (equality and inequality)
- `<`, `<=`, `>`, `>=` (range comparisons)
- `IS NULL`, `IS NOT NULL` (null checks)
- `IS DISTINCT FROM`, `IS NOT DISTINCT FROM` (null-safe comparisons)

### Logical Operators
- `AND`, `OR`, `XOR` (logical connectors)
- `NOT` (negation)

### Set Operations
- `IN`, `NOT IN` (membership tests)
- `BETWEEN`, `NOT BETWEEN` (range tests)

### Control Flow
- `CASE WHEN ... THEN ... ELSE ... END` (conditional expressions)

### Literals
- Numeric literals: `123`, `45.67`
- String literals: `'hello'`
- Boolean literals: `TRUE`, `FALSE`
- NULL literal: `NULL`

## Examples

### Range Queries
```python
# Files with sales between 1000 and 5000
planner.get_matching_files("sales_amount BETWEEN 1000 AND 5000")

# Files with any sales over 10000
planner.get_matching_files("sales_amount > 10000")
```

### Set Membership
```python
# Files containing specific regions
planner.get_matching_files("region IN ('US', 'CA')")

# Files not containing specific regions
planner.get_matching_files("region NOT IN ('UNKNOWN', 'TEST')")
```

### Complex Conditions
```python
# Combination of range and set conditions
planner.get_matching_files(
    "sales_amount > 5000 AND region IN ('US', 'EU') AND customer_id IS NOT NULL"
)

# Case expressions
planner.get_matching_files(
    "CASE WHEN region = 'US' THEN sales_amount > 1000 ELSE sales_amount > 500 END"
)
```

### Null Handling
```python
# Files that might contain null values in sales_amount
planner.get_matching_files("sales_amount IS NULL")

# Files with non-null sales amounts over 1000
planner.get_matching_files("sales_amount IS NOT NULL AND sales_amount > 1000")
```

## Performance Considerations

- **Metadata Quality**: More accurate metadata (tighter ranges, complete value sets) leads to better filtering
- **Expression Complexity**: Simple expressions evaluate faster than complex nested conditions
- **False Positives**: The library errs on the side of including files that might match rather than risk excluding files that do match

## Use Cases

- **Data Lake Query Optimization**: Skip irrelevant files in distributed query engines
- **ETL Pipeline Optimization**: Process only files containing relevant data
- **Data Catalog Integration**: Enhance metadata catalogs with query planning capabilities
- **Columnar Storage**: Optimize scans of Parquet, ORC, or similar formats

## Development

### Setup
```bash
git clone https://github.com/query-farm/python-sql-scan-planning.git
cd python-sql-scan-planning
rye sync
```

### Running Tests
```bash
rye run pytest
```

### Code Quality
```bash
rye run ruff check
rye run pytest --mypy
```

## Dependencies

- **sqlglot**: SQL parsing and AST manipulation
- **Python 3.12+**: Required for modern type hints and pattern matching

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Author

This Python module was created by [Query.Farm](https://query.farm).

# License

MIT Licensed.
