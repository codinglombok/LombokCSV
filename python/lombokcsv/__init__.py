"""LombokCSV - public API of the Python port."""

from lombokcsv.csv import (
    TYPE_SAMPLE_ROWS,
    CSV,
    CSVAggregator,
    CSVData,
    CSVError,
    CSVOptions,
    CSVParser,
    HTMLOptions,
    HTMLGenerator,
    AggregationOptions,
    DataType,
    detect_types,
    escape_html,
    is_boolean,
    is_date,
    is_number,
)

__version__ = "1.1.0"

__all__ = [
    "__version__",
    "TYPE_SAMPLE_ROWS",
    "AggregationOptions",
    "CSV",
    "CSVAggregator",
    "CSVData",
    "CSVError",
    "CSVOptions",
    "CSVParser",
    "DataType",
    "HTMLOptions",
    "HTMLGenerator",
    "detect_types",
    "escape_html",
    "is_boolean",
    "is_date",
    "is_number",
]
