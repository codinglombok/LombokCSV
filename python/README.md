# LombokCSV — Python port

Python implementation of the [LombokCSV](../../README.md) contract: RFC 4180 CSV parsing, column type detection, safe HTML tables, JSON export and GROUP BY aggregation. Zero runtime dependencies.

| Item | Value |
|---|---|
| Package | `lombokcsv` (PyPI) |
| Version | 1.1.0 |
| Contract | [SPEC](../../docs/SPEC_LombokCSV_v1.1.0.md) |
| Vectors | runs all 152 cases in [`vectors/lombokcsv-vectors-v1.json`](../../vectors/lombokcsv-vectors-v1.json) |
| Acceptance | every vector case passes with byte-identical results (GP-11) |
| Python | >= 3.9 |

## Installation

```bash
pip install lombokcsv
```

The package has not been published to PyPI yet; until then install from the repository root (`pip install ./python`).

## Quick start

```python
from lombokcsv import CSV, AggregationOptions

csv = CSV("Region,Product,Qty\nWest,Rice,120\nWest,Corn,80\nEast,Rice,95")

csv.get_headers()  # ['Region', 'Product', 'Qty']
csv.get_types()    # ['string', 'string', 'number']
csv.to_json()      # [{'Region': 'West', 'Product': 'Rice', 'Qty': '120'}, ...]
csv.to_html()

csv.aggregate(AggregationOptions(group_by="Region", sum=["Qty"], avg=["Qty"], count=True))
# [{'Region': 'West', 'Qty_sum': 200.0, 'Qty_avg': 100.0, 'count': 2},
#  {'Region': 'East', 'Qty_sum': 95.0, 'Qty_avg': 95.0, 'count': 1}]
```

The Python API mirrors the TypeScript reference with PEP 8 names: `toJSON` → `to_json`, `getHeaders` → `get_headers`, `className` → `class_name`, `hasHeader` → `has_header`. Behaviour, error codes (`INVALID_OPTION`, `UNKNOWN_COLUMN`) and the `[CODE] message` texts are identical across ports (SPEC section 7).

## Development

```bash
python -m pip install pytest coverage
python -m coverage run --branch --source=lombokcsv -m pytest -q
python -m coverage report -m --fail-under=90
```

Contributions are welcome; see [CONTRIBUTING.md](../../CONTRIBUTING.md).
