# LombokCSV

> CSV parsing that gives the same results in TypeScript, Python, Go, and PHP: an RFC 4180 parser, column type detection, safe HTML tables, JSON export, and GROUP BY aggregation. Zero runtime dependencies.

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![CI](https://github.com/codinglombok/LombokCSV/actions/workflows/ci.yml/badge.svg)](https://github.com/codinglombok/LombokCSV/actions/workflows/ci.yml)
[![npm](https://img.shields.io/npm/v/lombokcsv.svg)](https://www.npmjs.com/package/lombokcsv)
[![PyPI](https://img.shields.io/pypi/v/lombokcsv.svg)](https://pypi.org/project/lombokcsv/)
[![Vectors](https://img.shields.io/badge/shared%20vectors-152%20byte--identical-success)](vectors/)
[![Lombok Ecosystem](https://img.shields.io/badge/Lombok-Ecosystem-2e7d5b?logo=github)](https://github.com/codinglombok)

Part of the [Lombok Ecosystem](https://github.com/codinglombok).

## Mengapa library ini? (Why this library?)

- **Identical results in every language.** CSV parsing looks easy until the edge cases: doubled quotes, commas inside quotes, CRLF line endings, BOMs, unterminated quotes. LombokCSV writes the behaviour down as a normative specification ([SPEC](docs/SPEC_LombokCSV_v1.1.0.md)) and pins it with 152 shared test vectors, so the TypeScript app, the Python batch job, the Go service, and the PHP script all produce byte-identical output — including object key order and error messages.
- **One small package covers the common path from file to insight.** Parse, detect column types, render an HTML table that is safe against injected markup, export JSON, and summarise with GROUP BY / SUM / COUNT / AVG — without pulling in a single runtime dependency, without I/O, and without `eval`, so it runs the same in Node.js, Deno, Bun, browsers, edge runtimes, and every Python, Go, and PHP environment.
- **Explicit failure modes.** Invalid options and unknown columns raise errors with the same stable code and the same `[CODE] message` text in every language (`INVALID_OPTION`, `UNKNOWN_COLUMN`) instead of silently guessing.

Typical uses: previewing uploaded files in a web app, turning database exports into static report tables, summarising sensor or device logs, and small command-line conversions.

## Installation

| Language | Package | Status |
|---|---|---|
| TypeScript / JavaScript | `lombokcsv` (npm) | pending — publish staged behind the `v1.1.0` tag |
| Python | `lombokcsv` (PyPI) | pending — publish staged behind the `v1.1.0` tag |
| Go | `github.com/codinglombok/lombokcsv/go` | pending — `go/v1.1.0` tag |
| PHP | `codinglombok/lombokcsv` (Packagist) | pending — synced from the `v1.1.0` tag |
| Container | `ghcr.io/codinglombok/lombokcsv` | pending — pushed by `release.yml` |

Until the first tag, install from source: `npm install github:codinglombok/LombokCSV`, `pip install ./python`, or a Go/PHP `replace` to a local checkout.

## Quick start

### TypeScript

Install: `npm install lombokcsv` (npm).

```ts
import { CSV } from 'lombokcsv'

const csv = new CSV(`Region,Product,Qty
West,Rice,120
West,Corn,80
East,Rice,95`)

csv.getHeaders() // ['Region', 'Product', 'Qty']
csv.getTypes()   // ['string', 'string', 'number']
csv.toJSON()     // [{ Region: 'West', Product: 'Rice', Qty: '120' }, ...]
csv.toHTML({ className: 'report' })

csv.aggregate({ groupBy: 'Region', sum: ['Qty'], avg: ['Qty'], count: true })
// [ { Region: 'West', Qty_sum: 200, Qty_avg: 100, count: 2 },
//   { Region: 'East', Qty_sum: 95,  Qty_avg: 95,  count: 1 } ]
```

### Python

Install: `pip install lombokcsv` (PyPI).

```python
from lombokcsv import CSV, AggregationOptions

csv = CSV("Region,Product,Qty\nWest,Rice,120\nWest,Corn,80\nEast,Rice,95")

csv.get_headers()  # ['Region', 'Product', 'Qty']
csv.get_types()    # ['string', 'string', 'number']
csv.to_json()      # [{'Region': 'West', 'Product': 'Rice', 'Qty': '120'}, ...]
csv.to_html()

csv.aggregate(AggregationOptions(group_by="Region", sum=["Qty"], avg=["Qty"], count=True))
```

### Go

Install: `go get github.com/codinglombok/lombokcsv/go`.

```go
package main

import lombokcsv "github.com/codinglombok/lombokcsv/go"

func main() {
	csv, _ := lombokcsv.NewCSV("Region,Product,Qty\nWest,Rice,120\nWest,Corn,80\nEast,Rice,95", nil)

	rows, _ := csv.Aggregate(lombokcsv.AggregationOptions{
		GroupBy: "Region",
		Sum:     []any{"Qty"},
		Avg:     []any{"Qty"},
		Count:   true,
	})
	for _, row := range rows {
		fmt.Println(row) // key order preserved
	}
}
```

### PHP

Install: `composer require codinglombok/lombokcsv`.

```php
<?php

use CodingLombok\LombokCSV\Csv;

$csv = new Csv("Region,Product,Qty\nWest,Rice,120\nWest,Corn,80\nEast,Rice,95");

$csv->getHeaders(); // ['Region', 'Product', 'Qty']
$csv->getTypes();   // ['string', 'string', 'number']
$csv->toJSON();
$csv->toHTML();

$csv->aggregate(['groupBy' => 'Region', 'sum' => ['Qty'], 'avg' => ['Qty'], 'count' => true]);
```

## Ports

| Capability | TypeScript | Python | Go | PHP |
|---|---|---|---|---|
| `parseRows` / `parse` / type detection | yes | yes | yes | yes |
| `toHTML` | yes | yes | yes | yes |
| `toJSON` | yes | yes | yes | yes |
| `aggregate` (GROUP BY) | yes | yes | yes | yes |
| Shared vectors (152 cases) | pass | pass | pass | pass |
| CI coverage gate | 95/90 | 90 | 90 | 90 |

All four ports consume the same `vectors/lombokcsv-vectors-v1.json` file and are checked on three operating systems in CI.

## Features

| Feature | Details |
|---|---|
| Parsing | RFC 4180 quoting and doubled quotes, newlines inside quoted fields, CRLF / LF / CR line endings, leading BOM removed, custom delimiter and quote |
| Whitespace | `trim: true` (default) strips spaces and tabs around unquoted fields; quoted content is never changed; `trim: false` gives strict RFC 4180 |
| Type detection | `number`, `date`, `boolean`, `string` per column from the first 10 data rows |
| HTML | `<table>` with `<thead>` / `<tbody>`, numeric columns right-aligned, all text and the `class` / `id` attributes escaped |
| JSON | array of objects keyed by header (insertion order), or raw rows when there is no header |
| Aggregation | GROUP BY a column name or index with SUM, AVG, COUNT; non-numeric cells are ignored; `avg` is `null` without numbers |
| Errors | `CSVError` with a stable `code` (`INVALID_OPTION`, `UNKNOWN_COLUMN`) and a canonical `[CODE] message` text identical in every port |

Full API: [docs/API_LombokCSV_v1.1.0.md](docs/API_LombokCSV_v1.1.0.md). Usage guide: [docs/guide_how_to_use_LombokCSV_v1.1.0.md](docs/guide_how_to_use_LombokCSV_v1.1.0.md).

## Known limitations

The whole input is held in memory (no streaming), type detection samples only the first 10 rows, numbers are recognised only with a dot decimal separator, and there is no CSV writer. See [Known limitations](docs/full_summary_project_LombokCSV_v1.1.0.md#2-known-limitations).

## Security

Output escaping and the parser's guarantees are specified in [SPEC section 8](docs/SPEC_LombokCSV_v1.1.0.md#8-security-normative). Report vulnerabilities as described in [SECURITY.md](SECURITY.md).

## Versioning

Releases follow the ladder `v0.1.0 -> v0.2.0 -> ...`; a tag is never moved or deleted. The `check-version` job in `release.yml` refuses a tag that does not match every manifest, the top `CHANGELOG.md` entry, and the `docs/*_v<version>.md` file names. See [docs/how_to_dist_LombokCSV_v1.1.0.md](docs/how_to_dist_LombokCSV_v1.1.0.md).

## Development

```bash
npm ci
npm run check   # tsc, eslint, prettier, tests with coverage, build, standards check
npm run smoke   # smoke-test the built dist/ output
npm run fuzz    # fuzz the parser

# per-port suites
python -m coverage run --branch --source=lombokcsv -m pytest -q   # in python/
go test ./...                                                     # in go/
php php/tests/run.php                                             # from the repo root
```

See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/development_ide_LombokCSV_v1.1.0.md](docs/development_ide_LombokCSV_v1.1.0.md).

## Related libraries

- [LombokVector](https://github.com/codinglombok/LombokVector) — bit-identical vector math
- [LombokMarkDown](https://github.com/codinglombok/LombokMarkDown) — Markdown to HTML
- [LombokDocx](https://github.com/codinglombok/LombokDocx) — DOCX extraction
- [LombokHTML](https://github.com/codinglombok/LombokHTML) — HTML parsing and sanitising

## License

Apache-2.0. See [LICENSE](LICENSE).
