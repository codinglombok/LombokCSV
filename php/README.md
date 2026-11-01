# LombokCSV — PHP port

PHP implementation of the [LombokCSV](../../README.md) contract: RFC 4180 CSV parsing, column type detection, safe HTML tables, JSON export and GROUP BY aggregation. Zero dependencies (no Composer packages required at runtime).

| Item | Value |
|---|---|
| Package | `codinglombok/lombokcsv` (Packagist) |
| Version | 1.1.0 (Packagist picks the version up from the `v*` tag) |
| Contract | [SPEC](../../docs/SPEC_LombokCSV_v1.1.0.md) |
| Vectors | runs all 152 cases in [`vectors/lombokcsv-vectors-v1.json`](../../vectors/lombokcsv-vectors-v1.json) |
| Acceptance | every vector case passes with byte-identical results (GP-11) |
| PHP | >= 8.1 |

## Installation

```bash
composer require codinglombok/lombokcsv
```

The package is auto-synced to Packagist from `v*` tags; until the first tag install from source (`composer.json` sits at the repository root).

## Quick start

```php
<?php

use CodingLombok\LombokCSV\Csv;

$csv = new Csv("Region,Product,Qty\nWest,Rice,120\nWest,Corn,80\nEast,Rice,95");

$csv->getHeaders(); // ['Region', 'Product', 'Qty']
$csv->getTypes();   // ['string', 'string', 'number']
$csv->toJSON();     // [['Region' => 'West', 'Product' => 'Rice', 'Qty' => '120'], ...]
$csv->toHTML();

$csv->aggregate(['groupBy' => 'Region', 'sum' => ['Qty'], 'avg' => ['Qty'], 'count' => true]);
// [['Region' => 'West', 'Qty_sum' => 200.0, 'Qty_avg' => 100.0, 'count' => 2],
//  ['Region' => 'East', 'Qty_sum' => 95.0, 'Qty_avg' => 95.0, 'count' => 1]]
```

Errors are `CodingLombok\LombokCSV\CsvError` instances with a stable `errorCode` (`INVALID_OPTION`, `UNKNOWN_COLUMN`) and the canonical `[CODE] message` text; match on `errorCode`, not on the message (SPEC section 7).

## Development

The test runner has no Composer dependency of its own (a PSR-4 autoloader is built in):

```bash
php php/tests/run.php                 # api + vectors
php php/tests/run.php --coverage=90   # with pcov loaded (CI does this)
for f in $(find php/src php/tests -name '*.php'); do php -l "$f" > /dev/null || exit 1; done
```

Contributions are welcome; see [CONTRIBUTING.md](../../CONTRIBUTING.md).
